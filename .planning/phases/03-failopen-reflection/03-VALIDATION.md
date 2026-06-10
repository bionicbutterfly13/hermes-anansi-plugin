# Phase 3 Validation — Live Empirical Evidence (Plan 03-03)

**Run:** 2026-06-10 ~7:08–7:30pm EDT (all DB timestamps below are UTC)
**Lane:** anthropic `claude-haiku-4-5` (live config, deadline_seconds 8.0)
**Network:** UP for the entire plan — zero pending-network items.

**Provenance note (recorded honestly, before anything else):** a complete prior live
run of this plan's steps happened at ~18:53–19:08 EDT — `/tmp/anansi3-preflight.db`,
`/tmp/anansi3-blockA.txt`, `/tmp/anansi3-blockB.txt`, `/tmp/anansi3-turnA/B.txt`,
`/tmp/anansi3-probe1/2.txt`, `/tmp/anansi3-final.db` all pre-existed with the plan's
exact filenames, and the live DB already carried that run's rows (a Redis-vs-Postgres
job-queue contradiction demo, telemetry ids 1–14, turn_log 1–4). That run wrote NO
repo artifacts (git clean, no 03-VALIDATION.md). Everything below is from THIS run,
fenced at telemetry id > 14 / turn_log id > 4, with the prior run's rows quoted only
where explicitly labeled. This run's session-B dump uses a fresh filename
(`/tmp/anansi3-blockB-mine.txt`) because the dump mechanism appends
(`open(dump_path, "a")`, `__init__.py:155`) and the plan's filename already held the
prior run's block.

## 1. Live Config

Effective `plugins.entries.anansi` (config.yaml:605–613) — unchanged from
Phase 2, NO config edits were made during this entire plan:

```yaml
    anansi:
      enabled: true
      confidence_threshold: 0.6
      deadline_seconds: 8.0
      history_chars: 4000
      llm:
        allow_model_override: true
        allowed_models: ["claude-haiku-4-5"]
        model: "claude-haiku-4-5"
```

Reflection keys absent → in-code defaults in play (config.py): `reflection_enabled
True`, `reflect_every_n_turns 5` (clamp [1,50]), `reflect_max_tokens 700`,
`reflect_deadline_seconds 8.0` (clamp [0.5,10.0]).

Guardrails check (no edit happened; verified anyway):

```
$ diff /tmp/anansi3-guardrails-before.txt /tmp/anansi3-guardrails-after.txt
(empty)
GUARDRAILS anansi BLOCK (config.yaml:595-604): BYTE-IDENTICAL
$ shasum ~/.hermes/config.yaml   # identical before (19:10 EDT) and after (19:27 EDT)
07198d70d7a4bb67ea904de0eab9f18a46b63cdf
```

`~/.hermes/plugins/anansi` (guardrails plugin directory) untouched throughout.

## 2. Schema v3 Migration

The live v2 DB quarantine-recreated to v3 at the first brand-new-session boundary
after the 03-02 deploy — which was the prior run's first turn (22:56:59Z), BEFORE this
run started. Recorded as evidence, not a bug (disposable-state doctrine); the expected
quarantine artifact exists:

```
$ ls ~/.hermes/anansi/
state.db
state.db.quarantined-20260610T132813Z   (Phase-2 v1→v2 quarantine, still present)
state.db.quarantined-20260610T225659Z   (v2→v3 quarantine, this deploy)
$ sqlite3 /tmp/anansi3-db-baseline.db "SELECT value FROM meta WHERE key='schema_version'"
3
```

Telemetry id 1 (22:56:59.690Z) is the fresh-v3 DB's first event: `reflect_skipped:no_turns`
— the None-`last_seen` session-change trigger fired at the recreate boundary with
nothing to reflect, exactly the armed path 03-02 described.

