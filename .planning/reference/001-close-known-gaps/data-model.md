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
