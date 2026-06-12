# Phase 5: Proprietary Pivot State Reconciliation - Research

**Researched:** 2026-06-12
**Phase goal:** Restore learnship routing after the proprietary pivot: reconcile state with the withdrawn PR, expose the next proprietary discussion phase, and account for interrupted quick-task residue.

## Don't Hand-Roll

| Problem | Recommended solution | Why |
|---------|----------------------|-----|
| PR withdrawal state | Use the existing Phase 4 signoff withdrawal record plus GitHub's closed-PR/branch semantics as the factual boundary. Confidence: HIGH. Source: `.planning/phases/04-packaging-pr-prep/04-SIGNOFF.md`; GitHub Docs: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-branches-in-your-repository/deleting-and-restoring-branches-in-a-pull-request | A closed PR with a deleted branch is not a pending upstream gate. The planner should preserve the local evidence: PR #43906 was closed with withdrawal comment and the fork branch was deleted/verified empty. |
| Planning-state reconciliation | Reuse learnship's existing source-of-truth surfaces: `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/v1.0-MILESTONE-AUDIT.md`, phase discussion/context files. Confidence: HIGH. Source: local artifacts | Phase 5 is documentation/state cleanup. New scripts, new routing mechanisms, or code changes would create another source of truth and increase drift. |
| Decision/rationale capture | Reuse the existing `.planning/DECISIONS.md` style only if Phase 5 records a new durable decision; otherwise cite 05-DISCUSSION-LOG and DESIGN-REWIND. Confidence: MEDIUM. Source: 2026 ADR research: https://arxiv.org/abs/2604.27333 and https://arxiv.org/abs/2604.03826 | Recent ADR research favors concise decision records and shows that recent historical context improves decision-record quality. The local project already has concise decision entries; do not invent a new format. |
| Change accounting | Use the project's phase summary/verification conventions and, if a changelog exists later, Keep a Changelog categories. Confidence: MEDIUM. Source: https://keepachangelog.com/en/1.1.0/ | This repo currently has no `CHANGELOG.md`. Do not create a changelog just for Phase 5 unless the plan explicitly scopes it; account for the cleanup in the phase summary instead. |
| Empty quick-task residue | Prefer explicit scoped handling: either document it as harmless empty residue or remove only the known empty path if the plan chooses that. Confidence: HIGH. Source: Git docs: https://git-scm.com/docs/git-clean | `git clean` is intentionally broad and removes untracked files recursively when forced. For this phase, broad cleanup risks touching unrelated dirty files (`04-PARITY.md`, `PR_BODY.md`, `.serena/`). |

## Common Pitfalls

### Pitfall 1: Letting Phase 5 become proprietary feature design

**Confidence:** HIGH

**What goes wrong:** The planner starts designing the layered autobiographical user model, aligned drive, goals, heartbeat, user-dopamine, worldview store, or reconsolidation sweeps inside Phase 5.

**Why:** The proprietary pivot documents contain rich design material, and the empty quick-task path is named `001-add-phase-5-proprietary-user-model`, which can pull the phase toward implementation.

**How to avoid:** Treat `DESIGN-REWIND-2026-06-10.md` and `USER-MODEL-SOURCES-2026-06-10.md` as Phase 6 seed material only. Phase 5 success should be routing correctness: v1 stands, PR #43906 is withdrawn, and the next workflow is `discuss-phase 6` or equivalent proprietary discussion.

### Pitfall 2: Updating one planning artifact and leaving another stale

**Confidence:** HIGH

**What goes wrong:** `STATE.md` says Phase 5 is current, while `ROADMAP.md`, the milestone audit, or the phase summaries still imply Phase 4 PR signoff is pending.

**Why:** The audit explicitly found a cross-artifact project-management flow gap, not a code gap.

**How to avoid:** Plan a small consistency pass over only the relevant planning surfaces: `STATE.md`, `ROADMAP.md`, the milestone audit, and the Phase 5 summary/verification artifact. The wording should preserve the exact historical sequence: PR #43906 submitted, then withdrawn by Dr. Mani's decision on 2026-06-10, fork branch deleted, plugin proprietary, no upstream submission pending.

### Pitfall 3: Treating audit cleanup as broad repo cleanup

**Confidence:** HIGH

**What goes wrong:** The executor cleans untracked/dirty files beyond Phase 5, especially `.planning/phases/04-packaging-pr-prep/04-PARITY.md`, `.planning/phases/04-packaging-pr-prep/PR_BODY.md`, or `.serena/`.

