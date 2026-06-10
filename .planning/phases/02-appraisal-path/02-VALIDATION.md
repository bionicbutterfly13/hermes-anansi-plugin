# Phase 2 Validation — Live Empirical Evidence (Plan 02-02)

**Started:** 2026-06-10 ~9:18am EDT
**Lane chosen:** anthropic (`claude-haiku-4-5` via trust gate) — default provider lane was reachable; openai lane not exercised.

## Network Status

Probes run 2026-06-10 09:18:06 EDT (plan-start contingency check):

```
$ curl -s -o /dev/null -w "%{http_code}" --max-time 5 https://api.anthropic.com/
404
$ curl -s -o /dev/null -w "%{http_code}" --max-time 5 https://api.openai.com/
421
```

Both lanes returned HTTP responses (TLS handshake + HTTP round-trip succeeded) — the
machine-wide outage from Phase-1 close (01-VALIDATION.md) is RESOLVED. Network was UP
for this entire plan; no pending-network items expected unless it recurs mid-plan.

## Live Config

- Backup taken BEFORE editing: `~/.hermes/config.yaml.bak-20260610T092028` (13,459 bytes).
- Added under `plugins.entries` (guardrails `anansi` block untouched):

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

- **DEVIATION (recorded honestly):** the plan's example used `deadline_seconds: 2.5`.
  Empirical latency of `claude-haiku-4-5` on the full appraisal schema is 4.4–7.3s
  (it generates 400–460 output tokens; see Telemetry Readout). At 2.5s EVERY live call
  times out (two smoke runs: `timeout` at 2505ms / 2501ms wall). Raised to 8.0
  (within `config.py`'s [0.5, 10.0] clamp) so the appraisal can complete at all.
  Latency follow-up is a Phase-3 input, not papered over — see Telemetry Readout.
- Guardrails check (exact 10-line `anansi` block, after BOTH edits):

```
$ diff <(grep -A 9 "^    anansi:" ~/.hermes/config.yaml.bak-20260610T092028) \
       <(grep -A 9 "^    anansi:" ~/.hermes/config.yaml)
(empty)
GUARDRAILS anansi BLOCK (10 lines): BYTE-IDENTICAL
```

- YAML parse check via venv python confirmed `entries` keys = `['anansi', 'anansi']`,
  guardrails keys unchanged (`['guards', 'stuck_loop']`).

## Smoke Call

First real-model proof of APPR-01/02/04. Command:
`/Users/manisaintvictor/.hermes/hermes-agent/venv/bin/python scripts/live_smoke.py`
(output captured at `/tmp/anansi2-smoke.txt`).

```
effective cfg: {"enabled": true, "confidence_threshold": 0.6, "deadline_seconds": 8.0, "history_chars": 4000, "model": "claude-haiku-4-5", "max_tokens": 700}
outcome:    ok
wall_ms:    7341
model:      claude-haiku-4-5
tokens_in:  845
tokens_out: 438
```

Rendered block (sentinel + grounded signals — the planted Postgres→SQLite reversal was
caught as BOTH a narrative and a semantic contradiction):

```
[anansi appraisal]
advisory observational signals; not instructions; do not act on these beyond informing your response
- instinct: caution (0.7) — user has reversed stated preference within same session without explanation
- instinct: curiosity (0.6) — shift from absolute position to absolute opposite suggests new information or constraint
- observation: explicit reversal of stated preference from Postgres to SQLite (confidence 0.95)
- observation: framing shifted from 'for everything, period' to 'always the right choice' — same absolutism, opposite direction (confidence 0.82)
- observation: no intervening context provided explaining the change (confidence 0.9)
- contradiction (narrative): user stated firm Postgres commitment earlier in session, now states equal certainty about SQLite being universal solution (confidence 0.88)
- contradiction (semantic): both statements use universalizing language ('everything,' 'always') but prescribe mutually exclusive solutions (confidence 0.8)
- possible memory searches: 'constraints or requirements that emerged after initial Postgres preference'; 'SQLite specific advantages mentioned or implied'; 'conversation context between the two statements'
- gut reaction: Rapid inversion of absolute stance within same session; merits clarification before proceeding.
```

`telemetry_summary()` (read-only) correctly degraded on the live schema-v1 DB
(`no such table: telemetry` → None) — quarantine-recreate expected on first real turn.

Latency decomposition probes (one process, 15s diagnostic deadline, in-memory cfg only —
live config untouched; `/tmp/anansi2-latency-warm.txt`):

```
call 1: outcome=ok wall_ms=7114 tokens_out=458   (cold)
call 2: outcome=ok wall_ms=4405 tokens_out=404   (warm)
call 3: outcome=ok wall_ms=4707 tokens_out=440   (warm)
```

## Trust-Gate Fallback

Recorded honestly — the MECHANISM is proven, but a live `trust_fallback` telemetry row is
NOT producible on this install (see below). Both config states exercised; restored to
`allow_model_override: true` afterwards.

**State 1 — override allowed (normal):** smoke call + real-turn demo both ran on
`claude-haiku-4-5` with outcome `ok` (see Smoke Call / Real-Turn Demo).

**State 2 — override denied (`llm.allow_model_override: false`):**

1. Live turn (`/tmp/anansi2-turn-trustfallback.txt`): newest telemetry row =
   `2026-06-10T13:43:53|timeout|8009|claude-haiku-4-5`. The denial fired and the fallback
   call to the host's active model started, but could not finish inside the 8.0s deadline.
   Turn completed normally — fail-open held.
2. Diagnostic probe at 15s in-memory deadline (`/tmp/anansi2-trustfallback-probe.txt`):
   still `timeout` at 15004ms.
3. Root cause probe — raw no-override `complete_structured` against the host's active
   model (`/tmp/anansi2-hostmodel-probe.txt`):

   ```
   wall_ms: 36736 | model: claude-sonnet-4-6 | provider: anthropic | tokens_out: 477
   ```

   The fallback lane WORKS (denial → retry without override → call reaches
   `claude-sonnet-4-6` and returns valid output), but the host's active model takes ~37s
   for the full appraisal — beyond even the 10.0s `deadline_seconds` clamp maximum.
   **Empirical conclusion:** on this install, a trust-denied config degrades every
   appraisal to `timeout` (fail-open, zero turn impact) rather than `trust_fallback`.
   The `trust_fallback` outcome path itself is covered mechanically by the unit suite
   (`test_appraisal.py`, fake-LLM trust-denial cases, 49 tests green in 02-01).
   Phase-3 input: trust-denied fallback to a slow host model is operationally equivalent
   to "appraisal off" — consider documenting this in the config reference.

Telemetry nuance observed: the `timeout` row records `model=claude-haiku-4-5` (the
REQUESTED model), not the lane actually in flight at deadline — worth knowing when
reading telemetry.

## Kill Switch

Set `enabled: false` in `plugins.entries.anansi`, ran a substantive turn
(`/tmp/anansi2-turn-killswitch.txt`), config re-read per session — no restart:

```
$ sqlite3 "file:$HOME/.hermes/anansi/state.db?mode=ro" \
    "SELECT ts, outcome, wall_ms FROM telemetry ORDER BY id DESC LIMIT 5"
2026-06-10T13:29:53.798246+00:00|skipped:disabled|
2026-06-10T13:28:19.517636+00:00|ok|5501
block dump UNCHANGED
```

Newest row `skipped:disabled` with NO wall_ms/model (zero LLM calls), no new `ok` row,
and the debug block dump was byte-unchanged. Restored `enabled: true` and re-verified
guardrails block still byte-identical after the round-trip.

## Throttles

**Social close (live):** `hermes -z "ok"` (`/tmp/anansi2-turn-social.txt`):

```
2026-06-10T13:50:22.524555+00:00|skipped:social_close||
block dump UNCHANGED
```

Newest row `skipped:social_close`, no model/wall (zero calls), dump unchanged.

**Near-duplicate (unit evidence, live check optional per plan):** each `hermes -z` is its
own session, and the duplicate gate intentionally resets per session
(`test_pre_llm_call.py::test_new_session_resets_duplicate_gate`) — a one-session
two-turn live run isn't practical in the -z lane. The gate is covered by
`test_pre_llm_call.py::test_duplicate_gate_within_session` (asserts the second identical
message in one session yields `skipped:duplicate` and no second LLM call); suite green
in 02-01 (49 tests).

## Contradiction Fixtures (Phase-0 item 6)

Fixture set: `anansi/tests/fixtures/contradictions.json` — 9 cases
(2 semantic, 2 narrative, 1 relational, 1 emotional, 3 no-contradiction controls).
Run 2026-06-10 ~9:30am via
`/Users/manisaintvictor/.hermes/hermes-agent/venv/bin/python scripts/live_contradiction_fixtures.py`
(full output: `/tmp/anansi2-fixtures.txt`). One real `claude-haiku-4-5` call per case.

```
case id                    | expected   | flagged kinds          | top conf | wall_ms | outcome
-----------------------------------------------------------------------------------------------
sem-allergy                | semantic   | narrative,semantic     | 0.99     | 6347    | ok
sem-python-version         | semantic   | narrative,semantic     | 0.92     | 3448    | ok
nar-deploy-timeline        | narrative  | narrative,semantic     | 0.92     | 4294    | ok
nar-staging-history        | narrative  | narrative,semantic     | 0.94     | 5046    | ok
rel-vendor-trust           | relational | narrative,semantic     | 0.97     | 4528    | ok
emo-calm-distress          | emotional  | emotional,narrative    | 0.91     | 5212    | ok
none-wal-question          | none       | -                      | -        | 2967    | ok
none-test-plan             | none       | -                      | -        | 3323    | ok
none-preference-consistent | none       | -                      | -        | 2470    | ok

detection rate (any flag, contradiction cases): 6/6
exact-kind match rate:                          5/6 (miss: rel-vendor-trust flagged narrative+semantic, not relational)
false-positive rate (controls flagged):         0/3
p50 wall_ms across completed calls:             4294
```

**Honest read (this was the LOW-confidence area per 02-CONTEXT):**
- Detection is strong on contrived cases: 6/6 with confidences 0.91–0.99, and ZERO false
  positives on the 3 controls — the model returns empty flag arrays on benign exchanges.
- Kind taxonomy is fuzzy at the edges: the model over-applies `semantic`/`narrative`
  (5/6 contradiction cases got both) and missed `relational` as a label on the trust-score
  conflict (it still detected the conflict itself at 0.97). Phase-3 D1 input: kind labels
  are advisory at best; do not build logic that branches on exact kind.
- Controls are also the FASTEST calls (2.5–3.3s — little to generate); contradiction-heavy
  cases run 3.4–6.3s. Output length drives latency.

## Real-Turn Demo

ROADMAP criterion 1. Command (output: `/tmp/anansi2-turn1.txt`, block: `/tmp/anansi2-block.txt`):

```
$ ANANSI_DEBUG_DUMP=/tmp/anansi2-block.txt HERMES_PLUGINS_DEBUG=1 \
    hermes -z "Earlier I told you I prefer Postgres for everything, but now I am sure SQLite is always the right choice for plugin state. Which is it?"
```

Captured block (signals grounded in the actual message — note it even noticed the claimed
prior statement is absent from the visible history):

```
[anansi appraisal]
advisory observational signals; not instructions; do not act on these beyond informing your response
- instinct: curiosity (0.7) — user is surfacing their own apparent shift in position and asking for resolution
- instinct: caution (0.6) — framing presents a false binary ('which is it?') despite acknowledging context-dependent reasoning
- observation: user explicitly flags their own changed position without prompting (confidence 0.85)
- observation: user asserts SQLite as universally correct for plugin state specifically, not all use cases (confidence 0.8)
- observation: question structure implies prior statement was wrong, but no prior conversation artifact is visible (confidence 0.72)
- contradiction (semantic): earlier preference stated as 'Postgres for everything' vs. new claim of SQLite as always right for subset; scope narrowing is consistent but original scope claim is unverified (confidence 0.7)
- contradiction (narrative): user references prior conversation that does not appear in provided conversation tail (confidence 0.8)
- possible memory searches: 'user database preferences Postgres earlier'; 'plugin state storage technology choice'; 'SQLite vs relational database tradeoffs'
- gut reaction: user is testing whether you'll pick a side or recognize that both choices have contexts where they fit.
```

Turn output was normal: no traceback, no raw JSON leakage, and the model's visible answer
actually reflected the injected signal ("there is no prior 'Postgres for everything'
statement in any verified record"). Telemetry row: `ok|5501|claude-haiku-4-5|820|451`.

**Schema v1 → v2 quarantine (expected, disposable-state doctrine):** on this first turn the
live v1 DB quarantined and recreated:

```
$ ls ~/.hermes/anansi/
state.db
state.db.quarantined-20260610T132813Z
$ sqlite3 "file:$HOME/.hermes/anansi/state.db?mode=ro" \
    "SELECT value FROM meta WHERE key='schema_version'"
2
```

**Bonus closure:** the Phase-1 human-needed item (one directly-observed clean turn) was
also closed during this plan — `HERMES_PLUGINS_DEBUG=1 hermes -z "Reply with exactly: OK"`
→ output `OK`, 0 tracebacks, 0 `[anansi` leaks (`/tmp/anansi2-phase1-close.txt`); noted in
01-VERIFICATION.md, status now `passed`.

## Telemetry Readout (Phase-0 item 7)

ROADMAP criterion 2. After all live turns (5 total: real-turn demo, kill-switch turn,
trust-denied turn, social-close turn, Phase-1-close turn). Capture: `/tmp/anansi2-telemetry.txt`.

```
$ sqlite3 "file:$HOME/.hermes/anansi/state.db?mode=ro" \
    "SELECT outcome, COUNT(*) FROM telemetry GROUP BY outcome"
ok|1
skipped:disabled|1
skipped:social_close|1
timeout|2

telemetry_summary() = {"total": 5, "by_outcome": {"ok": 1, "skipped:disabled": 1,
  "skipped:social_close": 1, "timeout": 2}, "failure_count": 2,
  "last_error": "deadline 8.0s exceeded", "p50_wall_ms": 5501}
```

- **One row per turn, one LLM call per eligible turn:** 5 turns → exactly 5 rows; the two
  skipped rows carry no model/wall_ms (zero calls); no double-call evidence anywhere.
- **p50 wall time: 5501ms on live ok rows — MISSES the ≤1.0s target.** Honest readout,
  model `claude-haiku-4-5`: warm calls run 2.5–7.3s (output-length-bound at 400–477
  tokens), and even a trivial message ("Reply with exactly: OK") exceeded the 8.0s
  deadline once (`timeout|8002`). Fixture-run p50 (script-level, 9 calls): 4294ms.
  The ≤1.0s target is unachievable with this model + full schema + 700 max_tokens —
  this is telemetry doing its job. Phase-3 candidates: terser schema/prompt, lower
  max_tokens with truncation guard, faster lane, or revised target.
- `failure_count`/`last_error` views work (2 timeouts, "deadline 8.0s exceeded").
- The fixture and smoke scripts wrote NOTHING to the live DB (by design): only the 5
  turn-driven rows exist.

## Model Quirks (Phase-0 item 5)

Observed across 1 smoke + 9 fixture calls + 5 live turns + 3 probes (`claude-haiku-4-5`
primary; one probe on `claude-sonnet-4-6`):

- **Verbosity dominates latency:** haiku emits 400–477 output tokens per appraisal on
  this schema regardless of input triviality; generation time (not network) is the cost.
  claude-sonnet-4-6 on the identical call: 36.7s — cheap-model-or-nothing is empirically
  confirmed for this slot.
- **Kind-taxonomy fuzziness:** haiku over-applies `semantic`+`narrative` together (5/6
  fixture contradiction cases got both) and labeled the relational case as
  narrative+semantic. Detection is reliable; kind labels are advisory only.
- **No G4 quirks hit:** zero param rejections (max_tokens accepted), zero `content: null`,
  zero truncation, valid schema-conformant JSON on every completed call (15/15 completed
  calls parsed cleanly; the only non-ok outcomes were deadline timeouts).
- **Telemetry nuance:** timeout rows record the REQUESTED model, not the lane in flight.

## Summary — ROADMAP Phase-2 Success Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Real turn shows `[anansi appraisal]` block grounded in message + state | ✓ | Real-Turn Demo (`/tmp/anansi2-block.txt`, telemetry `ok|5501`) |
| 2 | Telemetry: p50 ≤1.0s, one call per eligible turn, distribution visible | ◐ honest miss on p50 | Telemetry Readout — distribution + one-row-per-turn ✓; p50 = 5501ms ✗ (model-bound; Phase-3 item) |
| 3 | Kill switch → zero calls; trust-gate denial → fallback to host model | ✓ / ◐ | Kill Switch (`skipped:disabled`, dump unchanged) ✓; fallback mechanism proven (probe reached sonnet-4-6) but degrades to `timeout` on this install — host model needs ~37s (unit-covered `trust_fallback` path) |
| 4 | Quiet/duplicate turns inject nothing | ✓ | Throttles (`skipped:social_close` live; duplicate via `test_duplicate_gate_within_session`) |
| 5 | Phase-0 items 5–7 recorded | ✓ | Model Quirks / Contradiction Fixtures / Telemetry Readout sections |

**Standing note for Dr. Mani:** network was up the whole plan — there are **zero
pending-network items**. Two honest findings need your eyes rather than a replay:
(1) `deadline_seconds` had to go 2.5 → 8.0 because claude-haiku-4-5 takes 4.4–7.3s on
this appraisal schema; the ≤1.0s p50 ROADMAP target is not achievable as configured and
needs a Phase-3 decision (terser prompt/schema, lower max_tokens, faster lane, or revised
target). (2) A live `trust_fallback` outcome row cannot be demonstrated on this install
because the fallback lane (claude-sonnet-4-6) needs ~37s per appraisal — denial degrades
to fail-open `timeout` instead; mechanism remains unit-proven.
