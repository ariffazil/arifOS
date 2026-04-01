# arifOS Estate — Ground Truth Platform Audit

Date: 2026-04-01
Status: GROUND TRUTH AUDIT (实地勘察)
Scope: All domains, workflows, deploy targets

## Verified Live Infrastructure

```
Cloudflare (DNS + HTTPS + Cache)
arif-fazil.com       → GitHub Pages (SPA, machine files broken)
arifOS.arif-fazil.com → GitHub Pages (developer docs, working)
arifOS:8080          → VPS Docker
arifOS:8080/mcp      → MCP server (live)
apex.arif-fazil.com  → 404 (broken)

VPS (20+ containers)
traefik :80/:443     → Cloudflare entry, Docker routing
arifOS:8080/mcp      → Constitutional MCP server
postgres / redis      → Data stores
ollama               → Local model inference
```

## HTTP Status (Verified)

| URL | Status |
|-----|--------|
| arif-fazil.com/llms.txt | 200 (HTML content-type (broken) |
| arifOS.arif-fazil.com/ | 200 |
| arifOS:8080/mcp | 200 |
| apex.arif-fazil.com | 404 |

## Perplexity Advisory vs Reality

| Claim | Verdict |
|-------|---------|
| Cloudflare Pages for human site | FALSE — GitHub Pages |
| Cloudflare Pages for docs | FALSE — GitHub Pages |
| VPS handles MCP server | TRUE |
| GitHub Actions CI/CD | TRUE |
| Traefik routing | TRUE |
| apex subdomain live | FALSE — 404 |

## Critical Problem: Machine Files

GitHub Pages returns index.html for ALL non-file requests.
Solution: VPS nginx serves /llms.txt /.well-known/ directly.

## Decision Record

| Item | Decision | Reason |
|------|----------|--------|
| Machine files on arif-fazil.com | VPS nginx | GitHub Pages cant serve TXT/JSON |
| Human site on arifOS-fazil.com | GitHub Pages | Cheap, CDN-backed |
| MCP server | VPS Docker | Already working |
| apex subdomain | Deprecate | Broken redirect |

Ditempa Bukan Diberi [ΔΩΨ | ARIF-MAIN]
