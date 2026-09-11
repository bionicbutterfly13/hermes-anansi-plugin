# Changelog

## 2026-09-10 - Retired planning workflow removal

### Fixes

- Removed the retired framework directories and command references. The binding
  constitution now lives at `.planning/reference/CONSTITUTION.md`; 17 engineering reference
  documents live under `.planning/reference/`. Principles I-VII are unchanged.
- Updated GSD plans, manifest, extracted content, historical classification paths,
  synchronized repository instructions and the README backlog link. Historical
  reference task lists remain evidence only; GSD phase plans govern execution.
- Kept the existing four Phase 8 plans and all imported requirements. Original
  source and classifier bytes remain in Git history; normalized copies are
  explicitly identified. Plugin source and test code are unchanged.

### Learnings

- Changing the active workflow leaves stale source paths and commands in imported
  documents, plans and receipts. Removal must update those consumers together
  while preserving engineering rules and distinguishing historical test claims.

### Verification

- Scanned all 186 tracked and task-owned files present in this worktree: no retired
  framework paths, names or commands remain. All 18 manifest documents are present
  and fully represented in extracted intel; 46 requirements and seven acceptance
  contracts remain. Principles I-VII and platform constraints are byte-identical.
- Verified 93 existing plan references. Three future summary references have
  explicit producers in the four unexecuted Phase 8 plans.
- `./scripts/test.sh`: 165 passed in 4.31s. Plugin and test source are unchanged.
  GSD recognizes seven active phases and four unexecuted Phase 8 plans. Health has
  zero errors and the same five pre-existing advisories; no new advisory remains.

## 2026-09-10 - Phase 8 planning status repair

### Fixes

- Added GSD's documented Progress table for active phases 8-14 and canonical plan-position fields. The migrated heading-only roadmap produced an empty cache phase list, while custom status prose survived the planning transition.
- Regenerated `.planning/state.json` through the official `state.planned-phase` command. Phase 8 now has four recognized, unexecuted plans and the next-step route resumes that phase. Synchronized repository status notes.

### Learnings

- A successful state setter does not necessarily publish a new cache. Verify the persisted cache against the phase inventory after the workflow transition.
- GSD 1.13.0 can report "no recognized labels" on an already-correct no-op transition. The replay preserved the correct cache; that warning alone does not prove missing labels.
- The cache's `executing` category includes `Ready to execute`; it is not proof of execution. Its "Phase 8 of 7" display combines a retained phase identifier with an active-phase count. The authoritative ledger remains zero completed plans and seven active phases.

### Verification

- Reproduced the original missing-phase/wrong-next-step cache from the pre-repair records in an isolated replay.
- Verified the canonical transition, a stable repeat transition, seven active phase entries, and four plans with zero summaries for Phase 8.
- Planning health reports zero errors. Existing filename advisories and an idle-main-worktree advisory remain; they do not authorize deleting provenance or the canonical checkout.
- Verified 54 source and phase-artifact hashes unchanged. No plugin runtime or installed GSD code changed.

## 2026-09-10 - GSD migration and legacy planning ingestion

### Features

- Prepared active GSD planning files and seven source-mapped future phases from
  18 tracked legacy planning documents. Preserved 46 functional requirements, 29 success
  criteria, 25 user stories and complete attributed source blocks.
- Preserved the previous planning state and repository instructions in a dated
  historical snapshot. Original inputs were unchanged at intake; the cleanup entry above normalizes their paths and workflow text.

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
