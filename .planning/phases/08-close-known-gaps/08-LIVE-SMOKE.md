# Phase 08 Live-Drive Smoke Record

**Date:** 2026-09-11
**Authorization:** No live-provider invocation authorized for ordinary Phase 08 execution.
**Status: UNRUN**

## Sole established command

```sh
$HERMES_HOME/hermes-agent/venv/bin/python scripts/live_drive_smoke.py
```

Run this command only after separate authorization. It is the only provider-backed
proof lane for the live-drive criterion.

## Exit semantics

- `0 = PASS`: a real appraisal returned signals and the first-person flagged
  drive want surfaced.
- `1 = FAIL`: a block rendered but the flagged drive want was missing, or the
  rendered block leaked the guarded second-person directive.
- `2 = INCONCLUSIVE`: network or provider/trust-gate availability prevented a
  real appraisal result. This is not a live pass and does not establish a
  drive-code defect.

Only separately authorized exit-0 evidence may change this status to PASS.
An offline test may verify the exit-2 boundary, but it must never synthesize a
provider-backed PASS.
