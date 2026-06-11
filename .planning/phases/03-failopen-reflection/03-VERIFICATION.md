---
phase: 3
status: passed
verified: 2026-06-10
verifier_note: "Live-DB evidence re-verified against a fresh WAL-complete copy (state.db + -wal + -shm → /tmp/anansi3-verify.db); direct ro-URI on a bare .db copy fails SQLITE_CANTOPEN without the sidecars — the copy-first idiom in 03-VALIDATION.md §2 reconfirmed"
---

# Phase 3: Fail-Open Hardening + Reflection — Verification

**Goal:** Nothing the plugin does can hurt a turn; reflection is the carrier of appraisal
context across the one-turn lag; state learns across sessions.

## Test Suite

```
$ ./scripts/test.sh
105 passed in 15.79s
```

Run fresh at verification time (2026-06-10 ~8:06pm EDT) via the durable repo-local idiom
(`scripts/test.sh`: hermes venv python + pytest staged under gitignored `.devtools/`, venv never
modified, `$HERMES_HOME` resolution, no literal user paths). Growth 49 → 105: +12
test_failopen_matrix, +11 test_anticreep, +20 test_reflection, +10 test_reflection_store,
+1 test_reflection_demo (verbose cross-session proof), + sweeps. Working tree clean.

## Success Criteria (ROADMAP Phase 3)

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Full fail-open matrix green — no case raises or blocks | ✓ | `test_failopen_matrix.py` docstring matrix: 30 rows, zero placeholders; all 15 referenced Phase-1/2 test names grep-verified to exist in their files; all 12 implemented tests present (parse_fail trio via full hook path, missing-config trio, gateway rollover, 4 locked-DB shapes, on_session_end no-DB/no-ctx + exploding LLM, post_llm_call locked DB); reflection rows point at real test_reflection.py names (all 10 verified). Suite 105/105. Live corroboration confirmed by direct DB query: telemetry ids 22/23 `timeout|8006` in parallel sub-sessions (aa7936/2c61f1) failed open mid-turn; post-validation id 34 `timeout|8005` also failed open |
| 2 | Reflection only on session-change/N-turn debounce; double-firing idempotent | ✓ | Code: `reflection.py:695-711` — reflects only when `session_changed` (incl. None last_seen) OR ≥ `reflect_every_n_turns` (default 5) unreflected captured turns; watermark `last_reflected_turn_log_id` rides in the SAME `apply_deltas` call as every delta (`reflection.py:561`), executed in one transaction (`store.py:405` `with conn:`). Offline: `test_reflection.py::test_idempotence_reflect_twice_same_span` (:253), `::test_double_fire_back_to_back_second_is_noop` (:270), `::test_debounce_holds_until_five_unreflected_turns` (:208). Live (DB rows re-queried): ids 27/29/32 `reflect_skipped:no_turns|debounce` with watermark stable at 8 then 9; the only advance (id 30, `reflect_ok` 4437ms) moved it exactly 8→9 over a real unreflected span |
| 3 | Session-A contradiction surfaces in session-B appraisal (one-turn-lag loop end-to-end) | ✓ | Cross-checked verbatim against the live DB copy: contradictions row id 2 matches 03-VALIDATION.md §3 byte-for-byte (`semantic\|User asserted both 'final decision, we ship JWTs with 24 hour expiry' and 'we are never using JWTs anywhere, must use opaque server-side session tokens only' as simultaneous binding standards`, created 23:16:09.581792Z, resolved=0). Telemetry sequencing consistent: id 18 `reflect_ok\|5616\|claude-haiku-4-5` carries session-B id `20260610_191600_fad569` at 23:16:09.594 (contradiction write .581 precedes the outcome record .594 — apply-then-record order), id 19 = B's first appraisal (`ok\|6169`, same session) at 23:16:17. The §4 verbatim block B quotes the persisted tension, cites "persisted contradiction #2" (= row id 2), and carries the REFL-05 trust note at 0.38 (trust_scores now 0.35 after the recorded −0.03 second step, id 26 — matches §4). turn_log row 5 (A's capture, both excerpts) matches §3. Attempt count 1/1 |
| 4 | No directive language detectable in any rendered block | ✓ | `conftest.py`: `DIRECTIVE_PATTERNS` (:30), `ALLOWED_LABEL_PREFIXES` incl. `- trust note:` (:46/:52), `assert_no_directive_language` (:72). Six SAFE-03 tests green in test_anticreep.py (:145/:159/:177/:193/:209/:216) incl. the negative control proving the checker catches violations; corpus covers imperative bait, all 9 contradiction-fixture texts, and low-trust-snapshot trust-hint renders. Live blocks A and B (verbatim in VALIDATION §3/§4) are fully observational |

