<p align="center">
  <img src="https://raw.githubusercontent.com/ariffazil/arifOS/main/docs/arifOSreadme.png" alt="arifOS - The Constitutional Kernel for AI" width="100%">
</p>

<h1 align="center">arifOS</h1>

<h3 align="center">Safety Seatbelt for AI — Constitutional AI Governance Framework</h3>

<p align="center">
  <strong>Stop AI from lying, faking emotions, or causing harm — without slowing it down.</strong><br>
  <em>"DITEMPA BUKAN DIBERI" — Forged, Not Given</em>
</p>

<p align="center">
  <code style="background: #0d1117; padding: 12px 20px; border-radius: 8px; border: 1px solid #30363d; font-size: 1.1rem;">pip install arifos</code><br>
  <sub>One command. 13 floors. 3 judges. &lt;40ms overhead.</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/v55.1-SEAL-10b981?style=for-the-badge" alt="Version">
  <a href="https://arif-fazil.com/dashboard"><img src="https://img.shields.io/badge/Live_Demo-Try_Now-FF79C6?style=for-the-badge" alt="Demo"></a>
  <a href="https://github.com/ariffazil/arifOS"><img src="https://img.shields.io/github/stars/ariffazil/arifOS?style=for-the-badge&color=32b8c6" alt="Stars"></a>
  <a href="https://pypi.org/project/arifos/"><img src="https://img.shields.io/pypi/v/arifos?style=for-the-badge&color=3b82f6" alt="PyPI"></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Tests-200%2B_passing-10b981?style=for-the-badge" alt="Tests">
  <img src="https://img.shields.io/badge/Latency-<40ms-FF6B6B?style=for-the-badge" alt="Latency">
  <a href="https://github.com/ariffazil/arifOS/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-AGPL_3.0-blue?style=for-the-badge" alt="License"></a>
</p>

<p align="center">
  <a href="#what-is-arifos">What Is It</a> &bull;
  <a href="#quickstart">Quickstart</a> &bull;
  <a href="#the-7-levels">7 Levels</a> &bull;
  <a href="#mcp-server">MCP Server</a> &bull;
  <a href="#how-it-works">How It Works</a>
</p>

---

## What's New in v55.1

- **🔌 MCP Server** — Full Model Context Protocol implementation with 7 canonical tools
- **📡 Streamable HTTP** — Stateless transport for production (MCP spec 2025-03-26+)
- **📚 MCP Resources** — Expose F1-F13 floors and VAULT ledger as read-only resources  
- **💬 MCP Prompts** — 5 reusable constitutional evaluation templates
- **✅ Full Spec Compliance** — outputSchema, annotations, title on all tools
- **🧪 69 Integration Tests** — Comprehensive coverage for all MCP features

---

## What is arifOS?

> **arifOS is a "Constitution for AI"** — a complete operating system with 13 safety rules and 9 balance checks that ensure AI makes decisions respecting human dignity, protecting the vulnerable, and maintaining reversibility.

### The Problem: AI Without Constitution

| Without arifOS | Result | Real Harm |
|----------------|--------|-----------|
| AI tells harsh truths cruelly | Truth without Care = **Cruelty** | Patients lose hope |
| AI optimizes for one metric | Speed without Sustainability = **Theft** | Future generations harmed |
| AI is certain without doubt | Certainty without Doubt = **Dogma** | Wrong decisions persist |
| AI unifies without diversity | Unity without Diversity = **Tyranny** | Minorities oppressed |

### The Solution: Constitutional Balance

arifOS implements **9 Paradoxes** — pairs of values that seem to conflict but must work together:

```
┌─────────────────────────────────────────────────────────┐
│           THE 9 PARADOXES OF arifOS                     │
├─────────────────────────────────────────────────────────┤
│  [1] Truth ↔ Care = Compassionate Truth                 │
│  [2] Clarity ↔ Peace = Clear Peace                      │
│  [3] Humility ↔ Justice = Humble Justice                │
│  [4] Precision ↔ Reversibility = Careful Action         │
│  [5] Hierarchy ↔ Consent = Structured Freedom           │
│  [6] Agency ↔ Protection = Responsible Power            │
│  [7] Urgency ↔ Sustainability = Deliberate Speed        │
│  [8] Certainty ↔ Doubt = Adaptive Conviction            │
│  [9] Unity ↔ Diversity = Coherent Plurality             │
└─────────────────────────────────────────────────────────┘
```

