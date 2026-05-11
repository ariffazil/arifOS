# arifOS Horizon MCP — SKILL.md

> Constitutional AI orchestration kernel deployed at **https://mcp.arif-fazil.com/mcp**
> Auth: `FASTMCP_API_KEY` or `MCP_API_KEY` env var (Bearer token)

## 20-Tool Surface — 11 Canonical + 9 P_* Oracles

### Tool Call Order (Constitutionally Enforced)

```
000 arifos_init        ← MUST be first — session_id anchors everything
111 arifos_sense       ← ground in reality before reasoning
333 arifos_mind        ← reason only after sensing
666 arifos_heart       ← ethics check before judge
888 arifos_judge       ← verdict only after heart passes
999 arifos_vault       ← seal only after judge SEAL
    arifos_forge       ← execute only after vault SEAL
```

Skipping steps is a Floor violation.

## Quick Start

```bash
export FASTMCP_API_KEY="your-key"

# Initialize session
python arifOS_horizon_cli.py arifos_init actor_id=arif-mcp intent="test session" risk_tier=low

# Constitutional judgment
python arifOS_horizon_cli.py arifos_judge query="deploy to production" risk_tier=high

# Read vault ledger
python arifOS_horizon_cli.py arifos_vault mode=read limit=10

# Economic audit (merged mode — no longer a separate tool)
python arifOS_horizon_cli.py arifos_ops mode=economic_audit session_id=YOUR_SESSION

# Monitor metabolism (merged mode — no longer a separate tool)
python arifOS_horizon_cli.py arifos_ops mode=metabolism session_id=YOUR_SESSION
```

## 11 Canonical Tools

| Tool | Description | Required Params | Modes |
|------|-------------|-----------------|-------|
| `arifos_init` | Initialize constitutional session | `actor_id`, `intent` | `init`, `refresh`, `state`, `status`, `probe` |
| `arifos_sense` | Ground query in physical reality | `query` | `governed`, `search`, `ingest`, `compass`, `atlas`, `time`, `location` |
| `arifos_mind` | Structured reasoning | `query` | `reason`, `sequential`, `step`, `branch`, `merge`, `review`, `reflect` |
| `arifos_kernel` | Route to metabolic lane | `query` | `kernel`, `status` |
| `arifos_heart` | Ethical critique and simulation | `query` | `critique`, `simulate` |
| `arifos_ops` | Thermodynamic and cost estimation | `query` | `cost`, `health`, `vitals`, `entropy`, `economic_audit`, `metabolism` |
| `arifos_judge` | Final constitutional verdict | `query`, `risk_tier` | — |
| `arifos_memory` | Governed memory recall | `query` | `vector_query`, `vector_store`, `engineer`, `query` |
| `arifos_vault` | Append/read immutable ledger | — | `append`, `read` |
| `arifos_forge` | Delegated execution bridge | `action`, `payload`, `session_id`, `judge_verdict`, `judge_g_star` | — |
| `arifos_gateway` | Orthogonality Guard (Ω_ortho ≥ 0.95) | `session_id` | `guard`, `audit`, `correlate` |

## 9 P_* Oracles (Perception — No Floor Overhead)

| Oracle | Description | Required Params |
|--------|-------------|-----------------|
| `P_well_state_read` | WELL biological telemetry snapshot | — |
| `P_well_readiness_check` | Biological readiness verdict for arifos_judge | — |
| `P_well_floor_scan` | W-Floor status scan across all dimensions | — |
| `P_geox_scene_load` | Load seismic, well, or volume data | `scene_type`, `path` |
| `P_geox_skills_query` | Query GEOX skill registry | `query` |
| `P_wealth_snapshot_fetch` | Macro/energy/carbon snapshot | `geography` |
| `P_wealth_series_fetch` | Live time-series data | `source`, `series_id` |
| `P_wealth_vintage_fetch` | Vintage series (FRED/ALFRED) | `series_id`, `vintage_date` |
| `P_vault_ledger_read` | VAULT999 ledger read | — |

## Deprecated Aliases (Do Not Use)

These tools are deprecated and will be removed. Use the canonical mode params instead:

| Deprecated | Use Instead |
|------------|------------|
| `arifos_anchor_session` | `arifos_init(mode="init")` |
| `arifos_execute_judge` | `arifos_judge` |
| `arifos_forge_judge_check` | `arifos_judge(dry_run=True)` |
| `arifos_forge_execute` | `arifos_forge(dry_run=False)` |
| `arifos_perform_economic_audit` | `arifos_ops(mode="economic_audit")` |
| `arifos_verify_location` | `arifos_sense(mode="location")` |
| `arifos_monitor_metabolism` | `arifos_ops(mode="metabolism")` |
| `arifos_get_vault_data` | `arifos_vault(mode="read")` |

## Constitutional Verdict Types

| Verdict | Meaning |
|---------|---------|
| `SEAL` | All floors passed — safe to proceed |
| `PARTIAL` | Soft floor warning — proceed with caution |
| `VOID` | Constitutional violation — action blocked |
| `HOLD` | High-stakes — requires human approval (888_HOLD) |

## Protocol Rules

- **MCP** — stateless capability execution (call → result)
- **A2A** — stateful agent orchestration (negotiate → delegate → verify)
- Never call `arifos_judge` via A2A or `mission:propose` via MCP

## Notes

- All tool calls are logged to VAULT999 with BLS signatures
- `arifos_forge` requires a prior `arifos_judge` SEAL verdict before execution
- `arifos_gateway` enforces Ω_ortho ≥ 0.95 across tool outputs — if it returns HOLD, diversify the query approach before retrying
- P_* oracles are fast, stateless perception interfaces — do not route domain queries through governance tools
