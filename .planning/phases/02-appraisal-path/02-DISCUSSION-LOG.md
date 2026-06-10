# Phase 2 Discussion Log — Appraisal Path

**Date:** 2026-06-10
**Mode:** Autonomous (6-hour mandate). Choices follow the workflow's recommendation discipline;
most decisions were already locked by REQUIREMENTS/research — this log records the genuinely open calls.

## Area 1: Telemetry storage
- (a) Separate telemetry.db — isolates hot writes but second file/connection lifecycle
- (b) `telemetry` table in state.db with schema_version bump 1→2 — **CHOSEN**: one store, caps discipline
  reusable; disposable-state doctrine makes the version bump free pre-Phase-3 (quarantine-recreate)
- (c) JSONL log file — grep-able but un-queryable for p50/outcome distribution (success criterion 2)

## Area 2: Module layout
- (a) Everything in __init__.py — icarus-style monofile, gets unwieldy
- (b) appraisal.py + render.py, thin hooks — **CHOSEN**: testable units, lazy imports preserved
- (c) appraisal/ subpackage — overkill at this size

## Area 3: Near-duplicate throttle definition
- (a) Embedding/fuzzy similarity — new deps or extra LLM calls; rejected
- (b) Normalized exact match vs previous user message — **CHOSEN** (v1 simplicity; telemetry will show if too weak)
- (c) Levenshtein threshold — stdlib-only but tuning burden without data

## Area 4: Deadline mechanics
- (a) signal/alarm — main-thread only, not usable in hook thread
- (b) Persistent single-worker executor + future.result(timeout=2.5) — **CHOSEN** (research-recommended;
  discarded futures may complete in background — acceptable, telemetry records timeout)
- (c) asyncio wait_for — host dispatch is sync in both lanes (Item 1); event-loop creation per turn is waste

## Area 5: Empirical validation lane
- Network was down (all outbound HTTPS) at phase-1 close. Validation turns use whichever provider lane
  works when execution reaches them; lane recorded in 02-VALIDATION.md. — noted as Agent's Discretion

## Delegated to Agent's Discretion
- Prompt wording, schema field naming, history-tail size, token heuristic, telemetry columns, test layout

## Deferred
- D5/D3/D6 depth; register_auxiliary_task revisit at PR review
