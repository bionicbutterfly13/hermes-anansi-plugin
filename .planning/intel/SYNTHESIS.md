# Synthesis

## Documents consumed

- ADR: 1
- PRD: 7
- SPEC: 5
- DOC: 5
- Total: 18

## Decisions

- Locked decisions: 0
- Proposed decisions: 1
- Source: .specify/memory/constitution.md
- Coverage: full 117-line constitution, including Principles I–VII, additional constraints, development workflow, and governance, is preserved in decisions.md.

## Requirements

- Extracted: 46
- IDs: REQ-001-close-known-gaps-fr-001 through REQ-001-close-known-gaps-fr-012; REQ-002-autobiographical-user-model-fr-001 through REQ-002-autobiographical-user-model-fr-008; REQ-003-reconsolidation-and-heartbeat-fr-001 through REQ-003-reconsolidation-and-heartbeat-fr-007; REQ-004-interruption-lanes-fr-001 through REQ-004-interruption-lanes-fr-005; REQ-005-tuning-and-audit-surfaces-fr-001 through REQ-005-tuning-and-audit-surfaces-fr-004; REQ-006-deferred-v1-and-parity-fr-001 through REQ-006-deferred-v1-and-parity-fr-006; REQ-007-drive-security-verification-fr-001 through REQ-007-drive-security-verification-fr-004.
- Acceptance contracts: 7 feature-scoped entries, each preserving its full source PRD verbatim.
- Coverage: all 46 FR IDs; all 29 feature-qualified SC IDs; all 25 user stories and their numbered acceptance scenarios; edge cases, assumptions, dependencies, and out-of-scope qualifiers from all seven PRDs.

## Constraints

- Extracted: 5
- schema: 2
- protocol: 3
- Coverage: full source content preserved for all five SPEC documents (288 source lines).

## Context topics

- Extracted: 5
- Coverage: full source content preserved for all five DOC documents (430 source lines).

## Dependency graph

- Explicit dependencies: specs/003-reconsolidation-and-heartbeat/spec.md → specs/002-autobiographical-user-model/spec.md; specs/004-interruption-lanes/spec.md → specs/003-reconsolidation-and-heartbeat/spec.md; specs/005-tuning-and-audit-surfaces/spec.md → specs/003-reconsolidation-and-heartbeat/spec.md.
- Cycles: 0
- Maximum traversal depth: 3 of 50
- Navigation-only cross references, including self-references and reciprocal plan/task links, were not dependency edges.

## Existing context check

- .planning/phases/06-proprietary-user-model-drive-design/06-CONTEXT.md:14-16,88-104 explicitly supersedes the older v1 heartbeat exclusion for a bounded later direction; it does not claim current implementation.
- Source implementation, checklist, and test claims are feature-branch or historical claims, not evidence that main implements them.

## Conflicts

- Blockers: 0
- Competing variants: 0
- Auto-resolved: 2
- Detail: .planning/INGEST-CONFLICTS.md

## Intel files

- decisions.md
- requirements.md
- constraints.md
- context.md
