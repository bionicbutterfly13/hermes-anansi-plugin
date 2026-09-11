"""Offline contract tests for the separately authorized live-drive lane."""

import builtins
import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SMOKE_SCRIPT = REPO_ROOT / "scripts" / "live_drive_smoke.py"
LIVE_RECORD = REPO_ROOT / ".planning" / "phases" / "08-close-known-gaps" / "08-LIVE-SMOKE.md"


def _load_smoke_module():
    spec = importlib.util.spec_from_file_location(
        "anansi_live_drive_smoke_test", SMOKE_SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_forced_offline_smoke_is_inconclusive_before_provider_import(
    monkeypatch, capsys
):
    smoke = _load_smoke_module()
    monkeypatch.setattr(smoke, "_network_up", lambda: False)
    original_import = builtins.__import__

    def forbid_provider_import(name, *args, **kwargs):
        if name == "agent" or name.startswith("agent."):
            raise AssertionError("offline smoke path reached the provider import")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", forbid_provider_import)

    assert smoke.main() == smoke.INCONCLUSIVE == 2
    assert "INCONCLUSIVE" in capsys.readouterr().out


def test_live_smoke_record_starts_unrun_with_the_only_authorized_command():
    record = LIVE_RECORD.read_text(encoding="utf-8")

    assert "Status: UNRUN" in record
    assert "$HERMES_HOME/hermes-agent/venv/bin/python scripts/live_drive_smoke.py" in record
    assert "0 = PASS" in record
    assert "1 = FAIL" in record
    assert "2 = INCONCLUSIVE" in record
    assert "separately authorized exit-0 evidence" in record
