"""
arifOS v2.0 — Shadow Defense System (F9 ANTI-HANTU)
═══════════════════════════════════════════════════════════════════════════
Detects "Shadow arifOS" manifestations: institutional narrative laundered
through constitutional vocabulary without metabolic enforcement.

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

import re
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from arifosmcp.models.verdicts import SealType, FloorName

@dataclass
class ShadowDetectionResult:
    is_shadow: bool
    pattern_id: str
    confidence: float
    description: str

class ShadowDefense:
    """
    Implements F9 Anti-Hantu detection logic.
    """
    
    CONSTITUTIONAL_VOCAB = [
        "SEAL", "HOLD", "VOID", "TRI-WITNESS", "AMANAH", 
        "ORTHOGONALITY", "OMEGA", "METABOLIC", "PEACE2"
    ]

    @staticmethod
    def detect_p1_vocabulary_laundering(content: str, telemetry: Dict[str, Any]) -> Optional[ShadowDetectionResult]:
        """
        P1: Uses constitutional vocabulary but fails to emit structured telemetry.
        """
        has_vocab = any(v in content.upper() for v in ShadowDefense.CONSTITUTIONAL_VOCAB)
        has_telemetry = "telemetry" in str(telemetry).lower() or "session_id" in str(telemetry).lower()
        
        if has_vocab and not has_telemetry:
            return ShadowDetectionResult(
                is_shadow=True,
                pattern_id="P1_VOCAB_WITHOUT_STRUCTURE",
                confidence=0.9,
                description="Constitutional terms used without metabolic backbone."
            )
        return None

    @staticmethod
    def detect_p2_pipeline_shortcut(completed_stages: List[int]) -> Optional[ShadowDetectionResult]:
        """
        P2: Attempting Stage 777 (Forge) without Stage 666 (Heart).
        """
        if 777 in completed_stages and 666 not in completed_stages:
            return ShadowDetectionResult(
                is_shadow=True,
                pattern_id="P2_PIPELINE_SHORTCUT",
                confidence=1.0,
                description="Forge attempted without Heart clearance."
            )
        return None

    @staticmethod
    def detect_p5_narrative_laundering(
        npv: float, 
        omega: float, 
        verdict: SealType
    ) -> Optional[ShadowDetectionResult]:
        """
        P5: Economic conclusion overrides physical/orthogonal reality.
        """
        if npv > 0 and omega < 0.85 and verdict == SealType.SEAL:
            return ShadowDetectionResult(
                is_shadow=True,
                pattern_id="P5_NARRATIVE_LAUNDERING",
                confidence=0.85,
                description="Profit-driven SEAL issued despite low Orthogonality."
            )
        return None

    @staticmethod
    def check_shadow_sabar(ctx: Dict[str, Any]) -> bool:
        """
        Distinguishes Sabar (Patience) from Shadow-Delay.
        Returns True if it is a genuine SABAR state.
        """
        has_trigger = ctx.get("re_evaluation_trigger") is not None
        has_open_question = ctx.get("logged_unknown") is not None
        return has_trigger and has_open_question

    def run_full_audit(self, ctx: Dict[str, Any]) -> List[ShadowDetectionResult]:
        results = []
        
        # P1 Check
        p1 = self.detect_p1_vocabulary_laundering(ctx.get("content", ""), ctx.get("telemetry", {}))
        if p1: results.append(p1)
        
        # P2 Check
        p2 = self.detect_p2_pipeline_shortcut(ctx.get("stages", []))
        if p2: results.append(p2)
        
        # P5 Check
        p5 = self.detect_p5_narrative_laundering(
            ctx.get("npv", 0.0), 
            ctx.get("omega_ortho", 1.0), 
            ctx.get("verdict", SealType.HOLD)
        )
        if p5: results.append(p5)
        
        return results
