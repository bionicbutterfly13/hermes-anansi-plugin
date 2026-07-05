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

from conftest import assert_no_directive_language

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
# G3: global drive_pressure modulates drive-note VERBOSITY (quiet<standard<firm)
# ---------------------------------------------------------------------------


def _note_count(block):
    return len([ln for ln in block.split("\n") if ln.startswith("- drive note:")])


def test_pressure_levels_are_distinguishable():
    """On IDENTICAL state (5 non-flagged goal notes, no energy cap), each
    drive_pressure level renders a distinguishable number of drive notes:
    quiet<standard<firm (SC-003)."""
    sig = _signals_with_n_goal_notes(5)
    quiet = render.render_block(sig, energy_budget=None, pressure="quiet")
    standard = render.render_block(sig, energy_budget=None, pressure="standard")
    firm = render.render_block(sig, energy_budget=None, pressure="firm")
    assert _note_count(quiet) == 1
    assert _note_count(standard) == 3
    assert _note_count(firm) == 5
    # strictly increasing + all three blocks differ
    assert quiet != standard != firm and quiet != firm
    for block in (quiet, standard, firm):
        assert_no_directive_language(block)


def test_pressure_standard_is_byte_identical_to_default():
    """pressure='standard' (and an unknown pressure) reproduces the pre-G3
    default render byte-for-byte — standard behaviour is unchanged."""
    sig = _signals_with_n_goal_notes(5)
    default = render.render_block(sig, energy_budget=None)  # no pressure arg
    assert render.render_block(sig, energy_budget=None, pressure="standard") == default
    assert render.render_block(sig, energy_budget=None, pressure="StAnDaRd ") == default
    # malformed / unknown pressure falls back to standard, never raises
    assert render.render_block(sig, energy_budget=None, pressure="nonsense") == default
    assert render.render_block(sig, energy_budget=None, pressure=42) == default
    assert render.render_block(sig, energy_budget=None, pressure=None) == default


def test_energy_budget_still_caps_pressure():
    """The energy budget is a HARD cap that clamps the pressure ceiling: firm
    (base 5) with budget=2 surfaces 2 notes (min(5, 2)); flagged wants remain
    exempt elsewhere."""
    sig = _signals_with_n_goal_notes(5)
    firm_capped = render.render_block(sig, energy_budget=2, pressure="firm")
    assert _note_count(firm_capped) == 2
    quiet_under_budget = render.render_block(sig, energy_budget=3, pressure="quiet")
    assert _note_count(quiet_under_budget) == 1  # quiet ceiling (1) < budget (3)


# ---------------------------------------------------------------------------
# G7: config-degradation detection (audit #5) — legible + secret-safe
# ---------------------------------------------------------------------------


def test_config_degradations_flags_rejected_and_clamped(monkeypatch):
    """Values the user provided but that were coerced away (rejected or clamped)
    are reported by get_degradations() as (key, secret-safe shape)."""
    monkeypatch.setattr(
        config,
        "_load_host_entry",
        lambda: {
            "drive_pressure": "code-red",   # rejected choice -> standard
            "drive_energy_budget": "lots",  # unparseable int -> default
            "drive_domains": "proj-a",      # non-list -> []
            "confidence_threshold": 5.0,    # clamped 5.0 -> 1.0
        },
    )
    config.get_cfg(force_reload=True)
    degraded = dict(config.get_degradations())
    assert set(degraded) == {
        "drive_pressure",
        "drive_energy_budget",
        "drive_domains",
        "confidence_threshold",
    }
    # shape only, never the literal value
    assert degraded["drive_pressure"] == "<str len=8>"  # 'code-red'
    assert degraded["drive_domains"] == "<str len=6>"  # 'proj-a'
    assert "code-red" not in " ".join(degraded.values())


def test_config_degradation_never_leaks_a_secret(monkeypatch):
    """A mistyped credential in a config field is NEVER quoted — only its length
    shape is recorded (secret-safety)."""
    secret = "sk-supersecret-DEADBEEF-42"
    monkeypatch.setattr(
        config, "_load_host_entry", lambda: {"drive_energy_budget": secret}
    )
    config.get_cfg(force_reload=True)
    degraded = dict(config.get_degradations())
    assert "drive_energy_budget" in degraded
    assert secret not in degraded["drive_energy_budget"]
    assert degraded["drive_energy_budget"] == "<str len=%d>" % len(secret)


def test_valid_config_has_no_degradations(monkeypatch):
    """Valid AND legitimately-normalized values (case, whitespace, string ints)
    produce ZERO degradations — no false positives."""
    monkeypatch.setattr(
        config,
        "_load_host_entry",
        lambda: {
            "drive_pressure": "FIRM",       # normalized, not degraded
            "drive_energy_budget": 2,
            "drive_domains": ["proj-a"],
            "confidence_threshold": 0.7,
            "history_chars": "4000",        # string int -> same value
        },
    )
    config.get_cfg(force_reload=True)
    assert config.get_degradations() == []


def test_get_degradations_never_raises_and_defaults_empty(monkeypatch):
    """No host entry -> valid defaults -> no degradations; get_degradations is
    always a list."""
    monkeypatch.setattr(config, "_load_host_entry", lambda: None)
    config.get_cfg(force_reload=True)
    assert config.get_degradations() == []
