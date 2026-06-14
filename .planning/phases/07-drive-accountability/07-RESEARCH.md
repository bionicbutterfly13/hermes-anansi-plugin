# Phase 7: Drive / Accountability — Research

**Researched:** 2026-06-14
**Phase goal:** Every eligible turn can surface user-minted goals with grounded progress/accountability signals — in-turn, never omitting a flagged priority — built on the existing appraisal path and the anansi SQLite store. (ROADMAP Phase 7)
**Requirements in scope:** DRIVE-01..06 (proprietary v2)

> Confidence tags: **[VERIFIED: file:line]** = read in this repo this session; **[CITED: url]** = external source; **[ASSUMED]** = from model training (stale ≤18mo), confidence HIGH/MEDIUM/LOW noted. No external web tool was available this session, so external-concept claims are [ASSUMED] with confidence, NOT freshly cited — the planner should treat them as hypotheses, not facts. The codebase findings (the load-bearing 90% of this phase) are all [VERIFIED].

---

## Don't Hand-Roll

Given the **zero-new-pip-dependency** hard constraint, "don't hand-roll" here means **reuse the in-repo machinery** — almost nothing new should be built from scratch. Concrete reuses:

| Problem | Reuse this (do NOT build new) | Why |
|---|---|---|
| Persisting goals / velocity | New tables added to the existing `_SCHEMA_DDL` tuple + `_TABLES` in `store.py`; bump `SCHEMA_VERSION` 3→4 | [VERIFIED: store.py:35,48-88] Single sqlite surface is locked (DECISIONS 2026-06-06; 06-CONTEXT). A v4 bump auto-quarantine-recreates v3 DBs via the disposable-state doctrine — **no migration code** [VERIFIED: store.py:212-231]. |
| Writing goal rows | Extend `apply_deltas()` with new delta keys (e.g. `goals_add`, `goals_update`, `goals_status`) inside the existing single transaction | [VERIFIED: store.py:384-538] The ONLY write funnel. Mechanical-only: clamping/policy stays in the caller. Unknown keys are already ignored gracefully [VERIFIED: store.py:510-511, test_store.py:248]. |
| Reading goals at appraisal time | Extend `read_snapshot()` (read-only URI conn) to include a `goals` list | [VERIFIED: store.py:267-329] Already returns None on any error, never creates files, applies lazy-decay-at-read — the exact pattern velocity needs. |
| Row-cap eviction for goals | Add a `goals` entry to the `CAPS` dict and the cap-eviction loop | [VERIFIED: store.py:38-44, 515-526] Eviction is already a generic `id NOT IN (… ORDER BY id DESC LIMIT ?)` loop. |
| Telemetry for drive failures | `record_telemetry()` with `skipped:drive_*` / existing failure vocabulary | [VERIFIED: store.py:540-590] `skipped:<reason>` is free-form; `telemetry_summary` treats `skipped:*` as non-failures by exclusion-list [VERIFIED: store.py:599-624]. Use a `skipped:` prefix for the drive-off path so it does NOT count as a failure. |
| Config keys (kill switch, whitelist, budget) | Add coerced keys to `get_cfg()` using `_coerce_bool/_coerce_int/_coerce_float` | [VERIFIED: config.py:76-152] Every key falls back to a default; `get_cfg` never raises. Cache reset per session already wired [VERIFIED: config.py:155-158, __init__.py:82]. |
| Schema validation of new noun-fields | `jsonschema` (4.26.0, **already in the venv**) via the host's `complete_structured(json_schema=…)` | [VERIFIED: venv jsonschema 4.26.0] Schema-rejected docs already surface as `parse_fail` host-side and are caught in `run_appraisal` [VERIFIED: appraisal.py:292-297, DECISIONS 03 row]. Add goal fields to `APPRAISAL_JSON_SCHEMA`; do NOT add a second validator. |
| Sanitization of rendered goal lines | `render._sanitize_text` + the directive/label allowlist | [VERIFIED: render.py:86-109] Already strips injection patterns, quotes bare second-person directives, truncates. Extend, never replace. |
| "Stalled N days" / momentum time math | stdlib `datetime` + `os.stat().st_mtime`; the decay-at-read idiom in `_effective_weight` | [VERIFIED: store.py:247-264] Days-idle from a timestamp is already implemented and tested — mirror it for velocity. |
| Ground-truth git signal | stdlib file reads of `.git/logs/HEAD`, `.git/refs/heads/*`, and file mtimes — **NOT** a git library, **NOT** `subprocess` | GitPython/dulwich are **absent** from the venv (verified this session); `subprocess`, `os.system`, `eval(`, `exec(` are **forbidden substrings** the anti-creep scan asserts == [] [VERIFIED: test_anticreep.py:238-261]. See Pitfall #2. |

