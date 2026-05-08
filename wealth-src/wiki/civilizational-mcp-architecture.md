---
title: Civilizational MCP Architecture
date: 2026-04-17
tags: [architecture, civilization, mcp, wealth]
---

# Civilizational MCP Architecture

WEALTH now has a **dual-surface MCP story**:

1. **`server.py`** is the canonical packaged valuation kernel.
2. **`mcp/server.py`** is a narrower civilizational domain demo layered beside it.

The civilizational surface does **not** replace the valuation kernel; it supplements it.

## 1. Domain lanes currently exposed

| Lane | Tools |
|---|---|
| Prospect economics | `wealth_evaluate_prospect` |
| Markets | `markets_analyze_ticker`, `markets_portfolio_stress_test` |
| Energy | `energy_crisis_assess`, `energy_shortage_predict` |
| Food | `food_security_index` |

Resources:

- `market://{ticker}/fundamentals`
- `energy://{region}/realtime-mix`
- `food://global/prices`

## 2. Relationship to the canonical kernel

The root `server.py` still owns the main WEALTH operational surface:

- valuation math
- leverage and entropy auditing
- personal and agent budgeting
- crisis and civilization scoring
- ingest / reconciliation
- policy / floor checks
- vault persistence

That means the architectural stack is:

```text
arifOS constitutional judgment
        ^
        |
 WEALTH server.py  (packaged capital kernel)
        +
 WEALTH mcp/server.py (civilizational demo lanes)
```

## 3. Design boundary

- Use **`server.py`** when you need the main WEALTH capital engine.
- Use **`mcp/server.py`** when you need the demo domain-oriented civilizational tools.
- If both are present, the packaged kernel remains authoritative.

## 4. Why the split is healthy

- The root kernel can keep growing as the durable valuation runtime.
- The civilizational surface can evolve faster without pretending to be the whole WEALTH system.
- GEOX-linked prospect economics can live in the demo lane while still feeding broader capital evaluation flows.

---
*Repo SOT aligned | 999 SEAL ALIVE*
