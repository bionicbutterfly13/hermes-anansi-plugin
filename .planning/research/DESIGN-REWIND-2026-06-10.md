# Design Rewind — proprietary direction (Dr. Mani, 2026-06-10 evening)

Status: open design discussion. No roadmap, no rush — increments adopted only as value is felt
("how each aspect improves the individual user experience with their Hermes agent in the
background as they go about their day").

## Context

- Upstream PR #43906 withdrawn + fork branch deleted 2026-06-10 (~10:20pm). Plugin is proprietary.
- v1 (4 phases, 31 reqs, 107 tests) stands as the foundation; nothing discarded.
- Process failure acknowledged: feature keep/drop was self-answered under autonomous mandates,
  never discussed. This doc is the rewind.

## Dr. Mani's design positions (verbatim-grounded)

1. **Aligned wanting, not pushiness.** "A certain amount of wanting me to succeed and wanting to
   have my stuff ready in time and wanting to help me keep my priorities aligned by representing
   them as its own wants." Drive whose objects are HIS goals. Pushiness ≠ wanting; the
   anti-pushiness premise had no documented incident behind it.
2. **Goals: he mints, jointly planned.** "Clearly I set the goals and we agree on them — we plan
   together and break them down and along the path I get an accountability partner who measures
   progress with me." Not agent-minted. Cf. goal systems now native in Codex/Claude harnesses.
3. **Dopamine = model of the USER, not agent reward.** "A dopamine model of the user that can be
   overridden or kept in check with boundaries and a constrained set of domains of influence —
   a synchronization or user-modeling mechanism and habit formation help." Points outward:
   his motivation dynamics, habit loops, momentum. Override-able; domain whitelist.
4. **Heartbeat: scheduled, well-spaced wakeups** → optimizable, budgeted. Desktop config panel
   (future) adjusts cadence/budgets to taste; all knobs in config.yaml plugins.entries block.
5. **Layered autobiographical USER model** — memory typed by cognitive function:
   episodic / semantic / procedural / strategic / worldview / goal (Anansi cognitive_memory_api
   taxonomy). Worldview = beliefs/values/boundaries as data. Beyond Hindsight (provenance-typed:
   experience/world/observation) and memory-os (storage-tiered). Hindsight = record of what
   happened/believed; this layer = the agent's stance + the user's autobiography.
6. **Source pool to mine** (surveys dispatched 2026-06-10 ~11pm): nemori (+ paper), REMem,
   Dionysus2.0 + dionysus-HDDLGym (his consciousness work: IWMT, autonoesis), ActiveInference.jl,
   enactive_inference_model, aif_iwai2025_thoughtseeds, Anansi recmem/reconsolidation, agi-memory.
7. **Anansi crown jewel already identified:** reconsolidation sweeps — belief flips → re-evaluate
   memories accepted/rejected because of the old belief (CONTESTED_BECAUSE / SUPPORTS edges).
   Nothing in the current stack does belief-revision propagation.

## Practical drive mapping (agreed direction, not yet scoped)

| Piece | Function |
|---|---|
| Goal objects (active/queued/backburner) | Dr. Mani-minted, jointly broken down, success criteria recorded |
| Appraisal hook (built) | Per-turn: relates-to-goal / stalled-N-days / contradicts-milestone — accountability inside existing turns |
| Scheduled heartbeat | Between sessions: measure real progress (git/state/milestones), prep status |
| Progress velocity (replaces agent-dopamine) | Per-goal momentum metric; stalled goals louder, moving goals quiet — inspectable |
| User-dopamine model | Separate: his motivation/habit dynamics; bounded domains; override-able |

## Open questions

- Desktop config panel depends on fixing the desktop cold-respawn defect (pool reap + 47s respawn
  vs 60s timeout — diagnosed in HANDOFF, unfixed).
- Where the user model lives: extend anansi state vs own store. (Hindsight stays
  untouched as provider — locked.)
- "There's more" — thread continues.
