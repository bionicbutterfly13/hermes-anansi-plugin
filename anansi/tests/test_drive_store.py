"""Drive goal-store contract tests (DRIVE-01): schema v4, round-trip,
candidate-default INERT, v3->v4 quarantine, caps, locked-DB fail-open.

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


def test_v4_schema_has_goals_table(tmp_path):
    db = tmp_path / "state.db"
    assert store.ensure_db(db) is True
    assert store.SCHEMA_VERSION == 4
    conn = sqlite3.connect(str(db))
    try:
        tables = {
            r[0]
            for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        assert "goals" in tables
        row = conn.execute(
            "SELECT value FROM meta WHERE key='schema_version'"
        ).fetchone()
        assert row == ("4",)
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


def test_v3_db_quarantine_recreates_at_v4(tmp_path):
    """A v3 DB (forced via meta) quarantine-recreates at v4 on first ensure_db
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
    assert snap["schema_version"] == 4
    # Fresh v4 DB is usable for goal writes.
    assert store.apply_deltas(
        {"goals_add": [{"text": "post-recreate goal", "status": "active"}]}, db
    ) is True
    assert store.read_snapshot(db)["goals"][0]["text"] == "post-recreate goal"


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
