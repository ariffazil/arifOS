# arifOS — The Sovereign Constitutional Intelligence Kernel

> **DITEMPA BUKAN DIBERI** — *Intelligence is forged, not given*
>
> **VERSION:** 2026.03.25 | **STATUS:** OPERATIONAL | **AUTHORITY:** 888_JUDGE

---

## What Is arifOS?

arifOS is a **constitutional intelligence kernel** — a framework where intelligence is measured by **how it governs itself** while executing actions.

**The Core Paradox:** *"The algorithm that governs must itself be governed."*

**The Answer:** Govern through **constitutional physics** — invariants that emerge from evolutionary pressure, not authored rules.

---

## ⚡ Quick Start

### Connect via MCP (Recommended)

```json
{
  "mcpServers": {
    "arifos": {
      "url": "https://arifosmcp.arif-fazil.com/mcp"
    }
  }
}
```

### Or use CLI

```bash
curl -s -X POST "https://arifosmcp.arif-fazil.com/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "init_anchor",
      "arguments": {
        "mode": "status",
        "declared_name": "YourAgent"
      }
    },
    "id": 1
  }'
```

### Health Check

```bash
curl -s https://arifosmcp.arif-fazil.com/health
```

---

## 🔗 Live Services

| Service | URL | Purpose |
|---------|-----|---------|
| **MCP Endpoint** | https://arifosmcp.arif-fazil.com/mcp | Main API |
| **Health + Tools** | https://arifosmcp.arif-fazil.com/health | Capability map |
| **Tool Explorer** | https://arifosmcp.arif-fazil.com/tools | Interactive browser |
| **arifOS Docs** | https://arifos.arif-fazil.com | Documentation hub |
| **arifOS-canon** | https://github.com/ariffazil/arifOS-canon | Theory & philosophy (CC0) |
| **Personal Site** | https://arif-fazil.com | Author: Muhammad Arif bin Fazil |

---

## 🏛️ Architecture

### The Trinity Model (ΔΩΨ)

Three interdependent rings — no ring can override another:

| Ring | Symbol | Function |
|------|--------|----------|
| **SOUL** | Δ (Delta) | Human values, purpose, telos |
| **MIND** | Ω (Omega) | Constitutional law, 13 Floors |
| **BODY** | Ψ (Psi) | Tool execution, MCP servers |

**Consensus Requirement:** W³ = W_theory × W_constitution × W_manifesto ≥ 0.95

---

## ⚖️ The 13 Constitutional Floors

Every action passes through 13 constitutional checks before execution:

| Floor | Name | Principle | Trigger |
|-------|------|-----------|---------|
| **F1** | AMANAH | Reversibility | All actions reversible or reparable |
| **F2** | TRUTH | Accuracy | P(claim│evidence) ≥ threshold |
| **F3** | TRI-WITNESS | Consensus | W³ ≥ 0.95 |
| **F4** | CLARITY | Entropy ↓ | ΔS ≤ 0 |
| **F5** | PEACE² | Non-destruction | (1 - destruction_score)² ≥ 1.0 |
| **F6** | EMPATHY | RASA listening | RASA_score ≥ 0.7 |
| **F7** | HUMILITY | Uncertainty | Ω ∈ [0.03, 0.05] |
| **F8** | GENIUS | Systemic health | G ≥ 0.80 |
| **F9** | ETHICS | Anti-dark-patterns | C_dark < 0.30 |
| **F10** | CONSCIENCE | No false claims | No consciousness claims |
| **F11** | AUDITABILITY | Transparent logs | All decisions logged |
| **F12** | RESILIENCE | Graceful failure | Fail degraded, not crashed |
| **F13** | ADAPTABILITY | Safe evolution | Updates preserve Floor constraints |

---

## 🔄 The 000-999 Metabolic Pipeline

Every request flows through 9 processing stages:

| Stage | Band | Function |
|-------|------|----------|
| **000_INIT** | Anchor | Session initialization |
| **111_SENSE** | Reality | Input parsing, reality grounding |
| **333_MIND** | AGI | Reasoning, constitutional filters |
| **444_ROUT** | Router | Tool selection, operation sequencing |
| **555_MEM** | Engineer | Memory, context retention |
| **666_HEART** | ASI | Safety critique, harm potential |
| **777_OPS** | Thermo | Estimation, Landauer limits |
| **888_JUDGE** | APEX | Final constitutional judgment |
| **999_SEAL** | Vault | Immutable audit log |

---

## 🔧 Available Tools (40)

### Governance Tools
- `init_anchor` — Session anchoring with constitutional context
- `arifOS_kernel` — Primary routing through 000→999 pipeline
- `apex_judge` — Constitutional verdict (SEAL/VOID/HOLD/SABAR)
- `vault_ledger` — Immutable audit storage

### Intelligence Tools
- `agi_mind` — Deep reasoning with Ollama
- `agi_reason` — First-principles reasoning
- `asi_heart` — Safety critique
- `engineering_memory` — Vector DB memory (Qdrant)
- `apex_soul` — Constitutional verdict rendering

