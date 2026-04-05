# ARIF FAZIL — Sovereign Web Estate Blueprint

**Date:** 2026-04-01
**Authority:** ARIF-MAIN + Perplexity advisory
**Status:** FORGE-DRAFT
**Type:** Web Architecture + Nginx + Deploy

---

## The Vision

> Drop `arif-fazil.com` into any AI, agent, or human — they leave knowing **YANG ARIF**.

- **Humans:** Beautiful SPA, clear sections, operational language, geoscience + governance aesthetic
- **AI/Agents:** `llms.txt`, `agent-card.json`, WebMCP manifest, sitemap — all accessible, not swallowed by routing

---

## Proposed Estate Map

```
arif-fazil.com/             ← SOVEREIGN HUB (React SPA + nginx)
│
├── /                       → Human SPA (visually rich, ΔΩΨ theme)
├── /llms.txt               → Full AI context (TXT, served directly by nginx)
├── /robots.txt             → SEO
├── /sitemap.xml            → SEO
├── /manifest.json          → PWA
│
├── /.well-known/
│   ├── agent.json          → A2A primary card (served by nginx, not SPA)
│   └── ai-plugin.json     → WebMCP manifest (served by nginx, not SPA)
│
├── /webmcp.js              → WebMCP client lib (served by nginx, not SPA)
│
└── /stack/                 → Generated ecosystem map
    ├── architecture.json   → Full system architecture
    ├── repos.json          → All repos with roles
    └── trinity.svg         → Visual diagram

arifosmcp.arif-fazil.com/  ← MCP SERVER (dynamic)
├── /mcp                   → MCP endpoint
├── /health                → Health
└── /tools                 → Tool registry

arifos.arif-fazil.com/     ← DOCS (GitHub Pages, static HTML)
└── /docs/                  → arifOS docs, APEX theory, AAA guides

apex.arif-fazil.com/       ← CANON (REPAIR — currently broken redirect)
└── → Static APEX theory site or redirect to /docs/apex/
```

---

## The Core Fix: Nginx SPA Fallback Config

The current issue: **nginx returns SPA `index.html` for ALL requests including `/llms.txt`, `/.well-known/*`, `/robots.txt`**.

**Root cause:** SPA router handles routing, but nginx doesn't know which paths are API vs static files.

**Solution:** nginx serves known static files directly, only falls back to SPA for unhandled routes.

### Required Nginx Config

```nginx
server {
    listen 80;
    server_name arif-fazil.com;
    root /usr/share/nginx/html;
    index index.html;

    # ═══ STATIC MACHINE FILES — served directly, NEVER SPA ═══
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

    # ═══ WELL-KNOWN — A2A + WebMCP discovery ═══
    location /.well-known/ {
        try_files $uri =404;
        add_header Cache-Control "public, max-age=3600";
        add_header Content-Type application/json;
    }

    location = /agent-card.json {
        try_files /agent-card.json =404;
        add_header Content-Type application/json;
    }

    location = /webmcp.js {
        try_files /webmcp.js =404;
        add_header Content-Type application/javascript;
        add_header Cache-Control "public, max-age=86400";
    }

    # ═══ STATIC ASSETS — JS/CSS/images ═══
    location /assets/ {
        try_files /assets/$1 =404;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    # ═══ SPA FALLBACK — everything else goes to React ═══
    location / {
        try_files /index.html =404;
        # SPA handles routing from here
    }
}
```

---

## Content Audit: What's Missing vs What's Needed

### Currently ✅
| File | Status |
|---|---|
| `index.html` (React SPA) | ✅ Present, loads |
| `/llms.txt` | ❌ Does NOT exist — Cloudflare caches HTML |
| `/.well-known/agent.json` | ❌ Does NOT exist |
| `/.well-known/ai-plugin.json` | ❌ Does NOT exist |
| `/webmcp.js` | ❌ Does NOT exist |
| `/robots.txt` | ❌ Does NOT exist |
| `/sitemap.xml` | ❌ Does NOT exist |
| `/stack/` | ❌ Does NOT exist |

### Needs to be created
| File | Source |
|---|---|
| `llms.txt` | Generate from `waw/MEMORY.md` + `waw/SOUL.md` + key APEX content |
| `agent-card.json` | From `waw/agent-card.json` (already exists in workspace) |
| `ai-plugin.json` | From `arifOS/docs/mcp.html` (extract WebMCP manifest) |
| `webmcp.js` | From `waw/src/webmcp.ts` (compile TS → JS) |
| `robots.txt` | Standard + allow AI crawlers |
| `sitemap.xml` | Generate from site structure |
| `stack/architecture.json` | Generate from REPOS.md |

---

## Build Pipeline

