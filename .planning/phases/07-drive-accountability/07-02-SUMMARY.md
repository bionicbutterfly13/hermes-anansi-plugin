# Plan 07-02 Summary

**Completed:** 2026-06-14
**Phase:** 7 — Drive / Accountability
**Branch:** phase-7-drive-accountability

## What was built

The read-time progress-velocity signal (DRIVE-02) that makes the drive layer
accountable: a stalled goal now surfaces LOUDER than a moving one — where
"louder" is SALIENCE and ORDERING (it renders first), never imperative
language. A pure stdlib helper (`store.goal_momentum`) derives per-goal
momentum (`stalled N days` / `moving` / `unknown` + a salience weight where
stalled > moving) from GROUND TRUTH — read-mode `open()` of the git
reflog/refs and `os.stat().st_mtime` — computed at appraisal-READ time inside
`read_snapshot` (mirroring the `_effective_weight` decay-at-read idiom), NOT
behind debounced reflection. Momentum flows into `build_context` as
observational state, `stalled_days` threads through the `goal_signals`
schema/parse and the rendered `- drive note:` line, and stalled goals are
ordered first in the block. User-authorized pressure metadata
(`support_style`/`push_when_stalled`) can raise a stalled goal's salience, but
the neutral stalled-days observation and the drive-caused effect render as
SEPARATE, inspectable clauses. Every velocity path is fail-open: any
exception (absent/corrupt `.git`, unparseable reflog, bad timestamp, absent
hint file) degrades to the benign `unknown` default and never raises into
`pre_llm_call`.

## Key files

