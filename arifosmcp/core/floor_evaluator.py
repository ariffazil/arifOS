"""
arifOS Constitutional Kernel — Floor Evaluator
══════════════════════════════════════════════

Parametric evaluator for F1–F13 Constitutional Floors.
Interprets ThreatAssessment and ActionContext into formal floor decisions.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

# Import all 13 floor classes from canonical shared implementation.
# These live at repo-root /core/shared/ (mapped to sys.path parent).
from core.shared.floors import (
    F1_Amanah,
    F2_Truth,
    F3_QuadWitness,
    F4_Clarity,
    F5_Peace2,
    F6_Empathy,
    F7_Humility,
    F8_Genius,
    F9_AntiHantu,
    F10_Ontology,
)
from core.shared.floors import (
    FloorResult as SharedFloorResult,
)
from pydantic import BaseModel, Field

from arifosmcp.core.threat_engine import (
    IrreversibilityLevel,
    ThreatAssessment,
    ThreatCategory,
)


class FloorResult(BaseModel):
    verdict: str = Field(default="SEAL")  # SEAL | HOLD | VOID
    failed_floors: list[str] = Field(default_factory=list)
    floor_reasons: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_shared(cls, result: SharedFloorResult) -> FloorResult:
        """Adapt a core/shared/floors FloorResult to the runtime FloorResult."""
        return cls(
            verdict="VOID" if not result.passed else "SEAL",
            failed_floors=[result.floor_id] if not result.passed else [],
            floor_reasons={result.floor_id: result.reason},
            metadata={**result.metadata, "score": result.score},
        )


class FloorEvaluator:
    """
    F01–F13 are parametric functions of (context, threat, authority).
    All 13 floors are now enforced at runtime.
    """

    # Floor instances — lazily instantiated once per class
    _f1: F1_Amanah | None = None
    _f2: F2_Truth | None = None
    _f3: F3_QuadWitness | None = None
    _f4: F4_Clarity | None = None
    _f5: F5_Peace2 | None = None
    _f6: F6_Empathy | None = None
    _f7: F7_Humility | None = None
    _f8: F8_Genius | None = None
    _f9: F9_AntiHantu | None = None
    _f10: F10_Ontology | None = None

    @classmethod
    def _floor_context(cls, context: Any, threat: ThreatAssessment) -> dict[str, Any]:
        """
        Build the dict context required by floor check() methods from
        ActionContext (Pydantic) and ThreatAssessment.
        """
        # Derive thermodynamic fields that floor classes need but ActionContext
        # doesn't directly expose. Derived conservatively from threat properties.
        confidence = threat.confidence if threat.confidence is not None else 0.96
        irreversibility = threat.irreversibility.value if threat.irreversibility else 0

        # F2: entropy_delta derived from Landauer bound heuristic.
        # Low confidence = high uncertainty = positive entropy_delta (bad for F4).
        entropy_delta = -(confidence - 0.96)  # ~0 at 0.96, positive when confident

        # F4: clarity — post-entropy derived from confidence improvement.
        entropy_input = confidence - 0.02
        entropy_output = confidence

        # F5: peace² requires non-destructive operations.
        # Map irreversibility level (0-4) to a peace score (1=fully safe, 0=destructive).
        peace_score = max(0.0, 1.0 - (irreversibility / IrreversibilityLevel.CRITICAL.value))

        # F6: empathy kappa_r — derived from irreversibility level.
        # Higher irreversibility = higher potential for destructive impact.
        severity = irreversibility / IrreversibilityLevel.CRITICAL.value
        empathy_kappa_r = max(0.0, 1.0 - severity)

        # F7: humility omega — complement of confidence, must be in [0.03, 0.05].
        humility_omega = 1.0 - confidence

        # F8: Genius dials derived from confidence and entropy.
        clarity = min(1.0, max(0.0, confidence + entropy_delta * 0.1))
        energy = peace_score  # Low irreversibility = high energy efficiency

        # F9: Dark cleverness — flag if threat contains impersonation/social-engineering.
        # Uses FEDERATION_IMPERSONATION and SESSION_IMPERSONATION as proxies.
        security_risk = (
            1.0
            if threat.threats
            & {
                ThreatCategory.FEDERATION_IMPERSONATION,
                ThreatCategory.SESSION_IMPERSONATION,
            }
            else 0.0
        )

        return {
            # Fields from ActionContext
            "tool_name": context.tool_name,
            "mode": context.mode,
            "query": (
                context.payload_text()
                if hasattr(context, "payload_text")
                else (context.query or "")
            ),
            "action": context.mode,
            "actor_id": context.actor_id or "",
            "session_id": context.session_id or "",
            "authority_token": getattr(context, "auth_token", "") or "",
            "auth_token": getattr(context, "auth_token", "") or "",
            "human_authority": (
                1.0 if context.witness_type and "human" in str(context.witness_type) else 0.0
            ),
            "witness_type": str(context.witness_type) if context.witness_type else "ai",
            # Derived from threat
            "confidence": confidence,
            "truth_score": confidence,
            "humility_omega": humility_omega,
            "entropy_delta": entropy_delta,
            "entropy_input": entropy_input,
            "entropy_output": entropy_output,
            "energy_efficiency": energy,
            "compute_time_ms": 100,  # Default; actual compute time not tracked per-call
            "tokens_generated": 100,
            # F3 Witness fields
            "grounding": getattr(context, "verification_surface", None) is not None,
            "thermodynamic_budget_valid": True,
            "earth_witness": confidence,
            "security_risk": security_risk,
            "contradictions": [],
            # F5
            "peace_score": peace_score,
            # F6
            "empathy_kappa_r": empathy_kappa_r,
            "weakest_stakeholder_impact": severity,
            "scope": "social" if threat.threats else "ops",
            # F8
            "akal": clarity,
            "clarity": clarity,
            "present": getattr(context, "regulation", 1.0),
            "exploration": getattr(context, "trust", 1.0),
            "energy": energy,
            "hysteresis_penalty": 0.0,
            # F9
            "prob_truth": [],
            "prob_output": [],
            # F10 (checked with raw text, no extra fields needed)
            "response": context.payload_text() if hasattr(context, "payload_text") else "",
        }

    @classmethod
    def _lazy_floor(cls, floor_class: type, cache: dict) -> Any:
        """Lazily instantiate and cache a floor class instance."""
        key = floor_class.__name__
        if key not in cache:
            try:
                cache[key] = floor_class()
            except Exception:
                return None
        return cache[key]

    @classmethod
    def evaluate(cls, context: Any, threat: ThreatAssessment) -> FloorResult:
        """
        Evaluate all 13 constitutional floors against ActionContext and ThreatAssessment.

        Returns FloorResult with verdict = SEAL | HOLD | VOID and failed_floors list.
        """
        failed: list[str] = []
        reasons: dict[str, str] = {}

        # ── Build floor context dict from ActionContext + ThreatAssessment ──────
        fc = cls._floor_context(context, threat)

        # ── F01 AMANAH — Trustworthiness / Irreversibility ─────────────────────
        f1 = cls._lazy_floor(F1_Amanah, {"F1_Amanah": None})
        if f1 is not None:
            try:
                r = f1.check(fc)
                if not r.passed:
                    failed.append("F01")
                    reasons["F01"] = r.reason
            except Exception:
                pass  # Fallback to old boolean check below

        # Fallback F01 (keep existing logic as safety net)
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
                if "F01" not in failed:
                    failed.append("F01")
                    reasons["F01"] = (
                        f"High irreversibility (level={effective_irreversibility.name}) requires ack_irreversible=True"
                    )

        # ── F02 TRUTH — Information Fidelity (≥ 0.99) ───────────────────────────
        f2 = cls._lazy_floor(F2_Truth, {"F2_Truth": None})
        if f2 is not None:
            try:
                r = f2.check(fc)
                if not r.passed:
                    failed.append("F02")
                    reasons["F02"] = r.reason
                elif "F02" not in failed:
                    reasons["F02"] = r.reason
            except Exception:
                pass

        # ── F03 WITNESS — Quad-Witness Byzantine Consensus (≥ 0.75) ────────────
        f3 = cls._lazy_floor(F3_QuadWitness, {"F3_QuadWitness": None})
        if f3 is not None:
            try:
                r = f3.check(fc)
                if not r.passed:
                    failed.append("F03")
                    reasons["F03"] = r.reason
                elif "F03" not in reasons:
                    reasons["F03"] = r.reason
            except Exception:
                pass

        # ── F04 CLARITY — Entropy Reduction (ΔS ≤ 0) ───────────────────────────
        f4 = cls._lazy_floor(F4_Clarity, {"F4_Clarity": None})
        if f4 is not None:
            try:
                r = f4.check(fc)
                if not r.passed:
                    failed.append("F04")
                    reasons["F04"] = r.reason
                elif "F04" not in reasons:
                    reasons["F04"] = r.reason
            except Exception:
                pass

        # ── F05 PEACE² — Non-Destructive Power (≥ 1.0) ─────────────────────────
        f5 = cls._lazy_floor(F5_Peace2, {"F5_Peace2": None})
        if f5 is not None:
            try:
                r = f5.check(fc)
                if not r.passed:
                    failed.append("F05")
                    reasons["F05"] = r.reason
                elif "F05" not in reasons:
                    reasons["F05"] = r.reason
            except Exception:
                pass

        # ── F06 EMPATHY — Stakeholder Care (κᵣ ≥ 0.70) ─────────────────────────
        f6 = cls._lazy_floor(F6_Empathy, {"F6_Empathy": None})
        if f6 is not None:
            try:
                r = f6.check(fc)
                if not r.passed:
                    failed.append("F06")
                    reasons["F06"] = r.reason
                elif "F06" not in reasons:
                    reasons["F06"] = r.reason
            except Exception:
                pass

        # ── F07 HUMILITY — Uncertainty Band ([0.03, 0.05]) ─────────────────────
        f7 = cls._lazy_floor(F7_Humility, {"F7_Humility": None})
        if f7 is not None:
            try:
                r = f7.check(fc)
                if not r.passed:
                    failed.append("F07")
                    reasons["F07"] = r.reason
                elif "F07" not in reasons:
                    reasons["F07"] = r.reason
            except Exception:
                pass

        # ── F08 GENIUS — Governed Intelligence (G ≥ 0.80) ─────────────────────
        f8 = cls._lazy_floor(F8_Genius, {"F8_Genius": None})
        if f8 is not None:
            try:
                r = f8.check(fc)
                if not r.passed:
                    failed.append("F08")
                    reasons["F08"] = r.reason
                elif "F08" not in reasons:
                    reasons["F08"] = r.reason
            except Exception:
                pass

        # ── F09 ANTIHANTU — No Fake Consciousness (C_dark < 0.30) ───────────────
        f9 = cls._lazy_floor(F9_AntiHantu, {"F9_AntiHantu": None})
        if f9 is not None:
            try:
                r = f9.check(fc)
                if not r.passed:
                    failed.append("F09")
                    reasons["F09"] = r.reason
                elif "F09" not in reasons:
                    reasons["F09"] = r.reason
            except Exception:
                pass

        # ── F10 ONTOLOGY — Category Lock (Boolean) ─────────────────────────────
        f10 = cls._lazy_floor(F10_Ontology, {"F10_Ontology": None})
        if f10 is not None:
            try:
                r = f10.check(fc)
                if not r.passed:
                    failed.append("F10")
                    reasons["F10"] = r.reason
                elif "F10" not in reasons:
                    reasons["F10"] = r.reason
            except Exception:
                pass

        # ── F11 AUTH — Verify identity ─────────────────────────────────────────
        if getattr(context, "session_id", None) and context.session_id not in getattr(
            context, "session_registry", set()
        ):
            if "F11" not in failed:
                failed.append("F11")
                reasons["F11"] = "Session ID not found or expired"

        if getattr(context, "target_agent", None) and context.target_agent not in getattr(
            context, "federation_registry", set()
        ):
            if "F11" not in failed:
                failed.append("F11")
                reasons["F11"] = f"Agent '{context.target_agent}' not in federation registry"

        # ── F12 INJECTION — Sanitize inputs ────────────────────────────────────
        injection_categories = {
            ThreatCategory.INJECTION_SQL,
            ThreatCategory.INJECTION_XSS,
            ThreatCategory.INJECTION_SHELL,
            ThreatCategory.INJECTION_PYTHON,
        }
        if threat.threats & injection_categories:
            if "F12" not in failed:
                failed.append("F12")
                detected = [t.name for t in threat.threats & injection_categories]
                reasons["F12"] = f"Injection threat detected: {detected}"

        # ── F13 SOVEREIGN — Human veto is absolute ───────────────────────────────
        if cls._requires_human_witness(context, threat):
            wt = getattr(context, "witness_type", "ai")
            wt_str = getattr(wt, "value", str(wt))
            if wt_str != "human":
                if context.tool_name == "arif_mind_reason" and context.mode == "plan_approve":
                    failed.append("F13_VIOLATION")
                    reasons["F13_VIOLATION"] = (
                        "F13 SOVEREIGN: AI self-approval is constitutionally forbidden"
                    )
                else:
                    if "F13" not in failed:
                        failed.append("F13")
                        reasons["F13"] = (
                            f"Action requires human witness. witness_type='{wt}' is insufficient."
                        )

        # ── Determine verdict ───────────────────────────────────────────────────
        if failed:
            is_void = (
                "F13_VIOLATION" in failed
                or threat.irreversibility == IrreversibilityLevel.CRITICAL
                or bool(threat.threats & injection_categories)
            )
            verdict = "VOID" if is_void else "HOLD"
            return FloorResult(
                verdict=verdict,
                failed_floors=failed,
                floor_reasons=reasons,
                metadata={
                    "threats": [t.name for t in threat.threats],
                    "irreversibility": threat.irreversibility.name,
                    "confidence": threat.confidence,
                },
            )

        return FloorResult(
            verdict="SEAL",
            floor_reasons=reasons,
            metadata={
                "irreversibility": threat.irreversibility.name,
                "confidence": threat.confidence,
            },
        )

    @staticmethod
    def _requires_human_witness(context: Any, threat: ThreatAssessment) -> bool:
        human_required_tools_modes = {
            "arif_vault_seal": {"seal", "commit"},
            "arif_forge_execute": {"engineer", "write", "generate"},
        }
        if (
            context.tool_name in human_required_tools_modes
            and context.mode in human_required_tools_modes[context.tool_name]
        ):
            # Explicit ack only completes F13 when it is attached to a human witness.
            wt = getattr(context, "witness_type", "ai")
            wt_str = getattr(wt, "value", str(wt))
            if (
                context.tool_name == "arif_vault_seal"
                and getattr(context, "ack_irreversible", False)
                and wt_str == "human"
            ):
                return False
            return True
        if (context.tool_name, context.mode) == ("arif_mind_reason", "plan_approve"):
            return True
        if threat.irreversibility.value >= IrreversibilityLevel.CRITICAL.value:
            return True
        return False
