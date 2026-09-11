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
