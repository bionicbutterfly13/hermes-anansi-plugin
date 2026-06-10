# Hermes Anansi Metacognition Plugin

## What This Is

A hook-based metacognition plugin for hermes-agent (NousResearch) that ports the **subconscious
appraisal pre-phase** from Dr. Mani's Anansi project, with all autonomy/pushiness removed. Before
the agent answers, a fast, cheap JSON-mode LLM call surfaces instincts, salient memories,
contradictions, and confidence signals, and injects them as a compact context block — giving the
agent a "gut reaction" layer without giving it initiative.

## Core Value

Every Hermes turn gets a grounded metacognitive appraisal (instincts + salience + contradictions)
injected before response generation — with zero capacity for autonomous action and zero impact on
turn reliability (strict fail-open).

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Plugin loads via hermes-agent's standard plugin mechanism (`plugin.yaml`, hook functions) with no vendored-code edits
- [ ] `pre_llm_call` hook runs the appraisal: fast JSON-mode LLM call over (user message + injected memory context + local appraisal state), output parsed into a compact block (≤ ~500 tokens) injected into context
- [ ] Appraisal is strictly fail-open: any error/timeout (LLM down, state corrupt) yields empty injection, never a crashed or blocked turn; hard timeout ≈ 2-3s
- [ ] Local appraisal state (lightweight affect summary, active-concern list, contradiction log, confidence/trust scores) persisted in SQLite under `$HERMES_HOME` — no Postgres, no stored procedures, no new daemons
- [ ] `on_session_end` hook runs the reflection pass: updates appraisal state from the session transcript (observations applied locally — the Anansi "apply_subconscious_observations" equivalent, reimplemented on SQLite)
- [ ] Coexists with Hindsight as the active MemoryProvider — this plugin NEVER takes the memory-provider slot; it reads whatever memory context is already injected
- [ ] Works with any configured provider (current default: anthropic / claude-sonnet-4-6); appraisal model independently configurable (small/cheap model), resolved from config — no hardcoded paths or models
- [ ] Tests covering: hook registration, appraisal parse/inject, fail-open paths, state persistence round-trip
- [ ] Packaged so it can be PR'd to NousResearch/hermes-agent (in-tree `plugins/` layout) while also installable standalone at `$HERMES_HOME/plugins/anansi`

### Out of Scope

- Heartbeat / always-on background cycles — the defining "pushiness" of original Anansi; explicitly dropped by Dr. Mani
- Outreach / reach_out / unsolicited contact — same reason; appraisal-only cycle
- Privilege ladder / backlog escalation / continuation nudges — dropped
- Dopamine modulation — replaced by plain confidence/trust scoring
- Postgres + AGE + RabbitMQ + Ollama + UI — original Anansi infra; plugin is SQLite-only, Docker-free
- Memory provider implementation — Hindsight keeps the provider slot (locked decision 2026-06-09)
- Plugin top-level `sys.path` mutation — known hermes-agent plugin-discovery design flaw (mnemosyne symlink incident); never execute path-mutating code at import time

## Context

- Source material: `/Volumes/Asylum/repos/hex-auto/Anansi` — `services/agent.py::run_subconscious_appraisal`
  (fast inline JSON-mode appraisal: instincts, emotional reactions, salient memories, memory-expansion cues;
  context = user message + memory context + affective state + goals + dopamine state),
  `core/subconscious.py` (thin wrapper over Postgres stored procs `get_subconscious_context` /
  `apply_subconscious_observations`).
- Hook precedent: icarus plugin (`~/.hermes/plugins/icarus`) provides `on_session_start`, `pre_llm_call`,
  `post_llm_call`, `on_session_end` and injects context per-turn; its fail-open patterns are the model.
- Prior design work (2026-06-09, obs #10029): the "mnemosyne" unified-provider plan was SHELVED, but its
  metacognition slice survives here: appraisal-only cycle, contradiction observation pipeline
  (semantic/narrative/relational/emotional), confidence/trust scoring instead of dopamine.
- This install: `~/.hermes`, hermes-agent at `~/.hermes/hermes-agent` branch `local-desktop-fixes`;
  7 PRs already open upstream from this fork (contribution machinery proven).

## Constraints

- **Compatibility**: must not modify vendored hermes-agent code; pure plugin — update-safe
- **Reliability**: appraisal can never degrade turn success; fail-open everywhere, bounded latency
- **Cost**: one extra small LLM call per turn max; injected block capped (~500 tokens); appraisal model configurable to a cheap tier
- **Privacy**: appraisal state stays local (SQLite under `$HERMES_HOME`); nothing leaves the machine beyond the LLM call itself
- **Paths**: resolve everything from config/env (`$HERMES_HOME`) — never literal paths (standing rule)
- **Contribution**: code quality + tests to upstream-PR standard; per-PR sign-off from Dr. Mani required before submission

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Hook-based plugin, NOT MemoryProvider | Hindsight keeps the provider slot (locked 2026-06-09) | — Pending |
| Keep appraisal pre-phase, drop heartbeat/outreach/privilege ladder | "Metacognition without pushiness" (Dr. Mani) | — Pending |
| SQLite local state replaces Postgres stored procs | Docker-free, no daemons, update-safe install | — Pending |
| Confidence/trust scoring replaces dopamine modulation | Same signal value, none of the drive mechanics | — Pending |
| `pre_llm_call` + `on_session_end` (+ `on_session_start` state load) | Proven icarus hook surface | — Pending |
| Develop standalone repo first, PR in-tree later | Mirrors neo4j/self-evolution repo pattern; PR needs sign-off | — Pending |

---
*Last updated: 2026-06-10 after autonomous new-project ceremony (self-answered under Dr. Mani's 6-hour mandate; answers grounded in HANDOFF.md, memory obs #10029/#10025, and Anansi/icarus source recon)*
