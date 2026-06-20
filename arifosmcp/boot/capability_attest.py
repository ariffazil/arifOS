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

# ── Derive arifOS tool count from canonical source ───────────────
try:
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    _ARIFOS_CANONICAL_COUNT = len(CANONICAL_TOOLS)  # currently 19
    _ARIFOS_DIAGNOSTIC_COUNT = 37  # see DIAGNOSTIC_TOOLS in constitutional_map.py
    _ARIFOS_TOTAL_COUNT = _ARIFOS_CANONICAL_COUNT + _ARIFOS_DIAGNOSTIC_COUNT
except ImportError:
    _ARIFOS_CANONICAL_COUNT = 19
    _ARIFOS_DIAGNOSTIC_COUNT = 37
    _ARIFOS_TOTAL_COUNT = 56
# ── Static capability baseline (FORGE_REGISTRY.md) ────────────────

_STATIC_CAPABILITIES: dict[str, dict[str, Any]] = {
    "arifOS": {
        "status": "DEGRADED_CLAIM",
        "attested_tools": [],
        "canonical_tool_count": _ARIFOS_CANONICAL_COUNT,
        "total_tool_count": _ARIFOS_TOTAL_COUNT,
        "note": "Static claim — live attestation via NATS not yet active. Canonical tool count derived from CANONICAL_TOOLS.",
        "degraded": True,
    },
    "GEOX": {
        "status": "DEGRADED_CLAIM",
        "attested_tools": [],
        "canonical_tool_count": 31,
        "total_tool_count": 37,
        "note": "Static claim — live attestation via NATS not yet active. Earth data organ, not authority.",
        "degraded": True,
    },
    "WEALTH": {
        "status": "DEGRADED_CLAIM",
        "attested_tools": [],
        "canonical_tool_count": 20,
        "total_tool_count": 21,
        "note": "Static claim — live attestation via NATS not yet active. Live WEALTH /health reports 21 tools (20 canonical + 1 legacy). Contract drift flagged if mismatch persists.",
        "degraded": True,
    },
    "WELL": {
        "status": "DEGRADED_CLAIM",
        "attested_tools": [],
        "canonical_tool_count": 18,
        "total_tool_count": 21,
        "note": "Static claim — live attestation via NATS not yet active. REFLECT_ONLY organ. Live WELL /health reports 21 tools, 18 registered.",
        "degraded": True,
    },
    "FORGE": {
        "status": "DEGRADED_CLAIM",
        "attested_tools": [],
        "canonical_tool_count": 15,
        "total_tool_count": 77,
        "note": "A-FORGE execution shell — must never be sovereign. Muscle, not judge. MCP gateway has 77 tools.",
        "degraded": True,
    },
    "GATEWAY": {
        "status": "DEGRADED_CLAIM",
        "attested_tools": [],
        "canonical_tool_count": 0,
        "total_tool_count": 0,
        "note": "AAA/OpenClaw external IO boundary — all external calls require human gate.",
        "degraded": True,
    },
    "VAULT999": {
        "status": "DEGRADED_CLAIM",
        "attested_tools": ["arif_vault_seal", "arif_evidence_fetch"],
        "canonical_tool_count": 2,
        "total_tool_count": 2,
        "note": "Immutable audit ledger — succession memory, not vibes. Tools: arif_vault_seal (999), arif_evidence_fetch (vault query). Live attestation pending NATS subscription.",
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
      - LIVE_ATTESTED: probed via HTTP /health within last call
      - DEGRADED_LIVE: live probe returned non-2xx
      - UNKNOWN: no information available
    """
    import json as _json
    import urllib.error as _ue
    import urllib.request as _ur

    # Organ probe map — hostname, port, expected canonical count
    _PROBES: dict[str, tuple[str, int, int]] = {
        "arifOS": ("127.0.0.1", 8088, _ARIFOS_CANONICAL_COUNT),
        "GEOX":   ("127.0.0.1", 8081, 31),
        "WEALTH": ("127.0.0.1", 18082, 20),
        "WELL":   ("127.0.0.1", 18083, 18),
        "FORGE":  ("127.0.0.1", 7071, 15),
        "GATEWAY":("127.0.0.1", 18789, 0),
        "VAULT999":("127.0.0.1", 8100, 2),  # vault999-api
    }

    out: dict[str, dict[str, Any]] = dict(_STATIC_CAPABILITIES)

    for organ, (host, port, declared_count) in _PROBES.items():
        if organ not in out:
            out[organ] = {
                "status": "UNKNOWN",
                "attested_tools": [],
                "canonical_tool_count": 0,
                "total_tool_count": 0,
                "degraded": True,
            }
        try:
            with _ur.urlopen(f"http://{host}:{port}/health", timeout=2.0) as r:
                body = r.read().decode("utf-8", errors="replace")
                if 200 <= r.status < 300:
                    out[organ]["status"] = "LIVE_ATTESTED"
                    out[organ]["degraded"] = False
                    # Try to extract tool count from JSON body
                    try:
                        d = _json.loads(body)
                        canonical = (
                            d.get("canonical_tools_loaded")
                            or d.get("canonical_tool_count")
                            or d.get("canonical_count")
                            or declared_count
                        )
                        total = (
                            d.get("total_declared_tools")
                            or d.get("total_tool_count")
                            or d.get("tools_exposed_via_mcp")
                            or declared_count
                        )
                        if isinstance(canonical, int) and canonical > 0:
                            out[organ]["canonical_tool_count"] = canonical
                        if isinstance(total, int) and total > 0:
                            out[organ]["total_tool_count"] = total
                    except (ValueError, TypeError):
                        pass
                else:
                    out[organ]["status"] = "DEGRADED_LIVE"
                    out[organ]["degraded"] = True
        except (_ue.URLError, _ue.HTTPError, OSError, TimeoutError) as e:
            out[organ]["status"] = "DEGRADED_LIVE"
            out[organ]["degraded"] = True
            out[organ]["note"] = (
                out[organ].get("note", "") + f" [live probe: {str(e)[:60]}]"
            ).strip()

    return out


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
