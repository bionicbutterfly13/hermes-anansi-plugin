---
phase: 08-close-known-gaps
plan: "04"
subsystem: offline-verification-and-regression
tags: [pytest, live-smoke, offline, fail-open, terminology]
requires:
  - phase: 08-03
    provides: persisted priority, rendering, and timing behavior exercised by the canonical regression gate
provides:
  - primary terminology for the reflection kill-switch regression
  - offline proof that the live-drive smoke lane returns INCONCLUSIVE before provider import, plus a positive import-guard control
  - a separately read technical record for later authorized provider evidence
affects: [phase-8-verification, live-drive-smoke, changelog]
actuals:
  tokens: 1386
  tasks: 2
  commits: 3
  plan_head_before: 002b2b44474d88e492d898bebdcdf86557301168
tech-stack:
  added: []
  patterns:
    - offline evidence asserts both sides of the provider-import boundary without synthesizing a provider result
    - runtime tests do not depend on mutable planning metadata; technical records are read back separately
key-files:
  created:
    - anansi/tests/test_live_drive_smoke.py
    - .planning/phases/08-close-known-gaps/08-LIVE-SMOKE.md
  modified:
    - anansi/tests/test_reflection.py
    - CHANGELOG.md
key-decisions:
  - "The offline test proves exit-2 behavior and absence of provider import, never a live PASS."
  - "The live-smoke record is a planning artifact whose status can change only with later authorized evidence; it is not a runtime-test fixture."
requirements-completed:
  - REQ-001-close-known-gaps-fr-010
  - REQ-001-close-known-gaps-fr-011
  - REQ-001-close-known-gaps-fr-012
coverage:
  - id: D1
    description: Reflection kill-switch test terminology uses primary wording without changing its assertions or runtime behavior.
    requirement: REQ-001-close-known-gaps-fr-011
    verification:
      - kind: unit
        ref: anansi/tests/test_reflection.py#test_primary_kill_switch_disables_reflection
        status: pass
    human_judgment: false
  - id: D2
    description: Forced-offline live-drive smoke exits 2 with INCONCLUSIVE output before the provider import seam, while a stubbed-available probe proves the same guard stops the attempted import before provider access.
    requirement: REQ-001-close-known-gaps-fr-010
    verification:
      - kind: unit
        ref: anansi/tests/test_live_drive_smoke.py#test_forced_offline_smoke_is_inconclusive_before_provider_import
        status: pass
      - kind: unit
        ref: anansi/tests/test_live_drive_smoke.py#test_available_network_path_reaches_the_provider_import_guard
        status: pass
    human_judgment: false
  - id: D3
    description: The technical record was read back separately and was UNRUN at verification time, with the sole established command and 0/1/2 exit meanings present.
    requirement: REQ-001-close-known-gaps-fr-010
    verification:
      - kind: other
        ref: rg documentation readback of .planning/phases/08-close-known-gaps/08-LIVE-SMOKE.md
        status: pass
    human_judgment: false
  - id: D4
    description: The canonical offline suite preserves Phase 8 fail-open, observational, anti-erasure, timeout, and SQLite contracts.
    requirement: REQ-001-close-known-gaps-fr-012
    verification:
      - kind: integration
        ref: ./scripts/test.sh
        status: pass
    human_judgment: false
duration: 4 min
completed: 2026-09-11
status: complete
---

# Phase 08 Plan 04: Offline Live-Smoke Boundary and Constitutional Gate Summary

**Offline live-smoke coverage proves both an unavailable-network exit and the provider-import guard without making runtime tests depend on the mutable live-evidence record.**

## Performance

- **Duration:** Initial execution: 4 min; the post-acceptance test-only correction was completed in a separate resumed session.
- **Started:** 2026-09-11T14:26:12Z, first task commit evidence.
- **Completed:** 2026-09-11T14:29:48Z
- **Tasks:** 2 completed
- **Files modified:** 4 task files, plus this uncommitted summary

## Accomplishments

- Renamed the reflection kill-switch test to primary terminology with unchanged assertions and no production diff.
- Added importlib-based offline smoke coverage that forces preflight unavailable, asserts exit `2`, captures `INCONCLUSIVE`, and proves the shared import guard fires before provider access when preflight is stubbed available.
- Preserved the UNRUN technical live-smoke record, read it back separately, and completed the 188-test canonical offline regression gate.

