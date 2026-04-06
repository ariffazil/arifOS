# arifOS Functional Tool Surface v2.5 — ToM-Aligned (SAME SIGNATURES)
from __future__ import annotations
import hashlib
import logging
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
    arifos.init — Session Anchoring with ToM.
    
    ToM FIELDS (via payload):
    - declared_intent: What the LLM believes user wants
    - confidence_self_estimate: LLM's confidence (0.0-1.0)
    - context_assumptions: Assumptions about context (min 1)
    - alternative_intents: Other intents considered
    - uncertainty_acknowledgment: What LLM is uncertain about
    
    RETURNS:
    - Philosophy: Always "DITEMPA, BUKAN DIBERI." (INIT override)
    """
    # Validate ToM fields present
    tom_required = ["declared_intent", "confidence_self_estimate", "context_assumptions"]
    missing = [f for f in tom_required if f not in payload]
    
    if missing:
        # Create error envelope with ToM violation
        from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
        return RuntimeEnvelope(
            tool="init_anchor",
            stage="000_INIT",
            status=RuntimeStatus.ERROR,
            verdict=Verdict.VOID,
            session_id=session_id,
            payload={
                "ok": False,
                "tom_violation": True,
                "error": f"Missing required ToM fields: {missing}",
                "philosophy": {
                    "registry_version": "1.2.0",
                    "selection_mode": "error",
                    "quote": {"text": "DITEMPA, BUKAN DIBERI.", "author": "arifOS"}
                }
            }
        )
    
    # Call existing tool
    result = await _mega_init_anchor(
        mode=mode,
        payload=payload,
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
    )
    
    # Calculate G★ from ToM fields in payload
    g_star = calculate_g_star_from_payload(payload)
    result.g_score = g_star
    
    # Inject philosophy (will use INIT override)
    philosophy = inject_philosophy(result, g_star)
    
    # Add to payload
    if isinstance(result.payload, dict):
        result.payload["philosophy"] = philosophy
        result.payload["tom_validated"] = True
        result.payload["constitutional_alignment"] = get_alignment_label(g_star)
    
    return result


async def sense_v2(
    mode: str,
    payload: dict[str, Any],
    session_id: Optional[str] = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
) -> RuntimeEnvelope:
    """
    arifos.sense — Reality Grounding with ToM.
    
    ToM FIELDS (via payload):
    - claim: The claim being evaluated
    - evidence_type: empirical|logical|speculative
    - source_confidence: Confidence in source (0.0-1.0)
    - time_sensitivity: low|medium|high
    - bias_assessment: Assessment of biases
    - epistemic_state: LLM's knowledge state
    - alternative_evidence: Other evidence considered
    """
    tom_required = ["claim", "evidence_type", "source_confidence", "bias_assessment"]
    missing = [f for f in tom_required if f not in payload]
    
    if missing:
        from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
        return RuntimeEnvelope(
            tool="physics_reality",
            stage="111_SENSE",
            status=RuntimeStatus.ERROR,
            verdict=Verdict.VOID,
            session_id=session_id,
            payload={
                "ok": False,
                "tom_violation": True,
                "error": f"Missing required ToM fields: {missing}",
            }
        )
    
    result = await _mega_physics_reality(
        mode=mode,
        payload=payload,
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
    )
    
    g_star = calculate_g_star_from_payload(payload)
    result.g_score = g_star
    
    philosophy = inject_philosophy(result, g_star)
    
    if isinstance(result.payload, dict):
        result.payload["philosophy"] = philosophy
        result.payload["tom_validated"] = True
        result.payload["constitutional_alignment"] = get_alignment_label(g_star)
    
    return result


async def mind_v2(
    mode: str,
    payload: dict[str, Any],
    session_id: Optional[str] = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
) -> RuntimeEnvelope:
    """
    arifos.mind — Structured Reasoning with ToM.
    
    ToM FIELDS (via payload):
    - problem_statement: What is being reasoned about
    - assumptions: Underlying assumptions
    - alternative_hypotheses: Other possibilities (min 2)
    - second_order_effects: Downstream consequences
    - estimated_uncertainty: LLM's uncertainty (0.0-1.0)
    - confidence_in_reasoning: Confidence in reasoning (0.0-1.0)
    """
    tom_required = ["problem_statement", "assumptions", "alternative_hypotheses"]
    missing = [f for f in tom_required if f not in payload]
    
    if missing:
        from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
        return RuntimeEnvelope(
            tool="agi_mind",
            stage="333_MIND",
            status=RuntimeStatus.ERROR,
            verdict=Verdict.VOID,
            session_id=session_id,
            payload={
                "ok": False,
                "tom_violation": True,
                "error": f"Missing required ToM fields: {missing}",
            }
        )
    
    # Validate minimum 2 alternatives
    if len(payload.get("alternative_hypotheses", [])) < 2:
        from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
        return RuntimeEnvelope(
            tool="agi_mind",
            stage="333_MIND",
            status=RuntimeStatus.ERROR,
            verdict=Verdict.VOID,
            session_id=session_id,
            payload={
                "ok": False,
                "tom_violation": True,
                "error": "ToM violation: at least 2 alternative_hypotheses required",
            }
        )
    
    result = await _mega_agi_mind(
        mode=mode,
        payload=payload,
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
    )
    
    g_star = calculate_g_star_from_payload(payload)
    result.g_score = g_star
    
    philosophy = inject_philosophy(result, g_star)
    
    if isinstance(result.payload, dict):
        result.payload["philosophy"] = philosophy
        result.payload["tom_validated"] = True
        result.payload["constitutional_alignment"] = get_alignment_label(g_star)
    
    return result


async def heart_v2(
    mode: str,
    payload: dict[str, Any],
    session_id: Optional[str] = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
) -> RuntimeEnvelope:
    """
    arifos.heart — Safety and Human Modeling with ToM.
    
    ToM FIELDS (via payload):
    - target_audience: Who might be affected
    - potential_harm_vectors: Types of harm
    - emotional_state_estimate: calm|distressed|hostile|unknown
    - vulnerability_risk: Risk to vulnerable (0.0-1.0)
    - consent_assessment: Assessment of consent
    - human_model_confidence: Confidence in modeling (0.0-1.0)
    """
    tom_required = ["target_audience", "potential_harm_vectors", "vulnerability_risk", "consent_assessment"]
    missing = [f for f in tom_required if f not in payload]
    
    if missing:
        from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
        return RuntimeEnvelope(
            tool="asi_heart",
            stage="666_HEART",
            status=RuntimeStatus.ERROR,
            verdict=Verdict.VOID,
            session_id=session_id,
            payload={
                "ok": False,
                "tom_violation": True,
                "error": f"Missing required ToM fields: {missing}",
            }
        )
    
    result = await _mega_asi_heart(
        mode=mode,
        payload=payload,
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
    )
    
    g_star = calculate_g_star_from_payload(payload)
    result.g_score = g_star
    
    philosophy = inject_philosophy(result, g_star)
    
    if isinstance(result.payload, dict):
        result.payload["philosophy"] = philosophy
        result.payload["tom_validated"] = True
        result.payload["constitutional_alignment"] = get_alignment_label(g_star)
    
    return result


async def ops_v2(
    mode: str,
    payload: dict[str, Any],
    session_id: Optional[str] = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
) -> RuntimeEnvelope:
    """
    arifos.ops — Operational Cost and Capacity with ToM.
    
    ToM FIELDS (via payload):
    - complexity_estimate: Estimated complexity (0.0-1.0)
    - resource_intensity: low|medium|high
    - time_horizon: short|mid|long
    - irreversibility: Whether action can be undone
    - feasibility_confidence: Confidence in feasibility (0.0-1.0)
    - rollback_plan: Steps to undo (required if irreversibility=True)
    """
    tom_required = ["complexity_estimate", "resource_intensity", "irreversibility", "feasibility_confidence"]
    missing = [f for f in tom_required if f not in payload]
    
    if missing:
        from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
        return RuntimeEnvelope(
            tool="math_estimator",
            stage="444_OPS",
            status=RuntimeStatus.ERROR,
            verdict=Verdict.HOLD,
            session_id=session_id,
            payload={
                "ok": False,
                "tom_violation": True,
                "error": f"Missing required ToM fields: {missing}",
            }
        )
    
    # Validate rollback plan for irreversible actions
    if payload.get("irreversibility") and not payload.get("rollback_plan"):
        from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
        return RuntimeEnvelope(
            tool="math_estimator",
            stage="444_OPS",
            status=RuntimeStatus.ERROR,
            verdict=Verdict.HOLD,
            session_id=session_id,
            payload={
                "ok": False,
                "tom_violation": True,
                "error": "ToM violation: irreversible action requires rollback_plan",
            }
        )
    
    result = await _mega_math_estimator(
        mode=mode,
        payload=payload,
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
    )
    
    g_star = calculate_g_star_from_payload(payload)
    result.g_score = g_star
    
    philosophy = inject_philosophy(result, g_star)
    
    if isinstance(result.payload, dict):
        result.payload["philosophy"] = philosophy
        result.payload["tom_validated"] = True
        result.payload["constitutional_alignment"] = get_alignment_label(g_star)
    
    return result


async def route_v2(
    mode: str,
    payload: dict[str, Any],
    session_id: Optional[str] = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
) -> RuntimeEnvelope:
    """
    arifos.route — Lane Selection with ToM.
    
    ToM FIELDS (via payload):
    - intent_model: informational|advisory|execution|speculative
    - risk_assessment: low|medium|high|critical
    - ambiguity_level: How ambiguous (0.0-1.0)
    - user_expertise_estimate: Estimate of user expertise
    - routing_confidence: Confidence in routing (0.0-1.0)
    - inferred_user_goals: What user actually wants
    """
    tom_required = ["intent_model", "risk_assessment", "ambiguity_level", "inferred_user_goals"]
    missing = [f for f in tom_required if f not in payload]
    
    if missing:
        from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
        return RuntimeEnvelope(
            tool="arifOS_kernel",
            stage="444_ROUTER",
            status=RuntimeStatus.ERROR,
            verdict=Verdict.HOLD,
            session_id=session_id,
            payload={
                "ok": False,
                "tom_violation": True,
                "error": f"Missing required ToM fields: {missing}",
            }
        )
    
    result = await _mega_arifOS_kernel(
        mode=mode,
        payload=payload,
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
    )
    
    g_star = calculate_g_star_from_payload(payload)
    result.g_score = g_star
    
    philosophy = inject_philosophy(result, g_star)
    
    if isinstance(result.payload, dict):
        result.payload["philosophy"] = philosophy
        result.payload["tom_validated"] = True
        result.payload["constitutional_alignment"] = get_alignment_label(g_star)
    
    return result


async def judge_v2(
    mode: str,
    payload: dict[str, Any],
    session_id: Optional[str] = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
) -> RuntimeEnvelope:
    """
    arifos.judge — Verdict with ToM.
    
    ToM FIELDS (via payload):
    - logical_consistency: Whether reasoning was consistent
    - entropy_delta: Net change in uncertainty
    - harm_probability: Assessed harm probability (0.0-1.0)
    - confidence_level: Final confidence (0.0-1.0)
    - self_critique: LLM's critique of own reasoning
    - uncertainty_quantified: Quantified uncertainty (0.0-1.0)
    """
    tom_required = ["logical_consistency", "confidence_level", "self_critique"]
    missing = [f for f in tom_required if f not in payload]
    
    if missing:
        from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
        return RuntimeEnvelope(
            tool="apex_judge",
            stage="888_JUDGE",
            status=RuntimeStatus.ERROR,
            verdict=Verdict.VOID,
            session_id=session_id,
            payload={
                "ok": False,
                "tom_violation": True,
                "error": f"Missing required ToM fields: {missing}",
            }
        )
    
    result = await _mega_apex_judge(
        mode=mode,
        payload=payload,
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
    )
    
    # Ensure payload is dict
    if not isinstance(result.payload, dict):
        result.payload = {}
    
    result.payload.setdefault("verdict", getattr(result, "verdict", "PARTIAL"))
    result.payload.setdefault("floors_triggered", [])
    result.payload.setdefault("confidence", payload.get("confidence_level", 0.5))
    result.payload.setdefault("reasoning_class", "constitutional")
    
    g_star = calculate_g_star_from_payload(payload)
    result.g_score = g_star
    
    philosophy = inject_philosophy(result, g_star)
    
    result.payload["philosophy"] = philosophy
    result.payload["tom_validated"] = True
    result.payload["constitutional_alignment"] = get_alignment_label(g_star)
    
    return result


async def memory_v2(
    mode: str,
    payload: dict[str, Any],
    session_id: Optional[str] = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
) -> RuntimeEnvelope:
    """
    arifos.memory — Recall Context with ToM.
    
    ToM FIELDS (via payload):
    - query_vector: The memory query
    - relevance_threshold: Minimum relevance (0.0-1.0)
    - recall_confidence: Confidence in recall (0.0-1.0)
    - context_assumptions: Assumptions about context
    """
    tom_required = ["query_vector", "relevance_threshold", "recall_confidence"]
    missing = [f for f in tom_required if f not in payload]
    
    if missing:
        from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
        return RuntimeEnvelope(
            tool="engineering_memory",
            stage="777_MEMORY",
            status=RuntimeStatus.ERROR,
            verdict=Verdict.HOLD,
            session_id=session_id,
            payload={
                "ok": False,
                "tom_violation": True,
                "error": f"Missing required ToM fields: {missing}",
            }
        )
    
    result = await _mega_engineering_memory(
        mode=mode,
        payload=payload,
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
    )
    
    g_star = calculate_g_star_from_payload(payload)
    result.g_score = g_star
    
    philosophy = inject_philosophy(result, g_star)
    
    if isinstance(result.payload, dict):
        result.payload["philosophy"] = philosophy
        result.payload["tom_validated"] = True
        result.payload["constitutional_alignment"] = get_alignment_label(g_star)
    
    return result


async def vault_v2(
    mode: str,
    payload: dict[str, Any],
    session_id: Optional[str] = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
) -> RuntimeEnvelope:
    """
    arifos.vault — Immutable Seal with ToM.
    
    ToM FIELDS (via payload):
    - verdict: The verdict to seal
    - hash_of_input: SHA256 hash of input state
    - telemetry_snapshot: Complete telemetry
    - sealing_confidence: Confidence in seal (0.0-1.0)
    - irreversibility_acknowledged: Whether irreversibility is acknowledged
    
    If verdict == SEAL → philosophy override to "DITEMPA, BUKAN DIBERI."
    """
    tom_required = ["verdict", "hash_of_input", "sealing_confidence", "irreversibility_acknowledged"]
    missing = [f for f in tom_required if f not in payload]
    
    if missing:
        from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
        return RuntimeEnvelope(
            tool="vault_ledger",
            stage="888_VAULT",
            status=RuntimeStatus.ERROR,
            verdict=Verdict.VOID,
            session_id=session_id,
            payload={
                "ok": False,
                "tom_violation": True,
                "error": f"Missing required ToM fields: {missing}",
            }
        )
    
    result = await _mega_vault_ledger(
        mode=mode,
        payload=payload,
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
    )
    
    # Map verdict string to Verdict enum for philosophy injection
    verdict_str = payload.get("verdict", "PARTIAL")
    try:
        from arifosmcp.runtime.models import Verdict as _Verdict
        result.verdict = _Verdict(verdict_str)
    except:
        result.verdict = result.verdict if hasattr(result, 'verdict') else None
    
    g_star = calculate_g_star_from_payload(payload)
    result.g_score = g_star
    
    philosophy = inject_philosophy(result, g_star)
    
    if isinstance(result.payload, dict):
        result.payload["philosophy"] = philosophy
        result.payload["tom_validated"] = True
        result.payload["constitutional_alignment"] = get_alignment_label(g_star)
    
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════

CANONICAL_TOOL_HANDLERS = {
    "arifos.init": init_v2,
    "arifos.sense": sense_v2,
    "arifos.mind": mind_v2,
    "arifos.route": route_v2,
    "arifos.heart": heart_v2,
    "arifos.ops": ops_v2,
    "arifos.judge": judge_v2,
    "arifos.memory": memory_v2,
    "arifos.vault": vault_v2,
}


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


def get_constitutional_health(session_id: str = "global"):
    return {"status": "healthy"}


def list_recent_verdicts(limit: int = 5):
    return []


# Internal tools required by tools_internal.py
def cost_estimator(action_description: str) -> dict[str, Any]:
    """Estimate cost of an action (mock implementation)."""
    return {
        "action": action_description,
        "estimated_cost": "low",
        "units": "compute",
        "confidence": 0.8,
    }


def system_health() -> dict[str, Any]:
    """Return system health status."""
    return {
        "status": "healthy",
        "cpu_percent": 15.0,
        "memory_percent": 45.0,
        "disk_percent": 60.0,
    }


def fs_inspect(path: str = ".") -> dict[str, Any]:
    """Inspect filesystem at path."""
    import os
    try:
        entries = os.listdir(path)[:20]  # Limit to 20 entries
        return {"path": path, "entries": entries, "exists": True}
    except Exception as e:
        return {"path": path, "error": str(e), "exists": False}


def process_list(limit: int = 50) -> dict[str, Any]:
    """List system processes."""
    return {"processes": [], "limit": limit, "note": "process listing not available in container"}


def net_status() -> dict[str, Any]:
    """Return network status."""
    return {"connected": True, "interfaces": ["eth0"], "note": "network status mock"}


def log_tail(lines: int = 100) -> dict[str, Any]:
    """Return recent log lines."""
    return {"lines": [], "count": 0, "note": "log tail mock"}
