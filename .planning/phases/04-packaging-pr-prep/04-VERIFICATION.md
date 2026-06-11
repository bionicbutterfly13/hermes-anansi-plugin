---
phase: 4
status: passed
verified: 2026-06-10
verifier_note: "All test counts re-run fresh, not taken from the summaries: 107 (plugin repo), 111 + 83 (worktree under upstream addopts, module-resolution probe re-confirmed worktree shadowing). Parity diff and all four 04-PARITY.md line-number claims reproduced at 9dd9ef0ec. Zero-push verified three ways (ls-remote empty, upstream push DISABLED, no matching PR in the author's upstream PR list, state=all). The phase ends at the sign-off gate by design — that is criterion 3 satisfied, not a pending check."
---

# Phase 4: Packaging + Upstream PR Prep — Verification

**Goal:** Contributable artifact — in-tree layout, docs, upstream-main parity — gated on
sign-off.

## Test Suite

```
$ ./scripts/test.sh                                      # plugin repo
107 passed in 7.42s

$ cd ~/.hermes/worktrees/pr-anansi && \
  PYTHONPATH="$PWD:<repo>/.devtools/pytest" <venv-py> -m pytest tests/plugins/anansi -q
111 passed, 1 warning in 18.47s                          # 107 plugin + 4 in-tree layout tests

$ ... -m pytest tests/hermes_cli/test_plugins.py -q
83 passed, 1 warning in 31.60s                           # host loader sanity
```

All three re-run fresh at verification time (2026-06-10 ~9:10pm EDT). The worktree runs
execute from the worktree root, so upstream's `pyproject.toml` addopts apply
(`-m 'not integration' --timeout=30 --timeout-method=thread`, pyproject.toml:335 —
`--timeout` would be an unrecognized flag without the staged pytest-timeout, so the green
runs prove the addopts were in effect). Module-resolution probe re-run: `hermes_cli` and
`agent` both import from the WORKTREE (`.../pr-anansi/hermes_cli/__init__.py`,
`.../pr-anansi/agent/__init__.py`), confirming upstream-main code shadowed the
editable local-desktop-fixes install. Growth 105 → 107 in the repo (telemetry vocabulary
test + PKG-01 manifest test), +4 in-tree (`test_intree_layout.py`, run standalone:
4 passed). Both working trees clean.

## Success Criteria (ROADMAP Phase 4)

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Plugin installs cleanly in both layouts | ✓ | **Standalone:** `~/.hermes/plugins/anansi` → `/Volumes/Asylum/repos/hermes-anansi-plugin/anansi` (readlink verified); live config has `anansi` in `plugins.enabled` AND `plugins.entries.anansi.enabled: true` (config.yaml:591/:605-606). **In-tree:** worktree `plugins/anansi/` holds exactly the 6 source modules + plugin.yaml + README.md, all 8 byte-identical to the plugin repo (diff -q, 8/8 identical); `test_intree_layout.py` 4/4 green (layout, manifest fields, opt-in discovery) inside the 111-test run and standalone |
| 2 | `pip_dependencies: []` verified; suite passes to host standards on upstream main | ✓ | PKG-01 test pair run directly: `test_pkg01_manifest_zero_deps_and_accurate_hooks` + `test_safe04_import_allowlist` — 2 passed; `plugin.yaml` (both copies) shows `pip_dependencies: []`, `kind: standalone`, `provides_hooks` = the four registered hooks. Worktree suite 111 passed at upstream/main 9dd9ef0ec under upstream's own addopts; loader sanity 83 passed alongside. Commit scope: `git diff upstream/main...HEAD --name-only` filtered against `plugins/anansi/` + `tests/plugins/anansi/` leaves ZERO files; exactly one commit (167be9f42, 22 files, +6364, parent = 9dd9ef0ec) |
| 3 | PR branch + PR_BODY.md ready; submission blocked pending Dr. Mani sign-off | ✓ | Branch `feat/anansi-plugin` exists in the worktree at the recorded base. PR_BODY.md complete per the 04-02 7-point checklist (see Plan Must-Haves). 04-SIGNOFF.md has all 7 sections ending in the verbatim STOP line. **Zero-push proven three ways at verification time:** `git ls-remote origin feat/anansi-plugin` → empty; `git remote -v` → `upstream DISABLED (push)`; `gh pr list --repo NousResearch/hermes-agent --author bionicbutterfly13 --state all` → no PR with head `feat/anansi-plugin` |

