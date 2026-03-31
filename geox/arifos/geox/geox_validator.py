"""
GEOX Validator — Earth → Language Contract Enforcement
DITEMPA BUKAN DIBERI

The core integrity layer. Converts raw geological tool outputs and LLM-generated
insights into validated, floor-compliant verdicts.

Verdict mapping:
  SEAL    — ≥80% insights supported, 0 contradicted
  PARTIAL — 50–79% supported OR ambiguous evidence exists
  SABAR   — <50% supported, insufficient data, wait/gather more
  VOID    — any contradicted insight detected

Constitutional floors enforced:
  F1  Amanah / Reversibility  — reversibility tag present
  F2  Truth ≥ 0.99           — accuracy claims bounded
  F4  Clarity                — units present in insight text
  F7  Humility               — uncertainty in [0.03, 0.15]
  F13 Sovereign              — human veto on high-risk insights
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

from arifos.geox.geox_schemas import (
    CoordinatePoint,
    GeoPrediction,
    GeoInsight,
    GeoQuantity,
    ProvenanceRecord,
)
from arifos.geox.geox_tools import BaseTool, GeoToolResult


# ---------------------------------------------------------------------------
# ValidationResult
# ---------------------------------------------------------------------------


@dataclass
class ValidationResult:
    """
    Result of validating a single GeoInsight or GeoPrediction against
    the tool ensemble.

    Attributes:
        insight_id:       UUID of the insight being validated.
        verdict:          'supported', 'ambiguous', or 'contradicted'.
        score:            Aggregate validation score [0.0, 1.0].
        evidence:         GeoQuantity objects used as evidence.
        explanation:      Human-readable explanation of the verdict.
        floor_violations: List of floor IDs that were violated (e.g. ["F4", "F7"]).
    """

    insight_id: str
    verdict: Literal["supported", "ambiguous", "contradicted"]
    score: float
    evidence: list[GeoQuantity] = field(default_factory=list)
    explanation: str = ""
    floor_violations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "insight_id": self.insight_id,
            "verdict": self.verdict,
            "score": round(self.score, 4),
            "evidence_count": len(self.evidence),
            "explanation": self.explanation,
            "floor_violations": self.floor_violations,
        }


# ---------------------------------------------------------------------------
# AggregateVerdict
# ---------------------------------------------------------------------------


@dataclass
class AggregateVerdict:
    """
    Aggregate verdict across all GeoInsights in a pipeline run.

    Maps to GEOX verdict vocabulary: SEAL | PARTIAL | SABAR | VOID

    Attributes:
        overall:          Top-level GEOX verdict.
        insight_verdicts: Individual ValidationResult per insight.
        seal_count:       Number of fully supported insights.
        partial_count:    Number of ambiguous insights.
        void_count:       Number of contradicted insights.
        confidence:       Aggregate confidence [0.0, 1.0].
        requires_audit:   True if 888 AUDIT stage is mandatory.
    """

    overall: Literal["SEAL", "PARTIAL", "SABAR", "VOID"]
    insight_verdicts: list[ValidationResult] = field(default_factory=list)
    seal_count: int = 0
    partial_count: int = 0
    void_count: int = 0
    confidence: float = 0.0
    requires_audit: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall": self.overall,
            "seal_count": self.seal_count,
            "partial_count": self.partial_count,
            "void_count": self.void_count,
            "confidence": round(self.confidence, 4),
            "requires_audit": self.requires_audit,
            "insight_verdicts": [v.to_dict() for v in self.insight_verdicts],
        }


# ---------------------------------------------------------------------------
# Prediction extraction patterns
# ---------------------------------------------------------------------------

# Regex patterns to extract testable predictions from LLM-generated text.
# Each pattern captures: (value_or_range, units, quantity_name)
_PREDICTION_PATTERNS: list[tuple[str, str, str]] = [
    # "net pay of 25 m" / "net pay: 25-45 m"
    (
        r"net\s+pay\s+(?:of\s+)?(\d+(?:\.\d+)?(?:\s*[-–to]+\s*\d+(?:\.\d+)?)?)\s*(m|meters?|metres?)",
        "m",
        "net_pay_m",
    ),
    # "HC column of 50 m" / "hydrocarbon column 30-80 m"
    (
        r"h(?:ydrocarbon\s+)?c(?:olumn)?\s+(?:of\s+)?(\d+(?:\.\d+)?(?:\s*[-–to]+\s*\d+(?:\.\d+)?)?)\s*(m|meters?|metres?)",
        "m",
        "hc_column_m",
    ),
    # "porosity of 18%" / "porosity 15-25%"
    (
        r"porosity\s+(?:of\s+)?(\d+(?:\.\d+)?(?:\s*[-–to]+\s*\d+(?:\.\d+)?)?)\s*(%|percent|fraction)?",
        "%",
        "porosity_pct",
    ),
    # "pressure of 3500 psi" / "reservoir pressure 25-35 MPa"
    (
        r"(?:reservoir\s+)?pressure\s+(?:of\s+)?(\d+(?:\.\d+)?(?:\s*[-–to]+\s*\d+(?:\.\d+)?)?)\s*(psi|MPa|mpa|kPa|bar)",
        "psi",
        "reservoir_pressure",
    ),
    # "temperature of 120 degC" / "formation temperature 100-130°C"
    (
        r"(?:formation\s+|reservoir\s+)?temperature\s+(?:of\s+)?(\d+(?:\.\d+)?(?:\s*[-–to]+\s*\d+(?:\.\d+)?)?)\s*(°?C|degC|°?F|degF)",
        "degC",
        "temperature",
    ),
    # "seismic velocity 2400 m/s" / "velocity 2200-3200 m/s"
    (
        r"(?:seismic\s+)?velocity\s+(?:of\s+)?(\d+(?:\.\d+)?(?:\s*[-–to]+\s*\d+(?:\.\d+)?)?)\s*(m/s|km/s)",
        "m/s",
        "seismic_velocity",
    ),
    # "density 2.3 g/cm3"
    (
        r"density\s+(?:of\s+)?(\d+(?:\.\d+)?(?:\s*[-–to]+\s*\d+(?:\.\d+)?)?)\s*(g/cm3|g/cc|kg/m3)",
        "g/cm3",
        "density",
    ),
    # "structural closure of 150 m"
    (
        r"(?:structural\s+)?closure\s+(?:of\s+)?(\d+(?:\.\d+)?(?:\s*[-–to]+\s*\d+(?:\.\d+)?)?)\s*(m|meters?|metres?)",
        "m",
        "structural_closure_m",
    ),
]


def _parse_range(s: str) -> tuple[float, float]:
    """
    Parse a numeric string like '25', '25-45', '25 to 45', or '25–45'
    into a (min, max) float tuple. Single values return (v*0.85, v*1.15).
    """
    s = s.strip()
    match = re.search(r"(\d+(?:\.\d+)?)\s*[-–to]+\s*(\d+(?:\.\d+)?)", s)
    if match:
        lo = float(match.group(1))
        hi = float(match.group(2))
        return (min(lo, hi), max(lo, hi))
    single = re.search(r"(\d+(?:\.\d+)?)", s)
    if single:
        v = float(single.group(1))
        return (round(v * 0.85, 4), round(v * 1.15, 4))
    return (0.0, 0.0)


# ---------------------------------------------------------------------------
# GeoXValidator
# ---------------------------------------------------------------------------


class GeoXValidator:
    """
    Earth → Language contract validator.
    Enforces arifOS Constitutional Floors on all geological intelligence.

    Now featuring the 888_JUDGE Adversarial Mode.
    """

    def __init__(self, confidence_threshold: float = 0.80):
        self.confidence_threshold = confidence_threshold

    async def adversarial_review(
        self, insight: GeoInsight, supporting_quantities: list[GeoQuantity]
    ) -> ValidationResult:
        """
        The 888_JUDGE mode.
        Instead of looking for support, this specifically looks for PHYSICAL VOID.
        If an insight claims 'net pay 50m' but physical quantities show 'shale presence 1.0',
        this method triggers an immediate CONTRADICTED verdict.
        """
        violations = []
        contradicted = False
        explanation = ""

        # 1. Floor F4 (Clarity) Check
        if not re.search(r"\d+\s*(m|MPa|degC|fraction|%)", insight.text):
            violations.append("F4")
            explanation += "Violation: Missing units or numeric bounds in insight text. "

        # 2. Adversarial Evidence Check (The Forge)
        # We look for 'anti-evidence'
        for qty in supporting_quantities:
            # Example: Lithology contradiction
            if "shale" in qty.quantity_type and "net pay" in insight.text.lower():
                # A high shale presence contradicts a 'net pay' (reservoir) claim
                if qty.value > 0.8:
                    contradicted = True
                    explanation += f"Contradiction: Physical quantity '{qty.quantity_type}' ({qty.value}) contradicts reservoir claim. "

            # Example: Porosity contradiction
            if "porosity" in qty.quantity_type and qty.value < 0.05:
                if "reservoir" in insight.text.lower() or "pay" in insight.text.lower():
                    contradicted = True
                    explanation += f"Contradiction: Extreme low porosity ({qty.value}) contradicts reservoir potential. "

        if contradicted:
            return ValidationResult(
                insight_id=insight.insight_id,
                verdict="contradicted",
                score=0.0,
                evidence=supporting_quantities,
                explanation=explanation,
                floor_violations=violations,
            )

        # Default to supported if no contradictions found and floor check passed
        return ValidationResult(
            insight_id=insight.insight_id,
            verdict="supported" if not violations else "ambiguous",
            score=1.0 if not violations else 0.5,
            evidence=supporting_quantities,
            explanation="Validated by 888_JUDGE. No physical contradictions detected.",
            floor_violations=violations,
        )

    # Minimum uncertainty for F7 compliance
    F7_UNCERTAINTY_MIN: float = 0.03
    F7_UNCERTAINTY_MAX: float = 0.15

    # Score thresholds for SEAL/PARTIAL/SABAR/VOID
    SEAL_THRESHOLD: float = 0.80
    PARTIAL_LOWER: float = 0.50

    def extract_predictions(self, text: str, location: CoordinatePoint) -> list[GeoPrediction]:
        """
        Parse LLM output text to extract testable geological claims.

        Uses regex patterns to identify quantitative predictions with
        units (e.g., net pay, pressure, porosity). Each extracted
        prediction gets a conservative confidence of 0.60 (pending
        tool validation).

        Args:
            text:     LLM-generated geological insight text.
            location: Spatial context for the predictions.

        Returns:
            List of GeoPrediction objects. May be empty if no
            quantitative patterns are found.
        """
        predictions: list[GeoPrediction] = []
        text_lower = text.lower()

        for pattern, default_units, quantity_type in _PREDICTION_PATTERNS:
            for match in re.finditer(pattern, text_lower, re.IGNORECASE):
                raw_value = match.group(1)
                detected_units = match.group(2) if match.lastindex >= 2 else default_units

                lo, hi = _parse_range(raw_value)
                if lo == 0.0 and hi == 0.0:
                    continue

                # Normalise units
                units = (
                    detected_units.strip().replace("°", "deg") if detected_units else default_units
                )
                # Convert percent porosity to fraction if needed
                if quantity_type == "porosity_pct" and (lo > 1.0 or hi > 1.0):
                    lo, hi = lo / 100.0, hi / 100.0
                    units = "fraction"

                prov = ProvenanceRecord(
                    source_id=f"LLM-EXTRACT-{quantity_type}",
                    source_type="human",
                    timestamp=datetime.now(timezone.utc),
                    confidence=0.60,
                    floor_check={
                        "F1_amanah": True,
                        "F2_truth": True,
                        "F4_clarity": True,
                        "F7_humility": True,
                        "F9_anti_hantu": True,
                        "F11_authority": False,  # LLM extraction = not primary source
                        "F13_sovereign": True,
                    },
                )

                try:
                    pred = GeoPrediction(
                        target=quantity_type,
                        location=location,
                        expected_range=(lo, hi),
                        units=units,
                        confidence=0.60,
                        supporting_quantities=[],
                        method="LLM_text_extraction",
                    )
                    predictions.append(pred)
                except Exception:
                    # Skip malformed predictions silently
                    continue

        return predictions

    async def verify_prediction(
        self, pred: GeoPrediction, tools: list[BaseTool]
    ) -> ValidationResult:
        """
        Verify a single GeoPrediction against the tool ensemble.

        Runs each tool that is relevant to the prediction's quantity_type
        and compares the predicted range against tool-returned quantities.
        Uses range overlap as the primary matching criterion.

        Args:
            pred:  The GeoPrediction to verify.
            tools: List of BaseTool instances to query.

        Returns:
            ValidationResult with verdict and collected evidence.
        """
        evidence: list[GeoQuantity] = []
        matching_count = 0
        total_count = 0
        floor_violations: list[str] = []

        for tool in tools:
            try:
                result: GeoToolResult = await tool.run(
                    {
                        "query": f"verify {pred.target}",
                        "location": pred.location,
                        "depth_range_m": (
                            pred.location.depth_m - 500 if pred.location.depth_m else 1000,
                            pred.location.depth_m + 500 if pred.location.depth_m else 3000,
                        ),
                        "scenario": {
                            "latitude": pred.location.latitude,
                            "longitude": pred.location.longitude,
                            "target_depth_m": pred.location.depth_m or 2500.0,
                        },
                        "timesteps_ma": [0.0, 5.0, 10.0],
                        "bbox": {
                            "west": pred.location.longitude - 0.5,
                            "east": pred.location.longitude + 0.5,
                            "south": pred.location.latitude - 0.5,
                            "north": pred.location.latitude + 0.5,
                        },
                        "bands": ["B04", "B08", "TIR"],
                        "date_range": ("2023-01-01", "2024-01-01"),
                        "image_path": f"synthetic_{pred.target}.png",
                        "interpretation_query": f"Estimate {pred.target}",
                        "basin": "Malay Basin",
                        "max_results": 3,
                    }
                )

                if not result.success:
                    continue

                for qty in result.quantities:
                    if _quantity_matches_target(qty, pred.target):
                        evidence.append(qty)
                        total_count += 1
                        lo, hi = pred.expected_range
                        # Allow 20% tolerance band around predicted range
                        tol = max(abs(hi - lo) * 0.2, abs(lo) * 0.1)
                        if (lo - tol) <= qty.value <= (hi + tol):
                            matching_count += 1

            except Exception:
                continue

        # Compute score
        if total_count == 0:
            score = 0.5  # no tool evidence → ambiguous
            verdict: Literal["supported", "ambiguous", "contradicted"] = "ambiguous"
            explanation = f"No tool returned data for '{pred.target}'. Result is ambiguous."
        else:
            match_ratio = matching_count / total_count
            if match_ratio >= 0.7:
                verdict = "supported"
                score = 0.5 + match_ratio * 0.5
                explanation = (
                    f"{matching_count}/{total_count} tool measurements fall within "
                    f"predicted range {pred.expected_range} {pred.units}."
                )
            elif match_ratio >= 0.3:
                verdict = "ambiguous"
                score = 0.4 + match_ratio * 0.3
                explanation = (
                    f"Mixed evidence: {matching_count}/{total_count} tool measurements "
                    f"within predicted range. Recommend additional data."
                )
            else:
                verdict = "contradicted"
                score = max_ratio = match_ratio * 0.3
                score = max(0.0, match_ratio * 0.4)
                explanation = (
                    f"Only {matching_count}/{total_count} measurements within range. "
                    f"Tool data contradicts predicted {pred.target}."
                )

        return ValidationResult(
            insight_id=f"pred-{pred.target}",
            verdict=verdict,
            score=min(1.0, score),
            evidence=evidence,
            explanation=explanation,
            floor_violations=floor_violations,
        )

    async def validate_insight(
        self, insight: GeoInsight, tools: list[BaseTool]
    ) -> ValidationResult:
        """
        Validate a complete GeoInsight against the tool ensemble.

        Extracts predictions from insight text, verifies each, and
        aggregates into a single ValidationResult for the insight.

        Args:
            insight: GeoInsight to validate.
            tools:   Tool instances to use for evidence gathering.

        Returns:
            ValidationResult with insight_id, verdict, score, and evidence.
        """
        floor_violations = self.check_floor_compliance(insight)
        floor_violation_list = [k for k, v in floor_violations.items() if not v]

        # Collect evidence from the insight's own support predictions
        all_predictions: list[GeoPrediction] = list(insight.support)

        # Also extract predictions from insight text
        location = (
            insight.support[0].location
            if insight.support
            else CoordinatePoint(latitude=4.5, longitude=103.7)
        )
        extracted = self.extract_predictions(insight.text, location)
        all_predictions.extend(extracted)

        if not all_predictions:
            # No predictions → unverifiable, treat as ambiguous
            return ValidationResult(
                insight_id=insight.insight_id,
                verdict="ambiguous",
                score=0.50,
                evidence=[],
                explanation=(
                    "No testable predictions found in insight. "
                    "Cannot verify without quantitative claims."
                ),
                floor_violations=floor_violation_list,
            )

        # Verify each prediction
        sub_results: list[ValidationResult] = []
        for pred in all_predictions:
            sub = await self.verify_prediction(pred, tools)
            sub_results.append(sub)

        # Aggregate
        verdicts = [r.verdict for r in sub_results]
        scores = [r.score for r in sub_results]
        all_evidence = [qty for r in sub_results for qty in r.evidence]

        if "contradicted" in verdicts:
            agg_verdict: Literal["supported", "ambiguous", "contradicted"] = "contradicted"
        elif all(v == "supported" for v in verdicts):
            agg_verdict = "supported"
        else:
            agg_verdict = "ambiguous"

        agg_score = sum(scores) / len(scores)
        explanation = " | ".join(r.explanation for r in sub_results)

        # Floor violations bump verdict
        if floor_violation_list and agg_verdict == "supported":
            agg_verdict = "ambiguous"
            explanation += f" [Floor violations: {', '.join(floor_violation_list)}]"

        return ValidationResult(
            insight_id=insight.insight_id,
            verdict=agg_verdict,
            score=round(agg_score, 4),
            evidence=all_evidence,
            explanation=explanation,
            floor_violations=floor_violation_list,
        )

    async def validate_batch(
        self, insights: list[GeoInsight], tools: list[BaseTool]
    ) -> AggregateVerdict:
        """
        Validate all insights in a pipeline run and produce the final
        GEOX aggregate verdict (SEAL | PARTIAL | SABAR | VOID).

        Verdict rules:
          SEAL    — ≥80% insights supported, 0 contradicted
          PARTIAL — 50–79% supported OR some ambiguous present
          SABAR   — <50% supported, need more data
          VOID    — any contradicted insight present

        Args:
            insights: All GeoInsight objects from the pipeline.
            tools:    Tool ensemble for evidence gathering.

        Returns:
            AggregateVerdict with overall verdict and per-insight results.
        """
        if not insights:
            return AggregateVerdict(
                overall="SABAR",
                insight_verdicts=[],
                seal_count=0,
                partial_count=0,
                void_count=0,
                confidence=0.0,
                requires_audit=True,
            )

        # Validate each insight (could be parallelised with asyncio.gather)
        import asyncio

        results = await asyncio.gather(
            *[self.validate_insight(i, tools) for i in insights],
            return_exceptions=False,
        )
        results = list(results)

        # Count verdicts
        supported = sum(1 for r in results if r.verdict == "supported")
        ambiguous = sum(1 for r in results if r.verdict == "ambiguous")
        contradicted = sum(1 for r in results if r.verdict == "contradicted")
        total = len(results)

        supported_ratio = supported / total if total else 0.0
        avg_score = sum(r.score for r in results) / total if total else 0.0

        # VOID: any contradicted insight
        if contradicted > 0:
            overall: Literal["SEAL", "PARTIAL", "SABAR", "VOID"] = "VOID"
            requires_audit = True
        elif supported_ratio >= self.SEAL_THRESHOLD:
            overall = "SEAL"
            requires_audit = False
        elif supported_ratio >= self.PARTIAL_LOWER:
            overall = "PARTIAL"
            requires_audit = ambiguous > 0
        else:
            overall = "SABAR"
            requires_audit = True

        return AggregateVerdict(
            overall=overall,
            insight_verdicts=results,
            seal_count=supported,
            partial_count=ambiguous,
            void_count=contradicted,
            confidence=round(avg_score, 4),
            requires_audit=requires_audit,
        )

    def check_floor_compliance(self, insight: GeoInsight) -> dict[str, bool]:
        """
        Check Constitutional Floor compliance for a single insight.

        Checks:
          F1  Amanah/Reversibility — insight text does not assert irreversible action
          F2  Truth ≥ 0.99       — no certainty claims without quantitative basis
          F4  Clarity            — at least one unit string present in text
          F7  Humility           — all supporting quantities have uncertainty in band
          F13 Sovereign          — high/critical risk insights flag human sign-off

        Returns:
            dict mapping floor IDs to bool (True = compliant).
        """
        text = insight.text
        compliance: dict[str, bool] = {}

        # F1: Reversibility — check insight doesn't use irreversible language without hedge
        irreversible_phrases = ["must drill", "immediately drill", "commit to", "final decision"]
        f1_ok = not any(phrase in text.lower() for phrase in irreversible_phrases)
        compliance["F1_amanah"] = f1_ok

        # F2: Truth — check no absolute certainty claims
        certainty_phrases = [
            "100% certain",
            "definitely contains",
            "guaranteed to",
            "absolutely confirmed",
        ]
        f2_ok = not any(phrase in text.lower() for phrase in certainty_phrases)
        compliance["F2_truth"] = f2_ok

        # F4: Clarity — at least one unit is mentioned
        unit_patterns = [
            r"\d+\s*m\b",
            r"\d+\s*km\b",
            r"\d+\s*MPa\b",
            r"\d+\s*psi\b",
            r"\d+\s*°?C\b",
            r"\d+\s*m/s\b",
            r"\d+\s*%\b",
            r"\d+\s*g/cm",
            r"\bfraction\b",
            r"\bdegC\b",
            r"\bmeters?\b",
            r"\bmetres?\b",
        ]
        f4_ok = any(re.search(p, text, re.IGNORECASE) for p in unit_patterns)
        compliance["F4_clarity"] = f4_ok

        # F7: Humility — check uncertainty bands in supporting quantities
        f7_ok = True
        for pred in insight.support:
            for qty in pred.supporting_quantities:
                if not qty.f7_override:
                    if not (self.F7_UNCERTAINTY_MIN <= qty.uncertainty <= self.F7_UNCERTAINTY_MAX):
                        f7_ok = False
                        break
        compliance["F7_humility"] = f7_ok

        # F13: Sovereign — high/critical must require sign-off
        if insight.risk_level in ("high", "critical"):
            compliance["F13_sovereign"] = insight.requires_human_signoff
        else:
            compliance["F13_sovereign"] = True

        # Propagate any existing floor_verdicts (don't overwrite tool-set values)
        for floor_id, tool_verdict in insight.floor_verdicts.items():
            if floor_id not in compliance:
                compliance[floor_id] = tool_verdict

        return compliance


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _quantity_matches_target(qty: GeoQuantity, target: str) -> bool:
    """
    Check if a GeoQuantity's quantity_type is semantically relevant
    to the prediction target string.
    """
    target_lower = target.lower()
    qty_type_lower = qty.quantity_type.lower()

    # Direct match
    if qty_type_lower == target_lower:
        return True

    # Partial semantic matches
    mappings = {
        "net_pay_m": ["net_pay", "pay", "reservoir_thickness"],
        "hc_column_m": ["hc_column", "oil_column", "gas_column"],
        "porosity_pct": ["porosity"],
        "porosity": ["porosity", "porosity_pct"],
        "reservoir_pressure": ["pressure", "pressure_psi"],
        "temperature": ["temperature_degc", "temperature"],
        "seismic_velocity": ["velocity", "seismic_velocity", "interval_velocity"],
        "density": ["density", "bulk_density"],
        "structural_closure_m": ["closure", "structural_closure"],
    }

    for key, synonyms in mappings.items():
        if target_lower == key or target_lower in synonyms:
            if qty_type_lower in synonyms or qty_type_lower == key:
                return True

    # Fuzzy: if target substring in qty_type or vice versa
    if target_lower in qty_type_lower or qty_type_lower in target_lower:
        return True

    return False
