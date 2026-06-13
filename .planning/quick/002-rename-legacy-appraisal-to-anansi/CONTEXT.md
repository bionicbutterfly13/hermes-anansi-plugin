# Quick Task 002: Scrub legacy naming after Anansi rename - Context

**Gathered:** 2026-06-13
**Status:** Ready for planning

<domain>
## Task Boundary

Scrub remaining legacy naming from the Anansi plugin repository after the runtime rename. This pass covers planning artifacts, research notes, quick-task records, and local project metadata.

</domain>

<decisions>
## Implementation Decisions

### Runtime identity
- Use `anansi` as the active package, plugin manifest name, config key, state directory, test import path, and user-facing sentinel.
- Remove old-name namespaces from code, tests, scripts, docs, and current agent-facing instructions.

### Legacy handling
- Do not keep an old-name runtime migration bridge; the final working tree should contain no old-name text.
- Do not keep a compatibility import package or old plugin alias; the new runtime identity is `anansi`.

### Safety and scope
- Preserve the existing fail-open behavior, hook names, SQLite-only local state, and zero new dependency posture.
- Do not touch unrelated dirty files: `.planning/phases/04-packaging-pr-prep/04-PARITY.md`, `.planning/phases/04-packaging-pr-prep/PR_BODY.md`, or `.serena/`.
- Historical references are rewritten too; this repository should present Anansi consistently.

</decisions>

<specifics>
## Specific Ideas

- Active state path becomes `$HERMES_HOME/anansi/state.db`.
- Active config key becomes `plugins.entries.anansi`.
- Active rendered block sentinel becomes `[anansi appraisal]`.
- Active debug env var becomes `ANANSI_DEBUG_DUMP`.

</specifics>
