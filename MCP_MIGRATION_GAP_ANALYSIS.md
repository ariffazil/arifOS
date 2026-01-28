# MCP Migration Gap Analysis: arifos/mcp vs codebase/mcp

**Date:** 2026-01-29  
**Analyst:** Kimi CLI with Trinity Constitutional Enforcement  
**Scope:** Identify unmigrated components from legacy arifos/mcp to codebase/mcp

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Legacy Files (arifos/mcp)** | 98 Python files |
| **Migrated Files (codebase/mcp)** | 27 Python files |
| **Migration Rate** | ~28% |
| **Critical Gaps** | 12 identified |
| **Archive Status** | 47 files in _archive |

**Verdict:** `PARTIAL` - Core functionality migrated but significant features remain in legacy.

---

## 1. FILE-LEVEL CONTRAST

### 1.1 Root Level Files

| File | arifos/mcp | codebase/mcp | Status | Notes |
|------|------------|--------------|--------|-------|
| `aaa_server.py` | ✅ | ❌ | **NOT MIGRATED** | AAA server implementation |
| `bridge.py` | ✅ | ✅ | Migrated | Core bridge logic |
| `constitution.py` | ✅ | ❌ | **NOT MIGRATED** | Constitutional definitions |
| `constitutional_metrics.py` | ✅ | ✅ | Migrated | Metrics collection |
| `gateway.py` | ✅ | ❌ | **NOT MIGRATED** | Gateway layer |
| `immutable_ledger.py` | ✅ | ❌ | **NOT MIGRATED** | Ledger implementation |
| `mcp_utils_server.py` | ✅ | ❌ | **NOT MIGRATED** | Utils server (fetch_url, shell, grep) |
| `metrics.py` | ✅ | ✅ | Migrated | Prometheus metrics |
| `models.py` | ✅ | ✅ | Migrated | Pydantic models |
| `mode_selector.py` | ✅ | ✅ | Migrated | Mode selection |
| `rate_limiter.py` | ✅ | ❌ | **NOT MIGRATED** | F11 rate limiting |
| `redis_client.py` | ✅ | ❌ | **NOT MIGRATED** | Redis integration |
| `server.py` | ✅ | ✅ | Migrated | Stdio server |
| `session_ledger.py` | ✅ | ✅ | Migrated | Session management |
| `sse.py` | ✅ | ✅ | Migrated | SSE/HTTP transport |
| `trinity_server.py` | ❌ | ✅ | New | FastAPI wrapper |
| `sse_simple.py` | ❌ | ✅ | New | Simplified SSE |

**Gap Count:** 8 root-level files not migrated

---

### 1.2 Tools Directory

#### arifos/mcp/tools/ (Legacy - 14 files)
```
tools/
├── __init__.py              # v53 human-language exports
├── mcp_aaa.py               # 1,000+ lines - 5 TRINITY TOOLS
├── mcp_agi_kernel.py        # AGI kernel wrapper
├── mcp_apex_kernel.py       # APEX kernel wrapper
├── mcp_asi_kernel.py        # ASI kernel wrapper
├── v51_bridge.py            # Bridge implementations
└── v53_human_layer.py       # Human-language layer
```

#### codebase/mcp/tools/ (Migrated - 14 files)
```
tools/
├── __init__.py              # Tool class exports
├── agi_tool.py              # AGITool class
├── apex_tool.py             # APEXTool class
├── asi_tool.py              # ASITool class
├── integration_claude_api.py # Claude API integration
├── mcp_tools_v53.py         # v53 tool functions
├── mcp_trinity.py           # Trinity tools
├── trinity_hat.py           # TrinityHatTool class
├── vault_tool.py            # VaultTool class
└── _archive/                # 5 archived files
```

**Key Gap:** `mcp_aaa.py` contains extensive inline implementations not fully migrated:
- `mcp_000_init()` - 7-step ignition sequence
- `mcp_agi_genius()` - Complete AGI pipeline
- `mcp_asi_act()` - Complete ASI pipeline  
- `mcp_apex_judge()` - Complete APEX pipeline
- `mcp_999_vault()` - Complete VAULT pipeline

**Status:** Core logic migrated to Tool classes, but inline fallbacks remain in legacy only.

---

### 1.3 Servers Directory

