# User-Model Source Survey — 2026-06-10 (four parallel surveys, full reports in session transcript)

Companion to DESIGN-REWIND-2026-06-10.md. Lens: daily background UX. Possibilities, not a roadmap.

## Source inventory

| Repo | What it is | Unique extractables | Maturity |
|---|---|---|---|
| /Volumes/Asylum/repos/agi-memory (QuixiAI, Feb 2026 = proto-Anansi v1.0.5) | Postgres/AGE 6-layer cognitive memory | Worldview schema: {confidence, stability(update resistance), category: belief/value/boundary/pattern/relationship, origin: discovered/user_stated/derived/foundational, trigger_patterns, response_type: refuse/negotiate/flag/educate}; dopamine RPE = (valence−expected)×(0.5+arousal/2), spike>0.15 → memory boost + tonic EMA (db/28_functions_dopamine.sql); 5 drives (curiosity/coherence/connection/competence/rest); energy budget 20u/cycle, costed actions (observe 0 → reach_out_public 7); observation ingestion pipeline (db/17_*, ~1500 lines: narrative/relationship/contradiction/emotional → discrete table/graph ops); boundary check (db/12_*: embedding 0.75 + keywords) | Production, 96 tests, PyPI |
| /Volumes/Asylum/repos/hex-auto/Anansi (May 2026) | Successor | RecMem turn-level consolidation (idempotency keys); reconsolidation sweeps (belief flip → re-eval CONTESTED_BECAUSE/SUPPORTS-linked memories, batch 8/LLM call); runtime persistence tables | Active |
| /Volumes/Asylum/repos/nemori (+ paper arxiv:2508.03341) | Episodic memory system | Boundary detection (confidence-scored semantic shift → auto-segment); prediction-correction (predict facts from model, diff vs reality = novelty detector); embedding dedup + supersession for belief updates | v0.2.0, 24 tests, LoCoMo-evaled |
| /Volumes/Asylum/repos/REMem (ICLR 2026) | Hybrid graph memory | Gist→fact extraction priming; per-type embedding stores; CONTRADICTS/SUPPORTS/CAUSES/DERIVED_FROM graph propagation | Runnable, thin tests |
| /Volumes/Asylum/repos/Dionysus2.0 (Dr. Mani) | IWMT-MAC consciousness architecture | Hot/Warm/Cold TTL tier migration (multi_tier_memory.py); MosaicObservation per-turn schema (6 obs types + self_awareness/self_model_coherence); IWMT spatial/temporal/causal coherence trackers; AutobiographicalJourney + episode boundaries + ConsciousnessLevel tagging (autonoesis: UNCONSCIOUS→METACONSCIOUS) | Runs; mixed maturity |
| /Volumes/Asylum/repos/dionysus-HDDLGym (Dr. Mani) | HTN planning | Goal → method → task decomposition; policy-weighted action selection — operationalizes "plan together and break down" + strategic layer | Mature framework |
| ActiveInference.jl / enactive_inference_model / aif_iwai2025_thoughtseeds | AIF/IWMT formalisms | CONCEPTS ONLY: EFE goal-salience score G = preference-mismatch − entropy-reduction; habit priors (EMA pseudo-counts per domain); precision-weighted state fusion (1 param/domain); meta-awareness = KL(evidence‖habit)×gate; distraction-buildup ∫mismatch dt > θ → reflect prompt | Published (2 peer-reviewed); code skip |

## Mapping to the layered autobiographical user model

| Layer | Mechanism (source) |
|---|---|
| Episodic | nemori boundary detection; Dionysus episode boundaries + autonoesis tags |
| Semantic | nemori prediction-correction + dedup/supersession |
| Procedural | REMem gist→fact; agi-memory procedural type (weakest layer everywhere) |
| Strategic | HDDLGym HTN hierarchies; agi-memory patterns w/ evidence chains |
| Worldview | agi-memory schema (confidence ⊥ stability; boundaries w/ response types); REMem contradiction edges; Anansi reconsolidation on flips |
| Goal | agi-memory goal-as-memory (priority active/queued/backburner; source=user_request — Dr. Mani mints); HTN breakdown; EFE ranking for what to surface |
| User-dopamine | agi-memory RPE pointed at USER + AIF habit priors + precision + distraction threshold |
| Boundedness | agi-memory energy budget (costed actions, hard cap/wakeup) + domain whitelist |

## Fit/overlap rules

- All schemas port into anansi SQLite; Postgres/AGE/Redis/Neo4j stacks stay behind.
- Hindsight remains sole MemoryProvider (locked). This layer = stance + user autobiography, not event memory.
- Energy budget is the structural answer to "kept in check with boundaries"; config (desktop panel later) sets budgets/cadence/domains.
- Reconsolidation + consolidation require the scheduled heartbeat (can't fit in 8s turns).

## Daily-UX value order (candidate increments)

1. Worldview store w/ supersession + contradiction edges — agent notices belief change ("you've reversed on X")
2. Goal layer + per-turn accountability (DESIGN-REWIND drive mapping)
3. Episode/autobiography — "what we did together" recall w/ autonoesis tags
4. User-dopamine habit sync — RPE + habit priors + distraction→reflect trigger, bounded domains
5. Reconsolidation sweeps on belief flips (heartbeat-gated)
