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
