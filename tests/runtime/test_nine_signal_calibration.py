"""Ω calibration pins — 2026-08-14 double-audit fix (FI-003 + external Copilot).

Prior behavior: nine_signal_from_session mapped raw confidence to Ω
(>=0.85 BIJAKSANA / >=0.60 BIJAK / else BANGANG), rewarding claimed
certainty and punishing honest humility. Both directions are wrong:

- Confident + miscalibrated agents earned BIJAKSANA (sophisticated bangang
  wearing the bijaksana label — violates WAJIB #74).
- Calibrated + underconfident agents were branded BANGANG (punishes the F7
  humility the constitution mandates).

Fixed behavior: unwitnessed confidence reports the honest ceiling BIJAK
(WAJIB #30: locally smart, not fully governed). BIJAKSANA on this path
requires kernel-witnessed adjudication (status SEAL/OK), not self-report.
"""

from arifosmcp.tools.nine_signal import nine_signal_from_session

_HEALTHY_SESSION = {
    "session_id": "SEAL-test-0001",
    "actor_verified": True,
    "authority": "FULL",
}


class TestUnwitnessedConfidence:
    def test_high_confidence_cannot_earn_bijaksana(self):
        ns = nine_signal_from_session("OK", _HEALTHY_SESSION, confidence=0.95)
        assert ns["omega"]["state"] == "BIJAK"
        assert ns["omega"]["en"] == "SMART"

    def test_extreme_confidence_still_cannot_earn_bijaksana(self):
        ns = nine_signal_from_session("OK", _HEALTHY_SESSION, confidence=0.999)
        assert ns["omega"]["state"] == "BIJAK"

    def test_low_confidence_is_not_bangang(self):
        ns = nine_signal_from_session("OK", _HEALTHY_SESSION, confidence=0.2)
        assert ns["omega"]["state"] == "BIJAK"

    def test_confidence_value_no_longer_moves_omega(self):
        # The mapping must be flat in confidence: 0.2, 0.6, 0.95 all BIJAK.
        states = {
            nine_signal_from_session("OK", _HEALTHY_SESSION, confidence=c)["omega"]["state"]
            for c in (0.2, 0.6, 0.95)
        }
        assert states == {"BIJAK"}

    def test_basis_records_unwitnessed_confidence(self):
        ns = nine_signal_from_session("OK", _HEALTHY_SESSION, confidence=0.9)
        assert ns["omega"]["basis"] == "unwitnessed_confidence"

    def test_unwitnessed_confidence_cannot_certify_selamat(self):
        # Healthy planes + BIJAK omega -> worst rank 2 -> SABAR, not SELAMAT.
        ns = nine_signal_from_session("OK", _HEALTHY_SESSION, confidence=0.95)
        assert ns["overall"]["state"] == "SABAR"


class TestWitnessedStatusPath:
    def test_seal_status_still_bijaksana(self):
        ns = nine_signal_from_session("SEAL", _HEALTHY_SESSION)
        assert ns["omega"]["state"] == "BIJAKSANA"
        assert ns["omega"]["en"] == "WISE"

    def test_ok_status_still_bijaksana(self):
        ns = nine_signal_from_session("OK", _HEALTHY_SESSION)
        assert ns["omega"]["state"] == "BIJAKSANA"

    def test_hold_status_is_bijak_not_bangang(self):
        ns = nine_signal_from_session("HOLD", _HEALTHY_SESSION)
        assert ns["omega"]["state"] == "BIJAK"

    def test_basis_records_status(self):
        ns = nine_signal_from_session("SEAL", _HEALTHY_SESSION)
        assert ns["omega"]["basis"] == "status"

    def test_healthy_witnessed_session_overall_selamat(self):
        ns = nine_signal_from_session("SEAL", _HEALTHY_SESSION)
        assert ns["overall"]["state"] == "SELAMAT"
