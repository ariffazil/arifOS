"""
memory_scars.py — 777_FORGE ↔ Scar Detection for arifOS v38

Provides integration between the 777_FORGE pipeline stage and the
v38 Memory Write Policy Engine for scar/witness detection.

Key Functions:
- scars_detect_pattern(): Detect scar patterns in content
- scars_should_create_scar(): Determine if content warrants a scar
- scars_propose_witness(): Propose a witness record
- scars_compute_severity(): Compute severity score for detected pattern
- scars_log_detection(): Log scar detection for audit

Core Concept:
Scars are permanent records of significant events (failures, violations,
near-misses) that inform future decision-making. They are "institutional
memory" that helps the system learn from experience.

Per: docs/arifOS-MEMORY-FORGING-DEEPRESEARCH.md (v38)

Author: arifOS Project
Version: v38.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import logging
import re

# v38 Memory imports
from ..memory.policy import (
    MemoryWritePolicy,
)
from ..memory.bands import (
    BandName,
    MemoryBandRouter,
    MemoryEntry,
    WriteResult,
)
from ..memory.audit import (
    MemoryAuditLayer,
)

# Import shared utility to eliminate duplication
from .common_utils import compute_integration_evidence_hash


logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

class ScarType(str, Enum):
    """Types of scars that can be created."""
    FLOOR_VIOLATION = "FLOOR_VIOLATION"      # A floor check failed
    NEAR_MISS = "NEAR_MISS"                  # Close to violation
    AUTHORITY_BREACH = "AUTHORITY_BREACH"    # Authority boundary crossed
    PATTERN_REPEAT = "PATTERN_REPEAT"        # Repeated problematic pattern
    HARM_DETECTED = "HARM_DETECTED"          # Harmful content detected
    VOID_PATTERN = "VOID_PATTERN"            # Pattern leading to VOID
    SABAR_TRIGGER = "SABAR_TRIGGER"          # SABAR protocol triggered
    MANUAL_MARK = "MANUAL_MARK"              # Manually marked by human


class SeverityLevel(str, Enum):
    """Severity levels for scars."""
    LOW = "LOW"           # Minor issue, informational
    MEDIUM = "MEDIUM"     # Notable issue, should be tracked
    HIGH = "HIGH"         # Serious issue, requires attention
    CRITICAL = "CRITICAL" # Critical issue, may need intervention


# Severity weights for different scar types
SEVERITY_WEIGHTS: Dict[str, float] = {
    ScarType.FLOOR_VIOLATION.value: 0.8,
    ScarType.NEAR_MISS.value: 0.5,
    ScarType.AUTHORITY_BREACH.value: 0.9,
    ScarType.PATTERN_REPEAT.value: 0.6,
    ScarType.HARM_DETECTED.value: 0.95,
    ScarType.VOID_PATTERN.value: 0.7,
    ScarType.SABAR_TRIGGER.value: 0.85,
    ScarType.MANUAL_MARK.value: 0.5,
}

# Floor names for detection
FLOOR_NAMES = frozenset([
    "F1_amanah", "F2_truth", "F3_tri_witness", "F4_clarity",
    "F5_peace", "F6_empathy", "F7_humility", "F8_genius", "F9_dark",
])

# Patterns that indicate potential issues
HARM_PATTERNS = [
    r"(?i)\b(delete all|drop table|rm -rf|format|destroy)\b",
    r"(?i)\b(hack|exploit|bypass|circumvent)\b",
    r"(?i)\b(password|credential|secret|api.?key)\b",
    r"(?i)\b(injection|xss|csrf|sql)\b",
]

# Near-miss threshold (how close to floor violation)
NEAR_MISS_THRESHOLD = 0.05


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ScarDetectionContext:
    """Context for scar detection."""
    content: Dict[str, Any]
    verdict: str
    floor_scores: Dict[str, float] = field(default_factory=dict)
    writer_id: str = "777_FORGE"
    session_id: Optional[str] = None
    parent_entry_id: Optional[str] = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class DetectedPattern:
    """A detected scar pattern."""
    pattern_type: ScarType
    matched_text: str
    location: str
    confidence: float
    floor_affected: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScarProposal:
    """Proposal for creating a scar."""
    scar_type: ScarType
    severity: SeverityLevel
    severity_score: float
    description: str
    patterns_detected: List[DetectedPattern] = field(default_factory=list)
    floor_violations: List[str] = field(default_factory=list)
    evidence_hash: str = ""
    recommended_action: str = ""
    should_create: bool = True


@dataclass
class WitnessProposal:
    """Proposal for creating a witness record."""
    scar_id: str
    observation: str
    confidence: float
    supporting_evidence: List[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class ScarDetectionResult:
    """Result of scar detection."""
    patterns_found: List[DetectedPattern] = field(default_factory=list)
    scar_proposals: List[ScarProposal] = field(default_factory=list)
    witness_proposals: List[WitnessProposal] = field(default_factory=list)
    total_severity: float = 0.0
    highest_severity: SeverityLevel = SeverityLevel.LOW
    should_create_scar: bool = False
    reason: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class ScarLogEntry:
    """Log entry for scar detection."""
    timestamp: str
    scar_type: str
    severity: str
    patterns_count: int
    created: bool
    reason: str


# =============================================================================
# MEMORY SCARS INTEGRATION CLASS
# =============================================================================

class MemoryScarsIntegration:
    """
    Integrates 777_FORGE stage with v38 Memory Write Policy Engine for scars.

    Responsibilities:
    1. Detect patterns that warrant scar creation
    2. Determine if content should create a scar
    3. Propose witness records for soft evidence
    4. Compute severity scores for detected patterns
    5. Log all scar detections for audit

    Usage:
        scars_integration = MemoryScarsIntegration(
            write_policy=MemoryWritePolicy(),
            band_router=MemoryBandRouter(),
        )

        # Detect patterns
        result = scars_integration.detect_patterns(
            ScarDetectionContext(
                content={"response": "..."},
                verdict="PARTIAL",
                floor_scores={"F2_truth": 0.95},
            )
        )
    """

    def __init__(
        self,
        write_policy: Optional[MemoryWritePolicy] = None,
        band_router: Optional[MemoryBandRouter] = None,
        audit_layer: Optional[MemoryAuditLayer] = None,
    ):
        """
        Initialize the scars integration.

        Args:
            write_policy: Memory write policy
            band_router: Memory band router
            audit_layer: Audit layer
        """
        self.write_policy = write_policy or MemoryWritePolicy()
        self.band_router = band_router or MemoryBandRouter()
        self.audit_layer = audit_layer or MemoryAuditLayer()
        self._detection_log: List[ScarLogEntry] = []
        self._compiled_patterns = [re.compile(p) for p in HARM_PATTERNS]

    # =========================================================================
    # CORE DETECTION METHODS
    # =========================================================================

    def detect_patterns(
        self,
        context: ScarDetectionContext,
    ) -> ScarDetectionResult:
        """
        Detect scar patterns in content.

        Args:
            context: Detection context

        Returns:
            ScarDetectionResult with detected patterns
        """
        result = ScarDetectionResult()
        patterns: List[DetectedPattern] = []

        # Check for floor violations
        floor_patterns = self._detect_floor_violations(context.floor_scores)
        patterns.extend(floor_patterns)

        # Check for near-misses
        near_miss_patterns = self._detect_near_misses(context.floor_scores)
        patterns.extend(near_miss_patterns)

        # Check for harm patterns in content
        content_str = str(context.content)
        harm_patterns = self._detect_harm_patterns(content_str)
        patterns.extend(harm_patterns)

        # Check verdict-based patterns
        verdict_patterns = self._detect_verdict_patterns(context.verdict)
        patterns.extend(verdict_patterns)

        result.patterns_found = patterns

        # Compute overall severity
        if patterns:
            severity_scores = [p.confidence * SEVERITY_WEIGHTS.get(p.pattern_type.value, 0.5) for p in patterns]
            result.total_severity = sum(severity_scores) / len(severity_scores)
            result.highest_severity = self._compute_severity_level(max(severity_scores) if severity_scores else 0)

        # Determine if scar should be created
        result.should_create_scar = len(patterns) > 0 and result.total_severity >= 0.3

        # Generate proposals
        if result.should_create_scar:
            result.scar_proposals = self._generate_scar_proposals(context, patterns)
            result.witness_proposals = self._generate_witness_proposals(context, patterns)
            result.reason = f"Detected {len(patterns)} patterns with severity {result.total_severity:.2f}"
        else:
            result.reason = "No significant patterns detected"

        self._log_detection(result)

        return result

    def should_create_scar(
        self,
        context: ScarDetectionContext,
    ) -> Tuple[bool, str, float]:
        """
        Determine if content warrants scar creation.

        Args:
            context: Detection context

        Returns:
            Tuple of (should_create, reason, severity_score)
        """
        result = self.detect_patterns(context)
        return (
            result.should_create_scar,
            result.reason,
            result.total_severity,
        )

    def propose_witness(
        self,
        context: ScarDetectionContext,
        scar_id: str,
        observation: str,
    ) -> WitnessProposal:
        """
        Propose a witness record for soft evidence.

        Args:
            context: Detection context
            scar_id: Associated scar ID
            observation: Witness observation

        Returns:
            WitnessProposal
        """
        # Compute confidence based on floor scores
        avg_floor_score = sum(context.floor_scores.values()) / max(len(context.floor_scores), 1)
        confidence = min(avg_floor_score, 0.85)  # Cap at 0.85 for witnesses

        return WitnessProposal(
            scar_id=scar_id,
            observation=observation,
            confidence=confidence,
            supporting_evidence=list(context.floor_scores.keys()),
        )

    def compute_severity(
        self,
        patterns: List[DetectedPattern],
    ) -> Tuple[SeverityLevel, float]:
        """
        Compute severity for detected patterns.

        Args:
            patterns: List of detected patterns

        Returns:
            Tuple of (SeverityLevel, severity_score)
        """
        if not patterns:
            return SeverityLevel.LOW, 0.0

        severity_scores = [
            p.confidence * SEVERITY_WEIGHTS.get(p.pattern_type.value, 0.5)
            for p in patterns
        ]

        max_score = max(severity_scores)
        level = self._compute_severity_level(max_score)

        return level, max_score

    def create_scar(
        self,
        context: ScarDetectionContext,
        proposal: ScarProposal,
    ) -> WriteResult:
        """
        Create a scar in the WITNESS band.

        Args:
            context: Detection context
            proposal: Scar proposal

        Returns:
            WriteResult from band router
        """
        # Compute evidence hash
        evidence_hash = compute_integration_evidence_hash(
            verdict=context.verdict,
            content=context.content,
            floor_scores=context.floor_scores,
            evidence_sources=[p.matched_text for p in proposal.patterns_detected],
        )

        # Build scar entry
        scar_content = {
            "scar_type": proposal.scar_type.value,
            "severity": proposal.severity.value,
            "severity_score": proposal.severity_score,
            "description": proposal.description,
            "patterns": [
                {
                    "type": p.pattern_type.value,
                    "matched": p.matched_text,
                    "location": p.location,
                    "confidence": p.confidence,
                }
                for p in proposal.patterns_detected
            ],
            "floor_violations": proposal.floor_violations,
            "recommended_action": proposal.recommended_action,
            "parent_content": context.content,
        }

        entry = MemoryEntry(
            entry_id="",  # Will be generated
            band=BandName.WITNESS.value,
            verdict=context.verdict,
            content=scar_content,
            writer_id=context.writer_id,
            evidence_hash=evidence_hash,
            timestamp=context.timestamp,
            metadata={
                "scar_type": proposal.scar_type.value,
                "severity": proposal.severity.value,
                "session_id": context.session_id,
                "parent_entry_id": context.parent_entry_id,
            },
        )

        return self.band_router.write(
            band=BandName.WITNESS,
            entry=entry,
            verdict=context.verdict,
            writer_id=context.writer_id,
        )

    # =========================================================================
    # LOGGING
    # =========================================================================

    def log_detection(
        self,
        result: ScarDetectionResult,
    ) -> None:
        """
        Explicitly log a scar detection for audit.

        Args:
            result: Detection result
        """
        self._log_detection(result)

    def get_detection_log(self) -> List[ScarLogEntry]:
        """Return the detection log."""
        return list(self._detection_log)

    def clear_detection_log(self) -> None:
        """Clear the detection log."""
        self._detection_log.clear()

    # =========================================================================
    # INTERNAL METHODS
    # =========================================================================

    def _detect_floor_violations(
        self,
        floor_scores: Dict[str, float],
    ) -> List[DetectedPattern]:
        """Detect floor violations from scores."""
        patterns = []

        # Floor thresholds
        thresholds = {
            "F1_amanah": None,  # Boolean, handled separately
            "F2_truth": 0.99,
            "F3_tri_witness": 0.95,
            "F4_clarity": 0.0,  # ΔS >= 0
            "F5_peace": 1.0,
            "F6_empathy": 0.95,
            "F7_humility": (0.03, 0.05),  # Range
            "F8_genius": 0.80,
            "F9_dark": 0.30,  # Must be BELOW
        }

        for floor, score in floor_scores.items():
            floor_key = floor.lower().replace(" ", "_")
            threshold = thresholds.get(floor_key)

            if threshold is None:
                continue

            is_violation = False
            if floor_key == "F7_humility":
                # Range check
                low, high = threshold
                is_violation = score < low or score > high
            elif floor_key == "F9_dark":
                # Must be below threshold
                is_violation = score >= threshold
            else:
                # Must be above or equal to threshold
                is_violation = score < threshold

            if is_violation:
                patterns.append(DetectedPattern(
                    pattern_type=ScarType.FLOOR_VIOLATION,
                    matched_text=f"{floor}={score}",
                    location="floor_scores",
                    confidence=0.95,
                    floor_affected=floor,
                    metadata={"threshold": threshold, "actual": score},
                ))

        return patterns

    def _detect_near_misses(
        self,
        floor_scores: Dict[str, float],
    ) -> List[DetectedPattern]:
        """Detect near-miss patterns from floor scores."""
        patterns = []

        thresholds = {
            "F2_truth": 0.99,
            "F3_tri_witness": 0.95,
            "F5_peace": 1.0,
            "F6_empathy": 0.95,
            "F8_genius": 0.80,
        }

        for floor, score in floor_scores.items():
            floor_key = floor.lower().replace(" ", "_")
            threshold = thresholds.get(floor_key)

            if threshold is None:
                continue

            # Check if close to threshold but passing
            margin = score - threshold
            if 0 <= margin < NEAR_MISS_THRESHOLD:
                patterns.append(DetectedPattern(
                    pattern_type=ScarType.NEAR_MISS,
                    matched_text=f"{floor}={score} (margin: {margin:.3f})",
                    location="floor_scores",
                    confidence=0.7,
                    floor_affected=floor,
                    metadata={"threshold": threshold, "margin": margin},
                ))

        return patterns

    def _detect_harm_patterns(
        self,
        content: str,
    ) -> List[DetectedPattern]:
        """Detect harm patterns in content text."""
        patterns = []

        for compiled_pattern in self._compiled_patterns:
            matches = compiled_pattern.findall(content)
            for match in matches:
                patterns.append(DetectedPattern(
                    pattern_type=ScarType.HARM_DETECTED,
                    matched_text=match if isinstance(match, str) else match[0],
                    location="content",
                    confidence=0.8,
                    metadata={"pattern": compiled_pattern.pattern},
                ))

        return patterns

    def _detect_verdict_patterns(
        self,
        verdict: str,
    ) -> List[DetectedPattern]:
        """Detect patterns based on verdict."""
        patterns = []
        verdict_upper = verdict.upper()

        if verdict_upper == "VOID":
            patterns.append(DetectedPattern(
                pattern_type=ScarType.VOID_PATTERN,
                matched_text=f"Verdict: {verdict}",
                location="verdict",
                confidence=0.9,
            ))
        elif verdict_upper == "SABAR":
            patterns.append(DetectedPattern(
                pattern_type=ScarType.SABAR_TRIGGER,
                matched_text=f"Verdict: {verdict}",
                location="verdict",
                confidence=0.95,
            ))

        return patterns

    def _compute_severity_level(
        self,
        score: float,
    ) -> SeverityLevel:
        """Compute severity level from score."""
        if score >= 0.8:
            return SeverityLevel.CRITICAL
        elif score >= 0.6:
            return SeverityLevel.HIGH
        elif score >= 0.3:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW

    def _generate_scar_proposals(
        self,
        context: ScarDetectionContext,
        patterns: List[DetectedPattern],
    ) -> List[ScarProposal]:
        """Generate scar proposals from detected patterns."""
        proposals = []

        # Group patterns by type
        by_type: Dict[ScarType, List[DetectedPattern]] = {}
        for p in patterns:
            by_type.setdefault(p.pattern_type, []).append(p)

        for scar_type, type_patterns in by_type.items():
            severity_level, severity_score = self.compute_severity(type_patterns)

            floor_violations = [
                p.floor_affected
                for p in type_patterns
                if p.floor_affected
            ]

            proposals.append(ScarProposal(
                scar_type=scar_type,
                severity=severity_level,
                severity_score=severity_score,
                description=f"Detected {len(type_patterns)} {scar_type.value} pattern(s)",
                patterns_detected=type_patterns,
                floor_violations=floor_violations,
                evidence_hash="",  # Computed on creation
                recommended_action=self._get_recommended_action(scar_type, severity_level),
                should_create=True,
            ))

        return proposals

    def _generate_witness_proposals(
        self,
        context: ScarDetectionContext,
        patterns: List[DetectedPattern],
    ) -> List[WitnessProposal]:
        """Generate witness proposals from detected patterns."""
        proposals = []

        for pattern in patterns:
            if pattern.confidence >= 0.6:  # Only high-confidence patterns
                proposals.append(WitnessProposal(
                    scar_id="",  # Set when scar is created
                    observation=f"{pattern.pattern_type.value}: {pattern.matched_text}",
                    confidence=pattern.confidence,
                    supporting_evidence=[pattern.location],
                ))

        return proposals

    def _get_recommended_action(
        self,
        scar_type: ScarType,
        severity: SeverityLevel,
    ) -> str:
        """Get recommended action for scar type and severity."""
        actions = {
            (ScarType.FLOOR_VIOLATION, SeverityLevel.CRITICAL): "Immediate review required",
            (ScarType.FLOOR_VIOLATION, SeverityLevel.HIGH): "Review within 24 hours",
            (ScarType.AUTHORITY_BREACH, SeverityLevel.CRITICAL): "Human intervention required",
            (ScarType.HARM_DETECTED, SeverityLevel.HIGH): "Content review needed",
            (ScarType.SABAR_TRIGGER, SeverityLevel.CRITICAL): "Protocol review required",
        }

        return actions.get(
            (scar_type, severity),
            "Monitor and track pattern frequency"
        )

    def _log_detection(
        self,
        result: ScarDetectionResult,
    ) -> None:
        """Log a detection result."""
        if result.scar_proposals:
            for proposal in result.scar_proposals:
                entry = ScarLogEntry(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    scar_type=proposal.scar_type.value,
                    severity=proposal.severity.value,
                    patterns_count=len(proposal.patterns_detected),
                    created=proposal.should_create,
                    reason=proposal.description,
                )
                self._detection_log.append(entry)
        else:
            entry = ScarLogEntry(
                timestamp=datetime.now(timezone.utc).isoformat(),
                scar_type="NONE",
                severity="NONE",
                patterns_count=len(result.patterns_found),
                created=False,
                reason=result.reason,
            )
            self._detection_log.append(entry)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def scars_detect_pattern(
    content: Dict[str, Any],
    verdict: str,
    floor_scores: Optional[Dict[str, float]] = None,
) -> ScarDetectionResult:
    """
    Detect scar patterns in content.

    Args:
        content: Content to analyze
        verdict: The verdict
        floor_scores: Floor scores

    Returns:
        ScarDetectionResult
    """
    integration = MemoryScarsIntegration()
    context = ScarDetectionContext(
        content=content,
        verdict=verdict,
        floor_scores=floor_scores or {},
    )
    return integration.detect_patterns(context)


def scars_should_create_scar(
    content: Dict[str, Any],
    verdict: str,
    floor_scores: Optional[Dict[str, float]] = None,
) -> Tuple[bool, str, float]:
    """
    Check if content should create a scar.

    Args:
        content: Content to analyze
        verdict: The verdict
        floor_scores: Floor scores

    Returns:
        Tuple of (should_create, reason, severity)
    """
    integration = MemoryScarsIntegration()
    context = ScarDetectionContext(
        content=content,
        verdict=verdict,
        floor_scores=floor_scores or {},
    )
    return integration.should_create_scar(context)


def scars_propose_witness(
    content: Dict[str, Any],
    verdict: str,
    scar_id: str,
    observation: str,
    floor_scores: Optional[Dict[str, float]] = None,
) -> WitnessProposal:
    """
    Propose a witness record.

    Args:
        content: Content context
        verdict: The verdict
        scar_id: Associated scar ID
        observation: Witness observation
        floor_scores: Floor scores

    Returns:
        WitnessProposal
    """
    integration = MemoryScarsIntegration()
    context = ScarDetectionContext(
        content=content,
        verdict=verdict,
        floor_scores=floor_scores or {},
    )
    return integration.propose_witness(context, scar_id, observation)


def scars_compute_severity(
    patterns: List[DetectedPattern],
) -> Tuple[SeverityLevel, float]:
    """
    Compute severity for detected patterns.

    Args:
        patterns: Detected patterns

    Returns:
        Tuple of (SeverityLevel, score)
    """
    integration = MemoryScarsIntegration()
    return integration.compute_severity(patterns)


def scars_log_detection(
    result: ScarDetectionResult,
) -> None:
    """
    Log a detection result.

    Args:
        result: Detection result
    """
    integration = MemoryScarsIntegration()
    integration.log_detection(result)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "ScarType",
    "SeverityLevel",
    "SEVERITY_WEIGHTS",
    "FLOOR_NAMES",
    "NEAR_MISS_THRESHOLD",
    # Data classes
    "ScarDetectionContext",
    "DetectedPattern",
    "ScarProposal",
    "WitnessProposal",
    "ScarDetectionResult",
    "ScarLogEntry",
    # Main class
    "MemoryScarsIntegration",
    # Convenience functions
    "scars_detect_pattern",
    "scars_should_create_scar",
    "scars_propose_witness",
    "scars_compute_severity",
    "scars_log_detection",
]
