# Requirements — Hermes Anansi Metacognition Plugin

**GSD migration, 2026-09-10:** the checked v1 ledger records historical implementation evidence, not fresh runtime verification. Phase 6 explicitly superseded the blanket heartbeat/user-dopamine exclusion for bounded future work. Constitution engineering invariants remain binding. Current imported work is under GSD Intake Requirements below; none is marked complete by this migration. Engineering references and extracted acceptance contracts are retained under `.planning/`, with retired workflow commands and paths normalized to GSD.

v1 selection made 2026-06-10 during the autonomous ceremony (self-answered under Dr. Mani's
mandate, following SUMMARY.md's recommended posture: table-stakes spine T1–T10 + near-free
differentiators D4/D7 + shallow D1/D2; defer D3/D5/D6 depth until telemetry validates signal
quality). Feature IDs (T*/D*) reference `.planning/research/FEATURES.md`.

## v1 Requirements

### PLUG — Plugin integration

- [x] **PLUG-01** Plugin loads via hermes-agent's standard mechanism: `plugin.yaml` with explicit `kind: standalone` and `provides_hooks`, `register(ctx)` with zero import-time side effects, installable at `$HERMES_HOME/plugins/anansi` (maps: skeleton; SUMMARY Key Decision 6a)
- [x] **PLUG-02** Every hook accepts `**kwargs` and tolerates unknown/missing kwargs (dispatcher injects extras; strict signatures TypeError every call)
- [x] **PLUG-03** The strings `MemoryProvider`/`register_memory_provider` never appear in `__init__.py` (manifest string-scan silently coerces plugin kind)
- [x] **PLUG-04** `pre_llm_call` returns `{"context": block}` or `None` — injection into user message only; system prompt never touched (host invariant)

### STATE — Local appraisal state (T8)

- [x] **STATE-01** SQLite store under `$HERMES_HOME` (path from config/env, never literal) with schema: affect_summary, concerns, contradictions, trust_scores, turn_log, schema_version
- [x] **STATE-02** WAL mode, synchronous=NORMAL, busy_timeout=5000; hot-path reads via read-only URI snapshot; writes confined to reflection pass
- [x] **STATE-03** Corrupt/locked/absent DB → quarantine-and-recreate (or skip), never a raised exception into the turn
- [x] **STATE-04** All state tables have caps + decay/pruning (anti: unbounded growth/hidden profiling); state stays local (privacy constraint)
- [x] **STATE-05** State round-trip covered by tests (write → reload → identical signals)

### APPR — Appraisal pre-phase (T1–T7, D4, D7)

- [x] **APPR-01** `pre_llm_call` runs ONE JSON-mode appraisal call via `ctx.llm.complete_structured` over (user_message + raw conversation_history + SQLite state) — NOT current-turn memory injection (amended input contract, one-turn lag) (T1)
- [x] **APPR-02** Observation-only prompt written fresh (not ported verbatim from Anansi `subconscious.md`); schema has noun fields only — instincts (typed vocabulary approach/avoid/caution/curiosity/protect with 0–1 intensity + reason — D7), salient observations, contradiction flags, confidence per signal, suggested memory searches (advisory text only — D4), gut reaction (≤200 chars)
- [x] **APPR-03** Per-signal confidence threshold (default 0.6); signals below threshold dropped (T5)
- [x] **APPR-04** Compact rendered block ≤500 tokens, top-3 per category, sentinel prefix (`[anansi appraisal]`), sanitized through icarus-style `_validate_safe_content` pipeline (T2)
- [x] **APPR-05** Empty-signal suppression: nothing salient → inject nothing (T4)
- [x] **APPR-06** Appraisal model separately configurable (cheap tier); on `PluginLlmTrustError` retry once with host's active model, then fail open (T6; SUMMARY Key Decision 3) — *annotation 2026-06-10 (R3): mechanism unit-proven; unproducible live on this install (host fallback ~37s exceeds the deadline clamp, degrades to the designed fail-open timeout); correct for installs with faster host models*
- [x] **APPR-07** Config kill switch disables the pre-phase entirely (T7)
- [x] **APPR-08** Throttle gates: skip appraisal on social closers / near-duplicate turns (icarus precedent)

### SAFE — Fail-open + anti-creep (T3)

