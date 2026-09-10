## REQ-001-close-known-gaps-fr-001
- source: specs/001-close-known-gaps/spec.md:202-203
- description: Persist per-goal pressure metadata through the single SQLite store so it round-trips a read/write cycle.
- acceptance: Given a goal minted with support_style=firm, push_when_stalled=true, stall_threshold_days=3, when persisted and read in a new snapshot, all three values are present and unchanged; given a persisted firm-pressure goal stalled past threshold, the under-support/push read reflects persisted pressure; given locked or corrupt state DB during pressure read, appraisal silently degrades to empty injection plus telemetry row.
- scope: per-goal pressure

## REQ-001-close-known-gaps-fr-002
- source: specs/001-close-known-gaps/spec.md:204-205
- description: Migrate an existing goals table without data loss and without raising; goals lacking new fields read documented defaults.
- acceptance: Given an existing populated goals table without new columns, it upgrades without data loss and without raising; goals predating columns read documented defaults; locked or corrupt DB during a new read/write degrades silently to empty injection plus telemetry.
- scope: goals migration

## REQ-001-close-known-gaps-fr-003
- source: specs/001-close-known-gaps/spec.md:206-207
- description: Read global drive_pressure and apply it to drive rendering, with invalid values coerced to the documented default.
- acceptance: Given drive_pressure=quiet, drive lines render at quiet level, distinct from standard/firm on the same goals; given malformed drive_pressure, config coerces to documented default and get_cfg does not raise.
- scope: global drive pressure

## REQ-001-close-known-gaps-fr-004
- source: specs/001-close-known-gaps/spec.md:208-209
- description: Emit a legible telemetry row whenever a config value is coerced away from the user-supplied value.
- acceptance: Given a malformed known-key value, config coercion emits a telemetry row naming key, rejected input, and applied default; given secret-like value, rejected value is redacted and never quoted verbatim; given valid config, no degradation telemetry emits.
- scope: configuration degradation telemetry

## REQ-001-close-known-gaps-fr-005
- source: specs/001-close-known-gaps/spec.md:210-211
- description: Redact secret-like config values in degradation telemetry and never raise or block the turn if telemetry storage is unavailable.
- acceptance: Given secret-like config value, degradation telemetry redacts the rejected value and never quotes it verbatim; given locked telemetry store, degradation-row emission fails open and never raises or blocks the turn.
- scope: configuration degradation telemetry

## REQ-001-close-known-gaps-fr-006
- source: specs/001-close-known-gaps/spec.md:212-214
- description: Bound rendered flagged wants with a proportionate cap while guaranteeing the highest-priority flagged wants render and visibly indicating withheld wants.
- acceptance: Given more flagged wants than cap, highest-priority flagged wants render and a visible marker gives N additional withheld wants; given wants at or under cap, all render with no marker; existing adversarial-crowding never-omit test still passes.
- scope: flagged wants

## REQ-001-close-known-gaps-fr-007
- source: specs/001-close-known-gaps/spec.md:215-216
- description: Keep the never-omit invariant under the cap, verified against persisted state rather than model output.
- acceptance: Given more flagged wants than cap, highest-priority flagged wants render and a visible withheld count marks others; existing never-omit adversarial-crowding test still passes so a flagged priority is never silently absent.
- scope: flagged wants

## REQ-001-close-known-gaps-fr-008
- source: specs/001-close-known-gaps/spec.md:217-218
- description: Avoid false-positive goal-to-signal associations caused by loose substring matching while preserving legitimate associations.
- acceptance: Given a goal key that is substring of an unrelated token, matching creates no spurious association; given a goal legitimately corresponding to a signal, association remains.
- scope: goal-to-signal matching

## REQ-001-close-known-gaps-fr-009
- source: specs/001-close-known-gaps/spec.md:219-220
- description: Handle stalled_days=0 with a well-formed fresh/active read distinct from stalled rendering and an empty line.
- acceptance: Given a goal with stalled_days=0, drive-want line renders a well-formed fresh/active read, not stalled and not blank.
- scope: fresh-goal rendering

## REQ-001-close-known-gaps-fr-010
- source: specs/001-close-known-gaps/spec.md:221-223
- description: Provide a documented single-command live-smoke lane for first-person owned-want voice and report an honest environment-gated outcome when no provider is reachable.
- acceptance: Given reachable model provider and persisted flagged goal, live drive smoke surfaces goal in first-person owned-want voice; given no reachable provider, live smoke reports honest environment-gated outcome and documented re-run lane remains ready.
- scope: live smoke verification

## REQ-001-close-known-gaps-fr-011
- source: specs/001-close-known-gaps/spec.md:224-225
- description: Rename master kill switch terminology in tests/comments to primary/main with no runtime behavior change.
- acceptance: Given renamed term, suite passes and no behavioral test assertion changes.
- scope: kill-switch terminology

## REQ-001-close-known-gaps-fr-012
- source: specs/001-close-known-gaps/spec.md:226-227
- description: Hold all constitution principles; keep full fail-open matrix and never-omit tests green without weakening a principle.
- acceptance: Full ./scripts/test.sh suite is green, including fail-open matrix and never-omit tests, with no assertion weakened relative to pre-change suite.
- scope: constitution compliance

## REQ-002-autobiographical-user-model-fr-001
- source: specs/002-autobiographical-user-model/spec.md:107-108
- description: Persist a worldview layer as typed, capped, decaying data on the single SQLite surface with supersession and contradiction edges.
- acceptance: Given a persisted worldview belief, a contradicting turn surfaces an observational worldview/contradiction note and never a second-person imperative; given a belief with supersession/contradiction edge, edge and belief round-trip intact; given locked/corrupt DB during worldview read, turn silently degrades to empty injection plus telemetry and never raises.
- scope: worldview store

## REQ-002-autobiographical-user-model-fr-002
- source: specs/002-autobiographical-user-model/spec.md:109-110
- description: Persist an episode/autobiography layer with an autonoesis tag, typed, capped, and decaying on the single SQLite surface.
- acceptance: Given a persisted episode, a related turn may surface an observational note grounded in it with no directive; given five model layers, schema defines each as typed, capped, decaying table on the single SQLite surface.
- scope: autobiographical episodes

## REQ-002-autobiographical-user-model-fr-003
- source: specs/002-autobiographical-user-model/spec.md:111-112
- description: Model the user's habit/motivation dynamics within whitelisted domains, override-able and never as an agent-reward signal.
- acceptance: Given user-dopamine model in whitelisted domain, appraisal may raise goal salience/ordering as inspectable drive effect, never agent-reward signal or truth/evidence change; given non-whitelisted domain it contributes nothing; given user override, next turn honors it.
- scope: user-dopamine

## REQ-002-autobiographical-user-model-fr-004
- source: specs/002-autobiographical-user-model/spec.md:113-114
- description: Surface all new layers only as observational appraisal notes with no directives or second-person imperatives.
- acceptance: Given a persisted worldview belief contradicted by a turn, appraisal surfaces an observational note, never second-person imperative; given a persisted episode and related turn, appraisal may surface observational note with no directive.
- scope: appraisal output

## REQ-002-autobiographical-user-model-fr-005
- source: specs/002-autobiographical-user-model/spec.md:115-116
- description: Make any salience or ordering effect inspectable as a drive effect separate from the neutral read.
- acceptance: Given user-dopamine model in whitelisted domain, appraisal may raise goal salience/ordering as an inspectable drive effect, never altering truth or evidence.
- scope: drive effects

## REQ-002-autobiographical-user-model-fr-006
- source: specs/002-autobiographical-user-model/spec.md:117-118
- description: Read freshness-critical signals at appraisal-read time from ground truth rather than through reflection debounce.
- acceptance: absent
- scope: freshness-critical signals

## REQ-002-autobiographical-user-model-fr-007
- source: specs/002-autobiographical-user-model/spec.md:119-120
- description: Apply caps, decay, and pruning to all new tables; locked/corrupt databases silently degrade; use no path literals or new dependencies.
- acceptance: Given locked/corrupt DB during worldview read, turn silently degrades to empty injection plus telemetry and never raises; locked/corrupt DB during any new-layer read/write silently degrades.
- scope: state tables

## REQ-002-autobiographical-user-model-fr-008
- source: specs/002-autobiographical-user-model/spec.md:121-122
- description: Give each layer a documented containment toggle so a user can turn it off.
- acceptance: absent
- scope: layer containment

## REQ-003-reconsolidation-and-heartbeat-fr-001
- source: specs/003-reconsolidation-and-heartbeat/spec.md:80-81
- description: Provide a scheduled heartbeat with execution mechanism chosen at plan phase and in-turn-only degradation if unavailable.
- acceptance: Given heartbeat fires between sessions, next user turn surfaces prepped context in-turn; given any heartbeat failure, it never raises, blocks, or emits outbound message; given unavailable heartbeat mechanism, degrade to in-turn-only behavior and never error.
- scope: scheduled heartbeat

## REQ-003-reconsolidation-and-heartbeat-fr-002
- source: specs/003-reconsolidation-and-heartbeat/spec.md:82-83
- description: Limit heartbeat to state preparation and next-real-turn surfacing; it must not interrupt, notify, or emit outbound communication.
- acceptance: Given heartbeat fires between sessions, next user turn surfaces prepped context in-turn; given failure, it never raises, blocks, or emits outbound message; given drive/heartbeat switch off, it does nothing.
- scope: next-turn context

## REQ-003-reconsolidation-and-heartbeat-fr-003
- source: specs/003-reconsolidation-and-heartbeat/spec.md:84-85
- description: Make heartbeat debounced and idempotent so double firing is a no-op.
- acceptance: Given heartbeat fires twice, comparison shows second firing is a no-op, idempotent and watermarked.
- scope: heartbeat idempotency

