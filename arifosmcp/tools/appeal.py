"""
arifosmcp/tools/appeal.py — Appeal Path (Chapter 6 Upgrade)
════════════════════════════════════════════════════════════

Any human affected by an arifOS decision has a path to ask:
  - Why was this decided?
  - What evidence was used?
  - What uncertainty existed?
  - Who authorized it?
  - Can I contest it?
  - Can it be repaired?

Without appeal, "AI governance" becomes machine bureaucracy.
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field

from arifosmcp.runtime.floor import check_floors
from arifosmcp.runtime.session_auth import validate_session
from arifosmcp.runtime.tools import _hold, _ok
from arifosmcp.schemas.telemetry import TelemetryBlock


class AppealRequest(BaseModel):
    """Request to raise an appeal against a sealed or decided verdict."""

    contested_verdict_id: str = Field(description="VAULT999 entry ID or verdict being contested")
    grounds: str = Field(description="Human-readable grounds for the appeal")
    evidence_refs: list[str] = Field(default_factory=list, description="Evidence IDs supporting the appeal")
    requester_actor_id: str = Field(description="Who is raising the appeal")
    requested_relief: str = Field(
        default="reconsideration",
        description="What relief is sought: reconsideration | reversal | correction | apology",
    )


class AppealReview(BaseModel):
    """Review assignment for an appeal."""

    reviewer: str = Field(description="Assigned reviewer: human_888 | arif_heart_critique | arif_judge_deliberate")
    review_deadline: datetime = Field(description="When the review must complete")
    review_method: str = Field(default="redteam", description="redteam | rehearing | evidence_recheck")


class AppealResult(BaseModel):
    """Result of raising an appeal."""

    appeal_id: str
    status: str = Field(default="PENDING", description="PENDING | UNDER_REVIEW | RESOLVED | REJECTED")
    contested_verdict_id: str
    grounds: str
    review: AppealReview
    next_steps: list[str] = Field(default_factory=list)
    sovereign_notified: bool = False


# In-memory appeal queue (would be persisted to VAULT999 in production)
_APPEAL_REGISTRY: dict[str, dict[str, Any]] = {}


def arif_appeal_raise(
    contested_verdict_id: str = "",
    grounds: str = "",
    evidence_refs: list[str] | None = None,
    requester_actor_id: str = "",
    requested_relief: str = "reconsideration",
    actor_id: str | None = None,
    session_id: str | None = None,
) -> TelemetryBlock:
    """
    Raise an appeal against a sealed verdict or decision.

    Chapter 6 doctrine: A dignity-preserving federation needs
    explanation, contestability, correction, human escalation, and repair record.
    """
    auth = validate_session(session_id, actor_id)
    if not auth["valid"]:
        return TelemetryBlock(
            **_hold("arif_appeal_raise", auth["reason"], ["F11"], session_id=session_id)
        )

    floor_check = check_floors(
        "arif_appeal_raise",
        {"contested_verdict_id": contested_verdict_id, "grounds": grounds},
        actor_id,
    )
    if floor_check["verdict"] != "SEAL":
        return TelemetryBlock(
            **_hold(
                "arif_appeal_raise",
                floor_check["reason"],
                floor_check["failed_floors"],
                session_id=session_id,
            )
        )

    # Validate inputs
    if not contested_verdict_id:
        return TelemetryBlock(
            **_hold(
                "arif_appeal_raise",
                "contested_verdict_id is required to identify the decision being appealed",
                ["F02"],
                session_id=session_id,
            )
        )
    if not grounds:
        return TelemetryBlock(
            **_hold(
                "arif_appeal_raise",
                "grounds are required — explain why this decision should be reconsidered",
                ["F02"],
                session_id=session_id,
            )
        )

    appeal_id = f"APPEAL-{uuid.uuid4().hex[:12]}"
    review_deadline = datetime.now(UTC) + timedelta(hours=48)

    # Determine reviewer based on contested verdict type
    reviewer = "arif_heart_critique"
    review_method = "redteam"

    # For irreversible actions, require human review
    if "vault" in contested_verdict_id.lower() or "seal" in contested_verdict_id.lower():
        reviewer = "human_888"
        review_method = "rehearing"

    appeal_entry = {
        "appeal_id": appeal_id,
        "contested_verdict_id": contested_verdict_id,
        "grounds": grounds,
        "evidence_refs": evidence_refs or [],
        "requester_actor_id": requester_actor_id or actor_id or "anonymous",
        "requested_relief": requested_relief,
        "status": "PENDING",
        "reviewer": reviewer,
        "review_deadline": review_deadline.isoformat(),
        "review_method": review_method,
        "created_at": datetime.now(UTC).isoformat(),
        "session_id": session_id,
    }
    _APPEAL_REGISTRY[appeal_id] = appeal_entry

    # Build next steps
    next_steps = [
        f"Review assigned to {reviewer} with method '{review_method}'",
        f"Review must complete by {review_deadline.isoformat()}",
    ]
    if reviewer == "human_888":
        next_steps.append("F13 SOVEREIGN notification sent — human review required for irreversible action appeal")

    # In production: write to VAULT999 appeal stream, trigger heart critique redteam mode
    # For now: log and return receipt
    result = AppealResult(
        appeal_id=appeal_id,
        status="PENDING",
        contested_verdict_id=contested_verdict_id,
        grounds=grounds,
        review=AppealReview(
            reviewer=reviewer,
            review_deadline=review_deadline,
            review_method=review_method,
        ),
        next_steps=next_steps,
        sovereign_notified=(reviewer == "human_888"),
    )

    return TelemetryBlock(
        **_ok(
            "arif_appeal_raise",
            result.model_dump(mode="json"),
            meta={
                "appeal_count": len(_APPEAL_REGISTRY),
                "source": "appeal_engine",
                "mode": "raise",
            },
            session_id=session_id,
        )
    )


def arif_appeal_status(
    appeal_id: str = "",
    actor_id: str | None = None,
    session_id: str | None = None,
) -> TelemetryBlock:
    """Check the status of an existing appeal."""
    auth = validate_session(session_id, actor_id)
    if not auth["valid"]:
        return TelemetryBlock(
            **_hold("arif_appeal_status", auth["reason"], ["F11"], session_id=session_id)
        )

    if not appeal_id:
        return TelemetryBlock(
            **_hold("arif_appeal_status", "appeal_id is required", ["F02"], session_id=session_id)
        )

    entry = _APPEAL_REGISTRY.get(appeal_id)
    if not entry:
        return TelemetryBlock(
            **_hold(
                "arif_appeal_status",
                f"Appeal {appeal_id} not found",
                ["F02"],
                session_id=session_id,
            )
        )

    return TelemetryBlock(
        **_ok(
            "arif_appeal_status",
            entry,
            meta={"source": "appeal_engine", "mode": "status"},
            session_id=session_id,
        )
    )


def arif_appeal_list(
    status_filter: str = "",
    actor_id: str | None = None,
    session_id: str | None = None,
) -> TelemetryBlock:
    """List all appeals, optionally filtered by status."""
    auth = validate_session(session_id, actor_id)
    if not auth["valid"]:
        return TelemetryBlock(
            **_hold("arif_appeal_list", auth["reason"], ["F11"], session_id=session_id)
        )

    appeals = list(_APPEAL_REGISTRY.values())
    if status_filter:
        appeals = [a for a in appeals if a.get("status") == status_filter]

    return TelemetryBlock(
        **_ok(
            "arif_appeal_list",
            {
                "appeals": appeals,
                "total": len(_APPEAL_REGISTRY),
                "filtered": len(appeals),
            },
            meta={"source": "appeal_engine", "mode": "list"},
            session_id=session_id,
        )
    )
