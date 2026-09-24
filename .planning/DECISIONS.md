# Decisions Register

## 2026-06-10 — Plugin renamed `anansi` → `anansi` (name collision with live plugin)

**Context:** Wave-1 execution halted at deploy: `$HERMES_HOME/plugins/anansi` already hosts a
LIVE, enabled plugin — "Anansi Metacognitive Guardrails" v0.1.0 (the separate anansi
self-correction project; hooks pre_tool_call/post_tool_call/transform_tool_result/on_session_end;
active guard config under `plugins.entries.anansi` in `~/.hermes/config.yaml:588-603`; state
modified same-day). No planning doc had been aware of it.

**Alternatives:**
1. Rename OUR plugin (chosen) — zero risk to live safety plugin; only touches brand-new uncommitted code + our own docs
2. Move the guardrails plugin aside — changes live safety behavior; requires Dr. Mani's explicit confirmation; rejected for autonomous execution

**Decision (self-answered under the 6-hour mandate):** plugin key/package = `anansi`;
state dir = `$HERMES_HOME/anansi/`; config key = `plugins.entries.anansi`.
Project title stays "Hermes Anansi Metacognition Plugin"; rendered sentinel stays `[anansi appraisal]`.
Dr. Mani may rename later (cost: dir + plugin.yaml name + enable key + docs sweep).

**Consequence:** all Phase-1+ docs/plans swept for the rename; executor re-run from scratch
(no commits had landed). The guardrails plugin was left untouched and verified still enabled.

## 2026-06-10 — R1–R3 roadmap revisions (from MEMORY-STACK-ANALYSIS-2026-06-10.md §6, Dr. Mani-accepted)

**R1 — SAFE-01 latency.** Original spec: hard deadline 2.5–3.0s. Live evidence (02-VALIDATION.md):
haiku appraisal is generation-bound at 4.4–7.3s; 2.5s times out 100%. Dr. Mani's decision
(2026-06-10): accept ~5s p50, max quality. New spec: configurable executor-bounded deadline,
**default 8.0s; p50 target ≤6s; zero retries** beyond trust-gate fallback. Accepted trade-off:
~5s serial pre-phase tax per eligible turn (suppression/throttle gates keep ineligible turns free).

**R2 — Reflection is the cross-lag carrier.** The one-turn memory lag (pre_llm_call fires before
memory prefetch) was accepted by Dr. Mani 2026-06-10 ("drop the ack issue"). Consequence:
Phase-3 reflection is not polish — it is the second half of the appraisal input contract, the
only channel by which memory-influenced context reaches future appraisals. Reflection inputs are
user messages + assistant response text + SQLite state; **never** the injected memory block,
which is ephemeral (appended at API-call time only, never persisted — conversation_loop.py:610-627).

**R3 — APPR-06 trust fallback: annotated, unchanged.** Mechanism unit-proven; unproducible live
here (host model ~37s/appraisal exceeds the deadline clamp → degrades to designed fail-open
timeout). Correct behavior for installs with faster host models. No code change.

## 2026-09-12 - Prevent timeout backlogs before increasing the wait

**Status:** Decision accepted by Dr. Mani; implemented in the uncommitted
`codex/clarify-appraisal-timeout` worktree. All 14 worker regression cases pass.
The full release gate still has one pre-existing failure; no live-test pass.

**Context:** `deadline_seconds` bounds the caller's wait, not cancellation of
the model request. Appraisal and reflection share one worker. The bounded live
diagnostic series produced two appraisal timeouts near eight seconds and one
process stopped after 55 seconds. A separate in-process check confirmed that a
queued request can execute after its caller has already timed out.

**Decision:** First, skip new appraisals while the worker is busy and cancel
expired queued work. Then investigate whether Hermes and the configured provider
connection can cancel a running request. Queued-work cancellation must not be
described as cancellation of a request that has already started.

**Accepted trade-off:** Some replies will proceed without fresh Anansi
observations while the worker is occupied. This approach prevents an accumulating
appraisal backlog; it does not free a worker whose running request remains stuck.

**Implementation:** GSD quick task `260912-cqc` checks Constitution Principles
I-VII and covers atomic worker admission, both shared callers, cancellation of
pending work and a worker-entry expiration guard. Busy reflection preserves
captured turns and the watermark, while retaining the established consumed
session-change trigger. This decision does not amend the constitution.

**Pending:** Repair the pre-existing nested-worktree Git discovery defect before
claiming a clean release gate. Commit, integration and further live verification
remain pending. Actual running-request cancellation support remains unverified.

**Deferred:** Additional workers and process isolation are not selected for the
initial repair. Increasing the timeout is not the selected backlog fix. Keep the
eight-second default and ten-second configuration ceiling unchanged for now;
the suggested 30-second diagnostic limit is not an implemented or validated
everyday setting. No further live-provider run is authorized by this record.

**Evidence:** Current call paths in [appraisal.py](../anansi/appraisal.py) and
[reflection.py](../anansi/reflection.py); the diagnostic results and Dr. Mani's
acceptance in this task; [quick-task verification](quick/260912-cqc-prevent-shared-appraisal-and-reflection-/260912-cqc-SUMMARY.md).
Earlier R1 records remain historical rationale for the default.
