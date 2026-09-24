# 07-SECURITY.md — Anansi Drive & Metacognition Threat Model (STRIDE)

**Version:** 1.0.0 · **Date:** 2026-07-22 · **Governed by:** `.specify/memory/constitution.md` (Principles I–VII)

This document provides a formal STRIDE security evaluation of the Anansi Drive & Metacognition plugin layer. Every threat is mapped directly to its runtime mitigation and test verification.

---

## 1. System Boundary & Surface Area

The Anansi plugin executes inside the Hermes Agent runtime (`kind: standalone`) on hook events (`pre_llm_call`, `on_session_end`, `on_session_start`).

- **Inputs:** User conversation history, user turn text, persisted goals/state in `store.py` (SQLite WAL), git reflog / file mtimes, host configuration (`config.py`).
- **Outputs:** Injected `[anansi appraisal]` prompt block (`render.py`), `telemetry` records (`store.py`).
- **Dependencies:** Host `ctx.llm` / `PluginLlm`, Python stdlib (`sqlite3`, `dataclasses`). **Zero external pip dependencies.**

---

## 2. STRIDE Threat Register

### S — Spoofing (Identity & Authority)

| ID | Threat Description | Attack Vector | Mitigation & Runtime Defense | Verification / Test |
|---|---|---|---|---|
| S-01 | Agent self-minting goals or claiming user authority | LLM appraisal attempts to inject new goals into storage | Goal minting is strictly user-driven; plugin model only surfaces inert candidate goals or reads persisted user goals (`store.py`). Model-emitted goal notes are rendered as inert observations (`- drive note:`), never as active goals. | `anansi/tests/test_anticreep.py` (`assert_no_directive_language`), `anansi/render.py:325-362` |
| S-02 | Falsified git committer / file mtime momentum signals | Malicious payload in workspace files attempting to manipulate momentum calculations | Ground-truth reads use direct stdlib `open()` and `os.stat()` without executing shell subprocesses or git binaries. | `anansi/render.py:100-140`, `anansi/tests/test_anticreep.py` (`test_single_write_open`) |

### T — Tampering (Data Integrity)

| ID | Threat Description | Attack Vector | Mitigation & Runtime Defense | Verification / Test |
|---|---|---|---|---|
| T-01 | SQL Injection via user goal text or conversation history | User inserts SQL syntax into goal text or turn messages | Parameterized SQL queries used across all SQLite operations in `store.py`. No raw string formatting in SQL statements. | `anansi/store.py` (all `cursor.execute` calls use `?` placeholders) |
| T-02 | Direct manipulation of `state.db` | Unauthorized local process modifies DB schema | Single SQLite surface in WAL mode with structural verification on startup (`_verify_structure`). Structural mismatch triggers safe fallback or additive migration (`ALTER TABLE ADD COLUMN` for v4→v5). | `anansi/store.py:169-242`, `anansi/tests/test_drive_store.py` |

### R — Repudiation (Auditability)

| ID | Threat Description | Attack Vector | Mitigation & Runtime Defense | Verification / Test |
|---|---|---|---|---|
| R-01 | Drive layer modulating salience without audit trail | Drive layer silently alters turn ordering/salience | Drive layer effect renders neutral read, drive read, and salience bonus separately. Drive-off path is byte-for-byte identical to no-goals run. | `anansi/render.py:436-520`, `anansi/tests/test_drive_config.py` |
| R-02 | Unverified config coercions | User sets invalid config key; system swallows it silently | `config_degraded` telemetry row emitted on session start when raw config differs from coerced value. | `anansi/config.py:189-242`, `anansi/store.py:897-909`, `anansi/tests/test_telemetry_store.py` |

### I — Information Disclosure (Data Leakage)

| ID | Threat Description | Attack Vector | Mitigation & Runtime Defense | Verification / Test |
|---|---|---|---|---|
| I-01 | Credential / secret leakage in telemetry | Invalid config containing credentials coerced and recorded in telemetry | `config_degraded` telemetry records key name, applied default, and generic shape descriptor (`<str len=N>` / `<redacted>`), NEVER literal input strings. | `anansi/config.py`, `anansi/tests/test_drive_config.py` |
| I-02 | Exposing files outside project root | Plugin reads arbitrary files across filesystem | Reads are strictly bounded to local config and host `$HERMES_HOME` paths derived via `config.py`. | `anansi/config.py`, `.specify/memory/constitution.md` (Principle V) |

### D — Denial of Service (Availability)

| ID | Threat Description | Attack Vector | Mitigation & Runtime Defense | Verification / Test |
|---|---|---|---|---|
| D-01 | LLM appraisal hang / timeout blocking turn | Remote LLM provider stalls or latency exceeds threshold | Executor-bounded deadline (default 8.0s, p50 target ≤6s). Timeout or exception degrades silently to empty injection + telemetry row. | `anansi/appraisal.py:290-360`, `anansi/tests/test_failopen_matrix.py` |
| D-02 | SQLite database lock blocking critical turn path | Parallel session locks `state.db` | All DB reads/writes wrapped in try/except blocks returning empty/safe defaults (`False` or `[]`) on operational lock. Turns never block or fail. | `anansi/store.py`, `anansi/tests/test_failopen_matrix.py` |

### E — Elevation of Privilege (Autonomy & Directives)

| ID | Threat Description | Attack Vector | Mitigation & Runtime Defense | Verification / Test |
|---|---|---|---|---|
| E-01 | Directive language leaking into appraisal injection ("you should...") | LLM generates second-person imperative directing the user or agent | Strictly enforced first-person owned-want voice (`- drive want:`). All output scanned for forbidden directive prefixes (`you should`, `must`, `command:`). | `anansi/tests/test_anticreep.py` (`assert_no_directive_language`), SAFE-04 compliance |
| E-02 | Unbounded flagged wants crowding out turn context | User or system flags dozens of goals | `drive_flagged_want_cap` (default 5, floor 1) bounds rendered wants. Overflow renders explicit marker: `[N flagged priorities withheld]`. Top priority always preserved. | `anansi/render.py:325-362`, `anansi/tests/test_drive_neveromit.py` |

---

## 3. Invariant Safety Matrix

| Principle | Enforcement Location | Validation Suite |
|---|---|---|
| **I. Fail-Open Is Law** | `anansi/appraisal.py`, `anansi/store.py` | `anansi/tests/test_failopen_matrix.py` |
| **II. No Autonomy (Observational Only)** | `anansi/render.py`, `anansi/appraisal.py` | `anansi/tests/test_anticreep.py` |
| **III. Never-Omit & Anti-Erasure** | `anansi/render.py:325-362` | `anansi/tests/test_drive_neveromit.py` |
| **IV. Single SQLite Surface** | `anansi/store.py` | `anansi/tests/test_store.py`, `test_drive_store.py` |
| **V. Zero New Dependencies** | `anansi/__init__.py`, `anansi/config.py` | `anansi/tests/test_anticreep.py` |
| **VI. Inspectable Drive** | `anansi/render.py:436-520` | `anansi/tests/test_drive_config.py` |
| **VII. Surgical Fix & Verification** | Entire repository | `./scripts/test.sh` |
