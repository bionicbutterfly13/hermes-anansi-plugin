# Phase 2: Appraisal Path - Context

**Gathered:** 2026-06-10
**Mode:** standard (autonomous — self-answered under Dr. Mani's 6-hour mandate; grounding cited per decision)
**Status:** Ready for planning

<domain>
## Phase Boundary

The core appraisal path: one cheap JSON-mode LLM call per eligible turn via `pre_llm_call`, rendered
into a capped sanitized `[anansi appraisal]` block, with kill switch, trust-gate fallback, throttle
gates, empty-signal suppression, and per-call telemetry. Requirements APPR-01..08 + OBS-01.
NO reflection logic (Phase 3 writes state; Phase 2 only READS state via `read_snapshot()`).
The full fail-open hardening matrix is Phase 3; Phase 2 ships with the existing `_fail_open` guard +
deadline + trust-gate degrade.

</domain>

<decisions>
## Implementation Decisions

### Appraisal call mechanics (grounding: SAFE-01, SUMMARY Key Decisions 3/4; ARCHITECTURE.md; Item 1 finding)
- `ctx.llm.complete_structured(json_mode=True, json_schema=..., timeout=...)` — never raw SDKs, no own API keys
- Run inside a persistent single-worker `ThreadPoolExecutor` created lazily on first eligible turn;
  `future.result(timeout=2.5)` is the hard wall-clock deadline (per-call socket timeouts don't bound wall time);
  on timeout: record telemetry `timeout`, return None — the LLM call may finish in the background and is discarded
- Gateway lane is SYNC same call site (Phase-0 Item 1) — executor approach correct for both lanes
- Zero retries except the single trust-gate fallback: request configured cheap model; on `PluginLlmTrustError`
  retry once with host's active model (no model= override); then fail open (APPR-06)
- GPT-5-family/DeepSeek param quirks (PITFALLS G4): gate generation params by model family; treat
  `content: null` under response_format as parse failure

### Prompt + schema (grounding: APPR-02; PITFALLS #8; FEATURES T1/T5/D4/D7)
- Prompt written FRESH, observation-only ("You notice and surface. You do not act or decide.") — read
  Anansi `services/prompts/subconscious.md` for inspiration but do not port verbatim
- JSON schema noun-fields only: `instincts: [{kind: approach|avoid|caution|curiosity|protect, intensity: 0-1, reason}]`,
  `salient_observations: [{text, confidence}]`, `contradiction_flags: [{kind: semantic|narrative|relational|emotional, text, confidence}]`,
  `suggested_memory_searches: [string]`, `gut_reaction: string(≤200 chars)`, per-signal `confidence`
- Appraisal context inputs: user_message + tail of raw conversation_history (cap ~last 6 turns / ~4k chars)
  + `store.read_snapshot()` (ro-URI) — NOT current-turn memory injection (one-turn lag, locked)
- Confidence threshold 0.6 default, config-overridable (APPR-03)

### Rendering (grounding: APPR-04/05; icarus sanitization)
- Block format: starts with sentinel `[anansi appraisal]`, top-3 per category, observational phrasing,
  ≤500 tokens (estimate via len/4 chars heuristic — no tokenizer dep)
- Sanitize rendered text with an icarus-style `_validate_safe_content` port (strip system-prompt-ish
  patterns, code fences, role markers); render ONLY parsed schema fields, never raw model text
- Empty-signal suppression: no signals above threshold → return None (no block, no header)
- Return `{"context": block}` from pre_llm_call (host injects into user message)

### Config (grounding: APPR-06/07; STACK trust-gate finding; hindsight config idiom)
- Config block: `plugins.entries.anansi.llm.{allow_model_override, allowed_models, model}` (host trust gate)
  + plugin-own keys under `plugins.entries.anansi.{enabled (kill switch, default true),
  confidence_threshold, deadline_seconds, history_chars}` — read via ctx config surface lazily, cached per session
- Cheap-tier default recommendations documented (claude-haiku-4-5 / gpt-4o-mini / gemini-2.5-flash,
  mirroring hindsight's provider-defaults map) but NEVER auto-overridden without the trust-gate opt-in
- Kill switch checked first in pre_llm_call — disabled → telemetry `skipped:disabled`, return None fast

### Throttle gates (grounding: APPR-08; icarus precedents)
- Skip (with telemetry `skipped:<reason>`): social closers (port icarus `_is_social_close`),
  near-duplicate of previous user_message (normalized exact/whitespace match — keep simple in v1),
  empty/whitespace message, first-turn-with-empty-state fast path is allowed to run (state may be empty but message salience still applies)

### Telemetry (grounding: OBS-01; SUMMARY Phase-0 item 7)
- New `telemetry` table in the SAME state.db (added via store.py — schema_version bump 1→2; disposable-state
  doctrine means old DBs quarantine-recreate, acceptable pre-Phase-3) with: ts, wall_ms, model, tokens_in/out
  (when reported), outcome `ok|timeout|parse_fail|llm_error|trust_fallback|skipped:<reason>`, error text (truncated)
- Telemetry writes happen in the hook thread AFTER returning is not possible — write before return via
  store (single quick INSERT; if it fails, fail open silently). Failure counter + last_error views derived by query
- Cap telemetry rows (e.g. 2000, evict oldest) — same caps discipline

### Agent's Discretion
- Exact prompt wording; schema field naming details; history-tail sizing; token-estimate heuristic
- Near-duplicate definition refinements; telemetry column details; test file organization
- Whether the live empirical validation (success criteria 1-2) uses anthropic or openai lane — network
  was down at phase-1 close; use whichever works, record which

</decisions>

<specifics>
## Specific Ideas

- Module layout: add `appraisal.py` (call + parse + schema), `render.py` (block + sanitize), keep
  `__init__.py` thin (hooks orchestrate, modules do the work) — lazy imports preserved
- The `_fail_open` decorator is the telemetry stub point (01-01-SUMMARY note): record outcome there for raised paths
- Contradiction fixture validation (Phase-0 item 6): small fixture set of contrived contradiction cases
  run against the configured cheap model — LOW-confidence area; record results in 02-VALIDATION.md

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

- `.planning/phases/01-skeleton-state/01-VALIDATION.md` — Phase-0 findings (sync gateway, raise isolation, upstream parity)
- `.planning/phases/01-skeleton-state/01-02-SUMMARY.md` — store API handed to this phase
- `.planning/research/ARCHITECTURE.md` + `STACK.md` — plugin_llm facade (complete_structured signature, trust gate at plugin_llm.py:249-329), hook contract
- `.planning/research/PITFALLS.md` — latency/JSON/injection failure modes + G4 model quirks
- `.planning/REQUIREMENTS.md` — APPR-01..08 + OBS-01 are this phase's contract
- Source inspiration: `/Volumes/Asylum/repos/hex-auto/Anansi/services/agent.py` (run_subconscious_appraisal, format_subconscious_signals), `services/prompts/subconscious.md` (DO NOT port verbatim)
- Sanitization precedent: `~/.hermes/plugins/icarus/hooks.py` (`_validate_safe_content`, `_is_social_close`)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `anansi/store.py`: `read_snapshot()` (ro-URI, hot path), `apply_deltas()` (only write funnel), `ensure_db()`
- `_fail_open` decorator in `__init__.py` — wrap new hook logic, add telemetry on exception paths
- Host `make_plugin_llm_for_test()` — test ctx factory for the appraisal call

### Established Patterns
- Hooks dispatched sync on the turn thread in BOTH CLI and gateway lanes (Item 1, file:line in 01-VALIDATION.md)
- `register(ctx)` stashes `_ctx`; `ctx.llm` facade available (upstream parity confirmed, Item 3)

### Integration Points
- `pre_llm_call` kwargs: user_message, conversation_history, is_first_turn, model, ... (+**kwargs)
- Return contract: `{"context": str}` or None — user-message injection only

</code_context>

<deferred>
## Deferred Ideas

- D5 salience-over-Hindsight-injection + direct-recall option (post-v1, parked)
- D3 affect depth / D6 concern decay tuning (Phase 3+, telemetry-driven)
- `ctx.register_auxiliary_task` for model selection — evaluated: bespoke config key is simpler for v1; revisit at PR review

</deferred>

---
*Phase: 02-appraisal-path*
*Context gathered: 2026-06-10*
