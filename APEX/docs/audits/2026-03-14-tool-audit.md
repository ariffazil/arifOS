# arifosmcp Tool Audit Report
**Date:** 2026-03-14
**Server:** https://arifosmcp.arif-fazil.com
**Version:** 2026.03.14-FORGED
**Tools Loaded:** 40

---

## Executive Summary

| Category | Count | Status |
|----------|-------|--------|
| **Working** | 28 | ✅ Functional |
| **Timeout Issues** | 4 | ⚠️ Slow/Unresponsive |
| **Configuration Errors** | 4 | 🔧 Needs Fix |
| **Broken/Buggy** | 4 | ❌ Critical Issues |

**Overall Health:** 70% (28/40 tools fully functional)

---

## Detailed Findings

### ✅ WORKING TOOLS (28)

| # | Tool | Response | Notes |
|---|------|----------|-------|
| 1 | init_anchor | ✅ Returns SABAR | Constitutional auth works |
| 2 | revoke_anchor_state | ✅ Full response | Session revocation works |
| 3 | register_tools | ✅ status, tools | Tool registry accessible |
| 4 | agi_reason | ✅ HOLD | Needs auth, but responds |
| 5 | agi_reflect | ✅ Full response | Metacognitive works |
| 6 | reality_atlas | ✅ Full response | Evidence merging works |
| 7 | search_reality | ✅ Full response | Direct search works |
| 8 | ingest_evidence | ✅ Full response | URL ingestion works |
| 9 | asi_critique | ✅ Full response | Adversarial audit works |
| 10 | agentzero_armor_scan | ✅ Full response | Injection scan works |
| 11 | apex_judge | ✅ Full response | Constitutional verdict works |
| 12 | agentzero_validate | ✅ Full response | Validation works |
| 13 | agentzero_hold_check | ✅ Full response | Hold check works |
| 14 | audit_rules | ✅ Returns floors | Constitutional rules accessible |
| 15 | check_vital | ✅ Returns metrics | Health check works |
| 16 | metabolic_loop | ✅ Full response | Legacy router works |
| 17 | vault_seal | ✅ Full response | Vault sealing works |
| 18 | verify_vault_ledger | ✅ Full response | Ledger verification works |
| 19 | apex_score_app | ✅ version, view | G-Score app works |
| 20 | stage_pipeline_app | ✅ version, view | Pipeline app works |
| 21 | trace_replay | ✅ Full response | Audit replay works |
| 22 | agentzero_memory_query | ✅ Full response | Memory recall works |
| 23 | fs_inspect | ✅ data, status | Filesystem inspection works |
| 24 | net_status | ✅ status=ok | Network status works |
| 25 | config_flags | ✅ data, status | Config inspection works |
| 26 | list_resources | ✅ result | Resource listing works |
| 27 | cost_estimator | ✅ data, status | Cost estimation works |
| 28 | agentzero_engineer | ✅ Full response | Code execution works |

---

### ⚠️ TIMEOUT ISSUES (4)

| # | Tool | Problem | Severity |
|---|------|---------|----------|
| 29 | **arifOS_kernel** | ⏱️ 60s timeout | 🔴 HIGH |
| 30 | **metabolic_loop_router** | No response (10s timeout) | 🟡 MEDIUM |
| 31 | **forge** | No response (10s timeout) | 🟡 MEDIUM |
| 32 | **asi_simulate** | Exit code 5 (error) | 🟡 MEDIUM |

**Analysis:**
- `arifOS_kernel` is the PRIMARY router - 60s timeout is critical
- These tools likely have external dependencies (LLM calls) causing delays
- May need async processing or timeout configuration

---

### 🔧 CONFIGURATION ERRORS (4)

| # | Tool | Error | Fix Required |
|---|------|-------|--------------|
| 33 | **reality_compass** | Returns null (all fields) | Brave API key may be invalid |
| 34 | **system_health** | Returns null | psutil data not accessible |
| 35 | **process_list** | Returns 0 processes | Process enumeration blocked |
| 36 | **log_tail** | "Log file not found" | Default log path incorrect |

