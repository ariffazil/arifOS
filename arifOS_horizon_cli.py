#!/usr/bin/env python3
"""
arifOS Horizon MCP CLI
Generated from live server: https://arifOS.fastmcp.app/mcp
Auth: Bearer token (set FASTMCP_API_KEY env or --token flag)
"""
import sys, os, json, asyncio
from pathlib import Path

# ── Auth ──────────────────────────────────────────────────────────────────────
TOKEN = os.environ.get("FASTMCP_API_KEY") or os.environ.get("MCP_API_KEY") or ""
if not TOKEN:
    sys.stderr.write("ERROR: Set FASTMCP_API_KEY or MCP_API_KEY\n")
    sys.exit(1)

URL = "https://arifOS.fastmcp.app/mcp"

# ── Client bootstrap ──────────────────────────────────────────────────────────
from fastmcp import Client
from fastmcp.client.auth import BearerAuth

async def get_client():
    return Client(URL, auth=BearerAuth(token=TOKEN))

# ── Tool wrappers ──────────────────────────────────────────────────────────────

async def call_arifos_init(**kwargs):
    """Initialize constitutional session with identity binding and telemetry seed"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_init", kwargs)

async def call_arifos_sense(**kwargs):
    """Ground query in physical reality via the 8-stage constitutional sensing protocol"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_sense", kwargs)

async def call_arifos_mind(**kwargs):
    """Structured reasoning with typed cognitive pipeline"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_mind", kwargs)

async def call_arifos_kernel(**kwargs):
    """Route request to correct metabolic lane or tool family"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_kernel", kwargs)

async def call_arifos_heart(**kwargs):
    """Red-team proposal for ethical risks"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_heart", kwargs)

async def call_arifos_ops(**kwargs):
    """Calculate operation costs, thermodynamics, capacity, and timing"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_ops", kwargs)

async def call_arifos_judge(**kwargs):
    """Final constitutional verdict evaluation"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_judge", kwargs)

async def call_arifos_memory(**kwargs):
    """Retrieve governed memory and engineering context"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_memory", kwargs)

async def call_arifos_vault(**kwargs):
    """Append immutable verdict record to Merkle-hashed ledger"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_vault", kwargs)

async def call_arifos_forge(**kwargs):
    """Delegated Execution Bridge — judge-validated action executor"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_forge", kwargs)

async def call_arifos_gateway(**kwargs):
    """Orthogonality Guard — supervises AGI||ASI lanes"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_gateway", kwargs)

async def call_arifos_monitor_metabolism(**kwargs):
    """Real-time dashboard of 13 Constitutional Floors"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_monitor_metabolism", kwargs)

async def call_arifos_execute_judge(**kwargs):
    """Run constitutional verdict evaluation on a candidate action"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_execute_judge", kwargs)

async def call_arifos_get_vault_data(**kwargs):
    """Read VAULT999 ledger and build current BLS seal card"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_get_vault_data", kwargs)

async def call_arifos_anchor_session(**kwargs):
    """Anchor a new arifOS session"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_anchor_session", kwargs)

async def call_arifos_forge_judge_check(**kwargs):
    """Pre-forge constitutional check — runs 888_JUDGE dry_run"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_forge_judge_check", kwargs)

async def call_arifos_forge_execute(**kwargs):
    """Execute forge after both gates pass"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_forge_execute", kwargs)

async def call_arifos_perform_economic_audit(**kwargs):
    """Perform a constitutional economic audit"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_perform_economic_audit", kwargs)

async def call_arifos_verify_location(**kwargs):
    """Verify a geospatial location against constitutional Earth Witness"""
    client = await get_client()
    async with client:
        return await client.call_tool("arifos_verify_location", kwargs)

async def call_P_well_state_read(**kwargs):
    """Read current WELL biological telemetry snapshot"""
    client = await get_client()
    async with client:
        return await client.call_tool("P_well_state_read", kwargs)

async def call_P_well_readiness_check(**kwargs):
    """Check biological readiness verdict for arifOS JUDGE"""
    client = await get_client()
    async with client:
        return await client.call_tool("P_well_readiness_check", kwargs)

async def call_P_well_floor_scan(**kwargs):
    """Scan W-Floor status across all dimensions"""
    client = await get_client()
    async with client:
        return await client.call_tool("P_well_floor_scan", kwargs)

async def call_P_geox_scene_load(**kwargs):
    """Load seismic, well, or volume data into witness context"""
    client = await get_client()
    async with client:
        return await client.call_tool("P_geox_scene_load", kwargs)

async def call_P_geox_skills_query(**kwargs):
    """Query GEOX skill registry by keyword or domain"""
    client = await get_client()
    async with client:
        return await client.call_tool("P_geox_skills_query", kwargs)

async def call_P_wealth_snapshot_fetch(**kwargs):
    """Fetch cross-source macro/energy/carbon snapshot"""
    client = await get_client()
    async with client:
        return await client.call_tool("P_wealth_snapshot_fetch", kwargs)

async def call_P_wealth_series_fetch(**kwargs):
    """Fetch live data series from open public source"""
    client = await get_client()
    async with client:
        return await client.call_tool("P_wealth_series_fetch", kwargs)

async def call_P_wealth_vintage_fetch(**kwargs):
    """Fetch specific vintage of series (FRED/ALFRED)"""
    client = await get_client()
    async with client:
        return await client.call_tool("P_wealth_vintage_fetch", kwargs)

async def call_P_vault_ledger_read(**kwargs):
    """Read VAULT999 ledger, build BLS seal card"""
    client = await get_client()
    async with client:
        return await client.call_tool("P_vault_ledger_read", kwargs)

# ── CLI dispatcher ────────────────────────────────────────────────────────────
COMMANDS = {
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
    "arifos_monitor_metabolism": call_arifos_monitor_metabolism,
    "arifos_execute_judge": call_arifos_execute_judge,
    "arifos_get_vault_data": call_arifos_get_vault_data,
    "arifos_anchor_session": call_arifos_anchor_session,
    "arifos_forge_judge_check": call_arifos_forge_judge_check,
    "arifos_forge_execute": call_arifos_forge_execute,
    "arifos_perform_economic_audit": call_arifos_perform_economic_audit,
    "arifos_verify_location": call_arifos_verify_location,
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
        print("arifOS Horizon CLI")
        print("Usage: python arifOS_horizon_cli.py <tool> [args...]")
        print('print("Example: python arifOS_horizon_cli.py arifos_judge query=\"test\" risk_tier=low")')
        print()
        print("Tools:")
        for name in sorted(COMMANDS.keys()):
            print(f"  {name}")
        sys.exit(1)

    tool = sys.argv[1]
    if tool not in COMMANDS:
        sys.stderr.write(f"Unknown tool: {tool}\n")
        sys.exit(1)

    # Parse remaining args as kwargs: key=value
    kwargs = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            # Auto-convert types
            if v.lower() == "true": v = True
            elif v.lower() == "false": v = False
            elif v.lower() == "null": v = None
            elif v.startswith("[") or v.startswith("{"): 
                try: v = json.loads(v)
                except: pass
            else:
                try: v = int(v)
                except:
                    try: v = float(v)
                    except: pass
            kwargs[k.strip()] = v

    result = asyncio.run(COMMANDS[tool](**kwargs))
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    main()
