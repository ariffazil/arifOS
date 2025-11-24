
from arifos_core.metrics import ConstitutionalMetrics

def test_delta_s_increases_with_clarity():
    m = ConstitutionalMetrics(
        truth=1.0, delta_s=0.5, peace_squared=1.05,
        kappa_r=0.97, omega_0=0.04, rasa=True, amanah=True,
        tri_witness=0.97
    )
    assert m.delta_s >= 0

def test_psi_calculation_monotonicity():
    m1 = ConstitutionalMetrics(
        truth=1.0, delta_s=0.1, peace_squared=1.05,
        kappa_r=0.97, omega_0=0.04, rasa=True, amanah=True,
        tri_witness=0.97
    )
    m2 = ConstitutionalMetrics(
        truth=1.0, delta_s=0.2, peace_squared=1.10,
        kappa_r=0.97, omega_0=0.04, rasa=True, amanah=True,
        tri_witness=0.97
    )
    assert m2.compute_psi() > m1.compute_psi()
