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
