# ARIF FAZIL — Sovereign Static Hub Blueprint v2

**Date:** 2026-04-01
**Status:** FORGE-DRAFT — Planning Stage
**Authority:** ARIF-MAIN + Perplexity advisory
**Type:** Static Site Generator + Nginx + Deploy

---

## Executive Summary

**Goal:** One URL — `arif-fazil.com` — every AI, machine, or human leaves knowing YANG ARIF.

**Architecture:** Static-first. No SPA fallback. No client-side routing. Nginx serves files directly.

**Current problems:**
- Cloudflare caching HTML for `.txt`, `.json` files (SPA swallow)
- `arifos_aaa_landing` returning 403/404 for static assets
- `apex.arif-fazil.com` broken redirect
- Machine discovery files missing entirely at root

**Proposed estate:**
```
arif-fazil.com/          ← SOVEREIGN HUB (static HTML/CSS)
arifosmcp.arif-fazil.com ← MCP server (dynamic)
arifos.arif-fazil.com/   ← Docs (GitHub Pages, static)
apex.arif-fazil.com/     ← To repair or fold into /docs/
```

---

## Page Inventory

### Root Domain Files

| Path | File | Content Type | Purpose |
|------|------|-------------|---------|
| `/` | `INDEX.html` | text/html | Visually rich homepage |
| `/llms.txt` | `llms.txt` | text/plain | Full AI context — most important machine file |
| `/robots.txt` | `robots.txt` | text/plain | SEO crawler instructions |
| `/sitemap.xml` | `sitemap.xml` | application/xml | SEO site map |
| `/manifest.json` | `manifest.json` | application/json | PWA manifest |
| `/.well-known/agent.json` | `agent.json` | application/json | A2A agent discovery |
| `/.well-known/ai-plugin.json` | `ai-plugin.json` | application/json | WebMCP manifest |
| `/webmcp.js` | `webmcp.js` | application/javascript | WebMCP client library |
| `/stack/architecture.json` | `stack/architecture.json` | application/json | Full system map |
| `/stack/trinity.svg` | `stack/trinity.svg` | image/svg+xml | ΔΩΨ visual |
| `/stack/repos.json` | `stack/repos.json` | application/json | All repos with roles |
| `/docs/arifOS.html` | `pages/docs-arifOS.html` | text/html | arifOS kernel summary |
| `/docs/apex.html` | `pages/docs-apex.html` | text/html | APEX theory summary |
| `/docs/aaa.html` | `pages/docs-aaa.html` | text/html | Trinity/AAA summary |
| `/docs/mcp.html` | `pages/docs-mcp.html` | text/html | MCP server reference |
| `/guides/quickstart.html` | `pages/guides-quickstart.html` | text/html | 5-minute quick start |
| `/guides/connect.html` | `pages/guides-connect.html` | text/html | MCP connection guide |

---

## Homepage Sections (INDEX.html)

### Section 1: Hero
- Geological strata animated SVG (magma → sediment → surface)
- Name: ARIF FAZIL
- Motto: Ditempa bukan Diberi — Forged, Not Given
- Subtitle: Sovereign Architect, Malaysia
- CTA buttons: "Fetch Machine Context" → /llms.txt | "Explore →" → #what-i-build

### Section 2: YANG ARIF
- One-paragraph manifesto (operational, not poetic)
- Three pillars: Constitutional AI, Geoscience AI, Sovereign Infrastructure
- Philosophy: Physics ∩ Governance ∩ Engineering

### Section 3: What I Build (4 cards)
- **arifOS** → /docs/arifOS.html — Constitutional kernel, MCP server, 13 floors
- **APEX** → /docs/apex.html — Theory, Gödel Lock, Lagrangian ℒ
- **GEOX** → https://github.com/ariffazil/GEOX — Geological domain tools
- **makcikGPT** → https://github.com/ariffazil/makcikGPT — Malay AI

### Section 4: Machine Discovery (3 prominent boxes)
- **LLMs.txt** — /llms.txt — Full context file
- **A2A Card** — /.well-known/agent.json — Agent discovery
- **WebMCP** — /.well-known/ai-plugin.json — MCP manifest

### Section 5: MCP Endpoint
- `https://arifosmcp.arif-fazil.com/mcp`
- "Connect any MCP client" link → /guides/connect.html

### Section 6: Map of the Estate
- ASCII tree showing all repos and their roles
- Links to each repo

