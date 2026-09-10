# Anansi — Remaining Promise Backlog (spec index)

Every promised-but-unbuilt or unverified item for the anansi plugin, captured as Spec Kit specs so
nothing is lost. Sourced from the `.planning/` archive (Phase 6 design, Phase 7 verification/UAT/learnings,
DECISIONS, HANDOFF, ROADMAP, research/) and cross-checked against `anansi/` code on 2026-07-05.

**Excluded on purpose:** the 16 anti-features (deliberate never-builds — heartbeat-as-daemon-without-user-turn,
outreach, privilege ladder, agent-dopamine, Postgres/AGE/RabbitMQ/Ollama/UI, memory-provider slot, tool
execution, directive language, turn gating, memory-provider writes, self-modifying prompts, unbounded state,
mood-driven output modulation, multi-call chains, `sys.path` mutation). Those stay unbuilt by design.
**Out of anansi scope:** graphify issue #1320 (separate repo); Hindsight-retain / memory-os-sync / L3
stack-health follow-ups (host-stack, not the plugin).

## Agreed sequencing (from 06-CONTEXT.md:93-94, 06-DISCUSSION-LOG.md:54-55)

Drive/accountability (Phase 7 — DONE) → **worldview store → episode/autobiography + user-dopamine →
reconsolidation**. The **scheduled heartbeat** is introduced in the increment that first needs between-session
work (reconsolidation). Interruption lanes (proactive-notify L2, code-red) and the desktop config panel come
after, each gated on its own precondition.

## Specs

| Spec | Covers | Sequencing |
|------|--------|-----------|
| [001-close-known-gaps](001-close-known-gaps/spec.md) | G1–G8 Phase-7 gap closure (DONE except G1 live run) | current |
| [002-autobiographical-user-model](002-autobiographical-user-model/spec.md) | Worldview store · episode/autobiography · user-dopamine · the 5-layer model | next (P1 = worldview) |
| [003-reconsolidation-and-heartbeat](003-reconsolidation-and-heartbeat/spec.md) | Belief-flip reconsolidation + the scheduled heartbeat it requires | after 002 |
| [004-interruption-lanes](004-interruption-lanes/spec.md) | Proactive-notify L2 · code-red interruption lane | after heartbeat; each gated |
| [005-tuning-and-audit-surfaces](005-tuning-and-audit-surfaces/spec.md) | Desktop config panel · multi-session under-response audit · passive outbox | after heartbeat |
| [006-deferred-v1-and-parity](006-deferred-v1-and-parity/spec.md) | D3/D5/D6 depth · upstream `post_memory_prefetch` hook · upstream-main parity re-verify · WAL-on-netmount caveat · aux-model routing · parked direct-Hindsight recall | opportunistic |
| [007-drive-security-verification](007-drive-security-verification/spec.md) | The missing `07-SECURITY.md` — STRIDE for the drive layer; live APPR-06 trust-fallback verification | any time |

## Canonical design references (read before planning any of these)

- `.planning/phases/06-proprietary-user-model-drive-design/06-CONTEXT.md`
- `.planning/phases/06-proprietary-user-model-drive-design/06-DISCUSSION-LOG.md`
- `.planning/research/DESIGN-REWIND-2026-06-10.md`
- `.planning/research/USER-MODEL-SOURCES-2026-06-10.md`
- `.planning/research/MEMORY-STACK-ANALYSIS-2026-06-10.md`
- `.specify/memory/constitution.md` (governs all of the above)
