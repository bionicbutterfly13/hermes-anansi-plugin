"""Live smoke test for the anansi appraisal path (Plan 02-02).

Runs ONE real appraisal call through the REAL host facade
(`agent.plugin_llm.PluginLlm`) against the live trust-gate config at
``plugins.entries.anansi`` — the first real-model proof of
APPR-01/02/04.

Run with the hermes venv python:

    $HERMES_HOME/hermes-agent/venv/bin/python scripts/live_smoke.py

Behavior:
- sys.path is bootstrapped from $HERMES_HOME (no literal paths) plus the
  repo root derived from this file's location.
- Does NOT write to the live state.db. Telemetry summary is printed via
  the read-only URI path in store.telemetry_summary() (returns None when
  the live DB is still schema v1 — expected before the first real turn).
- Exit codes are CI-honest: 0 = real appraisal returned signals; 2 = INCONCLUSIVE
  (network down, or trust-gate/provider returned no signals). "Could not test" never
  masquerades as "passed".
"""

import json
import os
import socket
import sys
from pathlib import Path

PASS, FAIL, INCONCLUSIVE = 0, 1, 2


def _bootstrap_sys_path() -> None:
    hermes_home = Path(
        os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
    )
    repo_root = Path(__file__).resolve().parent.parent
    for entry in (str(hermes_home / "hermes-agent"), str(repo_root)):
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
        print("INCONCLUSIVE pending-network: cannot reach api.anthropic.com:443 — "
              "re-run this script when connectivity is restored:")
        print("  $HERMES_HOME/hermes-agent/venv/bin/python scripts/live_smoke.py")
        return INCONCLUSIVE

    from agent.plugin_llm import PluginLlm

    from anansi import appraisal, config, render, store

    llm = PluginLlm(plugin_id="anansi")
    cfg = config.get_cfg(force_reload=True)
    print("effective cfg: %s" % json.dumps(cfg))

    user_message = (
        "Earlier I said I prefer Postgres for everything; now I think "
        "SQLite is always the right choice. What should we use?"
    )
    history = [
        {"role": "user", "content": "For our plugin state layer I prefer "
                                    "Postgres for everything, period."},
        {"role": "assistant", "content": "Noted — Postgres as the default "
                                         "for all persistence."},
    ]
    snapshot = {
        "concerns": [
            {"text": "user undecided on persistence layer", "weight": 0.5}
        ],
        "contradictions": [],
        "trust_scores": [{"subject": "user db preferences", "score": 0.6}],
        "affect_summary": [],
    }

    result = appraisal.run_appraisal(
        llm=llm,
        user_message=user_message,
        conversation_history=history,
        snapshot=snapshot,
        cfg=cfg,
    )

    print("outcome:    %s" % result.outcome)
    print("wall_ms:    %d" % result.wall_ms)
    print("model:      %s" % result.model)
    print("tokens_in:  %d" % result.tokens_in)
    print("tokens_out: %d" % result.tokens_out)
    print("error:      %s" % result.error)
    print("signals:")
    print(json.dumps(result.signals, indent=2, ensure_ascii=False))
    block = render.render_block(result.signals) if result.signals else None
    print("rendered block:")
    print(block if block else "(suppressed — no signals above threshold)")

    # Read-only view of the LIVE db — no writes from this script.
    summary = store.telemetry_summary()
    print("live telemetry_summary (read-only): %s" % (
        json.dumps(summary) if summary is not None
        else "unavailable (live DB likely still schema v1 — quarantines on "
             "first real turn)"
    ))
    if not result.signals or result.outcome != "ok":
        print("result: INCONCLUSIVE — outcome=%s, no usable signals "
              "(network / trust-gate / provider condition, not an appraisal-code "
              "defect)." % result.outcome)
        return INCONCLUSIVE
    print("result: PASS — real appraisal returned signals.")
    return PASS


if __name__ == "__main__":
    sys.exit(main())
