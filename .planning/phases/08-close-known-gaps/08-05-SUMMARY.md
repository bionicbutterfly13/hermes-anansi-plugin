---
phase: 08-close-known-gaps
plan: "05"
subsystem: configuration-and-fail-open-telemetry
tags: [python, config, fail-open, telemetry, sqlite, tdd]
requires:
  - phase: 08-04
    provides: canonical offline regression gate and live-evidence boundary
provides:
  - non-raising native non-finite integer config coercion
  - per-session shape-only telemetry for all five integer configuration keys
affects: [phase-8-verification, config, session-start-telemetry]
actuals:
  tokens: 1730
  tasks: 1
  commits: 2
  plan_head_before: 50eed75b9cd6470c52c9ecea1202d7e8c6db1bbd
tech-stack:
  added: []
  patterns:
    - integer coercion catches every native conversion exception while preserving finite clamping
    - config degradation descriptors remain shape-only across cached reads and session reloads
key-files:
  created: []
  modified:
    - anansi/config.py
    - anansi/tests/test_drive_config.py
    - anansi/tests/test_failopen_matrix.py
    - CHANGELOG.md
key-decisions:
  - "Catch OverflowError only at the existing _coerce_int conversion boundary."
  - "Keep non-finite input out of cached configuration state and persisted telemetry; retain only the existing shape and applied default."
requirements-completed:
  - REQ-001-close-known-gaps-fr-004
  - REQ-001-close-known-gaps-fr-005
  - REQ-001-close-known-gaps-fr-012
coverage:
  - id: D1
    description: Native positive infinity, negative infinity, and NaN for all five integer configuration keys resolve to documented defaults while finite strings and bounds retain their behavior.
    requirement: REQ-001-close-known-gaps-fr-004
    verification:
      - kind: unit
        ref: anansi/tests/test_drive_config.py#test_native_nonfinite_integer_values_degrade_to_defaults
        status: pass
      - kind: unit
        ref: anansi/tests/test_drive_config.py#test_integer_config_strings_and_bounds_remain_unchanged
        status: pass
    human_judgment: false
  - id: D2
    description: Cached reads do not reload or duplicate degradation records, and each real session reload persists exactly five shape-only integer degradation rows.
    requirement: REQ-001-close-known-gaps-fr-005
    verification:
      - kind: unit
        ref: anansi/tests/test_drive_config.py#test_nonfinite_integer_degradations_are_cached_then_reloaded
        status: pass
      - kind: integration
        ref: anansi/tests/test_failopen_matrix.py#test_session_start_records_nonfinite_integer_degradations_per_reload
        status: pass
    human_judgment: false
  - id: D3
    description: The canonical offline suite retains existing fail-open, never-omit, pressure, timing, consent, and live-boundary regressions.
    requirement: REQ-001-close-known-gaps-fr-012
    verification:
      - kind: integration
        ref: ./scripts/test.sh
        status: pass
    human_judgment: false
duration: 1 min
completed: 2026-09-11
status: complete
---

# Phase 08 Plan 05: Non-Finite Integer Configuration Summary

**Native infinity and NaN now fail open across all five integer configuration keys, with documented defaults and secret-safe per-session degradation telemetry.**

## Performance

- **Duration:** 1 min between RED and GREEN commits.
- **Started:** 2026-09-11T11:56:55-04:00
- **Completed:** 2026-09-11T11:57:46-04:00
- **Tasks:** 1 completed
- **Files modified:** 4

## Accomplishments

- Added table-driven coverage for positive infinity, negative infinity, NaN, finite numeric strings, bounds, cache reuse, and cache reset across `history_chars`, `max_tokens`, `reflect_every_n_turns`, `reflect_max_tokens`, and `drive_energy_budget`.
- Made `_coerce_int` catch the native `OverflowError` raised by `int(inf)` and `int(-inf)`, preserving the existing default and clamp behavior.
- Proved real `on_session_start` reloads write exactly five shape-only `config_degraded` rows per session, with no raw non-finite representation.

## TDD Evidence

- **RED:** `./scripts/test.sh anansi/tests/test_drive_config.py anansi/tests/test_failopen_matrix.py -x` failed in `test_native_nonfinite_integer_values_degrade_to_defaults` on the target behavior: `OverflowError: cannot convert float infinity to integer` from `_coerce_int`.
- **GREEN:** the same focused command passed, `52 passed in 1.71s`.
- **Canonical gate:** `./scripts/test.sh` passed, `199 passed in 5.37s`.
- **REFACTOR:** none needed; the production change is one exception-boundary addition.

## Task Commits

1. **Task 1 RED: cover non-finite integer config reloads** - `3ce98af` (`test`)
2. **Task 1 GREEN: handle non-finite integer config values** - `29d2892` (`fix`)

**Plan metadata:** skipped intentionally because `.planning/config.json` sets `planning.commit_docs` to `false`; this summary remains uncommitted for the orchestrator.

## Files Created/Modified

- `anansi/config.py` - catches `OverflowError` alongside existing integer conversion failures.
- `anansi/tests/test_drive_config.py` - table-driven coercion, finite-bound, cache, and reset coverage.
- `anansi/tests/test_failopen_matrix.py` - real session-start SQLite telemetry coverage for both infinity signs.
- `CHANGELOG.md` - dated root cause and reusable coercion-boundary learning.

## Decisions Made

- Caught `OverflowError` in `_coerce_int` only, leaving float coercion, key definitions, descriptor format, hook wiring, SQLite vocabulary, and finite clamp logic unchanged.
- Retained the existing descriptor contract: only `key`, `<float>`, and the applied default reach cache state or telemetry.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected an initially misplaced exception-boundary edit.**
- **Found during:** Task 1 GREEN verification.
- **Issue:** The first patch added `OverflowError` to `_coerce_float` instead of `_coerce_int`, leaving the target integer failure unchanged.
- **Fix:** Restored `_coerce_float` and applied the exception only to `_coerce_int` before rerunning the focused gate.
- **Files modified:** `anansi/config.py`.
- **Verification:** The target test changed from the expected `OverflowError` failure to a 52-test focused pass; the canonical 199-test suite passed.
- **Committed in:** `29d2892`.

**Total deviations:** 1 auto-fixed (1 bug).
**Impact on plan:** No final scope expansion or extra runtime behavior; the committed production diff is the planned one-line boundary correction.

## Issues Encountered

None.

## User Setup Required

None - no provider, host install, Docker action, or external configuration was used.

## Next Phase Readiness

The verifier's only Phase 8 config gap is covered by direct coercion, cached-read, session-reload, and canonical regression evidence. The separate provider-backed live lane remains UNRUN and deferred to Phase 14.

## Self-Check: PASSED

- All four declared task files exist.
- Both task commits exist after `50eed75b9cd6470c52c9ecea1202d7e8c6db1bbd`.
- The focused 52-test and canonical 199-test gates passed.

---
*Phase: 08-close-known-gaps*
*Completed: 2026-09-11*
