# 🚀 v60.0-FORGE — Constitutional AI Governance Kernel

> *"DITEMPA BUKAN DIBERI — Forged, not given"*

**Full Release:** [v60.0-FORGE](https://github.com/ariffazil/arifOS/releases/tag/v60.0-FORGE)  
**PyPI:** `pip install arifos==60.0.0`  
**MCP Registry:** [`io.github.ariffazil/aaa-mcp`](https://registry.modelcontextprotocol.io/?q=arif)

---

## 💎 What's New

### 🎯 MCP Registry Official Submission

arifOS is now officially submitted to the **MCP Registry** — the app store for MCP servers.

| Detail | Value |
|--------|-------|
| **Namespace** | [`io.github.ariffazil/aaa-mcp`](https://registry.modelcontextprotocol.io/?q=arif) |
| **Package** | `pip install arifos` |
| **Docker** | `ariffazil/arifos:v60.0` |
| **Live Endpoint** | https://aaamcp.arif-fazil.com/mcp |

```bash
# Claude Desktop, Cursor, and any MCP client can now discover arifOS
mcp-publisher search arifos
```

### 📁 Clean Presentation Layer

Organized the monorepo "chaos" into navigable value:

| Entry Point | Audience | Purpose |
|-------------|----------|---------|
| **[`aaa_mcp/`](aaa_mcp/)** | MCP Users | Clean, focused MCP server quickstart |
| **[`docs/architecture.md`](docs/architecture.md)** | Developers | Visual ASCII architecture diagrams |
| **Root README** | Everyone | Clear repository structure table |

### 🧠 5-Organ Kernel (v60 Architecture)

Every query now flows through the hardened constitutional pipeline:

```
000_INIT ──→ 111_SENSE ──→ 222_THINK ──→ 333_REASON ──→ 444_SYNC
 (F11,F12)     (F4)          (F2,F4,F7)    (F2,F4,F7)    (Trinity)
                ↓
555_EMPATHY ──→ 666_ALIGN ──→ 777_FORGE ──→ 888_JUDGE ──→ 999_SEAL
 (F5,F6,F9)    (F5,F6,F9)    (Internal)    (F3,F8,F11)   (F1,F3)
```

### ⚡ 10 Canonical MCP Tools

| Tool | Stage | Floors | Purpose |
|------|-------|--------|---------|
| `init_gate` | 000_INIT | F11, F12 | Session ignition & injection defense |
| `trinity_forge` | 000-999 | ALL | Unified constitutional pipeline |
| `agi_sense` | 111_SENSE | F4 | Intent classification & lane routing |
| `agi_think` | 222_THINK | F2, F4, F7 | Hypothesis generation |
| `agi_reason` | 333_REASON | F2, F4, F7 | Logic & deduction |
| `reality_search` | External | F2, F7, F10 | Web-grounded truth verification |
| `asi_empathize` | 555_EMPATHY | F5, F6 | Impact analysis & stakeholder care |
| `asi_align` | 666_ALIGN | F5, F6, F9 | Ethics & policy alignment |
| `apex_verdict` | 888_JUDGE | F3, F8, F11 | Final judgment (Ψ Soul) |
| `vault_seal` | 999_SEAL | F1, F3 | Immutable audit & cryptographic seal |

### 🔐 13 Constitutional Floors (Hardened)

| Floor | Principle | Threshold | Fail Action |
|-------|-----------|-----------|-------------|
| **F1** Amanah | Reversibility | Chain of Custody | VOID |
| **F2** Truth | Fidelity ≥ 0.99 | τ ≥ 0.99 | VOID |
| **F3** Consensus | Tri-Witness W₃ ≥ 0.95 | GM ≥ 0.95 | SABAR |
| **F4** Clarity | Entropy reduction | ΔS ≤ 0 | SABAR |
| **F5** Peace² | Stability | P² ≥ 1.0 | SABAR |
| **F6** Empathy | Stakeholder care | κᵣ ≥ 0.95 | SABAR |
| **F7** Humility | Uncertainty band | Ω₀ ∈ [0.03, 0.05] | VOID |
| **F8** Genius | Efficiency | G = A×P×X×E² ≥ 0.80 | SABAR |
| **F9** Anti-Hantu | No fake consciousness | C_dark < 0.30 | VOID |
| **F10** Ontology | Grounding | Symbol valid | VOID |
| **F11** Authority | Chain of command | Auth valid | VOID |
| **F12** Defense | Injection hardening | Risk < 0.85 | VOID |
| **F13** Sovereign | Human veto | Available | WARN |

---

## 🏗️ Architecture

### Trinity Framework (ΔΩΨ)

```
┌─────────────────────────────────────────────────────────────────┐
│                    arifOS v60.0-FORGE                           │
│           Constitutional AI Governance Kernel                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│   │  INIT   │→ │   AGI   │→ │   ASI   │→│  APEX   │           │
│   │ Airlock │  │  Mind   │  │  Heart  │  │  Soul   │           │
│   │ F11,F12 │  │F2,F4,F7 │  │F5,F6,F9 │  │F3,F8,F11│           │
│   └─────────┘  └─────────┘  └─────────┘  └────┬────┘           │
│                                               │                  │
│                                          ┌────┴────┐            │
│                                          │  VAULT  │            │
│                                          │ Memory  │            │
│                                          │ F1,F3   │            │
│                                          └─────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

### Repository Structure

```
arifOS/
├── 📦 aaa_mcp/              # MCP Server entry point
├── 🧠 core/                 # 5-Organ Kernel
├── 🌐 arif-fazil-sites/     # Website & docs
├── 🛠️ 333_APPS/             # Skills, tools, workflows
├── 📚 docs/                 # Documentation
└── 🧪 tests/                # Test suite
```

---

## 🚀 Deployment Options

| Method | Command | Best For |
|--------|---------|----------|
| **PyPI** | `pip install arifos` | Local development |
| **Docker** | `docker run ariffazil/arifos:v60.0` | Production |
| **Railway** | One-click deploy | Serverless hosting |
| **Render** | `render.yaml` | Full-stack apps |
| **MCP Registry** | Auto-discovered | Claude, Cursor, etc. |

### Claude Desktop

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "aaa_mcp"]
    }
  }
}
```

### Cursor

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "aaa_mcp"]
    }
  }
}
```

---

## 📊 Stats

| Metric | Value |
|--------|-------|
| **Python** | 3.10+ |
| **Lines of Code** | ~14,000 |
| **Test Coverage** | 85%+ |
| **Constitutional Floors** | 13 |
| **MCP Tools** | 10 canonical |
| **Pipeline Stages** | 10 (000-999) |
| **Organs** | 5 (INIT, AGI, ASI, APEX, VAULT) |

---

## 🙏 Acknowledgments

- **FastMCP 2.0+** — For the excellent MCP server framework
- **Anthropic** — For the Model Context Protocol specification
- **Railway** — For seamless deployment infrastructure
- **PyPI** — For Python package distribution
- **GitHub** — For hosting and MCP Registry namespace verification

---

## 🔗 Links

| Resource | URL |
|----------|-----|
| **Documentation** | https://arifos.arif-fazil.com |
| **MCP Endpoint** | https://aaamcp.arif-fazil.com/mcp |
| **Health Check** | https://aaamcp.arif-fazil.com/health |
| **PyPI** | https://pypi.org/project/arifos/ |
| **MCP Registry** | [registry.modelcontextprotocol.io/?q=arif](https://registry.modelcontextprotocol.io/?q=arif) |
| **GitHub Discussions** | https://github.com/ariffazil/arifOS/discussions |

---

## 📝 Migration from v55.x

No breaking changes. v60.0-FORGE is fully backward compatible with v55.5-HARDENED.

```bash
pip install --upgrade arifos
```

---

<p align="center">
<strong>DITEMPA BUKAN DIBERI — Forged, not given</strong><br>
🔥💎🧠
</p>
