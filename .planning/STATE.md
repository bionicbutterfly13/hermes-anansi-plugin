# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-10)

**Core value:** Every Hermes turn gets a grounded metacognitive appraisal injected before response generation; after PR #43906 was withdrawn, the plugin is proprietary and v1 remains the foundation.
**Current focus:** Phase 7 (Drive / Accountability) COMPLETE — all 4 plans executed on branch phase-7-drive-accountability; next is verify-work / review / ship for Phase 7

## Current Position

Phase: 7 of 7 (Drive / Accountability — first proprietary implementation increment) — COMPLETE
Plan: 07-04 COMPLETE (2/2 tasks, full suite green at 165 passed). Phase 7 done (4/4 plans). Next: verify-work / review / ship Phase 7.
Status: All four Phase 7 plans executed on branch phase-7-drive-accountability. DRIVE-01 (goal tables, schema v4, single sqlite surface), DRIVE-06 partial (drive kill switch + byte-for-byte invariant + non-failure telemetry), DRIVE-03 partial (goal_signals + `- drive note:` line) landed in 07-01. DRIVE-02 (07-02): stdlib-only `goal_momentum` helper derives per-goal momentum from GROUND TRUTH at appraisal-READ time; `stalled_days` threads through the `- drive note:` render line; stalled goals render FIRST; fail-open everywhere. DRIVE-04 (07-03): NEW first-person `- drive want:` line ("I want X moving (stalled N days)") as a LABEL allowance ONLY — `_SECOND_PERSON_DIRECTIVE_RE` + `conftest.DIRECTIVE_PATTERNS` UNCHANGED; existing SAFE-03/04 negative controls preserved + a symmetric drive-specific control added (first-person passes; second-person quoted or rejected). DRIVE-05 (07-03 — the never-omit red line): a `flagged_priority>0` goal is EXEMPT from BOTH the `[:3]` slice AND the token-cap line-drop — flagged wants render FIRST into a PROTECTED prefix, the cap loop stops at `max(protected_count, 2)`, and the guarantee reads PERSISTED goals (not model output) so a flagged goal surfaces even when the model omits it; proven under adversarial crowding + full-hook integration. Anti-complacency: a stalled `push_when_stalled`/`support_style='firm'` goal renders a VISIBLE `[under-support: ...]` clause separate from the neutral stalled read (Pitfall #9). DRIVE-06 remainder (07-04): the two remaining containment controls — a domain WHITELIST (`drive_domains`, default [] = unrestricted) suppresses off-domain goals from BOTH the persisted-goal slice AND echoed `goal_signals`, and a per-turn ENERGY BUDGET (`drive_energy_budget`, default 3, floor 0) caps NON-flagged drive lines while a flagged want is EXEMPT (never-omit beats the budget; DRIVE-05 > DRIVE-06). `drive_pressure` (quiet|standard|firm, code-red excluded) is coerced/documented config. All coerce defensively (`_coerce_str_list`/`_coerce_choice`) and get_cfg never raises; consolidated fail-open matrix gains a documented row per new drive path; README documents all three containment controls + a Drive subsection. Next workflow: `verify-work` / `/review` / `/ship` for Phase 7.
Last activity: 2026-06-14 — Executed plan 07-04 (DRIVE-06 remainder: domain whitelist + energy budget containment + consolidated fail-open matrix + README); 2 atomic commits; SUMMARY written; suite 151 → 165 passed. Phase 7 complete.

Progress: [██████████] 100% v1; Phase 6 design captured; Phase 7 COMPLETE (4/4 plans) — drive layer contained + adjustable, never-omit guaranteed

## Performance Metrics

**Velocity:**
- Total plans completed: 10
- Average duration: ~1 session
- Total execution time: ~7.5 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 — Skeleton + State | 2/2 | ~2h | ~1h |
| 2 — Appraisal Path | 2/2 | ~2h | ~1h |
| 3 — Fail-Open + Reflection | 3/3 | ~2.5h | ~1h |
| 4 — Packaging + PR Prep | 2/2 | ~1h | ~0.5h |
| 5 — Proprietary Pivot State Reconciliation | 1/1 | ~0.25h | ~0.25h |

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
| In-tree tests are a package (`tests.plugins.anansi.*`); plugin loads as module `anansi` via conftest spec-load, never `plugins.anansi` | 4 | Three-module-identity trap avoided; worktree root force-inserted at sys.path[0] shadows the editable install (04-02) |
| .devtools/pytest staged at upstream pins (pytest 9.0.2, pytest-timeout 2.4.0, pytest-asyncio 1.3.0) | 4 | Worktree runs need upstream's addopts (--timeout); plugin-repo suite re-verified green under the pins (04-02) |
| Phase 6 first increment = Drive/accountability; drive state extends anansi SQLite store (store.py) | 6 | discuss-phase 6 / 06-CONTEXT; single sqlite surface preserved |
| Never-omit invariant: agent guesses never outrank stated priorities; never silently drop a flagged item | 6 | Core drive red line; silent omission = betrayal (Dr. Mani top anti-value) |
| Drive surfacing in-turn only (no proactive push); heartbeat + code-red interruption deferred | 6 | Extends one-turn-lag idiom; fail-open preserved; code-red needs user-defined triggers only |
| Drive pressure adjustable + inspectable | 6 | Drive may adjust salience/urgency/persistence only; neutral read vs drive effect must stay visible |
| Anti-complacency is part of drive safety | 6 | User-authorized push zones prevent stalled high-priority goals from being quietly downranked; under-support must be surfaced |
| Goal state lives in store.py schema v4 (`goals` table); agent-nominated goals default to INERT `status='candidate'`, never surfaced as active until a goals_status promotion | 7 | DRIVE-01 (07-01); goal provenance — agent nominates, user mints; single sqlite surface preserved |
| Drive kill switch (`drive_enabled`) is SEPARATE from appraisal `enabled`; gated AFTER the appraisal check, no early-return; drive-off block is byte-for-byte identical to a no-goals run; `skipped:drive_disabled` is a non-failure | 7 | DRIVE-06 partial (07-01); success criterion 4 — drive-off suppression proven via byte-for-byte test + telemetry exclusion-list |
| Drive-off suppression is belt-and-suspenders: build_context omits the goals slice AND __init__ strips goal_signals before render | 7 | 07-01 — byte-for-byte invariant holds regardless of (fake/adversarial) model output, not just a faithful model |
| Per-goal momentum derived at READ time in store.read_snapshot (git reflog committer epoch + os.stat mtimes via stdlib read-mode open() only — NO subprocess/git lib), NOT behind debounced reflection | 7 | DRIVE-02 (07-02); a goal that stalled this turn reads stalled this turn (Pitfall #3); anti-creep forbidden-substring scan bricks on subprocess/os.system even in comments |
| "Stalled louder" = SALIENCE/ORDERING (stalled goals render first), never imperative loudness; neutral momentum (stalled_days) and drive-caused pressure effect (`[push zone]` clause) render SEPARATELY and stay inspectable | 7 | DRIVE-02 (07-02); SAFE-04 + reactance — loudness-via-imperative is forbidden; Pitfall #9 inspectability red line |
| `enrich_goal_signals` grounds each parsed goal_signal in the matching persisted goal's read-time momentum + pressure metadata; goal `domain` doubles as the per-goal mtime hint (repo-containment guarded) | 7 | DRIVE-02 (07-02); stalled signal anchored to ground truth even when the model omits stalled_days; no schema bump |
| First-person `- drive want:` voice is a LABEL allowance only (added to `conftest.ALLOWED_LABEL_PREFIXES`); `_SECOND_PERSON_DIRECTIVE_RE` + `conftest.DIRECTIVE_PATTERNS` stay UNCHANGED — second-person directives still quoted/neutralized; negative controls preserved + a symmetric drive control added | 7 | DRIVE-04 (07-03); SAFE-04 carve-out is first-person only; a checker that cannot fail proves nothing |
| Never-omit: a `flagged_priority>0` goal renders FIRST into a PROTECTED prefix, exempt from the `[:3]` slice AND the token-cap pop (`floor=max(protected_count,2)`); never-omit BEATS the soft ~500-token cap; the guarantee reads PERSISTED goals, not model output, so a flagged goal surfaces even when the model omits it | 7 | DRIVE-05 (07-03); the drive red line — silent omission = betrayal; proven under adversarial crowding + full-hook with a model payload that omits the goal |
| Anti-complacency: a stalled goal with `push_when_stalled`/`support_style='firm'` renders a VISIBLE `[under-support: ...]` clause SEPARATE from the neutral `stalled N days` read; APPR-05 precedence intact (empty signals ⇒ None even with a flagged goal) | 7 | DRIVE-05 (07-03); Pitfall #9 inspectability — drive effect never blended into the neutral read; a flagged goal rides a block, never forces one |
| Domain whitelist (`drive_domains`, default [] = unrestricted) suppresses off-domain goals from BOTH the persisted-goal slice AND the model's echoed `goal_signals` (`_filter_signals_by_goals`), so an off-domain goal cannot leak back through the model echo; empty whitelist = no-op (07-01..03 unchanged); fail-open returns the unfiltered set | 7 | DRIVE-06 (07-04); filtering only the persisted goals left an echoed off-domain `goal_signal` able to surface as a `- drive note:` — the signal-level filter closes that leak |
| Energy budget (`drive_energy_budget`, default 3, floor 0) caps NON-flagged drive notes at `min(3, budget)` INSIDE render_block (after the protected flagged prefix); a flagged `- drive want:` is structurally EXEMPT — never-omit (DRIVE-05) beats the budget (DRIVE-06) by construction; malformed budget ⇒ standing top-3 (fail-open) | 7 | DRIVE-06 (07-04); the cap trims `non_flagged_signals` only, never the protected prefix |
| `drive_pressure` (quiet\|standard\|firm; code-red EXCLUDED from Phase 7) is coerced/documented config with no behavioural branch yet — the adjustability surface a later heartbeat/panel increment tunes; coercion (`_coerce_choice`) never raises | 7 | DRIVE-06 (07-04); containment surface complete without over-building the firmness behaviour now |

## Blockers / Concerns

- ~~One-turn-lag ack~~ RESOLVED 2026-06-10: accepted by Dr. Mani; reflection carries appraisal context across the lag (R2)
- ~~p50 5501ms vs ≤1.0s target~~ RESOLVED 2026-06-10: target revised to p50 ≤6s / 8.0s deadline, max quality (R1, Dr. Mani decision)
- ~~Upstream-main parity of ctx.llm facade + manifest keys must be re-verified before Phase 4 PR~~ RESOLVED 2026-06-10 (04-02, 04-PARITY.md): diff vs 183d86b3e EMPTY at PR-time SHA 9dd9ef0ec; all surfaces verified by fresh grep
- ~~PR SUBMISSION GATE~~ CLOSED 2026-06-10: PR #43906 was submitted, then withdrawn by Dr. Mani decision; fork branch deleted; no upstream plugin submission remains pending.
- ~~`telemetry_summary` counts reflect_* outcomes as failures~~ RESOLVED 2026-06-10 (04-01, 87484eb): vocabulary fixed in both failure_count and last_error; mixed-outcome test added
- ~~Host sub-sessions run the full hook set — Phase-4 doc note~~ RESOLVED 2026-06-10 (04-01): documented honestly in anansi/README.md (sub-session section + WAL sidecar idiom)

## Roadmap Evolution

- Phase 7 added 2026-06-14: Drive / Accountability — first proprietary implementation increment. Homes the build designed in 06-CONTEXT (Phase 6 was design-only). Introduces proprietary requirement IDs DRIVE-01..06.

## Session Continuity

Last session: 2026-06-14 (executed Phase 7 plan 07-04 on branch phase-7-drive-accountability)
Stopped at: 07-04 complete (2 atomic commits, suite green 165 passed, SUMMARY written) — Phase 7 COMPLETE (4/4 plans); next: verify-work / review / ship Phase 7.
