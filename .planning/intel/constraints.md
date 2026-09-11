## Phase 1 Data Model — Close Known Gaps
- source: .planning/reference/001-close-known-gaps/data-model.md
- type: schema
- content:
````text
DATA_B2D4F6H8_START
# Phase 1 Data Model — Close Known Gaps

## Entity: Goal (extended)

Existing `goals` table (`store.py:99-103`, schema v4) gains three persisted **pressure-definition**
columns at schema v5. Momentum (`stalled_days`, `momentum`) is NOT persisted — it stays derived at read
time (Principle IV), so it is deliberately absent here.

| Column | Type | Default | Meaning | New? |
|--------|------|---------|---------|------|
| id | INTEGER PK | — | goal id | existing |
| text | TEXT NOT NULL | — | goal statement | existing |
| status | TEXT NOT NULL | 'candidate' | active/queued/backburner/candidate (CHECK) | existing |
| success_criteria | TEXT | NULL | user criteria | existing |
| flagged_priority | INTEGER NOT NULL | 0 | 0=unflagged; >0 magnitude = priority rank (now used as G4 sort key) | existing |
| domain | TEXT | NULL | domain tag (whitelist + mtime hint) | existing |
| created_at / updated_at | TEXT | — | timestamps | existing |
| **support_style** | TEXT | NULL | e.g. `firm`/`push`/`firmer`/`gentle`; drives the under-support clause | **v5** |
| **push_when_stalled** | INTEGER NOT NULL | 0 | bool; authorizes firmer support when stalled | **v5** |
| **stall_threshold_days** | INTEGER | NULL | days-stalled before push zone activates | **v5** |

**Validation / read defaults**: absent (`NULL`) `support_style` → no under-support clause; `push_when_stalled`
defaults 0 (off); `stall_threshold_days` NULL → use the render-side default. All reads via `goal.get(...)`
so missing keys degrade to defaults.

**Migration (v4→v5)**: additive `ALTER TABLE goals ADD COLUMN` for each new column, fail-open wrapped;
existing rows preserved with the new columns defaulted (see contracts/store-goals-schema.md).

**Write path**: `goals_add` (`store.py:714-735`) and `goals_update` (`store.py:736-751`) extended to
persist the three fields. **Read path**: unchanged — `_rows_as_dicts` `SELECT *` surfaces them.

## Entity: Config keys (extended)

Read via `get_cfg` (`config.py:189-242`); all coerced, never raise.

| Key | Type | Default | Choices/Range | New? | Consumer |
|-----|------|---------|---------------|------|----------|
| drive_pressure | choice | `standard` | quiet/standard/firm | existing (now READ) | render_block salience+verbosity (G3) |
| **drive_flagged_want_cap** | int | 5 | floor 1 | **new** | `_flagged_want_lines` cap (G4) |

`drive_flagged_want_cap` uses `_coerce_int(value, 5, lo=1)`; values <1 clamp to 1 (never-omit floor keeps
the single top flagged want).

## Entity: Config-degradation telemetry event (new outcome)

A `telemetry` row (existing table, `store.py:87`) with a new **non-failure** outcome.

| Field | Value |
|-------|-------|
| outcome | `config_degraded` |
| error | `"<key>: rejected <shape>, applied <default>"` — shape is `<str len=N>` / `<redacted>`, never the literal value |
| other columns | as `record_telemetry` supplies (ts, session_id, …) |

Classification: added to the non-failure exclusion set in `telemetry_summary` (`store.py:897-909`).
Emitted once per degraded key on config (re)load from `__init__.py`.

## State transitions

None. All three changes are additive/observational; no goal lifecycle state machine changes.
DATA_B2D4F6H8_END
````

## Implementation Plan: Anansi Completion — Close Known Gaps
- source: .planning/reference/001-close-known-gaps/plan.md
- type: protocol
- content:
````text
DATA_C3E5G7I9_START
# Implementation Plan: Anansi Completion — Close Known Gaps

**Branch**: `001-close-known-gaps` | **Date**: 2026-07-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `.planning/reference/001-close-known-gaps/spec.md`

## Summary

Eight hardening slices (G1–G8) that make the Phase 7 Drive/Accountability increment verified-complete
without adding any capability. The work is surgical edits to four existing modules — `store.py`
(persist per-goal pressure), `config.py` (wire `drive_pressure`, surface config degradations),
`render.py` (bound flagged wants, tighten goal matching, fix `stalled_days:0`, apply global pressure),
and one telemetry seam — plus a documented live-smoke closure lane (G1) and a one-line test rename (G8).
Every edit stays inside the existing single SQLite surface, the zero-dependency + import-allowlist
envelope, and the never-omit / fail-open invariants.

