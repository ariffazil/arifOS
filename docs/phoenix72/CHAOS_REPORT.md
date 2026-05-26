# CHAOS_REPORT.md — arifOS MCP Issues
**Generated:** 2026-05-25
**Severity Scale:** CRITICAL / HIGH / MEDIUM / LOW / INFO

---

## CRITICAL Issues (must fix before production)

### CHAOS-01: All 72 tools return hardcoded dummy data
**Severity:** CRITICAL
**Location:** `arifos_mcp/arifos_mcp/tools/canonical/*.py`
**Impact:** arifos_mcp is a non-functional stub. No real system calls.
**Evidence:**
- `arif_ops_measure()` returns `g_score: 0.85` — not from real system
- `arif_memory_recall()` returns `memories: []` — no real memory query
- `arif_vault_seal()` returns `entry_id: "vault-entry-001"` — fake hash
**Fix:** Wire each tool to real implementations (see TOOL_INVENTORY.md)

### CHAOS-02: FastMCP not installed in runtime environment
**Severity:** CRITICAL
**Location:** VPS Python environment
**Impact:** arifos_mcp cannot start via STDIO or HTTP transport
**Evidence:** `import fastmcp` times out / fails
**Fix:** `uv pip install fastmcp>=3.2.0` in arifos_mcp environment

### CHAOS-03: No session state tracking
**Severity:** CRITICAL
**Impact:** session_id and actor_id are accepted but never stored or validated
**Evidence:** `arif_session_init` generates a UUID but nothing checks it
**Fix:** Implement session registry with Redis or in-memory store

---

## HIGH Issues (reduce before seal)

### CHAOS-04: No memory integration
**Severity:** HIGH
**Impact:** `arif_memory_recall` always returns empty, misleading clients
**Evidence:** Live system reports `memory_mode: unavailable` but arifos_mcp pretends memory works
**Fix:** Return honest status: `{"status": "unavailable", "mode": "disabled"}`

### CHAOS-05: No vault integration
**Severity:** HIGH
**Impact:** `arif_vault_seal` returns fake hashes, no real ledger writes
**Evidence:** `chain_hash: "sha256:merkle-v3-root"` is hardcoded string
**Fix:** Call real VAULT999 endpoint or implement real append-only ledger

### CHAOS-06: HTTP transport disabled but not cleanly removed
**Severity:** HIGH
**Location:** `arifos_mcp/.mcp.json` — HTTP command has `"disabled": true`
**Impact:** Confusing — is HTTP available or not?
**Fix:** Either enable cleanly or remove HTTP from config entirely

### CHAOS-07: No organ proxy wiring
**Severity:** HIGH
**Impact:** GEOX (11), WEALTH (32), WELL (14) tools should proxy to live MCP servers at 8081/8082/8083
**Evidence:** All return hardcoded values, no HTTP calls to remote servers
**Fix:** Implement FastMCP proxy providers for each organ

---

## MEDIUM Issues (should fix)

### CHAOS-08: mcp_drift_check uses hardcoded count
**Severity:** MEDIUM
**Impact:** Drift detection is fake — always reports `drift = 0`
**Evidence:** `registered = 72  # placeholder — resolved at startup`
**Fix:** Query actual FastMCP tool registry at startup

### CHAOS-09: Constitutional middleware not implemented
**Severity:** MEDIUM
**Location:** `arifos_mcp/arifos_mcp/server/factory.py`
**Impact:** `ConstitutionalGateMiddleware` is defined but `evaluate_request()` is not imported
**Evidence:** `from arifos_mcp.governance.kernel import evaluate_request` — never implemented
**Fix:** Implement `evaluate_request()` in governance/kernel.py

### CHAOS-10: No error envelope — raw tracebacks leak
**Severity:** MEDIUM
**Impact:** Python errors exposed in tool responses
**Evidence:** `@mcp.tool()` decorators have no error handling wrapper
**Fix:** Wrap all tool implementations in try/except with canonical error envelope

### CHAOS-11: No test suite
**Severity:** MEDIUM
**Impact:** No regression protection
**Evidence:** `arifos_mcp/tests/` exists but contains no tests
**Fix:** Write contract tests (see PHASE 9)

---

## LOW Issues (nice to have)

### CHAOS-12: gateway.py has duplicate mcp_health_check
**Severity:** LOW
**Location:** `arifos_mcp/arifos_mcp/tools/canonical/gateway.py`
**Note:** Tool exists in both gateway.py and registry — check for duplication

### CHAOS-13: governance/kernel.py mostly empty
**Severity:** LOW
**Location:** `arifos_mcp/arifos_mcp/governance/kernel.py`
**Evidence:** No real floor evaluation logic

### CHAOS-14: prompts/registry.py has 317 lines
**Severity:** LOW
**Note:** Prompts exist but not validated against 9-prompt spec

---

## Permission Issues

### CHAOS-15: .arifos directory permission denied
**Severity:** HIGH
**Impact:** Wiki write operations fail with permission denied on `/root/arifOS/arifos_mcp/.arifos`
**Fix:** Check ownership — `ls -la /root/arifOS/arifos_mcp/.arifos`

---

## Count: 15 chaos items

| Severity | Count |
|----------|-------|
| CRITICAL | 3 |
| HIGH | 5 |
| MEDIUM | 4 |
| LOW | 3 |

**Total entropy reduction potential:** HIGH — fixing CHAOS-01, 02, 03, 04, 05, 07 would make arifos_mcp functional.

---

*Ditempa Bukan Diberi — Intelligence is forged, not given.*
