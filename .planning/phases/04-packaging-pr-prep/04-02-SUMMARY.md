# Plan 04-02 Summary

**Completed:** 2026-06-10 (~9:05pm EDT)
**Phase:** 4 — Packaging + Upstream PR Prep (final plan)

## What was built

The upstream-ready PR, prepared and stopped at the sign-off gate. PKG-03: upstream/main
fetched fresh (d1383a6b1 → `9dd9ef0ec99a87f078f7272b4323df5440b4b3f9`, one web-only
commit since planning); the parity diff vs baseline 183d86b3e across all four host
surfaces is EMPTY — `provides_hooks`, the `complete_structured` keyword-only signature
(superset of every kwarg the plugin passes), `PluginLlmTrustError`, and
`make_plugin_llm_for_test` all verified by fresh grep at the SHA (04-PARITY.md). PKG-02:
worktree `~/.hermes/worktrees/pr-anansi` on branch `feat/anansi-plugin`
at that SHA, with exactly one commit (`167be9f42bb339e323e8d8bddd7f62a8c68282d1`, 22 files,
+6364) adding only `plugins/anansi/*` (8 files) and
`tests/plugins/anansi/*` (14 files incl. the new `test_intree_layout.py`
manifest/discovery test modeled on the langfuse test). Suite green under upstream's own
pytest standards: **111 passed** (plugin suite, 107 + 4 layout tests) and **83 passed**
(`tests/hermes_cli/test_plugins.py` loader sanity), with `hermes_cli`/`agent`
probe-verified to import from the worktree (upstream-main code), not the editable
local-desktop-fixes install. PKG-04: PR_BODY.md (7-point content: what/safety/evidence/
limitations/parity/cross-refs/reviewer instructions, incl. the in-tree dry-run demo block
and the icarus-regex cross-reference) and 04-SIGNOFF.md (7 sections ending in the verbatim
STOP line) committed. **Nothing was pushed to any remote; no PR was opened.**

## Key files

- `.planning/phases/04-packaging-pr-prep/04-PARITY.md`: PR-time SHA, verbatim empty diff,
  manifest-key + complete_structured/trust-gate verdicts, PR_BODY conclusion sentence
- `.planning/phases/04-packaging-pr-prep/PR_BODY.md`: the literal upstream PR body
- `.planning/phases/04-packaging-pr-prep/04-SIGNOFF.md`: the single top-to-bottom sign-off
  artifact for Dr. Mani — diff stat, verbatim suite lines, inline PR body, fenced submit
  commands, STOP line
- Worktree `plugins/anansi/`: six source modules + plugin.yaml + README.md,
  copied byte-identical from the plugin repo
- Worktree `tests/plugins/anansi/`: full suite + fixtures + adapted conftest +
  new `test_intree_layout.py` (layout, manifest fields, discovered-but-not-loaded opt-in)

## Decisions made

- Worktree conftest registers the plugin as module `anansi` via
  `spec_from_file_location` + `submodule_search_locations`, registered in sys.modules
  BEFORE `exec_module` (module-identity rule held: nothing imports
  `plugins.anansi`); worktree root force-inserted at `sys.path[0]`
  (remove-then-insert) so the editable install of another branch can never shadow it.
- Test subpackage carries `__init__.py` (upstream `tests/` and `tests/plugins/` are both
  packages), so test modules live at `tests.plugins.anansi.*` — a distinct
  identity from the plugin module.
- `.devtools/pytest` staging wiped and re-staged at upstream's pins (pytest 9.0.2,
  pytest-timeout 2.4.0, pytest-asyncio 1.3.0); no extra dev dep was needed by upstream's
  tests/conftest.py at import time. Plugin-repo suite re-verified green (107) under the
  pinned staging.

## Deviations from plan

- The plan's grep for layout-relative paths (`parents[2]`/`parents[1]`) found
  `test_anticreep.py:38` (fixed to `parents[3] / "plugins" / "anansi"`, the
  langfuse-test idiom). Additionally, two test files (`test_anticreep.py`,
  `test_reflection_demo.py`) used `from conftest import ...`, which cannot resolve once
  the tests are a package — fixed in the worktree copies to `from .conftest import ...`
  (same-module relative import; covered by the plan's "fix it the same way" clause but
  beyond its grep, so recorded here). Plugin-repo originals untouched.
- None otherwise. Both `git push`/`gh pr create` strings exist only inside 04-SIGNOFF.md
  fenced code blocks; the in-action `git ls-remote origin feat/anansi-plugin`
  ran immediately after the worktree commit and again at close — empty both times.

## Notes for downstream

- The project is at the SIGN-OFF GATE: Dr. Mani reads 04-SIGNOFF.md top-to-bottom and
  either executes the two fenced commands or asks for changes (the plugin-rename open
  item in DECISIONS.md is cheapest before pushing).
- If upstream/main moves before submission, re-run the 04-PARITY diff command against
  the new tip (one command) and rebase the worktree branch if needed.
- The worktree copies of conftest.py + the two import lines intentionally diverge from
  the plugin-repo originals (in-tree layout adaptation) — any future sync of test changes
  into the worktree must preserve those three spots.
