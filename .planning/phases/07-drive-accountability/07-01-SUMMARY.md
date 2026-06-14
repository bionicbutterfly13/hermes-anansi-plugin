# Plan 07-01 Summary

**Completed:** 2026-06-14
**Phase:** 7 — Drive / Accountability
**Branch:** phase-7-drive-accountability

## What was built

The foundation tracer bullet for the drive layer: a user-minted goal now persists in the existing anansi SQLite surface (schema v4, `goals` table — no second DB), reaches the appraisal model as untrusted reference state via `build_context`, and comes back out as one observational `- drive note:` line in the rendered `[anansi appraisal]` block — in the same turn, through the existing `pre_llm_call` path, with no new hook and no new plugin module. The SEPARATE drive kill switch (`drive_enabled`, default True) lands too: it gates the drive contribution AFTER the appraisal `enabled` check without early-returning, so drive-off makes every goal-aware field vanish while the appraisal block stays byte-for-byte unchanged, recording a non-failure `skipped:drive_disabled` telemetry row.

This plan ships only the BASIC goal-aware field (`relates_to_goal` + `confidence`). Velocity-aware fields (`stalled_days`, momentum) are 07-02; the first-person `- drive want:` voice and never-omit invariant are 07-03.

## Key files

- `anansi/store.py` — `SCHEMA_VERSION` 3→4; new `goals` CREATE in `_SCHEMA_DDL` (id/text/status CHECK active|queued|backburner|candidate/success_criteria/flagged_priority/domain/created_at/updated_at); `goals` added to `_TABLES`, `CAPS` (50), the cap-eviction tuple, and `read_snapshot`'s returned dict; three MECHANICAL `apply_deltas` branches `goals_add`/`goals_update`/`goals_status` (goals_add defaults status to `candidate` — the INERT agent-nominated default).
- `anansi/config.py` — `DEFAULT_DRIVE_ENABLED = True`; `drive_enabled` coerced via `_coerce_bool` in `get_cfg` (never raises); documented under a new "Drive keys (DRIVE-06, Phase 7)" docstring block stating it is SEPARATE from `enabled`.
- `anansi/__init__.py` — `drive_on` flag set after the `enabled` kill switch (no early-return); once-per-eligible-turn `skipped:drive_disabled` telemetry when off; goals pulled from the snapshot and threaded into `run_appraisal` when on (None when off); render-path goal_signals stripped when off so the drive-off block is byte-for-byte identical to a no-goals run.
- `anansi/appraisal.py` — `goal_signals` array in `APPRAISAL_JSON_SCHEMA`; `APPRAISAL_PROMPT` describes goal_signals as OBSERVATIONS ONLY; `parse_signals` coerces/clamps/drops-below-threshold goal_signals (six-key shape now); `build_context` injects a compact `goals` slice (NON-candidate goals only) within the 12000-char cap, omitting the key entirely when goals is None/empty.
- `anansi/render.py` — `- drive note: relates to <sanitized> (confidence <fmt>)` line (top-3, after contradictions, before searches), sanitized via `_sanitize_text`; third-person observational.
- `anansi/tests/conftest.py` — `- drive note:` registered in `ALLOWED_LABEL_PREFIXES` (with forward-compat note for `- drive want:` in 07-03).
- New tests: `test_drive_store.py` (7), `test_drive_appraisal.py` (4); new rows in `test_failopen_matrix.py` (2).

## Decisions made

- **Drive-off suppression is belt-and-suspenders.** build_context omits the goals slice when drive is off (a faithful model then returns no goal_signals), AND `__init__.py` strips any `goal_signals` from the parsed result before render. This makes the byte-for-byte invariant hold regardless of what the (possibly fake/adversarial) model returns, not just for a faithful model.
- **`skipped:drive_disabled` is recorded once per ELIGIBLE turn**, at the point appraisal actually runs (after the throttle/ctx gates) — not at the early `enabled`/throttle gates — so it only fires on turns that would otherwise produce drive output.
- **`run_appraisal`/`build_context` gained a `goals=None` parameter in task 07-01-02** (as a no-op) so the `goals=goals` call site in `__init__.py` stays valid and that commit is green; the actual injection wiring lands in task 07-01-03. Each commit is independently green.

## Deviations from plan

- **Three pre-existing tests required necessary literal updates caused directly by the schema/config changes** (not in the plan's task file list, but unavoidable downstream of the changes the plan mandates):
  1. `test_reflection_store.py::test_v2_db_quarantined_and_recreated_at_v3` — hard-coded `SCHEMA_VERSION == 3` and `row == ("3",)`. Updated to `== 4` / `str(store.SCHEMA_VERSION)`. The test's intent (stale-schema DB quarantine-recreates at the CURRENT version) is preserved; only the version literals changed.
  2. `test_telemetry_store.py::test_get_cfg_defaults_when_host_config_unavailable` — asserts the full default cfg dict by equality; added `"drive_enabled": True` (the plan explicitly required the analogous `_DEFAULTS` update in test_failopen_matrix.py).
  3. `test_appraisal.py::test_vocabulary_gating_and_clamping` — asserts the exact empty parse_signals shape; added `"goal_signals": []` (the new six-key shape).
  These are all literal-contract updates forced by the plan's own schema-version bump and new config/parse fields — no behavioral test was weakened. `_SECOND_PERSON_DIRECTIVE_RE`, `DIRECTIVE_PATTERNS`, and the SAFE-04 negative controls are UNTOUCHED.

## Notes for downstream (07-02 / 07-03)

- The `goals` table already carries `flagged_priority` and `domain` columns (written now, read later) — 07-03's never-omit invariant and 07-04's domain whitelist do not need another schema bump.
- `goals_status` is the promotion path (candidate→active); 07-03 can promote an INERT candidate the user confirms.
- The `- drive note:` line is THIRD-PERSON. 07-03 adds the first-person `- drive want:` label — register it in `conftest.ALLOWED_LABEL_PREFIXES` (the forward-compat comment slot is already there) and keep `_SECOND_PERSON_DIRECTIVE_RE`/`DIRECTIVE_PATTERNS` untouched (first-person carve-out only).
- Velocity (07-02) must be computed at read time in the pre_llm_call path (Pitfall #3), NOT behind the reflection debounce; git/file ground truth via stdlib reads only (Pitfall #2 — no subprocess).
- The drive-off byte-for-byte invariant test (`test_drive_disabled_appraisal_unchanged`) is the regression guard for success criterion 4 — keep it green as velocity/voice fields are added.
