# STACK.md — Hermes Anansi Metacognition Plugin

Researched 2026-06-10. Ground truth: local hermes-agent install at `~/.hermes/hermes-agent`
(v0.16.0, branch `local-desktop-fixes`), icarus plugin (`~/.hermes/plugins/icarus`), hindsight
plugin (`~/.hermes/hermes-agent/plugins/memory/hindsight`), official docs at
hermes-agent.nousresearch.com, plus WebSearch verification (queries listed in Sources).

Headline: **this plugin needs zero new pip dependencies.** Everything required — plugin API,
host-owned LLM facade with JSON mode, SQLite — already ships with hermes-agent or the Python
stdlib. The stack decision is mostly "use the host's surfaces correctly," not "pick libraries."

## Recommended Stack

| Layer | Choice | Why | Confidence |
|-------|--------|-----|------------|
| Language | Python 3.11+ (support 3.11–3.13) | Host pins `requires-python = ">=3.11,<3.14"` in pyproject.toml; local interpreter is 3.11.13 | HIGH (read from pyproject.toml) |
| Plugin mechanism | hermes-agent plugin API: `plugin.yaml` + `__init__.py::register(ctx)` + `ctx.register_hook()` | Official, documented, update-safe; both icarus and hindsight use it | HIGH (official docs + 2 local precedents) |
| Hooks | `on_session_start`, `pre_llm_call`, `on_session_end` | `pre_llm_call` is the ONLY hook whose return value injects context (`{"context": str}` or plain string, appended to user message — never system prompt, preserving prompt cache). `on_session_end` fires after every `run_conversation()`, even on errors — correct slot for the reflection pass. Exact icarus hook surface. | HIGH (official hooks doc + icarus hooks.py) |
| Appraisal LLM call | `ctx.llm.complete_structured(json_mode=True, json_schema=..., timeout=..., max_tokens=..., model=...)` from `agent/plugin_llm.py` | This facade exists precisely for "plugin makes its own out-of-band model call." Host owns provider routing, auth, fallback; plugin never touches API keys. Returns `PluginLlmStructuredResult.parsed` (already-parsed JSON, fence-stripped) plus usage/cost. Async sibling `acomplete_structured()` available if the hook runs on an event loop. | HIGH (read plugin_llm.py source directly) |
| Appraisal model selection | Configurable via env (`ANANSI_MODEL`, `ANANSI_PROVIDER`) → passed as `model=`/`provider=` overrides; requires user config `plugins.entries.anansi.llm.allow_model_override: true` + `allowed_models: [...]`. Default: no override (host's active model) with documented cheap-tier recommendation. | Trust gate is fail-closed — overrides without config raise `PluginLlmTrustError`. Plan for this in docs/install: the plugin must degrade to the default model when the override is denied (catch `PluginLlmTrustError`, retry without override). | HIGH (trust-gate code read directly) |
| Default cheap-tier model recommendations | anthropic: `claude-haiku-4-5`; openai: `gpt-4o-mini` or `gpt-5-nano`; gemini: `gemini-2.5-flash`; openrouter: `qwen/qwen3.5-9b` | Mirror hindsight's `_PROVIDER_DEFAULT_MODELS` map verbatim — these are the host codebase's own current cheap-tier defaults. Web sources independently rank GPT-5 Nano / Claude Haiku 4.5 / Gemini Flash as the reliable cheap JSON tier in 2026. | MEDIUM (local map is HIGH as convention; "best cheap model" is MEDIUM, moves monthly) |
| State persistence | stdlib `sqlite3`, single DB file at `$HERMES_HOME/anansi/state.db` (resolve via `hermes_constants.get_hermes_home()`, never literal paths) | Zero deps, no daemon, matches PROJECT.md constraint. Hindsight precedent: profile-scoped config under `$HERMES_HOME/hindsight/`. | HIGH |
| SQLite configuration | `PRAGMA journal_mode=WAL` (persistent, set once at init), `PRAGMA synchronous=NORMAL`, `PRAGMA busy_timeout=5000`. Small transactions; one connection per hook invocation or a module-level connection guarded for thread use. | Standard 2026 guidance for low-concurrency agent state: WAL gives concurrent readers + queued writers; busy_timeout absorbs the rare lock collision; NORMAL is safe-with-WAL and faster than FULL. Agent workloads are ~single-digit writers/minute — pooling/async layers are overkill. | HIGH (sqlite.org WAL doc + multiple 2026 sources agree) |
| Appraisal schema/validation | stdlib `dataclasses` + defensive manual coercion of the parsed dict; pass `json_schema=` to `complete_structured` for provider-side `response_format` hints | The facade already builds `response_format: json_schema` for the provider and validates via `jsonschema` *if installed* (optional import, skipped silently otherwise). Don't duplicate that machinery. Fail-open requirement means validation failures must yield empty injection anyway — strict schema enforcement buys little. | HIGH (behavior read from plugin_llm.py `_parse_structured_text`) |
| Timeout / fail-open | `timeout=` kwarg on `complete_structured` (set ≈2–3s) + outer `try/except Exception` returning `None` from the hook | Host hooks are already non-blocking ("errors in any hook are caught and logged, never crashing the agent" — official docs), but the plugin must ALSO bound latency itself: host catches exceptions, it does not enforce a wall clock on a slow LLM call. `None` return = no injection. | HIGH (docs + plugin_llm signature) |
| Testing | `pytest`, mirroring the host's `tests/` layout; use `agent.plugin_llm.make_plugin_llm_for_test(plugin_id=..., policy=..., sync_caller=...)` to fake LLM responses; `tmp_path` + `HERMES_HOME` env override for SQLite round-trip tests | The host ships a purpose-built test helper for exactly this (injected policy + caller, no config.yaml round-trip, no real provider). Upstream PR standard requires tests in their framework. | HIGH (helper read in plugin_llm.py:1016) |
| Packaging | Standalone repo with the plugin as a plain directory installable at `$HERMES_HOME/plugins/anansi`; same layout drops into `hermes-agent/plugins/` for the upstream PR. `plugin.yaml` with `provides_hooks: [on_session_start, pre_llm_call, on_session_end]`. No `pip_dependencies` needed. | Loader reads `provides_hooks` (hermes_cli/plugins.py:1386). NOTE: hindsight's manifest uses a `hooks:` key, icarus uses `provides_hooks:` — the loader field is `provides_hooks`; the `hooks:` key appears to be advisory/legacy. Verify against the upstream-main loader at PR time. | HIGH for `provides_hooks`; MEDIUM on whether `hooks:` is also accepted upstream |

### plugin.yaml sketch (convention, from local precedents)

```yaml
name: anansi
version: 0.1.0
description: "Anansi — per-turn metacognitive appraisal (instincts, salience, contradictions) with fail-open injection."
provides_hooks:
  - on_session_start
  - pre_llm_call
  - on_session_end
requires_env: []        # no required keys — host owns LLM auth
# no pip_dependencies — stdlib only
```

## Alternatives Considered

| Alternative | Verdict | Reason |
|-------------|---------|--------|
| `pydantic` models for the appraisal schema | Viable, not recommended | Host core-pins `pydantic==2.13.4` so it's always importable at zero install cost — but the host's exact-pin policy means any pydantic-API usage couples the plugin to whatever pin upstream carries. Dataclasses + coercion is dependency-proof for the PR. Revisit only if the schema grows complex. (HIGH — pin read from pyproject.toml) |
| `jsonschema` as a declared dependency | Not needed | plugin_llm already soft-imports it; when absent, JSON mode still works and schema validation is skipped with a debug log. Fail-open design tolerates that. (HIGH) |
| `aiosqlite` / async DB layer | Rejected | Icarus hooks are plain sync functions and SQLite ops here are sub-millisecond row writes. If a hook ever runs on an asyncio loop, wrap the sync call in `asyncio.to_thread` rather than adding a dep. (HIGH for icarus precedent; MEDIUM on whether gateway-side hooks are ever awaited — check at implementation) |
| `instructor` / `outlines` / structured-output libraries | Rejected | 2026 ecosystem reviews rank these well for standalone apps, but they wrap provider clients the plugin must not own — `ctx.llm.complete_structured` is the sanctioned lane and already does fence-stripping + parse + optional validation. (HIGH) |
| Direct `openai`/`anthropic` SDK calls with own API key (icarus pattern: `OPENROUTER_API_KEY` via urllib) | Rejected | Icarus predates the `ctx.llm` facade and its key handling is exactly what plugin_llm was built to replace ("the plugin never sees raw OAuth tokens or API keys"). Also fails the "works with any configured provider" requirement. (HIGH) |
| JSON-file state (icarus `state.py` style) | Rejected for state, fine for nothing here | PROJECT.md specifies SQLite; contradiction log + concern list + score history are relational/append-heavy, where JSON files corrupt under concurrent sessions. SQLite WAL handles multi-session writes; flat JSON does not. (HIGH) |
| Tortoise/SQLAlchemy/peewee ORM | Rejected | 3–4 small tables, a handful of queries; an ORM adds a pip dependency and migration machinery for nothing. Raw SQL + dataclass row mappers. (HIGH) |
| Local model via Ollama for the appraisal call | Rejected | Explicitly out of scope in PROJECT.md (original Anansi infra being removed); also adds a daemon. The configurable-model knob covers users who route a local provider through the host's own provider config. (HIGH) |

## What NOT to Use

- **The MemoryProvider slot** (`register_memory_provider`) — Hindsight owns it (locked decision 2026-06-09). Provider plugins are exclusive: "only one of each type can be active at a time" (official plugins doc). This plugin is hooks-only and reads whatever memory context is already in the conversation.
- **`sys.path` mutation at import time** — known hermes-agent plugin-discovery design flaw (mnemosyne symlink incident, PROJECT.md). All imports relative (`from . import state`) like icarus.
- **Postgres, Apache AGE, RabbitMQ, Docker, background daemons, heartbeat threads** — the entire original Anansi infra is the anti-stack here. Also no `threading.Timer`/cron-like loops: "appraisal-only cycle" means all compute happens inside hook invocations.
- **System-prompt injection or conversation-history rewriting** — `pre_llm_call` injects into the user message by design ("Always the user message, never the system prompt. This preserves the prompt cache." — official hooks doc). Don't fight it.
- **Provider/model overrides without handling `PluginLlmTrustError`** — the trust gate is fail-closed; a missing `plugins.entries.anansi.llm` block means every override raises. Unhandled, that exception eats the appraisal on default installs.
- **`PRAGMA synchronous=OFF`** — tempting for speed, risks corruption on power loss; NORMAL+WAL is the accepted point on the curve (sqlite.org).
- **WAL on network-mounted `$HERMES_HOME`** — WAL needs shared-memory primitives; on NFS/network volumes it can silently misbehave. Edge case worth a startup check or a documented caveat, since `$HERMES_HOME` is user-relocatable. (MEDIUM — multiple 2026 sources, not verified against this install)
- **Hardcoded paths or model slugs** — standing rule; resolve via `get_hermes_home()`, env vars, and host config only.

## Versions

| Component | Version | Source / Note |
|-----------|---------|---------------|
| Python | `>=3.11,<3.14` | Host pyproject.toml; upper bound is load-bearing (cp314 wheel gaps in Rust transitives). Local: 3.11.13. HIGH |
| hermes-agent (target) | 0.16.0 (local fork, branch `local-desktop-fixes`); PR targets upstream `main` | plugin_llm.py and hook surface verified on this version — re-verify `ctx.llm` exists on upstream main before PR (this install has 7 open PRs of divergence). HIGH locally, MEDIUM for upstream main |
| sqlite3 | stdlib (SQLite ≥3.35 ships with Python 3.11; WAL since 3.7) | No pin needed. HIGH |
| pytest | match host dev tooling (host `tests/` + `conftest.py` exist; exact pin lives in host dev extras — confirm at implementation) | MEDIUM (presence verified, version not) |
| jsonschema | optional, undeclared | Soft-imported by plugin_llm; do not pin. HIGH |
| New pip dependencies | **none** (`pip_dependencies: []`) | Strongest possible posture for an upstream PR given the host's supply-chain-motivated exact-pin policy (pyproject.toml comments re: Mini Shai-Hulud worm, 2026-05-12). HIGH |
| Appraisal model defaults | `claude-haiku-4-5` (anthropic), `gpt-4o-mini`/`gpt-5-nano` (openai), `gemini-2.5-flash` (gemini), `qwen/qwen3.5-9b` (openrouter) | From hindsight's in-repo defaults map; web pricing snapshot 2026: Haiku 4.5 at ~$1/$5 per Mtok, GPT-5 Nano near-perfect structured output among budget models. MEDIUM — re-check at implementation, cheap tier churns. |

### Open items to verify during implementation (flagged, not blocking)

1. Whether `pre_llm_call` hooks are invoked sync or awaited in gateway sessions → decides `complete_structured` vs `acomplete_structured`. (Loader grep shows both lanes exist; icarus is sync.)
2. Whether upstream main's loader accepts the `hooks:` manifest key or only `provides_hooks:`.
3. Whether `pip_dependencies` in plugin.yaml is processed by the installer (hindsight declares it; no handler found in hermes_cli/plugins.py — likely lives in the install command). Moot if the plugin stays dependency-free.
4. `ctx.llm` availability on upstream main (facade confirmed in local 0.16.0 fork only).

### Sources

- Local ground truth: `~/.hermes/hermes-agent/agent/plugin_llm.py`, `~/.hermes/hermes-agent/hermes_cli/plugins.py`, `~/.hermes/hermes-agent/pyproject.toml`, `~/.hermes/plugins/icarus/{plugin.yaml,hooks.py}`, `~/.hermes/hermes-agent/plugins/memory/hindsight/{plugin.yaml,__init__.py}`
- [Hermes Agent — Plugins](https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins/)
- [Hermes Agent — Event Hooks](https://hermes-agent.nousresearch.com/docs/user-guide/features/hooks)
- [NousResearch/hermes-agent](https://github.com/nousresearch/hermes-agent)
- [SQLite — Write-Ahead Logging](https://sqlite.org/wal.html)
- [SQLite Is the Best Database for AI Agents (DEV)](https://dev.to/nathanhamlett/sqlite-is-the-best-database-for-ai-agents-and-youre-overcomplicating-it-1a5g)
- [Enabling WAL mode — Simon Willison TIL](https://til.simonwillison.net/sqlite/enabling-wal-mode)
- [Structured Output and JSON Mode Guide 2026 (TokenMix)](https://tokenmix.ai/blog/structured-output-json-guide)
- [Which LLMs Actually Produce Valid JSON (Medium)](https://medium.com/@lyx_62906/which-llms-actually-produce-valid-json-7c7b1a56c225)
- [Best LLM for JSON / Structured Output (Buzzi.ai)](https://www.buzzi.ai/tools/en/llm-pricing-comparison/best-for/json-output)
- [LLM Agent Architectures in 2026 (FutureAGI)](https://futureagi.com/blog/llm-agent-architectures-core-components/)
- [Reflective LLM-based Agent (Emergent Mind)](https://www.emergentmind.com/topics/reflective-llm-based-agent)
