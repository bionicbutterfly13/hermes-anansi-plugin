# Roadmap - Hermes Anansi Metacognition Plugin

GSD is active as of 2026-09-10. Phases 1-7 retain historical evidence and completion claims. The imported feature branch is unmerged. Phase 8 starts by reconciling against main; checked source tasks are not fresh verification. Phase 5 has an unresolved missing historical summary.

Created 2026-06-10 (autonomous ceremony). 4 coarse phases per SUMMARY.md's roadmap implications;
ordering follows the FEATURES.md dependency spine. Every v1 requirement maps to exactly one phase.

<details>
<summary>ARCHIVED planning baseline: Phases 1-7; Phase 5 evidence remains incomplete</summary>

### Phase 1: Skeleton + State (no LLM) — ✓ Complete 2026-06-10 (verification: passed, 17/17 — network-blocked item closed same day)

**Goal:** A loadable, inert, state-capable plugin — proven against the live install.

**Requirements:** PLUG-01, PLUG-02, PLUG-03, PLUG-04, STATE-01, STATE-02, STATE-03, STATE-04, STATE-05

**Success criteria:**
1. `hermes plugins enable anansi` loads the plugin; `HERMES_PLUGINS_DEBUG=1` shows hooks registered, kind=standalone
2. No-op hooks fire across a real turn without any effect on output or latency
3. State store round-trips all tables; corrupt-DB and locked-DB scenarios degrade silently (tests green)
4. Phase-0 validation items 1–4 from SUMMARY.md answered and recorded

### Phase 2: Appraisal Path (the core) — ✓ Complete 2026-06-10 (verification: passed, 12/12 must-haves, 49/49 tests; see 02-VERIFICATION.md)

**Goal:** Every eligible turn gets a grounded, capped, sanitized appraisal block — within budget.

**Requirements:** APPR-01, APPR-02, APPR-03, APPR-04, APPR-05, APPR-06, APPR-07, APPR-08, OBS-01

**Success criteria:**
1. A real `hermes` turn shows a `[anansi appraisal]` block with instincts/salience signals grounded in the actual message + state
2. Telemetry shows p50 ≤6s appraisal wall time within the 8.0s default deadline, one LLM call per eligible turn, outcome distribution visible *(revised 2026-06-10 R1 — original ≤1.0s; Dr. Mani accepted ~5s p50 / max quality)*
3. Kill switch off → zero appraisal calls; trust-gate denial → automatic fallback to host model (verified)
4. Quiet/duplicate turns inject nothing (suppression + throttle verified)
5. Phase-0 items 5–7 (model quirks, contradiction fixture quality, telemetry) recorded

### Phase 3: Fail-Open Hardening + Reflection — ✓ Complete 2026-06-10 (verification: passed, 18/18 must-haves, 4/4 criteria, 105/105 tests; see 03-VERIFICATION.md)

**Goal:** Nothing the plugin does can hurt a turn; reflection becomes the carrier of appraisal context across the one-turn lag — the second half of the appraisal input contract, not polish. State actually learns across sessions. *(Sharpened 2026-06-10 R2; reflection inputs = messages + assistant responses + state, never the ephemeral injected memory block.)*

**Requirements:** SAFE-01, SAFE-02, SAFE-03, SAFE-04, REFL-01, REFL-02, REFL-03, REFL-04, REFL-05

**Success criteria:**
1. Full fail-open matrix green (timeout, trust, malformed JSON, truncation, content:null, DB states, missing config) — no case raises or blocks
2. Reflection runs only on session-change/N-turn debounce; double-firing produces identical state (idempotence test)
3. After a session discussing topic X with a contradiction, the next session's appraisal surfaces it (one-turn-lag loop demonstrated end-to-end)
4. No directive language detectable in any rendered block (pattern test green)

### Phase 4: Packaging + Upstream PR Prep — ✓ Complete 2026-06-10 (verification: passed, 13/13 must-haves, 3/3 criteria; PR #43906 submitted then WITHDRAWN 2026-06-10 — plugin is proprietary, see research/DESIGN-REWIND-2026-06-10.md)

