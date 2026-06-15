"""Drive read-time velocity tests (DRIVE-02 / DRIVE-03 extends).

Proves the stdlib-only ground-truth momentum helper (store.goal_momentum):
'stalled N days' / 'moving' / 'unknown' derived at READ time from a git
reflog tail + file mtimes, fail-open on absent/corrupt .git / unparseable
reflog / bad timestamp, mtime ground truth winning per-goal, momentum
annotated into read_snapshot (NOT behind reflection), and a local mirror of
the anti-creep no-subprocess guard.

Task 07-02-02 adds the surfacing tests (stalled-before-moving ordering,
stalled-days in the drive note, pressure raising salience while the neutral
read stays inspectable) below the velocity section.

NEW test file (not a plugin module) — test_scan_targets_are_the_plugin_modules
is unaffected. Every test uses tmp_path; the real $HERMES_HOME / repo .git is
never read for assertions (synthesized tmp .git dirs only).
"""

import time
from datetime import datetime, timezone
from pathlib import Path

from anansi import appraisal, render, store
from conftest import assert_no_directive_language

_NOW = datetime.now(timezone.utc)


def _write_git(repo_root, epoch, *, ref="refs/heads/master", garbage=False):
    """Synthesize a minimal tmp `.git` with a HEAD + a reflog whose last line
    carries `epoch` as the committer epoch. garbage=True writes an
    unparseable reflog."""
    git_dir = Path(repo_root) / ".git"
    (git_dir / "logs").mkdir(parents=True, exist_ok=True)
    (git_dir / "refs" / "heads").mkdir(parents=True, exist_ok=True)
    (git_dir / "HEAD").write_text("ref: %s\n" % ref, encoding="utf-8")
    (git_dir / ref).write_text("a" * 40 + "\n", encoding="utf-8")
    if garbage:
        reflog = "this is not a reflog line at all\n@@@ nonsense @@@\n"
    else:
        old = "0" * 40
        new = "a" * 40
        # <old> <new> <name> <email> <epoch> <tz>\tcommit: <msg>
        reflog = (
            "%s %s Dr Mani <mani@example.com> %d -0400\tcommit: seed\n"
            % (old, new, int(epoch))
        )
    (git_dir / "logs" / "HEAD").write_text(reflog, encoding="utf-8")


# ---------------------------------------------------------------------------
# DRIVE-02: goal_momentum from ground truth (read-time)
# ---------------------------------------------------------------------------


def test_moving_goal_reads_moving(tmp_path):
    """A reflog committed ~now ⇒ 'moving', small/None stalled_days."""
    _write_git(tmp_path, _NOW.timestamp())
    result = store.goal_momentum({}, repo_root=tmp_path, now=_NOW)
    assert result["momentum"] == "moving"
    assert result["stalled_days"] is None
    assert result["salience"] == store._MOMENTUM_SALIENCE["moving"]


def test_stalled_goal_reads_stalled_n_days(tmp_path):
    """A reflog committed ~5 days ago ⇒ 'stalled', stalled_days == 5 (±1),
    salience strictly above the moving case."""
    epoch = (_NOW.timestamp()) - 5 * 86400
    _write_git(tmp_path, epoch)
    result = store.goal_momentum({}, repo_root=tmp_path, now=_NOW)
    assert result["momentum"] == "stalled"
    assert abs(result["stalled_days"] - 5) <= 1
    moving = store._MOMENTUM_SALIENCE["moving"]
    assert result["salience"] > moving  # stalled is LOUDER (salience only)


def test_absent_git_returns_unknown(tmp_path):
    """A repo_root with NO .git ⇒ 'unknown', salience 0, never raises."""
    result = store.goal_momentum({}, repo_root=tmp_path, now=_NOW)
    assert result == {"momentum": "unknown", "stalled_days": None, "salience": 0.0}


def test_unparseable_reflog_returns_unknown(tmp_path):
    """A garbage `.git/logs/HEAD` ⇒ 'unknown', no raise."""
    _write_git(tmp_path, _NOW.timestamp(), garbage=True)
    result = store.goal_momentum({}, repo_root=tmp_path, now=_NOW)
    assert result["momentum"] == "unknown"
    assert result["stalled_days"] is None


