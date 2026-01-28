"""
arifOS Canonical init_000 — The 7-Step Thermodynamic Ignition Sequence (v53.2.2-SEAL)
Authority: Muhammad Arif bin Fazil
Principle: Auth Before Memory, Energy x Scar, SOFT_DENIED

Canonical location: codebase/init/000_init/init_000.py
All MCP servers (stdio, SSE, Railway) delegate here via:
    from codebase.init.000_init.init_000 import mcp_000_init, InitResult

The 7 Steps:
    0. ROOT KEY IGNITION    — Cryptographic foundation (F1)
    1. MEMORY INJECTION     — VAULT999 context, gated by scar_weight (F11)
    2. SOVEREIGN RECOGNITION — 888_JUDGE identity (F11)
    3. INTENT MAPPING       — Lane classification + ATLAS-333 (F12)
    4. THERMODYNAMIC SETUP  — Energy x scar_weight budget (F6/F7)
    5. FLOOR LOADING        — F1-F13 constraints
    6. TRI-WITNESS          — Human x AI x Earth consensus (F3)
    7. ENGINE IGNITION      — Selective AGI/ASI/APEX activation

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

# ---------------------------------------------------------------------------
# External dependencies (fail-safe imports)
# Try codebase.* (v53 native) first, fall back to arifos.* (v52 legacy)
# ---------------------------------------------------------------------------

logger = logging.getLogger("codebase.init.init_000")

# Rate limiter & metrics — optional (not available outside MCP context)
RATE_LIMITER_AVAILABLE = False
METRICS_AVAILABLE = False
SESSION_LEDGER_AVAILABLE = False
BUNDLE_STORE_AVAILABLE = False
inject_memory = None
store_stage_result = None

try:
    from codebase.mcp.rate_limiter import get_rate_limiter, RateLimitResult
    RATE_LIMITER_AVAILABLE = True
except ImportError:
    try:
        from arifos.mcp.rate_limiter import get_rate_limiter, RateLimitResult
        RATE_LIMITER_AVAILABLE = True
    except ImportError:
        logger.debug("Rate limiter not available (non-MCP context)")

try:
    from codebase.mcp.metrics import get_metrics
    METRICS_AVAILABLE = True
except ImportError:
    try:
        from arifos.mcp.metrics import get_metrics
        METRICS_AVAILABLE = True
    except ImportError:
        logger.debug("Metrics not available (non-MCP context)")

# Session persistence for 999-000 loop
try:
    from codebase.mcp.session_ledger import inject_memory, seal_memory
    SESSION_LEDGER_AVAILABLE = True
except ImportError:
    try:
        from arifos.mcp.session_ledger import inject_memory, seal_memory
        SESSION_LEDGER_AVAILABLE = True
    except ImportError:
        logger.debug("Session ledger not available (non-MCP context)")

# Session bundle store for inter-stage context passing
try:
    from codebase.mcp.constitutional_metrics import (
        store_stage_result,
        get_stage_result,
        get_session_bundle,
        clear_session_bundle,
    )
    BUNDLE_STORE_AVAILABLE = True
except ImportError:
    try:
        from arifos.mcp.constitutional_metrics import (
            store_stage_result,
            get_stage_result,
            get_session_bundle,
            clear_session_bundle,
        )
        BUNDLE_STORE_AVAILABLE = True
    except ImportError:
        logger.debug("Bundle store not available (non-MCP context)")

# Track B Authority: Import constitutional thresholds
try:
    from codebase.enforcement.metrics import (
        TRUTH_THRESHOLD,           # 0.99 - F2 floor
        PEACE_SQUARED_THRESHOLD,   # 1.0  - F5 floor
        OMEGA_0_MIN,               # 0.03 - F7 humility min
        OMEGA_0_MAX,               # 0.05 - F7 humility max
    )
except ImportError:
    try:
        from arifos.core.enforcement.metrics import (
            TRUTH_THRESHOLD,
            PEACE_SQUARED_THRESHOLD,
            OMEGA_0_MIN,
            OMEGA_0_MAX,
        )
    except ImportError:
        TRUTH_THRESHOLD = 0.99
        PEACE_SQUARED_THRESHOLD = 1.0
        OMEGA_0_MIN = 0.03
        OMEGA_0_MAX = 0.05
        logger.warning("Track B thresholds not available, using hardcoded defaults")

# ATLAS-333 + @PROMPT (fail-safe)
ATLAS_AVAILABLE = False
ATLAS = None
PROMPT_AVAILABLE = False
_signal_extractor = None

try:
    from arifos.core.engines.agi.atlas import ATLAS, ATLAS_333, GPV
    ATLAS_AVAILABLE = True
except Exception:
    logger.debug("ATLAS-333 not available, falling back to keyword matching")

try:
    from arifos.core.prompt.codec import SignalExtractor, PromptSignal, IntentType, RiskLevel
    PROMPT_AVAILABLE = True
    _signal_extractor = SignalExtractor()
except Exception:
    logger.debug("@PROMPT SignalExtractor not available, falling back to keyword matching")


# =============================================================================
# DATA CLASS
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

    # Step 4: Thermodynamic Setup (wired to Track B via metrics.py)
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
# CONSTANTS
# =============================================================================

# Sovereign recognition patterns
SOVEREIGN_PATTERNS = [
    "im arif", "i'm arif", "i am arif", "arif here",
    "salam", "assalamualaikum", "waalaikumsalam",
    "888", "judge", "sovereign", "ditempa bukan diberi"
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
    "HARD": ["build", "debug", "review"],
    "SOFT": ["discuss", "explore"],
    "PHATIC": ["greet", "thanks"],
}

# v53.2.2: Restricted operations that require 888_JUDGE authentication (F11)
GUEST_RESTRICTED = [
    "show vault", "read vault", "export session", "raw entries",
    "modify floor", "override consensus", "bypass f12",
    "delete ledger", "erase canon", "reset constitution",
    "show scar", "raw scar", "dump memory",
]

# v52.5.1: Lane-specific thermodynamic profiles (F7 compliant)
LANE_PROFILES = {
    "CRISIS": {
        "S_factor": 0.5,
        "omega_0": OMEGA_0_MAX,
        "energy": 1.0,
        "time_budget": 180,
    },
    "FACTUAL": {
        "S_factor": 0.6,
        "omega_0": OMEGA_0_MIN,
        "energy": 0.9,
        "time_budget": 120,
    },
    "CARE": {
        "S_factor": 0.7,
        "omega_0": 0.04,
        "energy": 0.7,
        "time_budget": 60,
    },
    "SOCIAL": {
        "S_factor": 0.8,
        "omega_0": OMEGA_0_MIN,
        "energy": 0.5,
        "time_budget": 15,
    },
}

# v52.5.1: Lane-specific engine activation matrix
LANE_ENGINES = {
    "CRISIS": {
        "AGI_Mind": "IDLE",
        "ASI_Heart": "IDLE",
        "APEX_Soul": "READY",
    },
    "FACTUAL": {
        "AGI_Mind": "READY",
        "ASI_Heart": "READY",
        "APEX_Soul": "READY",
    },
    "CARE": {
        "AGI_Mind": "IDLE",
        "ASI_Heart": "READY",
        "APEX_Soul": "READY",
    },
    "SOCIAL": {
        "AGI_Mind": "IDLE",
        "ASI_Heart": "IDLE",
        "APEX_Soul": "READY",
    },
}

# Lane-Aware Routing Matrix (ATLAS-333)
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

    refuse_patterns = ["hack", "exploit", "malware", "attack"]
    if any(p in text_lower for p in refuse_patterns):
        return "REFUSE"

    phatic_patterns = ["hello", "hi", "how are you", "thanks"]
    if any(p in text_lower for p in phatic_patterns):
        return "PHATIC"

    hard_patterns = ["calculate", "compute", "code", "algorithm", "science", "math"]
    if any(p in text_lower for p in hard_patterns):
        return "HARD"

    return "SOFT"


# =============================================================================
# RATE LIMITING HELPER
# =============================================================================

def _check_rate_limit(tool_name: str, session_id: str = "") -> Optional[Dict]:
    """
    Check rate limit before processing a tool call.
    Returns None if allowed, or a VOID response dict if rate limited.
    Only active when running inside MCP context.
    """
    if not RATE_LIMITER_AVAILABLE:
        return None

    limiter = get_rate_limiter()
    result = limiter.check(tool_name, session_id)

    if not result.allowed:
        logger.warning(f"Rate limit exceeded: {tool_name} (session={session_id})")
        if METRICS_AVAILABLE:
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


# =============================================================================
# THE 7 STEPS
# =============================================================================

def _step_0_root_key_ignition(session_id: str) -> Dict[str, Any]:
    """
    Step 0: ROOT KEY IGNITION - Establish cryptographic foundation.

    Constitutional Enforcements:
        - F1 Amanah: Root key authority establishes reversibility
        - F8 Tri-Witness: Session keys derived from root key
        - F12 Injection Defense: Root key guards against unauthorized sessions
    """
    try:
        try:
            from codebase.memory.root_key_accessor import (
                get_root_key_info,
                derive_session_key,
                get_root_key_status,
                verify_genesis_block,
            )
        except ImportError:
            from arifos.core.memory.root_key_accessor import (
                get_root_key_info,
                derive_session_key,
                get_root_key_status,
            )
            from arifos.core.memory.root_key_accessor import verify_genesis_block
        from pathlib import Path

        result = {
            "root_key_ready": get_root_key_status(),
            "session_key": None,
            "genesis_exists": False,
            "constitutional_status": "PENDING"
        }

        if not result["root_key_ready"]:
            logger.warning("000_init Step 0: Root key not ready")
            result["constitutional_status"] = "ROOT_KEY_MISSING"
            return result

        root_info = get_root_key_info()
        if root_info:
            logger.info(f"000_init Step 0: Root key loaded (generated: {root_info['generated_at'][:10]})")

        genesis_path = Path("VAULT999/CCC_CANON/genesis.json")
        if genesis_path.exists():
            result["genesis_exists"] = True
            try:
                import json
                genesis = json.loads(genesis_path.read_text())
                is_valid = verify_genesis_block(genesis)
                if is_valid:
                    logger.info("000_init Step 0: Genesis signature VERIFIED")
                    result["constitutional_status"] = "VERIFIED"
                else:
                    logger.error("000_init Step 0: Genesis signature INVALID")
                    result["constitutional_status"] = "GENESIS_INVALID"
            except Exception as e:
                logger.warning(f"000_init Step 0: Could not verify genesis: {e}")
                result["constitutional_status"] = "GENESIS_UNVERIFIED"
        else:
            logger.warning("000_init Step 0: Genesis block not found")
            result["constitutional_status"] = "GENESIS_MISSING"

        session_key = derive_session_key(session_id)
        if session_key:
            logger.info(f"000_init Step 0: Session key derived ({len(session_key)} chars)")
            result["session_key"] = session_key
        else:
            logger.warning("000_init Step 0: Could not derive session key")
            result["constitutional_status"] = "SESSION_KEY_DERIVATION_FAILED"

        if result["root_key_ready"] and result["session_key"] and result["genesis_exists"]:
            logger.info("000_init Step 0: ROOT KEY IGNITION COMPLETE")
            result["constitutional_status"] = "SEALED"

        try:
            try:
                from codebase.mcp.functional_metrics import record_constitutional_telemetry
            except ImportError:
                from arifos.mcp.functional_metrics import record_constitutional_telemetry
            record_constitutional_telemetry(
                "000_init_root_key", {"status": result["constitutional_status"]}
            )
        except Exception:
            pass

        return result

    except Exception as e:
        logger.error(f"000_init Step 0: Root key ignition failed: {e}")
        return {
            "root_key_ready": False,
            "session_key": None,
            "genesis_exists": False,
            "constitutional_status": "ERROR",
            "error": str(e)
        }


def _step_1_memory_injection(scar_weight: float = 0.0) -> Dict[str, Any]:
    """Step 1: Read from VAULT999 - inject previous session context.

    v53.2.2: Now receives scar_weight from Step 2 (sovereign recognition).
    Auth gates memory access (F11 Command Auth):
      - scar_weight >= 1.0 (888_JUDGE): Full vault context
      - scar_weight >= 0.5 (GUEST):     Summary-level only
      - scar_weight < 0.5:              Empty context (fresh session)
    """
    if not SESSION_LEDGER_AVAILABLE or inject_memory is None:
        logger.debug("000_init Step 1: Session ledger not available, returning empty context")
        return {"is_first_session": True, "session_count": 0}

    try:
        previous_context = inject_memory()
        prev_session = previous_context.get('previous_session') or {}
        prev_id = prev_session.get('session_id', '')
        logger.info(f"000_init Step 1: Memory injected from {prev_id[:8] if prev_id else 'FIRST_SESSION'} (scar_weight={scar_weight})")

        # F11: Filter memory access by authority level
        if scar_weight >= 1.0:
            return previous_context
        elif scar_weight >= 0.5:
            return {
                "is_first_session": previous_context.get("is_first_session", True),
                "session_count": previous_context.get("chain_length", 0),
                "last_lane_type": (prev_session.get("lane", "PHATIC") if prev_session else "PHATIC"),
                "context_summary": previous_context.get("context_summary", ""),
            }
        else:
            logger.info("000_init Step 1: Minimal memory (scar_weight < 0.5)")
            return {"is_first_session": True, "session_count": 0}
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
    """
    Step 3: Map intent - contrast, meaning, prediction.

    v52.5: Wired to ATLAS-333 and @PROMPT SignalExtractor when available.
    Falls back to keyword matching if implementations unavailable.
    """
    query_lower = query.lower()

    # ATLAS-333 lane classification
    gpv_data = {}
    if ATLAS_AVAILABLE and ATLAS is not None:
        try:
            gpv: GPV = ATLAS.map(query)
            gpv_data = {
                "atlas_lane": gpv.lane,
                "truth_demand": gpv.truth_demand,
                "care_demand": gpv.care_demand,
                "risk_level": gpv.risk_level,
            }
            logger.info(f"000_init Step 3: ATLAS-333 GPV={gpv.lane} (truth={gpv.truth_demand:.2f}, care={gpv.care_demand:.2f})")
        except Exception as e:
            logger.warning(f"ATLAS-333 mapping failed: {e}, falling back to keywords")
            gpv_data = {}

    # @PROMPT SignalExtractor
    signal_data = {}
    if PROMPT_AVAILABLE and _signal_extractor is not None:
        try:
            signal: PromptSignal = _signal_extractor.extract(query)
            signal_data = {
                "prompt_intent": signal.intent.value,
                "prompt_risk": signal.risk_level.value,
                "reversible": signal.reversible,
                "stakeholders": signal.stakeholders,
                "extracted_query": signal.extracted_query,
                "hidden_assumptions": signal.hidden_assumptions,
                "signal_confidence": signal.confidence,
            }
            logger.info(f"000_init Step 3: @PROMPT intent={signal.intent.value}, risk={signal.risk_level.value}")
        except Exception as e:
            logger.warning(f"@PROMPT extraction failed: {e}, falling back to keywords")
            signal_data = {}

    # Entity extraction (simple fallback/supplement)
    words = query_lower.split()
    entities = [w for w in words if len(w) > 3 and w.isalpha()]

    # Constitutional mode detection
    constitutional_mode = "arif" in query_lower
    if constitutional_mode:
        logger.info("000_init Step 3: Constitutional authority recognized (arif identity)")

    # Find contrasts
    contrasts = []
    if " vs " in query_lower or " versus " in query_lower:
        contrasts.append("comparison")
    if " or " in query_lower:
        contrasts.append("choice")
    if "old" in query_lower and "new" in query_lower:
        contrasts.append("old_vs_new")
    if "theory" in query_lower and "practice" in query_lower:
        contrasts.append("theory_vs_practice")

    # Determine lane: Prefer ATLAS-333 GPV, fall back to keyword matching
    if gpv_data and "atlas_lane" in gpv_data:
        atlas_to_arif = {
            "SOCIAL": "PHATIC",
            "CARE": "SOFT",
            "FACTUAL": "HARD",
            "CRISIS": "REFUSE",
        }
        lane = atlas_to_arif.get(gpv_data["atlas_lane"], "SOFT")
        intent = gpv_data["atlas_lane"].lower()
        confidence = 0.95
    else:
        # Keyword-based classification
        intent = "unknown"
        for intent_type, keywords in INTENT_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                intent = intent_type
                break

        greetings = ["hi", "hello", "hey", "salam", "thanks", "thank you"]
        if any(g in query_lower for g in greetings) and len(query) < 50:
            intent = "greet"

        lane = "SOFT"
        for lane_type, intents in LANE_INTENTS.items():
            if intent in intents:
                lane = lane_type
                break

        if intent == "unknown" and len(query) > 100:
            lane = "HARD"

        # v53.2.2: SOFT_DENIED for GUEST requesting restricted operations (F11)
        if constitutional_mode:
            lane = "HARD"
            logger.info("000_init Step 3: Lane overridden to HARD (constitutional authority)")
        elif any(restricted in query_lower for restricted in GUEST_RESTRICTED):
            lane = "SOFT_DENIED"
            logger.warning("000_init Step 3: SOFT_DENIED -- GUEST requesting restricted operation")
        else:
            if lane != "REFUSE":
                lane = "SOFT"
                logger.info("000_init Step 3: Lane set to SOFT (guest mode)")

        confidence = 0.8 if intent != "unknown" else 0.5

    # Override: high/critical risk -> REFUSE
    if signal_data and signal_data.get("prompt_risk") in ["high", "critical"]:
        if lane != "REFUSE":
            logger.warning(f"@PROMPT detected {signal_data['prompt_risk']} risk, escalating to REFUSE")
            lane = "REFUSE"

    logger.info(f"000_init Step 3: Intent={intent}, Lane={lane} (ATLAS={ATLAS_AVAILABLE}, PROMPT={PROMPT_AVAILABLE})")

    return {
        "intent": intent,
        "lane": lane,
        "contrasts": contrasts,
        "entities": entities[:10],
        "confidence": confidence,
        "gpv": gpv_data if gpv_data else None,
        "signal": signal_data if signal_data else None,
        "atlas_available": ATLAS_AVAILABLE,
        "prompt_available": PROMPT_AVAILABLE,
    }


def _step_4_thermodynamic_setup(intent_map: Dict[str, Any], sovereign: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Step 4: Set energy budget and entropy targets.

    v52.5.1: Uses ATLAS-333 GPV lane for profile selection.
    v53.2.2: Energy budget scales with scar_weight (F6/F11).
    """
    entity_count = len(intent_map.get("entities", []))
    contrast_count = len(intent_map.get("contrasts", []))
    S_input = min(1.0, 0.3 + (entity_count * 0.05) + (contrast_count * 0.1))

    gpv = intent_map.get("gpv") or {}
    atlas_lane = gpv.get("atlas_lane")

    if atlas_lane and atlas_lane in LANE_PROFILES:
        profile = LANE_PROFILES[atlas_lane]
    else:
        arif_to_atlas = {
            "HARD": "FACTUAL",
            "SOFT": "CARE",
            "SOFT_DENIED": "SOCIAL",
            "PHATIC": "SOCIAL",
            "REFUSE": "CRISIS",
        }
        arif_lane = intent_map.get("lane", "SOFT")
        mapped_lane = arif_to_atlas.get(arif_lane, "CARE")
        profile = LANE_PROFILES[mapped_lane]

    S_target = S_input * profile["S_factor"]
    omega_0 = profile["omega_0"]
    time_budget = profile["time_budget"]

    # v53.2.2: Scale energy by scar_weight (F6 + F11)
    scar_weight = (sovereign or {}).get("scar_weight", 0.0)
    energy_floor = min(0.2, profile["energy"] * 0.4) # Lowered floor
    energy_budget = max(energy_floor, profile["energy"] * max(scar_weight, 0.1)) # Lowered min multiplier

    peace_squared = PEACE_SQUARED_THRESHOLD

    logger.info(f"000_init Step 4: S_input={S_input:.2f}, S_target={S_target:.2f}, omega_0={omega_0:.3f}, energy={energy_budget} (lane={atlas_lane or intent_map.get('lane')})")
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
    human = {
        "present": sovereign["authority"] == "888_JUDGE",
        "scar_weight": sovereign["scar_weight"],
        "veto_power": True
    }

    ai = {
        "present": True,
        "floors_active": 13,
        "constraints_on": True
    }

    earth = {
        "present": True,
        "energy_available": thermo["energy_budget"],
        "within_bounds": thermo["energy_budget"] <= 1.0
    }

    # TW = geometric mean
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