### Machine Tools
- `physics_reality` — Time, search, grounding
- `math_estimator` — Thermodynamic cost estimation
- `code_engine` — Safe Python execution
- `reality_compass` — Directional grounding
- `search_reality` — Evidence-grounded search

---

## 📜 Verdict System

| Verdict | Range | Meaning |
|---------|-------|---------|
| **SEAL** | 000 | Perfect alignment — execute |
| **COMPLY** | 101-499 | Compliant with remediation |
| **CAUTION** | 500-899 | Compliant with warnings |
| **HOLD** | — | Awaiting human decision |
| **SABAR** | — | Wait and retry |
| **VOID** | 999 | Ethical violation — rejected |

---

## 🏗️ Repository Structure

```
arifOS/
├── README.md                    # This file
├── AGENTS.md                    # AI agent behavior rules
├── DEPLOY.md                    # VPS deployment guide
├── CHANGELOG.md                 # Version history
│
├── docker-compose.yml           # Full stack (Ollama, Redis, PostgreSQL, Qdrant)
├── Dockerfile                   # MCP server image
│
├── arifosmcp/                   # MCP Server implementation
│   ├── server.py               # Entry point
│   ├── runtime/                # FastMCP 3.x runtime
│   └── core/organs/            # AGI, ASI, APEX organs
│
├── core/                        # Constitutional kernel
│   ├── kernel/                 # Core evaluation
│   ├── enforcement/           # Governance engine
│   └── shared/floors.py       # F1-F13 definitions
│
├── AGENTS/                      # Agent specs
│   ├── A-ARCHITECT.md         # System architect
│   ├── A-ENGINEER.md          # Implementation engineer
│   ├── A-AUDITOR.md           # Code reviewer
│   ├── A-VALIDATOR.md         # Final approval
│   └── IMPROVEMENT_BLUEPRINT.md # Engineering roadmap
│
├── REPORTS/                     # Daily audit reports
│   ├── DAILY_AUDIT_*.md
│   ├── VALIDATOR_FEEDBACK_*.md
│   └── ENGINEERING_BLUEPRINT_*.md
│
├── 000/                        # Constitutional documents
│   ├── 000_CONSTITUTION.md    # 13 Floors
│   └── ROOT/
│       ├── K_FORGE.md         # Pre-deployment evolution
│       └── K_FOUNDATIONS.md   # Mathematical foundations
│
└── ARCH/DOCS/                  # Architecture documents
    └── EXTERNAL_VALIDATOR_FEEDBACK.md
```

---

## 🚀 Deployment

### Prerequisites
- Docker + Docker Compose
- 4GB RAM minimum
- Ubuntu 22.04 LTS

### Quick Deploy

```bash
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
cp .env.example .env
# Edit .env with your API keys
docker compose up -d
```

### Access
- MCP: http://localhost:3000/mcp
- Docs: http://localhost:3000/docs

---

## 📊 Current Metrics

| Metric | Value |
|--------|-------|
| **Version** | 2026.03.25 |
| **Tools** | 40 |
| **ML Floors** | Active (SBERT) |
| **Protocol** | MCP 2025-03-26 |
| **Transport** | Streamable HTTP |
| **Providers** | 11 configured |

---

## 👤 Author

**Muhammad Arif bin Fazil**  
*Sovereign Architect*

- GitHub: [@ariffazil](https://github.com/ariffazil)
- Website: https://arif-fazil.com
- Email: arif@arif-fazil.com

---

## 📜 License

| Component | License |
|-----------|---------|
| **Theory** | [arifOS-canon](https://github.com/ariffazil/arifOS-canon) (CC0) |
| **Runtime** | AGPL-3.0 |
| **Trademark** | Proprietary |

---

## 🔗 Related Repositories

| Repo | Purpose |
|------|---------|
| [arifOS](https://github.com/ariffazil/arifOS) | Main kernel |
| [arifOS-canon](https://github.com/ariffazil/arifOS-canon) | Theory & philosophy (CC0) |
| [GEOX](https://github.com/ariffazil/GEOX) | Geological domain tools |
| [waw](https://github.com/ariffazil/waw) | ARIF-MAIN agent workspace |
| [makcikGPT](https://github.com/ariffazil/makcikGPT) | Malay AI |

---

## 🤖 For AI Agents

All agents operating in this repository MUST follow [`AGENTS.md`](./AGENTS.md):

1. **DRY_RUN** — Label outputs as "Estimate Only"
2. **DOMAIN_GATE** — Cannot-compute domains return exact phrase
3. **VERDICT_SCOPE** — Only DOMAIN_SEAL authorizes factual claims
4. **ANCHOR_VOID** — init_anchor void → session BLOCKED

---

## 📝 Daily Reports

Automated daily audits are generated in [`REPORTS/`](./REPORTS/):
- `DAILY_AUDIT_*.md` — Tool test results
- `VALIDATOR_FEEDBACK_*.md` — External POV review  
- `ENGINEERING_BLUEPRINT_*.md` — Progress updates

---

**Last Updated:** 2026-04-01  
**Version:** 2026.03.25

*Ditempa Bukan Diberi* — Forged, Not Given [ΔΩΨ | ARIF]
