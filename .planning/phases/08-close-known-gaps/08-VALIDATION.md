---
phase: "08"
slug: "close-known-gaps"
status: draft
nyquist_compliant: false
wave_0_complete: false
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

Baseline evidence verifies existing offline behavior only. Future regression selectors must be added before claiming new requirements pass. Preserve existing assertions. No host installation, dependency change, or live-provider call is authorized by this document.

## Sampling Rate

- After each implementation task, run its focused test command before any authorized commit.
- After each plan wave and before verification, run `./scripts/test.sh`.
- Target feedback latency: 60 seconds. Baseline measured 9.36s; future runtime remains unmeasured.

## Per-Task Verification Map

Task IDs below map planned regression work. Status remains pending and `wave_0_complete` remains false until execution produces current evidence.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 08-01-T1 | 08-01 | 1 | FR-001, FR-002, SC-002 | Constitution I, IV | Additive migration preserves goals, persisted pressure and threshold drive the per-goal render after reload, locked databases are not quarantined, and shared-store current-version assertions advance together | unit/hook | `./scripts/test.sh anansi/tests/test_drive_store.py anansi/tests/test_reflection_store.py` | yes; new regressions and current-version updates pending | pending |
| 08-01-T2 | 08-01 | 1 | FR-003, SC-003 | Constitution VI | Pressure affects rendering; invalid configuration defaults | unit/hook | `./scripts/test.sh anansi/tests/test_drive_config.py` | yes; new regressions pending | pending |
| 08-02-T1, 08-02-T2 | 08-02 | 2 | FR-004, FR-005, SC-004 | Constitution I | Shape-only degradation telemetry cannot leak input or block hooks | unit/hook | `./scripts/test.sh anansi/tests/test_drive_config.py anansi/tests/test_failopen_matrix.py anansi/tests/test_telemetry_store.py` | yes; new regressions pending | pending |
| 08-03-T1 | 08-03 | 3 | FR-006, FR-007, SC-005 | Constitution III | Every persisted flagged priority remains visible; source cap is superseded | store/hook | `./scripts/test.sh anansi/tests/test_drive_store.py anansi/tests/test_drive_neveromit.py` | yes; new regressions pending | pending |
| 08-03-T2 | 08-03 | 3 | FR-008, FR-009 | Constitution IV | Token associations and zero-day freshness use persisted read-time evidence | unit | `./scripts/test.sh anansi/tests/test_drive_velocity.py anansi/tests/test_failopen_matrix.py` | yes; new regressions pending | pending |
| 08-04-T1 | 08-04 | 4 | FR-011 | no runtime change | Terminology-only change preserves behavior | unit | `./scripts/test.sh anansi/tests/test_reflection.py` | yes | pending |
| 08-04-T2 | 08-04 | 4 | FR-010, FR-012, SC-001, SC-006 | Constitution I-VII | Offline smoke semantics remain truthful; existing fail-open and observational checks remain intact | offline/full suite | `./scripts/test.sh` | no; planned / existing suite yes | pending |

All FR abbreviations refer to `REQ-001-close-known-gaps-fr-NNN`. Source scenarios US-1 through US-8, all five edge cases, and SC-001 through SC-006 are mapped in 08-RESEARCH.md. Plans must preserve that mapping, including the constitution-over-cap disposition for US-4 and SC-005.

## Wave 0 Requirements

- [ ] 08-01-T1 adds locked-v4 migration, legacy-default, preservation, persisted threshold-to-render, and standard full-hook tests in test_drive_store.py, and updates only the current-schema v4 assertion/comment in test_reflection_store.py to v5 while historical v4 fixtures remain v4.
- [ ] 08-01-T2, 08-02-T1, and 08-02-T2 add pressure expansion, per-key degradation, redaction, and unavailable telemetry tests in test_drive_config.py and test_failopen_matrix.py.
- [ ] 08-03-T2 adds token matching, fresh-day, and persisted-over-model timing tests in test_drive_velocity.py.
- [ ] 08-03-T1 adds persisted all-flagged preservation tests in test_drive_store.py and test_drive_neveromit.py, including model omission and crowding.
- [ ] 08-04-T2 adds the offline live-smoke exit-contract test and runs the canonical suite.
- Existing infrastructure is available; no framework installation is planned.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live first-person owned-want voice | 08-04-T2; FR-010, US-7, SC-001 | Provider-backed execution requires separate authorization and available host | After authorization, run the documented scripts/live_drive_smoke.py command with the configured Hermes interpreter; record actual exit code and output. An unrun check stays unrun; an unavailable-provider result stays inconclusive. Neither is a live PASS. |

## Validation Sign-Off

- [ ] All implementation tasks have automated verification or explicit dependencies on new regressions.
- [ ] No three consecutive implementation tasks lack automated verification.
- [ ] Wave 0 covers all missing regression references.
- [ ] No watch-mode flags.
- [ ] Feedback latency meets the target.
- [ ] nyquist_compliant reflects validated evidence, not planning intent.

Approval: pending execution and validation.
