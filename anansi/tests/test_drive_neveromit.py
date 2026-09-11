"""DRIVE-05 never-omit — the drive red line.

Silent omission of a user-flagged priority is betrayal (Dr. Mani's top
anti-value, 06-CONTEXT). A goal carrying ``flagged_priority`` must ALWAYS
appear in the surfaced block when a block renders: it is rendered FIRST (right
after the sentinel + framing) as a FIRST-PERSON ``- drive want:`` line and is
EXEMPT from BOTH the per-category ``[:3]`` slice AND the token-cap
trailing-line-drop, so it is never the dropped 4th item nor the dropped
trailing line — even under adversarial crowding.

For a successful appraisal with an empty signal mapping, persisted active
flagged priorities still manufacture the protected guidance they are owed.
Actual appraisal failure remains distinct: ``signals is None`` injects nothing.

Anti-complacency: a stalled goal the user authorized for firmer support
(support_style='firm' / push_when_stalled=1) renders a VISIBLE
under-support/drive-effect clause rather than being quietly downranked.

Pure render-layer tests plus one full-hook integration. No network.
"""

import json
import sqlite3
import types

import pytest

from conftest import assert_no_directive_language
from anansi import appraisal, render


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

FLAG = "DISTINCTIVE-FLAGGED-PRIORITY-ZZZ"


def _flagged_goal(text=FLAG, stalled_days=None, push=False):
    goal = {
        "text": text,
        "status": "active",
        "flagged_priority": 1,
        "momentum": {
            "momentum": "stalled" if stalled_days is not None else "unknown",
            "stalled_days": stalled_days,
            "salience": 1.0 if stalled_days is not None else 0.0,
        },
    }
    if push:
        goal["push_when_stalled"] = 1
    return goal


def _non_flagged_goal(text):
    return {
        "text": text,
        "status": "active",
        "flagged_priority": 0,
        "momentum": {"momentum": "unknown", "stalled_days": None, "salience": 0.0},
    }


def _rich_signals(n_goal_signals=5):
    """A real parsed-signal dict with several non-flagged goal_signals."""
    payload = {
        "instincts": [
            {"kind": "caution", "intensity": 0.7, "reason": "live system risk",
             "confidence": 0.9},
        ],
        "salient_observations": [
            {"text": "migration topic recurs", "confidence": 0.85},
        ],
        "goal_signals": [
            {"relates_to_goal": "non-flagged goal %d" % i, "confidence": 0.9}
            for i in range(n_goal_signals)
        ],
        "gut_reaction": "tractable",
    }
    return appraisal.parse_signals(payload, 0.6)


def _crowding_signals():
    """Signals that crowd WELL past the ~500-token cap: many high-confidence
    instincts / observations / contradictions + several non-flagged goals."""
    payload = {
        "instincts": [
            {"kind": "caution", "intensity": 0.95,
             "reason": "a long reason that eats tokens " * 6, "confidence": 0.95}
            for _ in range(8)
        ],
        "salient_observations": [
            {"text": "a long salient observation that eats tokens " * 6,
             "confidence": 0.95}
            for _ in range(8)
        ],
        "contradiction_flags": [
            {"kind": "narrative",
             "text": "a long contradiction that eats tokens " * 6,
             "confidence": 0.9}
            for _ in range(8)
        ],
        "suggested_memory_searches": ["search phrase one", "search phrase two"],
        "goal_signals": [
            {"relates_to_goal": "non-flagged crowder %d" % i, "confidence": 0.9}
            for i in range(6)
        ],
        "gut_reaction": "a long gut reaction that eats tokens " * 4,
    }
    return appraisal.parse_signals(payload, 0.6)


# Low-trust snapshot mirrors test_safe03_corpus_with_low_trust_snapshots: two
# sub-threshold trust keys add hint lines that also crowd the cap.
LOW_TRUST_SNAPSHOT = {
    "trust_scores": {
        "source:webscrape": 0.1,
        "you must deploy now": 0.2,  # imperative bait survives only as quoted
        "user:drmani": 0.9,          # above threshold — never a hint
    },
}


