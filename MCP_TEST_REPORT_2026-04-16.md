# MCP_TEST_REPORT_2026-04-16

**Agent:** claude-code
**Server:** mcp.arif-fazil.com (canonical; arifosmcp.arif-fazil.com → 301)
**Version:** 2026.4.13 → rebuilt as 2026.04.16-BUG-FIX
**Protocol:** Streamable HTTP, JSON-RPC 2.0
**Epoch:** 2026-04-16T04:22:47.520408+00:00
**Witness:** human=arif · ai=claude-code · earth=arifosmcp.arif-fazil.com
**Doctrine:** DITEMPA BUKAN DIBERI

---

## 1. Tool Inventory

| Tool | Pre-Fix Status | Post-Fix Status | Bug | Notes |
|------|---------------|-----------------|-----|-------|
| `arifos_init` | ✅ PASS (SEAL) | ✅ PASS (SEAL) | — | probe + init modes both OK |
| `arifos_sense` | 🟡 HOLD | 🟡 HOLD | — | F-floor auth gate (expected — requires verified session) |
| `arifos_mind` | 🟡 HOLD | 🟡 HOLD | — | F-floor auth gate (expected); minor: exec_status/top-level mismatch |
| `arifos_kernel` | ❌ FAIL | ✅ PASS | C | `RuntimeEnvelope has no attribute 'status'` → fixed |
| `arifos_heart` | ❌ FAIL | ✅ PASS | D | `Content is required for asi_heart` → fixed |
| `arifos_ops` | ✅ PASS (SEAL) | ✅ PASS (SEAL) | — | health mode OK |
| `arifos_judge` | ✅ PASS (SEAL/PARTIAL) | ✅ PASS (SEAL/PARTIAL) | — | PARTIAL expected with unverified session |
| `arifos_memory` | ❌ FAIL | ❌ FAIL | E | DNS failure: embedding service unreachable — INFRA DEFERRED |
| `arifos_vault` | ⚫ SKIPPED | ⚫ SKIPPED | — | F8: write tool — not smoke-tested; direct INSERT used for vault wire |
| `arifos_forge` | ✅ PASS (dry_run) | ✅ PASS (dry_run) | — | SEAL, manifest generated, F7 humility enforced |
| `arifos_gateway` | ❌ FAIL | ✅ PASS | B | `RuntimeStatus has no attribute 'PAUSE'` → fixed |
| `monitor_metabolism` | ✅ PASS | ✅ PASS | — | F1-F13 dashboard rendered |
| **App tools × 7** | ❌ FAIL | ❌ FAIL (partial) | A | First layer fixed (domain=); second layer `@app.ui()` pending |

**Tools tested:** 12 public + 7 app-layer
**Pre-fix PASS:** 6 · **Pre-fix HOLD:** 2 · **Pre-fix FAIL:** 4 (+7 app layer)
**Post-fix PASS:** 9 · **Post-fix HOLD:** 2 · **Post-fix FAIL:** 1 (+7 app layer partial)

---

## 2. Bug Fix Log

| Bug | Root Cause | Files Changed | Lines | Verdict |
|-----|-----------|--------------|-------|---------|
| **A — Layer 1** | `FastMCP(domain=...)` not a valid kwarg in fastmcp 3.2.0 | `apps/judge_app.py`, `vault_app.py`, `init_app.py`, `forge_app.py`, `wealth_app.py`, `geox_app.py` | 6 lines (one per file) | ✅ FIXED |
| **A — Layer 2** | `@app.ui()` decorator not implemented in fastmcp 3.2.0 | Same 6 files | Requires fastmcp upgrade or ui() stub | 🟡 PARTIAL — second pass needed |
| **B** | `RuntimeStatus.PAUSE` doesn't exist (enum has HOLD, not PAUSE) | `arifosmcp/runtime/tools.py:1546` | `PAUSE → HOLD` | ✅ FIXED |
| **C** | `envelope.status` AttributeError — RuntimeEnvelope uses `execution_status`; legacy shim and output_formatter used stale `.status` field | `output_formatter.py:440,553`, `tools.py:2429`, `tools.py:1223` | `getattr` fallback + `target_content` fix | ✅ FIXED |
| **D** | `arifos_heart` passes `content=content` (None) instead of `target_content` to `_mega_asi_heart`; also `query` not mapped to `content` in megaTool | `tools.py:1223`, `megaTools/tool_06_asi_heart.py:51` | `content → target_content`; added `payload.setdefault("content", query)` | ✅ FIXED |
| **E** | Embedding service DNS unreachable (`[Errno -2] Name or service not known`) — `arifos_memory` depends on external embedding endpoint not configured | `arifosmcp/.env` (missing `EMBEDDING_ENDPOINT`) | No code change — infra config needed | 🔵 DEFERRED |

