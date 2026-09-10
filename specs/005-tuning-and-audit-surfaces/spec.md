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
