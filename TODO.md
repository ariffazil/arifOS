# arifOS TODO — Active Work Queue

**Version:** 2026.04.07
**Authority:** Muhammad Arif bin Fazil (999_VALIDATOR)
**SoT:** This file tracks active engineering work. ROADMAP.md owns horizon strategy.

> 888_HOLD items require explicit sovereign approval before execution.

---

## 🔴 P0 — Blockers (Ship This Week)

### ChatGPT Apps SDK Deployment (Path D)
- [x] `widget-csp.conf` — was MISSING, now created (`deployments/af-forge/widget-csp.conf`)
- [ ] **DNS**: Point `mcp.af-forge.io` → VPS IP (nginx currently configured for `arifos.federation`)
- [ ] **TLS**: Provision SSL cert for `mcp.af-forge.io` (nginx.conf has TLS block commented out — uncomment + run certbot)
- [ ] **nginx.conf**: Update `server_name arifos.federation` → `mcp.af-forge.io` in all server blocks
- [ ] **Verify**: `curl -I https://mcp.af-forge.io/widget/vault-seal` returns 200 with `frame-ancestors` CSP header
- [ ] **Vault999 volume backup**: Add `restic` or `borgbackup` cron before Phase 2 write-path opens (F11/F13 gate)

### Live MCP Tools (`/tools` returning 0)
- [ ] Investigate why `canonical_tools: 0` in `/health` — tools are registered but count is wrong
- [ ] Restart `arifosmcp` container after any code changes

---

## 🟡 P1 — Platform Agnosticism (Path A + B)

### Path A — Tool `platform=` Mode (1–2 weeks)
- [ ] Add `platform: Literal["mcp", "chatgpt_apps", "cursor", "api", "stdio"] = "mcp"` to all tool schemas in `tool_specs.py`
- [ ] Update `output_formatter.py` to dispatch on `platform`:
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
- [ ] `ARIFOS_APP_VERSION` in docker-compose.yml still hardcoded `2026.04.06` → update to `2026.04.07`
- [ ] Add `vault999-data` volume backup strategy (restic daily snapshot)
- [ ] Document `deploy.sh` usage — currently undocumented
- [ ] Multi-stage Dockerfile for `deployments/af-forge/` (separate from `arifosmcp/Dockerfile`)

### arifOS Runtime
- [ ] Fix `canonical_tools: 0` in `/health` (tools registered, count not propagating)
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
- [x] `/health` endpoint upgraded with SoT fields
- [x] `/.well-known/arifos-index.json` canonical index live
- [x] Landing page telemetry fixed (no `--` placeholders)
- [x] Lean `arifosmcp/Dockerfile` created
- [x] CHANGELOG.md, arifos.yml, AGENTS.md sealed
- [x] GitHub release `v2026.04.07` created with semantic notes
- [x] `af-forge/GEMINI.md` + `ALIGNMENT.md` updated to canonical `arifos.*` names
- [x] `waw/skills/.../verification-runbooks.md` updated to `arifos.init`
- [x] `widget-csp.conf` created (deployment blocker fixed)

---

*DITEMPA BUKAN DIBERI — Forged, Not Given [ΔΩΨ | ARIF]*
