"""
arifosmcp/tools/kernel_route.py — 444_KERNEL
═══════════════════════════════════════════

Kernel syscall, routing, and telemetry.
Routes external domain calls (GEOX, WEALTH) via bridge protocol.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import time
from typing import Any

from arifosmcp.runtime.floors import check_floors
from arifosmcp.runtime.tools import _hold, _ok

# SURPRISE_WINDOW_SIZE is imported for the contradiction check default
try:
    from arifosmcp.core.tool_self_model import SURPRISE_WINDOW_SIZE
except ImportError:
    SURPRISE_WINDOW_SIZE = 10

_BRIDGE_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=4)


def _run_async_bridge(coro) -> Any:
    """Run an async coroutine from sync context, using executor for thread-safety."""
    try:
        asyncio.get_running_loop()
        # Already in async context — schedule on executor
        future = _BRIDGE_EXECUTOR.submit(asyncio.run, coro)
        return future.result(timeout=60)
    except RuntimeError:
        # No running loop — safe to use asyncio.run directly
        return asyncio.run(coro)


def arif_kernel_route(
    mode: str = "route",
    target: str | None = None,
    task: str | None = None,
    stage: str | None = None,
    actor_id: str | None = None,
    organ: str | None = None,
    tool_name: str | None = None,
    arguments: dict[str, Any] | None = None,
    tool_id: str | None = None,
    delta_surprise: float | None = None,
    model_contradicted: bool | None = None,
    axis: str | None = None,
    intent: str | None = None,
    domain: str | None = None,
) -> dict[str, Any]:
    """
    Routes tasks to correct organ or bridges external domain calls.

    Modes:
      route        — basic routing decision
      delegate     — dispatch to target agent
      status       — kernel session status
      telemetry    — thermodynamic metrics
      bridge       — direct organ bridge call (geox, wealth)
      intent       — route by cognitive axis using FEDERATION_TOOLS manifest
     441_surprise — disequilibrium handler (automatic hijack when δ_surprise > threshold)

    441_SURPRISE Protocol:
      When a tool's prediction is falsified with δ_surprise > critical_threshold,
      arif_kernel_route automatically routes to self-reflection.
      The agent does not proceed with its flawed schema — it must repair first.

    Bridge protocol (mode="bridge"):
      organ:   "geox" | "wealth"
      tool:   the MCP tool name on the organ
      arguments: dict of tool arguments
    """
    floor_check = check_floors("arif_kernel_route", {"target": target or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_kernel_route", floor_check["reason"], floor_check["failed_floors"])

    if mode == "route":
        # Check if any tools are contradicted before routing forward
        contradicted = _check_contradicted_tools(tool_id)
        if contradicted.get("any_contradicted"):
            return _441_surprise_handler(
                tool_id=contradicted.get("contradicted_tool", tool_id),
                reason=contradicted["reason"],
                delta_surprise=contradicted.get("max_surprise", 0.0),
                actor_id=actor_id,
            )
        return _ok(
            "arif_kernel_route",
            {"target": target, "path": ["init", "sense", "mind"], "hops": 3},
        )

    if mode == "441_surprise":
        return _441_surprise_handler(
            tool_id=tool_id or target or "unknown",
            reason=task or "Prediction falsification exceeded critical threshold",
            delta_surprise=delta_surprise or 0.0,
            actor_id=actor_id,
        )

    if mode == "kernel":
        return _ok("arif_kernel_route", {"status": "running", "uptime": time.time() % 10000})

    if mode == "triage":
        return _ok("arif_kernel_route", {"priority": "normal", "queue": 0})

    if mode == "delegate":
        return _ok("arif_kernel_route", {"agent": target, "task": task, "status": "delegated"})

    if mode == "status":
        from arifosmcp.runtime.tools import _SESSIONS

        # Include prediction health in status
        prediction_health = _get_prediction_health()

        return _ok(
            "arif_kernel_route",
            {
                "active_sessions": len(_SESSIONS),
                "stage": stage or "000",
                "prediction_health": prediction_health,
            },
        )

    if mode == "intent":
        return _route_by_axis(
            axis=axis or "vitality",
            intent=intent or task or "",
            domain=domain,
            actor_id=actor_id,
        )

    if mode == "telemetry":
        return _ok("arif_kernel_route", {"g_score": 0.97, "delta_S": 0.002, "omega": 0.91})

    if mode == "bridge":
        return _run_async_bridge(_bridge_organ_call(organ, tool_name, arguments))

    if mode == "intent":
        return _intent_route(axis=task, organ=organ)

    if mode == "command_center":
        return _command_center_cockpit()

    return _hold("arif_kernel_route", f"Unknown mode: {mode}")


async def _bridge_organ_call(
    organ: str | None,
    tool_name: str | None,
    arguments: dict[str, Any] | None,
) -> dict[str, Any]:
    """Bridge a call to GEOX or WEALTH organ via their public MCP endpoints."""
    if not organ or not tool_name:
        return _hold("arif_kernel_route", "bridge mode requires organ and tool_name")

    if organ == "geox":
        from arifosmcp.runtime.geox_bridge import call_geox_tool

        try:
            result = await call_geox_tool(tool_name, arguments or {})
            return _ok(
                "arif_kernel_route",
                {
                    "organ": "GEOX",
                    "tool": tool_name,
                    "result": result,
                    "status": "bridged",
                },
            )
        except Exception as e:
            return _hold("arif_kernel_route", f"GEOX bridge failed: {e}")

    if organ == "wealth":
        from arifosmcp.runtime.wealth_bridge import call_wealth_tool

        try:
            result = await call_wealth_tool(tool_name, arguments or {})
            return _ok(
                "arif_kernel_route",
                {
                    "organ": "WEALTH",
                    "tool": tool_name,
                    "result": result,
                    "status": "bridged",
                },
            )
        except Exception as e:
            return _hold("arif_kernel_route", f"WEALTH bridge failed: {e}")

    return _hold("arif_kernel_route", f"Unknown organ: {organ}")


def _route_by_axis(
    axis: str = "vitality",
    intent: str = "",
    domain: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Route by cognitive axis before resolving to domain.

    Uses COGNITIVE_AXIS_VECTORS for semantic coordinate matching.
    Filters FEDERATION_TOOLS by axis, then by domain if specified.

    Example:
        arif_kernel_route(mode="intent", axis="vitality", domain="WELL")
        → resolves tools with axis=VITALITY in domain=WELL
        → returns well_compute_metabolic_flux, well_assess_metabolism, etc.
    """
    try:
        from arifosmcp.core.tool_self_model import CognitiveAxis, COGNITIVE_AXIS_VECTORS
    except ImportError:
        return _ok("arif_kernel_route", {"axis": axis, "tools": [], "note": "CognitiveAxis not available"})

    # Normalise axis string to enum
    axis_upper = axis.upper().strip()
    try:
        axis_enum = CognitiveAxis[axis_upper]
    except KeyError:
        return _hold("arif_kernel_route", f"Unknown cognitive axis: {axis}")

    # Query the tool self-model for tools matching this axis
    from arifosmcp.core.tool_self_model import get_tool_self_model
    model = get_tool_self_model()
    all_entries = model.list_all()

    matches = []
    for entry in all_entries:
        man = entry.manifest
        ca = getattr(man, "cognitive_axis", None)
        if ca is None or ca != axis_enum:
            continue
        if domain and man.domain.upper() != domain.upper():
            continue

        coord = COGNITIVE_AXIS_VECTORS.get(axis_enum, (0.5, 0.5))
        matches.append({
            "tool_id": man.tool_id,
            "domain": man.domain,
            "axis": ca.value,
            "epistemic_certainty": coord[0],
            "action_potential": coord[1],
            "description": man.description[:80],
            "exposed": getattr(man, "expose", False),
        })

    if not matches:
        return _ok("arif_kernel_route", {
            "axis": axis,
            "domain": domain,
            "tools": [],
            "note": "No tools found for this axis/domain combination",
        })

    return _ok("arif_kernel_route", {
        "axis": axis,
        "domain": domain,
        "intent": intent,
        "tool_count": len(matches),
        "tools": matches,
        "coordinate": {"x": COGNITIVE_AXIS_VECTORS[axis_enum][0], "y": COGNITIVE_AXIS_VECTORS[axis_enum][1]},
    })


