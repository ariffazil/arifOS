"""
arifosmcp/runtime/sensing_protocol.py — Governed Sensing Layer
═══════════════════════════════════════════════════════════════════════════════

Constitutional sensing protocol for arifos.sense.

Implements the 8-stage sensing flow:
    1. PARSE    → Extract entities, intent, time-dependence, risk
    2. CLASSIFY → Route to truth-class lane (A-E)
    3. DECIDE   → Whether search is needed
    4. PLAN     → Build evidence hierarchy
    5. SENSE    → Execute constrained retrieval
    6. NORMALIZE→ Convert to structured claims
    7. GATE     → Confidence/ambiguity checks
    8. HANDOFF  → Pass clean packet downstream

Author: Arif (Sovereign Architect)
Constitutional Seal: 999_VALIDATOR
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS — Truth Classification
# ═══════════════════════════════════════════════════════════════════════════════

class TruthClass(str, Enum):
    """The five lanes of truth classification."""
    ABSOLUTE_INVARIANT = "absolute_invariant"    # Lane A: Logic, math, physics
    CONDITIONAL = "conditional"                   # Lane B: Frame-dependent truths
    OPERATIONAL = "operational"                   # Lane C: Strategy, design, economics
    TIME_SENSITIVE = "time_sensitive"             # Lane D: Current events, live data
    HOLD = "hold"                                 # Lane E: Ambiguity too high


class ClaimType(str, Enum):
    """What kind of claim is being made."""
    DEFINITION = "definition"
    STATUS = "status"
    PREDICTION = "prediction"
    COMPARISON = "comparison"
    INSTRUCTION = "instruction"
    UNKNOWN = "unknown"


class TimeClass(str, Enum):
    """Temporal classification of the query."""
    TIMELESS = "timeless"         # Physics, math, definitions
    DATED = "dated"               # Historical facts
    LIVE = "live"                 # Current state (prices, roles, weather)
    RECENT = "recent"             # Within last ~30 days


class RiskClass(str, Enum):
    """Consequence level of the query."""
    LOW = "low"           # Informational
    MEDIUM = "medium"     # Operational impact
    HIGH = "high"         # Significant consequences
    CRITICAL = "critical" # Irreversible or safety-critical


class EvidenceRank(int, Enum):
    """5-tier evidence hierarchy."""
    DIRECT_MEASUREMENT = 1    # Primary data, sensors
    OFFICIAL_SOURCE = 2       # Laws, releases, policies
    TECHNICAL_DOCS = 3        # Specs, standards, methods
    SECONDARY_REPORTING = 4   # Reputable summaries
    SOCIAL_CHATTER = 5        # SEO, weak signal


class UncertaintyLevel(str, Enum):
    """Epistemic confidence bands."""
    LOW = "low"         # Well-grounded, multiple sources agree
    MODERATE = "moderate"  # Some gaps or single-source
    HIGH = "high"       # Significant ambiguity
    UNKNOWN = "unknown" # Cannot assess


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES — Sense Packet Structure
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Entity:
    """What is being asked about."""
    name: str
    type: str  # "organization", "person", "concept", "system", etc.
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class AmbiguityStatus:
    """Detected ambiguity and resolution."""
    detected: bool
    note: str | None = None
    candidate_interpretations: list[str] = field(default_factory=list)
    assumption_chosen: str | None = None
    risk_of_misclassification: str | None = None


@dataclass
class EvidencePlan:
    """Planned evidence gathering strategy."""
    preferred_sources: list[str] = field(default_factory=list)
    minimum_rank: EvidenceRank = EvidenceRank.SECONDARY_REPORTING
    freshness_hours: int | None = None  # None = timeless
    conflict_resolution: str = "source_hierarchy"  # How to handle conflicts
    minimum_evidence_threshold: int = 2


@dataclass
class ConflictCheck:
    """Status of source conflict detection."""
    status: str  # "pending", "none", "detected", "resolved"
    conflicts: list[dict] = field(default_factory=list)
    resolution_strategy: str | None = None


@dataclass
class SensePacket:
    """
    The governed sensing output — normalized observation package.
    
    This is what arifos.sense returns after constitutional processing.
    Not raw search results. Not links. Structured, bounded evidence.
    """
    # Input trace
    query: str
    query_triage: QueryTriage | None = None
    
    # Classification
    truth_class: TruthClass
    claim_type: ClaimType
    time_class: TimeClass
    
    # Decision
    search_required: bool
    reasoning_basis: list[str] = field(default_factory=list)  # If no search needed
    
    # Evidence plan (if search required)
    evidence_plan: EvidencePlan | None = None
    
    # Results (if search executed)
    evidence_bundle: list[dict] = field(default_factory=list)
    grounded_facts: list[str] = field(default_factory=list)
    
    # Quality gates
    ambiguity: AmbiguityStatus = field(default_factory=lambda: AmbiguityStatus(detected=False))
    conflict_check: ConflictCheck = field(default_factory=lambda: ConflictCheck(status="pending"))
    uncertainty: UncertaintyLevel = UncertaintyLevel.UNKNOWN
    
    # Temporal
    temporal_scope: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Handoff
    handoff: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for JSON serialization."""
        from dataclasses import asdict
        result = asdict(self)
        # Convert enums to strings
        result["truth_class"] = self.truth_class.value
        result["claim_type"] = self.claim_type.value
        result["time_class"] = self.time_class.value
        result["uncertainty"] = self.uncertainty.value
        if self.evidence_plan:
            result["evidence_plan"]["minimum_rank"] = self.evidence_plan.minimum_rank.value
        return result