- `anansi/store.py` — new DRIVE-02 velocity block: `_STALLED_DAYS_THRESHOLD`
  (2.0), `_MOMENTUM_SALIENCE` (stalled 1.0 > moving 0.3 > unknown 0.0),
  `_momentum_default()`, `_repo_root()` (cwd/`$HERMES_HOME`-parent walk-up to
  `.git`, never a literal), `_last_commit_epoch()` (read-mode `open()` of
  `.git/HEAD` → `.git/refs/heads/*` + last `.git/logs/HEAD` reflog line →
  committer epoch before the tz offset), `_days_idle_from_epoch/_iso`,
  `_goal_mtime_days_idle` (per-goal `domain` hint mtime, repo-containment
  guarded), and the public `goal_momentum(goal, repo_root, now)`. `read_snapshot`
  annotates each goal dict with `momentum` at read time (wrapped so a velocity
  failure cannot break the snapshot's None-on-error contract).
- `anansi/appraisal.py` — `goal_signals` schema gains optional `stalled_days`
  (integer ≥ 0); `_coerce_stalled_days` (clamped to `_MAX_STALLED_DAYS` 3650,
  dropped if non-numeric); `parse_signals` carries `stalled_days` through;
  `APPRAISAL_PROMPT` describes the momentum observation as neutral elapsed
  time, never a deadline/directive; `build_context` includes each non-candidate
  goal's `momentum`/`stalled_days`.
- `anansi/render.py` — `_MOMENTUM_RANK`, `_PUSH_SALIENCE_BONUS`,
  `_drive_salience`, `_push_when_stalled`, `_order_goal_signals` (stalled-first,
  stable), `_render_drive_note` (neutral `stalled N days` clause + a SEPARATE
  `[push zone: ...]` drive-effect clause), and `enrich_goal_signals` (anchors a
  parsed signal to the matching persisted goal's read-time momentum + pressure
  metadata). `_SECOND_PERSON_DIRECTIVE_RE` / `DIRECTIVE_PATTERNS` untouched.
- `anansi/__init__.py` — drive-on path now calls `render.enrich_goal_signals`
  on the parsed `goal_signals` (grounds stalled signals in persisted momentum);
  drive-off suppression unchanged (byte-for-byte invariant intact).
- `anansi/tests/test_drive_velocity.py` — NEW (12 tests): moving/stalled/
  absent-git/unparseable-reflog/bad-timestamp/mtime-hint, read_snapshot
  annotation (read-time proof), no-subprocess self-check, stalled-before-moving
  ordering, stalled-days-in-note, pressure-raises-salience-preserves-neutral,
  enrich-grounds-in-persisted-momentum.
- `anansi/tests/test_failopen_matrix.py` — 3 new velocity fail-open rows
  (absent-.git, unparseable-reflog, bad-timestamp → hook still renders, no
  raise, single `ok` row) + matrix-table doc entries.

## Decisions made

- **Forbidden-substring discipline extends to comments/docstrings.** The
  anti-creep `FORBIDDEN_SUBSTRINGS` scan is a plain whole-file substring match,
  so even `subprocess`/`os.system` in explanatory prose bricks the suite. The
  velocity comments say "NO shell-out, NO git library" instead. The local
  no-subprocess self-check test lives in the test file (tests/ is excluded from
  the plugin-module scan), so its assertion literals are safe.
- **Salience model is additive and inspectable.** `_drive_salience` =
  momentum rank (stalled 2 > moving 1 > unknown 0) + a `_PUSH_SALIENCE_BONUS`
  (10) only for a user-authorized stalled push + confidence tie-breaker. The
  neutral read is recoverable from `stalled_days`; the push bonus is recoverable
  from the pressure metadata — the two effects never blend (Pitfall #9).
- **`enrich_goal_signals` grounds the signal in ground truth.** Rather than
  trusting the model to echo `stalled_days`, `__init__` matches each parsed
  signal to its persisted goal (case-insensitive substring either direction)
  and attaches the read-time momentum + pressure metadata. This anchors the
  stalled signal even when the model omits it.
- **`domain` doubles as the per-goal mtime hint.** A goal's existing `domain`
  column is treated as a repo-relative path hint for `os.stat` (containment-
  guarded to inside the repo root); no schema bump needed.

## Deviations from plan

- **Pressure metadata (`support_style`/`push_when_stalled`) is read off the
  goal_signals item / persisted goal, not a new schema column.** The 07-01
  `goals` table has no pressure columns yet, so `enrich_goal_signals` copies
  through whatever pressure keys the persisted goal carries (forward-compatible
  when 07-04 adds them) and the render helpers read them defensively. The
  pressure render/ordering path is fully tested at the render layer today; the
  persistence of pressure columns is a later plan's concern. No constraint was
  violated — the neutral/drive-effect separation is proven now.
- **Added one extra test beyond the plan's enumerated list**
  (`test_enrich_grounds_signal_in_persisted_momentum`) to cover the new
  `enrich_goal_signals` wiring that grounds stalled signals in persisted
  momentum. 15 net-new tests total (120 → 135).

## Notes for downstream (07-03 / 07-04)

- **Momentum is on every goal dict from `read_snapshot` now** (`goal["momentum"]`
  = `{"momentum", "stalled_days", "salience"}`). 07-03's first-person
  `- drive want:` voice and the never-omit invariant can read this directly.
- **`enrich_goal_signals` is the seam for grounding** any future goal-aware
  field in persisted ground truth — extend it, don't add a parallel matcher.
- **Pressure columns are not yet persisted.** When 07-04 adds
  `support_style`/`push_when_stalled`/`stall_threshold_days` to the `goals`
  table, `enrich_goal_signals` already copies them through and the render
  helpers already consume them — only the schema/`apply_deltas` write side is
  missing.
- **The neutral-vs-drive separation is the inspectability red line** (Pitfall
  #9): keep `stalled_days` as the neutral read and the `[push zone: ...]`
  clause as the separate drive effect; do not blend them into one number.
- **Anti-creep landmine reminder:** never let the literal substrings
  `subprocess`/`os.system`/`eval(`/`exec(` into any of the six plugin modules
  — comments included. The git signal is stdlib read-mode `open()` + `os.stat`
  only.
