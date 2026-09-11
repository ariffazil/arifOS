#!/usr/bin/env python3
"""
SRO Propagation — Cross-agent reality sharing via A2A gateway.

When an SRO is created, superseded, or calibrated, this module notifies
all federation agents via the AAA A2A gateway.

Usage:
  from arifosmcp.memory.sro_propagation import propagate_sro_event

  propagate_sro_event(
      event_type="SRO_CREATED",
      agent_id="hermes-asi",
      claim_id="wo-MY-FISCAL-2026-DSR",
      payload={"jurisdiction": "Malaysia federal", "confidence": 0.88}
  )

F1 AMANAH: Non-destructive. Notifications are fire-and-forget.
F2 TRUTH: Every event carries provenance.
F11 AUDIT: Every propagation logged.

DITEMPA BUKAN DIBERI ⚒️
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# A2A gateway endpoint
AAA_A2A_URL = os.getenv("AAA_A2A_URL", "http://127.0.0.1:3001/a2a")

# Propagation log
PROPAGATION_LOG = Path("/root/.local/share/arifos/sro_propagation_log.jsonl")

# Federation agents to notify (all except self)
FEDERATION_AGENTS = [
    "hermes-asi",
    "333-AGI",
    "555-ASI",
    "888-APEX",
    "geox",
    "wealth",
    "well",
]


def propagate_sro_event(
    event_type: str,
    agent_id: str,
    claim_id: str,
    payload: dict[str, Any] | None = None,
    target_agents: list[str] | None = None,
) -> dict[str, Any]:
    """Propagate an SRO event to federation agents via A2A gateway.

    Args:
        event_type: SRO_CREATED, SRO_SUPERSEDED, or SRO_CALIBRATED
        agent_id: Agent that created/modified the SRO
        claim_id: SRO claim ID (wo-*)
        payload: Event-specific data
        target_agents: Override target list (default: all federation agents)

    Returns:
        Propagation receipt with event_id, targets, and status
    """
    event_id = f"sro-{uuid.uuid4().hex[:12]}"
    timestamp = datetime.now(UTC).isoformat()
    targets = target_agents or FEDERATION_AGENTS

    # Build event message
    message = _build_event_message(event_type, agent_id, claim_id, payload, timestamp)

    # Propagate to each target
    results = {}
    for target in targets:
        if target == agent_id:
            continue  # don't notify self
        try:
            result = _send_a2a(target, message, event_id, agent_id)
            results[target] = result
        except Exception as e:
            results[target] = {"status": "error", "error": str(e)}

    # Build receipt
    receipt = {
        "event_id": event_id,
        "event_type": event_type,
        "agent_id": agent_id,
        "claim_id": claim_id,
        "timestamp": timestamp,
        "targets": list(results.keys()),
        "results": results,
        "success_count": sum(1 for r in results.values() if r.get("status") != "error"),
        "total_count": len(results),
    }

    # Log propagation
    _log_propagation(receipt)

    return receipt


def _build_event_message(
    event_type: str,
    agent_id: str,
    claim_id: str,
    payload: dict[str, Any] | None,
    timestamp: str,
) -> str:
    """Build the A2A message for an SRO event."""
    parts = [
        f"[SRO_EVENT] {event_type}",
        f"Agent: {agent_id}",
        f"Claim: {claim_id}",
        f"Time: {timestamp}",
    ]

    if payload:
        if payload.get("jurisdiction"):
            parts.append(f"Jurisdiction: {payload['jurisdiction']}")
        if payload.get("truth_class"):
            parts.append(f"Truth class: {payload['truth_class']}")
        if payload.get("confidence") is not None:
            parts.append(f"Confidence: {payload['confidence']}")
        if payload.get("expires_at"):
            parts.append(f"Expires: {payload['expires_at']}")
        if payload.get("reason"):
            parts.append(f"Reason: {payload['reason']}")
        if payload.get("new_claim_id"):
            parts.append(f"New claim: {payload['new_claim_id']}")
        if payload.get("outcome") is not None:
            parts.append(f"Outcome: {payload['outcome']}")
        if payload.get("calibration_error") is not None:
            parts.append(f"Calibration error: {payload['calibration_error']}")

    parts.append(
        f"\nAction: Store this SRO event in your local memory for cross-agent reality sharing."
    )

    return "\n".join(parts)


def _send_a2a(
    target: str, message: str, event_id: str, agent_id: str = "333-AGI"
) -> dict[str, Any]:
    """Send an A2A message to a target agent."""
    import urllib.error
    import urllib.request

    # Include session token for A2A gateway authentication
    # A2A SDK expects token in metadata, not Authorization header
    session_token = os.environ.get("ARIFOS_SESSION_TOKEN", "")

    metadata = {
        "source": "sro-propagation",
        "event_id": event_id,
        "timestamp": datetime.now(UTC).isoformat(),
        # Use the originating agent_id (must be registered in AAA)
        "agent_id": agent_id,
    }
    if session_token:
        metadata["session_token"] = session_token
        metadata["act"] = session_token
        metadata["sct"] = session_token

    # A2A gateway requires session_id in params (F4 CLARITY / lineage)
    session_id = os.environ.get("ARIFOS_SESSION_ID", f"sro-prop-{uuid.uuid4().hex[:8]}")

    payload = {
        "jsonrpc": "2.0",
        "id": event_id,
        "method": "tasks/send",
        "params": {
            "id": event_id,
            "sessionId": session_id,
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": message}],
            },
            "metadata": metadata,
        },
    }

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        AAA_A2A_URL,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "A2A-Version": "1.0",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return {"status": "sent", "response": result}
    except urllib.error.URLError as e:
        return {"status": "error", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _log_propagation(receipt: dict[str, Any]) -> None:
    """Log propagation receipt."""
    PROPAGATION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PROPAGATION_LOG, "a") as f:
        f.write(json.dumps(receipt, default=str) + "\n")


# Convenience functions for specific event types
def propagate_created(agent_id: str, claim_id: str, **kwargs) -> dict[str, Any]:
    """Propagate SRO_CREATED event."""
    return propagate_sro_event("SRO_CREATED", agent_id, claim_id, kwargs)


def propagate_superseded(
    agent_id: str,
    old_claim_id: str,
    new_claim_id: str,
    reason: str,
    **kwargs,
) -> dict[str, Any]:
    """Propagate SRO_SUPERSEDED event."""
    payload = {"new_claim_id": new_claim_id, "reason": reason, **kwargs}
    return propagate_sro_event("SRO_SUPERSEDED", agent_id, old_claim_id, payload)


def propagate_calibrated(
    agent_id: str,
    claim_id: str,
    outcome: bool,
    calibration_error: float,
    **kwargs,
) -> dict[str, Any]:
    """Propagate SRO_CALIBRATED event."""
    payload = {"outcome": outcome, "calibration_error": calibration_error, **kwargs}
    return propagate_sro_event("SRO_CALIBRATED", agent_id, claim_id, payload)