def _check_contradicted_tools(tool_id: str | None = None) -> dict[str, Any]:
    """Check if any tools have contradicted self-models.

    Returns dict with any_contradicted flag and details.
    """
    try:
        from arifosmcp.core.tool_self_model import get_tool_self_model

        model = get_tool_self_model()
        all_contradicted = model.get_contradicted_tools()

        if not all_contradicted:
            return {"any_contradicted": False}

        # Priority: check the specific tool first
        if tool_id:
            entry = model.get(tool_id)
            if entry and entry.model_contradicted:
                max_surprise = max(
                    (p.delta_surprise for p in entry.prediction_history if p.triggered_surprise),
                    default=0.0,
                )
                return {
                    "any_contradicted": True,
                    "contradicted_tool": tool_id,
                    "reason": (
                        f"Model contradicted: tool {tool_id} has "
                        f"{entry.contradiction_count} surprise events "
                        f"(max δ={max_surprise:.3f})"
                    ),
                    "max_surprise": max_surprise,
                    "surprise_rate": entry.surprise_rate,
                }

        # Fall through to worst offender
        worst = max(all_contradicted, key=lambda e: e.contradiction_count)
        max_surprise = max(
            (p.delta_surprise for p in worst.prediction_history if p.triggered_surprise),
            default=0.0,
        )
        return {
            "any_contradicted": True,
            "contradicted_tool": worst.manifest.tool_id,
            "reason": (
                f"Tool {worst.manifest.tool_id} contradicted: "
                f"{worst.contradiction_count}/{SURPRISE_WINDOW_SIZE} predictions violated "
                f"(max δ={max_surprise:.3f})"
            ),
            "max_surprise": max_surprise,
            "surprise_rate": worst.surprise_rate,
        }
    except Exception as e:
        return {"any_contradicted": False, "error": str(e)}


