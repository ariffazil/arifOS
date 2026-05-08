# WEALTH MCP Tool Families — Current Repo SOT

> **Version:** v1.5.0  
> **Status:** ACTIVE REPO STATE  
> **Epistemic:** CLAIM  
> **DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

---

## 1. Runtime split

WEALTH currently exposes two MCP surfaces in-repo:

| Surface | File | Purpose |
|---|---|---|
| Canonical valuation kernel | `server.py` | Main packaged WEALTH runtime |
| Civilizational demo surface | `mcp/server.py` | Secondary domain demo for markets / energy / food / prospect evaluation |

The rest of this document treats `server.py` as the primary operational surface and `mcp/server.py` as a narrower extension.

---

## 2. Canonical kernel families (`server.py`)

### 2.1 Canonical 13-tool public surface
Tools:
- `wealth_future_value`
- `wealth_present_expect`
- `wealth_future_simulate`
- `wealth_info_value`
- `wealth_truth_validate`
- `wealth_survival_liquidity`
- `wealth_survival_leverage`
- `wealth_rule_enforce`
- `wealth_allocate_optimize`
- `wealth_game_coordinate`
- `wealth_sense_ingest`
- `wealth_past_record`
- `wealth_future_steward`

Core question: **Can every valuation, survival, governance, sensing, and record operation be expressed through the canonical 13-tool surface?**

Resources:
- `wealth://doctrine/valuation`
- `wealth://dimensions/definitions`

Core question: **Is the allocation constitutionally acceptable, and how is the evidence anchored?**

---

## 3. Civilizational demo family (`mcp/server.py`)

This secondary server currently carries six domain-facing demo tools:

| Domain | Tools |
|---|---|
| Prospect economics | `wealth_evaluate_prospect` |
| Markets | `markets_analyze_ticker`, `markets_portfolio_stress_test` |
| Energy | `energy_crisis_assess`, `energy_shortage_predict` |
| Food | `food_security_index` |

Resources:

- `market://{ticker}/fundamentals`
- `energy://{region}/realtime-mix`
- `food://global/prices`

This surface is **real**, but it is **not** the packaged kernel used by `npm run mcp`.

---

## 4. Legacy alias status

Legacy v1/v2 alias names are no longer exported by the canonical WEALTH MCP kernel.

Therefore:

- `registry.json` = canonical 11-band map
- `server.py` / `internal/monolith.py` = packaged runtime truth
- `mcp/server.py` = secondary civilizational demo truth

If those ever conflict, prefer the runtime files.

---

## 5. Failure modes

| Failure | Symptom | Mitigation |
|---|---|---|
| Wrong server assumption | Operators wire `mcp/server.py` thinking it is the packaged kernel | Use `server.py` for packaged/runtime integrations |
| Stale family docs | Docs describe dotted namespaces not implemented in code | Derive tool families from actual `@mcp.tool` surfaces |
| Canon/runtime confusion | `registry.json` count differs from `server.py` tool count | Treat registry as canonical topology, not exhaustive runtime inventory |
| Demo promoted as kernel | Civilizational surface treated as full production valuation engine | Label `mcp/server.py` explicitly as supplemental |

---

*Spec v1.5.0 | Repo SOT aligned*
