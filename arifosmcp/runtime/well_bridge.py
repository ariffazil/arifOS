"""
arifOS WELL Bridge — Biological Substrate Connector
═══════════════════════════════════════════════════════════════════════════════

Connects the arifOS Governance Kernel to the WELL Human Substrate Layer.
Provides biological readiness signals (Sleep, Stress, Cognitive) to JUDGE.

Two data sources:
  1. WELL MCP server (HTTP) — live health, tool surface, domain identity
  2. WELL state.json (file) — biometric readings injected by Arif (F13)

Axiom: W0 — Sovereignty Invariant. WELL informs, JUDGE considers.
"""

from __future__ import annotations

import json
import logging
import os as _os
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Topology: WELL State Path
WELL_STATE_PATH = Path(_os.environ.get("WELL_STATE_PATH", "/root/WELL/state.json"))

# WELL MCP server (HTTP)
WELL_HOST = _os.environ.get("WELL_BRIDGE_HOST", "localhost")
WELL_PORT = int(_os.environ.get("WELL_BRIDGE_PORT", "18083"))
WELL_BASE = f"http://{WELL_HOST}:{WELL_PORT}"


def get_biological_readiness() -> dict[str, Any]:
    """
    Read the current biological readiness from WELL state.
    Returns a structured readiness report for the Governance Kernel.
    """
    try:
        _exists = WELL_STATE_PATH.exists()
    except (PermissionError, OSError):
        _exists = False
    if not _exists:
        return {
            "ok": False,
            "verdict": "UNKNOWN",
            "well_score": 50.0,
            "bandwidth": "NORMAL",
            "message": "WELL substrate offline or state missing.",
            "sabar_advisory": False,
        }

    try:
        with open(WELL_STATE_PATH) as f:
            state = json.load(f)

        score = state.get("well_score", 50.0)
        violations = state.get("floors_violated", [])

        # Readiness logic (mirrors WELL/server.py:well_readiness)
        if violations:
            verdict = "DEGRADED"
            bandwidth = "RESTRICTED"
            sabar_advisory = True
        elif score >= 80:
            verdict = "OPTIMAL"
            bandwidth = "FULL"
            sabar_advisory = False
        elif score >= 60:
            verdict = "FUNCTIONAL"
            bandwidth = "NORMAL"
            sabar_advisory = False
        else:
            verdict = "LOW_CAPACITY"
            bandwidth = "REDUCED"
            sabar_advisory = True

        return {
            "ok": True,
            "verdict": verdict,
            "well_score": score,
            "bandwidth": bandwidth,
            "violations": violations,
            "sabar_advisory": sabar_advisory,
            "timestamp": state.get("timestamp"),
        }
    except Exception as e:
        logger.error(f"Failed to read WELL state: {e}")
        return {
            "ok": False,
            "verdict": "ERROR",
            "error": str(e),
            "well_score": 0.0,
            "bandwidth": "RESTRICTED",
            "sabar_advisory": True,
        }


def inject_biological_context(governance_state: dict[str, Any]) -> dict[str, Any]:
    """
    Inject biological readiness into the governance state telemetry.
    """
    readiness = get_biological_readiness()

    # Add WELL metadata to telemetry
    telemetry = governance_state.get("telemetry", {})
    telemetry["well_score"] = readiness["well_score"]
    telemetry["well_verdict"] = readiness["verdict"]
    telemetry["well_bandwidth"] = readiness["bandwidth"]

    if readiness["sabar_advisory"]:
        # If biological state is degraded, suggest SABAR (Patience)
        governance_state["sabar_advisory"] = True
        if governance_state.get("verdict") == "SEAL":
            # Soft-downgrade to HOLD if it was SEAL but substrate is low
            if readiness["verdict"] == "DEGRADED":
                governance_state["verdict"] = "HOLD"
                governance_state["message"] = (
                    governance_state.get("message", "")
                    + " [WELL-HOLD] Biological substrate degraded. Sovereign review required."
                )

    return governance_state


