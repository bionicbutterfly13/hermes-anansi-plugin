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
