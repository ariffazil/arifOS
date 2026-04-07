# arifOS TODO — Active Work Queue

**Version:** 2026.04.07-TIER1-SEALED
**Authority:** Muhammad Arif bin Fazil (999_VALIDATOR)
**SoT:** This file tracks active engineering work. ROADMAP.md owns horizon strategy.

> 888_HOLD items require explicit sovereign approval before execution.

---

## 🔴 P0 — Blockers (Ship This Week)

### ChatGPT Apps SDK Deployment (Path D)
- [x] `widget-csp.conf` — was MISSING, now created (`deployments/af-forge/widget-csp.conf`)
- [x] **nginx.conf**: `server_name` updated to `arifosmcp.arif-fazil.com` — consolidated, `mcp.af-forge.io` retired (2026.04.07)
- [x] **DNS-ready**: `arifosmcp.arif-fazil.com` already live via Traefik + Cloudflare
- [x] **DNS**: No action needed — domain consolidated to `arifosmcp.arif-fazil.com`
- [x] **TLS**: Cert extracted from Traefik `acme.json` → `deployments/af-forge/ssl/` (expires 2026-06-03); HTTPS block uncommented
- [x] **widget route**: `GET /widget/vault-seal` live on `arifosmcp.arif-fazil.com` with `frame-ancestors` CSP (served from Python app)
- [x] **Verify**: `curl -I https://arifosmcp.arif-fazil.com/widget/vault-seal` returns 200 with CSP header
- [ ] **Vault999 volume backup**: Add `restic` or `borgbackup` cron before Phase 2 write-path opens (F11/F13 gate)

### Live MCP Tools (`/tools` returning 0)
- [x] `canonical_tools` / `total_tools` fields added to `/health` endpoint (0461252f)
- [x] Duplicate `get_constitutional_health` registration removed from `server_horizon.py` (0461252f)
- [x] **`arifosmcp` container restarted on VPS** — `canonical_tools: 10` confirmed
- [x] **Verify**: `curl https://arifosmcp.arif-fazil.com/health | jq .canonical_tools` returns 10 ✅

---

## 🟡 P1 — Platform Agnosticism (Path A + B)

### Path A — Tool `platform=` Mode (1–2 weeks)
- [x] `platform: str = "unknown"` param added to all 10 tool functions in `tools.py` (ff78faef)
- [x] `_stamp_platform()` stamps `platform_context` onto every envelope
- [ ] Upgrade to `Literal["mcp", "chatgpt_apps", "cursor", "api", "stdio"]` type in `tool_specs.py` schemas
- [ ] Implement `output_formatter.py` dispatch on `platform`:
  - `chatgpt_apps` → widget-renderable JSON with `render_hint` field
  - `api` → flat JSON, no MCP envelope
  - `stdio` → human-readable text
  - `mcp` (default) → current behavior unchanged
- [ ] Add `platform` to `ToolExecutionContext` in `schemas.py`
- [ ] Test: `arifos.judge(platform="chatgpt_apps")` returns widget JSON

### Path B — MCP Profile Gateway (4–6 weeks)
- [ ] Design `ProfileMiddleware` — reads `X-Arifos-Platform` header at connection
- [ ] Define 4 profiles: `chatgpt_apps`, `cursor`, `enterprise`, `stdio`
- [ ] Profile → tool allowlist mapping in `tool_specs.py`
- [ ] Profile → output format mapping (reuses Path A formatters)
- [ ] Rate limiting per profile (enterprise gets higher limits)
- [ ] Tests: each profile exposes correct tool subset

---

## 🟢 P2 — Operational Hardening

### Docker / Deployment
- [x] `ARIFOS_APP_VERSION` in `docker-compose.yml` updated to `2026.04.07` (2026.04.07)
- [x] `arifosmcp/Dockerfile` lean multi-stage build created (6cb52348)
- [ ] `deployments/af-forge/Dockerfile` — verify multi-stage build is correct for VPS
- [ ] Add `vault999-data` volume backup strategy (restic daily snapshot)
- [ ] Document `deploy.sh` usage — currently undocumented

### arifOS Runtime
- [x] `canonical_tools` + `total_tools` fields added to `/health` — structural fix deployed (0461252f)
- [ ] **VPS restart required** to confirm `canonical_tools: 10` live
- [ ] `build_info.py` — ensure `ARIFOS_APP_VERSION` env var is read in container context
- [ ] Entropy budget: implement `chaos_score()` across all MCP endpoints (ROADMAP H1 pending)
- [ ] Provenance ledger: wire `arifos.vault` directly to AGI Mind Provenance

---

## 🔵 P3 — Future Horizons (ROADMAP alignment)

### Path C — REST Constitutional API (8–12 weeks, 2027)
- [ ] Design `POST /api/v1/judge`, `POST /api/v1/init`, `POST /api/v1/sense`, `GET /api/v1/health`
- [ ] API key auth layer (JWT or HMAC-signed tokens)
- [ ] OpenAI custom actions manifest pointing to REST endpoints
- [ ] Anthropic tool use adapter
- [ ] Python + TypeScript SDK client packages
- [ ] Rate limiting + versioning (`/api/v1/` prefix)

### ChatGPT Apps Phase 2 (after F11/F13 review)
- [ ] Write-path operations via ChatGPT widget (888_HOLD required)
- [ ] BLS attestation (3-of-5 juror quorum) for vault writes
- [ ] Explicit F11 (identity binding) + F13 (sovereign approval) gates before any write

### MCP Registry Submissions
- [ ] Claude Desktop marketplace: submit `io.github.ariffazil/arifosmcp`
- [ ] Cursor MCP directory: submit both entries
- [ ] LobeHub: sync descriptions with registry

---

## ✅ DONE (This Session — 2026.04.07)

- [x] Versioned file unification (−3841 lines): `tools_v2.py` → `tools.py` etc.
- [x] `arifos.v2.*` namespace fully purged from all active code
- [x] `/health` endpoint upgraded with SoT fields + `canonical_tools` / `total_tools`
- [x] `/.well-known/arifos-index.json` canonical index live
- [x] Landing page telemetry fixed (no `--` placeholders)
- [x] Lean `arifosmcp/Dockerfile` created
- [x] CHANGELOG.md, arifos.yml, AGENTS.md sealed
- [x] GitHub release `v2026.04.07` created with semantic notes
- [x] `af-forge/GEMINI.md` + `ALIGNMENT.md` updated to canonical `arifos.*` names
- [x] `waw/skills/.../verification-runbooks.md` updated to `arifos.init`
- [x] `widget-csp.conf` created (deployment blocker fixed)
- [x] `nginx.conf` `server_name arifosmcp.arif-fazil.com` — consolidated (mcp.af-forge.io retired)
- [x] `docker-compose.yml` service renamed `arifos-mcp`, env vars to `ARIFOS_MCP_*`, version `2026.04.07`
- [x] `__main__.py` env var aliases updated to `ARIFOS_MCP_*` (platform agnosticism)
- [x] `platform=` param added to all 10 tool functions (Path A foundation)
- [x] Duplicate `get_constitutional_health` registration fixed in `server_horizon.py`
- [x] `_security_check()` runtime hardening audit added to `server.py`
- [x] Merge conflict resolution: 55 upstream commits reconciled (8e1f52d7)

---

*DITEMPA BUKAN DIBERI — Forged, Not Given [ΔΩΨ | ARIF]*
