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
