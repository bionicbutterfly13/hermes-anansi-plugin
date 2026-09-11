---
phase: "08"
slug: "close-known-gaps"
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-09-10"
---

# Phase 8 Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| Framework | Existing pytest 9.1.1, Python 3.11.15 observed by researcher |
| Config file | scripts/test.sh controls interpreter and test paths |
| Quick run command | `./scripts/test.sh anansi/tests/test_drive_store.py anansi/tests/test_drive_config.py anansi/tests/test_drive_velocity.py anansi/tests/test_drive_neveromit.py anansi/tests/test_failopen_matrix.py` |
| Full suite command | `./scripts/test.sh` |
| Baseline | 165 passed in 9.36s on eb228d7, 2026-09-10 |

The historical baseline above verifies earlier offline behavior only. Current evidence: `./scripts/test.sh` passed 188 tests in 5.91s after the fourth wave merged at `d0d1354`, 2026-09-11. No host installation, dependency change, or live-provider call is authorized by this document.

## Sampling Rate

- After each implementation task, run its focused test command before any authorized commit.
- After each plan wave and before verification, run `./scripts/test.sh`.
- Target feedback latency: 60 seconds. Latest full-suite execution measured 5.91s.

## Per-Task Verification Map

All nine task IDs have executable offline verification. The live provider evidence check remains manual-only and UNRUN as agreed in the phase context.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 08-01-T1 | 08-01 | 1 | FR-001, FR-002, SC-002 | Constitution I, IV | Additive migration preserves goals; real persisted threshold evidence reaches the hook; locked v4 databases are not quarantined | unit/hook | `./scripts/test.sh anansi/tests/test_drive_store.py anansi/tests/test_reflection_store.py` | yes | passed |
| 08-01-T2 | 08-01 | 1 | FR-003, SC-003 | Constitution VI | Firm changes eligible note ordering; standard and authorization limits remain intact | unit/hook | `./scripts/test.sh anansi/tests/test_drive_config.py` | yes | passed |
| 08-02-T1, 08-02-T2 | 08-02 | 2 | FR-004, FR-005, SC-004 | Constitution I | Shape-only telemetry reports actual effective values and cannot block hooks | unit/hook | `./scripts/test.sh anansi/tests/test_drive_config.py anansi/tests/test_failopen_matrix.py anansi/tests/test_telemetry_store.py` | yes | passed |
| 08-03-T1 | 08-03 | 3 | FR-006, FR-007, SC-005 | Constitution III | Every persisted active flagged priority remains visible; source cap is superseded | store/hook | `./scripts/test.sh anansi/tests/test_drive_store.py anansi/tests/test_drive_neveromit.py` | yes | passed |
| 08-03-T2 | 08-03 | 3 | FR-008, FR-009 | Constitution IV | Whole-token associations and zero-day freshness use persisted evidence | unit/hook | `./scripts/test.sh anansi/tests/test_drive_velocity.py anansi/tests/test_failopen_matrix.py` | yes | passed |
| 08-04-T1 | 08-04 | 4 | FR-011 | no runtime change | Terminology-only change preserves assertions | unit | `./scripts/test.sh anansi/tests/test_reflection.py` | yes | passed |
| 08-04-T2 | 08-04 | 4 | FR-010, FR-012, SC-001, SC-006 | Constitution I-VII | Offline exit 2 and positive import-guard control preserve truthful live-evidence boundaries; full suite remains green | offline/full suite | `./scripts/test.sh` | yes | passed offline; live UNRUN |
| 08-05-T1 | 08-05 | 5 | FR-004, FR-005, FR-012 | Constitution I, V, VII | All five integer keys reject infinity and NaN without raising; actual session reloads persist shape-only diagnostics | unit/hook/full suite | `./scripts/test.sh anansi/tests/test_drive_config.py anansi/tests/test_failopen_matrix.py -x` and `./scripts/test.sh` | yes | passed |

All FR abbreviations refer to `REQ-001-close-known-gaps-fr-NNN`. Source scenarios US-1 through US-8, all five edge cases, and SC-001 through SC-006 are mapped in 08-RESEARCH.md. Plans must preserve that mapping, including the constitution-over-cap disposition for US-4 and SC-005.

## Wave 0 Requirements

