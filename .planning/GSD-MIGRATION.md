# GSD migration intake

Date: 2026-09-10

Status: **GSD migration and repaired legacy planning intake validated. Dr. Mani authorized commit, main integration and publication on 2026-09-10; Git history records the resulting integration.**

Subsequent cleanup, 2026-09-10: Dr. Mani requested removal of the retired workflow.
The constitution and 17 engineering documents now live under `.planning/`.
References, extracted source blocks and classifier records use the new paths;
retired commands and template references were removed. Engineering principles
and acceptance content are preserved. Original intake bytes and receipts remain
in commit `eb228d788fc474128d2c74514ffe44ab1052a253`. Historical byte-identity
checks below describe the intake before this normalization. Cleanup and Phase 8 planning are recorded together; implementation remains pending.

During the initial attempt, all 18 classifications passed schema, coverage and
manifest-override checks. The official synthesizer then detected two reference cycles: `plan.md -> plan.md`
and `plan.md -> tasks.md -> plan.md`. The first two edges come from the plan's
directory inventory; the return edge comes from the task ledger's prerequisites.
The original gate report is in the private evidence archive described below.
That first attempt synthesized no documents and changed no active plans,
configuration, instructions or runtime files. Its diagnostic outputs are preserved
in the repository's private `.git/gsd-repair/initial-ingest-evidence/` directory.
Dr. Mani then authorized repairing the updater and ingestion defects. The
repaired retry consumed all 18 documents, with zero blockers, zero competing
variants and two constitution-precedence resolutions. Complete source-content
coverage was checked before merging the intake into active planning files.
The [current conflict report](INGEST-CONFLICTS.md) records the two precedence resolutions.

## Settled

- Dr. Mani requested migration to GSD and legacy planning ingestion through GSD, with the GSD update check first.
- Installed Codex GSD version: **`@opengsd/gsd-core@1.13.0`**, using the package's official global Codex installer. The earlier `1.42.3` check queried the retired `get-shit-done-cc` package and did not establish currency on the maintained package lineage. The maintained checker returns `1.13.0`.
- The official installer used its documented `GSD_ALLOW_SYMLINKED_DEST=1` option for the existing, ownership-verified offload symlinks. Legacy GSD files were backed up first. All 147 recorded unrelated files retain their original hashes after installation.
- Classifier and synthesizer prompts are locally patched: document navigation no longer creates dependency-cycle blockers; explicit prerequisites, locked contradictions and acceptance variants retain their gates. Both full and compact source variants are patched, and the two full prompts shipped in the release were deployed through the official installer. This is a local repair, not an upstream release fix; future updates may replace it. Source, patch, package integrity and installation receipts are under `.git/gsd-repair/` in the original repository.
- The existing ingestion test suite passes 51/51 checks, and the agent contract check reports zero violations. Four actual-agent behavioral controls also passed independent verification: navigation passes, actual dependency cycles block, locked contradictory decisions block, and acceptance variants remain separate. The verifier confirmed unchanged fixture inputs and retained acceptance text. These controls do not by themselves prove successful ingestion of this project's documents.
- Project configuration now explicitly selects `runtime: codex` and the supported `resolve_model_ids: omit` setting through GSD's `config-set` command. Model resolution returns supported Codex models for the ingestion roles.
- The official `init ingest-docs` command ran successfully in this worktree, detected the project and all required agents, and selected merge mode because `.planning/` exists.
- Integration baseline: `main` and `origin/main` at `5413873f51447f70138717bc758851288e13b630`, verified after fetching `origin main`.
- Task branch: `chore/migrate-gsd`, in the sibling `hermes-anansi-plugin-migrate-gsd` worktree.
- The [manifest](ingest-manifest.yaml) maps the 18 imported documents to their current GSD locations. At intake, each original source was compared byte for byte with `001-close-known-gaps` at `af2a0bc3a45ceef3d37c15bba567e8f865879edc`; the current paths were introduced by the subsequent cleanup.
- This intake brings planning documents across the branch boundary. It does not bring the seven unmerged feature-branch commits or their runtime changes onto `main`.

## Migration result

Classifier records under `milestones/gsd-intake-2026-09-10/` now use portable GSD reference paths. Their README identifies the original receipt commit and the normalization. Re-running the official intake regenerates live classifications from the relative manifest; unchanged requirements do not need another merge.

- Active GSD PROJECT, REQUIREMENTS, ROADMAP and STATE now reflect the imported backlog, with seven source-mapped phases (8-14), 46 pending functional requirements, 29 preserved success criteria and 25 user stories.
- Complete source blocks for all 18 inputs were verified against unchanged inputs at intake. The first synthesis was too terse despite passing schema checks; the GSD synthesizer corrected it before migration. Cleanup normalized paths and workflow text in both the references and extracted blocks.
- Constitution precedence forbids withholding flagged priorities by a cap and leaves interruption exceptions deferred. Both lower-precedence source variants remain preserved.
- GSD roadmap analysis recognizes seven active phases, zero completed, and Phase 8 next. State snapshot agrees. Historical phases remain in a supported archive section, including the unresolved Phase 5 evidence gap.
- Both repository instruction files are synchronized. The prior seven planning/configuration/instruction files are preserved with hashes under `milestones/pre-gsd-2026-09-10/`.
- Ignored legacy config keys were archived and removed from the active config. Existing enabled defaults for Nyquist validation and AI integration are explicit. Automatic documentation commits and phase advancement are disabled.
- GSD health reports zero errors and four W019 advisories: DECISIONS.md, HANDOFF.md, GSD-MIGRATION.md and the official ingestion workflow's own INGEST-CONFLICTS.md. Historical/provenance paths are retained rather than removed to silence the checker. A global-defaults warning states that explicit project runtime/model settings take precedence; model resolution works.
- Source files, runtime code, test scripts and the published README remain unchanged by migration. Validation is planning/tooling-specific; no new plugin or live-provider test result is claimed.

## Pending

- Treat checked tasks, schema-v5 descriptions and test results in imported documents as claims about the feature branch or their recorded historical run. They are not evidence that the integration baseline implements those changes.
- Preserve the constitution's engineering invariants when changing the workflow. Importing a future feature does not authorize implementation or amendment of an invariant.
- Commit, main integration and publication were explicitly authorized by Dr. Mani after reviewing the validated migration.

## Deferred inputs

The original feature worktree contains three untracked planning documents. They remain there, unchanged, and are not part of the tracked legacy planning intake:

- `docs/07-SECURITY.md`, SHA-256 `56acc696306e8c070bf503ed88319e519530f6e4b4945239719acee553eb92fb`.
- `COMPLETION-PLAN.md` (original feature checkout, untracked), SHA-256 `0bc04ae777addac3e7ee569810c457385a3f5fad5378ed5103bb82c41d996ef1`.
- `LIVE-VERIFICATION.md` (original feature checkout, untracked), SHA-256 `4b892252f6ac1996523b7938ee12f318a39273c3f4295398f6983a84f48d3a32`.

The original untracked `scripts/live_trust_smoke.py` also remains outside this planning-only migration. Deferred material must be explicitly accounted for before claiming that every repository document has been ingested.

## Validation boundary

Intake checks cover source identity, repository containment, the 50-document limit, complete extracted source text, requirement mapping, historical snapshots and unchanged runtime files. GSD routing and state queries agree on Phase 8. No plugin tests or live-provider checks have been rerun as part of intake. The conflict gate and worktree planning migration are complete. The integration commit in Git history is the publication provenance.