## REQ-003-reconsolidation-and-heartbeat-fr-004
- source: specs/003-reconsolidation-and-heartbeat/spec.md:86-87
- description: Carry a per-heartbeat energy/attention budget with a hard cap per wakeup.
- acceptance: Per-heartbeat energy budget hard-caps costed actions; exceeding cap withholds work visibly rather than silently.
- scope: energy budget

## REQ-003-reconsolidation-and-heartbeat-fr-005
- source: specs/003-reconsolidation-and-heartbeat/spec.md:88-89
- description: Propagate belief flips across dependent memories, goals, episodes, and worldview edges on the single SQLite surface, idempotently on heartbeat.
- acceptance: Given worldview belief flips, heartbeat re-evaluates items depending on old belief and persists propagation; given propagation interrupted mid-process, resumption is idempotent with no double-application.
- scope: reconsolidation

## REQ-003-reconsolidation-and-heartbeat-fr-006
- source: specs/003-reconsolidation-and-heartbeat/spec.md:90-91
- description: Surface reconsolidation output observationally in-turn, never as a directive or silent omission of a user-flagged priority.
- acceptance: Given reconsolidation result touches user-flagged priority, next-turn surfacing never silently drops that priority.
- scope: reconsolidation output

## REQ-003-reconsolidation-and-heartbeat-fr-007
- source: specs/003-reconsolidation-and-heartbeat/spec.md:92-93
- description: Provide a separate heartbeat/drive kill switch and retain fail-open, zero-dependency, and config-path constraints.
- acceptance: Given any heartbeat failure, it never raises, blocks, or emits outbound message; given drive/heartbeat kill switch off, it does nothing.
- scope: heartbeat containment

## REQ-004-interruption-lanes-fr-001
- source: specs/004-interruption-lanes/spec.md:73-74
- description: Allow code-red only for objective user-defined conditions attached to user-flagged goals; the agent cannot self-declare urgency.
- acceptance: Given objective user-defined trigger on user-flagged goal, lane may interrupt on gentlest channel within hard rate limit; given only agent urgency assessment, lane cannot interrupt; given switch off or non-whitelisted domain, lane never fires; repeated triggers over rate limit are throttled.
- scope: code-red interruption lane

## REQ-004-interruption-lanes-fr-002
- source: specs/004-interruption-lanes/spec.md:75-76
- description: Keep code-red off by default and opt-in with a separate interrupt kill switch, domain whitelist, and hard rate limit on the gentlest channel.
- acceptance: Given objective user-defined trigger on user-flagged goal, lane may interrupt only within hard rate limit; given switch off or domain not whitelisted, lane never fires; repeated triggers exceeding rate limit are throttled.
- scope: code-red interruption lane

## REQ-004-interruption-lanes-fr-003
- source: specs/004-interruption-lanes/spec.md:77-78
- description: Keep proactive-notify L2 off by default and opt-in, gated on a verified desktop cold-respawn fix.
- acceptance: Given verified desktop cold-respawn fix and L2 opt-in, heartbeat may deliver surfaceable item on gentlest channel; given fix absent or L2 not opted-in, no proactive notification emits.
- scope: proactive notification L2

## REQ-004-interruption-lanes-fr-004
- source: specs/004-interruption-lanes/spec.md:79-80
- description: Emit from neither lane unless preconditions hold; both fail open and do not violate no-outreach when disabled.
- acceptance: Given switch off or non-whitelisted domain, lane never fires; given L2 defect unfixed or not opted-in, no proactive notification emits; unavailable channel degrades to next-turn surfacing without error or item loss; rate-limit withholding records and never spams.
- scope: interruption lanes

## REQ-004-interruption-lanes-fr-005
- source: specs/004-interruption-lanes/spec.md:81-82
- description: Make every interruption auditable by trigger, channel, and rate budget.
- acceptance: Code-red fires in 0% of cases without met user-defined trigger and every fire is attributable to one; lanes are off by default and each fire respects kill switch, whitelist, and rate limit.
- scope: interrupt audit records

## REQ-005-tuning-and-audit-surfaces-fr-001
- source: specs/005-tuning-and-audit-surfaces/spec.md:88-90
- description: Let a desktop config panel edit cadence, per-heartbeat budgets, and domain whitelists; changes take effect on the next config read and malformed input emits config_degraded telemetry.
- acceptance: Given panel changes per-heartbeat energy budget, next heartbeat uses new budget; given panel changes domain whitelist, next turn surfaces drive signals only from new whitelist; given malformed panel input, config coerces to documented default, emits config_degraded, and never raises.
- scope: desktop configuration panel

## REQ-005-tuning-and-audit-surfaces-fr-002
- source: specs/005-tuning-and-audit-surfaces/spec.md:91-92
- description: Read persisted cross-session history on heartbeat and observationally surface a possible-under-support flag without false alarms when support is adequate.
- acceptance: Given N sessions of low-pressure handling of stalled push_when_stalled goal, heartbeat audit surfaces possible-under-support flag observationally next turn; given adequate support, audit raises no flag.
- scope: under-response audit

## REQ-005-tuning-and-audit-surfaces-fr-003
- source: specs/005-tuning-and-audit-surfaces/spec.md:93-94
- description: Persist would-have-said items and surface them only in the next turn's appraisal, never outbound; cap and prune them.
- acceptance: Given would-have-said item, next turn shows it in appraisal block and never outbound; given empty outbox, nothing surfaces.
- scope: passive outbox

## REQ-005-tuning-and-audit-surfaces-fr-004
- source: specs/005-tuning-and-audit-surfaces/spec.md:95-96
- description: Keep all three surfaces fail-open, zero-dependency, config-path based, and unable to self-modify prompts or thresholds.
- acceptance: Fail-open, never-omit, and no-outreach tests are green with no new dependencies.
- scope: tuning and audit surfaces

## REQ-006-deferred-v1-and-parity-fr-001
- source: specs/006-deferred-v1-and-parity/spec.md:96-97
- description: Implement D5 salience filtering only after an upstream post_memory_prefetch-style hook exists; until then preserve a documented no-op.
- acceptance: Given upstream post_memory_prefetch hook, Anansi can re-rank injected memory observationally without dropping user-flagged items; given no hook, D5 does nothing and is documented pending-upstream with no error or false claim.
- scope: memory salience filtering

## REQ-006-deferred-v1-and-parity-fr-002
- source: specs/006-deferred-v1-and-parity/spec.md:98-99
- description: Re-verify and record upstream-main manifest, ctx.llm, pip_dependencies, and host-standard-suite parity.
- acceptance: Given current upstream main, plugin load accepts manifest hook key and ctx.llm resolves or documented fallback is taken, with result recorded; given current upstream main, host-standard suite pass/fail is recorded.
- scope: upstream host parity

## REQ-006-deferred-v1-and-parity-fr-003
- source: specs/006-deferred-v1-and-parity/spec.md:100-101
- description: Deepen dimensional affect and active-concern continuity without output-tone modulation or exceeding state caps.
- acceptance: Given affect telemetry, D3 depth displays valence/arousal decay-to-baseline as inspectable state and never modulates output tone; given concern history, D6 tuning decays/prunes stale concerns on validated policy.
- scope: dimensional affect and active-concern continuity

## REQ-006-deferred-v1-and-parity-fr-004
- source: specs/006-deferred-v1-and-parity/spec.md:102
- description: Add a WAL-on-network-mount startup check or documented caveat.
- acceptance: Given HERMES_HOME network mount, store initialization warns or documented caveat exists so WAL corruption risk is not silent.
- scope: SQLite WAL and network mounts

## REQ-006-deferred-v1-and-parity-fr-005
- source: specs/006-deferred-v1-and-parity/spec.md:103
- description: Decide and record auxiliary-model routing through ctx.register_auxiliary_task or the bespoke config key.
- acceptance: Given host ctx.register_auxiliary_task, routing evaluation records a decision to adopt it or retain bespoke config key.
- scope: auxiliary-model routing

## REQ-006-deferred-v1-and-parity-fr-006
- source: specs/006-deferred-v1-and-parity/spec.md:104
- description: Keep all work fail-open, zero-dependency, and config-path based.
- acceptance: D5 either works through real host hook or is documented tested no-op; upstream parity is recorded; D3/D6 stay inside state caps with no output-tone modulation; network-mount guard and auxiliary-model routing decision exist.
- scope: deferred v1 and parity

## REQ-007-drive-security-verification-fr-001
- source: specs/007-drive-security-verification/spec.md:82-84
- description: Produce a drive-layer security document with a STRIDE register and mitigation trace for goal-text rendering, ground-truth reads, configuration, and first-person voice carve-out.
- acceptance: Given drive inputs, threat register has each STRIDE category with mitigation traced to code/tests; given never-omit, SAFE-04, and anti-creep invariants, document confirms enforcement and tests or flags gap.
- scope: drive security

## REQ-007-drive-security-verification-fr-002
- source: specs/007-drive-security-verification/spec.md:85-86
- description: Run live Criterion-1 smoke against a provider and record PASS or honest INCONCLUSIVE reason; close spec-001 task T029 only on PASS.
- acceptance: Given reachable provider, live drive smoke exits 0 with first-person want line; given no provider, it exits 2 INCONCLUSIVE honestly and never false-passes.
- scope: live drive verification

## REQ-007-drive-security-verification-fr-003
- source: specs/007-drive-security-verification/spec.md:87-88
- description: Verify APPR-06 trust fallback live on a fast-enough host or record accepted deferral with reason; do not claim verification without evidence.
- acceptance: Given fast-enough host model and trust-gate denial, telemetry records completed trust_fallback retry; given slow host model, fallback exceeding deadline degrades to fail-open timeout and is recorded rather than treated as bug.
- scope: trust-gate fallback

