# hermes-anansi-plugin

Development home of **anansi** — an observational metacognitive appraisal
plugin for [hermes-agent](https://github.com/NousResearch/hermes-agent). Development is
spec-driven with [GitHub Spec Kit](https://github.com/github/spec-kit): governing principles
in `.specify/memory/constitution.md`, features under `specs/`. The earlier planning history is
preserved as a read-only archive in `.planning/`.

The plugin itself lives in [`anansi/`](anansi/README.md) and is
self-contained: that directory is what gets installed (standalone) or contributed
(in-tree). See its README for install instructions, the full configuration reference,
observability, and honest limitations.

## Development

```sh
./scripts/test.sh                 # full suite (stages pytest under .devtools/; host venv untouched)
./scripts/test.sh anansi/tests/test_anticreep.py   # one module
```

The live development deploy is a symlink, so the running install tracks this checkout:

```sh
ln -s "$(pwd)/anansi" "$HERMES_HOME/plugins/anansi"
hermes plugins enable anansi
```

Every commit keeps the suite green — the symlinked plugin is live in real sessions.
