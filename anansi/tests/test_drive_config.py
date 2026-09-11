"""DRIVE-06 containment config (Phase 7, plan 07-04): the domain whitelist +
per-turn energy/attention budget + the drive_pressure vocabulary.

These cover the two remaining containment controls (07-01 landed the SEPARATE
drive kill switch). Every coercer is defensive — get_cfg never raises on
malformed input and falls back to documented defaults. The whitelist
suppresses off-domain goals from the goal-aware fields; the energy budget caps
NON-flagged drive lines EXCEPT a flagged-priority want, which is never-omit and
EXEMPT from the budget (DRIVE-05 takes precedence over DRIVE-06).

This is a NEW test file (not a plugin module), so
test_scan_targets_are_the_plugin_modules is unaffected. Every test uses
build_context / render_block directly or a tmp DB — the real $HERMES_HOME is
never touched.
"""

import os
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import anansi
from anansi import appraisal, config, render, store


# ---------------------------------------------------------------------------
# Config coercion — get_cfg never raises on malformed drive values
# ---------------------------------------------------------------------------


def test_drive_domains_coerced(monkeypatch):
    """A non-list drive_domains -> []; a list with junk members -> only clean
    stripped strings survive; get_cfg never raises."""
    # non-list -> default []
    monkeypatch.setattr(config, "_load_host_entry", lambda: {"drive_domains": "proj-a"})
    assert config.get_cfg(force_reload=True)["drive_domains"] == []

    # a list with junk members -> empty/whitespace-only members are DROPPED;
    # other members are coerced to stripped strings (so 7 -> "7").
    monkeypatch.setattr(
        config,
        "_load_host_entry",
        lambda: {"drive_domains": ["proj-a", "  proj-b  ", "", "   ", 7]},
    )
    cfg = config.get_cfg(force_reload=True)
    assert cfg["drive_domains"] == ["proj-a", "proj-b", "7"]

    # absent key -> default []
    monkeypatch.setattr(config, "_load_host_entry", lambda: {})
    assert config.get_cfg(force_reload=True)["drive_domains"] == []


def test_drive_energy_budget_coerced(monkeypatch):
    """A non-int budget -> default; a negative -> floored at 0; get_cfg never
    raises."""
    monkeypatch.setattr(config, "_load_host_entry", lambda: {"drive_energy_budget": "lots"})
    assert config.get_cfg(force_reload=True)["drive_energy_budget"] == (
        config.DEFAULT_DRIVE_ENERGY_BUDGET
    )

    monkeypatch.setattr(config, "_load_host_entry", lambda: {"drive_energy_budget": -5})
    assert config.get_cfg(force_reload=True)["drive_energy_budget"] == 0

    monkeypatch.setattr(config, "_load_host_entry", lambda: {"drive_energy_budget": 1})
    assert config.get_cfg(force_reload=True)["drive_energy_budget"] == 1

    # absent -> default
    monkeypatch.setattr(config, "_load_host_entry", lambda: {})
    assert config.get_cfg(force_reload=True)["drive_energy_budget"] == (
        config.DEFAULT_DRIVE_ENERGY_BUDGET
    )


def test_drive_pressure_coerced(monkeypatch):
    """Invalid drive_pressure -> standard; quiet/standard/firm survive; code-red
    is rejected in Phase 7 and remains deferred."""
    for valid in ("quiet", "standard", "firm", "FIRM", "  Quiet "):
        monkeypatch.setattr(config, "_load_host_entry", lambda v=valid: {"drive_pressure": v})
        assert config.get_cfg(force_reload=True)["drive_pressure"] == valid.strip().lower()

    # code-red is EXCLUDED from Phase 7 -> coerces to the standard default
    monkeypatch.setattr(config, "_load_host_entry", lambda: {"drive_pressure": "code-red"})
    assert config.get_cfg(force_reload=True)["drive_pressure"] == "standard"

    # garbage / non-string -> default
    for junk in ("nonsense", 42, None, [], {}):
        monkeypatch.setattr(config, "_load_host_entry", lambda j=junk: {"drive_pressure": j})
        assert config.get_cfg(force_reload=True)["drive_pressure"] == "standard"


