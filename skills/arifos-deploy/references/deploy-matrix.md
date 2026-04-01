# Deploy Matrix — arifOS Estate

**Status:** OPERATIONAL — update when surfaces change

---

## Surface → Platform → CI Mapping

| Surface | Platform | CI Workflow | Trigger | Preview |
|---------|----------|-------------|---------|---------|
| arifOS-fazil.com (hub) | GitHub Pages (State A) / Cloudflare Pages (State B) | `deploy-hub.yml` | `sites/arifOS-fazil.com-source/**`, `.github/workflows/deploy-hub.yml` | Yes (PR deploy) |
| arifos.arifOS-fazil.com (docs) | GitHub Pages | `deploy-sites.yml` | `arifOSmcp/sites/developer/**`, `.github/workflows/deploy-sites.yml` | Yes |
| arifOS:8080/mcp (runtime) | VPS Docker | `deploy-vps.yml` | `arifOSmcp/**`, `docker-compose.yml`, `Dockerfile` | No |
| Machine files (llms.txt etc.) | GitHub Pages (same as hub) | `deploy-hub.yml` | `**/llms.txt`, `**/.well-known/**`, `**/robots.txt`, `**/sitemap.xml` | No |

---

## DNS Configuration

| Domain | CNAME / A | Points to | SSL |
|--------|-----------|-----------|-----|
| arifOS-fazil.com | CNAME | github.com → Cloudflare → GitHub Pages | Cloudflare Full |
| arifos.arifOS-fazil.com | CNAME | github.com → Cloudflare → GitHub Pages | Cloudflare Full |
| arifOS.arifOS-fazil.com | A | 72.62.71.199 (VPS IP) | Cloudflare Full |
| apex.arifOS-fazil.com | — | DEPRECATED — remove | — |

**Note:** All domains proxied through Cloudflare. DNS changes via Cloudflare dashboard or `wrangler`.

---

## Secrets Required

| Secret | Where stored | Used by | Access |
|--------|-------------|---------|--------|
| CLOUDFLARE_API_TOKEN | GitHub Secrets | `wrangler`, CI/CD | Needs human to create |
| CLOUDFLARE_ACCOUNT_ID | GitHub Secrets | `wrangler` | 22cc94b77b6481d2b054bee7952710e6 |
| VPS_HOST | GitHub Secrets | deploy-vps.yml | Encrypted, not readable |
| VPS_USERNAME | GitHub Secrets | deploy-vps.yml | Encrypted, not readable |
| VPS_SSH_KEY | GitHub Secrets | deploy-vps.yml | Encrypted, not readable |
| VPS_TAILSCALE_IP | GitHub Secrets | deploy-vps.yml | Encrypted, not readable |

---

## Content Ownership

| Content | Canonical source | Hub | Docs | Runtime |
|---------|----------------|-----|------|---------|
| arifOS overview | README.md, SOUL.md | Summary + link | Full | — |
| APEX theory | github.com/ariffazil/APEX | Summary + link | Reference | — |
| GEOX | github.com/ariffazil/GEOX | Summary + link | Reference | — |
| makcikGPT | github.com/ariffazil/makcikGPT | Summary + link | Reference | — |
| AAA | AAA/docs/ | Summary | Full | — |
| MCP endpoint | arifOSmcp/server.py | Link | Reference | Live |
| Tool registry | /health (live) | Link | Reference | Live |
| Architecture | ARCH/DOCS/ | — | Full | — |
| Floors (F01-F13) | core/shared/floors.py | Summary | Full | Live |

---

## GitHub Pages Configuration

- **arifOS repo** — GitHub Pages enabled, source = `main` branch `/ (root)`
- **CNAME file** — must contain `arifos.arifOS-fazil.com` for docs subdomain
- **Custom domain** — configured in repo Settings → Pages

**Note:** When hub and docs both need GitHub Pages from the same repo, they must use path-based routing or be separate Pages sites via CNAME subdomains. Current: docs uses `arifos.arifOS-fazil.com` CNAME pointing to same Pages site as root.