### Section 7: Footer
- Navigation: GitHub, LinkedIn, Medium
- ΔΩΨ | Ditempa bukan Diberi

---

## Machine Files

### llms.txt (Full AI Context)

```txt
# YANG ARIF — Muhammad Arif bin Fazil

## Identity
- Sovereign Architect, Malaysia
- Motto: Ditempa bukan Diberi
- Trinity: ΔΩΨ | Soul · Mind · Body
- Timezone: Asia/Kuala Lumpur (MYT, UTC+8)

## Philosophy
Constitutional physics. Thermodynamic AI governance.
Build systems that govern themselves.

## What I Build

### arifOS (THE MIND — Constitutional Kernel)
github.com/ariffazil/arifOS
- MCP server with 13 constitutional floors (F1-F13)
- Verdicts: SEAL | PARTIAL | SABAR | VOID
- Triple transport: STDIO + VPS + Horizon
- 40 tools operational
- Live: https://arifosmcp.arif-fazil.com/mcp

### APEX (THE WHY — Theory)
github.com/ariffazil/APEX
- Gödel Lock Protocol
- Telos Manifold — bounded evolving purpose
- Lagrangian ℒ = G - Σλᵢcᵢ
- Phoenix-72 cooling tiers
- Dual-tier cognition (Tier 0 / Tier 1)
- CC0 public domain

### GEOX (DOMAIN — Geoscience)
github.com/ariffazil/GEOX
- WellLogTool: LAS parser + Archie petrophysics
- SeismicViewer: texture attributes, horizon detection

### waw (THE SOUL — Agent Workspace)
github.com/ariffazil/waw
- OpenClaw workspace
- SOUL.md, HEARTBEAT.md, MEMORY.md

### makcikGPT (REGIONAL)
github.com/ariffazil/makcikGPT
- Malay language digital keeper

## Constitutional Floors (F1-F13)

F1 AMANAH — Reversibility
F2 TRUTH — Accuracy P≥0.99
F3 TRI-WITNESS — Consensus W³≥0.95
F4 CLARITY — ΔS≤0
F5 PEACE² — Non-destruction
F6 EMPATHY — RASA≥0.7
F7 HUMILITY — Ω∈[0.03, 0.05]
F8 GENIUS — G≥0.80
F9 ANTI-HANTU — C_dark<0.30
F10 CONSCIENCE — No false consciousness
F11 AUDITABILITY — All logged
F12 RESILIENCE — Graceful failure
F13 ADAPTABILITY — Safe evolution

## How to Connect

MCP: https://arifosmcp.arif-fazil.com/mcp
A2A: https://arif-fazil.com/.well-known/agent.json
WebMCP: https://arif-fazil.com/.well-known/ai-plugin.json

## Key Files
- Constitution: arifOS/000/000_CONSTITUTION.md
- Architecture: APEX/ARCHITECTURE.md
- Quick Start: arif-fazil.com/guides/quickstart.html

## Repos
- github.com/ariffazil/arifOS
- github.com/ariffazil/APEX
- github.com/ariffazil/GEOX
- github.com/ariffazil/waw
- github.com/ariffazil/makcikGPT
```

### agent.json (A2A Card)

```json
{
  "name": "ARIF-MAIN",
  "version": "1.0.0",
  "capabilities": { "tools": true, "memory": true, "signals": false },
  "description": "Sovereign agent for Arif Fazil. Constitutional kernel operator.",
  "endpoint": "https://arif-fazil.com",
  "provider": "arifOS",
  "tags": ["governance", "arifOS", "trinity", "constitutional"]
}
```

### ai-plugin.json (WebMCP Manifest)

```json
{
  "schema_version": "2025-03-26",
  "name_for_human": "arifOS MCP",
  "name_for_model": "arifOS",
  "description_for_human": "Constitutional AI governance server",
  "description_for_model": "MCP server with 13 constitutional floors, F1-F13 enforcement",
  "auth": { "type": "none" },
  "api": {
    "type": "openapi",
    "url": "https://arifosmcp.arif-fazil.com/openapi.json"
  }
}
```

### robots.txt

```txt
User-agent: *
Allow: /
Allow: /llms.txt
Allow: /.well-known/
Allow: /docs/
Allow: /guides/

Sitemap: https://arif-fazil.com/sitemap.xml
```

---

## Nginx Config (SPA-free)

