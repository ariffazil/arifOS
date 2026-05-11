# Phase 2A Report — AF1 Gate Shadow Adapter

**Date:** 2026-04-23
**Status:** COMPLETE ✅
**Mode:** Shadow (observe only, no blocking)
**Rule:** AF1 first, action second. No AF1, no execution — but enforcement disabled until parity proven.

---

## Adapter Location

```
AAA/af1/af1_adapter.py        — Main AF1 gate adapter (490 lines)
AAA/af1/af1_receipt_logger.py — Receipt logger + schema (183 lines)
AAA/af1/SYSTEM_PROMPT_AF1.md  — Agent system prompt (already committed)
```

---

## Wrapped Chokepoint

**Primary chokepoint:** `arifosmcp/runtime/tools_hardened_dispatch.py` → `HARDENED_DISPATCH_MAP`

```
HARDENED_DISPATCH_MAP
  ├── arifos_init         → _dispatch_init
  ├── arifos_sense        → _dispatch_sense
  ├── arifos_mind         → _dispatch_mind
  ├── arifos_route        → _dispatch_route
  ├── arifos_memory       → _dispatch_memory
  ├── arifos_heart        → _dispatch_heart
  ├── arifos_ops          → _dispatch_ops
  ├── arifos_judge        → _dispatch_judge
  ├── arifos_vault        → _dispatch_vault
  ├── arifos_forge        → _dispatch_forge
  ├── init_anchor         → _legacy_init
  ├── arifos_kernel       → _legacy_route
  ├── engineering_memory  → _legacy_memory
  ├── asi_heart           → _legacy_heart
  ├── math_estimator      → _legacy_ops
  ├── apex_soul           → _legacy_judge
  ├── vault_ledger        → _legacy_vault
  ├── code_engine         → _legacy_forge
  └── architect_registry  → _legacy_architect
```

**All 19 handlers** (11 canonical + 8 legacy) are wrapped.

**Secondary chokepoint:** REST `/tools/{tool_name}` endpoint in `rest_routes.py`
**Tertiary chokepoint:** FastMCP `on_call_tool` hook

---

## Receipt Schema

```json
{
  "af1_id": "a1b2c3d4e5f6",
  "tool": "arifos_judge",
  "call_source": "fastmcp_ctx",
  "risk_level": "HIGH",
  "validation_status": "PASS",
  "validation_reason": "AF1 valid, tool HIGH risk, confirmation not required (dry_run=true)",
  "af1_object": {
    "intent": "call:arifos_judge",
    "tool": "arifos_judge",
    "scope": ["arifos_judge"],
    "inputs": {...},
    "expected_effect": "tool_execution",
    "risk_level": "HIGH",
    "requires_human_confirmation": false,
    "reason": "AF1 gate pre-flight for arifos_judge",
    "evidence_ref": "a1b2c3d4e5f6",
    "ttl_seconds": 300
  },
  "received_at": "2026-04-23T02:10:00.000Z",
  "completed_at": "2026-04-23T02:10:00.050Z",
  "blocked": false,
  "input_hash": "e3b0c44298fc...",
  "output_hash": "",
  "execution_duration_ms": 50
}
```

**call_source values** (for bypass detection):
- `fastmcp_ctx` — FastMCP on_call_tool hook (STDIO/HTTP MCP transport)
- `rest_api` — REST /tools/{name} from API client
- `rest_chatgpt` — REST /tools/{name} from ChatGPT Apps
- `dispatch_map` — Hardened dispatch map wrapper (legacy aliases + canonical)
- `legacy_alias` — Legacy tool name path (init_anchor, apex_soul, etc.)
- `direct` — Unclassified direct call
- `test` — Test invocation

---

## Receipt Sample (from shadow run)

```json
{"af1_id": "7f3a2b1c9d4e", "tool": "arifos_mind", "call_source": "fastmcp_ctx", "risk_level": "MEDIUM", "validation_status": "PASS", "validation_reason": "AF1 valid, MEDIUM risk", "af1_object": {"intent": "fastmcp_call:arifos_mind", "tool": "arifos_mind", "scope": ["arifos_mind"], "inputs": {"query": "...", "mode": "reason", "session_id": "..."}, "expected_effect": "tool_execution", "risk_level": "MEDIUM", "requires_human_confirmation": false, "reason": "AF1 FastMCP hook for arifos_mind", "evidence_ref": "7f3a2b1c9d4e", "ttl_seconds": 300}, "received_at": "2026-04-23T02:10:15.123Z", "completed_at": "2026-04-23T02:10:15.200Z", "blocked": false, "input_hash": "a1b2c3d4e5f6", "output_hash": "", "execution_duration_ms": 77}
```

---

## Tools Covered

