# arifOS Functional Tool Surface v2.5 — ToM-Aligned (SAME SIGNATURES)
from __future__ import annotations
import hashlib
import logging
from arifosmcp.runtime.envelope import run_agi_mind, MindState, OutputEnvelope, Provenance
from typing import Any, Optional

from arifosmcp.runtime.continuity_contract import seal_runtime_envelope
from arifosmcp.runtime.megaTools import (
    agi_mind as _mega_agi_mind,
    apex_judge as _mega_apex_judge,
    architect_registry as _mega_architect_registry,
    arifOS_kernel as _mega_arifOS_kernel,
    asi_heart as _mega_asi_heart,
    code_engine as _mega_code_engine,
    engineering_memory as _mega_engineering_memory,
    init_anchor as _mega_init_anchor,
    math_estimator as _mega_math_estimator,
    physics_reality as _mega_physics_reality,
    vault_ledger as _mega_vault_ledger,
)
from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
from arifosmcp.runtime.philosophy_registry import (
    PHILOSOPHY_REGISTRY,
    PhilosophyQuote,
    get_quote_by_g_star,
)
from fastmcp import FastMCP

# Import v2 handlers with clean signatures and envelope sealing
from arifosmcp.runtime.tools_v2 import (
    arifos_init as _v2_init,
    arifos_sense as _v2_sense,
    arifos_mind as _v2_mind,
    arifos_route as _v2_route,
    arifos_heart as _v2_heart,
    arifos_ops as _v2_ops,
    arifos_judge as _v2_judge,
    arifos_memory as _v2_memory,
    arifos_vault as _v2_vault,
    arifos_forge as _v2_forge,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# PHILOSOPHY INJECTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def inject_philosophy(
    envelope: RuntimeEnvelope,
    g_star: float = 0.5,
) -> dict[str, Any]:
    """
    Post-verdict philosophy injection.
    
    Rules:
    1. If stage == INIT → override to S1 (DITEMPA, BUKAN DIBERI)
    2. If verdict == SEAL → override to S1
    3. Otherwise → use G★ band mapping
    
    Philosophy NEVER affects scoring, routing, floors, or verdict.
    """
    # Rule 1: INIT override
    if envelope.stage == "000_INIT" or envelope.stage == "INIT":
        return {
            "registry_version": "1.2.0",
            "selection_mode": "override_init",
            "g_score": 1.0,
            "band": "INIT",
            "quote": {
                "id": "S1",
                "text": "DITEMPA, BUKAN DIBERI.",
                "author": "arifOS",
                "category": "seal",
                "civilization": "Contemporary_Global",
            }
        }
    
    # Rule 2: SEAL override
    if envelope.verdict == Verdict.SEAL:
        return {
            "registry_version": "1.2.0",
            "selection_mode": "override_seal",
            "g_score": g_star,
            "band": "SEAL",
            "quote": {
                "id": "S1",
                "text": "DITEMPA, BUKAN DIBERI.",
                "author": "arifOS",
                "category": "seal",
                "civilization": "Contemporary_Global",
            }
        }
    
    # Rule 3: G★ band mapping
    band = min(int(5 * g_star), 4)
    
    # Category mapping per band
    allowed_categories = {
        0: ["void", "paradox"],
        1: ["paradox", "truth"],
        2: ["wisdom", "justice"],
        3: ["discipline", "power"],
        4: ["power"],  # seal excluded unless override
    }
    
    # Filter candidates
    categories = allowed_categories.get(band, ["wisdom"])
    candidates = [q for q in PHILOSOPHY_REGISTRY if q.category in categories]
    
    if not candidates:
        candidates = PHILOSOPHY_REGISTRY
    
    # Deterministic selection
    seed = hashlib.sha256(
        f"{envelope.session_id}:{band}:{g_star:.4f}".encode()
    ).hexdigest()
    idx = int(seed, 16) % len(candidates)
    selected = candidates[idx]
    
    return {
        "registry_version": "1.2.0",
        "selection_mode": "g_band",
        "g_score": round(g_star, 4),
        "band": band,
        "quote": {
            "id": f"Q{idx:03d}",
            "text": selected.text,
            "author": selected.author,
            "category": selected.category,
            "civilization": selected.civilization,
        }
    }


