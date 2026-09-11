"""Offline contract tests for the separately authorized live-drive lane."""

import builtins
import importlib.util
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SMOKE_SCRIPT = REPO_ROOT / "scripts" / "live_drive_smoke.py"


def _load_smoke_module():
    spec = importlib.util.spec_from_file_location(
        "anansi_live_drive_smoke_test", SMOKE_SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _forbid_provider_import(monkeypatch):
    original_import = builtins.__import__

    def forbid_provider_import(name, *args, **kwargs):
        if name == "agent" or name.startswith("agent."):
            raise AssertionError("offline smoke path reached the provider import")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", forbid_provider_import)


def test_forced_offline_smoke_is_inconclusive_before_provider_import(
    monkeypatch, capsys
):
    smoke = _load_smoke_module()
    monkeypatch.setattr(sys, "path", sys.path.copy())
    monkeypatch.setattr(smoke, "_bootstrap_sys_path", lambda: None)
    monkeypatch.setattr(smoke, "_network_up", lambda: False)
    _forbid_provider_import(monkeypatch)

    assert smoke.main() == smoke.INCONCLUSIVE == 2
    assert "INCONCLUSIVE" in capsys.readouterr().out


def test_available_network_path_reaches_the_provider_import_guard(monkeypatch):
    smoke = _load_smoke_module()
    monkeypatch.setattr(sys, "path", sys.path.copy())
    monkeypatch.setattr(smoke, "_bootstrap_sys_path", lambda: None)
    monkeypatch.setattr(smoke, "_network_up", lambda: True)
    _forbid_provider_import(monkeypatch)

    with pytest.raises(AssertionError, match="provider import"):
        smoke.main()
