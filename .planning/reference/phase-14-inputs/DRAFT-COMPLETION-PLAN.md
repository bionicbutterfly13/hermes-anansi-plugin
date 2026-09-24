# Anansi — Completion & Testing Plan (to verified-complete)

**Date:** 2026-07-10 · **Author:** pair-programming session (Fable 5) · **Status:** Draft for Dr. Mani's review
**Scope:** everything between today's state and a *fully implemented, fully validated* hermes-anansi — specs 001–007 plus the cross-cutting verification debt no spec currently owns.
**Governed by:** `.specify/memory/constitution.md` (Principles I–VII). Every phase below goes through the Spec Kit flow (`/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement`) with a Constitution Check; nothing here bypasses it.

---

## 1. Definition of done ("fully implemented")

Anansi is verified-complete when:

1. Every spec 001–007 is either **DONE with recorded evidence** or **explicitly closed as deferred-by-decision** (a dated note naming who decided and why — e.g. D5 upstream no-op, L2 host-defect gate).
2. `./scripts/test.sh` is green, and the three invariant suites (fail-open matrix, anti-creep, never-omit) have been **extended to every new surface** with zero weakened assertions.
3. All live lanes have a recorded outcome: `live_smoke.py` PASS, `live_drive_smoke.py` PASS (closes G1/T029), live trust-fallback outcome recorded or accepted-deferred with reason (007-US3).
4. A performance evidence record exists showing p50 ≤ 6s / deadline 8.0s holds with all layers enabled (constitution I; currently no spec owns this — see §4 Phase 2).
5. `07-SECURITY.md` (drive-layer STRIDE) exists with each mitigation traced to code/tests (007-US1).
6. Each increment has a CHANGELOG entry with Features / Fixes / **Learnings**.

The 16 anti-features in `specs/BACKLOG.md` stay unbuilt. A plan that schedules one is wrong by definition.

## 2. Current verified state (evidence-based, 2026-07-10)

| Item | State | Evidence |
|------|-------|----------|
| Spec 001 (G1–G8) | 33/34 tasks done; only T029 (live drive run) open, env-gated | `specs/001-close-known-gaps/tasks.md:119`; code verified in `store.py`, `config.py`, `render.py`, `__init__.py` |
| Full suite | **183/183 green**, 20.7s (run 2026-07-10) | `./scripts/test.sh` |
| Flake watch | `test_appraisal.py::test_ok_path_parses_signals_and_records_usage` failed once in 3 runs on 2026-07-10 | timing-sensitive (usage recording); root-cause if it recurs — do NOT weaken the assertion |
| PR #2 | OPEN (gap closure + Spec Kit migration, 7 commits ahead of main) | `gh pr list` |
| Specs 002–007 | All spec.md-only, not started | per-spec directory listing |
| Live proof | `live_drive_smoke.py` has **never recorded a PASS**; no canonical test touches a real model | `quickstart.md` INCONCLUSIVE record |
| Upstream parity | UNVERIFIED post-withdrawal | `specs/006.../spec.md:41` |

## 3. Sequencing

**Recommended order** (keeps the agreed macro-order *worldview → episode/user-dopamine → reconsolidation+heartbeat → lanes/tuning* from `BACKLOG.md:14-19`, and fixes four dependency inversions found in cross-review):

```
Phase 0  Merge & baseline lock                      (S, now)
Phase 1  Spec 007 pulled forward: STRIDE + harnesses (S)
Phase 2  Cross-cutting test infrastructure           (S–M, no spec owns it today)
Phase 3  Spec 002: worldview → episode → dopamine    (L, needs /speckit-clarify first)
Phase 4  Spec 003: heartbeat + reconsolidation       (L, governance-gated)
         + spec 006 FR-004/FR-005 pulled in as pre-work
Phase 5  Spec 005: outbox → audit → config panel     (L, outbox lands BEFORE 004)
Phase 6  Spec 004: interruption lanes                (L, amendment-gated)
Phase 7  Spec 006 remainder: parity, D3/D6, D5 no-op (M, ordering now explicit)
```