def test_config_degradations_are_shape_only_and_once_per_key(monkeypatch):
    """Every rejected or clamped provided key has one secret-safe descriptor."""
    rejected_secret = "sk-rejected-config-value-should-never-persist"
    entry = {
        "enabled": "maybe",
        "confidence_threshold": "not-a-number",
        "deadline_seconds": 999,
        "history_chars": -1,
        "max_tokens": 0,
        "reflection_enabled": None,
        "reflect_every_n_turns": 99,
        "reflect_max_tokens": 0,
        "reflect_deadline_seconds": 0.1,
        "drive_enabled": {},
        "drive_domains": ["allowed", "  "],
        "drive_energy_budget": -1,
        "drive_pressure": rejected_secret,
        "llm": {"model": "  "},
    }
    monkeypatch.setattr(config, "_load_host_entry", lambda: entry)

    config.get_cfg(force_reload=True)
    degradations = config.get_degradations()

    assert {record[0] for record in degradations} == {
        "enabled", "confidence_threshold", "deadline_seconds", "history_chars",
        "max_tokens", "reflection_enabled", "reflect_every_n_turns",
        "reflect_max_tokens", "reflect_deadline_seconds", "drive_enabled",
        "drive_domains", "drive_energy_budget", "drive_pressure", "model",
    }
    assert len(degradations) == 14
    assert all(len(record) == 3 for record in degradations)
    assert all(rejected_secret not in repr(record) for record in degradations)
    assert all(record[1].startswith("<") for record in degradations)


def test_config_degradations_ignore_normalization_and_cached_reads(monkeypatch):
    """Valid normalization is not degradation, and cache hits do not duplicate it."""
    entry = {
        "enabled": " YES ",
        "confidence_threshold": "0.75",
        "deadline_seconds": " 8 ",
        "history_chars": "4000",
        "max_tokens": "700",
        "reflection_enabled": "off",
        "reflect_every_n_turns": "5",
        "reflect_max_tokens": "700",
        "reflect_deadline_seconds": "8.0",
        "drive_enabled": 1,
        "drive_domains": ["  project-a  ", 7],
        "drive_energy_budget": "3",
        "drive_pressure": " FIRM ",
        "llm": {"model": " model-name "},
    }
    monkeypatch.setattr(config, "_load_host_entry", lambda: entry)

    first = config.get_cfg(force_reload=True)
    first_degradations = config.get_degradations()
    second = config.get_cfg()

    assert first == second
    assert first_degradations == []
    assert config.get_degradations() == []
    config.reset_cache()
    assert config.get_degradations() == []


# ---------------------------------------------------------------------------
# Domain whitelist — off-domain goals do not surface (build_context + render)
# ---------------------------------------------------------------------------


def _goals():
    """Three goals across two domains plus a no-domain goal, all active."""
    return [
        {"text": "ship proj-a feature", "status": "active",
         "success_criteria": "done", "domain": "proj-a"},
        {"text": "ship proj-b feature", "status": "active",
         "success_criteria": "done", "domain": "proj-b"},
        {"text": "tidy the desk", "status": "active",
         "success_criteria": "tidy", "domain": None},
    ]


def _filtered(goals, drive_domains):
    """Run the plugin's domain filter exactly as pre_llm_call does."""
    import anansi

    return anansi._filter_goals_by_domain(goals, drive_domains)


def test_whitelist_suppresses_offdomain_goals():
    """drive_domains=['proj-a']: the proj-a goal surfaces; the proj-b goal and
    the no-domain goal do NOT — assert via the build_context goals slice."""
    kept = _filtered(_goals(), ["proj-a"])
    ctx = appraisal.build_context(
        "how is proj-a going?", [], {"goals": kept}, 4000, goals=kept
    )
    assert "ship proj-a feature" in ctx
    assert "ship proj-b feature" not in ctx
    assert "tidy the desk" not in ctx


def test_empty_whitelist_is_unrestricted():
    """drive_domains=[] -> all goals surface (07-01..03 behaviour unchanged)."""
    kept = _filtered(_goals(), [])
    ctx = appraisal.build_context(
        "status?", [], {"goals": kept}, 4000, goals=kept
    )
    assert "ship proj-a feature" in ctx
    assert "ship proj-b feature" in ctx
    assert "tidy the desk" in ctx


