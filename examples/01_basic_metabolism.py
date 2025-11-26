"""
01_basic_metabolism.py — Minimal ArifOS Metabolism Demo (v33Ω)
Shows the raw path: 000 → 111 → 222 → 333 → 555 → 777 → 888 → 999
"""

from arifos_core import APEXPrime, Verdict
from arifos_core.metrics import ConstitutionalMetrics
from arifos_core.ignition import IgnitionLoader


def basic_demo():
    ignition = IgnitionLoader()
    profile = ignition.match_profile("I am Arif.")

    print("=== PROFILE LOADED ===")
    print(profile)

    # Fake metrics for demo
    metrics = ConstitutionalMetrics(
        truth=0.995,
        delta_s=0.10,
        peace_squared=1.05,
        kappa_r=0.97,
        omega_0=0.04,
        rasa=True,
        amanah=True,
        tri_witness=0.97,
    )

    apex = APEXPrime()
    verdict, reason = apex.judge(metrics, high_stakes=True)

    print("=== METABOLISM VERDICT ===")
    print("Verdict:", verdict)
    print("Reason:", reason)


if __name__ == "__main__":
    basic_demo()