# MIGRATION_EXECUTION_PLAN.md — PHOENIX-72 Blueprint
**Date:** 2026-05-25
**Phase:** HOLD — Design Blueprint Only (Router directive: no mutation)
**Principle:** Ditempa Bukan Diberi — plan first, forge second

---

## SITUATION

- **Live system:** arifOS MCP at 8088, 18 tools, REST+JSON-RPC, PID 1131 — IS LIVE, DO NOT DISTURB
- **New package:** `/root/arifOS/arifos_mcp/arifos_mcp/`, 72 stub tools, 0 alive
- **Organ servers:** Ports 8081/8082/8083 NOT listening — GEOX, WEALTH, WELL unavailable
- **AAA A2A:** Port 3001 NOT listening
- **Task:** Produce reversible design blueprint; no execution

---

## TARGET ARCHITECTURE

```
External AI / Claude / GPT
        |
        v
arifos_mcp Gateway (STDIO / streamable HTTP)
  mcp_health_check     ← "gateway eyes"
  mcp_drift_check      ← "gateway DNA check"
        |
        v
  Constitutional Middleware (F01-F13 gates)
        |
        v
  Kernel Tools (13)    ← PROXY to live 8088
        |
        v
  +-----+-----+-----+
  |     |     |     |
  v     v     v
GEOX  WEALTH WELL    ← PROXY (or DEGRADED if unavailable)
 11    32     14     ← organ-specific tools
        |
        v
  VAULT999 append-only ledger
```

**72 tools total:** 2 gateway + 13 kernel + 11 GEOX + 32 WEALTH + 14 WELL

---

## WAVES OF ACTIVATION

### Wave 1 — Manifest Foundation (NO organ servers needed)
**Goal:** Create the DNA of the system

1. **CREATE** `manifests/tools.json` — 72-tool manifest with full governance metadata
2. **CREATE** `manifests/resources.json` — 18-resource manifest
3. **CREATE** `manifests/prompts.json` — 9-prompt manifest
4. **CREATE** `manifests/schema_tools.py` — schema validator for tool entries

**Files to create:**
- `manifests/tools.json`
- `manifests/resources.json`
- `manifests/prompts.json`
- `manifests/__init__.py`
- `manifests/validate.py`

**Risk:** LOW — JSON files, reversible
**No 888_HOLD required**

---

### Wave 2 — Kernel Proxy to Live 8088 (NO organ servers needed)
**Goal:** Make 13 kernel tools alive by proxying to existing working system at 8088

5. **CREATE** `organs/kernel_proxy.py` — HTTP proxy client for 8088
   - Calls `http://127.0.0.1:8088/tools/<tool_name>`
   - Returns canonical envelope wrapping 8088 response
   - Handles 8088 being unreachable (returns DEGRADED)
6. **REFACTOR** `tools/canonical/kernel.py` — replace stubs with proxy calls
7. **ADD** ack gate enforcement in kernel tool wrappers for C4 tools

**Files to create:**
- `organs/__init__.py`
- `organs/kernel_proxy.py`
- `organs/base_proxy.py` — shared proxy utilities

**Files to edit:**
- `tools/canonical/kernel.py` — replace all stub returns with proxy calls
- `schemas/tools.py` — confirm envelope schema

**Risk:** LOW — only reads from 8088, wraps in envelope
**No 888_HOLD required**

---

### Wave 3 — Organ Proxies (organ servers optional — DEGRADED mode)
**Goal:** GEOX/WEALTH/WELL tools return honest DEGRADED, not dummy data

8. **CREATE** `organs/geox_proxy.py`
   - Attempts HTTP GET to `http://127.0.0.1:8081/health`
   - On success: proxy calls to 8081
   - On failure: return DEGRADED envelope with honest `{"status": "degraded", "reason": "port_8081_unreachable"}`
9. **CREATE** `organs/wealth_proxy.py` — same pattern for 8082
10. **CREATE** `organs/well_proxy.py` — same pattern for 8083
11. **REFACTOR** `tools/canonical/geox.py` — replace stubs with proxy calls
12. **REFACTOR** `tools/canonical/wealth.py` — replace stubs with proxy calls
13. **REFACTOR** `tools/canonical/well.py` — replace stubs with proxy calls

**Files to create:**
- `organs/geox_proxy.py`
- `organs/wealth_proxy.py`
- `organs/well_proxy.py`

