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
