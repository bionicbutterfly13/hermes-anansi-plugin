# Plan 03-01 Summary

**Completed:** 2026-06-10 (~6:15pm)

## What was built

The non-reflection SAFE half of Phase 3, suite 49 → 68 green. `scripts/test.sh` is the durable
repo-local test idiom (resolves the hermes venv python via `$HERMES_HOME`, stages pytest into
gitignored `.devtools/pytest` with `uv pip install --target` on first run — the venv is never
modified). SAFE-01 default honesty: `DEFAULT_DEADLINE_SECONDS` 2.5 → 8.0 in `config.py` AND the
second fallback at `appraisal.py:235` (live behavior unchanged — config.yaml already sets 8.0);
AGENTS.md/CLAUDE.md convention line updated in sync. `test_failopen_matrix.py` is THE consolidated
SAFE-02 matrix: docstring table maps every case to a test (referenced rows cite Phase 1–2 tests by
file::name, all grep-verified; 3 reflection rows are `added by 03-02` placeholders), with new
implementations for the parse_fail trio through the FULL registered hook path (malformed JSON,
mid-string truncation, `content: null`), the missing-config trio (entry absent / host loader raises /
malformed values coerced — against the REAL `get_cfg`), gateway session-rollover state reuse, and
four locked-DB rows (`BEGIN EXCLUSIVE` held by a second connection). `test_anticreep.py`: SAFE-03
corpus (14 rendered blocks via real `parse_signals`→`render_block`, incl. imperative bait + all 9
contradiction-fixture case texts) plus SAFE-04 static scans (forbidden-API substrings, AST
import-allowlist — pre-proves PKG-01, write-mode `open()` scan asserting the debug-dump append is
the plugin's only one). `conftest.py` exports `DIRECTIVE_PATTERNS` + `ALLOWED_LABEL_PREFIXES`
(includes `- trust note:`) + `assert_no_directive_language()` for 03-02 reuse.

## Key files
- scripts/test.sh + .gitignore (`.devtools/`) — canonical command: `./scripts/test.sh`
- anansi/{config,appraisal}.py — 8.0 default (R1)
- anansi/render.py — observational rephrasing of bare second-person directive payloads
- tests/{conftest,test_failopen_matrix,test_anticreep}.py

## Decisions made
- Directive checker quote-stripping: double-quoted spans stripped everywhere; single-quoted spans
  only on the memory-searches line (render single-quotes search phrases; stripping singles globally
  would mangle contractions like "it's" and mask payload between them).
- Render rephrasing mechanism: a field whose text carries `you should/must/need to/have to/shall`
  OUTSIDE double-quoted spans is wrapped whole in double quotes (inner doubles → singles) — bait
  survives only as reported material; already-quoted forms are not double-wrapped.
- Negative-control tests added for the checker itself (it must demonstrably catch a directive line
  and a non-allowlisted label).

## Deviations
- **WAL lock semantics vs the plan's locked-DB read row** (verified empirically before writing the
  test): under WAL — the production arrangement — `BEGIN EXCLUSIVE` equals IMMEDIATE and NEVER
  blocks readers, so `read_snapshot` returns a normal snapshot, not None. Implemented both truths:
  the telemetry-lock test asserts WAL reads still succeed under the held writer lock (the STATE-02
  design point), and the read-degradation row flips its tmp DB to rollback journal mode where
  EXCLUSIVE genuinely blocks readers → None, no raise. Also wrapped `store.sqlite3.connect` with
  `timeout=0.1` in that test (Python's default busy timeout is 5.0s) — same fast-lock idiom as the
  plan's `_DEFAULT_BUSY_TIMEOUT_MS=100` monkeypatch, extended to the read path.
- **render.py modified** (not in the plan's `files_modified` list, but explicitly sanctioned by
  task 3: "if any fixture produces a structurally directive line, that is a render.py bug — fix
  render.py (observational rephrasing), not the test"). The bait `you should migrate now` rendered
  as a structurally directive line under the old `_sanitize_text`; the quoting step above fixes it.
  Dry-run demo output byte-equivalent for all pre-existing fixtures (no second-person phrasing in
  them); 49 pre-existing tests untouched and green.

## Notes for downstream
- 03-02 extends: the 3 placeholder matrix rows in `test_failopen_matrix.py`'s docstring table, and
  the SAFE-03 corpus with reflection trust-hint lines (`- trust note:` already allowlisted).
- Locked-DB testing facts for 03-02's reflection-write row: WAL readers never block; write paths
  degrade via `monkeypatch.setattr(store, "_DEFAULT_BUSY_TIMEOUT_MS", 100)` /
  `apply_deltas(..., busy_timeout_ms=100)`; reader-blocking requires a rollback-journal tmp DB.
- `hermes_cli.config.load_config` is importable under the venv and monkeypatchable by dotted path —
  the missing-config idiom for any future config-failure test.
- Canonical test command (network only on first-ever staging): `./scripts/test.sh`; pass-through
  args work, e.g. `./scripts/test.sh anansi/tests/test_dryrun_demo.py -s`.