## Technical Context

**Language/Version**: Python 3.11 (hermes-agent venv at `$HERMES_HOME/hermes-agent/venv`)

**Primary Dependencies**: None added. Host surfaces only: `agent`, `hermes_cli`, `hermes_constants`;
stdlib `sqlite3`, `dataclasses`. (Import allowlist enforced by `test_anticreep.py:391-393`.)

**Storage**: One SQLite file (`store.py`, WAL) — the single state surface. `goals`, `telemetry`, `meta`
tables already exist.

**Testing**: pytest via `./scripts/test.sh` (hermes venv, `-m pytest -q` over `anansi/tests`; venv never
modified). Live end-to-end via `scripts/live_drive_smoke.py`.

**Target Platform**: hermes-agent 0.16.0 plugin (`kind: standalone`), hooks `pre_llm_call`,
`on_session_end`, `on_session_start`.

**Project Type**: Single Python package (`anansi/`), no frontend/service split.

**Performance Goals**: No regression to the appraisal deadline (default 8.0s, p50 ≤6s). None of these
slices add an LLM call or a blocking path.

**Constraints**: Fail-open everywhere (no hook path may raise/block); zero new deps; no new write-mode
`open()` (exactly one is allowed, the debug dump); no `open()` line may contain "config"; every rendered
line must use an `ALLOWED_LABEL_PREFIXES` label and pass `assert_no_directive_language`.

**Scale/Scope**: ~4 source files, ~6 test files touched; goals table is capped at newest 50 rows.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Impact of this feature | Verdict |
|-----------|------------------------|---------|
| I. Fail-Open Is Law | New store column read/write stays inside the existing `apply_deltas`/`read_snapshot` try-guards; new ALTER migration is wrapped and falls through to quarantine on failure; config-degradation telemetry uses the fail-open `record_telemetry`. No new raise path. | PASS |
| II. No Autonomy — Observational Only | No new directive. Global pressure (G3) modulates salience/ordering/verbosity ONLY — never the imperative-free literal strings. Withheld-marker (G4) uses the existing `- drive want:` label. | PASS |
| III. Never-Omit & Anti-Erasure | G4 cap keeps the top-priority flagged want + a visible withheld marker inside the protected prefix; guarantee still reads persisted goals. **G2 migration MUST NOT quarantine (discard) existing user goals** — see Complexity Tracking; additive ALTER chosen precisely to honor this principle. | PASS (with justified deviation) |
| IV. Single SQLite Surface, Ground-Truth at Read Time | Pressure *definition* persists as columns; `stalled_days`/momentum stay derived at read time (unchanged). No second surface. | PASS |
| V. Zero New Deps, Paths From Config | No imports added outside stdlib + host allowlist. New config keys read through `get_cfg` coercers; no path literals. | PASS |
| VI. Inspectable & Adjustable Drive | Global pressure and the flagged-want cap are new config knobs; neutral read vs drive effect stays separately rendered; drive-off byte-for-byte identity preserved. | PASS |
| VII. Minimal Surgical Change | Each slice is one edit in one place; existing helpers reused (`_coerce_choice`, `record_telemetry`, `_flagged_want_lines`). | PASS |

**Gate result: PASS.** One justified deviation (G2 additive migration vs the disposable-state doctrine) —
documented in Complexity Tracking; it exists to satisfy Principle III, a higher authority than the
module-local doctrine.

## Project Structure

### Documentation (this feature)

```text
.planning/reference/001-close-known-gaps/
├── plan.md              # This file
├── research.md          # Phase 0 — decisions per gap (grounded in code)
├── data-model.md        # Phase 1 — Goal pressure columns, config keys, telemetry event
├── quickstart.md        # Phase 1 — how to validate each slice
├── contracts/
│   ├── store-goals-schema.md    # goals table v5 column contract + migration
│   ├── config-keys.md           # drive_pressure + flagged-want cap key contracts
│   └── telemetry-outcomes.md    # config_degraded outcome contract
├── checklists/
│   └── requirements.md  # (source requirements checklist) — all green
└── tasks.md             # historical branch task ledger
```

### Source Code (repository root)