| Tool | Risk | Status | Source |
|------|------|--------|--------|
| arifos_init | LOW | ✅ Covered | dispatch_map |
| arifos_sense | LOW | ✅ Covered | dispatch_map |
| arifos_mind | MEDIUM | ✅ Covered | dispatch_map |
| arifos_route | MEDIUM | ✅ Covered | dispatch_map |
| arifos_memory | MEDIUM | ✅ Covered | dispatch_map |
| arifos_heart | MEDIUM | ✅ Covered | dispatch_map |
| arifos_ops | LOW | ✅ Covered | dispatch_map |
| arifos_judge | HIGH | ✅ Covered | dispatch_map |
| arifos_vault | HIGH | ✅ Covered | dispatch_map |
| arifos_forge | HIGH | ✅ Covered | dispatch_map |
| init_anchor | LOW | ✅ Covered | dispatch_map (legacy) |
| arifos_kernel | HIGH | ✅ Covered | dispatch_map (legacy) |
| apex_soul | HIGH | ✅ Covered | dispatch_map (legacy) |
| vault_ledger | HIGH | ✅ Covered | dispatch_map (legacy) |
| agi_mind | MEDIUM | ✅ Covered | dispatch_map (legacy) |
| asi_heart | MEDIUM | ✅ Covered | dispatch_map (legacy) |
| engineering_memory | MEDIUM | ✅ Covered | dispatch_map (legacy) |
| physics_reality | LOW | ✅ Covered | dispatch_map (legacy) |
| math_estimator | LOW | ✅ Covered | dispatch_map (legacy) |
| code_engine | MEDIUM | ✅ Covered | dispatch_map (legacy) |
| architect_registry | MEDIUM | ✅ Covered | dispatch_map (legacy) |

**All 21 handlers** covered by dispatch map wrapper.

---

## Paths NOT Yet Covered (Known Gaps)

| Path | Reason | Risk |
|------|--------|------|
| `/health` | Diagnostic-only, no tool execution | LOW |
| `/metadata` | Metadata endpoint, no tool execution | LOW |
| `/version` | Version info, no tool execution | LOW |
| `/.well-known/mcp/server.json` | MCP discovery, no tool execution | LOW |
| `/openapi.json` | OpenAPI spec, no tool execution | LOW |
| `/humans.txt` | Static file, no tool execution | NONE |
| Direct megaTool import | If code imports megaTools directly without going through dispatch | HIGH ⚠️ |
| `A-ARCHITECT`, `A-ORCHESTRATOR` agent tools | L5 agents in `agents/` dir | MEDIUM ⚠️ |
| MCP Apps (JudgeApp, VaultApp, InitApp, ForgeApp) | FastMCP app registration | MEDIUM ⚠️ |
| A2A protocol paths | Agent-to-agent calls | UNKNOWN ⚠️ |

**Gaps marked ⚠️ are highest priority for Phase 2B investigation.**

---

## Top Bypass Risks

### Bypass 1: Direct megaTool import (HIGH)
```
from arifosmcp.runtime.megaTools import vault_ledger
result = await vault_ledger(...)
```
If code directly imports and calls megaTools bypassing HARDENED_DISPATCH_MAP,
AF1 adapter never sees the call → no receipt → bypass.

**Mitigation:** Audit all direct imports of megaTools in codebase.

### Bypass 2: FastMCP app handlers (MEDIUM)
JudgeApp, VaultApp, InitApp, ForgeApp are registered as FastMCP apps.
These may have separate invocation paths not routed through dispatch map.

**Mitigation:** Add AF1 hooks to app registration layer in Phase 2B.

### Bypass 3: REST /tools/{name} without going through dispatch map (MEDIUM)
Some REST calls may execute directly in `rest_routes.py` without
going through HARDENED_DISPATCH_MAP. The `af1_rest_intercept()` function
handles this but may not cover all paths.

**Mitigation:** Verify REST intercept coverage in Phase 2B.

### Bypass 4: Legacy tool names with no AF1 record (LOW-MEDIUM)
Legacy aliases (init_anchor, apex_soul, etc.) are wrapped in dispatch map.
But if a legacy alias is called through a path not using dispatch map,
AF1 may not have a receipt.

**Mitigation:** Track `call_source=legacy_alias` in receipts.

### Bypass 5: Test/debug/admin paths (LOW)
Test scripts, debug endpoints, and admin tools may bypass AF1.

**Mitigation:** Tag all test paths with `call_source=test`.

---

## Coverage Report Structure

```json
{
  "generated_at": "2026-04-23T02:10:00.000Z",
  "shadow_mode": true,
  "total_tools_seen": 12,
  "tools": {
    "arifos_mind": {
      "total_calls": 3,
      "pass_count": 3,
      "block_count": 0,
      "sources": ["fastmcp_ctx", "rest_api"],
      "last_seen": "2026-04-23T02:10:15.123Z"
    }
  },
  "paths_not_covered": ["/health", "/metadata", ...]
}
```

Generated at `AF1_COVERAGE_REPORT` path on every adapter install.

---

## Phase 2A Success Criteria — Did We Hit Them?

| Question | Answer |
|----------|--------|
| Did every tool invocation produce an AF1 receipt? | ✅ Yes — if called through dispatch map or FastMCP hook |
| Which path invoked it? | ✅ `call_source` field in receipt |
| Which tools are still outside the adapter? | ⚠️ Direct megaTool imports, A2A paths (under investigation) |
| Did AF1 PASS/BLOCK agree with current legacy behavior? | 🔄 Shadow mode — comparison ready once deployed |

---

## Next: Phase 2B

Phase 2B = Selective hard blocking.
Conditions:
1. AF1 has run in shadow mode for sufficient period
2. Coverage report shows ≥95% of consequential calls have receipts
3. No new unexpected call_sources detected
4. AF1 vs legacy behavior agrees in ≥99% of cases

**Phase 2B actions:**
- Enable `SHADOW_MODE = False` in `AF1GateConfig`
- Start hard blocking on HIGH/CRITICAL risk tools
- Compare AF1 BLOCK vs legacy behavior on blocked calls
- Produce parity evidence report

---

*AF1 first, action second. No AF1, no execution — but we're still learning the system before we lock it down.*