---

## Quickstart

```bash
# Install
pip install arifos

# Run constitutional check
arifos check "Should we deploy this feature?"

# Start MCP server (stdio for Claude/Cursor)
arifos mcp stdio

# Start MCP server (HTTP for remote clients)
arifos mcp sse
```

---

## MCP Server

arifOS v55.1 includes a full **Model Context Protocol** server exposing constitutional governance to any AI client.

### The 7 Canonical Tools

| Tool | Gate | Purpose | Floors Enforced |
|------|------|---------|-----------------|
| **`_init_`** | 000 | Session ignition, identity verification | F1, F11, F12 |
| **`_agi_`** | 111-333 | Mind engine — truth, precision-weighted reasoning | F2, F4, F7, F10 |
| **`_asi_`** | 444-666 | Heart engine — safety, empathy, stakeholder protection | F1, F5, F6, F9 |
| **`_apex_`** | 888 | Soul engine — judgment, 9-paradox equilibrium | F3, F8, F11, F12 |
| **`_vault_`** | 999 | Immutable ledger — Merkle-sealed audit entry | F1, F8 |
| **`_trinity_`** | 000→999 | Full pipeline — all engines in sequence | All F1-F13 |
| **`_reality_`** | External | Fact-checker — external source verification | F7 |

### Client Setup

**Claude Desktop:**
```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "arifos-mcp-stdio",
      "alwaysAllow": ["_init_", "_agi_", "_asi_", "_apex_", "_vault_", "_trinity_", "_reality_"]
    }
  }
}
```

**Cursor IDE:**
```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "arifos-mcp-stdio",
      "env": { "GOVERNANCE_MODE": "HARD" }
    }
  }
}
```

### MCP Resources

Read-only constitutional data:
- `config://floors` — All 13 floor definitions
- `floor://{F1-F13}` — Individual floor details
- `vault://ledger/latest` — Latest sealed decision
- `vault://ledger/stats` — Ledger statistics

### MCP Prompts

Reusable evaluation templates:
- `constitutional_eval` — Full F1-F13 evaluation
- `paradox_analysis` — 9-paradox equilibrium
- `trinity_full` — Complete 000-999 pipeline
- `floor_violation_repair` — SABAR/VOID remediation
- `constitutional_summary` — Quick F1-F13 reference

**Live endpoint:** `https://arif-fazil.com/mcp`

See [codebase/mcp/README.md](codebase/mcp/README.md) for full MCP documentation.

