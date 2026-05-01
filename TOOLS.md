# TOOLS.md — Local Environment Notes

**Version:** 2026.05.01
**Purpose:** Safe local infrastructure notes only. No secrets, no credentials.

---

## What Goes Here

Environment-specific operational notes — SSH hosts, TTS, cameras, container names,
file paths, and infrastructure facts that are unique to this setup.

Skills define _how_ tools work. This file is for _your_ specifics.

---

## SSH Hosts

_(Add as needed — no actual credentials stored here.)_

| Alias | Host | User | Notes |
|-------|------|------|-------|
| af-forge | A-FORGE VPS | root | Primary VPS — arif-fazil.com + arifOS MCP |

---

## TTS

| Setting | Value |
|---------|-------|
| Preferred voice | _(not configured — add when known)_ |
| Default channel | telegram |

---

## Infrastructure

| Item | Value |
|------|-------|
| arifOS MCP container | `arifosmcp` (健康, Caddy proxied) |
| MCP endpoint | `https://mcp.arif-fazil.com/mcp` |
| Dashboard | `https://arifosmcp.arif-fazil.com/dashboard` |
| Site host path | `/root/sites/arif/` |
| Private key vault | `/root/sites/arif/.vault/did-ed25519.pem` |
| Vault999 path | `/root/volumes/vault999` |
| WELL state | `/root/WELL/state.json` |

---

## A2A Federation

| Item | Value |
|------|-------|
| AAA A2A Gateway | `aaa-a2a` on `arifos_core_network`, port 3001 → Caddy `aaa.arif-fazil.com` |
| Hermes ASI Agent | `hermes-agent` on `arifos_core_network`, port 3002 → Caddy `hermes.arif-fazil.com` |
| AAA judge endpoint | `http://hermes-agent:3002/judge` (AAA → Hermes for 888_JUDGMENT) |
| VAULT999 writer | `vault999-writer:5001` — reachable from `arifos_core_network` |
| Hermes image | `hermes-agent:v1.0.0` — A2A v1.0.0, 888_JUDGMENT (SEAL/HOLD_888/VOID) |

## arifOS MCP Bind Mounts (read-only where noted)

| Host path | Container path | Access |
|-----------|---------------|--------|
| `/root/arifOS/arifosmcp/runtime/tools_internal.py` | `/app/arifosmcp/runtime/tools_internal.py` | ro |
| `/root/WELL/state.json` | `/root/WELL/state.json` | ro |
| `/root/volumes/vault999` | `/var/lib/arifos/vault` | rw |

---

## OpenClaw

| Item | Value |
|------|-------|
| Workspace | `/srv/openclaw/workspace` |
| Gateway | openclaw gateway (systemd managed) |
| Skills dir | `/srv/openclaw/workspace/skills/` + `~/.agents/skills/` |
| Health probe | `skill: health-probe` |

---

## DO NOT Store Here

- Passwords or tokens
- API keys
- Database credentials
- Private keys (beyond path references)
- Raw secrets

Use path references only. Actual secrets stay in SECRETS.md (not committed to git).

---

**DITEMPA BUKAN DIBERI.**
