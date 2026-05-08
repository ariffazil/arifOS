# WEALTH — Capital Intelligence Engine

> **Constitutional Capital Allocation Layer for arifOS**
> **DITEMPA BUKAN DIBERI — Forged, Not Given**

[![WEALTH](https://img.shields.io/badge/WEALTH-v2026.05.02--KANON-00B894?style=flat-square)](https://github.com/ariffazil/wealth)
[![MCP](https://img.shields.io/badge/MCP-FastMCP_3.2.4-7C3AED?style=flat-square)](https://github.com/ariffazil/wealth)
[![arifOS](https://img.shields.io/badge/arifOS-F1%E2%80%93F13_Governed-FF6B00?style=flat-square)](https://github.com/ariffazil/arifOS)
[![License](https://img.shields.io/badge/License-AGPL_V3-4EAF0C?style=flat-square)](./LICENSE)

---

## What WEALTH Is

**WEALTH** is the capital allocation intelligence engine in the arifOS organism. It prices reward, survival, entropy, leverage, dignity, coordination, and policy constraints — so that capital decisions can be evaluated before arifOS applies the final constitutional judgment.

WEALTH does not make decisions. It produces **capital intelligence** — NPV, IRR, EMV, crisis triage, civilization stewardship — that arifOS's 888_JUDGE ratifies or voids.

```
Capital Signal → WEALTH Engine → Intelligence Output → arifOS 888_JUDGE → SEAL/HOLD/VOID
```

**This is not a calculator. This is epistemic capital sovereignty.**

---

## Position in the arifOS Trinity

```
ARIF (Human) → arifOS (Kernel) → WEALTH (Evidence) + GEOX (Earth) → arifOS JUDGE
     ↑              ↑                    ↑
  F13 VETO     F1–F13 FLOORS      Specialist Computation
```

WEALTH is the **capital evidence organ** — it surfaces the financial and economic dimensions of a decision so the constitutional kernel can apply judgment. arifOS never invests, allocates, or approves capital without WEALTH's input.

---

## Current Source of Truth

| Field | Value |
|-------|-------|
| Canonical repository | `https://github.com/ariffazil/wealth` |
| Version | `v2026.05.02-bbf8332` |
| Governing kernel | `arifOS F1–F13` |
| MCP tools (canonical kernel) | 48 tools (13 primitives × mode variants, each mode is a callable endpoint) |
| MCP tools (cross-domain demo) | 6 additional tools (separate `mcp/server.py`) |
| Capital scales | 8 (personal → household → sme → enterprise → national → crisis → civilization → agentic) |
| Capital types | 7 (financial, temporal, cognitive, social, ecological, strategic, thermodynamic) |
| Homepage | https://wealth.arif-fazil.com/ |

---

## Architecture — Sovereign Pipeline Families

> The MCP surface exposes **48 callable tools** — every mode and sub-mode is a first-class endpoint. The 13 canonical primitives (left column) are the architectural concept; the MCP tools are their operational surface.

| Family | Stage | Purpose | Canonical Primitive | MCP Tools (48 total) |
|--------|-------|---------|-------------------|----------------------|
| **SENSE** | 100 | Reality ingestion | `wealth_sense_ingest` | 7 tools: `wealth_sense_ingest`, `_fetch`, `_health`, `_reconcile`, `_snapshot`, `_sources`, `_vintage` |
| **MIND** | 200 | Epistemic modeling | `wealth_present_expect`, `wealth_future_simulate`, `wealth_info_value`, `wealth_truth_validate` | 6 tools: `wealth_mind_emv`, `_evoi`, `_evoi_mc`, `_monte_carlo`, `_schema`, `_correlation` |
| **SURVIVAL** | 300 | Solvency & stewardship | `wealth_survival_liquidity`, `wealth_survival_leverage`, `wealth_future_steward` | 8 tools: `wealth_survival_cashflow`, `_velocity`, `_triage`, `_dscr`, `_networth`, `_leverage`, `_liquidity`, `_civilization` |
| **REASON** | 400 | Capital discipline | `wealth_future_value`, `wealth_allocate_optimize`, `wealth_game_coordinate` | 9 tools: `wealth_reason_npv`, `_irr`, `_payback`, `_pi`, `_personal`, `_agent`, `_equilibrium`, `_game` + `wealth_npv_reward` |
| **JUDGE** | 888 | Constitutional gating | `wealth_rule_enforce` | 4 tools: `wealth_judge_floors`, `_policy`, `_kernel`, `_entropy` |
| **VAULT** | 999 | Immutable anchoring | `wealth_past_record` | 3 tools: `wealth_vault_init`, `_record`, `_snapshot` |

---

## MCP Server Surfaces

| Surface | File | Tools | Purpose |
|---------|------|-------|---------|
| **Canonical kernel** | `internal/monolith.py` | 48 MCP tools (13 primitives × mode variants) | Core valuation, risk, crisis, coordination |
| **Boot wrapper** | `server.py` | Thin compat | Points to canonical kernel |
| **Civilizational demo** | `mcp/server.py` | 6 tools | Markets, energy, food security domains |

**Packaging rule:** `internal/monolith.py` is the canonical kernel. `server.py` preserves external boot paths. `mcp/server.py` is a separate cross-domain demo surface.

---

## 13 Canonical Primitives

| Primitive | Modes | Dimension | Temporal Axis |
|-----------|-------|-----------|---------------|
| `wealth_future_value` | `npv`, `irr`, `pi`, `payback` | Time-Discounted Projection | **Future** |
| `wealth_present_expect` | — | Probability-Weighted EMV | **Present** |
| `wealth_future_simulate` | — | Stochastic Projection (Monte Carlo) | **Future** |
| `wealth_info_value` | `evoi`, `evoi_mc` | Expected Value of Information | **Future** |
| `wealth_truth_validate` | `schema`, `correlation`, `entropy` | Epistemic Integrity | **Present** |
| `wealth_survival_liquidity` | `cashflow`, `velocity`, `triage` | Survival Liquidity | **Present** |
| `wealth_survival_leverage` | `dscr`, `networth` | Structural Load + Balance Sheet | **Present** |
| `wealth_rule_enforce` | `floors`, `policy` | Governance Constraint F1–F13 | **Present** |
| `wealth_allocate_optimize` | `kernel`, `personal`, `agent` | Capital Allocation Brain | **Future** |
| `wealth_game_coordinate` | `equilibrium`, `game` | Multi-Agent Dynamics | **Future** |
| `wealth_sense_ingest` | `fetch`, `snapshot`, `sources`, `health`, `vintage`, `reconcile` | Reality Intake | **Cross-temporal** |
| `wealth_past_record` | `init`, `transaction`, `portfolio` | Memory & Audit Trail | **Past** |
| `wealth_future_steward` | — | Long-Horizon Planetary Boundaries | **Future** |

---

## Capital Scales

```
personal → household → sme → enterprise → national → crisis → civilization → agentic
```

Every scale has different risk tolerance, time horizon, and dignity constraints. WEALTH evaluates all of them under the same constitutional floors.

---

## arifOS Federation

arifOS is part of a federated AI governance system. Each organ has a narrow responsibility so no single agent becomes uncontrolled, unaccountable, or self-authorizing.

| Organ | Human Meaning | System Role | Docs |
|---|---|---|---|
| **ARIF / APEX** | Final human authority | F13 sovereign veto, approval, override, terminal judgment | [arif-fazil.com](https://arif-fazil.com) |
| **AAA** | Operator cockpit | Identity, A2A federation gateway, session control, agent supervision | [README](https://github.com/ariffazil/AAA) |
| **A-FORGE** | Execution shell | Runs tools, performs dry-runs, executes approved actions, reports outcomes | [README](https://github.com/ariffazil/A-FORGE) |
| **arifOS** | Governance kernel | Checks evidence, risk, authority, verdicts, and auditability before action | [README](https://github.com/ariffazil/arifOS) |
| **GEOX** | Earth intelligence | Seismic, petrophysics, basin, subsurface, and physics-grounded evidence | [README](https://github.com/ariffazil/geox) |
| **WEALTH** | Capital intelligence | NPV, IRR, EMV, risk scoring, crisis triage, economic judgment | [README](https://github.com/ariffazil/wealth) |
| **WELL** | Human readiness mirror | Operator pressure, biological state, cognitive load, human-system safety | [README](https://github.com/ariffazil/well) |
| **Ω-Wiki** | Knowledge base | Persistent compiled knowledge, doctrine, references, and memory surfaces | [wiki.arif-fazil.com](https://wiki.arif-fazil.com) |

### How the organs work together

A governed action should not move directly from prompt to execution.

```
Human / Agent request
→ AAA identifies the session
→ arifOS judges the request
→ GEOX / WEALTH / WELL provide domain evidence when needed
→ A-FORGE executes only approved actions
→ VAULT999 records the receipt
→ APEX / Human can veto at any time
```

> **AAA controls the session. arifOS judges. Domain organs provide evidence. A-FORGE executes. VAULT999 records. The human remains sovereign.**

---

## Live Sites

| Surface | URL |
|---------|-----|
| WEALTH | https://wealth.arif-fazil.com/ |
| arifOS Doctrine | https://arifos.arif-fazil.com/ |
| Human | https://arif-fazil.com/ |

*Capital is not money. Capital is stored choice. WEALTH prices the choice before arifOS seals it.*
*DITEMPA BUKAN DIBERI — Epistemic capital sovereignty is forged, not given.*
