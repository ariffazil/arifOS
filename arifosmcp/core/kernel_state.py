"""
kernel_state.py — Single authoritative truth surface for arifOS kernel health.
All attestation endpoints read from this. None compute independently.
Introduced: 2026-06-20 Phase 1 truth unification.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class KernelStatus(str, Enum):
    ALIVE = "ALIVE"
    DEGRADED = "DEGRADED"
    HALTED = "HALTED"
    BOOTSTRAPPING = "BOOTSTRAPPING"


class HealthProbeType(str, Enum):
    SELF = "self"              # kernel self-report (in-process)
    ORGAN_GENERIC = "organ_generic"   # organ HTTP probe
    PROCESS_LOCAL = "process_local"   # local process health
    TCP_CONNECT = "tcp_connect"       # raw TCP, not MCP
    MCP_SCHEMA = "mcp_schema"         # MCP protocol probe


@dataclass
class KernelStateRow:
    """A single row from arifosmcp_kernel_state — the ONE truth."""
    kernel_version: str
    constitution_hash: str
    schema_hash: str
    tool_count_canonical: int       # from CANONICAL_TOOLS dict
    tool_count_live: int            # from last HTTP probe cycle
    organ_count: int
    failed_calls_24h: int
    kernel_status: KernelStatus
    degradation_reason: str | None
    organ_status: dict
    declared_tools: dict            # from FEDERATION_ORGANS (constitutional)
    live_tools: dict                # from live HTTP probes (operational)
    last_refreshed_at: str
    seal_id: str | None
    probe_type: HealthProbeType


def read_kernel_state(supabase_client) -> KernelStateRow | None:
    """
    Read the ONE truth row from arifosmcp_kernel_state.
    Returns None if the table is not initialized or unreachable.

    All attestation endpoints — arif_os_attest, arif_organ_attest_all,
    hermes_system_status — must call this function and report from
    the same row. No endpoint may compute health independently.
    """
    try:
        res = (
            supabase_client.table("arifosmcp_kernel_state")
            .select("*")
            .order("last_refreshed_at", desc=True)
            .limit(1)
            .execute()
        )
        if not res.data:
            return None
        r = res.data[0]
        return KernelStateRow(
            kernel_version=r["kernel_version"],
            constitution_hash=r["constitution_hash"],
            schema_hash=r["schema_hash"],
            tool_count_canonical=r["tool_count_canonical"],
            tool_count_live=r["tool_count_live"],
            organ_count=r["organ_count"],
            failed_calls_24h=r["failed_calls_24h"],
            kernel_status=KernelStatus(r["kernel_status"]),
            degradation_reason=r.get("degradation_reason"),
            organ_status=r.get("organ_status", {}),
            declared_tools=r.get("declared_tools", {}),
            live_tools=r.get("live_tools", {}),
            last_refreshed_at=str(r["last_refreshed_at"]),
            seal_id=r.get("seal_id"),
            probe_type=HealthProbeType.MCP_SCHEMA,
        )
    except Exception:
        return None


def refresh_kernel_state(
    supabase_client,
    live_tool_counts: dict,
    version: str,
    constitution_hash: str = "UNSET",
    schema_hash: str = "UNSET",
) -> bool:
    """
    Called after each HTTP probe cycle completes.
    Writes the canonical + live counts into the single truth row.
    Only this function may write to arifosmcp_kernel_state.

    Returns True on success, False on failure (fail-open — attestation
    endpoints fall back to their local heuristics but flag the degradation).
    """
    from arifosmcp.constitutional_map import list_canonical_tools
    from arifosmcp.runtime.federation_registry import FEDERATION_ORGANS

    canonical_count = len(list_canonical_tools())
    live_total = sum(live_tool_counts.values())
    organ_count_val = len(live_tool_counts)

    declared = {
        k: v.get("canonical_tools", 0)
        for k, v in FEDERATION_ORGANS.items()
    }

    # Determine status
    if live_total == 0:
        status = "DEGRADED"
        reason = "All HTTP probes returned 0 tools — network or MCP layer issue"
    elif live_total < canonical_count:
        status = "DEGRADED"
        reason = (
            f"Live tools ({live_total}) below canonical floor ({canonical_count})"
        )
    else:
        status = "ALIVE"
        reason = None

    try:
        supabase_client.table("arifosmcp_kernel_state").upsert(
            {
                "id": 1,  # always overwrite the single truth row
                "kernel_version": version,
                "constitution_hash": constitution_hash,
                "schema_hash": schema_hash,
                "tool_count_canonical": canonical_count,
                "tool_count_live": live_total,
                "organ_count": organ_count_val,
                "kernel_status": status,
                "degradation_reason": reason,
                "declared_tools": declared,
                "live_tools": live_tool_counts,
                "last_refreshed_at": "now()",
                "sealed_by": "refresh_kernel_state",
            },
            on_conflict="id",
        ).execute()
        return True
    except Exception:
        return False
