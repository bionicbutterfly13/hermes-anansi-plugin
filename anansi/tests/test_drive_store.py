"""Drive goal-store contract tests (DRIVE-01 + G2): schema v5, round-trip,
per-goal pressure round-trip, candidate-default INERT, additive v4->v5 in-place
upgrade (preserves user goals), older-version quarantine, caps, locked-DB
fail-open.

Mirrors test_store.py's idioms exactly — every test uses tmp_path, the real
$HERMES_HOME is never touched. Direct sqlite3 use is test instrumentation
only; plugin code goes through store.py exclusively. This is a NEW test file
(not a plugin module), so test_scan_targets_are_the_plugin_modules is
unaffected.
"""

import sqlite3
import time

from anansi import store


def _quarantine_files(tmp_path):
    """Quarantined DB files (excluding WAL/SHM sidecars)."""
    return [
        p
        for p in tmp_path.glob("state.db.quarantined-*")
        if not (p.name.endswith("-wal") or p.name.endswith("-shm"))
    ]


def test_v5_schema_has_goals_table_with_pressure_columns(tmp_path):
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
        cols = {c[1] for c in conn.execute("PRAGMA table_info(goals)")}
        # G2: per-goal pressure DEFINITION columns persist at v5.
        assert {"support_style", "push_when_stalled", "stall_threshold_days"} <= cols
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


def test_v3_db_quarantine_recreates_at_current(tmp_path):
    """A v3 DB (forced via meta) still quarantine-recreates — only the additive
    v4->v5 step is upgraded in place; older/non-additive versions keep the
    disposable-state doctrine. Mirrors test_schema_version_mismatch_quarantined."""
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
    assert snap["schema_version"] == store.SCHEMA_VERSION
    # Fresh DB is usable for goal writes.
    assert store.apply_deltas(
        {"goals_add": [{"text": "post-recreate goal", "status": "active"}]}, db
    ) is True
    assert store.read_snapshot(db)["goals"][0]["text"] == "post-recreate goal"


def test_v4_db_upgrades_in_place_preserving_goals(tmp_path):
    """G2 (Principle III): a structurally-sound v4 DB is upgraded to v5 via
    additive ALTER — existing user goals SURVIVE, no quarantine — and the new
    pressure columns read as defaults."""
    db = tmp_path / "state.db"
    assert store.ensure_db(db) is True
    # Recreate a realistic v4 goals table (no pressure columns) with a user goal.
    conn = sqlite3.connect(str(db))
    try:
        with conn:
            conn.execute("DROP TABLE goals")
            conn.execute(
                "CREATE TABLE goals (id INTEGER PRIMARY KEY, text TEXT NOT NULL,"
                " status TEXT NOT NULL DEFAULT 'candidate'"
                " CHECK (status IN ('active','queued','backburner','candidate')),"
                " success_criteria TEXT, flagged_priority INTEGER NOT NULL DEFAULT 0,"
                " domain TEXT, created_at TEXT, updated_at TEXT)"
            )
            conn.execute(
                "INSERT INTO goals (text, status, flagged_priority)"
                " VALUES ('legacy flagged goal', 'active', 2)"
            )
            conn.execute("UPDATE meta SET value='4' WHERE key='schema_version'")
    finally:
        conn.close()

    assert store.ensure_db(db) is True
    assert _quarantine_files(tmp_path) == []  # upgraded in place, NOT quarantined
    snap = store.read_snapshot(db)
    assert snap is not None
    assert snap["schema_version"] == store.SCHEMA_VERSION  # now 5
    goals = snap["goals"]
    assert len(goals) == 1
    g = goals[0]
    assert g["text"] == "legacy flagged goal"  # user priority preserved
    assert g["flagged_priority"] == 2
    assert g["support_style"] is None
    assert g["push_when_stalled"] == 0
    assert g["stall_threshold_days"] is None


def test_goal_pressure_round_trip(tmp_path):
    """G2: support_style / push_when_stalled / stall_threshold_days round-trip
    the store via goals_add AND goals_update; a goal without them reads
    defaults."""
    db = tmp_path / "state.db"
    assert store.ensure_db(db) is True
    assert store.apply_deltas(
        {
            "goals_add": [
                {
                    "text": "land the launch",
                    "status": "active",
                    "flagged_priority": 1,
                    "support_style": "firm",
                    "push_when_stalled": 1,
                    "stall_threshold_days": 3,
                },
                {"text": "no-pressure goal", "status": "active"},
            ]
        },
        db,
    ) is True

    goals = {g["text"]: g for g in store.read_snapshot(db)["goals"]}
    firm = goals["land the launch"]
    assert firm["support_style"] == "firm"
    assert firm["push_when_stalled"] == 1
    assert firm["stall_threshold_days"] == 3
    plain = goals["no-pressure goal"]
    assert plain["support_style"] is None
    assert plain["push_when_stalled"] == 0
    assert plain["stall_threshold_days"] is None

    assert store.apply_deltas(
        {
            "goals_update": [
                {
                    "id": plain["id"],
                    "text": "no-pressure goal",
                    "support_style": "gentle",
                    "push_when_stalled": 0,
                    "stall_threshold_days": 7,
                }
            ]
        },
        db,
    ) is True
    updated = {g["text"]: g for g in store.read_snapshot(db)["goals"]}["no-pressure goal"]
    assert updated["support_style"] == "gentle"
    assert updated["stall_threshold_days"] == 7


def test_goals_cap_enforced(tmp_path):
    """goals capped at 50; survivors are the most recent rows — mirrors
    test_caps_enforced."""
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