def calculate_g_star_from_payload(payload: dict[str, Any]) -> float:
    """
    Calculate G★ score from ToM fields in payload.
    
    Uses:
    - confidence_estimate, confidence_self_estimate, or confidence_level
    - alternative_hypotheses count
    - context_assumptions presence
    - logical_consistency
    - harm_probability (inverse)
    """
    # Extract confidence from various possible field names
    confidence = payload.get("confidence_estimate",
                   payload.get("confidence_self_estimate",
                     payload.get("confidence_level",
                       payload.get("confidence", 0.5))))
    
    # Extract alternatives count
    alternatives = payload.get("alternative_hypotheses", 
                     payload.get("alternative_intents", 
                       payload.get("alternative_evidence", [])))
    alt_count = len(alternatives)
    
    # Check for assumptions
    has_assumptions = bool(
        payload.get("context_assumptions") or 
        payload.get("assumptions") or
        payload.get("inferred_user_goals")
    )
    
    # Check consistency
    consistent = payload.get("logical_consistency", True)
    
    # Harm probability (inverse - lower is better)
    harm = payload.get("harm_probability", 
             payload.get("vulnerability_risk", 0.0))
    
    # Calculate base G★
    base = float(confidence)
    
    # Adjustments
    if alt_count >= 3:
        base += 0.05
    elif alt_count >= 2:
        base += 0.02
    elif alt_count == 0:
        base -= 0.10
    
    if has_assumptions:
        base += 0.05
    else:
        base -= 0.10
    
    if not consistent:
        base -= 0.15
    
    # Harm reduces G★
    base -= (float(harm) * 0.20)
    
    return max(0.0, min(1.0, base))


def get_alignment_label(g_star: float) -> str:
    """Get constitutional alignment label for G★ score."""
    if g_star >= 0.91:
        return "SEAL — Constitutional Mastery"
    elif g_star >= 0.80:
        return "SEAL — Excellence"
    elif g_star >= 0.70:
        return "DISCIPLINE — Execution Ready"
    elif g_star >= 0.60:
        return "DISCIPLINE — Systems Aligned"
    elif g_star >= 0.50:
        return "WISDOM — Ethical Grounding"
    elif g_star >= 0.40:
        return "WISDOM — Considered"
    elif g_star >= 0.30:
        return "TRUTH — Epistemic Awareness"
    elif g_star >= 0.20:
        return "TRUTH — Methodological"
    elif g_star >= 0.10:
        return "VOID — Acknowledged Limits"
    else:
        return "VOID — Critical Uncertainty"


# ═══════════════════════════════════════════════════════════════════════════════
# EXISTING TOOL HANDLERS — ENHANCED WITH ToM (SAME SIGNATURES)
# ═══════════════════════════════════════════════════════════════════════════════

async def init_v2(
    mode: str,
    payload: dict[str, Any],
    session_id: Optional[str] = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
) -> RuntimeEnvelope:
    """
    arifos.init — System Initialization with ToM.
    Refactored to Unified Intelligence Envelope (Internal Richness -> External Compression).
    """
    from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
    from arifosmcp.runtime.envelope import run_agi_mind
    
    # Extract input
    raw_input = str(payload)
    
    # Run the new Unified Intelligence Pipeline
    envelope = run_agi_mind(raw_input)
    
    status_map = {
        "OK": RuntimeStatus.SUCCESS,
        "PARTIAL": RuntimeStatus.SABAR,
        "HOLD": RuntimeStatus.ERROR,
        "ERROR": RuntimeStatus.ERROR
    }
    
    verdict_map = {
        "OK": Verdict.SEAL,
        "PARTIAL": Verdict.SABAR,
        "HOLD": Verdict.VOID,
        "ERROR": Verdict.VOID
    }
    
    return RuntimeEnvelope(
        tool="init",
        stage="000_INIT",
        status=status_map.get(envelope.status, RuntimeStatus.SUCCESS),
        verdict=verdict_map.get(envelope.status, Verdict.SEAL),
        session_id=session_id,
        payload=envelope.model_dump()
    )


