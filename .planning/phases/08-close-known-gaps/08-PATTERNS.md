# Phase 8: Close Known Gaps - Pattern Map

**Mapped:** 2026-09-10\
**Files analyzed:** 13 proposed modifications\
**Analogs found:** 13 / 13

## File Classification

| New/Modified File | Role | Data Flow | Closest tracked analog | Match Quality |
|---|---|---|---|---|
| `anansi/store.py` | service / model | CRUD, file-I/O | `anansi/store.py` | exact |
| `anansi/config.py` | config | transform | `anansi/config.py` | exact |
| `anansi/render.py` | utility | transform | `anansi/render.py` | exact |
| `anansi/__init__.py` | provider / hook | event-driven | `anansi/__init__.py` | exact |
| `anansi/tests/test_drive_store.py` | test | CRUD, file-I/O | `anansi/tests/test_drive_store.py` | exact |
| `anansi/tests/test_drive_config.py` | test | transform | `anansi/tests/test_drive_config.py` | exact |
| `anansi/tests/test_drive_neveromit.py` | test | transform | `anansi/tests/test_drive_neveromit.py` | exact |
| `anansi/tests/test_drive_velocity.py` | test | transform, file-I/O | `anansi/tests/test_drive_velocity.py` | exact |
| `anansi/tests/test_failopen_matrix.py` | test | event-driven | `anansi/tests/test_failopen_matrix.py` | exact |
| `anansi/tests/test_reflection.py` | test | event-driven | `anansi/tests/test_reflection.py` | exact |
| `anansi/tests/test_reflection_store.py` | test | CRUD, event-driven | `anansi/tests/test_reflection_store.py` | exact |
| `anansi/tests/test_telemetry_store.py` | test | CRUD | `anansi/tests/test_telemetry_store.py` | exact |
| `anansi/README.md` | documentation | transform | `anansi/README.md` | exact |

All analog paths above were checked with `git ls-files`; all 13 are tracked sources. The untracked research artifact and the historical `001-close-known-gaps` branch are intake evidence, never analog paths.

## Pattern Assignments

### `anansi/store.py` (service/model, CRUD and file-I/O)

**Analog:** `anansi/store.py`

**Schema and fail-open pattern** (`anansi/store.py:62-103`, `200-246`):
```python
def ensure_db(db_path=None) -> bool:
    try:
        path = Path(db_path) if db_path is not None else get_db_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            if _verify_structure(path):
                return True
            _quarantine(path)
        return _create_fresh(path)
    except Exception as exc:
        logger.warning("anansi ensure_db failed (degrading): %s", exc)
        return False
```

Use the existing DDL tuple, `SCHEMA_VERSION`, `PRAGMA busy_timeout`, and boolean degradation contract. Add the narrow v4-to-v5 transition before the existing destructive recovery path. A locked but structurally sound v4 database must return `False` without `_quarantine` or sidecar changes.

**Goal write pattern** (`anansi/store.py:714-759`):
```python
elif key == "goals_add":
    for item in payload:
        conn.execute(
            "INSERT INTO goals"
            " (text, status, success_criteria, flagged_priority,"
            " domain, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (...),
        )
```

Extend both `goals_add` and `goals_update` atomically for the persisted pressure fields. Keep `apply_deltas()` as the only state-table writer and preserve its transaction/error pattern (`anansi/store.py:790-815`).

### `anansi/config.py` (config, transform)

**Analog:** `anansi/config.py`

**Coercion pattern** (`anansi/config.py:176-186`, `189-242`):
```python
def _coerce_choice(value, default, choices):
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in choices:
            return lowered
    return default

"drive_pressure": _coerce_choice(
    entry.get("drive_pressure"), DEFAULT_DRIVE_PRESSURE,
    _DRIVE_PRESSURE_CHOICES,
),
```

Keep config coercion pure, cached, and non-raising. Return a secret-safe degradation description alongside, or through a sibling helper fed from the raw entry; do not log raw rejected values.

### `anansi/render.py` (utility, transform)

**Analog:** `anansi/render.py`

**Persisted-state enrichment pattern** (`anansi/render.py:171-225`):
```python
sig["momentum"] = momentum.get("momentum")
days = momentum.get("stalled_days")
if isinstance(days, int) and "stalled_days" not in sig:
    sig["stalled_days"] = days
```

Replace the conditional model-value precedence with persisted read-time precedence: copy integer `0` too, and remove/ignore a model day count when persisted momentum has none. Use a stdlib whole-token subset match in this function, replacing its current substring association.

**Protected flagged-prefix pattern** (`anansi/render.py:404-428`, `516-528`):
```python
if not (instincts or observations or contradictions or searches
        or goal_signals or gut):
    return None

flagged_wants = _flagged_want_lines(goal_signals, goals)
lines = [SENTINEL, FRAMING]
lines.extend(flagged_wants)
protected_count = len(lines)

while len(block) // 4 > _MAX_BLOCK_TOKENS and len(lines) > floor:
    lines.pop()
```

Empty-signal suppression stays first. Within a nonempty block, every persisted flagged priority remains in the protected prefix, outside the token and energy limits. Do not add a cap, count, or withheld marker for flagged priorities. This follows Constitution III and `.planning/INGEST-CONFLICTS.md:13-19` over the historical source branch.

