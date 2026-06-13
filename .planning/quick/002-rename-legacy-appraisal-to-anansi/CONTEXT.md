# Quick Task 002: Rename legacy anansi identity to Anansi - Context

**Gathered:** 2026-06-13
**Status:** Ready for planning

<domain>
## Task Boundary

Rename the active plugin/runtime identity from the legacy v1 `anansi` / Anansi wording to `anansi` / Anansi. This is a runtime namespace rename, not only a docs rename.

</domain>

<decisions>
## Implementation Decisions

### Runtime identity
- Use `anansi` as the active package, plugin manifest name, config key, state directory, test import path, and user-facing sentinel.
- Remove active `anansi` namespaces from code, tests, scripts, docs, and current agent-facing instructions.

### Legacy handling
- Keep narrowly scoped legacy migration references only where needed to preserve an existing `$HERMES_HOME/anansi/state.db` state database.
- Do not keep a compatibility import package or old plugin alias; the new runtime identity is `anansi`.

### Safety and scope
- Preserve the existing fail-open behavior, hook names, SQLite-only local state, and zero new dependency posture.
- Do not touch unrelated dirty files: `.planning/phases/04-packaging-pr-prep/04-PARITY.md`, `.planning/phases/04-packaging-pr-prep/PR_BODY.md`, or `.serena/`.
- Avoid changing historical source-project references where "Anansi" means the old upstream/source system rather than this plugin namespace.

</decisions>

<specifics>
## Specific Ideas

- Active state path becomes `$HERMES_HOME/anansi/state.db`.
- Active config key becomes `plugins.entries.anansi`.
- Active rendered block sentinel becomes `[anansi appraisal]`.
- Active debug env var becomes `ANANSI_DEBUG_DUMP`.

</specifics>