## Requirement Coverage

| Req ID | Deliverable | Status |
|--------|-------------|--------|
| PKG-01 | Manifest test (`test_anticreep.py::test_pkg01_manifest_zero_deps_and_accurate_hooks`: `pip_dependencies == []`, kind/name, `provides_hooks` set-equal to AST-collected `register_hook` names) + `test_safe04_import_allowlist` (import-side half, cross-referenced in the docstring) — both run directly, 2 passed | ✓ |
| PKG-02 | Standalone: live symlink + enabled config (criterion 1). In-tree: worktree arrangement proven by 111-test run incl. 4 layout/discovery tests. Docs: `anansi/README.md` — config-block greps hit `reflect_deadline_seconds`/`reflect_every_n_turns`/`history_chars` (3), WAL sidecar idiom `state.db-wal` (1), sub-session note (4 hits); ships byte-identical in-tree; thin repo-root README.md exists | ✓ |
| PKG-03 | 04-PARITY.md records PR-time SHA `9dd9ef0ec99a87f078f7272b4323df5440b4b3f9` + verdicts. Independently reproduced: parity diff vs 183d86b3e across all four surfaces re-run → EMPTY; `git show 9dd9ef0ec` greps confirm `provides_hooks` (plugins.py:245/:1386), `PluginLlmTrustError` (:249), `complete_structured` (:683), `make_plugin_llm_for_test` (:1016) — every line number in 04-PARITY.md matches | ✓ |
| PKG-04 | PR prepared, NOT submitted: PR_BODY.md + 04-SIGNOFF.md committed (d713892); submit commands exist only inside 04-SIGNOFF.md fenced blocks; STOP line verbatim; nothing on any remote (criterion 3 proofs) | ✓ |

## Plan Must-Haves

| Plan | Must-Have | Status |
|------|-----------|--------|
| 04-01 | telemetry_summary vocabulary: reflect_ok/reflect_skipped:* non-failures in BOTH the comprehension (store.py:622-623) and last_error SQL (:627-629); docstring updated (:598-604); exclusion-list shape kept | ✓ |
| 04-01 | New mixed-outcome test asserting `failure_count == 2` with reflect_timeout as last_error (test_telemetry_store.py:205-218) green in suite | ✓ |
| 04-01 | PKG-01 manifest test + SAFE-04 allowlist cross-reference, both green (run directly: 2 passed) | ✓ |
| 04-01 | `anansi/README.md` complete (8-section greps hit); repo-root README.md exists | ✓ |
| 04-01 | Suite green ≥106 (107), offline | ✓ |
| 04-01 | Live symlink untouched and resolving; three commits (87484eb, 1a49dbb, 5a9e751) | ✓ |
| 04-02 | 04-PARITY.md: PR-time SHA, verbatim empty diff, provides_hooks + complete_structured/trust-gate verdicts — all reproduced independently | ✓ |
| 04-02 | Worktree branch at recorded SHA, exactly one commit touching only the two prefixes | ✓ (log count 1; filtered name-only empty; HEAD~1 = 9dd9ef0ec) |
| 04-02 | Plugin suite + layout test green under upstream addopts, worktree shadowing the editable install; tests/hermes_cli/test_plugins.py green | ✓ (111 + 83 re-run; probe re-confirmed) |
| 04-02 | PR_BODY.md per 7-point checklist: (1) what — opt-in standalone, complete_structured, sentinel block, reflection, SQLite WAL, zero deps ✓; (2) safety posture — fail-open law, anti-creep, kill switch ✓; (3) evidence — 111 count, p50 5563.5ms, 6/6 + 0/3 FP, cross-session 1/1, parallel timeouts, dry-run demo block, telemetry distribution ✓; (4) honest limitations — all four ✓; (5) parity note with SHA ✓; (6) icarus-regex cross-ref + post_memory_prefetch future work ✓; (7) reviewer instructions — enable, README pointer, test commands ✓ | ✓ |
| 04-02 | 04-SIGNOFF.md 7 sections in order (header, diff stat, suite proof, parity, inline PR body, fenced submit commands, STOP line verbatim); diff stat matches my reproduction (22 files, +6364) | ✓ |
| 04-02 | ZERO pushes: ls-remote empty; upstream push DISABLED; no PR opened (gh checked, state=all) | ✓ |
| 04-02 | hermes-agent main tree clean on `local-desktop-fixes`; plugin-repo suite still green; `.devtools/` gitignored (.gitignore:4) and absent from the worktree | ✓ |

