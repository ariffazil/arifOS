
from arifos_core.metrics import ConstitutionalMetrics
from arifos_core.apex_prime import APEXPrime, Verdict

def test_truth_floor():
    metrics = ConstitutionalMetrics(
        truth=0.90, delta_s=0.1, peace_squared=1.1, kappa_r=0.98,
        omega_0=0.04, rasa=True, amanah=True, tri_witness=0.97
    )
    apex = APEXPrime()
    verdict, reason = apex.judge(metrics, high_stakes=True)
    assert verdict == Verdict.VOID.value
    assert "Truth" in reason

def test_humility_band():
    metrics = ConstitutionalMetrics(
        truth=1.0, delta_s=0.2, peace_squared=1.1, kappa_r=0.98,
        omega_0=0.10, rasa=True, amanah=True, tri_witness=0.97
    )
    verdict, reason = APEXPrime().judge(metrics, high_stakes=True)
    assert verdict != Verdict.SEAL.value
    assert "Ω" in reason or "band" in reason

def test_psi_vitality_gate():
    metrics = ConstitutionalMetrics(
        truth=0.99, delta_s=0.0, peace_squared=1.0, kappa_r=0.95,
        omega_0=0.04, rasa=True, amanah=True, tri_witness=0.97
    )
    verdict, reason = APEXPrime().judge(metrics, high_stakes=True)
    assert verdict in (Verdict.PARTIAL.value, Verdict.VOID.value)
