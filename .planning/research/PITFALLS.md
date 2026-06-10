# PITFALLS — Per-Turn LLM Appraisal Sub-Call via Plugin Hooks

Research for the hermes-anansi metacognition plugin (pre_llm_call appraisal + on_session_end reflection).
Confidence levels: HIGH = official docs / verified local source code / multiple sources. MEDIUM = web-verified
with one strong source. LOW = single unverified source, needs validation.

Local ground truth cited throughout:
- `~/.hermes/plugins/icarus/hooks.py` (proven hook + fail-open patterns in this exact framework)
- `/Volumes/Asylum/repos/hex-auto/Anansi/services/agent.py` (the appraisal being ported)
- Memory note `hermes-sync-thread-state.md` (mnemosyne symlink incident, 2026-06-09)
- `.planning/PROJECT.md` (constraints: fail-open, ≤500-token block, 2–3s timeout, SQLite-only)

---

## Critical Pitfalls

### 1. Latency creep — the appraisal serializes onto every turn's critical path

**What:** A `pre_llm_call` appraisal runs BEFORE the main LLM call, so its full wall time (network + queue +
generation) adds directly to every turn's time-to-first-token. A "fast" call that p50s at 800ms can p99 at
8–15s when the provider is degraded — and a per-call socket timeout does not bound total wall time
(connect + read are separate timeouts; retries multiply them).

