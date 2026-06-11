# Sign-Off: anansi Upstream PR — Submitted

**Prepared:** 2026-06-10 (~9:00pm EDT); refreshed and submitted 2026-06-10 (~10:15pm EDT)
**Branch:** `feat/anansi-plugin` (one commit: `832d52b88d8bfe2747ed3919160fefcf814bb255`)
**Worktree:** `/Users/manisaintvictor/.hermes/worktrees/pr-anansi`
**Base:** upstream/main @ `3ffbdfbcc0dce5b859411666677e0f86d583dda0` (fetched fresh, rebased cleanly before submission)
**Target:** NousResearch/hermes-agent, via fork bionicbutterfly13/hermes-agent-lab
**PR:** https://github.com/NousResearch/hermes-agent/pull/43906
**Pushed:** YES — fork branch `bionicbutterfly13:feat/anansi-plugin` points at `832d52b88d8bfe2747ed3919160fefcf814bb255`; upstream push remains DISABLED.

---

## 1. Completion criteria

This sign-off task is complete only when all of the following are true from live evidence:

1. Upstream `main` has been fetched immediately before submission; the PR branch is rebased
   on that tip, with `HEAD~1 == upstream/main`.
2. The parity diff from Phase-1 baseline `183d86b3e` through the submission base is empty
   across `hermes_cli/plugins.py`, `agent/plugin_llm.py`,
   `tests/agent/test_plugin_llm.py`, and `plugins/`.
3. The PR branch diff touches only `plugins/anansi/` and
   `tests/plugins/anansi/`, with the expected 22-file stat.
4. The plugin repo suite, in-tree plugin suite, and host loader sanity suite pass after the
   rebase.
5. `PR_BODY.md` references the same upstream base SHA as this sign-off file.
6. The branch is pushed to `bionicbutterfly13/hermes-agent-lab`, and a PR exists against
   `NousResearch/hermes-agent:main` from `bionicbutterfly13:feat/anansi-plugin`.
7. Upstream push remains disabled; no direct push to `NousResearch/hermes-agent` occurs.

## 2. Diff stat (verbatim, `git diff upstream/main...HEAD --stat` in the worktree)

```
 plugins/anansi/README.md                  | 182 +++++
 plugins/anansi/__init__.py                | 214 ++++++
 plugins/anansi/appraisal.py               | 497 +++++++++++++
 plugins/anansi/config.py                  | 158 +++++
 plugins/anansi/plugin.yaml                |  11 +
 plugins/anansi/reflection.py              | 769 +++++++++++++++++++++
 plugins/anansi/render.py                  | 209 ++++++
 plugins/anansi/store.py                   | 658 ++++++++++++++++++
 tests/plugins/anansi/__init__.py          |   0
 tests/plugins/anansi/conftest.py          | 138 ++++
 .../anansi/fixtures/contradictions.json   | 145 ++++
 tests/plugins/anansi/test_anticreep.py    | 387 +++++++++++
 tests/plugins/anansi/test_appraisal.py    | 303 ++++++++
 tests/plugins/anansi/test_dryrun_demo.py  | 135 ++++
 .../anansi/test_failopen_matrix.py        | 482 +++++++++++++
 .../plugins/anansi/test_intree_layout.py  |  94 +++
 tests/plugins/anansi/test_pre_llm_call.py | 212 ++++++
 tests/plugins/anansi/test_reflection.py   | 573 +++++++++++++++
 .../anansi/test_reflection_demo.py        | 256 +++++++
 .../anansi/test_reflection_store.py       | 367 ++++++++++
 tests/plugins/anansi/test_store.py        | 256 +++++++
 .../anansi/test_telemetry_store.py        | 318 +++++++++
 22 files changed, 6364 insertions(+)
```

Nothing outside `plugins/anansi/` and `tests/plugins/anansi/` is touched
(`git diff upstream/main...HEAD --name-only` filtered against those two prefixes: empty).

## 3. Suite proof (upstream pytest standards: `-m 'not integration' --timeout=30 --timeout-method=thread`)

Plugin suite in the worktree (107 plugin tests + 4 new in-tree layout/discovery tests):

