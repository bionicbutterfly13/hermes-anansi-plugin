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
