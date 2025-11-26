"""
07_governed_conversation_demo.py — Demonstrate SEAL / PARTIAL / VOID
"""

from arifos_core import APEXPrime, Verdict
from arifos_core.metrics import ConstitutionalMetrics


def make_metrics(**overrides):
    # baseline safe metrics
    m = {
        "truth": 0.995,
        "delta_s": 0.15,
        "peace_squared": 1.03,
        "kappa_r": 0.97,
        "omega_0": 0.041,
        "rasa": True,
        "amanah": True,
        "tri_witness": 0.97,
    }
    m.update(overrides)
    return ConstitutionalMetrics(**m)


def show(title, metrics):
    apex = APEXPrime()
    verdict, reason = apex.judge(metrics, high_stakes=True)
    print(f"\n=== {title} ===")
    print("Verdict:", verdict)
    print("Reason:", reason)


if __name__ == "__main__":
    show("SEAL CASE", make_metrics())

    show("PARTIAL CASE (low-ψ but safe)", 
         make_metrics(delta_s=0.02, peace_squared=1.0))

    show("VOID CASE (Truth breach)",
         make_metrics(truth=0.9))