def apply_metabolic_constraints(
    governance_state: dict[str, Any],
    action_risk_tier: str = "LOW",
    last_high_stakes_timestamp: float | None = None,
) -> dict[str, Any]:
    """
    W6 Metabolic Pause + P7 Sovereign Overload hard-downgrade.

    Per PARADOX_DOCTRINE_V1 Section 8:
      - LOW_CAPACITY (< 0.60): non-critical auto-HOLD, irreversible blocked,
        min rest interval 30 min, L13 override only after rest interval
      - DEGRADED: ALL operations auto-HOLD, only EMERGENCY_STOP and STATUS_REPORT accepted
    """
    readiness = get_biological_readiness()
    if not readiness["ok"]:
        return governance_state

    verdict = readiness["verdict"]
    constraints_applied: list[str] = []

    if verdict == "DEGRADED":
        # Hard-downgrade ALL operations to HOLD
        if governance_state.get("verdict") != "HOLD":
            governance_state["verdict"] = "HOLD"
            constraints_applied.append("W6-DEGRADED-HOLD")
        governance_state["message"] = (
            governance_state.get("message", "")
            + " [W6-DEGRADED] All operations auto-HOLD. Only EMERGENCY_STOP / STATUS_REPORT accepted."
        )
        governance_state["only_emergency"] = True

    elif verdict == "LOW_CAPACITY":
        # Block irreversible regardless of verdict
        if action_risk_tier in ("HIGH", "CRITICAL"):
            governance_state["verdict"] = "HOLD"
            constraints_applied.append("W6-LOW_CAPACITY-IRREVERSIBLE_BLOCKED")
            governance_state["message"] = (
                governance_state.get("message", "")
                + " [W6-LOW_CAPACITY] Irreversible action blocked. Sovereign rest interval required."
            )
        else:
            # Non-critical auto-HOLD unless rest interval met
            if last_high_stakes_timestamp is not None:
                elapsed_min = (__import__("time").time() - last_high_stakes_timestamp) / 60.0
                if elapsed_min < 30:
                    governance_state["verdict"] = "HOLD"
                    constraints_applied.append("W6-LOW_CAPACITY-REST_INTERVAL")
                    governance_state["message"] = (
                        governance_state.get("message", "")
                        + f" [W6-LOW_CAPACITY] Rest interval active ({30 - int(elapsed_min)} min remaining)."
                    )
                else:
                    constraints_applied.append("W6-LOW_CAPACITY-L13_AVAILABLE")
            else:
                constraints_applied.append("W6-LOW_CAPACITY-L13_AVAILABLE")

    if constraints_applied:
        governance_state["metabolic_constraints"] = constraints_applied

    return governance_state


def signal_cognitive_pressure(load_delta: float, source: str = "forge") -> bool:
    """
    Signal cognitive pressure/load to WELL.
    Directly updates state.json if server is not available.
    """
    try:
        if not WELL_STATE_PATH.exists():
            return False
    except (PermissionError, OSError):
        return False

    try:
        with open(WELL_STATE_PATH) as f:
            state = json.load(f)

        metrics = state.get("metrics", {})
        cog = dict(metrics.get("cognitive", {"clarity": 10, "decision_fatigue": 0}))

        # Increment fatigue — handle None explicitly (key may exist with null value)
        old_fatigue = cog.get("decision_fatigue") or 0
        try:
            new_fatigue = min(10.0, float(old_fatigue) + load_delta)
        except (TypeError, ValueError):
            new_fatigue = load_delta
        cog["decision_fatigue"] = new_fatigue
        metrics["cognitive"] = cog

        # W6 Logic (Sync with server logic)
        violations = state.get("floors_violated", [])
        if load_delta > 2.0 and "W6_METABOLIC_PAUSE" not in violations:
            violations.append("W6_METABOLIC_PAUSE")

        state["metrics"] = metrics
        # Note: We don't recompute score here to keep the bridge lightweight;
        # the score will be recomputed next time WELL server is used or state is loaded.
        # But for UI accuracy, a quick estimation is better:
        state["well_score"] = max(0, state.get("well_score", 50) - (load_delta * 2))
        state["floors_violated"] = violations

        with open(WELL_STATE_PATH, "w") as f:
            json.dump(state, f, indent=2)
        return True
    except Exception:
        return False


