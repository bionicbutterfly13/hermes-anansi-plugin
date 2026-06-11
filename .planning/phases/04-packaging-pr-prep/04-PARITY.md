# PKG-03 Parity Re-Check — Upstream Main at PR Time

**Run:** 2026-06-10 ~8:50pm EDT
**PR-time upstream/main SHA:** `9dd9ef0ec99a87f078f7272b4323df5440b4b3f9`
**Phase-1 baseline SHA:** `183d86b3e`
**Distance:** 34 commits (`git rev-list --count 183d86b3e..9dd9ef0ec` = 34; main moved
d1383a6b1 → 9dd9ef0ec between planning ~8:25pm and this run — one new commit,
`fix(web): profiles page modal (#43858)`, web-only).

## Fetch + Diff (verbatim)

```
$ git -C ~/.hermes/hermes-agent fetch upstream
   d1383a6b1..9dd9ef0ec  main       -> upstream/main
$ git -C ~/.hermes/hermes-agent rev-parse upstream/main
9dd9ef0ec99a87f078f7272b4323df5440b4b3f9

$ git -C ~/.hermes/hermes-agent diff --stat 183d86b3e 9dd9ef0ec99a87f078f7272b4323df5440b4b3f9 \
    -- hermes_cli/plugins.py agent/plugin_llm.py tests/agent/test_plugin_llm.py plugins/
(empty — exit 0)
```

**Verdict: PARITY HOLDS.** All four surfaces (`hermes_cli/plugins.py`,
`agent/plugin_llm.py`, `tests/agent/test_plugin_llm.py`, `plugins/`) are byte-identical
from the Phase-1 baseline 183d86b3e through the PR-time SHA 9dd9ef0ec.

## Manifest-Key Verdict

Fresh grep at the PR-time SHA (`git show 9dd9ef0ec:hermes_cli/plugins.py`):

```
245:    provides_hooks: List[str] = field(default_factory=list)
1386:                provides_hooks=data.get("provides_hooks", []),
```

The loader's `_parse_manifest` reads **`provides_hooks`** (plugins.py:1386) into
`PluginManifest.provides_hooks` (plugins.py:245). The `hooks:` key seen in some in-tree
manifests (langfuse, disk-cleanup) is NOT read by any non-test code — it is informational
metadata. Our `plugin.yaml` uses `provides_hooks` — the correct, loader-read key. Keep it.

## `complete_structured` / Trust-Gate Verdict

Fresh grep at the PR-time SHA (`git show 9dd9ef0ec:agent/plugin_llm.py`):

```
249:class PluginLlmTrustError(PermissionError):
683:    def complete_structured(
1016:def make_plugin_llm_for_test(
```

Signature at 9dd9ef0ec (plugin_llm.py:683) is keyword-only:
`(instructions, input, json_schema, json_mode, schema_name, system_prompt, provider,
model, temperature, max_tokens, timeout, agent_id, profile, purpose)`.

Plugin call sites (grep-verified in `anansi/appraisal.py:253-276` and
`reflection.py:291-315`) pass exactly: `instructions`, `input`, `json_mode`,
`json_schema`, `timeout`, `purpose`, conditionally `max_tokens`, and `model` on the
override path. **Every kwarg the plugin passes is in the upstream signature — superset
check holds.** `PluginLlmTrustError` (line 249, the trust-gate fallback trigger) and
`make_plugin_llm_for_test` (line 1016, the test-fake factory) are both present.

## Conclusion (for PR_BODY)

Built and tested against upstream/main at `9dd9ef0ec99a87f078f7272b4323df5440b4b3f9`
(2026-06-10). All host surfaces the plugin depends on — the plugin loader's
`provides_hooks` manifest key, the `ctx.llm.complete_structured` keyword-only signature,
`PluginLlmTrustError`, and `make_plugin_llm_for_test` — are byte-identical to the
Phase-1 verification baseline (183d86b3e); no adaptation was needed.
