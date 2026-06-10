# Phase 3: Fail-Open Hardening + Reflection - Context

**Gathered:** 2026-06-10
**Mode:** standard (autonomous — gate answers pre-staged in MEMORY-STACK-ANALYSIS-2026-06-10.md §6 under Dr. Mani's 4-hour mandate; latency/lag decisions accepted by Dr. Mani in-session 2026-06-10)
**Status:** Ready for planning

<domain>
## Phase Boundary

Two halves: (a) the full SAFE fail-open matrix + anti-creep proofs (SAFE-01..04), and (b) the
reflection pass (REFL-01..05) — **the carrier of appraisal context across the one-turn lag**, the
second half of the appraisal input contract (R2, accepted). Reflection is the ONLY writer to state
tables (Phase 2 reads via `read_snapshot()`; `apply_deltas()` is the sole write funnel).
NO packaging/PR work (Phase 4). NO new pip dependencies. NO memory-provider writes ever (SAFE-04,
locked). Plugin install stays live at `$HERMES_HOME/plugins/anansi` throughout.

</domain>

<decisions>
## Implementation Decisions

### SAFE-01 latency (R1 — Dr. Mani decision 2026-06-10, locked)
- Spec: configurable executor-bounded wall-clock deadline, **default 8.0s**; p50 target ≤6s; zero
  retries beyond trust-gate fallback
- Code change: align in-code default `deadline_seconds` 2.5 → **8.0** (02-VERIFICATION observation 2;
  live config already sets 8.0 explicitly — behavior unchanged, default honesty fixed)
- Accepted trade-off (recorded in DECISIONS.md): ~5s serial pre-phase tax per eligible turn

### SAFE-02 fail-open matrix (inventory split — analysis §6)
- ALREADY tested in phases 1–2 (do not duplicate; reference in the matrix doc/test names): deadline
  timeout, llm raise, unwritable telemetry, corrupt-DB quarantine, kill switch, empty/duplicate/social
  gates, injection sanitization
- NEW work this phase: parse_fail path (malformed JSON, truncation, `content: null`),
  missing-config path, gateway session-rollover state reuse, reflection idempotency + debounce
  double-fire, reflection echo-exclusion, locked-DB during reflection write
- Every case asserts: no-raise + empty injection (or no state mutation for reflection cases) + normal turn

### SAFE-03 no-directive-language (new this phase)
- Unit test asserting no imperative/directive patterns in any rendered block across a corpus of
  rendered outputs (fixtures + property-style pattern list: "you should/must/do not/always/never do X",
  imperative-verb sentence starts in advisory lines, etc.)
- Audit BOTH the appraisal block renderer and any reflection-surfaced hints (REFL-05 advisory lines)

### SAFE-04 anti-creep static checks (new this phase)
- Static test: source scan asserts no memory-provider API usage (`retain`, `register_memory_provider`,
  `MemoryProvider`), no tool execution surfaces, no config self-writes from reflection code paths
- Keep PLUG-03 string-scan constraint intact (`__init__.py` clean)

### REFL-01 debounce + idempotency (analysis §6 pre-answer)
- `on_session_end` fires per turn (verified): cheap bookkeeping (turn_log append) EVERY firing;
  LLM reflection pass only on (a) session-id change, AND (b) at most once per 5 appraised turns
  mid-session
- Idempotency: `last_reflected_turn_id` in a meta table; reflecting twice over the same span is a
  no-op (idempotence test = ROADMAP criterion 2); reflection applied in ONE WAL transaction

### Reflection model/cost (analysis §6 pre-answer)
- Same `ctx.llm` facade, same configured cheap lane (haiku live), SINGLE call, max_tokens ≈700 —
  same ceiling as appraisal; worst case doubles per-turn LLM cost only on reflection turns
- Same executor-deadline discipline as appraisal (reuse the executor; fail open identically)

### REFL-02 deltas (R2-sharpened + §6 pre-answer)
- Inputs: user messages + assistant response text + SQLite state — **NEVER** the injected memory
  block (ephemeral, unpersisted — conversation_loop.py:610-627) and NEVER sentinel-prefixed
  `[anansi appraisal]` blocks (REFL-03 anti-echo)
- Bounds: ±0.15 max delta per scalar per reflection pass; concerns/contradictions stay under existing
  caps (20/50); no row deletion by reflection except cap-eviction
- All writes through `apply_deltas()` (or an extension of it) — single write funnel preserved

### Concern decay (analysis §6 pre-answer — heartbeat semantics without a scheduler)
- **Lazy elapsed-time decay at snapshot read**: effective_weight = weight × 0.5^(days_idle/7);
  rows dropping below 0.1 effective weight are pruned (at read or at next reflection write — agent's
  discretion which side prunes, but reads must never write on the hot path... prune in reflection pass)

### REFL-04 contradictions / REFL-05 trust hints
- Contradiction kind labels remain ADVISORY-only (Phase-2 finding: kinds over/mis-applied; never
  branch on exact kind); persisted + re-surfaced when relevant; shallow v1 against the existing
  9-case fixture set
- Confidence/trust surfaced as advisory hints ("low confidence on X") in the appraisal block —
  never a gate

### Test tooling constraint (02-VERIFICATION observation 1)
- pytest is NOT importable from the hermes-agent venv (uv-sync wipe risk makes installing there
  fragile). Use a repo-local dev approach: either stage pytest on PYTHONPATH (verifier's working
  idiom) or a repo-local `.venv` for dev tooling only. NEVER add runtime pip deps; NEVER rely on
  the hermes-agent venv carrying dev tools. Document the chosen test command in the plan.

### Agent's Discretion
- Reflection prompt wording; meta-table schema details; exact debounce counter implementation;
  test file organization; whether decay-prune lives in reflection write or a maintenance sweep
  inside the same transaction

</decisions>

<specifics>
## Specific Ideas

- Module layout: add `reflection.py` (transcript digest + delta extraction + apply), keep hooks thin
- Reuse the Phase-2 executor/deadline/telemetry plumbing for the reflection call (new outcome rows:
  `reflect_ok|reflect_timeout|reflect_parse_fail|reflect_skipped:<reason>`)
- ROADMAP criterion 3 (end-to-end demo): session discussing topic X with a contradiction → next
  session's appraisal surfaces it — this is the live proof that reflection actually carries context
  across the lag; record in 03-VALIDATION.md
- schema_version bump if new tables (meta/turn_log changes); disposable-state doctrine still applies

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

- `.planning/research/MEMORY-STACK-ANALYSIS-2026-06-10.md` §6 — gate pre-answers (this context's source)
- `.planning/phases/02-appraisal-path/02-VERIFICATION.md` — current verified state + 3 observations
- `.planning/phases/02-appraisal-path/02-VALIDATION.md` — live evidence + fixture set
- `.planning/phases/02-appraisal-path/02-01-SUMMARY.md` + `02-02-SUMMARY.md` — appraisal/telemetry API surface
- `.planning/REQUIREMENTS.md` — SAFE-01..04 + REFL-01..05 are this phase's contract (R1/R2/R3 annotations)
- `.planning/DECISIONS.md` — R1–R3 entries 2026-06-10
- Source inspiration: `/Volumes/Asylum/repos/hex-auto/Anansi` `apply_subconscious_observations` semantics (reimplement on SQLite, do not port)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `anansi/store.py`: `read_snapshot()`, `apply_deltas()` (THE write funnel), `ensure_db()`, telemetry table (schema v2)
- `anansi/appraisal.py` executor + deadline + parse pipeline; `render.py` sanitizer
- `_fail_open` decorator; 49-test suite green as of c038e93

### Established Patterns
- Hooks sync on turn thread both lanes; one LLM call per turn budget; telemetry row per outcome
- Live config: `plugins.entries.anansi` (config.yaml:605-613), deadline_seconds 8.0, haiku lane

### Integration Points
- `on_session_end` kwargs include session metadata (verify exact kwargs against host source before relying)
- State DB: `$HERMES_HOME/anansi/state.db` (path from config/env, never literal)

</code_context>

<deferred>
## Deferred Ideas

- D3 affect-depth deepening, D6 decay tuning — post-telemetry
- D5 salience-over-injection — v2-pending-upstream-hook (`post_memory_prefetch` hermes-agent PR candidate)
- Launchd/cron anything — no schedulers, lazy decay only (locked)

</deferred>

---
*Phase: 03-failopen-reflection*
*Context gathered: 2026-06-10*
