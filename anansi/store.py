"""anansi state store — the plugin's ENTIRE SQLite surface.

No other module in this plugin may import sqlite3 or touch state.db.

Contract (see .planning/phases/01-skeleton-state/01-CONTEXT.md, all locked):
- Location: $HERMES_HOME/anansi/state.db, resolved via the host's
  get_hermes_home() with an env-var fallback. Never a literal path.
- PRAGMAs: journal_mode=WAL (persistent, set at creation), synchronous=NORMAL
  and busy_timeout on every write connection. Hot-path reads open read-only
  URI connections (file:<path>?mode=ro) and never create files.
- Single write funnel: ALL writes go through apply_deltas() in one transaction.
- Disposable-state doctrine: ANY structural problem (corruption, schema_version
  mismatch, missing table, failed open) -> quarantine + recreate fresh. No
  migration framework.
- No public function in this module may raise to a caller. Failure values:
  ensure_db -> False, read_snapshot -> None, apply_deltas -> False.
"""

import json
import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("hermes.plugins.anansi.store")

SCHEMA_VERSION = 1

# Per-table row caps (seed values; tune later with telemetry).
CAPS = {
    "concerns": 20,
    "contradictions": 50,
    "turn_log": 500,
    "trust_scores": 64,
}

_DEFAULT_BUSY_TIMEOUT_MS = 5000

_TABLES = (
    "meta",
    "affect_summary",
    "concerns",
    "contradictions",
    "trust_scores",
    "turn_log",
)

# Caps/decay columns (expires_at, decayed_weight) are in the schema NOW even
# though only Phase 3 writes them — schema churn is the expensive part.
_SCHEMA_DDL = (
    """CREATE TABLE meta            (key TEXT PRIMARY KEY, value TEXT NOT NULL)""",
    """CREATE TABLE affect_summary  (id INTEGER PRIMARY KEY CHECK (id=1), summary TEXT,
                                     valence REAL, arousal REAL, intensity REAL, updated_at TEXT)""",
    """CREATE TABLE concerns        (id INTEGER PRIMARY KEY, text TEXT NOT NULL, weight REAL DEFAULT 1.0,
                                     decayed_weight REAL, status TEXT DEFAULT 'open', expires_at TEXT,
                                     created_at TEXT, updated_at TEXT)""",
    """CREATE TABLE contradictions  (id INTEGER PRIMARY KEY, kind TEXT CHECK (kind IN
                                     ('semantic','narrative','relational','emotional')),
                                     description TEXT NOT NULL, evidence TEXT,
                                     resolved INTEGER DEFAULT 0, decayed_weight REAL, expires_at TEXT,
                                     created_at TEXT)""",
    """CREATE TABLE trust_scores    (key TEXT PRIMARY KEY, value REAL NOT NULL, updated_at TEXT)""",
    """CREATE TABLE turn_log        (id INTEGER PRIMARY KEY, session_id TEXT, turn_id TEXT,
                                     user_excerpt TEXT, appraisal_json TEXT, created_at TEXT)""",
)


def get_db_path() -> Path:
    """Resolve $HERMES_HOME/anansi/state.db. Never raises."""
    home = None
    try:
        # Lazy host import — keeps this module importable outside the host.
        from hermes_constants import get_hermes_home

        home = Path(get_hermes_home())
    except Exception:
        home = None
    if home is None:
        home = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
    return home / "anansi" / "state.db"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _quarantine(db_path) -> None:
    """Move a structurally-broken DB (and WAL/SHM sidecars) out of the way.

    Renames state.db -> state.db.quarantined-<UTC ts>; on rename failure falls
    back to os.remove. Never raises — on total failure it returns and lets
    ensure_db report False when recreate fails.
    """
    try:
        path = Path(db_path)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        target = path.with_name(path.name + ".quarantined-" + ts)
        moved = False
        try:
            os.replace(path, target)
            moved = True
        except OSError:
            try:
                os.remove(path)
            except OSError:
                logger.warning(
                    "anansi state quarantine failed — could not rename or remove %s", path
                )
                return
        for suffix in ("-wal", "-shm"):
            sidecar = Path(str(path) + suffix)
            if sidecar.exists():
                try:
                    os.replace(sidecar, Path(str(target) + suffix))
                except OSError:
                    try:
                        os.remove(sidecar)
                    except OSError:
                        pass
        logger.warning(
            "anansi state DB quarantined: %s -> %s",
            path,
            target if moved else "(removed; rename failed)",
        )
    except Exception as exc:
        logger.warning("anansi quarantine error (continuing): %s", exc)
        logger.debug("quarantine failure detail", exc_info=True)


