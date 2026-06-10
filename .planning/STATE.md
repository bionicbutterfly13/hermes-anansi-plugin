# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-10)

**Core value:** Every Hermes turn gets a grounded metacognitive appraisal injected before response generation — with zero capacity for autonomous action and zero impact on turn reliability.
**Current focus:** Phase 2 — Appraisal Path (the core)

## Current Position

Phase: 2 of 4 (Appraisal Path)
Plan: 2 of 2 complete in current phase (02-01 + 02-02 done)
Status: Phase 2 execution complete — ready for verify-work
Last activity: 2026-06-10 — Plan 02-02 complete (live validation: real-turn block, fixtures 6/6 detection 0 FP, kill switch/throttles verified, p50 5501ms honest miss vs 1.0s target); Phase-1 human-needed item also closed (01-VERIFICATION now passed 17/17)

Progress: [████░░░░░░] 38%

## Performance Metrics

**Velocity:**
- Total plans completed: 4
- Average duration: ~1 session
- Total execution time: ~4 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 — Skeleton + State | 2/2 | ~2h | ~1h |
| 2 — Appraisal Path | 2/2 | ~2h | ~1h |

## Accumulated Decisions

| Decision | Phase | Rationale |
|----------|-------|-----------|
| Appraisal inputs = message + history + SQLite state (one-turn memory lag) | pre-1 | pre_llm_call fires before memory prefetch — ⚠ needs Dr. Mani ack |
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

## Blockers / Concerns

- ⚠ PROJECT.md amendment (reduced appraisal inputs / one-turn lag) awaits Dr. Mani acknowledgment
- ⚠ p50 appraisal wall time 5501ms vs ≤1.0s ROADMAP target — Phase-3 decision needed (terser prompt/schema, lower max_tokens, faster lane, or revised target)
- Upstream-main parity of ctx.llm facade + manifest keys must be re-verified before Phase 4 PR

## Session Continuity

Last session: 2026-06-10 (autonomous)
Stopped at: Plan 02-02 complete (live validation evidenced in 02-VALIDATION.md, zero pending-network items); next step verify-work for Phase 2
