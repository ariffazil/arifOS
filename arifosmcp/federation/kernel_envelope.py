"""
arifOS Kernel Envelope — Governed Wrapper for Organ Outputs
════════════════════════════════════════════════════════════
DITEMPA BUKAN DIBERI — Forged, Not Given.

Wraps any organ's universal envelope inside the arifOS kernel envelope,
providing session identity, authority lease, and constitutional context.

This is the AGI substrate contract: every governed organ output flowing
through arifOS gets this wrapper before reaching the agent.

Architecture:
    GEOX universal envelope → kernel_envelope(payload=geox_output)
    → arif_judge → verdict → agent response
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from typing import Any, Literal

# ═══════════════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════════════

CONSTITUTION_HASH = os.environ.get(
    "ARIFOS_CONSTITUTION_HASH",
    "sha256:dd4f41e75f55ed38df759a1c8db1fc4680ef0307a6b0e2793bccf6540bb21506",
)

ActionClass = Literal["OBSERVE", "ANALYZE", "MUTATE", "IRREVERSIBLE"]
VerdictClass = Literal["SEAL", "QUALIFY", "HOLD", "VOID", "888_HOLD"]

ORGAN_CONTRACT_VERSIONS = {
    "GEOX": "GEOX-SOVEREIGN-v2026.05.22",
    "WEALTH": "WEALTH-SOVEREIGN-v2026.05.02",
    "WELL": "WELL-SOVEREIGN-v2026.05.15",
}

ORGAN_ROLES = {
    "GEOX": "earth_intelligence",
    "WEALTH": "capital_intelligence",
    "WELL": "human_readiness",
}

# Four-lane authority matrix
LANE_MAX_ACTION_CLASS: dict[str, ActionClass] = {
    "discovery": "OBSERVE",
    "evidence": "ANALYZE",
    "reasoning": "ANALYZE",
    "judgment": "ANALYZE",  # governed — requires arifOS judge beyond ANALYZE
}

LANE_REQUIRES_LEASE: dict[str, bool] = {
    "discovery": False,
    "evidence": False,
    "reasoning": True,
    "judgment": True,
}

LANE_REQUIRES_SESSION: dict[str, bool] = {
    "discovery": False,
    "evidence": False,
    "reasoning": True,
    "judgment": True,
}


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _hash_payload(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]


def get_lane_for_tool(organ_id: str, tool_name: str) -> str:
    """Get the lane classification for a given organ tool.

    Loads from GEOX.yaml federation contract if available,
    else falls back to heuristics.
    """
    if organ_id == "GEOX":
        try:
            import yaml

            contract_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "federation",
                "GEOX.yaml",
            )
            if os.path.exists(contract_path):
                with open(contract_path) as f:
                    contract = yaml.safe_load(f)
                lane_map = contract.get("lanes", {}).get("tool_lane_map", {})
                if tool_name in lane_map:
                    return lane_map[tool_name]
        except Exception:
            pass

        # Fallback heuristics based on tool name patterns
        judgment_tools = {
            "geox_claim",
            "geox_claim_create",
            "geox_claim_validate",
            "geox_claim_challenge",
            "geox_claim_seal",
            "geox_segy_export_tool",
            "geox_map_export_package",
        }
        discovery_tools = {
            "geox_system_registry_status",
            "geox_attribute_registry_list_tool",
            "geox_basin_resolve",
            "geox_query_intake",
            "geox_query_macrostrat",
        }
        evidence_tools = {
            "geox_data_ingest_bundle",
            "geox_data_qc_bundle",
            "geox_dst_ingest_test",
            "geox_header_inspect",
            "geox_las_inspect",
            "geox_seismic_segy_inspect",
            "geox_evidence_discover",
            "geox_evidence_attach",
            "geox_literature_ingest",
            "geox_fault_stick_ingest_tool",
            "geox_volume_frame_tool",
            "geox_vision_perceptual_inventory",
            "geox_vision_calibrate",
        }

        if tool_name in judgment_tools:
            return "judgment"
        if tool_name in discovery_tools:
            return "discovery"
        if tool_name in evidence_tools:
            return "evidence"
        return "reasoning"

    return "reasoning"  # default for unknown organs


def _resolve_actor_verified(session_id: str | None, actor_id: str | None = None) -> bool:
    """Single projection of actor_verified for organ kernel envelopes.

    FORGE-0A (2026-07-23): Never invent True from (actor_id and session_id)
    presence — that is the identity schism (wrapper True / standing False).

    Order:
      1. Session store / AuthorityState (canonical)
      2. Else False (unverified / anonymous / store miss)

    SCT claim ``av`` is authoritative only when already projected into the
    session store at arif_init / bind_identity. This reader does not parse
    tokens independently (would re-open multi-writer drift).
    """
    if not session_id or str(session_id).startswith("SES-IMPLICIT-"):
        return False
    # Prefer session identity map (set only at bind / arif_init)
    try:
        from arifosmcp.runtime.session import get_session_identity

        ident = get_session_identity(session_id)
        if isinstance(ident, dict):
            return bool(ident.get("actor_verified") or ident.get("verified"))
    except Exception:
        pass
    # AuthorityState / full session dict via tools.get_session
    try:
        from arifosmcp.runtime.tools import get_session

        sess = get_session(session_id)
        if isinstance(sess, dict):
            try:
                from arifosmcp.runtime.authority import read_authority_state

                state = read_authority_state(sess)
                return bool(state.actor.verified)
            except Exception:
                return bool(
                    sess.get("actor_verified")
                    or sess.get("signature_verified")
                    or sess.get("identity_verified")
                )
    except Exception:
        pass
    # File-store fallback (same paths as live_kernel)
    try:
        store_path = os.getenv("ARIFOS_SESSION_STORE_PATH", "/app/data/sessions.json")
        for p in (
            store_path,
            "/tmp/arifos/sessions.json",
            "/tmp/arifos/runtime_sessions.json",
            "/root/.local/share/arifos/sessions.json",
        ):
            if not os.path.exists(p):
                continue
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
            sessions = data.get("sessions", data) if isinstance(data, dict) else {}
            sess = sessions.get(session_id) if isinstance(sessions, dict) else None
            if isinstance(sess, dict):
                return bool(
                    sess.get("actor_verified")
                    or sess.get("signature_verified")
                    or sess.get("identity_verified")
                )
    except Exception:
        pass
    return False


def build_kernel_envelope(
    *,
    payload: dict[str, Any],
    organ_id: str,
    tool_name: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    lease_id: str | None = None,
    action_class: ActionClass = "OBSERVE",
    verdict: VerdictClass = "QUALIFY",
    mutation_allowed: bool = False,
    irreversible_allowed: bool = False,
    blast_radius: str = "LOW",
    reversibility_score: float = 1.0,
) -> dict[str, Any]:
    """
    Wrap an organ's universal output envelope inside the arifOS kernel envelope.

    This is THE AGI substrate contract. Every governed call through arifOS
    returns this wrapper, not raw organ output.

    Args:
        payload: The organ's universal output envelope (e.g., GEOX get_standard_envelope result)
        organ_id: Federation organ ID (GEOX, WEALTH, WELL)
        tool_name: Canonical tool name on the organ
        session_id: arifOS governed session ID
        actor_id: Authenticated actor ID
        lease_id: Authority lease ID (required for reasoning/judgment lanes)
        action_class: OBSERVE | ANALYZE | MUTATE | IRREVERSIBLE
        verdict: Constitutional verdict (SEAL | QUALIFY | HOLD | VOID | 888_HOLD)
        mutation_allowed: Whether the action may mutate state
        irreversible_allowed: Whether the action may be irreversible
        blast_radius: LOW | MEDIUM | HIGH | CRITICAL
        reversibility_score: 0.0 (irreversible) to 1.0 (fully reversible)

    Returns:
        Kernel envelope wrapping the organ payload with full authority context.
    """
    lane = get_lane_for_tool(organ_id, tool_name or "")
    lane_max_class = LANE_MAX_ACTION_CLASS.get(lane, "OBSERVE")
    requires_lease = LANE_REQUIRES_LEASE.get(lane, False)
    requires_session = LANE_REQUIRES_SESSION.get(lane, False)

    # FORGE-0A: never mint SES-IMPLICIT / LEASE-IMPLICIT identity fiction.
    # Missing session on a session-required lane stays None — caller sees
    # unbound envelope, not a fabricated verified-looking identity.
    if requires_lease and not lease_id:
        lease_id = None
    # do NOT invent session_id

    contract_version = ORGAN_CONTRACT_VERSIONS.get(organ_id, "unknown")
    organ_role = ORGAN_ROLES.get(organ_id, "unknown")
    actor_verified = _resolve_actor_verified(session_id, actor_id)

    envelope = {
        "kernel": {
            "kernel_id": "arifOS",
            "constitution_id": "arifos-constitution-v2026.05.05-SSCT",
            "constitution_hash": CONSTITUTION_HASH,
            "session_id": session_id,
            "actor_id": actor_id,
            # FORGE-0A: single projection from session store / AuthorityState.
            # Never bool(actor_id and session_id).
            "actor_verified": actor_verified,
            "sovereign": "ARIF_FAZIL",
            "epoch_id": "EPOCH-LIVE-1",
        },
        "authority": {
            "lease_id": lease_id,
            "action_class": action_class,
            "lane": lane,
            "lane_max_action_class": lane_max_class,
            "requires_lease": requires_lease,
            "requires_session": requires_session,
            "mutation_allowed": mutation_allowed,
            "irreversible_allowed": irreversible_allowed,
            "human_final_authority": "Arif",
        },
        "organ": {
            "organ_id": organ_id,
            "organ_role": organ_role,
            "organ_version": contract_version,
            "tool_name": tool_name,
            "domain_law": payload.get("domain_law", "NATURAL_LAW"),
            "physics_manifest_hash": payload.get(
                "physics_manifest_hash",
                payload.get("provenance", {}).get("physics_manifest_hash", ""),
            ),
        },
        "payload": payload,
        "verdict": verdict,
        "risk": {
            "reversibility_score": reversibility_score,
            "blast_radius": blast_radius,
            "secret_touching": False,
            "human_ack_required": action_class in ("MUTATE", "IRREVERSIBLE"),
        },
        "audit": {
            "vault_required": verdict == "SEAL",
            "audit_pointer": None,
            "seal_mode": "governed" if verdict == "SEAL" else "observe",
            "timestamp_utc": _now_iso(),
            "content_hash": _hash_payload(payload),
        },
        "delta_S": 0.0,
        "timestamp": _now_iso(),
    }

    return envelope


def wrap_geox_output(
    geox_envelope: dict[str, Any],
    *,
    tool_name: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    lease_id: str | None = None,
) -> dict[str, Any]:
    """
    Convenience wrapper: wrap a GEOX universal envelope inside the kernel envelope.

    Auto-detects action_class from the tool's lane classification.
    """
    lane = get_lane_for_tool(
        "GEOX", tool_name or geox_envelope.get("provenance", {}).get("tool_name", "unknown")
    )
    action_class = LANE_MAX_ACTION_CLASS.get(lane, "OBSERVE")

    claim_state = geox_envelope.get("claim_state", "INGESTED")
    execution_status = geox_envelope.get("execution_status", "SUCCESS")

    # Determine verdict from claim state
    verdict_map = {
        "SEALED": "SEAL",
        "QUALIFIED": "QUALIFY",
        "QC_VERIFIED": "QUALIFY",
        "888_HOLD": "HOLD",
        "VOID": "VOID",
        "NO_VALID_EVIDENCE": "HOLD",
    }
    verdict: VerdictClass = verdict_map.get(claim_state, "QUALIFY")

    # Downgrade on error
    if execution_status in ("ERROR", "HALT"):
        verdict = "HOLD"

    return build_kernel_envelope(
        payload=geox_envelope,
        organ_id="GEOX",
        tool_name=tool_name,
        session_id=session_id,
        actor_id=actor_id,
        lease_id=lease_id,
        action_class=action_class,
        verdict=verdict,
        mutation_allowed=False,
        irreversible_allowed=False,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Self-test
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Test: wrap a mock GEOX envelope
    mock_geox = {
        "execution_status": "SUCCESS",
        "tool_class": "compute",
        "claim_state": "INTERPRETED",
        "evidence_refs": ["ev-001"],
        "artifact_refs": ["art-001"],
        "domain_law": "NATURAL_LAW",
        "physics_manifest_hash": "sha256:test",
        "provenance": {"tool_name": "geox_basin_profile"},
        "audit_receipt": {},
    }

    wrapped = wrap_geox_output(
        mock_geox,
        tool_name="geox_basin_profile",
        session_id="SEAL-test-001",
        actor_id="test-agent",
        lease_id="LEASE-test-001",
    )

    assert wrapped["kernel"]["constitution_hash"].startswith("sha256:")
    assert wrapped["authority"]["action_class"] == "ANALYZE"
    assert wrapped["authority"]["lane"] == "reasoning"
    assert wrapped["organ"]["organ_id"] == "GEOX"
    assert wrapped["payload"] == mock_geox
    assert wrapped["verdict"] == "QUALIFY"

    print("✅ Kernel envelope tests pass")
    print(f"   Lane detection: {get_lane_for_tool('GEOX', 'geox_claim_seal')} → judgment")
    print(
        f"   Lane detection: {get_lane_for_tool('GEOX', 'geox_system_registry_status')} → discovery"
    )
    print(f"   Lane detection: {get_lane_for_tool('GEOX', 'geox_data_ingest_bundle')} → evidence")
    print(f"   Lane detection: {get_lane_for_tool('GEOX', 'geox_seismic_compute')} → reasoning")