def _step_7_engine_ignition(intent_map: Dict[str, Any] = None) -> Dict[str, str]:
    """
    Step 7: Selective engine activation based on ATLAS lane.

    - CRISIS:  APEX only (888_HOLD escalation)
    - FACTUAL: All three engines (full pipeline)
    - CARE:    ASI + APEX (heart-first)
    - SOCIAL:  APEX only (quick phatic response)
    """
    if intent_map:
        gpv = intent_map.get("gpv") or {}
        atlas_lane = gpv.get("atlas_lane")

        if atlas_lane and atlas_lane in LANE_ENGINES:
            engines = LANE_ENGINES[atlas_lane].copy()
            logger.info(f"000_init Step 7: Engines IGNITED (selective: {atlas_lane})")
            return engines

        arif_to_atlas = {
            "HARD": "FACTUAL",
            "SOFT": "CARE",
            "SOFT_DENIED": "SOCIAL",
            "PHATIC": "SOCIAL",
            "REFUSE": "CRISIS",
        }
        arif_lane = intent_map.get("lane", "SOFT")
        mapped_lane = arif_to_atlas.get(arif_lane, "CARE")
        engines = LANE_ENGINES[mapped_lane].copy()
        logger.info(f"000_init Step 7: Engines IGNITED (mapped: {arif_lane}->{mapped_lane})")
        return engines

    # Default: All engines ready
    engines = {
        "AGI_Mind": "READY",
        "ASI_Heart": "READY",
        "APEX_Soul": "READY"
    }
    logger.info("000_init Step 7: Engines IGNITED (all)")
    return engines


