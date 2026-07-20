"""Decision-value scoring, activation, attribution, and decay for memory."""

from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from arifosmcp.schemas.memory_object import FutureValueBlock, MemoryAuthorityBlock

PROMOTION_THRESHOLD = 0.55
TEMPORARY_THRESHOLD = 0.30
_LOCK = threading.RLock()


def predicted_value(value: FutureValueBlock | dict[str, Any]) -> float:
    v = value if isinstance(value, FutureValueBlock) else FutureValueBlock.model_validate(value)
    score = (
        v.recurrence_probability
        * v.decision_impact
        * v.evidence_reliability
        * v.retrieval_specificity
        - v.maintenance_cost
        - v.privacy_risk
        - v.misapplication_risk
    )
    return round(max(-1.0, min(1.0, score)), 6)


def retrieval_value(value: FutureValueBlock | dict[str, Any]) -> float:
    v = value if isinstance(value, FutureValueBlock) else FutureValueBlock.model_validate(value)
    score = predicted_value(v) - v.staleness_risk - v.anchoring_risk - v.token_cost_normalized
    return round(max(-1.0, min(1.0, score)), 6)


def lifecycle_recommendation(
    value: FutureValueBlock | dict[str, Any],
    *,
    verified_useful_outcomes: int = 0,
    verified_harmful_outcomes: int = 0,
) -> str:
    score = predicted_value(value)
    if verified_harmful_outcomes > 0:
        return "revise"
    if score >= PROMOTION_THRESHOLD and verified_useful_outcomes > 0:
        return "eligible_for_promotion"
    if score >= TEMPORARY_THRESHOLD:
        return "temporary"
    return "do_not_promote"


def activation_changes(authority: MemoryAuthorityBlock | dict[str, Any]) -> dict[str, Any]:
    a = (
        authority
        if isinstance(authority, MemoryAuthorityBlock)
        else MemoryAuthorityBlock.model_validate(authority)
    )
    changes: dict[str, Any] = {"may_inform_reasoning": a.may_inform_reasoning}
    if a.may_change_routing:
        changes["routing_constraint"] = "memory_advisory"
    if a.may_restrict_tools:
        changes["tool_policy"] = "restrict_only"
    if a.may_lower_autonomy:
        changes["autonomy_direction"] = "lower_only"
    changes["authority_expansion_allowed"] = False
    return changes


def should_retrieve(value: FutureValueBlock | dict[str, Any]) -> bool:
    return retrieval_value(value) > 0.0


def decayed_confidence(confidence: float, months_elapsed: float, decay_per_month: float) -> float:
    return round(max(0.0, confidence - max(0.0, months_elapsed) * decay_per_month), 6)


def _events_path() -> Path:
    return Path(os.getenv("ARIFOS_MEMORY_VALUE_LEDGER", "/tmp/arifos/memory_value_events.jsonl"))


def _record(event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    event = {
        "event_id": f"mve-{uuid.uuid4().hex}",
        "event_type": event_type,
        "timestamp": datetime.now(UTC).isoformat(),
        **payload,
    }
    path = _events_path()
    with _LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
    return event


def record_retrieval(
    memory_id: str,
    decision_id: str,
    reason_selected: str,
    policy_changes: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _record(
        "memory_retrieved",
        {
            "memory_id": memory_id,
            "decision_id": decision_id,
            "reason_selected": reason_selected,
            "policy_changes": policy_changes or {},
        },
    )


def record_outcome(
    memory_id: str,
    decision_id: str,
    *,
    verified: bool,
    useful: bool,
    prevented_failure: bool = False,
    improved_route: bool = False,
    reduced_cost: bool = False,
    evidence_refs: list[str] | None = None,
) -> dict[str, Any]:
    if not verified or not evidence_refs:
        status = "UNVERIFIED"
    else:
        status = "USEFUL" if useful else "HARMFUL_OR_NO_VALUE"
    return _record(
        "memory_outcome",
        {
            "memory_id": memory_id,
            "decision_id": decision_id,
            "status": status,
            "effect": {
                "prevented_failure": prevented_failure,
                "improved_route": improved_route,
                "reduced_cost": reduced_cost,
            },
            "evidence_refs": evidence_refs or [],
        },
    )
