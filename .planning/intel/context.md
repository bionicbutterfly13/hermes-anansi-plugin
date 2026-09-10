## Anansi — Remaining Promise Backlog (spec index)
- source: specs/BACKLOG.md
- content:
````text
DATA_G7I9K1M3_START
# Anansi — Remaining Promise Backlog (spec index)

Every promised-but-unbuilt or unverified item for the anansi plugin, captured as Spec Kit specs so
nothing is lost. Sourced from the `.planning/` archive (Phase 6 design, Phase 7 verification/UAT/learnings,
DECISIONS, HANDOFF, ROADMAP, research/) and cross-checked against `anansi/` code on 2026-07-05.

**Excluded on purpose:** the 16 anti-features (deliberate never-builds — heartbeat-as-daemon-without-user-turn,
outreach, privilege ladder, agent-dopamine, Postgres/AGE/RabbitMQ/Ollama/UI, memory-provider slot, tool
execution, directive language, turn gating, memory-provider writes, self-modifying prompts, unbounded state,
mood-driven output modulation, multi-call chains, `sys.path` mutation). Those stay unbuilt by design.
**Out of anansi scope:** graphify issue #1320 (separate repo); Hindsight-retain / memory-os-sync / L3
stack-health follow-ups (host-stack, not the plugin).

## Agreed sequencing (from 06-CONTEXT.md:93-94, 06-DISCUSSION-LOG.md:54-55)

Drive/accountability (Phase 7 — DONE) → **worldview store → episode/autobiography + user-dopamine →
reconsolidation**. The **scheduled heartbeat** is introduced in the increment that first needs between-session
work (reconsolidation). Interruption lanes (proactive-notify L2, code-red) and the desktop config panel come
after, each gated on its own precondition.

## Specs

| Spec | Covers | Sequencing |
|------|--------|-----------|
| [001-close-known-gaps](001-close-known-gaps/spec.md) | G1–G8 Phase-7 gap closure (DONE except G1 live run) | current |
| [002-autobiographical-user-model](002-autobiographical-user-model/spec.md) | Worldview store · episode/autobiography · user-dopamine · the 5-layer model | next (P1 = worldview) |
| [003-reconsolidation-and-heartbeat](003-reconsolidation-and-heartbeat/spec.md) | Belief-flip reconsolidation + the scheduled heartbeat it requires | after 002 |
| [004-interruption-lanes](004-interruption-lanes/spec.md) | Proactive-notify L2 · code-red interruption lane | after heartbeat; each gated |
| [005-tuning-and-audit-surfaces](005-tuning-and-audit-surfaces/spec.md) | Desktop config panel · multi-session under-response audit · passive outbox | after heartbeat |
| [006-deferred-v1-and-parity](006-deferred-v1-and-parity/spec.md) | D3/D5/D6 depth · upstream `post_memory_prefetch` hook · upstream-main parity re-verify · WAL-on-netmount caveat · aux-model routing · parked direct-Hindsight recall | opportunistic |
| [007-drive-security-verification](007-drive-security-verification/spec.md) | The missing `07-SECURITY.md` — STRIDE for the drive layer; live APPR-06 trust-fallback verification | any time |

## Canonical design references (read before planning any of these)

- `.planning/phases/06-proprietary-user-model-drive-design/06-CONTEXT.md`
- `.planning/phases/06-proprietary-user-model-drive-design/06-DISCUSSION-LOG.md`
- `.planning/research/DESIGN-REWIND-2026-06-10.md`
- `.planning/research/USER-MODEL-SOURCES-2026-06-10.md`
- `.planning/research/MEMORY-STACK-ANALYSIS-2026-06-10.md`
- `.specify/memory/constitution.md` (governs all of the above)
DATA_G7I9K1M3_END
````

## Quickstart — Validate the Gap Closure
- source: specs/001-close-known-gaps/quickstart.md
- content:
````text
DATA_H8J0L2N4_START
# Quickstart — Validate the Gap Closure

Canonical test gate (whole suite): `./scripts/test.sh` — runs the hermes venv python `-m pytest -q` over
`anansi/tests` (venv never modified).

Run a single slice's tests, e.g.: `./scripts/test.sh anansi/tests/test_drive_store.py -q`.

## Per-slice validation