## REQ-007-drive-security-verification-fr-004
- source: specs/007-drive-security-verification/spec.md:89-90
- description: Make no code change for FR-002 or FR-003 unless a defect is found; the existing harnesses report honest exit codes.
- acceptance: 07-SECURITY.md exists with mitigations traced to code/tests; live drive outcome is recorded and closes Phase-7 Criterion 1 and T029 only on PASS; APPR-06 is live-produced or accepted-deferred with concrete reason.
- scope: verification debt


## REQ-001-close-known-gaps-acceptance-contract
- source: specs/001-close-known-gaps/spec.md:1-269
- description: Full source feature contract, preserving feature status, governing constraints, user scenarios and testing, acceptance scenarios, edge cases, functional requirements, success criteria, assumptions, dependencies, and out-of-scope qualifiers.
- acceptance:
````text
DATA_L2N4P6R8_START
# Feature Specification: Anansi Completion — Close Known Gaps

**Feature Branch**: `001-close-known-gaps`

**Created**: 2026-07-05

**Status**: Draft

**Input**: User description: "Close all known open gaps so the Phase 7 Drive/Accountability increment is verified-complete and shippable — hardening/finishing work on the existing plugin, not a new capability. Every change must hold the constitution (fail-open, no-autonomy, never-omit, single SQLite surface, zero new deps, paths-from-config)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Per-goal pressure survives a restart (Priority: P1)

Dr. Mani mints a goal with a specific support style ("firm") and a push-when-stalled flag, closes the
session, and returns later. The goal's pressure settings are still in effect — the drive read treats
that goal exactly as configured, because the pressure metadata was persisted, not held only in memory.

**Why this priority**: Per-goal pressure is a headline promise of the Drive layer. Today it only works
via injected test dicts and is lost on any real round-trip through the store — the shipped `goals` DDL
omits the pressure columns. Until it persists, the feature is demonstrably incomplete.

**Independent Test**: Mint a goal with non-default pressure, write it through the store, read it back in
a fresh snapshot, and confirm the pressure fields round-trip and drive the render. Locked-DB / corrupt-DB
still degrade silently.

**Acceptance Scenarios**:

1. **Given** a goal minted with `support_style=firm`, `push_when_stalled=true`, `stall_threshold_days=3`,
   **When** it is persisted and then read back in a new snapshot, **Then** all three pressure values are
   present on the goal and unchanged.
2. **Given** a persisted goal with firm pressure that has stalled past its threshold, **When** the drive
   block renders, **Then** the under-support/push read reflects the persisted pressure, not a default.
3. **Given** the state DB is locked or corrupt during the pressure read, **When** the appraisal runs,
   **Then** the turn degrades silently to an empty injection plus a telemetry row (fail-open holds).

---

### User Story 2 — Global drive pressure actually takes effect (Priority: P1)

Dr. Mani sets `drive_pressure: quiet` (or `firm`) in config expecting the whole drive layer to soften or
sharpen. Today the key is accepted and documented but never read, so the setting silently does nothing.
After this change, the global setting visibly changes how drive lines render.

**Why this priority**: A config key that is silently inert is a trust bug — the user believes they tuned
behavior that never changed. It is also a small, contained wiring fix.

**Independent Test**: Set `drive_pressure` to each valid value, render the drive block on identical state,
and confirm the output differs per setting. Invalid values coerce to the default without raising.

**Acceptance Scenarios**:

1. **Given** `drive_pressure=quiet`, **When** the drive block renders, **Then** drive lines render at the
   quiet level (distinct from standard/firm) on the same underlying goals.
2. **Given** a malformed `drive_pressure` value, **When** config is read, **Then** it coerces to the
   documented default and `get_cfg` does not raise.

---

### User Story 3 — Malformed config is legible, not silent (Priority: P1)

Dr. Mani mistypes a config value. Instead of the plugin silently swallowing it and using a default with
no trace, a telemetry row records that a specific key was rejected, what value was rejected, and what
default was substituted — so a degraded config is discoverable after the fact.

