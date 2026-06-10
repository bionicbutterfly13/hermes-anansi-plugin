# Plan 03-02 Summary

**Completed:** 2026-06-10 (~6:50pm EDT)
**Phase:** 3 — Fail-Open Hardening + Reflection

## What was built

The reflection pass — the cross-lag carrier (R2) — proven end-to-end offline against fake
LLMs, suite 68 → 105 green at every commit. Schema v3 (`701549d`): turn_log gains
`assistant_excerpt`, `apply_deltas` gains `meta_set`/`concerns_update`/`concerns_prune`/
`contradictions_resolve` (still THE single mechanical write funnel), new ro-URI readers
`get_meta()`/`read_turns_since()`, and `read_snapshot()` applies lazy decay
(`weight * 0.5 ** (days_idle/7)`, exclude effective < 0.1, READS NEVER WRITE). The engine
(`7c1c235`): `reflection.py` exports record_turn/build_digest/run_reflection/
parse_reflection/apply_reflection/maybe_reflect with `MAX_DELTA = 0.15`, reuses
`appraisal._get_executor()` (no second executor), debounces on session-change-OR-5-unreflected-
turns gated by the `last_reflected_turn_log_id` watermark, and applies watermark + bounded
deltas in ONE apply_deltas transaction (idempotence core; decay-prune happens here). Config
gains `reflection_enabled`/`reflect_every_n_turns`/`reflect_max_tokens`/
`reflect_deadline_seconds`. Wiring (`85897d8`): `post_llm_call` registered for turn capture
(the only hook carrying the assistant response — host contract verified), `on_session_end` +
`on_session_start` both route through `maybe_reflect`, REFL-04 resurfacing sentence added to
APPRAISAL_PROMPT, REFL-05 `- trust note:` advisory lines in `render_block(signals, snapshot)`
(sanitized, capped at 2, threshold < 0.4, empty-signal suppression takes precedence), the
SAFE-02 matrix reflection rows filled (zero placeholders remain) plus three new full-hook-path
rows, the SAFE-03 corpus extended with low-trust-snapshot renders (imperative-bait key comes
out quoted), and `test_reflection_demo.py -s` prints the offline cross-session proof.

## Key files

- `anansi/store.py`: SCHEMA_VERSION 3; new delta keys; get_meta/read_turns_since; lazy decay + `DECAY_PRUNE_THRESHOLD`
- `anansi/reflection.py`: the engine — REFLECTION_PROMPT/SCHEMA, ±0.15 clamps, caps (5/5/8), single-transaction apply, debounce gate, fail-open everywhere
- `anansi/config.py`: four reflection keys, defensive coercion (`_coerce_int` gained an optional `hi` clamp)
- `anansi/__init__.py` + `plugin.yaml`: post_llm_call capture hook; on_session_end/on_session_start reflection triggers; provides_hooks updated
- `anansi/render.py`: trust-hint lines through `_sanitize_text` + `_fmt`
- `tests/test_reflection_store.py` (10), `tests/test_reflection.py` (20), `tests/test_reflection_demo.py` (1, verbose), matrix + anticreep extensions

## Decisions made

- `read_snapshot(db_path, include_decayed=False)`: the reflection pass's "raw read" for
  prune-candidate discovery is a flag on the existing reader rather than a second reader —
  store.py stays the only sqlite surface, hot-path default behavior exactly as planned.
- `apply_deltas` busy_timeout default now follows `_DEFAULT_BUSY_TIMEOUT_MS` (was a literal
  5000 parameter default) so the plan's specified `_DEFAULT_BUSY_TIMEOUT_MS=100` monkeypatch
  genuinely governs locked-DB reflection-write tests; default behavior unchanged.
- Telemetry outcome vocabulary: `reflect_ok|reflect_timeout|reflect_parse_fail|`
  `reflect_llm_error|reflect_skipped:{disabled,no_ctx,no_turns,debounce,db_locked}`; trust
  fallback that succeeds reports `reflect_ok` (vocabulary kept small, per plan).
- Prune candidates skip ids the same pass adjusted/resolved (an adjustment refreshes
  updated_at — pruning it in the same transaction would race the model's own intent).
- Trust hints: absent key baseline 0.5; hints sorted lowest-first; values coerced
  defensively (non-numeric trust values skipped).

## Deviations from plan

1. **jsonschema is installed in the hermes venv (4.26.0)** — payloads driven through the
   full fake-LLM path must validate against REFLECTION_JSON_SCHEMA, so the
   unknown-contradiction-kind drop and out-of-range weight clamps are exercised via
   `parse_reflection` directly (host-side enum rejection surfaces as `reflect_parse_fail`
   before the parser ever sees the doc) — the exact split Phase 2 used for `parse_signals`.
2. **Green-at-every-commit collateral outside per-task file lists**: config-defaults
   equality dicts (test_telemetry_store.py, test_failopen_matrix.py `_DEFAULTS`) and the
   anticreep module-inventory set had to learn the new keys/module in the task-2 commit
   (reflection.py exists from task 2); the v2-hardcoded
   `test_v1_db_quarantined_and_recreated_as_v2` was renamed `..._at_current_schema` in the
   task-1 sweep (matrix reference updated in the same commit).
3. **Demo uses the monkeypatched `store.get_db_path` idiom, not a tmp HERMES_HOME env** —
   the established deterministic route (get_db_path prefers the host's get_hermes_home,
   which can ignore late env changes); documented in the demo docstring.
4. None of the plan's behavioral requirements were skipped or altered.

## Notes for downstream

- **03-03 live proof prerequisites are armed**: fresh-DB path (None last_seen counts as a
  session change) reflects on a single captured turn; on_session_start runs the pass BEFORE
  session B's first appraisal, so criterion 3 lands on turn 1.
- **Live deploy timeline**: the live v2 state.db quarantine-recreates at v3 on the next
  brand-new session's `on_session_start` (disposable-state doctrine). Until that boundary,
  `post_llm_call` capture against the v2 DB degrades silently (no assistant_excerpt column →
  apply_deltas False) — turn capture starts after the first new-session boundary; reads and
  telemetry on the v2 DB keep working meanwhile.
- Telemetry volume: one `reflect_*` row per turn (on_session_end fires per
  run_conversation) plus one per brand-new session; cap 2000 governs.
- Session-boundary latency: at most one reflect deadline (default 8.0s, same clamp [0.5,
  10.0]) once per boundary — accepted 03-CONTEXT cost decision; reflection runs the same
  cheap lane, max_tokens 700.
- Designed behavior (plan-amended): a failed session-change reflection has consumed that
  trigger (last_seen written pre-call); the unreflected span retries at the next debounce
  window or session change. Debounce counts captured (unreflected) turn_log rows, including
  captured-but-not-appraised turns — documented in reflection.py's module docstring.
