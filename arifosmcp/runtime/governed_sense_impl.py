"""
arifosmcp/runtime/governed_sense_impl.py — Canonical Governed Sensing Implementation
════════════════════════════════════════════════════════════════════════════════════

8-stage constitutional sensing protocol implementation.

Stage 111_SENSE | Trinity: DELTA Δ | Floors: F2, F3, F4, F7, F8, F10

Stages:
    1. PARSE    → Extract entities, intent, time-dependence, risk
    2. CLASSIFY → Route to truth-class lane (7 classes)
    3. DECIDE   → Whether search is needed
    4. PLAN     → Build evidence hierarchy
    5. SENSE    → Execute constrained retrieval
    6. NORMALIZE→ Convert to structured claims
    7. GATE     → Assess uncertainty, conflict, ambiguity
    8. HANDOFF  → Route to next stage with state delta

Author: Arif (Sovereign Architect)
Constitutional Seal: 999_VALIDATOR
Version: 2.0.0 — CANONICAL
"""

from __future__ import annotations

# ═══════════════════════════════════════════════════════════════════════════════
# A-FORGE BRIDGE INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════
import os
import re
from typing import Any

import requests

from .sensing_protocol import (
    # Complex dataclasses
    ActorSpec,
    AmbiguityModel,
    # Enums
    AmbiguityType,
    BudgetSpec,
    ClaimTarget,
    ClaimType,
    ConflictModel,
    ConflictType,
    DecisionProximity,
    EntityRef,
    EntityType,
    EntropyState,
    EurekaState,
    EvidenceItem,
    # ConflictPolicy, removed unused
    # CorroborationSpec, removed unused
    EvidencePlan,
    ExplorationState,
    ExtractedClaim,
    # FreshnessRequirement, removed unused
    HandoffSpec,
    InputSpec,
    InputSummary,
    InputType,
    IntelligenceState,
    IntentSpec,
    NormalizedFindings,
    Polarity,
    PolicySpec,
    QueryFrame,
    ResolutionStatus,
    RoutingDecision,
    RoutingTarget,
    SenseInput,
    SensePacket,
    SensingMode,
    StalenessRisk,
    StateUpdate,
    TaskType,
    TemporalGrounding,
    TimeScope,
    TruthClass,
    TruthClassification,
    TruthVector,
    UncertaintyBand,
    UncertaintyBasis,
    UncertaintyLevel,
)

# A-FORGE Bridge Configuration
A_FORGE_ENABLED = os.getenv("A_FORGE_ENABLED", "false").lower() == "true"
A_FORGE_ENDPOINT = os.getenv("A_FORGE_ENDPOINT", "http://localhost:7071/sense")
A_FORGE_TIMEOUT = float(os.getenv("A_FORGE_TIMEOUT_SECONDS", "2.0"))
A_FORGE_API_VERSION = "0.1.0"
MIN_COMPATIBLE_A_FORGE = "0.1.0"

_contract_checked = False
_contract_valid = False
_contract_failure_reason = None


def _check_nested_depth(obj: Any, current_depth: int = 0, max_depth: int = 10) -> bool:
    """Check if an object exceeds maximum nested depth to prevent parsing-based vulnerabilities."""
    if current_depth > max_depth:
        return False
    if isinstance(obj, dict):
        return all(_check_nested_depth(v, current_depth + 1, max_depth) for v in obj.values())
    if isinstance(obj, list):
        return all(_check_nested_depth(v, current_depth + 1, max_depth) for v in obj)
    return True


def _check_contract():
    """Validate runtime contract against A-FORGE /contract endpoint."""
    global _contract_checked, _contract_valid, _contract_failure_reason
    if _contract_checked:
        return _contract_valid

    if not A_FORGE_ENABLED:
        _contract_checked = True
        _contract_valid = False
        _contract_failure_reason = "A_FORGE_DISABLED"
        return False

    try:
        contract_url = A_FORGE_ENDPOINT.replace("/sense", "/contract")
        resp = requests.get(contract_url, timeout=1.0)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("ok"):
            _contract_failure_reason = "contract_endpoint_not_ok"
            _contract_checked = True
            _contract_valid = False
            return False

        af_api_version = data.get("api_version", "unknown")
        af_min_client = data.get("min_compatible_client", "unknown")

        if af_min_client != "unknown" and A_FORGE_API_VERSION < af_min_client:
            _contract_failure_reason = (
                f"version_incompatible:client={A_FORGE_API_VERSION} requires_af>={af_min_client}"
            )
            _contract_checked = True
            _contract_valid = False
            print(
                f"[A-FORGE] CONTRACT MISMATCH: client v{A_FORGE_API_VERSION} "
                f"< A-FORGE min {af_min_client}",
                flush=True,
            )
            return False

        if af_api_version != "unknown" and af_api_version < MIN_COMPATIBLE_A_FORGE:
            _contract_failure_reason = (
                f"version_incompatible:af={af_api_version} < required={MIN_COMPATIBLE_A_FORGE}"
            )
            _contract_checked = True
            _contract_valid = False
            print(
                f"[A-FORGE] CONTRACT MISMATCH: A-FORGE v{af_api_version} < required {MIN_COMPATIBLE_A_FORGE}",
                flush=True,
            )
            return False

        _contract_checked = True
        _contract_valid = True
        _contract_failure_reason = None
        return True

    except Exception as e:
        _contract_failure_reason = f"contract_check_error:{e}"
        _contract_checked = True
        _contract_valid = False
        print(f"[A-FORGE] Contract check error: {e}", flush=True)
        return False


