# L4_TOOLS — Production MCP Tools

**Level 4 | 80% Coverage | Medium-High Complexity**

> *"Tools are workflows with code — programmatic enforcement."*

---

## 🎯 Purpose

L4_TOOLS uses the **Model Context Protocol (MCP)** to expose the 000-999 metabolic loop as **7 callable tools** that any LLM can invoke. This is the **current production standard** for arifOS.

**Live Deployment:** [arif-fazil.com](https://arif-fazil.com)

---

## 📈 Effectiveness Spectrum

```
Coverage:  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░ 80%
Cost:      $0.10-0.15 per operation
Setup:     2 hours
Autonomy:  Medium (AI decides when to call)
```

---

## 🔧 The 7 Canonical Tools

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AAA MCP SERVER v53.2.9                           │
│                    codebase/mcp/sse.py                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  _init_ (000-IGNITION)                                              │
│    ✅ F11: Authority verification                                   │
│    ✅ F12: Injection scan                                           │
│    └── Session creation + budget allocation                         │
│                                                                     │
│  _agi_ (111-333 COGNITION-ATLAS)                                    │
│    ✅ F2: Truth verification τ≥0.99                                 │
│    ✅ F4: Clarity check ΔS≤0                                        │
│    ✅ F7: Humility Ω₀∈[0.03,0.05]                                   │
│    └── F10: Ontology validation                                     │
│                                                                     │
│  _asi_ (444-666 DEFEND-ACT)                                         │
│    ✅ F1: Amanah (reversibility check)                              │
│    ✅ F5: Peace² ≥1.0 (safety)                                      │
│    ✅ F6: Empathy κᵣ≥0.70                                           │
│    └── F9: Anti-Hantu <0.30                                         │
│                                                                     │
│  _apex_ (777-888 FORGE-DECREE)                                      │
│    ✅ F3: Tri-Witness ≥0.95                                         │
│    ✅ F8: Genius G≥0.80                                             │
│    ✅ F11: Command Auth                                             │
│    └── F12: Injection Defense                                       │
│                                                                     │
│  _vault_ (999-CRYSTALLIZE)                                          │
│    ✅ Merkle sealing (SHA-256)                                      │
│    ✅ Immutable ledger                                              │
│    └── Audit trail (HIPAA/SOC2/GDPR)                                │
│                                                                     │
│  _trinity_ (Full 000-999 cycle)                                     │
│    Orchestrates: init→agi→asi→apex→vault                            │
│                                                                     │
│  _reality_ (External fact-checking)                                 │
│    ✅ Brave Search API                                              │
│    ✅ Circuit breaker protection                                    │
│    └── F7 Humility disclosure                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Implementation Location

**Primary Source:** `codebase/mcp/` (canonical implementation)

**Local Mirror:** `333_APPS/L4_TOOLS/mcp/` (for documentation completeness)

| Component | Primary Location | Local Mirror | Status |
|-----------|-----------------|--------------|--------|
| MCP Server | `codebase/mcp/server.py` | `mcp/server.py` | ✅ Production |
| SSE Transport | `codebase/mcp/sse.py` | `mcp/sse.py` | ✅ Production |
| Tool Registry | `codebase/mcp/tools/` | `mcp/tools/` | ✅ Production |
| Models/Schemas | `codebase/mcp/models.py` | `mcp/models.py` | ✅ Production |
| Config | `codebase/mcp/mcp_config.json` | `mcp/mcp_config.json` | ✅ Production |
| Constitutional Metrics | `codebase/enforcement/` | — | ✅ Production |

> **Note:** Files in `333_APPS/L4_TOOLS/mcp/` are mirrors for documentation completeness. The canonical source remains in `codebase/mcp/`.

---

## 🛡️ Constitutional Floors Enforced

| Floor | Enforcement | Mechanism | Status |
|-------|-------------|-----------|--------|
| F1 Amanah | ✅ Full | Code-level reversibility check | **Active** |
| F2 Truth | ✅ Full | Programmatic verification | **Active** |
| F3 Tri-Witness | ⚠️ Partial | Requires multi-agent | Available |
| F4 Clarity | ✅ Full | Schema validation | **Active** |
| F5 Peace² | ✅ Full | Safety function | **Active** |
| F6 Empathy | ✅ Full | κᵣ computation | **Active** |
| F7 Humility | ✅ Full | Ω₀ bounds check | **Active** |
| F8 Genius | ✅ Full | G = A×P×X×E² calculation | **Active** |
| F9 Anti-Hantu | ✅ Full | Anomaly detection | **Active** |
| F10 Ontology | ✅ Full | Reality validation | **Active** |
| F11 Command Auth | ✅ Full | Caller verification | **Active** |
| F12 Injection | ✅ Full | Input sanitization | **Active** |
| F13 Sovereign | ✅ Full | Human authorization | **Active** |

---

## 🚀 Deployment History

### v53.0 — MCP Genesis (Archived)
- Initial MCP server implementation
- 3 basic tools (_init_, _agi_, _vault_)
- stdio transport only

### v53.5 — Expansion (Archived)
- Added _asi_, _apex_, _trinity_
- SSE transport added
- External gateways introduced

### v54.0 — Hardening (Archived)
- All 7 tools complete
- Constitutional enforcement hardened
- Rate limiting added

### v54.1-SEAL — Current 🟢 LIVE
- **Production deployment:** https://arif-fazil.com
- Full 7-tool suite operational
- VAULT999 integration active
- 24/7 monitoring

---

## 📊 Live Endpoints

| Endpoint | URL | Status |
|----------|-----|--------|
| Health Check | `https://arif-fazil.com/health` | 🟢 Online |
| MCP SSE | `https://arif-fazil.com/mcp` | 🟢 Online |
| Dashboard | `https://arif-fazil.com/dashboard` | 🟢 Online |
| Metrics | `https://arif-fazil.com/metrics/json` | 🟢 Online |

---

## 📊 Use Cases

| Scenario | Tool(s) | Benefit |
|----------|---------|---------|
| Safety evaluation | `_asi_` | F1, F5, F6 enforcement |
| Code generation | `_agi_` + `_apex_` | F2, F4, F8 verified |
| Full audit | `_trinity_` | Complete 000-999 cycle |
| Fact-checking | `_reality_` | External verification |
| Session sealing | `_vault_` | Immutable record |

---

## 🔗 Next Steps

### Immediate (v55.0)
- [ ] Model-agnostic adapters (Claude, GPT, Gemini, Kimi, Llama)
- [ ] Client auto-detection (Cursor, VS Code, Windsurf)
- [ ] Universal transport layer (stdio/sse/http/websocket)

### Future (v55.1+)
- [ ] Pluggable session backends (Redis, PostgreSQL)
- [ ] Enterprise SSO integration
- [ ] Multi-tenant architecture

---

## 👑 Authority

**Sovereign:** Muhammad Arif bin Fazil  
**Version:** v53.2.9-PROD  
**Live:** [arif-fazil.com](https://arif-fazil.com)  
**Creed:** DITEMPA BUKAN DIBERI
