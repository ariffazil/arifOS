"""
arifosmcp/tools/judge_deliberate.py — 888_JUDGE
═══════════════════════════════════════════════

Constitutional verdict engine.

Evidence pre-loading: vitals and heart output are piped into the judge
before adjudication so epistemic confidence is grounded in actual system state.

Post-SEAL auto-hook: When verdict is SEAL and vault_entry_id is provided,
the judge output is automatically routed to arif_vault_seal for immutable anchoring.
"""

from __future__ import annotations

import json as json_lib

from arifosmcp.runtime.tools import _arif_judge_deliberate
from arifosmcp.schemas.verdict import VerdictOutput


def arif_judge_deliberate(
    mode: str = "judge",
    candidate: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    vault_entry_id: str | None = None,
) -> VerdictOutput:
    """
    888_JUDGE: Constitutional adjudication and verdict emission.

    Args:
        vault_entry_id: If provided and verdict is SEAL, the output is
            automatically routed to arif_vault_seal for immutable anchoring
            (post-SEAL auto-hook per P3).
    """
    from arifosmcp.tools.ops import arif_ops_measure

    _evidence: dict = {}

    if mode != "history":
        if _evidence.get("vitals") is None:
            try:
                vitals_result = arif_ops_measure(mode="vitals")
                _evidence["vitals"] = getattr(vitals_result, "__dict__", {}) or {
                    "status": "unavailable"
                }
            except Exception:
                _evidence["vitals"] = {"status": "unavailable"}

    audit_entropy = _evidence.get("vitals", {}).get("audit_entropy")
    result = _arif_judge_deliberate(
        mode=mode,
        candidate=candidate,
        session_id=session_id,
        actor_id=actor_id,
        constitutional_chain_id=constitutional_chain_id,
        audit_entropy=audit_entropy,
        wealth_score=_evidence.get("wealth_score"),
        verification_surface=_evidence.get("verification_surface"),
    )

    verdict_str = str(result.get("verdict", ""))
    is_seal = "SEAL" in verdict_str

    if vault_entry_id and is_seal:
        try:
            from arifosmcp.tools.vault import arif_vault_seal

            payload_dict = {
                "tool": "arif_judge_deliberate",
                "candidate": candidate,
                "verdict": result.get("verdict", ""),
                "constitutional_chain_id": result.get("meta", {}).get("constitutional_chain_id"),
                "state_hash": result.get("meta", {}).get("state_hash"),
            }

            seal_result = arif_vault_seal(
                mode="seal",
                payload=json_lib.dumps(payload_dict),
                session_id=session_id,
                actor_id=actor_id,
                constitutional_chain_id=constitutional_chain_id,
                judge_state_hash=result.get("meta", {}).get("state_hash"),
            )
            if "meta" not in result:
                result["meta"] = {}
            result["meta"]["vault_sealed"] = True
            result["meta"]["vault_entry_id"] = getattr(seal_result, "entry_id", vault_entry_id)
        except Exception:
            if "meta" not in result:
                result["meta"] = {}
            result["meta"]["vault_sealed"] = False

    return VerdictOutput(**result)
