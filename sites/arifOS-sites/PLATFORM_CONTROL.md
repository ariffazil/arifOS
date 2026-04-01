# PLATFORM CONTROL — arifOS Estate Architecture

**Status:** DRAFT
**Date:** 2026-04-01
**Scope:** arifOS estate — domains, CI/CD, hosting model, content ownership

This document is the **control plane** for the arifOS web estate. It defines:
- Where each domain points and what it serves
- How deployments work
- Who owns what content
- Cache and purge policy

It does NOT cover: site visual design, page inventory, or implementation config (see BLUEPRINT_v2.md for those).

---

## Architecture States

### State A — Stabilize (current)

GitHub Pages for static surfaces. VPS Docker for MCP runtime. GitHub Actions as CI/CD spine.

**Why State A:** Eliminates SPA routing errors during current stabilization. Simpler to operate while cleaning up broken subdomains and machine file delivery.

**Trade-off:** Preview deployments are weaker than Cloudflare Pages. No per-page cache rules. GitHub Pages always returns index.html for non-matching paths — machine files must not rely on SPA routing.

### State B — Target steady state

Cloudflare Pages for all static delivery. VPS Docker for MCP runtime. GitHub Actions as CI/CD spine. Targeted cache invalidation.

**Why State B:** Full edge cache control by content class, stronger preview deployments, Cloudflare Rules for machine file TTL, lower operational entropy at scale.

**Trigger:** Activate State B after: (1) machine files verified working, (2) docs migrated, (3) CI/CD proven reliable.

---

## Verified Live Infrastructure

```
Cloudflare (DNS + HTTPS)
├── arifOS-fazil.com         → GitHub Pages (State A) / Cloudflare Pages (State B)
├── arifos.arifOS-fazil.com  → GitHub Pages (State A) / Cloudflare Pages (State B)
├── arifOS:8080              → VPS Docker
│   └── traefik :80/:443    → arifOS container
├── arifOS:8080/mcp         → MCP server (live)
└── apex.arifOS-fazil.com    → DEPRECATED (404)

VPS (20+ containers)
├── traefik (Cloudflare entry)
├── arifOS (MCP server)
├── postgres / redis / ollama / qdrant
└── 17 others

GitHub Actions
├── deploy-sites.yml      → GitHub Pages (docs + dev)
├── deploy-vps.yml        → VPS SSH deploy (MCP server)
└── deploy-cloudflare.yml → Dashboard eval reports
```

---

## Domain Ownership

| Domain | Platform | Purpose | Content owner |
|--------|----------|---------|---------------|
| arifOS-fazil.com | GitHub Pages / Cloudflare Pages | Sovereign hub — identity + machine discovery + project summaries | Arif |
| arifos.arifOS-fazil.com | GitHub Pages / Cloudflare Pages | Full docs — architecture, floors, pipeline, install, APIs | Arif |
| arifOS:8080/mcp | VPS Docker | Live MCP runtime — tool execution, constitutional checks | Arif |
| apex.arifOS-fazil.com | DEPRECATED | Redirects to 404. Fold into /docs/apex/ on arifos domain. | N/A |

**Note:** All `.arifOS.com` domain variants in old docs must be corrected to `.arifOS-fazil.com`. Naming drift becomes deployment drift.

---

## Content Ownership Matrix

Defines which surface owns full content vs. summary for each topic.

| Topic | Hub (arifOS-fazil.com) | Docs (arifos.arifOS-fazil.com) | Notes |
|-------|----------------------|-------------------------------|-------|
| arifOS overview | Summary + link | Full architecture + all floors + pipeline | Never duplicate full content |
| APEX theory | Summary + link to github.com/ariffazil/APEX | Reference only | APEX repo is canonical source |
| GEOX | Summary + link to github.com/ariffazil/GEOX | Reference only | GEOX repo is canonical source |
| AAA | Summary + link | Full AAA docs | |
| waw / w@w | Summary + link to github.com/ariffazil/waw | Reference only | waw repo is canonical source |
| makcikGPT | Summary + link to github.com/ariffazil/makcikGPT | Reference only | |
| MCP API | Link to /mcp endpoint | Full transport reference | Hub links, docs explains |
| Installation | Summary | Full install + Docker steps | Never duplicate step-by-step |
| Deployment | Summary | Full deploy + VPS ops | |
| Tool registry | Link to /health | Full tool list with descriptions | /health is live source of truth |

**Rule:** If a topic appears fully on both hub and docs, docs wins as canonical. Hub must only summarize and link.

---

## Truth Ownership Matrix

Where facts live and who is allowed to state them.

| Fact type | Canonical source | Static artifact | Auto-updates? |
|-----------|-----------------|-----------------|---------------|
| Tool count + list | `arifOSmcp/server.py` + /health | llms.txt | Yes — generated at build |
| Floor definitions | `core/shared/floors.py` + `000/000_CONSTITUTION.md` | Docs floors table | No — update manually on change |
| Version number | `CHANGELOG.md` | README version field | No — update on release |
| MCP protocol version | `arifOSmcp/server.py` | README protocol field | No — update on change |
| Endpoint URLs | This document + DNS | README + hub pages | No — update on change |
| Architecture decisions | `ARCH/DOCS/` | Docs architecture section | No — changelog in doc |
| Agent behavior rules | `AGENTS.md` | README agent section | No — changelog in doc |

