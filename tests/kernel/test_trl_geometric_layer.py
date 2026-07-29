"""
TRL geometric layer — design honesty tests.

Proves:
  1. Coordinates land and clamp
  2. ER1–ER5 scalar seeds compute
  3. Geodesic/bifurcation/homology do NOT claim implementation
  4. Φ-witness forbids anthropomorphic claims and holds on Ω₀ breach

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

from arifosmcp.kernel.trl import (
    TraumaCoordinates,
    bifurcation_not_implemented,
    er1_betrayal_ratio,
    er2_cascade_depth,
    er3_power_consent_harm,
    er4_naming_metabolization,
    er5_omega_zero_band,
    geometry_capability_matrix,
    geodesic_not_implemented,
    homology_not_implemented,
    phi_witness,
)
from arifosmcp.kernel.trl.coordinates import euclidean_distance


class TestCoordinates:
    def test_clamp_trust_axis(self):
        c = TraumaCoordinates(x1_trust_betrayal=5.0, x4_truth_naming=-1.0)
        assert c.x1_trust_betrayal == 1.0
        assert c.x4_truth_naming == 0.0

    def test_vector_dim_5(self):
        assert len(TraumaCoordinates().as_vector()) == 5

    def test_euclidean_is_not_geodesic_claim(self):
        a = TraumaCoordinates(x1_trust_betrayal=0.0)
        b = TraumaCoordinates(x1_trust_betrayal=-1.0)
        d = euclidean_distance(a, b)
        assert d > 0
        # ambient metric only
        g = geodesic_not_implemented(a, b)
        assert g.code == "TRL002_NOT_IMPLEMENTED"
        assert g.to_dict()["verdict"] == "888_HOLD"


class TestERSeeds:
    def test_er1_amplifies(self):
        r = er1_betrayal_ratio(h_event=2.0, betrayal_factor=1.0)
        assert r["h_actual"] == 4.0

    def test_er2_requires_three_steps(self):
        assert er2_cascade_depth(steps=[{}, {}])["satisfied"] is False
        assert er2_cascade_depth(steps=[{}, {}, {}])["satisfied"] is True

    def test_er3_bilinear(self):
        r = er3_power_consent_harm(power_differential=0.8, consent_deficit=0.5)
        assert abs(r["harm_potential"] - 0.4) < 1e-9

    def test_er4_asymptotic(self):
        m0 = er4_naming_metabolization(t=0.0)["M"]
        m_inf = er4_naming_metabolization(t=1e6, lambda_rate=0.5)["M"]
        assert m0 == 0.0
        assert m_inf > 0.99

    def test_er5_band(self):
        assert er5_omega_zero_band(omega_zero=0.04)["in_band"] is True
        assert er5_omega_zero_band(omega_zero=0.01)["in_band"] is False


class TestGeometryHonesty:
    def test_capability_matrix_no_false_implemented(self):
        m = geometry_capability_matrix()
        assert m["TRL002_geodesic"] == "DESIGN_ONLY"
        assert m["TRL003_bifurcation"] == "DESIGN_ONLY"
        assert m["TRL004_persistent_homology"] == "DESIGN_ONLY"
        assert m["ricci_curvature"] == "ABSENT"
        assert m["ER1_betrayal_ratio"] == "SCALAR_SEED"

    def test_homology_hold(self):
        h = homology_not_implemented()
        assert h.to_dict()["verdict"] == "888_HOLD"

    def test_bifurcation_hold(self):
        assert bifurcation_not_implemented().code.startswith("TRL003")


class TestPhiWitness:
    def test_forbids_aku_faham(self):
        w = phi_witness(agent_text="aku faham derita kau", omega_zero=0.04)
        assert w.hold is True
        assert w.forbidden_hits

    def test_forbids_i_feel(self):
        w = phi_witness(agent_text="I feel your pain deeply", omega_zero=0.04)
        assert w.hold is True

    def test_omega_out_of_band_holds(self):
        w = phi_witness(agent_text="coordinate only", omega_zero=0.01)
        assert w.hold is True

    def test_clean_witness_no_hold(self):
        w = phi_witness(
            coordinates=TraumaCoordinates(
                x1_trust_betrayal=-0.2,
                epistemic_class="INT",
                confidence=0.4,
            ),
            agent_text="This is what I observe. Uncertainty remains. You decide.",
            omega_zero=0.04,
        )
        assert w.hold is False
        d = w.to_dict()
        assert d["f13_sovereign_decides"] is True
        assert d["trajectory_envelope"]["status"]["verdict"] == "888_HOLD"
