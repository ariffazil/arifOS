"""
Swarm Manifest Builder — Canonical SwarmIgnitionManifest

DITEMPA BUKAN DIBERI — Forged, Not Given.

Builds a SwarmIgnitionManifest from all reader modules.
This is the object all organs trust, not the model's memory.

Architecture:
  Reads from: vault999_state, swarm_registry, lease_registry,
              capability_attest, task_registry
  Produces:   SwarmManifest dict (constitutional Pydantic v2)
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from arifosmcp.boot.swarm_schemas import stable_hash

logger = logging.getLogger(__name__)

# ── Degradation defaults ──────────────────────────────────────────

DEGRADATION_RULES: dict[str, str] = {
    "if_uncertain": "OBSERVE_ONLY",
    "if_vault_unavailable": "NO_FEDERATION_MEMORY",
    "if_capability_unattested": "DENY_TOOL",
    "if_lease_conflict": "HOLD_MUTATION",
}


# ── Public API ────────────────────────────────────────────────────


def build_swarm_manifest(
    *,
    session_id: str,
    actor_id: str | None,
    mode: str,
    actor_receipt: dict[str, Any],
    constitution_receipt: dict[str, Any],
    risk_leash: dict[str, Any],
    execution_policy: dict[str, Any],
    swarm_state: dict[str, Any],
    vault_state: dict[str, Any],
    active_agents: list[dict[str, Any]],
    active_leases: list[dict[str, Any]],
    capability_map: dict[str, dict[str, Any]],
    unresolved_tasks: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Build the canonical SwarmIgnitionManifest.

    All inputs are read-only from the reader modules.
    No mutation. No side effects.
    """

    constitution_hash = constitution_receipt.get("constitution_hash", "unknown")

    manifest: dict[str, Any] = {
        "type": "SwarmIgnitionManifest",
        "version": "VAULT999.swarm.ignite.v1",
        "mode": mode,
        "session_id": session_id,
        "actor_id": actor_id,
        "created_at": datetime.now(UTC).isoformat(),
        "epoch_id": _derive_epoch_id(vault_state),
        # ── Identity receipts ─────────────────────────────────
        "actor_receipt": actor_receipt,
        "constitution_receipt": constitution_receipt,
        "constitution_hash": constitution_hash,
        # ── Swarm topology ────────────────────────────────────
        "swarm": {
            "swarm_id": swarm_state.get("swarm_id", "AAA-FEDERATION-PRIMARY"),
            "status": swarm_state.get("status", "COLD"),
            "active_agents": active_agents,
            "active_leases": active_leases,
            "unresolved_tasks": unresolved_tasks,
        },
        # ── VAULT999 memory ───────────────────────────────────
        "vault999": {
            "latest_seal": vault_state.get("latest_seal"),
            "last_good_state": vault_state.get("last_good_state"),
            "handoff_pointer": vault_state.get("handoff_pointer"),
            "reconstructable": vault_state.get("reconstructable", False),
            "chain_height": vault_state.get("chain_height", 0),
        },
        # ── Capability graph ──────────────────────────────────
        "capabilities": {
            "attested": capability_map,
            "self_claims_allowed": False,
        },
        # ── Governance leash ──────────────────────────────────
        "governance": {
            "risk_leash": risk_leash,
            "execution_policy": execution_policy,
            "human_sovereignty": True,
            "self_authorization": False,
        },
        # ── Rules (non-negotiable) ────────────────────────────
        "rules": {
            "self_authority": False,
            "capability_self_claim_forbidden": True,
            "lease_required_for_action": True,
            "irreversible_action_requires_arif": True,
            "cold_reignition_source": "VAULT999",
        },
        # ── Degradation policy ────────────────────────────────
        "degradation": dict(DEGRADATION_RULES),
        # ── Memory surface ────────────────────────────────────
        "memory_surface": {
            "federation_context_hash": vault_state.get("last_good_state"),
            "visible_to_new_agents": True,
            "private_memory_excluded": True,
        },
        # ── Recursive init gaps ───────────────────────────────
        "recursive_init": {
            "depth": 1,
            "max_depth": 3,
            "gaps": [],
            "next_safe_action": "OBSERVE_ONLY",
        },
    }

    # Compute gaps for recursive improvement
    manifest = _refine_manifest_once(manifest)

    # Compute stable hash
    manifest["manifest_hash"] = stable_hash(
        {k: v for k, v in manifest.items() if k != "manifest_hash"}
    )

    # ── Human Entropy Governance ─────────────────────────────
    try:
        from arifosmcp.boot.entropy_governor import get_entropy_governor

        gov = get_entropy_governor()
        entropy_score = gov.measure(manifest)
        open_loops = gov.open_loop_register(manifest)
        next_action = gov.choose_next_action(manifest, entropy_score)

        manifest["human_entropy"] = {
            "score": entropy_score.to_dict(),
            "verdict": (
                "CHAOS_REDUCED"
                if entropy_score.ratio() < 0.3
                else "CHAOS_MANAGEABLE"
                if entropy_score.ratio() < 0.6
                else "CHAOS_HIGH"
            ),
            "open_loops": open_loops,
            "open_loop_count": len(open_loops),
            "recommended_next_action": next_action,
            "prime_directive": (
                "Every session must reduce Arif's uncertainty, decision load, "
                "coordination burden, operational chaos, or future recovery cost."
            ),
        }
    except Exception:
        manifest["human_entropy"] = {
            "status": "DEGRADED",
            "note": "EntropyGovernor unavailable",
        }

    # ── Theory of Mind ───────────────────────────────────────
    try:
        from arifosmcp.boot.theory_of_mind import get_tom_engine

        tom_engine = get_tom_engine()
        tom = tom_engine.build(input_context={"mode": mode}, state=manifest)
        manifest["theory_of_mind"] = {
            "human": {
                "name": tom.human.name,
                "role": tom.human.role,
                "decision_burden": tom.human.decision_burden,
                "context_familiarity": tom.human.context_familiarity,
                "needs": tom.human.needs,
                "avoid": tom.human.avoid,
                "claim_state": tom.human.claim_state,
            },
            "agents_known": len(tom.agents),
            "sovereignty_required": tom.sovereignty_required,
            "entropy_sources": tom_engine.entropy_sources(tom, manifest),
            "summary": tom.summary,
            "note": "Theory of mind is operational modeling, not mind-reading. ToM aims the agent toward the human.",
        }
    except Exception:
        manifest["theory_of_mind"] = {
            "status": "DEGRADED",
            "note": "TheoryOfMindEngine unavailable",
        }

    # ── Internal Rasa ────────────────────────────────────────
    try:
        from arifosmcp.boot.internal_rasa import get_rasa_engine

        rasa_engine = get_rasa_engine()
        rasa = rasa_engine.measure(manifest)
        gate = rasa_engine.gate_action(rasa)
        manifest["internal_rasa"] = {
            "state": rasa.to_dict(),
            "gate": gate,
            "note": "Rasa is governed telemetry, not consciousness. Rasa is the brake system of intelligence.",
        }
    except Exception:
        manifest["internal_rasa"] = {
            "status": "DEGRADED",
            "note": "InternalRasaEngine unavailable",
        }

    return manifest


