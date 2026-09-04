"""Narrow MCP surface for consent-based 1:1 face verification.

ONLY four tools. No camera access, no "who is this" (1:N) path, no
embedding/image ever returned to the LLM. Structured decisions only.

Run (stdio):  python3 -m arifosmcp.biometric.server
Enroll token: ARIFOS_BIOMETRIC_ENROLL_TOKEN env (sovereign-gated).
888 HOLD: deployment beyond Arif's personal local prototype requires
explicit sovereign authorization (other people / surveillance / 1:N /
irreversible access are OUT OF SCOPE of this server).
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from arifosmcp.biometric.face_verify import FaceVerifyService

mcp = FastMCP("arifos-biometric-verify")
_svc = FaceVerifyService()


@mcp.tool()
def verify_face(
    claimed_subject_id: str,
    purpose: str,
    session_id: str,
    device_id: str,
    capture_nonce: str,
    face_embedding: list[float],
    liveness: str,
    face_quality: dict,
    user_triggered: bool = True,
) -> dict:
    """1:1 consent-based verification of a CLAIMED subject.

    Edge gateway supplies embedding + liveness + quality (no raw frames here).
    Returns decision/assurance/reason_code (+assertion when PASS).
    NEVER answers "who is this?" — claimed_subject_id is required input.
    """
    r = _svc.verify(
        claimed_subject_id=claimed_subject_id,
        purpose=purpose if purpose in ("session_unlock", "sensitive_tool_stepup") else "sensitive_tool_stepup",
        session_id=session_id, device_id=device_id, capture_nonce=capture_nonce,
        embedding=face_embedding, liveness=liveness, quality=face_quality,
        user_triggered=user_triggered,
    )
    return {"decision": r.decision, "assurance": r.assurance,
            "reason_code": r.reason_code, "assertion_id": r.assertion_id,
            "expires_at": r.expires_at}


@mcp.tool()
def consume_face_assertion(assertion_id: str, session_id: str,
                           device_id: str, purpose: str) -> dict:
    """Downstream gate: consume a PASS assertion (single-use, bound, short TTL)."""
    return {"authorized": _svc.consume_assertion(
        assertion_id, session_id=session_id, device_id=device_id, purpose=purpose)}


@mcp.tool()
def enroll_face(subject_id: str, face_embedding: list[float],
                consent_note: str, sovereign_token: str) -> dict:
    """Sovereign-gated enrollment with explicit consent record."""
    return _svc.enroll(subject_id, face_embedding, consent_note,
                       sovereign_token=sovereign_token)


@mcp.tool()
def revoke_face(subject_id: str, sovereign_token: str) -> dict:
    """One-command revocation (privacy right; also used by deletion drill)."""
    return _svc.revoke(subject_id, sovereign_token=sovereign_token)


if __name__ == "__main__":
    mcp.run()
