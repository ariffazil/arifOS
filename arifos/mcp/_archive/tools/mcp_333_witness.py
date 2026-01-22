"""
333_WITNESS: Tri-Witness Collection & Signature.

A tool for independent observers to sign off on pending actions.
Implements F3 (Tri-Witness Consensus) + F6 (Ijma / Consensus).

When a high-risk action (666_act, resource deletion, etc.) is queued,
observers can inspect the request and sign with their own authority.

DITEMPA BUKAN DIBERI - Forged v50.4
"""

from datetime import datetime
from typing import Any, Dict

from arifos.core.governance.authority import Authority


async def mcp_333_witness(
    args: Dict[str, Any],
    authority: Authority = None,
    vault_manager: Any = None,
) -> Dict[str, Any]:
    """
    Sign a pending execution request.

    Args:
        witness_request_id: UUID of the pending action (from 666_act).
        approval: True (sign) or False (reject).

    Returns:
        Signed attestation, indexed in Vault.
    """

    # Legacy fallback
    if authority is None:
        return {"isError": True, "content": [{"type": "text", "text": "Authority required for witnessing."}]}

    witness_request_id = args.get("witness_request_id")
    approval = args.get("approval", False)
    reason = args.get("reason", "")

    if not witness_request_id:
        return {"isError": True, "content": [{"type": "text", "text": "Missing witness_request_id."}]}

    # Look up the pending request (Mocked for now as we haven't implemented Vault Pending queue in Phase 1a)
    # pending = vault_manager.get_pending_execution(witness_request_id)

    # Step 1: Verify this witness has authority to review (at least F3).
    if "F3" not in authority.scope_floors and "F6" not in authority.scope_floors:
        return {
            "isError": True,
            "content": [{
                "type": "text",
                "text": f"△{authority.agent_id} lacks F3/F6 to serve as witness."
            }]
        }

    # Step 2: Create attestation signature
    # In Phase 1a, we create a mocked signature since Vault extensions are in Phase 1b
    attestation = {
        "witness_id": authority.agent_id,
        "witness_authority_hash": authority.covenant_hash,
        "request_id": witness_request_id,
        "approval": approval,
        "reason": reason,
        "timestamp": datetime.now().isoformat(),
        # "signature": ...
    }

    # Step 3: Record attestation to Vault (F3 + F6 consensus building)
    # vault_manager.record_attestation(witness_request_id, attestation)

    # Step 4: Check if we've reached tri-witness threshold (Mocked)
    # attestations = vault_manager.get_attestations_for_request(witness_request_id)
    # approvals = [a for a in attestations if a["approval"]]

    approvals_count = 1 if approval else 0 # Simple mock
    threshold = 2

    if approvals_count >= threshold:
        # Threshold reached! Execute the pending action.
        # result = vault_manager.execute_pending_request(witness_request_id)
        result = "EXECUTED_MOCK"
        return {
            "isError": False,
            "content": [{
                "type": "text",
                "text": f"Tri-witness consensus achieved ({approvals_count}/{threshold}). Pending action executed. Result: {result}"
            }],
            "meta": {
                "status": "EXECUTED",
                "attestations": approvals_count,
                "result": result,
            }
        }
    else:
        return {
            "isError": False,
            "content": [{
                "type": "text",
                "text": f"Attestation recorded. Progress: {approvals_count}/{threshold} approvals. Awaiting more witnesses."
            }],
            "meta": {
                "status": "PENDING_MORE_WITNESSES",
                "approvals_so_far": approvals_count,
                "remaining": threshold - approvals_count,
            }
        }
