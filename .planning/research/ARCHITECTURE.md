# ARCHITECTURE.md — Per-Turn Context-Injection Plugin (hermes-anansi)

Research date: 2026-06-10. Ground truth from local source (hermes-agent branch `local-desktop-fixes`
at `~/.hermes/hermes-agent`, icarus plugin at `~/.hermes/plugins/icarus`, Anansi at
`/Volumes/Asylum/repos/hex-auto/Anansi`). Local code citations are HIGH confidence; web-derived
patterns are labeled MEDIUM/LOW.

---

## Recommended Architecture

**A standalone hook-based plugin** (`kind: standalone`) that registers three lifecycle hooks
(`on_session_start`, `pre_llm_call`, `on_session_end`), makes its appraisal LLM sub-call through
the host-owned `ctx.llm` facade, persists state in SQLite under `$HERMES_HOME/anansi/`, and treats
every external interaction as fail-open with a wall-clock deadline.

```
$HERMES_HOME/plugins/anansi/          # also mirrors to in-tree plugins/anansi/ for the upstream PR
├── plugin.yaml        # name: anansi, kind: standalone (EXPLICIT — see Anti-Patterns), provides_hooks
├── __init__.py        # register(ctx) ONLY — zero import-time side effects
├── hooks.py           # lifecycle adapters: deadline + fail-open guard around everything
├── appraisal.py       # pure: (user_message, history, state_snapshot) → context block str | None
├── store.py           # the ONLY module that touches SQLite ($HERMES_HOME/anansi/state.db)
├── reflection.py      # on_session_end observation application (SQLite port of Anansi stored procs)
├── prompts/           # appraisal + reflection system prompts (text files, not inline strings)
└── tests/
```

Key decisions and why (all grounded in verified host behavior):

1. **Hooks run synchronously on the turn thread.** `PluginManager.invoke_hook()` iterates
   callbacks sequentially with per-callback try/except (`hermes_cli/plugins.py:1574-1609`). There
   is no async hook dispatch. Every millisecond spent in `pre_llm_call` is added directly to
   perceived turn latency. → The appraisal call must run inside a `concurrent.futures`
   executor with `future.result(timeout=BUDGET)` so the hook returns within a hard wall-clock
   budget (recommend 2.5s soft / 3.0s hard per PROJECT.md), independent of provider behavior.
   (HIGH — dispatcher code read directly.)

2. **LLM sub-call via `ctx.llm.complete_structured(...)`** — the supported lane for plugin-owned
   model calls (`hermes_cli/plugins.py:302-316`, `agent/plugin_llm.py:1-58`). It accepts
   `json_mode=True`, `json_schema=...`, `max_tokens`, and a `timeout` that is plumbed through to
   `agent.auxiliary_client.call_llm` (`agent/plugin_llm.py:683-700, 945-958`). The plugin never
   holds provider keys. Two timeout layers: pass `timeout=` to the facade (provider-level) AND
   the executor deadline (wall-clock guarantee). (HIGH)