def test_bad_timestamp_returns_unknown(tmp_path):
    """A goal whose updated_at can't be parsed and no git ground truth ⇒
    benign default (no fabricated momentum)."""
    goal = {"text": "g", "updated_at": "not-a-timestamp"}
    result = store.goal_momentum(goal, repo_root=tmp_path, now=_NOW)
    assert result == {"momentum": "unknown", "stalled_days": None, "salience": 0.0}


def test_mtime_hint_used_when_present(tmp_path):
    """A goal with a resolvable file hint whose mtime is fresh reads 'moving'
    even when the repo reflog is stale — per-goal mtime ground truth wins."""
    # Repo reflog is 10 days stale...
    _write_git(tmp_path, _NOW.timestamp() - 10 * 86400)
    # ...but the goal's domain points at a freshly-touched file in the repo.
    target = Path(tmp_path) / "fresh_file.py"
    target.write_text("x = 1\n", encoding="utf-8")
    fresh = time.time()
    import os as _os

    _os.utime(target, (fresh, fresh))
    goal = {"text": "g", "domain": "fresh_file.py"}
    result = store.goal_momentum(goal, repo_root=tmp_path, now=_NOW)
    assert result["momentum"] == "moving"


def test_read_snapshot_annotates_momentum(tmp_path, monkeypatch):
    """read_snapshot annotates each goal dict with a READ-TIME momentum field
    — proving momentum is derived during the read, not persisted by
    reflection. Repo-root resolution is monkeypatched to a known stale .git."""
    db = tmp_path / "state.db"
    assert store.ensure_db(db) is True
    assert store.apply_deltas(
        {"goals_add": [{"text": "ship it", "status": "active"}]}, db
    ) is True

    # A known stale repo (reflog ~7 days ago); a goal with no mtime hint and a
    # fresh updated_at would otherwise read moving — the monkeypatched stale
    # reflog is the ground truth that wins over the goal's own timestamp only
    # when the goal has no fresher signal. Here we force the repo root to the
    # stale tmp git so the read is deterministic.
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_git(repo, _NOW.timestamp() - 7 * 86400)
    monkeypatch.setattr(store, "_repo_root", lambda start=None: repo)

    snap = store.read_snapshot(db)
    assert snap is not None
    goal = snap["goals"][0]
    assert "momentum" in goal  # READ-TIME annotation present
    assert goal["momentum"]["momentum"] in ("stalled", "moving", "unknown")
    # The goal has no mtime hint, so the repo reflog (stale) is ground truth.
    assert goal["momentum"]["momentum"] == "stalled"


def test_velocity_uses_no_subprocess_self_check():
    """A local mirror of the anti-creep guard: store.py source must contain
    neither 'subprocess' nor 'os.system' — fail fast if a future edit reaches
    for a shell to read git."""
    src = (Path(store.__file__)).read_text(encoding="utf-8")
    assert "subprocess" not in src
    assert "os.system" not in src


# ---------------------------------------------------------------------------
# DRIVE-03 extends: surfacing — stalled-first ordering + stalled-days clause +
# pressure-raises-salience-but-preserves-the-neutral-read (07-02-02)
# ---------------------------------------------------------------------------


def test_stalled_renders_before_moving():
    """Two goal_signals identical except momentum: the stalled drive-note line
    renders BEFORE the moving one (louder-via-ordering, not imperative). The
    block still passes the directive-language checker."""
    signals = appraisal.parse_signals(
        {
            "goal_signals": [
                {"relates_to_goal": "moving goal", "confidence": 0.8},
                {"relates_to_goal": "stalled goal", "confidence": 0.8,
                 "stalled_days": 4},
            ]
        },
        0.6,
    )
    block = render.render_block(signals)
    assert block is not None
    lines = [l for l in block.split("\n") if l.startswith("- drive note:")]
    assert len(lines) == 2
    stalled_idx = next(i for i, l in enumerate(lines) if "stalled goal" in l)
    moving_idx = next(i for i, l in enumerate(lines) if "moving goal" in l)
    assert stalled_idx < moving_idx  # stalled surfaces FIRST (salience/order)
    assert_no_directive_language(block)


