# INVARIANTS.md — arifOS Constitutional Kernel
> **DITEMPA BUKAN DIBERI** — Federated Source of Truth.
> **Owner:** arifOS
> **Last verified:** 2026-05-25
> **Authority:** This file is the live port/source-of-truth for arifOS.

## Owns
- Constitutional F1-F13 governance law
- MCP kernel runtime (port 8088)
- VAULT999 append-only ledger
- 13 canonical MCP tools
- A2A mesh protocol
- Federation epistemology and memory

## Does NOT Own
- Execution shell (→ A-FORGE)
- GEOX earth intelligence (→ GEOX)
- WEALTH capital intelligence (→ WEALTH)
- WELL human readiness (→ WELL, operational)
- APEX verdict engine (→ APEX, archived)

## Live Ports

| Service | Port | Process |
|---------|------|---------|
| arifOS kernel | **8088** | `python -m arifos.main` (systemd: arifos.service) |

## Public URLs

| Endpoint | URL |
|----------|-----|
| Health | `https://arifos.arif-fazil.com/health` |
| MCP | `https://arifos.arif-fazil.com/mcp` |
| Tools | `https://arifos.arif-fazil.com/tools` |

## Required Health Check
```bash
curl https://arifos.arif-fazil.com/health
# Expected: {"status":"healthy","version":"kanon-..."}
```

## Forbidden Stale Assumptions
- ❌ arifOS on port `8080` — it is `8088`
- ❌ arifOS on port `8080` in Caddyfile — it is `8088`
- ❌ arifOS is the "MCP server" only — it is the constitutional kernel
- ❌ arifOS side branch is canonical — `main` is always canonical

## MCP Config
- Main config: `arifosmcp/server.py`
- `.mcp.json` endpoint: `http://127.0.0.1:8088/mcp`

## Agent Entry
1. Read `AGENT_KERNEL_START.md`
2. Read `README.md`
3. Read `AGENTS.md`
4. Run `scripts/check-estate-invariants.sh`
5. Inspect git status before editing

## Related Files
- `AGENT_KERNEL_START.md` — estate entry ritual
- `Caddyfile` — live routing (VPS runtime)
- `arifosmcp/server.py` — canonical MCP server
- `core/floors.py` — F1-F13 enforcement