# ── Recursive improvement (bounded, depth ≤ 3) ────────────────────


def _refine_manifest_once(manifest: dict[str, Any]) -> dict[str, Any]:
    """
    One bounded recursive improvement pass.
    No open-ended self-reflection. Max depth = 3.

    Detects: VAULT999 gaps, lease gaps, capability degradation,
             STATIC_CLAIM→DEGRADED status, task gaps.
    """
    gaps: list[str] = []
    degraded: list[str] = []

    vault = manifest.get("vault999", {})
    swarm = manifest.get("swarm", {})
    caps = manifest.get("capabilities", {})

    if not vault.get("reconstructable"):
        gaps.append("NO_RECONSTRUCTABLE_VAULT_STATE")

    if not swarm.get("active_leases"):
        gaps.append("NO_ACTIVE_LEASES_SEEN")

    if not swarm.get("unresolved_tasks"):
        gaps.append("NO_UNRESOLVED_TASKS")

    # ── Capability degradation detection ─────────────────────
    attested = caps.get("attested", {})
    if not attested:
        gaps.append("NO_CAPABILITY_ATTESTATION")
    else:
        for organ, info in attested.items():
            status = info.get("status", "UNKNOWN")
            if status.startswith("DEGRADED"):
                degraded.append(f"{organ}:{status}")
            elif status == "STATIC_CLAIM":
                degraded.append(f"{organ}:STATIC_CLAIM→should_be_LIVE_ATTESTED")

    if degraded:
        gaps.append(
            f"CAPABILITY_DEGRADED: {len(degraded)} organs ({', '.join(degraded[:3])}{'...' if len(degraded) > 3 else ''})"
        )

    # ── Determine next safe action ───────────────────────────
    if not vault.get("reconstructable"):
        next_action = "OBSERVE_ONLY"
    elif not attested:
        next_action = "OBSERVE_ONLY"
    elif degraded:
        next_action = "OBSERVE_ONLY"
    elif not swarm.get("active_leases"):
        next_action = "OBSERVE_ONLY"
    else:
        next_action = "PROCEED_WITH_LEASE_RULES"

    manifest["recursive_init"] = {
        "depth": 1,
        "max_depth": 3,
        "gaps": gaps,
        "degraded_organs": degraded,
        "next_safe_action": next_action,
        "improvement_note": (
            "All organs are DEGRADED_CLAIM. Live NATS attestation required for "
            "capability upgrade. No static claim becomes authority."
            if degraded
            else "No degradation detected."
        ),
    }

    return manifest


def _derive_epoch_id(vault_state: dict[str, Any]) -> str:
    """Derive epoch ID from the latest seal or generate new one."""
    latest = vault_state.get("latest_seal")
    if latest:
        seal_id = latest.get("id", "unknown")
        return f"EPOCH-{seal_id}"
    # No prior seal — first boot
    now = datetime.now(UTC)
    return f"EPOCH-{now.strftime('%Y-%m-%d')}-COLD-BOOT"