@dataclass
class QueryTriage:
    """Stage 1: Parsed query structure."""
    entity: Entity | None = None
    claim_type: ClaimType = ClaimType.UNKNOWN
    time_class: TimeClass = TimeClass.TIMELESS
    domain: str = "unknown"  # physics, law, finance, software, geopolitics
    risk_class: RiskClass = RiskClass.LOW
    decision_proximity: str = "informative"  # or "decision_critical"
    detected_keywords: list[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# INVARIANT KNOWLEDGE BASE — What Not to Search
# ═══════════════════════════════════════════════════════════════════════════════

# Absolute invariants — first principles, no search needed
ABSOLUTE_INVARIANTS = {
    "physics": [
        "entropy", "thermodynamics", "conservation of energy", "speed of light",
        "gravity", "relativity", "quantum mechanics", "second law",
    ],
    "math": [
        "nash equilibrium", "entropy (information)", "pythagorean theorem",
        "turing completeness", "complexity", "algorithm",
    ],
    "logic": [
        "syllogism", "deductive reasoning", "inductive reasoning",
        "occam's razor", "falsification", "null hypothesis",
    ],
    "definitions": [
        "is defined as", "what is the meaning of", "definition of",
    ],
}

# Time-sensitive keywords — live search required
TIME_SENSITIVE_KEYWORDS = {
    "current": ["current", "now", "today", "latest", "recent"],
    "price": ["price", "cost", "rate", "value of", "trading at"],
    "role": ["ceo", "cto", "president", "leader", "head of", "minister"],
    "event": ["election", "war", "outage", "crash", "breach", "release"],
    "weather": ["weather", "temperature", "forecast"],
}

# Domain-specific freshness requirements (hours)
FRESHNESS_REQUIREMENTS = {
    "software": 168,      # 1 week for versions
    "security": 24,       # 1 day for CVEs
    "finance": 1,         # 1 hour for prices
    "news": 4,            # 4 hours for news
    "weather": 1,         # 1 hour
}


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 1: PARSE — Query Triage
# ═══════════════════════════════════════════════════════════════════════════════

def parse_query(query: str, session_context: dict | None = None) -> QueryTriage:
    """
    Parse the query into structured triage fields.
    
    Extracts:
        - entity: What is being asked about
        - claim_type: definition/status/prediction/comparison/instruction
        - time_class: timeless/dated/live/recent
        - domain: physics/law/finance/software/geopolitics
        - risk_class: low/medium/high/critical
        - decision_proximity: informative or decision-critical
    """
    q_lower = query.lower()
    triage = QueryTriage()
    
    # Detect claim type
    if any(w in q_lower for w in ["what is", "define", "meaning of", "definition"]):
        triage.claim_type = ClaimType.DEFINITION
    elif any(w in q_lower for w in ["current", "status", "state of", "who is", "where is"]):
        triage.claim_type = ClaimType.STATUS
    elif any(w in q_lower for w in ["will", "predict", "forecast", "future"]):
        triage.claim_type = ClaimType.PREDICTION
    elif any(w in q_lower for w in ["compare", "vs", "versus", "difference between", "better"]):
        triage.claim_type = ClaimType.COMPARISON
    elif any(w in q_lower for w in ["how to", "steps to", "guide", "tutorial"]):
        triage.claim_type = ClaimType.INSTRUCTION
    
    # Detect time class
    if any(w in q_lower for w in TIME_SENSITIVE_KEYWORDS["current"]):
        triage.time_class = TimeClass.LIVE
    elif any(w in q_lower for w in ["yesterday", "last week", "ago", "previous"]):
        triage.time_class = TimeClass.DATED
    elif any(w in q_lower for w in ["this week", "this month", "recently"]):
        triage.time_class = TimeClass.RECENT
    
    # Detect domain
    domains = {
        "physics": ["entropy", "energy", "force", "quantum", "relativity", "thermodynamics"],
        "math": ["equation", "theorem", "proof", "calculate", "formula", "algorithm"],
        "law": ["law", "legal", "regulation", "statute", "jurisdiction", "court"],
        "finance": ["price", "stock", "market", "trading", "crypto", "investment"],
        "software": ["code", "api", "library", "framework", "version", "github"],
        "geopolitics": ["war", "election", "country", "government", "policy", "treaty"],
    }
    for domain, keywords in domains.items():
        if any(k in q_lower for k in keywords):
            triage.domain = domain
            break
    
    # Detect risk class based on decision proximity
    critical_terms = ["delete", "production", "deploy", "irreversible", "money", "transfer"]
    if any(t in q_lower for t in critical_terms):
        triage.risk_class = RiskClass.HIGH
        triage.decision_proximity = "decision_critical"
    
    # Extract entity (simple heuristic: proper nouns after "of", "for", "about")
    entity_match = re.search(r'(?:of|for|about|is)\s+([A-Z][a-zA-Z\s]+?)(?:\?|$|\s+(?:today|now|currently))', query)
    if entity_match:
        triage.entity = Entity(name=entity_match.group(1).strip(), type="unknown")
    
    triage.detected_keywords = [w for w in q_lower.split() if len(w) > 3]
    return triage


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 2: CLASSIFY — Truth-Class Router
# ═══════════════════════════════════════════════════════════════════════════════

def classify_truth(triage: QueryTriage, query: str) -> TruthClass:
    """
    Route the query to the appropriate truth-class lane.
    
    Lanes:
        A — ABSOLUTE_INVARIANT: Offline reasoning only
        B — CONDITIONAL: Frame-dependent (jurisdiction, version)
        C — OPERATIONAL: Strategy, governance (principles + evidence)
        D — TIME_SENSITIVE: Live search required
        E — HOLD: Too ambiguous
    """
    q_lower = query.lower()
    
    # Check for absolute invariants (Lane A)
    for domain, terms in ABSOLUTE_INVARIANTS.items():
        if any(t in q_lower for t in terms):
            # But check if asking about "current understanding of..."
            if triage.time_class != TimeClass.LIVE:
                return TruthClass.ABSOLUTE_INVARIANT
    
    # Check for time-sensitivity (Lane D)
    if triage.time_class == TimeClass.LIVE:
        return TruthClass.TIME_SENSITIVE
    
    # Check for conditional/frame-dependent (Lane B)
    conditional_markers = [
        "in the us", "in malaysia", "under gdpr", "according to",
        "in python", "in version", "based on", "depending on",
    ]
    if any(m in q_lower for m in conditional_markers):
        return TruthClass.CONDITIONAL
    
    # Check for operational (Lane C)
    operational_markers = [
        "best practice", "should i", "recommend", "strategy",
        "tradeoff", "trade-off", "architecture", "design",
    ]
    if any(m in q_lower for m in operational_markers):
        return TruthClass.OPERATIONAL
    
    # Check for high ambiguity (Lane E - HOLD)
    if triage.claim_type == ClaimType.UNKNOWN and triage.entity is None:
        return TruthClass.HOLD
    
    # Default: If it looks like a definition query, treat as invariant
    if triage.claim_type == ClaimType.DEFINITION:
        return TruthClass.ABSOLUTE_INVARIANT
    
    # Default fallback: conditional (safest middle ground)
    return TruthClass.CONDITIONAL


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 4: PLAN — Evidence Hierarchy
# ═══════════════════════════════════════════════════════════════════════════════

def build_evidence_plan(
    triage: QueryTriage,
    truth_class: TruthClass,
    query: str,
) -> EvidencePlan | None:
    """
    Build the evidence gathering plan based on classification.
    
    Returns None if no search needed (invariant lane).
    """
    if truth_class == TruthClass.ABSOLUTE_INVARIANT:
        return None  # No search needed
    
    plan = EvidencePlan()
    
    # Set minimum rank based on risk
    if triage.risk_class == RiskClass.CRITICAL:
        plan.minimum_rank = EvidenceRank.DIRECT_MEASUREMENT
        plan.minimum_evidence_threshold = 3
    elif triage.risk_class == RiskClass.HIGH:
        plan.minimum_rank = EvidenceRank.OFFICIAL_SOURCE
        plan.minimum_evidence_threshold = 2
    else:
        plan.minimum_rank = EvidenceRank.SECONDARY_REPORTING
    
    # Set freshness based on domain and time class
    if triage.time_class == TimeClass.LIVE:
        plan.freshness_hours = FRESHNESS_REQUIREMENTS.get(triage.domain, 24)
    elif triage.time_class == TimeClass.RECENT:
        plan.freshness_hours = 168  # 1 week
    
    # Preferred sources based on domain
    domain_sources = {
        "software": ["official documentation", "github releases", "pypi/npm", "technical blogs"],
        "finance": ["stock exchange", "official filings", "bloomberg/reuters", "company investor relations"],
        "law": ["government gazette", "official court records", "legal databases"],
        "security": ["cve database", "security advisories", "vendor security notices"],
    }
    plan.preferred_sources = domain_sources.get(triage.domain, ["reputable sources"])
    
    return plan


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 6: NORMALIZE — Evidence to Claims
# ═══════════════════════════════════════════════════════════════════════════════

def normalize_evidence(
    raw_results: list[dict],
    plan: EvidencePlan,
) -> tuple[list[str], list[dict], ConflictCheck]:
    """
    Convert raw search results into structured claims.
    
    Returns:
        - grounded_facts: Verified statements
        - evidence_bundle: Structured evidence with provenance
        - conflict_check: Detected conflicts
    """
    facts = []
    bundle = []
    conflicts = []
    
    for result in raw_results:
        # Extract claims from result
        claim = {
            "text": result.get("title", result.get("description", "")),
            "source": result.get("url", result.get("engine", "unknown")),
            "timestamp": result.get("timestamp", datetime.now(timezone.utc).isoformat()),
            "rank": EvidenceRank.SECONDARY_REPORTING.value,  # Default
        }
        
        # Simple conflict detection: check for negations
        if any(neg in claim["text"].lower() for neg in ["not", "no longer", "false", "incorrect"]):
            conflicts.append({
                "claim": claim["text"],
                "reason": "negation_detected",
                "source": claim["source"],
            })
        
        bundle.append(claim)
        facts.append(claim["text"])
    
    conflict_status = "detected" if conflicts else "none"
    conflict_check = ConflictCheck(
        status=conflict_status,
        conflicts=conflicts,
        resolution_strategy="source_hierarchy" if conflicts else None,
    )
    
    return facts, bundle, conflict_check


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 7: GATE — Confidence and Uncertainty
# ═══════════════════════════════════════════════════════════════════════════════

def assess_uncertainty(
    evidence_count: int,
    conflict_check: ConflictCheck,
    plan: EvidencePlan,
) -> UncertaintyLevel:
    """Assess uncertainty based on evidence quality and conflicts."""
    if conflict_check.status == "detected":
        return UncertaintyLevel.HIGH
    
    if evidence_count < plan.minimum_evidence_threshold:
        return UncertaintyLevel.HIGH
    
    if evidence_count >= plan.minimum_evidence_threshold + 1:
        return UncertaintyLevel.LOW
    
    return UncertaintyLevel.MODERATE


def build_handoff(
    packet: SensePacket,
    triage: QueryTriage,
) -> dict[str, Any]:
    """Determine next stage based on packet state."""
    # High uncertainty or ambiguity → HOLD
    if packet.uncertainty in (UncertaintyLevel.HIGH, UncertaintyLevel.UNKNOWN):
        if packet.ambiguity.detected:
            return {
                "next": "narrow_ambiguity",
                "reason": "Query too ambiguous for reliable sensing",
                "required_action": "Clarify: " + (packet.ambiguity.note or "Query intent unclear"),
            }
        return {
            "next": "gather_more_evidence",
            "reason": f"Insufficient evidence (uncertainty: {packet.uncertainty.value})",
        }
    
    # Invariant → MIND (offline reasoning)
    if packet.truth_class == TruthClass.ABSOLUTE_INVARIANT:
        return {
            "next": "offline_reason",
            "target": "arifos.mind",
            "mode": "reason",
            "reason": "First principles sufficient",
        }
    
    # Has evidence → MIND (synthesize)
    if packet.evidence_bundle:
        return {
            "next": "synthesize",
            "target": "arifos.mind",
            "mode": "reason",
            "reason": "Grounded evidence ready for synthesis",
        }
    
    # Default → HEART (critique before proceeding)
    return {
        "next": "critique",
        "target": "arifos.heart",
        "mode": "critique",
        "reason": "Safety check before using evidence",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PROTOCOL — 8-Stage Governed Sensing
# ═══════════════════════════════════════════════════════════════════════════════

async def governed_sense(
    query: str,
    session_id: str | None = None,
    session_context: dict | None = None,
    risk_context: str | None = None,
    execute_search: bool = True,
) -> SensePacket:
    """
    Execute the full 8-stage governed sensing protocol.
    
    This is the constitutional intake layer for reality claims.
    Does not blindly search. Classifies, plans, then retrieves if needed.
    
    Args:
        query: The raw query string
        session_id: Session identifier
        session_context: Previous context for grounding
        risk_context: Override risk classification (low/medium/high/critical)
        execute_search: If False, return plan without executing (dry-run)
    
    Returns:
        SensePacket: Structured, bounded evidence package
    """
    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 1: PARSE
    # ═══════════════════════════════════════════════════════════════════════════
    triage = parse_query(query, session_context)
    
    # Apply risk context override
    if risk_context:
        triage.risk_class = RiskClass(risk_context)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 2: CLASSIFY
    # ═══════════════════════════════════════════════════════════════════════════
    truth_class = classify_truth(triage, query)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 3: DECIDE — Whether to search
    # ═══════════════════════════════════════════════════════════════════════════
    search_required = truth_class not in (
        TruthClass.ABSOLUTE_INVARIANT,
        TruthClass.HOLD,
    )
    
    # Build reasoning basis for invariants
    reasoning_basis = []
    if truth_class == TruthClass.ABSOLUTE_INVARIANT:
        if triage.domain == "physics":
            reasoning_basis = ["thermodynamics", "physical laws"]
        elif triage.domain == "math":
            reasoning_basis = ["mathematical proof", "axioms"]
        else:
            reasoning_basis = ["definitions", "established principles"]
    
    # Check for ambiguity that might trigger HOLD
    ambiguity = AmbiguityStatus(detected=False)
    if truth_class == TruthClass.HOLD:
        ambiguity = AmbiguityStatus(
            detected=True,
            note="Query too ambiguous to classify",
            candidate_interpretations=[
                "Could be asking for definition",
                "Could be asking for current status",
                "Could be asking for recommendation",
            ],
            risk_of_misclassification="high",
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 4: PLAN — Evidence hierarchy
    # ═══════════════════════════════════════════════════════════════════════════
    evidence_plan = build_evidence_plan(triage, truth_class, query)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 5: SENSE — Execute constrained retrieval (if needed)
    # ═══════════════════════════════════════════════════════════════════════════
    evidence_bundle = []
    grounded_facts = []
    conflict_check = ConflictCheck(status="pending")
    
    if search_required and execute_search and evidence_plan:
        # Import here to avoid circular dependencies
        from .reality_handlers import handler as reality_handler
        from .reality_models import BundleInput
        
        # Execute search with constraints
        bundle_input = BundleInput(
            type="query",
            value=query,
            mode="search",
            top_k=evidence_plan.minimum_evidence_threshold,
        )
        
        bundle = await reality_handler.handle_compass(
            bundle_input,
            {"session_id": session_id or "governed_sense"},
        )
        
        # Extract results
        for result in bundle.results:
            if hasattr(result, 'results'):
                # SearchResult
                for r in result.results:
                    evidence_bundle.append({
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "description": r.get("description", ""),
                        "source": result.engine,
                    })
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 6: NORMALIZE
    # ═══════════════════════════════════════════════════════════════════════════
    if evidence_bundle and evidence_plan:
        grounded_facts, normalized_bundle, conflict_check = normalize_evidence(
            evidence_bundle, evidence_plan
        )
        evidence_bundle = normalized_bundle
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 7: GATE — Assess uncertainty
    # ═══════════════════════════════════════════════════════════════════════════
    if evidence_plan:
        uncertainty = assess_uncertainty(
            len(evidence_bundle),
            conflict_check,
            evidence_plan,
        )
    else:
        uncertainty = UncertaintyLevel.LOW if truth_class == TruthClass.ABSOLUTE_INVARIANT else UncertaintyLevel.UNKNOWN
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 8: HANDOFF — Build packet
    # ═══════════════════════════════════════════════════════════════════════════
    packet = SensePacket(
        query=query,
        query_triage=triage,
        truth_class=truth_class,
        claim_type=triage.claim_type,
        time_class=triage.time_class,
        search_required=search_required,
        reasoning_basis=reasoning_basis,
        evidence_plan=evidence_plan,
        evidence_bundle=evidence_bundle,
        grounded_facts=grounded_facts,
        ambiguity=ambiguity,
        conflict_check=conflict_check,
        uncertainty=uncertainty,
        temporal_scope="current" if triage.time_class == TimeClass.LIVE else None,
        handoff={},  # Will be populated below
    )
    
    # Determine handoff
    packet.handoff = build_handoff(packet, triage)
    
    return packet


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    "TruthClass",
    "ClaimType", 
    "TimeClass",
    "RiskClass",
    "EvidenceRank",
    "UncertaintyLevel",
    # Classes
    "SensePacket",
    "QueryTriage",
    "Entity",
    "AmbiguityStatus",
    "EvidencePlan",
    "ConflictCheck",
    # Functions
    "governed_sense",
    "parse_query",
    "classify_truth",
    "build_evidence_plan",
    "normalize_evidence",
    # Constants
    "ABSOLUTE_INVARIANTS",
    "TIME_SENSITIVE_KEYWORDS",
    "FRESHNESS_REQUIREMENTS",
]