**Goal:** Contributable artifact — in-tree layout, docs, upstream-main parity — gated on sign-off.

**Requirements:** PKG-01, PKG-02, PKG-03, PKG-04

**Success criteria:**
1. Plugin installs cleanly in both layouts (standalone `$HERMES_HOME/plugins/anansi` and in-tree `plugins/`)
2. `pip_dependencies: []` verified; test suite passes to host standards on upstream main
3. PR branch + PR_BODY.md ready; submitted upstream as https://github.com/NousResearch/hermes-agent/pull/43906

### Phase 5: Proprietary Pivot State Reconciliation *(gap-closure cleanup)*

**Goal:** Restore learnship routing after the proprietary pivot: reconcile state with the withdrawn PR, expose the next proprietary discussion phase, and account for interrupted quick-task residue.

**Closes:** v1.0 milestone audit integration/flow gaps — stale Phase 4 sign-off state; missing post-withdrawal roadmap path for proprietary Phase 5 discussion.

**Status:** [~] Cleanup only — reconciles planning state after PR #43906 withdrawal; no plugin code or proprietary feature implementation.

**Depends on:** Phase 4

### Phase 6: Proprietary User Model + Drive Design *(discussion/design only)*

**Goal:** Discuss and design the proprietary direction before implementation: layered autobiographical user model, aligned drive/goals, scheduled heartbeat, user-dopamine, worldview, and reconsolidation direction.

**Status:** [x] Complete — design captured (06-CONTEXT.md, 2026-06-14); adjustable drive-pressure / anti-complacency addendum integrated 2026-06-14.

**Depends on:** Phase 5 cleanup

### Phase 7: Drive / Accountability *(first proprietary implementation increment)*

**Goal:** Every eligible turn can surface user-minted goals with grounded progress/accountability signals — in-turn, never omitting a flagged priority — built on the existing appraisal path and the anansi SQLite store.

**Requirements (proprietary v2 — new IDs):** DRIVE-01, DRIVE-02, DRIVE-03, DRIVE-04, DRIVE-05, DRIVE-06

- **DRIVE-01 — Goal objects:** user-minted goals persisted in new tables in the anansi SQLite store (`store.py`, single sqlite surface); status active/queued/backburner + success criteria + pressure metadata (`support_style`, `push_when_stalled`, thresholds). Agent never mints; may surface inert candidate goals that do nothing until the user confirms.
- **DRIVE-02 — Progress velocity:** per-goal momentum computed from ground truth (git / state timestamps, milestone status) at appraisal-read time (NOT behind debounced reflection); stalled goals weighted louder, moving goals quiet; user-authorized push zones raise salience without changing truth/evidence.
- **DRIVE-03 — In-turn goal-aware appraisal:** appraisal output gains goal-aware noun-fields (relates-to-goal / stalled-N-days / contradicts-milestone) plus inspectable drive-effect fields (neutral read / drive read / salience change + reason), surfaced in-turn via the existing `pre_llm_call` path; no heartbeat this increment.
- **DRIVE-04 — Drive voice:** first-person owned-want rendering permitted ("I want X ready by Friday"); second-person imperatives still neutralized (SAFE-04 first-person carve-out); pattern-tested.
- **DRIVE-05 — Never-omit + anti-complacency invariant:** user-flagged priorities are never silently dropped from surfaced guidance; stalled user-priority goals with authorized pressure cannot be quietly downranked; repeated low-pressure handling flags possible under-support. Enforced and tested.
- **DRIVE-06 — Containment + adjustability:** drive kill switch (separate from the appraisal kill switch) + domain whitelist + energy-budget + pressure/support-style config keys; all fail-open; drive-off path tested.