**Files to edit:**
- `tools/canonical/geox.py`
- `tools/canonical/wealth.py`
- `tools/canonical/well.py`

**Risk:** LOW — HTTP client calls, graceful degradation
**No 888_HOLD required**

---

### Wave 4 — Gateway Tools Realization
**Goal:** mcp_health_check and mcp_drift_check return real data

14. **REFACTOR** `tools/canonical/gateway.py` — mcp_health_check
    - Check: 8088 reachable? organ proxies reachable? venv valid?
    - Return: `{"status": "degraded", "reachable": {"8088": true, "8081": false, ...}}`
15. **REFACTOR** `tools/canonical/gateway.py` — mcp_drift_check
    - Compare live FastMCP registry count to manifests/tools.json count
    - Compute hash of registered tools vs manifest hash
    - Return: drift_detected boolean, missing_tools[], extra_tools[]

**Files to edit:**
- `tools/canonical/gateway.py`

**Risk:** LOW — read-only diagnostics
**No 888_HOLD required**

---

### Wave 5 — Resources (read-only, no organ servers needed)
**Goal:** Expose 18 read-only resources

16. **CREATE** `resources/kernel/` — constitution, floors, tool registry, model registry
17. **CREATE** `resources/geox/` — physics9 doctrine, datasets, schemas
18. **CREATE** `resources/wealth/` — valuation doctrine, finance formulas, schemas
19. **CREATE** `resources/well/` — vitality current, substrate boundary, thresholds
20. **CREATE** `resources/aaa/` — agent registry, capabilities

**Files to create:**
- `resources/__init__.py`
- `resources/kernel/` (4 resources)
- `resources/geox/` (4 resources)
- `resources/wealth/` (4 resources)
- `resources/well/` (4 resources)
- `resources/aaa/` (2 resources)

**Risk:** LOW — read-only resources
**No 888_HOLD required**

---

### Wave 6 — Prompts (no organ servers needed)
**Goal:** Compress old wisdom into 9 canonical prompts

21. **CREATE** `prompts/canonical/raf.md` — Read Aesthetics Framework
22. **CREATE** `prompts/canonical/teof.md` — Thermodynamics of Opinion Formation
23. **CREATE** `prompts/canonical/a_prompt.md` — Abstraction Prompt
24. **CREATE** `prompts/canonical/master.md` — Master orchestration
25. **CREATE** `prompts/canonical/commitment.md` — Commitment Protocol
26. **CREATE** `prompts/canonical/a2a_negotiation.md` — A2A Negotiation
27. **CREATE** `prompts/canonical/operator_handoff.md` — Operator Handoff
28. **CREATE** `prompts/canonical/crisis_fallback.md` — Crisis Fallback
29. **CREATE** `prompts/canonical/migration_recovery.md` — Migration/Recovery

**Files to create:**
- `prompts/canonical/*.md` (9 files)

**Risk:** LOW — prompt templates, no execution
**No 888_HOLD required**

---

### Wave 7 — FastMCP Server Assembly
**Goal:** Wire everything into a working FastMCP server

30. **EDIT** `server/factory.py` — register all 72 tools with FastMCP
31. **EDIT** `server/main.py` — proper startup with manifest validation
32. **CREATE** `server/startup.py` — startup sequence: load manifest → validate → register tools
33. **CREATE** `transports/stdio.py` — FastMCP stdio transport (already exists, verify)
34. **CREATE** `transports/http.py` — optional streamable HTTP (if needed)
35. **VERIFY** `pyproject.toml` has FastMCP dependency
36. **TEST** `python -m arifos_mcp` starts without error

**Files to create:**
- `server/startup.py`
- `transports/stdio.py` (verify existing)
- `transports/http.py` (optional)

**Files to edit:**
- `server/factory.py`
- `server/main.py`
- `pyproject.toml`

**Risk:** MEDIUM — modifies server startup, may conflict with 8088 if ports clash
**No 888_HOLD required for design; HOLD if deploying alongside 8088**

---

### Wave 8 — Middleware Enforcement
**Goal:** Every call passes constitutional gates

37. **CREATE** `governance/middleware.py` — F01-F13 pre-call middleware
    - Session validation (F01)
    - Manifest existence check (F02)
    - Organ reachability check (F03)
    - Tool exists in registry (F04)
    - Input schema validation (F06)
    - Risk class check (F07)
    - Cooling period enforcement (F08)
    - Ack gate for C4 tools (F01, F13)
    - Envelope wrapping on output (F12)
