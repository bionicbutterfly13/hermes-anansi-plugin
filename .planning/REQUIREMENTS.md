# Requirements — Hermes Anansi Metacognition Plugin

v1 selection made 2026-06-10 during the autonomous ceremony (self-answered under Dr. Mani's
mandate, following SUMMARY.md's recommended posture: table-stakes spine T1–T10 + near-free
differentiators D4/D7 + shallow D1/D2; defer D3/D5/D6 depth until telemetry validates signal
quality). Feature IDs (T*/D*) reference `.planning/research/FEATURES.md`.

## v1 Requirements

### PLUG — Plugin integration

- [x] **PLUG-01** Plugin loads via hermes-agent's standard mechanism: `plugin.yaml` with explicit `kind: standalone` and `provides_hooks`, `register(ctx)` with zero import-time side effects, installable at `$HERMES_HOME/plugins/anansi` (maps: skeleton; SUMMARY Key Decision 6a)
- [x] **PLUG-02** Every hook accepts `**kwargs` and tolerates unknown/missing kwargs (dispatcher injects extras; strict signatures TypeError every call)
- [x] **PLUG-03** The strings `MemoryProvider`/`register_memory_provider` never appear in `__init__.py` (manifest string-scan silently coerces plugin kind)
- [x] **PLUG-04** `pre_llm_call` returns `{"context": block}` or `None` — injection into user message only; system prompt never touched (host invariant)

### STATE — Local appraisal state (T8)

- [x] **STATE-01** SQLite store under `$HERMES_HOME` (path from config/env, never literal) with schema: affect_summary, concerns, contradictions, trust_scores, turn_log, schema_version
- [x] **STATE-02** WAL mode, synchronous=NORMAL, busy_timeout=5000; hot-path reads via read-only URI snapshot; writes confined to reflection pass
- [x] **STATE-03** Corrupt/locked/absent DB → quarantine-and-recreate (or skip), never a raised exception into the turn
- [x] **STATE-04** All state tables have caps + decay/pruning (anti: unbounded growth/hidden profiling); state stays local (privacy constraint)
- [x] **STATE-05** State round-trip covered by tests (write → reload → identical signals)

### APPR — Appraisal pre-phase (T1–T7, D4, D7)

- [ ] **APPR-01** `pre_llm_call` runs ONE JSON-mode appraisal call via `ctx.llm.complete_structured` over (user_message + raw conversation_history + SQLite state) — NOT current-turn memory injection (amended input contract, one-turn lag) (T1)
- [ ] **APPR-02** Observation-only prompt written fresh (not ported verbatim from Anansi `subconscious.md`); schema has noun fields only — instincts (typed vocabulary approach/avoid/caution/curiosity/protect with 0–1 intensity + reason — D7), salient observations, contradiction flags, confidence per signal, suggested memory searches (advisory text only — D4), gut reaction (≤200 chars)
- [ ] **APPR-03** Per-signal confidence threshold (default 0.6); signals below threshold dropped (T5)
- [ ] **APPR-04** Compact rendered block ≤500 tokens, top-3 per category, sentinel prefix (`[anansi appraisal]`), sanitized through icarus-style `_validate_safe_content` pipeline (T2)
- [ ] **APPR-05** Empty-signal suppression: nothing salient → inject nothing (T4)
- [ ] **APPR-06** Appraisal model separately configurable (cheap tier); on `PluginLlmTrustError` retry once with host's active model, then fail open (T6; SUMMARY Key Decision 3) — *annotation 2026-06-10 (R3): mechanism unit-proven; unproducible live on this install (host fallback ~37s exceeds the deadline clamp, degrades to the designed fail-open timeout); correct for installs with faster host models*
- [ ] **APPR-07** Config kill switch disables the pre-phase entirely (T7)
- [ ] **APPR-08** Throttle gates: skip appraisal on social closers / near-duplicate turns (icarus precedent)

### SAFE — Fail-open + anti-creep (T3)

