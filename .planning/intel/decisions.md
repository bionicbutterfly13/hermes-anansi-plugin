## Hermes Anansi Metacognition Plugin Constitution
- source: .specify/memory/constitution.md:1-117
- status: proposed
- decision:
````text
DATA_A1C3E5G7_START
<!--
Sync Impact Report
Version change: (template) → 1.0.0
Ratification: initial adoption 2026-07-05
Modified principles: n/a (first ratification)
Added sections:
  - Core Principles I–VII
  - Additional Constraints (Tech & Platform)
  - Development Workflow & Quality Gates
  - Governance
Removed sections: none
Templates requiring updates:
  ✅ .specify/templates/plan-template.md — Constitution Check section is generic (gates derived from this file); no hardcoded principle drift
  ✅ .specify/templates/spec-template.md — no constitution-specific slots to change
  ✅ .specify/templates/tasks-template.md — no principle-driven task types to add
Follow-up TODOs: none
-->

# Hermes Anansi Metacognition Plugin Constitution

The Anansi plugin injects a grounded metacognitive appraisal before each Hermes turn. It is a
proprietary hermes-agent 0.16.0 plugin. These principles govern every change. Where a principle is
marked NON-NEGOTIABLE, no code change, test edit, or convenience may weaken it.

## Core Principles

### I. Fail-Open Is Law (NON-NEGOTIABLE)

No code path in any hook MUST raise or block a turn. Appraisal work runs under an executor-bounded
deadline (default 8.0s, p50 target <=6s). Every failure MUST degrade to an empty injection plus a
telemetry row — never a raised exception and never a blocked or delayed response. Locked-DB,
corrupt-DB, timeout, malformed JSON, truncated output, `content: null`, and missing config are all
handled failure modes that MUST degrade silently. Rationale: the plugin sits on the critical path of
every turn; a metacognition layer that can break the turn is worse than no layer.

### II. No Autonomy — Observational Only (NON-NEGOTIABLE)

Output is observational noun-fields only. The plugin MUST NOT emit directives, execute tools, write
to any memory provider, or gate turns. Second-person imperatives MUST be neutralized or quoted as
reported material; only a first-person owned-want voice is permitted (the SAFE-04 carve-out). The
agent MUST NOT mint goals — it MAY surface inert candidate goals that do nothing until the user
confirms. Rationale: the plugin informs the model's self-appraisal; it never steers the user or the
agent's actions.

### III. Never-Omit & Anti-Erasure (NON-NEGOTIABLE)

User-flagged priorities MUST never be silently dropped from surfaced guidance. A flagged want is
exempt from the top-N slice, the token-cap line-drop, AND the energy budget, and the guarantee MUST
read PERSISTED state — not model output — so a flagged goal surfaces even when the model omits it.
Stalled user-authorized push zones MUST NOT be quietly downranked; repeated low-pressure handling of
such a goal MUST surface a visible under-support flag. Rationale: silent omission is the top
anti-value of this project — betrayal by erasure is the failure we build against.

### IV. Single SQLite Surface, Ground-Truth at Read Time

All state MUST round-trip through one `store.py` SQLite surface (WAL). Per-goal momentum MUST be
derived from ground truth — git reflog committer epochs plus file mtimes via stdlib read-only
`open()`, with NO subprocess and NO git library — at appraisal-READ time, not behind debounced
reflection. Rationale: a goal that stalled this turn must read as stalled this turn; a second state
surface or a deferred read would let truth drift from what the turn sees.

### V. Zero New Dependencies, Paths From Config

The plugin MUST add zero new pip dependencies — host `ctx.llm` surfaces plus stdlib (`sqlite3`,
`dataclasses`) only. All paths MUST come from config or environment (`$HERMES_HOME`), never
hardcoded literals. Config access MUST coerce defensively; `get_cfg` MUST never raise. Rationale:
the smallest dependency and path surface is the most portable and the least breakable on any install.

### VI. Inspectable & Adjustable Drive

The drive layer's effect MUST always be auditable: neutral read, drive read, and drive-caused
salience change MUST render separately and stay visible. Drive MUST be contained and adjustable via a
drive kill switch (separate from the appraisal kill switch), a domain whitelist, a per-turn energy
budget, and pressure/support-style config. All drive paths MUST fail open, and the drive-off path
MUST be byte-for-byte identical to a no-goals run. Rationale: a drive that changes salience without
showing its work cannot be trusted or tuned.

### VII. Minimal Surgical Change, Verify Before Ship, Learnings First-Class

Every change MUST be one fix in one place, touching only what the change requires and matching
existing style. Verification means running the code and checking output against ground truth — "it
should work" is not verification. Every significant fix MUST record why it broke and what we learned.
Rationale: multi-variable changes obscure cause; unverified claims ship bugs; uncaptured lessons are
paid for twice.

## Additional Constraints (Tech & Platform)

- **Language / runtime:** Python 3.11 (the hermes-agent venv). Tests run via `./scripts/test.sh`
  against that venv, which MUST never be modified.
- **Framework:** hermes-agent 0.16.0 hook-based plugin API — `pre_llm_call`, `on_session_end`,
  `on_session_start`. `kind: standalone` MUST be explicit; all hooks MUST accept `**kwargs`;
  `__init__.py` MUST never reference MemoryProvider strings (manifest string-scan landmine).
- **State:** stdlib `sqlite3` in WAL mode; the single `store.py` surface (Principle IV).
- **Voice:** agent-facing notes, prompts, and handoffs address the user as **Dr. Mani**.

## Development Workflow & Quality Gates

- Spec-driven flow: constitution → `speckit-specify` → `speckit-plan` → `speckit-tasks` →
  `speckit-implement`, with `speckit-clarify` / `speckit-analyze` / `speckit-checklist` as
  de-risking gates.
- Every plan MUST pass a Constitution Check: any conflict with Principles I–VII MUST be resolved or
  explicitly justified in the plan's Complexity Tracking before implementation.
- The full fail-open matrix and the never-omit tests are release gates; a change that would weaken
  either MUST NOT ship.
- Changes are verified by running the affected flow, not by re-reading the diff.

## Governance

This constitution supersedes other working practices for this repository. Amendments require Dr.
Mani's explicit sign-off and a recorded rationale. The never-omit (Principle III) and fail-open
(Principle I) invariants MUST NOT be weakened, narrowed, or bypassed to make a check pass. Versioning
follows semantic rules: MAJOR for backward-incompatible principle removals or redefinitions, MINOR
for a new principle or materially expanded section, PATCH for clarifications. All reviews and plans
MUST verify compliance with the principles above; unjustified complexity is grounds to reject a
change.

**Version**: 1.0.0 | **Ratified**: 2026-07-05 | **Last Amended**: 2026-07-05
DATA_A1C3E5G7_END
````
- scope: Anansi plugin; Hermes hooks; appraisal; user-flagged priorities; SQLite state; drive controls; configuration; release gates; governance. Taxonomy status is proposed because classification locked=false; binding authority is stated by the source constitution and task instruction.