## TDD Evidence

- **Original Task 2 RED/GREEN:** the original record-presence test drove creation of `08-LIVE-SMOKE.md`, but root acceptance later rejected that test contract because it coupled runtime verification to mutable metadata and made UNRUN permanent.
- **Acceptance correction:** `./scripts/test.sh anansi/tests/test_live_drive_smoke.py -x` passed, `2 passed`; the same two tests passed from an isolated fixture containing only the smoke script and test file, with no planning record present.
- **Constitutional gate:** `./scripts/test.sh` passed, `188 passed in 5.06s`.

## Task Commits

Each task was committed atomically with normal hooks:

1. **Task 1: Replace obsolete master terminology in the reflection test** - `00396cf` (`test`)
2. **Task 2: Prove the offline live-smoke boundary and complete the constitutional gate** - `fb68f2d` (`test`)
3. **Acceptance correction: decouple the smoke test from the live record** - `9f02b86` (`test`)

**Plan metadata:** uncommitted intentionally because `.planning/config.json` sets `planning.commit_docs` to `false`. `08-LIVE-SMOKE.md` and this summary remain for the orchestrator; no planning file was force-staged.

## Files Created/Modified

- `anansi/tests/test_reflection.py` - primary-named kill-switch regression.
- `anansi/tests/test_live_drive_smoke.py` - offline preflight, import-guard positive-control, and sys.path-isolation tests.
- `.planning/phases/08-close-known-gaps/08-LIVE-SMOKE.md` - technical live-evidence record, read separately as UNRUN at this verification point.
- `CHANGELOG.md` - dated Phase 8 features, root causes, and reusable lessons.

## Decisions Made

- Offline verification is limited to the no-network boundary. It does not invoke, import, or claim evidence from a live provider.
- The technical record can become PASS only from separately authorized exit-0 evidence; its status is not a permanent runtime-test assertion.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed the runtime-suite dependency on mutable live-evidence metadata.**
- **Found during:** Root acceptance of Task 2.
- **Issue:** The test read an intentionally uncommitted planning record and asserted its `UNRUN` status forever, so a fresh checkout could fail and a later authorized PASS would be treated as a regression.
- **Fix:** Removed the record fixture and test, added a shared import interception helper, and added a stubbed-network positive control that proves the interception fires before the provider import or call. Both test paths isolate `sys.path` with `monkeypatch`; neither performs networking, provider import, host configuration reads, or provider calls.
- **Files modified:** `anansi/tests/test_live_drive_smoke.py`.
- **Verification:** Focused suite passed in the repository and in an isolated fixture with no planning record; canonical suite passed, `188 passed`.
- **Committed in:** `9f02b86`.

**Total deviations:** 1 auto-fixed (1 bug).
**Impact on plan:** Corrects an acceptance regression without changing production code, the technical record, or the separately authorized live lane.

## Issues Encountered

The existing live-smoke script already had the correct exit-2 guard, so no production RED gate was manufactured. Root acceptance identified that the original metadata test was invalid: it could fail in a fresh checkout and reject a future legitimate record update. The correction keeps the record as separately checked documentation.

## User Setup Required

None - no external service configuration required. A future live-provider invocation requires separate authorization and is not part of this execution.

## Next Phase Readiness

Plan 08-04's runtime regression is complete. The technical record read UNRUN at this verification point, but remains eligible for a later separately authorized factual update. Shared planning state, roadmap, requirements, and configuration were not modified.

## Self-Check: PASSED

- `anansi/tests/test_reflection.py`, `anansi/tests/test_live_drive_smoke.py`, and `08-LIVE-SMOKE.md` exist.
- Task commits `00396cf`, `fb68f2d`, and `9f02b86` exist after `002b2b44474d88e492d898bebdcdf86557301168`.
- Current focused live-smoke gates passed with 2 tests in the repository and 2 tests from an isolated fixture without the planning record; the final canonical gate passed with 188 tests.

---
*Phase: 08-close-known-gaps*
*Completed: 2026-09-11*