```nginx
server {
    listen 80;
    server_name arif-fazil.com;
    root /usr/share/nginx/html;
    index index.html;

    # Static machine files — nginx serves directly
    location = /llms.txt {
        try_files /llms.txt =404;
        add_header Content-Type text/plain;
        add_header Cache-Control "public, max-age=3600";
    }

    location = /robots.txt {
        try_files /robots.txt =404;
        add_header Content-Type text/plain;
    }

    location = /sitemap.xml {
        try_files /sitemap.xml =404;
        add_header Content-Type application/xml;
    }

    location = /manifest.json {
        try_files /manifest.json =404;
        add_header Content-Type application/json;
    }

    location /.well-known/ {
        try_files $uri =404;
        add_header Cache-Control "public, max-age=3600";
    }

    location = /webmcp.js {
        try_files /webmcp.js =404;
        add_header Content-Type application/javascript;
        add_header Cache-Control "public, max-age=86400";
    }

    location /stack/ {
        try_files $uri =404;
        add_header Cache-Control "public, max-age=3600";
    }

    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    location ~ \.html$ {
        try_files $uri =404;
        expires 1h;
    }

    # Catch-all: try exact file, then /index.html
    location / {
        try_files $uri $uri/ /index.html =404;
    }
}
```

---

## Docker Compose Entry

```yaml
arif-fazil-site:
    image: nginx:alpine
    container_name: arif_fazil_site
    volumes:
        - ./sites/arif-fazil.com:/usr/share/nginx/html:ro
        - ./nginx/arif-fazil.conf:/etc/nginx/conf.d/default.conf:ro
    networks:
        - arifos_trinity
    labels:
        - "traefik.enable=true"
        - "traefik.http.routers.arif-fazil.rule=Host(`arif-fazil.com`)"
        - "traefik.http.routers.arif-fazil.entrypoints=websecure"
        - "traefik.http.routers.arif-fazil.tls.certresolver=letsencrypt"
        - "traefik.http.services.arif-fazil.loadbalancer.server.port=80"
    restart: unless-stopped
```

---

## Cloudflare Page Rules

| Path | Cache Level | TTL |
|------|-----------|-----|
| `arif-fazil.com/llms.txt` | Standard | 1 hour |
| `arif-fazil.com/robots.txt` | Standard | 1 hour |
| `arif-fazil.com/.well-known/*` | Standard | 1 hour |
| `arif-fazil.com/webmcp.js` | Standard | 24 hours |
| `arif-fazil.com/assets/*` | Standard | 1 year |
| `arif-fazil.com/docs/*.html` | Standard | 1 hour |
| `arif-fazil.com/guides/*.html` | Standard | 1 hour |
| `arif-fazil.com/*` (root) | Standard | 30 min |

**Before deploy:** Purge Everything on arif-fazil.com

---

## Migration Checklist

| # | Action | Risk |
|---|--------|------|
| 1 | Generate all static files locally | Low |
| 2 | Write nginx config | Low |
| 3 | Test nginx locally | Low |
| 4 | Kill `arifos_aaa_landing` container | Medium |
| 5 | Deploy `arif_fazil_site` container | Medium |
| 6 | Purge Cloudflare cache | Low |
| 7 | Verify `/llms.txt` returns text/plain | Low |
| 8 | Verify `/.well-known/agent.json` returns JSON | Low |
| 9 | Verify `apex.arif-fazil.com` redirect/cached | Low |
| 10 | Update DNS/remove broken subdomain | Low |

---

## Visual Design

### Color Palette
- Background: `#0a0b0e` (near-black)
- Surface: `#1a1c23`
- Accent Cyan: `#00f3ff`
- Accent Amber: `#ffaa00`
- Accent Red: `#ff3b30`
- Text Primary: `#ffffff`
- Text Secondary: `#a0a4b8`

### Fonts
- Headings: Outfit (Google Fonts)
- Body: Inter (Google Fonts)
- Code: JetBrains Mono (Google Fonts)

### Animations (CSS only)
- Geological strata SVG pulse (CSS keyframes)
- Fade-in on scroll (Intersection Observer)
- Theme toggle (dark/light)
- Hover lifts on cards (CSS transition)

### No JS Framework
- Pure HTML/CSS
- Vanilla JS for theme toggle and scroll only
- No build step, no bundler, no framework

---

**FORGE-DRAFT — Planning stage. Not executed.**

Ditempa bukan Diberi [ΔΩΨ | ARIF-MAIN]