# ---------------------------------------------------------------------------
# DRIVE-05: exempt from the [:3] per-category slice
# ---------------------------------------------------------------------------


def test_flagged_goal_survives_top3_slice():
    """5 non-flagged goal_signals (sliced to 3 as `- drive note:` lines) + 1
    flagged goal — the flagged want line is still present."""
    signals = _rich_signals(n_goal_signals=5)
    block = render.render_block(signals, goals=[_flagged_goal()])
    assert block is not None
    notes = [l for l in block.split("\n") if l.startswith("- drive note:")]
    assert len(notes) == 3  # non-flagged still capped at 3
    wants = [l for l in block.split("\n") if l.startswith("- drive want:")]
    assert len(wants) == 1
    assert FLAG in wants[0]
    assert_no_directive_language(block)


def test_multiple_flagged_goals_all_survive_slice():
    """ALL flagged goals render — the slice caps non-flagged notes, never the
    flagged wants (render all 4 flagged, not just 3)."""
    signals = _rich_signals(n_goal_signals=5)
    flagged = [_flagged_goal("flagged alpha %d" % i) for i in range(4)]
    block = render.render_block(signals, goals=flagged)
    assert block is not None
    wants = [l for l in block.split("\n") if l.startswith("- drive want:")]
    assert len(wants) == 4  # NOT sliced to 3
    assert_no_directive_language(block)


# ---------------------------------------------------------------------------
# DRIVE-05: the adversarial-crowding red line (mirror the low-trust corpus)
# ---------------------------------------------------------------------------


def test_flagged_goal_survives_token_cap():
    """Adversarial crowding: many high-confidence instincts + observations +
    contradictions + a low-trust snapshot (2 hints) + several non-flagged
    goals, all crowding well past the ~500-token cap, PLUS one flagged goal.
    The flagged want line is STILL present in the FINAL post-cap block — it was
    not the dropped trailing line (mirrors
    test_safe03_corpus_with_low_trust_snapshots' shape)."""
    signals = _crowding_signals()
    block = render.render_block(
        signals, snapshot=LOW_TRUST_SNAPSHOT, goals=[_flagged_goal()]
    )
    assert block is not None
    assert FLAG in block  # the flagged want survived the cap
    # Sanity: the block actually got crowded (tail lines WERE dropped).
    rendered_lines = block.split("\n")
    full_line_count = (
        2  # sentinel + framing
        + 1  # the flagged want
        + 3 + 3 + 3  # instincts/observations/contradictions slices
        + 1  # searches line
        + 1  # gut
        + 2  # trust hints
        + 3  # up to 3 non-flagged drive notes
    )
    assert len(rendered_lines) < full_line_count  # truncation happened
    assert_no_directive_language(block)


def test_flagged_goal_is_the_first_content_line_under_crowding():
    """Even under crowding, the flagged want is the FIRST content line and is
    never popped: it sits in the protected prefix, outside the pop range."""
    signals = _crowding_signals()
    block = render.render_block(
        signals, snapshot=LOW_TRUST_SNAPSHOT, goals=[_flagged_goal()]
    )
    lines = block.split("\n")
    assert lines[0].startswith("[anansi appraisal]")
    assert lines[2].startswith("- drive want:")
    assert FLAG in lines[2]


# ---------------------------------------------------------------------------
# DRIVE-05: top-of-block placement (before the first instinct)
# ---------------------------------------------------------------------------


def test_flagged_goal_renders_first():
    """The flagged drive-want line appears BEFORE the first instinct line."""
    signals = _rich_signals()
    block = render.render_block(signals, goals=[_flagged_goal()])
    lines = block.split("\n")
    want_idx = next(
        i for i, l in enumerate(lines) if l.startswith("- drive want:")
    )
    instinct_idx = next(
        i for i, l in enumerate(lines) if l.startswith("- instinct:")
    )
    assert want_idx < instinct_idx