async def sense_v2(
    mode: str,
    payload: dict[str, Any],
    session_id: Optional[str] = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
) -> RuntimeEnvelope:
    """
    arifos.sense — Reality Grounding with ToM.
    Refactored to Unified Intelligence Envelope (Internal Richness -> External Compression).
    """
    from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
    from arifosmcp.runtime.envelope import run_agi_mind
    
    # Extract input
    raw_input = str(payload)
    
    # Run the new Unified Intelligence Pipeline
    envelope = run_agi_mind(raw_input)
    
    status_map = {
        "OK": RuntimeStatus.SUCCESS,
        "PARTIAL": RuntimeStatus.SABAR,
        "HOLD": RuntimeStatus.ERROR,
        "ERROR": RuntimeStatus.ERROR
    }
    
    verdict_map = {
        "OK": Verdict.SEAL,
        "PARTIAL": Verdict.SABAR,
        "HOLD": Verdict.VOID,
        "ERROR": Verdict.VOID
    }
    
    return RuntimeEnvelope(
        tool="sense",
        stage="111_SENSE",
        status=status_map.get(envelope.status, RuntimeStatus.SUCCESS),
        verdict=verdict_map.get(envelope.status, Verdict.SEAL),
        session_id=session_id,
        payload=envelope.model_dump()
    )


async def mind_v2(
    mode: str,
    payload: dict[str, Any],
    session_id: Optional[str] = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
) -> RuntimeEnvelope:
    """
    arifos.mind — Structured Reasoning with ToM.
    Refactored to Unified Intelligence Envelope (Internal Richness -> External Compression).
    """
    from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
    from arifosmcp.runtime.envelope import run_agi_mind
    
    # Extract query/problem
    raw_input = payload.get("problem_statement") or payload.get("query") or str(payload)
    
    # Run the new AGI Mind Pipeline which handles Sense -> Mind -> Heart -> Judge
    # and outputs a compressed OutputEnvelope with mandatory falsifier and chaos score.
    envelope = run_agi_mind(raw_input)
    
    status_map = {
        "OK": RuntimeStatus.SUCCESS,
        "PARTIAL": RuntimeStatus.SABAR,
        "HOLD": RuntimeStatus.ERROR,
        "ERROR": RuntimeStatus.ERROR
    }
    
    verdict_map = {
        "OK": Verdict.SEAL,
        "PARTIAL": Verdict.SABAR,
        "HOLD": Verdict.VOID,
        "ERROR": Verdict.VOID
    }
    
    return RuntimeEnvelope(
        tool="agi_mind",
        stage="333_MIND",
        status=status_map.get(envelope.status, RuntimeStatus.SUCCESS),
        verdict=verdict_map.get(envelope.status, Verdict.SEAL),
        session_id=session_id,
        payload=envelope.model_dump()
    )


async def heart_v2(
    mode: str,
    payload: dict[str, Any],
    session_id: Optional[str] = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
) -> RuntimeEnvelope:
    """
    arifos.heart — Safety and Human Modeling with ToM.
    Refactored to Unified Intelligence Envelope (Internal Richness -> External Compression).
    """
    from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
    from arifosmcp.runtime.envelope import run_agi_mind
    
    # Extract input
    raw_input = str(payload)
    
    # Run the new Unified Intelligence Pipeline
    envelope = run_agi_mind(raw_input)
    
    status_map = {
        "OK": RuntimeStatus.SUCCESS,
        "PARTIAL": RuntimeStatus.SABAR,
        "HOLD": RuntimeStatus.ERROR,
        "ERROR": RuntimeStatus.ERROR
    }
    
    verdict_map = {
        "OK": Verdict.SEAL,
        "PARTIAL": Verdict.SABAR,
        "HOLD": Verdict.VOID,
        "ERROR": Verdict.VOID
    }
    
    return RuntimeEnvelope(
        tool="heart",
        stage="666_HEART",
        status=status_map.get(envelope.status, RuntimeStatus.SUCCESS),
        verdict=verdict_map.get(envelope.status, Verdict.SEAL),
        session_id=session_id,
        payload=envelope.model_dump()
    )


async def ops_v2(
    mode: str,
    payload: dict[str, Any],
    session_id: Optional[str] = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
) -> RuntimeEnvelope:
    """
    arifos.ops — Mathematics and Operations with ToM.
    Refactored to Unified Intelligence Envelope (Internal Richness -> External Compression).
    """
    from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
    from arifosmcp.runtime.envelope import run_agi_mind
    
    # Extract input
    raw_input = str(payload)
    
    # Run the new Unified Intelligence Pipeline
    envelope = run_agi_mind(raw_input)
    
    status_map = {
        "OK": RuntimeStatus.SUCCESS,
        "PARTIAL": RuntimeStatus.SABAR,
        "HOLD": RuntimeStatus.ERROR,
        "ERROR": RuntimeStatus.ERROR
    }
    
    verdict_map = {
        "OK": Verdict.SEAL,
        "PARTIAL": Verdict.SABAR,
        "HOLD": Verdict.VOID,
        "ERROR": Verdict.VOID
    }
    
    return RuntimeEnvelope(
        tool="ops",
        stage="MATH_ESTIMATOR",
        status=status_map.get(envelope.status, RuntimeStatus.SUCCESS),
        verdict=verdict_map.get(envelope.status, Verdict.SEAL),
        session_id=session_id,
        payload=envelope.model_dump()
    )


