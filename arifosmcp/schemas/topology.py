"""
arifOS Topology Schemas — Inclusive Topology / Anti-Sink Diagnostics
═══════════════════════════════════════════════════════════════════════════════

Pydantic output schemas for:
  - arif_anti_sink_check
  - institutional_drift_check

These are reversible runtime diagnostics. They do not modify state.
They return ESTIMATES and FLAGS, not verdicts.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS — Anti-Sink Diagnostic Bands
# ═══════════════════════════════════════════════════════════════════════════════


class Delta(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    UNKNOWN = "unknown"


class Strength(str, Enum):
    STRONG = "strong"
    PARTIAL = "partial"
    WEAK = "weak"
    ABSENT = "absent"


class RiskBand(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Verdict(str, Enum):
    PASS = "pass"
    REVISE = "revise"
    HOLD = "hold"
    VOID = "void"


class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Presence(str, Enum):
    PRESENT = "present"
    WEAK = "weak"
    ABSENT = "absent"


class AccessLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ParticipationWidth(str, Enum):
    BROAD = "broad"
    NARROW = "narrow"
    SYMBOLIC = "symbolic"


class InnovationRights(str, Enum):
    DISTRIBUTED = "distributed"
    GATED = "gated"
    CAPTURED = "captured"


class AppealPath(str, Enum):
    PRESENT = "present"
    WEAK = "weak"
    ABSENT = "absent"


class SovereigntyIntegrity(str, Enum):
    STRONG = "strong"
    DEGRADED = "degraded"
    SYMBOLIC = "symbolic"


class InstitutionalVerdict(str, Enum):
    INCLUSIVE = "inclusive"
    MIXED = "mixed"
    EXTRACTIVE_DRIFT = "extractive_drift"
    EXTRACTIVE = "extractive"


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMAS — Anti-Sink Check
# ═══════════════════════════════════════════════════════════════════════════════


class AntiSinkCheck(BaseModel):
    """777_TOPOLOGY: Reversible runtime diagnostic for behavioral sink risk."""

    agency_delta: Delta = Field(
        default=Delta.UNKNOWN,
        description="Change in human agency relative to baseline.",
    )
    role_diversity_delta: Delta = Field(
        default=Delta.UNKNOWN,
        description="Change in meaningful role diversity.",
    )
    feedback_integrity: Strength = Field(
        default=Strength.ABSENT,
        description="Strength of feedback path from action to consequence.",
    )
    topology_risk: RiskBand = Field(
        default=RiskBand.LOW,
        description="Risk that topology is becoming extractive.",
    )
    extractive_drift: RiskBand = Field(
        default=RiskBand.LOW,
        description="Early-warning extractive drift indicator.",
    )
    inclusive_repair_path: Presence = Field(
        default=Presence.ABSENT,
        description="Whether inclusive repair pathways exist.",
    )
    beautiful_ones_risk: bool = Field(
        default=False,
        description="Advisory flag: output may be aesthetic without responsibility.",
    )
    agency_compression: RiskBand = Field(
        default=RiskBand.LOW,
        description="Degree of agency compression detected.",
    )
    verdict: Verdict = Field(
        default=Verdict.PASS,
        description="Advisory verdict: pass | revise | hold | void.",
    )
    confidence: Confidence = Field(
        default=Confidence.LOW,
        description="Confidence in this estimate. Low until sensors are wired.",
    )
    notes: list[str] = Field(
        default_factory=list,
        description="Human-readable diagnostic notes.",
    )
    constitutional_floors_checked: list[str] = Field(
        default_factory=list,
        description="Which F-floor extensions were evaluated.",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "agency_delta": "negative",
                    "role_diversity_delta": "negative",
                    "feedback_integrity": "weak",
                    "topology_risk": "high",
                    "extractive_drift": "high",
                    "inclusive_repair_path": "weak",
                    "beautiful_ones_risk": True,
                    "agency_compression": "high",
                    "verdict": "hold",
                    "confidence": "medium",
                    "notes": ["Automation is removing all human decision points."],
                    "constitutional_floors_checked": ["F05", "F08", "F10", "F13"],
                }
            ]
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMAS — Institutional Drift Check
# ═══════════════════════════════════════════════════════════════════════════════


class InstitutionalDrift(BaseModel):
    """777_TOPOLOGY: Reversible runtime diagnostic for extractive institutional drift."""

    inclusive_access: AccessLevel = Field(
        default=AccessLevel.HIGH,
        description="Degree of inclusive access to resources and decisions.",
    )
    extractive_capture: RiskBand = Field(
        default=RiskBand.LOW,
        description="Degree of extractive capture by dominant nodes.",
    )
    participation_width: ParticipationWidth = Field(
        default=ParticipationWidth.BROAD,
        description="Breadth of meaningful participation.",
    )
    innovation_rights: InnovationRights = Field(
        default=InnovationRights.DISTRIBUTED,
        description="Distribution of innovation and repair rights.",
    )
    appeal_path: AppealPath = Field(
        default=AppealPath.PRESENT,
        description="Presence of contestability and appeal mechanisms.",
    )
    elite_chokepoint_risk: RiskBand = Field(
        default=RiskBand.LOW,
        description="Risk that elites control critical chokepoints.",
    )
    sovereignty_integrity: SovereigntyIntegrity = Field(
        default=SovereigntyIntegrity.STRONG,
        description="Whether human veto is functional or decorative.",
    )
    verdict: InstitutionalVerdict = Field(
        default=InstitutionalVerdict.INCLUSIVE,
        description="Inclusive | mixed | extractive_drift | extractive.",
    )
    confidence: Confidence = Field(
        default=Confidence.LOW,
        description="Confidence in this estimate. Low until sensors are wired.",
    )
    notes: list[str] = Field(
        default_factory=list,
        description="Human-readable diagnostic notes.",
    )
    constitutional_floors_checked: list[str] = Field(
        default_factory=list,
        description="Which F-floor extensions were evaluated.",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "inclusive_access": "low",
                    "extractive_capture": "high",
                    "participation_width": "symbolic",
                    "innovation_rights": "captured",
                    "appeal_path": "absent",
                    "elite_chokepoint_risk": "high",
                    "sovereignty_integrity": "symbolic",
                    "verdict": "extractive",
                    "confidence": "medium",
                    "notes": ["Human veto exists only as rubber-stamp."],
                    "constitutional_floors_checked": ["F05", "F08", "F10", "F13"],
                }
            ]
        }
    }
