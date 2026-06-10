"""Test scaffolding for the anansi store suite.

Inserts the repo root at the front of sys.path so `from anansi
import store` resolves regardless of pytest's cwd. sys.path mutation is
acceptable in test scaffolding — the prohibition is on plugin code.
"""

import sys
from pathlib import Path

_REPO_ROOT = str(Path(__file__).resolve().parents[2])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