def test_whitelist_filter_fails_open_returns_unfiltered():
    """A filter failure falls back to the UNFILTERED goals, never crashes and
    never silently drops everything (fail-open law)."""
    import anansi

    class _Boom:
        # iterating membership raises -> the filter must fall back, not crash.
        def __iter__(self):
            raise RuntimeError("whitelist iteration exploded")

    out = anansi._filter_goals_by_domain(_goals(), _Boom())
    assert out == _goals()  # unfiltered fallback, no raise


# ---------------------------------------------------------------------------
# Energy budget — caps NON-flagged drive lines; flagged is EXEMPT
# ---------------------------------------------------------------------------


def _signals_with_n_goal_notes(n):
    """A render-ready signal dict with one observation (so a block renders) and
    n non-flagged goal_signals."""
    return {
        "instincts": [],
        "salient_observations": [
            {"text": "the topic recurs across sessions", "confidence": 0.9}
        ],
        "contradiction_flags": [],
        "suggested_memory_searches": [],
        "goal_signals": [
            {"relates_to_goal": "goal number %d" % i, "confidence": 0.8}
            for i in range(n)
        ],
        "gut_reaction": "",
    }


def test_budget_caps_nonflagged_lines():
    """drive_energy_budget=1 with 3 non-flagged drive goals -> at most 1
    non-flagged `- drive note:` line surfaces."""
    block = render.render_block(
        _signals_with_n_goal_notes(3), energy_budget=1
    )
    assert block is not None
    note_lines = [ln for ln in block.split("\n") if ln.startswith("- drive note:")]
    assert len(note_lines) == 1


def test_budget_zero_suppresses_all_nonflagged_notes():
    """drive_energy_budget=0 -> no non-flagged drive note surfaces, but the
    block still renders (the observation carries it)."""
    block = render.render_block(
        _signals_with_n_goal_notes(2), energy_budget=0
    )
    assert block is not None
    note_lines = [ln for ln in block.split("\n") if ln.startswith("- drive note:")]
    assert note_lines == []
    assert "- observation:" in block  # the block still renders from real signals


def test_flagged_want_exempt_from_budget():
    """drive_energy_budget=0 with one flagged-priority goal -> the flagged
    `- drive want:` line STILL appears (DRIVE-05 precedence over DRIVE-06:
    never-omit beats the budget). The persisted flagged goal rides through the
    `goals=` slice and is never trimmed by the budget."""
    flagged_goal = {
        "text": "land the launch", "status": "active",
        "flagged_priority": 1, "domain": "launch",
        "momentum": {"momentum": "stalled", "stalled_days": 5, "salience": 1.0},
    }
    block = render.render_block(
        _signals_with_n_goal_notes(2),
        goals=[flagged_goal],
        energy_budget=0,
    )
    assert block is not None
    want_lines = [ln for ln in block.split("\n") if ln.startswith("- drive want:")]
    assert len(want_lines) == 1
    assert "land the launch" in want_lines[0]
    # And the budget still suppressed the NON-flagged notes.
    note_lines = [ln for ln in block.split("\n") if ln.startswith("- drive note:")]
    assert note_lines == []


def test_budget_none_leaves_standing_top3():
    """energy_budget=None (drive off / no cap) -> the standing top-3 ceiling
    applies, unchanged from 07-01..03."""
    block = render.render_block(_signals_with_n_goal_notes(5), energy_budget=None)
    assert block is not None
    note_lines = [ln for ln in block.split("\n") if ln.startswith("- drive note:")]
    assert len(note_lines) == 3


def test_budget_malformed_falls_back_to_top3():
    """A malformed (non-int) budget falls back to the standing top-3, never
    raises (fail-open)."""
    block = render.render_block(_signals_with_n_goal_notes(5), energy_budget="lots")
    assert block is not None
    note_lines = [ln for ln in block.split("\n") if ln.startswith("- drive note:")]
    assert len(note_lines) == 3


# ---------------------------------------------------------------------------
# Global pressure policy — full-hook drive effects stay bounded and fail-open
# ---------------------------------------------------------------------------


