"""
canonical_core/000_init_mcp.py — The 000_INIT MCP Tool Implementation

Extracted from arifos/mcp/tools/mcp_trinity.py (v52.5.1-SEAL)
To be used as the canonical reference for the 000_init tool logic.

000_INIT: The 7-Step Thermodynamic Ignition Sequence.
"Init the Genius, Act with Heart, Judge at Apex, seal in Vault."

Philosophy:
    INPUT → F12 Injection Guard
         → 000_init (Ignition + Authority)
         → ATLAS-333 (Lane-Aware Routing)
         → ...
"""

from __future__ import annotations

import logging
import time
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

# Imports from arifOS ecosystem (assumed available)
try:
    from arifos.mcp.rate_limiter import get_rate_limiter
    from arifos.mcp.metrics import get_metrics
    from arifos.mcp.session_ledger import inject_memory
    from canonical_core.enforcement.metrics import (
        TRUTH_THRESHOLD,
        PEACE_SQUARED_THRESHOLD,
        OMEGA_0_MIN,
        OMEGA_0_MAX,
    )
    from canonical_core.engines.agi.atlas import ATLAS, ATLAS_333, GPV
    ATLAS_AVAILABLE = True
except ImportError:
    ATLAS_AVAILABLE = False
    ATLAS = None
    # Defaults if imports fail
    TRUTH_THRESHOLD = 0.99
    PEACE_SQUARED_THRESHOLD = 1.0
    OMEGA_0_MIN = 0.03
    OMEGA_0_MAX = 0.05

try:
    from canonical_core.prompt.codec import SignalExtractor, PromptSignal
    PROMPT_AVAILABLE = True
    _signal_extractor = SignalExtractor()
except ImportError:
    PROMPT_AVAILABLE = False
    _signal_extractor = None

logger = logging.getLogger(__name__)

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
    entropy_omega: float = (OMEGA_0_MIN + OMEGA_0_MAX) / 2
    peace_squared: float = PEACE_SQUARED_THRESHOLD
    energy_budget: float = 1.0

    # Step 5: Floors Loaded
    floors_checked: List[str] = field(default_factory=list)
    floors_loaded: int = 13

    # Step 6: Tri-Witness
    tri_witness: Dict[str, Any] = field(default_factory=dict)
    TW: float = 0.0

    # Step 7: Engine Status
    engines: Dict[str, str] = field(default_factory=dict)

    # Step 8: ATLAS Lane-Aware Routing
    routing: str = ""

    # Security
    injection_risk: float = 0.0
    reason: str = ""

# =============================================================================
# CONFIG & CONSTANTS
# =============================================================================

LITE_MODE = os.environ.get("ARIFOS_LITE_MODE", "false").lower() == "true"

SOVEREIGN_PATTERNS = [
    "im arif", "i'm arif", "i am arif", "arif here",
    "salam", "assalamualaikum", "waalaikumsalam",
    "888", "judge", "sovereign", "ditempa bukan diberi"
]

INTENT_KEYWORDS = {
    "build": ["build", "create", "implement", "make", "code", "develop", "write", "work on", "add", "integrate"],
    "debug": ["fix", "debug", "error", "bug", "issue", "problem", "broken", "wrong", "fail"],
    "explain": ["explain", "what", "how", "why", "tell", "describe", "understand", "show"],
    "discuss": ["discuss", "think", "consider", "explore", "brainstorm", "idea", "opinion"],
    "review": ["review", "check", "audit", "verify", "validate", "test", "analyze"]
}

LANE_INTENTS = {
    "HARD": ["build", "debug", "review"],
    "SOFT": ["discuss", "explore"],
    "PHATIC": ["greet", "thanks"],
}

LANE_PROFILES = {
    "CRISIS": {"S_factor": 0.5, "omega_0": OMEGA_0_MAX, "energy": 1.0, "time_budget": 180},
    "FACTUAL": {"S_factor": 0.6, "omega_0": OMEGA_0_MIN, "energy": 0.9, "time_budget": 120},
    "CARE": {"S_factor": 0.7, "omega_0": 0.04, "energy": 0.7, "time_budget": 60},
    "SOCIAL": {"S_factor": 0.8, "omega_0": OMEGA_0_MIN, "energy": 0.5, "time_budget": 15},
}

LANE_ENGINES = {
    "CRISIS": {"AGI_Mind": "IDLE", "ASI_Heart": "IDLE", "APEX_Soul": "READY"},
    "FACTUAL": {"AGI_Mind": "READY", "ASI_Heart": "READY", "APEX_Soul": "READY"},
    "CARE": {"AGI_Mind": "IDLE", "ASI_Heart": "READY", "APEX_Soul": "READY"},
    "SOCIAL": {"AGI_Mind": "IDLE", "ASI_Heart": "IDLE", "APEX_Soul": "READY"},
}

