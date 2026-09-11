---
phase: 08-close-known-gaps
plan: "01"
subsystem: database-and-rendering
tags: [sqlite, migration, drive-pressure, fail-open, testing]
requires:
  - phase: 07-drive-containment
    provides: persisted goals, drive kill switch, energy budget, and protected flagged wants
provides:
  - schema-v5 goal pressure persistence with a lock-safe v4 upgrade
  - threshold-authorized push-zone and under-support rendering
  - bounded firm-only stalled-age ordering for authorized ordinary notes
affects: [08-02, 08-03, 08-04, drive-rendering]
actuals:
  tokens: null
  token_note: "Not measured: the earlier 7946 value was an estimate, not measured usage."
  tasks: 2
  commits: 4
  plan_head_before: f9d56cab0d147a40481e824362318981da2e5ef8
tech-stack:
  added: []
  patterns:
    - tri-state SQLite migration result, separating temporary unavailability from structural invalidity
    - persisted per-goal authorization kept separate from global pressure policy
key-files:
  created: []
  modified:
    - anansi/store.py
    - anansi/render.py
    - anansi/__init__.py
    - anansi/tests/test_drive_store.py
    - anansi/tests/test_reflection_store.py
    - anansi/tests/test_drive_config.py
key-decisions:
  - "A structurally sound locked v4 database returns unavailable and is never quarantined."
  - "Push-zone remains on third-person drive notes; first-person drive wants retain only under-support."
  - "Standard preserves the prior three-note output; firm alone orders authorized, threshold-satisfied ordinary notes by actual stalled age."
requirements-completed:
  - REQ-001-close-known-gaps-fr-001
  - REQ-001-close-known-gaps-fr-002
  - REQ-001-close-known-gaps-fr-003
coverage:
  - id: D1
    description: Schema v5 persists pressure fields and upgrades v4 goals without data loss or lock-triggered quarantine.
    requirement: REQ-001-close-known-gaps-fr-001
    verification:
      - kind: integration
        ref: anansi/tests/test_drive_store.py#test_populated_v4_db_migrates_additively_with_legacy_pressure_defaults
        status: pass
      - kind: integration
        ref: anansi/tests/test_drive_store.py#test_locked_v4_db_is_unavailable_without_quarantine_or_partial_migration
        status: pass
    human_judgment: false
  - id: D2
    description: Persisted threshold authorization reaches rendering through the hook while standard pressure remains compatible.
    requirement: REQ-001-close-known-gaps-fr-002
    verification:
      - kind: integration
        ref: anansi/tests/test_drive_store.py#test_persisted_pressure_authorizes_effect_only_after_its_threshold
        status: pass
      - kind: integration
        ref: anansi/tests/test_drive_store.py#test_pre_llm_call_passes_standard_pressure_without_changing_render_contract
        status: pass
    human_judgment: false
  - id: D3
    description: Quiet, standard, firm, invalid, and drive-off pressure paths stay bounded and fail open.
    requirement: REQ-001-close-known-gaps-fr-003
    verification:
      - kind: integration
        ref: anansi/tests/test_drive_config.py#test_pressure_full_hook_is_bounded_and_invalid_uses_standard
        status: pass
      - kind: integration
        ref: anansi/tests/test_drive_config.py#test_firm_full_hook_orders_authorized_notes_by_actual_stalled_age
        status: pass
      - kind: integration
        ref: anansi/tests/test_drive_config.py#test_pressure_drive_off_preserves_no_goals_appraisal_block
        status: pass
    human_judgment: false
duration: resumed-session
completed: 2026-09-11
status: complete
---

# Phase 08 Plan 01: Persisted Pressure Migration and Rendering Summary

**Goal pressure survives a lock-safe v4-to-v5 SQLite migration, and firm now visibly orders only authorized, threshold-satisfied ordinary notes by actual stalled age.**

## Performance

- **Duration:** resumed session, initial timestamp was not preserved
- **Tasks:** 2 completed
- **Files modified:** 6
- **Focused repair gate:** `./scripts/test.sh anansi/tests/test_drive_store.py anansi/tests/test_reflection_store.py anansi/tests/test_drive_config.py -x` — 36 passed
- **Full canonical gate:** `./scripts/test.sh` — 173 passed

## Accomplishments

- Added schema v5 pressure fields to fresh goal state, both goal write paths, snapshots, and a transactionally additive v4 migration.
- Kept locks distinct from corruption: unavailable v4 state remains untouched and is not quarantined.
- Repaired the rejected firm policy: standard preserves confidence ordering, while firm visibly orders only authorized, threshold-satisfied ordinary notes by longest actual stalled age within the same three-note energy bound.
- Replaced the stubbed threshold check with a full hook path through temporary SQLite state, real old file and row timestamps, a fresh snapshot, and deterministic appraisal signals.

## TDD Evidence

