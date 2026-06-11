# Plan 04-01 Summary

**Completed:** 2026-06-10 (~8:50pm EDT)
**Phase:** 4 — Packaging + Upstream PR Prep

## What was built

The contributable-on-paper layer: the 03-VERIFICATION carry-in fix landed
(`telemetry_summary` no longer mislabels `reflect_ok`/`reflect_skipped:*` as failures —
failure vocabulary is now exactly `timeout`/`llm_error`/`parse_fail`/`reflect_timeout`/
`reflect_llm_error`/`reflect_parse_fail`, exclusion-list shape kept so unknown future
outcomes still count; `last_error` follows the same definition; `p50_wall_ms` stays
appraisal-only). PKG-01 became provable by one test run: a new manifest test in
test_anticreep.py asserts `pip_dependencies == []`, `kind == standalone`,
`name == anansi`, and `provides_hooks` set-equal to the AST-collected
`ctx.register_hook` names in `__init__.py`, cross-referencing
`test_safe04_import_allowlist` as the import-side half. The canonical plugin README
(8 sections: overview/non-goals, both install layouts, full config block with
defaults+clamps, outcome vocabulary + telemetry_summary semantics, WAL sidecar copy
idiom, sub-session honesty, R1/R2/R3 limitations with the live timeout ratio,
state+privacy) plus a thin repo-root README. Suite 105 → 107, green at every commit.

## Key files

- `anansi/store.py`: telemetry_summary vocabulary fix (docstring + failure
  comprehension + last_error SQL — both places, kept in sync)
- `anansi/tests/test_telemetry_store.py`: new mixed-outcome test
  (`failure_count == 2`, `last_error` = the reflect_timeout row, p50 from the ok row only)
- `anansi/tests/test_anticreep.py`: `test_pkg01_manifest_zero_deps_and_accurate_hooks`
  (+ module-top `import yaml` — test-side only, PyYAML 6.0.3 in the hermes venv)
- `anansi/README.md`: canonical plugin README — ships verbatim into the
  in-tree arrangement (`plugins/anansi/README.md`) in 04-02
- `README.md`: thin repo doc (what this repo is, `./scripts/test.sh`, symlink deploy
  idiom, pointer to the plugin README)

## Decisions made

- PKG-01 cross-check asserts **set equality** between manifest `provides_hooks` and the
  AST-collected `register_hook` names (stronger than the plan's minimum "every listed
  hook appears" — also catches registered-but-undeclared hooks); AST scan chosen to
  match the module's existing static-proof style.
- README documents the full grep-verified skip-reason vocabulary
  (`skipped:disabled|no_ctx|empty|social_close|duplicate`,
  `reflect_skipped:disabled|no_ctx|no_turns|debounce|db_locked`) rather than a sample.
- "Writes confined to the reflection pass" phrased precisely in the README:
  belief-state writes only via `store.apply_deltas` inside reflection; bookkeeping
  writes (post_llm_call turn capture, telemetry rows) named honestly instead of
  overclaiming a read-only hot path.

## Deviations from plan

- None functional. Task-1 step 4 ("sweep existing summary tests for assertions encoding
  the old definition") found nothing to update: the lone pre-existing summary test seeds
  appraisal-only outcomes, so its assertions are identical under both vocabularies — it
  was left untouched (minimal-change rule).

## Notes for downstream

- 04-02: `anansi/README.md` is written to ship unchanged in-tree; its in-tree
  section deliberately does not overpromise (the arrangement is proven by 04-02). The
  PKG-01 manifest test + allowlist test are the "verify pip_dependencies: []" half of
  ROADMAP criterion 2; the upstream-main suite run is 04-02's.
- Suite count is now 107 (105 + telemetry vocabulary test + PKG-01 manifest test), all
  offline; test_anticreep.py now needs PyYAML at test time (venv-provided; plugin
  modules remain stdlib + host surfaces only — the allowlist scan covers plugin modules,
  not tests).
- Live deploy untouched: `~/.hermes/plugins/anansi` symlink still resolves;
  `~/.hermes/plugins/anansi` never entered. The only behavior change live sessions see is
  the corrected `telemetry_summary` derived view.