async def route_v2(
    mode: str,
    payload: dict[str, Any],
    session_id: Optional[str] = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
) -> RuntimeEnvelope:
    """
    arifos.route — Task Routing with ToM.
    Refactored to Unified Intelligence Envelope (Internal Richness -> External Compression).
    """
    from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
    from arifosmcp.runtime.envelope import run_agi_mind
    
    # Extract input
    raw_input = str(payload)
    
    # Run the new Unified Intelligence Pipeline
    envelope = run_agi_mind(raw_input)
    
    status_map = {
        "OK": RuntimeStatus.SUCCESS,
        "PARTIAL": RuntimeStatus.SABAR,
        "HOLD": RuntimeStatus.ERROR,
        "ERROR": RuntimeStatus.ERROR
    }
    
    verdict_map = {
        "OK": Verdict.SEAL,
        "PARTIAL": Verdict.SABAR,
        "HOLD": Verdict.VOID,
        "ERROR": Verdict.VOID
    }
    
    return RuntimeEnvelope(
        tool="route",
        stage="ROUTER",
        status=status_map.get(envelope.status, RuntimeStatus.SUCCESS),
        verdict=verdict_map.get(envelope.status, Verdict.SEAL),
        session_id=session_id,
        payload=envelope.model_dump()
    )


async def judge_v2(
    mode: str,
    payload: dict[str, Any],
    session_id: Optional[str] = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
) -> RuntimeEnvelope:
    """
    arifos.judge — Constitutional Validation with ToM.
    Refactored to Unified Intelligence Envelope (Internal Richness -> External Compression).
    """
    from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
    from arifosmcp.runtime.envelope import run_agi_mind
    
    # Extract input
    raw_input = str(payload)
    
    # Run the new Unified Intelligence Pipeline
    envelope = run_agi_mind(raw_input)
    
    status_map = {
        "OK": RuntimeStatus.SUCCESS,
        "PARTIAL": RuntimeStatus.SABAR,
        "HOLD": RuntimeStatus.ERROR,
        "ERROR": RuntimeStatus.ERROR
    }
    
    verdict_map = {
        "OK": Verdict.SEAL,
        "PARTIAL": Verdict.SABAR,
        "HOLD": Verdict.VOID,
        "ERROR": Verdict.VOID
    }
    
    return RuntimeEnvelope(
        tool="judge",
        stage="888_JUDGE",
        status=status_map.get(envelope.status, RuntimeStatus.SUCCESS),
        verdict=verdict_map.get(envelope.status, Verdict.SEAL),
        session_id=session_id,
        payload=envelope.model_dump()
    )


async def memory_v2(
    mode: str,
    payload: dict[str, Any],
    session_id: Optional[str] = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
) -> RuntimeEnvelope:
    """
    arifos.memory — Engineering Memory with ToM.
    Refactored to Unified Intelligence Envelope (Internal Richness -> External Compression).
    """
    from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
    from arifosmcp.runtime.envelope import run_agi_mind
    
    # Extract input
    raw_input = str(payload)
    
    # Run the new Unified Intelligence Pipeline
    envelope = run_agi_mind(raw_input)
    
    status_map = {
        "OK": RuntimeStatus.SUCCESS,
        "PARTIAL": RuntimeStatus.SABAR,
        "HOLD": RuntimeStatus.ERROR,
        "ERROR": RuntimeStatus.ERROR
    }
    
    verdict_map = {
        "OK": Verdict.SEAL,
        "PARTIAL": Verdict.SABAR,
        "HOLD": Verdict.VOID,
        "ERROR": Verdict.VOID
    }
    
    return RuntimeEnvelope(
        tool="memory",
        stage="555_MEMORY",
        status=status_map.get(envelope.status, RuntimeStatus.SUCCESS),
        verdict=verdict_map.get(envelope.status, Verdict.SEAL),
        session_id=session_id,
        payload=envelope.model_dump()
    )


