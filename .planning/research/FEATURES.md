# FEATURES.md — Metacognition / Subconscious Appraisal Plugin

**Domain:** Hook-based "subconscious appraisal" layer for hermes-agent — pre-turn instincts, salience, contradiction, and confidence signals. Appraisal only; zero autonomy.

**Researched:** 2026-06-10
**Ground truth:** `/Volumes/Asylum/repos/hex-auto/Anansi/services/agent.py::run_subconscious_appraisal`, `/Volumes/Asylum/repos/hex-auto/Anansi/services/prompts/subconscious.md`, `/Volumes/Asylum/repos/hex-auto/Anansi/core/subconscious.py`
**Constraints inherited from PROJECT.md:** fail-open, ≤~500-token injection, SQLite-only state, Hindsight keeps the MemoryProvider slot.

Confidence legend: **HIGH** = verified in local source and/or official docs + multiple sources. **MEDIUM** = web-verified, one strong source. **LOW** = single/unverified source — validate before relying on it.

---

## Table Stakes

Features every credible appraisal/reflection layer has. Omitting any of these makes the plugin feel broken or unsafe.

| # | Feature | What it is | Complexity | Depends on | Confidence |
|---|---------|------------|------------|------------|------------|
| T1 | **Per-turn appraisal call** | Fast JSON-mode LLM call over (user message + injected memory context + local state) producing structured signals: instincts, salient memories, gut reaction | Medium | — (core) | HIGH — exact mechanism in Anansi `run_subconscious_appraisal`; pre-turn metacognitive evaluation is the standard pattern in 2026 reflection literature |
| T2 | **Compact structured injection block** | Signals formatted into a small markdown block (Anansi: `## Subconscious Signals`, top-3 per category, gut reaction truncated to 200 chars). Cap total at ~500 tokens | Low | T1 | HIGH — Anansi `format_subconscious_signals` slices `[:3]` per category; context-budget discipline is universal advice |
| T3 | **Strict fail-open everywhere** | Any error/timeout/parse failure → empty injection, never a blocked turn. Anansi: `fallback={}`, exception → empty `SubconsciousOutput`, and the whole pre-phase is wrapped in try/except | Low–Medium | T1 | HIGH — verified in source at three layers; PROJECT.md hard requirement (timeout ≈ 2–3s) |
| T4 | **Empty-signal suppression** | If nothing is salient, inject nothing. Anansi returns `""` when only the header would be emitted; prompt instructs "return empty arrays" below confidence 0.6 | Low | T2 | HIGH — verified in source; prevents the layer from becoming per-turn noise |
| T5 | **Per-signal confidence threshold** | Appraisal model self-reports confidence per observation; only items above threshold (Anansi: 0.6) surface | Low | T1 | HIGH — in `subconscious.md` prompt schema (`"confidence": 0.7`); note the caveat under D2 about verbalized confidence reliability |
| T6 | **Separately configurable cheap appraisal model** | Appraisal model resolved from config independently of the main chat model (Anansi: `llm.subconscious` with fallback `llm.heartbeat`) | Low | — | HIGH — verified in source; one cheap call/turn is the accepted cost envelope |
| T7 | **Config kill switch** | Single boolean to disable the appraisal pre-phase entirely (Anansi: `chat.inline_subconscious_enabled`, default true) | Low | — | HIGH — verified in source |
| T8 | **Persistent local appraisal state** | Lightweight affect summary, active-concern list, contradiction log, confidence/trust scores in SQLite under `$HERMES_HOME`; loaded at `on_session_start`, fed into T1's context | Medium | schema design | HIGH that state persistence is table stakes (Anansi persists affect/goals/dopamine in Postgres; Reflexion's episodic memory buffer is the canonical pattern); MEDIUM on exact schema — this is the main porting design work |
| T9 | **Session-end reflection pass** | `on_session_end` reads the transcript, extracts observations, applies them to local state — the `apply_subconscious_observations` equivalent. Reflection-then-memory-update is the Reflexion verbal-reinforcement loop | Medium | T1 output shape, T8 | HIGH for the pattern (Reflexion, NeurIPS 2023, still the 2026 reference design); HIGH that Anansi does this via stored proc; MEDIUM on the SQLite reimplementation details |
| T10 | **Observability of the appraisal** | Log raw appraisal output and emit phase markers (Anansi emits `PHASE_CHANGE {"phase": "subconscious"}` events); without this you cannot debug why a signal appeared | Low | T1 | HIGH — verified in source; agent observability is repeatedly cited as a 2026 production requirement |

**Dependency spine:** T1 → T2/T4/T5 → injection; T8 → T1 (state feeds appraisal context) and T9 → T8 (reflection writes state). T3 wraps everything.

---

## Differentiators

Features that distinguish this plugin from generic "reflection" middleware. Most come straight from Anansi and are rare in the open ecosystem.