**Success criteria:**
1. A real turn surfaces a user-minted goal with a grounded progress/stalled signal in the appraisal block, in the first-person owned-want voice
2. Anti-creep tests pass with the first-person carve-out; second-person directives still neutralized
3. Never-omit / anti-complacency tests: a flagged priority always appears in surfaced guidance, and a stalled user-authorized push zone cannot be silently treated as low salience
4. Drive kill switch off → zero goal-aware fields injected; appraisal otherwise unchanged; full fail-open preserved
5. Drive state round-trips in the anansi SQLite store (single sqlite surface); locked-DB / corrupt-DB degrade silently
6. Drive effect is inspectable: neutral read, drive read, and drive-caused salience change are visible enough to audit

**Design source:** `.planning/phases/06-proprietary-user-model-drive-design/06-CONTEXT.md`
**Status:** [x] ✓ Complete 2026-06-14 — 4/4 plans executed, 165 tests green, verifier passed (07-VERIFICATION.md). 2 non-blocking gaps logged (pressure columns not persisted; global drive_pressure config-only). Next: verify-work 7.
**Depends on:** Phase 6 (design)

## Coverage

| Phase | Requirements | Count |
|-------|--------------|-------|
| 1 | PLUG-01..04, STATE-01..05 | 9 |
| 2 | APPR-01..08, OBS-01 | 9 |
| 3 | SAFE-01..04, REFL-01..05 | 9 |
| 4 | PKG-01..04 | 4 |
| 5 | Audit gap closure — no new v1 requirement IDs | 0 |
| 6 | Proprietary design discussion — no v1 requirement IDs | 0 |
| **Total** | **31 / 31 v1 requirements** | ✓ 100% |
| 7 | DRIVE-01..06 (proprietary v2 — beyond v1 scope) | 6 |

</details>

## Imported Work

Phase identifiers map the seven source specs; they do not impose a new total ordering. The source backlog permits parity work opportunistically and security verification at any time. Worldview precedes episodes/user-dopamine within Phase 9; reconsolidation and its bounded heartbeat follow.

### Phase 8: Close Known Gaps

**Goal:** Reconcile and verify the eight known gaps against main, preserving fail-open and never-omit; account for the unmerged development branch.

**Depends on:** Phase 7

**Requirements:** REQ-001-close-known-gaps-fr-001, REQ-001-close-known-gaps-fr-002, REQ-001-close-known-gaps-fr-003, REQ-001-close-known-gaps-fr-004, REQ-001-close-known-gaps-fr-005, REQ-001-close-known-gaps-fr-006, REQ-001-close-known-gaps-fr-007, REQ-001-close-known-gaps-fr-008, REQ-001-close-known-gaps-fr-009, REQ-001-close-known-gaps-fr-010, REQ-001-close-known-gaps-fr-011, REQ-001-close-known-gaps-fr-012

**Status:** Pending; no implementation or completion implied

**Source:** `specs/001-close-known-gaps/spec.md`; complete acceptance contract in `.planning/intel/requirements.md`.

**Success criteria:** Map all source user-story scenarios and SC IDs to verification evidence during planning. This migration satisfies no feature acceptance criterion.

### Phase 9: Autobiographical User Model

**Goal:** Plan the scope recorded in specs/002-autobiographical-user-model/spec.md within the binding constitution and source acceptance contract.

**Depends on:** Phase 8

**Requirements:** REQ-002-autobiographical-user-model-fr-001, REQ-002-autobiographical-user-model-fr-002, REQ-002-autobiographical-user-model-fr-003, REQ-002-autobiographical-user-model-fr-004, REQ-002-autobiographical-user-model-fr-005, REQ-002-autobiographical-user-model-fr-006, REQ-002-autobiographical-user-model-fr-007, REQ-002-autobiographical-user-model-fr-008

**Status:** Pending; no implementation or completion implied

**Source:** `specs/002-autobiographical-user-model/spec.md`; complete acceptance contract in `.planning/intel/requirements.md`.

**Success criteria:** Map all source user-story scenarios and SC IDs to verification evidence during planning. This migration satisfies no feature acceptance criterion.

### Phase 10: Reconsolidation and Heartbeat

**Goal:** Plan the scope recorded in specs/003-reconsolidation-and-heartbeat/spec.md within the binding constitution and source acceptance contract.

**Depends on:** Phase 9