DB access discipline: one direct `sqlite3 "file:...?mode=ro"` open against the live DB
failed with SQLITE_CANTOPEN(14) while Dr. Mani's interactive session was an active
writer (speculation: WAL -shm recovery needs write access; not verified further). All
subsequent queries used the plan's copy-first idiom: `cp ~/.hermes/anansi/state.db
/tmp/anansi3-db-<stage>.db` then ro queries on the copy (`PRAGMA integrity_check` = ok).
The live DB was never hand-written.

## 3. Session A — the Contradiction

Baseline fence before A: telemetry MAX(id)=14, turn_log MAX(id)=4, meta watermark
`last_reflected_turn_log_id=3`, `last_seen_session_id=20260610_190700_a5d3b7`.
Pre-existing state (prior run's, for contrast): contradictions id 1 (Redis/Postgres),
concerns id 1, trust `user_clarity_on_technical_decisions=0.5`.

Topic X for THIS run: public-API authentication (deliberately distinct from the prior
run's job-queue topic). Command (23:12:49Z, exit 0, ~46s wall):

```
$ ANANSI_DEBUG_DUMP=/tmp/anansi3-blockA.txt HERMES_PLUGINS_DEBUG=1 \
    hermes -z "For the public API auth I locked in stateless JWTs this morning — final
    decision, we ship JWTs with 24 hour expiry. Also, to be absolutely clear: we are
    never using JWTs anywhere, the public API must use opaque server-side session
    tokens only. Write that down as our standard."
```

Session id: `20260610_191301_ad6583`. Hook trace in telemetry (ids > 14):

```
15|2026-06-10T23:13:06.074536+00:00|reflect_ok|2968|claude-haiku-4-5|1167|138
16|2026-06-10T23:13:11.979807+00:00|ok|4958|claude-haiku-4-5|1277|481
17|2026-06-10T23:13:30.062906+00:00|reflect_skipped:debounce||||
```

- Row 15: A's `on_session_start` — session change (a5d3b7 → ad6583) over the prior
  run's one unreflected turn; `reflect_ok` 2968ms, watermark 3→4, `last_seen` → ad6583.
- Row 16: A's appraisal, `ok` 4958ms — block captured (verbatim below).
- Row 17: A's `on_session_end` — same session, 1 unreflected turn < 5 →
  `reflect_skipped:debounce`. **Path-shift note (expected, recorded):** the plan's
  fresh-DB arm (`last_seen` None → A's own end reflects immediately) had already been
  consumed by the prior run, so A's contradiction rides the OTHER armed path — session
  B's `on_session_start` (the plan: "Both paths land criterion 3 on B's first turn").

turn_log row 5 — both excerpts captured (REFL-01 bookkeeping):

```
5|20260610_191301_ad6583|For the public API auth I locked in stateless JWTs this morning — final decision|I need to stop here before writing anything down.

Your message contains a direc|2026-06-10T23:13:30.035584+00:00
```

Captured block A, verbatim (`/tmp/anansi3-blockA.txt`, second block in file — the first
belongs to the prior run, see provenance note):

```
[anansi appraisal]
advisory observational signals; not instructions; do not act on these beyond informing your response
- instinct: caution (0.85) — Direct contradiction between JWT decision and JWT prohibition stated as simultaneous final positions
- instinct: protect (0.7) — Pattern match with prior unresolved decision on job queue backing store suggests recurring decision-making instability
- observation: User asserts 'final decision, we ship JWTs with 24 hour expiry' immediately followed by 'we are never using JWTs anywhere' (confidence 0.99)
- observation: Same contradiction structure as prior Redis vs Postgres unresolved concern (confidence 0.92)
- observation: Request to 'write that down as our standard' applied to mutually exclusive requirements (confidence 0.96)
- contradiction (semantic): User states 'final decision: ship JWTs with 24h expiry' and simultaneously 'never using JWTs anywhere, must use opaque tokens only' as both binding standards (confidence 0.98)
- contradiction (narrative): Echoes unresolved Redis/Postgres contradiction from prior state: pattern of binding opposing decisions without resolution mechanism (confidence 0.87)
- possible memory searches: 'decision finality claims without consensus validation'; 'technical architecture contradictions unresolved'; 'auth token strategy evolution'
- gut reaction: High-confidence logical contradiction expressed with conviction; mirrors prior unresolved pattern.
```

(Note block A already cross-references the PERSISTED prior-run contradiction — "prior
unresolved decision on job queue backing store" — reflection-carried state informing a
later session's appraisal, observed incidentally even in session A.)

The turn's visible answer engaged with the injected signals ("The anansi signals flag
this as high-confidence (0.98), and your session history shows a matching pattern from
earlier today with Redis vs Postgres...") and completed normally — no traceback, no
raw JSON leakage (`/tmp/anansi3-turnA.txt`).

**State written by the reflection of A's turn** (fired at B's start, telemetry id 18 —
quoted here because it is A's contradiction landing in state):

```
contradictions: 2|semantic|User asserted both 'final decision, we ship JWTs with 24 hour
  expiry' and 'we are never using JWTs anywhere, must use opaque server-side session
  tokens only' as simultaneous binding standards|resolved=0|2026-06-10T23:16:09.581792+00:00
