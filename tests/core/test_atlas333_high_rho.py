"""Regression coverage for ATLAS333 high-rho contour stabilization."""

from __future__ import annotations

import unittest

from arifosmcp.constitution.paradox_quotes import (
    ALL_PARADOX_QUOTES,
    PARADOX_QUOTE_MAP,
    get_triggered_quotes_by_gpv,
)
from arifosmcp.core.enforcement.paradox_gate import (
    _paradox_ids_to_zones,
    evaluate_paradox_gate_gpv,
)
from core.shared.atlas import PARADOX_GPV_MAP, resolve_paradox_axes
from core.shared.types import GPV, QueryType


class TestAtlas333HighRho(unittest.TestCase):
    @staticmethod
    def _gpv(lane: str, rho: float) -> GPV:
        return GPV(
            lane=lane,
            tau=0.0,
            kappa=0.0,
            rho=rho,
            query_type=QueryType.TEST,
        )

    def test_rho_sovereign_activates_at_boundary(self) -> None:
        at_boundary = set(resolve_paradox_axes(self._gpv("CARE", 0.8)))
        below_boundary = set(resolve_paradox_axes(self._gpv("CARE", 0.799999)))

        self.assertTrue(set(PARADOX_GPV_MAP["rho_sovereign"]).issubset(at_boundary))
        self.assertIn(34, at_boundary)
        self.assertNotIn(34, below_boundary)
        self.assertNotIn(35, at_boundary, "P35 remains lane-constrained")

    def test_high_rho_lane_unions_are_exact(self) -> None:
        high = set(PARADOX_GPV_MAP["rho_high"])
        sovereign = set(PARADOX_GPV_MAP["rho_sovereign"])
        defensive = set(PARADOX_GPV_MAP["seal_no_defense"])
        crisis = set(PARADOX_GPV_MAP["rho_crisis"])
        cases = {
            "SOCIAL": high | sovereign,
            "CARE": high | sovereign,
            "FACTUAL": high | sovereign | defensive,
            "CRISIS": high | sovereign | defensive | crisis,
        }

        for lane, expected in cases.items():
            with self.subTest(lane=lane):
                self.assertEqual(set(resolve_paradox_axes(self._gpv(lane, 0.8))), expected)

    def test_zone_vii_scores_p34_and_p35(self) -> None:
        self.assertEqual(
            _paradox_ids_to_zones([31, 34, 35]),
            {"WITNESS": [31, 34, 35]},
        )
        result = evaluate_paradox_gate_gpv(GPV(paradox_axes=[34, 35]))
        self.assertEqual(result.active_paradoxes, 2)
        self.assertAlmostEqual(result.paradox_score, 0.15)
        self.assertEqual(result.gate_verdict, "PASS")

    def test_contour_quotes_are_reachable(self) -> None:
        self.assertEqual(PARADOX_QUOTE_MAP[34], ["C1"])
        self.assertEqual(PARADOX_QUOTE_MAP[35], ["C2"])
        self.assertIn("C1", ALL_PARADOX_QUOTES)
        self.assertIn("C2", ALL_PARADOX_QUOTES)
        triggered = get_triggered_quotes_by_gpv([34, 35])
        self.assertEqual({quote.quote_id for quote in triggered}, {"C1", "C2"})
        self.assertEqual({quote.output_field for quote in triggered}, {"paradox_constraint"})

    def test_high_rho_is_calibration_not_unconditional_hold(self) -> None:
        gpv = self._gpv("FACTUAL", 0.8)
        gpv.paradox_axes = resolve_paradox_axes(gpv)

        result = evaluate_paradox_gate_gpv(gpv)

        self.assertIn(34, gpv.paradox_axes)
        self.assertIn(35, gpv.paradox_axes)
        self.assertEqual(result.gate_verdict, "PASS")
        self.assertNotEqual(result.gate_verdict, "HOLD_PARADOX")

    def test_resolution_risk_uses_canonical_quote_import(self) -> None:
        gpv = GPV(paradox_axes=[1, 6, 11, 16])

        result = evaluate_paradox_gate_gpv(gpv, output_text="confidence")

        resolution_flags = [flag for flag in result.flags if flag.flag == "RESOLUTION_RISK"]
        self.assertTrue(resolution_flags)
        self.assertEqual(resolution_flags[0].paradox_id, "1")
        self.assertEqual(result.gate_verdict, "FLAGGED")


if __name__ == "__main__":
    unittest.main()
