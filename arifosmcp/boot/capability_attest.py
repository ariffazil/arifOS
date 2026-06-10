"""
Capability Attestation — CAPABILITY_LEDGER (NATS)

DITEMPA BUKAN DIBERI — Forged, Not Given.

Read organ-attested tool capabilities.
Agent self-claims are inadmissible. Only organ-attested capabilities
count as authority.

Wire: NATS subject arifos.swarm.capability.{organ}
      + FORGE_REGISTRY.md (static fallback)
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ── Static capability baseline (FORGE_REGISTRY.md) ────────────────

_STATIC_CAPABILITIES: dict[str, dict[str, Any]] = {
    "arifOS": {
        "status": "DEGRADED_CLAIM",
        "attested_tools": [],
        "tool_count": 13,
        "note": "Static claim — live attestation via NATS not yet active. Capability is not permission.",
        "degraded": True,
    },
    "GEOX": {
        "status": "DEGRADED_CLAIM",
        "attested_tools": [],
        "tool_count": 31,
        "note": "Static claim — live attestation via NATS not yet active. Earth data organ, not authority.",
        "degraded": True,
    },
    "WEALTH": {
        "status": "DEGRADED_CLAIM",
        "attested_tools": [],
        "tool_count": 19,
        "note": "Static claim — live attestation via NATS not yet active. Tool count mismatch with repo (claims 38). Contract drift detected.",
        "degraded": True,
    },
    "WELL": {
        "status": "DEGRADED_CLAIM",
        "attested_tools": [],
        "tool_count": 14,
        "note": "Static claim — live attestation via NATS not yet active. REFLECT_ONLY organ.",
        "degraded": True,
    },
    "FORGE": {
        "status": "DEGRADED_CLAIM",
        "attested_tools": [],
        "tool_count": 0,
        "note": "A-FORGE execution shell — must never be sovereign. Muscle, not judge.",
        "degraded": True,
    },
    "GATEWAY": {
        "status": "DEGRADED_CLAIM",
        "attested_tools": [],
        "tool_count": 0,
        "note": "AAA/OpenClaw external IO boundary — all external calls require human gate.",
        "degraded": True,
    },
    "VAULT999": {
        "status": "DEGRADED_CLAIM",
        "attested_tools": [],
        "tool_count": 0,
        "note": "Immutable audit ledger — sealed memory, not vibes.",
        "degraded": True,
    },
}


# ── Public API ────────────────────────────────────────────────────


def read_capability_attestations() -> dict[str, dict[str, Any]]:
    """
    Read CAPABILITY_LEDGER.

    Returns a dict of organ → capability info.
    Status values:
      - STATIC_CLAIM: from FORGE_REGISTRY.md (not live-attested)
      - NATS_ATTESTED: live attestation received via NATS
      - UNKNOWN: no information available
    """
    # TODO(forge-3): subscribe to NATS arifos.swarm.capability.>
    # For now, return static baseline
    return dict(_STATIC_CAPABILITIES)


def get_organ_capabilities(organ: str) -> dict[str, Any]:
    """
    Get capabilities for a specific organ.
    Returns UNKNOWN if organ not known.
    """
    return read_capability_attestations().get(
        organ,
        {
            "status": "UNKNOWN",
            "attested_tools": [],
            "tool_count": 0,
        },
    )


def attest_capability(
    *,
    organ: str,
    tool: str,
    schema_hash: str | None = None,
    side_effect_class: str = "OBSERVE",
) -> dict[str, Any]:
    """
    Record a capability attestation from an organ.

    Forge 3: This will publish to NATS arifos.swarm.capability.{organ}.
    For now, returns dry-run attestation.
    """
    return {
        "organ": organ,
        "tool": tool,
        "schema_hash": schema_hash,
        "side_effect_class": side_effect_class,
        "attested_by": organ,
        "status": "DRY_RUN_ATTESTATION",
        "note": "Live NATS attestation pending Forge 3",
    }


def detect_capability_drift(
    *,
    previous: dict[str, dict[str, Any]] | None = None,
    current: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Detect capability drift between two snapshots.

    Returns:
      drifted: True if any organ's tool count or status changed
      changes: list of change descriptions
      degraded_organs: list of organs that are DEGRADED_CLAIM
    """
    if previous is None:
        previous = {}
    if current is None:
        current = read_capability_attestations()

    changes: list[str] = []
    degraded: list[str] = []

    for organ, info in current.items():
        prev = previous.get(organ, {})

        if info.get("status", "").startswith("DEGRADED"):
            degraded.append(organ)

        if prev.get("tool_count", 0) != info.get("tool_count", 0):
            changes.append(
                f"{organ} tool_count: {prev.get('tool_count', 0)} → {info.get('tool_count', 0)}"
            )

        if prev.get("status") != info.get("status"):
            changes.append(f"{organ} status: {prev.get('status')} → {info.get('status')}")

    return {
        "drifted": len(changes) > 0 or len(degraded) > 0,
        "changes": changes,
        "degraded_organs": degraded,
        "all_degraded": len(degraded) == len(current),
        "next_safe_action": "OBSERVE_ONLY" if degraded else "PROCEED_WITH_CAUTION",
    }