def _verify_structure(path: Path) -> bool:
    """True iff the DB at path passes quick_check, has all six tables, and
    meta schema_version matches SCHEMA_VERSION. Never raises."""
    conn = None
    try:
        conn = sqlite3.connect(str(path))
        row = conn.execute("PRAGMA quick_check").fetchone()
        if row is None or row[0] != "ok":
            return False
        tables = {
            r[0]
            for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        if not set(_TABLES) <= tables:
            return False
        row = conn.execute(
            "SELECT value FROM meta WHERE key='schema_version'"
        ).fetchone()
        if row is None or str(row[0]) != str(SCHEMA_VERSION):
            return False
        return True
    except Exception:
        return False
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


def _create_fresh(path: Path) -> bool:
    """Create a new DB with the locked schema. WAL is set here (persistent)."""
    conn = None
    try:
        conn = sqlite3.connect(str(path))
        conn.execute("PRAGMA busy_timeout=%d" % _DEFAULT_BUSY_TIMEOUT_MS)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        with conn:
            for ddl in _SCHEMA_DDL:
                conn.execute(ddl)
            conn.execute(
                "INSERT INTO meta (key, value) VALUES ('schema_version', ?)",
                (str(SCHEMA_VERSION),),
            )
        return True
    except Exception as exc:
        logger.warning("anansi state DB creation failed (degrading): %s", exc)
        logger.debug("creation failure detail", exc_info=True)
        return False
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


def ensure_db(db_path=None) -> bool:
    """Create the DB + schema if absent; verify structure if present.

    ANY structural failure (corrupt file, bad quick_check, missing table,
    schema_version mismatch) -> quarantine then recreate fresh. Returns True
    if a usable DB exists at exit, False otherwise. Never raises.
    """
    try:
        path = Path(db_path) if db_path is not None else get_db_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            if _verify_structure(path):
                return True
            _quarantine(path)
        return _create_fresh(path)
    except Exception as exc:
        logger.warning("anansi ensure_db failed (degrading): %s", exc)
        logger.debug("ensure_db failure detail", exc_info=True)
        return False


def _rows_as_dicts(conn, table: str) -> list:
    cur = conn.execute("SELECT * FROM %s ORDER BY id" % table)
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def read_snapshot(db_path=None):
    """Hot-path read over a read-only URI connection.

    Returns the snapshot dict, or None on ANY error (absent file, locked,
    corrupt, missing table). Never raises, never creates files.
    """
    conn = None
    try:
        path = Path(db_path) if db_path is not None else get_db_path()
        conn = sqlite3.connect("file:%s?mode=ro" % path, uri=True)
        row = conn.execute(
            "SELECT value FROM meta WHERE key='schema_version'"
        ).fetchone()
        if row is None:
            return None
        schema_version = int(row[0])
        affect = None
        cur = conn.execute("SELECT * FROM affect_summary WHERE id=1")
        arow = cur.fetchone()
        if arow is not None:
            affect = dict(zip([c[0] for c in cur.description], arow))
        snapshot = {
            "schema_version": schema_version,
            "affect_summary": affect,
            "concerns": _rows_as_dicts(conn, "concerns"),
            "contradictions": _rows_as_dicts(conn, "contradictions"),
            "trust_scores": {
                key: value
                for key, value in conn.execute("SELECT key, value FROM trust_scores")
            },
            "turn_log_count": conn.execute(
                "SELECT COUNT(*) FROM turn_log"
            ).fetchone()[0],
        }
        return snapshot
    except Exception as exc:
        logger.warning("anansi read_snapshot failed (degrading): %s", exc)
        logger.debug("read_snapshot failure detail", exc_info=True)
        return None
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


def apply_deltas(deltas: dict, db_path=None, busy_timeout_ms: int = 5000) -> bool:
    """THE single write entry point — one transaction, caps enforced inside it.

    Recognized delta keys: affect_summary, concerns_add, concerns_resolve,
    contradictions_add, trust_scores, turn_log_add. Unknown keys are ignored
    with a debug log. Returns True on commit, False on ANY error (the
    transaction is rolled back). Never raises.
    """
    conn = None
    try:
        path = Path(db_path) if db_path is not None else get_db_path()
        now = _utc_now_iso()
        conn = sqlite3.connect(str(path))
        conn.execute("PRAGMA busy_timeout=%d" % int(busy_timeout_ms))
        conn.execute("PRAGMA synchronous=NORMAL")
        with conn:  # one transaction: commits on success, rolls back on error
            for key, payload in (deltas or {}).items():
                if key == "affect_summary":
                    conn.execute(
                        "INSERT INTO affect_summary"
                        " (id, summary, valence, arousal, intensity, updated_at)"
                        " VALUES (1, ?, ?, ?, ?, ?)"
                        " ON CONFLICT(id) DO UPDATE SET"
                        " summary=excluded.summary, valence=excluded.valence,"
                        " arousal=excluded.arousal, intensity=excluded.intensity,"
                        " updated_at=excluded.updated_at",
                        (
                            payload.get("summary"),
                            payload.get("valence"),
                            payload.get("arousal"),
                            payload.get("intensity"),
                            now,
                        ),
                    )
                elif key == "concerns_add":
                    for item in payload:
                        conn.execute(
                            "INSERT INTO concerns"
                            " (text, weight, status, created_at, updated_at)"
                            " VALUES (?, ?, 'open', ?, ?)",
                            (item.get("text"), item.get("weight", 1.0), now, now),
                        )
                elif key == "concerns_resolve":
                    for concern_id in payload:
                        conn.execute(
                            "UPDATE concerns SET status='resolved', updated_at=?"
                            " WHERE id=?",
                            (now, concern_id),
                        )
                elif key == "contradictions_add":
                    for item in payload:
                        conn.execute(
                            "INSERT INTO contradictions"
                            " (kind, description, evidence, created_at)"
                            " VALUES (?, ?, ?, ?)",
                            (
                                item.get("kind"),
                                item.get("description"),
                                item.get("evidence"),
                                now,
                            ),
                        )
                elif key == "trust_scores":
                    for score_key, score_value in payload.items():
                        conn.execute(
                            "INSERT INTO trust_scores (key, value, updated_at)"
                            " VALUES (?, ?, ?)"
                            " ON CONFLICT(key) DO UPDATE SET"
                            " value=excluded.value, updated_at=excluded.updated_at",
                            (score_key, float(score_value), now),
                        )
                elif key == "turn_log_add":
                    for item in payload:
                        appraisal = item.get("appraisal_json")
                        if isinstance(appraisal, (dict, list)):
                            appraisal = json.dumps(appraisal, ensure_ascii=False)
                        conn.execute(
                            "INSERT INTO turn_log"
                            " (session_id, turn_id, user_excerpt, appraisal_json,"
                            " created_at) VALUES (?, ?, ?, ?, ?)",
                            (
                                item.get("session_id"),
                                item.get("turn_id"),
                                item.get("user_excerpt"),
                                appraisal,
                                now,
                            ),
                        )
                else:
                    logger.debug("apply_deltas: ignoring unknown delta key %r", key)
            # Enforce caps inside the SAME transaction: evict oldest rows
            # (lowest id) beyond each cap; trust_scores evicts oldest
            # updated_at beyond its cap.
            for table in ("concerns", "contradictions", "turn_log"):
                conn.execute(
                    "DELETE FROM {t} WHERE id NOT IN"
                    " (SELECT id FROM {t} ORDER BY id DESC LIMIT ?)".format(t=table),
                    (CAPS[table],),
                )
            conn.execute(
                "DELETE FROM trust_scores WHERE key NOT IN"
                " (SELECT key FROM trust_scores"
                "  ORDER BY updated_at DESC, rowid DESC LIMIT ?)",
                (CAPS["trust_scores"],),
            )
        return True
    except Exception as exc:
        logger.warning("anansi apply_deltas failed (degrading): %s", exc)
        logger.debug("apply_deltas failure detail", exc_info=True)
        return False
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
