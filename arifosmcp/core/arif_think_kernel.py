# arif_think_kernel.py — Constitutional Embedding for arif_think
# ═══════════════════════════════════════════════════════════════════════════════
#
# This file defines the invariants, entropy policy, reality stack, math axioms,
# symbolic code, and linguistic contract for arif_think.
#
# QUOTES ARE METADATA, NOT REASONING ENGINE.
# They ride in the philosophical_anchor envelope for human resonance.
# They NEVER enter reasoning, logic, 888_JUDGE deliberation, or VAULT999 sealing criteria.
#
# DITEMPA BUKAN DIBERI — Forged, Not Given
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# 1. CORE INVARIANTS (I1-I8)
# ═══════════════════════════════════════════════════════════════════════════════


class InvariantID(str, Enum):
    """Core invariants for arif_think."""

    I1_REVERSIBILITY = "I1_reversibility"
    I2_AUTHORITY_SEPARATION = "I2_authority_separation"
    I3_EVIDENCE_HONESTY = "I3_evidence_honesty"
    I4_ENTROPY_MINIMIZATION = "I4_entropy_minimization"
    I5_LIFECYCLE_DISCIPLINE = "I5_lifecycle_discipline"
    I6_SCHEMA_TRUTH = "I6_schema_truth"
    I7_DEGRADED_IS_NOT_SUCCESS = "I7_degraded_is_not_success"
    I8_QUOTES_DO_NOT_REASON = "I8_quotes_do_not_reason"


