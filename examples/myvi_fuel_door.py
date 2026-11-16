"""The Myvi incident, encoded.

Incident (2026-11-12, Petron Sungai Besi): a driver spent 10 minutes at
the pump because the machine knew the fuel-door release and never said
it. The car's second failure: it refused to lock with the boot ajar —
and explained nothing.

This example shows the arifOS answer: a vehicle agent that EXPLAINS.
Run:  python3 examples/myvi_fuel_door.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from arifos_av import (
    AVGovernanceKernel, Capability, DriveAction, Evidence,
    SpeechAct, Tier, BoundedLadder,
)


def scenario_fuel_door(kernel):
    """Driver lost at the pump. The machine must speak."""
    action = DriveAction(
        name="explain_fuel_door",
        tier=Tier.T1,
        target="hmi",
        explain="Fuel door is push-open, rear-left; boot is ajar and blocks central locking.",
    )
    cap = Capability("explain_fuel_door", True, True, True, True)
    out = kernel.propose(action, cap, SpeechAct.DIRECTIVE,
                         evidence=[Evidence("OBS", "door_state=ajar"),
                                   Evidence("OBS", "driver_searching=600s")])
    return out, action.explain


def scenario_lock_refused(kernel):
    """Lock refused. Explanation first, action second."""
    action = DriveAction(
        name="central_lock",
        tier=Tier.T1,
        target="body_controller",
        explain="Central lock refused because the boot is not fully closed. Close the boot until it clicks, then lock.",
    )
    cap = Capability("central_lock", True, True, True, True)
    return kernel.propose(action, cap, SpeechAct.DIRECTIVE,
                          evidence=[Evidence("OBS", "boot_ajar=true")])


def main():
    kernel = AVGovernanceKernel(judge_name="vehicle-witness",
                                sovereign_name="driver")
    out, explanation = scenario_fuel_door(kernel)
    print("[1] fuel door  ->", out["status"])
    print("    machine says:", explanation)

    out2 = scenario_lock_refused(kernel)
    print("[2] central lock ->", out2["status"])
    print("    machine says:", "boot ajar -> close boot first")

    lad = BoundedLadder(
        primary=lambda t: None,
        alternative=lambda t: None,
        forensic=lambda t: None,
    )
    r = lad.run("resolve unknown sensor")
    print("[3] edge ladder ->", r.status, "|", r.note)
    print("ledger chain valid:", kernel.ledger.verify_chain())


if __name__ == "__main__":
    main()
