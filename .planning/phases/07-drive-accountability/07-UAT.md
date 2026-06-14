---
status: complete
phase: 07-drive-accountability
source: [07-01-SUMMARY.md, 07-02-SUMMARY.md, 07-03-SUMMARY.md, 07-04-SUMMARY.md]
started: 2026-06-14T17:40:00-04:00
updated: 2026-06-14T17:40:00-04:00
---

## Current Test
number: 1
name: Live goal-surfacing turn
expected: |
  A user-minted goal surfaces in the appraisal block of a REAL model turn,
  in the first-person owned-want voice ("- drive want: I want ...").
awaiting: none — drive live-harness built + run; Criterion 1 INCONCLUSIVE on environment (model providers unavailable), see Gaps

## Tests

### 1. Live goal-surfacing turn (Criterion 1)
expected: A real `hermes` turn (real model, real host facade) surfaces a user-minted goal in the `[anansi appraisal]` block as a `- drive want:` / `- drive note:` line, first-person, no "you should".
result: inconclusive (environment) — `scripts/live_drive_smoke.py` ran the real host facade + minted a flagged goal, but the appraisal returned `outcome=timeout` (deadline 8.0s) because the host model providers are unavailable: openrouter (payment/credit error) + nous (no auth, `run: hermes auth`); cfg `model: null` routed to those aux providers. NOT a drive-code defect — surfacing logic is proven by the offline full-hook suite (test_drive_neveromit.py). Re-run the harness after restoring a working provider to get the live PASS.

### 2. First-person carve-out, second-person still neutralized (Criterion 2)
expected: Anti-creep tests pass with the new `- drive want:` first-person line; planted second-person "you should…" is still quoted/neutralized; negative controls still fail on directives.
result: pass — proven by suite (test_anticreep.py + symmetric control; 165/165 green, verifier f52614c)

### 3. Never-omit under crowding (Criterion 3)
expected: A flagged-priority goal always appears in the surfaced block — survives the [:3] slice, the token cap, and an exhausted energy budget — even when the model omits it.
result: pass — proven by suite (test_drive_neveromit.py crowding + full-hook tests)

### 4. Drive kill switch off (Criterion 4)
expected: With drive disabled, zero goal-aware fields inject; the block is byte-for-byte identical to a no-goals run; appraisal otherwise unchanged; full fail-open preserved.
result: pass — proven by suite (byte-for-byte invariant + skipped:drive_disabled non-failure telemetry)

### 5. Drive state round-trip + degraded DB (Criterion 5)
expected: Goal state round-trips the single SQLite surface (schema v4); locked-DB / corrupt-DB degrade silently without raising.
result: pass — proven by suite (test_drive_store.py + test_failopen_matrix.py rows)

## Summary

total: 5
passed: 4
issues: 0
inconclusive_env: 1
pending: 0
skipped: 0
note: 0 code issues. The single non-pass (Test 1) is blocked on model-provider credentials, not on drive code. Re-run scripts/live_drive_smoke.py once a provider works.

## Gaps

- truth: "A real model turn surfaces a minted goal in the appraisal block"
  status: blocked-env
  reason: >
    Drive live-harness (scripts/live_drive_smoke.py) built + run: it minted a flagged goal by hand
    and invoked the REAL host facade (no live-state writes), but the appraisal returned
    outcome=timeout (deadline 8.0s) because the host model providers are unavailable — openrouter
    (payment/credit error) and nous (no auth: `run: hermes auth`); cfg model:null routed to those
    aux providers. The drive surfacing path is proven by the offline full-hook suite
    (test_drive_neveromit.py); the live PASS is blocked only on provider credentials.
  fix: >
    Restore a working provider (run `hermes auth`, fix openrouter billing, or pin an anthropic
    appraisal model with a valid key), then re-run
    `$HERMES_HOME/hermes-agent/venv/bin/python scripts/live_drive_smoke.py` (exit 0 = live PASS).
  severity: env-blocked (NOT a drive-code defect)
  test: 1