- [x] **SAFE-01** Configurable executor-bounded wall-clock deadline on the appraisal call, default 8.0s (per-call socket timeouts don't bound wall time); p50 target ≤6s; zero retries beyond the trust-gate fallback — *revised 2026-06-10 (R1): Dr. Mani accepted ~5s p50 / max quality; live haiku appraisal is generation-bound at 4.4–7.3s, so the original 2.5–3.0s spec times out 100%*
- [x] **SAFE-02** Fail-open test matrix: LLM timeout, trust rejection, malformed JSON, truncation, `content: null`, locked/corrupt/absent DB, missing config — every case asserts no-raise + empty injection + normal turn
- [x] **SAFE-03** Unit test asserts no imperative/directive language patterns in any rendered block (anti: hidden second policy layer)
- [x] **SAFE-04** Plugin never executes tools/searches, never writes to the memory provider, never gates/delays a turn, never modifies its own prompt/config from reflection (locked anti-features)

### REFL — Session-end reflection (T9, shallow D1/D2)

- [x] **REFL-01** `on_session_end`: cheap bookkeeping (turn_log append) every firing; LLM reflection pass only on session-id change or N-turn debounce, applied in one idempotent WAL transaction (amended: hook fires per turn)
- [x] **REFL-02** Reflection extracts observations → bounded conservative deltas to affect summary, concerns, contradiction log, trust scores (the `apply_subconscious_observations` equivalent on SQLite) — *sharpened 2026-06-10 (R2): reflection is the carrier of appraisal context across the one-turn lag — the second half of the appraisal input contract. Inputs are user messages + assistant response text + state; NOT the injected memory block (ephemeral, never persisted to the transcript — verified conversation_loop.py:610-627)*
- [x] **REFL-03** Reflection inputs exclude sentinel-prefixed appraisal blocks (anti echo-chamber)
- [x] **REFL-04** Contradiction signals (semantic/narrative/relational/emotional) persisted and re-surfaced when relevant — shallow v1, validated against a fixture set before deepening (D1)
- [x] **REFL-05** Confidence/trust scores surfaced as advisory hints ("low confidence on X") — never a gate (D2)

### OBS — Observability (T10)

- [x] **OBS-01** Per-call telemetry to plugin's own SQLite: wall_ms, tokens, model, outcome (`ok|timeout|parse_fail|llm_error|skipped:<reason>`); failure counter + last-error surfaced (cf. silent-outage lesson, PR #43313)

### PKG — Packaging + PR prep

- [x] **PKG-01** Zero new pip dependencies (`pip_dependencies: []`); stdlib + host surfaces only
- [x] **PKG-02** Dual layout: standalone `$HERMES_HOME/plugins/anansi` + in-tree `plugins/` arrangement for the upstream PR; docs include the `plugins.entries.anansi.llm` config block
- [x] **PKG-03** Re-verify `ctx.llm` facade + manifest key (`provides_hooks` vs `hooks`) against upstream main before PR (local 0.16.0 fork carries 7 PRs of divergence)
- [x] **PKG-04** Upstream PR prepared but submitted ONLY after Dr. Mani sign-off (standing directive)

## v2 Requirements

- **D3** Dimensional affect summary depth (valence/arousal/intensity with decay-to-baseline) — ship minimal in v1 state schema, deepen after telemetry
- **D5** Salience filtering over Hindsight-injected context — requires solving current-turn memory visibility (config-gated direct-Hindsight-recall option, parked)
- **D6** Active-concern continuity depth (decay/expiry policy tuning) — start aggressive caps, loosen with evidence
- Unselected table stakes: none (all 10 in v1)

## Historical v1 Exclusions (supersession noted above)

| Item | Reason |
|------|--------|
| Heartbeat / background cycles, outreach, privilege ladder, continuation nudges, dopamine modulation | Locked exclusions — "metacognition without pushiness" |
| Plugin-executed tool calls/searches, directive injection language, turn gating, memory-provider writes, goal generation, self-modifying prompts, mood-driven output modulation, multi-call appraisal chains | Autonomy-creep refusals (FEATURES.md anti-feature table) |
| Import-time `sys.path` mutation | mnemosyne-incident standing "never" |
| Postgres/AGE/RabbitMQ/Ollama/UI | Original Anansi infra; this plugin is SQLite-only, Docker-free |

---
*Last updated: 2026-06-10 — PLUG-01..04 + STATE-01..05 delivered by Phase 1 (see 01-VERIFICATION.md); R1/R2/R3 revisions applied from MEMORY-STACK-ANALYSIS-2026-06-10.md §6 (Dr. Mani-accepted decisions)*

## GSD Intake Requirements

46 feature-qualified functional requirements from seven PRDs. Full acceptance,
edge-case and success-criterion text is preserved in [intel/requirements.md](intel/requirements.md),
including all 29 source SC IDs and 25 user stories. Read each feature's shared
acceptance contract before planning; a checkbox summary is not its full contract.

### 001: Close Known Gaps (Phase 8)

Source: `.planning/reference/001-close-known-gaps/spec.md`.

- [x] **REQ-001-close-known-gaps-fr-001**: Persist per-goal pressure metadata through the single SQLite store so it round-trips a read/write cycle.
- [x] **REQ-001-close-known-gaps-fr-002**: Migrate an existing goals table without data loss and without raising; goals lacking new fields read documented defaults.
- [x] **REQ-001-close-known-gaps-fr-003**: Read global drive_pressure and apply it to drive rendering, with invalid values coerced to the documented default.
- [x] **REQ-001-close-known-gaps-fr-004**: Emit a legible telemetry row whenever a config value is coerced away from the user-supplied value.
- [x] **REQ-001-close-known-gaps-fr-005**: Redact secret-like config values in degradation telemetry and never raise or block the turn if telemetry storage is unavailable.
- [x] **REQ-001-close-known-gaps-fr-006**: Bound rendered flagged wants with a proportionate cap while guaranteeing the highest-priority flagged wants render and visibly indicating withheld wants.
  Source variant superseded by Principle III: reconcile without withholding any persisted flagged priority. The cap wording is provenance, not implementation authority.
- [x] **REQ-001-close-known-gaps-fr-007**: Keep the never-omit invariant under the cap, verified against persisted state rather than model output.
  Source variant superseded by Principle III: reconcile without withholding any persisted flagged priority. The cap wording is provenance, not implementation authority.
- [x] **REQ-001-close-known-gaps-fr-008**: Avoid false-positive goal-to-signal associations caused by loose substring matching while preserving legitimate associations.
- [x] **REQ-001-close-known-gaps-fr-009**: Handle stalled_days=0 with a well-formed fresh/active read distinct from stalled rendering and an empty line.
- [x] **REQ-001-close-known-gaps-fr-010**: Provide a documented single-command live-smoke lane for first-person owned-want voice and report an honest environment-gated outcome when no provider is reachable.
- [x] **REQ-001-close-known-gaps-fr-011**: Rename master kill switch terminology in tests/comments to primary/main with no runtime behavior change.
- [x] **REQ-001-close-known-gaps-fr-012**: Hold all constitution principles; keep full fail-open matrix and never-omit tests green without weakening a principle.

### 002: Autobiographical User Model (Phase 9)

Source: `.planning/reference/002-autobiographical-user-model/spec.md`.

- [ ] **REQ-002-autobiographical-user-model-fr-001**: Persist a worldview layer as typed, capped, decaying data on the single SQLite surface with supersession and contradiction edges.
- [ ] **REQ-002-autobiographical-user-model-fr-002**: Persist an episode/autobiography layer with an autonoesis tag, typed, capped, and decaying on the single SQLite surface.
- [ ] **REQ-002-autobiographical-user-model-fr-003**: Model the user's habit/motivation dynamics within whitelisted domains, override-able and never as an agent-reward signal.
- [ ] **REQ-002-autobiographical-user-model-fr-004**: Surface all new layers only as observational appraisal notes with no directives or second-person imperatives.
- [ ] **REQ-002-autobiographical-user-model-fr-005**: Make any salience or ordering effect inspectable as a drive effect separate from the neutral read.
- [ ] **REQ-002-autobiographical-user-model-fr-006**: Read freshness-critical signals at appraisal-read time from ground truth rather than through reflection debounce.
- [ ] **REQ-002-autobiographical-user-model-fr-007**: Apply caps, decay, and pruning to all new tables; locked/corrupt databases silently degrade; use no path literals or new dependencies.
- [ ] **REQ-002-autobiographical-user-model-fr-008**: Give each layer a documented containment toggle so a user can turn it off.

### 003: Reconsolidation and Heartbeat (Phase 10)

Source: `.planning/reference/003-reconsolidation-and-heartbeat/spec.md`.

- [ ] **REQ-003-reconsolidation-and-heartbeat-fr-001**: Provide a scheduled heartbeat with execution mechanism chosen at plan phase and in-turn-only degradation if unavailable.
- [ ] **REQ-003-reconsolidation-and-heartbeat-fr-002**: Limit heartbeat to state preparation and next-real-turn surfacing; it must not interrupt, notify, or emit outbound communication.
- [ ] **REQ-003-reconsolidation-and-heartbeat-fr-003**: Make heartbeat debounced and idempotent so double firing is a no-op.
- [ ] **REQ-003-reconsolidation-and-heartbeat-fr-004**: Carry a per-heartbeat energy/attention budget with a hard cap per wakeup.
- [ ] **REQ-003-reconsolidation-and-heartbeat-fr-005**: Propagate belief flips across dependent memories, goals, episodes, and worldview edges on the single SQLite surface, idempotently on heartbeat.
- [ ] **REQ-003-reconsolidation-and-heartbeat-fr-006**: Surface reconsolidation output observationally in-turn, never as a directive or silent omission of a user-flagged priority.
- [ ] **REQ-003-reconsolidation-and-heartbeat-fr-007**: Provide a separate heartbeat/drive kill switch and retain fail-open, zero-dependency, and config-path constraints.

### 004: Interruption Lanes (Phase 11)

Source: `.planning/reference/004-interruption-lanes/spec.md`.

**Deferred under constitution precedence.** Interruption/outreach exceptions are captured source variants, not approved implementation. A compliant scope decision is required before execution planning.

- [ ] **REQ-004-interruption-lanes-fr-001**: Allow code-red only for objective user-defined conditions attached to user-flagged goals; the agent cannot self-declare urgency.
- [ ] **REQ-004-interruption-lanes-fr-002**: Keep code-red off by default and opt-in with a separate interrupt kill switch, domain whitelist, and hard rate limit on the gentlest channel.
- [ ] **REQ-004-interruption-lanes-fr-003**: Keep proactive-notify L2 off by default and opt-in, gated on a verified desktop cold-respawn fix.
- [ ] **REQ-004-interruption-lanes-fr-004**: Emit from neither lane unless preconditions hold; both fail open and do not violate no-outreach when disabled.
- [ ] **REQ-004-interruption-lanes-fr-005**: Make every interruption auditable by trigger, channel, and rate budget.

### 005: Tuning and Audit Surfaces (Phase 12)

Source: `.planning/reference/005-tuning-and-audit-surfaces/spec.md`.

- [ ] **REQ-005-tuning-and-audit-surfaces-fr-001**: Let a desktop config panel edit cadence, per-heartbeat budgets, and domain whitelists; changes take effect on the next config read and malformed input emits config_degraded telemetry.
- [ ] **REQ-005-tuning-and-audit-surfaces-fr-002**: Read persisted cross-session history on heartbeat and observationally surface a possible-under-support flag without false alarms when support is adequate.
- [ ] **REQ-005-tuning-and-audit-surfaces-fr-003**: Persist would-have-said items and surface them only in the next turn's appraisal, never outbound; cap and prune them.
- [ ] **REQ-005-tuning-and-audit-surfaces-fr-004**: Keep all three surfaces fail-open, zero-dependency, config-path based, and unable to self-modify prompts or thresholds.

### 006: Deferred v1 and Parity (Phase 13)

Source: `.planning/reference/006-deferred-v1-and-parity/spec.md`.

- [ ] **REQ-006-deferred-v1-and-parity-fr-001**: Implement D5 salience filtering only after an upstream post_memory_prefetch-style hook exists; until then preserve a documented no-op.
- [ ] **REQ-006-deferred-v1-and-parity-fr-002**: Re-verify and record upstream-main manifest, ctx.llm, pip_dependencies, and host-standard-suite parity.
- [ ] **REQ-006-deferred-v1-and-parity-fr-003**: Deepen dimensional affect and active-concern continuity without output-tone modulation or exceeding state caps.
- [ ] **REQ-006-deferred-v1-and-parity-fr-004**: Add a WAL-on-network-mount startup check or documented caveat.
- [ ] **REQ-006-deferred-v1-and-parity-fr-005**: Decide and record auxiliary-model routing through ctx.register_auxiliary_task or the bespoke config key.
- [ ] **REQ-006-deferred-v1-and-parity-fr-006**: Keep all work fail-open, zero-dependency, and config-path based.

### 007: Drive Security Verification (Phase 14)

Source: `.planning/reference/007-drive-security-verification/spec.md`.

- [ ] **REQ-007-drive-security-verification-fr-001**: Produce a drive-layer security document with a STRIDE register and mitigation trace for goal-text rendering, ground-truth reads, configuration, and first-person voice carve-out.
- [ ] **REQ-007-drive-security-verification-fr-002**: Run live Criterion-1 smoke against a provider and record PASS or honest INCONCLUSIVE reason; close spec-001 task T029 only on PASS.
- [ ] **REQ-007-drive-security-verification-fr-003**: Verify APPR-06 trust fallback live on a fast-enough host or record accepted deferral with reason; do not claim verification without evidence.
- [ ] **REQ-007-drive-security-verification-fr-004**: Make no code change for FR-002 or FR-003 unless a defect is found; the existing harnesses report honest exit codes.

## Intake Traceability

| Source feature | Functional requirements | GSD phase | State |
|---|---:|---:|---|
| 001 | 12 | 8 | Complete on Phase 8 branch; verified 2026-09-11 |
| 002 | 8 | 9 | Pending verification/planning |
| 003 | 7 | 10 | Pending verification/planning |
| 004 | 5 | 11 | Deferred, authority gate |
| 005 | 4 | 12 | Pending verification/planning |
| 006 | 6 | 13 | Pending verification/planning |
| 007 | 4 | 14 | Pending verification/planning |
