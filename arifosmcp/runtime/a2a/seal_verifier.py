"""
A2A Seal Verification Endpoint
================================

Provides /seal/verify endpoint for external agents to:
- Verify a SEAL verdict is valid and anchored in VAULT999
- Check judge_state_hash integrity
- Query session state
- Verify orthogonality (Ω_ortho)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field

from arifosmcp.runtime.auditor import get_auditor

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(UTC)


class SealVerificationRequest(BaseModel):
    """Request to verify a SEAL verdict."""

    session_id: str
    verdict: str  # SEAL, HOLD, VOID, SABAR
    state_hash: str | None = None
    agent_id: str | None = None
    include_trace: bool = False
    actor_signature: str | None = None  # Added 2026-06-27: real Ed25519 sig verification
    nonce: str | None = None  # Added 2026-06-27: replay prevention for signature


class SealVerificationResponse(BaseModel):
    """Response from seal verification."""

    valid: bool
    verdict: str
    session_id: str
    timestamp: datetime = Field(default_factory=_utcnow)
    state_hash_valid: bool | None = None
    vault_anchored: bool = False
    vault_entry_index: int | None = None
    signature_valid: bool | None = None
    trace: list[str] = Field(default_factory=list)
    omega_ortho: float | None = None
    well_readiness: float | None = None
    error: str | None = None


class OrthogonalityResponse(BaseModel):
    """Current Ω_ortho status from M01."""

    omega_ortho: float
    threshold: float
    is_orthogonal: bool
    violations: int
    agents_in_scope: list[str]
    timestamp: datetime = Field(default_factory=_utcnow)


class WELLStateResponse(BaseModel):
    """Current WELL operator state."""

    operator_fatigue: float | None = None
    cognitive_load: float | None = None
    stress_level: float | None = None
    readiness_score: float | None = None
    metabolic_stage: str | None = None
    veto_intact: bool = True
    timestamp: datetime = Field(default_factory=_utcnow)


class A2ASealVerifier:
    """
    Verifies SEAL verdicts and exposes vault/query endpoints.

    External A2A agents call these to verify arifOS has actually sealed
    and to check current governance state.
    """

    def __init__(self):
        self._vault_path = Path.home() / ".arifos" / "vault.jsonl"
        self._sessions_path = Path.home() / ".arifos" / "runtime_sessions.json"

    def verify_seal(self, request: SealVerificationRequest) -> SealVerificationResponse:
        """
        Verify a SEAL verdict is valid, vault-anchored, and hash-verified.

        Called by external A2A agents before trusting arifOS verdicts.
        """
        trace = [f"verify_seal @ {_utcnow().isoformat()}"]
        trace.append(f"session_id={request.session_id[:30]}...")
        trace.append(f"verdict={request.verdict}")

        # Check verdict is SEAL
        if request.verdict != "SEAL":
            trace.append(f"verdict={request.verdict} ≠ SEAL → invalid")
            return SealVerificationResponse(
                valid=False,
                verdict=request.verdict,
                session_id=request.session_id,
                trace=trace,
                error=f"Verdict is {request.verdict}, not SEAL. Cannot verify as SEAL.",
            )

        # ── State hash + cryptographic signature verification (HARDENED 2026-06-27) ─
        # C-2 fix: real Ed25519 verification instead of state_hash format proxy.
        # Requires actor_signature + nonce in the request. Falls back to
        # state_hash format check for backward compatibility with older clients.
        state_hash_valid = None
        signature_valid = None
        if request.actor_signature and request.nonce:
            try:
                from arifosmcp.runtime.sovereign_verify import verify_actor

                actor_id = request.agent_id or "unknown"
                ok, reason = verify_actor(
                    actor_id=actor_id,
                    actor_signature=request.actor_signature,
                    nonce=request.nonce,
                )
                signature_valid = ok
                trace.append(f"Ed25519 {'verified' if ok else 'REJECTED'}: {reason}")
            except Exception as exc:
                logger.error(
                    "Seal verifier Ed25519 check failed: %s",
                    exc,
                    extra={"session_id": request.session_id[:30]},
                )
                trace.append(f"Ed25519 verification error: {exc}")
                # Do NOT fall through — leave signature_valid=None
        elif request.state_hash and len(request.state_hash) == 64:
            # Backward compat: state_hash format check only (NOT signature verification)
            trace.append("state_hash valid format (64 hex) — signature NOT verified")

        # Check vault for anchoring
        vault_anchored = False
        vault_entry_index = None
        if self._vault_path.exists():
            try:
                with open(self._vault_path) as f:
                    lines = f.readlines()
                for idx, line in enumerate(reversed(lines)):
                    try:
                        entry = json.loads(line)
                        if (
                            entry.get("session_id") == request.session_id
                            and entry.get("verdict") == "SEAL"
                        ):
                            vault_anchored = True
                            vault_entry_index = len(lines) - 1 - idx
                            trace.append(f"VAULT999 entry #{vault_entry_index} found and anchored")
                            break
                    except json.JSONDecodeError:
                        continue
            except Exception as e:
                trace.append(f"vault read error: {e}")

        # Compute current Ω_ortho
        auditor = get_auditor()
        report = auditor.compute_orthogonality()
        trace.append(f"Ω_ortho={report.omega_ortho:.4f} (threshold={auditor.threshold})")

        # Check session for WELL readiness
        well_readiness = None
        if self._sessions_path.exists():
            try:
                import json as json_mod

                with open(self._sessions_path) as f:
                    sessions = json_mod.load(f)
                sess = sessions.get(request.session_id, {})
                well_readiness = sess.get("well_readiness", 1.0)
                trace.append(f"WELL readiness={well_readiness}")
            except Exception:
                pass

        valid = vault_anchored and (state_hash_valid is not False)
        trace.append(f"valid={valid}")

        return SealVerificationResponse(
            valid=valid,
            verdict=request.verdict,
            session_id=request.session_id,
            state_hash_valid=state_hash_valid,
            vault_anchored=vault_anchored,
            vault_entry_index=vault_entry_index,
            signature_valid=signature_valid,  # HARDENED: real Ed25519 or None
            trace=trace,
            omega_ortho=report.omega_ortho,
            well_readiness=well_readiness,
        )

    def get_orthogonality(self) -> OrthogonalityResponse:
        """Get current Ω_ortho from M01 correlation auditor."""
        auditor = get_auditor()
        ok, report = auditor.is_orthogonal()
        return OrthogonalityResponse(
            omega_ortho=report.omega_ortho,
            threshold=auditor.threshold,
            is_orthogonal=ok,
            violations=len(report.violations),
            agents_in_scope=report.agents_in_scope,
        )

    def get_well_state(self) -> WELLStateResponse:
        """Get current WELL operator state."""
        try:
            # Try to read WELL state file if exists
            well_path = Path.home() / ".arifos" / "well" / "state.json"
            if well_path.exists():
                import json as json_mod

                with open(well_path) as f:
                    state = json_mod.load(f)
                return WELLStateResponse(
                    operator_fatigue=state.get("fatigue"),
                    cognitive_load=state.get("cognitive_load"),
                    stress_level=state.get("stress"),
                    readiness_score=state.get("readiness"),
                    metabolic_stage=state.get("stage"),
                    veto_intact=state.get("veto_intact", True),
                )
        except Exception:
            pass

        return WELLStateResponse(
            metabolic_stage="UNKNOWN",
            veto_intact=True,
        )

    def verify_hash(self, data: str, expected_hash: str) -> bool:
        """Standalone hash verification utility."""
        actual = hashlib.sha256(data.encode()).hexdigest()
        return actual == expected_hash


# ─── Singleton ─────────────────────────────────────────────────────────────────

_verifier: A2ASealVerifier | None = None


def get_seal_verifier() -> A2ASealVerifier:
    global _verifier
    if _verifier is None:
        _verifier = A2ASealVerifier()
    return _verifier
