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
  - .planning/quick/002-rename-legacy-appraisal-to-anansi/002-SUMMARY.md
autonomous: true
single_layer_justified: true
objective: "Scrub remaining legacy naming after the Anansi runtime rename while preserving behavior."
must_haves:
  truths:
    - "The active Python package directory is `anansi/`, and no old-name package remains."
    - "The plugin manifest name is `anansi` and config lookup uses `plugins.entries.anansi`."
    - "The state store resolves `$HERMES_HOME/anansi/state.db`."
    - "The rendered sentinel is `[anansi appraisal]`."
    - "`./scripts/test.sh` passes."
  artifacts:
    - anansi/plugin.yaml
    - anansi/__init__.py
    - anansi/store.py
    - anansi/tests
  key_links:
    - "README.md points to `anansi/README.md`."
    - "AGENTS.md and CLAUDE.md describe the active plugin source as `anansi/`."
---

# Plan 002: Rename Runtime Identity to Anansi

<objective>
This plan removes remaining old-name text from planning artifacts, research notes, quick-task records, local metadata, and runtime cleanup leftovers after the Anansi rename. Behavior stays the same: hook lifecycle, fail-open discipline, SQLite storage, no new dependencies, and test surfaces remain intact.
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
Remove any remaining old-name text from runtime cleanup leftovers, tests, scripts, docs, planning artifacts, research notes, and local metadata. Do not keep a runtime migration helper that requires the old name.
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
- .planning/quick/002-rename-legacy-appraisal-to-anansi/002-SUMMARY.md
</files>
<action>
Update active repo docs and agent-facing instructions so this project presents Anansi as the active plugin identity. Write `002-SUMMARY.md` with files changed, verification results, and dirty-state boundaries.
</action>
<verify>
`rg -n "anansi|Hermes Anansi Memory Plugin|\\[anansi appraisal\\]|plugins\\.entries\\.anansi|\\$HERMES_HOME/anansi" README.md AGENTS.md CLAUDE.md anansi/README.md .planning/quick/002-rename-legacy-appraisal-to-anansi`
</verify>
<done>
Active docs use Anansi as the plugin identity, and the quick-task summary exists.
</done>
</task>