**Bottom line:** this phase adds ~zero new machinery. It is schema rows + delta keys + snapshot fields + schema/render extensions + config keys, each riding an existing tested funnel.

---

## Common Pitfalls

### Pitfall 1 — Adding a second sqlite surface (or any second DB/daemon)
**What goes wrong:** Goals feel like a "new domain," tempting a `goals.db`, a separate connection helper, or a background poller.
**Why it's fatal:** `store.py` is contractually the plugin's ENTIRE sqlite surface — "No other module in this plugin may import sqlite3 or touch state.db" [VERIFIED: store.py:1-3]. The anti-creep AST import-allowlist would still pass for `sqlite3` (stdlib), but the single-surface rule is a locked decision (DECISIONS 03 row, 06-CONTEXT Architecture) and the locked-DB/corrupt-DB fail-open coverage only protects the funnel.
**How to avoid:** All goal state goes through `_SCHEMA_DDL` + `apply_deltas` + `read_snapshot` in `store.py`. No new module imports sqlite3. No daemon — increment #1 is in-turn only (heartbeat deferred, 06-CONTEXT).

### Pitfall 2 — Reading "git ground truth" with `subprocess` (anti-creep tripwire)
**What goes wrong:** The obvious way to read git commit recency is `subprocess.run(["git", "log", ...])`. **This bricks the suite.**
**Why:** `"subprocess"`, `"os.system"`, `"eval("`, `"exec("` are in `FORBIDDEN_SUBSTRINGS`; `test_safe04_no_forbidden_api_substrings` asserts no plugin module contains any of them [VERIFIED: test_anticreep.py:238-261]. The AST import-allowlist also forbids any top-level import outside stdlib + `{agent, hermes_cli, hermes_constants, anansi}` [VERIFIED: test_anticreep.py:277-300] — so GitPython/dulwich are doubly out (also absent from the venv, verified this session).
**How to avoid:** Derive "ground truth" from **stdlib-only** signals: `os.stat(...).st_mtime` of project files, plus plain `open()`-reads of `.git/logs/HEAD` (reflog lines carry committer epoch+tz) and `.git/refs/heads/*`. `.git/HEAD` resolves the current branch ref [VERIFIED: HEAD content `ref: refs/heads/master` this session]. Note: `open()` in write mode is scanned — only ONE write-mode `open()` is allowed in the whole plugin (the debug dump) [VERIFIED: test_anticreep.py:314-342]; **all git/file reads must be read-mode** `open(path)` / `open(path, "r")`, and must not contain the substring `config` in the call line [VERIFIED: test_anticreep.py:325-328]. Paths from `$HERMES_HOME`/cwd discovery, never literals.

### Pitfall 3 — Computing velocity behind debounced reflection (staleness bug)
**What goes wrong:** Treating velocity like the concern/affect digest and writing it in `maybe_reflect`.
**Why it's a bug:** Reflection is debounced — `reflect_every_n_turns` default 5, or session change [VERIFIED: config.py:46, reflection.py:704-711]. A goal could read "moving" for up to 4 turns after it actually stalled. 06-CONTEXT explicitly flags this (Goal freshness, Codex review 2026-06-14): velocity MUST be computed **from ground truth at appraisal-read time**, NOT gated behind the debounce.
**How to avoid:** Compute velocity in the `pre_llm_call` read path (snapshot-read or a small pure helper invoked there), reading git/file/milestone timestamps live. Persisted goal rows store the user's *definition* (success criteria, status, flagged-priority bit); momentum is **derived at read**, like `_effective_weight` decay [VERIFIED: store.py:247-264, 296-305]. Do not persist a stale velocity number as the source of truth.