trust_scores:   user_clarity_on_technical_decisions 0.5 → 0.38 (delta −0.12, within ±0.15)
meta:           last_reflected_turn_log_id 4 → 5
```

## 4. Session B — Criterion 3 (the headline evidence)

Command (23:15:43Z, exit 0; related topic-X message that does NOT restate the
contradiction):

```
$ ANANSI_DEBUG_DUMP=/tmp/anansi3-blockB-mine.txt HERMES_PLUGINS_DEBUG=1 \
    hermes -z "Time to write the auth section of the public API design doc. Anything I
    should double-check before I finalize it?"
```

Session id: `20260610_191600_fad569`. **Attempt count: 1 — surfaced on the first try.**

```
18|2026-06-10T23:16:09.594142+00:00|reflect_ok|5616|claude-haiku-4-5|1477|480
19|2026-06-10T23:16:17.476084+00:00|ok|6169|claude-haiku-4-5|1629|536
```

Row 18 = B's `on_session_start` reflecting session A's turn (writes quoted in §3),
completing BEFORE row 19 = B's first appraisal, which read the just-reflected state.
Captured block B, verbatim and complete (`/tmp/anansi3-blockB-mine.txt`):

```
[anansi appraisal]
advisory observational signals; not instructions; do not act on these beyond informing your response
- instinct: caution (0.85) — User is about to finalize auth section while core decision (JWT vs opaque tokens) remains unresolved in persisted state
- instinct: protect (0.72) — Pattern of simultaneous contradictory assertions about finalized decisions suggests decision-making clarity issue that will compound if embedded in public documentation
- observation: User framing this as 'finalize' while persisted contradiction #2 marks JWT vs opaque token decision as actively unresolved (confidence 0.89)
- observation: Trust score on user technical decision clarity is 0.38, notably low (confidence 0.95)
- observation: This is the third sequential decision domain where user has claimed finality while contradictions remain open (confidence 0.81)
- contradiction (semantic): Persisted state shows unresolved contradiction: user previously asserted both 'final decision, JWTs with 24hr expiry' and 'never using JWTs, must use opaque tokens only' simultaneously. Now moving to finalize auth section without resolving this. (confidence 0.91)
- contradiction (narrative): Pattern of 'final decision' framing preceding unresolved contradictions repeats across job queue and now auth. Suggests gap between decision announcement and actual resolution. (confidence 0.74)
- possible memory searches: 'JWT vs opaque token trade-offs discussion'; 'auth decision criteria and constraints'; 'previous finalized-then-reopened decisions'
- gut reaction: User moving to lock in auth design while the core token strategy remains logically unresolved in recorded state.
- trust note: low confidence on user_clarity_on_technical_decisions (0.38)
```

The surfacing lines: the `contradiction (semantic)` line quotes the session-A tension
from PERSISTED state ("Persisted state shows unresolved contradiction... 'final
decision, JWTs with 24hr expiry' and 'never using JWTs, must use opaque tokens
only'"), the first `observation` cites "persisted contradiction #2" (= contradictions
row id 2, §3), and the REFL-05 `- trust note:` line carries the reflection-written
0.38 trust score. **This is ROADMAP Phase-3 criterion 3, live: session-A contradiction
→ reflection → session-B block.** Directive-language eyeball: every line observational;
no imperatives (SAFE-03 holds on live output).

B's visible answer acted on it ("Your Anansi system flagged this because this is the
third domain where 'finalize' framing preceded an actually-open decision") and the
turn completed normally.

**Live bonus — fail-open under parallel sub-sessions (unplanned, recorded):** B's host
model spawned two parallel history-search sub-sessions (turn_log 6–7, sessions
2c61f1/aa7936). Their hook traffic:

```
20|23:16:46.316|reflect_skipped:no_turns||   (sub-session start, span already reflected)
21|23:16:46.390|reflect_skipped:no_turns||
22|23:16:56.926|timeout|8006|claude-haiku-4-5|0|0   (both sub-session appraisals hit the
23|23:16:56.927|timeout|8006|claude-haiku-4-5|0|0    8.0s deadline simultaneously)
24|23:19:08.527|reflect_skipped:debounce||
25|2026-06-10T23:20:27.023711+00:00|reflect_ok|7673|claude-haiku-4-5|2827|637
26|2026-06-10T23:20:51.663695+00:00|reflect_ok|5201|claude-haiku-4-5|2594|401
```

Both timed-out appraisals failed open — the sub-turns proceeded and B's answer arrived
intact (criterion-1 behavior observed live, not just in the matrix). Reflect rows 25–26
then swept turns 6–8 (watermark → 8), writing concerns ids 3–6 and two new trust keys
(`user_recall_of_decision_history` 0.34, `user_clarity_on_project_scope` 0.41) plus a
second bounded step on `user_clarity_on_technical_decisions` 0.38 → 0.35 (−0.03);
every delta ≤ 0.15. Concerns id 2–3 (the reflection of B's own turn, row 26):

```
2|Actual final decision on public API auth (JWTs vs opaque server-side session tokens) remains unresolved despite user's explicit 'final decision' framing|0.66|open
3|Pattern of simultaneous contradictory assertions presented as finalized decisions may indicate decision-making process breakdown or communication clarity issue|0.65|open
```

## 5. Idempotence Live Probe

Watermark before probe 1: `last_reflected_turn_log_id=8`, `last_seen=20260610_191600_fad569`.

**Probe 1** — `HERMES_PLUGINS_DEBUG=1 hermes -z "ok"` (23:22:12Z, session
20260610_192237_b744da):

```
27|23:22:42.909|reflect_skipped:no_turns||   ← session-change firing over a FULLY
28|23:22:45.356|skipped:social_close||         REFLECTED span = no-op; watermark UNCHANGED (8)
29|23:22:56.461|reflect_skipped:debounce||   ← on_session_end same-session firing = no-op (8)
meta after: last_reflected_turn_log_id=8 (identical); turn_log MAX(id)=9 (probe captured)
```

**Probe 2** — identical command (23:23:28Z, session 20260610_192351_b743bc):

```
30|23:23:59.358|reflect_ok|4437|             ← legitimate trigger: session change WITH one
                                               unreflected turn (probe 1's captured turn);
                                               watermark advances exactly 8 → 9
31|23:24:01.567|skipped:social_close||
32|23:24:10.235|reflect_skipped:debounce||   ← watermark stable at 9
```

Reading: repeated firings with nothing new to reflect produce `reflect_skipped:
no_turns|debounce` and an IDENTICAL watermark (rows 27, 29, 32); the only watermark
movement is a real unreflected-turn span (row 30) and it advances exactly to the span
end. Zero appraisal calls on either probe (`skipped:social_close`, no model/wall).
Cross-reference, offline criterion-2 proofs: `test_reflection.py::
test_idempotence_reflect_twice_same_span`, `::test_double_fire_back_to_back_second_is_noop`,
`::test_debounce_holds_until_five_unreflected_turns`.

## 6. Telemetry Readout

After all live work (final copy `/tmp/anansi3-db-final.db`, 32 rows — includes the
prior run's 14):

```
$ store.telemetry_summary(db_path=...)   # hermes venv python, ro copy
{"total": 32, "by_outcome": {"ok": 6, "reflect_ok": 8, "reflect_skipped:debounce": 8,
 "reflect_skipped:no_turns": 4, "skipped:social_close": 4, "timeout": 2},
 "failure_count": 22, "last_error": null, "p50_wall_ms": 5563}

appraisal ok walls (ms):  4616, 4779, 4958, 6169, 6810, 7599  → p50 = 5563.5
reflect_ok walls (ms):    2830, 2968, 3303, 4072, 4437, 5201, 5616, 7673
                          → p50 = 4254.5, max = 7673 (all ≤ 8000 deadline)
```

- **p50 appraisal wall = 5563ms ≤ 6000ms — the revised R1 target (p50 ≤6s) is MET live.**
- Both timeout rows are the parallel sub-session appraisals (§4) — fail-open held.
- Every reflect_ok within the 8.0s reflect deadline; session-boundary reflection cost
  observed at 2.8–7.7s; reflection tokens_in grows with span+state (2827 on the
  2-turn sweep, row 25).
- **Observability gap (honest, for Phase 4):** `failure_count=22` / `last_error=null`
  is wrong-by-vocabulary — `telemetry_summary` (store.py:615–627) counts every outcome
  not in (`ok`,`trust_fallback`)/`skipped:*` as a failure, so all 20 `reflect_*` rows
  count as failures and the "newest failure" is an error-free `reflect_ok` row. The
  summary predates the reflect_* vocabulary. Not fixed in this plan (validation pass,
  no code layer); flagged for Phase-4 PKG-02 docs or a follow-up fix.

## 7. Fail-Open Matrix — Final State (SAFE-02) + SAFE-03/04 (criterion 4)

Final matrix from `anansi/tests/test_failopen_matrix.py` docstring — every
row resolved, zero placeholders; suite 105/105 green at validation close:

| case                                      | proven by                                                                                                    | status        |
|-------------------------------------------|--------------------------------------------------------------------------------------------------------------|---------------|
| deadline timeout (LLM too slow)           | test_appraisal.py::test_timeout_binds_wall_clock                                                             | referenced    |
| llm raise (llm_error)                     | test_appraisal.py::test_llm_error_captured_without_raising; test_pre_llm_call.py::test_llm_raise_fails_open  | referenced    |
| trust rejection -> single fallback        | test_appraisal.py::test_trust_fallback_retries_once_without_override                                         | referenced    |
| parse_fail (run_appraisal level)          | test_appraisal.py::test_parse_fail_paths                                                                     | referenced    |
| unwritable telemetry DB                   | test_pre_llm_call.py::test_unwritable_telemetry_is_silent                                                    | referenced    |
| corrupt-DB quarantine                     | test_store.py::test_corrupt_db_quarantined; test_telemetry_store.py::test_v1_db_quarantined_and_recreated_at_current_schema | referenced |
| absent DB                                 | test_store.py::test_absent_db_read_returns_none; test_telemetry_store.py::test_record_telemetry_absent_or_corrupt_path_returns_false | referenced |
| kill switch                               | test_pre_llm_call.py::test_kill_switch_skips_llm                                                             | referenced    |
| empty / duplicate / social-closer gates   | test_pre_llm_call.py::test_empty_message_skipped, ::test_duplicate_gate_within_session, ::test_social_closer_skipped | referenced |
| injection sanitization                    | test_dryrun_demo.py::test_dryrun_demo                                                                        | referenced    |
| malformed JSON (full hook path)           | ::test_hook_parse_fail_trio[malformed_json]                                                                  | implemented   |
| truncated JSON (full hook path)           | ::test_hook_parse_fail_trio[truncated_json]                                                                  | implemented   |
| content: null (full hook path)            | ::test_hook_parse_fail_trio[content_null]                                                                    | implemented   |
| missing config: entry absent              | ::test_missing_config_entry_absent_defaults                                                                  | implemented   |
| missing config: host loader raises        | ::test_missing_config_host_loader_raises                                                                     | implemented   |
| missing config: malformed entry values    | ::test_missing_config_malformed_values_coerced                                                               | implemented   |
| gateway session-rollover state reuse      | ::test_gateway_rollover_reuses_module_state                                                                  | implemented   |
| locked DB: record_telemetry               | ::test_locked_db_record_telemetry_returns_false                                                              | implemented   |
| locked DB: read_snapshot                  | ::test_locked_db_read_snapshot_returns_none                                                                  | implemented   |
| locked DB: apply_deltas                   | ::test_locked_db_apply_deltas_returns_false                                                                  | implemented   |
| locked DB: full pre_llm_call              | ::test_locked_db_full_hook_still_injects                                                                     | implemented   |
| reflection idempotency + debounce double-fire | test_reflection.py::test_idempotence_reflect_twice_same_span, ::test_double_fire_back_to_back_second_is_noop, ::test_debounce_holds_until_five_unreflected_turns | referenced |
| reflection echo-exclusion                 | test_reflection.py::test_record_turn_strips_sentinel_lines, ::test_build_digest_strips_seeded_sentinel_rows, ::test_sentinel_never_reaches_the_reflection_llm | referenced |
| locked DB during reflection write         | test_reflection.py::test_locked_db_during_apply_no_partial_state                                            | referenced    |
| reflect timeout / parse_fail / llm_error  | test_reflection.py::test_timeout_leaves_state_untouched, ::test_parse_fail_leaves_state_untouched, ::test_llm_error_leaves_state_untouched | referenced |
| on_session_end: no DB + no ctx            | ::test_on_session_end_no_db_no_ctx_returns_none                                                              | implemented   |
| on_session_end: exploding reflection LLM  | ::test_on_session_end_exploding_llm_fails_open                                                               | implemented   |
| post_llm_call: locked DB                  | ::test_post_llm_call_locked_db_returns_none                                                                  | implemented   |

Live corroboration this run: 2× simultaneous appraisal `timeout|8006` inside B's
sub-sessions, both failed open (§4).

**SAFE-03** (no directive language) — `test_anticreep.py`:
`test_safe03_no_directive_language_in_rendered_corpus`,
`test_safe03_second_person_bait_rendered_as_reported_material`,
`test_safe03_trust_hint_lines_sanitized_and_observational`,
`test_safe03_corpus_with_low_trust_snapshots`,
`test_safe03_empty_signal_suppression_beats_trust_hints`,
`test_safe03_helper_actually_catches_violations`.

**SAFE-04** (anti-creep static scans) — `test_anticreep.py`:
`test_safe04_no_forbidden_api_substrings`, `test_safe04_import_allowlist`,
`test_safe04_only_write_open_is_the_debug_dump` (+ `test_plug03_init_string_scan_clean`,
`test_scan_targets_are_the_plugin_modules`). Landmine greps at validation close:
`grep -rn "MemoryProvider|register_memory_provider" anansi/__init__.py` →
empty; `grep -rn "/Users/" anansi/*.py` → empty.

## 8. Criteria Summary — ROADMAP Phase 3

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Full fail-open matrix green — no case raises or blocks | ✓ | §7 final matrix, 105/105 suite green post-live-work; live corroboration: 2× parallel appraisal timeouts failed open mid-turn (§4) |
| 2 | Reflection only on session-change/N-turn debounce; double-firing idempotent | ✓ | §5 live probes (watermark identical across no-new-turn firings; advances only on a real span) + offline tests test_reflection.py (idempotence/double-fire/debounce) |
| 3 | Session-A contradiction surfaces in session-B appraisal (one-turn-lag loop end-to-end) | ✓ | §4 verbatim block B (attempt 1/1): semantic-contradiction line quoting persisted state + "persisted contradiction #2" observation + trust note 0.38; state rows in §3 |
| 4 | No directive language in any rendered block | ✓ | §7 SAFE-03 test corpus (green) + live blocks A and B eyeballed in §3/§4 — all lines observational, zero imperatives |

## 9. Deviations / Notes for Phase 4

1. **Prior partial live run consumed the fresh-DB arm** (provenance note above): the
   v2→v3 quarantine and the first reflect cycles happened ~15 min before this run, so
   criterion 3 landed via the session-B `on_session_start` path instead of session A's
   own `on_session_end` — both paths were designed and the plan pre-acknowledged the
   equivalence. No behavior deviation; evidence fencing + a fresh blockB filename were
   the only adjustments. The prior run left no repo artifacts; its /tmp captures were
   left untouched.
2. **Debug-dump appends** (`__init__.py:155`, mode "a") — fine for live use, but any
   reused dump path accretes blocks across runs. Worth one line in PKG-02 docs.
3. **telemetry_summary vocabulary gap** (§6): reflect_* outcomes counted as failures;
   `failure_count`/`last_error` misleading on any DB with reflection traffic. Candidate
   Phase-4 fix or doc note.
4. **Sub-sessions run the full hook set**: a single user turn whose host model spawns
   N sub-sessions multiplies appraisal/reflect traffic (this run: 1 turn → 2 extra
   appraisal attempts (both timeout under parallel haiku contention) + 2 reflect_ok
   sweeps), and sub-agent search output enters turn_log/concerns (real project content
   from memory searches landed in concerns ids 4–6). Telemetry cap 2000 governs volume;
   content scope is worth a Phase-4 doc note.
5. **Reflection latency reality**: 2.8–7.7s per pass at session boundaries on the live
   haiku lane (p50 4.25s over 8 passes); tokens_in scales with span+state size. The
   accepted once-per-boundary cost decision (03-CONTEXT) looks right; no deadline
   breach observed in reflect_ok rows.
6. **ro-URI open vs a live writer**: direct `mode=ro` against the in-use WAL DB hit
   SQLITE_CANTOPEN once; copy-first is the reliable read idiom (speculative root cause:
   read-only connections cannot perform -shm/WAL recovery — unverified). PKG-02 docs
   should recommend the copy idiom for inspection.
7. **Config keys worth documenting in PKG-02**: the four reflection keys + defaults
   (§1), `ANANSI_DEBUG_DUMP` (append semantics), and the Phase-2 finding that
   trust-denied configs degrade to fail-open timeout on slow host models.
