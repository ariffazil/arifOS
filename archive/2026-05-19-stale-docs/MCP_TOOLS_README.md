# arifOS Federation — MCP Tools Summary

## Architecture

```
MCP Host (Claude Code/Desktop)
    │
    ├── P_MCP → Perceives (reads WELL, GEOX, VAULT, WEALTH)
    ├── T_MCP → Transforms (computes physics, math, monte_carlo)
    ├── V_MCP → Valuates (ranks by NPV, EMV, allocation)
    ├── G_MCP → Governs (routes, judges, enforces ethics)
    ├── E_MCP → Executes (mutates forge, vault, memory)
    └── M_MCP → Metacognizes (monitors omega, discovers skills)
```

## Quick Start

```bash
# Run unified server (all 6 agents)
python -m arifOS.arifosmcp.run

# Run single agent
python -m arifOS.arifosmcp.run --agent P

# Run multiple agents
python -m arifOS.arifosmcp.run --agents P,T,V

# Show tool catalog
python -m arifOS.arifosmcp.run --catalog
```

## Tool Count

| Agent | Tools | Domain |
|-------|-------|--------|
| P (Perception) | 9 | WELL, GEOX, WEALTH, VAULT reads |
| T (Transformation) | 7 | Physics, Math, Monte Carlo |
| V (Valuation) | 9 | NPV, EMV, DSCR, Allocation |
| G (Governance) | 8 | Init, Route, Mind, Judge, Ethics, Hold |
| E (Execution) | 8 | Forge, Vault, Memory, WELL |
| M (Meta) | 6 | Omega, Skills, Monitor, Evidence |
| **Total** | **47** | |

## Files

| File | Purpose |
|------|---------|
| `mcp_tools.py` | All 47 tools organized by agent |
| `mcp_servers.json` | Claude Desktop MCP config |
| `run.py` | Entry point for running servers |
| `a2a_aligned.py` | A2A protocol (agent-to-agent) |
| `a2a_server.py` | A2A server implementation |
| `agents_6.py` | Minimal 6-agent POC |
| `agents_9.py` | Production 9-agent design |

## MCP vs A2A

- **MCP**: Model ↔ Tools (within each agent)
- **A2A**: Agent ↔ Agent (coordination between agents)

Each agent exposes its tools via MCP. Inter-agent coordination uses A2A.