| # | Feature | What it is | Complexity | Depends on | Confidence |
|---|---------|------------|------------|------------|------------|
| D1 | **Contradiction surfacing** | Appraisal flags semantic/narrative/relational/emotional contradictions between current input and stored state/memory; contradiction log persisted and re-surfaced when relevant. Contradiction resolution is now a named category in 2026 memory benchmarks (BEAM) and a known failure mode of append-only memory | High | T1, T8, injected memory context | MEDIUM-HIGH — Anansi schema has `contradiction_observations`; ecosystem confirms the problem matters; the *quality* of cheap-model contradiction detection is unproven (LOW) — validate empirically |
| D2 | **Confidence/trust scoring (dopamine replacement)** | Per-domain trust scores and an overall confidence signal in state, surfaced as "low confidence on X" cues — same signal value as Anansi dopamine, none of the drive mechanics | Medium | T8, T9 | MEDIUM — design decision is locked (PROJECT.md); research caveat: verbalized self-confidence is a noisy, biased proxy (2026 calibration literature) — treat scores as *hints to the conscious layer*, never as gates |
| D3 | **Dimensional affect summary (valence/arousal)** | Persisted lightweight emotional state as primary_emotion + valence (−1..1) + arousal (0..1) + intensity, updated by reflection and decaying toward baseline. 2026 research (external affective subsystems, VAD-space steering) supports maintaining affect *outside* the LLM for consistency | Medium | T8, T9 | HIGH that Anansi does exactly this (prompt schema verified); MEDIUM that it improves output quality in an assistant context — measure before expanding |
| D4 | **Memory-expansion cues** | Appraisal suggests follow-up recall queries ("Suggested memory searches: ...") that the *conscious* agent may choose to run. Surfaces recall gaps without the plugin ever executing a search itself | Low | T1; value requires the agent to have a recall tool (Hindsight) | HIGH — verified in Anansi source and prompt; cleanly autonomy-free because it is advisory text only |
| D5 | **Salience filtering / noise demotion over injected memory** | Appraisal ranks the memory context Hindsight already injected: "these 3 matter because X; ignore Y as noise." Complements rather than competes with the provider — salience-tiering of retrieved context mirrors 2026 memory-orchestration practice | Medium | T1, Hindsight-injected context present | MEDIUM — Anansi does salient-memory filtering over its own RAG list; doing it over *another provider's* injection block is novel to this plugin — verify the appraisal model can reference Hindsight's memory IDs/format |
| D6 | **Active-concern continuity** | Open loops ("Dr. Mani asked about X yesterday, unresolved") carried in state across sessions with decay/expiry, surfaced only when relevant to the current turn | Medium | T8, T9 | MEDIUM — derived from Anansi goals/narrative observations; decay policy is unvalidated design (LOW) — keep the list small and aggressively pruned |
| D7 | **Instinct vocabulary with intensity** | Typed gut impulses (approach/avoid/caution/curiosity/protect) with 0–1 intensity and a one-line reason — richer than generic "reflection text" and cheap to render | Low | T1 | HIGH — verified in Anansi prompt and formatter |

**Recommended priority:** D4 and D7 are nearly free once T1 exists (same JSON schema). D1 and D2 are the project's stated identity ("metacognition slice") — build them, but behind the same fail-open/empty-suppression discipline. D3, D5, D6 are second-wave: ship minimal versions, validate signal quality before deepening.

---

## Anti-Features

Explicitly do NOT build. The first four are firm decisions from PROJECT.md ("metacognition without pushiness" — Dr. Mani); the rest are autonomy-creep patterns adjacent to this design that must be guarded against.

### Firm exclusions (locked)

