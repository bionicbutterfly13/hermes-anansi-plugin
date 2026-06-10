# Phase 1 Validation — Plan 01-01 (Loadable Inert Plugin vs Live Install)

**Date:** 2026-06-10
**Host:** hermes-agent (live install at `$HERMES_HOME` = `/Users/manisaintvictor/.hermes`), branch `local-desktop-fixes`
**Plugin:** `anansi` v0.1.0, deployed by symlink `$HERMES_HOME/plugins/anansi` → `/Volumes/Asylum/repos/hermes-anansi-plugin/anansi`

Note for Dr. Mani: the unrelated live plugin "Anansi Metacognitive Guardrails" at
`$HERMES_HOME/plugins/anansi` was left untouched throughout — it appears in every
plugin listing below as `anansi | enabled`, separate from our `anansi`.

---

## Item 1 — Gateway-lane dispatch

(Filled by task 01-01-03.)

## Item 2 — Hook-raise behavior

(Filled by task 01-01-03.)

## Item 3 — ctx.llm facade + manifest key on upstream main

**Answered now (not deferred).** Fetched upstream on 2026-06-10:

```
$ git -C ~/.hermes/hermes-agent fetch upstream main
   7df3aa34b..183d86b3e  main       -> upstream/main
$ git -C ~/.hermes/hermes-agent log -1 --format="%h %ad %s" --date=short upstream/main
183d86b3e 2026-06-10 fix(openrouter): route reasoning_effort to verbosity for adaptive Anthropic models (#43436)
```

**`provides_hooks` manifest key exists on upstream/main with the same shape:**

```
$ git show upstream/main:hermes_cli/plugins.py | grep -n "provides_hooks"
245:    provides_hooks: List[str] = field(default_factory=list)
1386:                provides_hooks=data.get("provides_hooks", []),
```

**Hook registration/dispatch surfaces match local citations exactly (same line anchors):**

```
$ git show upstream/main:hermes_cli/plugins.py | grep -n "def register_hook|def invoke_hook|telemetry_schema_version"
939:    def register_hook(self, hook_name: str, callback: Callable) -> None:
1574:    def invoke_hook(self, hook_name: str, **kwargs: Any) -> List[Any]:
1594:        kwargs.setdefault("telemetry_schema_version", OBSERVER_SCHEMA_VERSION)
1715:def invoke_hook(hook_name: str, **kwargs: Any) -> List[Any]:
```

**`ctx.llm` facade exists on upstream/main with the same shape:**

- `PluginContext.llm` property at upstream `hermes_cli/plugins.py:302-315` (lazy
  `from agent.plugin_llm import PluginLlm`, keyed by plugin id) — matches local.
- `agent/plugin_llm.py` exists on upstream/main: module docstring describes the
  host-owned facade with trust-gated overrides under
  `plugins.entries.<plugin>.llm.*`; `complete_structured` defined at
  `agent/plugin_llm.py:683` with `json_mode` (:689), `json_schema`, and
  `timeout: Optional[float]` (:696) kwargs; `parsed` populated when
  `json_mode=True` or `json_schema` given (:143).

**Conclusion:** upstream/main parity CONFIRMED for both `provides_hooks` and the
`ctx.llm` facade — the surfaces this plugin depends on are not local-only. Per the
standing STATE.md note, parity will still be re-verified immediately before the
Phase 4 PR (PKG-03), since upstream moves daily.

## Item 4 — Skeleton loads via plugins.enabled

Enabled with the documented subcommand (no fallback needed):

```
$ hermes plugins enable anansi
✓ Plugin anansi enabled. Takes effect on next session.
```

Loader debug proof captured from a real turn (`HERMES_PLUGINS_DEBUG=1`, full log at
`/tmp/anansi-dispatch-proof.txt`; `hermes plugins list` does not run full discovery,
so the turn's stderr is the load proof — the plan's documented fallback):

```
51:[plugins] DEBUG Parsed manifest: key=anansi name=anansi kind=standalone source=user path=/Users/manisaintvictor/.hermes/plugins/anansi
170:[plugins] DEBUG Loading plugin 'anansi' (source=user, kind=standalone, path=/Users/manisaintvictor/.hermes/plugins/anansi)
171:[plugins] DEBUG Plugin anansi registered hook: on_session_start
172:[plugins] DEBUG Plugin anansi registered hook: pre_llm_call
173:[plugins] DEBUG Plugin anansi registered hook: on_session_end
```

- `kind=standalone` — the manifest string-scan landmine did NOT coerce the kind.
- All three declared hooks registered, no others.
- `hermes plugins list` shows `anansi | enabled | 0.1.0 | user` (and,
  separately, the untouched guardrails plugin `anansi | enabled | 0.1.0 | user`).
- Discovery summary line: `[plugins] INFO Plugin discovery complete: 42 found, 36 enabled` — no load errors.

## Item 4b — Dispatch proof (real turn)

**Hooks fired.** The host's logging config does not surface plugin-logger DEBUG
lines, so per the plan's fallback the hooks were temporarily instrumented to append
to `/tmp/anansi-dispatch-proof-hooks.log`, one real turn was run, and the
instrumentation was then fully reverted (`git checkout -- anansi/__init__.py`;
`grep anansi-dispatch-proof-hooks __init__.py` returns nothing; working tree clean).
Result — ALL THREE hooks fired on a single `hermes -z` one-shot turn:

```
on_session_start 20260610_053454_13c33c
pre_llm_call 20260610_053454_13c33c
on_session_end 20260610_053454_13c33c
```

(`on_session_start` DOES fire on a `-z` one-shot: the host treats it as a fresh
session, so the open question in the plan resolves to "fires".)

**Output unchanged.** Prompt was `Reply with exactly: OK`; the model output was
exactly `OK` in every run. Zero occurrences of `[anansi` (outside `[plugins]` loader
tags) and zero `Traceback` in `/tmp/anansi-dispatch-proof.txt`,
`/tmp/anansi-hookfire-proof.txt`, and `/tmp/anansi-dispatch-proof-enabled2.txt`.

**Latency comparison (`/usr/bin/time -p`, same prompt):**

| Run | Plugin | real (s) | user (s) | sys (s) | Log |
|-----|--------|----------|----------|---------|-----|
| 1 | enabled | 234.88 | 10.48 | 2.50 | /tmp/anansi-dispatch-proof.txt |
| 2 | disabled | 29.58 | 10.68 | 2.21 | /tmp/anansi-dispatch-proof-disabled.txt |
| 3 | enabled | 24.50 | 10.84 | 2.42 | /tmp/anansi-dispatch-proof-enabled2.txt |

Reading for Dr. Mani: run 1's 234.88s is provider/network wait, not plugin
overhead — its user+sys CPU time (12.98s) is essentially identical to the other
runs (12.89s, 13.26s), and run 3 (enabled) was FASTER than the disabled baseline.
The enabled-vs-disabled delta is lost in run-to-run LLM variance; there is no
consistent regression from the no-op hooks. ROADMAP success criterion 2 (output
AND latency unchanged) is satisfied for the skeleton.

After the comparison the plugin was re-enabled (`✓ Plugin anansi enabled`).