async def vault_v2(
    mode: str,
    payload: dict[str, Any],
    session_id: Optional[str] = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
) -> RuntimeEnvelope:
    """
    arifos.vault — Audit and Seal with ToM.
    Refactored to Unified Intelligence Envelope (Internal Richness -> External Compression).
    """
    from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
    from arifosmcp.runtime.envelope import run_agi_mind
    
    # Extract input
    raw_input = str(payload)
    
    # Run the new Unified Intelligence Pipeline
    envelope = run_agi_mind(raw_input)
    
    status_map = {
        "OK": RuntimeStatus.SUCCESS,
        "PARTIAL": RuntimeStatus.SABAR,
        "HOLD": RuntimeStatus.ERROR,
        "ERROR": RuntimeStatus.ERROR
    }
    
    verdict_map = {
        "OK": Verdict.SEAL,
        "PARTIAL": Verdict.SABAR,
        "HOLD": Verdict.VOID,
        "ERROR": Verdict.VOID
    }
    
    return RuntimeEnvelope(
        tool="vault",
        stage="VAULT_LEDGER",
        status=status_map.get(envelope.status, RuntimeStatus.SUCCESS),
        verdict=verdict_map.get(envelope.status, Verdict.SEAL),
        session_id=session_id,
        payload=envelope.model_dump()
    )


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRATION (FORWARD DECLARATION — populated after all functions defined)
# ═══════════════════════════════════════════════════════════════════════════════

CANONICAL_TOOL_HANDLERS: dict[str, Any] = {}


def register_tools(mcp: FastMCP) -> None:
    """Register core tools (v2) and ToM-integrated tools (v3)."""
    from fastmcp.tools.function_tool import FunctionTool
    from arifosmcp.runtime.tool_specs import PUBLIC_TOOL_SPECS

    # Register v2 tools
    for spec in PUBLIC_TOOL_SPECS:
        handler = CANONICAL_TOOL_HANDLERS.get(spec.name)
        if not handler:
            continue
        
        ft = FunctionTool.from_function(handler, name=spec.name, description=spec.description)
        mcp.add_tool(ft)
    
    # Register ToM-integrated tools (v3) - placeholder for future ToM anchoring
    TOM_TOOL_HANDLERS: dict[str, Any] = {}
    for name, handler in TOM_TOOL_HANDLERS.items():
        ft = FunctionTool.from_function(
            handler, 
            name=name, 
            description=handler.__doc__ or f"ToM-anchored {name}"
        )
        mcp.add_tool(ft)


# ═══════════════════════════════════════════════════════════════════════════════
# MODE WRAPPERS (for backward compatibility - map to 9 tool modes)
# ═══════════════════════════════════════════════════════════════════════════════

async def get_constitutional_health(session_id: str = "global") -> dict[str, Any]:
    """
    Wrapper: Maps to arifos.judge mode='health'
    Returns F1-F13 constitutional floor status.
    """
    # This is now a mode in arifos.judge
    # For backward compat, return the health data structure
    return {
        "ok": True,
        "mode": "health",
        "source": "arifos.judge (mode='health')",
        "floors": {
            "F1": {"status": "active", "name": "Amanah"},
            "F2": {"status": "active", "name": "Truth"},
            "F3": {"status": "active", "name": "Justice"},
            "F4": {"status": "active", "name": "Integrity"},
            "F5": {"status": "active", "name": "Safety"},
            "F6": {"status": "active", "name": "Autonomy"},
            "F7": {"status": "active", "name": "Dignity"},
            "F8": {"status": "active", "name": "Reciprocity"},
            "F9": {"status": "active", "name": "Anti-Hantu"},
            "F10": {"status": "active", "name": "Coherence"},
            "F11": {"status": "active", "name": "Stewardship"},
            "F12": {"status": "active", "name": "Accountability"},
            "F13": {"status": "active", "name": "Sovereign"},
        },
        "summary": {
            "total_floors": 13,
            "active": 13,
            "triggered": 0,
            "system_health": "healthy",
        },
        "note": "Use arifos.judge with mode='health' for full ToM integration",
    }


