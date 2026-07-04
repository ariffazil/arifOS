<!-- SOT-MANIFEST
owner: Arif
last_verified: 2026-06-04
valid_from: 2026-05-26
valid_until: 2026-06-26
confidence: high
scope: /root/WEALTH
epistemic_status: CLAIM
-->

# WEALTH — Capital Intelligence & Resource Stewardship

> **WEALTH is the capital intelligence organ of the arifOS federation.** It computes value — NPV, IRR, risk scores, portfolio allocation, sovereign resource economics — and enforces constitutional rules that prevent AI from overstating returns, hiding downside risk, or authorizing resource allocation without human approval. It computes. It models. It never allocates alone.

> **In one sentence:** WEALTH is the financial brain of the federation — when any agent or decision needs a capital computation (NPV, cash flow, risk, game theory, civilizational boundary), WEALTH is the governed engine that runs it.

**Status:** OPERATIONAL | **Organ:** CAPITAL (Ω-WEALTH)
**Domain:** `wealth.arif-fazil.com`
**MCP endpoint:** `https://wealth.arif-fazil.com/mcp`
**Port:** 18082 (organ-standard; aligns with GEOX 18081)
**Governance wrapper:** ACTIVE ✅ (`[GOVERNANCE] WEALTH governance wrapper active — arifOS F1-F13`)
**systemd service:** `wealth-organ.service` (enabled, running)

---

## What This Is

WEALTH applies thermodynamic physics to capital systems. Heat flows from hot to cold; capital flows toward higher returns — but only under governed conditions. WEALTH models, quantifies, and governs that flow across 12 orthogonal dimensions.

**It owns:** Financial calculations, capital flow modeling, risk quantification, economic constraint analysis, civilizational boundary monitoring, inequality diagnosis.
**It does NOT own:** Constitutional judgment (→ arifOS), geoscience (→ GEOX), execution (→ A-FORGE).

---

## The 12 Ω-WEALTH Dimensions

Every capital question maps to one or more of these 12 thermodynamic dimensions:

| Ω | Dimension | Physics Analogy | Key Tool |
|---|-----------|----------------|----------|
| Ω-00 | Synthesis | Master field equation | `wealth_synthesize` |
| Ω-01 | Conservation | Mass conservation (assets, liabilities) | `wealth_conservation_capital` |
| Ω-02 | Flow | Mass flow rate (cashflow, burn, runway) | `wealth_flow_liquidity` |
| Ω-03 | Gradient | Pressure differential (mispricing) | `wealth_gradient_price` |
| Ω-04 | Entropy | Disorder (risk, uncertainty, tail risk) | `wealth_entropy_risk` |
| Ω-05 | Energy | Output per input (productivity, efficiency) | `wealth_energy_productivity` |
| Ω-06 | Time | Potential well decay (NPV, IRR, payback) | `wealth_time_discount` |
| Ω-07 | Inertia | Structural load (leverage, DSCR, fragility) | `wealth_inertia_leverage` |
| Ω-08 | Field | External environment (rates, FX, energy, carbon) | `wealth_field_macro` |
| Ω-09 | Signal | Evidence quality (information value, PoS) | `wealth_signal_information` |
| Ω-10 | Game | Multi-agent equilibrium (Nash, bargaining) | `wealth_game_coordination` |
| Ω-11 | Boundary | Constitutional floors (maruah, stewardship) | `wealth_boundary_governance` |
| Ω-12 | Hysteresis | Path dependence (ledger memory, sealed state) | `wealth_hysteresis_ledger` |

**Start with `wealth_synthesize` (Ω-00)** — it auto-selects and runs the relevant dimensions for your question.

---

## 44 Live MCP Tools

```
Public MCP surface:           38 tools
Internal aliases / hidden:    34 (registered, not exposed)
Total @mcp.tool decorators:   72
```

