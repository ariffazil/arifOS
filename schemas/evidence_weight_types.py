"""
arifOS EvidenceWeight Type System — No conclusion may claim greater
epistemic authority than its supporting evidence permits.

REALITY > EVERYTHING · Forged, Not Given

Replaces the text-based hierarchy in receipts with a hard type invariant:
  RAW_OBSERVATION > MEASURED_FACT > DERIVED_STATE > REASON_CODE > NARRATIVE_LABEL

becomes:

  EvidenceWeight: weight provenance × independence × freshness × integrity

The hierarchy is advisory, not absolute. Byzantine faults can make raw
observations less reliable than derived measurements. EvidenceWeight
captures this correctly.

Source: ChatGPT external analysis (2026-09-20) + 333-AGI synthesis
Status: PROPOSED — requires F13 ratification
"""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class EpistemicType(Enum):
    """
    Every consequential statement must belong to a type.
    No silent conversion between types. (W2)
    """

    OBSERVED = "OBSERVED"  # directly observed (file read, probe, curl)
    MEASURED = "MEASURED"  # instrument-verified, empirical
    DERIVED = "DERIVED"  # calculated from OBSERVED/MEASURED
    REMEMBERED = "REMEMBERED"  # from memory, with provenance (W12)
    REPORTED = "REPORTED"  # external claim, unverified (W13)
    PREDICTED = "PREDICTED"  # model prediction (W4: ≠ outcome)
    ASSUMED = "ASSUMED"  # working assumption, must be falsifiable
    CONTESTED = "CONTESTED"  # disputed, resolution pending
    UNKNOWN = "UNKNOWN"  # cannot witness (W4: must remain UNKNOWN)
    NORMATIVE = "NORMATIVE"  # value judgment, not fact (Facts ≠ Values)


class EvidenceWeight(Enum):
    """
    Weight of evidence supporting a claim.

    Hierarchy is advisory, not absolute. Byzantine faults can make
    raw observations less reliable than derived measurements.

    H01: Raw observation treated as infallible → FIX: EvidenceWeight
    H02: Confidence treated as truth → FIX: Weight ≠ confidence
    """

    BYZANTINE_PROVEN = 1.0  # signed, independent, fresh, integrity-verified
    MEASURED_FACT = 0.9  # directly measured, instrument-verified
    DERIVED = 0.8  # calculated from measured facts
    INTERPRETED = 0.6  # judgment call, requires review
    SPECULATIVE = 0.4  # hypothesis, capped confidence
    UNKNOWN = 0.0  # cannot witness
    STALE = -1.0  # once valid, now expired
    CONTRADICTED = -0.5  # contradicted by higher-weight evidence


@dataclass
class Provenance:
    """
    Every consequential claim retains provenance. (W3)

    Source: W3C PROV-O + arifOS synthesis
    """

    source: str  # where this came from
    agent: str  # who produced it
    process: str  # how it was produced
    time: str  # when (with uncertainty)
    version: str  # which version
    derivation: str  # how it was derived
    integrity: str  # hash/checksum
    freshness: str  # staleness status: LIVE/FRESH/STALE/EXPIRED
    counterevidence: list[str] = field(default_factory=list)
    supersedes: list[str] = field(default_factory=list)

    def is_fresh(self, policy_max_staleness: str) -> bool:
        """Check if this provenance satisfies freshness policy. (W6)"""
        freshness_order = {"LIVE": 0, "FRESH": 1, "STALE": 2, "EXPIRED": 3}
        return freshness_order.get(self.freshness, 99) <= freshness_order.get(
            policy_max_staleness, 0
        )


@dataclass
class Claim:
    """
    A consequential claim with full epistemic typing.

    Claim = (value, source, time, provenance, uncertainty, falsifier)

    W2: Epistemic typing
    W3: Provenance continuity
    W4: Uncertainty preservation
    W5: Contradiction preservation
    """

    value: str  # the claim content
    epistemic_type: EpistemicType  # what class of knowledge
    evidence_weight: EvidenceWeight  # how strong is the evidence
    provenance: Provenance  # full provenance chain
    uncertainty: float  # 0.0 = certain, 1.0 = maximally uncertain
    verification_condition: str  # what observation would verify this
    disconfirmation_condition: str  # what observation would disconfirm this
    authority_domain: str  # who has authority over this claim
    timestamp: str  # when this claim was made
    is_contested: bool = False  # W5: contradictions preserved
    contest_parties: list[str] = field(default_factory=list)

    def can_be_falsified(self) -> bool:
        """W4: UNKNOWN claims cannot be falsified. NORMATIVE claims require human judgment."""
        return self.epistemic_type not in (EpistemicType.UNKNOWN, EpistemicType.NORMATIVE)


