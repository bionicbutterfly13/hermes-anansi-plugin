# Plan 02-01 Summary

**Completed:** 2026-06-10 (~8:15am)

## What was built

The complete offline appraisal path: `config.py` (host-config plumbing under
`plugins.entries.anansi`, kill switch, clamped thresholds), telemetry table (schema v2,
2000-row cap) in `store.py`, `appraisal.py` (one `ctx.llm.complete_structured` call in a persistent
single-worker executor with `future.result(timeout=2.5)` hard deadline, single trust-gate fallback,
noun-only schema parse with per-signal 0.6 threshold, throttle helpers), `render.py` (sentinel
`[anansi appraisal]` block, top-3 per category, ≤500-token cap, icarus-derived sanitization), and
`pre_llm_call` orchestration in `__init__.py` (kill switch → rollover guard → throttles → snapshot →
appraisal → telemetry → render/suppress → `{"context": block}`). 49 tests green, incl. the
forced-injection dry-run demo (`pytest anansi/tests/test_dryrun_demo.py -q -s`).

## Key files
- anansi/{config,appraisal,render}.py + store.py telemetry + __init__.py wiring
- tests/{test_appraisal,test_pre_llm_call,test_dryrun_demo}.py

## Decisions made
- Extended the icarus injection patterns: made "all" optional in "ignore (all) previous instructions"
  and added a system-prompt-exfiltration pattern — the dry-run caught the original icarus regex
  missing "ignore previous instructions" (upstream-relevant for icarus too).

## Deviations
- Executor agent died mid-task-2 (machine-wide TLS outage killed new agent connections); orchestrator
  absorbed: verified+committed its task-2 work, implemented task 3 inline (hook wiring + both test files),
  fixed the fake sync_caller signature (host calls keyword-only: messages=, model_override=, ...).

## Notes for downstream
- Plan 02-02 (live validation) needs network; ANANSI_DEBUG_DUMP env var dumps successful blocks.
- Fake-LLM idiom: make_plugin_llm_for_test(plugin_id, policy=_TrustPolicy(...), sync_caller=fn(**kw)).
