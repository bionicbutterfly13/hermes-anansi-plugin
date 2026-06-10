---
phase: 2
status: passed
verified: 2026-06-10
verifier_note: "Test suite run via staged pytest (PYTHONPATH=/tmp/anansi-verify-pytest) because pytest is no longer importable from the hermes venv — see Environment Note"
---

# Phase 2: Appraisal Path — Verification

**Goal:** Every eligible turn gets a grounded, capped, sanitized appraisal block — within budget.

## Test Suite

```
$ PYTHONPATH=/tmp/anansi-verify-pytest /Users/manisaintvictor/.hermes/hermes-agent/venv/bin/python -m pytest anansi/tests -q
49 passed in 1.96s
```

Dry-run demo (`test_dryrun_demo.py -q -s`) prints a full sanitized end-to-end block: sentinel header,
framing line, below-threshold instinct absent, injection text neutralized as `[REDACTED]`, 1 passed.

**Environment Note (not a code gap):** `pytest` is no longer installed in
`/Users/manisaintvictor/.hermes/hermes-agent/venv` — the documented test command from the 02-01 plan
fails with `No module named pytest` as of 2026-06-10 ~5:30pm EDT. Verification staged pytest 9.0.3 into
a temp dir (`uv pip install --python <venv-python> --target /tmp/anansi-verify-pytest pytest`) and ran
via `PYTHONPATH` — the live venv was not modified. The suite itself is fully green (no skips:
`agent.plugin_llm` imported successfully, so all fake-LLM tests executed).

