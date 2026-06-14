# Plan 07-04 Summary

**Completed:** 2026-06-14
**Phase:** 7 — Drive / Accountability (FINAL plan — phase complete)
**Branch:** phase-7-drive-accountability

## What was built

The drive layer is now CONTAINED and ADJUSTABLE, closing the remaining DRIVE-06
surface and consolidating the fail-open matrix. 07-01 landed containment control
1 (the SEPARATE drive kill switch). This plan adds control 2 (a domain
WHITELIST — the drive surfaces goals only in user-named domains) and control 3
(a per-turn ENERGY/ATTENTION BUDGET — a hard cap on how many NON-flagged drive
lines surface), both resolving from `plugins.entries.anansi` config and both
fail-open to safe defaults. The never-omit invariant (DRIVE-05) takes precedence
over the budget: a flagged-priority want is EXEMPT and never dropped to satisfy
the cap. Every new drive path now has a documented row in the SAFE-02 fail-open
matrix, and the plugin README documents all three containment controls plus a
"Drive / accountability (Phase 7)" subsection.

## Key files

- `anansi/config.py` — `DEFAULT_DRIVE_DOMAINS=[]` (empty = unrestricted),
  `DEFAULT_DRIVE_ENERGY_BUDGET=3` (floor 0), `DEFAULT_DRIVE_PRESSURE="standard"`
  with `_DRIVE_PRESSURE_CHOICES={quiet,standard,firm}` (code-red excluded). New
  defensive coercers `_coerce_str_list` (non-list ⇒ default; junk members
  dropped/stringified) and `_coerce_choice` (out-of-vocabulary ⇒ default). All
  three keys added to `get_cfg` and documented in the module docstring's Drive
  block. `get_cfg` still never raises.
- `anansi/__init__.py` — `_filter_goals_by_domain` (whitelist applied to the
  persisted goals BEFORE they reach appraisal/render; empty whitelist = no
  filter; fail-open returns the unfiltered list) and `_filter_signals_by_goals`
  (when the whitelist is active, drops echoed `goal_signals` that don't relate
  to a surviving whitelisted goal, so an off-domain goal can't leak back through
  the model's echo). `render_block` is now called with `energy_budget=` (the
  per-turn cap; None when drive off).
- `anansi/render.py` — `render_block` gained an `energy_budget=None` param that
  caps the NON-flagged `- drive note:` lines at `min(3, budget)` (0 ⇒ no
  non-flagged note); flagged `- drive want:` lines were already emitted into the
  protected prefix and are NOT subject to the cap. Malformed budget falls back
  to the standing top-3 (fail-open).
- `anansi/tests/test_drive_config.py` — NEW (13 tests): domain/budget/pressure
  coercion (never raises), whitelist suppresses off-domain goals, empty
  whitelist unrestricted, whitelist filter fails open, budget caps non-flagged
  lines, budget=0 suppresses notes (block still renders), flagged want EXEMPT
  from budget=0, budget None/malformed fall back to top-3.
- `anansi/tests/test_failopen_matrix.py` — `_DEFAULTS` + `_cfg()` synced with
  the new drive keys; new `test_missing_config_malformed_drive_values_coerced`
  row; two new full-hook rows
  (`test_drive_whitelist_suppression_full_hook`,
  `test_drive_budget_cap_full_hook`); docstring matrix table gains six drive
  rows (kill-switch, locked-DB goal write [ref], malformed drive config,
  whitelist suppression, energy budget cap).
- `anansi/tests/test_telemetry_store.py` — the second `_DEFAULTS` equality
  assertion synced with the new keys (forced literal-contract update).
- `anansi/README.md` — a "Drive containment controls (DRIVE-06)" subsection
  documenting `drive_enabled` / `drive_domains` / `drive_energy_budget` (+
  `drive_pressure`) with defaults + semantics, the config YAML block updated,
  and a "Drive / accountability (Phase 7)" subsection (user-minted goals,
  grounded read-time velocity, first-person voice, the never-omit invariant).

## Decisions made

