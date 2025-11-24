"""
06_full_apex_runtime_demo.py — Full governed runtime demo
This shows how a prompt flows through:
Ignition → Metrics estimation → APEX PRIME → Cooling Ledger → zkPC
"""

import time

from arifos_core.apex_prime import APEXPrime
from arifos_core.metrics import ConstitutionalMetrics
from arifos_core.memory.cooling_ledger import (
    CoolingLedger, CoolingEntry, CoolingMetrics
)
from arifos_core.memory.zkpc import ZKPC
from arifos_core.ignition import IgnitionLoader


def demo():
    ignition = IgnitionLoader()
    profile = ignition.match_profile("I am Arif.")

    print("=== X-OS PROFILE ===")
    print(profile)

    # Demo metrics (normally computed by your engines)
    metrics = ConstitutionalMetrics(
        truth=0.995,
        delta_s=0.22,
        peace_squared=1.09,
        kappa_r=0.97,
        omega_0=0.041,
        rasa=True,
        amanah=True,
        tri_witness=0.97,
    )

    apex = APEXPrime()
    verdict, reason = apex.judge(metrics, high_stakes=True)

    print("\n=== APEX PRIME VERDICT ===")
    print(verdict, "::", reason)

    # Cooling Ledger
    ledger = CoolingLedger()
    entry = CoolingEntry(
        timestamp=time.time(),
        query="Explain APEX PRIME",
        candidate_output="APEX PRIME is the judiciary of ArifOS.",
        metrics=CoolingMetrics(
            truth=metrics.truth,
            delta_s=metrics.delta_s,
            peace_squared=metrics.peace_squared,
            kappa_r=metrics.kappa_r,
            omega_0=metrics.omega_0,
            rasa=metrics.rasa,
            amanah=metrics.amanah,
            tri_witness=metrics.tri_witness,
            psi=metrics.compute_psi(),
        ),
        verdict=verdict,
        floor_failures=[],
        sabar_reason=None,
        organs={"@RIF": False, "@WELL": False},
    )
    ledger.append(entry)

    print("\nCooling Ledger updated ✔")

    # zkPC Receipt
    zk = ZKPC()
    receipt = zk.make_receipt(
        request="Explain APEX PRIME",
        metrics=entry.to_json_dict()["metrics"],
        floor_pass={"all_floors": True},
        verdict={"verdict": verdict, "reason": reason},
    )
    zk.save_receipt(receipt)

    print("zkPC receipt committed ✔")


if __name__ == "__main__":
    demo()