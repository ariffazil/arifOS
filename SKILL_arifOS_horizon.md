# arifOS Horizon MCP — SKILL.md

> Constitutional AI orchestration kernel deployed at **https://arifOS.fastmcp.app/mcp**
> Auth: `FASTMCP_API_KEY` or `MCP_API_KEY` env var (Bearer token)

## Quick Start

```bash
# Set key
export FASTMCP_API_KEY="your-key"

# Call a tool
python arifOS_horizon_cli.py arifos_get_vault_data
python arifOS_horizon_cli.py arifos_judge query="test action" risk_tier=low
python arifOS_horizon_cli.py arifos_verify_location lat=4.2105 lon=101.9758
```

## Full Tool Reference (28 tools)

### GOVERNANCE (Ψ Soul — 11 tools)

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `arifos_init` | Initialize constitutional session with identity binding | `actor_id`, `intent` |
| `arifos_sense` | Ground query in physical reality via 8-stage sensing protocol | `query` |
| `arifos_mind` | Structured reasoning with typed cognitive pipeline | `query` |
| `arifos_kernel` | Route request to correct metabolic lane or tool family | `query` |
| `arifos_heart` | Red-team proposal for ethical risks (F5/F6/F9) | `query` |
| `arifos_ops` | Calculate operation costs, thermodynamics, capacity | `query` |
| `arifos_judge` | Final constitutional verdict evaluation (SEAL/PARTIAL/VOID/HOLD) | `query`, `risk_tier` |
| `arifos_memory` | Retrieve governed memory from vector store | `query` |
| `arifos_vault` | Append immutable verdict record to Merkle-hashed ledger | `verdict` |
| `arifos_forge` | Delegated Execution Bridge — judge-validated executor | `action`, `payload`, `session_id`, `judge_verdict`, `judge_g_star` |
| `arifos_gateway` | Orthogonality Guard — supervises AGI\|\|ASI lanes | `session_id` |

### SECONDARY GOVERNANCE (6 tools)

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `arifos_monitor_metabolism` | Real-time dashboard of 13 Constitutional Floors | — |
| `arifos_execute_judge` | Run constitutional verdict evaluation | `candidate_action` |
| `arifos_get_vault_data` | Read VAULT999 ledger and build BLS seal card | — |
| `arifos_anchor_session` | Anchor a new arifOS session | — |
| `arifos_forge_judge_check` | Pre-forge constitutional check (888_JUDGE dry_run) | `candidate_action` |
| `arifos_forge_execute` | Execute forge after both gates pass | `candidate_action` |

### P-AXIS — Perception (WELL/GEOX/WEALTH) (8 tools)

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `P_well_state_read` | Read current WELL biological telemetry snapshot | — |
| `P_well_readiness_check` | Check biological readiness verdict for arifOS JUDGE | — |
| `P_well_floor_scan` | Scan W-Floor status across all dimensions | — |
| `P_geox_scene_load` | Load seismic, well, or volume data into witness context | `scene_type`, `path` |
| `P_geox_skills_query` | Query GEOX skill registry by keyword or domain | `query` |
| `P_wealth_snapshot_fetch` | Fetch cross-source macro/energy/carbon snapshot | `geography` |
| `P_wealth_series_fetch` | Fetch live data series from open public source | `source`, `series_id` |
| `P_wealth_vintage_fetch` | Fetch specific vintage of series (FRED/ALFRED) | `series_id`, `vintage_date` |

### ECONOMIC AUDIT

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `arifos_perform_economic_audit` | Perform a constitutional economic audit | `initial_cost`, `annual_benefit`, `years` |

### LOCATION

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `arifos_verify_location` | Verify geospatial location against constitutional Earth Witness | `lat`, `lon` |

### VAULT LEDGER

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `P_vault_ledger_read` | Read VAULT999 ledger, build BLS seal card | — |

## Example Invocations

```bash
# Initialize a session
python arifOS_horizon_cli.py arifos_init actor_id=arif-mcp intent="test session" risk_tier=low

# Run constitutional judgment
python arifOS_horizon_cli.py arifos_judge query="deploy to production" risk_tier=high

# Verify a location (Malaysia)
python arifOS_horizon_cli.py arifos_verify_location lat=4.2105 lon=101.9758

# Read vault data
python arifOS_horizon_cli.py arifos_get_vault_data

# Economic audit
python arifOS_horizon_cli.py arifos_perform_economic_audit initial_cost=100000 annual_benefit=30000 years=5

# Query memory
python arifOS_horizon_cli.py arifos_memory query="previous decisions" mode=vector_query

# Monitor metabolism
python arifOS_horizon_cli.py arifos_monitor_metabolism

# Read vault ledger
python arifOS_horizon_cli.py P_vault_ledger_read limit=10
```

## Constitutional Verdict Types

| Verdict | Meaning |
|---------|---------|
| `SEAL` | All floors passed — safe to proceed |
| `PARTIAL` | Soft floor warning — proceed with caution |
| `VOID` | Constitutional violation — action blocked |
| `HOLD` | High-stakes — requires human approval (888_HOLD) |

## Notes

- All tool calls are logged to VAULT999 with BLS signatures
- `arifos_forge` requires a prior `arifos_judge` SEAL verdict before execution
- P-axis tools (P_*) interface with WELL (wellbeing), GEOX (geospatial), and WEALTH (economic) oracles
- Location verification uses the constitutional Earth Witness protocol
