---
phase: 08-close-known-gaps
plan: "03"
subsystem: drive-persistence-and-rendering
tags: [sqlite, fail-open, never-omit, token-matching, timing, testing]
requires:
  - phase: 08-01
    provides: persisted pressure metadata and pressure-aware drive rendering
  - phase: 08-02
    provides: phase-8 fail-open integration baseline
provides:
  - flagged-priority exemption from the persisted goals cap
  - active flagged wants through successful empty-signal hook output
  - ASCII whole-token association and persisted timing authority
affects: [08-04, drive-rendering, fail-open-verification]
actuals:
  tokens: 6480
  tasks: 2
  commits: 4
  plan_head_before: 6ad6c00da9016e82d6c7a0d36ba98e586c745078
tech-stack:
  added: []
  patterns:
    - persisted flagged rows remain outside unflagged retention and rendering limits
    - whole-token goal matching shares one predicate across enrichment and duplicate suppression
key-files:
  created: []
  modified:
    - anansi/store.py
    - anansi/__init__.py
    - anansi/render.py
    - anansi/tests/test_drive_store.py
    - anansi/tests/test_drive_neveromit.py
    - anansi/tests/test_drive_velocity.py
key-decisions:
  - "The configured goals cap retains only unflagged rows; every flagged row remains persisted."
  - "A successful empty signal mapping renders active flagged wants, while signals=None remains an empty failure injection."
  - "Persisted zero-day timing is fresh evidence, not stalled or model-authoritative timing."
requirements-completed:
  - REQ-001-close-known-gaps-fr-006
  - REQ-001-close-known-gaps-fr-007
  - REQ-001-close-known-gaps-fr-008
  - REQ-001-close-known-gaps-fr-009
coverage:
  - id: D1
    description: Persisted active flagged priorities survive unflagged cap pressure, domain filtering, successful empty appraisal signals, and token crowding without a withholding marker.
    requirement: REQ-001-close-known-gaps-fr-006
    verification:
      - kind: integration
        ref: anansi/tests/test_drive_store.py#test_goal_cap_preserves_all_flagged_priorities_under_unflagged_pressure
        status: pass
      - kind: integration
        ref: anansi/tests/test_drive_neveromit.py#test_persisted_flagged_priorities_survive_empty_signal_full_hook
        status: pass
    human_judgment: false
  - id: D2
    description: Whole-token association, read-time timing precedence, fresh zero-day wording, and stable drive ordering are deterministic.
    requirement: REQ-001-close-known-gaps-fr-008
    verification:
      - kind: unit
        ref: anansi/tests/test_drive_velocity.py#test_goal_text_matching_requires_nonempty_whole_token_subset
        status: pass
      - kind: unit
        ref: anansi/tests/test_drive_velocity.py#test_enrich_uses_persisted_timing_and_rejects_substring_associations
        status: pass
      - kind: unit
        ref: anansi/tests/test_drive_velocity.py#test_render_orders_flagged_then_stalled_then_fresh_with_stable_ties
        status: pass
      - kind: integration
        ref: ./scripts/test.sh anansi/tests/test_drive_velocity.py anansi/tests/test_failopen_matrix.py -x
        status: pass
    human_judgment: false
duration: 4 min
completed: 2026-09-11
status: complete
---

# Phase 08 Plan 03: Flagged Priority Preservation and Ground-Truth Timing Summary

**Persisted flagged priorities now survive cap pressure, domain filtering, and successful empty appraisals, while drive evidence uses whole-token associations and read-time timing.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-09-11T14:17:35Z
- **Completed:** 2026-09-11T14:21:47Z
- **Tasks:** 2 completed
- **Files modified:** 6

## Accomplishments

- Added a store-owned cap that evicts only unflagged goals, preserving 55 active flagged priorities under 60 unflagged inserts.
- Preserved active flagged goals through domain containment and full-hook rendering when a successful appraisal has `signals={}`; inactive candidate and backburner controls remain absent.
- Replaced substring matching with deterministic ASCII whole-token containment, made persisted timing authoritative, and rendered zero-day evidence as fresh.

## TDD Evidence

- **Task 1 RED:** `./scripts/test.sh anansi/tests/test_drive_store.py anansi/tests/test_drive_neveromit.py -x` failed at `test_goal_cap_preserves_all_flagged_priorities_under_unflagged_pressure` because the old global cap evicted flagged rows.
- **Task 1 GREEN:** the same command passed, `25 passed`.
- **Task 2 RED:** `./scripts/test.sh anansi/tests/test_drive_velocity.py anansi/tests/test_failopen_matrix.py -x` failed at `test_goal_text_matching_requires_nonempty_whole_token_subset` because `_goal_text_matches` did not exist.
- **Task 2 GREEN:** the same command passed, `41 passed`.
- **Plan gate:** `./scripts/test.sh anansi/tests/test_drive_store.py anansi/tests/test_drive_neveromit.py anansi/tests/test_drive_velocity.py anansi/tests/test_failopen_matrix.py -x` passed, `66 passed`.

## Task Commits

1. **Task 1 RED: cover persisted flagged priority preservation** - `bb2c1d6` (`test`)
2. **Task 1 GREEN: preserve flagged priorities through empty appraisals** - `5a42d95` (`feat`)
3. **Task 2 RED: cover token matching and persisted timing** - `cb2dd7e` (`test`)
4. **Task 2 GREEN: ground drive evidence in tokens and snapshots** - `0d6c3d6` (`feat`)

**Plan metadata:** uncommitted intentionally because `.planning/config.json` sets `planning.commit_docs` to `false`; the orchestrator owns planning artifacts.

## Files Created/Modified

- `anansi/store.py` - unflagged-only retention cap.
- `anansi/__init__.py` - active flagged domain exemption and token-precise domain signal filtering.
- `anansi/render.py` - successful-empty flagged output, whole-token matching, persisted timing, fresh rendering, and stable ordering.
- `anansi/tests/test_drive_store.py` - flagged cap-pressure persistence regression.
- `anansi/tests/test_drive_neveromit.py` - persisted full-hook empty-signal, inactive-control, failure, and drive-off regressions.
- `anansi/tests/test_drive_velocity.py` - token, timing-authority, freshness, and stable-order regressions.

## Decisions Made

- Constitution Principle III overrides the lower-precedence flagged-want cap: no flagged priority is counted, withheld, or evicted.
- `signals is None` remains the only appraisal-result path that suppresses injection after a failed appraisal; an empty mapping is a successful result.
- A persisted `stalled_days` integer, including `0`, replaces model timing. Missing persisted timing removes model timing rather than fabricating ground truth.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for Plan 08-04. Shared planning state remains unchanged for the orchestrator.

## Self-Check: PASSED

- All six declared source and test files exist.
- All four task commits exist after `6ad6c00da9016e82d6c7a0d36ba98e586c745078`.
- The targeted Task 1, Task 2, and 66-test plan gates passed.

---
*Phase: 08-close-known-gaps*
*Completed: 2026-09-11*
