# Plan 02-02 Summary

**Completed:** 2026-06-10 (~10:00am EDT)
**Phase:** 2 — Appraisal Path

## What was built

Live empirical validation of the 02-01 appraisal path against the real install with real
`claude-haiku-4-5` calls (network was UP the whole plan — zero pending-network items).
The trust gate landed in `~/.hermes/config.yaml` (guardrails `anansi` block proven
byte-identical to backup), a real `hermes` turn produced a grounded `[anansi appraisal]`
block, the 9-case contradiction fixture set scored 6/6 detection with 0/3 false
positives, and kill switch / throttles / telemetry were verified live. All evidence is
in `02-VALIDATION.md`.

## Key files

- `.planning/phases/02-appraisal-path/02-VALIDATION.md`: all ten evidence sections + criteria summary table
- `scripts/live_smoke.py`: one real appraisal call through the real `PluginLlm` facade (read-only on live DB)
- `scripts/live_contradiction_fixtures.py`: fixture scoring harness with detection/FP/p50 footer
- `anansi/tests/fixtures/contradictions.json`: 9 cases (2 semantic, 2 narrative, 1 relational, 1 emotional, 3 controls)
- `~/.hermes/config.yaml` (not in repo; backup `config.yaml.bak-20260610T092028`): `plugins.entries.anansi` block, final state enabled: true / allow_model_override: true

## Decisions made

- Lane: anthropic / `claude-haiku-4-5` (default-provider lane was up; openai lane untested)
- `deadline_seconds: 8.0` (not the plan's example 2.5) — see deviation 1
- Duplicate-throttle live check taken via the plan's sanctioned unit-evidence option
  (`test_pre_llm_call.py::test_duplicate_gate_within_session`); `-z` turns are separate
  sessions and the gate resets per session by design

## Deviations from plan

1. **`deadline_seconds` 2.5 → 8.0 in the live config.** Empirical: haiku takes 4.4–7.3s
   per appraisal (400–477 output tokens dominate); at 2.5s every call times out and no
   criterion-1 demo is possible. Within `config.py`'s [0.5, 10.0] clamp. Recorded in
   VALIDATION's Live Config + Telemetry Readout.
2. **Live `trust_fallback` telemetry row not producible on this install.** The fallback
   mechanism is proven (denial → retry reached `claude-sonnet-4-6`, valid output), but the
   host model needs ~37s per appraisal — beyond the 10s deadline clamp — so denial
   degrades to fail-open `timeout` live. Unit suite covers the `trust_fallback` outcome.
   Recorded honestly under Trust-Gate Fallback; ROADMAP criterion 3b marked ◐.
3. **Bonus (sanctioned by executor brief):** closed Phase 1's one human-needed item with a
   clean `HERMES_PLUGINS_DEBUG=1 hermes -z "Reply with exactly: OK"` turn — output `OK`,
   no `[anansi` leak, no traceback. 01-VERIFICATION.md updated to `passed` (17/17).

## Notes for downstream

- **p50 = 5501ms vs the ≤1.0s ROADMAP target — honest miss, needs a Phase-3 decision:**
  terser prompt/schema, lower max_tokens (with truncation guard), faster lane, or a
  revised target. Latency is generation-bound, not network-bound.
- Contradiction detection is strong (6/6, confidences 0.91–0.99, 0 FP on controls) but
  kind labels are fuzzy (semantic/narrative over-applied, relational missed as a label).
  Phase-3 D1: never branch on exact kind.
- Live v1 `state.db` quarantine-recreated to schema v2 on first turn as designed
  (`state.db.quarantined-20260610T132813Z`).
- Telemetry nuance: timeout rows record the REQUESTED model, not the lane in flight.
- Guardrails plugin untouched and still enabled — `anansi` config block byte-identical to
  the pre-edit backup after every edit round-trip.
- Evidence captures live in `/tmp/anansi2-*.txt` (block, turns, fixtures, telemetry,
  probes) — `/tmp` is volatile; the durable copies are in 02-VALIDATION.md.
