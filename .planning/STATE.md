# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-10)

**Core value:** Every Hermes turn gets a grounded metacognitive appraisal injected before response generation — with zero capacity for autonomous action and zero impact on turn reliability.
**Current focus:** Phase 4 — Packaging + Upstream PR Prep

## Current Position

Phase: 4 of 4 (Packaging + Upstream PR Prep)
Plan: 04-01 COMPLETE — next: 04-02 (in-tree arrangement, upstream-main parity re-check, PR branch + PR_BODY.md)
Status: Plan 04-01 executed (3 commits: 87484eb fix, 1a49dbb test, 5a9e751 docs; suite 105→107 green). All three 03-VERIFICATION carry-ins closed: telemetry_summary reflect_* vocabulary fixed + tested, sub-session timeout behavior documented, WAL sidecar copy idiom documented. PKG-01 provable by one test run; canonical plugin README + thin repo README in place
Last activity: 2026-06-10 — Plan 04-01 complete (telemetry vocabulary fix, PKG-01 manifest proof, README pair)

Progress: [█████████░] 90%

## Performance Metrics

**Velocity:**
- Total plans completed: 8
- Average duration: ~1 session
- Total execution time: ~7 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 — Skeleton + State | 2/2 | ~2h | ~1h |
| 2 — Appraisal Path | 2/2 | ~2h | ~1h |
| 3 — Fail-Open + Reflection | 3/3 | ~2.5h | ~1h |
| 4 — Packaging + PR Prep | 1/2 | ~0.5h | ~0.5h |

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
| telemetry_summary failure vocabulary keeps exclusion-list shape (non-failures: ok/trust_fallback/reflect_ok + skipped:*/reflect_skipped:*) | 4 | Unknown future outcomes count as failures by default — fail-loud in the derived view (04-01) |
| PKG-01 manifest test asserts set equality between provides_hooks and AST-collected register_hook names | 4 | Catches both undeclared registrations and stale manifest entries (04-01) |

## Blockers / Concerns

- ~~One-turn-lag ack~~ RESOLVED 2026-06-10: accepted by Dr. Mani; reflection carries appraisal context across the lag (R2)
- ~~p50 5501ms vs ≤1.0s target~~ RESOLVED 2026-06-10: target revised to p50 ≤6s / 8.0s deadline, max quality (R1, Dr. Mani decision)
- Upstream-main parity of ctx.llm facade + manifest keys must be re-verified before Phase 4 PR (04-02)
- ~~`telemetry_summary` counts reflect_* outcomes as failures~~ RESOLVED 2026-06-10 (04-01, 87484eb): vocabulary fixed in both failure_count and last_error; mixed-outcome test added
- ~~Host sub-sessions run the full hook set — Phase-4 doc note~~ RESOLVED 2026-06-10 (04-01): documented honestly in anansi/README.md (sub-session section + WAL sidecar idiom)

## Session Continuity

Last session: 2026-06-10 (autonomous)
Stopped at: Plan 04-01 complete (3 commits 87484eb/1a49dbb/5a9e751; SUMMARY written; suite 107 green) — next: execute 04-02 (in-tree arrangement, parity re-check, PR branch + PR_BODY.md, sign-off gate)