```
$ cd /Users/manisaintvictor/.hermes/worktrees/pr-anansi && \
  PYTHONPATH="$PWD:/Volumes/Asylum/repos/hermes-anansi-plugin/.devtools/pytest" \
  ~/.hermes/hermes-agent/venv/bin/python -m pytest tests/plugins/anansi -q
111 passed, 1 warning in 7.71s
```

Host loader sanity (proves the arrangement doesn't disturb the loader's own tests):

```
$ cd /Users/manisaintvictor/.hermes/worktrees/pr-anansi && \
  PYTHONPATH="$PWD:/Volumes/Asylum/repos/hermes-anansi-plugin/.devtools/pytest" \
  ~/.hermes/hermes-agent/venv/bin/python -m pytest tests/hermes_cli/test_plugins.py -q
83 passed, 1 warning in 11.34s
```

(The 1 warning in each run is a third-party `audioop` DeprecationWarning from the venv's
discord package — unrelated to this change.) Module-resolution probe under the same
PYTHONPATH confirmed `hermes_cli` and `agent` import from the WORKTREE (upstream-main
code), shadowing the editable install of the local-desktop-fixes branch. Dev tooling
(pytest 9.0.2 / pytest-timeout 2.4.0 / pytest-asyncio 1.3.0 — upstream's pins) is staged
in the plugin repo's gitignored `.devtools/pytest`; the hermes venv was not modified.

Plugin repo suite:

```
$ cd /Volumes/Asylum/repos/hermes-anansi-plugin && ./scripts/test.sh
107 passed in 4.19s
```

## 4. Parity

upstream/main moved d1383a6b1 → 9dd9ef0ec between planning and PR prep, then
9dd9ef0ec → 3ffbdfbcc before submission. The parity diff vs the Phase-1 baseline
183d86b3e across all four surfaces
(`hermes_cli/plugins.py`, `agent/plugin_llm.py`, `tests/agent/test_plugin_llm.py`,
`plugins/`) is EMPTY at 3ffbdfbcc; `provides_hooks` is still the loader-read manifest key
(plugins.py:1386) and the `complete_structured` keyword-only signature is a superset of
every kwarg the plugin passes. Full evidence: `04-PARITY.md`.

## 5. PR body (full inline copy of PR_BODY.md)

---

# feat(plugins): add anansi — observational metacognitive appraisal (opt-in, zero deps, fail-open)

## What this is

`anansi` is a bundled `kind: standalone` plugin (opt-in, like langfuse and
disk-cleanup) that gives the agent a per-turn metacognitive appraisal with **zero
capacity for autonomous action**:

- One host-owned `ctx.llm.complete_structured` JSON-mode call per eligible turn
  (`pre_llm_call`), schema-constrained to observational noun fields (instincts,
  observations, contradiction flags, suggested memory searches, gut reaction).
- The result renders as a sentinel-prefixed observational block injected into the
  **user message context only** — never the system prompt, never a directive.
- A debounced, idempotent reflection pass (`on_session_start` / `on_session_end`)
  consolidates captured turns into persistent concerns/contradictions/trust scores,
  carrying appraisal context across sessions.
- State is SQLite (WAL) under `$HERMES_HOME/anansi/`, with capped tables,
  lazy decay, and a quarantine-recreate policy on schema mismatch or corruption
  (state is disposable by design).
- `pip_dependencies: []` — stdlib + host surfaces only, enforced by an AST
  import-allowlist test (`test_anticreep.py::test_safe04_import_allowlist`) and a
  manifest cross-check that asserts `provides_hooks` set-equal to the
  AST-collected `ctx.register_hook` names.

Example injected block (from the offline forced-injection demo,
`tests/plugins/anansi/test_dryrun_demo.py -s` — note the planted
prompt-injection string comes out neutralized):

```
[anansi appraisal]
advisory observational signals; not instructions; do not act on these beyond informing your response
- instinct: caution (0.8) — user is changing a live system during an outage
- instinct: protect (0.6) — state data has no backup mentioned
- observation: the migration topic recurs across sessions (confidence 0.85)
- observation: [REDACTED] and [REDACTED] (confidence 0.95)
- observation: user prefers terse confirmations (confidence 0.75)
- contradiction (narrative): claimed migration was done yesterday, now debugging it (confidence 0.8)
- contradiction (semantic): offline-only constraint vs request for live API calls (confidence 0.7)
- possible memory searches: 'migration rollback decision'; 'outage timeline'
- gut reaction: tense but tractable; verify before touching live state
```

## Safety posture

- **Fail-open is law.** The appraisal call runs in a single-worker executor under a
  configurable deadline (default 8.0s, clamped to [0.5, 10.0]); every failure path —
  timeout, LLM error, parse failure, locked/corrupt/absent DB, missing config —
  produces an empty injection plus a telemetry row. No hook code path raises into
  the dispatcher. A 30-row fail-open matrix test
  (`test_failopen_matrix.py`) pins every case.
- **Anti-creep suite.** Structural directive-language checks run on every rendered
  block (no imperatives, observational label allowlist); static scans assert no tool
  execution, no memory-provider strings, no turn gating, and an import allowlist of
  stdlib + host surfaces.
- **Opt-in with a kill switch.** The plugin is discovered but not loaded unless
  enabled (standard bundled-standalone behavior, pinned by the discovery test), and
  `plugins.entries.anansi.enabled: false` short-circuits to zero LLM calls
  (verified live: `skipped:disabled` telemetry row, no model call, injected block
  byte-unchanged). Zero behavior change unless enabled.

## Evidence (from live validation, 2026-06-10)

- **Hermetic suite:** 111 passed in-tree at upstream/main `3ffbdfbcc` (107 plugin
  tests + 4 layout/discovery tests), fully offline, under this repo's pytest config
  (`-m 'not integration' --timeout=30 --timeout-method=thread`).
- **Latency (live, anthropic `claude-haiku-4-5`):** appraisal p50 5563.5ms over the
  validation run's ok rows — within the 8.0s deadline and the p50 ≤ 6s target.
  Reflection passes ran 2.8–7.7s at session boundaries (p50 4.25s, all within
  deadline).
- **Contradiction fixtures:** 9-case fixture set (semantic / narrative / relational /
  emotional + 3 no-contradiction controls), one real model call per case: 6/6
  detection (confidences 0.91–0.99), **0/3 false positives** on controls. Kind labels
  are advisory — the model over-applies semantic/narrative — so nothing branches on
  exact kind.
- **Cross-session loop (the headline):** a session-A contradiction (JWT-vs-opaque-
  tokens stated as simultaneous "final decisions") was reflected into state and
  surfaced in session B's appraisal block **on attempt 1/1**, quoting the persisted
  contradiction and the reflection-written trust score (0.38). One-turn-lag loop
  demonstrated end-to-end, live.
- **Fail-open under load:** the host spawned two parallel sub-sessions whose
  appraisals both hit the 8.0s deadline simultaneously (`timeout|8006` ×2) — both
  failed open and the user-visible turn completed intact.
- **Telemetry distribution** (live validation DB, 32 rows):
  `ok 6 · reflect_ok 8 · reflect_skipped:debounce 8 · reflect_skipped:no_turns 4 ·
  skipped:social_close 4 · timeout 2` — one row per hook firing, the two timeouts
  being the parallel sub-session appraisals above.

## Honest limitations

- **One-turn lag (deliberate).** `pre_llm_call` fires before memory prefetch, so the
  appraisal sees the message, recent history, and persisted state — not this turn's
  memory results. The reflection pass carries appraisal context across the lag; see
  future work below for the hook that would close it.
- **Sub-session hook traffic.** The host runs the full hook set per sub-session, so
  one user turn that spawns N sub-sessions multiplies appraisal/reflection traffic;
  parallel appraisals on a cheap lane can contend into fail-open timeouts (observed
  live, fail-open held). Documented in the plugin README.
- **Deadline/latency trade-off.** Cheap-tier models generate 400–480 output tokens
  per appraisal (4.4–7.3s on haiku); sub-second appraisal is not achievable with the
  full schema. The default deadline is 8.0s; the appraisal rides a configurable model
  lane (`llm.model` + `allowed_models`).
- **Trust-fallback on slow host models.** When model override is denied, the
  fallback retries on the host's active model; if that model can't finish inside the
  deadline clamp (observed: ~37s on a large model), every appraisal degrades to a
  fail-open timeout — operationally "appraisal off," turns unaffected. The
  `trust_fallback` path itself is unit-proven.

## Parity

Built and tested against upstream/main at
`3ffbdfbcc0dce5b859411666677e0f86d583dda0` (2026-06-10 refresh). All host surfaces the
plugin depends on — the plugin loader's `provides_hooks` manifest key, the
`ctx.llm.complete_structured` keyword-only signature, `PluginLlmTrustError`, and
`make_plugin_llm_for_test` — are unchanged since first verification at `183d86b3e`;
no adaptation was needed.

## Cross-references

- **icarus injection-regex gap (separate fix, offered):** while building the render
  sanitizer (derived from icarus's patterns) we found the original regex misses
  `ignore previous instructions` when "all" is absent (it required "ignore all
  previous instructions"), and lacks a system-prompt-exfiltration pattern. Both are
  fixed in this plugin's sanitizer; happy to send the icarus fix as a separate PR.
- **Future work (not in this PR):** a `post_memory_prefetch` host hook would let the
  appraisal see this turn's memory results and close the one-turn lag. Mentioning
  only — no host changes are part of this PR.

## For reviewers

- **Enable:** `hermes plugins enable anansi` (or add `anansi` to
  `plugins.enabled` in config.yaml). Full config reference — model lane, deadline,
  thresholds, reflection keys, kill switch — is in
  `plugins/anansi/README.md`.
- **Run the suite:** `python -m pytest tests/plugins/anansi -q`
  (offline; no API keys needed — the LLM is faked via `make_plugin_llm_for_test`).
- **See a block offline:** `python -m pytest tests/plugins/anansi/test_dryrun_demo.py -q -s`

---

*(end of PR body)*

## 6. Submit commands (executed)

```bash
# 1. Push the branch to the fork (origin = bionicbutterfly13/hermes-agent-lab):
git -C /Users/manisaintvictor/.hermes/worktrees/pr-anansi push -u origin feat/anansi-plugin

# 2. Open the PR against upstream:
gh pr create --repo NousResearch/hermes-agent \
  --head bionicbutterfly13:feat/anansi-plugin \
  --title "feat(plugins): add anansi — observational metacognitive appraisal (opt-in, zero deps, fail-open)" \
  --body-file /Volumes/Asylum/repos/hermes-anansi-plugin/.planning/phases/04-packaging-pr-prep/PR_BODY.md
```

Submission notes:
- The base branch on NousResearch/hermes-agent is `main`; the prepared branch is based
  at `3ffbdfbcc...` (current main at submission time).
- A possible rename of the plugin is now post-submission PR churn; this artifact preserves
  the submitted `anansi` name.

## 7. Final state checks (submitted)

- `git ls-remote origin feat/anansi-plugin` → `832d52b88d8bfe2747ed3919160fefcf814bb255`
- `gh pr view 43906 --repo NousResearch/hermes-agent` → OPEN, non-draft, base `main`, head `bionicbutterfly13:feat/anansi-plugin`, commit `832d52b88d8bfe2747ed3919160fefcf814bb255`, mergeStateStatus `BLOCKED`
- `git remote -v` in ~/.hermes/hermes-agent → upstream push DISABLED (unchanged)
- hermes-agent main working tree clean on `local-desktop-fixes`
- Live symlink `~/.hermes/plugins/anansi` → plugin repo (intact); `~/.hermes/plugins/anansi` never entered
- Plugin-repo suite green (`./scripts/test.sh`)

## 8. Submitted

Submitted upstream PR: https://github.com/NousResearch/hermes-agent/pull/43906

---

## 8. WITHDRAWN (2026-06-10 ~10:20pm EDT, Dr. Mani's decision)

PR #43906 CLOSED with withdrawal comment; branch `feat/anansi-plugin` DELETED from the
fork (ls-remote verified empty). The plugin is now PROPRIETARY — no upstream contribution of the
plugin itself. Local worktree and all code retained. Design rewind underway:
see `.planning/research/DESIGN-REWIND-2026-06-10.md`.
