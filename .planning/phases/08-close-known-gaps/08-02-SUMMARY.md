---
phase: 08-close-known-gaps
plan: "02"
subsystem: configuration-telemetry
tags: [configuration, telemetry, fail-open, sqlite, secret-safety, testing]
requires:
  - phase: 08-01
    provides: drive-pressure coercion and phase-8 integration baseline
provides:
  - shape-only config degradation descriptors scoped to the latest config load
  - once-per-session config_degraded telemetry that cannot alter hook output
  - config_degraded classification outside telemetry failures and last-error selection
affects: [08-03, 08-04, telemetry, fail-open-hooks]
actuals:
  tokens: 4732
  tasks: 2
  commits: 5
  plan_head_before: 9b9394fde53a1c5ebaef85febbda2228a674f883
tech-stack:
  added: []
  patterns:
    - cache-scoped shape-only configuration degradation records
    - nested telemetry-only fail-open boundary in session startup
key-files:
  created: []
  modified:
    - anansi/config.py
    - anansi/__init__.py
    - anansi/store.py
    - anansi/tests/test_drive_config.py
    - anansi/tests/test_failopen_matrix.py
    - anansi/tests/test_telemetry_store.py
key-decisions:
  - "Rejected configuration is represented only as key, shape, and applied default, never as a retained literal."
  - "Config diagnostics emit only during session-start reload and are isolated from subsequent hook behavior."
requirements-completed:
  - REQ-001-close-known-gaps-fr-004
  - REQ-001-close-known-gaps-fr-005
coverage:
  - id: D1
    description: Every malformed or clamped known configuration value yields one shape-only descriptor, while valid normalization and cache reads yield none.
    requirement: REQ-001-close-known-gaps-fr-004
    verification:
      - kind: unit
        ref: anansi/tests/test_drive_config.py#test_config_degradations_are_shape_only_and_once_per_key
        status: pass
      - kind: unit
        ref: anansi/tests/test_drive_config.py#test_config_degradations_describe_effective_values_without_raw_inputs
        status: pass
      - kind: unit
        ref: anansi/tests/test_drive_config.py#test_config_degradations_ignore_normalization_and_cached_reads
        status: pass
    human_judgment: false
  - id: D2
    description: Session startup emits secret-safe config_degraded telemetry outside failure accounting, and unavailable diagnostic telemetry leaves ordinary appraisal output unchanged.
    requirement: REQ-001-close-known-gaps-fr-005
    verification:
      - kind: integration
        ref: anansi/tests/test_failopen_matrix.py#test_session_start_emits_one_secret_safe_config_row_per_degradation
        status: pass
      - kind: integration
        ref: anansi/tests/test_failopen_matrix.py#test_unavailable_config_telemetry_does_not_change_next_hook_output
        status: pass
      - kind: integration
        ref: anansi/tests/test_telemetry_store.py#test_telemetry_summary_config_degraded_is_non_failure
        status: pass
    human_judgment: false
duration: resumed-executor-session
completed: 2026-09-11
status: complete
---

# Phase 08 Plan 02: Secret-Safe Configuration Telemetry Summary

**Configuration coercions now produce one inspectable row per session reload whose applied value is the actual effective scalar or container shape, while missing diagnostics cannot change an appraisal hook's result.**

## Performance

- **Duration:** resumed executor session, exact start timestamp was not captured.
- **Completed:** 2026-09-11.
- **Tasks:** 2 completed.
- **Files modified:** 6.
- **Focused gate:** `./scripts/test.sh anansi/tests/test_drive_config.py anansi/tests/test_failopen_matrix.py anansi/tests/test_telemetry_store.py -x` , 56 passed.
- **Canonical gate:** `./scripts/test.sh` , 181 passed.

## Accomplishments

- Added cache-scoped degradation records for rejected or clamped scalar, list, choice, and model values without retaining their rejected literals.
- Emitted one `config_degraded` row per record at session startup, with safe key, rejected-shape, and applied-effective fields.
- Preserved fail-open behavior when telemetry returns `False` or raises, and excluded configuration observations from failure counts and `last_error`.

## TDD Evidence