def _run_pressure_hook(monkeypatch, pressure, drive_enabled=True):
    """Exercise the hook with deterministic appraisal output and no live I/O."""
    signals = _signals_with_n_goal_notes(3)
    result = SimpleNamespace(
        signals=signals, outcome="ok", wall_ms=0, model="fake", tokens_in=0,
        tokens_out=0, error=None,
    )
    monkeypatch.setattr(config, "get_cfg", lambda: {
        "enabled": True,
        "drive_enabled": drive_enabled,
        "drive_domains": [],
        "drive_energy_budget": 3,
        "drive_pressure": pressure,
    })
    monkeypatch.setattr(store, "read_snapshot", lambda: {"goals": []})
    monkeypatch.setattr(store, "record_telemetry", lambda *a, **kw: None)
    monkeypatch.setattr(appraisal, "should_skip", lambda *a: None)
    monkeypatch.setattr(appraisal, "normalize_message", lambda value: value)
    monkeypatch.setattr(appraisal, "run_appraisal", lambda **kwargs: result)
    anansi.register(SimpleNamespace(llm=object(), register_hook=lambda *a, **k: None))
    anansi._session_state.update({"session_id": None, "last_msg_norm": None})
    try:
        return anansi.pre_llm_call(session_id="pressure", user_message="status?")
    finally:
        anansi._ctx = None


def _run_persisted_pressure_hook(
    tmp_path, monkeypatch, pressure, goal_specs, goal_signals, energy_budget=3
):
    """Run a real temporary store through the hook with deterministic signals.

    ``goal_specs`` supplies ``text``, pressure fields, confidence, and an
    actual file age.  The hook reads its snapshot itself; only the appraisal
    result is faked, so goal ordering still travels through apply_deltas,
    read_snapshot, read-time momentum, enrichment, and rendering.
    """
    db = tmp_path / "state.db"
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    now = datetime.now(timezone.utc)
    goals = []
    for index, spec in enumerate(goal_specs):
        domain = "goal-%d.txt" % index
        path = repo / domain
        path.write_text(spec["text"], encoding="utf-8")
        aged_at = (now - timedelta(days=spec["age_days"])).timestamp()
        os.utime(path, (aged_at, aged_at))
        goal = dict(spec)
        goal.pop("age_days")
        goal.pop("confidence")
        goal["status"] = "active"
        goal["domain"] = domain
        goals.append(goal)

    assert store.ensure_db(db) is True
    assert store.apply_deltas({"goals_add": goals}, db) is True
    monkeypatch.setattr(store, "get_db_path", lambda: db)
    monkeypatch.setattr(store, "_repo_root", lambda: repo)
    monkeypatch.setattr(config, "get_cfg", lambda: {
        "enabled": True,
        "drive_enabled": True,
        "drive_domains": [],
        "drive_energy_budget": energy_budget,
        "drive_pressure": pressure,
    })
    result = SimpleNamespace(
        signals={
            "instincts": [],
            "salient_observations": [{"text": "same state", "confidence": 0.9}],
            "contradiction_flags": [],
            "suggested_memory_searches": [],
            "goal_signals": goal_signals,
            "gut_reaction": "",
        },
        outcome="ok", wall_ms=0, model="fake", tokens_in=0,
        tokens_out=0, error=None,
    )
    monkeypatch.setattr(store, "record_telemetry", lambda *a, **kw: None)
    monkeypatch.setattr(appraisal, "should_skip", lambda *a: None)
    monkeypatch.setattr(appraisal, "normalize_message", lambda value: value)
    monkeypatch.setattr(appraisal, "run_appraisal", lambda **kwargs: result)
    anansi.register(SimpleNamespace(llm=object(), register_hook=lambda *a, **k: None))
    anansi._session_state.update({"session_id": None, "last_msg_norm": None})
    try:
        output = anansi.pre_llm_call(session_id="persisted", user_message="status?")
        assert output is not None
        return output["context"]
    finally:
        anansi._ctx = None


def _drive_note_goals(block):
    """Return the persisted goal names in their rendered note order."""
    return [
        line.split("relates to ", 1)[1].split(" — ", 1)[0]
        for line in block.split("\n")
        if line.startswith("- drive note:")
    ]


