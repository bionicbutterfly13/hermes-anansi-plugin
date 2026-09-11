# Feature Specification: Layered Autobiographical User Model

**Feature Branch**: `002-autobiographical-user-model`

**Created**: 2026-07-05

**Status**: Backlog (deferred proprietary v2 — designed in Phase 6, not yet built)

**Input**: Phase 6 proprietary design. The proprietary direction reintroduces "a layered autobiographical
user model, worldview, user-dopamine" (`.planning/phases/06-.../06-CONTEXT.md:14-16`). Agreed working order
for the later increments: **worldview store → episode/autobiography + user-dopamine → reconsolidation**
(`06-CONTEXT.md:93-94`, `06-DISCUSSION-LOG.md:54-55`). Reconsolidation is a separate spec (003).

This captures a designed-but-unbuilt direction. It MUST be re-scoped (GSD phase discussion → planning)
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