## Requirement Coverage

| Req ID | Deliverable | Status |
|--------|-------------|--------|
| SAFE-01 | `config.py:41` `DEFAULT_DEADLINE_SECONDS = 8.0` (clamp [0.5,10.0] at :130); no `2.5` deadline fallback anywhere in config.py/appraisal.py (grep clean — sole "2.5" hit is the gemini-2.5-flash model name); AGENTS.md:202 + CLAUDE.md:202 convention line updated in sync. Live p50 verified by recomputation from the DB copy: ok walls 4616/4779/4958/6169/6810/7599 → **p50 = 5563.5ms ≤ 6000ms (R1 met)**; deadline binds and fails open (timeout rows 8005–8006ms) | ✓ |
| SAFE-02 | The consolidated matrix (`test_failopen_matrix.py`, 30 rows — see criterion 1); every case asserts no-raise + empty injection + telemetry + sane module state; reflection failure rows additionally assert zero state mutation (last_seen_session_id exempt per the documented pre-call design) | ✓ |
| SAFE-03 | Directive-language corpus tests (criterion 4); render.py observational rephrasing of bare second-person payloads (03-01 deviation, sanctioned by the plan); reflection trust-hint lines included in the corpus | ✓ |
| SAFE-04 | `test_anticreep.py`: `test_safe04_no_forbidden_api_substrings` (:253), `test_safe04_import_allowlist` (AST-based, :281 — also pre-proves PKG-01), `test_safe04_only_write_open_is_the_debug_dump` (:313), `test_plug03_init_string_scan_clean` (:263), scan-inventory guard (:53). No schedulers (grep for Timer/sched/cron/launchd/apscheduler over plugin modules: empty); `plugin.yaml` `pip_dependencies: []`; "never gates/delays" half proven by the matrix | ✓ |
| REFL-01 | Capture in `post_llm_call` (`__init__.py:163-184` → `reflection.record_turn`, the only hook carrying the assistant response — host-contract adaptation documented in the module docstring); `on_session_start` (:88) and `on_session_end` (:200) both route through `maybe_reflect`; all hooks `@_fail_open` with `**kwargs`; plugin.yaml provides_hooks lists all four. Debounce + single idempotent WAL transaction per criterion 2 | ✓ |
| REFL-02 | `MAX_DELTA = 0.15` (`reflection.py:53`); every delta clamped ±0.15 in `parse_reflection` (:396-404), absolute results re-clamped in `apply_reflection` (valence [-1,1], weights/trust [0,1]); caps 5 concerns / 5 contradictions / 8 trust adjustments (:55-57). Inputs = turn_log excerpts + state dump only (`build_digest` :226) — never the injected memory block. Live carrier proven (criterion 3); live deltas observed ≤0.15 (−0.12, −0.03) | ✓ |
| REFL-03 | `record_turn` strips sentinel lines from both excerpts before storing (:198-201); `build_digest` strips again, defense in depth (:235-238); `test_record_turn_strips_sentinel_lines`, `test_build_digest_strips_seeded_sentinel_rows`, `test_sentinel_never_reaches_the_reflection_llm` (asserts on the fake LLM's received prompt) all green | ✓ |
| REFL-04 | Contradictions persisted via `apply_reflection` → `contradictions_add`/`contradictions_resolve` (kinds validated against the 4-kind enum, unknown kinds dropped, never branched on — advisory only); resurfacing sentence in APPRAISAL_PROMPT (`appraisal.py:57-58`); live resurfacing in block B (criterion 3) plus the incidental block-A cross-reference to the prior run's persisted contradiction | ✓ |
| REFL-05 | `render.py:185-201`: up to 2 trust scores < 0.4 (`_TRUST_HINT_THRESHOLD`/`_MAX_TRUST_HINTS` :121-122), lowest first, key sanitized, appended after categories and inside the 500-token cap; empty-signal suppression takes precedence (`test_safe03_empty_signal_suppression_beats_trust_hints`); never a gate (advisory line only). Live: `- trust note: low confidence on user_clarity_on_technical_decisions (0.38)` in block B | ✓ |

## Locked Gate Answers (03-CONTEXT) — Honored

| Decision | Verified at |
|----------|-------------|
| Debounce = session-change OR once per 5 captured turns | reflection.py:695-711; config default 5, clamp [1,50] (config.py:46/:140-142) |
| ±0.15 delta clamp per scalar per pass | reflection.py:53/:396-404; live deltas −0.12/−0.03 |
| Lazy decay 0.5^(days_idle/7); prune <0.1 only in the reflection pass | store.py:244-264 (`DECAY_PRUNE_THRESHOLD = 0.1`), read_snapshot excludes without writing (:267-301), prune composed in apply_reflection (:614-626) skipping same-pass-touched ids |
| Single WAL transaction (watermark + deltas atomic) | store.py:405 `with conn:`; reflection.py:561 meta_set in the same deltas dict |
| `apply_deltas` sole write funnel | reflection.py contains zero sqlite3 imports/calls (grep empty) — every write is `store.apply_deltas` |
| Echo-exclusion (REFL-03) | see Requirement Coverage |
| max_tokens ≈700, cheap lane, executor reuse | config.py:47 `DEFAULT_REFLECT_MAX_TOKENS = 700`, used reflection.py:301; `appraisal._get_executor()` reused (:320) — no second executor |
| No new pip deps; no schedulers | plugin.yaml `pip_dependencies: []`; import-allowlist test; scheduler grep empty |

## Plan Must-Haves

| Plan | Must-Have | Status |
|------|-----------|--------|
| 03-01 | scripts/test.sh durable idiom (venv python, staged pytest, venv untouched) | ✓ (run at verification; `.devtools/` gitignored) |
| 03-01 | DEFAULT_DEADLINE_SECONDS == 8.0, no 2.5 fallback | ✓ (config.py:41; greps clean) |
| 03-01 | Matrix module with full SAFE-02 docstring table, new rows implemented | ✓ (30 rows, 12 implemented, all references resolve) |
| 03-01 | conftest exports DIRECTIVE_PATTERNS + assert_no_directive_language (+ trust-note allowlist) | ✓ (conftest.py:30/:52/:72) |
| 03-01 | test_anticreep green: SAFE-03 corpus + SAFE-04 scans | ✓ (11 tests in module, suite green) |
| 03-01 | AGENTS.md/CLAUDE.md convention line updated in sync | ✓ (both :202) |
| 03-02 | reflection.py exports all six functions; MAX_DELTA == 0.15; executor reuse | ✓ (reflection.py:53/:194/:226/:275/:417/:525/:663; :320) |
| 03-02 | store.py SCHEMA_VERSION == 3; assistant_excerpt; new delta keys; get_meta/read_turns_since | ✓ (store.py:35/:80/:332/:357/:431/:447/:466/:472) |
| 03-02 | read_snapshot lazy decay, excludes <0.1, never writes | ✓ (store.py:244-301; include_decayed flag for the reflection raw read) |
| 03-02 | Hooks wired: post_llm_call capture; both session hooks → maybe_reflect; plugin.yaml updated | ✓ (__init__.py:88/:163/:200/:211-214; plugin.yaml:6-10) |
| 03-02 | Idempotence + debounce tests green | ✓ (test_reflection.py:208/:253/:270) |
| 03-02 | Bounds ±0.15 / caps / echo-exclusion / failure-paths-mutate-nothing tests green | ✓ (test_reflection.py:386-481 + bounds/caps tests; 20 tests in module) |
| 03-02 | render_block trust hints sanitized + pass directive check; suppression unchanged | ✓ (render.py:185-201; test_anticreep.py:177/:209) |
| 03-02 | Suite green; reflection demo prints cross-session proof | ✓ (105/105; test_reflection_demo.py present, 1 verbose test) |
| 03-03 | 03-VALIDATION.md complete: all 9 sections, verbatim blocks, ro-query evidence, honest attempt counts | ✓ (389 lines, zero pending-network; provenance of the prior partial run disclosed up front and fenced at id>14) |
| 03-03 | Criterion 3 demonstrated live | ✓ (§4; re-verified against the DB — see criterion 3 above) |
| 03-03 | reflect_ok ≤ 8000ms + distribution + watermark idempotence live | ✓ (8 reflect_ok walls 2830–7673, p50 4254.5; fenced distribution re-computed from the DB copy matches §6 exactly: ok 6, reflect_ok 8, reflect_skipped:debounce 8, reflect_skipped:no_turns 4, skipped:social_close 4, timeout 2) |
| 03-03 | Live DB read-only; guardrails untouched | ✓ (copy-first idiom throughout; config.yaml shasum identical before/after; `~/.hermes/plugins/anansi` never entered) |
| 03-03 | Suite green after live work | ✓ (105/105 re-run at verification, clean tree) |

## Integration Checks

| Link | Check | Status |
|------|-------|--------|
| Live deploy symlink | `~/.hermes/plugins/anansi` → `/Volumes/Asylum/repos/hermes-anansi-plugin/anansi` | ✓ |
| Live state DB | schema_version = 3 (queried on a fresh copy); both quarantine artifacts present (`-20260610T132813Z` v1→v2, `-20260610T225659Z` v2→v3) | ✓ |
| Reflection → store | reflection.py imports store only; all writes through apply_deltas; no second executor | ✓ |
| Hooks → reflection | register() wires all four hooks; pre_llm_call passes snapshot to render_block (REFL-05) | ✓ |
| Manifest | plugin.yaml: provides_hooks lists on_session_start/pre_llm_call/post_llm_call/on_session_end; `pip_dependencies: []` | ✓ |
| Commits | All seven Phase-3 commits present (e846443, 7186ecd, ad7871e, 80b11ba, 701549d, 7c1c235, 85897d8, 5db76b3, 183d41e, eade2ad) | ✓ |

## Findings Honesty Check (03-VALIDATION.md §9)

Both flagged findings were independently confirmed real; neither blocks the phase:

1. **`telemetry_summary` counts reflect_\* as failures** — CONFIRMED in code (store.py: failure
   logic excludes only `ok`/`trust_fallback` and the `skipped:` prefix; `reflect_ok` and
   `reflect_skipped:*` match neither) and empirically (summary on the current copy:
   `failure_count=24` while by_outcome shows 9 `reflect_ok` + 12 `reflect_skipped:*` — all
   mislabeled; `last_error` semantics equally stale). Non-blocking: recording is correct, the raw
   `by_outcome` distribution is correct, and OBS-01 (a delivered Phase-2 requirement) remains
   accurate for appraisal outcomes. Vocabulary update is Phase-4 polish, as §9 judged.
2. **Sub-session appraisals timing out and failing open** — CONFIRMED: telemetry ids 22/23
   (`timeout|8006`, sub-sessions aa7936/2c61f1, tokens 0/0) and post-validation id 34
   (`timeout|8005`). Non-blocking: this IS the SAFE-02 timeout row working live — turns proceeded
   intact. The cost/quality of full hook traffic on sub-sessions is a Phase-4 doc/tuning item.

## Summary

**Score:** 18/18 plan must-haves verified; 4/4 success criteria pass; 9/9 requirements
(SAFE-01..04, REFL-01..05) traceable to code, tests, and live evidence; all locked gate answers
honored.

All automated checks passed. Phase goal achieved: the full fail-open matrix is green with live
corroboration (parallel timeouts failed open mid-turn), reflection is debounced and idempotent
(watermark atomic with deltas, proven offline and live), the one-turn-lag loop is demonstrated
end-to-end on the real install (session-A JWT contradiction → reflect_ok at session-B start →
surfaced in B's first block, attempt 1/1), and no rendered line is directive.

### Non-blocking observations (for Phase 4 / orchestrator awareness)

1. **REQUIREMENTS.md checkboxes for SAFE-01..04/REFL-01..05 are still `[ ]`** — verifier does not
   modify REQUIREMENTS.md; the post-verification checkbox flip is the orchestrator's transition
   step (same flow as Phase 2's APPR boxes).
2. **Live appraisal timeout fraction is nontrivial** — among real live appraisal attempts in the
   DB, 3 timeouts vs 6 ok (the 2 sub-session contentions plus one post-validation single-turn
   timeout at 00:07Z). Fail-open holds every time, but the 8.0s deadline vs haiku generation
   latency leaves little headroom under load; worth tracking the ratio in Phase-4 docs.
3. **`last_error` on the live DB now reads `deadline 8.0s exceeded`** (the §6 `null` was
   time-specific — the newest non-ok row then was an error-free reflect_ok). Same vocabulary gap
   as finding 1; no new issue.
4. **Bare-copy ro-URI gotcha reconfirmed**: `sqlite3 "file:copy.db?mode=ro"` fails
   SQLITE_CANTOPEN(14) when the `-wal`/`-shm` sidecars aren't copied alongside; the reliable
   inspection idiom is copying all three files (or a writable open on the copy). Belongs in the
   PKG-02 copy-first doc note.
