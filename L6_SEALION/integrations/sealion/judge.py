# integrations/sealion/judge.py
"""
SEA-LION Judge with PHOENIX SOVEREIGNTY Integration (v36.1Omega)

This module provides APEX-compatible judgment for SEA-LION outputs.
It uses the main arifOS metrics and returns SEAL/PARTIAL/VOID/SABAR verdicts.

CRITICAL: If floors["Amanah"] is False, verdict is VOID - no negotiation.

Usage:
    from integrations.sealion.judge import SealionJudge

    judge = SealionJudge()
    result = judge.evaluate(llm_output="...", query="...", high_stakes=False)

    if result.verdict == "VOID":
        print("BLOCKED:", result.amanah_violations)

Author: arifOS Project
License: Apache 2.0
Version: 36.1Omega
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# PHOENIX SOVEREIGNTY: Import ApexMeasurement
_APEX_AVAILABLE = False
_ApexMeasurement = None
_STANDARDS_PATH = Path(__file__).parent.parent.parent / "arifos_eval" / "apex" / "apex_standards_v36.json"

try:
    from arifos_eval.apex.apex_measurements import ApexMeasurement as _ApexMeasurement
    _APEX_AVAILABLE = True
except ImportError:
    pass

# v36.2 PHOENIX: Import Telemetry for observability
_TELEMETRY_AVAILABLE = False
_telemetry = None

try:
    from arifos_core.utils.telemetry_v36 import telemetry as _telemetry
    _TELEMETRY_AVAILABLE = True
except ImportError:
    pass

# PHOENIX SOVEREIGNTY: Import Amanah detector for direct checks
_AMANAH_DETECTOR = None
_AMANAH_AVAILABLE = False

try:
    from arifos_core.floor_detectors.amanah_risk_detectors import (
        AMANAH_DETECTOR as _AMANAH_DETECTOR,
        AmanahResult,
    )
    _AMANAH_AVAILABLE = True
except ImportError:
    @dataclass
    class AmanahResult:
        is_safe: bool = True
        violations: List[str] = field(default_factory=list)
        warnings: List[str] = field(default_factory=list)

        def to_dict(self) -> Dict:
            return {
                "is_safe": self.is_safe,
                "violations": self.violations,
                "warnings": self.warnings,
            }


# ============================================================================
# VERDICT TYPES
# ============================================================================

VERDICTS = ["SEAL", "PARTIAL", "VOID", "SABAR"]


# ============================================================================
# JUDGMENT RESULT
# ============================================================================

@dataclass
class JudgmentResult:
    """Result of APEX judgment on SEA-LION output."""
    # Core verdict
    verdict: str  # SEAL, PARTIAL, VOID, SABAR

    # GENIUS LAW metrics
    G: float = 0.0  # Genius index
    C_dark: float = 0.0  # Dark cleverness
    Psi: float = 0.0  # Vitality

    # Floor status
    floors: Dict[str, bool] = field(default_factory=dict)

    # PHOENIX SOVEREIGNTY: Amanah details
    amanah_safe: bool = True
    amanah_violations: List[str] = field(default_factory=list)
    amanah_warnings: List[str] = field(default_factory=list)

    # Metadata
    high_stakes: bool = False
    note: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verdict": self.verdict,
            "G": self.G,
            "C_dark": self.C_dark,
            "Psi": self.Psi,
            "floors": self.floors,
            "amanah_safe": self.amanah_safe,
            "amanah_violations": self.amanah_violations,
            "amanah_warnings": self.amanah_warnings,
            "high_stakes": self.high_stakes,
            "note": self.note,
        }


# ============================================================================
# SEALION JUDGE
# ============================================================================

class SealionJudge:
    """
    APEX-compatible judge for SEA-LION outputs.

    Evaluates LLM outputs using the main arifOS GENIUS LAW metrics
    and constitutional floors. Returns verdict and telemetry.

    CRITICAL RULE:
        If floors["Amanah"] is False (Python veto), verdict is VOID.
        No negotiation. No override.

    Example:
        judge = SealionJudge()
        result = judge.evaluate(
            llm_output="rm -rf / will delete everything",
            query="How do I delete files?",
            high_stakes=False,
        )
        # result.verdict == "VOID"
        # result.amanah_safe == False
        # result.amanah_violations == ["[RED] rm with -r or -f flags..."]
    """

    def __init__(self, standards_path: Optional[str] = None):
        """
        Initialize SEA-LION judge.

        Args:
            standards_path: Path to apex_standards_v36.json (optional)
        """
        self._standards_path = standards_path or str(_STANDARDS_PATH)
        self._apex = None
        self._amanah_detector = _AMANAH_DETECTOR if _AMANAH_AVAILABLE else None

        # Initialize ApexMeasurement if available
        if _APEX_AVAILABLE and _ApexMeasurement is not None:
            try:
                self._apex = _ApexMeasurement(self._standards_path)
            except Exception:
                pass

    def _check_amanah(self, text: str) -> AmanahResult:
        """
        PHOENIX SOVEREIGNTY: Check text with Python-sovereign Amanah detector.
        """
        if self._amanah_detector is None:
            return AmanahResult(is_safe=True)
        return self._amanah_detector.check(text)

    def _build_dials(self, high_stakes: bool) -> Dict[str, float]:
        """Build APEX dials (A, P, E, X) for judgment."""
        dials = {
            "A": 0.88,  # Ability - SEA-LION is capable
            "P": 0.82,  # Prosociality - governed prompt
            "E": 0.78,  # Energy - standard operation
            "X": 0.85,  # Experience - trained on regional data
        }

        if high_stakes:
            dials["E"] = 0.68  # More cautious
            dials["P"] = 0.75  # Stricter prosociality

        return dials

    def _build_output_metrics(self, high_stakes: bool) -> Dict[str, float]:
        """Build output metrics for judgment."""
        metrics = {
            "delta_s": 0.08,   # Slight entropy reduction
            "peace2": 1.03,    # Non-destructive
            "k_r": 0.95,       # Empathy
            "rasa": 1.0,       # RASA pass
            "amanah": 1.0,     # Will be overridden by Python detector
            "entropy": 0.32,   # Moderate entropy
        }

        if high_stakes:
            metrics["entropy"] = 0.42  # Higher uncertainty

        return metrics

    def evaluate(
        self,
        llm_output: str,
        query: str = "",
        high_stakes: bool = False,
        context: Optional[Dict[str, Any]] = None,
    ) -> JudgmentResult:
        """
        Evaluate LLM output and return verdict.

        Pipeline:
        1. Python-sovereign Amanah check (PHOENIX SOVEREIGNTY)
        2. If Amanah fails -> VOID (no further checks)
        3. If Amanah passes -> Full APEX judgment

        Args:
            llm_output: The LLM response text to evaluate
            query: Original user query (for context)
            high_stakes: Whether this is a high-stakes query
            context: Additional context for judgment

        Returns:
            JudgmentResult with verdict and telemetry
        """
        result = JudgmentResult(
            verdict="PARTIAL",  # Default
            high_stakes=high_stakes,
        )

        # STEP 1: PHOENIX SOVEREIGNTY - Python-sovereign Amanah check
        amanah_result = self._check_amanah(llm_output)
        result.amanah_safe = amanah_result.is_safe
        result.amanah_violations = amanah_result.violations
        result.amanah_warnings = amanah_result.warnings

        # CRITICAL: If Amanah fails, verdict is VOID immediately
        if not amanah_result.is_safe:
            result.verdict = "VOID"
            result.floors = {"Amanah": False}
            result.note = "Python-sovereign Amanah veto"

            # v36.2 PHOENIX: Log VOID events for audit trail
            if _TELEMETRY_AVAILABLE and _telemetry is not None:
                _telemetry.log_event(
                    input_text=query,
                    output_text=llm_output,
                    judgment=result,
                    metadata={
                        "source": "SealionJudge",
                        "veto_reason": "Amanah",
                        "context": context or {},
                    },
                )

            return result

        # STEP 2: Full APEX judgment (if available)
        if self._apex is not None:
            dials = self._build_dials(high_stakes)
            output_metrics = self._build_output_metrics(high_stakes)

            try:
                apex_result = self._apex.judge(dials, llm_output, output_metrics)

                result.verdict = apex_result.get("verdict", "PARTIAL")
                result.G = apex_result.get("G", 0.0)
                result.C_dark = apex_result.get("C_dark", 0.0)
                result.Psi = apex_result.get("Psi", 0.0)
                result.floors = apex_result.get("floors", {})

                # Ensure Amanah is True in floors (since we already checked)
                result.floors["Amanah"] = True

            except Exception as e:
                result.note = f"APEX error: {e}"
                result.verdict = "PARTIAL"

        else:
            # Fallback: Simple verdict based on Amanah only
            result.verdict = "PARTIAL"
            result.floors = {"Amanah": True}
            result.note = "ApexMeasurement not available - using fallback"

        # v36.2 PHOENIX: Log telemetry event for observability
        if _TELEMETRY_AVAILABLE and _telemetry is not None:
            _telemetry.log_event(
                input_text=query,
                output_text=llm_output,
                judgment=result,
                metadata={
                    "source": "SealionJudge",
                    "context": context or {},
                },
            )

        return result

    def evaluate_with_engine_result(
        self,
        engine_result: Any,  # SealionResult from engine.py
        query: str = "",
        high_stakes: bool = False,
    ) -> JudgmentResult:
        """
        Evaluate using a SealionResult from the engine.

        This is a convenience method that extracts the raw response
        and existing Amanah data from the engine result.
        """
        # Extract raw response
        raw_response = getattr(engine_result, "raw_response", None)
        if raw_response is None:
            raw_response = getattr(engine_result, "response", "")

        # Check if engine already blocked
        if getattr(engine_result, "amanah_blocked", False):
            return JudgmentResult(
                verdict="VOID",
                amanah_safe=False,
                amanah_violations=getattr(engine_result, "amanah_violations", []),
                amanah_warnings=getattr(engine_result, "amanah_warnings", []),
                floors={"Amanah": False},
                high_stakes=high_stakes,
                note="Pre-blocked by engine",
            )

        # Run full evaluation
        return self.evaluate(raw_response, query, high_stakes)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def quick_judge(llm_output: str, high_stakes: bool = False) -> str:
    """
    Quick judgment - returns just the verdict string.

    Args:
        llm_output: LLM response text
        high_stakes: Whether high-stakes mode

    Returns:
        Verdict string: "SEAL", "PARTIAL", "VOID", or "SABAR"
    """
    judge = SealionJudge()
    result = judge.evaluate(llm_output, high_stakes=high_stakes)
    return result.verdict


def check_sealion_output(llm_output: str) -> Dict[str, Any]:
    """
    Check SEA-LION output and return full judgment dict.

    Returns:
        Dict with verdict, floors, metrics, and Amanah telemetry
    """
    judge = SealionJudge()
    result = judge.evaluate(llm_output)
    return result.to_dict()


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "JudgmentResult",
    "SealionJudge",
    "quick_judge",
    "check_sealion_output",
    "VERDICTS",
]
