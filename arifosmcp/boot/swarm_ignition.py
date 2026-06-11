"""
Swarm Ignition Orchestrator — INIT_0 through INIT_10

DITEMPA BUKAN DIBERI — Forged, Not Given.

Central orchestrator for the AGI-level recursive swarm ignition.
Called ONCE per agent boot from arif_session_init.

Architecture:
  tools.py → run_swarm_ignition() → 6 reader modules → SwarmManifest
  tools.py kekal public MCP surface. boot/ jadi ignition kernel.

Fail-closed: swarm unavailable = session continues, federation degraded.
"""

from __future__ import annotations

import logging
from typing import Any

from arifosmcp.boot.swarm_manifest import build_swarm_manifest
from arifosmcp.boot.swarm_registry import (
    read_swarm_state,
    announce_boot,
)
from arifosmcp.boot.vault999_state import (
    reconstruct_latest_state,
    seal_boot_receipt,
)
from arifosmcp.boot.lease_registry import (
    read_active_agents,
    read_active_leases,
)
from arifosmcp.boot.capability_attest import (
    read_capability_attestations,
)
from arifosmcp.boot.task_registry import (
    read_unresolved_tasks,
)

logger = logging.getLogger(__name__)

# ── Public API ────────────────────────────────────────────────────


def run_swarm_ignition(
    *,
    actor_receipt: dict[str, Any],
    constitution_receipt: dict[str, Any],
    risk_leash: dict[str, Any],
    execution_policy: dict[str, Any],
    session_id: str,
    actor_id: str | None,
    mode: str = "swarm_ignite",
) -> dict[str, Any]:
    """
    Deterministic, read-first swarm ignition.

    INIT_0 → INIT_1 (existing in tools.py — actor + constitution checks)
    INIT_2 → Which swarm?         → swarm_registry.read_swarm_state()
    INIT_3 → What did VAULT999 seal? → vault999_state.reconstruct_latest_state()
    INIT_4 → Who else is active?  → lease_registry.read_active_agents()
    INIT_5 → What leases exist?   → lease_registry.read_active_leases()
    INIT_6 → What organs attested? → capability_attest.read_capability_attestations()
    INIT_7 → What tasks unresolved? → task_registry.read_unresolved_tasks()
    INIT_8 → What action class?   → (existing in tools.py)
    INIT_9 → What must I refuse?  → (existing in tools.py)
    INIT_10 → Seal boot receipt   → vault999_state.seal_boot_receipt()

    No mutation except optional final VAULT999 boot seal.
    If sealing is unavailable or gated, return unsigned manifest.
    """

    # ── INIT_2: Swarm state ──────────────────────────────────
    swarm_state = read_swarm_state(session_id=session_id)

    # ── INIT_3: VAULT999 reconstruction ──────────────────────
    vault_state = reconstruct_latest_state()

    # ── INIT_4 + INIT_5: Active agents and leases ────────────
    active_agents = read_active_agents()
    active_leases = read_active_leases()

    # ── INIT_6: Capability attestations ──────────────────────
    capability_map = read_capability_attestations()

    # ── INIT_7: Unresolved tasks ─────────────────────────────
    unresolved_tasks = read_unresolved_tasks()

    # ── Build manifest ───────────────────────────────────────
    manifest = build_swarm_manifest(
        session_id=session_id,
        actor_id=actor_id,
        mode=mode,
        actor_receipt=actor_receipt,
        constitution_receipt=constitution_receipt,
        risk_leash=risk_leash,
        execution_policy=execution_policy,
        swarm_state=swarm_state,
        vault_state=vault_state,
        active_agents=active_agents,
        active_leases=active_leases,
        capability_map=capability_map,
        unresolved_tasks=unresolved_tasks,
    )

    # ── Announce boot to swarm ───────────────────────────────
    announce_boot(
        agent_id=actor_id or "anonymous",
        session_id=session_id,
    )

    # ── CapabilitySurface: honest live tool/agent/organs status ──
    # Eureka: "The primary resource is not tokens or time;
    # it is HONESTLY KNOWN CAPABILITY."
    try:
        from arifosmcp.boot.capability_surface import build_capability_surface

        surface = build_capability_surface(force_refresh=False, probe_live=True)
        manifest["capability_surface"] = {
            "version": surface.version,
            "timestamp": surface.timestamp,
            "tools": {
                name: {
                    "available": ts.available,
                    "status_alignment": ts.status_alignment,
                    "read_ok": ts.read_ok,
                    "write_ok": ts.write_ok,
                    "last_error": ts.last_error,
                    "note": ts.note,
                }
                for name, ts in surface.tools.items()
            },
            "agents": {
                aid: {
                    "tier": ag.tier,
                    "domains": ag.domains,
                    "status_alignment": ag.status_alignment,
                    "note": ag.note,
                }
                for aid, ag in surface.agents.items()
            },
            "organs": surface.organs,
            "summary": surface.summary,
            "eureka": surface.eureka,
            "invariant": surface.invariant,
        }
    except Exception as exc:
        logger.warning(f"CapabilitySurface build failed (degraded): {exc}")
        manifest["capability_surface"] = {
            "status": "DEGRADED",
            "note": f"CapabilitySurface unavailable: {exc}",
        }

    # ── INIT_10: Seal boot receipt ───────────────────────────
    # Fail-soft: if sealing fails, manifest is still valid
    try:
        seal = seal_boot_receipt(manifest)
        manifest["vault999_boot_seal"] = seal
    except Exception as exc:
        logger.warning(f"Boot seal failed (degraded): {exc}")
        manifest["vault999_boot_seal"] = {
            "status": "UNSEALED",
            "reason": str(exc),
            "degraded": True,
        }

    # ── Human Entropy: SESSION_CLOSE pattern ─────────────────
    # Every session must end with less chaos, clearer truth,
    # tighter risk, fewer open loops, and a sealed path forward.
    try:
        from arifosmcp.boot.entropy_governor import get_entropy_governor

        gov = get_entropy_governor()
        entropy_after = gov.measure(manifest)

        manifest["session_close"] = {
            "verdict": manifest.get("recursive_init", {}).get("next_safe_action", "OBSERVE_ONLY"),
            "entropy_delta": "measured_at_boot",
            "entropy_score": entropy_after.to_dict(),
            "open_loop_count": len(gov.open_loop_register(manifest)),
            "next_safe_action": gov.choose_next_action(manifest, entropy_after).get(
                "action", "OBSERVE_ONLY"
            ),
            "arif_required": entropy_after.irreversible_exposure > 0
            or entropy_after.decision_burden >= 3,
            "vault999_seal_required": entropy_after.missing_provenance >= 2,
            "prime_directive": (
                "Every session must end with less chaos, clearer truth, "
                "tighter risk, fewer open loops, and a sealed path forward."
            ),
        }
    except Exception as exc:
        logger.warning(f"EntropyGovernor failed (degraded): {exc}")
        manifest["session_close"] = {
            "verdict": "DEGRADED",
            "note": f"EntropyGovernor unavailable: {exc}",
        }

    return manifest
