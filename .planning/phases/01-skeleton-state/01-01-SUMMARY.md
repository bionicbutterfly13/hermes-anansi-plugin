# Plan 01-01 Summary

**Completed:** 2026-06-10
**Phase:** 1 — Skeleton + State

## What was built

The `anansi` plugin skeleton (`plugin.yaml` with explicit `kind: standalone`
+ `__init__.py` with `register(ctx)` and three `_fail_open`-guarded no-op hooks) was
verified against the plan spec, deployed by symlink into the live install, enabled
via `hermes plugins enable anansi`, and empirically proven across real
`hermes -z` turns. All four Phase-0 validation items are answered with evidence in
`01-VALIDATION.md` — load proof (kind=standalone, 3 hooks registered), dispatch
proof (all three hooks fired, output unchanged, latency delta lost in LLM variance),
hook-raise isolation (turn survives an unguarded raise), gateway-lane dispatch
(sync, same call site as CLI), and upstream-main parity (confirmed, not deferred).

## Key files

- `anansi/plugin.yaml`: manifest — name/kind/provides_hooks/pip_dependencies per spec
- `anansi/__init__.py`: register(ctx) + three fail-open no-op hooks; zero import-time side effects; no MemoryProvider strings
- `.planning/phases/01-skeleton-state/01-VALIDATION.md`: evidence for Phase-0 items 1, 2, 3, 4, 4b
- `$HERMES_HOME/plugins/anansi`: symlink → repo `anansi/` (live deploy)
- `.gitignore`: now excludes `__pycache__/` and `*.pyc`

## Decisions made

- **Item 3 answered now, not deferred:** upstream/main (183d86b3e, fetched
  2026-06-10) has identical `provides_hooks` (plugins.py:245, :1386) and `ctx.llm`
  facade (plugins.py:302-315; plugin_llm.py:683 `complete_structured` with
  json_mode/json_schema/timeout). PKG-03 re-verification before the Phase 4 PR
  still stands since upstream moves daily.
- **Gateway-lane finding locks Phase 2 design:** both lanes dispatch hooks through
  the single synchronous call site (`agent/turn_context.py:316-341`); sync
  `complete_structured` inside a ThreadPoolExecutor with a wall-clock deadline is
  correct for both lanes.
- `on_session_start` DOES fire on a `-z` one-shot turn (open question in the plan
  resolved to "fires" — all three hooks observed on a single one-shot).

## Deviations from plan

- **Task 01-01-01 was mostly pre-done (rerun context):** `plugin.yaml` and
  `__init__.py` existed from the prior halted run (commit 88990fb, post-rename)
  and matched the plan spec exactly — no drift in the spec files. The only fix
  was drift housekeeping: the prior commit had accidentally tracked
  `anansi/__pycache__/*.pyc`; untracked it and added `.gitignore`
  entries (commit 97a43a9). Symlink created fresh; all four verify checks pass.
- **Load proof came from the turn's debug stderr, not `plugins list`:**
  `hermes plugins list` does not run full discovery (no "Parsed manifest" debug
  lines) — used the plan's documented fallback (turn capture,
  `/tmp/anansi-dispatch-proof.txt`).
- **Hook-firing proof needed the temp-instrumentation fallback:** the host's
  logging config does not surface plugin-logger DEBUG lines, so hooks were
  temporarily instrumented to append to `/tmp/anansi-dispatch-proof-hooks.log`,
  then fully reverted (verified: grep clean, `git status` clean).
- **Dispatcher WARNING for the raise experiment was not visible in the live `-z`
  capture or `logs/agent.log`** — the host quiets turn-time logging in one-shot
  mode (agent.log stops at discovery; even routine turn INFO lines are absent).
  Turn survival was proven by the live raise turn (output `OK`, exit 0); the
  exact WARNING line was captured by driving the same raising hook through the
  real `PluginManager.invoke_hook` in-process
  (`/tmp/anansi-raise-dispatcher-proof.txt`). Recorded in Item 2.
- **Extra enabled timing run added:** the first enabled turn hit a 234.88s
  provider-wait outlier (user/sys CPU identical to other runs); a second enabled
  run (24.50s) vs the disabled baseline (29.58s) shows the hook delta is lost in
  run-to-run noise — enabled was faster than disabled.
- **Task 3 step 1's combined commit was superseded** by the per-task commits
  already landed (97a43a9, 31d1d02), satisfying the same revert-baseline purpose.

## Notes for downstream

- For Dr. Mani: the unrelated live "Anansi Metacognitive Guardrails" plugin at
  `$HERMES_HOME/plugins/anansi` was never touched and remains enabled (visible in
  every plugin listing alongside `anansi`).
- Phase 2 can rely on: sync hook dispatch in both lanes (executor + wall-clock
  deadline pattern confirmed correct), upstream parity of `ctx.llm`, and the
  fail-open guard already in place as the telemetry stub point.
- Plugin debug observability is poor by default: turn-time plugin logs are not
  surfaced in `-z` mode. Phase 2 telemetry (state-DB failure counters per
  ARCHITECTURE.md anti-pattern 8) is the real observability lane — console
  logging cannot be relied on.
- Plan 01-02 (state store) is unblocked; `anansi` is enabled and inert
  on the live install.
