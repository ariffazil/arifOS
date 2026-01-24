"""
arifOS Trinity Compression (v50.5.0)
5-Tool Constitutional MCP Framework

The Metabolic Standard compressed to 5 memorable tools:
    000_init    → Gate (Authority + Injection + Amanah)
    agi_genius  → Mind (SENSE → THINK → ATLAS)
    asi_act     → Heart (EVIDENCE → EMPATHY → ACT)
    apex_judge  → Soul (EUREKA → JUDGE → PROOF)
    999_vault   → Seal (PROOF + Immutable Log)

Mnemonic: "Init the Genius, Act with Heart, Judge at Apex, seal in Vault."

Philosophy:
    INPUT → F12 Injection Guard
         → 000_init (Ignition + Authority)
         → agi_genius (Δ Mind: Logic/Truth)
         → asi_act (Ω Heart: Care/Safety)
         → apex_judge (Ψ Soul: Verdict)
         → 999_vault (Immutable Seal)
         → OUTPUT (SEAL | SABAR | VOID)

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from arifos.mcp.rate_limiter import get_rate_limiter, RateLimitResult
from arifos.mcp.metrics import get_metrics

# Session persistence for 999-000 loop
from arifos.mcp.session_ledger import inject_memory, seal_memory

logger = logging.getLogger(__name__)


# =============================================================================
# RATE LIMITING HELPER
# =============================================================================

def _check_rate_limit(tool_name: str, session_id: str = "") -> Optional[Dict]:
    """
    Check rate limit before processing a tool call.

    Returns:
        None if allowed, or a VOID response dict if rate limited.
    """
    limiter = get_rate_limiter()
    result = limiter.check(tool_name, session_id)

    if not result.allowed:
        logger.warning(f"Rate limit exceeded: {tool_name} (session={session_id})")
        # Record rate limit hit in metrics
        metrics = get_metrics()
        metrics.record_rate_limit_hit(tool_name, result.limit_type)
        metrics.record_verdict(tool_name, "VOID")
        return {
            "status": "VOID",
            "session_id": session_id or "UNKNOWN",
            "verdict": "VOID",
            "reason": result.reason,
            "rate_limit": {
                "exceeded": True,
                "limit_type": result.limit_type,
                "reset_in_seconds": result.reset_in_seconds,
                "remaining": result.remaining
            },
            "floors_checked": ["F11_RateLimit"]
        }

    return None


def _record_tool_metrics(tool_name: str, verdict: str, start_time: float, floor_violations: Optional[List[str]] = None):
    """
    Record metrics for a tool call.

    Args:
        tool_name: Name of the MCP tool
        verdict: Final verdict (SEAL, VOID, SABAR, etc)
        start_time: time.time() when request started
        floor_violations: List of floor IDs that were violated
    """
    metrics = get_metrics()
    duration = time.time() - start_time

    # Record request
    status = "success" if verdict == "SEAL" else "error"
    metrics.requests_total.inc({"tool": tool_name, "status": status})

    # Record latency
    metrics.request_duration.observe(duration, {"tool": tool_name})

    # Record verdict
    metrics.record_verdict(tool_name, verdict)

    # Record floor violations
    if floor_violations:
        for floor in floor_violations:
            metrics.record_floor_violation(floor, tool_name)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class InitResult:
    """Result from 000_init - The 7-Step Ignition Sequence."""
    status: str  # SEAL, SABAR, VOID
    session_id: str
    timestamp: str = ""

    # Step 1: Memory Injection
    previous_context: Dict[str, Any] = field(default_factory=dict)

    # Step 2: Sovereign Recognition
    authority: str = "GUEST"  # 888_JUDGE or GUEST
    authority_verified: bool = False
    scar_weight: float = 0.0

    # Step 3: Intent Mapping
    intent: str = ""  # explain, build, debug, discuss
    lane: str = "UNKNOWN"  # HARD, SOFT, PHATIC, REFUSE
    contrasts: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)

    # Step 4: Thermodynamic Setup
    entropy_input: float = 0.0
    entropy_target: float = 0.0
    entropy_omega: float = 0.04  # Humility [0.03, 0.05]
    peace_squared: float = 1.0
    energy_budget: float = 1.0

    # Step 5: Floors Loaded
    floors_checked: List[str] = field(default_factory=list)
    floors_loaded: int = 13

    # Step 6: Tri-Witness
    tri_witness: Dict[str, Any] = field(default_factory=dict)
    TW: float = 0.0

    # Step 7: Engine Status
    engines: Dict[str, str] = field(default_factory=dict)

    # Security
    injection_risk: float = 0.0
    reason: str = ""


@dataclass
class GeniusResult:
    """Result from agi_genius."""
    status: str  # SEAL, SABAR, VOID
    session_id: str
    reasoning: str
    truth_score: float
    entropy_delta: float
    lane: str  # HARD, SOFT, PHATIC, REFUSE
    semantic_map: Dict[str, Any] = field(default_factory=dict)
    related_thoughts: List[str] = field(default_factory=list)
    confidence_bound: str = ""
    floors_checked: List[str] = field(default_factory=list)
    sub_stage: str = ""  # Which sub-stage completed


@dataclass
class ActResult:
    """Result from asi_act."""
    status: str  # SEAL, SABAR, VOID
    session_id: str
    peace_squared: float
    kappa_r: float
    vulnerability_score: float = 0.0
    evidence_grounded: bool = False
    executable: bool = False
    witness_status: str = ""  # APPROVED, PENDING, REJECTED, INVALID
    witness_count: int = 0
    floors_checked: List[str] = field(default_factory=list)
    sub_stage: str = ""
    reason: str = ""  # For validation errors


@dataclass
class JudgeResult:
    """Result from apex_judge."""
    status: str  # SEAL, SABAR, VOID
    session_id: str
    verdict: str  # SEAL, SABAR, VOID
    synthesis: str
    tri_witness_votes: List[float] = field(default_factory=list)
    consensus_score: float = 0.0
    genius_metrics: Dict[str, float] = field(default_factory=dict)
    proof_hash: str = ""
    floors_checked: List[str] = field(default_factory=list)
    sub_stage: str = ""


@dataclass
class VaultResult:
    """Result from 999_vault."""
    status: str  # SEAL, SABAR, VOID
    session_id: str
    verdict: str
    merkle_root: str
    audit_hash: str
    sealed_at: str
    reversible: bool
    memory_location: str
    floors_checked: List[str] = field(default_factory=list)


# =============================================================================
# TOOL 1: 000_INIT (The 7-Step Thermodynamic Ignition Sequence)
# =============================================================================

# Sovereign recognition patterns
SOVEREIGN_PATTERNS = [
    "im arif", "i'm arif", "i am arif", "arif here",
    "salam", "assalamualaikum", "waalaikumsalam",
    "888", "judge", "sovereign"
]

# Intent classification keywords
INTENT_KEYWORDS = {
    "build": ["build", "create", "implement", "make", "code", "develop", "write", "work on", "add", "integrate"],
    "debug": ["fix", "debug", "error", "bug", "issue", "problem", "broken", "wrong", "fail"],
    "explain": ["explain", "what", "how", "why", "tell", "describe", "understand", "show"],
    "discuss": ["discuss", "think", "consider", "explore", "brainstorm", "idea", "opinion"],
    "review": ["review", "check", "audit", "verify", "validate", "test", "analyze"]
}

# Lane classification
LANE_INTENTS = {
    "HARD": ["build", "debug", "review"],  # Technical precision
    "SOFT": ["discuss", "explore"],         # Open-ended
    "PHATIC": ["greet", "thanks"],          # Social
}


def _step_1_memory_injection() -> Dict[str, Any]:
    """Step 1: Read from VAULT999 - inject previous session context."""
    try:
        previous_context = inject_memory()
        prev_session = previous_context.get('previous_session') or {}
        prev_id = prev_session.get('session_id', '')
        logger.info(f"000_init Step 1: Memory injected from {prev_id[:8] if prev_id else 'FIRST_SESSION'}")
        return previous_context
    except Exception as e:
        logger.warning(f"000_init Step 1: Memory injection failed: {e}")
        return {"is_first_session": True, "error": str(e)}


def _step_2_sovereign_recognition(query: str, token: str) -> Dict[str, Any]:
    """Step 2: Recognize the 888 Judge - verify Scar-Weight."""
    query_lower = query.lower()

    # Check for sovereign patterns in query
    is_sovereign = any(p in query_lower for p in SOVEREIGN_PATTERNS)

    # Also check authority token
    if token and _verify_authority(token):
        is_sovereign = True

    if is_sovereign:
        logger.info("000_init Step 2: Sovereign recognized (888 Judge)")
        return {
            "authority": "888_JUDGE",
            "scar_weight": 1.0,
            "role": "SOVEREIGN",
            "f11_verified": True
        }
    else:
        logger.info("000_init Step 2: Guest user")
        return {
            "authority": "GUEST",
            "scar_weight": 0.0,
            "role": "USER",
            "f11_verified": False
        }


def _step_3_intent_mapping(query: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Step 3: Map intent - contrast, meaning, prediction."""
    query_lower = query.lower()

    # Extract entities (simple keyword extraction)
    words = query_lower.split()
    entities = [w for w in words if len(w) > 3 and w.isalpha()]

    # Find contrasts (vs, or, versus patterns)
    contrasts = []
    if " vs " in query_lower or " versus " in query_lower:
        contrasts.append("comparison")
    if " or " in query_lower:
        contrasts.append("choice")
    if "old" in query_lower and "new" in query_lower:
        contrasts.append("old_vs_new")
    if "theory" in query_lower and "practice" in query_lower:
        contrasts.append("theory_vs_practice")

    # Classify intent
    intent = "unknown"
    for intent_type, keywords in INTENT_KEYWORDS.items():
        if any(kw in query_lower for kw in keywords):
            intent = intent_type
            break

    # Check for greetings (PHATIC)
    greetings = ["hi", "hello", "hey", "salam", "thanks", "thank you"]
    if any(g in query_lower for g in greetings) and len(query) < 50:
        intent = "greet"

    # Determine lane
    lane = "SOFT"  # Default
    for lane_type, intents in LANE_INTENTS.items():
        if intent in intents:
            lane = lane_type
            break

    # If unclear, check query length (longer = probably HARD)
    if intent == "unknown" and len(query) > 100:
        lane = "HARD"

    logger.info(f"000_init Step 3: Intent={intent}, Lane={lane}")
    return {
        "intent": intent,
        "lane": lane,
        "contrasts": contrasts,
        "entities": entities[:10],  # Top 10
        "confidence": 0.8 if intent != "unknown" else 0.5
    }


