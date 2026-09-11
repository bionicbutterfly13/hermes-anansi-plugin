---
phase: 08-close-known-gaps
plan: "01"
status: resolved
reviewed_head: 21ede38
date: 2026-09-11
---

# 08-01 acceptance review

The initial review at `d68513e` held wave 1 before merge. The two findings below
are preserved as history; repair evidence at `21ede38` resolves both.

## Resolution after delegated decision

Dr. Mani delegated the firm behavior choice. `61ad9ec` orders the authorized,
threshold-eligible ordinary notes by persisted stalled age in firm mode, preserving
standard ordering, confidence tie-breaks, and existing ceilings. Full-hook tests
now assert the actual expected note sequence and a visible firm/standard difference,
with unauthorized and below-threshold controls. Persisted age also now overrides
conflicting model timing, as required by the constitution and already planned in
08-03.

`21ede38` replaces the mocked threshold path with real temporary SQLite state,
four-day-old files and row timestamps, a fresh snapshot and the real hook around
a fake appraisal response. The threshold-three and threshold-five controls reach
the correct distinct drive-want/drive-note effects without mocked momentum or
snapshots. The executor's canonical suite passes 173 tests. The parent reviewed
the committed diff and updated assertions; the merge gate must run the suite
again on the combined phase branch before cleanup.

## Findings

1. **Firm has no demonstrated visible difference from standard.** At
   `anansi/render.py:135`, both note ceilings are three. At lines 136 and 149-168,
   the uniform authorized-push bonus changes from 10 to 15, while both values
   already dominate the entire neutral-rank/confidence range. Thus normal ordering
   remains unchanged. The full-hook test at `anansi/tests/test_drive_config.py:269`
   compares quiet against standard, but never compares firm against standard.
   Its final assertions compare internal scores only. An independent 320-case
   probe produced identical standard/firm output in every tested case: four
   generic stalled goals, all 16 push-authorization combinations, two confidence
   assignments, two input orders and five energy budgets. This misses the plan's
   identical-input distinguishability requirement. A user decision is pending on
   making firm prioritize the longest-stalled goals within the three slots.

2. **The required persisted-threshold full-hook regression is missing.**
   `anansi/tests/test_drive_store.py:257-282` replaces read-time momentum with a
   constant and invokes enrichment/rendering directly. The hook test at lines
   285-316 creates an empty database and supplies no goal signals. Neither proves
   that two persisted goals with thresholds three/five and actual four-day-old
   timestamps reach the hook with the correct threshold effects. Add the
   plan-specified temporary-database, fake-appraisal hook regression; preserve
   the existing tests and the distinct drive-note/drive-want rendering contract.

## Verified evidence

- `88677f2`: Task 1 migration and persisted pressure wiring.
- `d68513e`: Task 2 bounded pressure policy and tests.
- Root-run canonical `./scripts/test.sh`: **171 passed in 4.94s** at `d68513e`.
- Executor targeted plan gate: **34 passed**.
- Supported process-local Codex permissions restored normal commits. No global
  config or installed GSD source was changed.
- Private evidence is in the original repository's
  `.git/gsd-repair/phase8-execution/`, including the launch receipts, full process
  logs, original partial patch and `08-01-pressure-acceptance.json`.

## Conclusion

At the original reviewed commit, passing tests did not close these acceptance gaps. The executor summary's
`status: complete` and FR-003 completion claim are not accepted. Its task-token
estimate also is not measured process usage. Preserve the two commits and its
uncommitted summary in the manifest-owned executor worktree. Continue in that
same lane after the pressure behavior decision; do not redispatch from scratch,
merge this wave, or advance tracking as complete until the repairs above passed.
