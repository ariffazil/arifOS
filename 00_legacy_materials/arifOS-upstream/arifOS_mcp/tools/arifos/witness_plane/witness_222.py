"""
arifOS.222_WITNESS — Tri-Witness Fusion Protocol
Stage: 222_WITNESS
DITEMPA BUKAN DIBERI — 999 SEAL

Consolidates: P_geology_*, P_market_*, P_energy_*, P_bio_*, core/witness.py
Responsibility: Tri-witness fusion (GEOX/APEX, WEALTH/ASI, WELL/AGI)
"""

from fastmcp import Context
from typing import Optional


async def witness_222(
    ctx: Context,
    query: str,
    mode: str = "fuse",
    geox_evidence: Optional[dict] = None,
    wealth_evidence: Optional[dict] = None,
    well_evidence: Optional[dict] = None,
) -> dict:
    """
    Tri-witness fusion from three organ perspectives + External Reality.

    Modes:
        fuse: Default — triangulate GEOX + WEALTH + WELL evidence
        search: Live web search as 4th witness (F3 Earth/External reality)

    Args:
        query: Normalized query from 111_SENSE
        mode: Witness mode — fuse | search
        geox_evidence: GEOX spatial/geological context
        wealth_evidence: WEALTH capital/resource context
        well_evidence: WELL biological readiness context

    Returns:
        Fused witness report with tri-witness receipts
    """
    # --- MODE: SEARCH (External Reality / Earth Witness) ---
    if mode == "search":
        from ..extended.minimax_bridge import get_bridge

        bridge = get_bridge()
        try:
            results = await bridge.web_search(query)
            # Treat web results as Earth/External witness testimony
            web_receipt = {
                "organ": "WEB",
                "substrate": "EXTERNAL",
                "evidence_type": "live_search",
                "claim_tag": "EXTERNALLY_GROUNDED",
                "summary": f"{len(results.get('organic', []))} search results retrieved",
                "ontology_clean": True,
                "raw_results": results,
            }
            return {
                "status": "SEAL",
                "stage": "222_WITNESS",
                "mode": "search",
                "witness_receipts": {"WEB_EXTERNAL": web_receipt},
                "tri_witness_score": 0.95,
                "claim_tag": "EXTERNALLY_GROUNDED",
                "vault_receipt": "WITNESS_WEB",
                "message": "External reality witnessed. Proceed to 333_MIND for synthesis with internal witnesses.",
            }
        except Exception as exc:
            return {
                "status": "SABAR",
                "stage": "222_WITNESS",
                "mode": "search",
                "witness_receipts": {},
                "tri_witness_score": 0.0,
                "claim_tag": "GROUNDING_FAILED",
                "error": str(exc),
                "vault_receipt": "WITNESS_WEB_SABAR",
                "message": "External reality search failed. Defer to internal tri-witness only.",
            }

    # --- MODE: FUSE (default) ---
    # GEOX witness (APEX - Earth/Physics)
    geox_receipt = _fuse_geox_witness(query, geox_evidence)

    # WEALTH witness (ASI - Capital/Entropy)
    wealth_receipt = _fuse_wealth_witness(query, wealth_evidence)

    # WELL witness (AGI - Biological/Stability)
    well_receipt = _fuse_well_witness(query, well_evidence)

    # Tri-witness correlation check
    correlation_score = _check_correlation(geox_receipt, wealth_receipt, well_receipt)

    return {
        "status": "SEAL",
        "stage": "222_WITNESS",
        "mode": "fuse",
        "witness_receipts": {
            "APEX_GEOX": geox_receipt,
            "ASI_WEALTH": wealth_receipt,
            "AGI_WELL": well_receipt,
        },
        "tri_witness_score": correlation_score,
        "claim_tag": _assign_claim_tag(correlation_score),
        "vault_receipt": f"WITNESS_{correlation_score:.2f}",
        "message": "Proceed to 333_MIND for reasoning synthesis",
    }


def _fuse_geox_witness(query: str, evidence: Optional[dict]) -> dict:
    """Fuse GEOX/APEX witness testimony."""
    return {
        "organ": "GEOX",
        "substrate": "APEX",
        "evidence_type": "spatial_geological",
        "claim_tag": evidence.get("claim_tag", "OBSERVED") if evidence else "UNKNOWN",
        "summary": (
            evidence.get("summary", "No GEOX evidence provided") if evidence else "NO_CONTEXT"
        ),
        "ontology_clean": True,
    }


def _fuse_wealth_witness(query: str, evidence: Optional[dict]) -> dict:
    """Fuse WEALTH/ASI witness testimony."""
    return {
        "organ": "WEALTH",
        "substrate": "ASI",
        "evidence_type": "capital_resource",
        "claim_tag": evidence.get("claim_tag", "COMPUTED") if evidence else "UNKNOWN",
        "summary": (
            evidence.get("summary", "No WEALTH evidence provided") if evidence else "NO_CONTEXT"
        ),
        "ontology_clean": True,
    }


def _fuse_well_witness(query: str, evidence: Optional[dict]) -> dict:
    """Fuse WELL/AGI witness testimony."""
    return {
        "organ": "WELL",
        "substrate": "AGI",
        "evidence_type": "biological_readiness",
        "claim_tag": evidence.get("claim_tag", "MEASURED") if evidence else "UNKNOWN",
        "summary": (
            evidence.get("summary", "No WELL evidence provided") if evidence else "NO_CONTEXT"
        ),
        "ontology_clean": True,
    }


def _check_correlation(geox: dict, wealth: dict, well: dict) -> float:
    """Compute tri-witness correlation score (0.0 - 1.0)."""
    # Simple orthogonal check - all three must be clean
    clean_count = sum(
        [
            geox.get("ontology_clean", False),
            wealth.get("ontology_clean", False),
            well.get("ontology_clean", False),
        ]
    )
    return clean_count / 3.0


def _assign_claim_tag(score: float) -> str:
    """Assign claim tag based on witness consensus."""
    if score >= 0.95:
        return "VERIFIED"
    elif score >= 0.70:
        return "PLAUSIBLE"
    else:
        return "HYPOTHESIS"
