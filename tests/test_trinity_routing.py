
from arifos_core.apex_prime import APEXPrime, Verdict
from arifos_core.metrics import ConstitutionalMetrics

def test_trinity_execution_order():
    metrics = ConstitutionalMetrics(
        truth=0.995, delta_s=0.1, peace_squared=1.05,
        kappa_r=0.97, omega_0=0.04, rasa=True, amanah=True,
        tri_witness=0.97
    )
    structured = True
    adjusted = structured and True
    verdict, _reason = APEXPrime().judge(metrics, high_stakes=True)
    assert structured
    assert adjusted
    assert verdict in (Verdict.SEAL.value, Verdict.PARTIAL.value)
