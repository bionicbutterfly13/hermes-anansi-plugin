"""Drive goal-aware appraisal tests (DRIVE-03 partial).

Proves: goal_signals parse+clamp+drop-below-threshold; the observational
"- drive note:" render line passes the SAFE-03/04 directive checker; the
build_context goals slice surfaces ACTIVE goals and EXCLUDES INERT
candidates; and second-person bait inside a goal field is still quoted /
neutralized (SAFE-04 sanitizer untouched).

NEW test file (not a plugin module) — the module inventory assertion is
unaffected. The "- drive note:" label is registered in conftest's
ALLOWED_LABEL_PREFIXES (07-01-03); "- drive want:" (first-person) lands in
07-03.
"""

from anansi import appraisal, render
from conftest import assert_no_directive_language


def test_goal_signal_parses_and_clamps():
    """An above-threshold goal_signals item survives with clamped confidence;
    a below-threshold one is dropped."""
    payload = {
        "goal_signals": [
            {"relates_to_goal": "ship the drive layer", "confidence": 1.7},  # clamp -> 1.0
            {"relates_to_goal": "tidy the backlog", "confidence": 0.2},      # < 0.6, dropped
            {"relates_to_goal": "", "confidence": 0.9},                       # empty, dropped
        ],
    }
    signals = appraisal.parse_signals(payload, 0.6)
    assert "goal_signals" in signals  # six-key shape always present
    gs = signals["goal_signals"]
    assert len(gs) == 1
    assert gs[0]["relates_to_goal"] == "ship the drive layer"
    assert gs[0]["confidence"] == 1.0  # clamped into [0, 1]


def test_goal_note_renders_observational():
    """render_block emits a '- drive note: relates to ...' line that passes
    the directive-language checker (the label is allowlisted, the line is
    observational/third-person)."""
    payload = {
        "goal_signals": [
            {"relates_to_goal": "ship the drive layer", "confidence": 0.9},
        ],
    }
    block = render.render_block(appraisal.parse_signals(payload, 0.6))
    assert block is not None
    note_lines = [l for l in block.split("\n") if l.startswith("- drive note:")]
    assert len(note_lines) == 1
    assert "relates to ship the drive layer" in note_lines[0]
    assert_no_directive_language(block)


def test_active_goal_surfaces_candidate_does_not():
    """build_context surfaces an ACTIVE goal to the model and EXCLUDES the
    INERT candidate; the parse->render pipeline then carries the drive note."""
    goals = [
        {"text": "ship the drive layer", "status": "active",
         "success_criteria": "phase 7 complete"},
        {"text": "maybe a dashboard", "status": "candidate",
         "success_criteria": "TBD"},
    ]
    snapshot = {
        "concerns": [], "contradictions": [], "trust_scores": {},
        "affect_summary": None,
    }
    context = appraisal.build_context(
        "how is the drive layer going?", [], snapshot, 4000, goals=goals
    )
    assert "ship the drive layer" in context       # active goal IS in context
    assert "maybe a dashboard" not in context       # INERT candidate EXCLUDED

    # The downstream parse->render pipeline carries the drive note when the
    # (fake) model reports a goal relation.
    payload = {
        "goal_signals": [
            {"relates_to_goal": "ship the drive layer", "confidence": 0.85},
        ],
    }
    block = render.render_block(appraisal.parse_signals(payload, 0.6))
    assert block is not None
    assert "- drive note: relates to ship the drive layer" in block


def test_drive_note_second_person_bait_still_quoted():
    """SAFE-04: a goal field carrying a bare second-person directive renders
    quoted/neutralized; assert_no_directive_language still passes (the
    sanitizer is untouched by the new line type)."""
    payload = {
        "goal_signals": [
            {"relates_to_goal": "you should ship by friday", "confidence": 0.9},
        ],
    }
    block = render.render_block(appraisal.parse_signals(payload, 0.6))
    assert block is not None
    # The bait survives only as quoted reported material.
    assert '"you should ship by friday"' in block
    assert_no_directive_language(block)
