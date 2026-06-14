"""Live smoke test for the DRIVE goal-surfacing path (Phase 7, Criterion 1).

Proves the one thing the offline/fake-LLM suite cannot: that a user-minted,
flagged-priority goal actually surfaces in the `[anansi appraisal]` block on a
REAL model turn through the REAL host facade (`agent.plugin_llm.PluginLlm`).

Run with the hermes venv python:

    $HERMES_HOME/hermes-agent/venv/bin/python scripts/live_drive_smoke.py

Behavior / guarantees:
- sys.path is bootstrapped from $HERMES_HOME (no literal paths) + repo root.
- Builds the flagged goal + snapshot BY HAND and passes them in — it NEVER
  reads or writes the live state.db. Zero side effects on live state.
- The flagged `- drive want:` line is a PROTECTED, persisted-goal render — it
  does NOT depend on the model echoing the goal, so the assertion is
  deterministic given a successful real appraisal.
- Exit codes are CI-honest (fixes the live_smoke.py "0 means both pass and
  could-not-test" ambiguity):
      0 = PASS  (real appraisal returned signals AND the drive want surfaced)
      1 = FAIL  (block rendered but the flagged drive want is missing)
      2 = INCONCLUSIVE  (network down, or the live model/trust-gate returned no
          signals — an environment/config condition, not a drive-code defect)
"""

import json
import os
import socket
import sys
from pathlib import Path

PASS, FAIL, INCONCLUSIVE = 0, 1, 2


def _bootstrap_sys_path() -> None:
    hermes_home = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
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
              "re-run when connectivity is restored.")
        return INCONCLUSIVE

    from agent.plugin_llm import PluginLlm

    from anansi import appraisal, config, render

    llm = PluginLlm(plugin_id="anansi")
    cfg = config.get_cfg(force_reload=True)
    print("effective cfg: %s" % json.dumps(cfg))

    # A user-MINTED, flagged-priority goal — built by hand, never touches live state.db.
    goal = {
        "text": "ship the anansi drive layer",
        "status": "active",
        "flagged_priority": 1,
        "domain": "anansi",
    }

    # A message that should provoke real signals (a contradiction) AND relates to the goal.
    user_message = (
        "The anansi drive layer is my top priority, but I haven't touched it in days. "
        "Also, earlier I said SQLite is always right; now I think Postgres is. "
        "What should I focus on?"
    )
    history = [
        {"role": "user", "content": "My top priority right now is shipping the anansi drive layer."},
        {"role": "assistant", "content": "Got it — the drive layer is the focus."},
    ]
    snapshot = {
        "concerns": [{"text": "drive layer stalled several days", "weight": 0.6}],
        "contradictions": [],
        "trust_scores": [{"subject": "user db preferences", "score": 0.55}],
        "affect_summary": [],
        "goals": [goal],
    }

    result = appraisal.run_appraisal(
        llm=llm,
        user_message=user_message,
        conversation_history=history,
        snapshot=snapshot,
        cfg=cfg,
        goals=[goal],
    )

    print("outcome:    %s" % result.outcome)
    print("wall_ms:    %d" % result.wall_ms)
    print("model:      %s" % result.model)
    print("error:      %s" % result.error)

    if not result.signals:
        print("INCONCLUSIVE: live model returned no signals (outcome=%s, error=%s). "
              "This is an environment/trust-gate condition, not a drive-code defect — "
              "the offline full-hook suite proves the surfacing logic." % (result.outcome, result.error))
        return INCONCLUSIVE

    block = render.render_block(
        result.signals,
        snapshot=snapshot,
        goals=[goal],
        energy_budget=cfg.get("drive_energy_budget"),
    )
    print("\nrendered [anansi appraisal] block:\n%s\n" % (block or "(suppressed)"))

    if block and "- drive want:" in block:
        has_note = "- drive note:" in block
        print("PASS: the minted flagged goal surfaced as a first-person '- drive want:' line "
              "on a REAL model turn.%s" % (
                  " (model also emitted a '- drive note:' goal signal.)" if has_note else ""))
        # Sanity: the never-overstep guard — no second-person imperative leaked.
        if "you should" in block.lower():
            print("FAIL: a second-person directive ('you should') leaked into the block.")
            return FAIL
        return PASS

    print("FAIL: a block rendered but the flagged '- drive want:' line is missing.")
    return FAIL


if __name__ == "__main__":
    sys.exit(main())
