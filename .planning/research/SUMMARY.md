# Research Summary — Hermes Anansi Metacognition Plugin

Synthesized 2026-06-10 from `.planning/research/{STACK,FEATURES,ARCHITECTURE,PITFALLS}.md`.
All four researchers worked from the same local ground truth (hermes-agent 0.16.0 fork at
`~/.hermes/hermes-agent`, icarus plugin, Anansi source at `/Volumes/Asylum/repos/hex-auto/Anansi`),
so confidence on the integration surface is unusually high — most findings are read-from-source,
not inferred.

## Executive Summary

This is a **hooks-only context-injection plugin** for hermes-agent: a per-turn "subconscious
appraisal" (instincts, salience, contradictions, confidence) produced by one cheap JSON-mode LLM
call in `pre_llm_call`, plus a debounced reflection pass in `on_session_end` that maintains local
SQLite state. The research converges on a single strong conclusion: **almost nothing needs to be
invented — the host already provides every surface this plugin needs** (`ctx.llm.complete_structured`
for the sub-call, the `{"context": str}` hook return contract for injection, stdlib `sqlite3` for
state), and icarus/Hindsight provide working precedents for every hard part (fail-open guards,
JSON-repair parsing, output sanitization, config resolution, throttle gates). STACK.md's headline —
**zero new pip dependencies** — holds across all four files.

The risk profile is equally clear. The two failure classes that can actually hurt are (1) **turn
reliability/latency** — hooks run synchronously on the turn thread with no host-side timeout
(ARCHITECTURE.md), so the plugin must enforce its own wall-clock deadline and be fail-open at every
layer; and (2) **behavioral contamination** — the appraisal is simultaneously a consumer of
potentially poisoned memory context and a brand-new injection channel into the main model
(PITFALLS.md #3, #8), so its output must be structurally constrained (fixed schema, noun fields,
no imperatives, sanitized rendering). One requirement in PROJECT.md is **not satisfiable as
written**: the appraisal cannot read the current turn's Hindsight-injected memory context, because
memory prefetch runs *after* `pre_llm_call` (ARCHITECTURE.md, verified at call sites). That forces
a requirement amendment, detailed below.

Recommended posture for v1: build the table-stakes spine (T1–T10 from FEATURES.md) plus the
near-free differentiators (instinct vocabulary D7, memory-expansion cues D4), ship the identity
features (contradiction surfacing D1, confidence/trust D2) behind the same fail-open and
empty-suppression discipline, and defer affect/salience/concern-decay depth (D3, D5, D6) until
real telemetry validates signal quality.

## Key Decisions Forced by Research

These are not preferences — each is forced by verified host behavior or a binding constraint.
The roadmapper should treat them as fixed.

1. **`pre_llm_call` fires BEFORE memory prefetch → appraisal inputs are reduced, with a one-turn
   lag on memory visibility.** ARCHITECTURE.md verified (turn_context.py:316 vs :359-374) that
   Hindsight's `prefetch_all` runs after the hooks, and prior-turn injections are ephemeral —
   never written back to `messages`. The hook therefore sees: `user_message` + raw
   `conversation_history` + local SQLite state, **not** the current turn's injected memory.
   PROJECT.md's "reads whatever memory context is already injected" must be amended. Decision:
   accept the reduced input for v1 (zero coupling, zero added latency — ARCHITECTURE.md's
   recommendation). Practical consequence: any memory-derived signal the appraisal surfaces is
   based on state accumulated through the *previous* session-end reflection — a deliberate
   one-turn(-plus) lag, not a bug. The config-gated direct-Hindsight-recall option stays parked
   as a possible post-v1 enhancement.

2. **`on_session_end` fires per turn, not per session → reflection must be debounced and
   idempotent.** ARCHITECTURE.md verified (turn_finalizer.py:410-411) that the hook fires at the
   end of every `run_conversation` — once per user message — plus safety-net firings on
   interrupted exits. An un-debounced LLM reflection there doubles per-turn LLM calls and busts
   the one-extra-call budget (PITFALLS.md anti-pattern #3). Decision: cheap bookkeeping (turn_log
   append) on every firing; the LLM reflection pass runs only on session-id change or after N
   accumulated turns, applied in one idempotent WAL transaction.

