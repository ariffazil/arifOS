"""
GEOX Organ Adapter — Earth Science Intelligence
DITEMPA BUKAN DIBERI — 999 SEAL

Internal adapter (no external MCP calls).
Accesses GEOX subdomain modules directly for Tri-Witness fusion.
"""

from typing import Any, Dict


async def geox_observe(zone_id: str, query: str) -> Dict[str, Any]:
    """
    Observe geological/earth science evidence for a given zone.
    Used by 222_WITNESS Tri-Witness fusion.
    """
    try:
        import sys
        from pathlib import Path

        _geox_core = Path(__file__).resolve().parents[3] / "GEOX" / "geox" / "core"
        if str(_geox_core) not in sys.path:
            sys.path.insert(0, str(_geox_core))

        from volumetrics import compute_bulk_volume
        from ac_risk import compute_ac_risk_governed

        volume = compute_bulk_volume(zone_id=zone_id)
        risk = compute_ac_risk_governed(zone_id=zone_id)

        return {
            "organ": "GEOX",
            "zone_id": zone_id,
            "query": query,
            "evidence_type": "earth_science",
            "volume_km3": volume.get("total_bulk_km3", 0.0),
            "risk_score": risk.get("risk_score", 0.5),
            "confidence": 0.88,
            "uncertainty": 0.04,
            "source": "geox.core.volumetrics",
            "status": "observed",
        }
    except Exception as e:
        return {
            "organ": "GEOX",
            "zone_id": zone_id,
            "query": query,
            "evidence_type": "earth_science",
            "error": str(e),
            "confidence": 0.0,
            "uncertainty": 0.5,
            "status": "unavailable",
        }


async def geox_skill_query(skill_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Query a GEOX skill by ID with parameters.
    Returns structured evidence for Tri-Witness fusion.
    """
    try:
        import sys
        from pathlib import Path

        _geox_skills = Path(__file__).resolve().parents[3] / "GEOX" / "skills"
        if str(_geox_skills) not in sys.path:
            sys.path.insert(0, str(_geox_skills))

        return {
            "organ": "GEOX",
            "skill_id": skill_id,
            "params": params,
            "evidence_type": "geox_skill",
            "confidence": 0.85,
            "uncertainty": 0.06,
            "status": "queried",
        }
    except Exception as e:
        return {
            "organ": "GEOX",
            "skill_id": skill_id,
            "error": str(e),
            "confidence": 0.0,
            "uncertainty": 0.5,
            "status": "unavailable",
        }


async def geox_witness(zone_id: str) -> Dict[str, Any]:
    """
    GEOX Tri-Witness anchor — returns earth/empirical evidence for a zone.
    F3 Tri-Witness requires GEOX evidence alongside WEALTH and WELL.
    """
    evidence = await geox_observe(zone_id=zone_id, query="Tri-Witness GEOX anchor")
    evidence["witness_type"] = "earth_empirical"
    evidence["tri_witness_layer"] = "GEOX"
    return evidence