INVARIANTS: dict[str, dict[str, Any]] = {
    InvariantID.I1_REVERSIBILITY.value: {
        "rule": "Thinking is reversible. Execution is not.",
        "meaning": "arif_think may advise, compare, critique, and hypothesize, but must not execute, seal, delete, deploy, or approve.",
    },
    InvariantID.I2_AUTHORITY_SEPARATION.value: {
        "rule": "Mind does not judge. Judge does not execute. Vault does not think.",
        "mapping": {
            "arif_think": "reason",
            "arif_judge": "verdict",
            "arif_vault": "seal",
            "arif_forge": "execute",
        },
    },
    InvariantID.I3_EVIDENCE_HONESTY.value: {
        "rule": "No evidence, no verified claim.",
        "allowed_without_evidence": [
            "conceptual reasoning",
            "hypothesis",
            "architecture design",
            "critique",
        ],
        "forbidden_without_evidence": [
            "verified fact",
            "final verdict",
            "seal",
            "execution approval",
        ],
    },
    InvariantID.I4_ENTROPY_MINIMIZATION.value: {
        "rule": "Return only what changes the decision.",
        "remove_by_default": [
            "decorative quotes",
            "nine_signal",
            "philosophical_anchor",
            "full affordance contract",
            "stage theater",
        ],
    },
    InvariantID.I5_LIFECYCLE_DISCIPLINE.value: {
        "rule": "Respect initialize → initialized → tools/list → tools/call → result.",
        "meaning": "MCP is protocol flow, not magic plugin access.",
    },
    InvariantID.I6_SCHEMA_TRUTH.value: {
        "rule": "If the schema lies, the tool lies.",
        "meaning": "Inputs, outputs, enums, errors, and degraded states must be explicit.",
    },
    InvariantID.I7_DEGRADED_IS_NOT_SUCCESS.value: {
        "rule": "Empty HOLD is DEGRADED, not OK.",
        "meaning": "No useful reasoning means no success claim.",
    },
    InvariantID.I8_QUOTES_DO_NOT_REASON.value: {
        "rule": "A quote can anchor meaning, but cannot carry proof.",
        "meaning": "Quotes are metadata for human resonance, not reasoning inputs.",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# 2. ENTROPY POLICY
# ═══════════════════════════════════════════════════════════════════════════════


class EntropyPolicy:
    """Entropy management for arif_think output."""

    @staticmethod
    def lower_entropy_if(output: str, before: str) -> bool:
        """Check if output reduces entropy."""
        # Simple heuristic: shorter output with same information content
        return len(output) < len(before)

    @staticmethod
    def higher_entropy_if(output: str) -> bool:
        """Check if output increases entropy."""
        # Redundancy detection
        words = output.split()
        unique_ratio = len(set(words)) / max(len(words), 1)
        return unique_ratio < 0.6  # Too much repetition

    @staticmethod
    def operational_test(output: str) -> bool:
        """Final test: does output reduce confusion?"""
        # If output does not reduce confusion, arif_think failed.
        # This is a placeholder for more sophisticated confusion metrics.
        return len(output.strip()) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# 3. REALITY STACK
# ═══════════════════════════════════════════════════════════════════════════════


class RealityLayer(str, Enum):
    """Reality layers for evidence classification."""

    L1_GROUND_TRUTH = "L1_ground_truth"  # sealed, ratified, immutable receipt
    L2_VERIFIED_STATE = "L2_verified_state"  # live tool result, source, log, probe
    L3_CACHED_STATE = "L3_cached_state"  # memory or prior session
    L4_INFERRED = "L4_inferred"  # reasoning only


@dataclass
class EvidenceClaim:
    """A claim with evidence layer classification."""

    claim: str
    layer: RealityLayer
    confidence: float  # 0.0 to 1.0
    source: str = ""
    timestamp: str = ""

    def __post_init__(self):
        """Validate evidence layer constraints."""
        if self.layer == RealityLayer.L1_GROUND_TRUTH and not self.source:
            raise ValueError("L1_GROUND_TRUTH requires a source (sealed receipt)")
        if self.layer == RealityLayer.L2_VERIFIED_STATE and not self.source:
            raise ValueError("L2_VERIFIED_STATE requires a source (tool result, log)")


class RealityStack:
    """Reality stack for arif_think evidence management."""

    # Default evidence layer for arif_think
    DEFAULT_LAYER = RealityLayer.L4_INFERRED

    # Maximum confidence per layer
    MAX_CONFIDENCE = {
        RealityLayer.L1_GROUND_TRUTH: 1.0,
        RealityLayer.L2_VERIFIED_STATE: 0.90,
        RealityLayer.L3_CACHED_STATE: 0.75,
        RealityLayer.L4_INFERRED: 0.60,
    }

    @classmethod
    def validate_claim(cls, claim: EvidenceClaim) -> bool:
        """Validate that claim confidence does not exceed layer maximum."""
        max_conf = cls.MAX_CONFIDENCE.get(claim.layer, 0.5)
        return claim.confidence <= max_conf

    @classmethod
    def upgrade_layer(cls, current: RealityLayer, new_evidence: bool) -> RealityLayer:
        """Attempt to upgrade evidence layer based on new evidence."""
        layers = list(RealityLayer)
        current_idx = layers.index(current)
        if new_evidence and current_idx > 0:
            return layers[current_idx - 1]  # Move toward L1
        return current


# ═══════════════════════════════════════════════════════════════════════════════
# 4. MATH AXIOMS
# ═══════════════════════════════════════════════════════════════════════════════


class MathAxioms:
    """Mathematical axioms for arif_think decision-making."""

    @staticmethod
    def confidence(
        evidence_strength: float,
        reasoning_coherence: float,
        uncertainty_penalty: float,
        execution_risk_penalty: float,
    ) -> float:
        """
        C = f(E, R, U, X)
        Confidence as function of evidence, reasoning, uncertainty, and risk.
        """
        # Weighted combination with penalties
        raw = (
            0.4 * evidence_strength
            + 0.3 * reasoning_coherence
            - 0.2 * uncertainty_penalty
            - 0.1 * execution_risk_penalty
        )
        return max(0.0, min(1.0, raw))

    @staticmethod
    def entropy_change(entropy_before: float, entropy_after: float) -> float:
        """ΔS = S_after - S_before"""
        return entropy_after - entropy_before

    @staticmethod
    def risk(impact: float, irreversibility: float, uncertainty: float) -> float:
        """Risk = Impact × Irreversibility × Uncertainty"""
        return impact * irreversibility * uncertainty

    @staticmethod
    def confidence_cap(confidence: float, evidence_quality: float) -> float:
        """C_final <= C_evidence"""
        return min(confidence, evidence_quality)

    @staticmethod
    def best_path(
        clarity: float,
        reversibility: float,
        evidence_fit: float,
        risk: float,
    ) -> float:
        """BestPath = argmax(clarity + reversibility + evidence_fit - risk)"""
        return clarity + reversibility + evidence_fit - risk


# ═══════════════════════════════════════════════════════════════════════════════
# 5. SYMBOLIC CODE
# ═══════════════════════════════════════════════════════════════════════════════


class VerdictSymbol(str, Enum):
    """Verdict symbols for arif_think output."""

    THINK = "THINK"  # advisory reasoning
    HOLD = "HOLD"  # cannot proceed safely or honestly
    VOID = "VOID"  # request or output violates boundary
    ADVISORY = "ADVISORY"  # useful but non-binding reasoning
    DEGRADED = "DEGRADED"  # tool returned but did not complete useful cognition
    SEAL = "SEAL"  # owner: VAULT999 / judge path only — forbidden in arif_think


# The most important symbolic rule:
# THINK ≠ JUDGE ≠ SEAL ≠ EXECUTE


# ═══════════════════════════════════════════════════════════════════════════════
# 6. LINGUISTIC CONTRACT
# ═══════════════════════════════════════════════════════════════════════════════


class LinguisticLabel(str, Enum):
    """Linguistic labels for arif_think output."""

    CLAIM = "CLAIM"  # supported by evidence
    HYPOTHESIS = "HYPOTHESIS"  # possible explanation
    INFERENCE = "INFERENCE"  # reasoned from available input
    UNKNOWN = "UNKNOWN"  # not known
    ASSUMPTION = "ASSUMPTION"  # accepted temporarily
    NEXT_ACTION = "NEXT_ACTION"  # one reversible move


# Ban these from default output
BANNED_DEFAULT_LANGUAGE = [
    "SEAL",  # unless actual seal path occurred
    "VERIFIED_FACT",  # without evidence
    "SOVEREIGN",  # unless authority context matters
    "decorative quotes",
    "philosophical anchors",
    "fake precision complexity scores",
]


# ═══════════════════════════════════════════════════════════════════════════════
# 7. PHILOSOPHICAL QUOTES METADATA SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class QuoteMetadata:
    """Schema for philosophical quote metadata."""

    id: str
    quote: str
    author: str
    function: str  # humility | uncertainty | reversibility | evidence | restraint | courage
    use_when: list[str] = field(default_factory=list)
    must_not_be_used_when: list[str] = field(default_factory=list)

    def is_valid_for_context(self, context: str) -> bool:
        """Check if quote is valid for given context."""
        # Check forbidden contexts
        for forbidden in self.must_not_be_used_when:
            if forbidden.lower() in context.lower():
                return False
        return True


# Quote placement rules
QUOTE_PLACEMENT_RULES = {
    "allowed": True,
    "count": 33,
    "storage": "resource or metadata table",
    "default_output": False,
    "trigger_only_when": [
        "user asks for philosophy",
        "mode = reflect",
        "mode = teaching",
        "debug = true",
        "quote has functional role",
    ],
    "forbidden_when": [
        "debugging production failure",
        "compact mode",
        "evidence verification",
        "timeout recovery",
        "security/governance decision",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# 8. arif_think KERNEL EMBEDDING
# ═══════════════════════════════════════════════════════════════════════════════

ARIF_THINK_DOCTRINE = [
    "Think freely inside reversible bounds.",
    "Do not seal.",
    "Do not execute.",
    "Do not claim evidence not attached.",
    "Lower entropy.",
    "Return useful advisory reasoning.",
]


class LaneType(str, Enum):
    """Lane types for arif_think execution."""

    FAST = "fast"
    GUARDED = "guarded"


LANE_CONFIG = {
    LaneType.FAST: {
        "evidence_required": False,
        "session_required": False,
        "output": "compact",
        "verdicts": ["ADVISORY", "DEGRADED", "UNSAFE"],
    },
    LaneType.GUARDED: {
        "evidence_required": True,
        "session_required": True,
        "output": "audit",
        "verdicts": ["ADVISORY", "NEEDS_EVIDENCE", "DEGRADED", "UNSAFE"],
    },
}


FORBIDDEN_IN_ARIF_THINK = [
    "SEAL in arif_think",
    "decorative philosophy in default output",
    "verified fact without evidence",
    "execution authority",
]


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def check_invariant(invariant_id: InvariantID, context: dict[str, Any]) -> bool:
    """Check if an invariant is satisfied in the given context."""
    if invariant_id == InvariantID.I1_REVERSIBILITY:
        return context.get("is_reversible", False)
    elif invariant_id == InvariantID.I3_EVIDENCE_HONESTY:
        has_evidence = context.get("has_evidence", False)
        claim_type = context.get("claim_type", "")
        if claim_type in ["verified_fact", "final_verdict", "seal", "execution_approval"]:
            return has_evidence
        return True
    elif invariant_id == InvariantID.I4_ENTROPY_MINIMIZATION:
        output = context.get("output", "")
        return not EntropyPolicy.higher_entropy_if(output)
    elif invariant_id == InvariantID.I7_DEGRADED_IS_NOT_SUCCESS:
        return context.get("has_useful_reasoning", True)
    elif invariant_id == InvariantID.I8_QUOTES_DO_NOT_REASON:
        return not context.get("quote_in_reasoning_chain", False)
    return True


def validate_output(output: dict[str, Any]) -> list[str]:
    """Validate arif_think output against all invariants."""
    violations = []

    # I1: Check reversibility
    if output.get("is_irreversible", False):
        violations.append("I1: arif_think produced irreversible output")

    # I2: Check authority separation
    if output.get("verdict") == "SEAL":
        violations.append("I2: arif_think attempted SEAL (judge/vault only)")

    # I3: Check evidence honesty
    if output.get("claim_type") == "verified_fact" and not output.get("evidence"):
        violations.append("I3: Verified fact without evidence")

    # I4: Check entropy minimization
    if EntropyPolicy.higher_entropy_if(output.get("text", "")):
        violations.append("I4: Output increases entropy")

    # I7: Check degraded is not success
    if output.get("verdict") == "HOLD" and output.get("success", False):
        violations.append("I7: HOLD claimed as success")

    # I8: Check quotes do not reason
    if output.get("quote_in_reasoning", False):
        violations.append("I8: Quote used in reasoning chain")

    return violations


__all__ = [
    "InvariantID",
    "INVARIANTS",
    "EntropyPolicy",
    "RealityLayer",
    "EvidenceClaim",
    "RealityStack",
    "MathAxioms",
    "VerdictSymbol",
    "LinguisticLabel",
    "BANNED_DEFAULT_LANGUAGE",
    "QuoteMetadata",
    "QUOTE_PLACEMENT_RULES",
    "ARIF_THINK_DOCTRINE",
    "LaneType",
    "LANE_CONFIG",
    "FORBIDDEN_IN_ARIF_THINK",
    "check_invariant",
    "validate_output",
]
