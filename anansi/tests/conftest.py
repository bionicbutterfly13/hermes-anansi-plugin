"""Test scaffolding for the anansi suite.

Inserts the repo root at the front of sys.path so `from anansi
import store` resolves regardless of pytest's cwd, and makes the host
hermes-agent package importable (for agent.plugin_llm test fakes) when it
isn't already. sys.path mutation is acceptable in test scaffolding — the
prohibition is on plugin code. No literal user paths: the host location is
resolved via $HERMES_HOME with the conventional fallback.
"""

import os
import sys
from pathlib import Path

_REPO_ROOT = str(Path(__file__).resolve().parents[2])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)


def _ensure_host_on_path():
    try:
        import agent.plugin_llm  # noqa: F401

        return
    except ImportError:
        pass
    home = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
    agent_dir = home / "hermes-agent"
    if (agent_dir / "agent" / "plugin_llm.py").exists():
        agent_path = str(agent_dir)
        if agent_path not in sys.path:
            sys.path.insert(0, agent_path)


_ensure_host_on_path()
