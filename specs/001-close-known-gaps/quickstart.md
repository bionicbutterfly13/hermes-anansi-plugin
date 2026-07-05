# Quickstart — Validate the Gap Closure

Canonical test gate (whole suite): `./scripts/test.sh` — runs the hermes venv python `-m pytest -q` over
`anansi/tests` (venv never modified).

Run a single slice's tests, e.g.: `./scripts/test.sh anansi/tests/test_drive_store.py -q`.

## Per-slice validation

| Gap | What to run | Expected |
|-----|-------------|----------|
| G2 persist pressure | `./scripts/test.sh anansi/tests/test_drive_store.py` | Goal round-trips `support_style`/`push_when_stalled`/`stall_threshold_days`; v4→v5 upgrade PRESERVES existing goal rows; locked-DB write still returns False |
| G3 drive_pressure | `./scripts/test.sh anansi/tests/test_drive_config.py anansi/tests/test_drive_velocity.py` | `quiet`/`standard`/`firm` produce distinguishable blocks on identical state; literal strings unchanged; `standard` == today |
| G7 config telemetry | `./scripts/test.sh anansi/tests/test_telemetry_store.py anansi/tests/test_drive_config.py` | Malformed key → one `config_degraded` row (non-failure), rejected value NOT quoted; valid config → zero rows |
| G4 flagged cap | `./scripts/test.sh anansi/tests/test_drive_neveromit.py` | >cap flagged goals → top-priority present + `[N flagged priorities withheld]` marker; existing all-survive test (≤cap) still green |
| G5 matching | `./scripts/test.sh anansi/tests/test_drive_velocity.py` | Substring false-positives dropped; legitimate goal↔signal matches still fire |
| G6 stalled 0 | `./scripts/test.sh anansi/tests/test_drive_velocity.py` | `stalled_days=0` renders fresh/active, ranks moving, no "stalled 0 days" clause |
| G8 rename | `./scripts/test.sh anansi/tests/test_reflection.py` | `test_primary_kill_switch_disables_reflection` passes; no other "master" token changed |

## Full-suite gate (all constitution invariants)

```
./scripts/test.sh
```
Must be green including `test_anticreep.py` (forbidden-substrings, import allowlist, single write-open,
label prefixes), `test_failopen_matrix.py`, and `test_drive_neveromit.py`. No assertion may be weakened
relative to the pre-change suite.

## G1 — Live Criterion-1 (environment-gated)

One command, no args:

```
$HERMES_HOME/hermes-agent/venv/bin/python scripts/live_drive_smoke.py
```

Requires: `HERMES_HOME` set, network egress to `api.anthropic.com:443`, host LLM creds configured.

Exit codes: `0` PASS (real turn surfaced the first-person `- drive want:` line), `1` FAIL (block rendered
but want missing, or a second-person directive leaked), `2` INCONCLUSIVE (network down or trust-gate/no
signals — an environment condition, not a code defect). Currently INCONCLUSIVE due to provider outage
(openrouter billing + nous auth); re-run when a provider is reachable to close Criterion 1.