**Why this priority**: Silent config degradation is the exact "make malformed config legible" audit item
(#5). It converts an invisible failure into an inspectable one without changing fail-open behavior.

**Independent Test**: Feed several malformed config keys, run the config read, and confirm one telemetry
row per degraded key with key name, rejected value (secret-safe), and applied default — and that nothing
raised.

**Acceptance Scenarios**:

1. **Given** a malformed value for a known key, **When** config is coerced, **Then** a telemetry row is
   emitted naming the key, the rejected input, and the default applied.
2. **Given** a config value that looks like a secret/credential, **When** degradation telemetry is
   emitted, **Then** the rejected value is redacted, never quoted verbatim.
3. **Given** all config is valid, **When** config is read, **Then** no degradation telemetry is emitted.

---

### User Story 4 — Flagged wants are bounded but never dropped (Priority: P2)

When Dr. Mani has flagged many priorities, the drive block still surfaces the most critical flagged wants
first and visibly, but does not flood the block with an unbounded list. The cap trims only the
least-critical flagged tail, and does so visibly — the highest-priority flagged goals always appear.

**Why this priority**: Never-omit (Principle III) must be preserved, but an unbounded flagged list (only
the ≤50 global CAPS ceiling today) can crowd out everything else. A proportionate, visible cap protects
both invariants.

**Independent Test**: Persist more flagged goals than the cap, render, and confirm the top-priority
flagged wants appear, the tail is trimmed with a visible indication of how many were withheld, and the
never-omit tests still pass.

**Acceptance Scenarios**:

1. **Given** more flagged wants than the cap, **When** the block renders, **Then** the highest-priority
   flagged wants render and a visible marker indicates that N additional flagged wants were withheld.
2. **Given** flagged wants at or under the cap, **When** the block renders, **Then** all render with no
   withheld marker.
3. **Given** the existing never-omit adversarial-crowding test, **When** it runs against the capped
   render, **Then** it still passes (a flagged priority is never silently absent).

---

### User Story 5 — Goal matching is precise, not loose (Priority: P2)

A goal titled "auth" does not get spuriously associated with an unrelated signal that merely contains the
substring "auth" (e.g. "author"). Legitimate associations still match.

**Why this priority**: Loose substring matching creates false-positive goal associations, which mislead
the drive read. Tightening it improves signal quality without new machinery.

**Independent Test**: Provide goal/signal pairs that currently false-match under substring logic and pairs
that should legitimately match; confirm the false matches drop and the true matches survive.

**Acceptance Scenarios**:

1. **Given** a goal whose key is a substring of an unrelated token, **When** matching runs, **Then** no
   spurious association is created.
2. **Given** a goal that legitimately corresponds to a signal, **When** matching runs, **Then** the
   association is still made.

---

### User Story 6 — Freshly-touched goals read correctly at 0 days (Priority: P2)

A goal touched today (0 days stalled) renders as active/fresh, not as blank or mistakenly stalled.

**Why this priority**: The `stalled_days:0` edge case is a small correctness bug in the drive-want render
that misrepresents ground truth for the most recently active goals.

**Independent Test**: Render a goal with `stalled_days=0` and confirm the want line reads as fresh/active
and is well-formed, distinct from both the stalled rendering and an empty line.

**Acceptance Scenarios**:

1. **Given** a goal with `stalled_days=0`, **When** the drive-want line renders, **Then** it renders a
   well-formed fresh/active read (not stalled, not blank).

---

### User Story 7 — Live turn proves the first-person want voice (Priority: P3)

Against a reachable model provider, a real Hermes turn surfaces a user-minted goal in the first-person
owned-want voice — closing the one live acceptance criterion (Criterion 1) that was left inconclusive
because providers were unavailable.

**Why this priority**: The behavior is unit-proven; only the live end-to-end confirmation is outstanding,
and it is blocked purely on environment (provider credentials). It should be a one-command re-run once a
provider is reachable.

**Independent Test**: With a provider configured, run the drive live-smoke lane and confirm a real turn's
appraisal block contains a first-person want line grounded in a persisted goal.

**Acceptance Scenarios**:

1. **Given** a reachable model provider and a persisted flagged goal, **When** the live drive smoke runs,
   **Then** the turn's appraisal surfaces that goal in the first-person owned-want voice.
2. **Given** no provider is reachable, **When** the live smoke runs, **Then** it reports an honest
   environment-gated outcome (not a false pass) and the documented re-run lane remains ready.

---

### User Story 8 — Terminology no longer collides with the git trunk (Priority: P3)

The "master kill switch" term in tests/comments is renamed to "primary/main" so it does not read as a
reference to the git trunk (which was renamed master→main). No behavior changes.

**Why this priority**: Pure clarity/cosmetic cleanup; low risk, removes a naming landmine for future
readers.

**Independent Test**: Grep confirms the old term is gone from tests/comments, the suite still passes, and
no runtime code path changed.

**Acceptance Scenarios**:

1. **Given** the renamed term, **When** the suite runs, **Then** it passes and no behavioral test changed
   its assertions.

---

### Edge Cases

- **Pressure migration on an existing DB**: an already-populated `goals` table without the new columns
  must upgrade without data loss and without raising; goals predating the columns read as documented
  defaults.
- **Locked/corrupt DB during any new read/write**: degrades silently to empty injection + telemetry.
- **Config degradation telemetry under a locked telemetry store**: emitting the degradation row must
  itself fail open (never raise, never block the turn).
- **Flagged-want cap == 0 or negative**: coerces to a safe floor that still honors never-omit for the
  single highest-priority flagged goal.
- **All goals fresh (every `stalled_days=0`)**: block renders active reads with no stalled/under-support
  language.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST persist per-goal pressure metadata (`support_style`, `push_when_stalled`,
  `stall_threshold_days`) through the single SQLite store so it round-trips a read/write cycle.
- **FR-002**: The persistence change MUST migrate an existing `goals` table without data loss and without
  raising; goals lacking the new fields MUST read documented defaults.
- **FR-003**: The system MUST read the global `drive_pressure` setting and apply it to drive rendering
  (quiet / standard / firm), with invalid values coerced to the documented default.
- **FR-004**: The system MUST emit a legible telemetry row whenever a config value is coerced away from
  the user-supplied value, identifying the key, the rejected value, and the applied default.
- **FR-005**: Config-degradation telemetry MUST redact secret-like values and MUST NOT raise or block the
  turn even if the telemetry store is unavailable.
- **FR-006**: The system MUST bound the number of rendered flagged wants with a proportionate cap while
  GUARANTEEING the highest-priority flagged wants always render; withheld flagged wants MUST be indicated
  visibly.
- **FR-007**: The never-omit invariant MUST continue to hold under the new cap — a flagged priority MUST
  never be silently absent from the surfaced block (verified against persisted state, not model output).
- **FR-008**: Goal-to-signal matching MUST avoid false-positive associations caused by loose substring
  matching, while preserving legitimate associations.
- **FR-009**: The drive-want render MUST correctly handle `stalled_days=0`, producing a well-formed
  fresh/active read distinct from the stalled rendering and from an empty line.
- **FR-010**: The system MUST provide a documented, single-command live-smoke lane that confirms a real
  turn surfaces a persisted goal in the first-person owned-want voice, and MUST report an honest
  environment-gated outcome (never a false pass) when no provider is reachable.
- **FR-011**: The "master kill switch" terminology in tests/comments MUST be renamed to "primary/main"
  with no change to any runtime behavior.
- **FR-012**: Every change MUST hold all constitution principles; the full fail-open matrix and the
  never-omit tests MUST remain green, and no principle may be weakened to pass a check.

### Key Entities *(include if feature involves data)*

- **Goal**: a user-minted objective persisted in the store. Gains persisted pressure attributes
  (`support_style`, `push_when_stalled`, `stall_threshold_days`) in addition to its existing status,
  success criteria, and flagged-priority bit. Momentum/`stalled_days` remain derived at read time, not
  persisted.
- **Config degradation event**: an observable record (telemetry row) describing a rejected config value —
  key, redacted rejected input, applied default — emitted only when degradation occurs.
- **Drive render block**: the surfaced drive output whose flagged-want lines are now bounded and whose
  global pressure level is now driven by config.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the eight named gaps (G1–G8) are closed or, for the environment-gated live check,
  left with a documented ready-to-run closure lane and an honest gated outcome.
- **SC-002**: Per-goal pressure round-trips the store in 100% of read-back checks; zero data loss on
  migration of a pre-existing goals table.
- **SC-003**: Each valid `drive_pressure` setting produces a distinguishable rendered result on identical
  state; every invalid value coerces to default with zero raised exceptions.
- **SC-004**: Every config-degradation event produces exactly one legible, secret-safe telemetry row;
  valid config produces zero such rows.
- **SC-005**: Under adversarial flagged-want crowding, the highest-priority flagged want is present in
  100% of renders, and the block never exceeds the configured flagged-want cap plus the visible
  withheld-count marker.
- **SC-006**: The full test suite (`./scripts/test.sh`) is green, including the fail-open matrix and the
  never-omit tests, with no assertion weakened relative to the pre-change suite.

## Assumptions

- The existing single-SQLite-surface store (`store.py`) and the existing telemetry surface are reused; no
  new storage or dependency is introduced.
- Momentum (`stalled_days`) remains a read-time derivation from ground truth; only the user's pressure
  *definition* is persisted (consistent with the constitution's read-time-truth principle).
- "Proportionate cap" for flagged wants is a small configured integer with a safe floor that always
  honors never-omit for at least the single highest-priority flagged goal; the exact default is chosen at
  plan time from existing CAPS conventions.
- Live Criterion-1 (G1) may remain outstanding at ship time strictly due to provider availability; its
  closure lane and honest gated reporting are the deliverable, not the live credentials themselves.
- The rename (G8) touches only tests/comments/wording, never runtime branching logic.
DATA_L2N4P6R8_END
````
- scope: per-goal pressure; global drive pressure; configuration degradation telemetry; flagged wants; goal-to-signal matching; freshly-touched rendering; live smoke verification; kill-switch terminology; constitution compliance; success criteria: 001-close-known-gaps-SC-001, 001-close-known-gaps-SC-002, 001-close-known-gaps-SC-003, 001-close-known-gaps-SC-004, 001-close-known-gaps-SC-005, 001-close-known-gaps-SC-006

## REQ-002-autobiographical-user-model-acceptance-contract
- source: specs/002-autobiographical-user-model/spec.md:1-148
- description: Full source feature contract, preserving feature status, governing constraints, user scenarios and testing, acceptance scenarios, edge cases, functional requirements, success criteria, assumptions, dependencies, and out-of-scope qualifiers.
- acceptance:
````text
DATA_M3O5Q7S9_START
# Feature Specification: Layered Autobiographical User Model

**Feature Branch**: `002-autobiographical-user-model`

**Created**: 2026-07-05

**Status**: Backlog (deferred proprietary v2 — designed in Phase 6, not yet built)

**Input**: Phase 6 proprietary design. The proprietary direction reintroduces "a layered autobiographical
user model, worldview, user-dopamine" (`.planning/phases/06-.../06-CONTEXT.md:14-16`). Agreed working order
for the later increments: **worldview store → episode/autobiography + user-dopamine → reconsolidation**
(`06-CONTEXT.md:93-94`, `06-DISCUSSION-LOG.md:54-55`). Reconsolidation is a separate spec (003).

This captures a designed-but-unbuilt direction. It MUST be re-scoped (`/speckit-clarify` → `/speckit-plan`)
before implementation — Phase 6 left the internals to plan-phase.

## Governing constraints (constitution + Phase 6 locks)

- All state stays on the **single anansi SQLite surface** (`store.py`) — new tables, no new DB file, no
  daemon (`06-CONTEXT.md:97-99`; rejected: separate user-model DB, `06-DISCUSSION-LOG.md:61-62`).
- Fail-open, no-autonomy, never-omit, zero-new-deps, paths-from-config all still hold (constitution I–VII).
- Hindsight remains the sole MemoryProvider; this plugin never takes the provider slot (`06-CONTEXT.md:21-23`).
- Canonical layer→mechanism→value-order mapping lives in
  `.planning/research/USER-MODEL-SOURCES-2026-06-10.md` — read it before planning.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Worldview store (Priority: P1) — first of the later increments

Anansi persists the user's stable beliefs/worldview **as data** (not as free text buried in memory), so
later appraisal can notice when the current turn contradicts a held belief, and so reconsolidation (spec
003) has something to propagate belief-flips across.

**Why this priority**: It is the agreed next increment (`06-CONTEXT.md:93`, survey's #1,
`06-DISCUSSION-LOG.md:52-53`) and the substrate reconsolidation requires. "Worldview-as-data … [is one of]
the high-novelty later increments" (`06-CONTEXT.md:130-131`).

**Independent Test**: Persist a worldview belief; a later turn whose content contradicts it surfaces an
observational contradiction/worldview note (never a directive); the belief round-trips the store and
degrades silently on locked/corrupt DB.

**Acceptance Scenarios**:
1. **Given** a persisted worldview belief, **When** a turn's content contradicts it, **Then** the appraisal
   surfaces an observational worldview/contradiction note — never a second-person imperative.
2. **Given** a worldview belief with a supersession/contradiction edge (per USER-MODEL-SOURCES candidate #1),
   **When** it is read back, **Then** the edge and belief round-trip intact.
3. **Given** a locked/corrupt DB, **When** the worldview read runs, **Then** the turn degrades silently
   (empty injection + telemetry), never raises.

---

### User Story 2 — Episode / autobiography layer (Priority: P2)

Anansi persists episodic/autobiographical structure about the user (events, with autonoesis — the
self-knowing "this happened to me" tag per USER-MODEL-SOURCES candidate #3), so appraisal can ground goal
and worldview signals in the user's actual history.

**Why this priority**: Middle of the agreed order (`06-CONTEXT.md:93-94`). Part of the "layered
autobiographical user model" the direction reintroduces (`06-CONTEXT.md:14-16`;
`.planning/research/DESIGN-REWIND-2026-06-10.md:29-33` position 5 — episodic/semantic/procedural/strategic/
worldview/goal typing, of which only the goal layer is partly realized in Phase 7).

**Independent Test**: Persist an episode; a related later turn surfaces an observational episodic note
grounded in it; round-trips; fail-open.

**Acceptance Scenarios**:
1. **Given** a persisted episode, **When** a related turn occurs, **Then** appraisal may surface an
   observational note grounded in that episode (no directive).
2. **Given** the five model layers (episodic/semantic/procedural/strategic/worldview/goal), **When** the
   schema is defined, **Then** each layer is a typed, capped, decaying table on the single sqlite surface.

---

### User Story 3 — User-dopamine (habit/motivation sync) (Priority: P2)

Anansi models the **user's** motivation/habit dynamics (not the agent's reward), bounded to whitelisted
domains and override-able, so drive salience can reflect the user's real momentum patterns.

**Why this priority**: Paired with episode/autobiography in the agreed order (`06-CONTEXT.md:93-94`;
USER-MODEL-SOURCES candidate #4 "user-dopamine habit sync").

**Independent Test**: With a user-dopamine model in a whitelisted domain, a habit signal adjusts a goal's
salience/ordering (never truth), and the effect is inspectable and override-able; outside the whitelist it
does nothing.

**Acceptance Scenarios**:
1. **Given** a user-dopamine model in a whitelisted domain, **When** appraisal runs, **Then** it may raise a
   goal's salience/ordering as an **inspectable** drive effect — never as an agent-reward signal, never
   altering truth/evidence.
2. **Given** a domain NOT on the whitelist, **When** appraisal runs, **Then** user-dopamine contributes
   nothing (containment holds).
3. **Given** the user overrides a user-dopamine inference, **When** the next turn runs, **Then** the
   override is honored.

---

### Edge Cases
- Empty / brand-new user model → no worldview/episode notes; behaves exactly like today (no manufactured
  block; APPR-05 suppression holds).
- Contradiction between a worldview belief and a user-minted goal → surfaced observationally, never resolved
  autonomously (never-omit; the user decides).
- Locked/corrupt DB during any new-layer read/write → silent degrade.
- User-dopamine in a domain later removed from the whitelist → immediately stops contributing.

## Requirements *(mandatory)*

- **FR-001**: Persist a **worldview** layer (stable beliefs) as typed data on the single sqlite surface,
  with supersession + contradiction edges (USER-MODEL-SOURCES #1), capped + decaying like every state table.
- **FR-002**: Persist an **episode/autobiography** layer (events with an autonoesis tag), typed, capped,
  decaying, on the single sqlite surface.
- **FR-003**: Model **user-dopamine** (the user's habit/motivation dynamics) bounded to whitelisted domains,
  override-able, and NEVER an agent-reward signal.
- **FR-004**: All new layers surface ONLY observational notes in the appraisal; no directives, no second-
  person imperatives (SAFE-04 / constitution II).
- **FR-005**: Any salience/ordering effect from these layers MUST be inspectable as a drive effect, separate
  from the neutral read (constitution VI; `06-CONTEXT.md:67-72`).
- **FR-006**: All reads happen at appraisal-read time from ground truth where applicable; nothing gated
  behind the reflection debounce for freshness-critical signals (constitution IV; `06-CONTEXT.md:100-103`).
- **FR-007**: All new tables have caps + decay + pruning (STATE-04 parity); locked/corrupt DB degrades
  silently; no path literals; zero new deps.
- **FR-008**: Each layer has a documented containment toggle (extends the drive kill switch + domain
  whitelist model) so a user can turn any layer off.

## Key Entities *(data)*
- **Worldview belief** — a held belief with supersession + contradiction edges; typed, capped, decaying.
- **Episode** — an autobiographical event with an autonoesis tag; typed, capped, decaying.
- **User-dopamine signal** — the user's per-domain habit/motivation state; whitelist-bounded, override-able.
- **Drive-effect field** — the inspectable record of how a layer changed appraisal salience (reuses the
  Phase-7 neutral-read/drive-read/drive-effect rendering).

## Success Criteria *(mandatory)*
- **SC-001**: The five autobiographical layers (episodic/semantic/procedural/strategic/worldview/goal) are
  each a typed, capped, decaying table on the single sqlite surface, with the goal layer (Phase 7) unchanged.
- **SC-002**: A worldview contradiction surfaces observationally in ≥1 grounded scenario, with zero
  directive-language findings.
- **SC-003**: User-dopamine effect is 100% contained to whitelisted domains and 100% inspectable/override-
  able; zero agent-reward semantics.
- **SC-004**: Full fail-open matrix + never-omit tests remain green; no new pip dependency; no new DB file.

## Assumptions
- Exact schemas + metrics are set at plan-phase (`06-CONTEXT.md:108-109` left this to Agent's Discretion).
- Reconsolidation (belief-flip propagation over the worldview store) is spec 003, not here.
- Depth is incremental: ship minimal per layer, validate signal quality before deepening
  (FEATURES.md D3/D5/D6 "second-wave" posture).

## Out of Scope (here)
- Reconsolidation / heartbeat (spec 003). Interruption lanes (spec 004). Config panel (spec 005).
- Any agent-reward/dopamine (permanent anti-feature). Any autonomy/outreach.
DATA_M3O5Q7S9_END
````
- scope: worldview store; autobiographical episodes; user-dopamine; drive effects; layer containment; success criteria: 002-autobiographical-user-model-SC-001, 002-autobiographical-user-model-SC-002, 002-autobiographical-user-model-SC-003, 002-autobiographical-user-model-SC-004

## REQ-003-reconsolidation-and-heartbeat-acceptance-contract
- source: specs/003-reconsolidation-and-heartbeat/spec.md:1-115
- description: Full source feature contract, preserving feature status, governing constraints, user scenarios and testing, acceptance scenarios, edge cases, functional requirements, success criteria, assumptions, dependencies, and out-of-scope qualifiers.
- acceptance:
````text
DATA_N4P6R8T0_START
# Feature Specification: Reconsolidation + Scheduled Heartbeat

**Feature Branch**: `003-reconsolidation-and-heartbeat`

**Created**: 2026-07-05

**Status**: Backlog (deferred proprietary v2 — the "crown jewel" + the mechanism it requires)

**Input**: "Worldview-as-data and reconsolidation (belief-flip propagation) are the high-novelty later
increments; **reconsolidation structurally requires the heartbeat**" (`06-CONTEXT.md:130-131`). The heartbeat
"is introduced in the increment that first requires between-session work (reconsolidation/consolidation)"
(`06-CONTEXT.md:94`). LAST in the agreed working order (`06-CONTEXT.md:93-94`). Depends on the worldview
store (spec 002).

## Governing constraints
- Single sqlite surface, fail-open, no-autonomy, never-omit, zero-new-deps (constitution I–VII).
- Heartbeat is **not** an anti-feature violation: the firm exclusion is "no timers/daemons/scheduled
  appraisal that fire without a real turn" for v1; Phase 6 explicitly OVERRIDES the heartbeat exclusion for
  the proprietary direction (`06-CONTEXT.md:24-26`) — BUT the heartbeat here only **preps** context; it
  surfaces on the user's next real turn, never interrupts (see FR-004).

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Scheduled heartbeat that preps, never interrupts (Priority: P1)

A between-session heartbeat prepares goal/progress/worldview context so that on the user's **next** turn the
appraisal is richer — without any proactive/unsolicited interruption.

**Why this priority**: Reconsolidation cannot run inside an 8s turn ("Reconsolidation + consolidation require
the scheduled heartbeat — can't fit in 8s turns", USER-MODEL-SOURCES:36); the heartbeat is the enabling
mechanism.

**Independent Test**: Trigger the heartbeat; confirm it writes prepped state (idempotently, debounced) and
that the next real turn surfaces it in-turn; confirm it never emits any outbound/interrupt and fully
fails open.

**Acceptance Scenarios**:
1. **Given** a heartbeat fires between sessions, **When** the user's next turn runs, **Then** the appraisal
   surfaces the prepped context in-turn (the proven one-turn-lag idiom, `06-CONTEXT.md:33-36,163-167`).
2. **Given** the heartbeat fires twice, **When** state is compared, **Then** the second firing is a no-op
   (idempotent, watermarked — the reflection debounce precedent, `06-CONTEXT.md:169-170`).
3. **Given** any heartbeat failure, **When** it runs, **Then** it never raises, never blocks, never emits an
   outbound message (fail-open + no-outreach preserved).
4. **Given** the drive/heartbeat kill switch is off, **When** the heartbeat would fire, **Then** it does
   nothing.

---

### User Story 2 — Reconsolidation: belief-flip propagation (Priority: P1)

When a worldview belief flips, anansi re-evaluates memories/goals/episodes that depended on the old belief
and records the propagation — "belief flips → re-evaluate memories … belief-revision propagation"
(`DESIGN-REWIND-2026-06-10.md:38`, the "Anansi crown jewel"). Runs on the heartbeat, not in-turn.

**Why this priority**: The highest-novelty promised capability; nothing in the current stack does belief-
revision propagation (`DESIGN-REWIND:38`).

**Independent Test**: Flip a worldview belief; confirm dependent items are re-evaluated on the next heartbeat
and the propagation is recorded and later surfaced observationally in-turn — never as a directive, never
silently dropping a user priority.

**Acceptance Scenarios**:
1. **Given** a worldview belief flips, **When** the heartbeat runs, **Then** items depending on the old
   belief are re-evaluated and the propagation is persisted.
2. **Given** a reconsolidation result touches a user-flagged priority, **When** it surfaces next turn,
   **Then** the flagged priority is never silently dropped (never-omit).
3. **Given** reconsolidation is mid-propagation and the process is interrupted, **When** it resumes, **Then**
   it is idempotent (no double-application).

---

### Edge Cases
- Heartbeat mechanism unavailable on this host (no cron/daemon/host-hook) → degrade to in-turn-only behavior;
  never error.
- Belief flip with no dependents → reconsolidation is a no-op.
- Heartbeat on a network-mounted `$HERMES_HOME` (WAL caveat, STACK.md:64) → see spec 006 startup check.

## Requirements *(mandatory)*

- **FR-001**: Provide a scheduled heartbeat whose execution mechanism (cron / daemon / host-hook) is chosen
  at plan-phase (`06-CONTEXT.md:188-189`); it MUST degrade to in-turn-only when no mechanism is available.
- **FR-002**: The heartbeat only PREPS state; surfacing happens on the user's next real turn (one-turn-lag
  idiom). It MUST NOT interrupt, notify, or emit any outbound communication (no-outreach anti-feature holds).
- **FR-003**: The heartbeat is debounced + idempotent (watermark), following the reflection precedent; double
  firing is a no-op.
- **FR-004**: The heartbeat carries a **per-heartbeat energy/attention budget** (costed-actions model, hard
  cap per wakeup) — the Phase-6 containment control now fully exercised (`06-CONTEXT.md:59-60`).
- **FR-005**: Reconsolidation propagates belief-flips across dependent memories/goals/episodes/worldview
  edges, persisting the propagation on the single sqlite surface; runs on the heartbeat, idempotent.
- **FR-006**: Reconsolidation output surfaces observationally in-turn; never a directive; never silently
  drops a user-flagged priority (never-omit).
- **FR-007**: A heartbeat/drive kill switch (separate from appraisal) turns the whole mechanism off;
  fail-open throughout; zero new deps; paths from config.

## Key Entities *(data)*
- **Heartbeat run** — a watermarked, budgeted between-session prep pass.
- **Reconsolidation event** — a recorded belief-flip propagation over worldview edges + dependent items.
- **Energy/attention budget** — the per-wakeup hard cap on costed actions.

## Success Criteria *(mandatory)*
- **SC-001**: The heartbeat preps state and surfaces next-turn with zero outbound emissions in 100% of runs;
  double-firing is provably idempotent.
- **SC-002**: A worldview belief flip re-evaluates 100% of its dependents on the next heartbeat, idempotently.
- **SC-003**: The per-heartbeat energy budget hard-caps costed actions; exceeding it withholds work visibly
  rather than silently.
- **SC-004**: Full fail-open + never-omit + no-outreach tests green; no new pip dependency; no new DB file.

## Assumptions
- Depends on the worldview store (spec 002).
- The heartbeat execution mechanism and reconsolidation internals are set at plan-phase.
- This is where the heartbeat's per-wakeup budget (designed in Phase 6) is first fully used.

## Out of Scope (here)
- Proactive between-session NOTIFICATION (L2) and code-red interruption — spec 004 (crossing the interrupt
  line is a separate, gated decision; the heartbeat here never interrupts).
DATA_N4P6R8T0_END
````
- scope: scheduled heartbeat; reconsolidation; energy budget; idempotency; next-turn context; success criteria: 003-reconsolidation-and-heartbeat-SC-001, 003-reconsolidation-and-heartbeat-SC-002, 003-reconsolidation-and-heartbeat-SC-003, 003-reconsolidation-and-heartbeat-SC-004

## REQ-004-interruption-lanes-acceptance-contract
- source: specs/004-interruption-lanes/spec.md:1-104
- description: Full source feature contract, preserving feature status, governing constraints, user scenarios and testing, acceptance scenarios, edge cases, functional requirements, success criteria, assumptions, dependencies, and out-of-scope qualifiers.
- acceptance:
````text
DATA_O5Q7S9U1_START
# Feature Specification: Interruption Lanes (Proactive-Notify L2 + Code-Red)

**Feature Branch**: `004-interruption-lanes`

**Created**: 2026-07-05

**Status**: Backlog (deferred + gated — each lane crosses the interrupt line and has its own precondition)

**Input**: Phase 6 deferred both proactive between-session notification and a bounded code-red lane. These
are the ONLY places anansi is permitted to consider crossing the in-turn/next-turn surfacing ceiling, and
both are OFF by default and heavily constrained. Depends on the heartbeat (spec 003).

## Governing constraints (these lanes exist to be safe, not autonomous)
- The default surfacing ceiling is in-turn / next-turn; proactive-notify was **rejected as the ceiling**
  ("crosses interrupt line; lineage of the 'go to sleep' failure", `06-DISCUSSION-LOG.md:18-19`).
- No-outreach + fail-open remain law; every lane is opt-in / OFF by default.
- The agent NEVER self-declares urgency — only USER-defined objective triggers may interrupt
  (`06-DISCUSSION-LOG.md:70-73`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Code-red interruption lane (Priority: P1 of this spec) — user-defined only

A bounded urgency-interruption lane fires **only** on objective, user-defined conditions attached to
user-flagged goals, on the gentlest available channel, rate-limited, and OFF by default.

**Why this priority**: Left explicitly OPEN (deferred, not a flat "never") "to decide … when the heartbeat
increment is planned, with concrete usage in hand" (`06-CONTEXT.md:38-41`, `06-DISCUSSION-LOG.md:70-73`).

**Independent Test**: Configure an objective user-defined trigger on a flagged goal; confirm it fires only
when that condition is objectively met, on the gentlest channel, within the rate limit; confirm the agent
can never self-trigger; confirm the lane's own kill switch and domain whitelist gate it; confirm fail-open.

**Acceptance Scenarios**:
1. **Given** an objective user-defined trigger on a user-flagged goal, **When** the condition is met,
   **Then** the lane may interrupt on the gentlest channel, within the hard rate limit.
2. **Given** the agent's own assessment of urgency (no user-defined objective trigger met), **When** it would
   like to interrupt, **Then** it CANNOT — the agent never self-declares urgency.
3. **Given** the interrupt kill switch is off OR the goal's domain is not whitelisted, **Then** the lane
   never fires.
4. **Given** repeated triggers, **When** they exceed the rate limit, **Then** they are throttled (hard rate
   limit on the gentlest channel).

---

### User Story 2 — Proactive between-session notification (L2) (Priority: P2) — gated on a host fix

An opt-in proactive notification surfaced between sessions (not waiting for the next turn), enabled only
after the desktop cold-respawn defect is fixed.

**Why this priority**: "Proactive between-session notification (L2) — later opt-in increment; depends on the
desktop cold-respawn defect fix" (`06-CONTEXT.md:190-191`). In-turn/next-session surfacing was chosen
specifically to sidestep that defect (`06-DISCUSSION-LOG.md:15-16`).

**Independent Test**: With the desktop cold-respawn defect confirmed fixed and L2 opted-in, a between-session
notification is delivered on the gentlest channel; without the fix or the opt-in, nothing is emitted.

**Acceptance Scenarios**:
1. **Given** the desktop cold-respawn defect is fixed AND L2 is opted-in, **When** a heartbeat produces a
   surfaceable item, **Then** L2 may deliver it on the gentlest channel.
2. **Given** the defect is NOT fixed OR L2 is not opted-in, **When** a heartbeat runs, **Then** no proactive
   notification is emitted (default behavior).

---

### Edge Cases
- Channel unavailable → degrade to next-turn surfacing (never error, never lose the item — passive-outbox
  fallback, spec 005).
- User-defined trigger references a goal that was deleted → the trigger is inert.
- Rate limit reached → withhold + record, never spam.

## Requirements *(mandatory)*
- **FR-001**: The code-red lane fires ONLY on objective, user-defined conditions attached to user-flagged
  goals; the agent MUST NOT be able to self-declare urgency.
- **FR-002**: The code-red lane is OFF by default, opt-in, with its own interrupt kill switch, a domain
  whitelist, and a hard rate limit on the gentlest channel (`06-CONTEXT.md:38-41`).
- **FR-003**: Proactive-notify L2 is OFF by default, opt-in, and MUST be gated on a verified fix of the
  desktop cold-respawn defect (`06-CONTEXT.md:190-191`).
- **FR-004**: Neither lane emits anything unless its preconditions hold; both fail open (a lane failure never
  raises or blocks a turn) and never violate no-outreach when disabled.
- **FR-005**: Every interruption is auditable (what fired, which user-defined trigger, which channel, within
  which rate budget).

## Key Entities *(data)*
- **User-defined trigger** — an objective condition on a user-flagged goal that may authorize an interrupt.
- **Channel + rate budget** — the gentlest channel and its hard rate limit.
- **Interrupt audit record** — the inspectable log of any fired interruption.

## Success Criteria *(mandatory)*
- **SC-001**: Code-red fires in 0% of cases lacking a met user-defined objective trigger; 100% of fires are
  attributable to a user-defined trigger on a flagged goal.
- **SC-002**: With L2's precondition unmet, 0 proactive notifications are emitted.
- **SC-003**: Both lanes are OFF by default; every fire respects the kill switch, whitelist, and rate limit.
- **SC-004**: Fail-open + no-outreach-when-disabled tests green.

## Assumptions
- Depends on the heartbeat (spec 003) for between-session firing.
- The desktop cold-respawn defect fix is tracked separately (host/desktop, `DESIGN-REWIND:53-56` "unfixed").
- "Gentlest channel" is defined at plan-phase.

## Out of Scope (here)
- The default in-turn/next-turn surfacing (already shipped). Any agent-initiated urgency (permanent
  anti-feature). General outreach (permanent anti-feature) — these lanes are the only bounded exceptions,
  and only under user-defined objective triggers.
DATA_O5Q7S9U1_END
````
- scope: code-red interruption lane; proactive notification L2; user-defined triggers; containment; audit records; success criteria: 004-interruption-lanes-SC-001, 004-interruption-lanes-SC-002, 004-interruption-lanes-SC-003, 004-interruption-lanes-SC-004

## REQ-005-tuning-and-audit-surfaces-acceptance-contract
- source: specs/005-tuning-and-audit-surfaces/spec.md:1-116
- description: Full source feature contract, preserving feature status, governing constraints, user scenarios and testing, acceptance scenarios, edge cases, functional requirements, success criteria, assumptions, dependencies, and out-of-scope qualifiers.
- acceptance:
````text
DATA_P6R8T0V2_START
# Feature Specification: Tuning & Audit Surfaces

**Feature Branch**: `005-tuning-and-audit-surfaces`

**Created**: 2026-07-05

**Status**: Backlog (deferred proprietary v2 — observability/tuning surfaces over the drive + heartbeat)

**Input**: Phase 6 deferred a desktop config panel, a full multi-session under-response audit, and (from the
memory-stack analysis) a passive outbox. These make the drive layer tunable and its behavior auditable across
sessions. Depend on the heartbeat (spec 003) for the between-session pieces.

## Governing constraints
- Single sqlite surface, fail-open, no-autonomy, never-omit, zero-new-deps (constitution I–VII).
- Tuning changes config only; it never lets the agent self-modify prompts/thresholds from reflection
  (permanent anti-feature).

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Desktop config panel (Priority: P1 of this spec)

A desktop panel lets the user tune the drive/heartbeat controls live — **cadence, budgets, and domains** —
instead of hand-editing config.

**Why this priority**: "A desktop config panel tunes all three [containment controls] later"
(`06-CONTEXT.md:60`); "Desktop config panel for tuning cadence / budgets / domains" (`06-CONTEXT.md:198`).

**Independent Test**: Change cadence/budget/domain in the panel; confirm the change flows to
`plugins.entries.anansi` config and takes effect on the next read; malformed input coerces safely (and emits
the G7 config-degradation telemetry).

**Acceptance Scenarios**:
1. **Given** the panel changes the per-heartbeat energy budget, **When** the next heartbeat runs, **Then** it
   uses the new budget.
2. **Given** the panel changes the domain whitelist, **When** the next turn runs, **Then** only the new
   whitelisted domains surface drive signals.
3. **Given** a malformed value entered via the panel, **When** config is read, **Then** it coerces to the
   documented default and emits a `config_degraded` telemetry row (G7) — never raises.

---

### User Story 2 — Multi-session under-response audit (Priority: P2)

Across sessions, anansi notices when a stalled high-priority goal with authorized push has been repeatedly
handled at low pressure, and surfaces a possible-under-support flag — the between-session completion of the
in-turn anti-complacency signal shipped in Phase 7.

**Why this priority**: "Full under-response audit across multiple sessions — later heartbeat/user-model
increment … Phase 7 owns the first in-turn anti-complacency signal" (`06-CONTEXT.md:194-195`);
"Heartbeat-level … multi-session under-response auditing remain later" (`06-DISCUSSION-LOG.md:102-103`).

**Independent Test**: Over several sessions of low-pressure handling of a stalled authorized-push goal,
confirm an under-support flag surfaces (observationally), reading persisted cross-session history.

**Acceptance Scenarios**:
1. **Given** N sessions of low-pressure handling of a stalled `push_when_stalled` goal, **When** the audit
   runs on the heartbeat, **Then** a possible-under-support flag is surfaced observationally next turn.
2. **Given** the goal is being adequately supported, **When** the audit runs, **Then** no flag is raised
   (no false alarms).

---

### User Story 3 — Passive outbox (Priority: P3)

Would-have-said items are recorded to state and surfaced inside the next turn's appraisal block, instead of
being lost or triggering outreach — "the principled middle is a passive outbox" (`MEMORY-STACK-ANALYSIS-
2026-06-10.md:87`).

**Why this priority**: A safe substitute for outreach; also the fallback when an interruption channel (spec
004) is unavailable.

**Independent Test**: Produce a would-have-said item; confirm it persists and surfaces in the next turn's
appraisal, never as an outbound message.

**Acceptance Scenarios**:
1. **Given** a would-have-said item, **When** the next turn runs, **Then** it appears in the appraisal block
   (in-turn), never emitted outbound.
2. **Given** the outbox is empty, **Then** nothing is surfaced (APPR-05 suppression holds).

---

### Edge Cases
- Panel offline / not installed → config remains hand-editable; nothing breaks.
- Under-response audit with no cross-session history yet → no flag.
- Passive-outbox overflow → capped + pruned like every state table (oldest evicted, visibly).

## Requirements *(mandatory)*
- **FR-001**: The desktop config panel edits `plugins.entries.anansi` config for cadence, per-heartbeat
  budgets, and domain whitelists; changes take effect on the next config read; malformed input coerces
  safely and emits `config_degraded` telemetry (G7).
- **FR-002**: The multi-session under-response audit reads persisted cross-session history on the heartbeat
  and surfaces a possible-under-support flag observationally; no false alarms when support is adequate.
- **FR-003**: A passive outbox persists would-have-said items and surfaces them in the next turn's appraisal
  only; never emits outbound (no-outreach); capped + pruned.
- **FR-004**: All three surfaces fail open, add zero deps, use paths from config, and never let the agent
  self-modify its own prompts/thresholds.

## Key Entities *(data)*
- **Config change** — a user tuning of cadence/budget/domain (coerced, degradation-audited).
- **Under-response record** — persisted cross-session low-pressure-handling history + the derived flag.
- **Outbox item** — a would-have-said note surfaced in-turn, capped/pruned.

## Success Criteria *(mandatory)*
- **SC-001**: Panel edits round-trip to config and take effect next read in 100% of cases; malformed input
  never raises and always emits a degradation row.
- **SC-002**: The under-response audit flags true under-support and produces zero false alarms on adequately-
  supported goals in the test fixtures.
- **SC-003**: The passive outbox surfaces in-turn with zero outbound emissions.
- **SC-004**: Fail-open + never-omit + no-outreach tests green; no new deps.

## Assumptions
- The between-session pieces (under-response audit, outbox surfacing timing) depend on the heartbeat (003).
- The desktop panel is a separate UI surface; its transport to config is defined at plan-phase.

## Out of Scope (here)
- The interruption lanes themselves (spec 004). The user-model layers (spec 002).
DATA_P6R8T0V2_END
````
- scope: desktop configuration panel; under-response audit; passive outbox; success criteria: 005-tuning-and-audit-surfaces-SC-001, 005-tuning-and-audit-surfaces-SC-002, 005-tuning-and-audit-surfaces-SC-003, 005-tuning-and-audit-surfaces-SC-004

## REQ-006-deferred-v1-and-parity-acceptance-contract
- source: specs/006-deferred-v1-and-parity/spec.md:1-119
- description: Full source feature contract, preserving feature status, governing constraints, user scenarios and testing, acceptance scenarios, edge cases, functional requirements, success criteria, assumptions, dependencies, and out-of-scope qualifiers.
- acceptance:
````text
DATA_Q7S9U1W3_START
# Feature Specification: Deferred v1 Differentiators + Upstream Parity + Infra

**Feature Branch**: `006-deferred-v1-and-parity`

**Created**: 2026-07-05

**Status**: Backlog (v1 items shipped minimal-or-parked; some blocked on an upstream host hook)

**Input**: Several v1 differentiators shipped as minimal/parked, and a few infra/parity items were left
open. Sourced from FEATURES.md, `.planning/research/MEMORY-STACK-ANALYSIS-2026-06-10.md`,
`.planning/research/STACK.md`, `.planning/research/ARCHITECTURE.md`, and the v1 milestone audit.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — D5: salience filtering over injected memory (Priority: P1) — needs an upstream hook

Anansi ranks/filters the memory context Hindsight already injected, by salience — which is impossible today
because `pre_llm_call` fires BEFORE memory prefetch and the injected block is ephemeral.

**Why this priority**: "D5 — salience filtering over injected memory: dead in v1 … Mark D5
v2-pending-upstream-hook; queue the hook as a hermes-agent PR candidate"
(`MEMORY-STACK-ANALYSIS:97`; FEATURES.md:44).

**Independent Test**: With a `post_memory_prefetch` (or equivalent) host hook available, anansi re-ranks the
injected memory by salience and the effect is observable; without the hook, D5 is a documented no-op.

**Acceptance Scenarios**:
1. **Given** an upstream `post_memory_prefetch` hook exists, **When** memory is injected, **Then** anansi can
   re-rank it by salience (observationally, never dropping user-flagged items).
2. **Given** no such hook, **When** a turn runs, **Then** D5 does nothing and is documented as
   pending-upstream (no error, no false claim of the capability).

---

### User Story 2 — Upstream-main parity re-verification (Priority: P2)

Confirm the plugin's host-surface assumptions still hold against upstream hermes-agent main — the checks
that went moot when PR #43906 was withdrawn but were never re-confirmed.

**Why this priority**: Phase 4 Criterion 2 ("test suite passes to host standards on upstream main") is
UNVERIFIED post-withdrawal; STACK.md:79-84 open items 2 & 4 — whether upstream's loader accepts
`hooks:` vs `provides_hooks:`, and whether `ctx.llm` exists on upstream main ("confirmed in local 0.16.0
fork only").

**Independent Test**: Against current upstream main: the manifest key is accepted, `ctx.llm` facade exists
(or the fallback path is exercised), `pip_dependencies: []` is processed, and the suite passes to host
standards — each recorded.

**Acceptance Scenarios**:
1. **Given** current upstream main, **When** the plugin loads, **Then** the manifest hook key is accepted and
   `ctx.llm` resolves (or the documented fallback is taken) — result recorded.
2. **Given** current upstream main, **When** the suite runs to host standards, **Then** pass/fail is recorded
   (closing Phase 4 Criterion 2 either way).

---

### User Story 3 — Dimensional affect (D3) + active-concern continuity (D6) depth (Priority: P3)

Deepen the minimal v1 versions: dimensional affect (valence/arousal with decay-to-baseline as displayed
state) and active-concern continuity (concern decay-policy tuning), after affect telemetry exists.

**Why this priority**: "D3, D5, D6 are second-wave: ship minimal versions, validate signal quality before
deepening" (FEATURES.md); dopamine is "recoverable via the queued v2 affect model … revisit only as
observable state after affect telemetry exists" (`MEMORY-STACK-ANALYSIS:91`).

**Acceptance Scenarios**:
1. **Given** affect telemetry exists, **When** D3 depth is added, **Then** valence/arousal decay-to-baseline
   is displayed as inspectable state — never used to modulate output tone (mood-driven modulation stays an
   anti-feature).
2. **Given** concern history, **When** D6 decay-policy tuning is added, **Then** stale concerns decay/prune
   on a validated policy.

---

### User Story 4 — Infra hygiene (Priority: P3)

Two small guardrails: a WAL-on-network-mount startup check/caveat, and a decision on host aux-model routing.

**Why this priority**: STACK.md:64 "WAL on network-mounted `$HERMES_HOME` … worth a startup check or a
documented caveat"; ARCHITECTURE.md:316 / SUMMARY.md:142-144 `ctx.register_auxiliary_task` aux-model routing
"evaluate in phase design" (currently a bespoke config key is used instead).

**Acceptance Scenarios**:
1. **Given** `$HERMES_HOME` is a network mount, **When** the store initializes, **Then** a startup check
   warns or a caveat is documented (no silent WAL corruption risk).
2. **Given** the host exposes `ctx.register_auxiliary_task`, **When** aux-model routing is evaluated, **Then**
   a decision (adopt vs keep the bespoke config key) is recorded.

---

### Edge Cases
- D5 with no upstream hook → explicit no-op + doc note, never a fabricated capability.
- Upstream main diverged so far the plugin won't load → recorded as a parity finding, fail-open at runtime.

## Requirements *(mandatory)*
- **FR-001**: D5 salience filtering is implemented ONLY once an upstream `post_memory_prefetch`-style hook
  exists (queue it as a hermes-agent PR candidate); until then it is a documented no-op, never a false claim.
- **FR-002**: Re-verify upstream-main parity (manifest key, `ctx.llm` facade, `pip_dependencies` processing,
  host-standard suite) and record the result, closing Phase 4 Criterion 2.
- **FR-003**: Deepen D3 (dimensional affect as displayed state, decay-to-baseline) and D6 (concern decay
  tuning) without ever modulating output tone from affect (anti-feature) or exceeding state caps.
- **FR-004**: Add a WAL-on-network-mount startup check or documented caveat.
- **FR-005**: Decide + record aux-model routing (`ctx.register_auxiliary_task`) vs the bespoke config key.
- **FR-006**: Everything fail-open, zero new deps, paths from config.

## Success Criteria *(mandatory)*
- **SC-001**: D5 either works via a real host hook or is a documented, tested no-op — no fabricated behavior.
- **SC-002**: Upstream-main parity is re-verified and recorded; Phase 4 Criterion 2 is closed either way.
- **SC-003**: D3/D6 depth ships without any output-tone modulation and within state caps.
- **SC-004**: A network-mount WAL guard exists (check or caveat); the aux-model routing decision is recorded.

## Assumptions
- The upstream `post_memory_prefetch` hook is a hermes-agent contribution, gated on Dr. Mani's sign-off
  (proprietary posture; no public/upstream work without sign-off).
- The config-gated direct-Hindsight-recall option stays PARKED (`SUMMARY.md:53`) unless explicitly revived.

## Out of Scope (here)
- The proprietary user-model layers (spec 002). Any change to the anti-features (mood modulation, outreach,
  memory-provider writes).
DATA_Q7S9U1W3_END
````
- scope: memory salience filtering; upstream parity; dimensional affect; active concerns; WAL; auxiliary-model routing; success criteria: 006-deferred-v1-and-parity-SC-001, 006-deferred-v1-and-parity-SC-002, 006-deferred-v1-and-parity-SC-003, 006-deferred-v1-and-parity-SC-004

## REQ-007-drive-security-verification-acceptance-contract
- source: specs/007-drive-security-verification/spec.md:1-105
- description: Full source feature contract, preserving feature status, governing constraints, user scenarios and testing, acceptance scenarios, edge cases, functional requirements, success criteria, assumptions, dependencies, and out-of-scope qualifiers.
- acceptance:
````text
DATA_R8T0V2X4_START
# Feature Specification: Drive Security + Live Verification Debt

**Feature Branch**: `007-drive-security-verification`

**Created**: 2026-07-05

**Status**: Backlog (a promised artifact never produced + live checks never run)

**Input**: Three verification debts recorded but not discharged: (1) the Phase-7 security doc `07-SECURITY.md`
was expected and never produced (`07-LEARNINGS.md` frontmatter `missing_artifacts: ["07-SECURITY.md"]`);
(2) the live Criterion-1 drive turn was never run (env-blocked); (3) the APPR-06 trust-gate fallback is
unverified live. These need a real provider and/or a security pass, not new features.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Produce the drive-layer security doc `07-SECURITY.md` (Priority: P1)

The drive layer (goals, pressure, first-person voice, ground-truth git/file reads) gets a STRIDE-style threat
register + mitigation check, matching the per-phase security discipline that every other phase followed.

**Why this priority**: A promised phase artifact is simply missing (`07-LEARNINGS.md:7`). The drive layer
added a new injection/behavior surface (goal text rendered, git/file reads) that was never formally
threat-modeled.

**Independent Test**: `07-SECURITY.md` exists with a STRIDE register covering the drive surfaces, each threat
classified with its mitigation traced to a test or code path.

**Acceptance Scenarios**:
1. **Given** the drive layer's inputs (user goal text, git reflog/file reads, config), **When** the threat
   register is built, **Then** each STRIDE category has entries with mitigations traced to code/tests.
2. **Given** the never-omit + SAFE-04 + anti-creep invariants, **When** the doc reviews them, **Then** it
   confirms each is enforced-and-tested (or flags a gap).

---

### User Story 2 — Run the live Criterion-1 drive turn (Priority: P1) — env-gated

Confirm, against a real model provider, that a live turn surfaces a user-minted goal in the first-person
owned-want voice — the one Phase-7 success criterion left INCONCLUSIVE because providers were down. (This is
task T029 of spec 001; recorded here as the live-verification home.)

**Why this priority**: "A real model turn surfaces a minted goal in the appraisal block" is UNVERIFIED
(`07-UAT.md:21,51`; `07-VERIFICATION.md:94-99`). The logic is unit-proven; only the live pass is missing.

**Independent Test**: With a reachable provider, `scripts/live_drive_smoke.py` returns exit 0 (PASS) with the
`- drive want:` line present and no `you should` leak.

**Acceptance Scenarios**:
1. **Given** a reachable provider (openrouter billing restored OR `hermes auth` for nous), **When**
   `$HERMES_HOME/hermes-agent/venv/bin/python scripts/live_drive_smoke.py` runs, **Then** it exits 0 and the
   first-person want line is present.
2. **Given** no provider, **When** it runs, **Then** it exits 2 (INCONCLUSIVE) honestly — never a false pass.

---

### User Story 3 — Verify APPR-06 trust-gate fallback live (Priority: P2)

Confirm the "trust-gate denial → single retry with the host's active model → then fail open" path on an
install where the host model is fast enough to actually complete within the deadline.

**Why this priority**: "Mechanically proven; unproducible live on this install (host fallback ~37s > clamp;
degrades to designed fail-open timeout)" (`MEMORY-STACK-ANALYSIS:116`; DECISIONS R3:39-41). Phase 2 Criterion
3 is UNVERIFIED live.

**Independent Test**: On a host whose active model completes an appraisal under the deadline, force a
trust-gate denial and confirm the single fallback retry produces a `trust_fallback` outcome (not a timeout).

**Acceptance Scenarios**:
1. **Given** a fast-enough host model and a trust-gate denial, **When** appraisal runs, **Then** telemetry
   records `trust_fallback` (the retry completed) — the mechanism produced live, not just unit-proven.
2. **Given** a slow host model, **When** the fallback exceeds the deadline, **Then** it degrades to a
   fail-open timeout (the documented accepted behavior) — recorded, not treated as a bug.

---

### Edge Cases
- No fast host model available anywhere → APPR-06 live check stays deferred with the accepted-won't-fix note,
  not a false failure.
- Security doc surfaces a real gap → it becomes its own spec/fix, not silently absorbed.

## Requirements *(mandatory)*
- **FR-001**: Produce `07-SECURITY.md` (or an equivalent `SECURITY.md` for the drive layer) with a STRIDE
  register + mitigation trace covering goal text rendering, ground-truth git/file reads, config, and the
  first-person voice carve-out.
- **FR-002**: Run the live Criterion-1 drive smoke against a real provider and record PASS (exit 0) or the
  honest INCONCLUSIVE reason; close spec-001 task T029 on PASS.
- **FR-003**: Verify APPR-06 trust-fallback live on a fast-enough host (or record it as accepted-deferred
  with the reason); never claim it verified without evidence.
- **FR-004**: No code change is required for FR-002/FR-003 unless a defect is found; the harnesses already
  exist and report honest exit codes.

## Success Criteria *(mandatory)*
- **SC-001**: `07-SECURITY.md` exists; every drive-surface threat has a classified mitigation traced to
  code/tests.
- **SC-002**: The live drive turn is run and its outcome (PASS / honest INCONCLUSIVE) is recorded; on PASS,
  Phase-7 Criterion 1 and spec-001 T029 are closed.
- **SC-003**: APPR-06 live behavior is either produced (`trust_fallback` observed) or recorded as
  accepted-deferred with the concrete reason — never asserted without evidence.

## Assumptions
- FR-002/FR-003 are blocked only on provider/host availability, not on code.
- Evidence-over-assertion (constitution VII): no live criterion is marked met without a recorded run.

## Out of Scope (here)
- New drive features. Any change to the accepted fail-open-on-slow-host behavior (that is by design).
DATA_R8T0V2X4_END
````
- scope: drive security; live drive verification; trust-gate fallback; success criteria: 007-drive-security-verification-SC-001, 007-drive-security-verification-SC-002, 007-drive-security-verification-SC-003
