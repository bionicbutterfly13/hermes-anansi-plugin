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
