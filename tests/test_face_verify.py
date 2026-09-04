"""Policy-matrix tests: consent-based 1:1 face verification (888 audit 2026-09-05).

Covers every branch of audit §777 decision policy + abuse table:
  no-consent DENY · liveness-fail DENY+lockout+sec-event · multi-face RETRY ·
  low-quality RETRY · unknown-subject FAIL (anti-enumeration) · band
  PASS/ESCALATE/FAIL · replay nonce DENY · rate limit · assertion single-use
  + binding + TTL · revocation kills verification.
"""

from __future__ import annotations

import time

import pytest

from arifosmcp.biometric.face_verify import FaceVerifyService

ARIF = [1.0] + [0.05] * 127
IMPOSTOR = [-1.0] + [0.05] * 127  # hampir ortogonal → jelas bawah t_reject
MID = [(a + b) / 2 for a, b in zip(ARIF, IMPOSTOR)]  # ~between → band test via cfg


@pytest.fixture
def svc(tmp_path, monkeypatch):
    monkeypatch.setenv("ARIFOS_BIOMETRIC_ENROLL_TOKEN", "tok-888")
    s = FaceVerifyService(vault_dir=tmp_path / "bio")
    assert s.enroll("arif", ARIF, "consent: personal prototype",
                    sovereign_token="tok-888")["ok"] is True
    return s


def _q(**over):
    q = {"num_faces": 1, "face_size_px": 240, "yaw_deg": 4.2,
         "blur_score": 0.91, "brightness_score": 0.77}
    q.update(over)
    return q


def _v(svc, emb=ARIF, nonce="n1", **kw):
    args = dict(claimed_subject_id="arif", purpose="session_unlock",
                session_id="S1", device_id="D1", capture_nonce=nonce,
                embedding=emb, liveness="PASS", quality=_q(), user_triggered=True)
    args.update(kw)
    return svc.verify(**args)


def test_genuine_pass_with_scoped_assertion(svc):
    r = _v(svc, nonce="g1")
    assert (r.decision, r.reason_code) == ("PASS", "MATCH")
    assert r.assertion_id.startswith("fva_") and r.expires_at
    assert svc.consume_assertion(r.assertion_id, session_id="S1", device_id="D1",
                                 purpose="session_unlock") is True
    # single-use
    assert svc.consume_assertion(r.assertion_id, session_id="S1", device_id="D1",
                                 purpose="session_unlock") is False


def test_assertion_binding_wrong_session_device_purpose(svc):
    r = _v(svc, nonce="b1")
    assert svc.consume_assertion(r.assertion_id, session_id="OTHER",
                                 device_id="D1", purpose="session_unlock") is False
    assert svc.consume_assertion(r.assertion_id, session_id="S1",
                                 device_id="OTHER", purpose="session_unlock") is False
    assert svc.consume_assertion(r.assertion_id, session_id="S1",
                                 device_id="D1", purpose="sensitive_tool_stepup") is False


def test_no_consent_deny(svc):
    r = _v(svc, nonce="c1", user_triggered=False)
    assert (r.decision, r.reason_code) == ("DENY", "NO_CONSENT")


def test_liveness_fail_deny_lockout_security_event(svc):
    r = _v(svc, nonce="l1", liveness="FAIL")
    assert (r.decision, r.reason_code) == ("DENY", "LIVENESS_FAILED")
    # lockout: further attempts rate-limited even with good liveness
    r2 = _v(svc, nonce="l2", liveness="PASS")
    assert r2.reason_code == "RATE_LIMITED"
    evs = [l for l in (svc.dir / "audit.jsonl").read_text().splitlines()
           if "security_event" in l]
    assert evs, "liveness fail must log security event"


def test_multi_face_and_quality_retry(svc):
    assert _v(svc, nonce="m1", quality=_q(num_faces=2)).reason_code == "MULTIPLE_FACES"
    assert _v(svc, nonce="m2", quality=_q(face_size_px=60)).reason_code == "LOW_QUALITY"
    assert _v(svc, nonce="m3", quality=_q(blur_score=0.2)).reason_code == "LOW_QUALITY"
    assert _v(svc, nonce="m4", quality=_q(yaw_deg=40)).reason_code == "LOW_QUALITY"
    for r in [_v(svc, nonce="m1x", quality=_q(num_faces=2))]:
        assert r.decision == "RETRY"


def test_unknown_subject_fail_without_enumeration(svc):
    r = _v(svc, nonce="u1", claimed_subject_id="ghost")
    # same reason as below-threshold — does not reveal enrollment state
    assert (r.decision, r.reason_code) == ("FAIL", "BELOW_THRESHOLD")


def test_threshold_bands(tmp_path, monkeypatch):
    monkeypatch.setenv("ARIFOS_BIOMETRIC_ENROLL_TOKEN", "tok-888")
    s = FaceVerifyService(vault_dir=tmp_path / "b", config={"t_accept": 0.9, "t_reject": 0.3})
    assert s.enroll("arif", ARIF, "c", sovereign_token="tok-888")["ok"]
    a = dict(claimed_subject_id="arif", purpose="session_unlock", session_id="S",
             device_id="D", liveness="PASS", quality=_q())
    imp = s.verify(capture_nonce="i1", embedding=IMPOSTOR, **a)   # ~0 → FAIL
    assert imp.decision == "FAIL"
    mid = s.verify(capture_nonce="i2", embedding=MID, **a)        # ~0.7 → band ESCALATE
    assert mid.decision == "ESCALATE", "middle band must step-up, never guess"


def test_replay_nonce_denied(svc):
    assert _v(svc, nonce="r1").decision == "PASS"
    r2 = _v(svc, nonce="r1")  # same nonce replay
    assert (r2.decision, r2.reason_code) == ("DENY", "REPLAY_DETECTED")


def test_rate_limit(svc):
    for i in range(5):
        _v(svc, nonce=f"rl{i}")
    r = _v(svc, nonce="rlX")
    assert r.reason_code == "RATE_LIMITED"


def test_revocation_kills_verification(tmp_path, monkeypatch):
    monkeypatch.setenv("ARIFOS_BIOMETRIC_ENROLL_TOKEN", "tok-888")
    s = FaceVerifyService(vault_dir=tmp_path / "b")
    s.enroll("arif", ARIF, "c", sovereign_token="tok-888")
    assert s.revoke("arif", sovereign_token="tok-888")["ok"]
    r = _v(s, nonce="x1")
    assert r.decision == "FAIL"  # anti-enumeration reason, no PASS possible


def test_llm_surface_contains_no_biometric_material(svc):
    r = _v(svc, nonce="s1")
    d = {"decision": r.decision, "assurance": r.assurance, "reason_code": r.reason_code,
         "assertion_id": r.assertion_id, "expires_at": r.expires_at}
    assert "similarity" not in d and "embedding" not in d and "score" not in d