```text
anansi/
├── store.py         # G2: goals DDL v4→v5 + additive ALTER migration; goals_add/goals_update persist
│                    #     pressure cols. G7: record_telemetry already exists; add config_degraded to the
│                    #     non-failure exclusion list in telemetry_summary.
├── config.py        # G3: no change to coercion; G7: get_cfg surfaces degradations (raw vs coerced diff).
│                    #     New key: drive_flagged_want_cap (G4).
├── render.py        # G4: _flagged_want_lines priority-sort + cap + withheld marker.
│                    # G5: normalize goal↔signal matching at :194-195, :353-354, :468-471.
│                    # G6: gate stalled_days on `> 0` at :145, :246-247, :314.
│                    # G3: render_block(pressure=...) modulates note_limit + _drive_salience.
├── __init__.py      # G7: emit config_degraded telemetry rows on session-start/reload (has session_id).
└── tests/
    ├── test_drive_store.py       # G2 round-trip + v4→v5 migration-preserves-rows test
    ├── test_drive_config.py      # G3 pressure-applied, G4 cap key, G7 degradation
    ├── test_drive_neveromit.py   # G4 cap keeps top flagged + withheld marker
    ├── test_drive_velocity.py    # G6 stalled_days:0 reads as moving
    ├── test_telemetry_store.py   # G7 config_degraded is a non-failure; update hardcoded cfg dict
    ├── test_failopen_matrix.py   # G7 mirror row; update pinned cfg dict shape
    └── test_reflection.py        # G8 rename test_master_kill_switch → test_primary_kill_switch
```

**Structure Decision**: Single-package edits; no new modules (adding a module would trip the anti-creep
scan-target test). All persistence stays in `store.py`, all config in `config.py`, all rendering in
`render.py` — matching the established one-surface-per-concern layout.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| G2 uses additive `ALTER TABLE goals ADD COLUMN` instead of the module's quarantine-and-recreate doctrine (`store.py:16-19`) | The doctrine discards existing goal rows on a `SCHEMA_VERSION` bump. Those rows include user-minted, possibly flagged goals. Silently dropping them violates Principle III (Never-Omit & Anti-Erasure). SQLite `ALTER ADD COLUMN` is non-destructive and additive-only. | Pure quarantine-recreate (the simpler, in-doctrine path) is rejected because it erases user priorities — the exact failure the constitution is built against. The ALTER path is fail-open wrapped: on any ALTER error it falls through to the existing `_quarantine` + `_create_fresh`, so `ensure_db` still never raises. |
DATA_C3E5G7I9_END
````

## Contract — config keys
- source: .planning/reference/001-close-known-gaps/contracts/config-keys.md
- type: protocol
- content:
````text
DATA_D4F6H8J0_START
# Contract — config keys

## `drive_pressure` (existing key, now consumed)

- Source: `get_cfg()["drive_pressure"]`, coerced by `_coerce_choice` (`config.py:237-240`).
- Default: `standard`. Choices: `quiet | standard | firm` (`code-red` excluded by design).
- Consumer (NEW): `render_block(pressure=...)`.
- Effect envelope (Principle II/VI): modulates ONLY
  - `note_limit` verbosity (`render.py:481-487`): quiet ≤ standard ≤ firm (bounded by existing max 3),
  - salience bonus in `_drive_salience` (`render.py:137-156`): larger under firm, smaller under quiet.
- MUST NOT change: any literal want/note string, the neutral `stalled N days` clause, the
  `[under-support: ...]` / `[push zone: ...]` effect text. `standard` reproduces today's output
  byte-for-byte.

## `drive_flagged_want_cap` (new key)

- Source: `get_cfg()["drive_flagged_want_cap"]`, coerced by `_coerce_int(value, 5, lo=1)`.
- Default: `5`. Floor: `1` (values <1 clamp to 1 — never-omit keeps the single top flagged want).
- Consumer: `_flagged_want_lines` (`render.py:325-362`).
- Effect: at most `cap` flagged want lines render (priority-ordered, top always kept); if more flagged
  goals exist, a `- drive want: [N flagged priorities withheld]` marker is appended. Both the kept wants
  and the marker live in the protected prefix (never dropped).
- Fail-open: malformed value coerces to 5; `get_cfg` never raises.

## Cross-cutting

- Any new key MUST be added to the hardcoded expected cfg dict in
  `test_get_cfg_defaults_when_host_config_unavailable` (`test_telemetry_store.py:240-258`) and the pinned
  cfg in `test_failopen_matrix.py:143`.
DATA_D4F6H8J0_END
````

## Contract — goals table schema v5 + migration
- source: .planning/reference/001-close-known-gaps/contracts/store-goals-schema.md
- type: schema
- content:
````text
DATA_E5G7I9K1_START
# Contract — `goals` table schema v5 + migration

