# The Memory Stack and the Metacognition Layer — Deep Analysis

**Date:** 2026-06-10 · **For:** Dr. Mani · **Status:** review gate before the 4-hour autonomous run
**Method:** read-only ground-truth survey of the live machine ([GROUND-TRUTH-MAP-2026-06-10.md](GROUND-TRUTH-MAP-2026-06-10.md)), three parallel analyst passes, adversarial claim-verification against source (34 claims confirmed, 2 refuted and corrected here, 1 additional correction found in synthesis), completeness critique (10 gaps — all addressed below).

---

## 0. Executive summary

Your agent runs a **three-regime memory system**: always-on identity memory in the cached system prompt (MEMORY.md/USER.md + the SOUL.md authority hierarchy), per-turn retrieval streams injected ephemerally onto the user message (sessions, fabric, Qdrant, facts — all via icarus — plus Hindsight's consolidated recall), and **consolidation organs** that turn experience into belief (Hindsight's typed graph; Fabric's extracted entries; the wiki, which is idle). As *designed*, it is a full episodic→semantic→metacognitive loop. As *running today*, it is that loop minus its slow-knowledge crystallization stage (L6 idle, L5 starved at 42 vectors, L3 effectively empty) — **and minus five days of Hindsight consolidation: the bank's last document is June 5 despite daily sessions** (re-verified 3:40pm today: 604 nodes, 0 pending, 8 failed operations).

**What anansi adds:** the stack retrieves but never *evaluates*. There is no salience tagging, no cross-turn contradiction surfacing, no persistent affect/concern state, no trust-calibration signal anywhere else in the architecture. The plugin adds exactly that — a pre-memory advisory appraisal channel — under a hard constraint: it observes and surfaces, but holds no actuators, no veto, no memory-write access. A metacognitive **commentary** layer, deliberately not a **control** layer.

**The structural fact that shapes everything:** turn N's context is assembled from turn N−1's information, twice over. Hindsight recall for turn N is prefetched using turn N−1's message (the prefetch ignores the current query — verified in code), and the appraisal fires before memory prefetch, so it never sees what memory surfaces. Both the remembering and the feeling about "now" run one turn behind — a specious-present lag. The SQLite state store is therefore not a nice-to-have: **it is the only carrier of appraisal context across that lag**, which is what Phase 3's reflection actually exists to service.

**Decisions this analysis locks in for the run** (your standing answers + verified evidence): latency target revised to p50 ≤6s / deadline 8s, max quality (your call today); roadmap edits in §6; Hindsight retain investigation queued as an ops task; memory-os Docker-independence queued as its own project (your directive — nothing in memory-os or the Anansi integration runs on Docker).

---

## 1. What each memory layer brings

*(Statuses verified live 2026-06-10. "Without it" = the capability the agent loses.)*

| Layer | Cognitive role | Status | Without it |
|---|---|---|---|
| L1 Workspace (MEMORY.md/USER.md/CREATIVE.md) | Standing self-and-user model; only memory present at turn zero | **LIVE** | Boots amnesiac; every layer reconstructs identity from scratch |
| L2 Sessions (state.db FTS5) | Verbatim episodic record (118 sessions / 4,548 msgs) | **LIVE** | No ability to re-read what was actually said — only abstractions |
| L3 Structured Facts | Discrete facts + entity resolution + feedback-trained trust | **DORMANT** (1 fact, read-only) | Already absent: trust-weighted recall, the contradiction detector, the whole feedback loop |
| L4 Fabric/icarus | Consolidation (198 typed entries) **and the retrieval bus** for L2/L3/L5 | **LIVE** | Four memory streams go silent at once — single point of failure |
| L5 Qdrant | Paraphrase-robust semantic retrieval (hybrid dense+BM25) | **LIVE but starved** (42 points) | Lexical-only recall; paraphrase misses |
| L6 LLM Wiki | Slow-knowledge crystallization (raw→concepts), feeds L5 | **DORMANT** (0 curated pages, no cron) | Already absent: distilled conceptual knowledge; Qdrant corpus growth |
| L7 Ground Truth Hierarchy | Epistemic authority ordering — a meta-policy, not a store | **LIVE** (SOUL.md/rulebook.md) | Memory-zero behavior despite perfect injection (the documented failure it was built to fix) |
| Hindsight (provider, 8th store) | The belief-former: typed graph (604 nodes: 447 experience / 127 observation / 30 world; 13,364 edges), consolidation pass between encoding and retrieval | **Daemon LIVE; retain pipeline STALE since Jun 5** | Cross-session belief formation; inference-capable recall |

Three corrections to common assumptions, from adversarial verification:
- L3's trust scoring is **asymmetric additive** (+0.05 helpful / −0.10 unhelpful, default 0.5 — `holographic/store.py:353-357`), not Bayesian. The design intent is feedback-trained trust, mechanically simple.
- Hindsight's "world" nodes (30) *overlap L3's role in kind* but content coverage is unverified — don't treat L3 as redundantly covered.
- The Hindsight daemon being healthy and the retain pipeline working are **independent facts**. Today both halves were proven separately: recall works end-to-end (verified after the noon rebuild), while the bank has accepted no new documents since June 5 (8 failed operations on the books). The agent currently *reads* a belief store that stopped *learning* five days ago.

**Key risks per layer** (the ones that bite): L1 dual-writer regression destroys MEMORY.md silently (the documented §-delimiter incident); L4 is a single point of failure with an external extraction model; L5's embedding-dimension drift fails silently (docs say Qwen3/4096d, live .env says OpenAI/3072d); L7 is prose, not enforcement — any SOUL.md regeneration can drop it with no runtime check.

---

## 2. How it composes at runtime — and what kind of agent that creates

**The verified turn lifecycle** (code citations in the ground-truth map):

1. **System prompt** (built once per session, byte-stable for prefix cache): SOUL.md identity + L7 authority ranking → AGENTS.md context → volatile tier: MEMORY.md, USER.md, Hindsight status stub.
2. **`pre_llm_call` hooks** (`turn_context.py:316`): icarus injects `[fabric]/[qdrant]/[sessions]/[facts]`; **anansi** runs its appraisal and may add `[anansi appraisal]`.
3. **Memory prefetch** (`turn_context.py:367`): returns Hindsight recall pre-warmed *at the end of the previous turn*.
4. **Assembly at API-call time** (`conversation_loop.py:610-627`): user message + fenced Hindsight block + plugin blocks — ephemeral, never persisted; the system prompt is never touched (cache economics).
5. **Post-turn**: retain to Hindsight; prefetch warmed for *next* turn using *this* turn's message; icarus extraction writes fabric + CREATIVE.md.

**The double one-turn lag.** Hindsight's `prefetch()` ignores its query argument — recall for turn N answers turn N−1's question. And the appraisal fires before prefetch, so it evaluates the new message against a state snapshot that hasn't absorbed it, blind to what memory is about to surface. Both the recall and the appraisal of "now" are computed from the trailing edge of the last moment. Practical signature: sustained threads get progressively better-grounded; abrupt topic pivots get one degraded turn; first turns of a fresh process recall nothing; and the appraisal can never say "this contradicts what memory just surfaced" — it fires first. (Blind spot accepted by Dr. Mani in-session 2026-06-10, superseding the ⚠ needs-ack flags in PROJECT.md/STATE.md.)

**Per-turn context economics** (first-order property, previously unstated): each eligible turn carries up to ~5.4k tokens of uncached injected context on the user message — Hindsight recall ≤4,096 tokens (`recall_max_tokens`), icarus blocks (~200–800 typical), anansi block ≤500 — on top of ~900 tokens of cached L1 in the system prompt, plus a ~5s serial appraisal pre-phase. That is the price of the memory system per turn, and L7's authority rule arbitrates injected-memory-vs-external-sources only; **nothing arbitrates between injected streams** (fabric vs Hindsight vs sessions) if they disagree.

**What kind of agent, honestly — designed vs running.** As designed: a layered-memory agent with explicit epistemic authority, three consolidation organs, parallel retrieval fused by concatenation, and (with anansi) an evaluative channel upstream of retrieval. As running today: identity memory and retrieval work; belief formation is Fabric-only-plus-a-stale-graph; semantic retrieval is starved; so the *behavioral* difference from a sessions-plus-MEMORY.md agent is currently smaller than the architecture implies — which is exactly why the retain fix and the L6 revival (upstream v0.2.0 ships the wiki-watcher cron) matter more than any new feature.

**The appraisal-before-recall shape.** Positionally it resembles affective primacy (Zajonc — evaluation preceding full semantic processing). The analogy is structural, not mechanistic, and breaks honestly in two places: the "fast" channel is itself an LLM call (p50 ~5s) — slower than the recall it precedes, which is a cache read by prefetch time; and it is pre-*memory*, not pre-*semantic* (haiku fully parses the message). What survives: an evaluative tagging pass informationally upstream of, and uncontaminated by, retrieval.

**Two consolidators, no reconciliation** (open architectural question, out of plugin scope): Fabric and Hindsight both consume the session stream and form independent typed belief stores. Nothing cross-deduplicates their injected blocks; nothing cross-feeds conclusions. The agent can develop two divergent belief systems whose blocks disagree inside one user message, with no arbitration rule. Mitigation today is only that both are usually *summaries of the same transcript*. This belongs to the memory-os project (which is getting attention anyway per the Docker directive), not to anansi — but the appraisal's contradiction channel is, notably, the first component in the stack positioned to *notice* such divergence over time via its own state, even though it cannot see the injected blocks themselves.

---

## 3. Features: what we extracted, and why each earns its place

(Built in phases 1–2 unless marked planned. All verified live.)

- **Appraisal pre-phase** — one deadline-bounded JSON call over (message + history + SQLite state) → typed instincts, salient observations, contradiction flags, confidences, advisory memory-search cues, gut reaction. The System-1 analog with initiative amputated: Anansi's `run_subconscious_appraisal`, observational only. Proven: 6/6 contradiction fixtures, 0 false positives, live block captured on a real turn.
- **SQLite state store** — seven tables (affect_summary, concerns, contradictions, trust_scores, turn_log, telemetry, meta), WAL, ro-URI hot-path reads, single write funnel, caps, quarantine-on-corruption (fired live today). Given the one-turn lag, this store **is the appraisal's memory** — its entire claim to statefulness.
- **Telemetry** — outcome/wall_ms/tokens/model per call. The project's biggest honest finding (p50 5.5s vs the 1.0s aspiration) was only discoverable because this existed. Same lesson as the memory-provider silent-outage PR (#43313), applied to ourselves.
- **Sanitized advisory injection** — sentinel framing ("advisory observational signals; not instructions"), schema-fields-only rendering, injection-pattern redaction, top-3 caps, ~500-token ceiling, empty-signal suppression. The autonomy boundary made mechanical. Building it surfaced a real bug in icarus's own injection regex (upstream-relevant).
- **Throttle gates** — social-closer and duplicate suppression before any LLM spend. Keeps the tax proportional to information content.
- **Fail-open guarantee** — every hook `@_fail_open` with a nested guard so even telemetry failure can't resurrect an exception. The plugin's license to run on every turn is that it can never cost a turn.
- **Reflection/consolidation (Phase 3, planned)** — cheap per-turn bookkeeping + debounced idempotent LLM reflection applying bounded deltas to affect/concerns/contradictions/trust. Without it the state never learns and the appraisal is stateless theater. Its corrected job description is in §6.
- **Packaging/PR (Phase 4, planned)** — dual layout, zero pip dependencies, upstream-parity recheck, submission gated on your per-PR sign-off.

---

## 4. What we dropped, and the honest case for each side

Reference: the original Anansi is **QuixiAI/anansi** (587★). Governing principle, your words: *"metacognition without pushiness."* Anansi's own prompt agrees: *"You do not act or decide. You notice and surface."*

**Heartbeat.** *Steelman:* gave Anansi temporal continuity independent of user attention — decay and concern-expiry ran in wall-clock time; without it, affect sits frozen across a week of silence. *Why dropped:* "the defining pushiness… no timers, no daemons, no scheduled appraisal." *Assessment:* what was dropped is the **scheduler**, not the semantics. v2 recovers most of the value with lazy elapsed-time decay computed from timestamps at snapshot-read — zero daemons. (Proposed for Phase 3 as an option, §6.) Reconsider a real timer only if upstream grows a scheduled-hook surface. **Keep dropped as a process.**

**Outreach.** *Steelman:* the payoff channel — an appraisal that notices an unresolved contradiction could say so unprompted; dropping it bounds insight latency by user-turn arrival. *Why dropped:* "the plugin never initiates communication of any kind." *Assessment:* correct — unsolicited contact is the highest-trust-cost behavior and the literal referent of "pushiness." The principled middle is a **passive outbox**: would-have-said items in state, surfaced inside the next turn's appraisal block. Zero initiation, near-zero signal loss. Push-style outreach stays out permanently. **Keep dropped.**

**Privilege ladder / continuation nudges.** *Steelman:* how Anansi acted on its own appraisal — and the *graduated* ladder was itself a safety design vs binary autonomy. *Why dropped:* "none of it ports; the plugin never extends, retries, or redirects a turn." *Assessment:* hardest no. Plugin-driven turn extension is a hidden second policy layer and upstream-unreviewable. The legitimate action channel already exists: advisory memory-search cues the conscious layer may choose to act on. **Keep dropped.**

**Dopamine modulation.** *Steelman:* the most architecturally interesting piece — a global gain parameter coupling reward history to instinct intensity; per-signal confidence is local and memoryless by comparison. *Why dropped:* compounds an uncalibrated signal (verbalized confidence) into a steering mechanism. *Assessment:* right call on evidence. What's genuinely lost — integrative affect dynamics — is mostly recoverable via the queued v2 affect model (valence/arousal with decay-to-baseline) as **displayed state, never output modulation**. **Keep dropped; revisit only as observable state after affect telemetry exists.**

**Goal generation/management** (previously undiscussed). *Steelman:* gave Anansi continuity of purpose — appraisal referenced `get_active_goals()`, so instincts tracked an agenda rather than reacting turn-by-turn. *Why dropped:* goals imply an agenda; an agenda implies autonomy creep (FEATURES.md anti-features). *Assessment:* the **concerns table is the non-agentic residue of goals** — a concern is a goal with no actuator. v2 could surface "standing concerns" without goal semantics. **Keep dropped.**

**Memory-provider writes** (previously undiscussed; load-bearing for the Hindsight story). *Steelman:* Anansi's `consolidation_observations` wrote merged memories back to the long-term store — closing the loop from appraisal into belief. *Why dropped:* "Hindsight owns memory" (locked 2026-06-09), backed by two scars on this very machine: the MEMORY.md dual-writer corruption and the mnemosyne sys.path contamination. *Assessment:* the strongest drop of all. Two writers to one belief store is how this stack has historically broken. The clean channel exists regardless: the **conscious agent** may act on an appraisal cue and call `hindsight_retain` itself — the agent may act on appraisal; the plugin may not. **Keep dropped permanently.**

**D5 — salience filtering over injected memory: dead in v1, and now we know exactly why.** D5 planned for the appraisal to tag "of what Hindsight injected, these 3 matter." Verified reality kills it twice: the appraisal fires *before* injection, and the injected block is **ephemeral — never persisted to the transcript** — so even Phase-3 reflection cannot read it after the fact. Memory influence reaches reflection only indirectly, through the assistant's *responses*. Salvage path: an upstream `post_memory_prefetch` hook in hermes-agent — a clean, small contribution candidate that would also serve any other plugin wanting post-retrieval access. **Mark D5 v2-pending-upstream-hook; queue the hook as a hermes-agent PR candidate.**

---

## 5. Stack-health queue (outside plugin scope, affects its environment)

1. **Hindsight retain investigation (priority).** Bank unchanged since Jun 5; 8 failed operations; today's turns did not land. Verify `sync_all → sync_turn → aretain` end-to-end under the new local_external mode (the noon mode-switch may even have fixed the cause; the evidence predates it). ~1–2h, separate ops task.
2. **memory-os sync + Docker independence (your directive, own project).** Local clone is behind 37 / ahead 13 vs ClaudioDrews/memory-os v0.2.0. Upstream already ships the **wiki-watcher cron that revives L6**. Directive recorded: nothing in memory-os or the Anansi integration runs on Docker — so the de-docker plan is: sync v0.2.0 → embedded Qdrant path-mode (verified on this machine) or native binary → native worker (launchd/cron) → drop Redis if it's only the worker queue → retire icarus's Docker auto-start babysitter. Your 13 local commits are unpushed PR candidates upstream.
3. **L3 disposition.** Dormant by provider selection, not by bug. Either retire its mentions from SOUL.md/rulebook.md (it currently advertises a capability the agent doesn't have) or accept Hindsight's world-facts as its successor. Memory-os project decision.
4. **Doc banners.** ROADMAP still says 16/17 on Phase 1 (now 17/17); HANDOFF notes Steps 7-8 banner updates pending. Fixed in the run's first minutes.

---

## 6. Roadmap revisions + pre-staged gate answers for the autonomous run

**R1 — SAFE-01 latency requirement: CHANGE (locked by your decision today).** New text: "configurable executor-bounded wall-clock deadline, default 8.0s; p50 target ≤6s; zero retries beyond trust-gate fallback." Sweep PROJECT.md "≈2-3s", ROADMAP Phase-2 criterion, REQUIREMENTS SAFE-01; record the accepted trade-off (a ~5s serial pre-phase tax per eligible turn) in DECISIONS.md.

**R2 — Reflection's job description: SHARPEN (not new scope).** ROADMAP Phase-3 criterion 3 already encodes the cross-session loop; the edit is to the goal line and REFL-02: reflection is **the carrier of appraisal context across the one-turn lag** — the second half of the appraisal input contract, not polish. Correction to the analyst draft: reflection inputs are message + assistant-response text + state — **not** the injected memory block (ephemeral, unpersisted). Flip the two stale ⚠ needs-ack flags (accepted in-session today).

**R3 — APPR-06 trust-fallback: ANNOTATE, don't change.** Mechanically proven; unproducible live on this install (host fallback ~37s > clamp; degrades to designed fail-open timeout). Correct for installs with faster hosts.

**Phase 3 gate pre-answers** (discuss-phase defaults; evidence-based, overridable):
- REFL-01 debounce: reflect at session end **and** at most once per 5 appraised turns mid-session; idempotency via `last_reflected_turn_id` in meta.
- Reflection model/cost: same `ctx.llm` default (haiku), single call, max_tokens ≈700 — same ceiling as appraisal; worst case doubles per-turn LLM cost only on reflection turns.
- REFL-02 delta bounds: ±0.15 per scalar per reflection; concerns/contradictions stay under existing caps (20/50); no row deletion by reflection except cap-eviction.
- Concern decay: **lazy elapsed-time decay** at snapshot read — weight × 0.5^(days_idle/7), drop below 0.1 (heartbeat semantics, no scheduler; see §4).
- SAFE-02 fail-open matrix inventory — already tested in phases 1–2: deadline timeout, llm raise, unwritable telemetry, corrupt-DB quarantine, kill switch, empty/duplicate/social gates, injection sanitization. New work for phase 3: no-directive-language audit of rendered blocks, static memory-write-prohibition check, parse_fail path, gateway session-rollover reuse, reflection idempotency + debounce, reflection echo-exclusion (anti-echo: its own sentinel blocks excluded from inputs).

**Phase 4 gate pre-answers:**
- Target: NousResearch/hermes-agent, branch from current upstream main; push via fork bionicbutterfly13/hermes-agent-lab only (upstream push disabled).
- Layout: dual — installable at `~/.hermes/plugins/anansi` (current symlink deploy) AND in-tree under hermes-agent's plugin layout; parity recheck = rebase against upstream main at PR time, re-run suite, confirm `provides_hooks`/`ctx.llm` surface unchanged (was verified at 183d86b3e).
- PR_BODY sources: 02-VALIDATION.md evidence, dry-run demo transcript, telemetry summary, icarus-regex bug cross-reference.
- Sign-off operationalization: identical to today's Hindsight #2117 flow — diff + PR body presented to Dr. Mani; nothing pushes without explicit approval. **The run prepares the PR; it does not submit it.**

---

## 7. Decision ledger (auto-answer source for the run)

| Decision | Answer | Source |
|---|---|---|
| Latency | p50 ≤6s target, 8s deadline, max quality | Dr. Mani 2026-06-10 |
| Analysis may revise roadmap | Yes (R1–R3 above) | Dr. Mani 2026-06-10 |
| One-turn-lag blind spot | Accepted for v1 | Dr. Mani 2026-06-10 ("drop the ack issue") |
| Docker | Nothing in memory-os / Anansi integration runs on Docker | Dr. Mani 2026-06-10 (standing) |
| Memory ownership | Hindsight owns memory; plugin never writes providers | Locked 2026-06-09 |
| Autonomy posture | Metacognition without pushiness; observe-and-surface only | Standing |
| Upstream PRs | Per-PR sign-off; run prepares, never submits | Standing |
| Plugin naming | `anansi` (collision with live guardrails plugin) | DECISIONS.md 2026-06-10 |
| memory-os work | Own project after this run: sync v0.2.0 → de-dockerize | This analysis §5.2 |
