# Anansi Live Verification Evidence Ledger

**Governed by:** `.specify/memory/constitution.md` (Principle VII: Evidence over assertion).
**Purpose:** Canonical record of live harness runs executed against external model providers and host platforms.

---

## Exit Code Legend

- **`0 (PASS)`**: Real appraisal turn completed successfully, returned valid signals, and verified expected rendering behavior (e.g. first-person want line surfaced).
- **`1 (FAIL)`**: Appraisal completed but failed required assertions (e.g. missing drive want line or directive language leaked).
- **`2 (INCONCLUSIVE)`**: Environment-gated outcome (e.g. network down, model provider credentials missing, provider billing outage, or model response timeout). Not a plugin code defect.

---

## Log of Live Runs

| Date (UTC) | Script | Exit Code | Outcome / Result | Host / Model / Environment Notes |
|---|---|---|---|---|
| 2026-07-22 | `scripts/live_drive_smoke.py` | `2 (INCONCLUSIVE)` | `outcome=timeout, error=deadline 8.0s exceeded` | OpenRouter billing / Nous auth unavailable in local environment. Harness executed cleanly and degraded fail-open. |

---

## Verification Ritual

1. **Before any major release or spec increment**, re-run available live smoke harnesses:
   ```bash
   $HERMES_HOME/hermes-agent/venv/bin/python scripts/live_drive_smoke.py
   $HERMES_HOME/hermes-agent/venv/bin/python scripts/live_trust_smoke.py
   ```
2. Record date, exit code, and environment details in this ledger.
3. Offline contract test suite (`./scripts/test.sh`) MUST remain 100% green at all times.