- [x] 08-01-T1 adds locked-v4 migration, legacy-default, preservation, persisted threshold-to-render, and standard full-hook tests in test_drive_store.py, and updates only the current-schema v4 assertion/comment in test_reflection_store.py to v5 while historical v4 fixtures remain v4.
- [x] 08-01-T2, 08-02-T1, and 08-02-T2 add pressure expansion, per-key degradation, redaction, and unavailable telemetry tests in test_drive_config.py and test_failopen_matrix.py.
- [x] 08-03-T2 adds token matching, fresh-day, and persisted-over-model timing tests in test_drive_velocity.py.
- [x] 08-03-T1 adds persisted all-flagged preservation tests in test_drive_store.py and test_drive_neveromit.py, including model omission and crowding.
- [x] 08-04-T2 adds the offline live-smoke exit-contract test and runs the canonical suite.
- Existing infrastructure is available; no framework installation is planned.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live first-person owned-want voice | 08-04-T2; FR-010, US-7, SC-001 | Provider-backed execution requires separate authorization and available host | After authorization, run the documented scripts/live_drive_smoke.py command with the configured Hermes interpreter; record actual exit code and output. An unrun check stays unrun; an unavailable-provider result stays inconclusive. Neither is a live PASS. |

## Validation Sign-Off

- [x] All implementation tasks have automated verification.
- [x] No three consecutive implementation tasks lack automated verification.
- [x] Wave 0 covers all missing regression references.
- [x] No watch-mode flags.
- [x] Feedback latency meets the target.
- [x] nyquist_compliant reflects validated offline evidence, not live provider proof.

Validation: offline task coverage audited on 2026-09-11. Independent phase verification remains pending. Live provider status remains UNRUN.

## Validation Audit 2026-09-11

| Metric | Count |
|--------|-------|
| Plans audited | 4 |
| Implementation tasks mapped | 8 |
| Functional requirement IDs mapped | 12 |
| Current automated coverage gaps | 0 |
| New tests generated by this audit | 0 |
| Separately authorized live checks still UNRUN | 1 |

The initial audit matched every task's verify command and requirement IDs to existing
green tests and the final 188-test post-merge gate. Acceptance corrections were
already completed before this audit: observable firm behavior and a full persisted
threshold path, truthful effective config diagnostics, and runtime tests independent
of mutable planning records. The technical live record was read separately and
preserved byte-for-byte during executor cleanup. No missing-test agent was needed.

### Independent review supersedes initial coverage sign-off

`08-REVIEW.md` subsequently established three blockers and one warning missed by
the green suite: legacy-shaped updates clear pressure consent, malformed priorities
bypass domain/cap containment, and actual fresh persisted reads never produce zero.
Coverage is PARTIAL until those paths are repaired and their regressions pass.
This historical interim status was superseded by the verified repair passes below.

### Final review-fix validation

At `50eed75`, all original findings and the additional non-finite-priority
coercion finding are resolved in the independent `08-REVIEW.md` re-review.
The added regressions cover legacy-shaped consent-preserving updates, actual
malformed SQLite priorities and domain/cap containment, and real persisted
zero-day state through the hook. All 194 tests passed after merge in 9.25s and
again during independent re-review. Six focused repair regressions also passed
independently. There are no remaining reported automated coverage gaps.
`nyquist_compliant` is restored to true for offline task coverage. Live provider
evidence remains UNRUN and is not inferred from any of these checks.

### Phase-verifier gap

The final verifier found native positive/negative infinity raises in `_coerce_int`
for all five integer config keys before degradation descriptors are produced.
`08-VERIFICATION.md` records 23/25 truths verified and the exact failing family.
Offline validation is pending this bounded gap closure; nyquist_compliant is false.

### Verified gap closure supersedes the pending status

Plan 08-05 is merged at `f23ee37023e04dd9514b4425e3f00c53c04f19e1`.
Its production change catches `OverflowError` only in `_coerce_int`. Five added
tests cover all five integer keys with both infinity signs and NaN, finite
normalization and bounds, cache reuse/reset, and exact SQLite diagnostics across
two real session starts. Existing tests remain enabled and unchanged.
The independent reviewer passed all 52 focused tests in 1.64s and found no
unresolved issue. The post-merge canonical gate passed all 199 tests in 6.32s.
Current coverage: five plans, nine tasks, twelve functional requirements,
zero reported automated gaps. Offline Nyquist compliance is restored; final
goal verification subsequently passed 25/25 at this source head. Live provider evidence remains UNRUN, deferred to
Phase 14, and is excluded from the offline compliance claim.
