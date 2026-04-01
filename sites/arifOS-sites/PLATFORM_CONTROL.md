# PLATFORM CONTROL — arifOS Estate v3

**Status:** DRAFT
**Date:** 2026-04-01
**Author:** ARIF-MAIN + Perplexity review

---

## Platform Decisions (VERIFIED)

| Domain | Platform | Rationale |
|--------|----------|-----------|
| arifOS-fazil.com | GitHub Pages | CDN-backed, zero ops, deploy-on-push |
| arifos.arifOS.com | GitHub Pages | Docs remain canonical |
| arifOS.arifOS.com:8080 | VPS Docker | Runtime needs process control |
| Machine files | GitHub Pages artifact | Versioned at build |
| CI/CD spine | GitHub Actions | Source = truth, push → deploy |
| DNS + HTTPS | Cloudflare | Already configured |

---

## Sitemap (EXACT)

```
arifOS-fazil.com/
├── /                    → GitHub Pages
├── /llms.txt            → Generated at build from arifOS/MEMORY.md + SOUL.md
├── /robots.txt           → Generated
├── /sitemap.xml         → Generated
├── /.well-known/
│   ├── agent.json       → From waw/.well-known/
│   └── ai-plugin.json   → From arifOS/docs/
├── /projects/
│   ├── arifOS.html     → Summary + link to arifos.arifOS.com
│   ├── GEOX.html       → Summary + link to github
│   └── makcikGPT.html   → Summary + link to github
└── /stack/
    ├── architecture.json → Generated from REPOS.md
    └── trinity.svg      → Static asset
```

---

## Cache Classes

| Class | Files | TTL |
|-------|-------|-----|
| Machine txt/json | llms.txt, .well-known/* | 1h |
| Semantic HTML | *.html | 1h stale-while-revalidate |
| Versioned assets | /assets/*, *.css | 1y (immutable at build) |
| Docs | arifos.arifOS.com/* | 1h stale-while-revalidate |

Purge: Targeted only for changed machine files (llms.txt, .well-known/*).

---

## CI/CD Path

```
push to main
    ↓
GitHub Actions: build arifOS-fazil.com
    ↓
GitHub Pages artifact
    ↓
Cloudflare CDN (stale-while-revalidate: 3600)
    ↓
arifOS-fazil.com updated
```

---

## What's NOT in scope (DEFER)

- webmcp.js — Not publicly justified
- Theme toggle — Dark-first only
- Full Nginx config — Implementation detail, later appendix
- Docker Compose for static hub — Runtime note only
- apex.arifOS subdomain — Deprecated

---

## Perplexity Fixes Applied

| Issue | Fix |
|-------|------|
| Mixed hosting philosophy | GitHub Pages for all static, VPS Docker only for MCP runtime |
| Docs duplication | arifos.arifOS.com owns full docs, arifOS-fazil.com owns summaries |
| Over-mythic llms.txt | Plain functional descriptions, internal labels removed |
| Tool count drift | Generated from source at build, not hardcoded |
| Color system cyan/amber/red | Kept as-is, no new tokens |
| SPA routing swallowing files | GitHub Pages + versioned machine files |

---

Ditempa bukan Diberi [ΔΩΨ | ARIF-MAIN]
