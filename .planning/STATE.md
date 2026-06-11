# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-10)

**Core value:** Every Hermes turn gets a grounded metacognitive appraisal injected before response generation — with zero capacity for autonomous action and zero impact on turn reliability.
**Current focus:** Phase 4 — Packaging + Upstream PR Prep

## Current Position

Phase: 4 of 4 (Packaging + Upstream PR Prep)
Plan: not yet planned
Status: Phase 3 VERIFIED PASSED (d10300c: 18/18 must-haves, 4/4 criteria, 105/105 tests) — SAFE/REFL checkboxes flipped, Phase-3 banner set. Phase-4 carry-ins from 03-VERIFICATION: telemetry_summary reflect_* vocabulary gap (polish), sub-session appraisal timeout fraction (doc item), WAL sidecar copy idiom (PKG-02 inspection note)
Last activity: 2026-06-10 — Phase 3 verified passed; live cross-session loop proven on attempt 1/1 (03-VALIDATION.md, 03-VERIFICATION.md)

Progress: [████████░░] 80%

## Performance Metrics

**Velocity:**
- Total plans completed: 7
- Average duration: ~1 session
- Total execution time: ~6.5 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 — Skeleton + State | 2/2 | ~2h | ~1h |
| 2 — Appraisal Path | 2/2 | ~2h | ~1h |
| 3 — Fail-Open + Reflection | 3/3 | ~2.5h | ~1h |

## Accumulated Decisions

| Decision | Phase | Rationale |
|----------|-------|-----------|
| Appraisal inputs = message + history + SQLite state (one-turn memory lag) | pre-1 | pre_llm_call fires before memory prefetch — ✓ accepted by Dr. Mani 2026-06-10 |
| Reflection debounced + idempotent | pre-1 | on_session_end fires per turn |
| Zero new pip dependencies | pre-1 | Host surfaces + stdlib suffice; best PR posture |
| Confidence advisory-only; noun-fields-only schema; sanitized rendering | pre-1 | Calibration noise + injection-surface defense |
| kind: standalone explicit; **kwargs on all hooks; no MemoryProvider strings | pre-1 | Manifest string-scan + dispatcher kwarg landmines |
| Plugin renamed anansi → anansi | 1 | Name collision with live "Anansi Metacognitive Guardrails" plugin (see DECISIONS.md 2026-06-10) |
| Gateway lane dispatches hooks SYNC via same call site as CLI (turn_context.py:316-341) | 1 | Verified by code read; sync complete_structured in executor is correct for both lanes (Phase 2) |
| Item 3 answered: upstream/main has provides_hooks + ctx.llm parity (183d86b3e) | 1 | Fetched + diffed 2026-06-10; PKG-03 re-check still required before Phase 4 PR |
| Live lane: anthropic claude-haiku-4-5; deadline_seconds 8.0 (not 2.5) | 2 | Empirical: haiku appraisal is 4.4–7.3s generation-bound; 2.5s times out 100% |
| Contradiction kind labels advisory-only (never branch on exact kind) | 2 | Fixtures: 6/6 detection, 0/3 FP, but semantic/narrative over-applied, relational mislabeled |
| Trust-denied config degrades to fail-open timeout on this install (not trust_fallback) | 2 | Host model sonnet-4-6 needs ~37s/appraisal > 10s deadline clamp; mechanism unit-proven |
| WAL `BEGIN EXCLUSIVE` never blocks readers (== IMMEDIATE); reader-blocking lock tests need a rollback-journal tmp DB | 3 | Verified empirically 2026-06-10; locked-DB matrix rows assert both truths (test_failopen_matrix.py) |
| Bare second-person directive payload text quoted as reported material by render._sanitize_text (SAFE-03) | 3 | "you should migrate now" rendered structurally directive; quoting keeps the line observational |
| Dev tooling staged repo-locally (.devtools/pytest via uv --target); hermes venv never modified | 3 | uv-sync wipe risk locked in 03-CONTEXT; ./scripts/test.sh is the canonical test command |
| Reflection raw read = `read_snapshot(include_decayed=True)` flag, not a second reader; apply_deltas busy-timeout default follows `_DEFAULT_BUSY_TIMEOUT_MS` | 3 | store.py stays the only sqlite surface; locked-DB tests govern the real write path (03-02) |
| jsonschema (4.26.0) is live in the hermes venv: schema-rejected docs surface as parse_fail host-side; vocabulary-gating tested at the parse layer | 3 | Same split as Phase 2's parse_signals; full-path fake payloads must validate (03-02) |

## Blockers / Concerns

- ~~One-turn-lag ack~~ RESOLVED 2026-06-10: accepted by Dr. Mani; reflection carries appraisal context across the lag (R2)
- ~~p50 5501ms vs ≤1.0s target~~ RESOLVED 2026-06-10: target revised to p50 ≤6s / 8.0s deadline, max quality (R1, Dr. Mani decision)
- Upstream-main parity of ctx.llm facade + manifest keys must be re-verified before Phase 4 PR
- `telemetry_summary` failure_count/last_error counts reflect_* outcomes as failures (vocabulary predates reflection) — Phase-4 doc/fix candidate (03-VALIDATION.md §6)
- Host sub-sessions run the full hook set (appraisal + capture + reflection per sub-session; parallel haiku appraisals can contend into timeout — fail-open held live) — Phase-4 doc note (03-VALIDATION.md §9)

## Session Continuity

Last session: 2026-06-10 (autonomous)
Stopped at: Plan 03-03 complete (03-VALIDATION.md committed 183d41e; SUMMARY written; suite 105 green) — Phase 3 execution complete; next step verify-work for Phase 3