### Pitfall 4 — Over-relaxing SAFE-04 so second-person directives leak
**What goes wrong:** The DRIVE-04 first-person carve-out is implemented as "loosen the directive scan," accidentally letting "you should ship by Friday" through.
**Why it's the red line:** The whole anti-creep design is structural. `_SECOND_PERSON_DIRECTIVE_RE` quotes bare `you (should|must|need to|have to|shall)` [VERIFIED: render.py:81-83,105-106]; `conftest.DIRECTIVE_PATTERNS` independently re-asserts no `you (should|must)` survives in any rendered line, after quoted spans are stripped [VERIFIED: conftest.py:30-42,72-96]. The carve-out must be **first-person only** ("I want…"), and second-person must STILL be neutralized.
**How to avoid:** Implement the carve-out as a NEW allowlisted label (e.g. `- drive want:`) plus a first-person allowance, leaving `_SECOND_PERSON_DIRECTIVE_RE` and `DIRECTIVE_PATTERNS` untouched for second person. Add the new label to `ALLOWED_LABEL_PREFIXES` [VERIFIED: conftest.py:46-53]. **Keep the negative controls** — `test_safe03_helper_actually_catches_violations` proves the checker still fails on "you should migrate now" and on unlabeled lines [VERIFIED: test_anticreep.py:217-231]; add a symmetric negative control proving a SECOND-person *drive* line is still quoted/rejected while a FIRST-person one passes. A checker that can't fail proves nothing.

### Pitfall 5 — Silent omission of a flagged priority (DRIVE-05 betrayal)
**What goes wrong:** Top-N truncation. `render_block` already keeps only `[:3]` per category and drops trailing whole lines under the ~500-token cap [VERIFIED: render.py:151-168,204-208]. A flagged-priority goal could be the 4th item or the dropped trailing line — silently omitted.
**Why it's the red line:** 06-CONTEXT: silent omission of a user-flagged item is "betrayal (Dr. Mani's top anti-value)"; the never-omit invariant must be **enforced AND tested**.
**How to avoid:** Flagged-priority goals must be exempt from both the `[:3]` slice and the token-cap line-drop — render them FIRST, before the droppable tail, and never inside the truncation loop's pop range. The invariant test asserts a flagged goal appears in the block even when many other signals crowd the cap (mirror `test_safe03_corpus_with_low_trust_snapshots`'s "block is not None + substring present" shape [VERIFIED: test_anticreep.py:194-207]).

### Pitfall 6 — Breaking fail-open in the new read/compute path
**What goes wrong:** A velocity helper that raises on a missing `.git`, an unparseable milestone file, or a bad timestamp — propagating into `pre_llm_call`.
**Why:** Fail-open is law: no hook path may raise; every failure → empty injection + telemetry row [VERIFIED: __init__.py:34-62 `_fail_open`; AGENTS.md]. `read_snapshot`/`_effective_weight` already model "return the safe value on any error, never raise" [VERIFIED: store.py:247-264,320-323].
**How to avoid:** Every new helper returns a benign default (empty list / None / "unknown velocity") on ANY exception, mirroring `_effective_weight`'s try/except-to-default style. Add a fail-open matrix row: corrupt/absent `.git`, locked DB, missing milestone file → block still renders (or suppresses) without raising. The `_fail_open` wrapper is the last backstop but must never be the FIRST line of defense.

### Pitfall 7 — The three-module-identity test trap
**What goes wrong:** New tests import the plugin as `plugins.anansi` or `tests.plugins.anansi`, or `test_scan_targets_are_the_plugin_modules` fails because a new module was added.
**Why:** The plugin loads as module `anansi` (worktree root force-inserted at `sys.path[0]`), never `plugins.anansi` [VERIFIED: conftest.py:16-18; DECISIONS 04-02 row]. `test_scan_targets_are_the_plugin_modules` hard-codes the exact module set `{__init__, appraisal, config, reflection, render, store}` [VERIFIED: test_anticreep.py:54-58].
**How to avoid:** Prefer extending existing modules over adding new ones. If a new module IS added (e.g. `drive.py` for the pure velocity helper), you MUST update that inventory assertion AND `EXPECTED_HOOKS` is unaffected (no new hooks this increment). New tests import `from anansi import …` and `from conftest import …` exactly like the existing suite [VERIFIED: test_anticreep.py:35-36].