3. **Cheap-model override is config-gated and fail-closed.** Model/provider overrides require
   `plugins.entries.anansi.llm.allow_model_override: true` (+ optional `allowed_models` allowlist)
   in config.yaml; a missing block means "no overrides", and the policy is re-read per call so
   config edits apply without restart (`agent/plugin_llm.py:202-246, 249-329`). The plugin should
   read its appraisal model from its own `$HERMES_HOME/anansi/config.json` and request it as
   `model=` only when configured — falling back silently to the user's active model if the trust
   gate rejects it (catch `PluginLlmTrustError`, degrade, don't fail the turn). (HIGH)

4. **Fail-open is two-layered.** The dispatcher already isolates a raising hook
   (`hermes_cli/plugins.py:1597-1608`) and both call sites wrap the whole hook pass in
   try/except (`agent/turn_context.py:340-341`, `agent/turn_finalizer.py:425-426`) — but relying
   on that produces WARNING log noise and gives no graceful degradation. The anansi hook must
   catch internally and return `None` (= no injection) on any error: LLM timeout, parse failure,
   corrupt/locked SQLite, missing config. Precedents: every icarus helper returns `[]`/`None` on
   exception (`~/.hermes/plugins/icarus/hooks.py:335-370, 390-433, 463-500`); Anansi itself
   returns an empty `SubconsciousOutput()` when the appraisal call fails
   (`/Volumes/Asylum/repos/hex-auto/Anansi/services/agent.py:220-222`). (HIGH)

5. **SQLite, WAL, single-writer discipline.** Hot path (`pre_llm_call`) does READS ONLY, using
   read-only URI connections (`sqlite3.connect("file:...?mode=ro", uri=True)` — icarus precedent
   at `hooks.py:408, 482`). All writes happen in `on_session_end`. Apply
   `PRAGMA journal_mode=WAL`, `synchronous=NORMAL`, `busy_timeout=5000` on the write connection.
   (Local precedent HIGH; PRAGMA guidance MEDIUM — verified against sqlite.org/wal.html and
   2026 community guidance, consistent across sources.)

6. **Injection goes into the user message, never the system prompt.** This is a host invariant,
   not a choice: plugin context from `pre_llm_call` is appended to the current turn's user
   message at API-call time only, never persisted, explicitly to preserve the prompt-cache
   prefix (`hermes_cli/plugins.py:1588-1592`, `agent/conversation_loop.py:610-626, 656-665`).
   The Anansi `build_system_prompt(subconscious_output=...)` injection point
   (`Anansi/services/agent.py:235-243`) therefore CANNOT be ported as-is — the port is:
   `format_subconscious_signals()`-style block (`Anansi/services/agent.py:90-125`) returned as
   `{"context": block}`. (HIGH)

---

## Component Boundaries

| Component | Owns | Must NOT do |
|-----------|------|-------------|
| `__init__.py` | `register(ctx)`: calls `ctx.register_hook()` 3×, stashes `ctx` for `ctx.llm` access | Import heavy deps, mutate `sys.path`, mention the strings `MemoryProvider`/`register_memory_provider` anywhere in its source (see Anti-Patterns #2) |
| `hooks.py` | Hook signatures, wall-clock deadline (executor), top-level fail-open guard, per-session dedup/throttle state | Business logic, SQL, prompt text |
| `appraisal.py` | Prompt assembly, `ctx.llm.complete_structured` call, JSON parse/validate, ≤500-token block formatting | Direct provider calls, file I/O besides reading prompt files |
| `store.py` | Schema creation/migration (`schema_version` table), read snapshot (hot path, `mode=ro`), apply observations (write path, WAL) | Being imported for anything but state; long-held connections on the hot path |
| `reflection.py` | The `apply_subconscious_observations` equivalent: contradiction log, concern list, confidence/trust score updates | Heartbeat/outreach/privilege logic (out of scope per PROJECT.md) |
| config | `$HERMES_HOME/anansi/config.json` → env fallback, mirroring Hindsight's resolution order (`plugins/memory/hindsight/__init__.py:297-339`); paths from `hermes_constants.get_hermes_home()` (used by the host's own plugin scanner, `hermes_cli/plugins.py:1105`) | Literal paths, hardcoded model names |

Allowed host imports (lazy, inside functions, mirroring Hindsight's lazy-import pattern):
`hermes_constants.get_hermes_home`. Everything else arrives via the `ctx` object at register
time. The icarus plugin imports nothing from the host at all — that is the bar.

### State schema (recommended)

```sql
-- $HERMES_HOME/anansi/state.db
CREATE TABLE schema_version (version INTEGER NOT NULL);
CREATE TABLE affect_summary  (id INTEGER PRIMARY KEY CHECK (id=1), summary TEXT, valence REAL,
                              arousal REAL, updated_at TEXT);          -- single-row
CREATE TABLE concerns        (id INTEGER PRIMARY KEY, text TEXT, weight REAL, status TEXT,
                              created_at TEXT, updated_at TEXT);
CREATE TABLE contradictions  (id INTEGER PRIMARY KEY, kind TEXT CHECK (kind IN
                              ('semantic','narrative','relational','emotional')),
                              description TEXT, evidence TEXT, resolved INTEGER DEFAULT 0,
                              created_at TEXT);
CREATE TABLE scores          (key TEXT PRIMARY KEY, value REAL, updated_at TEXT); -- confidence/trust
CREATE TABLE turn_log        (id INTEGER PRIMARY KEY, session_id TEXT, turn_id TEXT,
                              user_excerpt TEXT, appraisal_json TEXT, created_at TEXT);
```
(MEDIUM — shape derived from PROJECT.md requirements + Anansi stored-proc inputs/outputs
referenced in `Anansi/core/subconscious.py`; validate during phase design.)

---

## Data Flow

### Turn time (`pre_llm_call`)

```
agent core builds TurnContext
  └─ invoke_hook("pre_llm_call", ...)              agent/turn_context.py:316-341  [sync, turn thread]
       └─ anansi hook:
            1. throttle gate (skip social closers / near-identical repeats — icarus hooks.py:185-202, 588-592 precedent)
            2. store.read_snapshot()                ms-scale SQLite read, mode=ro; None on error
            3. appraisal.run(user_message, last-K history turns, snapshot)
                 └─ executor.submit(ctx.llm.complete_structured,
                        json_mode=True, max_tokens≈800, timeout=2.5, purpose="anansi appraisal")
                    .result(timeout=3.0)            hard wall-clock deadline
            4. parse JSON → format block ≤500 tokens (port of format_subconscious_signals,
                 Anansi/services/agent.py:90-125)
            5. return {"context": block}  — or None at ANY failure point
  └─ core joins all hook results with "\n\n"        agent/turn_context.py:332-339
  └─ appended to current turn's user message at API-call time ONLY (ephemeral, never persisted)
                                                    agent/conversation_loop.py:615-626
```

**Critical ordering finding:** the Hindsight memory prefetch (`prefetch_all`) runs AFTER the
`pre_llm_call` hooks (`agent/turn_context.py:359-374` vs hook at `:316`), and prior-turn
injections are ephemeral (never written back to `messages`, `agent/conversation_loop.py:610-614`).
**The hook therefore cannot see the current turn's injected memory context.** PROJECT.md's
assumption that the appraisal "reads whatever memory context is already injected" is NOT
satisfiable from hook kwargs. Appraisal inputs are: `user_message` + raw `conversation_history`
+ local SQLite state. Surface this to the roadmapper as a requirement amendment — the honest
options are (a) accept the reduced input (recommended: zero coupling, zero latency added), or
(b) a config-gated, budget-shared direct Hindsight recall from inside the plugin (adds latency
and couples to the provider; not recommended for v1). (HIGH — both call sites read directly.)

### Reflection time (`on_session_end`)

```
turn finalizer (every run_conversation!) → invoke_hook("on_session_end", ...)
                                                    agent/turn_finalizer.py:410-426
  └─ anansi hook:
       1. cheap bookkeeping ALWAYS: append turn_log row (session_id, turn_id, appraisal_json)
       2. LLM reflection pass DEBOUNCED: only when (session_id changed since last reflection)
          OR (N turns accumulated) — because this hook fires per turn, not per session (below)
       3. apply observations to SQLite in one WAL transaction; fail-open (log + skip on error)
```

`on_session_start`: load/initialize state, reset per-session throttle sets (icarus resets its
dedup sets here, `hooks.py:107-117`). Optionally return a one-line `{"context": ...}` state
summary; keep it tiny or return `None`.

---

## Hook Contract (exact signatures, file:line)

### Dispatcher semantics (applies to all hooks)

`PluginManager.invoke_hook(hook_name, **kwargs)` — `hermes_cli/plugins.py:1574-1609`:
- Synchronous, sequential, registration order; returns list of non-`None` results.
- Each callback wrapped in try/except — a raising plugin logs a WARNING, never breaks the turn.
- The dispatcher injects `telemetry_schema_version` into kwargs (`plugins.py:1594`) →
  **every hook MUST accept `**kwargs`** or it will raise `TypeError` on every call.
- Registration: `ctx.register_hook(name, callback)` (`hermes_cli/plugins.py:939-954`); unknown
  names warn but still store (forward-compat).

### `pre_llm_call`

Dispatched at `agent/turn_context.py:320-331` with EXACTLY these kwargs:

```python
_invoke_hook(
    "pre_llm_call",
    session_id=agent.session_id,
    task_id=effective_task_id,
    turn_id=turn_id,
    user_message=original_user_message,
    conversation_history=list(messages),          # full message dicts, pre-injection
    is_first_turn=(not bool(conversation_history)),
    model=agent.model,
    platform=getattr(agent, "platform", None) or "",
    sender_id=getattr(agent, "_user_id", None) or "",
)
```

Required plugin-side signature:

```python
def pre_llm_call(session_id="", task_id="", turn_id="", user_message="",
                 conversation_history=None, is_first_turn=False, model="",
                 platform="", sender_id="", **kwargs):
    ...
    return {"context": "..."}   # or a plain str, or None
```

Return contract (`hermes_cli/plugins.py:1582-1592` + consumption at
`agent/turn_context.py:332-339`): a dict with a truthy `"context"` key or a non-empty string;
all plugin results are joined with `"\n\n"` and appended to the current turn's user message at
API-call time (`agent/conversation_loop.py:615-626`). `None` = inject nothing. Context is
ephemeral — never persisted to the session DB. Icarus's working signature matches:
`pre_llm_call(session_id="", user_message="", is_first_turn=False, **kwargs)`
(`~/.hermes/plugins/icarus/hooks.py:573`).

### `on_session_end`

Dispatched at `agent/turn_finalizer.py:413-424` with EXACTLY these kwargs:

```python
_invoke_hook(
    "on_session_end",
    session_id=agent.session_id,
    task_id=effective_task_id,
    turn_id=turn_id,
    completed=completed,
    interrupted=interrupted,
    model=agent.model,
    platform=getattr(agent, "platform", None) or "",
)
```

Required plugin-side signature:

```python
def on_session_end(session_id="", task_id="", turn_id="", completed=False,
                   interrupted=False, model="", platform="", **kwargs):
    ...   # return value ignored
```

**The name is misleading: this fires at the end of EVERY `run_conversation` call — once per
user message in multi-turn sessions** (comment at `agent/turn_finalizer.py:410-411`; the
memory-provider session-end is explicitly deferred to CLI atexit/gateway expiry,
`turn_finalizer.py:403-408`). Additional safety-net firings on interrupted exits at
`cli.py:1019-1043` and `cli.py:12984-12995`. Icarus's signature for reference:
`on_session_end(session_id="", platform="", completed=False, **kwargs)`
(`~/.hermes/plugins/icarus/hooks.py:979`). Design consequence: reflection must be idempotent
and debounced (see Data Flow). (HIGH)

### `on_session_start`

Icarus working signature: `on_session_start(session_id="", platform="", **kwargs)` → optional
`{"context": str}` (`~/.hermes/plugins/icarus/hooks.py:107-180`). Host test-payload shape is
`{"session_id": ...}` (`hermes_cli/hooks.py:142`). Exact core call-site kwargs not re-verified
this session (MEDIUM) — `**kwargs` makes this moot.

### `ctx.llm` sub-call surface (for the appraisal)

`PluginContext.llm` property (`hermes_cli/plugins.py:302-316`) → `PluginLlm` keyed by plugin id.
The appraisal call (`agent/plugin_llm.py:683-700`):

```python
result = ctx.llm.complete_structured(
    instructions=...,                  # required, non-empty
    input=[{"type": "text", "text": appraisal_context}],
    json_mode=True,                    # or json_schema={...} for validated output
    system_prompt=...,
    model=cfg_model or None,           # gated: plugins.entries.anansi.llm.allow_model_override
    max_tokens=800,
    timeout=2.5,                       # plumbed to call_llm (plugin_llm.py:945-958)
    purpose="anansi subconscious appraisal",
)
# result.parsed is the dict when content_type == "json", else None  (plugin_llm.py:140-156)
```

Raises `PluginLlmTrustError` on ungated overrides (fail-closed, `plugin_llm.py:249-329`) —
catch it, retry once with no override, then fail open. Async siblings `acomplete_structured`
exist (`plugin_llm.py:823+`) but hooks are dispatched synchronously, so the sync API inside an
executor is the simpler, correct choice.

---

## Build Order

1. **Skeleton + registration** — `plugin.yaml` (explicit `kind: standalone`), `register(ctx)`,
   no-op hooks with correct signatures; test via `HERMES_PLUGINS_DEBUG=1` (`plugins.py:89-119`)
   and `hermes plugins enable anansi` (opt-in gate, `plugins.py:1196-1213`).
2. **store.py** — schema, WAL pragmas, read-snapshot + apply-observations, round-trip tests.
   No LLM yet.
3. **Appraisal path** — prompt port from Anansi (`run_subconscious_appraisal` context assembly,
   `Anansi/services/agent.py:133-227`, minus the asyncpg/affect/goals/dopamine fetches →
   replaced by the SQLite snapshot), `ctx.llm` call, parse, block formatting, injection test.
4. **Fail-open hardening** — tests for: LLM timeout (executor deadline), trust-gate rejection,
   malformed JSON, locked/corrupt/absent DB, missing config. Every test asserts the hook
   returns `None`/no-raise and the turn proceeds.
5. **Reflection pass** — per-turn bookkeeping + debounced LLM reflection; idempotency tests
   (hook fires per turn, not per session).
6. **Packaging** — dual layout (standalone `$HERMES_HOME/plugins/anansi` + in-tree `plugins/`)
   for the upstream PR.

---

## Integration Points

| Point | Mechanism | Citation |
|-------|-----------|----------|
| Discovery | user dir `~/.hermes/plugins/anansi/` with `plugin.yaml` + `__init__.py:register(ctx)`; module imported as `hermes_plugins.anansi` | `hermes_cli/plugins.py:1104-1109, 1514-1527` |
| Activation | opt-in via `plugins.enabled` in config.yaml (`hermes plugins enable anansi`) | `plugins.py:1196-1213` |
| LLM access | `ctx.llm` facade; trust knobs under `plugins.entries.anansi.llm.*` | `plugins.py:302-316`; `plugin_llm.py:33-53` |
| Hindsight coexistence | memory providers are `kind: exclusive` with separate discovery; hooks are additive and untouched by the provider slot — no conflict by construction | `plugins.py:1155-1165` |
| Icarus coexistence | both plugins' `pre_llm_call` results are concatenated by the dispatcher; ordering between plugins is registration order — do not depend on it | `turn_context.py:332-339` |
| Paths/config | `hermes_constants.get_hermes_home()` + `$HERMES_HOME/anansi/config.json` → env fallback (Hindsight resolution-order precedent) | `plugins/memory/hindsight/__init__.py:297-339` |
| Optional aux-model routing | `ctx.register_auxiliary_task("anansi", ...)` gives users a model-picker entry for the appraisal model — cleaner than a bespoke config key; evaluate in phase design | `plugins.py:828-937` |

---

## Anti-Patterns

1. **Blocking the turn thread past the budget.** Hooks are synchronous (`plugins.py:1574-1609`);
   there is no host-side hook timeout. A hung provider call = a hung turn. Always
   executor + `future.result(timeout=...)`. Note the leaked worker thread keeps running after
   timeout — use a small persistent `ThreadPoolExecutor(max_workers=1)`, not a thread per turn
   (Hindsight's single long-lived background thread is the in-repo precedent,
   `hindsight/__init__.py:196-229, 960-1004`). (HIGH)

2. **Mentioning `MemoryProvider` in `__init__.py` — even in a comment.** The manifest parser
   string-scans the first 8192 bytes of `__init__.py` and auto-coerces the plugin to
   `kind: exclusive` (memory provider) if it sees `register_memory_provider` or
   `MemoryProvider`, which silently prevents loading through `plugins.enabled`
   (`plugins.py:1344-1373`). Coercion only applies when `kind` is absent from the manifest →
   **declare `kind: standalone` explicitly in plugin.yaml** and keep those strings out of
   `__init__.py`. (HIGH — this is exactly the class of silent failure that burned the
   mnemosyne symlink incident.)

3. **Treating `on_session_end` as once-per-session.** It fires per `run_conversation`
   (`turn_finalizer.py:410-411`). Un-debounced LLM reflection there = one extra LLM call per
   turn on top of the appraisal, doubling cost and violating the one-extra-call budget. (HIGH)

4. **Touching the system prompt.** Injection lands in the user message by host design to keep
   the prompt-cache prefix byte-stable (`conversation_loop.py:656-665`). Any port of Anansi's
   `build_system_prompt` injection must be abandoned, not adapted. (HIGH)

5. **Import-time side effects.** No `sys.path` mutation, no DB creation, no config reads at
   module import — `register(ctx)` runs during discovery inside the host's try/except
   (`plugins.py:1440-1510`); a heavy or failing import marks the plugin errored. Lazy-import
   inside functions (Hindsight precedent, observation #9988). (HIGH; also PROJECT.md hard
   constraint)

6. **Writing SQLite on the hot path / shared rw connections.** Reads use `mode=ro` URI
   connections (icarus `hooks.py:408, 482`); writes confined to the reflection path with WAL +
   `busy_timeout`. A locked DB must degrade to "no snapshot", not an exception reaching the
   dispatcher. (HIGH for local precedent; PRAGMA details MEDIUM)

7. **Unbounded JSON-repair loops or trusting model output.** Single parse attempt with a
   lenient extractor (icarus `_parse_json_robust`, `hooks.py:758-795`, caps repair at 20
   strips); cap the injected block (~500 tokens), strip code fences, and length-limit every
   field (icarus `_sanitize_context_text`, `hooks.py:552-570`). (HIGH)

8. **Silent-failure blindness from total fail-open.** Fail-open everywhere means the plugin can
   be 100% broken while turns look fine. Record a failure counter + last-error in the state DB
   and log one WARNING per failure class per session, so `hermes`-side debugging has a signal.
   (MEDIUM — synthesis of fail-open guidance; the [2026 fallback-strategy literature]
   (https://futureagi.com/blog/what-is-llm-fallback-strategy-2026/) makes the same point about
   degraded-mode observability.)

9. **Hardcoded paths or models.** Resolve everything from `get_hermes_home()`/config (standing
   rule; the icarus `MEMORY_OS_REPO` default literal at `hooks.py:250` is the documented
   counter-example, observation #9973). (HIGH)

---

## Sources

Local (HIGH confidence, read this session):
- `~/.hermes/hermes-agent/hermes_cli/plugins.py` (dispatch, discovery, registration, trust)
- `~/.hermes/hermes-agent/agent/plugin_llm.py` (ctx.llm facade)
- `~/.hermes/hermes-agent/agent/turn_context.py`, `agent/turn_finalizer.py`,
  `agent/conversation_loop.py` (hook call sites + injection)
- `~/.hermes/hermes-agent/hermes_cli/hooks.py` (canonical hook payload shapes)
- `~/.hermes/plugins/icarus/hooks.py`, `plugin.yaml` (working hook + fail-open precedent)
- `~/.hermes/hermes-agent/plugins/memory/hindsight/__init__.py` (config resolution, thread/loop
  lifecycle, graceful degradation)
- `/Volumes/Asylum/repos/hex-auto/Anansi/services/agent.py:90-279` (component being ported)

Web (MEDIUM/LOW — directional only, superseded by local ground truth where they conflict):
- [LLM Agent Architectures in 2026](https://futureagi.com/blog/llm-agent-architectures-core-components/)
- [Microsoft Agent Framework — Agent Pipeline / middleware context injection](https://learn.microsoft.com/en-us/agent-framework/agents/agent-pipeline)
- [LangChain context engineering / middleware hooks](https://docs.langchain.com/oss/python/langchain/context-engineering)
- [What Is an LLM Fallback Strategy? 2026 Field Guide](https://futureagi.com/blog/what-is-llm-fallback-strategy-2026/)
- [Agentic Design Patterns 2026 catalog](https://www.augmentcode.com/guides/agentic-design-patterns)
- [SQLite WAL docs](https://sqlite.org/wal.html), [Single-writer SQLite architecture](https://www.bugsink.com/blog/database-transactions/),
  [SQLite for AI agents](https://dev.to/nathanhamlett/sqlite-is-the-best-database-for-ai-agents-and-youre-overcomplicating-it-1a5g)