**Fresh-day rendering pattern** (`anansi/render.py:278-322`):
```python
stalled_days = _resolve_stalled_days(item)
clause = "I want progress on %s" % want
if isinstance(stalled_days, int):
    clause = "I want %s moving (stalled %d days)" % (want, stalled_days)
```

Make stalled-specific wording and ordering require `stalled_days > 0`; zero is a concrete fresh/active state, not a missing or stalled value.

### `anansi/__init__.py` (provider/hook, event-driven)

**Analog:** `anansi/__init__.py`

**Lazy import and fail-open boundary** (`anansi/__init__.py:86-113`, `143-159`):
```python
@_fail_open
def pre_llm_call(..., **kwargs):
    from . import appraisal, config, render, store  # lazy
    cfg = config.get_cfg()
    if not cfg.get("enabled", True):
        store.record_telemetry("skipped:disabled", session_id=session_id)
        return None
```

Wire effective `drive_pressure` into the existing render call and record configuration degradation inside a narrow nested failure boundary. Telemetry failure must not change hook output; imports remain lazy and every hook keeps `**kwargs`.

### Test files

All test files should retain `tmp_path` databases and direct `sqlite3` only as test instrumentation. Use their own focused analogs:

| File | Analog excerpts to copy | Required Phase 8 extension |
|---|---|---|
| `anansi/tests/test_drive_store.py` | `:26-64` schema/round-trip fixture; `:164-184` locked goal write returns `False` | Build a genuine v4 goals table, prove additive migration/default read-back, and prove a held lock leaves v4 DB and rows intact. |
| `anansi/tests/test_drive_config.py` | `:25-87` monkeypatched host-entry coercion assertions | Cover each valid pressure output, invalid-default behavior, one secret-safe degradation event per malformed key, and no event for valid input. |
| `anansi/tests/test_drive_neveromit.py` | `:129-283` persisted flagged goals, model omission, token crowding | Preserve all flagged priorities, including adversarial historical-cap-like inputs; assert no withheld marker. |
| `anansi/tests/test_drive_velocity.py` | `:116-142` read-time momentum test; `:160-209` render assertions | Add substring rejection, whole-token subset retention, conflicting model/persisted day replacement, and zero-day fresh rendering. |
| `anansi/tests/test_failopen_matrix.py` | `:297-319` malformed config; `:606-671` locked store/hook resilience | Make unavailable degradation telemetry a full-hook fail-open assertion; retain existing matrix breadth. |
| `anansi/tests/test_reflection.py` | `:481-533` locked DB and kill-switch behavior | Rename only the test/comment terminology from `master kill switch` to `primary/main`; preserve its behavioral assertions. |
| `anansi/tests/test_reflection_store.py` | `:335-370` rollback-journal exclusive-lock degradation | Keep this only if Phase 8 changes shared store semantics that need reflection regression coverage; do not change reflection behavior for terminology-only work. |
| `anansi/tests/test_telemetry_store.py` | `:82-161` record-row and unavailable-store tests | Assert telemetry row shape/redaction through the existing store interface and retain the false-return contract on unavailable storage. |

### `anansi/README.md` (documentation, transform)

**Analog:** `anansi/README.md`

**Contract wording pattern** (`anansi/README.md:41-50`, `90-115`):
```markdown
- **The never-omit invariant.** A user-flagged priority is NEVER silently
  dropped: it renders first, is exempt from the per-category slice and the
  token-cap line-drop, and is read from PERSISTED goal state (not model output).
```

Re-author documentation only after implementation settles. State valid configuration and the existing live-smoke lane accurately; never document a flagged-priority cap or withheld marker.

## Shared Patterns

### Fail-open hook boundary
**Source:** `anansi/__init__.py:86-113`\
**Apply to:** `anansi/__init__.py`, all hook-path tests

```python
try:
    return fn(*args, **kwargs)
except Exception as exc:
    logger.warning("anansi hook %s failed (degrading): %s", fn.__name__, exc)
    try:
        from . import store
        store.record_telemetry("llm_error", error=(fn.__name__ + ": " + str(exc))[:300])
    except Exception:
        pass
    return None
```

### SQLite ownership and transaction discipline
**Source:** `anansi/store.py:818-868`\
**Apply to:** schema migration, goal writes, telemetry tests

```python
conn.execute("PRAGMA busy_timeout=%d" % _DEFAULT_BUSY_TIMEOUT_MS)
with conn:
    conn.execute(...)
return True
```

No module other than `store.py` accesses runtime SQLite. A lock is availability failure, not grounds to erase a valid v4 database.

### Constitutional rendering precedence
**Source:** `anansi/render.py:404-428,516-528`; `.planning/INGEST-CONFLICTS.md:13-19`\
**Apply to:** `render.py`, never-omit tests, README

Persisted flagged goals are exempt from the top-N slice, soft token cap, and energy budget. The current baseline suppresses a successful empty signal mapping. The Phase 8 target selected by `08-03-PLAN.md` overrides that baseline only for persisted active flagged goals: `signals={}` still renders their protected wants, while actual appraisal failure represented by `signals is None` remains an empty injection.

## No Analog Found

None. Phase 8 extends existing store, config, rendering, hook, test, and documentation surfaces.

## Metadata

**Analog search scope:** `anansi/`, `anansi/tests/`, `.planning/reference/`, `.planning/`\
**Files scanned:** 13 proposed files plus constitution and intake-conflict sources\
**Pattern extraction date:** 2026-09-10