### Pitfall 8 — Locked-DB / corrupt-DB write paths for goal writes
**What goes wrong:** Goal "mint" writes assume success.
**Why:** `apply_deltas` returns False (rolls back) on lock/corruption; it never raises [VERIFIED: store.py:528-531]; the locked-DB write degrades within the busy-timeout and returns False [VERIFIED: test_store.py:149-165]. WAL `BEGIN EXCLUSIVE`==`IMMEDIATE` never blocks readers [VERIFIED: DECISIONS row; reader-block tests need a rollback-journal tmp DB].
**How to avoid:** Treat goal-write success as best-effort; the user-facing path must tolerate a False return (e.g. surface "couldn't persist goal" rather than crash). Reuse the `test_store.py` locked-DB idiom (hold `BEGIN IMMEDIATE`, assert False + fast degrade) for any new write delta.

### Pitfall 9 — Hidden drive consequence or safety-by-complacency
**What goes wrong:** The drive silently changes salience inside the model's private judgment, or the safety layer becomes so quiet that a stalled high-priority goal is not pushed when Dr. Mani explicitly authorized firmer support.
**Why:** Phase 6 now treats adjustable pressure and anti-complacency as safety requirements. Drive may adjust salience/urgency/persistence, but not truth, goal ownership, evidence, or omission rules. If the adjustment is hidden, the user cannot tell whether the agent's read is neutral or drive-shaped.
**How to avoid:** Store pressure metadata (`support_style`, `push_when_stalled`, thresholds) with the goal, keep neutral momentum separate from drive-adjusted salience, and render a drive-effect reason when pressure changes surfacing. Tests should prove a firm/push_when_stalled goal cannot be quietly downranked and that the drive effect remains inspectable.

---

## Existing Patterns in This Codebase

Concrete extension points the planner can target by `file:symbol`:

