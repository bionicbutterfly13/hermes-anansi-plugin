---
phase: 7
phase_name: Drive / Accountability
extracted: 2026-06-14
plan_count: 4
summary_count: 4
missing_artifacts: ["07-SECURITY.md"]
---

# Phase 7: Drive / Accountability — Learnings

## Decisions

### D1: Drive state extends the single SQLite surface (schema v3→4, no migration code)
**What:** Goals + velocity live in new tables/fields in `store.py` (`SCHEMA_VERSION` 3→4); v3 DBs fail `_verify_structure` and are quarantine-recreated — no migration path.
**Why:** The locked single-sqlite-surface rule means drive inherits the proven WAL store + fail-open + locked-DB test coverage for free. Disposable-state doctrine makes a version bump cheaper and safer than migration code.
**Source:** 06-CONTEXT.md, 07-01-SUMMARY.md

### D2: Git ground truth via stdlib only, computed at appraisal-READ time
**What:** Velocity reads `.git/HEAD` + `.git/logs/HEAD` tail + `os.stat().st_mtime` with read-mode `open()` — never `subprocess`/`os.system`/a git library — and is computed at read time, not in `reflection.maybe_reflect`.
**Why:** The anti-creep forbidden-substring + import-allowlist scans brick the suite on any shell/SDK reach. Reflection is debounced (`reflect_every_n_turns` default 5), which would staleness stalled/moving signals up to 4 turns.
**Source:** 07-RESEARCH.md (Pitfalls #2, #3), 07-02-SUMMARY.md

### D3: SAFE-04 first-person carve-out is a LABEL allowance, not a regex relaxation
**What:** DRIVE-04 added a new `- drive want:` entry to `conftest.ALLOWED_LABEL_PREFIXES`; `_SECOND_PERSON_DIRECTIVE_RE` and `DIRECTIVE_PATTERNS` are byte-for-byte unchanged, and the negative controls were preserved + extended with a symmetric second-person control.
**Why:** Relaxing the directive regex would weaken the safety guarantee globally. A label allowance lets "I want X" through while "you should…" is still quoted/neutralized everywhere.
**Source:** 07-03-SUMMARY.md, 07-VERIFICATION.md

### D4: Never-omit beats the energy budget (DRIVE-05 > DRIVE-06)
**What:** Flagged-priority wants render into a protected prefix, exempt from the `[:3]` slice, the token cap (`floor=max(protected_count,2)`), AND the energy budget; the guarantee reads PERSISTED goals, so a flagged goal surfaces even when the model omits it.
**Why:** Silent omission of a user-stated priority is treated as betrayal (Dr. Mani's top anti-value). A hard guarantee must structurally outrank every soft control — even at the cost of a slightly-over-cap block.
**Source:** 06-CONTEXT.md, 07-03-SUMMARY.md, 07-04-SUMMARY.md

### D5: Implementation code on a per-phase branch; planning docs on the trunk
**What:** Phase 7 code landed on `phase-7-drive-accountability`, merged to trunk via PR #1; planning artifacts commit directly to the trunk. (Trunk renamed `master`→`main` this cycle.)
**Why:** Clean isolation keeps the trunk green and makes the increment a reviewable, abandonable unit. `/ship` requires a feature branch.
**Source:** session branching decision; [[git-private-remote-and-branching]]

## Lessons

### L1: Extending a well-factored plugin is rows/fields/labels, not new subsystems
**What happened:** The whole drive layer rode existing tested funnels — delta keys + snapshot fields (`store.py`), schema/parse/build_context (`appraisal.py`), render helpers, config coercers. No new module; the module-inventory test stayed green.
**Why it matters:** When the substrate is clean, big-sounding features are small surgical extensions. The expensive part is schema churn — so bump the version once and write all columns up front.
**Source:** 07-01..04-SUMMARY.md

### L2: Wave membership ≠ parallelizable — file overlap forces serialization
**What happened:** 07-02/03/04 were all "Wave 2" but every one edits `render.py`/`appraisal.py`/`__init__.py`, so they ran as a strict `depends_on` chain, one executor at a time.
**Why it matters:** Parallel execution must key on file-conflict, not just declared wave. Encode the serialization in `depends_on` or the executor will clobber.
**Source:** 07-02/03/04 frontmatter, execution record

### L3: The deterministic suite proves logic, not live behavior
**What happened:** 165 green fake-LLM tests + a passing verifier still left Criterion 1 (a real model turn surfacing a goal) unproven; it needed a live provider.
**Why it matters:** A live-verification lane (with CI-honest exit codes) is a distinct, necessary artifact — "all tests green" ≠ "works live."
**Source:** 07-UAT.md, 07-VERIFICATION.md

### L4: Distinguish forced contract-sync edits from test-weakening
**What happened:** Executors updated a few existing tests (schema-version assertion, `_DEFAULTS` dict, empty-parse-shape keys) — all forced directly by their own schema/default changes, none weakening behavior.
**Why it matters:** Changing a schema or default legitimately requires updating its literal-contract tests; that's not the same as relaxing a guarantee. Review should tell them apart.
**Source:** 07-01-SUMMARY.md (deviations)

## Patterns

### P1: Protected-prefix + floor-guarded cap
**When to use:** Any "must-never-drop X under a size cap" guarantee. Render the protected items first, record `protected_count`, and stop the truncation pop at `max(protected_count, 2)` — accept a slightly-over-cap result rather than violate the hard guarantee.
**Source:** anansi/render.py `render_block`

### P2: Read-time ground-truth signal (never behind a debounce)
**When to use:** Any freshness-sensitive signal that must be current per-turn. Compute it on the read path (mirror the existing decay idiom), never in the debounced write/reflection path.
**Source:** anansi/store.py velocity helpers

### P3: Stdlib-only git introspection
**When to use:** Cheap git recency without `subprocess`/SDK. Read `.git/HEAD` + the last `.git/logs/HEAD` line; take the committer epoch as `fields[-2]` (robust to variable-length committer names); stay branch-agnostic (resolve HEAD dynamically); fail-open to "unknown".
**Source:** anansi/store.py `_last_commit_epoch`

### P4: Fail-open helper idiom
**When to use:** Any helper on a fail-open hook path. Wrap the body in `try/except` returning a benign default (unfiltered input / empty list / safe sentinel); never raise into the hook.
**Source:** anansi/__init__.py + render.py drive helpers

### P5: CI-honest exit codes for live smoke (0 pass / 1 fail / 2 inconclusive)
**When to use:** Any network/credential-dependent verification script. "Could not test" (network down, no signals) must return a DISTINCT code from "passed" so automation can't misread it.
**Source:** scripts/live_drive_smoke.py, scripts/live_smoke.py (audit #4 fix)

## Surprises

### S1: The live UAT was blocked by provider billing/auth, not by code
**What was surprising:** The real appraisal returned `outcome=timeout` because the host providers were down — openrouter (payment/credit error) and nous (`run: hermes auth`), with cfg `model: null` routing to them.
**Impact:** Criterion 1 deferred as env-inconclusive; the drive live-harness now stands as the one-command re-run lane once a provider works.
**Source:** 07-UAT.md

### S2: A concurrent quick task moved the plan target mid-execution
**What was surprising:** quick-004 (adjustable-drive-controls) modified the Phase 6 design + all four 07 plans WHILE 07-01 was executing, growing the pressure-ladder / anti-complacency scope.
**Impact:** Paused to reconcile before Wave 2; the regenerated plans already covered the addendum, so execution continued. Takeaway: check the working tree before each wave — concurrent processes can shift the target.
**Source:** session execution record

### S3: Pressure columns were specified but not persisted
**What was surprising:** The 07-01 must-have named `support_style`/`push_when_stalled`/`stall_threshold_days` as `goals` DDL columns, but the shipped DDL omits them — behavior is proven via injected test dicts, persistence deferred.
**Impact:** Documented low-impact gap; per-goal pressure works in-render but doesn't round-trip the store yet.
**Source:** 07-VERIFICATION.md

---

*Extracted from Phase 7 artifacts on 2026-06-14*
