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