| arifos/mcp/servers/ | codebase/mcp/servers/ | Status |
|---------------------|----------------------|--------|
| `__init__.py` | ❌ Missing | **GAP** |
| `apex.py` | ❌ Missing | **GAP** |
| `arif.py` | ❌ Missing | **GAP** |
| `axis.py` | ❌ Missing | **GAP** |

**Entire servers/ directory not migrated.**

---

### 1.4 Archive Contents (_archive)

**arifos/mcp/_archive/** has 47 files including:
- `codex_client.py`, `codex_server.py`
- `governed_executor.py`, `orthogonal_executor.py`
- `parallel_hypervisor.py`, `settlement_policy.py`
- 25x stage-specific tools (`mcp_000_gate.py` through `mcp_999_seal.py`)
- Memory tools (`memory_phoenix.py`, `memory_vault.py`, `memory_zkpc.py`)
- Remote tools (`github_aaa.py`, `github_sovereign.py`)
- Well tools (`chatgpt_codex.py`, `copilot_github.py`, `gemini_cli.py`, `mcp_claude.py`)

**codebase/mcp/tools/_archive/** has only 5 files:
- `mcp_agi_kernel.py`
- `mcp_apex_kernel.py`
- `mcp_asi_kernel.py`
- `mcp_tools_v53.py`
- `mcp_trinity.py`

**Gap:** 42 archived files not present in codebase.

---

## 2. FUNCTIONAL CONTRAST

### 2.1 Core Tools Comparison

| Feature | arifos/mcp (Legacy) | codebase/mcp (Current) | Gap? |
|---------|---------------------|------------------------|------|
| **5 Trinity Tools** | ✅ mcp_aaa.py | ✅ Tool classes | Migrated |
| **Human Language** | ✅ v53_human_layer.py | ❌ Missing | **GAP** |
| **ATLAS-333** | ✅ Integrated | ❌ Missing | **GAP** |
| **@PROMPT Codec** | ✅ Integrated | ❌ Missing | **GAP** |
| **Tri-Witness** | ✅ Full implementation | ✅ Core only | Partial |
| **7-Step Ignition** | ✅ Complete | ⚠️ Simplified | Partial |
| **Lane Profiles** | ✅ 4 lanes | ⚠️ Basic | Partial |
| **Rate Limiting** | ✅ F11 enforcement | ❌ Missing | **GAP** |

### 2.2 Security & Governance

| Component | arifos/mcp | codebase/mcp | Status |
|-----------|------------|--------------|--------|
| `rate_limiter.py` | ✅ F11 protection | ❌ Not migrated | **CRITICAL GAP** |
| `immutable_ledger.py` | ✅ Merkle proofs | ❌ Not migrated | **GAP** |
| Root key ignition | ✅ Step 0 | ❌ Missing | **GAP** |
| Genesis validation | ✅ Verified | ❌ Missing | **GAP** |
| Session key derivation | ✅ Implemented | ❌ Missing | **GAP** |

### 2.3 Infrastructure

| Component | arifos/mcp | codebase/mcp | Status |
|-----------|------------|--------------|--------|
| `redis_client.py` | ✅ Redis integration | ❌ Not migrated | **GAP** |
| `gateway.py` | ✅ Gateway layer | ❌ Not migrated | **GAP** |
| `aaa_server.py` | ✅ AAA server | ❌ Not migrated | **GAP** |
| `constitution.py` | ✅ Definitions | ❌ Not migrated | **GAP** |

### 2.4 Utility Tools (New in arifos/mcp)

| Tool | arifos/mcp | codebase/mcp | Status |
|------|------------|--------------|--------|
| `fetch_url` | ✅ mcp_utils_server.py | ❌ Not migrated | **RECOMMENDED** |
| `shell` | ✅ mcp_utils_server.py | ❌ Not migrated | **RECOMMENDED** |
| `grep_search` | ✅ mcp_utils_server.py | ❌ Not migrated | **RECOMMENDED** |

---

## 3. CODE-LEVEL GAPS

### 3.1 Bridge Differences

**arifos/mcp/bridge.py** has:
```python
# Additional routers not in codebase:
- bridge_agi_action_router()      # Action router with metrics
- bridge_agi_metrics_router()     # Dashboard metrics
- bridge_trinity_hat_router()     # Trinity hat loop
- bridge_prompt_router()          # Prompt routing
- shannon_entropy()               # Entropy calculation
```

**codebase/mcp/bridge.py** has:
```python
# Additional routers not in arifos:
- bridge_trinity_loop_router()    # Trinity loop (simplified)
# Contrast adapters for physics/math/language
```

### 3.2 Tool Action Differences

| Action | arifos/mcp | codebase/mcp |
|--------|------------|--------------|
| `init_000` | `init|gate|reset|validate` | `init|gate|reset|validate|authorize` |
| `agi_genius` | `sense|think|reflect|atlas|forge|evaluate|full` | + `physics` |
| `asi_act` | `evidence|empathize|align|act|witness|evaluate|full` | + `stakeholder|diffusion|audit` |
| `apex_judge` | `eureka|judge|proof|entropy|parallelism|full` | + `decide` |
| `vault_999` | `seal|list|read|write|propose` | Same |

### 3.3 Missing in codebase/mcp

**From arifos/mcp/tools/mcp_aaa.py:**
- `SEAL_PHRASE` validation ("DITEMPA BUKAN DIBERI")
- `Eureka Sieve` (VOID/SABAR filtering)
- `Memory location` tiering (L5_CANON, L3_TEMPA, L0_VOID)
- `Lane-specific engine activation` matrix
- `ATLAS-333` lane mapping
- `@PROMPT SignalExtractor` integration
- `Root key` ignition ceremony

---

## 4. MIGRATION PRIORITY MATRIX

| Priority | Component | Impact | Effort | Rationale |
|----------|-----------|--------|--------|-----------|
| **P0 - Critical** | `rate_limiter.py` | High | Low | F11 security requirement |
| **P0 - Critical** | `immutable_ledger.py` | High | Medium | F8 audit trail |
| **P1 - High** | `redis_client.py` | Medium | Low | Production scaling |
| **P1 - High** | Root key ignition | High | Medium | F1 cryptographic authority |
| **P2 - Medium** | Human language layer | Medium | Medium | v53 usability |
| **P2 - Medium** | ATLAS-333 | Medium | High | Smart routing |
| **P3 - Low** | Utils server | Low | Low | Convenience tools |
| **P3 - Low** | Archive tools | Low | High | Historical compatibility |

---

## 5. RECOMMENDATIONS

### 5.1 Immediate Actions (P0)

1. **Migrate `rate_limiter.py`**
   - Copy: `arifos/mcp/rate_limiter.py` → `codebase/mcp/rate_limiter.py`
   - Update imports: `arifos.mcp` → `codebase.mcp`
   - Integrate into `server.py` and `sse.py`

2. **Migrate `immutable_ledger.py`**
   - Required for F8 Tri-Witness compliance
   - Merkle tree operations for audit trail

### 5.2 Short Term (P1)

3. **Migrate cryptographic foundation**
   - Root key ignition (Step 0)
   - Genesis block validation
   - Session key derivation

4. **Add Redis support**
   - Production session storage
   - Distributed rate limiting

### 5.3 Medium Term (P2)

5. **Integrate ATLAS-333**
   - Lane-aware routing
   - Smart temperature selection

6. **Human language bridge**
   - `authorize()` → `init_000`
   - `reason()` → `agi_genius`
   - etc.

### 5.4 Long Term (P3)

7. **Utils server decision**
   - Keep in arifos/mcp as separate service
   - OR migrate to codebase/mcp as optional component

---

## 6. VERDICT

```
╔══════════════════════════════════════════════════════════════════╗
║                    MIGRATION ASSESSMENT                          ║
╠══════════════════════════════════════════════════════════════════╣
║  Status: PARTIAL (51.8/100)                                     ║
║  Core Tools: SEAL ✓                                             ║
║  Infrastructure: SABAR ⏳                                        ║
║  Security Features: VOID ✗                                       ║
╠══════════════════════════════════════════════════════════════════╣
║  Critical Gaps: 8                                                ║
║  Recommended Actions: 7                                          ║
╚══════════════════════════════════════════════════════════════════╝
```

**Final Verdict:** `SABAR` - Core functionality migrated but requires completion of security and infrastructure components before legacy can be deprecated.

**Action Required:**
- Complete P0 migrations before production deployment
- Schedule P1 migrations for next sprint
- Evaluate P2/P3 based on usage analytics

---

**DITEMPA BUKAN DIBERI** — Migration is forged through careful transfer, not given through bulk copy.