- [ ] **SAFE-01** Configurable executor-bounded wall-clock deadline on the appraisal call, default 8.0s (per-call socket timeouts don't bound wall time); p50 target ≤6s; zero retries beyond the trust-gate fallback — *revised 2026-06-10 (R1): Dr. Mani accepted ~5s p50 / max quality; live haiku appraisal is generation-bound at 4.4–7.3s, so the original 2.5–3.0s spec times out 100%*
- [ ] **SAFE-02** Fail-open test matrix: LLM timeout, trust rejection, malformed JSON, truncation, `content: null`, locked/corrupt/absent DB, missing config — every case asserts no-raise + empty injection + normal turn
- [ ] **SAFE-03** Unit test asserts no imperative/directive language patterns in any rendered block (anti: hidden second policy layer)
- [ ] **SAFE-04** Plugin never executes tools/searches, never writes to the memory provider, never gates/delays a turn, never modifies its own prompt/config from reflection (locked anti-features)

### REFL — Session-end reflection (T9, shallow D1/D2)

- [ ] **REFL-01** `on_session_end`: cheap bookkeeping (turn_log append) every firing; LLM reflection pass only on session-id change or N-turn debounce, applied in one idempotent WAL transaction (amended: hook fires per turn)
- [ ] **REFL-02** Reflection extracts observations → bounded conservative deltas to affect summary, concerns, contradiction log, trust scores (the `apply_subconscious_observations` equivalent on SQLite) — *sharpened 2026-06-10 (R2): reflection is the carrier of appraisal context across the one-turn lag — the second half of the appraisal input contract. Inputs are user messages + assistant response text + state; NOT the injected memory block (ephemeral, never persisted to the transcript — verified conversation_loop.py:610-627)*
- [ ] **REFL-03** Reflection inputs exclude sentinel-prefixed appraisal blocks (anti echo-chamber)
- [ ] **REFL-04** Contradiction signals (semantic/narrative/relational/emotional) persisted and re-surfaced when relevant — shallow v1, validated against a fixture set before deepening (D1)
- [ ] **REFL-05** Confidence/trust scores surfaced as advisory hints ("low confidence on X") — never a gate (D2)

### OBS — Observability (T10)

- [ ] **OBS-01** Per-call telemetry to plugin's own SQLite: wall_ms, tokens, model, outcome (`ok|timeout|parse_fail|llm_error|skipped:<reason>`); failure counter + last-error surfaced (cf. silent-outage lesson, PR #43313)

### PKG — Packaging + PR prep

- [ ] **PKG-01** Zero new pip dependencies (`pip_dependencies: []`); stdlib + host surfaces only
- [ ] **PKG-02** Dual layout: standalone `$HERMES_HOME/plugins/anansi` + in-tree `plugins/` arrangement for the upstream PR; docs include the `plugins.entries.anansi.llm` config block
- [ ] **PKG-03** Re-verify `ctx.llm` facade + manifest key (`provides_hooks` vs `hooks`) against upstream main before PR (local 0.16.0 fork carries 7 PRs of divergence)
- [ ] **PKG-04** Upstream PR prepared but submitted ONLY after Dr. Mani sign-off (standing directive)

## v2 Requirements

- **D3** Dimensional affect summary depth (valence/arousal/intensity with decay-to-baseline) — ship minimal in v1 state schema, deepen after telemetry
- **D5** Salience filtering over Hindsight-injected context — requires solving current-turn memory visibility (config-gated direct-Hindsight-recall option, parked)
- **D6** Active-concern continuity depth (decay/expiry policy tuning) — start aggressive caps, loosen with evidence
- Unselected table stakes: none (all 10 in v1)

## Out of Scope

| Item | Reason |
|------|--------|
| Heartbeat / background cycles, outreach, privilege ladder, continuation nudges, dopamine modulation | Locked exclusions — "metacognition without pushiness" |
| Plugin-executed tool calls/searches, directive injection language, turn gating, memory-provider writes, goal generation, self-modifying prompts, mood-driven output modulation, multi-call appraisal chains | Autonomy-creep refusals (FEATURES.md anti-feature table) |
| Import-time `sys.path` mutation | mnemosyne-incident standing "never" |
| Postgres/AGE/RabbitMQ/Ollama/UI | Original Anansi infra; this plugin is SQLite-only, Docker-free |

---
*Last updated: 2026-06-10 — PLUG-01..04 + STATE-01..05 delivered by Phase 1 (see 01-VERIFICATION.md); R1/R2/R3 revisions applied from MEMORY-STACK-ANALYSIS-2026-06-10.md §6 (Dr. Mani-accepted decisions)*
