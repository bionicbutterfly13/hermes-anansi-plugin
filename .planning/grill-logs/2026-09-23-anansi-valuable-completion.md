# Grill log: Anansi to valuable completion

Started: 2026-09-23. Interviewer: Claude Code (grilling skill). Decider: Dr. Mani.

## Evidence baseline (verified 2026-09-23)

- `main` (df51b36, 2026-09-11) is the canonical lineage: GSD planning, Phase 8 merged
  (G2-G8 closed, G4 flagged cap rejected by constitution). README says the older
  branch is no longer the source of release status.
- Branch `001-close-known-gaps` / PR #2 (OPEN since 2026-07-05) is superseded. Only
  unique runtime delta: `531f390` (DEFAULT_MODEL = gpt-4o-mini; main keeps None).
- 4 untracked files in the 001 worktree (docs/07-SECURITY.md, scripts/live_trust_smoke.py,
  specs/COMPLETION-PLAN.md, specs/LIVE-VERIFICATION.md) are listed as deferred inputs in
  main's GSD-MIGRATION.md. SECURITY draft has stale citations; live_trust_smoke.py cannot
  force a trust denial (DEFAULT_MODEL=None) and its outcome vocabulary is wrong; the
  ledger row `trust_fallback_inconclusive` is not real evidence.
- Worktree `.claude/worktrees/clarify-appraisal-timeout` (branch codex/clarify-appraisal-timeout,
  nested inside the 001 worktree) holds UNCOMMITTED quick task 260912-cqc: 6 modified files
  (+172/-21) + test_worker.py; its STATE says 212 passed / 1 pre-existing failure.
- Offline suite on main against hermes-agent 0.21.3 venv: 199 passed, 0 skipped, 6.19s.
- Host 0.21.3 compat: all 4 hooks, ctx.llm.complete_structured, PluginLlmTrustError,
  manifest, config path compatible; host validator 13/13 ok; deprecated-import scan clean.
- Host semantic change: since 7b3dcee928 (2026-07-14) pre_llm_call context is stored as
  api_content and replayed every later turn (turn_context.py:815-853). Every anansi block
  now accumulates in history. Multimodal turns drop the block (turn_context.py:88).
- Anansi is NOT installed or enabled in ~/.hermes or any profile. Live provider evidence: UNRUN.
- No goal-entry path exists (README: "An external caller must populate goals"), so the
  drive layer has no real user input.
- GSD roadmap next: Phase 9 (worldview/episode/user-dopamine), then 10-14.
- New host APIs relevant to backlog: on_session_finalize, register_system_prompt_section,
  register_auxiliary_task, ctx.state, ctx.spawn_task, ctx.inject_message (gated).
  No post_memory_prefetch; no plugin cron hook.

## Settled

- **Q1 (2026-09-23) Definition of valuable completion:** Dr. Mani chose "b": a v1 used
  daily first, then decide the roadmap from real use. Concretely: install in one profile,
  fix context-replay cost, add goal entry, record a live PASS; Phase 9+ scope is chosen
  afterwards from observed usage. Rationale: all later phases stack on appraisal/drive
  output no real model has produced yet.

- **Q2 (2026-09-23) Lineage cleanup:** Dr. Mani chose "a" (full plan): (1) commit
  260912-cqc on `codex/clarify-appraisal-timeout`; (2) fix `_repo_root()` to follow a
  `.git` FILE, with a test, as its own commit; (3) merge to main `--no-ff`; (4) move the 4
  untracked files to `main/.planning/reference/phase-14-inputs/` marked DRAFT and drop the
  fabricated `trust_fallback_inconclusive` ledger row; (5) close PR #2 unmerged with a
  comment pointing at Phase 8, delete branch `001-close-known-gaps` and its worktree;
  (6) `531f390` gpt-4o-mini default NOT ported now (model choice is a later question).
  Execution waits for end-of-grill confirmation.

