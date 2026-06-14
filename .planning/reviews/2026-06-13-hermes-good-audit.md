# Hermes `/good` Audit — stored 2026-06-13

> **Provenance:** External audit deposited by Dr. Mani ("from hermes for storage"), 2026-06-13,
> during `discuss-phase 6`. **Stored verbatim. Findings NOT yet actioned.**
> Routing plan for actionable items is at the bottom — execute via `/quick` AFTER the
> Phase 6 discussion closes. Do not start proprietary implementation from this review
> (the audit's own item #7).

---

## 1. What's good

- Test suite is green: `./scripts/test.sh` returned `107 passed in 7.29s`.
- Graphify was available and ran successfully:
  - `graphify update . --no-cluster`
  - generated `graphify-out/graph.json`
  - graphify reported 1061 nodes, 1235 edges
  - multigraph diagnostic found no duplicate same-endpoint collapse risk: `directed_same_endpoint_collapsed_edges: 0`.
- The plugin boundary is clean:
  - `anansi/plugin.yaml:1-11` declares `kind: standalone`, four hooks, and `pip_dependencies: []`.
  - `anansi/README.md:9-11` states zero new deps, zero autonomy, fail-open behavior.
- Core hook design is thin and auditable:
  - `anansi/__init__.py:34-60` wraps hooks in fail-open handling.
  - `anansi/__init__.py:92-160` keeps `pre_llm_call` ordered: config kill switch, throttle, snapshot, appraisal, telemetry, render.
  - graphify confirms `run_appraisal()` connects to `parse_signals()`, `build_context()`, `AppraisalResult`, and `_get_executor()`.
- Safety tests are meaningful, not decorative:
  - `anansi/tests/test_anticreep.py:238-261` scans for forbidden APIs like memory-provider writes, tool execution, subprocess, raw config writes, eval, exec.
  - `anansi/tests/test_anticreep.py:160-224` includes negative controls proving the directive-language checker can fail.
- Planning state is mostly explicit:
  - `.planning/STATE.md:7-15` says v1 is verified, PR path withdrawn, and next workflow is Phase 6 design discussion.
  - `.planning/ROADMAP.md:72-82` maps 31/31 v1 requirements as covered.

## 2. What's broken

- Repo status is now dirty because `/good` generated graphify output:
  - `git status --short` shows `?? graphify-out/`.
  - `.gitignore:1-5` does not ignore `graphify-out/`.
  - Not a code failure, but a workflow failure if graphify output is meant to be ephemeral.
- Project status files disagree:
  - `AGENTS.md:169-172` says Phase 5, status planning, last updated 2026-06-12.
  - `.planning/STATE.md:7-15` says current focus is Phase 6, Phase 5 cleanup complete, next workflow `discuss-phase 6`.
  - Will mislead future agents because AGENTS.md is loaded as repo instruction.
- No live plugin smoke was run in this `/good` pass.
  - Offline tests passed.
  - Did not run `scripts/live_smoke.py`; not claiming live Hermes install, provider trust gate, latency, or enabled-plugin wiring works right now.
- Graphify report is partial:
  - Ran no-cluster AST update, not full semantic extraction.
  - There is `graphify-out/graph.json`, but no `GRAPH_REPORT.md`.
  - Graphify evidence is structural, not semantic/LLM-clustered.

## 3. What pretends to work but doesn't

- "All tests green" does not mean "live appraisal works."
  - The suite is offline/fake-LLM by design: `anansi/README.md:178-182`.
  - Good for determinism, but does not prove live model auth, model override trust, network, or p50 latency.
- `scripts/live_smoke.py` can exit 0 on network failure:
  - `scripts/live_smoke.py:50-54` prints pending-network and returns success.
  - User-friendly, but automation could misread it as a real live-pass unless it checks stdout.
- Config fallback can make malformed config look healthy:
  - `anansi/config.py:3-6` says unreadable/malformed config falls back to defaults.
  - `anansi/config.py:39-48` defaults include `DEFAULT_ENABLED = True`.
  - A broken or misspelled config can therefore still "work" by silently using defaults.
- Planning status pretends to be canonical in two places:
  - `.planning/STATE.md` appears current.
  - `AGENTS.md` still advertises older Phase 5 status.
  - Agents reading AGENTS first can route work against stale phase state.
- Graphify can look like a complete graph report but currently is not:
  - Structural graph exists and is useful.
  - No clustering/semantic report was generated.
  - Treat it as code topology evidence only.

## 4. What works that shouldn't

- Malformed or missing config still enables the plugin by default.
  - Protects user turns from config crashes, but can preserve appraisal calls when the operator thought config disabled or changed them.
  - Safer: fail-open for the turn, but make config degradation visible in telemetry/doctor.
- `live_smoke.py` returning exit 0 for pending network works too smoothly.
  - Good for manual workflow; bad for CI/automation because "could not test" and "passed" share the same exit code.
- `graphify-out/` can be generated into the repo without ignore/commit policy.
  - Works because graphify writes locally; should not leave accidental untracked state unless this repo intentionally tracks graph artifacts.
- The fail-open doctrine is correct, but it can hide health loss.
  - Hooks swallowing failures is required for not hurting turns.
  - But without an external health summary, failures can accumulate as "everything seems fine" until telemetry is inspected.

## 5. Prioritized ranked solutions (as received)

1. **Fix status drift between AGENTS.md and .planning/STATE.md** — sev high / leverage high / blast low. Verify: both files agree Phase 6 is next/current. Fix: update AGENTS/CLAUDE current-phase block to Phase 6 or make it defer to `.planning/STATE.md`.
2. **Decide graphify artifact policy** — sev med / leverage high / blast low. Verify: `git status --short` clean after policy. Options: commit `graphify-out/graph.json`, or add `graphify-out/` to `.gitignore`.
3. **Add a live-verification lane distinct from offline tests** — sev high / leverage high / blast med. Verify: a command proving actual Hermes plugin load + one real/explicitly-mocked live-compatible turn. Distinguish passed / pending-network / auth-failed / plugin-not-enabled / timeout.
4. **Change live_smoke.py automation semantics** — sev med / leverage med / blast low. Verify: network-down path exits distinct code or supports `--ci` that fails on pending-network. Keep manual-friendly behavior; CI must not treat "untested" as pass.
5. **Surface config fallback as telemetry/diagnostic evidence** — sev med / leverage med / blast med. Verify: malformed `plugins.entries.anansi` produces a visible telemetry/config-health warning without breaking turns. Don't necessarily change fail-open; make the fallback legible.
6. **Generate a fuller graphify report when doing architectural review** — sev low / leverage med / blast low. Verify: produce `GRAPH_REPORT.md` or equivalent semantic/cluster artifact.
7. **Keep Phase 6 behind Learnship discussion** — sev med / leverage high / blast low. Verify: `/ls` or `.planning/STATE.md` points to `discuss-phase 6`. Do not start proprietary user-model/drive implementation from this status review; route through the planned discussion phase.

---

## Routing plan (to execute AFTER Phase 6 discussion — not now)

| Audit item | Route | Notes |
|---|---|---|
| #1 status drift (AGENTS.md Phase 5 vs STATE.md Phase 6) | `/quick` | Smallest, highest-leverage. AGENTS.md current-phase block should defer to STATE.md or read Phase 6. |
| #2 graphify-out policy | `/quick` | Decision needed: ignore vs track. Default recommendation: `.gitignore` it (ephemeral analysis artifact). |
| #3 live-verification lane | own `/quick` or fold into a future phase | Larger; design a status-distinguishing live lane. |
| #4 live_smoke.py CI semantics | `/quick` | Add distinct exit code / `--ci` flag. |
| #5 config-degradation telemetry | `/quick` | Make fallback legible without changing fail-open. |
| #6 fuller graphify report | ad-hoc | Only when doing architectural review. |
| #7 keep Phase 6 gated | n/a | Already honored — this discussion IS the gate. |