**Requirements:** REQ-003-reconsolidation-and-heartbeat-fr-001, REQ-003-reconsolidation-and-heartbeat-fr-002, REQ-003-reconsolidation-and-heartbeat-fr-003, REQ-003-reconsolidation-and-heartbeat-fr-004, REQ-003-reconsolidation-and-heartbeat-fr-005, REQ-003-reconsolidation-and-heartbeat-fr-006, REQ-003-reconsolidation-and-heartbeat-fr-007

**Status:** Pending; no implementation or completion implied

**Source:** `specs/003-reconsolidation-and-heartbeat/spec.md`; complete acceptance contract in `.planning/intel/requirements.md`.

**Success criteria:** Map all source user-story scenarios and SC IDs to verification evidence during planning. This migration satisfies no feature acceptance criterion.

### Phase 11: Interruption Lanes

**Goal:** Plan the scope recorded in specs/004-interruption-lanes/spec.md within the binding constitution and source acceptance contract.

**Depends on:** Phase 10; separate authority gate

**Requirements:** REQ-004-interruption-lanes-fr-001, REQ-004-interruption-lanes-fr-002, REQ-004-interruption-lanes-fr-003, REQ-004-interruption-lanes-fr-004, REQ-004-interruption-lanes-fr-005

**Status:** Deferred; constitution authority gate before implementation

**Source:** `specs/004-interruption-lanes/spec.md`; complete acceptance contract in `.planning/intel/requirements.md`.

**Success criteria:** Map all source user-story scenarios and SC IDs to verification evidence during planning. This migration satisfies no feature acceptance criterion.

### Phase 12: Tuning and Audit Surfaces

**Goal:** Plan the scope recorded in specs/005-tuning-and-audit-surfaces/spec.md within the binding constitution and source acceptance contract.

**Depends on:** Phase 10

**Requirements:** REQ-005-tuning-and-audit-surfaces-fr-001, REQ-005-tuning-and-audit-surfaces-fr-002, REQ-005-tuning-and-audit-surfaces-fr-003, REQ-005-tuning-and-audit-surfaces-fr-004

**Status:** Pending; no implementation or completion implied

**Source:** `specs/005-tuning-and-audit-surfaces/spec.md`; complete acceptance contract in `.planning/intel/requirements.md`.

**Success criteria:** Map all source user-story scenarios and SC IDs to verification evidence during planning. This migration satisfies no feature acceptance criterion.

### Phase 13: Deferred v1 and Parity

**Goal:** Plan the scope recorded in specs/006-deferred-v1-and-parity/spec.md within the binding constitution and source acceptance contract.

**Depends on:** Source evidence and compatibility gates; opportunistic

**Requirements:** REQ-006-deferred-v1-and-parity-fr-001, REQ-006-deferred-v1-and-parity-fr-002, REQ-006-deferred-v1-and-parity-fr-003, REQ-006-deferred-v1-and-parity-fr-004, REQ-006-deferred-v1-and-parity-fr-005, REQ-006-deferred-v1-and-parity-fr-006

**Status:** Pending; no implementation or completion implied

**Source:** `specs/006-deferred-v1-and-parity/spec.md`; complete acceptance contract in `.planning/intel/requirements.md`.

**Success criteria:** Map all source user-story scenarios and SC IDs to verification evidence during planning. This migration satisfies no feature acceptance criterion.

### Phase 14: Drive Security Verification

**Goal:** Plan the scope recorded in specs/007-drive-security-verification/spec.md within the binding constitution and source acceptance contract.

**Depends on:** Phase 7 baseline; may run at any time

**Requirements:** REQ-007-drive-security-verification-fr-001, REQ-007-drive-security-verification-fr-002, REQ-007-drive-security-verification-fr-003, REQ-007-drive-security-verification-fr-004

**Status:** Pending; no implementation or completion implied

**Source:** `specs/007-drive-security-verification/spec.md`; complete acceptance contract in `.planning/intel/requirements.md`.

**Success criteria:** Map all source user-story scenarios and SC IDs to verification evidence during planning. This migration satisfies no feature acceptance criterion.
