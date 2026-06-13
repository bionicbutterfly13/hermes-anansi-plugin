---
wave: 1
depends_on: []
files_modified:
  - anansi/
  - scripts/test.sh
  - scripts/live_smoke.py
  - scripts/live_contradiction_fixtures.py
  - README.md
  - AGENTS.md
  - CLAUDE.md
  - .planning/quick/002-rename-anansi-to-anansi/002-SUMMARY.md
autonomous: true
single_layer_justified: true
objective: "Rename the active plugin/runtime identity from anansi to Anansi while preserving behavior and migration safety."
must_haves:
  truths:
    - "The active Python package directory is `anansi/`, and no active `anansi/` package remains."
    - "The plugin manifest name is `anansi` and config lookup uses `plugins.entries.anansi`."
    - "The state store resolves `$HERMES_HOME/anansi/state.db` and has a narrow legacy migration path from the old v1 state location."
    - "The rendered sentinel is `[anansi appraisal]`."
    - "`./scripts/test.sh` passes."
  artifacts:
    - anansi/plugin.yaml
    - anansi/__init__.py
    - anansi/store.py
    - anansi/tests
  key_links:
    - "README.md points to `anansi/README.md`."
    - "AGENTS.md and CLAUDE.md no longer describe the active plugin source as `anansi/`."
---

# Plan 002: Rename Runtime Identity to Anansi

<objective>
This plan renames the active plugin namespace, config key, state path, docs, tests, and scripts from the legacy anansi identity to Anansi. Behavior stays the same: hook lifecycle, fail-open discipline, SQLite storage, no new dependencies, and test surfaces remain intact. A narrow legacy state migration path preserves existing local state without keeping an old plugin alias.
</objective>

## Tasks

<task id="002-01">
<title>Rename runtime package and plugin identity</title>
<files>
- anansi/
- scripts/test.sh
- scripts/live_smoke.py
- scripts/live_contradiction_fixtures.py
</files>
<action>
Move `anansi/` to `anansi/`. Update Python imports, plugin id strings, manifest name, logging namespaces, thread names, debug env var, active config key, active state path, rendered sentinel, live scripts, and test paths to use `anansi` / `[anansi appraisal]`. In `anansi/store.py`, add a narrowly scoped legacy migration helper that moves an existing `$HERMES_HOME/anansi/state.db` and WAL sidecars to `$HERMES_HOME/anansi/state.db` only when the new DB does not exist.
</action>
<verify>
`rg -n "anansi|\\[anansi appraisal\\]|ANANSI|plugins\\.entries\\.anansi|\\$HERMES_HOME/anansi" anansi scripts README.md AGENTS.md CLAUDE.md`

`./scripts/test.sh`
</verify>
<done>
The active runtime package is `anansi`, tests import `anansi`, the manifest name is `anansi`, the state path is `$HERMES_HOME/anansi/state.db`, and the full suite passes.
</done>
</task>

<task id="002-02">
<title>Update active docs and quick-task accounting</title>
<files>
- README.md
- AGENTS.md
- CLAUDE.md
- anansi/README.md
- .planning/quick/002-rename-anansi-to-anansi/002-SUMMARY.md
</files>
<action>
Update active repo docs and agent-facing instructions so this project presents Anansi as the active plugin identity. Keep historical Anansi references only where they describe old source material, the legacy v1 name, or the narrow migration path. Write `002-SUMMARY.md` with files changed, verification results, dirty-state boundaries, and any intentional legacy references that remain.
</action>
<verify>
`rg -n "anansi|Hermes Anansi Memory Plugin|\\[anansi appraisal\\]|plugins\\.entries\\.anansi|\\$HERMES_HOME/anansi" README.md AGENTS.md CLAUDE.md anansi/README.md .planning/quick/002-rename-anansi-to-anansi`
</verify>
<done>
Active docs use Anansi as the plugin identity, quick-task summary exists, and any remaining legacy references are explicitly migration/history scoped.
</done>
</task>
