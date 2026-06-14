# Phase 6 Discussion Log

**Date:** 2026-06-14
**Mode:** standard
**Areas selected by Dr. Mani:** Autonomy boundary, Scope & sequencing, Architecture & heartbeat
**Not selected:** Drive & user-dopamine (partially covered under Autonomy → Containment + the
never-omit invariant).

> Audit trail only — not referenced by downstream agents. Shows all options considered, not just the
> chosen one.

## Area: Autonomy boundary

### Q1 — Surfacing (the autonomy ceiling)
- **In-turn, next session — CHOSEN.** Heartbeat preps; surfaces next turn; no interrupt; extends
  one-turn-lag; sidesteps the desktop cold-respawn defect.
- Per-domain config tier — rejected (inherits proactive-push blocker; adds surface early).
- Proactive notify (L2) — rejected (crosses interrupt line; lineage of the "go to sleep" failure).
- Observe-only + goals (L0+) — rejected (too thin given the premise).

### Q2 — Drive voice
- **Observational + first-person owned want — CHOSEN.** Facts + "I want X"; never "you should".
  SAFE-04 relaxed for first-person, still neutralizes second-person directives.
- Soft suggestion — rejected (crosses into prompting).
- Action-proposing — rejected (turns appraisal into a to-do generator).
- Strictly observational — rejected (under-delivers on aligned wanting).

### Q3 — Goal provenance
- You mint, agent decomposes only — considered.
- **You mint + agent may surface inert candidates — CHOSEN.** Nominate, never mint; candidate inert
  until confirmed.
- Agent infers provisional goals — rejected (closest to the pushiness being avoided).

### Q4 — Containment
- **Switch + whitelist + energy budget — CHOSEN.** Drive kill switch separate from appraisal +
  domain whitelist + per-heartbeat energy budget; all in config.
- Switch + whitelist, budget later — rejected (prefer bounded from day one).
- Single global kill switch — rejected (no constrained domains of influence).
- Note: Dr. Mani asked to clarify the difference between the latter two (the domain whitelist);
  re-asked with the distinction explicit, then chose all three.

### Emergent invariant (from grounding interview)
- **Never-omit:** the agent must never silently drop a user-stated priority; its guesses never
  outrank stated goals. Hard drive-layer invariant — silent omission = betrayal (Dr. Mani's top
  anti-value). Corrective-without-pushy via multiple low-reactance perspectives.

## Area: Scope & sequencing

### First increment
- **Drive / accountability — CHOSEN.** Verbatim: "we'll do number 1 first." Goals + progress
  velocity + in-turn goal-aware appraisal + never-omit. Reuses appraisal hook; no heartbeat.
- Worldview store first — considered (survey's #1; more machinery).
- User-model substrate first — rejected (slowest to value).
- Working order for the rest (approved, revisable): worldview → episode/user-dopamine →
  reconsolidation.

## Area: Architecture & heartbeat

### Drive state store
- **Extend anansi SQLite store — CHOSEN.** New tables in store.py; single sqlite surface preserved;
  inherits fail-open + locked-DB coverage.
- Separate user-model DB — rejected (breaks single-sqlite-surface rule; two WAL files).
- Decide at plan time — rejected (load-bearing enough to lock now).
- Heartbeat: deferred — drive-first surfaces in-turn; mechanism designed in the increment that needs
  between-session work.

### Code-red interruption (follow-up question)
- Reserve user-defined code-red lane — considered.
- Keep flat "never push" — considered.
- **Defer the call — CHOSEN.** Increment #1 is in-turn only regardless; decide a bounded,
  user-defined code-red lane when the heartbeat increment is planned. Principle captured: only
  USER-defined objective triggers may interrupt — the agent never self-declares urgency.

## Process note
- Dr. Mani directed that the public article "Programming a Deeper Hermes" is NOT a design input;
  design is driven by `.planning` vision/plans. Article archived at
  `docs/journal/2026-06-13-programming-a-deeper-hermes.md`.
- Codex review 2026-06-14 corrected the one-turn-lag framing: appraisal sees current message +
  history (not purely prior state); lag is ≥1 turn (reflection debounced, default 5) not exactly
  one; human-intuition comparison is a metaphor. Corrected framing folded into 06-CONTEXT
  (Established Patterns + goal-freshness). Published journal article left as-is per Dr. Mani.

## Deferred ideas
- Heartbeat execution mechanism; proactive-notify (L2); worldview / episode / user-dopamine /
  reconsolidation internals; desktop config panel.
