# arifOS Site Preservation Contract

**Version:** 1.0
**Date:** 2026-04-29
**Authority:** Muhammad Arif bin Fazil
**Scope:** All arifOS agents operating on production web surfaces

---

## Rule 1 — Existing Site Is Protected

The existing arifOS public surface (`arif-fazil.com`, `arifos.arif-fazil.com`, `mcp.arif-fazil.com`) is a live production artifact. Agents **may not**:

- Replace the homepage with a redesign
- Remove or disable existing routes
- Overwrite static files in `/var/www/html/` or `/root/sites/` without explicit intent
- Modify Caddyfile routing unless the change is explicitly required to expose a new endpoint
- Touch Docker volumes or run destructive operations

**Rollback anchor:** `preserve-site-before-mcp-<commit>` tag on every session start.

---

## Rule 2 — Additive First

New functionality must be added as **new pages/endpoints**, not by replacing existing ones.

| Desired addition | Correct approach |
|---|---|
| MCP evidence surface | Add `/mcp/status`, `/mcp/auth` alongside existing homepage |
| Tool listing | Add `/tools.json` and `/tools` page — don't rebuild homepage |
| Health identity | Add `X-Deployment-Hash` header to existing `/health` endpoint |
| Constitution floors | Add `/api/constitution` or extend existing `/constitution` response |

---

## Rule 3 — No Silent Redesign

Any of the following requires **explicit 888_JUDGE approval**:

- Homepage layout or theme change
- Route removal or redirect
- Renaming existing paths
- Replacing existing HTML files
- Modifying `server.py` beyond the ASGI mount block

---

## Rule 4 — Diff Discipline

Before every commit, the agent must:

```bash
git diff --name-only
git diff --stat
```

Then verify: only approved files were touched. If unexpected files appear in the diff → **HOLD**.

**Approved file allowlist:**
- `arifosmcp/runtime/rest_routes.py`
- `arifosmcp/runtime/landing_page.html`
- `arifosmcp/server.py` (ASGI mount block ONLY)
- `arifosmcp/runtime/build_info.py`
- `Dockerfile` (metadata ARGs/ENV/LABEL only)
- `docker-compose*.yml` (image tag / env / pull_policy only)
- `000/GOVERNANCE/SITE_PRESERVATION_CONTRACT.md` (this file)
- `Caddyfile` (only when routing change is explicitly required)

**Never allowed:**
- `docker system prune -a`
- `docker volume prune`
- Deleting `/var/www/html/` or `/root/sites/` files
- Modifying secrets or credentials
- Rewriting `server.py` core startup path

---

## Rule 5 — Production Truth

A change is **not complete** until live endpoints prove it. For every patch:

1. **Before**: note the rollback tag (`preserve-site-before-mcp-<commit>`)
2. **Deploy**: apply the patch
3. **Verify**: curl the endpoint — must return expected JSON/HTML
4. **Commit**: with changed files listed in the commit message
5. **Announce**: what was added, what was verified, what the rollback path is

---

## One Layer Per Patch

The correct execution sequence for any site work:

```
Layer 1: Backend endpoints (REST routes, JSON responses)
Layer 2: New human-readable pages (/tools, /mcp/status)
Layer 3: Homepage live-data integration (fetch from existing endpoints)
Layer 4: Design improvements (only after layers 1-3 are verified)
```

**Do not combine layers in a single session.**

---

## Rollback Procedure

```bash
# Find the preserve tag
git tag --list "preserve-site-*"

# Restore to preserved state
git checkout preserve/site-before-mcp-<commit>

# Or revert a bad commit
git revert <bad_commit_hash>
git push --force origin main  # only if explicitly approved
```

---

**DITEMPA BUKAN DIBERI — Forged, Not Given**