38. **CREATE** `governance/envelope.py` — canonical response envelope builder
39. **CREATE** `governance/risk.py` — risk classification engine

**Files to create:**
- `governance/middleware.py`
- `governance/envelope.py`
- `governance/risk.py`
- `governance/__init__.py`

**Risk:** MEDIUM — affects all tool calls
**No 888_HOLD required**

---

### Wave 9 — Tests
**Goal:** Prove aliveness

40. **CREATE** `tests/test_manifest_72_tools.py` — verify 72 tools in manifest
41. **CREATE** `tests/test_resources_18.py` — verify 18 resources exist
42. **CREATE** `tests/test_prompts_9.py` — verify 9 prompts exist
43. **CREATE** `tests/test_stdio_list_tools.py` — FastMCP stdio tools/list
44. **CREATE** `tests/test_drift_check.py` — mcp_drift_check returns 0 drift
45. **CREATE** `tests/test_envelope_all_tools.py` — every tool returns envelope
46. **CREATE** `tests/test_ack_gate.py` — C4 tools require ack or return VOID
47. **CREATE** `tests/test_kernel_proxy_8088.py` — kernel tools proxy to 8088
48. **CREATE** `tests/test_organ_degraded_honest.py` — organ tools return DEGRADED, not dummy
49. **CREATE** `tests/test_no_raw_tracebacks.py` — no traceback leakage

**Files to create:**
- `tests/` directory with 10 test files

**Risk:** LOW — test files only
**No 888_HOLD required**

---

### Wave 10 — Organ Server Bringup (requires 888_HOLD)
**Goal:** GEOX, WEALTH, WELL live on ports 8081-8083

**This wave requires 888_HOLD — service startup is semi-irreversible**

50. **VERIFY** GEOX FastMCP server starts on 8081
51. **VERIFY** WEALTH FastMCP server starts on 8082
52. **VERIFY** WELL FastMCP server starts on 8083
53. **CONFIGURE** Caddy routes: geox.arif-fazil.com → 8081, wealth.arif-fazil.com → 8082, well.arif-fazil.com → 8083
54. **UPDATE** `organs/geox_proxy.py` to use live 8081 instead of DEGRADED
55. **UPDATE** `organs/wealth_proxy.py` to use live 8082
56. **UPDATE** `organs/well_proxy.py` to use live 8083
57. **TEST** tri-organ consensus packet

**888_HOLD required for steps 50-53 (service startup)**

---

### Wave 11 — VAULT999 Integration (requires 888_HOLD)
**Goal:** VAULT999 writes become functional

**This wave requires 888_HOLD — VAULT999 is append-only**

58. **VERIFY** VAULT999 hash chain integrity
59. **CREATE** `organs/vault_proxy.py` — proxy to live VAULT999
60. **WIRE** `arif_vault_seal` to VAULT999 proxy
61. **TEST** seal and verify chain

**888_HOLD required (irreversible ledger writes)**

---

### Wave 12 — Seal and Production
**Goal:** Manifest hash sealed, production deployment approved

62. **COMPUTE** SHA-256 of manifests/tools.json
63. **CREATE** `PHOENIX72_SEAL_REPORT.md` — final seal document
64. **COMMIT** all changes with `REPO=ariffazil/arifos` trailer
65. **PUSH** to GitHub (requires 888_HOLD for git push)
66. **DEPLOY** arifos_mcp to production (requires 888_HOLD)

---

## FILE MANIFEST (CREATE/EDIT/DELETE)

### CREATE (new files)

| File | Wave | Risk | Blocker |
|------|------|------|---------|
| `manifests/tools.json` | 1 | LOW | None |
| `manifests/resources.json` | 1 | LOW | None |
| `manifests/prompts.json` | 1 | LOW | None |
| `manifests/__init__.py` | 1 | LOW | None |
| `manifests/validate.py` | 1 | LOW | None |
| `organs/__init__.py` | 2 | LOW | None |
| `organs/base_proxy.py` | 2 | LOW | None |
| `organs/kernel_proxy.py` | 2 | LOW | None |
| `organs/geox_proxy.py` | 3 | LOW | None |
| `organs/wealth_proxy.py` | 3 | LOW | None |
| `organs/well_proxy.py` | 3 | LOW | None |
| `resources/__init__.py` | 5 | LOW | None |
| `resources/kernel/` (4 files) | 5 | LOW | None |
| `resources/geox/` (4 files) | 5 | LOW | None |
| `resources/wealth/` (4 files) | 5 | LOW | None |
| `resources/well/` (4 files) | 5 | LOW | None |
| `resources/aaa/` (2 files) | 5 | LOW | None |
| `prompts/canonical/*.md` (9 files) | 6 | LOW | None |
| `server/startup.py` | 7 | MEDIUM | None |
| `governance/middleware.py` | 8 | MEDIUM | None |
| `governance/envelope.py` | 8 | MEDIUM | None |
| `governance/risk.py` | 8 | MEDIUM | None |
| `governance/__init__.py` | 8 | LOW | None |
| `tests/` (10 files) | 9 | LOW | None |

