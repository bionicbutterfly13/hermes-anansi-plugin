---
title: Derive git ground truth with stdlib-only reads under a no-subprocess tripwire
date: 2026-06-14
category: best-practices
module: anansi/store.py
problem_type: best_practice
component: _last_commit_epoch
severity: medium
tags: [stdlib-only, git-reflog, no-subprocess, fail-open, zero-dependency, import-allowlist, ground-truth, read-path]
applies_when: zero-dependency or sandboxed Python where subprocess/git libraries are forbidden but git recency is needed
---

# Derive git ground truth with stdlib-only reads under a no-subprocess tripwire

## Context

Phase 7 (Drive / Accountability) needed **commit recency** as ground truth for per-goal progress velocity ("stalled N days / moving"). The obvious routes are both blocked by the plugin's own guardrails:

- The anti-creep test asserts a forbidden-substring list `== []` across *all* source — no `subprocess`, `os.system`, `eval`, `exec` (whole-file substring match, so even a comment trips it).
- A non-stdlib **import allowlist** — `GitPython` / `dulwich` are absent by design (zero new pip dependencies is a hard project rule).

So "just shell out to `git log`" and "just `import git`" are both tripwire violations that brick the suite. The signal still has to come from somewhere real.

## Guidance

Read git's plumbing as **plain files** with stdlib `open()` + `os.stat`:

1. `open()` `.git/HEAD` — resolve `ref: refs/heads/<branch>` (read-only; the loose ref file is optional and may be packed away, so don't depend on it).
2. Read the **last non-empty line** of `.git/logs/HEAD` (the reflog) — it is the most recent commit/checkout entry regardless of branch.
3. Parse the committer epoch by **indexing from the end**: split off the `\t<message>` tail; in the head part `fields[-1]` is the tz offset and `fields[-2]` is the epoch. Indexing from the front breaks the moment a committer name contains spaces.
4. Be **branch-agnostic** (the reflog tail is authoritative regardless of the current branch — this also means a `master`→`main` rename can't break it).
5. Wrap the whole thing in `try/except Exception: return None` → **fail-open to "unknown"**, never raise inside a hook.

For per-file recency, `os.stat(path).st_mtime` with a containment guard (`Path(candidate).resolve().relative_to(repo_root)`) keeps reads inside the repo and dodges path traversal.

## Why This Matters

- Keeps **two invariants intact at once**: zero new dependencies *and* fail-open (no hook path may raise/block) — while still getting real ground truth, with no behavioral test regression.
- **Indexing-from-end is the load-bearing trick.** Git reflog lines are `<old> <new> <Committer Name> <email> <epoch> <tz>\t<msg>`; the committer name is variable-length, so any positional-from-front parse is a latent bug.
- Fail-open to "unknown" preserves the rule that the signal degrades silently — a missing/corrupt `.git`, a packed ref, or an unparseable reflog all produce a benign default rather than a crash.

## When to Apply

- Zero-dependency, sandboxed, or import-allowlist-gated Python that still needs git recency/identity.
- Any read-path signal where forking a subprocess is too heavy or outright forbidden.
- Generalizes to other `.git` plumbing reads (HEAD sha, current branch name) — same file-read + fail-open discipline.

## Examples

**Do (stdlib, fail-open, end-indexed):** `anansi/store.py` `_last_commit_epoch` —
```python
reflog = Path(repo_root) / ".git" / "logs" / "HEAD"
last = [ln for ln in open(reflog, "r", encoding="utf-8").read().splitlines() if ln.strip()][-1]
head_part = last.split("\t", 1)[0]
fields = head_part.split()          # name may contain spaces
return float(int(fields[-2]))       # fields[-1] = tz, fields[-2] = epoch
# all wrapped in try/except Exception: return None
```

**Don't (both trip the tripwire):**
```python
subprocess.run(["git", "log", "-1", "--format=%ct"])   # forbidden-substring scan -> RED
import git                                              # import-allowlist -> RED
```

## Related

- **Never-omit beats a soft cap** — `anansi/render.py` `render_block`: render protected items first, record `protected_count`, stop the truncation pop at `floor = max(protected_count, 2)`, accept slightly-over-cap rather than violate the hard guarantee.
- **SAFE-04 first-person carve-out as a LABEL allowance** — add an allowed label prefix, never relax the second-person directive regex.
- **Read-time ground-truth signal** — compute freshness on the read path, never behind the debounced reflection write path.
- **CI-honest exit codes** for live smoke (`0` pass / `1` fail / `2` inconclusive) — "could not test" must not read as "passed."
- Phase artifacts: `.planning/phases/07-drive-accountability/07-LEARNINGS.md` (patterns P1–P5), `07-RESEARCH.md` (Pitfalls #2/#3).
