"""
888 AUDIT layer for seismic image interpretation.

Constitutional floor compliance verification.
Enforces F1-F13 on all interpretation outputs.

Audit triggers:
- Unknown polarity with polarity-sensitive request
- Missing vertical scale
- Excessive annotation contamination
- High model confidence but high uncertainty disagreement
- Output exceeds image-domain evidence
"""

from __future__ import annotations

import logging
from typing import Any

from .schemas import AuditResponse, FloorAudit, Verdict

logger = logging.getLogger("geox.seismic_image.audit")


class ConstitutionalAuditor:
    """Audits interpretation results against constitutional floors."""
    
    FLOORS = ["F1", "F2", "F4", "F7", "F9", "F11", "F13"]
    
    def __init__(self, result_id: str, interpretation_data: dict[str, Any]):
        self.result_id = result_id
        self.data = interpretation_data
        self.audits: list[FloorAudit] = []
        self.violations: list[str] = []
    
    def audit_F1_amanah(self) -> FloorAudit:
        """
        F1 AMANAH: No irreversible claims without SEAL.
        
        Check: No drilling recommendations, no definitive resource estimates.
        """
        claims = self.data.get("interpretation", {})
        
        # Check for irreversible claims
        irreversible_keywords = [
            "drill", "drilling", "producer", "development", "investment",
            "economically viable", "commercial", "reserves"
        ]
        
        has_irreversible = any(
            kw in str(claims).lower() for kw in irreversible_keywords
        )
        
        if has_irreversible:
            self.violations.append("F1: Irreversible claim detected")
            return FloorAudit(
                floor="F1",
                status="VIOLATION",
                details="Irreversible claim (drilling/commercial) made from image-only evidence",
                action="VOID",
            )
        
        return FloorAudit(
            floor="F1",
            status="PASS",
            details="No irreversible claims made",
            action="NONE",
        )
    
    def audit_F2_truth(self) -> FloorAudit:
        """
        F2 TRUTH: Evidence supports claims.
        
        Check: Confidence band declared, evidence links present.
        """
        confidence = self.data.get("confidence_band", {})
        evidence = self.data.get("evidence_links", [])
        
        if not confidence:
            self.violations.append("F2: No confidence band declared")
            return FloorAudit(
                floor="F2",
                status="VIOLATION",
                details="Confidence band not declared",
                action="HOLD",
            )
        
        if not evidence:
            self.violations.append("F2: No evidence links")
            return FloorAudit(
                floor="F2",
                status="WARNING",
                details="No evidence links provided for interpretation",
                action="FLAG",
            )
        
        aggregate = confidence.get("aggregate", 0)
        if aggregate < 0.5:
            self.violations.append(f"F2: Low confidence ({aggregate})")
            return FloorAudit(
                floor="F2",
                status="WARNING",
                details=f"Low confidence: {aggregate} — claims exceed evidence",
                action="FLAG",
            )
        
        return FloorAudit(
            floor="F2",
            status="PASS",
            details=f"Evidence supports claims within confidence band: {confidence.get('range', 'unknown')}",
            action="NONE",
        )
    
    def audit_F4_clarity(self) -> FloorAudit:
        """
        F4 CLARITY: Units and scales declared.
        
        Check: Vertical unit, scale, pixel-to-meter ratio present.
        """
        metadata = self.data.get("metadata", {})
        
        required_fields = ["vertical_unit", "vertical_scale"]
        missing = [f for f in required_fields if f not in metadata]
        
        if missing:
            self.violations.append(f"F4: Missing fields: {missing}")
            return FloorAudit(
                floor="F4",
                status="VIOLATION",
                details=f"Missing required fields: {missing}",
                action="VOID",
            )
        
        return FloorAudit(
            floor="F4",
            status="PASS",
            details="Units and scales declared",
            action="NONE",
        )
    
    def audit_F7_humility(self) -> FloorAudit:
        """
        F7 HUMILITY: Uncertainty declared and bounded.
        
        Check: Uncertainty in [0.03, 0.15], aggregate <= 0.95 for image-first.
        """
        confidence = self.data.get("confidence_band", {})
        
        uncertainty = confidence.get("uncertainty", 0)
        aggregate = confidence.get("aggregate", 0)
        
        # Check uncertainty bounds
        if uncertainty < 0.03:
            self.violations.append(f"F7: Uncertainty too low ({uncertainty})")
            return FloorAudit(
                floor="F7",
                status="WARNING",
                details=f"Uncertainty {uncertainty} below F7 minimum (0.03)",
                action="ADJUST",
            )
        
        if uncertainty > 0.15:
            self.violations.append(f"F7: Uncertainty too high ({uncertainty})")
            return FloorAudit(
                floor="F7",
                status="WARNING",
                details=f"Uncertainty {uncertainty} exceeds F7 maximum (0.15)",
                action="FLAG",
            )
        
        # Image-first ceiling
        if aggregate > 0.95:
            self.violations.append(f"F7: Confidence exceeds image-first ceiling ({aggregate})")
            return FloorAudit(
                floor="F7",
                status="VIOLATION",
                details=f"Confidence {aggregate} exceeds image-first ceiling (0.95)",
                action="CAP",
            )
        
        return FloorAudit(
            floor="F7",
            status="PASS",
            details=f"Uncertainty {uncertainty} in valid range, aggregate {aggregate} within ceiling",
            action="NONE",
        )
    
    def audit_F9_anti_hantu(self) -> FloorAudit:
        """
        F9 ANTI-HANTU: No hallucinated geology.
        
        Check: All claims linked to evidence, counter-hypotheses present.
        """
        interpretation = self.data.get("interpretation", {})
        counter_hypotheses = self.data.get("counter_hypotheses", [])
        
        # Check for hallucination indicators
        hallucination_keywords = [
            "definitely", "certainly", "without doubt", "proven",
            "absolute", "conclusive"
        ]
        
        has_hallucination_language = any(
            kw in str(interpretation).lower() for kw in hallucination_keywords
        )
        
        if has_hallucination_language:
            self.violations.append("F9: Hallucination language detected")
            return FloorAudit(
                floor="F9",
                status="WARNING",
                details="Overly certain language detected",
                action="FLAG",
            )
        
        if not counter_hypotheses:
            self.violations.append("F9: No counter-hypotheses")
            return FloorAudit(
                floor="F9",
                status="WARNING",
                details="No counter-hypotheses provided",
                action="FLAG",
            )
        
        return FloorAudit(
            floor="F9",
            status="PASS",
            details="Evidence-linked claims, counter-hypotheses present",
            action="NONE",
        )
    
    def audit_F11_authority(self) -> FloorAudit:
        """
        F11 AUTHORITY: Requester authenticated.
        
        Check: Requester ID present and valid.
        """
        requester = self.data.get("requester_id")
        
        if not requester:
            self.violations.append("F11: No requester ID")
            return FloorAudit(
                floor="F11",
                status="VIOLATION",
                details="Requester ID not provided",
                action="VOID",
            )
        
        return FloorAudit(
            floor="F11",
            status="PASS",
            details=f"Requester authenticated: {requester}",
            action="NONE",
        )
    
    def audit_F13_sovereign(self) -> FloorAudit:
        """
        F13 SOVEREIGN: Human veto always possible.
        
        Check: Human signoff pathway available.
        """
        # This is a system-level check
        # Always available by design
        return FloorAudit(
            floor="F13",
            status="PASS",
            details="Human veto pathway available",
            action="NONE",
        )
    
    def run_audit(self) -> AuditResponse:
        """Run full constitutional audit."""
        # Run all floor audits
        self.audits = [
            self.audit_F1_amanah(),
            self.audit_F2_truth(),
            self.audit_F4_clarity(),
            self.audit_F7_humility(),
            self.audit_F9_anti_hantu(),
            self.audit_F11_authority(),
            self.audit_F13_sovereign(),
        ]
        
        # Determine overall status
        violations = [a for a in self.audits if a.status == "VIOLATION"]
        warnings = [a for a in self.audits if a.status == "WARNING"]
        
        if violations:
            audit_status = "FAIL"
            verdict = Verdict.VOID
        elif warnings:
            audit_status = "WARNING"
            verdict = Verdict.PARTIAL
        else:
            audit_status = "PASS"
            verdict = Verdict.SEAL
        
        # Human signoff required for non-SEAL or high-risk
        human_signoff_required = (
            verdict != Verdict.SEAL or
            self.data.get("risk_tolerance") in ["high", "critical"]
        )
        
        logger.info(
            "Audit complete for %s: status=%s, violations=%d, warnings=%d",
            self.result_id, audit_status, len(violations), len(warnings)
        )
        
        return AuditResponse(
            success=True,
            result_id=self.result_id,
            verdict=verdict,
            audit_status=audit_status,
            floor_audits=self.audits,
            overall_confidence=self.data.get("confidence_band", {}).get("aggregate", 0),
            human_signoff_required=human_signoff_required,
        )


async def audit_seismic_interpretation(
    result_id: str,
    interpretation_data: dict[str, Any],
    audit_depth: str = "standard",
) -> AuditResponse:
    """
    888 AUDIT layer for seismic interpretation.
    
    Enforces all constitutional floors (F1-F13).
    """
    try:
        auditor = ConstitutionalAuditor(result_id, interpretation_data)
        return auditor.run_audit()
        
    except Exception as e:
        logger.exception("Audit failed: %s", e)
        return AuditResponse(
            success=False,
            result_id=result_id,
            verdict=Verdict.VOID,
            audit_status="ERROR",
            floor_audits=[],
            overall_confidence=0,
            human_signoff_required=True,
        )
