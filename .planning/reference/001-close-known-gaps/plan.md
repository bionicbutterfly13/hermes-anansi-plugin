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
