#!/usr/bin/env python3
"""
arifOS Horizon MCP CLI
Generated from live server: https://mcp.arif-fazil.com/mcp
Auth: Bearer token (set FASTMCP_API_KEY env or --token flag)

11 canonical tools + 9 P_* oracles (20 total surface).
Deprecated aliases removed — use mode params on canonical tools instead:
  arifos_anchor_session     → arifos_init(mode="init")
  arifos_execute_judge      → arifos_judge
  arifos_forge_judge_check  → arifos_judge(dry_run=True)
  arifos_forge_execute      → arifos_forge(dry_run=False)
  arifos_perform_economic_audit → arifos_ops(mode="economic_audit")
  arifos_verify_location    → arifos_sense(mode="location")
  arifos_monitor_metabolism → arifos_ops(mode="metabolism")
  arifos_get_vault_data    → arifos_vault(mode="read")
"""
import sys, os, json, asyncio
from pathlib import Path

# ── Auth ──────────────────────────────────────────────────────────────────────
TOKEN = os.environ.get("FASTMCP_API_KEY") or os.environ.get("MCP_API_KEY") or ""
if not TOKEN:
    sys.stderr.write("ERROR: Set FASTMCP_API_KEY or MCP_API_KEY\n")
    sys.exit(1)

URL = "https://mcp.arif-fazil.com/mcp"

# ── Client bootstrap ──────────────────────────────────────────────────────────
from fastmcp import Client
from fastmcp.client.auth import BearerAuth


async def get_client():
    return Client(URL, auth=BearerAuth(token=TOKEN))


# ═══════════════════════════════════════════════════════════════════════════════
# 11 CANONICAL TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

async def call_arifos_init(**kwargs):
    """Initialize constitutional session. Modes: init, refresh, state, status, probe."""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_init", kwargs)


async def call_arifos_sense(**kwargs):
    """Ground in physical reality. Modes: governed, search, ingest, compass, atlas, time, location."""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_sense", kwargs)


async def call_arifos_mind(**kwargs):
    """Structured reasoning. Modes: reason, sequential, step, branch, merge, review, reflect."""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_mind", kwargs)


async def call_arifos_kernel(**kwargs):
    """Route to correct metabolic lane. Modes: kernel, status."""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_kernel", kwargs)


async def call_arifos_heart(**kwargs):
    """Ethical critique and consequence simulation. Modes: critique, simulate."""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_heart", kwargs)


async def call_arifos_ops(**kwargs):
    """Thermodynamic and operational cost estimation. Modes: cost, health, vitals, entropy, economic_audit, metabolism."""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_ops", kwargs)


async def call_arifos_judge(**kwargs):
    """Final constitutional verdict. Outputs: SEAL, PARTIAL, VOID, HOLD."""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_judge", kwargs)


async def call_arifos_memory(**kwargs):
    """Governed memory recall. Modes: vector_query, vector_store, engineer, query."""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_memory", kwargs)


async def call_arifos_vault(**kwargs):
    """Append/read immutable ledger. Modes: append (default), read."""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_vault", kwargs)


async def call_arifos_forge(**kwargs):
    """Delegated Execution Bridge — requires arifos_judge SEAL verdict first."""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_forge", kwargs)


async def call_arifos_gateway(**kwargs):
    """Orthogonality Guard. Modes: guard, audit, correlate."""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_gateway", kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# 9 P_* ORACLES — Domain perception interfaces
# ═══════════════════════════════════════════════════════════════════════════════

async def call_P_well_state_read(**kwargs):
    """WELL biological telemetry snapshot."""
    client = await get_client()
    async with client:
        return await client.call_tool("P_well_state_read", kwargs)


async def call_P_well_readiness_check(**kwargs):
    """Biological readiness verdict for arifos_judge."""
    client = await get_client()
    async with client:
        return await client.call_tool("P_well_readiness_check", kwargs)


async def call_P_well_floor_scan(**kwargs):
    """W-Floor status scan across all dimensions."""
    client = await get_client()
    async with client:
        return await client.call_tool("P_well_floor_scan", kwargs)


async def call_P_geox_scene_load(**kwargs):
    """Load seismic, well, or volume data into witness context."""
    client = await get_client()
    async with client:
        return await client.call_tool("P_geox_scene_load", kwargs)


