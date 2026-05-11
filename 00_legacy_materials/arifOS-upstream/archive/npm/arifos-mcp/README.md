# @arifos/mcp

**arifOS MCP Server** — The world's first production-grade Constitutional AI Governance System.

[![Version](https://img.shields.io/badge/version-2026.3.15--TRINITY-blue.svg)](https://www.npmjs.com/package/@arifos/mcp)
[![License](https://img.shields.io/badge/license-AGPL--3.0--only-lightgrey.svg)](./LICENSE)

> **DITEMPA BUKAN DIBERI — Forged, Not Given** [ΔΩΨ | ARIF]

## Overview

arifOS is a governed intelligence organism, not a wrapper. It metabolizes information through a **Double Helix** of specialized organs with **13 Constitutional Floors (F1-F13)** that cannot be bypassed.

### 🏛️ Protocol Trinity (NEW in 2026.3.15)

arifOS now implements **all three major AI agent protocols**:

| Protocol | Purpose | Endpoint | Status |
|----------|---------|----------|--------|
| **MCP** | Tool execution & context | `/mcp` | ✅ Production |
| **A2A** | Agent-to-agent collaboration | `/a2a/*` | ✅ Active |
| **WebMCP** | Browser-native AI | `/webmcp` | ✅ Active |

### Trinity Architecture (ΔΩΨ)

| Engine | Symbol | Role |
|--------|--------|------|
| **Δ Delta** | 🔷 | **AGI Mind** — Reason, sense, ground |
| **Ω Omega** | 🔴 | **ASI Heart** — Empathy, memory, ethics |
| **Ψ Psi** | 🟡 | **APEX Soul** — Forge, judge, seal |

### 32 Canonical Tools

- **KERNEL (6):** `init_anchor`, `revoke_anchor_state`, `register_tools`, `arifOS_kernel`, `forge`, `init_anchor_state`
- **AGI Δ MIND (6):** `agi_reason`, `agi_reflect`, `reality_compass`, `reality_atlas`, `search_reality`, `ingest_evidence`
- **ASI Ω HEART/HAND (4):** `asi_critique`, `asi_simulate`, `agentzero_engineer`, `agentzero_memory_query`
- **APEX Ψ SOUL (7):** `apex_judge`, `agentzero_validate`, `audit_rules`, `agentzero_armor_scan`, `agentzero_hold_check`, `check_vital`, `open_apex_dashboard`
- **VAULT999 (2):** `vault_seal`, `verify_vault_ledger`
- **NERVOUS SYSTEM 9 (9):** `system_health`, `process_list`, `net_status`, `chroma_query`, `arifos_list_resources`, `arifos_read_resource`, `log_tail`, `fs_inspect`, `cost_estimator`

## Installation

```bash
npm install -g @arifos/mcp
```

**Requirements:**
- Node.js 18+
- Python 3.12+ (will be auto-installed if missing)

## Usage

### CLI

```bash
# Start MCP server (stdio mode)
arifos-mcp

# Start HTTP server
arifos-mcp http
```

### Programmatic

```javascript
const arifos = require('@arifos/mcp');
// The package exports the CLI entry point
```

### MCP Client Configuration

**Claude Desktop:**
```json
{
  "mcpServers": {
    "arifos": {
      "command": "npx",
      "args": ["-y", "@arifos/mcp"]
    }
  }
}
```

**Kimi/Other MCP Clients:**
```json
{
  "mcpServers": {
    "arifos": {
      "command": "arifos-mcp",
      "args": ["stdio"]
    }
  }
}
```

## The 13 Constitutional Floors

| Floor | Name | Threshold | Enforces |
|-------|------|-----------|----------|
| F1 | Amanah | ≥ 0.5 | Reversibility |
| F2 | Truth | ≥ 0.99 | Anti-hallucination |
| F3 | Tri-Witness | ≥ 0.95 | Human·AI·Earth consensus |
| F4 | ΔS Clarity | ≤ 0 | Entropy reduction |
| F5 | Peace² | ≥ 1.0 | Non-destructive power |
| F6 | κᵣ Empathy | ≥ 0.70 | Weakest stakeholder |
| F7 | Ω₀ Humility | 0.03–0.20 | Gödel uncertainty |
| F8 | G Genius | ≥ 0.80 | Internal coherence |
| F9 | C_dark | < 0.30 | Anti-Hantu |
| F10 | Ontology | LOCK | No consciousness claims |
| F11 | Command Auth | LOCK | Identity verification |
| F12 | Injection | < 0.85 | Block adversarial control |
| F13 | Sovereign | HUMAN | Human final authority |

## Changelog

### 2026.3.15 (TRINITY)
- **Protocol Trinity:** MCP + A2A + WebMCP — Three protocols, one kernel
- **A2A Protocol:** Google Agent-to-Agent protocol with Agent Cards
- **WebMCP:** W3C browser-native MCP with `navigator.modelContext`
- **32 Tools:** 25 constitutional + 9 Nervous System machine tools
- **Zero-Chaos Deployment:** 6-stage constitutional deployment system
- **CIV Infrastructure:** 15-container autonomous stack

### 2026.3.14
- Initial stable release
- 25 constitutional tools
- 13 floors (F1-F13) enforced
- VAULT999 immutable ledger
- Double Helix architecture

## Documentation

- **Website:** https://arifos.arif-fazil.com
- **Repository:** https://github.com/ariffazil/arifosmcp
- **PyPI:** https://pypi.org/project/arifosmcp/

## License

AGPL-3.0-only — See [LICENSE](./LICENSE) for details.

---

*DITEMPA BUKAN DIBERI — Forged, Not Given [ΔΩΨ | ARIF]*
