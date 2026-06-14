# Phase 6: Proprietary User Model + Drive Design - Context

**Gathered:** 2026-06-14
**Mode:** standard
**Status:** Complete — addendum integrated 2026-06-14

<domain>
## Phase Boundary

Phase 6 is design/discussion only — it shapes the proprietary v2 direction and captures the
decisions that drive a future implementation milestone. No plugin code is written in this phase.

The proprietary direction reintroduces capabilities v1 deliberately dropped for upstream-PR posture
(now moot — PR #43906 withdrawn, plugin proprietary): a drive/accountability layer, a layered
autobiographical user model, worldview, user-dopamine, reconsolidation, and (later) a scheduled
heartbeat.

This phase delivers locked design decisions for: the autonomy boundary, the build sequence (first
increment + working order), and the storage architecture for the first increment.

**Locked, NOT reopened:** Hindsight remains the sole MemoryProvider; SQLite-only (no
Postgres/AGE/Redis); v1's 107-test foundation is kept, nothing discarded; fail-open remains law.

**This phase OVERRIDES three v1 "Out of Scope" decisions on the record** (heartbeat, dopamine,
autonomy/unprompted-surfacing) — see DESIGN-REWIND-2026-06-10.md. The override is deliberate and
bounded by the decisions below.
</domain>

<decisions>
## Implementation Decisions

### Autonomy boundary — Surfacing
- The scheduled heartbeat preps goal/progress context between sessions; it surfaces as goal-aware
  appraisal on the user's NEXT turn. No proactive/unsolicited interruption (no L2 push). Extends the
  proven one-turn-lag idiom; preserves strict fail-open. Proactive notification is a later opt-in
  increment.
- OPEN (deferred, NOT settled as a flat "never"): whether a bounded "code red" interruption lane
  exists — fired only by OBJECTIVE, USER-DEFINED conditions on user-flagged goals (the agent never
  self-declares urgency), opt-in / OFF by default, with its own interrupt kill switch + domain
  whitelist + hard rate limit on the gentlest channel. Deferred to the heartbeat increment's
  planning, with concrete usage in hand. Increment #1 is in-turn only regardless (no heartbeat).

### Autonomy boundary — Drive voice
- Surfaced drive may state facts AND express the agent's want in the FIRST person ("I want X ready
  by Friday"). It may NEVER use second-person imperatives ("you should…").
- SAFE-04 / anti-creep is relaxed to permit first-person want-language while the sanitizer continues
  to neutralize/quote second-person directives. Implementation consequence: anti-creep tests gain a
  first-person carve-out; the directive-language scan still applies to second-person.

### Autonomy boundary — Goal provenance
- The user mints every top-level goal. The agent NEVER originates one.
- The agent MAY decompose a user-minted goal (sub-tasks, success criteria) and MAY surface a
  candidate top-level goal as an INERT suggestion that does nothing until the user confirms.
  Nominate, never mint.

### Autonomy boundary — Containment
- Three controls, all in `plugins.entries.anansi` config: (1) a drive kill switch SEPARATE from the
  appraisal kill switch (drive off while appraisal stays on); (2) a domain whitelist (drive operates
  only in user-named domains); (3) a per-heartbeat energy/attention budget (costed-actions model,
  hard cap per wakeup). A desktop config panel tunes all three later.

### Autonomy boundary — Adjustable pressure + drive consequence visibility
- Drive pressure is adjustable, not hidden inside the model's private judgment. The first in-turn
  implementation exposes a bounded pressure ladder (`quiet` / `standard` / `firm`); `code-red`
  remains deferred to the heartbeat/interruption planning lane and still requires user-defined
  objective triggers.
- The drive may adjust salience, urgency, persistence, and surfacing priority. It may NOT adjust
  truth, goal ownership, evidence, or omission rules. Any drive-caused salience change must be
  inspectable as a drive effect rather than blended into the neutral read.
- Surfacing must make the consequence of drive visible: neutral read, drive read, and drive effect
  (for example, "raised salience because goal X is stalled 5 days and marked firm support"). The
  user should be able to see how the drive changed the appraisal.
- Anti-complacency is part of safety, not a relaxation of it. User-authorized push zones
  (`support_style`, `push_when_stalled`, and threshold metadata) prevent high-priority stalled goals
  from being quietly downranked when the user most needs support. Repeated low-pressure handling of
  a stalled user-priority should flag itself as possible under-support, not disappear behind
  caution.

### The never-omit invariant (drive red line)
- The agent's guesses must never outrank the user's stated goals/priorities, and it must NEVER
  silently drop something the user flagged as mattering. Stated priorities stay surfaced/visible even
  when the agent would rank them last. Hard invariant for the drive layer — must be enforced AND
  tested. This is the core of "aligned wanting, not pushiness"; silent omission is treated as a
  betrayal (Dr. Mani's top anti-value).
- Corrective-without-pushy mechanism: surface blind spots via MULTIPLE low-reactance perspectives —
  never a single prescription, never silent omission.

### Scope & sequencing
- First increment (tracer bullet): **Drive / accountability** — goal objects (user-minted) +
  per-goal progress velocity + in-turn goal-aware appraisal, with the never-omit invariant baked in.
  Reuses the existing appraisal hook; needs NO heartbeat.
- Working order for later increments (revisable): worldview store → episode/autobiography +
  user-dopamine → reconsolidation. Heartbeat is introduced in the increment that first requires
  between-session work (reconsolidation/consolidation).

### Architecture
- Drive state (goals, progress velocity) lives in the EXISTING anansi SQLite store (new tables in
  `store.py`). Single sqlite surface preserved (locked v1 rule); inherits fail-open + locked-DB
  coverage. No new DB file, no daemon.
- Goal freshness: progress-velocity / stalled signals are computed from GROUND TRUTH (git,
  file/state timestamps, milestone status) at appraisal-read time — NOT gated behind debounced
  reflection — so goal signals are never stale by the reflection debounce (`reflect_every_n_turns`
  default 5). Flagged by Codex review 2026-06-14.
- Heartbeat execution mechanism is DEFERRED to the increment that needs it (drive-first surfaces
  in-turn).

### Agent's Discretion
- Exact table schemas for goals + progress velocity, and the progress-velocity metric formula →
  plan-phase.
- Exact config keys/shape for the containment and pressure controls → plan-phase.
- Exact rendering shape for neutral read / drive read / drive effect → plan-phase, but it must keep
  the drive consequence visible and must not collapse pressure into unstated model judgment.

</decisions>

<specifics>
## Specific Ideas

- "Aligned wanting, not pushiness": a drive whose objects are the user's goals, represented as the
  agent's own first-person wants. (DESIGN-REWIND #1.)
- Progress velocity replaces agent-dopamine for goals: per-goal momentum; stalled goals louder,
  moving goals quiet; inspectable.
- Calibrated pressure replaces global pressure: per-goal support style and push thresholds let the
  user authorize stronger momentum support locally without giving the agent global permission to
  pressure.
- Drive consequence visibility: the rendered/appraisal surface should show when drive raised,
  lowered, or preserved salience, and why.
- User-dopamine (later increment) models the USER's motivation/habit dynamics, bounded to whitelisted
  domains and override-able — never an agent-reward signal.
- Worldview-as-data and reconsolidation (belief-flip propagation) are the high-novelty later
  increments; reconsolidation structurally requires the heartbeat.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

- .planning/research/DESIGN-REWIND-2026-06-10.md — proprietary direction, Dr. Mani's positions
- .planning/research/USER-MODEL-SOURCES-2026-06-10.md — source survey, layer→mechanism mapping, value order
- .planning/PROJECT.md — v1 foundation, constraints, locked decisions
- .planning/DECISIONS.md — v1 locked decisions (single sqlite surface, SAFE-04, kind:standalone)
- anansi/store.py — the sqlite surface the drive state extends
- anansi/appraisal.py, anansi/render.py — the in-turn surfacing + sanitization path

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `anansi/appraisal.py` + `pre_llm_call` path: the in-turn surfacing channel for goal-aware
  appraisal — drive increment #1 rides this, no new hook.
- `anansi/store.py` (SQLite/WAL): the single sqlite surface; drive tables extend it; fail-open +
  locked-DB tests already cover the write path.
- `anansi/render.py` `_sanitize_text` + SAFE-04 anti-creep tests: the directive-language guard that
  must gain a first-person want-language carve-out.
- `anansi/config.py`: where the three containment controls resolve from config.

### Established Patterns
- One-turn-lag idiom (`pre_llm_call` fires before memory prefetch): the model for
  heartbeat-preps-then-surfaces-next-turn. PRECISION (Codex review 2026-06-14): the appraisal DOES
  see the current user message + conversation history every turn (`__init__.py:126-130`) — the lag
  applies only to MEMORY-derived signals, and it is ≥1 turn, not exactly one, because reflection is
  debounced (`reflect_every_n_turns` default 5 / session change). The gut reaction is an early read,
  not an authoritative synthesis.
- Reflection debounce/idempotence (`on_session_end` per turn): the precedent any
  between-session/heartbeat work must follow.
- Fail-open everywhere; advisory-only signals (never branch on a guess) — the never-omit invariant
  extends this stance.
- Drive pressure is explicit metadata, not hidden reward shaping. Later agents must keep neutral read
  and drive-adjusted read separable enough to audit.

### Integration Points
- Goal-aware noun-fields added to the appraisal output schema, surfaced through render with the
  first-person want carve-out.
- New goal/velocity tables in `store.py`, read at appraisal time, written by reflection / (future)
  heartbeat.
- Pressure metadata (`support_style`, `push_when_stalled`, thresholds) rides with goal state. Drive
  effect fields ride with appraisal/render output so a user can inspect how salience changed.

</code_context>

<deferred>
## Deferred Ideas

- Scheduled heartbeat execution mechanism (cron / daemon / host-hook) — deferred to the increment
  that first needs between-session work.
- Proactive between-session notification (L2) — later opt-in increment; depends on the desktop
  cold-respawn defect fix.
- "Code red" urgency-interruption lane — open question, user-defined triggers only; decided at
  heartbeat-increment planning (see Surfacing decision).
- Full under-response audit across multiple sessions — later heartbeat/user-model increment if it
  needs between-session history. Phase 7 owns the first in-turn anti-complacency signal.
- Worldview store, episode/autobiography, user-dopamine, reconsolidation — later increments per the
  working order.
- Desktop config panel for tuning cadence / budgets / domains.

</deferred>

---
*Phase: 06-proprietary-user-model-drive-design*
*Context gathered: 2026-06-14*
