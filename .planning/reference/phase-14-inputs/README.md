# Phase 14 inputs (DRAFT)

**Status: DRAFT.** These four files are inputs for Phase 14 (live-provider
verification), filed here by Phase 08.1 decision D-02. They are not evidence,
not an executable verification lane and not an authorization for any live run.
Nothing in them establishes current `main` behavior.

They were untracked drafts in the main checkout. They were moved here on
2026-09-24 by plan 08.1-01 so their bytes are tracked; the `DRAFT-` prefix and
this README mark their status.

## Provenance

| Tracked copy | Source path (untracked; deleted after the move is verified) | Original SHA-256 | Copy |
|---|---|---|---|
| `DRAFT-07-SECURITY.md` | `docs/07-SECURITY.md` | `56acc696306e8c070bf503ed88319e519530f6e4b4945239719acee553eb92fb` | byte-identical |
| `DRAFT-COMPLETION-PLAN.md` | `specs/COMPLETION-PLAN.md` | `0bc04ae777addac3e7ee569810c457385a3f5fad5378ed5103bb82c41d996ef1` | byte-identical |
| `DRAFT-LIVE-VERIFICATION.md` | `specs/LIVE-VERIFICATION.md` | `4b892252f6ac1996523b7938ee12f318a39273c3f4295398f6983a84f48d3a32` | one line removed |
| `DRAFT-live_trust_smoke.py` | `scripts/live_trust_smoke.py` | `dac4eb926a4a76ad625e1cab0ccce3decd3420188a7565033b6bf44c10fa4fc3` | byte-identical |

## The one change

`DRAFT-LIVE-VERIFICATION.md` differs from its source by exactly one deleted
line: the "Log of Live Runs" row dated 2026-07-22 for
`scripts/live_trust_smoke.py`. No live run produced that result (grill log
2026-09-23), so it is not carried into a tracked file. Everything else in that
file is unchanged, including the other 2026-07-22 row for
`scripts/live_drive_smoke.py`; no independent record of that run was found
either, so treat it as an unverified claim, not evidence.

## Known limits

- `DRAFT-live_trust_smoke.py` is not a supported proof lane. It cannot force a
  trust denial while the plugin's default model is `None`, and its outcome
  vocabulary does not match the plugin's telemetry outcomes (grill log
  2026-09-23).
- `DRAFT-07-SECURITY.md` carries stale code citations (grill log 2026-09-23).
- Phase 14 must re-derive any claim here against the code and a real run
  before relying on it.
