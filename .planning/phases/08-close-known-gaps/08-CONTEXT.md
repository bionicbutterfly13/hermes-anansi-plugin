# Phase 8: Close Known Gaps - Context

Captured by the authorized GSD merge-mode intake on 2026-09-10.

<domain>
Reconcile and verify the eight known gaps against main, preserving fail-open and never-omit; account for the unmerged development branch.
Source: `specs/001-close-known-gaps/spec.md`.
</domain>

<decisions>
## Binding constraints
- Constitution Principles I-VII remain binding; classifier status grants no permission to amend them.
- Preserve the complete acceptance contract in `.planning/intel/requirements.md`, including user stories, edge cases, assumptions and SC IDs.
- Apply `.planning/INGEST-CONFLICTS.md`: flagged priorities cannot be withheld by a cap; interruption exceptions are not approved under the current constitution.
- Dependencies: Phase 7. Phase numbers alone add no dependencies.
- State: Pending; no implementation or completion implied.
</decisions>

<specifics>
Requirements: REQ-001-close-known-gaps-fr-001, REQ-001-close-known-gaps-fr-002, REQ-001-close-known-gaps-fr-003, REQ-001-close-known-gaps-fr-004, REQ-001-close-known-gaps-fr-005, REQ-001-close-known-gaps-fr-006, REQ-001-close-known-gaps-fr-007, REQ-001-close-known-gaps-fr-008, REQ-001-close-known-gaps-fr-009, REQ-001-close-known-gaps-fr-010, REQ-001-close-known-gaps-fr-011, REQ-001-close-known-gaps-fr-012.
Read `.planning/intel/SYNTHESIS.md` and per-type intel before planning.
</specifics>

<code_context>
Integration baseline: main 5413873f51447f70138717bc758851288e13b630.
Imported source: 001-close-known-gaps at af2a0bc3a45ceef3d37c15bba567e8f865879edc.
Its runtime commits are unmerged; checked tasks and historical tests need verification against the implementation selected for this phase.
</code_context>

<deferred>
No feature implementation, provider access, Hermes installation, commit or publication is authorized merely by this intake. Excluded source inputs remain listed in `.planning/GSD-MIGRATION.md`.
</deferred>
