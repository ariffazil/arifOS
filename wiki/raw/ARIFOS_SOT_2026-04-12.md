# arifOS State of the Tree (SOT) — 2026-04-12

> **Canonical reference for arifOS repository state**  
> **Seal:** 999_SEAL ACHIEVED 🔒  
> **Version:** 2026.04.11  
> **Authority:** 888_APEX

---

## Quick Reference

| Attribute | Value |
|-----------|-------|
| **Repository** | https://github.com/ariffazil/arifOS |
| **Main Branch** | `902635f` - Update geox submodule to latest main |
| **Status** | ✅ OPERATIONAL |
| **Seal** | 999_SEAL |
| **Architecture** | V2.0.0 Production Hardening |
| **Tools** | 33 constitutional |
| **Substrates** | 5/6 operational |

---

## Live Endpoints (Verified)

### Primary MCP Server
| Endpoint | URL | Status |
|----------|-----|--------|
| MCP | https://arifosmcp.arif-fazil.com/mcp | ✅ LIVE |
| Health | https://arifosmcp.arif-fazil.com/health | ✅ LIVE |
| Tools | https://arifosmcp.arif-fazil.com/tools | ✅ LIVE |

### MCP Substrates (Internal)
| Service | Port | Status |
|---------|------|--------|
| mcp_time | :8001 | ✅ OK |
| mcp_filesystem | :8002 | ✅ OK |
| mcp_git | :8003 | ✅ OK |
| mcp_memory | :8004 | ✅ OK |
| mcp_fetch | :8005 | ✅ OK |
| mcp_everything | :8006 | ⚠️ OPTIONAL |

### Trinity Ecosystem
| Ring | Domain | Status |
|------|--------|--------|
| SOUL | arif-fazil.com | ✅ LIVE |
| MIND | arifos.arif-fazil.com | ✅ LIVE |
| BODY | aaa.arif-fazil.com | ✅ LIVE |

---

## Repository Structure

### Core Components

```
arifOS/
├── arifosmcp/              # MCP server implementation
│   ├── tool_registry.json  # 33 constitutional tools
│   ├── server.py           # Unified entry point
│   └── evals/              # MCP inspector tests
├── core/                   # Constitutional floors
│   ├── floors.py           # F1-F13 enforcement
│   ├── shared/             # Shared utilities
│   └── prompts/            # Production prompts
├── deployments/            # Deployment automation
│   ├── deploy.sh           # VPS/Horizon deploy
│   └── docker-compose.*    # Orchestration
├── geox/                   # GEOX submodule
├── skills/                 # Agent skill definitions
├── wiki/                   # Documentation (98 files)
└── server.py               # Root unified server
```

### Key Files

| File | Purpose | Last Updated |
|------|---------|--------------|
| `README.md` | Main documentation | 2026-04-11 |
| `MCP_SITES_SEAL.md` | Deployment verification | 2026-04-11 |
| `server.py` | Unified server entry | 2026-04-11 |
| `docker-compose.yml` | Full stack orchestration | 2026-04-11 |
| `pyproject.toml` | Python dependencies | 2026-04-10 |

---

## Recent Commits (Last 30 Days)

```
902635f Update geox submodule to latest main
da8cc95 🔩 SEAL: arifOS V2.0.0 Production Hardening
144188d fix(runtime): fix circular import in runtime/server.py redirect
df2feac feat(server): fully unify Horizon gateway into unified server
05276d4 refactor(stdio): update stdio servers to use unified root server
1deb801 refactor(server): unify all server.py into single root entry point
4686af4 fix(mcp): repair arifos_init and arifos_kernel async/await bugs
9f1d97c Merge branch 'fix/broken-tools'
aaf5969 fix(evals): extract verdict from verdict_detail.code
9c54f54 fix(megaTools): FastMCP Context compatibility
cef71cb DUAL TRANSPORT: arifOS MCP SSE + HTTP dual seal
8375136 feat(runtime): MCP server v2 with unified transport
c1b04cb core/floors.py: wire F3/F5/F8 into evaluate()
e978a17 feat(mcp): wire A-FORGE into arifOS schema
```

---

## Architecture v3: Thermodynamic Kernel

### The 9+1 Constitutional Tools

| Tool | Stage | Function |
|------|-------|----------|
| `arifos.init` | 000_INIT | Session anchoring |
| `arifos.sense` | 111_SENSE | Reality grounding |
| `arifos.mind` | 333_MIND | Structured reasoning |
| `arifos.route` | 444_ROUT | Tool selection |
| `arifos.heart` | 666_HEART | Safety critique |
| `arifos.ops` | 444_OPS | Operational cost |
| `arifos.judge` | 888_JUDGE | Constitutional verdict |
| `arifos.memory` | 777_MEMORY | Context recall |
| `arifos.vault` | 999_VAULT | Immutable seal |
| `arifos.forge` | Execution | Delegated action bridge |

### 13 Constitutional Floors

| Floor | Name | Type | Status |
|-------|------|------|--------|
| F1 | AMANAH (Reversibility) | Hard | ✅ Enforced |
| F2 | TRUTH (Accuracy) | Hard | ✅ Enforced |
| F3 | TRI-WITNESS (Consensus) | Soft | ✅ Enforced |
| F4 | CLARITY (Entropy) | Soft | ✅ Enforced |
| F5 | PEACE² (Non-Destruction) | Soft | ✅ Enforced |
| F6 | EMPATHY (RASA) | Soft | ✅ Enforced |
| F7 | HUMILITY (Uncertainty) | Soft | ✅ Enforced |
| F8 | GENIUS (System Health) | Soft | ✅ Enforced |
| F9 | ETHICS (Anti-Dark) | Hard | ✅ Enforced |
| F10 | CONSCIENCE (No Claims) | Hard | ✅ Enforced |
| F11 | AUDITABILITY (Logs) | Soft | ✅ Enforced |
| F12 | RESILIENCE (Graceful) | Soft | ✅ Enforced |
| F13 | ADAPTABILITY (Safe Evo) | Hard | ✅ Enforced |

---

## Active Branches

| Branch | Commit | Status |
|--------|--------|--------|
| main | 902635f | ✅ Current |
| fix/broken-tools | aa9f321 | ✅ Merged |
| codex/reconcile-origin-main-2026-04-03 | 226422b | 🏛️ Archive |

---

## Environment Configuration

### Required Variables

```bash
ARIFOS_DEV_MODE=false
ARIFOS_API_KEY=<redacted>
ARIFOS_ENABLE_PHASE2_TOOLS=1
OPENAI_API_KEY=<redacted>
ANTHROPIC_API_KEY=<redacted>
DATABASE_URL=postgresql://...
```

### Feature Flags

| Flag | Status |
|------|--------|
| ENABLE_DANGEROUS_TOOLS | ✅ Enabled |
| ENABLE_BACKGROUND_JOBS | ✅ Enabled |
| ENABLE_EXPERIMENTAL_TOOLS | ✅ Enabled |

---

## Known Issues

| Issue | Severity | Status |
|-------|----------|--------|
| mcp_everything optional | Low | ⚠️ By design |
| fix/broken-tools branch archived | Low | ✅ Merged to main |

---

## Next Actions

| Priority | Action | Target |
|----------|--------|--------|
| Low | Update wiki with unified server docs | 2026-04-15 |
| Low | Document SSE + HTTP dual transport | 2026-04-15 |
| Low | Archive old branches | 2026-04-20 |

---

*SOT verified: 2026-04-12*  
*Seal: 999_SEAL | Authority: 888_APEX*
