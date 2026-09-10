# Changelog

## 2026-09-10 - GSD migration and Spec Kit ingestion

### Features

- Prepared active GSD planning files and seven source-mapped future phases from
  18 tracked Spec Kit documents. Preserved 46 functional requirements, 29 success
  criteria, 25 user stories and complete attributed source blocks.
- Preserved the previous planning state and repository instructions in a dated
  historical snapshot. Original Spec Kit inputs remain unchanged.

### Fixes

- Reconciled phase headings/state and project configuration with the maintained
  GSD runtime. Repository instructions now agree on the active workflow.
- The external Codex GSD installation was updated from the retired package
  lineage to `@opengsd/gsd-core@1.13.0`. A separately retained local prompt repair
  distinguishes document navigation from explicit dependency cycles. It is not
  a change to Anansi runtime code or an upstream release fix.

### Learnings

- A no-update result only establishes currency for the package queried.
- A plan listing itself or its future task ledger does not create a prerequisite
  cycle. Actual dependency and locked-decision conflicts must still block.
- Schema-valid summaries can omit acceptance criteria and concrete contracts.
  Complete source-content coverage was verified before active planning changed.
- Source branch checkmarks and test counts are historical evidence, not proof
  that the integration branch implements or correctly verifies those changes.
