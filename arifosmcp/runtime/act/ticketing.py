"""
ACT ticketing — AAA human-in-loop ticket construction.

When ART issues HOLD, ACT constructs a standard approval ticket
for the AAA cockpit. The ticket carries everything a human needs
to decide: approve, modify, or abort.

DITEMPA BUKAN DIBERI — Tickets are forged, not configured.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal


TicketUrgency = Literal["routine", "elevated", "urgent", "critical"]


@dataclass
class ApprovalTicket:
    """Standard ACT approval ticket for AAA cockpit.

    Constructed when ART issues HOLD or ACT requires a human gate.
    """
    ticket_id: str
    plan_id: str
    task_ids: list[str] = field(default_factory=list)

    # What happened
    hold_reason: str = ""
    art_verdict: str = ""
    act_pattern_required: str = ""

    # Context
    tool_name: str = "unknown"
    blast_radius: str = "unknown"
    action_class: str = "unknown"
    is_reversible: bool = False
    compensation_available: bool = False

    # Evidence
    evidence_summary: str = ""
    well_readiness: str = "unknown"

    # Decision surface
    proposed_actions: list[str] = field(default_factory=list)
    default_if_silent: str = "HOLD"  # never auto-SEAL

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    urgency: TicketUrgency = "routine"


def create_hold_ticket(
    plan_id: str,
    hold_reason: str,
    tool_name: str = "unknown",
    action_class: str = "unknown",
    blast_radius: str = "unknown",
    is_reversible: bool = False,
    act_pattern_required: str = "HUMAN_IN_LOOP_CHANGE",
) -> ApprovalTicket:
    """Construct a standard HOLD ticket for AAA."""
    import uuid

    ticket_id = f"ticket_{uuid.uuid4().hex[:12]}"

    # Determine urgency
    urgency: TicketUrgency = "routine"
    if not is_reversible:
        urgency = "urgent"
    if blast_radius in ("high", "CIVILIZATIONAL", "INFRASTRUCTURE"):
        urgency = "critical"
    elif action_class in ("IRREVERSIBLE", "EXTERNAL_SIDE_EFFECT"):
        urgency = "elevated"

    return ApprovalTicket(
        ticket_id=ticket_id,
        plan_id=plan_id,
        hold_reason=hold_reason,
        art_verdict="HOLD",
        act_pattern_required=act_pattern_required,
        tool_name=tool_name,
        blast_radius=blast_radius,
        action_class=action_class,
        is_reversible=is_reversible,
        default_if_silent="HOLD",
        urgency=urgency,
        proposed_actions=[
            "Review HOLD reason and evidence",
            "Approve: lift HOLD, resume with pattern",
            "Modify: change plan parameters, re-submit",
            "Abort: mark plan ABORTED, log reason",
        ],
    )