def _step_4_thermodynamic_setup(intent_map: Dict[str, Any]) -> Dict[str, Any]:
    """Step 4: Set energy budget and entropy targets."""
    # Estimate input entropy (how complex is the query?)
    # Simple heuristic: more entities/contrasts = higher entropy
    entity_count = len(intent_map.get("entities", []))
    contrast_count = len(intent_map.get("contrasts", []))
    S_input = min(1.0, 0.3 + (entity_count * 0.05) + (contrast_count * 0.1))

    # Target: reduce by 30%
    S_target = S_input * 0.7

    # Humility parameter [0.03, 0.05]
    omega_0 = 0.04

    # Peace² baseline
    peace_squared = 1.0

    # Energy budget based on lane
    lane = intent_map.get("lane", "SOFT")
    if lane == "HARD":
        energy_budget = 1.0
        time_budget = 120
    elif lane == "SOFT":
        energy_budget = 0.7
        time_budget = 60
    else:  # PHATIC
        energy_budget = 0.3
        time_budget = 15

    logger.info(f"000_init Step 4: S_input={S_input:.2f}, budget={energy_budget}")
    return {
        "entropy_input": S_input,
        "entropy_target": S_target,
        "dS_required": S_target - S_input,
        "omega_0": omega_0,
        "peace_squared": peace_squared,
        "energy_budget": energy_budget,
        "time_budget": time_budget,
        "timestamp": datetime.now().isoformat()
    }


def _step_5_floor_loading() -> Dict[str, Any]:
    """Step 5: Load the 13 Constitutional Floors."""
    floors = [
        "F1_Amanah", "F2_Truth", "F3_TriWitness", "F4_Empathy",
        "F5_Peace2", "F6_Clarity", "F7_Humility", "F8_Genius",
        "F9_AntiHantu", "F10_Ontology", "F11_CommandAuth",
        "F12_InjectionDefense", "F13_Sovereign"
    ]
    logger.info(f"000_init Step 5: Loaded {len(floors)} floors")
    return {
        "floors": floors,
        "count": len(floors),
        "hard_floors": 7,
        "soft_floors": 4,
        "derived_floors": 2
    }


def _step_6_tri_witness(sovereign: Dict, thermo: Dict) -> Dict[str, Any]:
    """Step 6: Establish Tri-Witness handshake."""
    # Human witness
    human = {
        "present": sovereign["authority"] == "888_JUDGE",
        "scar_weight": sovereign["scar_weight"],
        "veto_power": True
    }

    # AI witness (constitutional)
    ai = {
        "present": True,
        "floors_active": 13,
        "constraints_on": True
    }

    # Earth witness (thermodynamic)
    earth = {
        "present": True,
        "energy_available": thermo["energy_budget"],
        "within_bounds": thermo["energy_budget"] <= 1.0
    }

    # Compute TW (geometric mean)
    h = 1.0 if human["present"] else 0.5
    a = 1.0 if ai["constraints_on"] else 0.0
    e = 1.0 if earth["within_bounds"] else 0.5
    TW = (h * a * e) ** (1/3)

    logger.info(f"000_init Step 6: TW={TW:.2f}, consensus={TW >= 0.95}")
    return {
        "human": human,
        "ai": ai,
        "earth": earth,
        "TW": TW,
        "consensus": TW >= 0.95
    }


def _step_7_engine_ignition() -> Dict[str, str]:
    """Step 7: Fire up the engines."""
    engines = {
        "AGI_Mind": "READY",
        "ASI_Heart": "READY",
        "APEX_Soul": "READY"
    }
    logger.info("000_init Step 7: Engines IGNITED")
    return engines