- **Whitelist suppresses BOTH the persisted goals AND the model's echoed
  signals.** Filtering only the persisted `goals=` slice left an off-domain goal
  able to surface as a `- drive note:` when the model echoed a `goal_signal` for
  it. `_filter_signals_by_goals` closes that leak: when the whitelist is active,
  a `goal_signal` only survives if it relates to a surviving whitelisted goal.
  Empty whitelist = no-op (default behaviour unchanged).
- **The energy budget is applied inside `render_block`, after the protected
  flagged prefix is assembled.** This is the only place that guarantees the
  flagged-want exemption structurally: the budget trims `non_flagged_signals`,
  never the protected prefix, so never-omit (DRIVE-05) beats the budget
  (DRIVE-06) by construction.
- **`drive_pressure` is read-only config for now.** The key is coerced and
  documented (vocabulary `quiet|standard|firm`, code-red excluded) but does not
  yet drive a behavioural branch in this increment — it is the adjustability
  surface a later panel/heartbeat increment tunes. Persisting it as a coerced,
  never-raising config value now keeps the containment surface complete.

## Deviations from plan

- **Added `_filter_signals_by_goals` to `__init__.py` (not in the plan's task-01
  action text).** The plan said to filter goals before render; in practice the
  model's echoed `goal_signals` also reach `render_block` and would have
  surfaced an off-domain goal as a drive note. The signal-level filter was
  necessary to satisfy the must-have "goals outside the whitelist are suppressed
  from goal-aware fields." Committed with task-02 (it was needed by the
  whitelist full-hook matrix row). No constraint weakened; fail-open preserved.
- **Synced a SECOND `_DEFAULTS` copy** in `test_telemetry_store.py::test_get_cfg_defaults_when_host_config_unavailable`
  (the plan named `test_failopen_matrix._DEFAULTS` explicitly and said "and any
  other _DEFAULTS copy"). A literal-contract update forced by the new config
  keys — no behavioural test weakened.
- **Two unrelated untracked planning dirs (`.planning/quick/003-*`, `.serena/`)
  were left out of both task commits** (staged files explicitly, not `-A`), so
  each commit is exactly its task's files.
- **15 net-new tests** (13 in test_drive_config.py + 2 full-hook matrix rows),
  suite 151 → 165, slightly above the plan's minimum.

## Notes for downstream

- **`drive_pressure` has no behavioural branch yet** — it is coerced/persisted
  config only. A future increment (heartbeat / desktop panel) reads it to tune
  firmness; the coercion + default are already in place and never raise.
- **Pressure COLUMNS are still not persisted** on the `goals` table
  (`support_style`/`push_when_stalled`/`stall_threshold_days`). 07-02/07-03's
  render+enrich path already consumes them defensively (copy-through); only the
  schema/`apply_deltas` write side is missing if a later plan wants per-goal
  persisted pressure.
- **The whitelist filters by the goal `domain` column** (also the per-goal mtime
  hint from 07-02). Goals with no domain are suppressed when a whitelist is
  active — by design (an unlisted/absent domain is outside the whitelist).
- **Containment is complete:** all three controls (kill switch, whitelist,
  budget) resolve from `plugins.entries.anansi`, fail open, and are documented in
  config.py + README. A desktop config panel to tune them live remains deferred
  (06-CONTEXT).

## Self-Check

| Must-have | Status |
|-----------|--------|
| `drive_domains`/`drive_energy_budget`/`drive_pressure` in get_cfg, coerced, never raise, documented | ✓ |
| Non-empty whitelist suppresses off-domain goals; empty whitelist unchanged — tested | ✓ |
| Energy budget caps non-flagged lines; flagged want EXEMPT (DRIVE-05 > DRIVE-06) — tested | ✓ |
| Fail-open matrix row for every new drive path; table updated | ✓ |
| `_DEFAULTS` (both copies) synced; malformed drive values coerce to defaults | ✓ |
| README documents all three controls + Drive subsection; every key in config.py; suite green; no new plugin module | ✓ |
| Two commits, one per task | ✓ |
