# PHOENIX-72 Archive — Obsolete Migration Crisis Docs

**Archived:** 2026-05-26  
**Reason:** These docs were created during the Docker→bare-metal systemd migration (PHOENIX-72). They document a crisis state that is now resolved. All GEOX, WEALTH, WELL services are live on their correct ports.

## What Was Wrong (Historical)

| Issue | Status |
|-------|--------|
| GEOX port 8081 not listening | ✅ FIXED — GEOX MCP now live on port 8081 |
| WEALTH offline | ✅ FIXED — WEALTH MCP live on port 18082 |
| WELL offline | ✅ FIXED — WELL MCP live on port 18083 |
| All domain tools returning DEGRADED | ✅ FIXED — All tools operational |

## Files Archived

- `TOOL_LIFECYCLE_STATUS.md` — Listed all tools as DEGRADED
- `PHOENIX72_GAP_MATRIX.md` — Port mapping during migration
- `PERMISSION_RISK_REPORT.md` — Risk assessment during crisis
- `MIGRATION_EXECUTION_PLAN.md` — Migration steps (now complete)
- `MIGRATION_MAP.md` — Port topology during migration

## Current Truth

See `/root/arifOS/docs/SOT_MAP.md` for current federation state.

**DITEMPA BUKAN DIBERI — Crisis resolved, 2026-05-26**