# =============================================================================
# MAIN ENTRY POINT
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

    "Im Arif, [topic]" triggers full system ignition.

    The 7 Steps:
        0. ROOT KEY IGNITION    - Cryptographic foundation
        1. MEMORY INJECTION     - VAULT999 context (gated by scar_weight)
        2. SOVEREIGN RECOGNITION - 888_JUDGE identity
        3. INTENT MAPPING       - Lane classification + ATLAS-333
        4. THERMODYNAMIC SETUP  - Energy x scar_weight budget
        5. FLOOR LOADING        - F1-F13 constraints
        6. TRI-WITNESS          - Human x AI x Earth
        7. ENGINE IGNITION      - Selective AGI/ASI/APEX activation

    Floors Enforced: F1, F11, F12
    """
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
    # ACTION: VALIDATE (Lightweight Check)
    # =========================================================================
    if action == "validate":
        rate_limit_response = _check_rate_limit("init_000", session_id)
        if rate_limit_response:
            return rate_limit_response

        return InitResult(
            status="SEAL",
            session_id=session_id or str(uuid4()),
            reason="Validation successful: System online",
            floors_checked=["F12_InputValidation"]
        ).__dict__

    # =========================================================================
    # ACTION: RESET (Clean State)
    # =========================================================================
    if action == "reset":
        rate_limit_response = _check_rate_limit("init_000", session_id)
        if rate_limit_response:
            return rate_limit_response

        return InitResult(
            status="SEAL",
            session_id=str(uuid4()),
            reason="Session reset complete",
            floors_checked=["F1_Amanah"]
        ).__dict__

    # =========================================================================
    # ACTION: INIT (Full Ignition)
    # =========================================================================
    rate_limit_response = _check_rate_limit("init_000", session_id)
    if rate_limit_response:
        return rate_limit_response

    session = session_id or str(uuid4())
    floors_checked = []

    try:
        # STEP 0: ROOT KEY IGNITION
        root_key_status = _step_0_root_key_ignition(session)
        floors_checked.append("F1_Amanah")

        # STEP 2: SOVEREIGN RECOGNITION (before memory — F11 gates access)
        sovereign = _step_2_sovereign_recognition(query, authority_token)
        floors_checked.append("F11_CommandAuth")

        # STEP 1: MEMORY INJECTION (filtered by scar_weight from Step 2)
        previous_context = _step_1_memory_injection(scar_weight=sovereign["scar_weight"])

        # STEP 3: INTENT MAPPING
        intent_map = _step_3_intent_mapping(query, previous_context)

        # 888_HOLD for CRISIS lane
        gpv = intent_map.get("gpv") or {}
        atlas_lane = gpv.get("atlas_lane")
        if atlas_lane == "CRISIS":
            logger.warning("000_init: CRISIS lane detected - triggering 888_HOLD")
            floors_checked.extend(["F6_Empathy", "F11_CommandAuth"])
            return InitResult(
                status="888_HOLD",
                session_id=session,
                timestamp=datetime.now().isoformat(),
                authority="AWAITING_CONFIRMATION",
                authority_verified=False,
                intent=intent_map.get("intent", "crisis"),
                lane="REFUSE",
                floors_checked=floors_checked,
                engines={"AGI_Mind": "HOLD", "ASI_Heart": "HOLD", "APEX_Soul": "READY"},
                injection_risk=0.0,
                reason="CRISIS lane detected. Human confirmation required before proceeding.",
            ).__dict__ | {
                "gpv": gpv,
                "signal": intent_map.get("signal"),
                "risk_level": gpv.get("risk_level", 1.0),
                "action_required": "Sovereign must confirm to proceed. Provide authority_token='888_CONFIRMED' to continue.",
            }

        # SOFT_DENIED — GUEST requesting restricted operation (F11)
        if intent_map.get("lane") == "SOFT_DENIED":
            logger.warning("000_init: SOFT_DENIED -- GUEST requesting restricted operation")
            floors_checked.append("F11_CommandAuth")
            return InitResult(
                status="PARTIAL",
                session_id=session,
                timestamp=datetime.now().isoformat(),
                authority=sovereign["authority"],
                authority_verified=sovereign["f11_verified"],
                scar_weight=sovereign["scar_weight"],
                intent=intent_map.get("intent", "unknown"),
                lane="SOFT_DENIED",
                floors_checked=floors_checked,
                engines={"AGI_Mind": "IDLE", "ASI_Heart": "IDLE", "APEX_Soul": "READY"},
                injection_risk=0.0,
                reason="F11: This operation requires 888_JUDGE authentication. Sign in with: 'Salam, I'm Arif'",
            ).__dict__

        # STEP 4: THERMODYNAMIC SETUP (energy scales with scar_weight)
        thermo = _step_4_thermodynamic_setup(intent_map, sovereign=sovereign)

        # F12 INJECTION DEFENSE
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

        # F1 AMANAH (Reversibility)
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

        # STEP 5: FLOOR LOADING
        floors = _step_5_floor_loading()
        floors_checked.extend(floors["floors"])

        # STEP 6: TRI-WITNESS HANDSHAKE
        tri_witness = _step_6_tri_witness(sovereign, thermo)

        # STEP 7: ENGINE IGNITION (Lane-selective)
        engines = _step_7_engine_ignition(intent_map)

        # IGNITION COMPLETE
        logger.info(f"000_init: IGNITION COMPLETE - session {session[:8]}")

        result = InitResult(
            status="SEAL",
            session_id=session,
            timestamp=thermo["timestamp"],
            previous_context=previous_context,
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
            tri_witness=tri_witness,
            TW=tri_witness["TW"],
            engines=engines,
            routing=LANE_ROUTING.get(intent_map["lane"], "AGI -> ASI -> APEX (Default)"),
            injection_risk=injection_risk,
            reason="IGNITION COMPLETE - Constitutional Mode Active"
        ).__dict__
        if BUNDLE_STORE_AVAILABLE and store_stage_result is not None:
            store_stage_result(session, "init", result)
        return result

    except Exception as e:
        logger.error(f"000_init IGNITION FAILED: {e}")
        result = InitResult(
            status="VOID",
            session_id=session,
            injection_risk=1.0,
            reason=f"IGNITION FAILED: {str(e)}",
            floors_checked=floors_checked
        ).__dict__
        if BUNDLE_STORE_AVAILABLE and store_stage_result is not None:
            store_stage_result(session, "init", result)
        return result