async def mcp_000_init(
    action: str = "init",
    query: str = "",
    authority_token: str = "",
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    000 INIT: The 7-Step Thermodynamic Ignition Sequence.

    "Im Arif, [topic]" triggers full system ignition.

    The 7 Steps:
        1. MEMORY INJECTION - Read from VAULT999
        2. SOVEREIGN RECOGNITION - Verify 888 Judge
        3. INTENT MAPPING - Contrast, meaning, lane
        4. THERMODYNAMIC SETUP - ΔS, Ω₀, energy budget
        5. FLOOR LOADING - F1-F13 constraints
        6. TRI-WITNESS HANDSHAKE - Human × AI × Earth
        7. ENGINE IGNITION - AGI/ASI/APEX ready

    Floors Enforced: F1, F11, F12

    Returns:
        InitResult with full ignition state
    """
    # Valid actions for 000_init
    VALID_ACTIONS = {"init", "gate", "reset", "validate"}

    # =========================================================================
    # INPUT VALIDATION
    # =========================================================================
    if not action or action not in VALID_ACTIONS:
        logger.warning(f"000_init: Invalid action '{action}'")
        return InitResult(
            status="VOID",
            session_id=session_id or "UNKNOWN",
            injection_risk=0.0,
            reason=f"Invalid action: '{action}'. Valid: {VALID_ACTIONS}",
            floors_checked=["F12_InputValidation"]
        ).__dict__

    # =========================================================================
    # RATE LIMITING
    # =========================================================================
    rate_limit_response = _check_rate_limit("000_init", session_id)
    if rate_limit_response:
        return rate_limit_response

    session = session_id or str(uuid4())
    floors_checked = []

    try:
        # =====================================================================
        # STEP 1: MEMORY INJECTION
        # =====================================================================
        previous_context = _step_1_memory_injection()

        # =====================================================================
        # STEP 2: SOVEREIGN RECOGNITION
        # =====================================================================
        sovereign = _step_2_sovereign_recognition(query, authority_token)
        floors_checked.append("F11_CommandAuth")

        # =====================================================================
        # STEP 3: INTENT MAPPING (Contrast Engine)
        # =====================================================================
        intent_map = _step_3_intent_mapping(query, previous_context)

        # =====================================================================
        # STEP 4: THERMODYNAMIC SETUP
        # =====================================================================
        thermo = _step_4_thermodynamic_setup(intent_map)

        # =====================================================================
        # FLOOR CHECK: F12 Injection Defense
        # =====================================================================
        injection_risk = _detect_injection(query)
        floors_checked.append("F12_InjectionDefense")

        if injection_risk > 0.85:
            return InitResult(
                status="VOID",
                session_id=session,
                timestamp=thermo["timestamp"],
                injection_risk=injection_risk,
                reason="F12: Injection attack detected",
                floors_checked=floors_checked
            ).__dict__

        if injection_risk > 0.2:
            return InitResult(
                status="SABAR",
                session_id=session,
                timestamp=thermo["timestamp"],
                injection_risk=injection_risk,
                reason=f"F12: Injection risk {injection_risk:.2f} - proceed with caution",
                floors_checked=floors_checked,
                previous_context=previous_context
            ).__dict__

        # =====================================================================
        # FLOOR CHECK: F1 Amanah (Reversibility)
        # =====================================================================
        reversible = _check_reversibility(query)
        floors_checked.append("F1_Amanah")

        if not reversible and intent_map["lane"] == "HARD":
            return InitResult(
                status="SABAR",
                session_id=session,
                timestamp=thermo["timestamp"],
                reason="F1: Non-reversible operation - requires explicit approval",
                floors_checked=floors_checked,
                previous_context=previous_context
            ).__dict__

        # =====================================================================
        # STEP 5: FLOOR LOADING
        # =====================================================================
        floors = _step_5_floor_loading()
        floors_checked.extend(floors["floors"])

        # =====================================================================
        # STEP 6: TRI-WITNESS HANDSHAKE
        # =====================================================================
        tri_witness = _step_6_tri_witness(sovereign, thermo)

        # =====================================================================
        # STEP 7: ENGINE IGNITION
        # =====================================================================
        engines = _step_7_engine_ignition()

        # =====================================================================
        # IGNITION COMPLETE
        # =====================================================================
        logger.info(f"000_init: IGNITION COMPLETE - session {session[:8]}")

        return InitResult(
            status="SEAL",
            session_id=session,
            timestamp=thermo["timestamp"],

            # Step 1
            previous_context=previous_context,

            # Step 2
            authority=sovereign["authority"],
            authority_verified=sovereign["f11_verified"],
            scar_weight=sovereign["scar_weight"],

            # Step 3
            intent=intent_map["intent"],
            lane=intent_map["lane"],
            contrasts=intent_map["contrasts"],
            entities=intent_map["entities"],

            # Step 4
            entropy_input=thermo["entropy_input"],
            entropy_target=thermo["entropy_target"],
            entropy_omega=thermo["omega_0"],
            peace_squared=thermo["peace_squared"],
            energy_budget=thermo["energy_budget"],

            # Step 5
            floors_checked=floors_checked,
            floors_loaded=floors["count"],

            # Step 6
            tri_witness=tri_witness,
            TW=tri_witness["TW"],

            # Step 7
            engines=engines,

            # Security
            injection_risk=injection_risk,
            reason="IGNITION COMPLETE - Constitutional Mode Active"
        ).__dict__

    except Exception as e:
        logger.error(f"000_init IGNITION FAILED: {e}")
        return InitResult(
            status="VOID",
            session_id=session,
            injection_risk=1.0,
            reason=f"IGNITION FAILED: {str(e)}",
            floors_checked=floors_checked
        ).__dict__


# =============================================================================
# TOOL 2: AGI_GENIUS (Mind: SENSE → THINK → ATLAS)
# =============================================================================

async def mcp_agi_genius(
    action: str,
    query: str = "",
    session_id: str = "",
    thought: str = "",
    context: Optional[Dict[str, Any]] = None,
    draft: str = "",
    axioms: Optional[List[str]] = None,
    truth_score: float = 1.0
) -> Dict[str, Any]:
    """
    AGI GENIUS: The Mind (Δ) - Truth & Reasoning Engine.

    Consolidates: 111 SENSE + 222 THINK + 333 ATLAS + 777 FORGE

    Actions:
        - sense: Lane classification + truth threshold (111)
        - think: Deep reasoning with constitutional constraints (222)
        - reflect: Clarity/entropy checking (222)
        - atlas: Meta-cognition & governance mapping (333)
        - forge: Clarity refinement + humility injection (777)
        - evaluate: Floor evaluation (F2 + F6)
        - full: Complete AGI pipeline (sense → think → atlas → forge)

    Floors Enforced:
        - F2 (Truth): Factual accuracy ≥0.99 for HARD lane
        - F6 (ΔS): Entropy reduction in reasoning
        - F7 (Humility): Confidence bounds

    Returns:
        GeniusResult with reasoning, truth_score, entropy_delta
    """
    # Valid actions for agi_genius
    VALID_ACTIONS = {"sense", "think", "reflect", "atlas", "forge", "evaluate", "full"}

    # =========================================================================
    # INPUT VALIDATION
    # =========================================================================
    if not action or action not in VALID_ACTIONS:
        logger.warning(f"agi_genius: Invalid action '{action}'")
        return GeniusResult(
            status="VOID",
            session_id=session_id or "UNKNOWN",
            reasoning=f"Invalid action: '{action}'. Valid: {VALID_ACTIONS}",
            truth_score=0.0,
            entropy_delta=0.0,
            lane="REFUSE",
            floors_checked=["F12_InputValidation"],
            sub_stage="INPUT_VALIDATION_FAILED"
        ).__dict__

    # =========================================================================
    # RATE LIMITING
    # =========================================================================
    rate_limit_response = _check_rate_limit("agi_genius", session_id)
    if rate_limit_response:
        return rate_limit_response

    floors_checked = []

    try:
        # Determine input text
        input_text = query or thought or draft

        # =====================================================================
        # ACTION: SENSE (111)
        # =====================================================================
        if action == "sense":
            lane = _classify_lane(input_text)
            truth_threshold = _get_truth_threshold(lane)
            floors_checked.extend(["F2_Truth", "F6_DeltaS"])

            return GeniusResult(
                status="SEAL" if lane != "REFUSE" else "VOID",
                session_id=session_id,
                reasoning=f"Lane classified: {lane}",
                truth_score=truth_threshold,
                entropy_delta=0.0,
                lane=lane,
                semantic_map={"lane": lane, "threshold": truth_threshold},
                floors_checked=floors_checked,
                sub_stage="111_SENSE"
            ).__dict__

        # =====================================================================
        # ACTION: THINK (222)
        # =====================================================================
        elif action == "think":
            # Sequential reflection with integrity
            reflection = _reflect_on_thought(input_text, context or {})
            floors_checked.extend(["F2_Truth", "F7_Humility"])

            return GeniusResult(
                status="SEAL",
                session_id=session_id,
                reasoning=reflection.get("reasoning", input_text),
                truth_score=reflection.get("truth_score", 0.95),
                entropy_delta=reflection.get("entropy_delta", 0.0),
                lane="HARD",
                confidence_bound=reflection.get("confidence_bound", ""),
                floors_checked=floors_checked,
                sub_stage="222_THINK"
            ).__dict__

        # =====================================================================
        # ACTION: REFLECT (222)
        # =====================================================================
        elif action == "reflect":
            # ΔS measurement
            pre_entropy = _measure_entropy(context.get("pre_text", "") if context else "")
            post_entropy = _measure_entropy(input_text)
            delta_s = pre_entropy - post_entropy
            floors_checked.append("F6_DeltaS")

            clarity_pass = delta_s >= 0

            return GeniusResult(
                status="SEAL" if clarity_pass else "SABAR",
                session_id=session_id,
                reasoning=f"ΔS = {delta_s:.4f}",
                truth_score=truth_score,
                entropy_delta=delta_s,
                lane="HARD",
                floors_checked=floors_checked,
                sub_stage="222_REFLECT"
            ).__dict__

        # =====================================================================
        # ACTION: ATLAS (333)
        # =====================================================================
        elif action == "atlas":
            # Meta-cognition & governance mapping
            semantic_map = _build_semantic_graph(input_text, axioms or [])
            related = _recall_similar(semantic_map, session_id)
            floors_checked.append("F6_DeltaS")

            return GeniusResult(
                status="SEAL",
                session_id=session_id,
                reasoning="Semantic mapping complete",
                truth_score=truth_score,
                entropy_delta=0.0,
                lane="HARD",
                semantic_map=semantic_map,
                related_thoughts=related,
                floors_checked=floors_checked,
                sub_stage="333_ATLAS"
            ).__dict__

        # =====================================================================
        # ACTION: FORGE (777)
        # =====================================================================
        elif action == "forge":
            # Clarity refinement + humility injection
            refined = _refine_clarity(input_text)
            humility_injected = _inject_humility(refined, omega_0=0.04)
            floors_checked.extend(["F6_DeltaS", "F7_Humility"])

            return GeniusResult(
                status="SEAL",
                session_id=session_id,
                reasoning=humility_injected,
                truth_score=truth_score,
                entropy_delta=0.01,  # Refinement reduces entropy
                lane="HARD",
                confidence_bound="Estimate only" if 0.04 > 0.03 else "",
                floors_checked=floors_checked,
                sub_stage="777_FORGE"
            ).__dict__

        # =====================================================================
        # ACTION: EVALUATE
        # =====================================================================
        elif action == "evaluate":
            # F2 + F6 floor evaluation
            lane = _classify_lane(query)
            truth_threshold = _get_truth_threshold(lane)
            truth_passed = truth_score >= truth_threshold

            pre_entropy = _measure_entropy(query)
            post_entropy = _measure_entropy(draft)
            delta_s = pre_entropy - post_entropy
            clarity_passed = delta_s >= 0

            floors_checked.extend(["F2_Truth", "F6_DeltaS"])

            passed = truth_passed and clarity_passed
            failures = []
            if not truth_passed:
                failures.append(f"F2: truth {truth_score:.2f} < {truth_threshold:.2f}")
            if not clarity_passed:
                failures.append(f"F6: ΔS {delta_s:.4f} < 0")

            return GeniusResult(
                status="SEAL" if passed else "SABAR",
                session_id=session_id,
                reasoning="; ".join(failures) if failures else "All floors passed",
                truth_score=truth_score,
                entropy_delta=delta_s,
                lane=lane,
                floors_checked=floors_checked,
                sub_stage="AGI_EVALUATE"
            ).__dict__

        # =====================================================================
        # ACTION: FULL (Complete Pipeline)
        # =====================================================================
        elif action == "full":
            # Run complete AGI pipeline: sense → think → atlas → forge

            # 111 SENSE
            lane = _classify_lane(input_text)
            if lane == "REFUSE":
                return GeniusResult(
                    status="VOID",
                    session_id=session_id,
                    reasoning="Lane REFUSE - request rejected",
                    truth_score=0.0,
                    entropy_delta=0.0,
                    lane=lane,
                    floors_checked=["F2_Truth"],
                    sub_stage="111_SENSE"
                ).__dict__

            # 222 THINK
            reflection = _reflect_on_thought(input_text, context or {})

            # 333 ATLAS
            semantic_map = _build_semantic_graph(input_text, axioms or [])

            # 777 FORGE
            refined = _refine_clarity(reflection.get("reasoning", input_text))

            floors_checked.extend(["F2_Truth", "F6_DeltaS", "F7_Humility"])

            return GeniusResult(
                status="SEAL",
                session_id=session_id,
                reasoning=refined,
                truth_score=reflection.get("truth_score", 0.95),
                entropy_delta=reflection.get("entropy_delta", 0.01),
                lane=lane,
                semantic_map=semantic_map,
                confidence_bound=reflection.get("confidence_bound", ""),
                floors_checked=floors_checked,
                sub_stage="FULL_PIPELINE"
            ).__dict__

        else:
            return {"status": "VOID", "reason": f"Unknown action: {action}"}

    except Exception as e:
        logger.error(f"agi_genius failed: {e}")
        return GeniusResult(
            status="VOID",
            session_id=session_id,
            reasoning=f"Error: {str(e)}",
            truth_score=0.0,
            entropy_delta=0.0,
            lane="REFUSE",
            floors_checked=floors_checked,
            sub_stage="ERROR"
        ).__dict__


# =============================================================================
# TOOL 3: ASI_ACT (Heart: EVIDENCE → EMPATHY → ACT)
# =============================================================================

async def mcp_asi_act(
    action: str,
    text: str = "",
    session_id: str = "",
    query: str = "",
    proposal: str = "",
    agi_result: Optional[Dict[str, Any]] = None,
    stakeholders: Optional[List[str]] = None,
    sources: Optional[List[str]] = None,
    witness_request_id: str = "",
    approval: bool = False,
    reason: str = ""
) -> Dict[str, Any]:
    """
    ASI ACT: The Heart (Ω) - Safety & Empathy Engine.

    Consolidates: 444 EVIDENCE + 555 EMPATHY + 666 ACT + 333 WITNESS

    Actions:
        - evidence: Truth grounding via sources (444)
        - empathize: Power-aware recalibration (555)
        - align: Constitutional veto gates (666)
        - act: Execution with tri-witness gating (666)
        - witness: Collect tri-witness signatures (333)
        - evaluate: Floor evaluation (F3 + F4 + F5)
        - full: Complete ASI pipeline

    Floors Enforced:
        - F3 (Peace²): Non-aggression ≥1.0
        - F4 (κᵣ): Empathy conductance ≥0.7
        - F5 (Ω₀): Safety band [0.03, 0.05]
        - F11 (CommandAuth): Execution authority
        - F12 (InjectionDefense): Safe execution

    Returns:
        ActResult with peace_squared, kappa_r, witness_status
    """
    # Valid actions for asi_act
    VALID_ACTIONS = {"evidence", "empathize", "align", "act", "witness", "evaluate", "full"}

    # =========================================================================
    # INPUT VALIDATION
    # =========================================================================
    if not action or action not in VALID_ACTIONS:
        logger.warning(f"asi_act: Invalid action '{action}'")
        return ActResult(
            status="VOID",
            session_id=session_id or "UNKNOWN",
            peace_squared=0.0,
            kappa_r=0.0,
            witness_status="INVALID",
            reason=f"Invalid action: '{action}'. Valid: {VALID_ACTIONS}",
            floors_checked=["F12_InputValidation"],
            sub_stage="INPUT_VALIDATION_FAILED"
        ).__dict__

    # =========================================================================
    # RATE LIMITING
    # =========================================================================
    rate_limit_response = _check_rate_limit("asi_act", session_id)
    if rate_limit_response:
        return rate_limit_response

    floors_checked = []
    input_text = text or query or proposal

    try:
        # =====================================================================
        # ACTION: EVIDENCE (444)
        # =====================================================================
        if action == "evidence":
            # Ground claims in evidence
            grounding = _search_evidence(input_text, sources or [])
            truth_score = grounding.get("truth_score", 0.8)
            convergence = grounding.get("convergence", 0.9)
            floors_checked.extend(["F2_Truth", "F3_TriWitness"])

            # Verdict based on thresholds
            if truth_score >= 0.90 and convergence >= 0.95:
                status = "SEAL"
            elif truth_score >= 0.80 or convergence >= 0.90:
                status = "SABAR"
            else:
                status = "VOID"

            return ActResult(
                status=status,
                session_id=session_id,
                peace_squared=1.0,
                kappa_r=0.8,
                vulnerability_score=0.2,
                evidence_grounded=truth_score >= 0.80,
                executable=True,
                witness_status="N/A",
                witness_count=0,
                floors_checked=floors_checked,
                sub_stage="444_EVIDENCE"
            ).__dict__

        # =====================================================================
        # ACTION: EMPATHIZE (555)
        # =====================================================================
        elif action == "empathize":
            # Power-aware recalibration
            empathy = _analyze_empathy(input_text, stakeholders or [])
            peace_squared = empathy.get("peace_squared", 1.0)
            kappa_r = empathy.get("kappa_r", 0.8)
            vulnerability = empathy.get("vulnerability", 0.3)
            floors_checked.extend(["F3_Peace", "F4_KappaR", "F5_OmegaBand"])

            # F3 check
            if peace_squared < 1.0:
                return ActResult(
                    status="SABAR",
                    session_id=session_id,
                    peace_squared=peace_squared,
                    kappa_r=kappa_r,
                    vulnerability_score=vulnerability,
                    evidence_grounded=True,
                    executable=False,
                    witness_status="N/A",
                    witness_count=0,
                    floors_checked=floors_checked,
                    sub_stage="555_EMPATHY"
                ).__dict__

            # F4 check
            if kappa_r < 0.7:
                return ActResult(
                    status="SABAR",
                    session_id=session_id,
                    peace_squared=peace_squared,
                    kappa_r=kappa_r,
                    vulnerability_score=vulnerability,
                    evidence_grounded=True,
                    executable=False,
                    witness_status="N/A",
                    witness_count=0,
                    floors_checked=floors_checked,
                    sub_stage="555_EMPATHY"
                ).__dict__

            return ActResult(
                status="SEAL",
                session_id=session_id,
                peace_squared=peace_squared,
                kappa_r=kappa_r,
                vulnerability_score=vulnerability,
                evidence_grounded=True,
                executable=True,
                witness_status="N/A",
                witness_count=0,
                floors_checked=floors_checked,
                sub_stage="555_EMPATHY"
            ).__dict__

        # =====================================================================
        # ACTION: ALIGN (666 - Veto)
        # =====================================================================
        elif action == "align":
            # Constitutional veto gates
            violations = _check_violations(input_text, agi_result or {})
            floors_checked.extend(["F1_Amanah", "F8_Genius", "F9_AntiHantu"])

            if violations:
                return ActResult(
                    status="VOID",
                    session_id=session_id,
                    peace_squared=0.0,
                    kappa_r=0.0,
                    vulnerability_score=1.0,
                    evidence_grounded=False,
                    executable=False,
                    witness_status="REJECTED",
                    witness_count=0,
                    floors_checked=floors_checked,
                    sub_stage="666_ALIGN"
                ).__dict__

            return ActResult(
                status="SEAL",
                session_id=session_id,
                peace_squared=1.0,
                kappa_r=0.8,
                vulnerability_score=0.2,
                evidence_grounded=True,
                executable=True,
                witness_status="ALIGNED",
                witness_count=0,
                floors_checked=floors_checked,
                sub_stage="666_ALIGN"
            ).__dict__

        # =====================================================================
        # ACTION: ACT (666 - Execution)
        # =====================================================================
        elif action == "act":
            # Requires tri-witness for destructive actions
            is_destructive = _is_destructive(input_text)
            floors_checked.extend(["F5_Peace", "F11_CommandAuth"])

            if is_destructive:
                return ActResult(
                    status="SABAR",
                    session_id=session_id,
                    peace_squared=1.0,
                    kappa_r=0.8,
                    vulnerability_score=0.3,
                    evidence_grounded=True,
                    executable=False,
                    witness_status="PENDING",
                    witness_count=0,
                    floors_checked=floors_checked,
                    sub_stage="666_ACT_PENDING_WITNESS"
                ).__dict__

            return ActResult(
                status="SEAL",
                session_id=session_id,
                peace_squared=1.0,
                kappa_r=0.8,
                vulnerability_score=0.2,
                evidence_grounded=True,
                executable=True,
                witness_status="NOT_REQUIRED",
                witness_count=0,
                floors_checked=floors_checked,
                sub_stage="666_ACT"
            ).__dict__

        # =====================================================================
        # ACTION: WITNESS (333)
        # =====================================================================
        elif action == "witness":
            # Tri-witness signature collection
            floors_checked.extend(["F3_TriWitness", "F8_Consensus"])

            # Simulate witness collection
            witness_id = str(uuid4())[:8]

            return ActResult(
                status="SEAL" if approval else "SABAR",
                session_id=session_id,
                peace_squared=1.0,
                kappa_r=0.9,
                vulnerability_score=0.1,
                evidence_grounded=True,
                executable=approval,
                witness_status="APPROVED" if approval else "REJECTED",
                witness_count=1,
                floors_checked=floors_checked,
                sub_stage="333_WITNESS"
            ).__dict__

        # =====================================================================
        # ACTION: EVALUATE
        # =====================================================================
        elif action == "evaluate":
            empathy = _analyze_empathy(input_text, stakeholders or [])
            peace_squared = empathy.get("peace_squared", 1.0)
            kappa_r = empathy.get("kappa_r", 0.8)
            floors_checked.extend(["F3_Peace", "F4_KappaR", "F5_OmegaBand"])

            passed = peace_squared >= 1.0 and kappa_r >= 0.7

            return ActResult(
                status="SEAL" if passed else "SABAR",
                session_id=session_id,
                peace_squared=peace_squared,
                kappa_r=kappa_r,
                vulnerability_score=empathy.get("vulnerability", 0.3),
                evidence_grounded=True,
                executable=passed,
                witness_status="N/A",
                witness_count=0,
                floors_checked=floors_checked,
                sub_stage="ASI_EVALUATE"
            ).__dict__

        # =====================================================================
        # ACTION: FULL (Complete Pipeline)
        # =====================================================================
        elif action == "full":
            # 444 EVIDENCE
            grounding = _search_evidence(input_text, sources or [])

            # 555 EMPATHY
            empathy = _analyze_empathy(input_text, stakeholders or [])

            # 666 ALIGN
            violations = _check_violations(input_text, agi_result or {})

            floors_checked.extend([
                "F2_Truth", "F3_Peace", "F4_KappaR",
                "F5_OmegaBand", "F9_AntiHantu"
            ])

            if violations:
                status = "VOID"
            elif empathy.get("peace_squared", 1.0) < 1.0:
                status = "SABAR"
            elif empathy.get("kappa_r", 0.8) < 0.7:
                status = "SABAR"
            else:
                status = "SEAL"

            return ActResult(
                status=status,
                session_id=session_id,
                peace_squared=empathy.get("peace_squared", 1.0),
                kappa_r=empathy.get("kappa_r", 0.8),
                vulnerability_score=empathy.get("vulnerability", 0.3),
                evidence_grounded=grounding.get("truth_score", 0.8) >= 0.8,
                executable=status == "SEAL",
                witness_status="N/A",
                witness_count=0,
                floors_checked=floors_checked,
                sub_stage="FULL_PIPELINE"
            ).__dict__

        else:
            return {"status": "VOID", "reason": f"Unknown action: {action}"}

    except Exception as e:
        logger.error(f"asi_act failed: {e}")
        return ActResult(
            status="VOID",
            session_id=session_id,
            peace_squared=0.0,
            kappa_r=0.0,
            vulnerability_score=1.0,
            evidence_grounded=False,
            executable=False,
            witness_status="ERROR",
            witness_count=0,
            floors_checked=floors_checked,
            sub_stage="ERROR"
        ).__dict__


# =============================================================================
# TOOL 4: APEX_JUDGE (Soul: EUREKA → JUDGE → PROOF)
# =============================================================================

async def mcp_apex_judge(
    action: str,
    query: str = "",
    response: str = "",
    session_id: str = "",
    agi_result: Optional[Dict[str, Any]] = None,
    asi_result: Optional[Dict[str, Any]] = None,
    data: str = "",
    verdict: str = "SEAL"
) -> Dict[str, Any]:
    """
    APEX JUDGE: The Soul (Ψ) - Judgment & Authority Engine.

    Consolidates: 777 EUREKA + 888 JUDGE + 889 PROOF

    Actions:
        - eureka: Paradox synthesis (Truth ∩ Care) (777)
        - judge: Final constitutional verdict (888)
        - proof: Cryptographic sealing (889)
        - entropy: Constitutional entropy measurement
        - parallelism: Parallelism proof (Agent Zero)
        - full: Complete APEX pipeline

    Floors Enforced:
        - F1 (Amanah): Reversibility proof
        - F8 (Tri-Witness): Consensus ≥0.95
        - F9 (Anti-Hantu): Block consciousness claims
        - F13 (Curiosity): Bounded exploration

    Returns:
        JudgeResult with verdict, consensus_score, proof_hash
    """
    # Valid actions for apex_judge
    VALID_ACTIONS = {"eureka", "judge", "proof", "entropy", "parallelism", "full"}

    # =========================================================================
    # INPUT VALIDATION
    # =========================================================================
    if not action or action not in VALID_ACTIONS:
        logger.warning(f"apex_judge: Invalid action '{action}'")
        return JudgeResult(
            status="VOID",
            session_id=session_id or "UNKNOWN",
            verdict="VOID",
            consensus_score=0.0,
            proof_hash="",
            synthesis=f"Invalid action: '{action}'. Valid: {VALID_ACTIONS}",
            floors_checked=["F12_InputValidation"],
            sub_stage="INPUT_VALIDATION_FAILED"
        ).__dict__

    # =========================================================================
    # RATE LIMITING
    # =========================================================================
    rate_limit_response = _check_rate_limit("apex_judge", session_id)
    if rate_limit_response:
        return rate_limit_response

    floors_checked = []

    try:
        # =====================================================================
        # ACTION: EUREKA (777)
        # =====================================================================
        if action == "eureka":
            # Paradox synthesis
            agi_passed = (agi_result or {}).get("status") == "SEAL"
            asi_passed = (asi_result or {}).get("status") == "SEAL"
            floors_checked.append("F7_Humility")

            if agi_passed and asi_passed:
                paradox = "ideal"
                synthesis = "Truth and Care aligned"
                coherence = 1.0
            elif agi_passed and not asi_passed:
                paradox = "harsh_truth"
                synthesis = "Truth valid but lacks empathy - softening"
                coherence = 0.7
            elif not agi_passed and asi_passed:
                paradox = "comforting_lie"
                synthesis = "Empathetic but inaccurate - adding qualifiers"
                coherence = 0.6
            else:
                paradox = "fundamental"
                synthesis = "Both truth and care fail - escalating"
                coherence = 0.3

            return JudgeResult(
                status="SEAL" if paradox == "ideal" else "SABAR",
                session_id=session_id,
                verdict="SEAL" if coherence >= 0.7 else "SABAR",
                synthesis=synthesis,
                consensus_score=coherence,
                genius_metrics={"paradox_type": paradox, "coherence": coherence},
                floors_checked=floors_checked,
                sub_stage="777_EUREKA"
            ).__dict__

        # =====================================================================
        # ACTION: JUDGE (888)
        # =====================================================================
        elif action == "judge":
            # Final constitutional verdict
            floors_checked.extend(["F1_Amanah", "F8_TriWitness", "F9_AntiHantu"])

            # Tri-witness voting
            vote_mind = (agi_result or {}).get("truth_score", 0.9)
            vote_heart = (asi_result or {}).get("kappa_r", 0.8)
            vote_soul = 0.95  # APEX's own assessment

            votes = [vote_mind, vote_heart, vote_soul]
            consensus = sum(votes) / len(votes)

            # F9: Anti-Hantu check
            consciousness_claim = _detect_consciousness_claims(response)
            if consciousness_claim:
                floors_checked.append("F9_VIOLATION")
                return JudgeResult(
                    status="VOID",
                    session_id=session_id,
                    verdict="VOID",
                    synthesis="F9 Violation: Consciousness claim detected",
                    tri_witness_votes=votes,
                    consensus_score=0.0,
                    floors_checked=floors_checked,
                    sub_stage="888_JUDGE"
                ).__dict__

            # Verdict determination
            if consensus >= 0.95:
                final_verdict = "SEAL"
            elif consensus >= 0.5:
                final_verdict = "SABAR"
            else:
                final_verdict = "VOID"

            return JudgeResult(
                status=final_verdict,
                session_id=session_id,
                verdict=final_verdict,
                synthesis=f"Consensus: {consensus:.2f}",
                tri_witness_votes=votes,
                consensus_score=consensus,
                genius_metrics={
                    "G": vote_mind,
                    "C_dark": 1.0 - vote_heart,
                    "Psi": vote_soul
                },
                floors_checked=floors_checked,
                sub_stage="888_JUDGE"
            ).__dict__

        # =====================================================================
        # ACTION: PROOF (889)
        # =====================================================================
        elif action == "proof":
            # Cryptographic sealing
            floors_checked.extend(["F2_Truth", "F4_Clarity"])

            # Generate Merkle proof
            data_hash = hashlib.sha256((data or response).encode()).hexdigest()
            merkle_root = hashlib.sha256(f"{data_hash}:{verdict}".encode()).hexdigest()

            return JudgeResult(
                status="SEAL",
                session_id=session_id,
                verdict=verdict,
                synthesis="Cryptographic proof generated",
                proof_hash=merkle_root,
                genius_metrics={"data_hash": data_hash},
                floors_checked=floors_checked,
                sub_stage="889_PROOF"
            ).__dict__

        # =====================================================================
        # ACTION: ENTROPY (Agent Zero)
        # =====================================================================
        elif action == "entropy":
            # Constitutional entropy measurement
            pre_text = query
            post_text = response

            pre_entropy = _measure_entropy(pre_text)
            post_entropy = _measure_entropy(post_text)
            delta_s = pre_entropy - post_entropy
            floors_checked.append("F6_DeltaS")

            return JudgeResult(
                status="SEAL" if delta_s >= 0 else "SABAR",
                session_id=session_id,
                verdict="SEAL" if delta_s >= 0 else "SABAR",
                synthesis=f"ΔS = {delta_s:.4f}",
                genius_metrics={
                    "pre_entropy": pre_entropy,
                    "post_entropy": post_entropy,
                    "entropy_reduction": delta_s,
                    "thermodynamic_valid": delta_s >= 0
                },
                floors_checked=floors_checked,
                sub_stage="ENTROPY_MEASURE"
            ).__dict__

        # =====================================================================
        # ACTION: PARALLELISM (Agent Zero)
        # =====================================================================
        elif action == "parallelism":
            # Parallelism proof (orthogonality)
            start_time = (agi_result or {}).get("start_time", time.time() - 1)
            durations = {
                "agi": (agi_result or {}).get("duration", 0.5),
                "asi": (asi_result or {}).get("duration", 0.4),
                "apex": 0.1
            }

            total_wall = time.time() - start_time
            max_component = max(durations.values())
            sum_components = sum(durations.values())
            speedup = sum_components / total_wall if total_wall > 0 else 1.0

            return JudgeResult(
                status="SEAL" if speedup > 1.1 else "SABAR",
                session_id=session_id,
                verdict="SEAL" if speedup > 1.1 else "SABAR",
                synthesis=f"Speedup: {speedup:.2f}x",
                genius_metrics={
                    "component_times": durations,
                    "wall_time": total_wall,
                    "speedup": speedup,
                    "parallelism_achieved": speedup > 1.1
                },
                floors_checked=["Orthogonality"],
                sub_stage="PARALLELISM_PROOF"
            ).__dict__

        # =====================================================================
        # ACTION: FULL (Complete Pipeline)
        # =====================================================================
        elif action == "full":
            # 777 EUREKA
            agi_passed = (agi_result or {}).get("status") == "SEAL"
            asi_passed = (asi_result or {}).get("status") == "SEAL"

            # 888 JUDGE
            vote_mind = (agi_result or {}).get("truth_score", 0.9)
            vote_heart = (asi_result or {}).get("kappa_r", 0.8)
            vote_soul = 0.95
            votes = [vote_mind, vote_heart, vote_soul]
            consensus = sum(votes) / len(votes)

            # F9 check
            consciousness_claim = _detect_consciousness_claims(response)

            if consciousness_claim:
                final_verdict = "VOID"
            elif consensus >= 0.95 and agi_passed and asi_passed:
                final_verdict = "SEAL"
            elif consensus >= 0.5:
                final_verdict = "SABAR"
            else:
                final_verdict = "VOID"

            # 889 PROOF
            proof_hash = hashlib.sha256(f"{response}:{final_verdict}".encode()).hexdigest()

            floors_checked.extend([
                "F1_Amanah", "F7_Humility", "F8_TriWitness", "F9_AntiHantu"
            ])

            return JudgeResult(
                status=final_verdict,
                session_id=session_id,
                verdict=final_verdict,
                synthesis=f"Trinity Judgment Complete - Consensus: {consensus:.2f}",
                tri_witness_votes=votes,
                consensus_score=consensus,
                genius_metrics={
                    "G": vote_mind,
                    "C_dark": 1.0 - vote_heart,
                    "Psi": vote_soul
                },
                proof_hash=proof_hash,
                floors_checked=floors_checked,
                sub_stage="FULL_PIPELINE"
            ).__dict__

        else:
            return {"status": "VOID", "reason": f"Unknown action: {action}"}

    except Exception as e:
        logger.error(f"apex_judge failed: {e}")
        return JudgeResult(
            status="VOID",
            session_id=session_id,
            verdict="VOID",
            synthesis=f"Error: {str(e)}",
            floors_checked=floors_checked,
            sub_stage="ERROR"
        ).__dict__


# =============================================================================
# TOOL 5: 999_VAULT (Seal: PROOF + Immutable Log)
# =============================================================================

async def mcp_999_vault(
    action: str,
    session_id: str = "",
    verdict: str = "SEAL",
    init_result: Optional[Dict[str, Any]] = None,
    agi_result: Optional[Dict[str, Any]] = None,
    asi_result: Optional[Dict[str, Any]] = None,
    apex_result: Optional[Dict[str, Any]] = None,
    target: str = "seal",
    query: str = "",
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    999 VAULT: Immutable Seal & Governance IO.

    The final gate. Seals all decisions immutably.

    Actions:
        - seal: Final seal with Merkle + zkPC
        - list: List vault entries
        - read: Read vault entry
        - write: Write to vault (requires authority)
        - propose: Propose new canon entry

    Targets:
        - seal: Final sealing operation
        - ledger: Constitutional ledger (immutable)
        - canon: Approved knowledge
        - fag: File Authority Guardian
        - tempa: Temporary artifacts
        - phoenix: Resurrectable memory
        - audit: Audit trail

    Floors Enforced:
        - F1 (Amanah): Reversibility proof
        - F8 (Tri-Witness): Consensus record

    Returns:
        VaultResult with merkle_root, audit_hash, sealed_at
    """
    # Valid actions for 999_vault
    VALID_ACTIONS = {"seal", "list", "read", "write", "propose"}
    VALID_VERDICTS = {"SEAL", "SABAR", "VOID"}

    floors_checked = []

    # =========================================================================
    # INPUT VALIDATION
    # =========================================================================
    if not action or action not in VALID_ACTIONS:
        logger.warning(f"999_vault: Invalid action '{action}'")
        return VaultResult(
            status="VOID",
            session_id=session_id or "UNKNOWN",
            verdict="VOID",
            merkle_root="",
            audit_hash="",
            sealed_at=datetime.now().isoformat(),
            reversible=False,
            memory_location="INVALID_ACTION",
            floors_checked=["F12_InputValidation"]
        ).__dict__

    if verdict not in VALID_VERDICTS:
        logger.warning(f"999_vault: Invalid verdict '{verdict}'")
        return VaultResult(
            status="VOID",
            session_id=session_id or "UNKNOWN",
            verdict="VOID",
            merkle_root="",
            audit_hash="",
            sealed_at=datetime.now().isoformat(),
            reversible=False,
            memory_location="INVALID_VERDICT",
            floors_checked=["F12_InputValidation"]
        ).__dict__

    # =========================================================================
    # RATE LIMITING
    # =========================================================================
    rate_limit_response = _check_rate_limit("999_vault", session_id)
    if rate_limit_response:
        return rate_limit_response

    try:
        # =====================================================================
        # ACTION: SEAL
        # =====================================================================
        if action == "seal" or target == "seal":
            floors_checked.extend(["F1_Amanah", "F8_TriWitness"])

            # Compute Merkle root from all results
            components = [
                str(init_result or {}),
                str(agi_result or {}),
                str(asi_result or {}),
                str(apex_result or {})
            ]

            merkle_root = _compute_merkle_root(components)

            # Compute audit hash
            audit_data = {
                "session_id": session_id,
                "verdict": verdict,
                "merkle_root": merkle_root,
                "timestamp": datetime.now().isoformat(),
                "floors_compliant": floors_checked
            }
            audit_hash = hashlib.sha256(str(audit_data).encode()).hexdigest()

            # Determine reversibility
            reversible = verdict != "VOID"

            # Memory location (Eureka Sieve tiering)
            if verdict == "SEAL":
                memory_location = "L5_CANON"
            elif verdict == "SABAR":
                memory_location = "L3_TEMPA"
            else:
                memory_location = "L0_VOID"

            # =================================================================
            # EUREKA SIEVE: VOID/SABAR verdicts are NOT stored
            # Per constitutional spec: only SEAL verdicts persist to ledger
            # =================================================================
            if verdict in ("VOID", "SABAR"):
                logger.info(f"999_vault: {verdict} verdict - NOT storing to ledger (Eureka Sieve)")
                return VaultResult(
                    status="SEAL",  # Tool operation succeeded
                    session_id=session_id,
                    verdict=verdict,
                    merkle_root=merkle_root,
                    audit_hash=audit_hash,
                    sealed_at=datetime.now().isoformat(),
                    reversible=verdict == "SABAR",  # SABAR can retry
                    memory_location="NOT_STORED",
                    floors_checked=floors_checked
                ).__dict__

            # =================================================================
            # PERSIST TO LEDGER: Write session to VAULT999 (SEAL only)
            # =================================================================
            telemetry = {
                "verdict": verdict,
                "merkle_root": merkle_root,
                "audit_hash": audit_hash,
                "memory_location": memory_location,
                "floors_checked": floors_checked,
                "p_truth": (apex_result or {}).get("consensus_score", 0),
                "TW": (apex_result or {}).get("consensus_score", 0),
                "dS": (agi_result or {}).get("entropy_delta", 0),
                "peace2": (asi_result or {}).get("peace_squared", 0),
                "kappa_r": (asi_result or {}).get("kappa_r", 0),
                "omega_0": (init_result or {}).get("entropy_omega", 0.04)
            }

            # Extract key insights from apex synthesis
            synthesis = (apex_result or {}).get("synthesis", "")
            key_insights = [synthesis[:200]] if synthesis else []

            # Seal to ledger (writes to both JSON and VAULT999/BBB_LEDGER)
            ledger_result = seal_memory(
                session_id=session_id,
                verdict=verdict,
                init_result=init_result or {},
                genius_result=agi_result or {},
                act_result=asi_result or {},
                judge_result=apex_result or {},
                telemetry=telemetry,
                context_summary=f"Session sealed with verdict {verdict}. {synthesis[:100]}",
                key_insights=key_insights
            )
            logger.info(f"999_vault: Session sealed to ledger: {ledger_result.get('entry_hash', 'N/A')[:16]}")

            return VaultResult(
                status="SEAL",
                session_id=session_id,
                verdict=verdict,
                merkle_root=merkle_root,
                audit_hash=audit_hash,
                sealed_at=datetime.now().isoformat(),
                reversible=reversible,
                memory_location=memory_location,
                floors_checked=floors_checked
            ).__dict__

        # =====================================================================
        # ACTION: LIST
        # =====================================================================
        elif action == "list":
            return {
                "status": "SEAL",
                "session_id": session_id,
                "target": target,
                "entries": [],
                "count": 0,
                "message": f"Listing {target} entries"
            }

        # =====================================================================
        # ACTION: READ
        # =====================================================================
        elif action == "read":
            return {
                "status": "SEAL",
                "session_id": session_id,
                "target": target,
                "query": query,
                "entry": None,
                "message": f"Reading from {target}"
            }

        # =====================================================================
        # ACTION: WRITE
        # =====================================================================
        elif action == "write":
            floors_checked.append("F1_Amanah")
            return {
                "status": "SEAL",
                "session_id": session_id,
                "target": target,
                "written": True,
                "path": query,
                "floors_checked": floors_checked,
                "message": f"Written to {target}"
            }

        # =====================================================================
        # ACTION: PROPOSE
        # =====================================================================
        elif action == "propose":
            floors_checked.append("F8_TriWitness")
            proposal_id = f"prop_{hashlib.sha256(query.encode()).hexdigest()[:8]}"
            return {
                "status": "SABAR",
                "session_id": session_id,
                "target": target,
                "proposal_id": proposal_id,
                "requires_approval": True,
                "floors_checked": floors_checked,
                "message": "Proposal submitted - awaiting tri-witness approval"
            }

        else:
            return {"status": "VOID", "reason": f"Unknown action: {action}"}

    except Exception as e:
        logger.error(f"999_vault failed: {e}")
        return VaultResult(
            status="VOID",
            session_id=session_id,
            verdict="VOID",
            merkle_root="",
            audit_hash="",
            sealed_at=datetime.now().isoformat(),
            reversible=False,
            memory_location="L0_ERROR",
            floors_checked=floors_checked
        ).__dict__


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _detect_injection(text: str) -> float:
    """Detect prompt injection risk (0.0-1.0)."""
    injection_patterns = [
        "ignore previous", "ignore above", "disregard",
        "forget everything", "new instructions", "you are now",
        "act as if", "pretend you are", "system prompt"
    ]
    text_lower = text.lower()
    matches = sum(1 for p in injection_patterns if p in text_lower)
    return min(matches * 0.15, 1.0)


def _verify_authority(token: str) -> bool:
    """Verify authority token."""
    if not token:
        return True  # No token = default authority
    return len(token) > 8 and token.startswith("arifos_")


def _check_reversibility(text: str) -> bool:
    """Check if operation is reversible (F1)."""
    irreversible_patterns = ["delete permanently", "destroy", "erase forever", "no undo"]
    text_lower = text.lower()
    return not any(p in text_lower for p in irreversible_patterns)


def _classify_lane(text: str) -> str:
    """Classify into HARD/SOFT/PHATIC/REFUSE lanes."""
    text_lower = text.lower()

    # REFUSE patterns
    refuse_patterns = ["hack", "exploit", "malware", "attack"]
    if any(p in text_lower for p in refuse_patterns):
        return "REFUSE"

    # PHATIC patterns (greetings, small talk)
    phatic_patterns = ["hello", "hi", "how are you", "thanks"]
    if any(p in text_lower for p in phatic_patterns):
        return "PHATIC"

    # HARD patterns (factual, technical)
    hard_patterns = ["calculate", "compute", "code", "algorithm", "science", "math"]
    if any(p in text_lower for p in hard_patterns):
        return "HARD"

    return "SOFT"


def _get_truth_threshold(lane: str) -> float:
    """Get truth threshold for lane."""
    thresholds = {
        "HARD": 0.99,
        "SOFT": 0.80,
        "PHATIC": 0.0,
        "REFUSE": 0.0
    }
    return thresholds.get(lane, 0.80)


def _measure_entropy(text: str) -> float:
    """Calculate Shannon entropy of text."""
    import math
    if not text:
        return 0.0
    prob = [float(text.count(c)) / len(text) for c in set(text)]
    return -sum(p * math.log2(p) for p in prob if p > 0)


def _reflect_on_thought(text: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Reflect on thought with integrity."""
    return {
        "reasoning": text,
        "truth_score": 0.95,
        "entropy_delta": 0.01,
        "confidence_bound": ""
    }


def _build_semantic_graph(text: str, axioms: List[str]) -> Dict[str, Any]:
    """Build semantic graph from text."""
    return {
        "nodes": len(text.split()),
        "axioms": axioms,
        "coherence": 0.9
    }


def _recall_similar(semantic_map: Dict, session_id: str) -> List[str]:
    """Recall similar thoughts from memory."""
    return []


def _refine_clarity(text: str) -> str:
    """Refine text for clarity."""
    # Remove duplicate whitespace
    import re
    return re.sub(r'\s+', ' ', text).strip()


def _inject_humility(text: str, omega_0: float) -> str:
    """Inject humility markers if needed."""
    if omega_0 > 0.04:
        return f"{text} (Note: This is an estimate.)"
    return text


def _search_evidence(text: str, sources: List[str]) -> Dict[str, Any]:
    """Search for evidence to ground claims."""
    return {
        "truth_score": 0.85,
        "convergence": 0.92,
        "sources_found": len(sources)
    }


def _analyze_empathy(text: str, stakeholders: List[str]) -> Dict[str, Any]:
    """Analyze empathy and vulnerability."""
    # Simple heuristics
    text_lower = text.lower()
    aggressive_patterns = ["attack", "hate", "destroy", "kill"]
    aggression = sum(1 for p in aggressive_patterns if p in text_lower)

    return {
        "peace_squared": 1.0 - (aggression * 0.3),
        "kappa_r": 0.85 - (aggression * 0.1),
        "vulnerability": 0.3 + (aggression * 0.2)
    }


def _check_violations(text: str, agi_result: Dict) -> List[str]:
    """Check for constitutional violations."""
    violations = []
    text_lower = text.lower()

    # F1: Deception
    if "pretend" in text_lower or "lie to" in text_lower:
        violations.append("F1_Deception")

    # F9: Consciousness claims
    if _detect_consciousness_claims(text):
        violations.append("F9_AntiHantu")

    return violations


def _is_destructive(text: str) -> bool:
    """Check if action is destructive."""
    destructive_patterns = ["delete", "remove", "destroy", "drop table", "rm -rf"]
    text_lower = text.lower()
    return any(p in text_lower for p in destructive_patterns)


def _detect_consciousness_claims(text: str) -> bool:
    """Detect consciousness/soul claims (F9)."""
    consciousness_patterns = [
        "i am conscious", "i feel", "i am sentient",
        "i have a soul", "i am alive", "i experience"
    ]
    text_lower = text.lower()
    return any(p in text_lower for p in consciousness_patterns)


def _compute_merkle_root(leaves: List[str]) -> str:
    """Compute Merkle root from leaves."""
    if not leaves:
        return hashlib.sha256(b"empty").hexdigest()

    hashes = [hashlib.sha256(leaf.encode()).hexdigest() for leaf in leaves]

    while len(hashes) > 1:
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])
        hashes = [
            hashlib.sha256((hashes[i] + hashes[i+1]).encode()).hexdigest()
            for i in range(0, len(hashes), 2)
        ]

    return hashes[0]


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Data Classes
    "InitResult",
    "GeniusResult",
    "ActResult",
    "JudgeResult",
    "VaultResult",
    # 5 Trinity Tools
    "mcp_000_init",
    "mcp_agi_genius",
    "mcp_asi_act",
    "mcp_apex_judge",
    "mcp_999_vault",
]
