# Roadmap — Hermes Anansi Metacognition Plugin (v1.0)

Created 2026-06-10 (autonomous ceremony). 4 coarse phases per SUMMARY.md's roadmap implications;
ordering follows the FEATURES.md dependency spine. Every v1 requirement maps to exactly one phase.

## Phase 1 — Skeleton + State (no LLM)

**Goal:** A loadable, inert, state-capable plugin — proven against the live install.

**Requirements:** PLUG-01, PLUG-02, PLUG-03, PLUG-04, STATE-01, STATE-02, STATE-03, STATE-04, STATE-05

**Success criteria:**
1. `hermes plugins enable anansi` loads the plugin; `HERMES_PLUGINS_DEBUG=1` shows hooks registered, kind=standalone
2. No-op hooks fire across a real turn without any effect on output or latency
3. State store round-trips all tables; corrupt-DB and locked-DB scenarios degrade silently (tests green)
4. Phase-0 validation items 1–4 from SUMMARY.md answered and recorded

## Phase 2 — Appraisal Path (the core)

**Goal:** Every eligible turn gets a grounded, capped, sanitized appraisal block — within budget.

**Requirements:** APPR-01, APPR-02, APPR-03, APPR-04, APPR-05, APPR-06, APPR-07, APPR-08, OBS-01

**Success criteria:**
1. A real `hermes` turn shows a `[anansi appraisal]` block with instincts/salience signals grounded in the actual message + state
2. Telemetry shows p50 ≤1.0s appraisal wall time, one LLM call per eligible turn, outcome distribution visible
3. Kill switch off → zero appraisal calls; trust-gate denial → automatic fallback to host model (verified)
4. Quiet/duplicate turns inject nothing (suppression + throttle verified)
5. Phase-0 items 5–7 (model quirks, contradiction fixture quality, telemetry) recorded

## Phase 3 — Fail-Open Hardening + Reflection

**Goal:** Nothing the plugin does can hurt a turn; state actually learns across sessions.

**Requirements:** SAFE-01, SAFE-02, SAFE-03, SAFE-04, REFL-01, REFL-02, REFL-03, REFL-04, REFL-05

**Success criteria:**
1. Full fail-open matrix green (timeout, trust, malformed JSON, truncation, content:null, DB states, missing config) — no case raises or blocks
2. Reflection runs only on session-change/N-turn debounce; double-firing produces identical state (idempotence test)
3. After a session discussing topic X with a contradiction, the next session's appraisal surfaces it (one-turn-lag loop demonstrated end-to-end)
4. No directive language detectable in any rendered block (pattern test green)

## Phase 4 — Packaging + Upstream PR Prep

**Goal:** Contributable artifact — in-tree layout, docs, upstream-main parity — gated on sign-off.

**Requirements:** PKG-01, PKG-02, PKG-03, PKG-04

**Success criteria:**
1. Plugin installs cleanly in both layouts (standalone `$HERMES_HOME/plugins/anansi` and in-tree `plugins/`)
2. `pip_dependencies: []` verified; test suite passes to host standards on upstream main
3. PR branch + PR_BODY.md ready; **submission blocked pending Dr. Mani sign-off**

## Coverage

| Phase | Requirements | Count |
|-------|--------------|-------|
| 1 | PLUG-01..04, STATE-01..05 | 9 |
| 2 | APPR-01..08, OBS-01 | 9 |
| 3 | SAFE-01..04, REFL-01..05 | 9 |
| 4 | PKG-01..04 | 4 |
| **Total** | **31 / 31 v1 requirements** | ✓ 100% |