@dataclass
class Contradiction:
    """
    A first-class contradiction. Never averaged, never silently resolved. (W5)

    H10: Contradictions silently averaged or overwritten → FIX: This class
    """

    id: str
    claim_a: str  # first claim
    claim_b: str  # contradicting claim
    source_a: str  # provenance of claim_a
    source_b: str  # provenance of claim_b
    weight_a: EvidenceWeight  # EvidenceWeight of claim_a
    weight_b: EvidenceWeight  # EvidenceWeight of claim_b
    precedence: str  # which has higher EvidenceWeight and why
    resolution: str  # OPEN / RESOLVED / SUPERSEDED / ABANDONED
    created_at: str  # when detected
    last_checked: str  # when last verified still open

    def __post_init__(self):
        """W5: Contradiction is permanent until explicitly resolved."""
        assert self.resolution in ("OPEN", "RESOLVED", "SUPERSEDED", "ABANDONED")
        if self.resolution == "OPEN":
            assert self.precedence != "", "OPEN contradiction must declare precedence"


@dataclass
class NegativeKnowledge:
    """
    What the system does NOT know. (Gate 1 from v2 init)

    An agent that doesn't know its ignorance is dangerous.
    """

    unmeasured_scalars: list[str]  # G, C_dark, W3 if unmeasured
    degraded_organs: list[str]  # which organs are down
    unknown_human_state: bool  # can we read Arif?
    unresolved_contradictions: int  # how many OPEN contradictions
    stale_data: list[str]  # what's older than TTL
    missing_witnesses: list[str]  # what lacks independent verification
    unverifiable_claims: list[str]  # what cannot be falsified
    clock_uncertainty_ms: int  # estimated clock uncertainty

    def total_unknowns(self) -> int:
        """Total count of unknowns across all categories."""
        return (
            len(self.unmeasured_scalars)
            + len(self.degraded_organs)
            + (1 if self.unknown_human_state else 0)
            + self.unresolved_contradictions
            + len(self.stale_data)
            + len(self.missing_witnesses)
            + len(self.unverifiable_claims)
        )


@dataclass
class ToolCapability:
    """
    Per-tool capability assessment. (CapabilityRoot)

    H06: Tool existence ≠ tool availability
    H07: Tool availability ≠ authority
    """

    name: str
    available: bool  # tool exists in registry
    reachable: bool  # endpoint responds
    healthy: bool  # passes health check
    authorized: bool  # current session authorized
    appropriate: bool  # matches task type
    side_effect: str  # NONE / REVERSIBLE / BOUNDED_EXTERNAL / IRREVERSIBLE
    reversible: bool  # can be undone
    cost: float  # estimated cost (tokens/money)
    freshness: str  # data staleness: LIVE/FRESH/STALE/EXPIRED
    evidence_weight: float  # EvidenceWeight of last probe (0.0-1.0)

    def is_usable(self) -> bool:
        """Tool is usable only if ALL conditions met."""
        return (
            self.available
            and self.reachable
            and self.healthy
            and self.authorized
            and self.appropriate
            and self.evidence_weight > 0.0
        )


@dataclass
class CapabilityRoot:
    """
    What actually works right now? (Root 7)

    Maps to A-FORGE tool registry + organ health + MCP server status.
    """

    tools: list[ToolCapability]
    mcp_servers: dict[str, str]  # name -> UP/DOWN/DEGRADED
    fallback_chains: dict[str, list[str]]  # tool -> fallback list
    cost_per_tool: dict[str, float]
    rate_limits: dict[str, str]

    def ready_tools(self) -> list[ToolCapability]:
        """Only tools that pass all capability checks."""
        return [t for t in self.tools if t.is_usable()]

    def held_tools(self) -> list[ToolCapability]:
        """Tools that exist but cannot be used."""
        return [t for t in self.tools if not t.is_usable()]


# ── Ashby's Law: Requisite Variety ──────────────────────────────────────────
# Constitution = constraints ≠ complete world model
# Federation supplies requisite variety:

VARIETY_MAP = {
    "arifOS": "Constraint / authority / adjudication",
    "CHRON": "Temporal variety",
    "FRAME": "Epistemic independence",
    "GEOX": "Earth-domain variety",
    "WEALTH": "Economic-domain variety",
    "WELL": "Biological/personal-state variety",
    "HERMES": "Human-meaning boundary",
    "A-FORGE": "Execution variety",
    "AAA": "Skill variety",
}