- **Q3 (2026-09-23) Replayed appraisal blocks:** Dr. Mani chose "a": tag each block with a
  turn marker in the header plus an "applies to this message only" line, and record each
  block's token size in telemetry. Revisit option B (move stable flagged priorities/goals to
  `register_system_prompt_section`) after a week of daily use. Host fork is NOT patched (C
  rejected: breaks prompt-cache stability, adds upstream merge cost).

- **Q4 (2026-09-23) Goal entry:** Dr. Mani chose "a": user-invoked `/goal` slash command via
  `ctx.register_command` (`add <text> [--domain X] [--files a,b]`, `flag <id>`,
  `status <id> active|queued|backburner`, `list`) plus a `hermes anansi goals ...` CLI via
  `register_cli_command` sharing one handler. Reflection-proposed candidate goals (B) are
  revisited after a week of use. YAML file (C) and agent tool (D) rejected.

- **Q5 (2026-09-23) Install profile:** Dr. Mani chose "a": `chief-of-staff` (only daily-used
  profile; goal/concern continuity is its job). Rollback = `enabled: false`. Latency impact is
  measured, not assumed.

- **Q6 (2026-09-23) Model routing:** Dr. Mani chose "a": register aux tasks `anansi_appraisal`
  and `anansi_reflection`, pass `task=` on calls; chief-of-staff config
  `auxiliary.anansi_appraisal` = `openai-codex` / `gpt-5.4`; reflection stays `auto` (main
  model, off the reply path); fall back to main model if the host lacks the API. Whether gpt-5.4
  meets p50 <= 6s is unverified and is measured by the live gate.

- **Q7 (2026-09-23) v1 exit gate:** Dr. Mani chose "a", which authorizes the live run.
  (1) `scripts/live_drive_smoke.py` exit 0 on chief-of-staff with the gpt-5.4 aux model,
  recorded in `08-LIVE-SMOKE.md`. (2) Seven days of telemetry: p50 <= 6s; timeouts <= 10% of
  appraised turns; parse_fail + llm_error <= 5%; median block size reported. (3) With
  `ANANSI_DEBUG_DUMP` on, on day 7 sample 20 random blocks with their turn context. Dr. Mani
  labels each useful, neutral or misleading. (4) Decision rule: >= 50% useful and 0
  misleading means go to Phase 9. < 25% useful means freeze. Anything between means the next
  increment is appraisal-prompt quality, not new layers. The thresholds were proposed by the
  interviewer and accepted; they are not measured baselines.

- **Q8 (2026-09-23) Kill-switch scope:** Dr. Mani chose "a": `enabled: false` stops turn
  capture as well as appraisal and reflection, with a regression test asserting no `turn_log`
  row is written. The purge command (B) is revisited if the day-7 review finds unwanted
  excerpts.

- **Q9 (2026-09-23) Tracking:** Dr. Mani said "yes" to A with the reorder. Insert GSD Phase 8.1
  "Daily-use v1" via `/gsd-phase` insert. Plans:
  8.1-01 lineage cleanup + `_repo_root()` `.git`-file fix (Q2);
  8.1-02 install on chief-of-staff (symlink) + first live smoke on the main model as the
  latency baseline;
  8.1-03 turn marker + block-size telemetry (Q3);
  8.1-04 `/goal` command + CLI (Q4);
  8.1-05 aux-task model routing (Q6);
  8.1-06 kill switch stops capture (Q8).
  Phase exit = the Q7 gate (live smoke exit 0, 7-day telemetry, day-7 20-block review,
  decision rule). Phases 9-14 are marked "gated on the 8.1 decision rule".

## Corrections

