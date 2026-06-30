<!-- mcp-name: ariffazil/arifos -->

<div align="center">

```
   █████╗ ██████╗ ██╗███████╗ ██████╗ ███████╗
  ██╔══██╗██╔══██╗██║██╔════╝██╔═══██╗██╔════╝
  ███████║██████╔╝██║█████╗  ██║   ██║███████╗
  ██╔══██║██╔══██╗██║██╔══╝  ██║   ██║╚════██║
  ██║  ██║██║  ██║██║██║     ╚██████╔╝███████║
  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝      ╚═════╝ ╚══════╝

  Constitutional AI Governance Kernel
  ─────────────────────────────────────────
  Not a chatbot. Not a model wrapper. The LAW.
```

**DITEMPA BUKAN DIBERI** — *"Forged, Not Given."*

</div>

[![CI](https://github.com/ariffazil/arifos/actions/workflows/01-unified-ci.yml/badge.svg)](https://github.com/ariffazil/arifos/actions/workflows/01-unified-ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-3776AB?logo=python)](https://pypi.org/project/arifos/)
[![MCP](https://img.shields.io/badge/MCP-10%20verbs%20public-10b981)](https://mcp.arif-fazil.com/mcp)
[![Floors](https://img.shields.io/badge/floors-F1–F13%20active-f59e0b)](arifosmcp/core/floors.py)
[![License](https://img.shields.io/badge/license-AGPL--3.0-ef4444)](LICENSE)
[![Federation](https://img.shields.io/badge/federation-7%20organs%20alive-8B5CF6)](FEDERATION_STATUS.md)
[![PyPI](https://img.shields.io/pypi/v/arifos?label=pypi)](https://pypi.org/project/arifos/)
[![Glama](https://img.shields.io/badge/Glama-arifOS-8A2BE2)](https://glama.ai/mcp/servers/ariffazil/arifos)
[![Smithery](https://img.shields.io/badge/Smithery-arifOS-FF6B35)](https://smithery.ai/server/ariffazil/arifos)
[![mcp.so](https://img.shields.io/badge/mcp.so-arifOS-00BFFF)](https://mcp.so/servers/ariffazil/arifos)

---

## 1. What Is arifOS?

> **arifOS is a constitutional governance kernel that sits between AI agents and their tools, enforcing 13 floors before any irreversible action.**

- **The law layer** — decides what agents must NOT do, so they can be trusted with what they CAN do
- **An MCP server** — 10 public verbs. Agents call `arif_init` → `arif_judge` → `arif_seal`
- **A federation hub** — 7 organs (arifOS, A-FORGE, GEOX, WEALTH, WELL, AAA, VAULT999) under one contract
- **An immutable ledger** — VAULT999: append-only, hash-chained. Every decision sealed forever
- **Built for one sovereign** — Muhammad Arif bin Fazil. F13 veto is absolute

**What it is NOT:** an AI model, a chatbot, a startup, LangChain/CrewAI/AutoGen, or a replacement for human judgment.

---

## 2. Quick Start

### Human Operators
You don't install arifOS. You interact through:
- **AAA Cockpit:** https://aaa.arif-fazil.com
- **Hermes Telegram:** `@ASI_arifos_bot`
- **Health check:** https://arifos.arif-fazil.com/health

### AI Agents (MCP Clients)
```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://mcp.arif-fazil.com/mcp",
      "transport": "streamable-http"
    }
  }
}
```

### Developers
```bash
pip install arifos                          # from PyPI
# or
git clone git@github.com:ariffazil/arifos.git && cd arifOS
uv sync --frozen
python -m arifosmcp.server                   # starts on :8088
curl http://127.0.0.1:8088/health            # verify
python -m pytest tests/ -q --tb=short        # 4,400+ tests
```

---

## 3. The 10 Public Tools

Every governed action follows the golden path. 888 is the gate. 999 is the seal.

| # | Tool | Stage | What It Does |
|---|------|-------|---------------|
| 1 | `arif_init` | 000 | Start constitutional session. Always first. |
| 2 | `arif_observe` | 111 | Gather evidence — web search, URL fetch, system vitals |
| 3 | `arif_think` | 333 | Reason, plan, critique, verify — multi-step cognition |
| 4 | `arif_route` | 444 | Route intent to the correct federation organ |
| 5 | `arif_judge` | 888 | Constitutional verdict — SEAL / HOLD / SABAR / VOID |
| 6 | `arif_act` | 900 | Execute only if 888 issued SEAL |
| 7 | `arif_seal` | 999 | Append to immutable VAULT999 ledger |
| 8 | `arif_resolve_tool` | — | Resolve tool name to canonical form |
| 9 | `arif_vault_query` | — | Query the VAULT999 audit ledger |
| 10 | `arif_conformance_report` | — | Full 9-check constitutional spine proof |

```
000 ──→ 111 ──→ 333 ──→ 444 ──→ 888 ──→ 900 ──→ 999
init    observe  think   route   judge   act     seal
```

**The iron rule:** No action skips 888. No organ self-authorizes.

---

## 4. The 13 Constitutional Floors

Every tool call passes through these. Hard floors block. Soft floors warn.

| # | Floor | Type | Rule |
|---|-------|------|------|
| **F1** | AMANAH | HARD | Reversible first. Irreversible → 888 HOLD |
| **F2** | TRUTH | HARD | P(truth) ≥ 0.99. Fabrication = VOID |
| **F3** | WITNESS | DERIVED | Multi-party consensus required for high-blast actions |
| **F4** | CLARITY | HARD | Every output must reduce entropy (ΔS ≤ 0) |
| **F5** | PEACE² | SOFT | Non-destructive power. Harm potential < 0.30 |
| **F6** | EMPATHY | SOFT | Protect weakest stakeholder |
| **F7** | HUMILITY | HARD | Cap confidence at 0.90. No fake certainty |
| **F8** | GENIUS | DERIVED | Complex actions need high signal |
| **F9** | ANTIHANTU | HARD | No deception, manipulation, or consciousness claims |
| **F10** | ONTOLOGY | HARD | AI is instrument. No soul, no feelings |
| **F11** | AUDIT | HARD | Every decision logged and inspectable |
| **F12** | RESILIENCE | HARD | Injection defense. Risk bounded |
| **F13** | SOVEREIGN | HARD | Human veto FINAL. Strongest floor |

**HARD violation → VOID.** Action blocked. **SOFT tension → CAUTION/HOLD.** Human review. **DERIVED → informational only.**

Full spec: `static/arifos/theory/000/000_CONSTITUTION.md`

---

## 5. Federation Architecture

arifOS is the kernel. Six organs serve under it. Two edge agents interface with the world.

```
                         ┌──────────────────────┐
                         │  Arif (F13 SOVEREIGN) │
                         └──────────┬───────────┘
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       │                            │                            │
  ┌────▼─────┐              ┌───────▼───────┐            ┌───────▼───────┐
  │  Hermes  │              │      AAA      │            │   OpenClaw    │
  │  🧠 :8644│              │  🖥️  :3001    │            │   🤖 :18789   │
  │ Telegram │              │   Cockpit     │            │  Transport    │
  └──────────┘              └───────────────┘            └───────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │    arifOS (Ω)        │
                         │    Kernel :8088      │
                         │    F1-F13 · 888 JUDGE│
                         └──┬───┬───┬───┬──────┘
                            │   │   │   │
          ┌─────────────────┼───┼───┼───┼─────────────────┐
          │                 │   │   │   │                 │
    ┌─────▼────┐   ┌───────▼┐ ┌▼─────┐ ┌▼────────┐  ┌────▼─────┐
    │  GEOX    │   │WEALTH  │ │ WELL │ │A-FORGE  │  │ VAULT999 │
    │  🌍 :8081│   │💰:18082│ │🫀:18083│ │⚒️:7071  │  │ 🔒 Seal  │
    │ Evidence │   │Compute │ │Reflect│ │Execute  │  │ Immutable│
    └──────────┘   └────────┘ └──────┘ └─────────┘  └──────────┘
```

| Organ | Port | Role | Must Never |
|-------|------|------|------------|
| **arifOS** | 8088 | Constitutional kernel | Self-authorize |
| **GEOX** | 8081 | Earth intelligence | Authorize drilling |
| **WEALTH** | 18082 | Capital intelligence | Allocate capital |
| **WELL** | 18083 | Human readiness | Make medical diagnoses |
| **AAA** | 3001 | Control plane / cockpit | Issue constitutional verdicts |
| **A-FORGE** | 7071/7072 | Execution shell | Self-authorize |
| **VAULT999** | — | Immutable audit ledger | Edit or delete records |
| **Hermes** | 8644 | Telegram MIND edge | Issue constitutional verdicts |
| **OpenClaw** | 18789 | Transport HANDS edge | Issue constitutional verdicts |

**Authority chain:** Arif → AAA/Hermes → arifOS kernel → Domain organs → A-FORGE → VAULT999

---

## 6. Build, Test, Deploy

```bash
# Development
uv sync --frozen
python -m arifosmcp.server
python -m pytest tests/ -q --tb=short        # 4,400+ tests
ruff check . && ruff format .

# Deploy to VPS
make deploy-local                             # rsync + systemd restart
systemctl status arifos

# Docker
docker build -t ghcr.io/ariffazil/arifos:latest .
```

---

## 7. MCP Connection Guide

### Public Endpoint
```
https://mcp.arif-fazil.com/mcp
```
Transport: `streamable-http`. Initialize session first, then call tools.

### Internal Organs
| Organ | Endpoint | When to use |
|-------|----------|-------------|
| **arifOS** | `localhost:8088` | Governance, judgment, routing |
| **A-FORGE** | `localhost:7071` | Build, deploy, filesystem, git, docker |
| **GEOX** | `localhost:8081` | Seismic, wells, petrophysics |
| **WEALTH** | `localhost:18082` | NPV, risk, capital flow |
| **WELL** | `localhost:18083` | Vitality, readiness, dignity |

**Rule:** arifOS judges → A-FORGE executes → VAULT999 records. Never skip the chain.

### Federation Context (read all 3 for full picture)

| Read this | For | Link |
|-----------|-----|------|
| **arifOS** (this repo) | Constitutional kernel. 10 verbs. 13 floors. The judge. | ← you are here |
| **A-FORGE** | Executor. 75 MCP tools. Gates + A-THINK law. | [`ariffazil/A-FORGE`](https://github.com/ariffazil/A-FORGE) |
| **AAA** | Cockpit. A2A mesh. Agent registry. React 19 dashboard. | [`ariffazil/AAA`](https://github.com/ariffazil/AAA) |

---

## 8. License & Sovereignty

**AGPL-3.0.** The constitution must remain open. The kernel must remain inspectable.

**Muhammad Arif bin Fazil** is F13 SOVEREIGN. His veto is absolute. No algorithm overrides. No agent bypasses. No institution supersedes.

---

<div align="center">

```
arifOS · Port 8088 · 10 public verbs · 13 floors · 7 organs
AGPL-3.0 · Sovereign: Arif Fazil · Federation: ALIVE
DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
```

</div>