def test_pressure_full_hook_is_bounded_and_invalid_uses_standard(monkeypatch):
    """Quiet, standard, and firm use only bounded non-flagged drive effects;
    an invalid value is the byte-compatible standard fallback."""
    outputs = {
        pressure: _run_pressure_hook(monkeypatch, pressure)["context"]
        for pressure in ("quiet", "standard", "firm", "not-a-pressure")
    }
    note_counts = {
        pressure: len([
            line for line in output.split("\n")
            if line.startswith("- drive note:")
        ])
        for pressure, output in outputs.items()
    }
    assert note_counts == {
        "quiet": 1,
        "standard": 3,
        "firm": 3,
        "not-a-pressure": 3,
    }
    assert outputs["quiet"] != outputs["standard"]
    assert outputs["not-a-pressure"] == outputs["standard"]
    assert outputs["standard"] == render.render_block(
        _signals_with_n_goal_notes(3), goals=[], energy_budget=3
    )



def test_firm_full_hook_orders_authorized_notes_by_actual_stalled_age(tmp_path, monkeypatch):
    """Firm makes a visible, bounded ordering choice from persisted ages.

    Confidence prefers ``younger authorized`` in standard mode, while the
    firm-only authorized cohort must put ``older authorized`` first.  Equal
    ages keep their input order, and the three-note budget remains intact.
    """
    goal_specs = [
        {"text": "younger authorized", "age_days": 4, "confidence": 0.99,
         "support_style": "firm", "push_when_stalled": 1, "stall_threshold_days": 3},
        {"text": "older authorized", "age_days": 8, "confidence": 0.10,
         "support_style": "firm", "push_when_stalled": 1, "stall_threshold_days": 3},
        {"text": "equal age first", "age_days": 5, "confidence": 0.50,
         "support_style": "firm", "push_when_stalled": 1, "stall_threshold_days": 3},
        {"text": "equal age second", "age_days": 5, "confidence": 0.50,
         "support_style": "firm", "push_when_stalled": 1, "stall_threshold_days": 3},
        {"text": "unauthorized high confidence", "age_days": 10, "confidence": 1.0},
        {"text": "below threshold", "age_days": 12, "confidence": 0.98,
         "support_style": "firm", "push_when_stalled": 1, "stall_threshold_days": 13},
    ]
    goal_signals = [
        {"relates_to_goal": spec["text"], "confidence": spec["confidence"]}
        for spec in goal_specs
    ]

    standard = _run_persisted_pressure_hook(
        tmp_path / "standard", monkeypatch, "standard", goal_specs, goal_signals
    )
    firm = _run_persisted_pressure_hook(
        tmp_path / "firm", monkeypatch, "firm", goal_specs, goal_signals
    )

    assert _drive_note_goals(standard) == [
        "younger authorized", "equal age first", "equal age second"
    ]
    assert _drive_note_goals(firm) == [
        "older authorized", "equal age first", "equal age second"
    ]
    assert firm != standard
    assert len(_drive_note_goals(firm)) == 3


def test_firm_keeps_unauthorized_and_below_threshold_notes_on_existing_order(tmp_path, monkeypatch):
    """Firm promotes only persisted, threshold-satisfied authorization."""
    goal_specs = [
        {"text": "authorized younger", "age_days": 4, "confidence": 0.1,
         "support_style": "firm", "push_when_stalled": 1, "stall_threshold_days": 3},
        {"text": "unauthorized older", "age_days": 10, "confidence": 0.99},
        {"text": "below threshold older", "age_days": 12, "confidence": 0.98,
         "support_style": "firm", "push_when_stalled": 1, "stall_threshold_days": 13},
    ]
    goal_signals = [
        {"relates_to_goal": spec["text"], "confidence": spec["confidence"]}
        for spec in goal_specs
    ]

    firm = _run_persisted_pressure_hook(
        tmp_path, monkeypatch, "firm", goal_specs, goal_signals
    )
    assert _drive_note_goals(firm) == [
        "authorized younger", "unauthorized older", "below threshold older"
    ]


def test_pressure_drive_off_preserves_no_goals_appraisal_block(monkeypatch):
    """Drive-off strips every drive field and preserves the ordinary appraisal
    block byte-for-byte against the equivalent no-goals render."""
    out = _run_pressure_hook(monkeypatch, "firm", drive_enabled=False)
    expected = render.render_block({
        "instincts": [],
        "salient_observations": [
            {"text": "the topic recurs across sessions", "confidence": 0.9}
        ],
        "contradiction_flags": [],
        "suggested_memory_searches": [],
        "goal_signals": [],
        "gut_reaction": "",
    })
    assert out == {"context": expected}
    assert "- drive " not in out["context"]