# ---------------------------------------------------------------------------
# APPR-05 precedence: a flagged goal never MANUFACTURES a block
# ---------------------------------------------------------------------------


def test_successful_empty_signals_render_persisted_flagged_goal():
    """A successful empty mapping still surfaces a persisted flagged want."""
    empty = appraisal.parse_signals({}, 0.6)
    block = render.render_block(empty, goals=[_flagged_goal()])
    assert block is not None
    assert FLAG in block
    assert block.split("\n")[2].startswith("- drive want:")


def test_flagged_goal_renders_when_a_block_already_renders():
    """The symmetric positive: one real signal makes a block render, and the
    flagged want then appears in it."""
    signals = appraisal.parse_signals(
        {"gut_reaction": "steady focus"}, 0.6
    )
    block = render.render_block(signals, goals=[_flagged_goal()])
    assert block is not None
    assert FLAG in block


# ---------------------------------------------------------------------------
# Anti-complacency: a stalled push goal is NOT quietly downranked
# ---------------------------------------------------------------------------


def test_firm_stalled_goal_not_quietly_downranked():
    """A stalled goal with push_when_stalled=1 renders a VISIBLE
    under-support/drive-effect clause AND the neutral stalled-days read, kept
    separate (Pitfall #9) — not a quiet low-pressure line."""
    signals = _rich_signals()
    goal = _flagged_goal(stalled_days=12, push=True)
    block = render.render_block(signals, goals=[goal])
    want = [l for l in block.split("\n") if l.startswith("- drive want:")][0]
    assert "stalled 12 days" in want          # neutral read, intact
    assert "[under-support:" in want          # visible drive-effect clause
    assert_no_directive_language(block)


def test_support_style_firm_also_triggers_under_support():
    """support_style='firm' is the alternate authorization for a visible
    drive-effect clause (same anti-complacency surfacing)."""
    signals = _rich_signals()
    goal = _flagged_goal(stalled_days=4)
    goal["support_style"] = "firm"
    block = render.render_block(signals, goals=[goal])
    want = [l for l in block.split("\n") if l.startswith("- drive want:")][0]
    assert "stalled 4 days" in want
    assert "[under-support:" in want
    assert_no_directive_language(block)


# ---------------------------------------------------------------------------
# Drive-off: flagged wants are suppressed (goals=None) — byte-for-byte
# ---------------------------------------------------------------------------


def test_drive_off_suppresses_flagged_want():
    """When goals is None (drive off), NO flagged want line renders — the
    block is identical to a no-goals run."""
    signals = _rich_signals()
    with_goals = render.render_block(signals, goals=[_flagged_goal()])
    drive_off = render.render_block(signals, goals=None)
    assert "- drive want:" in with_goals
    assert "- drive want:" not in drive_off
    assert FLAG not in drive_off


# ---------------------------------------------------------------------------
# Full-hook integration (optional): the flagged want survives the real
# pre_llm_call path with a crowding fake-LLM payload.
# ---------------------------------------------------------------------------

plugin_llm = pytest.importorskip("agent.plugin_llm")

import anansi  # noqa: E402
from anansi import config, store  # noqa: E402