| Tool | Ω | What It Does |
|------|---|-------------|
| `wealth_synthesize` | 00 | Master verdict — routes all dimensions, returns SEAL/SABAR/VOID |
| `wealth_conservation_capital` | 01 | Balance sheet: assets, liabilities, net position |
| `wealth_flow_liquidity` | 02 | Cash flow, burn rate, runway calculation |
| `wealth_gradient_price` | 03 | Price differential, mispricing detection, spread alerts |
| `wealth_entropy_risk` | 04 | Risk distribution, tail risk (CVaR), uncertainty map |
| `wealth_energy_productivity` | 05 | Return on capital, PI, productivity index |
| `wealth_time_discount` | 06 | NPV, IRR, payback, time-value-of-money |
| `wealth_inertia_leverage` | 07 | DSCR, leverage stress test, structural fragility |
| `wealth_field_macro` | 08 | Live macro data: Brent, MYR/USD, Malaysia GDP, inflation |
| `wealth_signal_information` | 09 | Evidence quality score, PoS for E&P wells (wildcat/appraisal/dev) |
| `wealth_game_coordination` | 10 | Game theory: Nash equilibria for multi-party deals (PSC, sovereign) |
| `wealth_boundary_governance` | 11 | Constitutional floor compliance, maruah dignity score |
| `wealth_hysteresis_ledger` | 12 | Path-dependent capital state, sealed financial memory |
| `wealth_inequality_kernel` | IEQ | 5-dimension inequality diagnosis (pass `preset='malaysia'` for live WB data) |
| `wealth_sensor_snapshot` | 08 | Multi-source macro snapshot (ECB, FRED, OWID, Ember, WorldBank) |
| `wealth_stewardship_civilization` | Future | Long-horizon planetary boundary + civilization continuity |
| `wealth_health_check` | System | Federation health probe |

---

## Architecture

```
Capital Question
        ↓
┌──────────────────────────────────────────┐
│  wealth_synthesize (Ω-00 Master)         │  ← Start here for any question
│  Auto-selects relevant Ω dimensions      │    Returns unified SEAL/SABAR/VOID
└─────────────────┬────────────────────────┘
                  ↓
┌──────────────────────────────────────────┐
│  Ω-01 through Ω-12 Dimension Tools      │  ← Or call directly for specific analysis
│  (NPV, DSCR, game theory, entropy...)   │
└─────────────────┬────────────────────────┘
                  ↓
┌──────────────────────────────────────────┐
│  888_JUDGE Gate (via arifOS)             │  ← Constitutional verdict on capital action
│  SEAL / SABAR / HOLD / VOID             │
└─────────────────┬────────────────────────┘
                  ↓
┌──────────────────────────────────────────┐
│  VAULT999 Immutable Record               │  ← Audit trail sealed forever
└──────────────────────────────────────────┘
```

---

## The Runtime — What to Use and Why

### Python Kernel (canonical — use this for everything)

The canonical kernel lives in **`internal/monolith.py`**:

```
internal/
└── monolith.py    ← ~11,871 lines — ALL 38 live tools + all Ω logic
                      This is THE kernel. One file by design.
```

The 12 Ω-dimensions are deeply mathematically coupled (NPV feeds IRR feeds risk entropy). Splitting them creates circular imports and breaks the physics invariants. The monolith is intentional architecture, not technical debt.

**`server.py` at root** = 15-line backward-compatibility shim only:
```python
# server.py (the whole file)
from internal.monolith import mcp
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

**`mcp/server.py`** = cross-domain demo surface exposing 6 tools — not production.

### Node.js Kernel (legacy JS)

The `host/kernel/` directory contains a legacy JS kernel (`floors.js`, `finance.js`, `seal.js`). Used by `cli.js` and the JS test suite for numerical parity validation. Not the primary execution path.

---

## Quick Start

```bash
# Install Python side
pip install -e .

# Start MCP server (port 18082) — use monolith directly
python internal/monolith.py

# Or via the wrapper (same result)
python server.py

# Stdio mode (local agents — Claude Code, OpenCode, Continue CLI)
python internal/monolith.py --transport stdio
# or
MCP_TRANSPORT=stdio python internal/monolith.py

# Install Node.js side (for legacy CLI tools)
npm install

# Run JS tests (NPV, IRR, DSCR numerical parity checks)
npm test

# CLI operations
npm run boot    # Initialize capital state
npm run check   # Run health checks
npm run seal    # Seal session to VAULT999

