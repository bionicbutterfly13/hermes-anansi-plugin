# Hermes Anansi Metacognition Plugin

## What This Is

A Hermes hook plugin that supplies observational metacognitive appraisal and local
SQLite state. Its implemented foundation and limitations are documented in
`README.md`; historical phase artifacts record the development evidence.

## Core Value

Ground appraisal in persisted state and user priorities while preserving fail-open
turn handling and the prohibition on autonomous action.

## Active Workflow

GSD is the active planning workflow as of 2026-09-10,
authorized by Dr. Mani. Use `$gsd-progress`, then the relevant GSD phase workflow.
`.planning/PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md` and `STATE.md` are the active
planning surface. Phase contexts carry imported decisions and constraints.

The constitution lives at `.planning/reference/CONSTITUTION.md`; 17 imported engineering
documents live under `.planning/reference/`. Their extracted content remains in
`.planning/intel/`. Retired workflow commands and paths were normalized to GSD
on 2026-09-10 at Dr. Mani's direction. Principles I-VII and acceptance criteria
are preserved. Reference task lists describe historical branch work; only plans
under `.planning/phases/` form the active execution queue.

## Binding Engineering Decisions

Read `.planning/reference/CONSTITUTION.md` before every non-trivial change.

- Fail-open remains mandatory, including failures introduced by new paths.
- Output remains observational: no directives, autonomous tools, memory-provider
  writes or turn gating.
- Persisted flagged priorities must not be omitted or erased to satisfy a cap.
- Use the single SQLite surface and read freshness-critical ground truth at read time.
- Add no plugin dependencies; resolve paths from configuration/environment.
- Keep drive pressure adjustable, inspectable and separate from the neutral read.
- Make minimal changes and verify actual behavior; never weaken assertions to pass.

The imported classifier's `locked: false` reflects the absence of the literal
status marker `Accepted`, not permission to change a ratified constitution.
These decisions remain binding by Dr. Mani's governing instruction.

## Current Milestone

Reconcile and verify the imported backlog against the integration baseline.
Phase 8 addresses the known gaps; Phase 9 preserves the agreed worldview-first
sequence, then episodes/autobiography and user-dopamine. Phase 10 captures bounded
reconsolidation/heartbeat. Later scope and its gates remain in Phases 11-14.

The source interruption exceptions in Phase 11 remain deferred under constitution
precedence. Source cap requirements in Phase 8 must be reconciled without
withholding flagged priorities. See `.planning/INGEST-CONFLICTS.md` for both
precedence resolutions; source text is retained even where it cannot authorize
implementation.

## Requirements

The active ledger is `.planning/REQUIREMENTS.md`: 46 imported functional
requirements remain pending, with Phase 11 deferred under constitution precedence.
Their full acceptance contracts retain 29 success criteria and 25 user stories in
`.planning/intel/requirements.md`. Historical v1 checkmarks remain explicitly
separate from current verification. No feature is completed by this migration.

## Evidence and Branch Boundaries

- Integration baseline: main `5413873f51447f70138717bc758851288e13b630`.
- Imported source: `001-close-known-gaps` at
  `af2a0bc3a45ceef3d37c15bba567e8f865879edc`.
- This intake does not merge that branch's runtime changes. Its checked tasks and
  recorded test results are not current-main completion evidence.
- The old active planning files and instructions are preserved under
  `.planning/milestones/pre-gsd-2026-09-10/`. Existing phase evidence, decisions,
  research and solutions remain available as history.
- Phase 5's missing summary is unresolved historical evidence, not newly fabricated
  completion. Deferred untracked inputs are listed in `.planning/GSD-MIGRATION.md`.

## Quality and Publication Gates

Run `./scripts/test.sh` for plugin implementation changes and appropriate targeted
checks for planning-only changes. Live-provider behavior requires separate live
evidence; neither a unit-test count nor setup success establishes it.

The repository is public by Dr. Mani's direction. Commit, push and upstream
submission still require their applicable explicit authorization. Automatic GSD
document commits and phase advancement are disabled for this intake.

## Historical Context

Historical technical rationale remains in `.planning/DECISIONS.md`, existing
phase contexts and `.planning/research/`. Explicit Phase 6 supersession governs
bounded future heartbeat/user-dopamine work; it does not authorize autonomous
outreach, a new memory provider, background daemons or a privilege ladder.