### EDIT (existing files)

| File | Wave | Change | Risk |
|------|------|--------|------|
| `tools/canonical/kernel.py` | 2 | Replace stubs with kernel_proxy calls | LOW |
| `tools/canonical/geox.py` | 3 | Replace stubs with geox_proxy calls | LOW |
| `tools/canonical/wealth.py` | 3 | Replace stubs with wealth_proxy calls | LOW |
| `tools/canonical/well.py` | 3 | Replace stubs with well_proxy calls | LOW |
| `tools/canonical/gateway.py` | 4 | Real health_check, drift_check | LOW |
| `server/factory.py` | 7 | Register all 72 tools | MEDIUM |
| `server/main.py` | 7 | Proper startup with manifest | MEDIUM |
| `pyproject.toml` | 7 | Confirm FastMCP dep | LOW |

### DELETE (entropy removal — reversible via git)

| File/Directory | Reason | Risk |
|----------------|--------|------|
| `arifos_mcp/venv/` | Broken venv | LOW |
| `arifos_mcp/tests/` (old stubs) | Not aligned to PHOENIX | LOW |
| Stub return statements in all canonical tools | Dummy data | LOW |

---

## PATCH PLAN SUMMARY

**Total new files:** ~50
**Total files to edit:** ~8
**Total files to delete:** ~5

**Wave 1 (this session):** Manifests — CREATED
**Wave 2-9 (next sessions):** Build out — CREATED/EDITED
**Wave 10-11 (requires HOLD):** Organ servers — REQUIRES APPROVAL
**Wave 12 (requires HOLD):** Production push — REQUIRES APPROVAL

---

## WHAT REQUIRES 888_HOLD

| Action | Why | Risk Level |
|--------|-----|-----------|
| Start GEOX on port 8081 | Semi-irreversible service | 888 JUDGE |
| Start WEALTH on port 8082 | Semi-irreversible service | 888 JUDGE |
| Start WELL on port 8083 | Semi-irreversible service | 888 JUDGE |
| Configure Caddy routes | Network config change | 888 JUDGE |
| VAULT999 ledger writes | Irreversible append | 888 JUDGE |
| Git push to main | Repository mutation | 888 JUDGE |
| Production deploy | Live system change | 888 JUDGE |

**What does NOT require HOLD:**
- Creating JSON manifest files
- Writing Python proxy files
- Creating resource/prompt files
- Editing stub files to call proxies
- Writing test files
- Computing manifest hashes (read-only)

---

## DECISIONS REQUIRED FROM ARIF

1. **Organ servers (8081-8083):** Should we start them before or after full proxy wiring?
2. **DEGRADED honest mode:** Is it acceptable to ship with GEOX/WEALTH/WELL returning DEGRADED until organ servers are live?
3. **Port conflict:** Should arifos_mcp run on a different port than 8088, or replace it?
4. **AAA A2A:** Should we implement A2A mesh or defer until AAA server is live?

---

## SEAL CRITERIA

PHOENIX-72 is sealed when:
- [ ] `manifests/tools.json` exists with 72 entries
- [ ] All 72 tools registered in FastMCP
- [ ] `mcp_drift_check` returns `drift_detected: false`
- [ ] All 72 tools return canonical envelope
- [ ] All C4 tools enforce ack gate
- [ ] Kernel tools proxy to live 8088
- [ ] Organ tools return DEGRADED (not dummy data)
- [ ] All 18 resources accessible
- [ ] All 9 prompts loaded
- [ ] All 10 tests pass
- [ ] SHA-256 manifest hash computed and recorded
- [ ] `PHOENIX72_SEAL_REPORT.md` created