## Integration Checks

| Link | Check | Status |
|------|-------|--------|
| In-tree source ↔ repo source | All 8 files byte-identical (diff -q) | ✓ |
| Worktree conftest adaptation | `parents[3]` repo root force-inserted at sys.path[0] (remove-then-insert, conftest.py:18-21); `spec_from_file_location` + sys.modules registration before exec (:24-31); the two `from .conftest import` fixes present in test_anticreep.py:35 / test_reflection_demo.py:26 (recorded 04-02 deviation) | ✓ |
| Worktree base | HEAD~1 = `9dd9ef0ec...` = `git rev-parse upstream/main` = the SHA in 04-PARITY.md, 04-SIGNOFF.md, and PR_BODY.md (consistent across all three artifacts) | ✓ |
| Manifest | In-tree plugin.yaml: name/kind/four provides_hooks/`pip_dependencies: []` — the loader-read key per the reproduced plugins.py:1386 grep | ✓ |
| Commits | 04-01: 87484eb, 1a49dbb, 5a9e751; 04-02: 401a32b, d713892 (+ summaries 3a16400, cde8fd1; plan-hardening 50bf35c) — all present, both trees clean | ✓ |

## Summary

**Score:** 13/13 plan must-haves verified; 3/3 success criteria pass; 4/4 requirements
(PKG-01..04) traceable to tests, artifacts, and independently reproduced evidence.

All automated checks passed. Phase goal achieved: the plugin is contributable in both
layouts (live standalone install verified enabled; in-tree arrangement green to upstream's
own test standards at the freshly verified upstream/main SHA), the zero-dependency claim is
proven by tests rather than assertion, parity holds byte-identical from the Phase-1
baseline through the PR-time SHA, and the PR is fully prepared — branch, body, sign-off
artifact — with zero pushes, verified three independent ways.

The project now sits at the designed SIGN-OFF GATE: Dr. Mani reads 04-SIGNOFF.md
top-to-bottom and either executes the two fenced commands or requests changes.

### Non-blocking observations

1. **REQUIREMENTS.md checkboxes for PKG-01..04 are still `[ ]`** — verifier does not modify
   REQUIREMENTS.md; the post-verification flip is the orchestrator's transition step (same
   flow as Phases 2 and 3).
2. **04-SIGNOFF.md section 7 heading is bare (`## 7.`)** — cosmetic; the STOP line below it
   is verbatim per the plan.
3. **Suite wall-times differ from the 04-02 run** (111 in 18.47s vs recorded 6.70s; 83 in
   31.60s vs 14.35s) — counts identical; timing variance only, likely concurrent load.
4. **"`~/.hermes/plugins/anansi` never entered" is reported by the summaries** and honored by
   this verification (never accessed), but is not independently provable post-hoc; the
   adjacent checkable facts (symlink target, clean trees, commit scope) all hold.
5. **If upstream/main moves before submission**, the 04-PARITY diff re-run is one command
   (recorded in 04-02-SUMMARY notes); the DECISIONS.md plugin-rename open item is cheapest
   before pushing.
