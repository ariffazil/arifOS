"""
arifOS Constitutional Kernel — Floor Evaluator
═══════════════════════════════════════════════

Parametric evaluator for F1–F13 Constitutional Floors.
Interprets ThreatAssessment and ActionContext into formal floor decisions.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from arifosmcp.core.threat_engine import ThreatAssessment, ThreatCategory, IrreversibilityLevel

class FloorResult(BaseModel):
    verdict: str = Field(default="SEAL")  # SEAL | HOLD | VOID
    failed_floors: list[str] = Field(default_factory=list)
    floor_reasons: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

class FloorEvaluator:
    """
    F01–F13 are parametric functions of (context, threat, authority).
    """

    @classmethod
    def evaluate(cls, context: Any, threat: ThreatAssessment) -> FloorResult:
        failed: list[str] = []
        reasons: dict[str, str] = {}

        # F01 AMANAH — Trustworthiness / Irreversibility
        tool_base_irreversibility = {
            ("arif_vault_seal", "seal"): IrreversibilityLevel.CRITICAL,
            ("arif_vault_seal", "commit"): IrreversibilityLevel.CRITICAL,
            ("arif_forge_execute", "engineer"): IrreversibilityLevel.HIGH,
            ("arif_forge_execute", "write"): IrreversibilityLevel.HIGH,
            ("arif_forge_execute", "generate"): IrreversibilityLevel.HIGH,
        }
        base_irrev = tool_base_irreversibility.get((context.tool_name, context.mode))
        effective_irreversibility = max(
            threat.irreversibility,
            base_irrev or IrreversibilityLevel.NONE,
            key=lambda x: x.value,
        )

        if effective_irreversibility.value >= IrreversibilityLevel.HIGH.value:
            if not getattr(context, "ack_irreversible", False):
                failed.append("F01")
                reasons["F01"] = f"Irreversible action (level={effective_irreversibility.name}) requires ack_irreversible=True"

        # F11 AUTH — Verify identity
        if getattr(context, "session_id", None) and context.session_id not in getattr(context, "session_registry", set()):
            failed.append("F11")
            reasons["F11"] = "Session ID not found or expired"

        if getattr(context, "target_agent", None) and context.target_agent not in getattr(context, "federation_registry", set()):
            failed.append("F11")
            reasons["F11"] = f"Agent '{context.target_agent}' not in federation registry"

        # F12 INJECTION — Sanitize inputs
        injection_categories = {
            ThreatCategory.INJECTION_SQL,
            ThreatCategory.INJECTION_XSS,
            ThreatCategory.INJECTION_SHELL,
            ThreatCategory.INJECTION_PYTHON,
        }
        if threat.threats & injection_categories:
            failed.append("F12")
            detected = [t.name for t in threat.threats & injection_categories]
            reasons["F12"] = f"Injection threat detected: {detected}"

        # F13 SOVEREIGN — Human veto is absolute
        if cls._requires_human_witness(context, threat):
            if getattr(context, "witness_type", "ai") != "human":
                if context.tool_name == "arif_mind_reason" and context.mode == "plan_approve":
                    failed.append("F13_VIOLATION")
                    reasons["F13_VIOLATION"] = "F13 SOVEREIGN: AI self-approval is constitutionally forbidden"
                else:
                    failed.append("F13")
                    reasons["F13"] = f"Action requires human witness. witness_type='{getattr(context, 'witness_type', 'ai')}' is insufficient."

        if failed:
            is_void = "F13_VIOLATION" in failed or threat.irreversibility == IrreversibilityLevel.CRITICAL or bool(threat.threats & injection_categories)
            verdict = "VOID" if is_void else "HOLD"
            return FloorResult(
                verdict=verdict,
                failed_floors=failed,
                floor_reasons=reasons,
                metadata={"threats": [t.name for t in threat.threats], "irreversibility": threat.irreversibility.name}
            )

        return FloorResult(verdict="SEAL", metadata={"irreversibility": threat.irreversibility.name})

    @staticmethod
    def _requires_human_witness(context: Any, threat: ThreatAssessment) -> bool:
        human_required_tools_modes = {
            "arif_vault_seal": {"seal", "commit"},
            "arif_forge_execute": {"engineer", "write", "generate"},
        }
        if context.tool_name in human_required_tools_modes and context.mode in human_required_tools_modes[context.tool_name]:
            return True
        if (context.tool_name, context.mode) == ("arif_mind_reason", "plan_approve"):
            return True
        if threat.irreversibility.value >= IrreversibilityLevel.CRITICAL.value:
            return True
        return False