def test_stalled_days_shown_in_drive_note():
    """A stalled goal renders a '- drive note: ... stalled 3 days ...' line;
    a moving goal renders without the stalled clause."""
    stalled = appraisal.parse_signals(
        {"goal_signals": [
            {"relates_to_goal": "ship it", "confidence": 0.9, "stalled_days": 3}
        ]},
        0.6,
    )
    block = render.render_block(stalled)
    assert block is not None
    note = next(l for l in block.split("\n") if l.startswith("- drive note:"))
    assert "stalled 3 days" in note
    assert "relates to ship it" in note
    assert_no_directive_language(block)

    moving = appraisal.parse_signals(
        {"goal_signals": [
            {"relates_to_goal": "ship it", "confidence": 0.9}
        ]},
        0.6,
    )
    mblock = render.render_block(moving)
    assert mblock is not None
    mnote = next(l for l in mblock.split("\n") if l.startswith("- drive note:"))
    assert "stalled" not in mnote  # no stalled clause for a moving goal


def test_pressure_raises_salience_but_preserves_neutral_read():
    """Two stalled goals with IDENTICAL neutral momentum but different
    support_style/push metadata: the firm/push goal renders FIRST and carries a
    SEPARATE drive-effect clause, while BOTH keep the same neutral stalled-days
    observation (the neutral read stays inspectable)."""
    parsed = appraisal.parse_signals(
        {"goal_signals": [
            {"relates_to_goal": "quiet stalled goal", "confidence": 0.8,
             "stalled_days": 5},
            {"relates_to_goal": "pushed stalled goal", "confidence": 0.8,
             "stalled_days": 5},
        ]},
        0.6,
    )
    # The pressure metadata is user-authored (not model output) — attach it the
    # way __init__.enrich would, off the persisted goal.
    for sig in parsed["goal_signals"]:
        if "pushed" in sig["relates_to_goal"]:
            sig["support_style"] = "firm"
            sig["push_when_stalled"] = True

    block = render.render_block(parsed)
    assert block is not None
    lines = [l for l in block.split("\n") if l.startswith("- drive note:")]
    pushed_idx = next(i for i, l in enumerate(lines) if "pushed stalled" in l)
    quiet_idx = next(i for i, l in enumerate(lines) if "quiet stalled" in l)
    assert pushed_idx < quiet_idx  # pressure raised the pushed goal's salience

    pushed_line = lines[pushed_idx]
    quiet_line = lines[quiet_idx]
    # The NEUTRAL read is identical and intact for BOTH (inspectable).
    assert "stalled 5 days" in pushed_line
    assert "stalled 5 days" in quiet_line
    # The drive effect is rendered SEPARATELY, only on the pushed goal.
    assert "push zone" in pushed_line
    assert "push zone" not in quiet_line
    assert_no_directive_language(block)


def test_enrich_grounds_signal_in_persisted_momentum():
    """render.enrich_goal_signals anchors a parsed signal to the matching
    persisted goal's READ-TIME momentum — stalled_days + pressure metadata
    flow in even when the model didn't echo them."""
    goal_signals = [{"relates_to_goal": "ship the drive layer", "confidence": 0.9}]
    goals = [
        {
            "text": "ship the drive layer",
            "status": "active",
            "support_style": "firm",
            "push_when_stalled": 1,
            "momentum": {"momentum": "stalled", "stalled_days": 6, "salience": 1.0},
        },
    ]
    enriched = render.enrich_goal_signals(goal_signals, goals)
    assert enriched[0]["stalled_days"] == 6
    assert enriched[0]["momentum"] == "stalled"
    assert enriched[0]["support_style"] == "firm"
    # Render the enriched signals directly (render_block reads stalled_days /
    # support_style / push_when_stalled off each item).
    block = render.render_block({"goal_signals": enriched})
    assert block is not None
    note = next(l for l in block.split("\n") if l.startswith("- drive note:"))
    assert "stalled 6 days" in note
    assert "push zone" in note
    assert_no_directive_language(block)
