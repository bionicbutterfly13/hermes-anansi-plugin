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

(pending — task 02-02-03)

## Kill Switch

(pending — task 02-02-03)

## Throttles

(pending — task 02-02-03)

## Contradiction Fixtures (Phase-0 item 6)

(pending — task 02-02-02)

## Real-Turn Demo

(pending — task 02-02-03)

## Telemetry Readout (Phase-0 item 7)

(pending — task 02-02-03)

## Model Quirks (Phase-0 item 5)

(pending — collected across smoke/fixtures/turns; so far: claude-haiku-4-5 is VERBOSE on
this schema — 400–460 output tokens per appraisal, dominating wall time at ~4.5s warm.
No param rejections; JSON parsed cleanly on every completed call.)