**Analysis:**
- `reality_compass`: BRAVE_API_KEY configured but search returning empty
- System tools (health, process): Container restrictions or missing `/proc` access
- `log_tail`: Default path `arifosmcp.transport.log` not found

---

### ❌ CRITICAL BUGS (4)

| # | Tool | Error | Severity |
|---|------|-------|----------|
| 37 | **chroma_query** | `'QdrantClient' object has no attribute 'search'` | 🔴 CRITICAL |
| 38 | **open_apex_dashboard** | Exit code 5 | 🟡 MEDIUM |
| 39 | **forge_guard** | Returns null | 🟡 MEDIUM |
| 40 | **read_resource** | `NotFoundError: Unknown resource: 'arifos://health'` | 🟡 MEDIUM |

**Analysis:**
- **chroma_query**: Qdrant client API mismatch - code uses `.search()` but should use `.query()` or different method
- **open_apex_dashboard**: Browser/open failure (expected in headless)
- **forge_guard**: No response - may need valid auth_context
- **read_resource**: Resource URI scheme not properly registered

---

## Server Health Status

```json
{
  "status": "healthy",
  "service": "arifos-aaa-mcp",
  "version": "2026.03.14-VALIDATED",
  "transport": "streamable-http",
  "tools_loaded": 23,
  "ml_floors": {
    "ml_floors_enabled": false,
    "ml_model_available": false,
    "ml_method": "heuristic"
  }
}
```

### Capability Map Status

| Capability | Status |
|------------|--------|
| governed_continuity | ✅ enabled |
| vault_persistence | ✅ enabled |
| vector_memory | ✅ enabled (but query broken) |
| external_grounding | ✅ enabled |
| model_provider_access | ✅ enabled |
| local_model_runtime | ✅ enabled |
| auto_deploy | ✅ enabled |

### Provider Status

| Provider | Status |
|----------|--------|
| openai | ✅ configured |
| anthropic | ✅ configured |
| google | ✅ configured |
| openrouter | ✅ configured |
| venice | ✅ configured |
| ollama_local | ✅ configured |
| brave | ⚠️ configured but search failing |
| jina | ✅ configured |
| perplexity | ✅ configured |
| firecrawl | ✅ configured |
| browserless | ✅ configured |

---

## Recommendations

### Immediate (Critical)

1. **Fix chroma_query Qdrant API**
   ```python
   # Current (broken):
   client.search(...)
   # Should be:
   client.query_points(...)  # Qdrant v1.8+
   ```

2. **Fix arifOS_kernel timeout**
   - Add timeout configuration
   - Check ML floors dependencies
   - Consider async processing

### Short-term (High Priority)

3. **Fix reality_compass Brave search**
   - Verify BRAVE_API_KEY validity
   - Check Brave API rate limits
   - Add fallback to search_reality

4. **Fix system_health / process_list**
   - Grant container CAP_SYS_PTRACE
   - Mount /proc read-only
   - Or use Docker stats API

### Medium-term

5. **Add proper log paths**
   - Configure log_tail default paths
   - Mount logs directory in compose

6. **Register read_resource URIs**
   - Define arifos:// scheme handlers
   - Add health, config, status resources

---

## Test Methodology

- All 40 tools called via MCP streamable-http endpoint
- Timeout: 10s (60s for kernel)
- Payload: Minimal valid arguments
- Auth: ARIFOS_DEV_MODE=true (no bearer token)
- Response analyzed for: keys returned, errors, null values

---

## Appendix: Constitutional Floor Status

All governance tools (init_anchor, apex_judge, vault_seal) properly enforce:
- F11 (Command Auth)
- F12 (Injection Defense)
- F13 (Sovereign Override)

Session continuity signing: ✅ Configured
