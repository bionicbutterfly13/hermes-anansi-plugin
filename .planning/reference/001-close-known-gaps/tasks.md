---
description: "Task list for Anansi Completion — Close Known Gaps"
---

# Tasks: Anansi Completion — Close Known Gaps

**Input**: Design documents from `.planning/reference/001-close-known-gaps/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md,
`.planning/reference/CONSTITUTION.md`

**Tests**: INCLUDED — the spec requires each vertical to ship code + tests, and the constitution makes the
fail-open matrix + never-omit tests release gates.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different file, no dependency on an incomplete task)
- **[US#]**: The user story / gap this task serves

**File-conflict rule (why so little [P])**: the gaps cluster in a few files. `store.py` → US1(G2)+US3(G7);
`render.py` → US2(G3)+US4(G4)+US5(G5)+US6(G6); `config.py` → US3+US4; `__init__.py` → US2+US3. Tasks
touching the same file are SEQUENTIAL. Only genuinely disjoint work (US8 rename, US7 docs) is `[P]`.

**Global acceptance check on every task**: `./scripts/test.sh` stays green, including `test_anticreep.py`
(forbidden-substrings, import allowlist, single write-open, label prefixes), `test_failopen_matrix.py`, and
`test_drive_neveromit.py`. No existing assertion may be weakened.

---

## Phase 1: Setup

- [x] T001 Create feature branch `001-close-known-gaps` from `main` (`git switch -c 001-close-known-gaps`).
- [x] T002 Baseline: run `./scripts/test.sh` and record the current pass count (expected 165) so any later regression is visible.

---

## Phase 2: US1 — Persist per-goal pressure (G2, P1) 🎯 MVP

**Goal**: `support_style` / `push_when_stalled` / `stall_threshold_days` round-trip the store; existing
goals survive the upgrade. **Independent test**: write a goal with the three fields, read it back in a
fresh snapshot, assert equality; upgrade a v4 DB and assert existing rows survive.

- [x] T003 [US1] Add the three columns to the `goals` DDL and bump `SCHEMA_VERSION` 4→5 in `anansi/store.py` (DDL at store.py:99-103, version at store.py:35), per contracts/store-goals-schema.md.
- [x] T004 [US1] Persist the three fields in the `goals_add` INSERT (store.py:714-735) and `goals_update` SET (store.py:736-751), reading via `item.get(...)` with defaults (push_when_stalled default 0).
- [x] T005 [US1] Add the fail-open additive-migration branch in `ensure_db` (store.py:238-242): on a structurally-valid v4 DB, run `ALTER TABLE goals ADD COLUMN ...` ×3 + `UPDATE meta` to '5', wrapped in try/except that falls through to `_quarantine` + `_create_fresh` on any error. `ensure_db` MUST still never raise.
- [x] T006 [US1] Tests in `anansi/tests/test_drive_store.py`: (a) round-trip the three fields; (b) v4→v5 upgrade PRESERVES existing goal rows with new columns defaulted (mirror `test_v3_db_quarantine_recreates_at_v4:118-138` but assert survival); (c) `test_locked_db_goal_write_returns_false` still green with the new INSERT columns.
- [x] T007 [US1] Acceptance: `./scripts/test.sh anansi/tests/test_drive_store.py` green; fail-open (locked/corrupt DB) preserved; single SQLite surface unchanged; no anti-creep violation. Then full-suite spot check.

---

## Phase 3: US2 — Wire global drive_pressure (G3, P1)

**Goal**: `drive_pressure` (quiet/standard/firm) visibly modulates the drive block; `standard` reproduces
today's output. **Independent test**: render identical state at each level, assert distinguishable output
and byte-identical literal strings.

- [x] T008 [US2] Thread a `pressure` param into `render_block` and modulate `note_limit` (render.py:481-487) + the salience bonus in `_drive_salience` (render.py:137-156) ONLY — never touch the literal want/note strings, the neutral `stalled N days` clause, or the `[under-support:]`/`[push zone:]` effect text. `standard` == current behavior.
- [x] T009 [US2] Wire the value through in `anansi/__init__.py`: pass `get_cfg()["drive_pressure"]` into `render_block(pressure=...)`.
- [x] T010 [US2] Tests in `anansi/tests/test_drive_config.py` (+ velocity fixtures): quiet/standard/firm produce distinguishable blocks on identical state; assert `standard` matches the pre-change render byte-for-byte; assert no directive language introduced (`assert_no_directive_language`).
- [x] T011 [US2] Acceptance: `./scripts/test.sh anansi/tests/test_drive_config.py anansi/tests/test_drive_velocity.py` green; constitution Principle II (salience/ordering/verbosity only) upheld; drive-off byte-for-byte identity preserved.

---

## Phase 4: US3 — Config-degradation telemetry (G7, P1)

**Goal**: one legible, secret-safe `config_degraded` telemetry row per coerced-away config value; zero
rows when config is valid. **Independent test**: feed malformed keys, assert one row each with redacted
value; valid config → none.

- [x] T012 [US3] In `anansi/config.py` `get_cfg` (config.py:189-242), after building the cache, collect degradations (raw `entry.get(key)` present AND != coerced value) into a secret-safe list: `(key, applied_default, shape)` where shape is `<str len=N>` / `<redacted>` — NEVER the literal value. Expose via a private cfg entry or module accessor. Do NOT import `store` in config.py.
- [x] T013 [US3] Add `"config_degraded"` to the non-failure exclusion set in `telemetry_summary` (`anansi/store.py:897-909`) and its docstring (store.py:876-882).
- [x] T014 [US3] In `anansi/__init__.py`, on session-start / config force-reload (has `session_id`), emit one `record_telemetry("config_degraded", error="<key>: rejected <shape>, applied <default>", ...)` per degradation. Guard against per-turn re-emission. Fail-open: must not raise or block if telemetry store is locked.
- [x] T015 [US3] Tests: in `anansi/tests/test_telemetry_store.py` assert `config_degraded` is a non-failure in `telemetry_summary` (mirror reflect-vocabulary test :196-218 and `test_drive_disabled_is_non_failure` :433-449); in `test_drive_config.py` assert one row per malformed key and that the rejected literal is NOT in the stored `error` text; valid config → zero rows.
- [x] T016 [US3] Update the hardcoded expected cfg dict in `test_get_cfg_defaults_when_host_config_unavailable` (test_telemetry_store.py:240-258) and the pinned cfg in `test_failopen_matrix.py:143` if the cfg dict shape changed.
- [x] T017 [US3] Acceptance: `./scripts/test.sh anansi/tests/test_telemetry_store.py anansi/tests/test_drive_config.py` green; fail-open preserved; no secret leaked to telemetry; new outcome classified non-failure.

---

## Phase 5: US4 — Bound flagged wants (G4, P2)

**Goal**: at most `drive_flagged_want_cap` flagged wants render (top priority always kept) + a visible
`[N flagged priorities withheld]` marker; never-omit preserved. **Independent test**: >cap flagged goals →
top present + marker; ≤cap → all present, no marker.

- [x] T018 [US4] Add config key `drive_flagged_want_cap` (default 5, floor 1 via `_coerce_int(v,5,lo=1)`) in `anansi/config.py`; add it to the pinned cfg dicts (test_telemetry_store.py:240-258, test_failopen_matrix.py:143).
- [x] T019 [US4] In `_flagged_want_lines` (`anansi/render.py:325-362`): sort flagged goals by `int(flagged_priority)` desc → momentum/stalled_days → persisted order; cap to `cap` lines always keeping index 0; append synthetic `- drive want: [N flagged priorities withheld]` when exceeded. Keep dedup/skip consistent with `flagged_goal_texts` (render.py:418-422) and the drive-note skip (render.py:468-472) so a withheld goal can't reappear as a note. Marker lands in the protected prefix.
- [x] T020 [US4] Tests in `anansi/tests/test_drive_neveromit.py`: >cap flagged → top-priority want present + withheld marker present, both inside the protected prefix (not dropped by slice/budget/token-cap); `test_multiple_flagged_goals_all_survive_slice` (4 flagged, default cap 5) still shows all 4; assert the marker uses an allowed label and passes `assert_no_directive_language`.
- [x] T021 [US4] Acceptance: `./scripts/test.sh anansi/tests/test_drive_neveromit.py` green; Principle III never-omit intact (top flagged always present, withholding is VISIBLE not silent); reads persisted goals not model output.

---

## Phase 6: US5 — Precise goal↔signal matching (G5, P2)

**Goal**: no false-positive associations from loose substring; legitimate matches preserved.
**Independent test**: substring-only pairs no longer match; true pairs still match.

- [x] T022 [US5] Replace the three bidirectional substring matches in `anansi/render.py` (:194-195, :353-354, :468-471) with normalized matching (lower/strip/collapse-ws/strip-punct, then full-string equality OR whole-word-token containment). Apply the SAME normalization at all three sites (keep-in-sync, Principle #9).
- [x] T023 [US5] Tests in `anansi/tests/test_drive_velocity.py`: false-positive pairs (e.g. "ship"/"relationship", "api"/"therapist") no longer associate; the existing `enrich_goal_signals` grounding pairs (:251-276) still match.
- [x] T024 [US5] Acceptance: `./scripts/test.sh anansi/tests/test_drive_velocity.py` green; matching precise; no legitimate association lost.

---

## Phase 7: US6 — stalled_days == 0 reads as moving (G6, P2)

**Goal**: a 0-day goal renders fresh/active, ranks moving, emits no "stalled 0 days" clause.
**Independent test**: render `stalled_days=0` → active read, no stalled clause, moving rank.

- [x] T025 [US6] Change the three gates in `anansi/render.py` from `isinstance(stalled_days, int)` to `isinstance(stalled_days, int) and stalled_days > 0`: `_drive_salience` (:145), `_render_drive_note` (:246-247), `_render_drive_want` (:314).
- [x] T026 [US6] Tests in `anansi/tests/test_drive_velocity.py`: a `stalled_days=0` goal renders active (no "stalled" substring, mirrors moving-goal assertion :184-209) and does not receive the push bonus; a genuinely stalled goal (>0) still renders "stalled N days".
- [x] T027 [US6] Acceptance: `./scripts/test.sh anansi/tests/test_drive_velocity.py` green; velocity ordering + neutral-read inspectability preserved.

---

## Phase 8: US7 — Live Criterion-1 closure lane (G1, P3)

**Goal**: documented one-command lane + honest gated outcome; run when a provider is reachable.
**Independent test**: the command reports PASS/FAIL/INCONCLUSIVE honestly.

- [x] T028 [P] [US7] Document the live-smoke closure lane in `.planning/reference/001-close-known-gaps/quickstart.md` (already drafted) and in the plugin README: exact command `$HERMES_HOME/hermes-agent/venv/bin/python scripts/live_drive_smoke.py`, env gate (HERMES_HOME, api.anthropic.com:443, host creds), exit codes 0/1/2. No harness code change.
- [ ] T029 [US7] When a model provider is reachable (openrouter billing restored OR `hermes auth` for nous), run the command; record PASS (exit 0) to close Criterion 1, or the honest INCONCLUSIVE reason. (Environment-gated — may remain open at ship with the lane ready.)

---

## Phase 9: US8 — Rename "master kill switch" (G8, P3)

- [x] T030 [P] [US8] Rename `test_master_kill_switch_disables_reflection` → `test_primary_kill_switch_disables_reflection` in `anansi/tests/test_reflection.py:518`. Leave all `sqlite_master` and `refs/heads/master` occurrences untouched. No runtime change.
- [x] T031 [US8] Acceptance: `./scripts/test.sh anansi/tests/test_reflection.py` green; grep confirms no other "master" token changed.

---

## Phase 10: Polish & Cross-Cutting

- [x] T032 Run the FULL suite: `./scripts/test.sh`. Assert green and pass count ≥ baseline (T002); confirm the anti-creep, fail-open matrix, and never-omit suites all pass with no weakened assertion.
- [x] T033 Add a dated `CHANGELOG.md` entry (Features / Fixes / Learnings) covering G1–G8, including the G2 anti-erasure migration decision (ALTER over quarantine) and its rationale.
- [x] T034 Update `anansi/README.md` config reference for the new `drive_flagged_want_cap` key and the now-live `drive_pressure` behavior.

---

## Dependencies & Execution Order

- **Setup (T001–T002)** first.
- **US1 (G2)** is the MVP and the store-schema foundation — do it first among the stories.
- **Same-file chains (sequential)**: store.py → US1 then US3(T013); render.py → US2 → US4 → US5 → US6;
  config.py → US3(T012) then US4(T018); __init__.py → US2(T009) then US3(T014).
- **Parallel [P]**: T028 (docs), T030 (rename) — disjoint from the code chains.
- **Polish (T032–T034)** last, after all stories land.

## Implementation Strategy

- **MVP = US1 (G2)** — persisted pressure is the headline completeness fix and unblocks nothing downstream
  but proves the migration approach. Ship + verify it first.
- Then P1 remainder (US2, US3), then P2 (US4–US6), then P3 (US7–US8), then polish.
- Verify each story with its targeted `./scripts/test.sh <file>` before moving on (Principle #7: one thing
  at a time, verify, next).

## Parallel Example

```
# After the render.py chain is done, these are safe together (different files):
T028 [P] docs closure lane   (quickstart.md + README)
T030 [P] rename test         (test_reflection.py)
```
