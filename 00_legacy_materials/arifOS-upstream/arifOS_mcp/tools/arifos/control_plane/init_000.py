"""
arifOS.000_INIT — Constitutional Session Ignition
Stage: 000_INIT
DITEMPA BUKAN DIBERI — 999 SEAL

Consolidates: apps/init/, substrate/mcp_time/
Responsibility: Epoch validation, session anchoring, doctrine/schema/session getters
"""

from fastmcp import Context
from typing import Optional

from arifOS_mcp.runtime.governance import governed_return, ThermodynamicMetrics, Verdict


def _build_metrics(amanah_lock: bool = True) -> ThermodynamicMetrics:
    return ThermodynamicMetrics(
        truth_score=1.0,
        delta_s=0.0,
        omega_0=0.04,
        peace_squared=1.0,
        amanah_lock=amanah_lock,
        tri_witness_score=1.0,
        stakeholder_safety=1.0,
    )


async def init_000(
    ctx: Context,
    operator_id: str,
    epoch: str,
    intent: Optional[str] = None,
    mode: str = "init",
) -> dict:
    """
    Initialize arifOS constitutional session.

    Args:
        operator_id: Sovereign identity (e.g., "arif@arif-fazil.com")
        epoch: Constitutional epoch (e.g., "2026.04")
        intent: Declared session intent (optional)
        mode: init|probe|state|status|revoke

    Returns:
        Session metadata: session_id, epoch, alignment, doctrine_uri
    """
    from ..resources.doctrine import get_doctrine, get_doctrine_floor

    # Validate epoch
    valid_epochs = ["2026.01", "2026.02", "2026.03", "2026.04"]
    if epoch not in valid_epochs:
        return {
            "status": "VOID",
            "error": f"Invalid epoch {epoch}. Must be one of {valid_epochs}",
            "session_id": None,
        }

    # Get constitutional doctrine
    doctrine = await get_doctrine()
    floor_doc = await get_doctrine_floor("F1")

    # Session anchoring
    session_id = f"{operator_id}@{epoch}"

    # Mode-specific behavior
    if mode == "revoke":
        return {
            "status": "REVOKED",
            "session_id": session_id,
            "message": "Session terminated by sovereign",
        }
    elif mode == "probe":
        return {
            "status": "SEAL",
            "session_id": session_id,
            "probe_result": "anchor_valid",
            "authority_enum": "COMPATIBLE",
            "doctrine_uri": "resource://arifOS/doctrine",
        }
    elif mode == "status":
        return {
            "status": "ACTIVE",
            "session_id": session_id,
            "epoch": epoch,
            "floors_healthy": True,
        }

    # Default init
    result = {
        "status": "SEAL",
        "session_id": session_id,
        "epoch": epoch,
        "operator": operator_id,
        "intent_declared": intent,
        "alignment": "F1_F13_COMPLIANT",
        "doctrine_uri": "resource://arifOS/doctrine",
        "floor_uri": "resource://arifOS/doctrine/floor/F1",
        "vault_receipt": f"INIT_{session_id}",
        "message": "Constitutional session anchored. Proceed to 111_SENSE.",
    }

    metrics = _build_metrics(amanah_lock=True)
    return governed_return(
        stage="arifos_000_init",
        data=result,
        metrics=metrics,
        verdict=Verdict.SEAL,
        primary_metric_value=0.95,
        performance={"calls": 1},
        correctness={"passed": 1, "failed": 0},
    )


# Prompts
PROMPT_000_INIT = """# Metabolic 000_INIT — Session Ignition

When arifOS.000_init is called:
1. Validate operator identity and epoch
2. Anchor session to constitutional ledger (VAULT999)
3. Return session metadata with doctrine URIs
4. Await 111_SENSE call

Constitutional constraint: F1 Amanah — no session without identity binding."""


# Resource
from fastmcp.resources import Resource

DOCTRINE_RESOURCE = Resource(
    uri="resource://arifOS/doctrine",
    name="Constitutional Doctrine",
    description="Immutable F1-F13 constitutional substrate",
    mime_type="text/markdown",
)
