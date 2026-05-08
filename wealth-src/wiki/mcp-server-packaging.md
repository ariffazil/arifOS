---
title: WEALTH MCP Server Packaging
date: 2026-04-17
tags: [mcp, server, integration, packaging, wealth]
---

# WEALTH MCP Server Packaging

The current repo state exposes **two Python MCP servers**, with one canonical packaged kernel and one supplemental domain demo.

## Packaged truth surface

- **File:** `server.py`
- **Role:** Main WEALTH valuation kernel
- **Used by:** `package.json`, `fastmcp.json`, `mcp.json`, `Dockerfile`
- **Current size:** 29 tools + 2 resources

Representative capabilities:

- Valuation math: NPV, IRR, PI, EMV, payback, Monte Carlo
- Financial state: net worth, cashflow, personal decisioning, agent budgets
- Governance: entropy audit, floor checks, policy audit, init
- Persistence: vault-backed transaction and portfolio snapshot recording

## Supplemental demo surface

- **File:** `mcp/server.py`
- **Role:** Civilizational markets / energy / food / prospect demo
- **Current size:** 6 tools + 3 resources

Current tools:

- `wealth_evaluate_prospect`
- `markets_analyze_ticker`
- `markets_portfolio_stress_test`
- `energy_crisis_assess`
- `energy_shortage_predict`
- `food_security_index`

## Operational rule

If another system needs the **real packaged WEALTH runtime**, wire **`server.py`**.

If another system needs the **civilizational demo surface**, wire **`mcp/server.py`**.

## Why this matters

Older repo notes described:

- a Node `mcp/server.js` surface that is no longer the source of truth, or
- only the smaller civilizational FastMCP file without mentioning the main valuation kernel.

The current repo SOT is the split above.

## Run commands

```bash
cd /root/WEALTH
python server.py
python mcp/server.py
```

---
*Repo SOT update | 999 SEAL ALIVE*