- **Task 1 RED:** `./scripts/test.sh anansi/tests/test_drive_config.py -x` failed because `config.get_degradations` did not exist.
- **Task 1 GREEN:** `./scripts/test.sh anansi/tests/test_drive_config.py -x` passed, 17 tests.
- **Task 2 RED:** `./scripts/test.sh anansi/tests/test_drive_config.py anansi/tests/test_failopen_matrix.py anansi/tests/test_telemetry_store.py -x` failed because session startup stored no `config_degraded` rows.
- **Task 2 GREEN:** the same focused command passed, 55 tests.
- **Acceptance-repair RED:** `./scripts/test.sh anansi/tests/test_drive_config.py anansi/tests/test_failopen_matrix.py -x` failed because `deadline_seconds=999` reported applied `8.0` instead of effective `10.0`.
- **Acceptance-repair GREEN:** the focused gate passed, 56 tests; the canonical gate passed, 181 tests.

## Task Commits

1. **Task 1 RED: add configuration degradation coverage** , `4cd74bb` (`test`).
2. **Task 1 GREEN: track secret-safe configuration degradation** , `f759dc2` (`feat`).
3. **Task 2 RED: cover degradation telemetry and unavailable diagnostics** , `bb20f31` (`test`).
4. **Task 2 GREEN: emit degradation telemetry outside failure behavior** , `7af5bc0` (`feat`).
5. **Acceptance repair: report actual effective diagnostic values** , `57f3f7d` (`fix`).

**Plan metadata:** uncommitted intentionally because `.planning/config.json` sets `planning.commit_docs` to `false`; the orchestrator owns planning artifacts.

## Files Created/Modified

- `anansi/config.py` , shape-only per-load degradation detection and reset behavior.
- `anansi/__init__.py` , session-start diagnostic emission within an isolated fail-open boundary.
- `anansi/store.py` , non-failure `config_degraded` telemetry vocabulary.
- `anansi/tests/test_drive_config.py` , coercion, secret-safety, normalization, and cache idempotency tests.
- `anansi/tests/test_failopen_matrix.py` , session-start rows and unavailable-telemetry full-hook tests.
- `anansi/tests/test_telemetry_store.py` , non-failure summary classification test.

## Decisions Made

- Rejected values never leave `config.py`; only `(key, shape, applied_effective)` records are cached for the most recent load.
- A descriptor's applied field describes the actual effective value after coercion: safe scalars directly and containers by type/length only.
- Diagnostic telemetry is only emitted after `on_session_start` resets and reloads the configuration. Per-turn cached reads emit nothing.
- `config_degraded` remains queryable in `by_outcome`, but does not become a failure or select `last_error`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Diagnostics described declared defaults instead of applied effective values.**
- **Found during:** root acceptance review of the completed 08-02 lane.
- **Issue:** Clamped values, such as `deadline_seconds=999`, produced effective config `10.0` while descriptors and persisted telemetry said `8.0`. Partially filtered lists likewise reported the default shape instead of the surviving effective shape.
- **Fix:** Build the descriptor's applied field from the effective config, reducing containers to their type/length shape before caching and formatting.
- **Files modified:** `anansi/config.py`, `anansi/__init__.py`, `anansi/tests/test_drive_config.py`, `anansi/tests/test_failopen_matrix.py`.
- **Verification:** RED then focused 56-test and canonical 181-test gates prove upper/lower clamps, invalid-parse fallback, filtered-list shape, and raw-value/member absence from descriptors and stored messages.
- **Committed in:** `57f3f7d`.

**Total deviations:** 1 auto-fixed (1 bug).

## Issues Encountered

- The prior 180-test acceptance claim was rejected: it allowed telemetry to state declared defaults rather than the values actually applied by `get_cfg()`. The repair adds direct descriptor and persisted-row assertions for the four rejected cases.

## User Setup Required

None , no external service configuration is required.

## Next Phase Readiness

Plan 08-02 now has corrected effective-value diagnostics plus focused config, telemetry, and full-hook fail-open evidence. The untracked 08-01 summary was preserved and not staged. Shared planning state remains unchanged for the orchestrator.

## Self-Check: PASSED

- All six declared source and test files exist.
- All five measured plan commits exist after `9b9394fde53a1c5ebaef85febbda2228a674f883`.
- The focused 56-test gate and canonical 181-test gate passed.

---
*Phase: 08-close-known-gaps*
*Completed: 2026-09-11*
