# Changelog

All notable changes to the Anansi Metacognition Plugin. Format: Features / Fixes / Learnings.

## 2026-07-05 — Anansi Completion: close known gaps (spec `001-close-known-gaps`, G1–G8)

Hardening pass that makes the Phase 7 Drive/Accountability increment verified-complete. Planned and
executed spec-driven with GitHub Spec Kit (`.specify/memory/constitution.md` + `specs/001-close-known-gaps/`).
Suite: 165 → 183 tests, all green; no existing assertion weakened; fail-open matrix, never-omit, and
anti-creep scans all still pass.

### Features

- **Per-goal pressure persists (G2).** `goals` schema v4→v5 adds `support_style`, `push_when_stalled`,
  `stall_threshold_days`; they round-trip the store instead of only working via injected test dicts.
- **`drive_pressure` is live (G3).** The global `quiet|standard|firm` setting now modulates the drive-note
  verbosity ceiling (salience/ordering/verbosity only, never wording). `standard` is byte-identical to prior
  output; the energy budget still caps further.
- **Config-degradation telemetry (G7, audit #5).** When a provided config value is coerced away (rejected or
  clamped), a legible, secret-safe `config_degraded` telemetry row is recorded (key + shape + applied
  default), once per session — a degraded config is now discoverable instead of silently swallowed. Classified
  as a non-failure.
- **Bounded flagged wants (G4).** New `drive_flagged_want_cap` (default 5, floor 1) bounds how many flagged
  `- drive want:` lines render; the highest-priority wants always render and any overflow is surfaced as a
  visible `[N flagged priorities withheld]` marker — never a silent drop.

### Fixes

- **`stalled_days == 0` no longer reads as stalled (G6).** A goal touched today (0 days idle) now renders
  fresh/moving with no "stalled 0 days" clause and no false push-zone bonus; the three consumers
  (`_drive_salience`, `_render_drive_note`, `_render_drive_want`) gate on `> 0`.
- **Precise goal↔signal matching (G5).** Replaced loose bidirectional substring matching (which mis-associated
  e.g. "ship"↔"relationship", "api"↔"therapist") with normalized whole-word token-subset matching at all three
  sites; legitimate whole-word associations still fire.
- **Terminology (G8).** Renamed the `test_master_kill_switch_disables_reflection` test to `…primary…` to avoid
  confusion with the git trunk rename (master→main). No runtime change.

### Docs / process

- **Live Criterion-1 lane (G1).** Documented the one-command live-smoke closure lane
  (`$HERMES_HOME/hermes-agent/venv/bin/python scripts/live_drive_smoke.py`, exit 0/1/2) in the feature
  quickstart; it remains environment-gated (provider outage) and reports an honest INCONCLUSIVE, never a false
  pass. Re-run when a provider is reachable to close the live criterion.

### Learnings

- **Anti-erasure beats the disposable-state doctrine (G2).** `store.py` normally quarantine-recreates on a
  schema bump — which would silently discard user-minted (possibly flagged) goals. That collides with the
  constitution's Never-Omit / Anti-Erasure principle, so v4→v5 uses an additive `ALTER TABLE ADD COLUMN`
  upgrade that preserves existing goals, falling through to quarantine only if the ALTER fails (still
  fail-open). This is the one place the disposable-state doctrine is deliberately relaxed, and only for a
  strictly additive step.
- **A silently-inert config key is a trust bug.** `drive_pressure` was accepted, documented, and coerced —
  but never read. The user believed they had tuned behavior that never changed. Wiring it (G3) plus the
  config-degradation telemetry (G7) close two variants of the same class: config that looks honored but is not.
- **Detecting "degraded" cleanly means separating rejection/clamping from normalization.** `"FIRM"`→`"firm"`
  and `"4000"`→`4000` are honored intent, not degradations; only unparseable or clamped values are flagged —
  and the rejected value is never quoted (shape only), so a mistyped credential can't leak into telemetry.