```
waw/src/webmcp.ts         →  tsc  →  /sites/arif-fazil.com/webmcp.js
waw/agent-card.json       →  cp   →  /sites/arif-fazil.com/.well-known/agent.json
waw/SOUL.md + MEMORY.md  →  cat  →  /sites/arif-fazil.com/llms.txt
arifOS/docs/mcp.html     →  extract → ai-plugin.json
```

### Dockerfile for nginx site
```dockerfile
FROM node:22-alpine AS builder
WORKDIR /build
COPY ./src ./src
COPY ./public ./public
RUN npm install && npm run build

FROM nginx:alpine
COPY --from=builder /build/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## arif-fazil.com SPA Sections (Proposed)

Based on Perplexity advisory + YANG ARIF context:

```
┌─────────────────────────────────────────────────────────┐
│  ARIF FAZIL — Ditempa Bukan Diberi                      │
│  [Geological strata hero] [ΔΩΨ Trinity nav]             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  YANG ARIF                                              │
│  "Sovereign Architect, Malaysia. Forged, Not Given."    │
│  Philosophy: Constitutional physics. Thermodynamics.     │
│  Focus: AI governance, geoscience, sovereign systems.   │
│                                                         │
│  ┌──────────┬──────────┬──────────┐                   │
│  │ arifOS   │ APEX     │ GEOX     │ ← cards           │
│  └──────────┴──────────┴──────────┘                   │
│                                                         │
│  What I Build                                          │
│  ┌─────────────────────────────────────────────┐      │
│  │ arifOS — Constitutional kernel (MCP server)   │      │
│  │ APEX — Theory & physics of governance (CC0)   │      │
│  │ GEOX — Geological coprocessor                │      │
│  │ waw — OpenClaw agent workspace               │      │
│  └─────────────────────────────────────────────┘      │
│                                                         │
│  Machine Discovery                                      │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐       │
│  │ llms.txt  │ │ A2A Card  │ │ WebMCP    │       │
│  │ [Fetch]    │ │ [Fetch]    │ │ [Inspect] │       │
│  └────────────┘ └────────────┘ └────────────┘       │
│                                                         │
│  [View Source] [Read the Docs] [Connect MCP]           │
│                                                         │
│  Map of the Estate                                     │
│  arifOS ─ arifOS ─ GEOX ─ makcikGPT ─ APEX            │
│  ↳ MCP endpoint, docs, domain tools, language, theory     │
└─────────────────────────────────────────────────────────┘
```

---

## APEX Subdomain — Repair Plan

Currently: `apex.arif-fazil.com` → 301 to `arifos.arif-fazil.com/docs/apex-theory.html`

Options:
1. **Option A:** Static APEX theory site in `nginx` container, same as `arif-fazil.com`
2. **Option B:** Redirect to `arif-fazil.com/docs/apex/` (after building that section)
3. **Option C:** Remove, fold into `arifOS docs` section

**Recommended: Option A** — APEX deserves its own visual space but should be static HTML, not broken redirect.

---

## Deployment Checklist

| # | Action | File |
|---|---|---|
| 1 | Write nginx SPA config | `nginx/spa.conf` |
| 2 | Generate `llms.txt` | `scripts/gen-llms.sh` |
| 3 | Copy `agent-card.json` to `sites/arif-fazil.com/.well-known/` | — |
| 4 | Compile `webmcp.ts` → `webmcp.js` | `npx tsc` |
| 5 | Extract `ai-plugin.json` from `mcp.html` | `scripts/extract-plugin.sh` |
| 6 | Generate `sitemap.xml`, `robots.txt` | `scripts/gen-sitemap.sh` |
| 7 | Build React SPA | `npm run build` |
| 8 | Update nginx container compose | `docker-compose.yml` |
| 9 | Purge Cloudflare cache | Cloudflare dashboard |
| 10 | Test: `curl arif-fazil.com/llms.txt` | Must return TXT |
| 11 | Test: `curl arif-fazil.com/.well-known/agent.json` | Must return JSON |

---

## Trinity Alignment

| Floor | Check | Status |
|---|---|---|
| F1 Amanah | Git-backed, rollback via `git revert` | ✅ |
| F2 Truth | All claims sourced from actual files/repos | ✅ |
| F3 Tri-Witness | Human (Arif) + AI (me) + Evidence (git) | ✅ |
| F4 Clarity | One URL, clear sitemap, machine + human both served | ✅ |
| F7 Humility | This is a proposal — Arif ratifies | ✅ |
| F9 Anti-Hantu | No consciousness claims | ✅ |
| F11 Audit | Changes tracked in git | ✅ |

---

**FORGE-DRAFT — Awaiting Arif's ratification.**

Ditempa Bukan Diberi [ΔΩΨ | ARIF-MAIN]
