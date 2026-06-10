# Phase 1 Discussion Log — Skeleton + State

**Date:** 2026-06-10
**Mode:** Autonomous (Dr. Mani's 6-hour self-answer mandate). Each "choice" below was selected by
the agent following the workflow's own recommendation discipline; grounding cited per decision.
Dr. Mani can override any of these — they re-enter planning via `plan-phase 1` re-run.

## Area 1: Package layout

Options considered:
- (a) Single `__init__.py` monofile — simplest, but Phase 2/3 growth makes it icarus-sized (1000+ lines)
- (b) `__init__.py` + `store.py`, more modules later — **CHOSEN (recommended)**: hooks/registration
  separate from state; matches "minimal now, grows clean"
- (c) Full package scaffold (appraisal.py, render.py, etc. now) — speculative; violates Nothing Extra

Deployment options:
- (a) Develop directly in `$HERMES_HOME/plugins/anansi` — untracked, mixes runtime with source
- (b) Repo + symlink into `$HERMES_HOME/plugins/` — **CHOSEN**: icarus-adjacent precedent; keeps git
  clean; the mnemosyne incident was about import-time sys.path mutation, not symlinks per se
- (c) In-tree hermes-agent worktree now — premature; that's Phase 4's PR arrangement

## Area 2: SQLite schema shape

- (a) Generic `observations(type, payload_json)` table — flexible but caps/decay unenforceable per type
- (b) Explicit tables per signal type — **CHOSEN (recommended)**: REQUIREMENTS STATE-01 names them;
  per-table caps/decay; queryable telemetry
- Schema-change policy: (a) alembic-style migrations — overkill; (b) quarantine-and-recreate on any
  mismatch — **CHOSEN**: state is advisory/disposable (STATE-03 already locks this for corruption;
  extended to version mismatch)

## Area 3: DB location

- (a) `$HERMES_HOME/plugins/anansi/data.db` — inside the (symlinked) plugin dir; would land in the repo
- (b) `$HERMES_HOME/anansi/state.db` — **CHOSEN (recommended)**: mirrors hindsight's profile-scoped
  `$HERMES_HOME/hindsight/` pattern; per-profile isolation for free; survives plugin reinstall
- (c) `~/.anansi/` shared global — breaks profile isolation (the desktop profile-isolation trap taught
  us profile-scoped state matters here)

## Area 4: Hook skeleton surface

- (a) Register only hooks Phase 1 exercises — minimal but defers dispatch proof
- (b) All three hooks as guarded no-ops — **CHOSEN (recommended)**: proves the full dispatch surface
  (incl. the None-return no-injection path) before any logic exists; fail-open guard becomes
  scaffolding from day one rather than a Phase-3 retrofit

## Delegated to Agent's Discretion
- Exact cap numbers (seed: concerns ≤20, contradictions ≤50, turn_log ≤500)
- Column details, logger naming, test layout, meta table format

## Deferred ideas
- Direct-Hindsight-recall option (post-v1)
- `ctx.register_auxiliary_task` evaluation (Phase 2)
