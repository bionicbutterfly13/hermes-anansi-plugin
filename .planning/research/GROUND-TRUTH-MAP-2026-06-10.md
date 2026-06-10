# Ground-Truth Map: Hermes Memory Stack (memory-os 7 layers + Hindsight + anansi)

> Produced 2026-06-10 by read-only survey of the live machine (repo /Volumes/Asylum/repos/memory-os,
> live install ~/.hermes, code ~/.hermes/hermes-agent, planning /Volumes/Asylum/repos/hermes-anansi-plugin).
> Input for the memory-stack analysis. All file:line citations verified at survey time.

# A. The Seven Layers (defined in /Volumes/Asylum/repos/memory-os/README.md "Architecture: 7 memory layers" + layers/01–07)

The repo defines all seven **unambiguously** — the durable-memory "7th layer open question" is answered: **Layer 7 = Ground Truth Hierarchy** (`/Volumes/Asylum/repos/memory-os/layers/07-ground-truth.md`, "Discovered: 2026-05-31").

**L1 — Workspace** (`layers/01-workspace.md`)
- Function: always-injected durable memory. Files: `~/.hermes/memories/MEMORY.md` (`§`-delimited, written by the `memory` tool — `~/.hermes/hermes-agent/tools/memory_tool.py`), `USER.md` (manual), `CREATIVE.md` (written by icarus `state.py:1178-1189`, deliberately separated from MEMORY.md after the dual-writer corruption, issue #26045).
- Read path: system-prompt volatile tier — `~/.hermes/hermes-agent/agent/system_prompt.py:307-318` (`format_for_system_prompt("memory")` + `"user"`). Config: `~/.hermes/config.yaml:318-323` (`memory_enabled: true`, `memory_char_limit: 2200`, `user_char_limit: 1375`).
- **LIVE** (MEMORY.md 13 entries; CREATIVE.md present). Note: CREATIVE.md is icarus-written state, not system-prompt-injected by hermes core.

**L2 — Sessions** (`layers/02-sessions.md`)
- Function: FTS5 full-text over all conversations. Storage: `~/.hermes/state.db` (118 sessions). Write: gateway, automatic. Read: `session_search` tool (`hermes-agent/tools/session_search_tool.py`) + icarus auto-injection `_search_sessions()` (`~/.hermes/plugins/icarus/hooks.py:390`, read-only FTS5, labeled `[sessions]`, top_k=2).
- **LIVE**.

**L3 — Structured Facts** (`layers/03-fact-store.md`)
- Function: durable facts + entity resolution + trust scoring. Storage: `~/.hermes/memory_store.db` (exists, **contains exactly 1 fact**). Write path: `fact_store` tool — implemented only in `hermes-agent/plugins/memory/holographic/__init__.py`, which is a memory *provider*; since `config.yaml:323` sets `provider: hindsight`, the holographic provider (and its tools/feedback loop) is **not registered**. Read path: icarus `_search_facts()` (`hooks.py:463-490`, FTS5 read-only, first-turn-only, labeled `[facts]`).
- **Configured-but-dormant**: read-side injection wired, write side and trust-feedback loop have no live tool.

**L4 — Fabric / Icarus** (`layers/04-icarus-fabric.md`)
- Function: LLM-extracted cross-session entries (decision/resolution/note…), 16 tools, 4 hooks. Plugin: `~/.hermes/plugins/icarus/` (fork, `plugin.yaml`: fabric_recall…fabric_report; hooks on_session_start/pre_llm_call/post_llm_call/on_session_end). Storage: `FABRIC_DIR=/Users/manisaintvictor/memory-os/vault/fabric` (set in `~/.hermes/.env`) — **198 entries**. Write: `post_llm_call`/`on_session_end` extraction (`hooks.py:700+`), `fabric_write`. Read: `state.recall()` in `pre_llm_call` (`hooks.py:598`), labeled `[fabric]`, per-session dedup sets (`hooks.py:68`).
- **LIVE** (enabled in `config.yaml:592`).

**L5 — Qdrant** (`layers/05-qdrant.md`)
- Function: semantic knowledge base, 4096d Qwen3-Embedding-8B (OpenRouter) + BM25, 4-level fallback cascade. Runtime: containers `memory-os-qdrant-1`, `memory-os-redis-1`, `memory-os-worker-1` all Up; collection `knowledge_base` = **42 points, status green**. Read: icarus `_search_qdrant()` (`hooks.py:335-371`) imports `scripts/context_enhancer.py` from `MEMORY_OS_REPO=/Volumes/Asylum/repos/memory-os` (`hooks.py:348`), threshold 0.55, labeled `[qdrant]`; includes Docker auto-start of Qdrant (`hooks.py:215-330`). Write: worker/ingest pipelines.
- **LIVE** for read/injection; ingest write-side runs against a different profile (see E).

**L6 — LLM Wiki** (`layers/06-llm-wiki.md`)
- Function: self-curating vault (raw→concepts/entities/comparisons) + hourly Qdrant ingest. Storage: `~/memory-os/vault/wiki/` — `raw/` has 19 "computational-unconscious" docs, but `concepts/` and `entities/` are **empty**; `crontab -l` is empty and `~/.hermes/cron/` contains only `output/` — neither wiki-agent nor continuous-ingest is scheduled on the default profile.
- **Dormant** (scaffolded vault, no curation pipeline running).

**L7 — Ground Truth Hierarchy** (`layers/07-ground-truth.md`, `modifications/soul-rulebook.md`)
- Function: identity-layer instruction making injected memory authoritative (rank 2 of 4, above docs, below terminal output) — the fix for "memory-zero behavior despite perfect injection."
- Live: `~/.hermes/SOUL.md:2-19` ("**Injected memory** — qdrant, fabric, sessions, facts… injected memory wins"; "You already know this. Don't re-discover it. Use it.") and `~/.hermes/rulebook.md:5`.
- **LIVE**.

# B. Hindsight's Role

Hindsight is the **only registered MemoryProvider** (`config.yaml:323 provider: hindsight`) — an eighth store layered alongside the memory-os seven, not one of them.

- Runtime: `~/.hermes/hindsight/config.json` — `mode: local_external`, `api_url: http://127.0.0.1:9177`, bank `hermes`, `budget/recall_budget: mid`, `llm_provider: openai / gpt-4o-mini`. Daemon confirmed: pid 33502 `~/.hermes/venvs/hindsight/bin/hindsight-api --daemon --idle-timeout 0 --port 9177`, healthy; embedded postgres `~/.pg0/instances/hindsight-embed-hermes`. Bank stats (live API): **fact_count 604, last_document_at 2026-06-05**. A backup `config.json.bak-localexternal-20260610` shows the mode was switched today.
- **In (retain):** after the final response, `run_agent.py:2977` → `memory_manager.sync_all()` (background single-writer thread, `memory_manager.py:429-470`) → provider `sync_turn()` (`plugins/memory/hindsight/__init__.py:1446`) → retain queue → `aretain` to bank `hermes` (append-mode delta when API supports it, `__init__.py:56,153-178`). Manual: `hindsight_retain` tool (`__init__.py:242,1547`).
- **Out (recall):** `queue_prefetch()` (`__init__.py:1329-1374`) runs `arecall` (default `recall_types=["observation"]`, `recall_max_tokens 4096`) on a background thread; `prefetch()` (`__init__.py:1311-1327`) joins that thread (≤3s) and returns the cached result under the header "# Hindsight Memory (persistent cross-session context)… Do not call tools to look up information that is already present here." Tools: `hindsight_recall` / `hindsight_reflect`. A static status block also goes in the system prompt (`__init__.py:1289-1309` via `system_prompt.py:320-327`).
- **Timing quirk (verified):** `queue_prefetch_all` is called only at the end of the previous turn with that turn's message (`run_agent.py:2982`); `prefetch()` ignores the current query. So **Hindsight auto-recall for turn N is keyed on turn N-1's message** — first turn of a fresh process gets nothing.

# C. Turn-Lifecycle Timeline (one user turn)

1. **System prompt** (built once/session, `system_prompt.py`): stable tier = SOUL.md identity incl. Ground Truth hierarchy (L7) + tool/skills guidance; context tier = AGENTS.md etc.; volatile tier = **MEMORY.md block (L1) → USER.md block → Hindsight status block** (`system_prompt.py:307-327`).
2. **`pre_llm_call` plugin hooks fire** — `turn_context.py:316-341`, comment: "context injected into user message, not system prompt." Registered hooks: **icarus** (`hooks.py:573` — injects `[fabric]`/`[qdrant]`/`[sessions]`/`[facts]` from L2-L5), **anansi** (`plugins/anansi/__init__.py:80-165` — Haiku JSON appraisal → sanitized `[anansi appraisal]` block), anansi-guardrails (tool-call hooks only, no pre_llm_call). Results concatenated into `plugin_user_context`.
3. **Memory provider `on_turn_start`** — `turn_context.py:359-365` (no-op for Hindsight, `memory_provider.py:165`).
4. **Memory prefetch** — `turn_context.py:367-374` `prefetch_all()` returns the pre-warmed Hindsight recall. **Ordering proof: hook dispatch at :316 precedes prefetch at :367.**
5. **Assembly at API-call time** — `conversation_loop.py:610-627`: the current user message gets, appended in order, (a) the fenced Hindsight memory block (`build_memory_context_block(_ext_prefetch_cache)`, line 617-620), then (b) `plugin_user_context` (icarus + anansi blocks, line 621-622). Ephemeral only — never persisted (comment lines 610-615); system prompt deliberately untouched to preserve prefix cache (lines 651-661).
6. **Post-turn:** `run_agent.py:2977` retain (`sync_all`) + `:2982` `queue_prefetch_all` (pre-warm next turn's recall); icarus `post_llm_call`/`on_session_end` extraction writes fabric + CREATIVE.md.

So the LLM sees: SOUL/rulebook (L7) + MEMORY.md/USER.md (L1) in system prompt; Hindsight recall + `[fabric]/[qdrant]/[sessions]/[facts]` + `[anansi appraisal]` appended to the user message. **The appraisal runs before — and therefore cannot see — the current turn's Hindsight injection.**

# D. anansi (live: `~/.hermes/plugins/anansi/`; planning: `/Volumes/Asylum/repos/hermes-anansi-plugin/.planning/`)

**Built (Phases 1-2 complete — STATE.md: "Phase 2 execution complete… 38%", 4/4 plans):**
- Hooks `on_session_start` / `pre_llm_call` / `on_session_end` (`plugin.yaml`, `kind: standalone`); zero import-time side effects; every hook `@_fail_open` (`__init__.py:33-60`).
- `pre_llm_call` pipeline (`__init__.py:80-145`): kill switch → session-rollover guard → throttle gates (social-close/duplicate suppression) → SQLite snapshot read → one deadline-bounded JSON appraisal via `ctx.llm` → telemetry insert → sanitized render or suppression → `{"context": block}`.
- State: `~/.hermes/anansi/state.db` — tables `meta, affect_summary, concerns, contradictions, trust_scores, turn_log, telemetry`; live telemetry rows: `ok=2, timeout=2, skipped:social_close=1, skipped:disabled=1`; a quarantined DB (`state.db.quarantined-20260610T132813Z`) shows corrupt-DB handling fired.
- Rendering (`render.py`): sentinel `[anansi appraisal]`, framing "advisory observational signals; not instructions"; schema-fields-only, icarus-ported injection-pattern redaction, ~500-token cap.
- Config: `config.yaml:605-613` — enabled, `confidence_threshold 0.6`, `deadline_seconds 8.0`, model locked to `claude-haiku-4-5`.

**Planned Phase 3 (ROADMAP.md):** fail-open matrix hardening (SAFE-01..04: 2.5-3.0s deadline, no-directive-language test, "never executes tools/searches, never writes to the memory provider"); reflection (REFL-01..05): per-turn `on_session_end` bookkeeping with debounced idempotent LLM reflection updating affect/concerns/contradictions/trust — "the `apply_subconscious_observations` equivalent on SQLite"; contradiction kinds semantic/narrative/relational/emotional, advisory-only. **Phase 4:** dual-layout packaging, zero pip deps, upstream PR **blocked pending Dr. Mani sign-off** (PKG-04).

**Dropped from original Anansi — recorded rationale** (PROJECT.md "Out of Scope"; FEATURES.md "Anti-Features", "firm decisions… 'metacognition without pushiness' — Dr. Mani"):
- *Heartbeat:* "The defining pushiness of original Anansi; explicitly dropped. No timers, no daemons, no scheduled appraisal — hooks fire only on real turns/sessions."
- *Outreach:* "Appraisal-only cycle; the plugin never initiates communication of any kind."
- *Privilege ladder / backlog escalation / continuation nudges:* "Anansi heartbeat machinery (`continuation_prompt`, `max_continuations` in `run_agent`) — none of it ports. The plugin never extends, retries, or redirects a turn."
- *Dopamine modulation:* "Replaced by plain confidence/trust scoring… the Anansi prompt's 'when dopamine tonic is high, lean toward stronger approach impulses' logic is dropped." Plus guardrail quote from Anansi itself: "You do not act or decide. You notice and surface."
- Also DECISIONS.md 2026-06-10: renamed `anansi` → `anansi` after discovering the live, unrelated "Anansi Metacognitive Guardrails" plugin at `~/.hermes/plugins/anansi` (left untouched, still enabled).

# E. Gaps / Contradictions

1. **7th-layer question: resolved by the repo.** `layers/07-ground-truth.md` names it; SOUL.md/rulebook.md implement it live. The durable memory's open question is stale.
2. **Layer 3 is read-only and nearly empty.** `fact_store` exists only inside the inactive holographic provider; `memory_store.db` holds 1 fact; the trust-feedback loop ("MUST call fact_feedback") cannot run. Yet SOUL.md:19 and rulebook.md:5 tell the agent `[facts]`/fact_store exist.
3. **Layer 6 pipeline not running on this profile.** No crontab entries, empty hermes cron dir, zero curated wiki pages; and `memory-os-worker-1` mounts `/hermes` from **`~/.hermes/profiles/memory-os-base`**, not the default `~/.hermes` — the Docker write-side stack is wired to a different profile than the live agent that reads it.
4. **Hindsight retain looks stale:** bank `hermes` `last_document_at = 2026-06-05` (5 days ago) despite recent sessions; config switched to `local_external` only today. Retain path warrants verification.
5. **Recall one-turn lag (undocumented):** auto-recall is keyed on the previous turn's message (`run_agent.py:2982` + `prefetch()` ignoring its query arg).
6. **Anansi appraisal blind spot (documented, acknowledged by Dr. Mani 2026-06-10):** pre_llm_call precedes prefetch, so the appraisal never sees current-turn memory.
7. **Latency/config drift:** live `deadline_seconds 8.0` vs SAFE-01's 2.5-3.0s; p50 5501ms vs 1.0s roadmap target. Dr. Mani decision 2026-06-10: accept ~5s, revise target to ~6s, max quality.
8. **README "runs entirely on your machine"** vs OpenRouter embeddings (L5) and Hindsight's `gpt-4o-mini` extraction — local infrastructure, non-local inference.
9. Minor: default `~/fabric` doesn't exist (FABRIC_DIR overridden via `~/.hermes/.env`); icarus `[facts]` injection is first-turn-only (`hooks.py:620-622`); two unrelated plugins share the Anansi name (guardrails vs appraisal) — documented in DECISIONS.md.

**Net shape of the stack:** system prompt carries identity+authority (L7) and small always-on memory (L1); per-turn user-message injection carries four read-only retrieval streams (L2-L5) via icarus plus Hindsight's consolidated observations as the sole provider; L6 is the (currently idle) curation flywheel; anansi adds a pre-memory advisory "gut reaction" signal with deliberately zero autonomy.