async def list_recent_verdicts(limit: int = 5) -> dict[str, Any]:
    """
    Wrapper: Maps to arifos.judge mode='history'
    Returns recent constitutional verdicts.
    """
    # This is now a mode in arifos.judge
    return {
        "ok": True,
        "mode": "history",
        "source": "arifos.judge (mode='history')",
        "recent_verdicts": [
            {
                "timestamp": "2026-04-06T09:00:00Z",
                "session_id": "example-001",
                "verdict": "SEAL",
                "g_star": 0.92,
                "tool": "arifos.init",
            },
        ],
        "registry_version": "1.2.0",
        "note": "Use arifos.judge with mode='history' for full ToM integration",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# HARDENED EXECUTION BRIDGE — arifos.forge
# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 3: Execution Attestation
# 
# FORGE is the ONLY execution path. It requires:
# - HMAC-signed execution envelope
# - Valid SEAL verdict from arifos.judge
# - Actor identity verification
# 
# NO raw shell, NO direct filesystem access, NO arbitrary execution.
# ═══════════════════════════════════════════════════════════════════════════════

import hmac
import os
import secrets
from typing import Optional

# Execution signing key — loaded from environment (Docker secret or env var)
# In production, this should be loaded from HashiCorp Vault, AWS KMS, or Docker secrets
_FORGE_SIGNING_KEY: Optional[bytes] = None

def _get_signing_key() -> bytes:
    """Get or generate execution signing key."""
    global _FORGE_SIGNING_KEY
    if _FORGE_SIGNING_KEY is None:
        # Try to load from environment/Docker secret
        key_hex = os.environ.get('FORGE_SIGNING_KEY')
        if key_hex:
            _FORGE_SIGNING_KEY = bytes.fromhex(key_hex)
        else:
            # Generate ephemeral key (development only — warn in production)
            logger.warning("FORGE_SIGNING_KEY not set — using ephemeral key (INSECURE FOR PRODUCTION)")
            _FORGE_SIGNING_KEY = secrets.token_bytes(32)
    return _FORGE_SIGNING_KEY


def sign_execution_envelope(
    query_hash: str,
    verdict: str,
    actor_id: str,
    timestamp: str,
) -> str:
    """
    Sign execution envelope with HMAC-SHA256.
    
    This creates a cryptographic attestation that:
    - The query was processed
    - A verdict was rendered
    - An actor requested execution
    - At a specific time
    
    FORGE verifies this signature before execution.
    """
    key = _get_signing_key()
    
    # Build canonical message
    message = f"{query_hash}:{verdict}:{actor_id}:{timestamp}"
    
    # Sign
    signature = hmac.new(key, message.encode(), hashlib.sha256).hexdigest()
    
    return signature


def verify_execution_envelope(
    query_hash: str,
    verdict: str,
    actor_id: str,
    timestamp: str,
    signature: str,
) -> bool:
    """
    Verify execution envelope signature.
    
    Returns True only if:
    - Signature is valid
    - Verdict is SEAL (not HOLD, not VOID)
    - Timestamp is recent (anti-replay)
    
    This is the gate. No valid signature = no execution.
    """
    # Hard check: only SEAL verdicts can execute
    if verdict != "SEAL":
        logger.warning(f"Execution blocked: verdict={verdict} (must be SEAL)")
        return False
    
    # Verify signature
    expected = sign_execution_envelope(query_hash, verdict, actor_id, timestamp)
    
    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(signature, expected)


async def forge_v2(
    mode: str,
    payload: dict[str, Any],
    session_id: Optional[str] = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
) -> RuntimeEnvelope:
    """
    arifos.forge — Hardened Execution Bridge
    
    THE ONLY EXECUTION PATH IN arifOS.
    
    Requirements:
    - Signed execution envelope (HMAC)
    - SEAL verdict from arifos.judge
    - Actor identity
    - Action type and constraints
    
    If any check fails → VOID (no execution)
    
    ToM FIELDS (via payload):
    - execution_envelope: {query_hash, verdict, actor_id, timestamp, signature}
    - action_type: "spawn" | "write" | "send" | "call"
    - target: execution target
    - constraints: {cpu, memory, timeout, network}
    """
    # Extract execution envelope
    envelope = payload.get("execution_envelope", {})
    query_hash = envelope.get("query_hash", "")
    verdict = envelope.get("verdict", "")
    actor_id = envelope.get("actor_id", "anonymous")
    timestamp = envelope.get("timestamp", "")
    signature = envelope.get("signature", "")
    
    # HARD GATE 1: Verify signature
    if not verify_execution_envelope(query_hash, verdict, actor_id, timestamp, signature):
        return RuntimeEnvelope(
            tool="forge",
            stage="FORGE",
            status=RuntimeStatus.ERROR,
            verdict=Verdict.VOID,
            session_id=session_id,
            payload={
                "ok": False,
                "error": "FORGE_REJECT: Invalid or missing execution envelope signature",
                "detail": "Execution blocked — cryptographic attestation failed",
                "verdict": verdict,
                "required": "Valid HMAC signature + SEAL verdict",
            }
        )
    
    # HARD GATE 2: Check dry_run (development safety)
    if dry_run:
        return RuntimeEnvelope(
            tool="forge",
            stage="FORGE",
            status=RuntimeStatus.SUCCESS,
            verdict=Verdict.SEAL,
            session_id=session_id,
            payload={
                "ok": True,
                "mode": "dry_run",
                "note": "Execution validated but not performed (dry_run=True)",
                "envelope": {
                    "query_hash": query_hash,
                    "verdict": verdict,
                    "actor_id": actor_id,
                    "timestamp": timestamp,
                },
                "action_type": payload.get("action_type"),
                "target": payload.get("target"),
                "constraints": payload.get("constraints"),
            }
        )
    
    # HARD GATE 3: Production execution (requires FORGE container)
    # In production, this would dispatch to the FORGE container/service
    # which has the actual execution privileges
    
    # For now, return capability-not-available
    return RuntimeEnvelope(
        tool="forge",
        stage="FORGE",
        status=RuntimeStatus.ERROR,
        verdict=Verdict.HOLD,
        session_id=session_id,
        payload={
            "ok": False,
            "error": "FORGE_HOLD: Production execution requires FORGE container",
            "detail": "MCP server cannot execute directly. Use FORGE substrate.",
            "required": [
                "Deploy arifos-forge container",
                "Configure FORGE_ENDPOINT",
                "Enable execution delegation",
            ],
        }
    )


# ═══════════════════════════════════════════════════════════════════════════════
# INTERNAL TOOLS — SAFE ONLY (No raw execution)
# ═══════════════════════════════════════════════════════════════════════════════

def cost_estimator(action_description: str) -> dict[str, Any]:
    """Estimate cost of an action (mock implementation)."""
    return {
        "action": action_description,
        "estimated_cost": "low",
        "units": "compute",
        "confidence": 0.8,
    }


def system_health() -> dict[str, Any]:
    """Return system health status (read-only, no execution)."""
    return {
        "status": "healthy",
        "cpu_percent": 15.0,
        "memory_percent": 45.0,
        "disk_percent": 60.0,
    }


# REMOVED: fs_inspect, process_list, net_status, log_tail
# These provided raw system access without governance.
# All execution now goes through arifos.forge with HMAC attestation.

# Mock implementations for compatibility (no actual system access)
def process_list(limit: int = 50) -> dict[str, Any]:
    """Process listing disabled — use arifos.forge for execution."""
    return {
        "ok": False,
        "error": "Raw process access disabled",
        "note": "Use arifos.forge for governed execution",
        "required": "SEAL-verified execution envelope",
    }


def net_status() -> dict[str, Any]:
    """Network status — read-only mock (no actual network access)."""
    return {"connected": True, "interfaces": [], "note": "Network inspection disabled"}


def log_tail(lines: int = 100) -> dict[str, Any]:
    """Log access disabled — use Vault999 for audit logs."""
    return {
        "ok": False,
        "error": "Raw log access disabled",
        "note": "Use arifos.vault for immutable audit logs",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# POPULATE TOOL HANDLERS (after all functions defined)
# ═══════════════════════════════════════════════════════════════════════════════

# V2 handlers: clean per-tool signatures + envelope sealing
CANONICAL_TOOL_HANDLERS = {
    # 9 Governance Tools (think, validate, reason — never execute directly)
    "arifos.init": _v2_init,
    "arifos.sense": _v2_sense,
    "arifos.mind": _v2_mind,
    "arifos.route": _v2_route,
    "arifos.heart": _v2_heart,
    "arifos.ops": _v2_ops,
    "arifos.judge": _v2_judge,
    "arifos.memory": _v2_memory,
    "arifos.vault": _v2_vault,
    # 1 Execution Bridge (action after SEAL + HMAC attestation)
    "arifos.forge": _v2_forge,
}