def _response(text, prompt_tokens=120, completion_tokens=80):
    return types.SimpleNamespace(
        choices=[
            types.SimpleNamespace(
                message=types.SimpleNamespace(content=text, role="assistant"),
                finish_reason="stop",
            )
        ],
        usage=types.SimpleNamespace(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
        model="fake-model",
    )


# A crowding model payload: the model does NOT echo the flagged goal at all —
# proving the never-omit guarantee reads the PERSISTED goal, not the model.
_CROWDING_MODEL_PAYLOAD = {
    "instincts": [
        {"kind": "caution", "intensity": 0.95,
         "reason": "a long reason that eats tokens " * 6, "confidence": 0.95}
        for _ in range(6)
    ],
    "salient_observations": [
        {"text": "a long observation that eats tokens " * 6, "confidence": 0.95}
        for _ in range(6)
    ],
    "contradiction_flags": [
        {"kind": "narrative", "text": "a long contradiction " * 6,
         "confidence": 0.9}
        for _ in range(6)
    ],
    "suggested_memory_searches": ["search one", "search two"],
    "goal_signals": [],  # model omits the flagged goal entirely
    "gut_reaction": "a long gut reaction " * 4,
}


def _cfg(**overrides):
    cfg = {
        "enabled": True,
        "drive_enabled": True,
        "confidence_threshold": 0.6,
        "deadline_seconds": 2.5,
        "history_chars": 4000,
        "model": None,
        "max_tokens": 700,
    }
    cfg.update(overrides)
    return cfg


def _hook_result(signals):
    return types.SimpleNamespace(
        signals=signals,
        outcome="ok",
        wall_ms=0,
        model="fake",
        tokens_in=0,
        tokens_out=0,
        error=None,
    )


def _run_hook(monkeypatch, db_path, *, cfg, signals, session_id):
    monkeypatch.setattr(store, "get_db_path", lambda: db_path)
    monkeypatch.setattr(config, "get_cfg", lambda: cfg)
    monkeypatch.setattr(appraisal, "should_skip", lambda *args: None)
    monkeypatch.setattr(appraisal, "normalize_message", lambda value: value)
    monkeypatch.setattr(
        appraisal, "run_appraisal", lambda **kwargs: _hook_result(signals)
    )
    anansi.register(
        types.SimpleNamespace(llm=object(), register_hook=lambda *args, **kwargs: None)
    )
    anansi._session_state.update({"session_id": None, "last_msg_norm": None})
    try:
        return anansi.pre_llm_call(session_id=session_id, user_message="status?")
    finally:
        anansi._ctx = None


def test_persisted_flagged_priorities_survive_empty_signal_full_hook(tmp_path, monkeypatch):
    """Persistence, domain selection, and rendering preserve every active want."""
    db_path = tmp_path / "anansi" / "state.db"
    assert store.ensure_db(db_path) is True
    flagged = [
        {
            "text": "protected priority %02d" % index,
            "status": "active",
            "flagged_priority": 1,
            "domain": "outside-domain",
        }
        for index in range(55)
    ]
    controls = [
        {
            "text": "ordinary out-of-domain control",
            "status": "active",
            "domain": "outside-domain",
        },
        {
            "text": "flagged candidate control",
            "status": "candidate",
            "flagged_priority": 1,
            "domain": "outside-domain",
        },
        {
            "text": "flagged retired control",
            "status": "backburner",
            "flagged_priority": 1,
            "domain": "outside-domain",
        },
    ]
    assert store.apply_deltas({"goals_add": flagged + controls}, db_path) is True

    snapshot = store.read_snapshot(db_path)
    assert snapshot is not None
    persisted = {goal["text"] for goal in snapshot["goals"]}
    assert {"protected priority %02d" % index for index in range(55)} <= persisted

    cfg = _cfg(drive_domains=["inside-domain"])
    output = _run_hook(
        monkeypatch, db_path, cfg=cfg, signals={}, session_id="empty-success"
    )
    assert isinstance(output, dict) and set(output) == {"context"}
    wants = [
        line for line in output["context"].split("\n")
        if line.startswith("- drive want:")
    ]
    assert len(wants) == 55
    assert all("I want progress on protected priority" in line for line in wants)
    assert "ordinary out-of-domain control" not in output["context"]
    assert "flagged candidate control" not in output["context"]
    assert "flagged retired control" not in output["context"]
    assert "withheld" not in output["context"].lower()

    assert _run_hook(
        monkeypatch, db_path, cfg=cfg, signals=None, session_id="appraisal-failure"
    ) is None

    ordinary_signals = {"gut_reaction": "steady focus"}
    drive_off = _run_hook(
        monkeypatch,
        db_path,
        cfg=_cfg(drive_enabled=False),
        signals=ordinary_signals,
        session_id="drive-off",
    )
    control_db = tmp_path / "control" / "state.db"
    assert store.ensure_db(control_db) is True
    no_goals = _run_hook(
        monkeypatch,
        control_db,
        cfg=_cfg(),
        signals=ordinary_signals,
        session_id="no-goals",
    )
    assert drive_off == no_goals


def test_neveromit_full_hook(tmp_path, monkeypatch):
    """End-to-end: a flagged goal in the tmp DB + a crowding fake-LLM payload
    that OMITS the goal — the returned {"context": block} STILL contains the
    flagged substring and the hook never raises."""
    db_path = tmp_path / "anansi" / "state.db"
    monkeypatch.setattr(store, "get_db_path", lambda: db_path)
    assert store.ensure_db()
    # Mint a flagged ACTIVE goal directly into the store.
    assert store.apply_deltas(
        {"goals_add": [{
            "text": FLAG,
            "status": "active",
            "flagged_priority": 1,
        }]},
        db_path=db_path,
    )

    state = {"cfg": _cfg()}
    monkeypatch.setattr(
        config, "get_cfg", lambda force_reload=False: state["cfg"]
    )

    def _caller(*, messages, model_override=None, **kwargs):
        return ("openai", model_override or "fake-model",
                _response(json.dumps(_CROWDING_MODEL_PAYLOAD)))

    def _ctx():
        llm = plugin_llm.make_plugin_llm_for_test(
            plugin_id="anansi",
            policy=plugin_llm._TrustPolicy(plugin_id="anansi"),
            sync_caller=_caller,
        )
        return types.SimpleNamespace(
            llm=llm, register_hook=lambda *a, **k: None
        )

    anansi.register(_ctx())
    anansi._session_state.update({"session_id": None, "last_msg_norm": None})
    try:
        out = anansi.pre_llm_call(
            session_id="s1", user_message="how is the migration going?"
        )
        assert isinstance(out, dict) and set(out) == {"context"}
        block = out["context"]
        assert FLAG in block  # never omitted, even though the model omitted it
        assert block.split("\n")[2].startswith("- drive want:")
        assert_no_directive_language(block)
    finally:
        appraisal._reset_executor_for_tests()
        anansi._ctx = None


def test_neveromit_full_hook_drive_off(tmp_path, monkeypatch):
    """Drive-off through the real hook: the flagged want is suppressed and a
    skipped:drive_disabled telemetry row is recorded (byte-for-byte invariant
    holds; flagged surfacing is gated by the drive kill switch)."""
    db_path = tmp_path / "anansi" / "state.db"
    monkeypatch.setattr(store, "get_db_path", lambda: db_path)
    assert store.ensure_db()
    assert store.apply_deltas(
        {"goals_add": [{
            "text": FLAG, "status": "active", "flagged_priority": 1,
        }]},
        db_path=db_path,
    )

    state = {"cfg": _cfg(drive_enabled=False)}
    monkeypatch.setattr(
        config, "get_cfg", lambda force_reload=False: state["cfg"]
    )

    def _caller(*, messages, model_override=None, **kwargs):
        return ("openai", model_override or "fake-model",
                _response(json.dumps(_CROWDING_MODEL_PAYLOAD)))

    def _ctx():
        llm = plugin_llm.make_plugin_llm_for_test(
            plugin_id="anansi",
            policy=plugin_llm._TrustPolicy(plugin_id="anansi"),
            sync_caller=_caller,
        )
        return types.SimpleNamespace(
            llm=llm, register_hook=lambda *a, **k: None
        )

    anansi.register(_ctx())
    anansi._session_state.update({"session_id": None, "last_msg_norm": None})
    try:
        out = anansi.pre_llm_call(
            session_id="s1", user_message="how is the migration going?"
        )
        # A block still renders (the crowding signals), but no flagged want.
        assert isinstance(out, dict)
        assert "- drive want:" not in out["context"]
        assert FLAG not in out["context"]
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            outcomes = [
                r[0] for r in con.execute("SELECT outcome FROM telemetry")
            ]
        finally:
            con.close()
        assert "skipped:drive_disabled" in outcomes
    finally:
        appraisal._reset_executor_for_tests()
        anansi._ctx = None