| Gap | What to run | Expected |
|-----|-------------|----------|
| G2 persist pressure | `./scripts/test.sh anansi/tests/test_drive_store.py` | Goal round-trips `support_style`/`push_when_stalled`/`stall_threshold_days`; v4→v5 upgrade PRESERVES existing goal rows; locked-DB write still returns False |
| G3 drive_pressure | `./scripts/test.sh anansi/tests/test_drive_config.py anansi/tests/test_drive_velocity.py` | `quiet`/`standard`/`firm` produce distinguishable blocks on identical state; literal strings unchanged; `standard` == today |
| G7 config telemetry | `./scripts/test.sh anansi/tests/test_telemetry_store.py anansi/tests/test_drive_config.py` | Malformed key → one `config_degraded` row (non-failure), rejected value NOT quoted; valid config → zero rows |
| G4 flagged cap | `./scripts/test.sh anansi/tests/test_drive_neveromit.py` | >cap flagged goals → top-priority present + `[N flagged priorities withheld]` marker; existing all-survive test (≤cap) still green |
| G5 matching | `./scripts/test.sh anansi/tests/test_drive_velocity.py` | Substring false-positives dropped; legitimate goal↔signal matches still fire |
| G6 stalled 0 | `./scripts/test.sh anansi/tests/test_drive_velocity.py` | `stalled_days=0` renders fresh/active, ranks moving, no "stalled 0 days" clause |
| G8 rename | `./scripts/test.sh anansi/tests/test_reflection.py` | `test_primary_kill_switch_disables_reflection` passes; no other "master" token changed |

## Full-suite gate (all constitution invariants)

```
./scripts/test.sh
```
Must be green including `test_anticreep.py` (forbidden-substrings, import allowlist, single write-open,
label prefixes), `test_failopen_matrix.py`, and `test_drive_neveromit.py`. No assertion may be weakened
relative to the pre-change suite.

## G1 — Live Criterion-1 (environment-gated)

One command, no args:

```
$HERMES_HOME/hermes-agent/venv/bin/python scripts/live_drive_smoke.py
```

Requires: `HERMES_HOME` set, network egress to `api.anthropic.com:443`, host LLM creds configured.

Exit codes: `0` PASS (real turn surfaced the first-person `- drive want:` line), `1` FAIL (block rendered
but want missing, or a second-person directive leaked), `2` INCONCLUSIVE (network down or trust-gate/no
signals — an environment condition, not a code defect). Currently INCONCLUSIVE due to provider outage
(openrouter billing + nous auth); re-run when a provider is reachable to close Criterion 1.
DATA_H8J0L2N4_END
````

## Specification Quality Checklist: Anansi Completion — Close Known Gaps
- source: specs/001-close-known-gaps/checklists/requirements.md
- content:
````text
DATA_I9K1M3O5_START
# Specification Quality Checklist: Anansi Completion — Close Known Gaps

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-07-05
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- This is brownfield finishing work on an existing plugin. A few named entities (the single SQLite
  store, the `drive_pressure` config key, per-goal pressure fields, the `stalled_days` derivation) appear
  in the spec because they ARE the feature's contract — the gaps are defined relative to existing,
  documented surfaces. This is intentional and keeps each requirement testable; it does not introduce
  new implementation prescriptions (no languages/frameworks/algorithms dictated).
- SC-006 names `./scripts/test.sh` because it is the project's canonical verification gate; the outcome
  (green suite, unweakened assertions) is the measurable target, not the tool.
- No [NEEDS CLARIFICATION] markers: the eight gaps (G1–G8) were sourced directly from the phase-7
  verification, UAT, and review artifacts, so scope is fully determined.
- Ready for `/speckit-plan` (or `/speckit-clarify` if deeper de-risking is wanted first).
DATA_I9K1M3O5_END
````

## Phase 0 Research — Close Known Gaps
- source: specs/001-close-known-gaps/research.md
- content:
````text
DATA_J0L2N4P6_START
# Phase 0 Research — Close Known Gaps

Every decision below is anchored to current code (file:line). No NEEDS CLARIFICATION remain.

## G2 — Persist per-goal pressure

**Decision**: Add `support_style TEXT`, `push_when_stalled INTEGER NOT NULL DEFAULT 0`,
`stall_threshold_days INTEGER` to the `goals` DDL (`store.py:99-103`); bump `SCHEMA_VERSION` 4→5
(`store.py:35`); persist the three fields in `goals_add` (`store.py:714-735`) and `goals_update`
(`store.py:736-751`). `_rows_as_dicts` (`SELECT *`, `store.py:249-252`) surfaces them into the snapshot
goal dict automatically, so the render path's `goal.get("support_style")` resolves once columns exist.

**Migration — additive ALTER, not quarantine**: The module doctrine (`store.py:16-19`) quarantines and
recreates on any version mismatch, which *discards existing goal rows*. Because goals are user-minted and
may be flagged priorities, discarding them violates Principle III. Add an upgrade branch in `ensure_db`
(between the `_verify_structure` success and the quarantine call, `store.py:238-242`): when the DB is
otherwise valid but at v4, run `ALTER TABLE goals ADD COLUMN ...` for each new column inside a
`try/except` that, on any failure, falls through to the existing `_quarantine` + `_create_fresh`. This
keeps `ensure_db` fail-open (never raises) AND preserves user goals on the happy path.