- **Q6 model (2026-09-23), supersedes `gpt-5.4`:** Dr. Mani: "gpt 6 sol is the model to use".
  No `gpt-6-sol` ID exists in the host code or in any profile config. Known IDs: `gpt-5.6-sol`
  (270 host refs; default for most profiles) and `gpt-6-astra` (132 refs; architect profile).
  The exact ID is pending Dr. Mani's answer. Aux-task routing (Q6-A) is unchanged.
  **Resolved 2026-09-23:** Dr. Mani said gpt-6-sol had just been released and asked for Hermes to
  be updated. The upstream sync was merged into the fork as `d3378a6a49` (tag
  `pre-upstream-sync-20260923`; 2173 upstream commits; clean merge; not pushed to origin).
  hermes-agent is now 0.21.4 and `gpt-6-sol` is in `hermes_cli/codex_models.py:20`.
  Checks: host imports ok; codex/gpt6 tier tests 13 passed; fork kanban tests 9 passed; anansi
  suite 199 passed on 0.21.4; host plugin validator ok; `register_auxiliary_task`,
  `register_command`, `register_cli_command`, and `complete_structured(task=...)` are present.
  Final value: `auxiliary.anansi_appraisal` = `openai-codex` / `gpt-6-sol`.
  Account-level acceptance of gpt-6-sol is UNVERIFIED: the picker lists it through the
  forward-compat template (codex_models.py:43) even when live discovery lacks it. Plan 8.1-02's
  live smoke run verifies it.
  Dr. Mani ran `hermes update --yes` on 2026-09-24. Exit 0; web UI built; config format v44 -> v46
  for root and all 10 profiles; "enabled the connections toolset for cli, telegram"; Desktop app
  rebuilt at /Applications/Hermes.app; HEAD stays at d3378a6a49 with a clean tree.

## Execution assumptions (stated, not asked)

- Primary checkout `/Volumes/Asylum/repos/hermes-anansi-plugin` switches to `main` after PR #2
  closes. The linked worktree `hermes-anansi-plugin-main` is removed after its untracked files
  (including this log) are committed on a branch. Each 8.1 plan runs on its own
  `fix/`/`feat/` branch and sibling worktree, merged `--no-ff`, then cleaned up.
- Every plan gets a CHANGELOG entry with Features / Fixes / Learnings.

## Additional evidence (2026-09-23, after Q1)

- 260912-cqc summary (`.planning/quick/260912-cqc-*/260912-cqc-SUMMARY.md` in the
  clarify-appraisal-timeout worktree): status incomplete; shared worker admission repair;
  212 passed / 1 failed. The failure (`test_drive_neveromit.py:436`) is environmental:
  `_repo_root()` skips a linked worktree's `.git` FILE and climbs to the parent checkout,
  reading a 68-day-old reflog. Same bug as README limitation "linked Git worktrees are not
  recognized". Real users with worktrees get wrong stalled/moving estimates.

## Corrections

(none yet)

## Additional evidence (2026-09-23, after Q2)

- Host replay is intentional: `agent/turn_context.py` `_stamp_api_content_sidecar` stores the
  exact sent bytes; historical user rows replay `api_content` "so the prompt-cache prefix stays
  byte-stable". Patching this out would break cache stability in the fork.
- Anansi block soft cap `_MAX_BLOCK_TOKENS = 500` (render.py:25); flagged priorities may exceed it.
  Host spill threshold `hooks.output_spill.max_chars` default 10000 (never reached by anansi).
- Growth estimate: up to ~500 tokens per appraised turn stays in history until host compaction;
  e.g. 40 appraised turns = ~20k tokens of past appraisals, each labeled `[anansi appraisal]`
  with no turn marker, so the model cannot tell a stale flag from a current one.

## Additional evidence (2026-09-23, after Q3)

- Goals are written only through `store.apply_deltas` keys `goals_add` / `goals_update` /
  `goals_status` (store.py:809-865). Nothing in anansi calls them: reflection never mints goals.
  The goals table is empty for any real user.
- Host 0.21.3 offers `ctx.register_command(name, handler)` (in-session `/name`, user-invoked;
  hermes_cli/plugins.py:663) and `ctx.register_cli_command` (`hermes <name> ...`; :649), plus
  `register_tool` (:460; agent-invoked).
