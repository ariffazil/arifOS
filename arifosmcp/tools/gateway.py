"""
arifosmcp/tools/gateway_connect.py — 666g_GATEWAY
═════════════════════════════════════════════════

Cross-agent routing (A2A) and federation hub.
"""

from __future__ import annotations

import json
import uuid
from typing import Any

from arifosmcp.runtime.law import check_laws
from arifosmcp.runtime.peer_contract import (
    PeerFederationContract,
    get_arifos_peer_contract_hash,
    get_arifos_peer_contract_url,
)
from arifosmcp.runtime.tools import _hold, _ok


def arif_gateway_connect(
    mode: str = "route",
    target_agent: str | None = None,
    actor_id: str | None = None,
    contract_url: str | None = None,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    floor_check = check_laws("arif_gateway_connect", {"target_agent": target_agent or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_gateway_connect", floor_check["reason"], floor_check["violated_laws"])

    if mode == "route":
        return _ok(
            "arif_gateway_connect",
            {"target": target_agent, "protocol": "A2A", "status": "routed"},
        )
    if mode == "discover":
        # P1-REPAIR-4: Include federation organs alongside external agents.
        # External agents: egress paths to third-party AI providers.
        # Federation organs: AAA (control plane), A-FORGE (execution), GEOX (earth),
        #   WEALTH (capital), WELL (vitality), APEX (apex logic).
        return _ok(
            "arif_gateway_connect",
            {
                "agents": [
                    # Federation organs (internal A2A mesh)
                    "AAA",
                    "A-FORGE",
                    "GEOX",
                    "WEALTH",
                    "WELL",
                    "APEX",
                    # External bridge agents
                    "kimi",
                    "claude",
                    "gemini",
                ],
                "protocol": "A2A",
                "note": "Federation organs exposed via internal A2A mesh; "
                "external agents via bridge protocol",
            },
        )
    if mode == "handshake":
        return _ok(
            "arif_gateway_connect",
            {
                "target": target_agent,
                "handshake": "OK",
                "capability_token": uuid.uuid4().hex[:16],
            },
        )
    if mode == "seal":
        return _ok(
            "arif_gateway_connect",
            {
                "target": target_agent,
                "seal": "cross-agent-SEAL",
                "status": "pending_888",
            },
        )

    if mode == "consensus":
        # F3 WITNESS: Cross-organ Tri-Witness consensus for proposed actions.
        # Delegates to tools/organ_consensus.py.
        # target_agent is used as the proposed_action description.
        try:
            from arifosmcp.tools.organ_consensus import arif_organ_consensus

            raw = arif_organ_consensus(
                proposed_action=target_agent or "unspecified",
                session_id=None,
                actor_id=actor_id,
            )
            # arif_organ_consensus is async — handle both sync/async returns
            import asyncio

            if asyncio.iscoroutine(raw):
                try:
                    loop = asyncio.get_event_loop()
                    raw = loop.run_until_complete(raw)
                except RuntimeError:
                    raw = {"status": "async_context_required"}
            return _ok(
                "arif_gateway_connect",
                raw if isinstance(raw, dict) else {"result": str(raw)},
            )
        except Exception as exc:
            return _hold("arif_gateway_connect", f"consensus probe failed: {exc}")

    if mode == "peer_contract":
        # P2P Federation Contract v1 discovery/validation.
        # If a remote contract is supplied, validate it; otherwise advertise
        # arifOS's own contract for peer negotiation.
        if contract_url or contract:
            try:
                if contract is None and contract_url:
                    import urllib.request

                    with urllib.request.urlopen(contract_url, timeout=10) as resp:
                        contract = json.loads(resp.read().decode("utf-8"))
                validated = PeerFederationContract.model_validate(
                    contract if contract is not None else {}
                )
                return _ok(
                    "arif_gateway_connect",
                    {
                        "protocol": "P2P",
                        "mode": "peer_contract_validate",
                        "organ": validated.peer_id.organ,
                        "authority_class": validated.authority_class.value,
                        "contract_version": validated.contract_version,
                        "valid": True,
                    },
                )
            except Exception as exc:
                return _hold(
                    "arif_gateway_connect",
                    f"peer_contract validation failed: {exc}",
                )

        return _ok(
            "arif_gateway_connect",
            {
                "protocol": "P2P",
                "mode": "peer_contract_attest",
                "peer_contract_url": get_arifos_peer_contract_url(),
                "peer_contract_hash": get_arifos_peer_contract_hash(),
                "authority_class": "judge",
                "note": "arifOS peer contract available for P2P negotiation.",
            },
        )

    return _hold("arif_gateway_connect", f"Unknown mode: {mode}")
