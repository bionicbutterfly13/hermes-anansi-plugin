# Feature Specification: Drive Security + Live Verification Debt

**Feature Branch**: `007-drive-security-verification`

**Created**: 2026-07-05

**Status**: Backlog (a promised artifact never produced + live checks never run)

**Input**: Three verification debts recorded but not discharged: (1) the Phase-7 security doc `07-SECURITY.md`
was expected and never produced (`07-LEARNINGS.md` frontmatter `missing_artifacts: ["07-SECURITY.md"]`);
(2) the live Criterion-1 drive turn was never run (env-blocked); (3) the APPR-06 trust-gate fallback is
unverified live. These need a real provider and/or a security pass, not new features.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Produce the drive-layer security doc `07-SECURITY.md` (Priority: P1)

The drive layer (goals, pressure, first-person voice, ground-truth git/file reads) gets a STRIDE-style threat
register + mitigation check, matching the per-phase security discipline that every other phase followed.

**Why this priority**: A promised phase artifact is simply missing (`07-LEARNINGS.md:7`). The drive layer
added a new injection/behavior surface (goal text rendered, git/file reads) that was never formally
threat-modeled.

**Independent Test**: `07-SECURITY.md` exists with a STRIDE register covering the drive surfaces, each threat
classified with its mitigation traced to a test or code path.

**Acceptance Scenarios**:
1. **Given** the drive layer's inputs (user goal text, git reflog/file reads, config), **When** the threat
   register is built, **Then** each STRIDE category has entries with mitigations traced to code/tests.
2. **Given** the never-omit + SAFE-04 + anti-creep invariants, **When** the doc reviews them, **Then** it
   confirms each is enforced-and-tested (or flags a gap).

---

### User Story 2 — Run the live Criterion-1 drive turn (Priority: P1) — env-gated

Confirm, against a real model provider, that a live turn surfaces a user-minted goal in the first-person
owned-want voice — the one Phase-7 success criterion left INCONCLUSIVE because providers were down. (This is
task T029 of spec 001; recorded here as the live-verification home.)

**Why this priority**: "A real model turn surfaces a minted goal in the appraisal block" is UNVERIFIED
(`07-UAT.md:21,51`; `07-VERIFICATION.md:94-99`). The logic is unit-proven; only the live pass is missing.

**Independent Test**: With a reachable provider, `scripts/live_drive_smoke.py` returns exit 0 (PASS) with the
`- drive want:` line present and no `you should` leak.

**Acceptance Scenarios**:
1. **Given** a reachable provider (openrouter billing restored OR `hermes auth` for nous), **When**
   `$HERMES_HOME/hermes-agent/venv/bin/python scripts/live_drive_smoke.py` runs, **Then** it exits 0 and the
   first-person want line is present.
2. **Given** no provider, **When** it runs, **Then** it exits 2 (INCONCLUSIVE) honestly — never a false pass.

---

### User Story 3 — Verify APPR-06 trust-gate fallback live (Priority: P2)

Confirm the "trust-gate denial → single retry with the host's active model → then fail open" path on an
install where the host model is fast enough to actually complete within the deadline.

**Why this priority**: "Mechanically proven; unproducible live on this install (host fallback ~37s > clamp;
degrades to designed fail-open timeout)" (`MEMORY-STACK-ANALYSIS:116`; DECISIONS R3:39-41). Phase 2 Criterion
3 is UNVERIFIED live.

**Independent Test**: On a host whose active model completes an appraisal under the deadline, force a
trust-gate denial and confirm the single fallback retry produces a `trust_fallback` outcome (not a timeout).

**Acceptance Scenarios**:
1. **Given** a fast-enough host model and a trust-gate denial, **When** appraisal runs, **Then** telemetry
   records `trust_fallback` (the retry completed) — the mechanism produced live, not just unit-proven.
2. **Given** a slow host model, **When** the fallback exceeds the deadline, **Then** it degrades to a
   fail-open timeout (the documented accepted behavior) — recorded, not treated as a bug.

---

### Edge Cases
- No fast host model available anywhere → APPR-06 live check stays deferred with the accepted-won't-fix note,
  not a false failure.
- Security doc surfaces a real gap → it becomes its own spec/fix, not silently absorbed.

## Requirements *(mandatory)*
- **FR-001**: Produce `07-SECURITY.md` (or an equivalent `SECURITY.md` for the drive layer) with a STRIDE
  register + mitigation trace covering goal text rendering, ground-truth git/file reads, config, and the
  first-person voice carve-out.
- **FR-002**: Run the live Criterion-1 drive smoke against a real provider and record PASS (exit 0) or the
  honest INCONCLUSIVE reason; close spec-001 task T029 on PASS.
- **FR-003**: Verify APPR-06 trust-fallback live on a fast-enough host (or record it as accepted-deferred
  with the reason); never claim it verified without evidence.
- **FR-004**: No code change is required for FR-002/FR-003 unless a defect is found; the harnesses already
  exist and report honest exit codes.

## Success Criteria *(mandatory)*
- **SC-001**: `07-SECURITY.md` exists; every drive-surface threat has a classified mitigation traced to
  code/tests.
- **SC-002**: The live drive turn is run and its outcome (PASS / honest INCONCLUSIVE) is recorded; on PASS,
  Phase-7 Criterion 1 and spec-001 T029 are closed.
- **SC-003**: APPR-06 live behavior is either produced (`trust_fallback` observed) or recorded as
  accepted-deferred with the concrete reason — never asserted without evidence.

## Assumptions
- FR-002/FR-003 are blocked only on provider/host availability, not on code.
- Evidence-over-assertion (constitution VII): no live criterion is marked met without a recorded run.

## Out of Scope (here)
- New drive features. Any change to the accepted fail-open-on-slow-host behavior (that is by design).