**Why it happens:** Reflection/appraisal steps are sequential by default; teams budget for the median and
get burned by the tail. Provider-side queueing and reasoning-model "thinking" tokens inflate latency
unpredictably. (MEDIUM — [Trajectory Reduction paper](https://arxiv.org/pdf/2509.23586) notes reflection
steps add latency and suggests parallelizing at the cost of context; [Maxim guide](https://www.getmaxim.ai/articles/how-to-reduce-llm-cost-and-latency-a-practical-guide-for-production-ai/).)

**How to avoid:**
- Enforce ONE hard wall-clock deadline (~2–3s per PROJECT.md) around the entire appraisal —
  `asyncio.wait_for` / thread + join-with-timeout — not just per-request socket timeouts.
- Zero retries on the appraisal call. Miss the deadline → empty injection, move on.
- Skip the appraisal when it can't add value: social closers and near-duplicate turns. icarus already has
  both gates (`_is_social_close`, the 0.85 token-overlap gate, hooks.py:185–202, 588–593) — copy them. (HIGH — local source)
- Pay one-time costs once per process, not per turn (icarus `_qdrant_start_attempted` at-most-once pattern,
  hooks.py:240–242). (HIGH — local source)
- Use a flash-tier model; if the configured model is a reasoning model, force minimal reasoning (see Gotcha #4).

**Detection:** Log appraisal wall-time per turn into the plugin's SQLite state; alert/inspect when p95
exceeds the deadline (means the timeout isn't actually binding). A turn that visibly "hangs before the
agent starts typing" is this pitfall.

---

### 2. Cost creep — a "cheap" call per turn is a 2x call-count multiplier

**What:** One extra LLM call per turn doubles call count, and cost grows silently if the appraisal input
(memory context + state + transcript) grows unbounded. Anansi fed up to 12,000 chars of context and allowed
1,800 output tokens per appraisal (agent.py:207, 216) — far more than needed to produce a ≤500-token block.

**Why it happens:** Inputs accrete (memory injection grows, contradiction logs grow, affect summaries grow)
and nobody re-checks token counts after launch; internal sub-calls are often invisible in cost dashboards.
(MEDIUM — [Braintrust cost-attribution playbook](https://www.braintrust.dev/articles/how-to-track-llm-costs-2026)
identifies untracked per-feature sub-calls and token spikes as the main cost leak; HIGH for the Anansi
numbers — local source.)

**How to avoid:**
- Hard-cap appraisal INPUT (recommend ≤ ~4k tokens: truncate memory context the way Anansi truncated goals
  `[:2000]` and total context `[:12000]`, but tighter) and OUTPUT (`max_tokens` ≈ 700, enough for the
  parsed ≤500-token block plus JSON overhead).
- Make the appraisal model independently configurable to a cheap tier (PROJECT.md requirement) and default
  it to one — icarus defaults extraction to `deepseek/deepseek-v4-flash` / `gpt-5-nano` (hooks.py:22–24). (HIGH)
- Record prompt_tokens/completion_tokens per appraisal in SQLite; surface a running daily total.

**Detection:** Token counts per appraisal trending up week-over-week; provider bill line for the appraisal
model exceeding the estimate in the budget section below.

---

### 3. Prompt injection via memory — the appraisal reads poisoned context AND writes a new injection surface

**What:** The appraisal consumes whatever memory context Hindsight/icarus injected (PROJECT.md: "reads
whatever memory context is already injected"). Poisoned memory (a planted instruction stored weeks ago)
can steer the appraisal's output; the appraisal block itself then becomes a SECOND injection channel into
the main model — laundered through the plugin and carrying its implicit authority. Memory-poisoning is a
deferred attack: write and read are separated in time, so it evades turn-level review.

**Why it happens:** Agents trust their own data pipeline; retrieved/memorized content is treated as
legitimate context. (HIGH — multiple 2026 sources: [OWASP-aligned 2026 agent security overview](https://swarmsignal.net/ai-agent-security-2026/),
[indirect prompt injection state of the art](https://zylos.ai/research/2026-04-12-indirect-prompt-injection-defenses-agents-untrusted-content/),
[corrupted-memory web agents, arXiv:2506.17318](https://arxiv.org/pdf/2506.17318).)

**How to avoid:**
- Sanitize the appraisal's OUTPUT before injection with the existing icarus pipeline:
  `_INJECTION_PATTERNS` + `_validate_safe_content` + `_sanitize_context_text` (hooks.py:505–570). Treat the
  appraisal model's output as untrusted text, not as plugin-authored text. (HIGH — local source, proven defenses)
- Constrain output structurally: parse JSON into a fixed schema, render the injected block from the parsed
  FIELDS (instincts/salience/contradictions/confidence), never pass raw model prose through.
- Frame the injected block as data, not instructions: a clearly labeled observation block
  ("[anansi appraisal] signals, advisory only"), no imperative phrasing.
- In the appraisal system prompt, instruct the model that memory context is untrusted reference material.
  (MEDIUM — standard guidance, imperfect defense; don't rely on it alone.)
- Reflection pass (`on_session_end`) writes derived observations to local SQLite, not to the shared memory
  store — keeps the poisoning blast radius local and avoids the write-side of memory poisoning.

**Detection:** Appraisal blocks containing imperatives, tool directives, URLs, or `[SYSTEM:`-style prefixes
(the `_is_system_injection` prefix list, hooks.py:34–44, is a starting signature set). Log every injected
block; spot-check for directive density.

---

### 4. JSON-mode / structured-output failures — valid-looking output that isn't

**What:** The appraisal depends on a JSON-mode response every turn. Real failure modes: markdown-fenced
JSON, truncated JSON (max_tokens hit mid-object), dropped/renamed fields, single object instead of array
(or wrapped `{"entries": [...]}`), refusals, and provider bugs returning `content: null` under
`response_format` (icarus hit this with DeepSeek — hooks.py:886–887).

**Why it happens:** JSON *mode* guarantees syntax at best, not schema; truncation and refusal bypass even
that. Plain JSON mode shows 2–12% schema-mismatch rates depending on provider; large/deeply-nested schemas
make constrained decoding worse. (MEDIUM — [structured-output production guide](https://pub.towardsai.net/llm-structured-outputs-in-production-how-to-stop-json-from-breaking-your-ai-workflow-66703754d341),
[2026 structured-output comparison](https://pockit.tools/blog/llm-structured-output-complete-guide/);
HIGH for the DeepSeek null and fence-stripping cases — local source.)

**How to avoid:**
- Keep the schema small and flat (a handful of top-level keys — Anansi's `_parse_subconscious_output` reads
  a flat dict, agent.py:61–87).
- Reuse/port icarus `_parse_json_robust` (hooks.py:758–795): fence stripping, first-`{`/`[` seek,
  progressive trailing-char strip. Add: check `finish_reason` for truncation; treat `content: null` as failure.
- Validate parsed output field-by-field with defaults (every field optional; missing → empty), exactly as
  both Anansi (`return SubconsciousOutput()` on non-dict, agent.py:224–225) and icarus (type/length filters,
  hooks.py:906–924) do.
- Any parse failure → empty injection (fail-open). Never retry-loop on parse errors inside the turn.

**Detection:** Count parse-failure rate per model in SQLite; >2–3% sustained means the configured appraisal
model/params combo is wrong (see Gotcha #4 on model param quirks).

---

### 5. Hook exceptions breaking turns — one unhandled error nukes turn reliability

**What:** An exception escaping `pre_llm_call` can abort or corrupt the entire turn — the user loses a
response because an *optional* enrichment failed. Same for `on_session_end` breaking session teardown.
This is the single constraint PROJECT.md marks non-negotiable ("zero impact on turn reliability").

**Why it happens:** Narrow `except` clauses miss real-world error types (DNS failures, `OSError`,
`sqlite3.DatabaseError`, `asyncio.TimeoutError`); "fail-open vs fail-closed" is chosen implicitly by
whatever the framework does with a raised hook exception — don't find out in production. (MEDIUM —
[runtime governance fail-open/fail-closed analysis](https://arxiv.org/pdf/2603.16586); HIGH for the
local patterns below.)

**How to avoid:**
- One outermost `try/except Exception` per hook entry point that logs a warning and returns `None`/empty —
  the exact Anansi pattern at BOTH levels: inside `run_subconscious_appraisal` (warning + empty
  `SubconsciousOutput()`, agent.py:220–222) and again at the call site (agent.py:382–410). Belt and suspenders.
- Sub-steps get their own narrower try/excepts with `logger.debug` (Anansi affect/goals/dopamine fetches,
  agent.py:158–205) so one degraded input doesn't kill the whole appraisal — degraded context beats no appraisal.
- Hook return contract: return `{"context": str}` or `None`, never raise (icarus contract, hooks.py:180, 696).
- Test the fail-open paths explicitly (PROJECT.md requires it): LLM down, timeout, corrupt SQLite, malformed
  JSON, missing config — each must yield a normal turn with empty injection.
- Don't trust the framework to sandbox you: verify experimentally what hermes-agent does when a hook raises,
  then make it moot by never raising.

**Detection:** Any turn failure whose traceback includes the plugin module = release blocker. Log a
distinct marker (e.g., `[anansi] appraisal skipped: <reason>`) on every fail-open so silent-degradation
weeks are visible (cf. the upstream `#43313` lesson: configured-but-unavailable memory logged at DEBUG →
week-long silent outage).

---

### 6. State corruption — SQLite under concurrent hooks and crash-mid-write

**What:** Appraisal state (affect summary, concerns, contradiction log, scores) read in `pre_llm_call` and
written in `on_session_end` can be corrupted by concurrent sessions (two gateways + CLI + desktop run
against the same `$HERMES_HOME` on this install), crash-mid-write, or schema drift between plugin versions.
Corrupt state then poisons every future appraisal — or worse, crashes the hook (see Pitfall 5).

**Why it happens:** Default SQLite (rollback journal, no busy_timeout) raises "database is locked"
immediately under a second writer; WAL-mode DBs copied without their `-wal` file are stale/corrupt; WAL on
network filesystems silently misbehaves. (HIGH — [SQLite concurrency write-up](https://tenthousandmeters.com/blog/sqlite-concurrent-writes-and-database-is-locked-errors/),
[production SQLite setup](https://oneuptime.com/blog/post/2026-02-02-sqlite-production-setup/view), multiple sources agree.)

**How to avoid:**
- `PRAGMA journal_mode=WAL`, `PRAGMA synchronous=NORMAL`, `PRAGMA busy_timeout=5000` on every connection;
  short transactions; one write transaction per hook invocation.
- Open read-only where possible: icarus uses `file:...?mode=ro` URIs for cross-DB reads (hooks.py:408, 482) —
  do the same when the appraisal only reads.
- Treat state as advisory cache: on ANY read error or failed validation, proceed with empty state (the
  appraisal still runs on the user message + memory context alone) and quarantine the bad file
  (rename `.corrupt-<ts>`), recreate schema. Never block a turn on state health.
- Version the schema (`PRAGMA user_version`), migrate forward explicitly; unknown version → quarantine + recreate.
- Keep the DB under `$HERMES_HOME` on local disk (it is), never a network mount/Docker volume.

**Detection:** `sqlite3.DatabaseError`/`OperationalError` in plugin logs; `PRAGMA integrity_check` in tests
and a doctor-style status command; state file size growing without bound (missing pruning of
concern/contradiction logs).

---

### 7. Self-reinforcing feedback loops — the appraisal eats its own output

**What:** Two loops to design against. (a) Internal: `on_session_end` reflection updates state from a
transcript whose responses were already shaped by injected appraisal blocks — the appraisal can amplify its
own prior moods/concerns each session until state drifts into a fixed obsession. (b) External: icarus
`post_llm_call`/`on_session_end` capture assistant responses into fabric/memory; Hindsight memorizes turns.
Appraisal-flavored phrasing gets stored, later retrieved as "memory context", and re-fed to the next
appraisal — an echo chamber across plugins.

**Why it happens:** Memory write/read separation hides the loop (same mechanism that makes memory poisoning
hard to spot — see Pitfall 3 sources). No web source documents this for appraisal layers specifically; this
is reasoned from the local architecture. (LOW–MEDIUM — flag for validation in early sessions.)

**How to avoid:**
- Tag the injected block with a fixed sentinel prefix (e.g., `[anansi appraisal]`) and EXCLUDE
  sentinel-bearing text from the reflection pass's inputs and from any state update derived from transcripts
  (icarus's `_is_system_injection` prefix-exclusion is the local precedent, hooks.py:41–44, 941–945).
- Decay/prune state: cap concern and contradiction lists (icarus caps creative lists at 15–20 entries,
  hooks.py:732–750), decay confidence scores toward neutral without re-evidence.
- Keep reflection updates conservative: bounded deltas per session, not wholesale rewrites.

**Detection:** State diffs across sessions showing the same concern strengthening with no new user input;
appraisal blocks quoting their own previous phrasing; confidence scores saturating at 0 or 1.

---

### 8. Autonomy creep — appraisal output drifts from observation to instruction

**What:** The Anansi source material was built for initiative (heartbeat, outreach, privilege ladder, goal
pursuit). Ported carelessly, the appraisal prompt/fields produce imperatives ("you should reach out",
"prioritize task X"), and the main model — primed to follow context — treats them as orders. The plugin
becomes a steering wheel, exactly what PROJECT.md scoped out ("metacognition without pushiness").

**Why it happens:** Prompt text and schema fields inherited from the autonomous version carry drive
mechanics implicitly (dopamine modulation, active goals, heartbeat decision context — agent.py:171–205
feeds goals + dopamine into the appraisal context). Injected context with directive framing measurably
shifts agent behavior (same mechanism as injection — Pitfall 3 sources). (HIGH for the inherited-source
risk — local source; MEDIUM for the behavioral-shift mechanism.)

**How to avoid:**
- Do NOT port the goals/dopamine context inputs (already decided: confidence/trust replaces dopamine; goals
  out of scope). Re-write the subconscious system prompt from scratch for observation-only output; don't
  start from `load_subconscious_prompt()`.
- Schema enforces it: fields are nouns (instincts, salient_memories, contradictions, confidence), no
  `suggested_action` / `next_step` / `should_*` fields. Strip imperative sentences from rendered output.
- Frame the block explicitly: "advisory signals; not instructions; do not act on these beyond informing
  your response."
- Add a test asserting the rendered block contains no imperative/directive patterns (reuse the
  `_validate_safe_content` directive-density heuristic, hooks.py:532–549, inverted as a unit test).

**Detection:** Agent responses referencing the appraisal as a reason for unrequested actions ("based on my
instincts I went ahead and..."); directive-density heuristic firing on rendered blocks.

---

## Ecosystem-Specific Gotchas (hermes-agent / this install)

### G1. Plugin discovery EXECUTES top-level plugin code — never mutate global state at import (the mnemosyne incident)
hermes-agent provider discovery imports plugin modules, running their top-level code. On 2026-06-09 a stale
`~/.hermes/plugins/mnemosyne` symlink's `cli.py` did `sys.path.insert` at import, contaminating provider
discovery so `hermes memory status` falsely reported hindsight "available ✓" (imported from anaconda, not
the venv). Logged upstream as design issue, not yet fixed. **Rule: plugin module top level = constants and
function defs only.** No `sys.path` mutation, no `os.environ` writes, no I/O, no network at import time.
Note icarus itself bends this inside a hook (`sys.path.insert` for memory-os, hooks.py:348–349, and an
env-var write at 353–354) — runtime-scoped, but do not copy that pattern; resolve imports via packaging.
(HIGH — verified incident, memory note + PROJECT.md out-of-scope item)

### G2. Hook surface and return contract come from icarus, not from docs
Proven hook set on this install: `on_session_start`, `pre_llm_call(session_id, user_message, is_first_turn,
**kwargs)`, `post_llm_call`, `on_session_end(session_id, platform, completed, **kwargs)`. Inject by
returning `{"context": "<text>"}`; return `None` to inject nothing. Always accept `**kwargs` — the
framework adds parameters over time. (HIGH — local source, hooks.py:107, 573, 699, 979)

### G3. Context stacking — you are the third injector on every turn
Hindsight (memory provider) and icarus (fabric + qdrant + sessions + facts) already inject per-turn
context. An unconditioned ≤500-token appraisal block stacks on top. Respect the cap strictly, dedup across
turns (icarus `_injected_*` sets pattern, hooks.py:66–69), and skip injection when the appraisal found
nothing notable — an empty-but-present block every turn is pure token tax. (HIGH — local architecture)

### G4. Appraisal-model parameter landmines (configurable model requirement)
Verified locally in icarus: GPT-5-family models reject `max_tokens`/`temperature` and need
`max_completion_tokens` + `reasoning_effort: "minimal"` or they burn the whole budget on reasoning and
return EMPTY content (hooks.py:853–859); DeepSeek under `response_format` has returned `content: null`
(hooks.py:886–887). Since the appraisal model is config-resolved, gate generation params by model family
and treat `null`/empty content as a parse failure (fail-open). (HIGH — local source)

### G5. Credential resolution order can 401 the appraisal call
On this install a stale `ANTHROPIC_API_KEY` in `~/.zshrc` shadowed a valid OAuth token because resolution
order differed by call path (PRs #43313/#43345 territory). If the plugin resolves provider credentials
itself for the appraisal call, prefer going through hermes-agent's provider/config machinery rather than
raw env reads — and treat 401s as a fail-open case with a distinct log reason, since the MAIN call may
still work via a different resolution path. (HIGH — verified incident, memory note)

### G6. Module globals are per-process, not per-session
icarus resets its module-level sets in `on_session_start` (hooks.py:110–113) because the process may serve
multiple sessions (gateways stay up for days on this install — two headless gateways run from the venv).
Keep per-session appraisal state keyed by `session_id` in SQLite, not in module globals; reset any
process-level caches on session start. (HIGH — local source + install facts)

### G7. Paths and homes
Resolve everything from `$HERMES_HOME` with a fallback chain (icarus `_resolve_state_db` pattern,
hooks.py:376–387). Standing rule: never literal paths. The plugin must also work installed either in-tree
(`plugins/` for the upstream PR) or at `$HERMES_HOME/plugins/anansi` — no assumptions about its own location.
(HIGH — PROJECT.md constraint + global rule)

---

## Cost & Latency Budget Guidance

Estimates flagged as such; validate against the first week of real telemetry.

| Budget item | Target | Hard limit | Rationale |
|---|---|---|---|
| Appraisal wall-time (p50) | ≤ 1.0s | — | Flash-tier JSON call with ~3–4k token input |
| Appraisal wall-time (hard deadline) | — | 2–3s, zero retries | PROJECT.md requirement; one `asyncio.wait_for`-style outer deadline |
| Appraisal input tokens | ≤ ~4k | truncate, never fail | Anansi capped raw context at 12k chars; tighter is fine for signal extraction |
| Appraisal output tokens | ≤ ~700 (`max_tokens`) | — | Enough for the ≤500-token rendered block + JSON overhead; Anansi's 1800 was oversized |
| Injected block | ≤ 500 tokens, omit when empty | 500 | PROJECT.md cap; stacking with Hindsight + icarus (G3) |
| Calls per turn | exactly 1 (or 0 when skipped) | 1 | PROJECT.md constraint; skip on social closers / near-duplicate turns |
| Reflection pass (`on_session_end`) | 1 call per session, ≤ ~8k input | 45s timeout | Off the turn path; icarus uses 45s for its session-end extraction (hooks.py:880) |

**Cost estimate (LOW confidence on exact prices — verify current cheap-tier pricing at build time):**
at flash-tier pricing on the order of $0.05–0.50 per 1M input tokens, a 4k-in/0.7k-out appraisal costs
roughly $0.0003–0.002 per turn → ~100 turns/day ≈ **$0.03–0.20/day**. The risk is not the unit price but
unbounded input growth (Pitfall 2) — the caps are what keep this number flat.

**Mandatory telemetry (cheap, local):** per appraisal, write to the plugin SQLite: wall_ms, prompt_tokens,
completion_tokens, model, outcome (`ok | timeout | parse_fail | llm_error | skipped:<reason>`). This makes
every pitfall above detectable from one table and feeds the validation of these LOW/MEDIUM-confidence
estimates. (Per-call attribution is the consistent 2026 recommendation —
[Braintrust](https://www.braintrust.dev/articles/how-to-track-llm-costs-2026),
[MLflow observability guide](https://mlflow.org/articles/setting-up-llm-observability-pipelines-in-2026/).)

---

## Source Index

**Local (HIGH confidence ground truth):**
- `/Volumes/Asylum/repos/hex-auto/Anansi/services/agent.py:133–227, 382–410` — appraisal + two-level fail-open
- `~/.hermes/plugins/icarus/hooks.py` — hook contract, sanitization (`_INJECTION_PATTERNS`,
  `_validate_safe_content`), `_parse_json_robust`, model-param quirks, social/overlap gates, ro-mode SQLite
- `~/.claude/projects/-Users-manisaintvictor--hermes/memory/hermes-sync-thread-state.md` — mnemosyne symlink
  incident; credential-order 401; silent memory-provider outage (PR #43313)
- `/Volumes/Asylum/repos/hermes-anansi-plugin/.planning/PROJECT.md` — binding constraints

**Web (2026):**
- https://arxiv.org/pdf/2509.23586 — reflection-step latency/cost trade-offs
- https://www.getmaxim.ai/articles/how-to-reduce-llm-cost-and-latency-a-practical-guide-for-production-ai/
- https://www.braintrust.dev/articles/how-to-track-llm-costs-2026 — per-feature sub-call cost attribution
- https://swarmsignal.net/ai-agent-security-2026/ — memory poisoning, OWASP agent top-10 framing
- https://zylos.ai/research/2026-04-12-indirect-prompt-injection-defenses-agents-untrusted-content/
- https://arxiv.org/pdf/2506.17318 — context-manipulation attacks on agent memory
- https://pub.towardsai.net/llm-structured-outputs-in-production-how-to-stop-json-from-breaking-your-ai-workflow-66703754d341
- https://pockit.tools/blog/llm-structured-output-complete-guide/ — provider schema-failure rates
- https://arxiv.org/pdf/2603.16586 — fail-open vs fail-closed runtime governance
- https://tenthousandmeters.com/blog/sqlite-concurrent-writes-and-database-is-locked-errors/
- https://oneuptime.com/blog/post/2026-02-02-sqlite-production-setup/view — WAL/busy_timeout/backup rules
- https://mlflow.org/articles/setting-up-llm-observability-pipelines-in-2026/