**Principle:** Static prose plus drifting facts is a risk. Any number in a static document should either auto-generate from source or be labeled as indicative only.

---

## Machine Files

Machine-readable discovery files served at stable canonical paths on arifOS-fazil.com.

| File | Purpose | Generated from | Served at |
|------|---------|---------------|----------|
| llms.txt | LLM context injection | arifOS/MEMORY.md + SOUL.md + REPOS.md | /llms.txt (stable URL) |
| robots.txt | Crawler control | Static | /robots.txt |
| sitemap.xml | Search indexing | Generated at build | /sitemap.xml |
| agent.json | Agent discovery | `waw/.well-known/agent.json` | /.well-known/agent.json |
| ai-plugin.json | Plugin discovery | `arifOS/docs/ai-plugin.json` | /.well-known/ai-plugin.json |
| manifest.json | PWA manifest | Static | /manifest.json |

**Policy:** Public path names for canonical discovery files NEVER change. /llms.txt and /.well-known/agent.json must always resolve at those exact paths.

- **Generation:** GitHub Actions generates machine files at build from versioned sources.
- **Serving:** Stable canonical URLs — versioned internally in content, not in path.
- **Purge:** Targeted — only republish machine files when their source content changes.

---

## Cache Classes (State B target)

| Class | Examples | TTL | Purge trigger |
|-------|----------|-----|--------------|
| Machine txt/json | llms.txt, .well-known/* | 1h, stale-while-revalidate | Source content changed |
| Semantic HTML | *.html | 1h stale-while-revalidate | CI/CD deploy |
| Immutable assets | /assets/*, *.css, *.js | 1y (immutable at build) | Never (filename versioned) |
| Docs | arifos.arifOS-fazil.com/* | 1h stale-while-revalidate | CI/CD deploy |

**State A (GitHub Pages):** Cache behavior is default GitHub Pages only. Machine files on GitHub Pages are unreliable — they require VPS nginx for Content-Type enforcement. Use the hosted VPS endpoint or self-host to serve machine files reliably.

---

## CI/CD Spine (GitHub Actions)

### On push to main

```
push to main
    ↓
Path filter: which files changed?
    ↓
arifOS-fazil.com source → build → deploy hub
arifos source → build → deploy docs
arifOSmcp/ source → build → deploy VPS runtime
    ↓
Generate machine files (llms.txt, sitemap.xml, .well-known/*)
    ↓
Selective purge: only machine files whose sources changed
    ↓
Smoke test: curl /health on arifOS
```

### On pull_request

- Preview deployments to temporary URLs
- Smoke test on preview URL
- Status check required to merge

### Failure behavior

- Static deploy failure → PR blocked, deploy-vps skipped
- Runtime deploy failure → VPS not touched, alert fired
- No partial deploys — all-or-none per surface

---

## Decision Log

| Decision | Why |
|----------|-----|
| Hub owns summaries, docs owns full | Eliminates duplication, roles are clear |
| Runtime is separate from static | Different deploy cadence, different ops model |
| Canonical machine files at root | AI agents and crawlers expect discovery files at root |
| Targeted purge over purge-everything | Lower blast radius, faster deploys |
| State A before State B | Stabilize broken machine files first, then optimize |
| apex subdomain deprecated | Was redirecting to blank — zero value, full confusion cost |

---

## Cutover Checklist (State A → State B)

- [ ] All machine files verified working at stable canonical paths
- [ ] Content ownership matrix reviewed and no duplication found
- [ ] CI/CD on push to main proven reliable for 3+ consecutive deploys
- [ ] Preview URLs working on pull_request
- [ ] Cloudflare Pages projects created for arifOS-fazil.com and arifos.arifOS-fazil.com
- [ ] DNS updated to point to Cloudflare Pages
- [ ] Old GitHub Pages deploys disabled
- [ ] Cloudflare cache classes verified in Cloudflare Rules dashboard
- [ ] Selective purge verified working for llms.txt and .well-known/*
- [ ] Rollback tested: revert to previous Cloudflare Pages deployment

---

## Scope Boundaries

**PLATFORM_CONTROL.md owns:** control plane, hosting model, CI/CD, domain ownership, cache policy, purge policy, truth ownership, decision log, cutover checklist.

**BLUEPRINT_v2.md owns:** site IA, page inventory, content ownership per page, visual rules, homepage structure, machine file content specifications.

**PLATFORM_AUDIT.md owns:** gap analysis, broken things found, migration risks, Perplexity advisory vs. reality comparison.

---

Ditempa bukan Diberi [ΔΩΨ | ARIF-MAIN]

---

## Cloudflare Credentials

| Secret | Value |
|--------|-------|
| CLOUDFLARE_ACCOUNT_ID | 22cc94b77b6481d2b054bee7952710e6 |
| CLOUDFLARE_API_TOKEN | Stored in GitHub Secrets — ariffazil/arifOS |
| Cloudflare Dashboard | https://dash.cloudflare.com/22cc94b77b6481d2b054bee7952710e6 |

