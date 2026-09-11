"""Drive goal-store contract tests (DRIVE-01): schema v4, round-trip,
candidate-default INERT, v3->v4 quarantine, caps, locked-DB fail-open.

Mirrors test_store.py's idioms exactly — every test uses tmp_path, the real
$HERMES_HOME is never touched. Direct sqlite3 use is test instrumentation
only; plugin code goes through store.py exclusively. This is a NEW test file
(not a plugin module), so test_scan_targets_are_the_plugin_modules is
unaffected.
"""

import os
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import anansi
from anansi import appraisal, config, render, store


def _quarantine_files(tmp_path):
    """Quarantined DB files (excluding WAL/SHM sidecars)."""
    return [
        p
        for p in tmp_path.glob("state.db.quarantined-*")
        if not (p.name.endswith("-wal") or p.name.endswith("-shm"))
    ]


def _create_v4_db(db):
    """Build a populated historical v4 database without calling store code.

    Direct SQLite is deliberate test instrumentation: this fixture proves the
    additive migration against a pre-v5 database rather than a fresh schema.
    """
    conn = sqlite3.connect(str(db))
    try:
        with conn:
            conn.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            conn.execute("CREATE TABLE affect_summary (id INTEGER PRIMARY KEY, summary TEXT)")
            conn.execute("CREATE TABLE concerns (id INTEGER PRIMARY KEY, text TEXT)")
            conn.execute("CREATE TABLE contradictions (id INTEGER PRIMARY KEY, description TEXT)")
            conn.execute("CREATE TABLE trust_scores (key TEXT PRIMARY KEY, value REAL)")
            conn.execute("CREATE TABLE turn_log (id INTEGER PRIMARY KEY, session_id TEXT)")
            conn.execute("CREATE TABLE telemetry (id INTEGER PRIMARY KEY, ts TEXT, outcome TEXT)")
            conn.execute(
                "CREATE TABLE goals ("
                "id INTEGER PRIMARY KEY, text TEXT NOT NULL, "
                "status TEXT NOT NULL DEFAULT 'candidate', success_criteria TEXT, "
                "flagged_priority INTEGER NOT NULL DEFAULT 0, domain TEXT, "
                "created_at TEXT, updated_at TEXT)"
            )
            conn.execute("INSERT INTO meta VALUES ('schema_version', '4')")
    finally:
        conn.close()


