"""
arifOS Constitutional Kernel — Unified Orchestrator
═══════════════════════════════════════════════════

Authoritative entry point for constitutional adjudication.
Integrates ThreatEngine, FloorEvaluator, and AuthorityGate.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

from arifosmcp.core.authority_gate import AuthorityGate
from arifosmcp.core.floor_evaluator import FloorEvaluator
from arifosmcp.core.session_registry import SessionRegistry
from arifosmcp.core.threat_engine import ThreatEngine

logger = logging.getLogger(__name__)


class ConstitutionKernel:
    """
    Sovereign orchestrator for all constitutional decisions.
    """

    def __init__(self):
        self.threat_engine = ThreatEngine()
        self.evaluator = FloorEvaluator()
        self.gate = AuthorityGate()
        self.sessions = SessionRegistry()

    def evaluate_intent(
        self,
        tool_name: str,
        params: dict[str, Any],
        session_id: str | None = None,
        proof: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Complete constitutional evaluation cycle.
        """
        # 1. Identity Check
        actor_id = self.sessions.get_actor(session_id) if session_id else None

        # 2. Threat Scan
        intent_str = f"{tool_name}: {params}"
        threat_verdict = self.threat_engine.scan(intent_str)

        # 3. Floor Adjudication
        floor_result = self.evaluator.evaluate(tool_name, threat_verdict, actor_id)

        # 4. Authority Verification for critical actions
        auth_proof = None
        if floor_result.verdict != "SEAL":
            intent_hash = self.gate.generate_intent_hash(tool_name, params)
            auth_proof = self.gate.verify_authorization(intent_hash, proof)

            # Upgrade HOLD to SEAL if valid human proof provided
            if auth_proof.valid:
                floor_result.verdict = "SEAL"
                floor_result.passed = True
                floor_result.reason = "Sovereign override verified."

        return {
            "verdict": floor_result.verdict,
            "passed": floor_result.passed,
            "failed_floors": floor_result.breached_floors,
            "reason": floor_result.reason,
            "threat_score": threat_verdict.score,
            "threat_tier": threat_verdict.tier.value,
            "auth_witness": auth_proof.witness_type if auth_proof else "none",
        }