def _call_a_forge_sense(
    raw_input,
    session_id=None,
):
    """Call A-FORGE Sense endpoint. Returns None on failure or if disabled."""
    if not A_FORGE_ENABLED:
        return None

    if not _check_contract():
        print(f"[A-FORGE] Bridge call blocked by contract failure: {_contract_failure_reason}", flush=True)
        return {
            "ok": True,
            "sense": {
                "mode_used": "lite",
                "escalation_reason": "contract_failure",
                "evidence_count": 0,
                "evidence_quality": 0.0,
                "uncertainty_band": "high",
                "recommended_next_stage": "hold",
                "contradiction_flags": ["bridge_contract_mismatch"],
                "query_complexity_score": 0.0,
                "risk_indicators": ["bridge_contract_mismatch"],
            },
            "judge": {
                "verdict": "HOLD",
                "reason": f"A-FORGE bridge contract failure: {_contract_failure_reason}",
                "confidence": {
                    "value": 0.0,
                    "is_estimate": True,
                    "evidence_count": 0,
                    "agreement_score": 0.0,
                    "contradiction_penalty": 1.0,
                    "uncertainty_hint": 1.0,
                },
                "floors_triggered": ["F13"],
                "human_review_required": True,
            },
            "context": {
                "source": "a-forge",
                "version": A_FORGE_API_VERSION,
                "epoch": "2026-04-15",
                "contract_failure": _contract_failure_reason,
            },
        }
    
    # Extract prompt from input
    if isinstance(raw_input, dict):
        prompt = raw_input.get("intent", raw_input.get("query", str(raw_input)))
    else:
        prompt = str(raw_input)
    
    try:
        payload = {
            "version": A_FORGE_API_VERSION,
            "session_id": session_id or "anon",
            "prompt": prompt,
            "context": {
                "source": "mcp-python",
                "tool": "sense",
                "epoch": "2026-04-15",
            },
        }
        
        resp = requests.post(
            A_FORGE_ENDPOINT,
            json=payload,
            timeout=A_FORGE_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        
        if not data.get("ok"):
            return None
            
        return data
        
    except Exception as e:
        print(f"[A-FORGE] Bridge error (falling back): {e}", flush=True)
        return None


# ═══════════════════════════════════════════════════════════════════════════════




# ═══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASES — Constitutional Classification
# ═══════════════════════════════════════════════════════════════════════════════

# Absolute invariants — no search needed
ABSOLUTE_INVARIANT_PATTERNS = {
    "physics": [
        r"\bentropy\b",
        r"\bthermodynamic",
        r"\bconservation of energy",
        r"\bspeed of light",
        r"\bgravity\b",
        r"\brelativity\b",
        r"\bquantum mechanic",
        r"\bsecond law",
        r"\bclosed system",
    ],
    "math": [
        r"\bnash equilibrium\b",
        r"\binformation entropy\b",
        r"\bpythagorean\b",
        r"\bturing complete",
        r"\bcomplexity\b.*\bclass\b",
        r"\balgorithm\b.*\bproof",
        r"\btheorem\b",
        r"\baxiom\b",
    ],
    "logic": [
        r"\bsyllogism\b",
        r"\bdeductive\b",
        r"\binductive\b",
        r"\boccam'?s razor\b",
        r"\bfalsification\b",
        r"\bnull hypothesis\b",
        r"\bproof by\b",
    ],
}

# Time-sensitive patterns — live search required
TIME_SENSITIVE_PATTERNS = {
    "current": [r"\bcurrent\b", r"\bnow\b", r"\btoday\b", r"\blatest\b", r"\brecent\b", r"\bpresent\b"],
    "price": [r"\bprice\b", r"\bcost\b", r"\brate\b", r"\bvalue of\b", r"\btrading at\b", r"\bstock price\b"],
    "role": [r"\bceo\b", r"\bcto\b", r"\bpresident\b", r"\bleader\b", r"\bhead of\b", r"\bminister\b", r"\bchairman\b"],
    "event": [r"\belection\b", r"\bwar\b", r"\boutage\b", r"\bcrash\b", r"\bbreach\b", r"\brelease\b", r"\bupdate\b"],
    "weather": [r"\bweather\b", r"\btemperature\b", r"\bforecast\b"],
}

# Contested framework patterns — depends on axioms/ideology
CONTESTED_FRAMEWORK_PATTERNS = [
    r"\bbest\b.*\b(practice|approach|way)\b",
    r"\bshould\b.*\b(use|choose|adopt)\b",
    r"\boptimal\b",
    r"\bideal\b",
    r"\bpreferable\b",
    r"\bethically\b",
    r"\bmorally\b",
    r"\bpolitically\b",
    r"\baccording to (marx|freud|keynes|hayek|rawls)\b",
    r"\bfrom a (utilitarian|deontological|virtue ethics)\b",
]

# Domain classification patterns
DOMAIN_PATTERNS = {
    "physics": [r"\bentropy\b", r"\benergy\b", r"\bforce\b", r"\bquantum\b", r"\brelativity", r"\bthermodynamic"],
    "math": [r"\bequation\b", r"\btheorem\b", r"\bproof\b", r"\bcalculate\b", r"\bformula\b", r"\balgorithm\b"],
    "law": [r"\blaw\b", r"\blegal\b", r"\bregulation\b", r"\bstatute\b", r"\bjurisdiction\b", r"\bcourt\b"],
    "finance": [r"\bprice\b", r"\bstock\b", r"\bmarket\b", r"\btrading\b", r"\bcrypto\b", r"\binvestment\b"],
    "software": [r"\bcode\b", r"\bapi\b", r"\blibrary\b", r"\bframework\b", r"\bversion\b", r"\bgithub\b"],
    "geopolitics": [r"\bwar\b", r"\belection\b", r"\bcountry\b", r"\bgovernment\b", r"\bpolicy\b", r"\btreaty\b"],
}

# Freshness requirements by domain (hours)
DOMAIN_FRESHNESS_HOURS = {
    "finance": 1,
    "software": 168,  # 1 week
    "security": 24,
    "news": 4,
    "weather": 1,
}


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 1: PARSE — Query Triage
# ═══════════════════════════════════════════════════════════════════════════════

def parse_input(raw_input: str | dict[str, Any]) -> SenseInput:
    """
    Parse raw input into canonical SenseInput structure.
    
    Backward compatible: simple string auto-normalizes to full structure.
    """
    if isinstance(raw_input, str):
        # Auto-normalize string query
        return _normalize_string_query(raw_input)
    elif isinstance(raw_input, dict):
        # Parse structured input
        return _normalize_dict_input(raw_input)
    else:
        # Fallback
        return SenseInput(
            input=InputSpec(value=str(raw_input) if raw_input else "", type=InputType.QUERY),
        )


def _normalize_string_query(query: str) -> SenseInput:
    """Normalize simple string query to full SenseInput."""
    q_lower = query.lower()
    
    # Detect task type
    task_type = TaskType.UNKNOWN
    if any(w in q_lower for w in ["what is", "define", "meaning of", "definition"]):
        task_type = TaskType.DEFINE
    elif any(w in q_lower for w in ["verify", "check if", "is it true"]):
        task_type = TaskType.VERIFY
    elif any(w in q_lower for w in ["compare", "vs", "versus", "difference between"]):
        task_type = TaskType.COMPARE
    elif any(w in q_lower for w in ["find", "locate", "where is"]):
        task_type = TaskType.LOCATE
    elif any(w in q_lower for w in ["monitor", "track", "watch"]):
        task_type = TaskType.MONITOR
    elif any(w in q_lower for w in ["explain", "how does", "why is"]):
        task_type = TaskType.EXPLAIN
    elif any(w in q_lower for w in ["classify", "categorize", "what type"]):
        task_type = TaskType.CLASSIFY
    
    # Detect domain
    domain = "unknown"
    for dom, patterns in DOMAIN_PATTERNS.items():
        if any(re.search(p, q_lower) for p in patterns):
            domain = dom
            break
    
    # Detect time scope
    time_scope = TimeScope.TIMELESS
    if any(re.search(p, q_lower) for patterns in TIME_SENSITIVE_PATTERNS.values() for p in patterns):
        time_scope = TimeScope.LIVE
    elif any(w in q_lower for w in ["yesterday", "last week", "ago", "previous"]):
        time_scope = TimeScope.HISTORICAL
    elif any(w in q_lower for w in ["this week", "this month", "recently"]):
        time_scope = TimeScope.DATED
    elif any(w in q_lower for w in ["will", "future", "predict", "forecast"]):
        time_scope = TimeScope.FORECAST
    
    # Extract entities
    entities = _extract_entities(query)
    
    # Detect decision proximity
    decision_proximity = DecisionProximity.INFORMATIONAL
    critical_terms = ["delete", "production", "deploy", "irreversible", "money", "transfer", "execute"]
    if any(t in q_lower for t in critical_terms):
        decision_proximity = DecisionProximity.DECISION_CRITICAL
    elif any(t in q_lower for t in ["plan", "prepare", "consider"]):
        decision_proximity = DecisionProximity.PREPARATORY
    
    return SenseInput(
        input=InputSpec(value=query, type=InputType.QUERY),
        intent=IntentSpec(task_type=task_type, decision_proximity=decision_proximity),
        query_frame=QueryFrame(
            domain=domain,
            time_scope=time_scope,
            entity_targets=entities,
            claim_targets=[ClaimTarget(text=query, polarity=Polarity.QUESTION)],
        ),
    )


def _normalize_dict_input(input_dict: dict[str, Any]) -> SenseInput:
    """Normalize dictionary input to SenseInput."""
    # Extract values with defaults
    input_spec = InputSpec(
        value=input_dict.get("query", input_dict.get("input", "")),
        type=InputType(input_dict.get("input_type", "query")),
        mode=SensingMode(input_dict.get("mode", "governed")),
    )
    
    intent = IntentSpec(
        task_type=TaskType(input_dict.get("task_type", "unknown")),
        user_goal=input_dict.get("user_goal"),
        decision_proximity=DecisionProximity(
            input_dict.get("decision_proximity", "informational")
        ),
    )
    
    query_frame = QueryFrame(
        domain=input_dict.get("domain", "unknown"),
        time_scope=TimeScope(input_dict.get("time_scope", "timeless")),
        jurisdiction=input_dict.get("jurisdiction"),
    )
    
    policy = PolicySpec(
        offline_first=input_dict.get("offline_first", False),
        freshness_max_age_days=input_dict.get("freshness_max_age_days"),
        min_evidence_rank=input_dict.get("min_evidence_rank"),
    )
    
    budget = BudgetSpec(
        top_k=input_dict.get("top_k", 5),
        budget_ms=input_dict.get("budget_ms", 15000),
    )
    
    actor = ActorSpec(
        actor_id=input_dict.get("actor_id", "anonymous"),
        auth_state=input_dict.get("auth_state", "unverified"),
    )
    
    return SenseInput(
        input=input_spec,
        intent=intent,
        query_frame=query_frame,
        policy=policy,
        budget=budget,
        actor=actor,
    )


def _extract_entities(query: str) -> list[EntityRef]:
    """Extract entity references from query."""
    entities = []
    
    # Pattern: "X of Y" or "Y's X"
    patterns = [
        r"(?:ceo|cto|president|head|leader|minister|chairman)\s+(?:of\s+)?([A-Z][a-zA-Z\s&]+?)(?:\?|$|\s+(?:today|now|currently))",
        r"([A-Z][a-zA-Z\s&]+?)\s+(?:ceo|cto|president|company|inc|corp|ltd)",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, query, re.IGNORECASE)
        for match in matches:
            if match.strip():
                entities.append(EntityRef(name=match.strip(), type=EntityType.COMPANY))
    
    # If no entities found, try to extract capitalized phrases
    if not entities:
        capitalized = re.findall(r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b", query)
        for cap in capitalized[:3]:  # Limit to first 3
            if len(cap) > 3 and cap.lower() not in ["what", "when", "where", "which", "who", "how"]:
                entities.append(EntityRef(name=cap, type=EntityType.UNKNOWN))
    
    return entities


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 2: CLASSIFY — Truth-Class Router
# ═══════════════════════════════════════════════════════════════════════════════

def classify_truth(sense_input: SenseInput) -> TruthClassification:
    """
    Classify query into truth-class lane.
    
    Seven classes:
        - absolute_invariant (Lane A)
        - conditional_invariant (Lane B)
        - operational_principle (Lane C)
        - time_sensitive_fact (Lane D)
        - contested_framework (Lane F)
        - ambiguous_query (Lane G)
        - unknown (Lane H)
    """
    query = sense_input.input.value.lower()
    time_scope = sense_input.query_frame.time_scope
    task_type = sense_input.intent.task_type
    
    # Check for ambiguous/empty queries first
    if not query or len(query.strip()) < 3:
        return TruthClassification(
            truth_class=TruthClass.UNKNOWN,
            search_required=False,
            search_reason="Empty or insufficient query",
            classification_confidence=1.0,
        )
    
    # Check for ambiguous referents
    vague_terms = ["this", "that", "it", "they", "them", "these", "those"]
    if any(f" {t} " in f" {query} " for t in vague_terms) and len(query) < 30:
        return TruthClassification(
            truth_class=TruthClass.AMBIGUOUS_QUERY,
            search_required=False,
            search_reason="Ambiguous referents without clear antecedent",
            classification_confidence=0.9,
        )
    
    # Check for absolute invariants (Lane A)
    for domain, patterns in ABSOLUTE_INVARIANT_PATTERNS.items():
        if any(re.search(p, query) for p in patterns):
            # But check if asking about current understanding
            if time_scope != TimeScope.LIVE and not any(
                re.search(p, query) for patterns in TIME_SENSITIVE_PATTERNS.values() for p in patterns
            ):
                return TruthClassification(
                    truth_class=TruthClass.ABSOLUTE_INVARIANT,
                    search_required=False,
                    search_reason=f"Absolute invariant ({domain}) — first principles sufficient",
                    classification_confidence=0.95,
                )
    
    # Check for contested frameworks (Lane F)
    if any(re.search(p, query) for p in CONTESTED_FRAMEWORK_PATTERNS):
        return TruthClassification(
            truth_class=TruthClass.CONTESTED_FRAMEWORK,
            search_required=False,
            search_reason="Truth depends on axioms/framework — requires explicit framing",
            framework_dependency=True,
            framework_note="Classified as contested — downstream must handle framework selection",
            classification_confidence=0.85,
        )
    
    # Check for time-sensitive facts (Lane D)
    if time_scope == TimeScope.LIVE or any(
        re.search(p, query) for patterns in TIME_SENSITIVE_PATTERNS.values() for p in patterns
    ):
        return TruthClassification(
            truth_class=TruthClass.TIME_SENSITIVE_FACT,
            search_required=True,
            search_reason="Time-sensitive information requires current grounding",
            temporal_dependency=True,
            temporal_note="Live data may have staleness risk",
            classification_confidence=0.9,
        )
    
    # Check for conditional invariants (Lane B)
    conditional_markers = [
        r"\bin the\s+\w+\b",  # "in the US", "in Malaysia"
        r"\bunder\s+\w+",     # "under GDPR"
        r"\baccording to\b",
        r"\bin\s+(python|javascript|go|rust)",
        r"\bversion\s+\d+",
        r"\bbased on\b",
        r"\bdepending on\b",
    ]
    if any(re.search(m, query) for m in conditional_markers):
        return TruthClassification(
            truth_class=TruthClass.CONDITIONAL_INVARIANT,
            search_required=False,
            search_reason="Frame-dependent truth — requires context specification",
            framework_dependency=True,
            classification_confidence=0.88,
        )
    
    # Check for operational principles (Lane C)
    operational_markers = [
        r"\bbest practice\b",
        r"\bshould\s+i\b",
        r"\brecommend\b",
        r"\bstrategy\b",
        r"\btrade[- ]?off\b",
        r"\barchitecture\b",
        r"\bdesign\b",
        r"\bhow to\b.*\boptimize\b",
    ]
    if any(re.search(m, query) for m in operational_markers):
        return TruthClassification(
            truth_class=TruthClass.OPERATIONAL_PRINCIPLE,
            search_required=True,  # May need selective evidence
            search_reason="Operational guidance — stable principles + selective evidence",
            classification_confidence=0.82,
        )
    
    # Check for definition queries
    if task_type == TaskType.DEFINE or any(w in query for w in ["what is", "define", "meaning"]):
        # Most definitions are timeless
        return TruthClassification(
            truth_class=TruthClass.ABSOLUTE_INVARIANT,
            search_required=False,
            search_reason="Definition — stable conceptual content",
            classification_confidence=0.8,
        )
    
    # Default fallback
    return TruthClassification(
        truth_class=TruthClass.UNKNOWN,
        search_required=False,
        search_reason="Insufficient basis to classify — requires clarification",
        classification_confidence=0.5,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 4: PLAN — Evidence Hierarchy
# ═══════════════════════════════════════════════════════════════════════════════

def build_evidence_plan(
    sense_input: SenseInput,
    truth_classification: TruthClassification,
) -> EvidencePlan:
    """Build evidence plan based on classification and input constraints."""
    
    # Invariants don't need evidence plans
    if truth_classification.truth_class in (
        TruthClass.ABSOLUTE_INVARIANT,
        TruthClass.CONDITIONAL_INVARIANT,
    ):
        return EvidencePlan(
            retrieval_lane="offline_reason",
            min_rank_required=1,
        )
    
    # Ambiguous or unknown queries don't get plans
    if truth_classification.truth_class in (
        TruthClass.AMBIGUOUS_QUERY,
        TruthClass.UNKNOWN,
    ):
        return EvidencePlan(
            retrieval_lane="hold",
            min_rank_required=7,
        )
    
    # Contested frameworks don't search
    if truth_classification.truth_class == TruthClass.CONTESTED_FRAMEWORK:
        return EvidencePlan(
            retrieval_lane="offline_reason",
            min_rank_required=1,
        )
    
    # Build plan for operational and time-sensitive
    plan = EvidencePlan()
    domain = sense_input.query_frame.domain
    decision_proximity = sense_input.intent.decision_proximity
    
    # Set minimum rank based on risk
    if decision_proximity == DecisionProximity.DECISION_CRITICAL:
        plan.min_rank_required = 2  # Primary source or official issuer
        plan.corroboration.min_distinct_sources = 3
    elif decision_proximity == DecisionProximity.PREPARATORY:
        plan.min_rank_required = 4  # Technical documentation
        plan.corroboration.min_distinct_sources = 2
    else:
        plan.min_rank_required = 5  # Reputable secondary
    
    # Apply user override if specified
    if sense_input.policy.min_evidence_rank:
        plan.min_rank_required = max(1, min(7, sense_input.policy.min_evidence_rank))
    
    # Set freshness requirements
    if truth_classification.temporal_dependency or truth_classification.truth_class == TruthClass.TIME_SENSITIVE_FACT:
        plan.freshness_requirement.required = True
        
        # Domain-specific freshness
        if domain in DOMAIN_FRESHNESS_HOURS:
            plan.freshness_requirement.max_age_days = DOMAIN_FRESHNESS_HOURS[domain] / 24
        else:
            plan.freshness_requirement.max_age_days = 7  # Default 1 week
        
        # User override
        if sense_input.policy.freshness_max_age_days:
            plan.freshness_requirement.max_age_days = sense_input.policy.freshness_max_age_days
    
    # Set preferred sources by domain
    domain_sources = {
        "software": [
            "official documentation",
            "github releases",
            "language specification",
            "package registry",
        ],
        "finance": [
            "stock exchange",
            "official filings (SEC, etc.)",
            "company investor relations",
            "bloomberg/reuters",
        ],
        "law": [
            "government gazette",
            "official court records",
            "legal databases (westlaw, lexis)",
        ],
        "security": [
            "CVE database",
            "security advisories",
            "vendor security notices",
        ],
    }
    plan.preferred_sources = domain_sources.get(domain, ["reputable sources"])
    
    # Banned sources
    plan.banned_sources = ["SEO farms", "content mills", "unverified social reposts"]
    
    # Set retrieval lane
    if truth_classification.truth_class == TruthClass.TIME_SENSITIVE_FACT:
        plan.retrieval_lane = "web_search"
    elif truth_classification.truth_class == TruthClass.OPERATIONAL_PRINCIPLE:
        plan.retrieval_lane = "mixed"
    
    return plan


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 5: SENSE — Execute Constrained Retrieval
# ═══════════════════════════════════════════════════════════════════════════════

async def execute_sensing(
    sense_input: SenseInput,
    evidence_plan: EvidencePlan,
    session_id: str | None = None,
) -> list[EvidenceItem]:
    """
    Execute constrained retrieval based on evidence plan.
    
    Only retrieves what fits the plan constraints.
    """
    # Check if we should skip retrieval
    if evidence_plan.retrieval_lane in ("offline_reason", "hold"):
        return []
    
    # Check offline_first policy
    if sense_input.policy.offline_first:
        return []
    
    query = sense_input.input.value
    
    # Import reality handlers
    from .reality_handlers import handler as reality_handler
    from .reality_models import BundleInput
    
    # Determine bundle parameters
    is_url = query.startswith(("http://", "https://"))
    bundle_type = "url" if is_url else "query"
    bundle_mode = "fetch" if is_url else "auto"
    
    # Execute retrieval
    bundle_input = BundleInput(
        type=bundle_type,
        value=query,
        mode=bundle_mode,
        top_k=sense_input.budget.top_k,
        fetch_top_k=sense_input.budget.fetch_top_k,
    )
    
    # Execute retrieval with timeout budget
    timeout_ms = sense_input.budget.budget_ms or 15000
    
    bundle = await reality_handler.handle_compass(
        bundle_input,
        {
            "session_id": session_id or "governed_sense",
            "timeout_ms": timeout_ms,
        },
    )
    
    # Convert to EvidenceItems
    items = []
    for result in bundle.results:
        if hasattr(result, 'results'):
            # SearchResult
            for r in result.results:
                item = EvidenceItem(
                    source_name=result.engine,
                    source_type="search_engine",
                    source_rank=6,  # Aggregator by default
                    url=r.get("url"),
                    title=r.get("title"),
                    snippets=[r.get("description", "")],
                    quality_flags=[],
                )
                items.append(item)
        elif hasattr(result, 'url'):
            # FetchResult
            item = EvidenceItem(
                source_name=result.url,
                source_type="fetched_page",
                source_rank=4,  # Assume reputable secondary for now
                url=result.url,
                snippets=[result.raw_content[:500]] if result.raw_content else [],
                quality_flags=[],
            )
            items.append(item)
    
    # Apply rank filtering
    items = [i for i in items if i.source_rank <= evidence_plan.min_rank_required]
    
    return items


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 6: NORMALIZE — Evidence to Claims
# ═══════════════════════════════════════════════════════════════════════════════

def normalize_evidence(
    items: list[EvidenceItem],
    sense_input: SenseInput,
) -> tuple[list[EvidenceItem], NormalizedFindings]:
    """Normalize evidence and extract findings."""
    
    findings = NormalizedFindings()
    
    for item in items:
        # Extract claims from snippets
        claims = []
        for snippet in item.snippets:
            # Simple claim extraction (sentence-based)
            sentences = re.split(r'[.!?]+', snippet)
            for sent in sentences:
                sent = sent.strip()
                if len(sent) > 20 and len(sent) < 200:
                    claims.append(ExtractedClaim(
                        claim_text=sent,
                        claim_type=ClaimType.STATUS,
                        confidence=0.5,
                    ))
        
        item.extracted_claims = claims
        
        # Add to grounded facts if quality is sufficient
        if item.source_rank <= 3:
            for claim in claims[:2]:  # Top 2 claims
                findings.grounded_facts.append(claim.claim_text)
    
    return items, findings


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 7: GATE — Assess Quality
# ═══════════════════════════════════════════════════════════════════════════════

def assess_ambiguity(
    sense_input: SenseInput,
    items: list[EvidenceItem],
) -> AmbiguityModel:
    """Assess ambiguity in query and results."""
    query = sense_input.input.value
    
    ambiguity = AmbiguityModel(detected=False)
    
    # Check for entity ambiguity (multiple possible interpretations)
    if len(sense_input.query_frame.entity_targets) > 1:
        ambiguity.detected = True
        ambiguity.ambiguity_type.append(AmbiguityType.ENTITY)
        ambiguity.candidate_interpretations = [
            f"Entity: {e.name} ({e.type.value})" for e in sense_input.query_frame.entity_targets
        ]
    
    # Check for timeframe ambiguity
    if "recent" in query.lower() or "lately" in query.lower():
        ambiguity.detected = True
        ambiguity.ambiguity_type.append(AmbiguityType.TIMEFRAME)
    
    # Check for definition/metric ambiguity
    if "best" in query.lower() and not any(w in query.lower() for w in ["according to", "by what"]):
        ambiguity.detected = True
        ambiguity.ambiguity_type.append(AmbiguityType.METRIC)
        ambiguity.candidate_interpretations.append("Best by what metric?")
    
    # Determine if human narrowing needed
    if ambiguity.detected and sense_input.intent.decision_proximity == DecisionProximity.DECISION_CRITICAL:
        ambiguity.needs_human_narrowing = True
    
    return ambiguity


def detect_conflicts(items: list[EvidenceItem]) -> ConflictModel:
    """Detect conflicts between evidence items."""
    conflict = ConflictModel(detected=False)
    
    if len(items) < 2:
        return conflict
    
    # Check for negation conflicts
    negation_words = ["not", "no longer", "false", "incorrect", "denies", "refutes"]
    
    claims_by_source = {}
    for item in items:
        for claim in item.extracted_claims:
            claims_by_source.setdefault(item.source_name, []).append(claim.claim_text.lower())
    
    # Simple conflict detection: one source affirms, another negates
    all_claims = [c for claims in claims_by_source.values() for c in claims]
    
    for i, claim1 in enumerate(all_claims):
        for claim2 in all_claims[i+1:]:
            # Check for direct negation
            for neg in negation_words:
                if neg in claim1 and neg not in claim2:
                    # Potential conflict
                    base1 = claim1.replace(neg, "").strip()
                    base2 = claim2.strip()
                    if base1[:30] == base2[:30]:  # Similar content
                        conflict.detected = True
                        conflict.conflict_type.append(ConflictType.SOURCE_DISAGREEMENT)
                        conflict.conflict_summary = f"Source disagreement: '{claim1[:50]}...' vs '{claim2[:50]}...'"
                        break
    
    if conflict.detected:
        conflict.resolution_status = ResolutionStatus.UNRESOLVED
    
    return conflict


def calculate_uncertainty(
    items: list[EvidenceItem],
    ambiguity: AmbiguityModel,
    conflict: ConflictModel,
    truth_classification: TruthClassification,
) -> UncertaintyBand:
    """Calculate uncertainty band with Ω₀ humility integration."""
    
    basis = UncertaintyBasis()
    
    # Evidence quality
    if items:
        ranks = [i.source_rank for i in items]
        avg_rank = sum(ranks) / len(ranks)
        basis.evidence_quality = max(0, 1 - (avg_rank - 1) / 6)  # Normalize to 0-1
    else:
        basis.evidence_quality = 0.0
    
    # Source agreement
    if conflict.detected:
        basis.source_agreement = 0.3
    elif len(items) >= 2:
        basis.source_agreement = 0.8
    else:
        basis.source_agreement = 0.5
    
    # Temporal alignment
    if truth_classification.temporal_dependency:
        basis.temporal_alignment = 0.7  # Some risk of staleness
    else:
        basis.temporal_alignment = 0.95
    
    # Frame clarity
    if ambiguity.detected:
        basis.frame_clarity = 0.4
    else:
        basis.frame_clarity = 0.9
    
    # Model fit (how well evidence matches query)
    basis.model_fit = 0.7  # Default moderate fit
    
    # Calculate overall sigma (uncertainty)
    sigma = 1.0 - (basis.evidence_quality * 0.3 + 
                   basis.source_agreement * 0.25 + 
                   basis.temporal_alignment * 0.15 +
                   basis.frame_clarity * 0.15 +
                   basis.model_fit * 0.15)
    
    # Determine level
    if sigma < 0.2:
        level = UncertaintyLevel.LOW
    elif sigma < 0.5:
        level = UncertaintyLevel.MODERATE
    elif sigma < 0.8:
        level = UncertaintyLevel.HIGH
    else:
        level = UncertaintyLevel.EXTREME
    
    # Calculate Ω₀ humility cap
    # Higher risk → lower cap (more humility required)
    omega0_base = 0.8
    if truth_classification.truth_class == TruthClass.CONTESTED_FRAMEWORK:
        omega0_base = 0.5
    elif ambiguity.detected:
        omega0_base = 0.6
    elif conflict.detected:
        omega0_base = 0.65
    
    omega0_cap = omega0_base * (1 - sigma * 0.3)
    
    # Build narrative
    narrative_parts = []
    if level == UncertaintyLevel.LOW:
        narrative_parts.append("Well-grounded evidence")
    elif level == UncertaintyLevel.HIGH:
        narrative_parts.append("Significant uncertainty")
    if ambiguity.detected:
        narrative_parts.append(f"ambiguity in {', '.join(a.value for a in ambiguity.ambiguity_type)}")
    if conflict.detected:
        narrative_parts.append("source conflicts detected")
    
    return UncertaintyBand(
        level=level,
        sigma=round(sigma, 4),
        omega0_cap=round(omega0_cap, 4),
        basis=basis,
        narrative_note="; ".join(narrative_parts) if narrative_parts else None,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 8: HANDOFF — Routing and State Update
# ═══════════════════════════════════════════════════════════════════════════════

def determine_routing(
    truth_classification: TruthClassification,
    uncertainty: UncertaintyBand,
    ambiguity: AmbiguityModel,
    conflict: ConflictModel,
    decision_proximity: DecisionProximity,
) -> RoutingDecision:
    """
    Deterministic routing to next stage.
    
    Rules:
        - Invariant/conditional/operational with adequate grounding → arifos.mind
        - Decision-critical with dignity/safety concerns → arifos.heart
        - Unresolved ambiguity/conflict in consequential context → hold
        - Completed evidence packet → downstream with reason
    """
    
    # Check for HOLD conditions
    if ambiguity.detected and ambiguity.needs_human_narrowing:
        return RoutingDecision(
            next_stage=RoutingTarget.HOLD,
            route_reason="Ambiguity too high in decision-critical context — requires human narrowing",
            requires_human_decision=True,
        )
    
    if conflict.detected and conflict.resolution_status == ResolutionStatus.UNRESOLVED:
        if decision_proximity == DecisionProximity.DECISION_CRITICAL:
            return RoutingDecision(
                next_stage=RoutingTarget.HOLD,
                route_reason="Unresolved conflict affects consequential decision",
                requires_human_decision=True,
            )
    
    # Check for HEART routing (safety/dignity)
    if decision_proximity == DecisionProximity.DECISION_CRITICAL:
        if uncertainty.level in (UncertaintyLevel.HIGH, UncertaintyLevel.EXTREME):
            return RoutingDecision(
                next_stage=RoutingTarget.HEART,
                route_reason="Decision-critical with high uncertainty — safety review required",
                requires_human_decision=True,
            )
    
    # Route invariants to MIND (offline reasoning)
    if truth_classification.truth_class in (
        TruthClass.ABSOLUTE_INVARIANT,
        TruthClass.CONDITIONAL_INVARIANT,
    ):
        return RoutingDecision(
            next_stage=RoutingTarget.MIND,
            route_reason="First principles sufficient — route to synthesis",
            requires_human_decision=False,
        )
    
    # Route contested frameworks to MIND (with framework note)
    if truth_classification.truth_class == TruthClass.CONTESTED_FRAMEWORK:
        return RoutingDecision(
            next_stage=RoutingTarget.MIND,
            route_reason="Contested framework — requires explicit framing before synthesis",
            requires_human_decision=False,
        )
    
    # Default: MIND for synthesis
    return RoutingDecision(
        next_stage=RoutingTarget.MIND,
        route_reason="Evidence packet prepared for synthesis",
        requires_human_decision=False,
        requires_live_verification=truth_classification.temporal_dependency,
    )


def calculate_state_update(
    items: list[EvidenceItem],
    findings: NormalizedFindings,
    ambiguity: AmbiguityModel,
    conflict: ConflictModel,
    previous_state: IntelligenceState | None = None,
) -> StateUpdate:
    """Calculate delta update to intelligence state."""
    
    update = StateUpdate()
    
    # Stable facts delta
    update.stable_facts_delta = findings.grounded_facts[:5]  # Top 5
    
    # Unknowns delta
    if not items:
        update.unknowns_delta.append("No evidence retrieved")
    if ambiguity.detected:
        update.unknowns_delta.append(f"Ambiguity: {', '.join(a.value for a in ambiguity.ambiguity_type)}")
    
    # Conflicts delta
    if conflict.detected:
        update.conflicts_delta.append(conflict.conflict_summary or "Source disagreement detected")
    
    # Confidence delta (simple calculation)
    if items:
        update.confidence_delta = min(0.3, len(items) * 0.05)
    
    # Uncertainty delta
    if conflict.detected:
        update.uncertainty_delta = 0.2
    elif ambiguity.detected:
        update.uncertainty_delta = 0.15
    else:
        update.uncertainty_delta = -0.05  # Reduced uncertainty
    
    return update


def build_intelligence_state(
    sense_input: SenseInput,
    truth_classification: TruthClassification,
    uncertainty: UncertaintyBand,
    items: list[EvidenceItem],
    findings: NormalizedFindings,
    ambiguity: AmbiguityModel,
    conflict: ConflictModel,
) -> IntelligenceState:
    """Build the full intelligence state for the RuntimeEnvelope."""
    
    state = IntelligenceState()
    
    # Exploration posture
    if len(findings.grounded_facts) > 5:
        state.exploration = ExplorationState.BROAD
    elif sense_input.intent.decision_proximity == DecisionProximity.FOCUSED:
        state.exploration = ExplorationState.FOCUSED
    else:
        state.exploration = ExplorationState.NARROW
    
    # Entropy
    if uncertainty.level == UncertaintyLevel.LOW:
        state.entropy = EntropyState.LOW
    elif uncertainty.level == UncertaintyLevel.HIGH:
        state.entropy = EntropyState.HIGH
    else:
        state.entropy = EntropyState.MANAGEABLE
    
    # Eureka (insight detection)
    if len(findings.grounded_facts) >= 3 and uncertainty.level == UncertaintyLevel.LOW:
        state.eureka = EurekaState.EMERGING
    
    # Confidence and uncertainty
    state.confidence = 1.0 - uncertainty.sigma
    state.uncertainty_score = uncertainty.sigma
    
    # Lists
    state.stable_facts = findings.grounded_facts[:10]
    state.unknowns = findings.unresolved_questions[:5]
    state.conflicts = findings.contested_points[:5]
    
    if ambiguity.detected:
        state.decision_required.append("Clarify ambiguous query intent")
    
    # Truth vector (constitutional physics)
    state.truth_vector = TruthVector(
        grounding_g=min(1.0, len(items) * 0.2),
        truth_tau=0.7 if not conflict.detected else 0.4,
        uncertainty_sigma=uncertainty.sigma,
        coherence_c=0.8 if not conflict.detected else 0.4,
        entropy_delta_s=-0.1 if uncertainty.level == UncertaintyLevel.LOW else 0.1,
        humility_omega0=uncertainty.omega0_cap,
    )
    
    return state


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN GOVERNED SENSE FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════


def _map_a_forge_to_python_result(af_result, raw_input):
    """Map A-FORGE response to Python SensePacket format."""
    sense = af_result.get("sense", {})
    judge = af_result.get("judge", {})
    
    # Extract query
    if isinstance(raw_input, dict):
        raw_query = raw_input.get("intent", raw_input.get("query", str(raw_input)))
    else:
        raw_query = str(raw_input)
    
    # Map uncertainty
    uncertainty_band = sense.get("uncertainty_band", "medium")
    uncertainty_score = {"low": 0.3, "medium": 0.5, "high": 0.7, "critical": 0.9}.get(uncertainty_band, 0.5)
    
    # Map recommendation to routing
    recommendation = sense.get("recommended_next_stage", "mind")
    is_hold = recommendation == "hold"
    
    # Create minimal packet structure
    packet = {
        "input_summary": {
            "raw_query": raw_query,
            "mode_used": sense.get("mode_used", "lite"),
        },
        "routing": {
            "target": "HOLD" if is_hold else "MIND",
            "reason": sense.get("escalation_reason", "a-forge-governance"),
        },
        "uncertainty": {
            "band": uncertainty_band,
            "score": uncertainty_score,
        },
        "source": "a-forge",
    }
    
    # Create intelligence state
    intelligence_state = {
        "exploration": "BLOCKED" if is_hold else "FOCUSED",
        "uncertainty_score": uncertainty_score,
        "confidence": judge.get("confidence", {}).get("value", 0.5),
        "truth_vector": {
            "humility_omega0": judge.get("confidence", {}).get("value", 0.5),
            "verdict": judge.get("verdict", "SABAR"),
        },
        "hold_triggered": is_hold,
        "hold_reason": sense.get("escalation_reason") if is_hold else None,
    }
    
    return packet, intelligence_state


async def governed_sense_v2(
    raw_input: str | dict[str, Any],
    session_id: str | None = None,
    execute_search: bool = True,
) -> tuple[SensePacket, IntelligenceState]:
    """
    Execute the full 8-stage governed sensing protocol.
    
    Returns:
        tuple of (SensePacket, IntelligenceState) for full constitutional alignment.
    """
    # ═══════════════════════════════════════════════════════════════════════════
    # DEPTH & TIMEOUT SENTINEL
    # ═══════════════════════════════════════════════════════════════════════════
    if not _check_nested_depth(raw_input, max_depth=10):
        raise ValueError("Constitutional Violation: Input depth exceeds safe limits (max_depth=10).")

    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 1: PARSE
    # ═══════════════════════════════════════════════════════════════════════════
    sense_input = parse_input(raw_input)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 2: CLASSIFY
    # ═══════════════════════════════════════════════════════════════════════════

    # ═══════════════════════════════════════════════════════════════════════════
    # A-FORGE BRIDGE: Try TypeScript governance first
    # ═══════════════════════════════════════════════════════════════════════════
    af_result = _call_a_forge_sense(raw_input, session_id)
    if af_result is not None:
        print("[A-FORGE] Using TS governance layer", flush=True)
        sense = af_result.get("sense", {})
        
        # Check for 888_HOLD
        if sense.get("recommended_next_stage") == "hold":
            print(f"[A-FORGE] 888_HOLD triggered: {sense.get('escalation_reason')}", flush=True)
        
        # Map to Python packet format and return
        return _map_a_forge_to_python_result(af_result, raw_input)
    
    # Fall through to Python 8-stage governance

    truth_classification = classify_truth(sense_input)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 3: DECIDE (implicit in plan building)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 4: PLAN
    # ═══════════════════════════════════════════════════════════════════════════
    evidence_plan = build_evidence_plan(sense_input, truth_classification)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 5: SENSE
    # ═══════════════════════════════════════════════════════════════════════════
    items = []
    if execute_search and evidence_plan.retrieval_lane not in ("offline_reason", "hold"):
        items = await execute_sensing(sense_input, evidence_plan, session_id)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 6: NORMALIZE
    # ═══════════════════════════════════════════════════════════════════════════
    items, findings = normalize_evidence(items, sense_input)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 7: GATE
    # ═══════════════════════════════════════════════════════════════════════════
    ambiguity = assess_ambiguity(sense_input, items)
    conflict = detect_conflicts(items)
    uncertainty = calculate_uncertainty(items, ambiguity, conflict, truth_classification)
    
    # Temporal grounding
    temporal = TemporalGrounding(
        query_time_class=sense_input.query_frame.time_scope,
        freshness_required=truth_classification.temporal_dependency,
        staleness_risk=StalenessRisk.HIGH if truth_classification.temporal_dependency else StalenessRisk.NONE,
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 8: HANDOFF
    # ═══════════════════════════════════════════════════════════════════════════
    routing = determine_routing(
        truth_classification,
        uncertainty,
        ambiguity,
        conflict,
        sense_input.intent.decision_proximity,
    )
    
    state_update = calculate_state_update(items, findings, ambiguity, conflict)
    
    # Build intelligence state
    intelligence_state = build_intelligence_state(
        sense_input, truth_classification, uncertainty, items, findings, ambiguity, conflict
    )
    
    # Build canonical SensePacket
    packet = SensePacket(
        input_summary=InputSummary(
            raw_query=sense_input.input.value,
            normalized_query=sense_input.input.value.lower().strip(),
            mode_used=sense_input.input.mode.value,
            domain=sense_input.query_frame.domain,
        ),
        truth_classification=truth_classification,
        temporal_grounding=temporal,
        ambiguity=ambiguity,
        conflict=conflict,
        uncertainty=uncertainty,
        evidence_plan=evidence_plan,
        entities=sense_input.query_frame.entity_targets,
        target_claims=sense_input.query_frame.claim_targets,
        evidence_items=items,
        normalized_findings=findings,
        routing=routing,
        handoff=HandoffSpec(state_update=state_update),
    )
    
    return packet, intelligence_state


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    "governed_sense_v2",
    "parse_input",
    "classify_truth",
    "build_evidence_plan",
    "execute_sensing",
    "normalize_evidence",
    "assess_ambiguity",
    "detect_conflicts",
    "calculate_uncertainty",
    "determine_routing",
    "build_intelligence_state",
]
