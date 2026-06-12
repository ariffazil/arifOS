"""
RCA Gateway MCP Tools — Accident Report Litigation Hold operations.
══════════════════════════════════════════════════════════════

MCP tools that operate on the state machine, report versions, and Merkle log.
All mutations emit receipts and update the Merkle tree.
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from typing import Any

from .merkle_log import MerkleTree, canonical_bytes
from .state_machine import (
    ActionType,
    Audience,
    DisclosureReceipt,
    Incident,
    IncidentState,
    IncidentStore,
    ReasonCode,
    ReportVersion,
    ReviewAction,
)


def handle_rca_tool(
    tool_name: str,
    arguments: dict[str, Any],
    store: IncidentStore,
    merkle: MerkleTree,
) -> dict[str, Any]:
    """Route an RCA tool call to the appropriate handler."""

    handlers: dict[str, Any] = {
        "incident.create": _incident_create,
        "incident.get": _incident_get,
        "incident.list": _incident_list,
        "report.submit": _report_submit,
        "report.get_version": _report_get_version,
        "litigation.mark_active": _litigation_mark_active,
        "review.start": _review_start,
        "review.complete": _review_complete,
        "review.escalate": _review_escalate,
        "override.sign": _override_sign,
        "disclosure.publish": _disclosure_publish,
        "timeline.get": _timeline_get,
        "gateway.rca_health": _rca_health,
    }

    handler = handlers.get(tool_name)
    if handler is None:
        return {"error": f"Unknown RCA tool: {tool_name}"}

    try:
        return handler(arguments, store, merkle)
    except Exception as exc:
        return {"error": f"Tool error: {str(exc)}"}


# ═══════════════════════════════════════════════════════════════════════════
# INCIDENT TOOLS
# ═══════════════════════════════════════════════════════════════════════════


def _incident_create(
    args: dict, store: IncidentStore, merkle: MerkleTree
) -> dict[str, Any]:
    incident = Incident(
        incident_id=args.get("incident_id", f"INC-{uuid.uuid4().hex[:12].upper()}"),
        title=args["title"],
        occurred_at=args["occurred_at"],
        jurisdiction=args.get("jurisdiction", "federal"),
        affected_parties=args.get("affected_parties", []),
        infrastructure_type=args.get("infrastructure_type", "pipeline"),
        operator_entity=args.get("operator_entity", ""),
    )
    store.create(incident)
    leaf_idx = merkle.append_canonical({
        "action": "incident.create",
        "incident_id": incident.incident_id,
        "title": incident.title,
        "timestamp": time.time(),
    })
    return {
        "status": "CREATED",
        "incident": incident.to_dict(),
        "merkle_leaf_index": leaf_idx,
    }


def _incident_get(
    args: dict, store: IncidentStore, merkle: MerkleTree
) -> dict[str, Any]:
    incident = store.get(args["incident_id"])
    if not incident:
        return {"error": f"Incident not found: {args['incident_id']}"}
    return {"incident": incident.to_dict()}


def _incident_list(
    args: dict, store: IncidentStore, merkle: MerkleTree
) -> dict[str, Any]:
    state_filter = args.get("state")
    if state_filter:
        incidents = store.list_by_state(IncidentState(state_filter))
    else:
        incidents = store.list_all()
    return {"count": len(incidents), "incidents": [i.to_dict() for i in incidents]}


# ═══════════════════════════════════════════════════════════════════════════
# REPORT TOOLS
# ═══════════════════════════════════════════════════════════════════════════


def _report_submit(
    args: dict, store: IncidentStore, merkle: MerkleTree
) -> dict[str, Any]:
    incident = store.get(args["incident_id"])
    if not incident:
        return {"error": f"Incident not found: {args['incident_id']}"}

    if incident.state != IncidentState.REPORT_DRAFTED:
        incident.transition(IncidentState.REPORT_DRAFTED, args.get("actor", "system"))

    content = args.get("content", "")
    content_hash = hashlib.sha256(content.encode()).hexdigest()

    version = ReportVersion(
        report_id=f"RPT-{incident.incident_id}",
        incident_id=incident.incident_id,
        version_id=args.get("version_id", "v1.0"),
        parent_version_id=args.get("parent_version_id"),
        hash=f"sha256:{content_hash}",
        created_at=time.time(),
        created_by_role=args.get("actor_role", "independent_committee"),
        classification=args.get("classification", "CONFIDENTIAL"),
        content_uri=args.get("content_uri", ""),
    )

    incident.seal_version(version)
    ok, detail = incident.transition(IncidentState.REPORT_SUBMITTED, args.get("actor", "system"))

    leaf_idx = merkle.append_canonical({
        "action": "report.submit",
        "incident_id": incident.incident_id,
        "version_id": version.version_id,
        "hash": version.hash,
        "actor_role": version.created_by_role,
        "timestamp": time.time(),
    })

    return {
        "status": "SUBMITTED" if ok else "TRANSITION_FAILED",
        "detail": detail,
        "version": version.to_dict(),
        "merkle_leaf_index": leaf_idx,
    }


def _report_get_version(
    args: dict, store: IncidentStore, merkle: MerkleTree
) -> dict[str, Any]:
    incident = store.get(args["incident_id"])
    if not incident:
        return {"error": f"Incident not found: {args['incident_id']}"}
    version_id = args.get("version_id", "v1.0")
    for v in incident.versions:
        if v.version_id == version_id:
            return {"version": v.to_dict()}
    return {"error": f"Version not found: {version_id}"}


# ═══════════════════════════════════════════════════════════════════════════
# LITIGATION TOOLS
# ═══════════════════════════════════════════════════════════════════════════


def _litigation_mark_active(
    args: dict, store: IncidentStore, merkle: MerkleTree
) -> dict[str, Any]:
    incident = store.get(args["incident_id"])
    if not incident:
        return {"error": f"Incident not found: {args['incident_id']}"}

    if incident.state != IncidentState.REPORT_SUBMITTED:
        return {"error": f"Incident must be in REPORT_SUBMITTED, but is {incident.state.value}"}

    incident.litigation_refs = args.get("litigation_refs", [])
    ok, detail = incident.transition(IncidentState.LITIGATION_ACTIVE, args.get("actor", "system"))

    leaf_idx = merkle.append_canonical({
        "action": "litigation.mark_active",
        "incident_id": incident.incident_id,
        "litigation_refs": incident.litigation_refs,
        "timestamp": time.time(),
    })

    return {
        "status": "LITIGATION_ACTIVE" if ok else "TRANSITION_FAILED",
        "detail": detail,
        "merkle_leaf_index": leaf_idx,
    }


# ═══════════════════════════════════════════════════════════════════════════
# REVIEW TOOLS
# ═══════════════════════════════════════════════════════════════════════════


def _review_start(
    args: dict, store: IncidentStore, merkle: MerkleTree
) -> dict[str, Any]:
    incident = store.get(args["incident_id"])
    if not incident:
        return {"error": f"Incident not found: {args['incident_id']}"}

    ok, detail = incident.transition(IncidentState.LEGAL_REVIEW, args.get("actor", "system"))
    if not ok:
        return {"status": "TRANSITION_FAILED", "detail": detail}

    review = ReviewAction(
        action_id=f"REV-{uuid.uuid4().hex[:8].upper()}",
        report_id=f"RPT-{incident.incident_id}",
        version_id="v1.0",
        actor_role=args.get("actor_role", "agc"),
        action_type=ActionType.REVIEW_START,
        reason_code=ReasonCode.LITIGATION_RISK,
        legal_basis=args.get("legal_basis", ""),
        started_at=time.time(),
        deadline_at=incident.review_deadline_at,
    )
    incident.add_review_action(review)

    leaf_idx = merkle.append_canonical(review.to_dict())

    return {
        "status": "LEGAL_REVIEW",
        "review": review.to_dict(),
        "merkle_leaf_index": leaf_idx,
    }


def _review_complete(
    args: dict, store: IncidentStore, merkle: MerkleTree
) -> dict[str, Any]:
    incident = store.get(args["incident_id"])
    if not incident:
        return {"error": f"Incident not found: {args['incident_id']}"}

    ok, detail = incident.transition(IncidentState.REVIEW_COMPLETE, args.get("actor", "system"))

    leaf_idx = merkle.append_canonical({
        "action": "review.complete",
        "incident_id": incident.incident_id,
        "actor": args.get("actor", "system"),
        "timestamp": time.time(),
    })

    return {
        "status": "REVIEW_COMPLETE" if ok else "TRANSITION_FAILED",
        "detail": detail,
        "merkle_leaf_index": leaf_idx,
    }


def _review_escalate(
    args: dict, store: IncidentStore, merkle: MerkleTree
) -> dict[str, Any]:
    incident = store.get(args["incident_id"])
    if not incident:
        return {"error": f"Incident not found: {args['incident_id']}"}

    if incident.state != IncidentState.LEGAL_REVIEW:
        return {"error": f"Incident must be in LEGAL_REVIEW, but is {incident.state.value}"}

    ok, detail = incident.transition(IncidentState.REVIEW_STALLED, "auto-escalation")

    leaf_idx = merkle.append_canonical({
        "action": "review.escalate",
        "incident_id": incident.incident_id,
        "reason": "DEADLINE_BREACH",
        "timestamp": time.time(),
    })

    return {
        "status": "REVIEW_STALLED" if ok else "TRANSITION_FAILED",
        "detail": detail,
        "merkle_leaf_index": leaf_idx,
    }


# ═══════════════════════════════════════════════════════════════════════════
# SOVEREIGN OVERRIDE
# ═══════════════════════════════════════════════════════════════════════════


def _override_sign(
    args: dict, store: IncidentStore, merkle: MerkleTree
) -> dict[str, Any]:
    incident = store.get(args["incident_id"])
    if not incident:
        return {"error": f"Incident not found: {args['incident_id']}"}

    if incident.state not in {IncidentState.REVIEW_STALLED}:
        return {"error": f"Override requires REVIEW_STALLED, but is {incident.state.value}"}

    ok, detail = incident.transition(IncidentState.SOVEREIGN_OVERRIDE, args.get("actor", "sovereign"))

    leaf_idx = merkle.append_canonical({
        "action": "override.sign",
        "incident_id": incident.incident_id,
        "actor": args.get("actor", "sovereign"),
        "directive": args.get("directive", "APPROVE_DISCLOSURE"),
        "timestamp": time.time(),
    })

    return {
        "status": "SOVEREIGN_OVERRIDE" if ok else "TRANSITION_FAILED",
        "detail": detail,
        "merkle_leaf_index": leaf_idx,
    }


# ═══════════════════════════════════════════════════════════════════════════
# DISCLOSURE
# ═══════════════════════════════════════════════════════════════════════════


def _disclosure_publish(
    args: dict, store: IncidentStore, merkle: MerkleTree
) -> dict[str, Any]:
    incident = store.get(args["incident_id"])
    if not incident:
        return {"error": f"Incident not found: {args['incident_id']}"}

    valid_states = {
        IncidentState.NO_LITIGATION,
        IncidentState.REVIEW_COMPLETE,
        IncidentState.REVIEW_STALLED,
        IncidentState.SOVEREIGN_OVERRIDE,
    }
    if incident.state not in valid_states:
        return {"error": f"Cannot disclose from state {incident.state.value}"}

    ok, detail = incident.transition(IncidentState.DISCLOSED, args.get("actor", "system"))

    receipt = DisclosureReceipt(
        receipt_id=f"RCPT-DISC-{uuid.uuid4().hex[:12].upper()}",
        report_id=f"RPT-{incident.incident_id}",
        disclosed_version_id=args.get("version_id", "v1.0"),
        audience=Audience(args.get("audience", "PUBLIC")),
        redaction_log_hash=args.get("redaction_log_hash", hashlib.sha256(b"").hexdigest()),
        signed_by_role=args.get("actor_role", "sovereign"),
    )
    incident.add_disclosure(receipt)

    leaf_idx = merkle.append_canonical(receipt.to_dict())

    return {
        "status": "DISCLOSED" if ok else "TRANSITION_FAILED",
        "detail": detail,
        "receipt": receipt.to_dict(),
        "merkle_leaf_index": leaf_idx,
    }


# ═══════════════════════════════════════════════════════════════════════════
# TIMELINE
# ═══════════════════════════════════════════════════════════════════════════


def _timeline_get(
    args: dict, store: IncidentStore, merkle: MerkleTree
) -> dict[str, Any]:
    incident = store.get(args["incident_id"])
    if not incident:
        return {"error": f"Incident not found: {args['incident_id']}"}
    return {
        "incident_id": incident.incident_id,
        "current_state": incident.state.value,
        "transitions": incident.transitions,
        "review_actions": [a.to_dict() for a in incident.review_actions],
        "versions": [v.to_dict() for v in incident.versions],
        "disclosure_receipts": [r.to_dict() for r in incident.disclosure_receipts],
    }


def _rca_health(
    args: dict, store: IncidentStore, merkle: MerkleTree
) -> dict[str, Any]:
    stalled = store.list_by_state(IncidentState.REVIEW_STALLED)
    return {
        "status": "healthy",
        "total_incidents": len(store.list_all()),
        "stalled_reviews": len(stalled),
        "merkle_tree_size": merkle.tree_size,
        "merkle_root": merkle.root_hash.hex() if merkle.root_hash else None,
    }