**The four sequencing fixes** (each was implicit or inverted in `BACKLOG.md`):

1. **007 before 002** — the STRIDE register is cheapest before three new layers land on the drive surfaces it audits; a finding after 002 costs a rework cycle. 007 is S-sized and unblocked (only its two live runs stay env-gated).
2. **005-US3 (passive outbox) before 004** — 004's EC-1 mandates degradation to the outbox when a channel is unavailable; landing 004 first makes its own edge case unbuildable.
3. **006 FR-004 (WAL-on-netmount guard) + FR-005 (aux-routing decision) before/with 003** — 003 explicitly defers its WAL edge case to 006-FR-004; both are unblocked S items, so "opportunistic" scheduling would silently violate the dependency.
4. **Merge 001 before starting 002** — 002's schema work (v5 → v6) builds directly on the v5 store on this branch; starting 002 off an unmerged feature branch compounds the merge decision.

Alternatives considered: (A) strict BACKLOG order — rejected: leaves security/verification debt last and keeps the 004/005 inversion; (C) stop at 001+007 as a "verified v1" milestone — legitimate fallback if v2 is postponed, but not "fully implemented."

## 4. Phase detail

### Phase 0 — Merge & baseline lock (S)

- [ ] Record the 2026-07-10 full-suite evidence (183/183, 20.7s) in PR #2 / CHANGELOG, then **merge PR #2** (Dr. Mani's call — decision Q1, §7).
- [ ] Close spec 001 as "DONE, G1 lane-ready-gated" per its SC-001 escape hatch, or hold open for a live PASS (decision Q2).
- [ ] Log the appraisal-test flake as a watch item in CHANGELOG; if it fails twice more, root-cause under `systematic-debugging` before any new work.
- **Validation:** suite green on main post-merge; recorded evidence, not assertion.

### Phase 1 — Spec 007 pulled forward (S)

