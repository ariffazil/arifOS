import unittest
from arifos_core import Metrics, apex_review

class TestApexReview(unittest.TestCase):
    def test_seal_when_all_floors_pass(self):
        metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.04,
            amanah=True,
            tri_witness=1.0,
            psi=1.0,
        )
        verdict = apex_review(metrics, high_stakes=True)
        self.assertEqual(verdict, "SEAL")

    def test_partial_when_soft_floors_fail(self):
        metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=0.9,   # fails Peace²
            kappa_r=0.95,
            omega_0=0.04,
            amanah=True,
            tri_witness=1.0,
            psi=1.0,
        )
        verdict = apex_review(metrics, high_stakes=True)
        self.assertEqual(verdict, "PARTIAL")

    def test_void_when_hard_floors_fail(self):
        metrics = Metrics(
            truth=0.95,   # fails Truth
            delta_s=-0.1, # fails ΔS
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.02, # fails Ω₀
            amanah=False, # fails Amanah
            tri_witness=1.0,
            psi=0.9,      # fails Ψ
        )
        verdict = apex_review(metrics, high_stakes=True)
        self.assertEqual(verdict, "VOID")

if __name__ == "__main__":
    unittest.main()
