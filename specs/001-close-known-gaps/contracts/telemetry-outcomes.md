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
