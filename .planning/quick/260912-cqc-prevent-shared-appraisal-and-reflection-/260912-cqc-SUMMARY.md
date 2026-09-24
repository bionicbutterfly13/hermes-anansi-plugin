---
phase: quick
plan: 260912-cqc
status: incomplete
date: "2026-09-12"
subsystem: worker scheduling
tags: [concurrency, appraisal, reflection, fail-open]
requirements-completed: []
---

# Worker repair implemented; release gate not clean

## Delivered

The shared `_submit_if_idle` helper atomically admits one unfinished future.
Both callers skip when busy. A timed-out caller cancels a pending future but
retains admission ownership for a running one. The worker wrapper checks its
expiry before entering the model call, including when cancellation loses the
executor-start race. Completion, exceptions and cancellation permit the next
request without replacing the executor.

Appraisal hooks record `skipped:worker_busy` and return no injection. Reflection
records `reflect_skipped:worker_busy`, preserves captured turns and the reflection
watermark, and keeps the previously documented consumed-session trigger. The
next session or debounce trigger can retry those turns.

The existing model/trust fallback, prompts, defaults, configuration ceiling,
worker count, storage schema and drive rendering are unchanged. The config and
call-path comments now explain the actual cancellation boundary.

## Verification

- Baseline full canonical gate, before behavioral edits: **198 passed, 1 failed**
  in 18.27s.
- New regression module before repair: **10 failed, 2 passed**. Failures cover
  busy admission in all four caller combinations, contention, pending cancellation,
  startup races and busy hook/reflection telemetry. Submission-error recovery
  already passed. Two model-exception recovery cases were added afterward.
- Targeted worker/appraisal/reflection run after repair: **51 cases passed**
  (before adding the two model-exception cases).
- Final `./scripts/test.sh`: **212 passed, 1 failed** in 17.71s. All **14 new
  worker regression cases** pass. Existing tests and assertions were preserved.
- `git diff --check` passed. Production executor submission is centralized in
  the admission helper; both callers use it.
- `graphify update .` completed its AST-only update. Generated graph output is
  ignored by the existing repository rule.

The one failure is identical before and after: `test_persisted_flagged_priorities_survive_empty_signal_full_hook`
at `anansi/tests/test_drive_neveromit.py:436`. All 55 protected wants survive;
their expected fresh-progress wording does not match the computed momentum.
Read-only reproduction confirms `_repo_root()` skips the linked worktree's
`.git` FILE and climbs to the parent checkout's `.git` DIRECTORY. Its reflog time
is `2026-07-05T17:05:38+00:00`; a newly timestamped goal is therefore classified
as stalled for 68 days on this run. No repository-discovery or rendering fix is
included here. This remains a release-gate failure, not a waived assertion.

## GSD execution record

Official runtime `@opengsd/gsd-core` 1.13.0 provided `init.quick` and this task ID.
Default quick mode excluded optional discussion, research, checker and verifier
steps. Execution was inline, using the documented Codex adapter and single-agent
sequential isolation gate, inside the existing task-owned worktree.

Planner contributions were checked: API detector returned `detected:false`;
assumption-delta returned `phase_unresolved` for the quick ID, an advisory skip;
no schema paths were in scope. No executor contribution hooks were returned.
The model-bake warning affects agent routing; no child agents were dispatched.

`quick-tasks-migrate` ran before the canonical table was added. The table was
written using the quick workflow's documented schema rather than the append
helper, which would label this uncommitted repair with the previous HEAD hash.
Phase 9 and roadmap completion were not advanced.

## Remaining work and limits

Implementation and its regression checks are complete. Overall status remains
incomplete because the full release gate fails and changes are uncommitted.
Repair nested-worktree discovery next under a separate scope decision, then run
the full gate. No commit, merge, push, plugin install or provider call occurred.
Running requests still cannot be stopped by cancelling their Python future;
they can keep the worker occupied and delay process exit. Cancellation research
and any new live-provider trial remain separate follow-ups.