# Docker
docker build -t wealth .
docker run -p 18082:18082 wealth
```

### Connect via Claude Desktop / Agent Config

**HTTP (public or local):**

```json
{
  "mcpServers": {
    "wealth": {
      "type": "http",
      "url": "https://wealth.arif-fazil.com/mcp"
    }
  }
}
```

**Stdio (local-only, no token, no port):**

```json
{
  "mcpServers": {
    "wealth": {
      "command": "python3",
      "args": ["internal/monolith.py", "--transport", "stdio"],
      "cwd": "/root/WEALTH"
    }
  }
}
```

---

## Repository Structure

```
WEALTH/
│
├── internal/
│   └── monolith.py            # THE CANONICAL KERNEL — 17 live tools, all Ω math
│
├── server.py                  # 15-line backward-compat shim → imports monolith
│
├── host/                      # Modular libraries (internal deps of monolith)
│   ├── coordination/          # LP allocator, cooperative/strategic/commons protocols
│   ├── epistemic/             # Correlation guard, EVOI calculator, schema validator
│   ├── governance/            # Floor hooks, policy engine, vault bridge
│   ├── ingest/                # Data adapters: ECB, FRED, OWID, Ember, WorldBank
│   ├── kernel/                # JS legacy: floors.js, finance.js, seal.js, vault999.js
│   └── wealth/                # JS: cashflow, networth, projection, maruah-score
│
├── civilizational/            # Boundary monitors (Calhoun sink, extractive drift)
├── canon/                     # Constitutional specs (13 Markdown files)
├── mcp/
│   └── server.py              # Cross-domain demo — 6 tools only (not production)
│
├── tests/                     # Python pytest + Node.js node:test
├── docs/                      # Architecture, operations
│
├── pyproject.toml             # Python packaging (PROPRIETARY license)
├── package.json               # Node.js packaging
└── cli.js                     # Node CLI: boot, check, seal, capitalx
```

---

## For Agentic Coders: How to Extend

### Add a new Ω dimension tool

1. Add the function to `internal/monolith.py` with `@mcp.tool` decorator:

```python
@mcp.tool
async def wealth_my_new_tool(
    input_value: float,
    mode: str = "compute",
) -> dict:
    """
    Ω-XX: My New Dimension — what this computes.
    
    Physics analogy: This is like [physical analogy here].
    """
    # computation
    result = compute_something(input_value)
    
    return {
        "verdict": "SEAL",
        "dimension": "Ω-XX",
        "payload": {"result": result},
        "epistemic_status": "CLAIM",
        "audit_trail": {"input": input_value, "mode": mode}
    }
```

2. If it involves capital allocation, route the final verdict through arifOS `arif_judge_deliberate`
3. Add tests in `tests/`

### Use `wealth_synthesize` as your entry point

For any capital question, call `wealth_synthesize` first. Pass a `question` and relevant `context`. It routes to the correct Ω dimensions and returns a unified verdict:

```python
result = await wealth_synthesize(
    question="Is this offshore development project value-accretive for Malaysia?",
    scale_mode="sovereign",
    actors=["NOC", "Partner", "Federal", "State"],
    context={"foreign_entity": True, "reversible": False}
)
```

### GEOX ↔ WEALTH Integration

GEOX feeds prospect economics to WEALTH for POS/EMV calculations:

```python
# GEOX provides: geox_prospect_evaluate → prospect_ref + ac_risk_score
# WEALTH consumes: wealth_signal_information(well_type="wildcat", pos=0.25)
# Then: wealth_expectation_emv(pos, gross_resources_mmboe, oil_price)
```

---


---

## TREE777 Wiki

Full architecture documentation and Ω-dimension theory:
→ **https://wiki.arif-fazil.com**

---

## 🏛️ Federation

| Organ | Repository | Role | Port |
|-------|-----------|------|------|
| **arifOS** | [ariffazil/arifOS](https://github.com/ariffazil/arifOS) | Constitutional Kernel · F1-F13 | 8088 |
| **AAA** | [ariffazil/AAA](https://github.com/ariffazil/AAA) | Reality Console · A2A Gateway | 3001 |
| **A-FORGE** | [ariffazil/A-FORGE](https://github.com/ariffazil/A-FORGE) | Execution Shell | 7071 |
| **GEOX** | [ariffazil/geox](https://github.com/ariffazil/geox) | Earth Intelligence | 8081 |
| **WEALTH** | [ariffazil/wealth](https://github.com/ariffazil/wealth) | Capital Intelligence | 18082 |
| **WELL** | [ariffazil/well](https://github.com/ariffazil/well) | Human Readiness | 18083 |
| **arif-sites** | [ariffazil/arif-sites](https://github.com/ariffazil/arif-sites) | Public Surfaces | 443 |

> **Constitutional authority:** F1-F13 floors, 888_JUDGE, and VAULT999 live in `ariffazil/arifOS`.  
> **Live federation status:** See `ariffazil/arifOS/FEDERATION_STATUS.md`.
## 📄 Contributing

This repository operates under the arifOS Federation constitution (F1–F13).  
See [AGENTS.md](AGENTS.md) for the canonical boot sequence and agent operating rules.

## 📜 License

AGPL-3.0. See [LICENSE](LICENSE).

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given.



> **Evidence Contract.** This organ emits the standard envelope (epistemic_tag, evidence_quality, source_attribution, uncertainty_band, delta_S) per [arifOS 000_CONSTITUTION.md](../../arifOS/static/arifos/theory/000/000_CONSTITUTION.md) Appendix B. arifOS reads the envelope and applies L01–L13. This organ does not self-judge.


## Changelog

- **v2026.06.06-LAW-SEAL** (2026-06-06): Constitution unified. arifOS canonical 000_CONSTITUTION.md. 13 Laws (L01-L13) live in arifOS only. Evidence Contract line added. AGENTS.md updated.
