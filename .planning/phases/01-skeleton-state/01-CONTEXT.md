# Phase 1: Skeleton + State - Context

**Gathered:** 2026-06-10
**Mode:** standard (autonomous — self-answered under Dr. Mani's 6-hour mandate; every decision below cites its grounding)
**Status:** Ready for planning

<domain>
## Phase Boundary

A loadable, inert, state-capable plugin proven against the live install: plugin.yaml + register(ctx)
+ no-op hooks that survive real turns, plus the SQLite state store with full round-trip tests and
silent degradation. NO LLM calls, NO injection, NO reflection logic — those are Phases 2–3.
Requirements: PLUG-01..04, STATE-01..05. Phase-0 validation items 1–4 from research SUMMARY.md fold in.

</domain>

<decisions>
## Implementation Decisions

### Package layout (grounding: ARCHITECTURE.md build order; icarus/hindsight precedents)
- Plugin source lives in this repo at `anansi/`: `__init__.py` (register + hook functions only),
  `store.py` (all SQLite), `plugin.yaml`, `tests/`
- Deployed by symlink `$HERMES_HOME/plugins/anansi` → repo `anansi/` during development (icarus-style
  external plugin; in-tree arrangement is Phase 4 work)
- `plugin.yaml`: `name: anansi`, explicit `kind: standalone`, `provides_hooks: [on_session_start,
  pre_llm_call, on_session_end]`, `pip_dependencies: []` (PKG-01 enforced from day one)
- `__init__.py` has zero import-time side effects: no DB open, no path mutation, no config reads at
  module top level; everything initializes lazily inside `register(ctx)`/first hook call (PLUG-01/03)

### Hook skeleton (grounding: ARCHITECTURE.md hook contract; PLUG-02/04)
- All three hooks registered as no-ops in Phase 1: signatures accept the documented kwargs PLUS
  `**kwargs`; always return `None` (pre_llm_call returning None = no injection — proves the
  no-injection path through the dispatcher)
- `on_session_start` will eventually warm the state snapshot; in Phase 1 it only verifies store
  availability (silent on failure)
- Every hook body wrapped in the fail-open guard from the start (try/except → log to plugin
  logger + telemetry stub, return None) — the guard is Phase-1 scaffolding, not Phase-3 retrofit

### SQLite store (grounding: STATE-01..05; STACK.md §SQLite; SUMMARY Key Decision 4)
- Location: `$HERMES_HOME/anansi/state.db` — mirrors hindsight's `$HERMES_HOME/hindsight/` profile-scoped
  pattern; per-profile state for free; resolved via the host's `get_hermes_home()`/config, never literal
- Explicit tables (not a generic observations table): `affect_summary`, `concerns`, `contradictions`,
  `trust_scores`, `turn_log`, `meta` (holds schema_version) — REQUIREMENTS names these; explicit
  schemas keep caps/decay enforceable per-table
- PRAGMAs: WAL, synchronous=NORMAL, busy_timeout=5000; hot-path reads open `file:...?mode=ro` URI;
  writes only through a single `apply_deltas()` entry point (transaction-wrapped) so Phase 3
  reflection inherits a safe write funnel
- Disposable-state doctrine: ANY structural problem (corruption, schema_version mismatch, failed
  migration) → quarantine (rename to `state.db.quarantined-<ts>`) + recreate fresh. Appraisal state
  is advisory; losing it costs nothing but warm-up. No migration framework in v1 (STATE-03)
- Caps + decay columns built into the schema now (`expires_at`/`decayed_weight`, per-table row caps)
  even though only Phase 3 writes them — schema churn is the expensive part (STATE-04)

### Verification against the live install (grounding: SUMMARY Phase-0 items 1–4)
- Load proof: `hermes plugins enable anansi` (or `plugins.enabled` config) + `HERMES_PLUGINS_DEBUG=1`
  shows kind=standalone and three hooks registered
- Dispatch proof: one real `hermes -z` turn with debug logging — hooks fire, output unchanged
- Hook-raise experiment: deliberately raise in a scratch branch once, observe caught-and-logged
  behavior, record in phase notes, then never raise again
- Gateway-lane dispatch check (sync vs awaited): read the gateway code path; only run a live gateway
  test if reading is inconclusive

### Agent's Discretion
- Exact cap numbers (start aggressive per research: concerns ≤20, contradictions ≤50,
  turn_log ≤500 rows — tune later with telemetry)
- Column-level schema details within the named tables
- Logger naming, debug-log formats, test file organization
- Whether `meta` holds JSON or key-value rows

</decisions>

<specifics>
## Specific Ideas

- Follow hindsight's config-resolution idiom (`$HERMES_HOME`-scoped dir + env-var overrides) and
  icarus's fail-open hook style — these two plugins are the house style for this codebase
- Test with the host-shipped `make_plugin_llm_for_test()` helper where ctx is needed (STACK.md find)

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

- `.planning/research/ARCHITECTURE.md` — exact hook signatures (file:line cites), dispatch order, anti-patterns
- `.planning/research/STACK.md` — host surfaces (plugin_llm facade, manifest keys), SQLite guidance
- `.planning/research/SUMMARY.md` — Key Decisions 4/6 and Phase-0 validation items 1–4
- `.planning/REQUIREMENTS.md` — PLUG-01..04, STATE-01..05 are this phase's contract
- Live precedents: `~/.hermes/plugins/icarus/{plugin.yaml,hooks.py}`, `~/.hermes/hermes-agent/plugins/memory/hindsight/__init__.py`, `~/.hermes/hermes-agent/hermes_cli/plugins.py` (loader)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- icarus `hooks.py`: fail-open guard shape, throttle-gate helpers (`_is_social_close`), `_validate_safe_content` (Phase 2 reuse)
- hindsight `__init__.py`: `$HERMES_HOME` config resolution, lazy initialization, availability checks
- host `make_plugin_llm_for_test()`: purpose-built test ctx factory

### Established Patterns
- External plugins live at `$HERMES_HOME/plugins/<name>/` with plugin.yaml; loader string-scans `__init__.py` for kind coercion (the landmine)
- Hooks dispatched synchronously on the turn thread (plugins.py:1574-1609); dispatcher injects extra kwargs (e.g. telemetry_schema_version)

### Integration Points
- Loader: `~/.hermes/hermes-agent/hermes_cli/plugins.py` (provides_hooks manifest key at :1386)
- Hook call sites: turn_context.py:316 (pre_llm_call, BEFORE memory prefetch at :359-374), turn_finalizer.py:410-411 (on_session_end, per turn)

</code_context>

<deferred>
## Deferred Ideas

- Config-gated direct-Hindsight-recall for current-turn memory visibility (post-v1; parked in SUMMARY Open Questions)
- `ctx.register_auxiliary_task` for appraisal model selection — evaluate in Phase 2 design

</deferred>

---
*Phase: 01-skeleton-state*
*Context gathered: 2026-06-10*