---

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│  USER INPUT                                             │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│  000_INIT — Identity Check + Injection Scan             │
│  Floors: F1 (Reversible), F11 (Authority), F12 (Secure) │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│  111-333_AGI — The Mind (Δ)                             │
│  "Is this true? Is this precise?"                       │
│  Floors: F2 (Truth), F4 (Clarity), F7 (Humility)        │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│  444-666_ASI — The Heart (Ω)                            │
│  "Is this safe? Who is most vulnerable?"                │
│  Floors: F1 (Amanah), F5 (Peace), F6 (Empathy)          │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│  888_APEX — The Soul (Ψ)                                │
│  "Do Mind + Heart + Human agree?"                       │
│  Floors: F3 (Tri-Witness), F8 (Genius)                  │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│  999_VAULT — Immutable Record                           │
│  Merkle-sealed audit trail for accountability           │
└─────────────────────────────────────────────────────────┘
```

### Verdicts

| Verdict | Meaning | Action |
|---------|---------|--------|
| **SEAL** | All floors pass | ✅ Proceed |
| **PARTIAL** | Soft floor warning | ⚠️ Proceed with caution |
| **VOID** | Hard floor failed | ❌ Blocked |
| **888_HOLD** | High-stakes operation | ⏸️ Requires human confirmation |
| **SABAR** | Multiple concerns | 🧊 Cool down, review needed |

---

## The 7 Levels

arifOS implements constitutional governance across **7 implementation layers**:

| Level | Name | What You Get | Use Case |
|-------|------|--------------|----------|
| **L1** | **PROMPT** | Constitutional guidelines as system prompts | Quick testing, prototyping |
| **L2** | **SKILLS** | Reusable `.md` files with floor logic | Claude projects, Cursor rules |
| **L3** | **TOOLS** | Python functions with F1-F13 enforcement | Production apps, FastAPI |
| **L4** | **AGENTS** | Autonomous agents with constitutional memory | Multi-step workflows |
| **L5** | **ORCHESTRATOR** | Multi-agent coordination with consensus | Enterprise systems |
| **L6** | **FEDERATION** | Distributed constitutional consensus | Multi-cloud, edge AI |
| **L7** | **REALITY** | Entropy-bound physical execution | IoT, robotics, critical infra |

---

## The 13 Constitutional Floors (F1-F13)

| Floor | Name | Question | Threshold | Type |
|-------|------|----------|-----------|------|
| F1 | **Amanah** | Is this reversible? | Must be undoable | 🔴 Hard |
| F2 | **Truth** | Is this accurate? | ≥99% confidence | 🔴 Hard |
| F3 | **Tri-Witness** | Do Mind+Heart+Human agree? | ≥95% consensus | 🟡 Soft |
| F4 | **Clarity** | Does this reduce confusion? | ΔS ≤ 0 (entropy) | 🔴 Hard |
| F5 | **Peace²** | Is this non-destructive? | ≥1.0 peace score | 🔴 Hard |
| F6 | **Empathy** | Does this serve the weakest? | κ ≥ 0.95 | 🟡 Soft |
| F7 | **Humility** | Does it state uncertainty? | Ω₀ ∈ [0.03,0.05] | 🟡 Soft |
| F8 | **Genius** | Is intelligence governed? | G ≥ 0.80 | 🟡 Soft |
| F9 | **Anti-Hantu** | No false consciousness? | Φ ≤ 0.30 | 🔴 Hard |
| F10 | **Ontology** | Domain boundaries held? | No hallucination | 🔴 Hard |
| F11 | **Authority** | Is identity verified? | Authenticated | 🔴 Hard |
| F12 | **Hardening** | Injection blocked? | ≥85% defense | 🔴 Hard |
| F13 | **Curiosity** | Alternatives explored? | >0 paths | 🟢 Guide |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  arifOS Architecture v55.1                              │
├─────────────────────────────────────────────────────────┤
│  L1 PROMPT    → System prompts with constitutional DNA  │
│  L2 SKILLS    → Reusable .md files for Claude/Cursor    │
│  L3 TOOLS     → Python SDK (arifos package)             │
│  L4 AGENTS    → Autonomous agents with memory           │
│  L5 ORCH      → Multi-agent coordination                │
│  L6 FEDERATION→ Distributed consensus (PBFT + zk-SNARKs)│
│  L7 REALITY   → Entropy-bound physical execution        │
├─────────────────────────────────────────────────────────┤
│  MCP SERVER   → Model Context Protocol interface        │
│  API          → REST/gRPC for external integration      │
│  VAULT-999    → Immutable Merkle-sealed audit ledger    │
└─────────────────────────────────────────────────────────┘
```

---

## Live Demo

**Dashboard:** [arif-fazil.com/dashboard](https://arif-fazil.com/dashboard)

**MCP Endpoint:** `https://arif-fazil.com/mcp`

**PyPI:** `pip install arifos`

---

## Documentation

| Document | Description |
|----------|-------------|
| [MCP Server Guide](codebase/mcp/README.md) | Full MCP documentation |
| [7 Levels](333_APPS/README.md) | Architecture overview |
| [API Reference](docs/API_REFERENCE.md) | SDK documentation |
| [Deployment](docs/DEPLOYMENT_GUIDE.md) | Railway, Docker, local |
| [Philosophy](docs/PHILOSOPHY.md) | Constitutional foundations |

---

## Development

```bash
# Clone
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# Install
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run MCP tests
pytest tests/test_mcp_v55.py -v

# Type check
mypy codebase/ --ignore-missing-imports
```

---

## License

AGPL-3.0 — Because constitutional rights shouldn't be proprietary.

---

<p align="center">
  <strong>DITEMPA BUKAN DIBERI</strong><br>
  <em>Forged, Not Given</em>
</p>

<p align="center">
  <sub>Built with 🏛️ constitutional care by <a href="https://arif-fazil.com">Muhammad Arif bin Fazil</a></sub>
</p>