**Rationale**: SQLite `ALTER ADD COLUMN` is non-destructive; new columns are nullable / defaulted, so
pre-existing rows read documented defaults. **Alternatives considered**: (a) pure quarantine-recreate —
rejected (erases user priorities); (b) `PRAGMA user_version` migration framework — rejected (over-build;
the codebase has no such framework and one bump doesn't justify it).

**Fail-open to preserve**: `apply_deltas` write guard (`store.py:627-815`, returns False on lock — test
`test_locked_db_goal_write_returns_false`), `read_snapshot` ro-connection guard (`store.py:492-561`),
`_verify_structure` (`store.py:169-197`). Mirror `test_v3_db_quarantine_recreates_at_v4`
(`test_drive_store.py:118-138`) for a v4→v5 test, PLUS a new test asserting existing goal rows survive the
ALTER upgrade with the new columns defaulted.

## G3 — Wire global `drive_pressure`

**Decision**: Thread a `pressure` argument into `render_block` (already receives `energy_budget`) sourced
from `get_cfg()["drive_pressure"]` in `__init__.py`. Map the level to two existing, text-neutral levers:
`note_limit` verbosity (`render.py:481-487`) and a salience bonus in `_drive_salience` (`render.py:137-156`,
analogous to `_PUSH_SALIENCE_BONUS`). `quiet` → fewer notes / smaller bonus; `firm` → up to the existing
max / larger bonus; `standard` → today's behavior unchanged.

**Rationale**: config already defines + coerces the key (`config.py:89-90, 237-240`, default `standard`,
choices `{quiet,standard,firm}`) — it is only unread. **Hard constraint**: pressure MUST NOT touch the
imperative-free literal strings in `_render_drive_want`/`_render_drive_note` (constitution: salience/
ordering/verbosity only, never imperative loudness). The neutral `stalled N days` clause and the
`[under-support: ...]`/`[push zone: ...]` effects stay byte-identical across levels.

**Alternatives considered**: adding a new pressure vocabulary — rejected (`code-red` is deliberately
excluded, `config.py:52-54`; keep the three).

## G7 — Config-degradation telemetry

**Decision**: `get_cfg` (`config.py:189-242`) is the only scope holding both the raw `entry.get(key)` and
the coerced value. After building the cache, collect a list of degradations (key, applied default, and a
secret-safe shape indicator of the rejected value) where raw != coerced and raw is not None/absent. Expose
that list via the cfg dict (a private `_degradations` entry) or a module accessor. Emit one
`record_telemetry("config_degraded", error="<key>: rejected <shape>, applied <default>", ...)` row per
degradation from `__init__.py` on session-start / force-reload (the path that has a `session_id` and
already calls `record_telemetry`) — NOT from inside `config.py` (which does not import `store` and must
stay standalone-importable).

**Non-failure classification**: add `"config_degraded"` to the non-failure exclusion set in
`telemetry_summary` (`store.py:897-909`) and its docstring (`store.py:876-882`), else the exclusion-list
logic counts it as a failure. Mirror `test_drive_disabled_is_non_failure` (`test_failopen_matrix.py:433-449`)
and the reflect-vocabulary test (`test_telemetry_store.py:196-218`).

**Secret-safety**: no credential-aware redactor exists (`render._sanitize_text`, `render.py:86`, is
injection-focused, not secret-aware). Therefore DO NOT quote the rejected value — emit a shape indicator
(`<str len=N>` / `<redacted>`), so a mistyped credential is never written to telemetry. Fail-open:
`record_telemetry` already never raises (`store.py:859-862`); emitting must not block the turn.

**Re-emission guard**: emit only on config (re)load, not every turn, so a persistently-degraded config
doesn't spam telemetry each `pre_llm_call`.

## G4 — Bound flagged wants

**Decision**: In `_flagged_want_lines` (`render.py:325-362`) sort the flagged `plist` by
`int(goal.get("flagged_priority"))` descending (magnitude is currently read but unused as a sort key,
`render.py:256-265`), then by momentum/`stalled_days`, then persisted order for stability. Emit at most
`k` want lines (`k` = new config key `drive_flagged_want_cap`, default 5, floor 1), ALWAYS keeping index 0
(top priority). If more than `k` flagged goals exist, append a synthetic
`"- drive want: [N flagged priorities withheld]"` marker line. The whole list lands in the protected
prefix (`render.py:425`, counted by `protected_count` at `:428`), so the top wants and the marker are
never dropped by the `[:3]` slice, the energy budget, or the token cap.

**Rationale**: today flagged wants are unbounded (only the soft token cap, which is itself flagged-exempt).
A visible, priority-ordered cap protects both Principle III (top flagged always shown; withholding is
explicit, not silent) and readability. **Constraint**: keep dedup/skip consistent with `flagged_goal_texts`
(`render.py:418-422`) and the drive-note skip (`render.py:468-472`) so a withheld flagged goal cannot
reappear as a third-person note. **Must keep green**: `test_multiple_flagged_goals_all_survive_slice`
adapts — with default cap 5 and 4 flagged goals it still shows all 4; add a new test with >5 flagged
proving top-priority present + withheld marker.

**Alternatives considered**: no cap (status quo) — rejected (unbounded crowding); dropping lowest silently
— rejected (violates "withholding must be visible").

## G5 — Precise goal↔signal matching

**Decision**: Replace the three bidirectional substring matches (`render.py:194-195`, `:353-354`,
`:468-471`) with normalized matching: lowercase, strip, collapse internal whitespace, strip surrounding
punctuation, then require full-string equality OR whole-word-token containment (token-subset) — not raw
`in`. This drops false positives ("ship" ⊄ "relationship", "api" ⊄ "therapist") while keeping legitimate
associations.

**Rationale**: goals carry an integer `id` (PK) but only `text` is threaded into signal matching today;
id-equality would be strongest but requires threading the id through `goal_signals` — larger surface.
Normalized whole-word equality is the minimal-surgical fix (Principle VII) that removes the defect.
**Alternatives considered**: thread goal `id` end-to-end — deferred as heavier; revisit if normalized
matching proves insufficient. **Must keep green**: velocity grounding tests (`enrich_goal_signals`,
`test_drive_velocity.py:251-276`) — legitimate matches must still fire.

## G6 — `stalled_days == 0` reads as moving

**Decision**: Change the three `isinstance(stalled_days, int)` gates to `isinstance(stalled_days, int) and
stalled_days > 0`: `_drive_salience` (`render.py:145`), `_render_drive_note` (`render.py:246-247`),
`_render_drive_want` (`render.py:314`). A goal touched today (`stalled_days == 0`) then renders as fresh/
active, ranks as `moving` (not `stalled` rank 2), and never emits a "stalled 0 days" clause or a spurious
push bonus.

**Rationale**: `_coerce_stalled_days` (`appraisal.py:439-448`) legitimately retains 0, but a model-echoed
`stalled_days: 0` currently hits the stalled branch. **Must keep green**: `test_drive_velocity.py:184-209`
asserts `"stalled" not in` a moving goal's note — the fix makes a 0-day goal satisfy that.

## G1 — Live Criterion-1 closure lane

**Decision**: No code change to the harness — `scripts/live_drive_smoke.py` already returns honest exit
codes (0 PASS / 1 FAIL / 2 INCONCLUSIVE, `:32`, `:54-57`, `:107-111`). Deliverable: document the exact
one-command re-run and the env gate in `quickstart.md` and the README, and run it once a provider is
reachable. Invocation: `$HERMES_HOME/hermes-agent/venv/bin/python scripts/live_drive_smoke.py` (no args;
needs `HERMES_HOME`, egress to `api.anthropic.com:443`, host LLM creds). It is currently INCONCLUSIVE due
to provider outage (openrouter billing + nous auth), not a code defect.

**Rationale**: the surfacing logic is proven offline (full-hook never-omit tests); only the live confirm is
outstanding and is environment-gated. **Alternatives considered**: mocking a live turn — rejected (would
not close a *live* acceptance criterion honestly).

## G8 — Rename "master kill switch"

**Decision**: Rename only `test_master_kill_switch_disables_reflection` →
`test_primary_kill_switch_disables_reflection` (`test_reflection.py:518`). Leave every other "master"
occurrence untouched: `sqlite_master` (system table) at `store.py:180` + several tests, and
`refs/heads/master` (git ref) at `test_drive_velocity.py:29`. No runtime branch uses the word "master"
(kill switch reads `cfg.get("enabled")`, `__init__.py:157,161-162`).

**Rationale**: pure clarity; zero behavior change. **Alternatives considered**: renaming all "master"
tokens — rejected (breaks SQL and a git-ref string).
DATA_J0L2N4P6_END
````

## Tasks: Anansi Completion — Close Known Gaps
- source: specs/001-close-known-gaps/tasks.md
- content:
````text
DATA_K1M3O5Q7_START
---
description: "Task list for Anansi Completion — Close Known Gaps"
---

# Tasks: Anansi Completion — Close Known Gaps

**Input**: Design documents from `specs/001-close-known-gaps/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md,
`.specify/memory/constitution.md`

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

- [x] T028 [P] [US7] Document the live-smoke closure lane in `specs/001-close-known-gaps/quickstart.md` (already drafted) and in the plugin README: exact command `$HERMES_HOME/hermes-agent/venv/bin/python scripts/live_drive_smoke.py`, env gate (HERMES_HOME, api.anthropic.com:443, host creds), exit codes 0/1/2. No harness code change.
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
DATA_K1M3O5Q7_END
````