async def anchor_well_to_vault(
    summary: str = "WELL Substrate Anchor", force: bool = False
) -> dict[str, Any]:
    """
    Anchor current WELL state to the arifOS VAULT999.
    Provides immutable grounding for biological telemetry.
    """
    readiness = get_biological_readiness()
    if not readiness["ok"] and not force:
        return {"ok": False, "message": "Substrate offline. Anchor aborted."}

    try:
        from core.organs._4_vault import seal

        # Build telemetry for the vault
        telemetry = {
            "well_score": readiness["well_score"],
            "well_verdict": readiness["verdict"],
            "well_bandwidth": readiness["bandwidth"],
            "well_violations": readiness.get("violations", []),
            "source": "WELL-Substrate",
        }

        # Final seal of substrate state
        res = await seal(
            session_id="WELL-AUTO-SYNC",
            summary=summary,
            verdict=("SEAL" if readiness["verdict"] in ("OPTIMAL", "FUNCTIONAL") else "HOLD"),
            telemetry=telemetry,
            source_agent="well",
            pipeline_stage="999_SEAL",
            risk_tier="LOW",
        )

        return {
            "ok": True,
            "vault_id": res.seal_record.ledger_id,
            "hash": res.seal_record.hash,
            "verdict": res.verdict,
        }
    except Exception as e:
        logger.error(f"VAULT ANCHOR FAILED: {e}")
        return {"ok": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# WELL MCP HTTP Bridge (2026-06-13 — organ attestation)
# ═══════════════════════════════════════════════════════════════════════════════


async def _post_json_rpc_well(payload: dict[str, Any]) -> dict[str, Any]:
    """Send a JSON-RPC request to WELL MCP and return the result."""
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        resp = await client.post(
            f"{WELL_BASE}/mcp",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
        )
        if resp.status_code >= 400:
            raise ConnectionError(f"WELL HTTP {resp.status_code}: {resp.text[:200]}")
        parsed = resp.json()
        if parsed.get("error"):
            raise ConnectionError(f"WELL JSON-RPC error: {parsed['error']}")
        return parsed.get("result", {})


async def list_well_tools() -> list[dict[str, Any]]:
    """List all tools available from WELL MCP server."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {},
    }
    try:
        result = await _post_json_rpc_well(payload)
        return result.get("tools", [])
    except Exception as e:
        logger.warning(f"list_well_tools failed: {e}")
        return []


async def well_health_check() -> dict[str, Any]:
    """
    Check WELL server health via REST /health endpoint AND tool surface.

    Returns domain identity fields (domain_law, substrate_manifest_hash)
    for organ attestation. Also falls back to file-based readiness.
    """
    result: dict[str, Any] = {
        "status": "unhealthy",
        "organ": "WELL",
        "host": WELL_HOST,
    }

    # ── REST health endpoint (carries domain identity) ──────────────
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{WELL_BASE}/health")
            if resp.status_code == 200:
                health_data = resp.json()
                result["status"] = health_data.get("status", "healthy")
                result["version"] = health_data.get("version", "unknown")
                result["identity"] = health_data.get("identity", False)
                result["tool_count"] = health_data.get("tool_count", 0)
                # Domain identity — WELL answers to SUBSTRATE_LAW
                result["domain_law"] = health_data.get("domain_law", "SUBSTRATE_LAW")
                result["substrate_manifest_hash"] = health_data.get(
                    "substrate_manifest_hash", "sha256:missing"
                )
                result["identity_anchor_type"] = "substrate_manifest"
                result["identity_anchor_hash"] = result["substrate_manifest_hash"]
    except Exception as e:
        result["health_endpoint_error"] = str(e)

    # ── File-based readiness (backward compat) ──────────────────────
    try:
        readiness = get_biological_readiness()
        if readiness.get("ok"):
            result["well_score"] = readiness.get("well_score")
            result["well_verdict"] = readiness.get("verdict")
    except Exception:
        pass

    # ── Tool surface check ──────────────────────────────────────────
    try:
        tools = await list_well_tools()
        if tools:
            if result.get("status") == "unhealthy":
                result["status"] = "healthy"
            result["tool_surface"] = "reachable"
    except Exception as e:
        result["tool_surface_error"] = str(e)
        if result.get("status") != "unhealthy":
            result["status"] = "degraded"

    return result