**Why:** `git status` currently contains unrelated dirty state, and cleanup tasks often invite broad `git clean` or formatting passes.

**How to avoid:** The plan should list allowed files exactly. If residue handling is needed, target only `.planning/quick/001-add-phase-5-proprietary-user-model/` after confirming it is still empty, or document it as residue. Do not use broad cleanup commands. Git's own documentation frames `git clean` as recursive removal of untracked files from the working tree when forced: https://git-scm.com/docs/git-clean.

### Pitfall 4: Re-opening the upstream contribution lane

**Confidence:** HIGH

**What goes wrong:** The plan preserves language like "awaiting signoff", "PR prep", or "upstream submission pending", which causes learnship routing to point back to Phase 4.

**Why:** Phase 4 really did prepare and submit the PR before the pivot, so old signoff language can look authoritative unless superseded.

**How to avoid:** Make Phase 4 complete-with-withdrawal, not pending. GitHub docs support the lifecycle distinction: branches associated with closed or merged pull requests can be deleted, while open pull requests block branch deletion. Source: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-branches-in-your-repository/deleting-and-restoring-branches-in-a-pull-request.

### Pitfall 5: Recording the proprietary pivot as a new v1 requirement

**Confidence:** HIGH

**What goes wrong:** Phase 5 adds requirement IDs or reopens v1 coverage despite the audit showing 31/31 v1 requirements satisfied.

**Why:** The pivot is important, but it is governance/routing work, not plugin behavior.

**How to avoid:** Keep Phase 5 mapped to "audit gap closure - no new v1 requirement IDs." Any proprietary capability belongs to Phase 6 or a later milestone after discussion.

### Pitfall 6: Over-documenting with a new process format

**Confidence:** MEDIUM

**What goes wrong:** The planner adds new documentation systems, ADR templates, or changelog machinery during cleanup.

**Why:** Decision-log hygiene is relevant, and 2026 ADR literature emphasizes documentation quality, but this repo already has a working learnship pattern.

**How to avoid:** Use the existing pattern: phase context, discussion log, plan, summary/verification, and `.planning/DECISIONS.md` only for durable new decisions. Recent ADR studies are useful as support for concise rationale capture, not as a reason to migrate formats. Sources: https://arxiv.org/abs/2604.27333 and https://arxiv.org/abs/2604.03826.

## Existing Patterns in This Codebase

- **Phase context as binding input:** Phase plans open with "Read before implementing (binding)" and cite the phase context plus decision register. Phase 5 should do the same with `05-CONTEXT.md`, `05-DISCUSSION-LOG.md`, the milestone audit, and the Phase 4 withdrawal section.
- **Explicit must-haves:** Prior plans use frontmatter `must_haves` and exact allowed files. For Phase 5, must-haves should be phrased as state/routing assertions, not code behavior.
- **Locked-decision language:** Phase 3 and Phase 4 plans treat context decisions as locked and avoid re-litigating accepted constraints. Phase 5 should lock "cleanup only" and "Phase 6 owns proprietary design."
- **Dirty-state boundaries:** The milestone audit explicitly names unrelated dirty files and interrupted quick-task residue. Phase 5 should preserve that boundary and avoid touching unrelated files.
- **Decision register style:** `.planning/DECISIONS.md` records context, alternatives, decision, and consequence. If Phase 5 adds a decision, it should follow that style and remain concise.
- **Audit as source of truth:** `.planning/v1.0-MILESTONE-AUDIT.md` already establishes that v1 requirements are satisfied and only integration/flow gaps remain. The planner should use it as the reason Phase 5 exists.
- **Proprietary design seed docs:** `DESIGN-REWIND-2026-06-10.md` and `USER-MODEL-SOURCES-2026-06-10.md` should be referenced as deferred Phase 6 inputs, not Phase 5 implementation material.

## Recommended Approach

Plan Phase 5 as a single cleanup slice over planning artifacts only. The plan should reconcile learnship routing away from the obsolete Phase 4 PR signoff gate, preserve the audit finding that v1 requirements are complete, and route next to a separate proprietary Phase 6 discussion.

The executor should touch only files explicitly named by the plan, with special care around existing unrelated dirty files. The final summary should state that PR #43906 was submitted, withdrawn on 2026-06-10, the fork branch was deleted, no upstream plugin submission remains pending, and proprietary user-model/drive work is deferred to Phase 6.