| Anti-feature | Why excluded |
|--------------|--------------|
| **Heartbeat / always-on background cycles** | The defining pushiness of original Anansi; explicitly dropped. No timers, no daemons, no scheduled appraisal — hooks fire only on real turns/sessions |
| **Outreach / reach_out / unsolicited contact** | Appraisal-only cycle; the plugin never initiates communication of any kind |
| **Privilege ladder / backlog escalation / continuation nudges** | Anansi heartbeat machinery (`continuation_prompt`, `max_continuations` in `run_agent`) — none of it ports. The plugin never extends, retries, or redirects a turn |
| **Dopamine/reward modulation** | Replaced by plain confidence/trust scoring (D2). No tonic/spike state, no intensity modulation of instincts by reward level (the Anansi prompt's "when dopamine tonic is high, lean toward stronger approach impulses" logic is dropped) |

### Autonomy-creep features to refuse (researcher-identified)

| Anti-feature | Why it's creep |
|--------------|----------------|
| **Plugin-executed tool calls or memory searches** | D4's expansion cues must stay advisory text. The moment the appraisal phase *runs* a search or tool, it has initiative. Anansi's own prompt is the rule: "You do not act or decide. You notice and surface." |
| **Directive/steering language in the injection** | Signals must be observational ("instinct: caution (0.7) — topic resembles prior incident"), never imperative ("refuse this", "do X first"). Directives convert appraisal into a hidden second policy layer |
| **Turn gating on appraisal results** | E.g., blocking or delaying the answer when confidence is low. Violates fail-open; also unsound — 2026 calibration research shows verbalized confidence is too noisy to use as a control signal |
| **Writing to the memory provider** | Anansi's `consolidation_observations` suggested memory merges. Here, all observations apply to *local SQLite state only*. Hindsight owns memory (locked 2026-06-09); mutating it from the plugin is both autonomy creep and a provider-boundary violation |
| **Goal generation/management** | Anansi fed `get_active_goals()` into appraisal and had goal machinery. Goal *creation* is drive mechanics. At most, track concerns (D6) as decaying observations — never as goals the agent is urged to pursue |
| **Self-modifying prompts/config from the reflection pass** | T9 updates *state*, never its own appraisal prompt, thresholds, or model selection. Unbounded self-modification is the classic self-improvement creep path |
| **Unbounded state growth / hidden profiling** | Append-only observation logs degrade retrieval and become a privacy liability (2026 memory-curation literature: uncurated memory accumulates contradictions and noise, and became an attack surface). Enforce caps, decay, and pruning on every state table; state stays local per PROJECT.md privacy constraint |
| **Mood-driven output modulation** | Persisting affect (D3) is fine; *enforcing* tone/behavior changes from it (temperature shifts, persona switching) is steering. The conscious model sees the affect line and decides for itself |
| **Multi-call appraisal chains / debate loops** | Multi-agent debate and LATS-style search exist in the 2026 reflection ecosystem but blow the one-cheap-call-per-turn cost and latency budget. One call, hard timeout, done |
| **Import-time `sys.path` mutation** | Known hermes-agent plugin-discovery flaw (mnemosyne symlink incident, PROJECT.md). Implementation-level, but listed here because it is a standing "never" |

---

## Feature Dependency Map (build-order hint for roadmapper)

```
T6/T7 (config)  ──┐
T1 (appraisal call) ──► T5 (thresholds) ──► T2 (injection) ──► T4 (suppression)
        │                                        ▲
T3 (fail-open wraps all)                         │
        │                                        │
T8 (SQLite state) ──► feeds T1 context ──► D1/D2/D3/D6 signals
        ▲
T9 (session-end reflection) writes T8
T10 (observability) instruments everything
D4/D7 ride on T1's schema (near-free)
D5 requires Hindsight-injected context to be readable/referencable
```

---

## Sources

- Local (HIGH): `/Volumes/Asylum/repos/hex-auto/Anansi/services/agent.py` (`run_subconscious_appraisal`, `format_subconscious_signals`, `SubconsciousOutput`), `/Volumes/Asylum/repos/hex-auto/Anansi/services/prompts/subconscious.md`, `/Volumes/Asylum/repos/hex-auto/Anansi/core/subconscious.py`, `/Volumes/Asylum/repos/hermes-anansi-plugin/.planning/PROJECT.md`
- Reflexion — verbal reinforcement + episodic memory buffer: https://arxiv.org/abs/2303.11366 ; 2026 pattern surveys: https://zylos.ai/research/2026-03-06-ai-agent-reflection-self-evaluation-patterns , https://zylos.ai/research/2026-05-12-agent-self-correction-reflexion-to-prm
- Metacognitive capabilities taxonomy (uncertainty estimation, error detection, reflection): https://www.emergentmind.com/topics/metacognitive-capabilities-in-llms ; metacognitive error-correction architecture: https://dilab.gatech.edu/test/wp-content/uploads/2026/02/A-Metacognitive-Architecture-for-Correcting-LLM-Errors-in-AI-Agents.pdf
- Affective dynamics / external affect subsystem, VAD framing: https://co-r-e.com/method/affective-dynamics-llm-agents ; valence–arousal structure in LLM representations: https://arxiv.org/pdf/2604.07382 , https://arxiv.org/html/2604.00005v1 ; appraisal-based chain-of-emotion: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11086867/
- Contradiction detection / memory curation / salience tiering (2026): https://mem0.ai/blog/state-of-ai-agent-memory-2026 , https://0latency.ai/blog/contradiction-detection.html , https://dev.to/vektor_memory_43f51a32376/the-state-of-ai-agent-memory-in-2026-what-the-research-actually-shows-3aja , https://llms3.com/blog/when-memory-became-the-attack-surface-may-2026
- Confidence calibration limits (verbalized confidence is a noisy control signal): https://zylos.ai/research/2026-04-18-llm-calibration-uncertainty-production-agents , https://arxiv.org/abs/2603.05881 , https://dl.acm.org/doi/10.1145/3711896.3736569

**Known gaps (flagged, not hidden):** No public production example was found of a *pre-turn* appraisal injection layer as a plugin for a third-party agent harness — Anansi appears to be the only direct precedent in scope (LOW external validation; HIGH internal). Cheap-model contradiction-detection quality and concern-decay policy are unvalidated — recommend the roadmapper flag those phases for empirical validation.
