---
phase: quick
plan: 260912-cqc
type: execute
wave: 1
depends_on: []
files_modified:
  - anansi/appraisal.py
  - anansi/reflection.py
  - anansi/config.py
  - anansi/tests/test_worker.py
  - CHANGELOG.md
  - .planning/DECISIONS.md
  - .planning/STATE.md
autonomous: true
requirements: []
must_haves:
  truths:
    - Busy appraisal and reflection callers skip without adding queued work.
    - Concurrent callers cannot both reserve the single worker.
    - Expired pending work is cancelled and cannot make a later model call.
    - A timed-out running request keeps the worker busy until it finishes.
    - Skipped reflection preserves its state watermark and captured turns.
---

# Shared worker backlog repair

Approved by Dr. Mani on 2026-09-12 following the recorded timeout decision.
GSD quick task, executed inline under the Codex skill adapter in the existing
task-owned `codex/clarify-appraisal-timeout` worktree. Official runtime identity:
`@opengsd/gsd-core` 1.13.0. `init.quick` supplied this directory and no new branch.
Quick dispatch isolation resolves to orchestrator-worktree and its documented
single-agent gate selects sequential execution. No additional agents dispatched.
Commit, integration, publication and live-provider runs require separate authority.

## Settled scope

Use one shared admission helper around the existing lazy single-worker executor.
Under a short lock, check the tracked future and submit only when it is absent
or done. Return `skipped:worker_busy` / `reflect_skipped:worker_busy` otherwise.
Keep reservation while a timed-out request runs; release implicitly when its
future finishes, including exceptions and cancellation. Cancel pending futures
on caller timeout. Guard the worker entry against an already-expired deadline,
covering cancellation that loses the race with executor startup.

Keep the default 8 seconds and 10-second clamp, model selection, prompts, trust
fallback, one worker, and reflection's documented consumed-session trigger.
Running-request cancellation research and a further provider trial are deferred.

## Constitution check

I: Busy callers return no injection with existing skipped telemetry; timeout
remains bounded. Running requests are not claimed cancelled or bounded at exit.
II: No autonomous work, directives or new model capabilities.
III: Preserve priority rendering and all existing assertions. The established
failed-appraisal empty-injection boundary remains in force.
IV: No schema or storage changes; reflection watermark advances only on success.
V: Only stdlib concurrency primitives; no new dependency or config path.
VI: Drive controls and drive-off rendering stay untouched.
VII: One scheduling repair shared by both paths, reproducible offline tests,
dated root-cause notes. No constitution amendment or complexity exception.

## Tasks

<task type="auto">
  <name>1. Add regression coverage for worker admission and expiration</name>
  <files>anansi/tests/test_worker.py</files>
  <action>Use events/barriers and controlled futures, not a live provider. Cover
  both busy-owner/caller combinations, concurrent callers, pending cancellation,
  a started-but-expired wrapper, recovery after completion or submission error,
  hook telemetry and reflection watermark preservation. Release all test workers
  in finally blocks.</action>
  <verify>./scripts/test.sh anansi/tests/test_worker.py -q</verify>
  <done>New contracts reproduce the defect before the repair.</done>
</task>

<task type="auto">
  <name>2. Implement shared admission and timeout cancellation</name>
  <files>anansi/appraisal.py, anansi/reflection.py, anansi/config.py</files>
  <action>Add the atomic helper and integrate both callers. Reset its tracking
  with the existing executor test reset. Update the timeout comments to distinguish
  cancelled pending work from a still-running request.</action>
  <verify>./scripts/test.sh anansi/tests/test_worker.py anansi/tests/test_appraisal.py anansi/tests/test_reflection.py -q</verify>
  <done>No background backlog through either production submission path; all
  affected regression checks pass.</done>
</task>

<task type="auto">
  <name>3. Verify and record the result</name>
  <files>CHANGELOG.md, .planning/DECISIONS.md, .planning/STATE.md, quick summary</files>
  <action>Run the canonical full gate, inspect the diff, document results and any
  pre-existing failures. Update quick-task tracking without advancing Phase 9.
  Leave changes uncommitted for Dr. Mani.</action>
  <verify>./scripts/test.sh; git diff --check</verify>
  <done>Tested implementation and outstanding release checks are distinguished
  in the summary; no live or published claim.</done>
</task>

## Baseline

Before behavioral edits, `./scripts/test.sh`: **198 passed, 1 failed** in 18.27s.
Failure: `test_persisted_flagged_priorities_survive_empty_signal_full_hook`, at
`anansi/tests/test_drive_neveromit.py:436`, expects every protected want to contain
`I want fresh progress on protected priority`. This is a pre-existing release-gate
failure, not permission to weaken the assertion or modify unrelated rendering.
