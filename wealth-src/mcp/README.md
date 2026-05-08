# WEALTH MCP Surfaces

This repo ships **two** MCP servers. They are not interchangeable.

## 1. Canonical packaged kernel

- **Canonical file:** `internal/monolith.py`
- **Compat wrapper:** `server.py`
- **Role:** Primary WEALTH valuation kernel
- **Used by:** `server.py`, `fastmcp.json`, `mcp.json`, MCP packaging, Docker/host boot paths
- **Scope:** 13 canonical MCP tools + packaged resources

Run it with:

```bash
cd /root/WEALTH
python internal/monolith.py
# or the external compat wrapper:
python server.py
```

`internal/monolith.py` is the source of truth for the packaged WEALTH MCP runtime.
`server.py` is a thin compatibility wrapper that preserves public entrypoints.

## 2. Civilizational demo surface

- **File:** `mcp/server.py`
- **Role:** Secondary FastMCP demo for markets, energy, food, and prospect economics
- **Scope:** 6 tools + 3 resources

Run it with:

```bash
cd /root/WEALTH
python mcp/server.py
```

Current demo tools:

- `wealth_evaluate_prospect`
- `markets_analyze_ticker`
- `markets_portfolio_stress_test`
- `energy_crisis_assess`
- `energy_shortage_predict`
- `food_security_index`

## Practical rule

If you are wiring WEALTH into another system and need the **real packaged kernel**, target
**`internal/monolith.py`** conceptually and use **`server.py`** only when an external tool
expects the historical root entrypoint.

If you are experimenting with domain-specific civilizational demos, use **`mcp/server.py`**.
