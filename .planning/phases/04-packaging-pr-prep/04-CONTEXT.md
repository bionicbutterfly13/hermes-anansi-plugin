# Phase 4: Packaging + Upstream PR Prep - Context

**Gathered:** 2026-06-10
**Mode:** standard (autonomous — gate answers pre-staged in MEMORY-STACK-ANALYSIS-2026-06-10.md §6 under Dr. Mani's 4-hour mandate)
**Status:** Ready for planning

<domain>
## Phase Boundary

Contributable artifact: dual-layout packaging, docs, upstream-main parity re-verification, PR branch
+ PR_BODY.md. Requirements PKG-01..04. **The run PREPARES the PR; it NEVER submits** — submission
only after Dr. Mani sign-off (standing directive; same flow as Hindsight PR #2117 today: diff + PR
body presented, explicit approval before push-to-PR). NO new features; carry-in polish items from
03-VERIFICATION are in scope only where listed below.

</domain>

<decisions>
## Implementation Decisions

### Target + push mechanics (analysis §6, locked)
- Target repo: NousResearch/hermes-agent; branch from **current upstream main** (not the local
  0.16.0 fork branch, which carries 7 PRs of divergence)
- Push via fork **bionicbutterfly13/hermes-agent-lab** ONLY — upstream push is disabled on this
  machine by design; verify the remote config before any push
- PKG-04 sign-off gate: prepare branch + PR_BODY.md, present diff + body to Dr. Mani, STOP

### Dual layout (PKG-02)
- Standalone: `$HERMES_HOME/plugins/anansi` (current symlink deploy keeps working —
  do not break the live install)
- In-tree: hermes-agent's plugin layout (`plugins/` — check how icarus or other in-tree plugins
  are arranged upstream and match it)
- Docs include the `plugins.entries.anansi` config block (llm lane, enabled,
  confidence_threshold, deadline_seconds 8.0 default, reflection keys) + install instructions for
  both layouts
- Doc the WAL sidecar inspection idiom (03-VERIFICATION observation: copying state.db without
  -wal/-shm fails SQLITE_CANTOPEN; copy all three)
- Doc the sub-session behavior honestly (host runs full hook set per sub-session; parallel
  appraisals can contend into fail-open timeout — observed live, fail-open held)

### Parity re-check (PKG-03)
- Fetch upstream main fresh at PR time; re-verify `provides_hooks` manifest key + `ctx.llm`
  facade surface (complete_structured signature, trust gate) — was verified at 183d86b3e, MUST
  re-verify at the actual PR-time SHA
- Run the full suite against the upstream-main arrangement (in-tree layout) to host standards

### PKG-01 zero-dep proof
- `pip_dependencies: []` in plugin.yaml verified + a test/static check asserting stdlib + host
  surfaces only (the SAFE-04 AST import-allowlist already proves this — reference it)

### PR_BODY.md sources (analysis §6)
- 02-VALIDATION.md + 03-VALIDATION.md evidence (live blocks, fixture detection 6/6 0FP, p50 5563ms,
  cross-session loop proof attempt 1/1)
- Dry-run demo transcript; telemetry summary
- The icarus-regex bug cross-reference (recorded in HANDOFF upstream-candidates)
- Honest limitations section: one-turn lag (deliberate, reflection carries context), sub-session
  hook traffic, deadline/latency trade-off (R1), trust-fallback degraded path on slow hosts (R3)

### Carry-in polish (from 03-VERIFICATION, in scope)
- `telemetry_summary` vocabulary: count reflect_* outcomes correctly (not as failures) —
  small store.py fix + test; everything else in telemetry stays as-is
- No other code changes — Phase 4 is packaging; resist scope creep

### Agent's Discretion
- README structure; PR_BODY length/tone; whether in-tree arrangement uses a copy or restructured
  tree in a packaging/ dir; test-layout adaptation details for upstream standards

</decisions>

<specifics>
## Specific Ideas

- Mirror the #2117 sign-off artifact pattern: a single file Dr. Mani can read top-to-bottom
  (diff stat + PR body + how-to-submit commands) saved in the repo
- Upstream PR candidate cross-references to note in PR_BODY or keep for separate PRs:
  `post_memory_prefetch` hook (D5 salvage) — mention as future work, do not implement
</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

- `.planning/research/MEMORY-STACK-ANALYSIS-2026-06-10.md` §6 phase-4 pre-answers + §7 ledger
- `.planning/phases/03-failopen-reflection/03-VERIFICATION.md` — carry-in observations
- `.planning/phases/02-appraisal-path/02-VALIDATION.md` + `03-failopen-reflection/03-VALIDATION.md` — PR evidence
- `.planning/REQUIREMENTS.md` PKG-01..04
- `~/.hermes/hermes-agent` — local checkout (branch local-desktop-fixes; upstream = NousResearch/hermes-agent, fork remote = bionicbutterfly13/hermes-agent-lab); READ-ONLY except for creating the PR branch/worktree per plan
- Today's sign-off precedent: Hindsight PR #2117 flow (issues #2114/#2115)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Full plugin at repo root `anansi/` — 105-test suite, ./scripts/test.sh idiom
- SAFE-04 static scans (import allowlist) double as the PKG-01 zero-dep proof

### Integration Points
- plugin.yaml manifest (kind: standalone, provides_hooks, pip_dependencies)
- Live deploy symlink must keep working throughout (Dr. Mani's sessions use it)

</code_context>

<deferred>
## Deferred Ideas

- `post_memory_prefetch` upstream hook PR (D5 salvage) — separate contribution, future
- Plugin rename decision (anansi vs other) — Dr. Mani may rename at PR review
</deferred>

---
*Phase: 04-packaging-pr-prep*
*Context gathered: 2026-06-10*
