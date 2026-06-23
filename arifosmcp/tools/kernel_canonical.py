"""
arifosmcp/tools/kernel_canonical.py — 444_KERNEL_CANONICAL
═══════════════════════════════════════════════════════════

RULE 14 MODE-FIRST NAMING canonical tools.
Replaces the 16-mode bloat in arif_kernel_route with 5 clean named tools.

Each tool has ONE responsibility. Modes are internal expansion, not naming.

Canonical tools (stable names):
  arif_route        — route intent to organ (new canonical routing entry point)
  arif_triage       — session status, priority, preflight
  arif_kernel_status — telemetry, discovery, prediction health
  arif_bridge_connect — direct organ tool call (canonical noun_verb name, forged 2026-06-21)
  arif_bridge       — [DEPRECATED] legacy noun-only name, retained for backward compat

Soft-deprecated (still work, emit warning):
  arif_kernel_route — absorbs all old modes via passthrough

Ratified: 2026-06-20
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import logging
from pathlib import Path
from typing import Any

from arifosmcp.core.federation_contracts import validate_organ_output
from arifosmcp.runtime.law import check_laws
from arifosmcp.runtime.tools import _hold, _ok

logger = logging.getLogger(__name__)

try:
    from arifosmcp.core.tool_self_model import SURPRISE_WINDOW_SIZE
except ImportError:
    SURPRISE_WINDOW_SIZE = 10

_BRIDGE_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# ─── Intent map cache ────────────────────────────────────────────────────────
_intent_map_cache: dict[str, Any] | None = None


def _load_intent_map() -> dict[str, Any]:
    """Load organ intent map once, cache forever."""
    global _intent_map_cache
    if _intent_map_cache is not None:
        return _intent_map_cache
    try:
        import yaml

        map_path = Path(__file__).parent.parent / "config" / "organ_intent_map.yaml"
        if map_path.exists():
            with open(map_path) as f:
                _intent_map_cache = yaml.safe_load(f)
                return _intent_map_cache
    except Exception:
        pass
    # Fallback: hardcoded map
    _intent_map_cache = {
        "organ_routes": {
            "geox": {
                "organ": "GEOX",
                "port": 8081,
                "intent_keywords": [
                    "seismic",
                    "well log",
                    "las",
                    "petrophysics",
                    "horizon",
                    "fault",
                    "amplitude",
                    "basin",
                    "prospect",
                    "subsurface",
                    "velocity",
                    "lithology",
                    "porosity",
                    "permeability",
                    "resistivity",
                    "gamma ray",
                    "sonic",
                    "density",
                    "structural",
                    "trap",
                ],
            },
            "wealth": {
                "organ": "WEALTH",
                "port": 18082,
                "intent_keywords": [
                    "portfolio",
                    "npv",
                    "irr",
                    "emv",
                    "option",
                    "derivative",
                    "capital",
                    "hedge",
                    "risk metric",
                    "allocation",
                    "stress test",
                ],
            },
            "well": {
                "organ": "WELL",
                "port": 18083,
                "intent_keywords": [
                    "vitality",
                    "biometric",
                    "sleep",
                    "heart rate",
                    "hrv",
                    "metabolic",
                    "readiness",
                    "recovery",
                    "autonomic",
                ],
            },
        }
    }
    return _intent_map_cache


def _route_intent_to_organ(intent: str, explicit_organ: str | None = None) -> str:
    """Resolve organ by keyword matching against intent map."""
    if explicit_organ:
        return explicit_organ.lower()
    if not intent:
        return "arifos"
    intent_lower = intent.lower()
    intent_map = _load_intent_map()
    organ_routes = intent_map.get("organ_routes", {})
    # Longest keyword match wins
    best_match = None
    best_len = 0
    for organ_key, organ_config in organ_routes.items():
        for kw in organ_config.get("intent_keywords", []):
            if kw.lower() in intent_lower and len(kw) > best_len:
                best_len = len(kw)
                best_match = organ_config.get("organ", organ_key.upper())
    return best_match or "arifos"


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL TOOL 1: arif_route
# ═══════════════════════════════════════════════════════════════════════════════


def arif_route(
    intent: str,
    organ: str | None = None,
    task: str | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
    organ_tool: str | None = None,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Canonical routing entry point. Routes an intent to the correct organ.

    RULE 14: Mode-first. This is ONE tool for all routing decisions.
    The mode parameter does not exist here — routing is the only operation.

    Args:
        intent:        Natural-language description of what the user wants.
                      e.g. "interpret this seismic section", "assess portfolio risk"
        organ:        Optional explicit organ override. If provided, intent matching
                      is skipped and this organ is used directly.
        task:         Alias for intent (backward compat).
        actor_id:     Calling actor.
        session_id:   Governing session.
        organ_tool:   The tool name on the target organ to call.
                      If absent, returns routing decision only (no bridge call).
        arguments:    Arguments to pass to organ_tool.

    Returns:
        routing_decision:  organ, port, tool_prefix
        bridge_result:    (if organ_tool provided) result from organ tool call

    Example:
        arif_route(intent="seismic interpretation")
        → {"organ": "GEOX", "port": 8081, "tool_prefix": "geox_", "status": "routed"}

        arif_route(intent="portfolio stress test", organ_tool="wealth_portfolio",
                   arguments={"mode": "stress"})
        → routes to WEALTH, calls wealth_portfolio(mode="stress"), returns result
    """
    floor_check = check_laws("arif_route", {"intent": intent}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_route", floor_check["reason"], floor_check["violated_laws"])

    target_organ = _route_intent_to_organ(intent, organ)
    intent_map = _load_intent_map()
    organ_config = intent_map.get("organ_routes", {}).get(target_organ.lower(), {})
    port = organ_config.get("port", 0)
    tool_prefix = organ_config.get("tool_prefix", "")

    routing = {
        "intent": intent,
        "organ": target_organ.upper(),
        "port": port,
        "tool_prefix": tool_prefix,
        "organ_tool": organ_tool,
        "status": "routed",
        "routing_rule": "intent_map",
    }

    # If no organ_tool specified, return routing decision only
    if not organ_tool:
        return _ok("arif_route", routing)

    # Bridge call to organ
    if target_organ.lower() == "geox":
        result = _bridge_geox(organ_tool, arguments or {}, session_id, actor_id)
        routing["bridge_result"] = result
        routing["bridge_status"] = "called"
        return _ok("arif_route", routing)

    if target_organ.lower() == "wealth":
        result = _bridge_wealth(organ_tool, arguments or {}, session_id, actor_id)
        routing["bridge_result"] = result
        routing["bridge_status"] = "called"
        return _ok("arif_route", routing)

    if target_organ.lower() == "well":
        result = _bridge_well(organ_tool, arguments or {}, session_id, actor_id)
        routing["bridge_result"] = result
        routing["bridge_status"] = "called"
        return _ok("arif_route", routing)

    if target_organ.lower() == "a-forge":
        return _ok("arif_route", {**routing, "bridge_status": "a-forge: use A-FORGE MCP directly"})

    if target_organ.lower() == "arifos":
        return _ok("arif_route", {**routing, "bridge_status": "kernel-local: no bridge needed"})

    return _hold("arif_route", f"Unknown organ: {target_organ}")


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL TOOL 2: arif_triage
# ═══════════════════════════════════════════════════════════════════════════════


def arif_triage(
    mode: str = "status",
    session_id: str | None = None,
    stage: str | None = None,
    actor_id: str | None = None,
    priority: str | None = None,
) -> dict[str, Any]:
    """
    Session status, priority queue, and preflight checks.

    RULE 14: One tool, defined modes.
    Modes:
        status     — active session count and current stage
        preflight  — pre-session safety probe (no session required)
        triage     — priority assessment for a task

    Args:
        mode:        "status" | "preflight" | "triage"
        session_id:   Optional session to query
        stage:       Stage hint (used if session_id not provided)
        actor_id:    Calling actor
        priority:    Task priority hint for triage mode

    Returns:
        Structured triage data appropriate to mode.
    """
    floor_check = check_laws("arif_triage", {"mode": mode}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_triage", floor_check["reason"], floor_check["violated_laws"])

    from arifosmcp.runtime.tools import _SESSIONS

    if mode == "status":
        prediction_health = _get_prediction_health()
        live_stage = "unknown"
        if session_id:
            sess = _SESSIONS.get(session_id, {})
            live_stage = sess.get("stage", stage or "unknown")
        elif stage:
            live_stage = stage
        return _ok(
            "arif_triage",
            {
                "active_sessions": len(_SESSIONS),
                "stage": live_stage,
                "stage_source": "session" if session_id else ("parameter" if stage else "unknown"),
                "prediction_health": prediction_health,
                "mode": "status",
            },
        )

    if mode == "preflight":
        from arifosmcp.constitutional_map import CANONICAL_TOOLS

        return _ok(
            "arif_triage",
            {
                "kernel": "alive",
                "observe_only": True,
                "mutation_allowed": False,
                "external_side_effects_allowed": False,
                "irreversible_allowed": False,
                "session_required": True,
                "session_id_present": bool(session_id),
                "actor_id_present": bool(actor_id),
                "actor_verified": False,
                "authority_mode": "OBSERVE_ONLY",
                "stage": stage or "000",
                "canonical_tool_count": len(CANONICAL_TOOLS),
                "active_sessions": len(_SESSIONS),
                "next_safe_action": "Call arif_init(mode='ping' | 'light' | 'full')",
                "mode": "preflight",
            },
        )

    if mode == "triage":
        # Simple priority classification
        priority_map = {
            "critical": 1,
            "high": 2,
            "normal": 3,
            "low": 4,
        }
        q_priority = priority_map.get(priority.lower() if priority else "normal", 3)
        return _ok(
            "arif_triage",
            {
                "priority": priority or "normal",
                "priority_score": q_priority,
                "queue_depth": 0,
                "recommended_lane": "AGI" if q_priority <= 2 else "AGI",
                "mode": "triage",
            },
        )

    return _hold("arif_triage", f"Unknown mode: {mode}")


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL TOOL 3: arif_bridge_connect (low-level organ call)
# ═══════════════════════════════════════════════════════════════════════════════
# arif_bridge_connect (CANONICAL, forged 2026-06-21): follows arif_<noun>_<verb> convention.


def arif_bridge_connect(
    organ: str,
    tool_name: str,
    arguments: dict[str, Any] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Low-level direct organ tool call.
    Bypasses intent map — caller must know which organ and tool to call.

    RULE 14: This is a direct bridge, not routing by intent.
    Use arif_route for intent-based routing. Use arif_bridge only when
    the organ and tool are known ahead of time.

    This is the internal bridge implementation also used by arif_route.

    Args:
        organ:       "geox" | "wealth" | "well" | "geox" (case-insensitive)
        tool_name:   MCP tool name on the target organ
        arguments:   Tool arguments dict
        actor_id:    Calling actor (injected into envelope)
        session_id:  Governing session

    Returns:
        Kernel-wrapped organ output with envelope.
    """
    floor_check = check_laws("arif_bridge", {"organ": organ, "tool": tool_name}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_bridge", floor_check["reason"], floor_check["violated_laws"])

    organ_lower = organ.lower()
    if organ_lower == "geox":
        return _bridge_geox(tool_name, arguments or {}, session_id, actor_id)
    if organ_lower == "wealth":
        return _bridge_wealth(tool_name, arguments or {}, session_id, actor_id)
    if organ_lower == "well":
        return _bridge_well(tool_name, arguments or {}, session_id, actor_id)
    return _hold("arif_bridge", f"Unknown organ: {organ}")


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL TOOL 5: arif_kernel_attest (organ attestation)
# ═══════════════════════════════════════════════════════════════════════════════


def arif_kernel_attest(
    organ: str | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Live organ attestation. One tool, organ is a parameter.

    RULE 14: One tool, organ is a parameter, not a name.
    If organ is None, attest all organs.

    Args:
        organ:      Specific organ to attest, or None for all
        actor_id:   Calling actor
        session_id: Governing session

    Returns:
        Per-organ attestation records with liveness.
    """
    floor_check = check_laws("arif_kernel_attest", {"organ": organ or "all"}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_kernel_attest", floor_check["reason"], floor_check["violated_laws"])

    import asyncio

    from arifosmcp.runtime.heartbeat_registry import federation_liveness
    from arifosmcp.runtime.organ_attestation import attest_all_organs, attest_organ

    if organ and organ.upper() in ("GEOX", "WEALTH", "WELL", "arifOS"):
        result = asyncio.run(attest_organ(organ.upper(), actor_id=actor_id, session_id=session_id))
        return _ok("arif_kernel_attest", {"mode": "single", "organ": organ.upper(), **result})

    result = asyncio.run(attest_all_organs(actor_id=actor_id, session_id=session_id))
    liveness = federation_liveness()
    return _ok(
        "arif_kernel_attest",
        {
            "mode": "all",
            "attestation": result,
            "liveness": liveness,
        },
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL TOOL 6: arif_kernel_health (federation health)
# ═══════════════════════════════════════════════════════════════════════════════


def arif_kernel_health(
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Federation liveness heartbeat snapshot.
    One tool, no modes needed — health is singular.

    Args:
        actor_id: Calling actor

    Returns:
        Federation-wide liveness data.
    """
    floor_check = check_laws("arif_kernel_health", {}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_kernel_health", floor_check["reason"], floor_check["violated_laws"])

    from arifosmcp.runtime.heartbeat_registry import federation_liveness

    liveness = federation_liveness()
    return _ok("arif_kernel_health", {"liveness": liveness})


# ═══════════════════════════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


def _run_async(coro) -> Any:
    """Run async coroutine from sync context."""
    try:
        asyncio.get_running_loop()
        future = _BRIDGE_EXECUTOR.submit(asyncio.run, coro)
        return future.result(timeout=60)
    except RuntimeError:
        return asyncio.run(coro)


def _assert_organ_attested(organ: str) -> dict[str, Any] | None:
    """Fail-closed gate: require recent ALIVE attestation before bridging."""
    from arifosmcp.runtime.heartbeat_registry import is_organ_stale
    from arifosmcp.runtime.organ_attestation import get_organ_attestation

    rec = get_organ_attestation(organ.upper())
    if rec is None:
        return _hold("arif_bridge", f"Organ {organ} has no live attestation.")
    if rec.status in ("REVOKED", "DEGRADED_CLAIM", "DEGRADED", "UNATTESTED"):
        return _hold("arif_bridge", f"Organ {organ} status={rec.status}")
    if is_organ_stale(organ.upper()):
        return _hold("arif_bridge", f"Organ {organ} heartbeat stale. Re-attest.")
    return None


def _bridge_geox(
    tool_name: str, arguments: dict, session_id: str | None, actor_id: str | None
) -> dict[str, Any]:
    """Bridge a call to GEOX organ."""
    hold = _assert_organ_attested("geox")
    if hold:
        return hold
    try:
        from arifosmcp.federation.kernel_envelope import wrap_geox_output
        from arifosmcp.runtime.epistemic_injector import (
            read_epistemic,
            verify_route_eligibility,
        )
        from arifosmcp.runtime.geox_bridge import call_geox_tool

        result = _run_async(call_geox_tool(tool_name, arguments))
        validated = validate_organ_output("geox", result)
        wrapped = wrap_geox_output(
            validated["output"],
            tool_name=tool_name,
            session_id=session_id,
            actor_id=actor_id,
            lease_id=arguments.get("lease_id"),
        )

        # ── Epistemic route gate (2026-06-21) ─────────────────────────────
        # Check if the bridged result claims executive authority but is AI-generated.
        # AI may recommend action, not self-approve action.
        _source_epi = read_epistemic(wrapped) if isinstance(wrapped, dict) else None
        if _source_epi:
            _eligible, _reason = verify_route_eligibility(_source_epi, "EXECUTIVE")
            if not _eligible:
                logger.warning(
                    "EPISTEMIC ROUTE GATE: GEOX bridge blocked for %s — %s",
                    tool_name,
                    _reason,
                )
                return _hold("arif_bridge", f"Epistemic route gate: {_reason}", ["F2_TRUTH"])

        return _ok(
            "arif_bridge",
            {
                "organ": "GEOX",
                "tool": tool_name,
                "result": wrapped,
                "status": "bridged",
                "boundary_enforced": validated["boundary_enforced"],
                "violations": validated["violations"],
                "_epistemic_checked": True,
            },
        )
    except Exception as e:
        return _hold("arif_bridge", f"GEOX bridge failed: {e}")


def _bridge_wealth(
    tool_name: str, arguments: dict, session_id: str | None, actor_id: str | None
) -> dict[str, Any]:
    """Bridge a call to WEALTH organ."""
    hold = _assert_organ_attested("wealth")
    if hold:
        return hold
    try:
        from arifosmcp.runtime.epistemic_injector import (
            read_epistemic,
            verify_route_eligibility,
        )
        from arifosmcp.runtime.wealth_bridge import call_wealth_tool

        result = _run_async(call_wealth_tool(tool_name, arguments))
        validated = validate_organ_output("wealth", result)

        # ── Epistemic route gate (2026-06-21) ─────────────────────────────
        _source_epi = (
            read_epistemic(validated["output"]) if isinstance(validated["output"], dict) else None
        )
        if _source_epi:
            _eligible, _reason = verify_route_eligibility(_source_epi, "EXECUTIVE")
            if not _eligible:
                logger.warning(
                    "EPISTEMIC ROUTE GATE: WEALTH bridge blocked for %s — %s",
                    tool_name,
                    _reason,
                )
                return _hold("arif_bridge", f"Epistemic route gate: {_reason}", ["F2_TRUTH"])

        return _ok(
            "arif_bridge",
            {
                "organ": "WEALTH",
                "tool": tool_name,
                "result": validated["output"],
                "status": "bridged",
                "boundary_enforced": validated["boundary_enforced"],
                "violations": validated["violations"],
                "_epistemic_checked": True,
            },
        )
    except Exception as e:
        return _hold("arif_bridge", f"WEALTH bridge failed: {e}")


def _bridge_well(
    tool_name: str, arguments: dict, session_id: str | None, actor_id: str | None
) -> dict[str, Any]:
    """Bridge a call to WELL organ."""
    hold = _assert_organ_attested("well")
    if hold:
        return hold
    try:
        from arifosmcp.runtime.epistemic_injector import (
            read_epistemic,
            verify_route_eligibility,
        )
        from arifosmcp.runtime.well_bridge import call_well_tool

        result = _run_async(call_well_tool(tool_name, arguments))

        # ── Epistemic route gate (2026-06-21) ─────────────────────────────
        _source_epi = read_epistemic(result) if isinstance(result, dict) else None
        if _source_epi:
            _eligible, _reason = verify_route_eligibility(_source_epi, "EXECUTIVE")
            if not _eligible:
                logger.warning(
                    "EPISTEMIC ROUTE GATE: WELL bridge blocked for %s — %s",
                    tool_name,
                    _reason,
                )
                return _hold("arif_bridge", f"Epistemic route gate: {_reason}", ["F2_TRUTH"])

        return _ok(
            "arif_bridge",
            {
                "organ": "WELL",
                "tool": tool_name,
                "result": result,
                "status": "bridged",
                "_epistemic_checked": True,
            },
        )
    except Exception as e:
        return _hold("arif_bridge", f"WELL bridge failed: {e}")


def _get_prediction_health() -> dict[str, Any]:
    """Get self-model prediction health summary."""
    try:
        from arifosmcp.core.tool_self_model import get_tool_self_model

        model = get_tool_self_model()
        return model.get_prediction_summary()
    except Exception:
        return {"error": "prediction model not available"}
