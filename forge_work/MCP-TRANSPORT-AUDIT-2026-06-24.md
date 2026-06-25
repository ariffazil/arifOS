# MCP Transport + Blueprint Integration Audit — 2026-06-24

**Actor:** FORGE (000Ω)  
**Session:** Autonomous forge after Arif directive  
**Status:** COMPLETE — Phase 1-3 tested, Phase 4 held (sabar)

---

## Summary

Audited arifOS MCP transport layer against FastMCP docs + MCP spec + Claude blueprint.
Tested all declared capabilities. Found 1 bug, 1 missing install, 1 design insight.

---

## 1. Transport Architecture (OBSERVED)

| Property | Value | Source |
|---|---|---|
| Transport | streamable-http (stateless) | `/health`, `transport/http.py` |
| Framework | FastMCP 3.4.2 | `pip show fastmcp` |
| Server header | 3.2.0 (stale) → 3.4.2 (fixed by other agent) | `server.py` comment |
| Protocol versions | 2025-11-25, 2025-03-26 | `arif_canary version_echo` |
| Session management | Mcp-Session-Id header | Tested via curl |
| Public tools | 7 canonical verbs | `/tools` endpoint |
| Internal tools | 17 (CANONICAL_TOOLS) | `/health` surface_consistency |
| Middleware | CORSMiddleware + GlobalPanicMiddleware | `transport/http.py` |

### Canonical 7 (Public MCP Surface)

```
arif_init     (000) — Session bootstrap
arif_observe  (111) — Reality observation
arif_think    (333) — Reasoning
arif_route    (555) — Intent routing
arif_judge    (888) — Constitutional verdict
arif_act      (900) — Execution gate
arif_seal     (999) — Immutable ledger anchor
```

### Additional Diagnostic Tools (via MCP)

```
arif_canary          — Transport diagnostic probe (6 modes)
arif_resolve_tool    — Tool name resolution
arif_get_affordance  — Constitutional affordance contract
hermes_vault_query   — VAULT999 audit ledger query
```

---

## 2. Capability Testing Results

### ✅ Tasks (SEP-1686)

| Test | Result |
|---|---|
| Capability declared | ✅ `tasks.list`, `tasks.cancel`, `tasks.requests` |
| `tasks/list` | ✅ Returns `{"tasks": []}` |
| `fastmcp[tasks]` installed | ❌ NOT INSTALLED |
| Docket available | ✅ `import docket` works |
| Task-enabled tools | ⚠️ None declared (`task=True` not on any `@mcp.tool`) |

**Action:** Install `fastmcp[tasks]` when long-running governance operations are needed.
**Not urgent:** No tools currently need async task execution.

### ✅ list_changed Notification

| Test | Result |
|---|---|
| Capability declared | ✅ `tools.listChanged: true` |
| Notification accepted | ✅ Empty response (correct JSON-RPC notification behavior) |
| Client support | ⚠️ Uneven (Gemini CLI issue #19509 still open) |

**Action:** Already implemented server-side. Don't rely on client-side enforcement.

### ⚠️ isError:true Pattern

| Test | Result |
|---|---|
| Call arif_act with fake seal | Returns `isError: true` |
| Reason | "Output validation error: outputSchema defined but no structured output returned" |
| Intentional? | ❌ NO — this is FastMCP schema validation, not governance design |

**BUG FOUND:** `arif_act` governance blocks return plain text instead of structured output matching `outputSchema`. FastMCP catches this and wraps as `isError:true`, but the message is about schema validation, not governance.

**Fix:** `arif_act` should return structured output matching its `outputSchema` even when blocking:
```python
# Current (broken): returns plain text
return "888_HOLD: No valid seal found"

# Fixed: returns structured output
return {
    "status": "HOLD",
    "tool": "arif_act",
    "verdict": "HOLD",
    "result": {"reason": "No valid seal found", "seal_verdict_id": "fake-seal-id"},
    "nine_signal": {...},
    "reasons": ["No valid SEAL from arif_judge + arif_seal"]
}
```

**This is a real bug.** The isError:true from schema validation is confusing — the LLM sees "Output validation error" instead of "888_HOLD: No valid seal."

### ✅ outputSchema

| Test | Result |
|---|---|
| All 7 canonical tools | ✅ Have outputSchema |
| structuredContent | ✅ Returned alongside text fallback |
| Schema validation | ✅ FastMCP validates before sending |

---

## 3. Surface Consistency Analysis

**Verdict: DIVERGENT** — but by design.

| Vantage | Count | Hash | Matches |
|---|---|---|---|
| CANONICAL_13 | 7 | d53b77bbc45962e8 | ✅ |
| CANONICAL_TOOLS | 17 | 8a83e9a8720de858 | ❌ |
| tool_registry.json | 7 | d53b77bbc45962e8 | ✅ |
| Public MCP surface | 7 | (via /tools) | ✅ |

**The divergence is expected:** CANONICAL_TOOLS includes 10 internal tools not exposed via MCP.
The public surface is intentionally restricted to 7 verbs.

**No action needed** — this is constitutional design, not drift.

---

## 4. Blueprint Integration Status

| Blueprint Area | arifOS Status | Other Agent | FORGE |
|---|---|---|---|
| FastMCP version header | ✅ Fixed (3.2.0 → 3.4.2) | DONE | — |
| Ed25519 VAULT signing | 🔄 In progress | IN PROGRESS | — |
| isError:true pattern | ⚠️ Bug found | — | DOCUMENTED |
| Tasks capability | ✅ Declared, functional | — | TESTED |
| list_changed | ✅ Declared, accepted | — | TESTED |
| OAuth 2.1 RS | ⏸️ 888_HOLD (sabar) | — | HELD |
| Cross-model testing | ❌ Not implemented | — | DEFERRED |

---

## 5. Bug Report: arif_act Schema Validation Error

**Severity:** P2 (governance signal is lost in schema noise)  
**Reproduce:** Call `arif_act` with invalid `seal_verdict_id`  
**Expected:** Structured HOLD response with governance reason  
**Actual:** `isError: true` with "Output validation error: outputSchema defined but no structured output returned"  
**Root cause:** `arif_act` returns plain text on governance block, not structured output  
**Fix:** Return dict matching `outputSchema` even on HOLD/block  

---

## 6. Recommendations

### Immediate (P1)
- [x] FastMCP version header fixed
- [ ] Fix arif_act to return structured output on governance blocks

### Short-term (P2)
- [ ] Install `fastmcp[tasks]` when async governance needed
- [ ] Add MCP Inspector CLI to CI (`npx @modelcontextprotocol/inspector --cli`)

### Long-term (P3, sabar)
- [ ] OAuth 2.1 RS when external clients arrive
- [ ] Cross-model testing matrix (Claude, GPT, Copilot, curl)

---

## 7. Evidence Paths

- Health response: `curl http://localhost:8088/health`
- Tools list: `curl http://localhost:8088/tools`
- MCP initialize: `curl -X POST http://localhost:8088/mcp` (JSON-RPC)
- Canary tests: `arif_canary` ping, version_echo, transport_echo
- Other agent's work: `git diff arifosmcp/server.py`, `forge_work/BLUEPRINT_INGEST_2026-06-24.md`

---

**DITEMPA BUKAN DIBERI.** The transport is live. The constitution is enforced. One bug found, one phase held.
