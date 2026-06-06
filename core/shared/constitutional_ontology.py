"""
arifOS Unified Constitutional Ontology
====================================

The canonical output contract that ALL domain modules (WELL, GEOX, WEALTH)
must emit before the kernel processes their output.

This is the semantic primitive layer that enables:
- Cross-domain validation
- Ontology conformance
- Kernel rejection of malformed payloads

Version: v1.0-FORGE
Author: arifOS Constitutional Kernel
DITEMPA BUKAN DIBERI 🔥
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator

# ============================================================================
# CANONICAL RISK LEVELS — Shared across all domains
# ============================================================================


class RiskLevel(str, Enum):
    """Universal risk classification. All domains MUST use these values."""

    LOW = "LOW"  # Reversible, no stakeholder impact
    MODERATE = "MODERATE"  # Partially reversible, minor impact
    HIGH = "HIGH"  # Irreversible potential, significant impact
    CRITICAL = "CRITICAL"  # Irreversible, major stakeholder harm
    UNKNOWN = "UNKNOWN"  # Cannot assess - requires escalation


class ConfidenceLevel(str, Enum):
    """Universal confidence semantics. Replaces ad-hoc confidence floats."""

    VERIFIED = "VERIFIED"  # Evidence chain complete, source confirmed
    INFERRED = "INFERRED"  # Logical deduction, plausible but unconfirmed
    ASSUMED = "ASSUMED"  # Heuristic, likely but unverified
    UNKNOWN = "UNKNOWN"  # Insufficient data


# ============================================================================
# FORMAL STATE MACHINE — Mandatory runtime states
# ============================================================================


class RuntimeState(str, Enum):
    """
    Mandatory runtime states. ALL execution flows through these states.

    Kernel enforces explicit transitions. No probabilistic routing for the
    state machine itself - that is deterministic by definition.
    """

    OBSERVE = "OBSERVE"  # Input received, gathering context
    ANALYZE = "ANALYZE"  # Processing, reasoning active
    SIMULATE = "SIMULATE"  # What-if projection
    AWAIT_APPROVAL = "AWAIT_APPROVAL"  # Blocked on human/governance
    EXECUTE = "EXECUTE"  # Action being performed
    VERIFY = "VERIFY"  # Post-action validation
    SEAL = "SEAL"  # Committed to ledger
    PAUSE = "PAUSE"  # Voluntary hold
    LOCKDOWN = "LOCKDOWN"  # Emergency freeze
    VOID = "VOID"  # Invalid state - reject immediately


# ============================================================================
# REVERSIBILITY CLASSIFICATION — Universal
# ============================================================================


class Reversibility(str, Enum):
    """
    All actions classified by reversibility.

    Kernel enforces policy based on this value.
    """

    REVERSIBLE = "REVERSIBLE"  # Full rollback possible
    PARTIALLY_REVERSIBLE = "PARTIALLY_REVERSIBLE"  # Some state change irreversible
    IRREVERSIBLE = "IRREVERSIBLE"  # No rollback possible - needs 888_HOLD
    UNKNOWN = "UNKNOWN"  # Cannot determine


# ============================================================================
# CONSTITUTIONAL ONTOLOGY PAYLOAD — The mandatory output contract
# ============================================================================


class ConstitutionalOntologyPayload(BaseModel):
    """
    The ONE canonical schema that ALL domain modules must emit.

    If a domain module cannot map its output to this schema, the kernel
    MUST reject the payload with VOID.

    Fields marked REQUIRED must be present in every output.
    Optional fields have defaults but should be populated.
    """

    # === REQUIRED FIELDS ===

    session_id: str = Field(..., description="Unique session identifier (UUIDv4)")

    trace_id: str = Field(..., description="Unique trace for this specific operation (UUIDv4)")

    state: RuntimeState = Field(..., description="Current runtime state")

    domain: str = Field(..., description="Source domain: WELL | GEOX | WEALTH | ARIFOS | UNKNOWN")

    # === SEMANTIC PRIMITIVES ===

    risk: RiskLevel = Field(default=RiskLevel.UNKNOWN, description="Universal risk classification")

    confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.UNKNOWN, description="Confidence semantics"
    )

    reversibility: Reversibility = Field(
        default=Reversibility.UNKNOWN, description="Reversibility classification"
    )

    # === EVIDENCE CHAIN ===

    evidence_chain: list[str] = Field(
        default_factory=list,
        description="List of evidence hashes supporting this output",
    )

    sources: list[str] = Field(default_factory=list, description="Source URIs or references")

    # === METRIC PRIMITIVES ===

    entropy_delta: float = Field(
        default=0.0, description="ΔS entropy change (positive = disorder increase)"
    )

    stability: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Stability score (1.0 = perfectly stable)",
    )

    # === FLOOR COMPLIANCE ===

    floors_passed: list[str] = Field(default_factory=list, description="F1-L13 floors that passed")

    floors_failed: list[str] = Field(default_factory=list, description="F1-L13 floors that failed")

    floors_pending: list[str] = Field(
        default_factory=list, description="F1-L13 floors awaiting evaluation"
    )

    # === IDENTITY & AUTHORITY ===

    actor_id: str = Field(default="anonymous", description="Identity of actor making the request")

    authority_level: str = Field(default="anonymous", description="Authority classification")

    # === OUTPUT CONTRACT ===

    observation: str = Field(default="", description="What was observed (OBSERVE state)")

    analysis: str = Field(default="", description="Analysis result (ANALYZE state)")

    assumption: str = Field(default="", description="Key assumptions made")

    action: str = Field(default="", description="Proposed/executed action")

    verdict: str = Field(
        default="SEAL",
        description="Constitutional verdict: SEAL | PROVISIONAL | PARTIAL | SABAR | HOLD | VOID",
    )

    # === TEMPORAL ===

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="ISO-8601 timestamp"
    )

    valid_until: Optional[datetime] = Field(
        default=None, description="TTL for this output's authority"
    )

    # === TRACEABILITY ===

    parent_trace_id: Optional[str] = Field(
        default=None, description="Parent trace for lineage tracking"
    )

    kernel_epoch: str = Field(default="v2026.05", description="Kernel version for compatibility")

    # === VALIDATORS ===

    @field_validator("domain")
    @classmethod
    def domain_must_be_valid(cls, v: str) -> str:
        valid = {
            "WELL",
            "GEOX",
            "WEALTH",
            "ARIFOS",
            "AAA",
            "APEX",
            "A-FORGE",
            "UNKNOWN",
        }
        if v.upper() not in valid:
            raise ValueError(f"Invalid domain: {v}. Must be one of {valid}")
        return v.upper()

    @field_validator("verdict")
    @classmethod
    def verdict_must_be_constitutional(cls, v: str) -> str:
        valid = {
            "SEAL",
            "PROVISIONAL",
            "PARTIAL",
            "SABAR",
            "HOLD",
            "HOLD_888",
            "VOID",
            "PAUSED",
        }
        if v.upper() not in valid:
            raise ValueError(f"Invalid verdict: {v}. Must be one of {valid}")
        return v.upper()

    @field_validator("risk")
    @classmethod
    def risk_must_be_constitutional(cls, v: RiskLevel) -> RiskLevel:
        if v == RiskLevel.UNKNOWN:
            return v  # Allow UNKNOWN but flag for escalation
        return v

    # === HELPERS ===

    def is_terminal(self) -> bool:
        """Check if this payload represents a terminal state."""
        return self.state in {
            RuntimeState.SEAL,
            RuntimeState.VOID,
            RuntimeState.LOCKDOWN,
        }

    def requires_approval(self) -> bool:
        """Check if this payload requires human approval."""
        if self.verdict in {"HOLD", "HOLD_888"}:
            return True
        if self.risk in {RiskLevel.CRITICAL, RiskLevel.HIGH}:
            return True
        if self.reversibility == Reversibility.IRREVERSIBLE:
            return True
        if self.state == RuntimeState.AWAIT_APPROVAL:
            return True
        return False

    def can_kernel_process(self) -> bool:
        """
        Check if kernel can process this payload.

        Returns False if:
        - Required fields are missing
        - Invalid state transition
        - Floor violation detected
        """
        if self.state == RuntimeState.VOID:
            return False
        if len(self.floors_failed) > 0:
            # Hard floors failed = cannot proceed
            hard_floors = {"F1", "F2", "F6", "L10", "L11", "L12", "L13"}
            if any(f in hard_floors for f in self.floors_failed):
                return False
        return True


# ============================================================================
# ONTOLOGY VALIDATOR — Rejects non-conformant payloads
# ============================================================================


class OntologyValidator:
    """
    Validates domain outputs against the constitutional ontology.

    Usage:
        validator = OntologyValidator()
        result = validator.validate(payload)
        if not result.valid:
            kernel.reject(result.error)
    """

    def __init__(self, strict: bool = True):
        self.strict = strict

    def validate(self, payload: dict | ConstitutionalOntologyPayload) -> "ValidationResult":
        """
        Validate a payload against the ontology.

        In strict mode: rejects payloads that cannot be mapped.
        In lenient mode: attempts coercion with warnings.
        """
        if isinstance(payload, dict):
            try:
                validated = ConstitutionalOntologyPayload(**payload)
            except Exception as e:
                return ValidationResult(
                    valid=False,
                    error=f"Ontology mapping failed: {str(e)}",
                    payload=None,
                )
        else:
            validated = payload

        # Check required fields
        if not validated.session_id:
            return ValidationResult(
                valid=False,
                error="Missing required field: session_id",
                payload=validated,
            )

        if not validated.trace_id:
            return ValidationResult(
                valid=False, error="Missing required field: trace_id", payload=validated
            )

        # Check state validity
        try:
            RuntimeState(validated.state.value)
        except ValueError:
            return ValidationResult(
                valid=False,
                error=f"Invalid runtime state: {validated.state}",
                payload=validated,
            )

        # Check if kernel can process
        if not validated.can_kernel_process():
            return ValidationResult(
                valid=False,
                error=f"Kernel cannot process: floors_failed={validated.floors_failed}, state={validated.state}",
                payload=validated,
            )

        return ValidationResult(valid=True, error=None, payload=validated)

    def enforce(
        self, payload: dict | ConstitutionalOntologyPayload
    ) -> ConstitutionalOntologyPayload:
        """
        Enforce ontology conformance. Raises if invalid.

        Use this when you want hard rejection vs soft validation.
        """
        result = self.validate(payload)
        if not result.valid:
            raise OntologyViolation(f"ONTOLOGY REJECTED: {result.error}")
        return result.payload


class ValidationResult(BaseModel):
    """Result of ontology validation."""

    valid: bool
    error: Optional[str] = None
    payload: Optional[ConstitutionalOntologyPayload] = None


class OntologyViolation(Exception):
    """Raised when ontology enforcement fails."""

    pass


# ============================================================================
# EXPORT PUBLIC API
# ============================================================================
__all__ = [
    "RiskLevel",
    "ConfidenceLevel",
    "RuntimeState",
    "Reversibility",
    "ConstitutionalOntologyPayload",
    "OntologyValidator",
    "ValidationResult",
    "OntologyViolation",
]
