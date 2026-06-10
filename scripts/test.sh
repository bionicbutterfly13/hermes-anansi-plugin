#!/bin/sh
# anansi test runner — the durable repo-local test idiom (Phase 3).
#
# pytest is NOT installed in the hermes-agent venv and must never be installed
# into it (uv-sync wipe risk — 03-CONTEXT test-tooling constraint, locked).
# This script stages pytest into $REPO/.devtools/pytest once via
# `uv pip install --target` and runs the suite through PYTHONPATH using the
# hermes venv python. The venv itself is never modified.
#
# Usage:
#   ./scripts/test.sh                                        # full suite
#   ./scripts/test.sh anansi/tests/test_dryrun_demo.py -s
set -eu

REPO=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
VENV_PY="${HERMES_HOME:-$HOME/.hermes}/hermes-agent/venv/bin/python"
STAGE="$REPO/.devtools/pytest"

if [ ! -x "$VENV_PY" ]; then
    echo "error: hermes venv python not found at $VENV_PY" >&2
    exit 1
fi

if ! PYTHONPATH="$STAGE" "$VENV_PY" -c "import pytest" >/dev/null 2>&1; then
    echo "staging pytest into $STAGE (one-time; the hermes venv is NOT modified)" >&2
    uv pip install --python "$VENV_PY" --target "$STAGE" pytest
fi

if [ "$#" -eq 0 ]; then
    set -- "$REPO/anansi/tests"
fi

cd "$REPO"
export PYTHONPATH="$STAGE"
exec "$VENV_PY" -m pytest "$@" -q