## Schema (v5)

```sql
CREATE TABLE goals (
  id INTEGER PRIMARY KEY,
  text TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'candidate'
    CHECK (status IN ('active','queued','backburner','candidate')),
  success_criteria TEXT,
  flagged_priority INTEGER NOT NULL DEFAULT 0,
  domain TEXT,
  created_at TEXT,
  updated_at TEXT,
  support_style TEXT,                                  -- v5
  push_when_stalled INTEGER NOT NULL DEFAULT 0,        -- v5
  stall_threshold_days INTEGER                         -- v5
);
```

`SCHEMA_VERSION = 5` (`store.py:35`).

## Migration contract (v4 → v5)

- **Precondition**: an existing DB whose `meta.schema_version == '4'` and whose structure otherwise
  verifies.
- **Action**: in `ensure_db`, before quarantine, attempt additive upgrade:
  ```sql
  ALTER TABLE goals ADD COLUMN support_style TEXT;
  ALTER TABLE goals ADD COLUMN push_when_stalled INTEGER NOT NULL DEFAULT 0;
  ALTER TABLE goals ADD COLUMN stall_threshold_days INTEGER;
  UPDATE meta SET value='5' WHERE key='schema_version';
  ```
  wrapped in `try/except`. On ANY error → fall through to existing `_quarantine` + `_create_fresh`.
- **Postcondition (happy path)**: every pre-existing goal row is preserved; new columns read
  `NULL / 0 / NULL`. `ensure_db` returns True.
- **Postcondition (failure path)**: DB quarantined + recreated fresh at v5; `ensure_db` returns True.
- **Invariant**: `ensure_db` NEVER raises (Principle I).

## Round-trip contract

- `goals_add` persists `support_style`, `push_when_stalled` (default 0), `stall_threshold_days`.
- `goals_update` updates the same three.
- `read_snapshot` surfaces them via `SELECT *`; a persisted goal read back equals what was written for
  these fields.
- Locked/corrupt DB during write → `apply_deltas` returns False (no raise); during read →
  `read_snapshot` returns None.

## Tests (mirror existing shapes)

- v4→v5 migration preserves rows: new test mirroring `test_v3_db_quarantine_recreates_at_v4`
  (`test_drive_store.py:118-138`) but asserting existing goal rows SURVIVE with defaulted new columns.
- Round-trip: extend `test_drive_store.py` to write a goal with the three fields and assert read-back
  equality.
- Locked-DB unchanged: `test_locked_db_goal_write_returns_false` must stay green with the new INSERT cols.
DATA_E5G7I9K1_END
````

## Contract — config_degraded telemetry outcome
- source: .planning/reference/001-close-known-gaps/contracts/telemetry-outcomes.md
- type: protocol
- content:
````text
DATA_F6H8J0L2_START
# Contract — `config_degraded` telemetry outcome

## Outcome

- String: `config_degraded`
- Classification: **non-failure**. Add it to the exclusion set in `telemetry_summary`
  (`store.py:897-909`) and the docstring vocabulary (`store.py:876-882`), alongside
  `ok`/`trust_fallback`/`reflect_ok` and the `skipped:*` / `reflect_skipped:*` prefixes. Without this it
  would be counted as a failure (exclusion-list is fail-loud by design).

## Row shape

- Written via existing `record_telemetry("config_degraded", error=<msg>, session_id=..., db_path=...)`.
- `error` = `"<key>: rejected <shape>, applied <default>"` where `<shape>` is a secret-safe indicator
  (`<str len=N>`, `<redacted>`, or a type name) — NEVER the literal rejected value.
- One row per degraded key.

## Emission

- Site: `__init__.py` on session-start / config force-reload (has `session_id`; already calls
  `record_telemetry`). NOT from `config.py` (no `store` import; stays standalone).
- Frequency guard: emitted once per (re)load, not per turn.
- Fail-open: `record_telemetry` never raises (`store.py:859-862`); a locked telemetry store degrades to a
  logged warning and the turn proceeds.

## Tests

- Non-failure classification: mirror `test_drive_disabled_is_non_failure`
  (`test_failopen_matrix.py:433-449`) and the reflect-vocabulary test (`test_telemetry_store.py:196-218`)
  — assert `summary["failure_count"]` excludes `config_degraded` and `by_outcome["config_degraded"] >= 1`.
- Secret-safety: assert the rejected literal value is NOT present in the stored `error` text.
DATA_F6H8J0L2_END
````