- Constitution II: agent MUST NOT mint goals; MAY surface inert candidate goals until the user
  confirms. A user-invoked command is not agent autonomy; an agent tool that writes goals is.

## Additional evidence (2026-09-23, after Q4)

- 10 profiles + root. Last activity: chief-of-staff 2026-09-23; engineering, architect, root
  2026-09-20; marketing-orchestrator 09-13; strategist, archimedes 09-10; others older/none.
- All use provider `openai-codex`; root and chief-of-staff default model `gpt-5.6-terra`,
  engineering `gpt-5.6-sol`. chief-of-staff also runs a gateway platform (`platforms/photon`).

## Additional evidence (2026-09-23, after Q5)

- `ctx.register_auxiliary_task(key, display_name=, description=, defaults=)` (plugins.py:867)
  gives the plugin its own `auxiliary.<key>` config slot. `plugin_llm._check_task`
  (plugin_llm.py:207-236): a task key the plugin registered itself is allowed with NO trust
  override; unset/"auto" means the main model.
- chief-of-staff aux config: `title_generation` already uses provider `openai-codex`, model
  `gpt-5.4` (proves that model works on this account); other aux slots are `auto`.
- Current anansi default: `llm.model` unset, so appraisal and reflection run on the profile's
  main model (gpt-5.6-terra for chief-of-staff) under an 8.0s deadline. Its latency is unmeasured.

## Additional evidence (2026-09-23, after Q6)

- `.planning/phases/08-close-known-gaps/08-LIVE-SMOKE.md`: Status UNRUN; live command
  `scripts/live_drive_smoke.py` requires SEPARATE authorization; exit 0/1/2 semantics.
- `store.telemetry_summary()` (store.py:986) gives total, by_outcome, failure_count,
  last_error, p50_wall_ms. p50 covers ok/trust_fallback rows only, so timeouts are excluded
  and must be read as a separate rate.

## Additional evidence (2026-09-23, after Q7)

- `post_llm_call` (`__init__.py`) calls `reflection.record_turn` with no `enabled` check, so
  `enabled: false` still stores up to 2,000 chars of user and assistant text per turn
  (reflection.py:194-214; README "not a complete data-collection switch").
- `turn_log` is capped at 500 rows (store.py:41), and reflected rows are not deleted after
  consolidation.

## Open frontier (planned order)

1. Q1 Definition of "valuable completion" (roadmap-complete vs daily-use v1)
2. Lineage cleanup: close PR #2, rescue 260912-cqc work, salvage 4 untracked files, 531f390
3. Context-replay cost under host 0.21.3 (strip/replace/accept)
4. Goal entry mechanism (drive layer input)
5. Live verification gate and install target (root profile vs a named profile)
6. Roadmap order after v1 (Phase 9 vs 14 first; which phases are dropped)

## Frontier status

Empty as of 2026-09-23. Deferred until after the day-7 review: option B of Q3 (system-prompt
section), candidate goals (Q4-B), purge command (Q8-B), whether to port 531f390, moving
reflection to `on_session_finalize`, and Phase 9-14 scope.
Awaiting Dr. Mani's confirmation of shared understanding before any execution.

## Superseded next-question notes

Q9 Tracking: how the v1 work is recorded in GSD (inserted phase vs quick tasks).
Dr. Mani asked (2026-09-23) whether option A still lets him see Anansi function. Answer given:
yes; tracking does not change visibility. Proposed amendment: move install + first live smoke
to plan 8.1-02, right after cleanup, so every later plan is visible live through the symlink.
The main-model run also gives a latency baseline before aux routing. Awaiting confirmation.
Correction (2026-09-23): Dr. Mani's question referred to Q8 (kill switch), not Q9. Answer given:
Q8-A changes only the `enabled: false` state. With `enabled: true` (default), capture,
appraisal, reflection and the visible block all run unchanged. The only loss is that turns taken
while Anansi is off are never learned from. Q9 remains open, with the reorder proposal pending.