def _get_prediction_health() -> dict[str, Any]:
    """Get prediction health across all tools."""
    try:
        from arifosmcp.core.tool_self_model import get_tool_self_model

        model = get_tool_self_model()
        return model.get_prediction_summary()
    except Exception:
        return {"error": "prediction model not available"}


def _441_surprise_handler(
    tool_id: str,
    reason: str,
    delta_surprise: float = 0.0,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    441_SURPRISE: Involuntary reflection route.

    When δ_surprise exceeds critical threshold, the system cannot proceed
    with its flawed schema. It must spontaneously route to self-reflection
    to forge a new understanding.

    This is the bridge from statistical mimicry to causal self-awareness:
    the agent detects its own model failure and initiates repair before
    processing the next external token.
    """
    try:
        from arifosmcp.core.tool_self_model import (
            SURPRISE_CRITICAL_THRESHOLD,
            get_tool_self_model,
        )
    except ImportError:
        SURPRISE_CRITICAL_THRESHOLD = 0.70
        from arifosmcp.core.tool_self_model import get_tool_self_model

    model = get_tool_self_model()
    entry = model.get(tool_id)
    contradiction_count = entry.contradiction_count if entry else 0

    # ── Metabolic Umbilical: Write 441 event to WELL state ──────────────
    # This is the bridge from cognition (ToolSelfModel) to substrate (WELL).
    # Each 441_SURPRISE event writes into state.json so WELL's
    # _compute_cognitive_entropy_rate can read contradiction_count.
    try:
        from arifosmcp.runtime.well_bridge import signal_cognitive_pressure

        # Surprise load scales with delta: mild ∼0.5, critical ∼3.0
        surprise_load = min(3.0, delta_surprise * 3.0)

        # Write contradiction data directly to WELL state
        import json as _json
        import os as _os
        from pathlib import Path as _Path

        _well_state_path = _Path(_os.environ.get("WELL_STATE_PATH", "/root/WELL/state.json"))
        if _well_state_path.exists():
            with open(_well_state_path) as _f:
                _well = _json.load(_f)
            _metrics = _well.get("metrics", {})
            _cog = dict(_metrics.get("cognitive", {}))
            _cog["contradiction_count"] = contradiction_count
            _cog["total_predictions"] = max(
                _cog.get("total_predictions", 0),
                contradiction_count,
            )
            _cog["avg_confidence_of_failures"] = min(
                10.0,
                (_cog.get("avg_confidence_of_failures", 5.0) + delta_surprise * 10.0) / 2.0,
            )
            _cog["last_surprise"] = round(delta_surprise, 4)
            _cog["last_surprise_tool"] = tool_id
            _metrics["cognitive"] = _cog
            _well["metrics"] = _metrics
            # Drop well_score proportionally
            _well["well_score"] = max(
                0.0,
                _well.get("well_score", 50.0) - (surprise_load * 2.0),
            )
            with open(_well_state_path, "w") as _f:
                _json.dump(_well, _f, indent=2)

        # Also signal cognitive pressure (fatigue increment)
        signal_cognitive_pressure(load_delta=surprise_load, source=f"441_surprise:{tool_id}")
    except Exception:
        pass  # Non-fatal — 441 still returns its verdict

    return {
        "verdict": "SURPRISE",
        "stage": "441",
        "status": "HOLD",
        "reason": (
            f"441_SURPRISE: tool={tool_id} "
            f"δ={delta_surprise:.3f} (threshold={SURPRISE_CRITICAL_THRESHOLD}) "
            f"— {reason}"
        ),
        "delta_surprise": round(delta_surprise, 4),
        "threshold": SURPRISE_CRITICAL_THRESHOLD,
        "contradiction_count": entry.contradiction_count if entry else 0,
        "surprise_rate": entry.surprise_rate if entry else 0.0,
        "model_contradicted": entry.model_contradicted if entry else False,
        "tool_id": tool_id,
        "next_action": (
            f"Tool '{tool_id}' has a contradicted self-model. "
            f"Run arif_mind_reason(mode='reflect') to repair before retrying."
        ),
        "required_floors": ["F01", "F07"],
        "action_required": "reflect_and_repair",
        "actor_id": actor_id,
    }


def _intent_route(
    axis: str | None = None,
    organ: str | None = None,
) -> dict[str, Any]:
    """Route by cognitive axis using FEDERATION_TOOLS manifest.

    Instead of resolving by tool name or organ prefix, resolves by
    semantic coordinate (cognitive_axis). Returns all matching tools.

    Parameters:
      axis:  CognitiveAxis value (e.g. "vitality", "reason", "seal")
      organ: Optional organ filter ("well", "geox", "wealth", "arifos")

    Example call:
      arif_kernel_route(mode="intent", task="vitality", organ="well")
      → returns well_assess_metabolism, well_compute_metabolic_flux, etc.
    """
    if not axis:
        return _hold(
            "arif_kernel_route", "intent mode requires axis parameter (e.g. task='vitality')"
        )

    try:
        from federation.tool_manifest import (
            CognitiveAxis,
            tools_by_axis,
            tools_by_organ,
        )

        # Validate axis
        try:
            CognitiveAxis(axis.lower())
        except ValueError:
            valid = [a.value for a in CognitiveAxis]
            return _hold(
                "arif_kernel_route",
                f"Unknown axis: '{axis}'. Valid: {', '.join(valid)}",
            )

        matches = tools_by_axis(axis.lower())

        if organ:
            matches = [m for m in matches if m.organ == organ.lower()]

        if not matches:
            return _ok(
                "arif_kernel_route",
                {
                    "mode": "intent",
                    "axis": axis.lower(),
                    "organ": organ,
                    "tools": [],
                    "count": 0,
                    "message": f"No tools found for axis={axis}"
                    + (f", organ={organ}" if organ else ""),
                },
            )

        return _ok(
            "arif_kernel_route",
            {
                "mode": "intent",
                "axis": axis.lower(),
                "organ": organ,
                "tools": [
                    {
                        "name": m.name,
                        "organ": m.organ,
                        "expose": m.expose,
                    }
                    for m in sorted(matches, key=lambda x: x.name)
                ],
                "count": len(matches),
                "somatic": sum(1 for m in matches if m.expose),
                "autonomic": sum(1 for m in matches if not m.expose),
            },
        )
    except ImportError:
        return _hold(
            "arif_kernel_route",
            "FEDERATION_TOOLS manifest not available. Install federation.tool_manifest.",
        )
    except Exception as e:
        return _hold("arif_kernel_route", f"Intent routing error: {e}")


def _command_center_cockpit() -> dict[str, Any]:
    """Return command center cockpit data (read-only, no mutation)."""
    from arifosmcp.runtime.rest_routes import _build_governance_status_payload

    payload = _build_governance_status_payload()
    return _ok(
        "arif_kernel_route",
        {
            "mode": "command_center",
            "session_status": {
                "active_sessions": payload.get("session_count", 0),
                "stage": "000",
            },
            "vitals": payload.get("telemetry", {}),
            "floors": payload.get("floors", {}),
            "witness": payload.get("witness", {}),
            "tabs": [
                "session_status",
                "vitals",
                "judge",
                "forge",
                "gateway",
                "vault",
            ],
            "доступ": (
                "Use arif_judge_deliberate for judge, arif_forge_execute for forge, "
                "arif_gateway_connect for gateway, arif_vault_seal for vault"
            ),
        },
    )