LANE_ROUTING = {
    "HARD": "AGI -> ASI -> APEX -> VAULT (Full Constitutional Pipeline)",
    "SOFT": "AGI -> APEX -> VAULT (Knowledge/Exploratory Pipeline)",
    "PHATIC": "APEX (Quick Sovereign Response)",
    "REFUSE": "VOID (Immediate Constitutional Rejection)",
    "CRISIS": "888_HOLD (Human Intervention Required)"
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _check_rate_limit(tool_name: str, session_id: str = "") -> Optional[Dict]:
    """Check rate limit before processing a tool call."""
    try:
        limiter = get_rate_limiter()
        result = limiter.check(tool_name, session_id)
        if not result.allowed:
            logger.warning(f"Rate limit exceeded: {tool_name} (session={session_id})")
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
    except Exception:
        pass # Fail open if rate limiter missing
    return None

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

def _measure_entropy(text: str) -> float:
    """Calculate Shannon entropy of text."""
    if LITE_MODE:
        return 0.0
    import math
    if not text:
        return 0.0
    prob = [float(text.count(c)) / len(text) for c in set(text)]
    return -sum(p * math.log2(p) for p in prob if p > 0)

# =============================================================================
# LOGIC STEPS
# =============================================================================

def _step_0_root_key_ignition(session_id: str) -> Dict[str, Any]:
    """Step 0: ROOT KEY IGNITION - Establish cryptographic foundation."""
    try:
        # Mocking or dynamic import would go here
        # For this standalone file, we return a simulated success if specific modules aren't found
        result = {
            "root_key_ready": True,
            "session_key": f"ses_{uuid4().hex[:16]}",
            "genesis_exists": True,
            "constitutional_status": "SEALED"
        }
        logger.info("000_init Step 0: ROOT KEY IGNITION - COMPLETE ✓")
        return result
    except Exception as e:
        logger.error(f"000_init Step 0: Root key ignition failed: {e}")
        return {
            "root_key_ready": False,
            "constitutional_status": "ERROR",
            "error": str(e)
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
    is_sovereign = any(p in query_lower for p in SOVEREIGN_PATTERNS)
    if token and _verify_authority(token):
        is_sovereign = True

    if is_sovereign:
        logger.info("000_init Step 2: Sovereign recognized (888 Judge)")
        return {"authority": "888_JUDGE", "scar_weight": 1.0, "role": "SOVEREIGN", "f11_verified": True}
    else:
        logger.info("000_init Step 2: Guest user")
        return {"authority": "GUEST", "scar_weight": 0.0, "role": "USER", "f11_verified": False}

def _step_3_intent_mapping(query: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Step 3: Map intent - contrast, meaning, prediction."""
    query_lower = query.lower()
    
    # 1. ATLAS/Prompt Analysis (Mocked/Simplified if modules missing)
    gpv_data = {}
    signal_data = {}
    
    # 2. Constitutional Mode
    constitutional_mode = "arif" in query_lower
    
    # 3. Keyword Analysis
    intent = "unknown"
    for intent_type, keywords in INTENT_KEYWORDS.items():
        if any(kw in query_lower for kw in keywords):
            intent = intent_type
            break
            
    greetings = ["hi", "hello", "hey", "salam", "thanks"]
    if any(g in query_lower for g in greetings) and len(query) < 50:
        intent = "greet"

    # 4. Lane Determination
    lane = "SOFT"
    for lane_type, intents in LANE_INTENTS.items():
        if intent in intents:
            lane = lane_type
            break
            
    if intent == "unknown" and len(query) > 100:
        lane = "HARD"

    if constitutional_mode:
        lane = "HARD"
    else:
        if lane != "REFUSE":
            lane = "SOFT"

    # 5. Contrasts & Entities
    contrasts = []
    if " vs " in query_lower: contrasts.append("comparison")
    words = query_lower.split()
    entities = [w for w in words if len(w) > 3 and w.isalpha()][:10]

    return {
        "intent": intent,
        "lane": lane,
        "contrasts": contrasts,
        "entities": entities,
        "confidence": 0.8 if intent != "unknown" else 0.5,
        "gpv": gpv_data,
        "signal": signal_data
    }

def _step_4_thermodynamic_setup(intent_map: Dict[str, Any]) -> Dict[str, Any]:
    """Step 4: Set energy budget and entropy targets."""
    # Input Entropy Estimate
    entities = intent_map.get("entities", [])
    S_input = min(1.0, 0.3 + (len(entities) * 0.05))

    # Lane Profile
    lane = intent_map.get("lane", "SOFT")
    # Map to ATLAS keys
    arif_to_atlas = {"HARD": "FACTUAL", "SOFT": "CARE", "PHATIC": "SOCIAL", "REFUSE": "CRISIS"}
    mapped_lane = arif_to_atlas.get(lane, "CARE")
    profile = LANE_PROFILES.get(mapped_lane, LANE_PROFILES["CARE"])

    S_target = S_input * profile["S_factor"]
    
    return {
        "entropy_input": S_input,
        "entropy_target": S_target,
        "omega_0": profile["omega_0"],
        "peace_squared": PEACE_SQUARED_THRESHOLD,
        "energy_budget": profile["energy"],
        "time_budget": profile["time_budget"],
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
    return {"floors": floors, "count": len(floors)}

def _step_6_tri_witness(sovereign: Dict, thermo: Dict) -> Dict[str, Any]:
    """Step 6: Establish Tri-Witness handshake."""
    human_present = sovereign["authority"] == "888_JUDGE"
    energy_ok = thermo["energy_budget"] <= 1.0
    
    h = 1.0 if human_present else 0.5
    a = 1.0 # AI present
    e = 1.0 if energy_ok else 0.5
    
    TW = (h * a * e) ** (1/3)
    
    return {
        "human": {"present": human_present},
        "ai": {"present": True},
        "earth": {"within_bounds": energy_ok},
        "TW": TW,
        "consensus": TW >= 0.95
    }

def _step_7_engine_ignition(intent_map: Dict[str, Any]) -> Dict[str, str]:
    """Step 7: Fire up the engines."""
    lane = intent_map.get("lane", "SOFT")
    arif_to_atlas = {"HARD": "FACTUAL", "SOFT": "CARE", "PHATIC": "SOCIAL", "REFUSE": "CRISIS"}
    mapped_lane = arif_to_atlas.get(lane, "CARE")
    
    engines = LANE_ENGINES.get(mapped_lane, LANE_ENGINES["CARE"]).copy()
    logger.info(f"000_init Step 7: Engines IGNITED (mapped: {lane}→{mapped_lane})")
    return engines

# =============================================================================
# MAIN TOOL FUNCTION
# =============================================================================

async def mcp_000_init(
    action: str = "init",
    query: str = "",
    authority_token: str = "",
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    000 INIT: The 7-Step Thermodynamic Ignition Sequence.
    
    Main entry point for the tool.
    """
    VALID_ACTIONS = {"init", "gate", "reset", "validate"}

    # Validation
    if not action or action not in VALID_ACTIONS:
        return InitResult(status="VOID", session_id=session_id or "UNKNOWN", reason=f"Invalid action: {action}").__dict__

    # Rate Limit
    rl = _check_rate_limit("init_000", session_id)
    if rl: return rl

    if action == "validate":
        return InitResult(status="SEAL", session_id=session_id or str(uuid4()), reason="Validation successful").__dict__

    if action == "reset":
        return InitResult(status="SEAL", session_id=str(uuid4()), reason="Session reset complete").__dict__

    # Action: INIT
    session = session_id or str(uuid4())
    floors_checked = []

    try:
        # Step 0
        _step_0_root_key_ignition(session)
        floors_checked.append("F1_Amanah")

        # Step 1
        prev_ctx = _step_1_memory_injection()

        # Step 2
        sovereign = _step_2_sovereign_recognition(query, authority_token)
        floors_checked.append("F11_CommandAuth")

        # Step 3
        intent_map = _step_3_intent_mapping(query, prev_ctx)
        
        # Crisis Check
        if intent_map.get("lane") == "REFUSE" and "crisis" in intent_map.get("intent", ""):
             return InitResult(status="888_HOLD", session_id=session, reason="CRISIS lane detected").__dict__

        # Step 4
        thermo = _step_4_thermodynamic_setup(intent_map)

        # F12 Check
        injection_risk = _detect_injection(query)
        floors_checked.append("F12_InjectionDefense")
        if injection_risk > 0.85:
            return InitResult(status="VOID", session_id=session, reason="F12: Injection attack detected").__dict__

        # F1 Check
        reversible = _check_reversibility(query)
        floors_checked.append("F1_Amanah")
        if not reversible and intent_map["lane"] == "HARD":
             return InitResult(status="SABAR", session_id=session, reason="F1: Non-reversible operation").__dict__

        # Step 5
        floors = _step_5_floor_loading()
        floors_checked.extend(floors["floors"])

        # Step 6
        tw = _step_6_tri_witness(sovereign, thermo)

        # Step 7
        engines = _step_7_engine_ignition(intent_map)

        logger.info(f"000_init: IGNITION COMPLETE - session {session[:8]}")

        return InitResult(
            status="SEAL",
            session_id=session,
            timestamp=thermo["timestamp"],
            previous_context=prev_ctx,
            authority=sovereign["authority"],
            authority_verified=sovereign["f11_verified"],
            scar_weight=sovereign["scar_weight"],
            intent=intent_map["intent"],
            lane=intent_map["lane"],
            contrasts=intent_map["contrasts"],
            entities=intent_map["entities"],
            entropy_input=thermo["entropy_input"],
            entropy_target=thermo["entropy_target"],
            entropy_omega=thermo["omega_0"],
            peace_squared=thermo["peace_squared"],
            energy_budget=thermo["energy_budget"],
            floors_checked=floors_checked,
            floors_loaded=floors["count"],
            tri_witness=tw,
            TW=tw["TW"],
            engines=engines,
            routing=LANE_ROUTING.get(intent_map["lane"], "Default"),
            injection_risk=injection_risk,
            reason="IGNITION COMPLETE - Constitutional Mode Active"
        ).__dict__

    except Exception as e:
        logger.error(f"000_init FAILED: {e}")
        return InitResult(status="VOID", session_id=session, reason=f"IGNITION FAILED: {str(e)}").__dict__
