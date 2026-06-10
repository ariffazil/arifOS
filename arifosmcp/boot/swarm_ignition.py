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

    return manifest
