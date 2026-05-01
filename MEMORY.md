# MEMORY.md — OPENCLAW Selective Persistence

**Version:** 2026.05.01-KANON
**Last updated:** 2026-05-01 03:55 UTC
**Status:** SEALED

---

## Sealed Facts

### OC-001 — OPENCLAW Runtime Governance Upgrade — SEALED 2026-05-01

**Git commit:** cce9843b

All gap files created and synced to git. OPENCLAW governance is now 000-999 bounded.

| File | Status | Purpose |
|------|--------|---------|
| AGENTS.md | ✅ Updated | ReAct loop → 000-999 governed loop |
| AUTONOMY.md | ✅ Created | L0-L5 permission ladder |
| CHECKPOINT.md | ✅ Created | Session continuity + recovery |
| HEARTBEAT.md | ✅ Rewritten | Live runtime protocol |
| LOOP.md | ✅ Created | 000-999 operational implementation |
| DECISIONS.md | ✅ Created | Sealed decision log |
| TASKS.md | ✅ Created | Active work ledger |
| TOOLS.md | ✅ Populated | Local environment notes |
| RECOVERY.md | ✅ Created | Failure recovery runbook |
| FLOORS.md | ✅ Created | F1-F13 standalone reference |
| SOUL.md | ✅ Updated | Version header added |
| AGENT_STATE.md | ✅ Created | Agent identity and intelligence state |

**Archived (stale):** CLAUDE.md, GEMINI.md, ARIF.md — prepended archive notice.

**Workspace cleaned:** Removed AAA_README.md, tommy_thomas_dossier.md, ARIF-TEMPLATE.md (not governance content).

**Maturity:** 32/75 → ~43/75 (governance-correct, not yet operationally-live).

---

### WEALTH MCP Exposed — 2026-05-01

**Bug fixed:** wealth-organ ran with `transport="sse"` which only exposes GET/POST at non-standard paths. Fixed by changing to `transport="http"` in monolith.py line 4115.

WEALTH MCP live at `https://wealth.arif-fazil.com/mcp` (HTTP transport, session-based).

Added `wealth.arif-fazil.com` → `wealth-organ:8082` route to Caddyfile.

---

### arifOS MCP v0.2 REAL BACKEND — Deployed 2026-04-26

6 governance backend files wired into `server.py`: vault_chain.py, session_state.py, interceptor.py, forge_app.py, judge_app.py, vault_audit.py.

---

### arif-fazil.com .well-known Files — Cloudflare Cache Issue

API token lacks "Cache Purge" permission — manual purge required via Cloudflare Dashboard.

---

## Archived Logs

*Older entries in memory/*.md*
