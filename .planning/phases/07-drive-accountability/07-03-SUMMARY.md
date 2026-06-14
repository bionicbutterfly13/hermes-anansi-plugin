# Plan 07-03 Summary

**Completed:** 2026-06-14
**Phase:** 7 — Drive / Accountability
**Branch:** phase-7-drive-accountability

## What was built

The drive layer earned its first-person voice and its hardest guarantee. Two
red lines landed:

1. **DRIVE-04 — first-person `- drive want:` line + SAFE-04 carve-out.** A NEW
   allowlisted `- drive want:` label voices a flagged/owned goal in the FIRST
   person ("I want X moving (stalled N days)"), implemented purely as a label
   ALLOWANCE — NOT a loosening of the second-person directive scan.
   `_SECOND_PERSON_DIRECTIVE_RE` and `conftest.DIRECTIVE_PATTERNS` are
   byte-for-byte UNCHANGED. A genuine first-person line never matches the
   second-person regex, so it passes `_sanitize_text` unquoted; a second-person
   directive smuggled into the goal text is still quoted/neutralized as reported
   material everywhere. The existing negative controls are PRESERVED and a
   symmetric drive-specific control was ADDED (first-person passes; second-person
   is quoted or, if un-sanitized, correctly rejected).

2. **DRIVE-05 — never-omit a flagged priority (the drive red line).** A goal
   with `flagged_priority > 0` is EXEMPT from BOTH the `[:3]` per-category slice
   AND the token-cap trailing-line-drop. Flagged wants render FIRST (right after
   the sentinel + framing), sit in a PROTECTED prefix, and the cap loop's guard
   stops at `max(protected_count, 2)` so the pop never reaches a flagged line —
   never-omit beats the soft ~500-token cap. The guarantee reads the PERSISTED
   goals directly (not the model's `goal_signals`), so a flagged goal surfaces
   even when the model omitted it. Proven under adversarial crowding (many
   high-confidence instincts/observations/contradictions + low-trust hints +
   non-flagged goals all past the cap) and through the full `pre_llm_call` hook
   with a model payload that omits the goal entirely.

3. **Anti-complacency addendum.** A stalled goal with `support_style='firm'` or
   `push_when_stalled=1` renders a VISIBLE `[under-support: user-authorized
   firmer support]` clause alongside the neutral `stalled N days` read — kept
   SEPARATE/inspectable (Pitfall #9), never quietly downranked.

APPR-05 precedence is intact: zero appraisal signals ⇒ `render_block` returns
None even with a flagged goal present (a flagged goal rides a block, never forces
one). Drive-off (`goals=None`) suppresses all want lines — byte-for-byte
invariant preserved.

## Key files

- `anansi/render.py` — new helpers `_is_flagged`, `_want_text`,
  `_resolve_stalled_days` (reads top-level `stalled_days` OR nested
  `momentum.stalled_days`), `_render_drive_want` (first-person + visible
  under-support clause), `_flagged_want_lines` (builds protected want lines from
  PERSISTED flagged goals, prefers a matching enriched signal, dedup). `render_block`
  gained a `goals=None` param: flagged wants render FIRST into a protected
  prefix (`protected_count`); the `- drive note:` loop now SKIPS goals already
  voiced as wants (no duplicate, never the dropped 4th note); the cap loop guard
  is `len(lines) > max(protected_count, 2)`. `enrich_goal_signals` carries
  `flagged_priority` through. `_SECOND_PERSON_DIRECTIVE_RE` UNCHANGED.
- `anansi/__init__.py` — `render_block(..., goals=goals)` so persisted flagged
  goals (with `flagged_priority` + momentum) reach render; `goals` is None when
  drive is off, preserving the byte-for-byte drive-off block.
- `anansi/tests/conftest.py` — `- drive want:` added to `ALLOWED_LABEL_PREFIXES`
  with a comment marking the DRIVE-04 first-person carve-out;
  `DIRECTIVE_PATTERNS` UNCHANGED.
- `anansi/tests/test_anticreep.py` — 4 new tests: want-line passes the checker;
  the symmetric first-person-passes/second-person-quoted-or-rejected control;
  `_SECOND_PERSON_DIRECTIVE_RE` unchanged assertion; corpus-with-flagged-want
  stays directive-free. Existing negative controls UNTOUCHED.
- `anansi/tests/test_drive_neveromit.py` — NEW (12 tests): slice exemption,
  multiple-flagged survival, adversarial-crowding survival (mirrors the low-trust
  corpus shape), first-content-line/top-of-block placement, APPR-05 precedence
  (empty signals ⇒ None even with a flagged goal), anti-complacency
  (push_when_stalled + support_style='firm' both surface the under-support
  clause), drive-off suppression, and two full-hook integration tests (flagged
  want survives a crowding model payload that omits the goal; drive-off
  suppresses + records `skipped:drive_disabled`).

## Decisions made

- **Never-omit reads PERSISTED goals, not model output.** `_flagged_want_lines`
  is built from `snapshot["goals"]` (carrying `flagged_priority`), not solely the
  model's `goal_signals`. A flagged goal therefore surfaces even when the model
  omits its signal — the guarantee does not depend on a cooperative model. When a
  matching enriched signal exists, it is merged in so the want line keeps the
  read-time `stalled_days`.
- **Never-omit beats the soft cap.** If the protected prefix alone exceeded the
  ~500-token cap, the block is accepted slightly over cap rather than dropping a
  flagged want. The cap is a soft target; never-omit is a hard guarantee. Coded
  as `floor = max(protected_count, 2)` and documented at the loop.
- **`_resolve_stalled_days` bridges the two shapes.** A persisted goal carries
  `momentum.stalled_days` (nested); an enriched goal_signal carries a top-level
  `stalled_days`. The want line reads either, so a flagged persisted goal still
  shows its neutral stalled read even with no model signal.
- **No new schema, no appraisal.py change.** `flagged_priority` already existed
  on the goals table (07-01) and flows through `read_snapshot`; the want line is
  rendered from goal state + momentum, so DRIVE-04/05 needed no schema bump and
  no `appraisal.py` edit (it was staged for the commit but had no diff).

## Deviations from plan

- **Added 2 tests beyond the plan's enumerated list** (16 net-new total, not the
  ~9 minimum): `test_multiple_flagged_goals_all_survive_slice`,
  `test_support_style_firm_also_triggers_under_support`,
  `test_drive_off_suppresses_flagged_want`,
  `test_flagged_goal_is_the_first_content_line_under_crowding`,
  `test_flagged_goal_renders_when_a_block_already_renders`,
  `test_neveromit_full_hook_drive_off`, plus the `test_drive04_*` quartet. They
  cover the multi-flagged slice exemption, the firm-style anti-complacency path,
  and the drive-off suppression of wants through the real hook — all directly on
  the plan's must-haves, none weakening any constraint. Suite 135 → 151.
- **No behavioral test was modified.** The SAFE-03/04 negative controls are
  untouched; only additive corpus/labels/tests were introduced.

## Notes for downstream (07-04)

- **`render_block(signals, snapshot, goals)` is the surfacing seam.** 07-04's
  domain whitelist / energy budget can gate which goals reach `goals=` (filter
  before render); the never-omit protected-prefix logic then applies to whatever
  flagged goals survive the whitelist. A whitelist must NOT silently drop a
  flagged goal — if a flagged goal is filtered, that is a never-omit concern and
  must surface, not vanish.
- **Pressure columns still not persisted.** `support_style` / `push_when_stalled`
  are still read off the goal_signal / persisted goal defensively (07-02's
  forward-compat copy-through). When 07-04 adds the columns to the goals table +
  `apply_deltas`, the render/enrich path already consumes them — only the write
  side is missing.
- **The `[under-support: ...]` clause is the anti-complacency surface.** Keep it
  SEPARATE from the neutral `stalled N days` read (Pitfall #9 inspectability).
- **Anti-creep landmine reminder.** `_SECOND_PERSON_DIRECTIVE_RE` and
  `conftest.DIRECTIVE_PATTERNS` are the SAFE-04 second-person guards — never relax
  them; the first-person carve-out is the LABEL only. Never let
  `subprocess`/`os.system`/`eval(`/`exec(` into any of the six plugin modules
  (comments included — the forbidden-substring scan is a whole-file match).