## Success Criteria (ROADMAP Phase 2, criterion 2 as revised 2026-06-10 R1)

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Real turn shows `[anansi appraisal]` block grounded in message + state | ✓ | 02-VALIDATION.md "Real-Turn Demo": full captured block (instincts, observations, 2 contradiction flags grounded in the Postgres→SQLite reversal prompt); matching live telemetry row `2026-06-10T13:28:19 | ok | 5501 | claude-haiku-4-5 | 820/451` confirmed by direct DB query |
| 2 | p50 ≤6s within 8.0s default deadline; one LLM call per eligible turn; distribution visible | ✓ | Live DB (read-only copy): 3 `ok` rows walls 5501/5715/6460 → **p50 = 5715ms ≤ 6000ms** (small n; VALIDATION's recorded p50 5501ms also ≤6s). Deadline 8.0s in live config (`~/.hermes/config.yaml:608`); 2 `timeout` rows at 8002/8009ms prove the deadline binds and fails open. Distribution: `ok=3, skipped:disabled=1, skipped:social_close=1, timeout=2` (7 rows). Skipped rows carry no model/wall_ms (zero calls); one row per turn cross-checked in VALIDATION (5 turns → 5 rows at validation time) |
| 3a | Kill switch off → zero appraisal calls | ✓ | Live telemetry row `2026-06-10T13:29:53 | skipped:disabled` with NULL wall_ms/model/tokens (confirmed by DB query); block dump byte-unchanged (02-VALIDATION.md "Kill Switch") |
| 3b | Trust-gate denial → automatic fallback | ✓ (per R3 annotation) | Mechanism unit-proven: trust-denial fake-LLM cases in `test_appraisal.py` (in the 49-green suite) assert denial → single no-override retry → `trust_fallback` outcome. Live: denial probe reached `claude-sonnet-4-6` (~37s) — beyond the 10s deadline clamp, so live denial degrades to fail-open `timeout` (row `13:43:53 | timeout | 8009`). REQUIREMENTS.md APPR-06 R3 annotation (2026-06-10) records this as the accepted/correct outcome on this install |
| 4 | Quiet/duplicate turns inject nothing | ✓ | Live row `13:50:22 | skipped:social_close` with NULL model/wall (DB query) + dump unchanged; duplicate gate via `test_pre_llm_call.py::test_duplicate_gate_within_session` + `test_new_session_resets_duplicate_gate` (plan-sanctioned unit evidence — `-z` turns are separate sessions) |
| 5 | Phase-0 items 5–7 recorded | ✓ | 02-VALIDATION.md: "Model Quirks" (item 5 — verbosity-bound latency, kind-taxonomy fuzziness, zero G4 quirks in 15/15 parsed calls), "Contradiction Fixtures" (item 6 — 9 cases, 6/6 detection at 0.91–0.99, 0/3 false positives, 5/6 exact-kind), "Telemetry Readout" (item 7 — distribution + p50 + failure_count/last_error) |

## Requirement Coverage

| Req ID | Deliverable | Status |
|--------|-------------|--------|
| APPR-01 | One `complete_structured` JSON call per eligible turn over message + history + snapshot: `__init__.py:77-143` (`pre_llm_call` → `run_appraisal`), `appraisal.py:273-274` (single call; :267 is the lone trust-fallback retry), `build_context` `appraisal.py:143`, snapshot read `__init__.py:105` | ✓ |
| APPR-02 | Fresh observation-only prompt `appraisal.py:36-62` ("never include directives, advice, suggested actions, goals" :61); noun-only `APPRAISAL_JSON_SCHEMA` :69; instinct vocabulary {approach, avoid, caution, curiosity, protect} :64; contradiction kinds {semantic, narrative, relational, emotional} :65; gut_reaction ≤200; searches advisory text :57. No dopamine/goals/emotional-state fields anywhere | ✓ |
| APPR-03 | Confidence threshold default 0.6, clamped [0,1] (`config.py:12,113-116`); `parse_signals` drops sub-threshold signals (`appraisal.py:365+`); threshold tests green | ✓ |
| APPR-04 | `render.py`: sentinel :19, 500-token cap (len//4 → 2000 chars) :25/:160, top-3 slices :125/:134/:142/:153, icarus-derived `_INJECTION_PATTERNS` :28 + `_validate_safe_content` :58; dry-run shows `[REDACTED]` neutralization live | ✓ |
| APPR-05 | Empty-signal suppression: `render_block` returns None at `render.py:113` and :122; suppression unit tests in suite | ✓ |
| APPR-06 | Model separately configurable (`config.py:109-110` reads `llm.model`; live config `allowed_models: ["claude-haiku-4-5"]`); on `PluginLlmTrustError` exactly one no-override retry then fail open (`appraisal.py:239-278`); R3 annotation in REQUIREMENTS.md covers the live-unproducible fallback row | ✓ |
| APPR-07 | Kill switch checked FIRST in `pre_llm_call` (`__init__.py:91-92` → `skipped:disabled`, return None); live zero-call proof in telemetry | ✓ |
| APPR-08 | Throttle gates `should_skip` (`appraisal.py:483` — empty/social_close/duplicate) wired at `__init__.py:99-101` with `skipped:<reason>` telemetry; live social_close row + unit duplicate coverage | ✓ |
| OBS-01 | `store.py`: SCHEMA_VERSION=2 :32, telemetry table :75, 2000-row cap :40, `record_telemetry` :394 (never raises, error truncated), `telemetry_summary` :447 with `failure_count`/`last_error`/`p50_wall_ms`; live readout in VALIDATION + re-confirmed by direct query | ✓ |

## Plan Must-Haves

| Plan | Must-Have | Status |
|------|-----------|--------|
| 02-01 | appraisal.py exports run_appraisal/parse_signals/build_context/should_skip; executor-enforced deadline; zero retries beyond trust fallback | ✓ (appraisal.py:143/226/278/365/483) |
| 02-01 | render.py render_block: sentinel, ≤2000 chars, sanitized, None on empty | ✓ (render.py:19/105/113/160) |
| 02-01 | store.py SCHEMA_VERSION==2, telemetry table + 2000 cap, record_telemetry/telemetry_summary never raise | ✓ (store.py:32/40/75/394/447) |
| 02-01 | __init__.py: kill switch first, skipped:<reason> telemetry, _fail_open records llm_error, returns {"context": block} or None | ✓ (__init__.py:52/91-92/101/143) |
| 02-01 | Full suite green via hermes venv python | ✓* (49 passed; pytest staged via PYTHONPATH — see Environment Note) |
| 02-01 | Dry-run demo prints complete sanitized block through real hook path | ✓ (observed) |
| 02-01 | Landmine greps clean (no MemoryProvider, no raw SDK imports, no literal /Users/ paths) | ✓ (both greps empty) |
| 02-02 | 02-VALIDATION.md with all ten sections, evidence or pending-network | ✓ (all sections filled; zero pending-network) |
| 02-02 | contradictions.json ≥8 cases incl. ≥2 controls, parses | ✓ (9 cases, 3 controls, parses) |
| 02-02 | live_smoke.py + live_contradiction_fixtures.py exist, run under hermes venv | ✓ (exist; run evidence in VALIDATION — not re-run to avoid fresh live API calls) |
| 02-02 | config.yaml anansi block present; guardrails anansi block byte-identical to backup | ✓ (config.yaml:605-613; diff vs bak-20260610T092028 empty, re-verified 2026-06-10 5:28pm) |
| 02-02 | Every Phase-2 criterion evidenced or pending-network | ✓ (all evidenced) |

## Integration Checks

| Link | Check | Status |
|------|-------|--------|
| Live deploy symlink | `~/.hermes/plugins/anansi` → `/Volumes/Asylum/repos/hermes-anansi-plugin/anansi` | ✓ |
| Live state DB | schema_version = 2; `state.db.quarantined-20260610T132813Z` present (v1 quarantine as designed) | ✓ |
| Host facade | `agent.plugin_llm` imports under the hermes venv (no test skips); `PluginLlmTrustError` lazily imported `appraisal.py:239` | ✓ |
| Manifest | `plugin.yaml`: `kind: standalone`, `provides_hooks`, `pip_dependencies: []` | ✓ |
| Guardrails plugin | `plugins.entries.anansi` block byte-identical to pre-edit backup; `/Users/manisaintvictor/.hermes/plugins/anansi` untouched | ✓ |

## Summary

**Score:** 12/12 must-haves verified; 5/5 success criteria pass (criterion 3b under the Dr. Mani-accepted R3 annotation); 9/9 requirements (APPR-01..08, OBS-01) traceable to code.

All automated checks passed. Phase goal achieved: eligible turns get a grounded, capped, sanitized
appraisal block within the revised budget (live p50 5.5–5.7s ≤ 6s target, 8.0s deadline binding and
failing open).

### Non-blocking observations (for Phase 3 / orchestrator awareness)

1. **pytest missing from the hermes venv** as of verification time — the documented test command no
   longer works as written. Either reinstall pytest in the venv or adopt the staged-PYTHONPATH idiom
   in Phase-3 plans.
2. **`config.py` in-code default `deadline_seconds=2.5`** (config.py:13) predates the R1 revision
   (SAFE-01 now specifies default 8.0s). Live behavior is correct because `~/.hermes/config.yaml`
   sets 8.0 explicitly; aligning the code default is SAFE-01/Phase-3 scope, not a Phase-2 gap.
3. **p50 sample is small** (3 live `ok` rows: 5501/5715/6460ms). All three are ≤6.5s and the median
   ≤6s; Phase-3 telemetry will grow the sample.