3. **Model-override trust gate is fail-closed → the plugin must fail OPEN around it.** STACK.md
   and ARCHITECTURE.md both verified (plugin_llm.py:249-329) that `model=`/`provider=` overrides
   raise `PluginLlmTrustError` unless the user configures
   `plugins.entries.anansi.llm.allow_model_override: true` (+ `allowed_models`). On a default
   install, an unhandled override exception silently eats the appraisal every turn. Decision:
   request the cheap-tier model only when configured; catch `PluginLlmTrustError`, retry once with
   no override (host's active model), then fail open. Document the config block in install docs;
   default cheap-tier recommendations mirror Hindsight's `_PROVIDER_DEFAULT_MODELS` map
   (claude-haiku-4-5 / gpt-4o-mini / gemini-2.5-flash — STACK.md, MEDIUM, re-check at build).

4. **Zero new dependencies — stdlib + host surfaces only.** STACK.md: `pip_dependencies: []` is
   the strongest posture for the upstream PR given the host's supply-chain-motivated exact-pin
   policy. Concretely: `ctx.llm.complete_structured` (never raw provider SDKs or own API keys —
   the icarus urllib pattern is explicitly the thing plugin_llm replaced), stdlib `sqlite3`
   (WAL, synchronous=NORMAL, busy_timeout=5000; reads via `mode=ro` URIs on the hot path,
   writes confined to reflection), dataclasses + defensive coercion instead of pydantic
   (pin-coupling risk) or jsonschema (already soft-imported by the facade).

5. **Appraisal confidence is advisory-only — never a gate.** FEATURES.md (D2 caveat + anti-feature
   "turn gating on appraisal results") and PITFALLS.md #8 agree: 2026 calibration literature shows
   verbalized self-confidence is too noisy to use as a control signal, and any gating violates
   fail-open. Decision: confidence/trust scores render as observational hints ("low confidence on
   X") in the injected block; the schema contains only noun fields (no `suggested_action`,
   `should_*`), rendered text is sanitized through the icarus `_validate_safe_content` /
   `_sanitize_context_text` pipeline, and a unit test asserts no imperative/directive patterns in
   any rendered block.

6. **Two structural landmines with one-line fixes (do them in phase 1).** (a) Declare
   `kind: standalone` explicitly in plugin.yaml and never let the strings `MemoryProvider` /
   `register_memory_provider` appear in `__init__.py` — the manifest parser string-scans the file
   and silently coerces the plugin to a memory provider, blocking load (ARCHITECTURE.md
   anti-pattern #2; same failure class as the mnemosyne incident). (b) Every hook accepts
   `**kwargs` — the dispatcher injects extra kwargs and a strict signature raises `TypeError` on
   every call (ARCHITECTURE.md hook contract).

7. **Injection goes into the user message, never the system prompt — host invariant.** The Anansi
   `build_system_prompt` injection point cannot be ported; the port is
   `format_subconscious_signals`-style block returned as `{"context": block}` (ARCHITECTURE.md
   decision 6, STACK.md "What NOT to Use").

## Phase-0 Validation Items

Empirically verify before/while building — each is cheap and de-risks a later phase.

1. **Sync vs awaited hook dispatch in gateway sessions** (STACK.md open item 1). Decides
   `complete_structured` inside an executor (recommended) vs `acomplete_structured`. Local read
   says sync sequential dispatch (plugins.py:1574-1609); confirm gateway lane behaves the same.
2. **What actually happens when a hook raises** (PITFALLS.md #5). Docs and source say
   caught-and-logged; verify experimentally once, then make it moot by never raising.
3. **`ctx.llm` availability and manifest key (`provides_hooks` vs `hooks`) on upstream main**
   (STACK.md open items 2 and 4). The facade is verified only on the local 0.16.0 fork, which
   carries 7 PRs of divergence. Required before the PR phase, not before building.
4. **Skeleton loads via `plugins.enabled`** with explicit `kind: standalone`, confirmed via
   `HERMES_PLUGINS_DEBUG=1` and `hermes plugins enable anansi` (ARCHITECTURE.md build-order step 1).
5. **GPT-5-family / DeepSeek param quirks on the configured appraisal model** (PITFALLS.md G4):
   `max_completion_tokens` + `reasoning_effort: minimal` for GPT-5 family; `content: null` under
   `response_format` treated as parse failure. Gate generation params by model family.
6. **Cheap-model contradiction-detection quality** (FEATURES.md D1, LOW confidence): can a
   flash-tier model actually flag semantic/narrative/relational/emotional contradictions worth
   injecting? Validate with a fixture set during the appraisal phase before deepening D1.
7. **Appraisal latency/cost telemetry from day one** (PITFALLS.md mandatory telemetry): per-call
   wall_ms, token counts, model, outcome (`ok|timeout|parse_fail|llm_error|skipped:<reason>`)
   written to the plugin's own SQLite. This is the validation instrument for every LOW/MEDIUM
   estimate in the budget table (p50 ≤1.0s, hard deadline 2-3s, ~$0.03-0.20/day at 100 turns).

## Open Questions

- **Requirement amendment sign-off:** PROJECT.md's "reads whatever memory context is already
  injected" needs Dr. Mani's acknowledgment of the reduced-input reality (Key Decision 1). The
  roadmapper should surface this in the first phase's context, not bury it.
- **Reflection debounce policy:** session-id-change vs N-turns threshold (and what N is) is
  design work, not research — ARCHITECTURE.md gives the shape, not the numbers.
- **Concern-decay and state-pruning policy** (FEATURES.md D6, LOW): caps, decay rates, and
  pruning cadence for concerns/contradictions are unvalidated design. Start aggressive (small
  caps, fast decay) and loosen with evidence; PITFALLS.md #7 (self-reinforcing feedback) is the
  failure mode if this is wrong.
- **Echo-chamber across plugins** (PITFALLS.md #7b, LOW-MEDIUM): appraisal-flavored text stored
  by icarus/Hindsight and re-retrieved as memory. The sentinel-prefix exclusion (`[anansi appraisal]`)
  is the planned mitigation; whether it suffices needs early-session observation.
- **`ctx.register_auxiliary_task` for model selection** (ARCHITECTURE.md integration points):
  possibly cleaner than a bespoke config key for the appraisal model — evaluate during phase
  design, low stakes either way.
- **No external precedent exists** for a pre-turn appraisal-injection plugin on a third-party
  harness (FEATURES.md known gaps). Anansi is the only direct precedent. Internal confidence is
  high; external validation is zero — expect to learn from telemetry, not literature.

## Roadmap Implications

Suggested 4-phase shape (ARCHITECTURE.md's build order maps onto it cleanly; FEATURES.md's
dependency spine confirms the ordering):

- **Phase 1 — Skeleton + State (no LLM).** plugin.yaml (`kind: standalone` explicit,
  `provides_hooks`), `register(ctx)` with zero import-time side effects, no-op hooks with correct
  `**kwargs` signatures, load/enable verification (Phase-0 items 1-4 fold in here). `store.py`:
  schema (affect_summary, concerns, contradictions, scores, turn_log, schema_version), WAL
  pragmas, ro-URI read snapshot, quarantine-and-recreate on corruption, round-trip tests.
  Delivers: a loadable, inert, state-capable plugin. Covers FEATURES T6/T7/T8 foundations.

- **Phase 2 — Appraisal path (the core).** Rewritten observation-only prompt (NOT ported from
  `load_subconscious_prompt()` — PITFALLS.md #8), `ctx.llm.complete_structured` inside a
  persistent single-worker executor with the 2.5s/3.0s deadline, trust-gate catch-and-degrade,
  icarus-style robust JSON parse, field-by-field defaults, ≤500-token block rendering with
  sanitization and sentinel prefix, empty-signal suppression, throttle gates (social closers,
  near-duplicate turns). Covers T1-T5, D4, D7. Phase-0 items 5-7 validate here.

- **Phase 3 — Fail-open hardening + reflection.** Explicit test matrix per PITFALLS.md #5:
  LLM timeout, trust rejection, malformed JSON, truncation, `content: null`, locked/corrupt/absent
  DB, missing config — every case asserts no-raise + empty injection + normal turn. Then the
  debounced, idempotent `on_session_end` reflection pass writing conservative bounded deltas
  (T9, D1, D2, minimal D3/D6), with sentinel-exclusion from reflection inputs and the
  failure-counter/last-error observability (T10, ARCHITECTURE.md anti-pattern #8 — fail-open
  without observability is silent-outage blindness, cf. PR #43313).

- **Phase 4 — Packaging + upstream PR prep.** Dual layout (standalone `$HERMES_HOME/plugins/anansi`
  + in-tree `plugins/`), docs including the `plugins.entries.anansi.llm` config block, upstream-main
  re-verification (Phase-0 item 3), test suite to host standards, Dr. Mani sign-off gate before
  submission.

**Flag for deeper per-phase research:** none of the phases needs more *integration* research —
the hook contract, facade, and precedents are fully read. Phase 2 needs *empirical* validation
(cheap-model signal quality, latency distribution); Phase 3's decay/debounce numbers are design
judgment to be tuned by the Phase-2 telemetry.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Read directly from host source (plugin_llm.py, plugins.py, pyproject.toml) + two working local plugin precedents; only cheap-model picks and upstream-main parity are MEDIUM |
| Features | HIGH (table stakes) / MEDIUM (differentiators) | T1-T10 verified in Anansi source + Reflexion-pattern literature; D1 quality, D3 value, D6 decay policy are LOW-MEDIUM and flagged for empirical validation |
| Architecture | HIGH | Every hook call site, kwarg payload, and return contract cited file:line from this install; only the exact `on_session_start` core kwargs and PRAGMA fine points are MEDIUM |
| Pitfalls | HIGH (local) / MEDIUM (web) | The big five (latency, fail-open, JSON failures, state corruption, autonomy creep) are grounded in verified local incidents and source; cost numbers and feedback-loop risk are LOW-MEDIUM, covered by mandatory telemetry |

Overall: integration risk is low and well-mapped; the genuine unknowns are signal-quality
questions only answerable by shipping the appraisal and reading its telemetry.