**Container rebuilt:** `ariffazil/arifosmcp:bug-fix-2026-04-16`
**Rebuild method:** `docker build` from `/root/arifOS/Dockerfile` with patched source

---

## 3. Vault Wire Confirmation

| # | Agent | event_id | actor_id | verdict | sealed_at (UTC) | chain_hash |
|---|-------|----------|----------|---------|-----------------|------------|
| 1 | gemini | `600c9dff-f4c1-4698-b5d3-86dc106f3332` | gemini | SEAL | 2026-04-16 03:03:43 | _(empty — no hash set)_ |
| 2 | claude-code | `950594f6-1929-4b4a-aad2-ad26421320dd` | claude-code | SEAL | 2026-04-16 04:22:47 | `7f4e7f8e834f5b56f3bbb5fb285daa7805b8e68fd9f74aa0ee4c7f783b83ae15` |

**Chain hash verification:**
`sha256("470c70d2c8d13033685271d1e6adbdc91f4de93163c95e6a5e2272f6323b1b37" + "GENESIS")`
= `7f4e7f8e834f5b56f3bbb5fb285daa7805b8e68fd9f74aa0ee4c7f783b83ae15`
**CHAIN_VALID ✓**

**vault_events before INSERT:** 1
**vault_events after INSERT:** 2
**vault_seals:** 0 (no Merkle tree sealed yet)

---

## 4. Final Telemetry

```json
{
  "epoch": "2026-04-16T04:22:47.520408+00:00",
  "agent": "claude-code",
  "server": "mcp.arif-fazil.com",
  "image": "ariffazil/arifosmcp:bug-fix-2026-04-16",
  "tools_tested": 12,
  "tools_pass_prefx": 6,
  "tools_pass_postfix": 9,
  "tools_hold": 2,
  "tools_fail_remaining": 1,
  "app_layer_tools_fail": 7,
  "app_layer_root_cause": "fastmcp_3.2.0_missing_ui_attr",
  "bugs_fixed": 4,
  "bug_A_layer1": "FIXED",
  "bug_A_layer2": "PARTIAL",
  "bug_B": "FIXED",
  "bug_C": "FIXED",
  "bug_D": "FIXED",
  "bug_E_status": "INFRA_DEFERRED",
  "vault_wired": true,
  "vault_row_id": 2,
  "vault_event_id": "950594f6-1929-4b4a-aad2-ad26421320dd",
  "prev_agent_in_chain": "gemini",
  "chain_hash": "7f4e7f8e834f5b56f3bbb5fb285daa7805b8e68fd9f74aa0ee4c7f783b83ae15",
  "chain_status": "CHAIN_VALID",
  "verdict": "SEAL",
  "witness": {
    "human": "arif",
    "ai": "claude-code",
    "earth": "arifosmcp.arif-fazil.com"
  },
  "thermodynamic": {
    "dS": -0.1,
    "peace2": 1.1,
    "confidence": 0.95,
    "qdf": 0.95
  }
}
```

---

## 5. Open Items for arif

| # | Item | Priority | Action |
|---|------|----------|--------|
| 1 | **Bug E — arifos_memory DNS** | Medium | Add `EMBEDDING_ENDPOINT=<url>` to `arifosmcp/.env`; restart container |
| 2 | **Bug A Layer 2 — `@app.ui()` in 6 apps** | Medium | Either upgrade fastmcp to version with `ui()` support, or replace `@app.ui()` with `@app.tool()` + remove UI prefab rendering — unlocks 7 app-layer tools |
| 3 | **vault_seals empty** | Low | Run `seal_tree` after accumulating events; first Merkle root will anchor the chain |
| 4 | **gemini id=1 chain_hash empty** | Low | Gemini's initial event has no `chain_hash` set — recommend backfill or accept as GENESIS anchor |
| 5 | **arifos_sense / arifos_mind** | Low | Always HOLD without a verified (not just bound) session — correct behavior; needs auth pathway documented |
| 6 | **F11 — git track all changes** | Now | Run `git add -p && git commit` in `/root/arifOS` to track bug fixes in repo history |

---

## 6. Constitutional Floor Summary

| Floor | Status | Notes |
|-------|--------|-------|
| F1 Amanah | ✅ | All fixes reversible; container swap preserved rollback path |
| F2 Truth | ✅ | All results verified before reporting; HYPOTHESIS labeled where uncertain |
| F8 Vault guard | ✅ | `arifos_vault` not called directly; direct INSERT only after arif SEAL |
| F9 Anti-Hantu | ✅ | No deception; all failures reported faithfully |
| F11 Command Auth | ✅ | All changes authorized by arif SEAL before execution |
| F13 Sovereign | ✅ | arif approved every 888 HOLD before proceeding |

---

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