async def call_P_geox_skills_query(**kwargs):
    """Query GEOX skill registry by keyword or domain."""
    client = await get_client()
    async with client:
        return await client.call_tool("P_geox_skills_query", kwargs)


async def call_P_wealth_snapshot_fetch(**kwargs):
    """Cross-source macro/energy/carbon snapshot."""
    client = await get_client()
    async with client:
        return await client.call_tool("P_wealth_snapshot_fetch", kwargs)


async def call_P_wealth_series_fetch(**kwargs):
    """Live data series from open public source."""
    client = await get_client()
    async with client:
        return await client.call_tool("P_wealth_series_fetch", kwargs)


async def call_P_wealth_vintage_fetch(**kwargs):
    """Specific vintage of series (FRED/ALFRED)."""
    client = await get_client()
    async with client:
        return await client.call_tool("P_wealth_vintage_fetch", kwargs)


async def call_P_vault_ledger_read(**kwargs):
    """VAULT999 ledger read — returns BLS seal card and entries."""
    client = await get_client()
    async with client:
        return await client.call_tool("P_vault_ledger_read", kwargs)


# ── CLI dispatcher ────────────────────────────────────────────────────────────
COMMANDS = {
    # 11 canonical
    "arifos_init": call_arifos_init,
    "arifos_sense": call_arifos_sense,
    "arifos_mind": call_arifos_mind,
    "arifos_kernel": call_arifos_kernel,
    "arifos_heart": call_arifos_heart,
    "arifos_ops": call_arifos_ops,
    "arifos_judge": call_arifos_judge,
    "arifos_memory": call_arifos_memory,
    "arifos_vault": call_arifos_vault,
    "arifos_forge": call_arifos_forge,
    "arifos_gateway": call_arifos_gateway,
    # 9 P_* oracles
    "P_well_state_read": call_P_well_state_read,
    "P_well_readiness_check": call_P_well_readiness_check,
    "P_well_floor_scan": call_P_well_floor_scan,
    "P_geox_scene_load": call_P_geox_scene_load,
    "P_geox_skills_query": call_P_geox_skills_query,
    "P_wealth_snapshot_fetch": call_P_wealth_snapshot_fetch,
    "P_wealth_series_fetch": call_P_wealth_series_fetch,
    "P_wealth_vintage_fetch": call_P_wealth_vintage_fetch,
    "P_vault_ledger_read": call_P_vault_ledger_read,
}


def main():
    if len(sys.argv) < 2:
        print("arifOS Horizon CLI — 20 tools (11 canonical + 9 P* oracles)")
        print("Usage: python arifOS_horizon_cli.py <tool> [args...]")
        print()
        print("Canonical tools:")
        canonical = [
            "arifos_init", "arifos_sense", "arifos_mind", "arifos_kernel",
            "arifos_heart", "arifos_ops", "arifos_judge", "arifos_memory",
            "arifos_vault", "arifos_forge", "arifos_gateway",
        ]
        for name in canonical:
            print(f"  {name}")
        print()
        print("P_* Oracles:")
        oracles = [
            "P_well_state_read", "P_well_readiness_check", "P_well_floor_scan",
            "P_geox_scene_load", "P_geox_skills_query",
            "P_wealth_snapshot_fetch", "P_wealth_series_fetch", "P_wealth_vintage_fetch",
            "P_vault_ledger_read",
        ]
        for name in oracles:
            print(f"  {name}")
        sys.exit(1)

    tool = sys.argv[1]
    if tool not in COMMANDS:
        sys.stderr.write(f"Unknown tool: {tool}\n")
        sys.exit(1)

    kwargs = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            if v.lower() == "true":
                v = True
            elif v.lower() == "false":
                v = False
            elif v.lower() == "null":
                v = None
            elif v.startswith("[") or v.startswith("{"):
                try:
                    v = json.loads(v)
                except Exception:
                    pass
            else:
                try:
                    v = int(v)
                except Exception:
                    try:
                        v = float(v)
                    except Exception:
                        pass
            kwargs[k.strip()] = v

    result = asyncio.run(COMMANDS[tool](**kwargs))
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