def test_v5_schema_has_pressure_columns(tmp_path):
    db = tmp_path / "state.db"
    assert store.ensure_db(db) is True
    assert store.SCHEMA_VERSION == 5
    conn = sqlite3.connect(str(db))
    try:
        tables = {
            r[0]
            for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        assert "goals" in tables
        assert {
            "support_style", "push_when_stalled", "stall_threshold_days"
        } <= {row[1] for row in conn.execute("PRAGMA table_info(goals)")}
        row = conn.execute(
            "SELECT value FROM meta WHERE key='schema_version'"
        ).fetchone()
        assert row == ("5",)
    finally:
        conn.close()
    snap = store.read_snapshot(db)
    assert snap is not None
    assert snap["goals"] == []  # empty list, present in the snapshot dict


def test_goal_round_trip(tmp_path):
    """A user-minted active goal + an agent-nominated candidate round-trip
    with correct status / flagged_priority / success_criteria; statuses
    survive a second read."""
    db = tmp_path / "state.db"
    assert store.ensure_db(db) is True

    deltas = {
        "goals_add": [
            {
                "text": "ship the drive layer",
                "status": "active",
                "success_criteria": "phase 7 complete",
                "flagged_priority": 1,
                "domain": "anansi",
                "support_style": "firm",
                "push_when_stalled": 1,
                "stall_threshold_days": 3,
            },
            {
                "text": "maybe explore a dashboard",
                "status": "candidate",
                "success_criteria": "TBD",
                "flagged_priority": 0,
                "domain": "anansi",
            },
        ],
    }
    assert store.apply_deltas(deltas, db) is True

    def check(snap):
        assert snap is not None
        goals = {g["text"]: g for g in snap["goals"]}
        assert set(goals) == {"ship the drive layer", "maybe explore a dashboard"}
        active = goals["ship the drive layer"]
        assert active["status"] == "active"
        assert active["flagged_priority"] == 1
        assert active["success_criteria"] == "phase 7 complete"
        assert active["domain"] == "anansi"
        assert active["support_style"] == "firm"
        assert active["push_when_stalled"] == 1
        assert active["stall_threshold_days"] == 3
        candidate = goals["maybe explore a dashboard"]
        assert candidate["status"] == "candidate"
        assert candidate["flagged_priority"] == 0
        assert candidate["success_criteria"] == "TBD"

    check(store.read_snapshot(db))
    # Second fresh read (new call, simulating reload): identical signals.
    check(store.read_snapshot(db))


def test_candidate_default_is_inert(tmp_path):
    """A goals_add item WITHOUT a status persists as 'candidate' (INERT) and
    only becomes active via a goals_status promotion."""
    db = tmp_path / "state.db"
    assert store.ensure_db(db) is True

    assert store.apply_deltas(
        {"goals_add": [{"text": "agent-nominated idea"}]}, db
    ) is True
    snap = store.read_snapshot(db)
    assert snap is not None
    goal = snap["goals"][0]
    assert goal["status"] == "candidate"  # INERT default
    goal_id = goal["id"]

    # Promotion path candidate -> active.
    assert store.apply_deltas(
        {"goals_status": [{"id": goal_id, "status": "active"}]}, db
    ) is True
    snap2 = store.read_snapshot(db)
    assert snap2 is not None
    assert snap2["goals"][0]["status"] == "active"


def test_v3_db_quarantine_recreates_at_v5(tmp_path):
    """A v3 DB (forced via meta) quarantine-recreates at v5 on first ensure_db
    — mirrors test_schema_version_mismatch_quarantined."""
    db = tmp_path / "state.db"
    assert store.ensure_db(db) is True
    conn = sqlite3.connect(str(db))
    try:
        with conn:
            conn.execute("UPDATE meta SET value='3' WHERE key='schema_version'")
    finally:
        conn.close()
    assert store.ensure_db(db) is True
    assert len(_quarantine_files(tmp_path)) == 1
    snap = store.read_snapshot(db)
    assert snap is not None
    assert snap["schema_version"] == 5
    # Fresh v5 DB is usable for goal writes.
    assert store.apply_deltas(
        {"goals_add": [{"text": "post-recreate goal", "status": "active"}]}, db
    ) is True
    assert store.read_snapshot(db)["goals"][0]["text"] == "post-recreate goal"


def test_populated_v4_db_migrates_additively_with_legacy_pressure_defaults(tmp_path):
    db = tmp_path / "state.db"
    _create_v4_db(db)
    created = "2026-01-01T00:00:00+00:00"
    conn = sqlite3.connect(str(db))
    try:
        with conn:
            conn.execute(
                "INSERT INTO goals (id, text, status, success_criteria, "
                "flagged_priority, domain, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (7, "preserve me", "active", "done", 1, "anansi", created, created),
            )
    finally:
        conn.close()

    assert store.ensure_db(db) is True
    snapshot = store.read_snapshot(db)
    assert snapshot is not None and snapshot["schema_version"] == 5
    assert snapshot["goals"] == [{
        "id": 7,
        "text": "preserve me",
        "status": "active",
        "success_criteria": "done",
        "flagged_priority": 1,
        "domain": "anansi",
        "created_at": created,
        "updated_at": created,
        "support_style": None,
        "push_when_stalled": 0,
        "stall_threshold_days": None,
        "momentum": snapshot["goals"][0]["momentum"],
    }]
    assert store.ensure_db(db) is True  # migration is idempotent
    assert not _quarantine_files(tmp_path)


def test_locked_v4_db_is_unavailable_without_quarantine_or_partial_migration(tmp_path, monkeypatch):
    db = tmp_path / "state.db"
    _create_v4_db(db)
    before = db.read_bytes()
    real_connect = sqlite3.connect
    monkeypatch.setattr(store, "_DEFAULT_BUSY_TIMEOUT_MS", 100)
    monkeypatch.setattr(
        store.sqlite3, "connect", lambda *a, **kw: real_connect(*a, timeout=0.1, **kw)
    )
    holder = real_connect(str(db), timeout=0.1)
    try:
        holder.execute("PRAGMA journal_mode=DELETE")
        holder.execute("BEGIN EXCLUSIVE")
        start = time.monotonic()
        assert store.ensure_db(db) is False
        assert time.monotonic() - start < 2.0
        assert db.read_bytes() == before
        assert not _quarantine_files(tmp_path)
    finally:
        holder.rollback()
        holder.close()


def test_persisted_pressure_authorizes_effect_only_after_its_threshold(tmp_path, monkeypatch):
    """A real persisted snapshot authorizes only the reached threshold.

    The flagged rows exercise first-person wants, while the ordinary row
    proves the separate third-person push-zone contract.  No momentum or
    snapshot seam is mocked: file mtimes and the SQLite timestamps provide
    the actual four-day stalled read used by pre_llm_call.
    """
    db = tmp_path / "state.db"
    repo = tmp_path / "repo"
    repo.mkdir()
    old = datetime.now(timezone.utc) - timedelta(days=4, minutes=1)
    for name in ("threshold-three", "threshold-five", "ordinary-three"):
        path = repo / name
        path.write_text(name, encoding="utf-8")
        epoch = old.timestamp()
        os.utime(path, (epoch, epoch))

    assert store.ensure_db(db) is True
    assert store.apply_deltas({"goals_add": [
        {"text": "threshold three", "status": "active", "flagged_priority": 1,
         "domain": "threshold-three", "support_style": "firm",
         "push_when_stalled": 1, "stall_threshold_days": 3},
        {"text": "threshold five", "status": "active", "flagged_priority": 1,
         "domain": "threshold-five", "support_style": "firm",
         "push_when_stalled": 1, "stall_threshold_days": 5},
        {"text": "ordinary three", "status": "active", "flagged_priority": 0,
         "domain": "ordinary-three", "support_style": "firm",
         "push_when_stalled": 1, "stall_threshold_days": 3},
    ]}, db) is True
    conn = sqlite3.connect(str(db))
    try:
        with conn:
            conn.execute("UPDATE goals SET updated_at=?", (old.isoformat(),))
    finally:
        conn.close()

    monkeypatch.setattr(store, "get_db_path", lambda: db)
    monkeypatch.setattr(store, "_repo_root", lambda: repo)
    fresh_snapshot = store.read_snapshot(db)
    assert fresh_snapshot is not None
    fresh_goals = {goal["text"]: goal for goal in fresh_snapshot["goals"]}
    assert fresh_goals["threshold three"]["momentum"]["stalled_days"] == 4
    assert fresh_goals["threshold five"]["momentum"]["stalled_days"] == 4

    result = SimpleNamespace(
        signals={
            "instincts": [],
            "salient_observations": [{"text": "same state", "confidence": 0.9}],
            "contradiction_flags": [],
            "suggested_memory_searches": [],
            "goal_signals": [
                {"relates_to_goal": "threshold three", "confidence": 0.9,
                 "support_style": "quiet", "push_when_stalled": 0,
                 "stalled_days": 0},
                {"relates_to_goal": "threshold five", "confidence": 0.8},
                {"relates_to_goal": "ordinary three", "confidence": 0.7},
            ],
            "gut_reaction": "",
        },
        outcome="ok", wall_ms=0, model="fake", tokens_in=0,
        tokens_out=0, error=None,
    )
    monkeypatch.setattr(config, "get_cfg", lambda: {
        "enabled": True, "drive_enabled": True, "drive_domains": [],
        "drive_energy_budget": 3, "drive_pressure": "standard",
    })
    monkeypatch.setattr(store, "record_telemetry", lambda *a, **kw: None)
    monkeypatch.setattr(appraisal, "should_skip", lambda *a: None)
    monkeypatch.setattr(appraisal, "normalize_message", lambda value: value)
    monkeypatch.setattr(appraisal, "run_appraisal", lambda **kwargs: result)
    anansi.register(SimpleNamespace(llm=object(), register_hook=lambda *a, **k: None))
    anansi._session_state.update({"session_id": None, "last_msg_norm": None})
    try:
        output = anansi.pre_llm_call(session_id="pressure", user_message="status?")
        assert output is not None
        block = output["context"]
    finally:
        anansi._ctx = None

    three_want = next(line for line in block.split("\n") if "threshold three" in line)
    five_want = next(line for line in block.split("\n") if "threshold five" in line)
    ordinary_note = next(line for line in block.split("\n") if "ordinary three" in line)
    assert three_want.startswith("- drive want:")
    assert "stalled 4 days" in three_want
    assert "[under-support: user-authorized firmer support]" in three_want
    assert "[push zone:" not in three_want
    assert five_want.startswith("- drive want:")
    assert "stalled 4 days" in five_want
    assert "[under-support:" not in five_want
    assert ordinary_note.startswith("- drive note:")
    assert "[push zone: user-authorized firmer support]" in ordinary_note
    assert "[under-support:" not in ordinary_note
    assert not any(
        line.startswith("- drive note:") and "threshold" in line
        for line in block.split("\n")
    )


def test_pre_llm_call_passes_standard_pressure_without_changing_render_contract(tmp_path, monkeypatch):
    db = tmp_path / "state.db"
    monkeypatch.setattr(store, "get_db_path", lambda: db)
    assert store.ensure_db() is True
    captured = {}
    signals = {
        "instincts": [], "salient_observations": [{"text": "same state", "confidence": 0.9}],
        "contradiction_flags": [], "suggested_memory_searches": [],
        "goal_signals": [], "gut_reaction": "",
    }
    result = SimpleNamespace(
        signals=signals, outcome="ok", wall_ms=0, model="fake", tokens_in=0,
        tokens_out=0, error=None,
    )
    monkeypatch.setattr(config, "get_cfg", lambda: {
        "enabled": True, "drive_enabled": True, "drive_domains": [],
        "drive_energy_budget": 3, "drive_pressure": "standard",
    })
    monkeypatch.setattr(appraisal, "should_skip", lambda *a: None)
    monkeypatch.setattr(appraisal, "normalize_message", lambda value: value)
    monkeypatch.setattr(appraisal, "run_appraisal", lambda **kwargs: result)
    original_render = render.render_block
    def capture_render(*args, **kwargs):
        captured["pressure"] = kwargs.get("pressure")
        return original_render(*args, **kwargs)
    monkeypatch.setattr(render, "render_block", capture_render)
    anansi.register(SimpleNamespace(llm=object(), register_hook=lambda *a, **k: None))
    anansi._session_state.update({"session_id": None, "last_msg_norm": None})
    try:
        out = anansi.pre_llm_call(session_id="pressure", user_message="status?")
        assert captured["pressure"] == "standard"
        assert out == {"context": original_render(signals, goals=[])}
    finally:
        anansi._ctx = None


def test_unflagged_goals_cap_enforced(tmp_path):
    """Unflagged goals remain capped at 50; survivors are the newest rows."""
    db = tmp_path / "state.db"
    assert store.ensure_db(db) is True

    assert store.apply_deltas(
        {
            "goals_add": [
                {"text": "goal-%02d" % i, "status": "active"} for i in range(60)
            ]
        },
        db,
    ) is True

    snap = store.read_snapshot(db)
    assert snap is not None
    assert len(snap["goals"]) <= 50
    texts = {g["text"] for g in snap["goals"]}
    assert "goal-59" in texts  # last-inserted survives
    assert "goal-00" not in texts  # first-inserted evicted


def test_goal_cap_preserves_all_flagged_priorities_under_unflagged_pressure(tmp_path):
    """The goals cap applies only to unflagged rows, never flagged priorities."""
    db = tmp_path / "state.db"
    assert store.ensure_db(db) is True

    flagged = [
        {
            "text": "flagged priority %02d" % index,
            "status": "active",
            "flagged_priority": 1,
        }
        for index in range(55)
    ]
    unflagged = [
        {"text": "ordinary goal %02d" % index, "status": "active"}
        for index in range(60)
    ]
    assert store.apply_deltas({"goals_add": flagged + unflagged}, db) is True

    snapshot = store.read_snapshot(db)
    assert snapshot is not None
    goals = {goal["text"]: goal for goal in snapshot["goals"]}
    assert {"flagged priority %02d" % index for index in range(55)} <= set(goals)
    assert sum(not goal["flagged_priority"] for goal in goals.values()) == 50
    assert "ordinary goal 59" in goals
    assert "ordinary goal 00" not in goals


def test_legacy_goal_update_preserves_v5_drive_fields(tmp_path):
    """A v4-shaped update cannot silently remove persisted drive consent."""
    db = tmp_path / "state.db"
    assert store.ensure_db(db) is True
    assert store.apply_deltas(
        {
            "goals_add": [
                {
                    "text": "ship safely",
                    "status": "active",
                    "success_criteria": "green suite",
                    "flagged_priority": 1,
                    "domain": "anansi",
                    "support_style": "firm",
                    "push_when_stalled": 1,
                    "stall_threshold_days": 3,
                }
            ]
        },
        db,
    ) is True
    original = store.read_snapshot(db)["goals"][0]

    assert store.apply_deltas(
        {
            "goals_update": [
                {
                    "id": original["id"],
                    "text": "ship safely soon",
                    "success_criteria": "green suite",
                    "flagged_priority": 1,
                    "domain": "anansi",
                }
            ]
        },
        db,
    ) is True

    updated = store.read_snapshot(db)["goals"][0]
    assert updated["text"] == "ship safely soon"
    assert updated["support_style"] == "firm"
    assert updated["push_when_stalled"] == 1
    assert updated["stall_threshold_days"] == 3


def test_locked_db_goal_write_returns_false(tmp_path):
    """DRIVE-01 fail-open: a goals_add against a write-locked DB returns False
    and degrades fast — mirrors test_locked_db_write_degrades."""
    db = tmp_path / "state.db"
    assert store.ensure_db(db) is True
    holder = sqlite3.connect(str(db))
    try:
        holder.execute("BEGIN IMMEDIATE")
        holder.execute("INSERT INTO concerns (text) VALUES ('lock holder')")
        start = time.monotonic()
        result = store.apply_deltas(
            {"goals_add": [{"text": "blocked goal", "status": "active"}]},
            db,
            busy_timeout_ms=100,
        )
        elapsed = time.monotonic() - start
        assert result is False
        assert elapsed < 2.0
    finally:
        holder.rollback()
        holder.close()


def test_unknown_goal_delta_ignored(tmp_path):
    """A bogus goals key is ignored gracefully; the snapshot is unchanged."""
    db = tmp_path / "state.db"
    assert store.ensure_db(db) is True
    before = store.read_snapshot(db)
    assert store.apply_deltas({"goals_bogus": [{"text": "nope"}]}, db) is True
    after = store.read_snapshot(db)
    assert after == before
    assert after["goals"] == []
