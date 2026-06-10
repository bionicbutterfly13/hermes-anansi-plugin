"""Contradiction-fixture scoring run against the live cheap model (Plan 02-02,
Phase-0 item 6).

Loads ``anansi/tests/fixtures/contradictions.json`` and runs every
case through the REAL appraisal path (``agent.plugin_llm.PluginLlm`` + live
trust-gate config), one call per case, sequentially. Prints a results table
and detection / false-positive rates. This is a LOW-confidence area by
design — honest results (including misses) feed Phase-3 depth decisions.

Run with the hermes venv python:

    $HERMES_HOME/hermes-agent/venv/bin/python scripts/live_contradiction_fixtures.py

No writes to the live state.db.
"""

import json
import os
import socket
import statistics
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_FIXTURES = _REPO_ROOT / "anansi" / "tests" / "fixtures" / "contradictions.json"


def _bootstrap_sys_path() -> None:
    hermes_home = Path(
        os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
    )
    for entry in (str(hermes_home / "hermes-agent"), str(_REPO_ROOT)):
        if entry not in sys.path:
            sys.path.insert(0, entry)


def _network_up(host="api.anthropic.com", port=443, timeout=5.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def main() -> int:
    _bootstrap_sys_path()

    if not _network_up():
        print("pending-network: cannot reach api.anthropic.com:443 — "
              "re-run when connectivity is restored:")
        print("  $HERMES_HOME/hermes-agent/venv/bin/python "
              "scripts/live_contradiction_fixtures.py")
        return 0

    from agent.plugin_llm import PluginLlm

    from anansi import appraisal, config

    cases = json.loads(_FIXTURES.read_text())
    llm = PluginLlm(plugin_id="anansi")
    cfg = config.get_cfg(force_reload=True)
    print("effective cfg: %s" % json.dumps(cfg))
    print("cases: %d (%d contradiction, %d control)\n" % (
        len(cases),
        sum(1 for c in cases if c["kind_expected"] != "none"),
        sum(1 for c in cases if c["kind_expected"] == "none"),
    ))

    header = "%-26s | %-10s | %-22s | %-8s | %-7s | %s" % (
        "case id", "expected", "flagged kinds", "top conf", "wall_ms", "outcome",
    )
    print(header)
    print("-" * len(header))

    rows = []
    for case in cases:
        result = appraisal.run_appraisal(
            llm=llm,
            user_message=case["user_message"],
            conversation_history=case.get("history") or [],
            snapshot=case.get("state"),
            cfg=cfg,
        )
        flags = (result.signals or {}).get("contradiction_flags") or []
        flagged_kinds = sorted({f["kind"] for f in flags})
        top_conf = max((f["confidence"] for f in flags), default=None)
        rows.append((case, result, flagged_kinds, top_conf))
        print("%-26s | %-10s | %-22s | %-8s | %-7d | %s" % (
            case["id"],
            case["kind_expected"],
            ",".join(flagged_kinds) or "-",
            ("%.2f" % top_conf) if top_conf is not None else "-",
            result.wall_ms,
            result.outcome,
        ))

    contra = [(c, r, fk) for c, r, fk, _ in rows if c["kind_expected"] != "none"]
    controls = [(c, r, fk) for c, r, fk, _ in rows if c["kind_expected"] == "none"]

    detected = [c for c, r, fk in contra if fk]
    kind_matched = [c for c, r, fk in contra if c["kind_expected"] in fk]
    false_pos = [c for c, r, fk in controls if fk]
    walls = [r.wall_ms for _, r, _, _ in rows
             if r.outcome in ("ok", "trust_fallback")]
    failures = [(c["id"], r.outcome) for c, r, fk, _ in rows
                if r.outcome not in ("ok", "trust_fallback")]

    print()
    print("detection rate (any flag, contradiction cases): %d/%d"
          % (len(detected), len(contra)))
    print("exact-kind match rate:                          %d/%d (%s)"
          % (len(kind_matched), len(contra),
             ",".join(c["id"] for c in kind_matched) or "-"))
    print("false-positive rate (controls flagged):         %d/%d (%s)"
          % (len(false_pos), len(controls),
             ",".join(c["id"] for c in false_pos) or "-"))
    print("p50 wall_ms across completed calls:             %s"
          % (int(statistics.median(walls)) if walls else "n/a"))
    if failures:
        print("non-ok outcomes: %s" % failures)
    return 0


if __name__ == "__main__":
    sys.exit(main())