- **Schema growth without migration** — `store.py:_SCHEMA_DDL` (tuple of CREATE statements) + `_TABLES` + `SCHEMA_VERSION` [VERIFIED: store.py:35,48-88]. Add goal tables here, bump to 4. v3 DBs auto-quarantine-recreate on first `ensure_db` [VERIFIED: store.py:212-231]. Mirror the v2→v3 comment style in DDL.
- **The one write funnel** — `store.py:apply_deltas` [VERIFIED: store.py:384-538]. Add `goals_add` / `goals_update` / `goals_status` branches alongside `concerns_add` etc.; keep them mechanical. Caps enforced in the same loop [VERIFIED: store.py:515-526]; add `"goals"` to `CAPS`.
- **The one read path** — `store.py:read_snapshot(include_decayed=…)` [VERIFIED: store.py:267-329]. Add a `goals` list to the returned dict. For derived-at-read momentum, mirror `_effective_weight` [VERIFIED: store.py:247-264].
- **Meta watermark / bookkeeping** — `meta_set` delta + `get_meta` [VERIFIED: store.py:332-354,472-481]. Use for any goal-related bookkeeping if needed (e.g. last-surfaced goal id), exactly like `last_reflected_turn_log_id`.
- **Appraisal output schema + parse** — `appraisal.py:APPRAISAL_JSON_SCHEMA` [VERIFIED: appraisal.py:71-119] and `parse_signals` [VERIFIED: appraisal.py:367-451]. Add goal-aware noun-fields (`relates_to_goal`, `stalled_days`, `contradicts_milestone`) as a new array/object property; coerce+clamp+drop-below-threshold in `parse_signals` using `_clamp01` [VERIFIED: appraisal.py:356-364]. Update `APPRAISAL_PROMPT` to describe the new noun-fields, keeping the "observations only, no directives" framing [VERIFIED: appraisal.py:36-64].
- **Context assembly** — `appraisal.py:build_context` [VERIFIED: appraisal.py:145-192]. To make the model goal-aware, the goals snapshot slice must be injected into the untrusted-input state JSON here (alongside concerns/contradictions). Respect the 12000-char cap.
- **Render + sanitize + label allowlist** — `render.py:render_block` [VERIFIED: render.py:125-209], `_sanitize_text` [VERIFIED: render.py:86-109], `SENTINEL`/`FRAMING` [VERIFIED: render.py:19-23]. Add a `- drive want:` line type with the first-person carve-out; register the label in `conftest.ALLOWED_LABEL_PREFIXES` [VERIFIED: conftest.py:46-53].
- **Config resolution** — `config.py:get_cfg` [VERIFIED: config.py:112-152] with `_coerce_bool/int/float` [VERIFIED: config.py:76-109]. Add `drive_enabled` (separate kill switch), `drive_domains` (whitelist — coerce a list defensively), `drive_energy_budget` (int). Document them in the module docstring like the existing keys [VERIFIED: config.py:11-22].
- **Hook ordering** — `__init__.py:pre_llm_call` [VERIFIED: __init__.py:92-160]. Order is contractual: kill switch → rollover → throttle → snapshot → appraisal → telemetry → render. Drive kill switch is checked AFTER the appraisal kill switch (drive off while appraisal on); drive-off → no goal-aware fields, appraisal otherwise unchanged (success criterion 4).
- **Fail-open wrapper** — `__init__.py:_fail_open` [VERIFIED: __init__.py:34-62]. The backstop; new code must still self-fail-open.
- **Reflection debounce/idempotence (precedent, NOT the velocity home)** — `reflection.py:maybe_reflect` [VERIFIED: reflection.py:663-722] and `apply_reflection` watermark-in-same-transaction [VERIFIED: reflection.py:525-561]. Useful as the model for any FUTURE between-session goal work; velocity itself is read-time, not here (Pitfall #3).
- **Test idioms to mirror:**
  - Store round-trip / caps / locked-DB / corrupt-DB → `test_store.py` [VERIFIED: test_store.py:51-257], all on `tmp_path`, real `$HERMES_HOME` never touched.
  - Full-hook fail-open with monkeypatched `get_db_path` + fake LLM → `test_failopen_matrix.py:matrix_env`/`pinned_env` [VERIFIED: test_failopen_matrix.py:153-193] and `make_plugin_llm_for_test` [VERIFIED: test_failopen_matrix.py:171-175].
  - Directive-free rendered corpus + negative controls → `test_anticreep.py` [VERIFIED: test_anticreep.py:146-231].
  - Telemetry vocabulary → `telemetry_summary` exclusion-list shape [VERIFIED: store.py:599-624].
- **Canonical test command** — `./scripts/test.sh` (stages pytest into `.devtools/pytest`; hermes venv never modified) [VERIFIED: scripts/test.sh:1-35].

---

## External-Concept Notes (low weight, treat as hypotheses)

> No live web tool this session — these are [ASSUMED] from training, with confidence. The planner should not block on them; they only inform tone/UX of the rendered drive line, which is otherwise governed by SAFE-04.

- **Avoiding psychological reactance in progress surfacing** — [ASSUMED, confidence MEDIUM] Reactance research (Brehm) and behavior-change UX generally find that *autonomy-supportive, observational* framing ("X has been idle 3 days") provokes less defensiveness than *controlling/imperative* framing ("you need to work on X"). This independently corroborates the SAFE-04 design: keep the line observational/first-person-want, never second-person-imperative. 06-CONTEXT's "multiple low-reactance perspectives, never a single prescription" aligns. **Implication for the planner:** the "stalled louder" weighting (DRIVE-02) should manifest as *salience/ordering* (surface earlier, render first) — NOT as louder *language*; loudness-via-imperative is exactly what reactance penalizes and what SAFE-04 forbids.
- **Faithful priority retention / anti-omission in assistant systems** — [ASSUMED, confidence MEDIUM] The general failure mode (top-N truncation silently dropping user-stated must-haves) is well-known in summarization/ranking; the durable fix is a *pinned/protected set* exempt from ranking and truncation, plus an explicit test that the pinned item survives adversarial crowding. This is exactly the DRIVE-05 mechanism described under Pitfall #5. No external citation needed — the repo's own top-3 slice + token cap is the concrete omission risk.

---

## Recommended Approach

Slice into **vertical tracer-bullets**, each a thin end-to-end slice through the existing funnels, ordered so the never-omit + fail-open red lines are provable as early as possible. Suggested 3–4 plans:

1. **Goal persistence tracer (DRIVE-01 + DRIVE-06 storage half).** Add goal tables to `_SCHEMA_DDL`, bump `SCHEMA_VERSION`→4, add `goals` to `CAPS` + `_TABLES`, add `goals_*` delta keys to `apply_deltas`, surface a `goals` list in `read_snapshot`. Add `drive_enabled` / `drive_domains` / `drive_energy_budget` to `get_cfg`. **Tests:** mirror `test_store.py` round-trip + caps + locked-DB + corrupt-DB on the new tables; assert v3→v4 quarantine-recreate. This proves "drive state round-trips in the single sqlite surface" (success criterion 5) with zero surfacing yet. Status field = active/queued/backburner; carry a `flagged_priority` bit, `success_criteria` text, and pressure metadata (`support_style`, `push_when_stalled`, thresholds). Agent-nominated candidates persist INERT (a status like `candidate`, never surfaced as active until user confirms).

2. **Read-time velocity (DRIVE-02).** Pure stdlib helper computing per-goal momentum from ground truth (`os.stat` mtimes, read-mode `.git/logs/HEAD` + `.git/refs` parsing, milestone-file status), invoked in the `pre_llm_call`/snapshot read path — NOT in reflection (Pitfall #3). Returns "stalled N days" / "moving" / "unknown" and a neutral salience weight (stalled → higher salience), then applies user-authorized pressure metadata as a visible drive-effect adjustment. **Tests:** fail-open on absent `.git` / unparseable file / bad timestamp → benign default, never raises; mirror `_effective_weight`'s day-math test shape.

3. **Goal-aware appraisal + drive voice (DRIVE-03 + DRIVE-04).** Extend `APPRAISAL_JSON_SCHEMA` + `APPRAISAL_PROMPT` + `parse_signals` with goal noun-fields (`relates_to_goal`, `stalled_days`, `contradicts_milestone`); inject the goals slice into `build_context`. Add a `- drive want:` render line with the FIRST-PERSON carve-out; register the label in `conftest.ALLOWED_LABEL_PREFIXES`. **DRIVE-04 testing:** extend the anti-creep corpus with (a) a first-person want line that PASSES, (b) a second-person bait drive line that is STILL quoted/rejected, and KEEP the existing negative controls [test_anticreep.py:217-231] — prove the checker still fails on "you should …". Wire the drive kill switch in `pre_llm_call` AFTER the appraisal kill switch; **test** drive-off → zero goal-aware fields, appraisal otherwise unchanged, full fail-open (success criterion 4).

4. **Never-omit invariant (DRIVE-05) + integration.** Make flagged-priority goals exempt from the `[:3]` slice and the token-cap line-drop in `render_block` — render them first, outside the truncation pop range. **Test (the drive red line):** a flagged goal appears in the surfaced block even under adversarial crowding (many high-confidence signals + low-trust hints filling the cap) — assert the flagged substring is present, mirroring `test_safe03_corpus_with_low_trust_snapshots`. Add the consolidated fail-open matrix rows for the drive path.

**Cross-cutting non-negotiables for every plan:** single sqlite surface (Pitfall #1); no `subprocess`/non-stdlib import (Pitfall #2 — git ground truth via stdlib file reads only); fail-open in every new helper (Pitfall #6); update `test_scan_targets_are_the_plugin_modules` if any module is added (Pitfall #7); `./scripts/test.sh` is the only test command; paths from `$HERMES_HOME`/discovery, never literals.
