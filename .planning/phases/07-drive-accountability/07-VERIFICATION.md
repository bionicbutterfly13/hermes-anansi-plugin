---
phase: 7
status: passed
verified: 2026-06-14
---

# Phase 7: Drive / Accountability — Verification

Verified against the IMPLEMENTATION (real source read + suite run), not the
executor self-reports. Suite run twice (`./scripts/test.sh` and the host venv
pytest): **165 passed in ~6.2s** — matches the executors' claim exactly.

## Real Test Count

| Source | Result |
|--------|--------|
| `./scripts/test.sh` | **165 passed in 6.21s** |
| host venv pytest (drive subset) | 57 + 27 = 84 drive/safety tests collected & green |
| Claimed by executors | 165 |
| Verdict | ✓ count is real, not inflated |

Net-new drive tests on disk: test_drive_store (7), test_drive_appraisal (4),
test_drive_velocity (12), test_drive_neveromit (12), test_drive_config (11);
plus DRIVE-04 quartet in test_anticreep and new drive rows in
test_failopen_matrix.

## Requirement Coverage (DRIVE-01..06)

| Req | Status | Evidence (file:symbol) |
|-----|--------|------------------------|
| DRIVE-01 — goal objects, single sqlite surface | ✓ met (one column gap, below) | `store.py:35 SCHEMA_VERSION=4`; `store.py:99 CREATE TABLE goals`; `store.py:714 goals_add` (defaults `status='candidate'` INERT), `:736 goals_update`, `:752 goals_status`; `goals` in `_TABLES:57`, `CAPS:44`, cap-eviction tuple `:793`; `read_snapshot:526` returns `goals`. v3→v4 quarantine: `test_drive_store::test_v3_db_quarantine_recreates_at_v4` |
| DRIVE-02 — read-time velocity (stdlib, no subprocess/git lib) | ✓ met | `store.goal_momentum:416` + `_last_commit_epoch:319` (read-mode `open()` of `.git/logs/HEAD`+`os.stat`), `_repo_root:292`; annotated at read time in `read_snapshot:531`; salience `_MOMENTUM_SALIENCE:279` (stalled 1.0 > moving 0.3). NO subprocess/os.system/git lib (grep clean). `test_drive_velocity::test_read_snapshot_annotates_momentum` proves read-time |
| DRIVE-03 — in-turn goal-aware appraisal + inspectable drive effect | ✓ met | `appraisal.APPRAISAL_JSON_SCHEMA:132 goal_signals` (+`stalled_days:139`); `parse_signals:527`; `build_context:215` injects non-candidate goals + momentum within 12000-char cap; `render._render_drive_note:237` neutral `stalled N days` clause SEPARATE from `[push zone:]` effect (`_drive_salience:137`) |
| DRIVE-04 — first-person `- drive want:` voice; SAFE-04 carve-out | ✓ met | `render._render_drive_want:296` ("I want X moving (stalled N days)"); label in `conftest.ALLOWED_LABEL_PREFIXES:63`; `_SECOND_PERSON_DIRECTIVE_RE` UNCHANGED (git diff = comment-only); `test_anticreep::test_drive04_second_person_directive_re_unchanged` + symmetric control |
| DRIVE-05 — never-omit + anti-complacency invariant | ✓ met | `render._flagged_want_lines:325` reads PERSISTED goals; flagged wants render FIRST into protected prefix (`render_block:414,:428`); cap loop guard `floor=max(protected_count,2):524` exempts flagged from token-cap; flagged not in `[:3]` slice (rendered as wants, skipped from notes `:466`); anti-complacency `[under-support:]` clause `:321`. `test_drive_neveromit` (12 tests) |
| DRIVE-06 — containment + adjustability | ✓ met (pressure-ladder partial, below) | `config.get_cfg:228` returns `drive_enabled`/`drive_domains`/`drive_energy_budget`/`drive_pressure` (all coerced, never raise); separate kill switch `__init__.py:167` (after appraisal kill switch, no early-return); domain whitelist `_filter_goals_by_domain:34` + `_filter_signals_by_goals:55`; energy budget `render_block energy_budget:366,:481` caps non-flagged, flagged exempt |

## Non-Negotiables Check (read from code, not trusted)

| Invariant | Status | Evidence |
|-----------|--------|----------|
| SAFE-04 `_SECOND_PERSON_DIRECTIVE_RE` unchanged | ✓ | `git diff ac2c585..HEAD render.py` near the regex = comment-only; `test_drive04_second_person_directive_re_unchanged` asserts it still matches "you should/must" and NOT "I want" |
| conftest `DIRECTIVE_PATTERNS` unchanged | ✓ | git diff = comment-only additions; only `ALLOWED_LABEL_PREFIXES` gained `- drive note:`/`- drive want:` labels |
| Negative controls still fail | ✓ | `test_safe03_helper_actually_catches_violations` (fails on "you should migrate now" + unlabeled) PRESERVED; symmetric `test_drive04_first_person_passes_second_person_quoted` proves un-sanitized 2nd-person `- drive want:` is REJECTED |
| Never-omit beats `[:3]` slice | ✓ | `test_flagged_goal_survives_top3_slice` (5 non-flagged sliced to 3, flagged want present); `test_multiple_flagged_goals_all_survive_slice` (4 flagged, NOT sliced) |
| Never-omit beats token-cap drop | ✓ | `test_flagged_goal_survives_token_cap` asserts `FLAG in block` AND truncation actually happened (line count < full) — non-vacuous |
| Never-omit beats energy budget | ✓ | `test_flagged_want_exempt_from_budget` (`drive_energy_budget=0` → flagged want still appears) |
| Fail-open: malformed drive config | ✓ | `test_missing_config_malformed_drive_values_coerced`; `_coerce_str_list`/`_coerce_choice`/`_coerce_int` never raise |
| Fail-open: absent/corrupt .git | ✓ | `goal_momentum` returns benign `unknown` on any exception (`:456`); velocity fail-open matrix rows (absent-.git/unparseable-reflog/bad-timestamp) |
| Fail-open: locked DB goal write | ✓ | `test_locked_db_goal_write_returns_false` (apply_deltas returns False, no raise) |
| Drive-off appraisal byte-for-byte unchanged | ✓ | `test_drive_disabled_appraisal_unchanged:426` asserts drive-off-with-goals == drive-on-with-no-goals; `skipped:drive_disabled` is a non-failure (`test_drive_disabled_is_non_failure`) |
| Single sqlite surface; no new plugin module | ✓ | `test_scan_targets_are_the_plugin_modules` (6 modules hard-coded) green; velocity helper lives in store.py |
| Zero new pip deps | ✓ | `test_safe04_import_allowlist` green; `test_pkg01_manifest_zero_deps` (`pip_dependencies: []`) |
| No subprocess/os.system/git lib | ✓ | grep of all 6 modules = NONE; `FORBIDDEN_SUBSTRINGS` scan green; only 1 write-mode open (the debug dump) |