- [ ] `/speckit-plan` + `/speckit-tasks` for 007 (spec-only today).
- [ ] **FR-001:** write `07-SECURITY.md` — STRIDE over goal-text rendering, git/file ground-truth reads, config surface, first-person voice carve-out; each mitigation traced to a test or code path; confirm never-omit + SAFE-04 + anti-creep enforced-and-tested or flag gaps. Decide doc location at plan time (top-level `SECURITY.md` recommended; `.planning/` is read-only).
- [ ] **FR-003 harness gap:** build the missing live trust-fallback lane — a `scripts/live_trust_smoke.py` (or documented procedure) that forces a trust-gate denial and asserts a `trust_fallback` telemetry outcome, with the same honest 0/1/2 exit codes as the existing lanes. Unit-tested offline; live run stays env-gated.
- [ ] **Evidence ledger:** create one canonical place for live-run outcomes (recommend `specs/LIVE-VERIFICATION.md`): script, date, exit code, environment note. Fixes the "no owner/trigger for env-gated re-runs" gap — the ledger is re-checked **at the start of every subsequent phase** (that is the trigger; the phase's implementer is the owner).
- **Validation:** doc exists with traced mitigations; new lane exits 2 honestly with no provider; ledger committed with current INCONCLUSIVE entries.

### Phase 2 — Cross-cutting test infrastructure (S–M)

Work no spec currently owns; without it, later phases can silently regress. Constitution I makes overruns *invisible by design* (fail-open converts a deadline overrun into an empty injection), so:

- [ ] **Performance lane:** (a) offline — a pytest marker measuring plugin-side overhead of the full `pre_llm_call` path with fake LLMs against a fixed budget; (b) live — extend the smoke lanes to emit `wall_ms` into the evidence ledger; (c) telemetry — a documented query over the existing `telemetry_summary` p50 to check p50 ≤ 6s on real usage. Budget per new read path is set at each spec's plan phase (002 adds three).
- [ ] **Green-skip canary:** every hook-level test file `importorskip`s `agent.plugin_llm`; outside the hermes venv the suite green-skips most of its surface. Add a canary that **fails** (not skips) when the import is unavailable, or a collected-count floor (`≥183`) asserted in `test.sh`.
- [ ] **Empty-injection watch:** a documented telemetry query for the silent-degrade rate (empty injections + failure outcomes per N turns), so fail-open masking is observable in the field.
- [ ] **Named fail-open holes from 001:** add the two missing matrix tests — locked-DB *pressure read* during appraisal degrades to empty injection + telemetry, and `config_degraded` telemetry under a locked telemetry store itself fails open.
- **Validation:** perf test red when budget exceeded (prove by temporary slowdown, then revert); canary red outside the venv; queries documented in README or quickstart.

### Phase 3 — Spec 002: autobiographical user model (L)

The spec mandates re-scoping before implementation (`spec.md:14-15`). **`/speckit-clarify` must settle, in order of blast radius:**

1. **Five-vs-six layers:** SC-001 demands typed/capped/decaying tables for layers the spec never gives FRs (semantic, procedural, strategic). In or out? If out, fix SC-001; if in, write their FRs. (Decision Q3.)
2. **Dependency edges as a testability requirement:** 003's SC-002 ("100% of dependents re-evaluated") is only verifiable if 002's schema ships **enumerable** dependency/supersession/contradiction edges. This is a design-for-testability constraint on 002, not a 003 chore — retrofitting is far costlier.
3. Write paths (what mints beliefs/episodes: appraisal output, reflection, explicit user statements), the dopamine override mechanism and its observable, containment-toggle composition with the existing kill switch + whitelist, per-layer latency budget share, caps/decay values, and a falsifiable criterion for "a related turn" (US2).

Then `/speckit-plan` (Constitution Check) → `/speckit-tasks` → implement **one layer at a time** (Principle VII): worldview (US1/P1) → episode (US2) → user-dopamine (US3), each landing with:

- Schema v5 → v6 **additive** migration test (G2 precedent: upgrade in place, never erase).
- Extension of all three invariant suites: fail-open (locked/corrupt DB on each new read/write path — including the *read-during-appraisal* case 001 only covered for writes), anti-creep (directive-language corpus over each new note type; dopamine never agent-reward), never-omit (contradictions surfaced not resolved; empty model = APPR-05 suppression, byte-identical to today).
- Per-layer containment-toggle test (FR-008) and read-time-freshness test (FR-006: reads not gated behind reflection debounce).
- Perf lane re-measure with all three read paths on.
- **Validation:** all 9 acceptance scenarios as named tests; SC-002 zero directive findings; SC-003 whitelist containment + override honored; suite green; CHANGELOG with learnings.

### Phase 4 — Spec 003: heartbeat + reconsolidation (L, governance-gated)

- [ ] **Governance gate (before plan):** the scheduled heartbeat overlaps the excluded anti-feature "heartbeat-as-daemon-without-user-turn"; the Phase-6 override lives only in the read-only `.planning/` archive. Record the justified exception (or amend the constitution) with Dr. Mani's sign-off in the 003 plan's Complexity Tracking. (Decision Q4.)
- [ ] Pre-work pulled from 006: FR-004 WAL-on-netmount guard (decide runtime check vs documented caveat — scope differs materially), FR-005 aux-routing decision recorded.
- [ ] `/speckit-clarify` must define what the spec leaves unverifiable: the heartbeat mechanism (cron/host-hook/in-turn-degraded — constrained by zero-new-deps), what a "costed action" and the budget value are, the "withholds visibly" surface (recommend: telemetry row type, mirroring `config_degraded`), how degraded in-turn-only mode detects mechanism absence, and whether the heartbeat switch is the drive switch or a third switch. **Also settle 004's trigger grammar here** — triggers evaluate on the heartbeat, so the schema is 003's to carry even though 004 consumes it.
- Testing (defined at plan time, not retrofitted): watermark idempotence (double-fire no-op — reflection precedent exists), **crash-injection** for interrupted-propagation resume (kill mid-propagation, assert idempotent completion), SC-002 dependent-enumeration assertion over 002's edges, a **zero-emission harness** (heartbeat fires → assert no outbound surface of any kind; becomes the "no-outreach" release gate SC-004 names), offline e2e heartbeat demo test (dry-run precedent), budget-cap withhold-visibly test.
- **Validation:** all of the above green; kill switch renders heartbeat inert; suite green; perf lane unchanged on in-turn paths.

### Phase 5 — Spec 005: tuning & audit surfaces (L)

Order within the spec: **US3 passive outbox first** (004's fallback dependency), then US2 audit, then US1 panel.

- [ ] `/speckit-clarify`: quantify N sessions / "low pressure" / "adequately supported" for the under-response audit (SC-002's zero-false-alarm claim is untestable until then); outbox cap value + visible-eviction rendering; panel transport (see Q5) and concurrent hand-edit semantics.
- [ ] **US1 config panel lives outside the plugin boundary** (Principle V forbids a UI stack in-plugin): an external surface writing `plugins.entries.anansi`; the plugin-side test surface is config round-trip + `config_degraded` coercion on malformed writes + "panel absent → nothing breaks."
- **Validation:** outbox zero-outbound test joins the no-outreach gate; audit true-positive/zero-false-alarm fixtures; suite green.

### Phase 6 — Spec 004: interruption lanes (L, amendment-gated)

- [ ] **Hard gate:** Principle II has no outreach carve-out and `BACKLOG.md` lists outreach among the never-builds. 004 proceeds only after a constitution amendment or recorded justified exception with Dr. Mani's explicit sign-off (Decision Q6). Until then it is not schedulable backlog.
- [ ] L2 (US2) additionally needs a **defined verification procedure** for the desktop cold-respawn fix (external repo): who attests, how it's evidenced. Without it, L2 stays gated regardless of local readiness.
- [ ] Plan must define: trigger grammar (carried from Phase 4), "gentlest channel" enumeration + rate budget, the FR-005 interrupt-audit record schema (new table, schema bump, retention + inspection surface per Principle VI), and the SC-001 telemetry query that computes fire-attribution.
- **Validation:** OFF-by-default proven; agent-cannot-self-trigger test; kill-switch/whitelist/rate-limit gates; channel-unavailable → outbox fallback; deleted-goal trigger inert; audit record round-trip; no-outreach-when-disabled joins the release gates.

### Phase 7 — Spec 006 remainder (M)

- [ ] FR-002 upstream parity re-verify against a fresh upstream `main` checkout; record each result (manifest accepted, `ctx.llm` resolves or fallback, zero-deps processed, suite to host standards) in the evidence ledger — closing Phase 4 Criterion 2 *either way*.
- [ ] FR-003 D3/D6 depth: gated on affect telemetry existing — decide at 005 plan time which spec owns that telemetry; bind "never modulate output tone from affect" to a named `test_anticreep.py` regression test.
- [ ] FR-001 D5: stays a **documented, tested no-op** unless Dr. Mani signs off an upstream hook contribution (proprietary posture; PR #43906 precedent — default is no). The no-op itself gets a test (SC-001).
- **Validation:** parity findings recorded; D6 decay policy has a stated acceptance threshold before tuning starts.

## 5. Testing & validation architecture (the standing system)

Five lanes, each extended per phase — a feature is not done until all five have an answer:

| Lane | Mechanism | Gate |
|------|-----------|------|
| Offline contract suite | `./scripts/test.sh` (fake PluginLlm, zero network) | green, every task |
| Invariant release gates | fail-open matrix · anti-creep · never-omit · (from Phase 4) no-outreach | green, no weakened assertions, **extended to every new surface** |
| Offline e2e demos | dry-run demo · reflection demo · (Phase 4) heartbeat demo | render/behave with zero network |
| Live smoke lanes | `live_smoke` · `live_drive_smoke` · (Phase 1) trust-fallback · manual, env-gated, honest 0/1/2 exits | outcomes recorded in the evidence ledger; ledger re-checked at every phase start |
| Perf & field observability | offline overhead budget test · `wall_ms` in ledger · telemetry p50 + empty-injection queries | p50 ≤ 6s; budget red-line per new read path |

Rules that hold across all lanes: never weaken an assertion to pass; "could not test" must exit INCONCLUSIVE, never PASS; every significant fix records why it broke and what was learned.

## 6. Risk register (ranked)

1. **002 layer-scope ambiguity** — blocks the next increment and, transitively, 003's verifiability. Mitigation: Phase 3 clarify gate, edges-as-testability requirement.
2. **Perf invisibility** — fail-open masks overruns as empty injections; three new read paths + heartbeat could silently kill injection. Mitigation: Phase 2 perf lane before 002.
3. **Fail-open read-path holes** — locked-DB *pressure read* during appraisal and locked-telemetry `config_degraded` have no named tests. Mitigation: close in Phase 2 or with 002's matrix extension (cheap now, miserable from live symptoms).
4. **Live-proof drift** — every phase stacks behavior on a drive layer whose real-model behavior has never recorded a PASS. Mitigation: ledger + phase-start re-check ritual.
5. **Governance surprises** — 003 (timers override) and 004 (outreach exception) both need recorded sign-off; discovering that at implement time wastes a cycle. Mitigation: gates named in Phases 4/6; decisions queued now (§7).
6. **Flaky appraisal test** — one failure in three runs on 2026-07-10. Mitigation: watch item; two more failures → systematic-debugging, never assertion-weakening.

## 7. Decision queue for Dr. Mani

| # | Decision | Phase blocked | Recommendation |
|---|----------|---------------|----------------|
| Q1 | Merge PR #2 now with recorded 183-green evidence? | 0 | Merge |
| Q2 | Close 001 as "lane-ready, G1 honest-gated" or hold for live PASS? | 0 | Close gated; G1 closure moves to 007-US2 via the ledger |
| Q3 | 002 scope: worldview/episode/dopamine only, or all six layer types? | 3 | Three layers; re-word SC-001; park semantic/procedural/strategic as a follow-on spec |
| Q4 | Sign off the 003 heartbeat justified exception (v1 no-timers override)? | 4 | Record as justified exception in 003 plan, not a constitution amendment |
| Q5 | Config panel transport (external surface writing `plugins.entries.anansi`)? | 5 | External surface; plugin ships only the config contract |
| Q6 | 004 interruption lanes: amend constitution or record bounded exception — or drop the lanes? | 6 | Bounded, recorded exception; L2 stays gated on the host fix |
| Q7 | D5 upstream hook contribution? | 7 | No (proprietary posture); D5 stays a tested, documented no-op |

## 8. Exit checklist (verified-complete)

- [ ] PR #2 merged; main green with recorded evidence
- [ ] `SECURITY.md` (STRIDE) traced to tests/code
- [ ] Evidence ledger live; `live_smoke` PASS, `live_drive_smoke` PASS (G1/T029 closed), trust-fallback recorded or accepted-deferred
- [ ] Perf lane in place; p50 ≤ 6s evidence with all layers on
- [ ] Spec 002 layers shipped, one at a time, all five test lanes extended
- [ ] Spec 003 heartbeat + reconsolidation shipped under recorded exception; zero-emission gate green
- [ ] Spec 005 outbox → audit → panel shipped; outbox precedes 004
- [ ] Spec 004 shipped under recorded exception (or explicitly dropped by decision)
- [ ] Spec 006: parity recorded, D3/D6 done or deferred-by-decision, D5 no-op tested
- [ ] Every increment: CHANGELOG entry with learnings; no weakened assertion anywhere