- **Task 1 RED:** a genuine schema RED run existed before this resumed session. The partial implementation was preserved as instructed; no RED commit was invented or reconstructed.
- **Task 1 GREEN:** `./scripts/test.sh anansi/tests/test_drive_store.py anansi/tests/test_reflection_store.py -x` — 21 passed, before and after the push-zone placement review.
- **Task 2 RED:** `./scripts/test.sh anansi/tests/test_drive_config.py -x` — failed at `test_pressure_full_hook_is_bounded_and_invalid_uses_standard`: quiet rendered 3 notes instead of 1.
- **Acceptance-repair RED:** `./scripts/test.sh anansi/tests/test_drive_config.py -x` — failed at `test_firm_full_hook_orders_authorized_notes_by_actual_stalled_age`: firm retained confidence order instead of actual stalled-age order.
- **Acceptance-repair GREEN:** `./scripts/test.sh anansi/tests/test_drive_config.py -x` — 15 passed; `./scripts/test.sh anansi/tests/test_drive_store.py -x` — 11 passed.

## Task Commits

1. **Task 1: Migrate safely and carry one persisted pressure setting through the hook** — `88677f2` (`feat`)
2. **Task 2: Expand quiet, standard, and firm pressure behavior** — `d68513e` (`feat`)
3. **Acceptance repair: make firm pressure age-sensitive** — `61ad9ec` (`fix`)
4. **Acceptance repair: exercise persisted pressure through hook** — `21ede38` (`test`)

**Plan metadata:** skipped, `commit_docs` is disabled. This SUMMARY is intentionally uncommitted for the orchestrator.

## Files Created/Modified

- `anansi/store.py` — schema v5 DDL, tri-state v4 migration, and pressure-field persistence.
- `anansi/render.py` — threshold-aware per-goal effects and explicit firm-only stalled-age ordering.
- `anansi/__init__.py` — passes configured pressure only on the drive-on render path.
- `anansi/tests/test_drive_store.py` and `anansi/tests/test_reflection_store.py` — migration, lock, round-trip, threshold, hook, and current-schema regressions.
- `anansi/tests/test_drive_config.py` — full-hook pressure, invalid input, standard compatibility, and drive-off regressions.

## Decisions Made

- A locked v4 database is temporary unavailability, not corruption. `ensure_db` returns `False` without moving sidecars, migrating partially, or erasing state.
- The rendering-contract review removed push-zone from first-person drive wants. Push-zone remains the drive-note effect; under-support remains the drive-want effect.
- Global pressure does not overwrite persisted support style, push authorization, or threshold. Firm reorders only the already-authorized cohort; standard is unchanged.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Firm rendered identically to standard for normal competing goals.**
- **Found during:** root acceptance review after the earlier completion claim.
- **Issue:** Uniform firm and standard bonuses preserved confidence ordering, so the supposed firm policy was not observable.
- **Fix:** Added a firm-only tuple key that prioritizes user-authorized, threshold-satisfied stalled goals and orders that cohort by actual stalled age; standard and quiet retain their prior ordering.
- **Files modified:** `anansi/render.py`, `anansi/tests/test_drive_config.py`
- **Verification:** Full-hook RED then GREEN test covers conflicting confidence and age, unauthorized and below-threshold controls, equal-age stable ties, standard difference, and the three-note ceiling.
- **Committed in:** `61ad9ec`

**2. [Rule 2 - Missing critical verification] Threshold evidence bypassed the production path.**
- **Found during:** root acceptance review after the earlier completion claim.
- **Issue:** The test stubbed `goal_momentum` and called rendering directly, so it did not prove persisted data reached `pre_llm_call` or that actual timestamps governed authorization.
- **Fix:** Replaced it with temporary SQLite state through `apply_deltas`, real four-day file and row timestamps, fresh `read_snapshot`, deterministic appraisal output, and `pre_llm_call`.
- **Files modified:** `anansi/tests/test_drive_store.py`
- **Verification:** Threshold 3 renders flagged-want under-support and ordinary-note push-zone; threshold 5 stays neutral; flagged wants do not duplicate as notes.
- **Committed in:** `21ede38`

**Total deviations:** 2 auto-fixed (1 bug, 1 missing critical verification).

## Issues Encountered

- The earlier executor could not create Git's `index.lock`. Dr. Mani authorized the supported metadata write grant before this resume; both normal-hook task commits then succeeded.
- The earlier completion was rejected. It did not prove a distinct firm result or a real persisted threshold-to-hook path; both gaps are covered by the repair commits above.

## User Setup Required

None, no external service configuration required.

## Next Phase Readiness

Plan 08-01 now has repair evidence for both rejected gaps. The summary remains uncommitted because `commit_docs: false`; the orchestrator owns it and all shared planning-state updates.

## Self-Check: PASSED

- All six declared code/test files exist.
- All four implementation and repair commits are present after `f9d56cab0d147a40481e824362318981da2e5ef8`.
- The final canonical suite passed: 173 tests.

---
*Phase: 08-close-known-gaps*
*Completed: 2026-09-11*