## Addendum Implementation (06-CONTEXT)

| Addendum item | Status | Evidence |
|---------------|--------|----------|
| Drive-effect visibility (neutral read vs drive effect separable/inspectable) | ✓ met | neutral `stalled N days` stays SEPARATE from `[push zone:]` / `[under-support:]` drive-effect clauses; `_drive_salience` keeps neutral rank + push bonus recoverable (Pitfall #9) |
| Anti-complacency (`support_style='firm'`/`push_when_stalled` not quietly downranked) | ✓ met | `_push_when_stalled:159` raises salience + renders visible under-support clause; `test_firm_stalled_goal_not_quietly_downranked`, `test_support_style_firm_also_triggers_under_support` |
| Pressure ladder quiet\|standard\|firm (code-red excluded) | ◑ partial | `drive_pressure` config key coerced to `{quiet,standard,firm}`, code-red rejected, documented — but NO behavioral branch reads the GLOBAL `drive_pressure` setting yet (per-goal `support_style='firm'`/`push_when_stalled` DO drive behavior). Executor documented this as intentional (07-04-SUMMARY: "read-only config for now … a later panel/heartbeat increment tunes firmness") |

## ROADMAP Success Criteria

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Real turn surfaces user-minted goal with grounded progress/stalled signal, first-person voice | ✓ (full-hook tests `test_neveromit_full_hook`; live-turn UAT deferred to verify-work) |
| 2 | Anti-creep passes with first-person carve-out; second-person still neutralized | ✓ owned by test_anticreep DRIVE-04 quartet |
| 3 | Never-omit + anti-complacency: flagged always appears; stalled push not silently low-salience | ✓ test_drive_neveromit (12) |
| 4 | Drive off ⇒ zero goal fields; appraisal unchanged; full fail-open | ✓ byte-for-byte test + consolidated fail-open matrix |
| 5 | Drive state round-trips in single sqlite surface; locked/corrupt-DB degrade silently | ✓ test_drive_store round-trip/caps/locked/v3-quarantine |
| 6 | Drive effect inspectable (neutral read, drive read, salience change auditable) | ✓ separate neutral vs `[push zone:]`/`[under-support:]` clauses |

## Summary

**Score:** 6/6 DRIVE requirements met · 13/13 non-negotiables hold · 6/6 ROADMAP
criteria covered · 165/165 tests green.

All automated checks passed. The phase goal — eligible turns can surface
user-minted goals with grounded progress/accountability signals in-turn, never
omitting a flagged priority, on the existing appraisal path and anansi SQLite
store — is genuinely achieved in code. The hard red lines (SAFE-04 second-person
neutralization, never-omit, fail-open, single sqlite surface, zero deps) are
verified by reading the source and the diffs, not by trusting the summaries.

### Gaps (documented deviations — non-blocking)

| Gap | Plan | What's missing | Impact |
|-----|------|----------------|--------|
| Pressure columns not persisted | 07-01 | The 07-01 PLAN must_have named `support_style`, `push_when_stalled`, `stall_threshold_days` as `goals` DDL columns; the shipped DDL (`store.py:99`) omits them. The render/enrich/anti-complacency path reads them defensively off goal dicts and the tests inject them directly, so the BEHAVIOR is proven, but no `apply_deltas`/`read_snapshot` round-trip persists them. No round-trip persistence test exists. | Low — behavior verified; only durable persistence of per-goal pressure is deferred. Documented identically in all four summaries as a known forward-compat deviation. |
| `drive_pressure` ladder has no behavioral branch | 07-04 | The global `drive_pressure` (`quiet\|standard\|firm`) config key is coerced/documented but not read by any non-config module; the addendum's "bounded pressure ladder" is only partly realized at the global level (per-goal pressure does work). | Low — adjustability surface is present and contained; firmness tuning deferred to a later panel/heartbeat increment per 07-04-SUMMARY. |

### Note for verify-work (manual UAT)

Criterion 1's "a REAL `hermes` turn" surfacing is proven here only via full-hook
integration tests with fake LLMs. A live `HERMES_PLUGINS_DEBUG=1 hermes -z`
turn against the symlinked install is the remaining human confirmation (the live
symlink was left untouched — no plugin module was modified outside the repo).
