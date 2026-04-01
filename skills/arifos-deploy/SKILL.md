---
name: arifos-deploy
description: "arifOS sovereign deployment: static hub, docs, runtime, and machine files. Use when deploying arifOS estate surfaces. Encodes deployment philosophy, estate roles, CI/CD policy, machine file invariants, and rollback doctrine. Triggers: deploy, build site, CI/CD, publish, machine files, llms.txt, static hub, Cloudflare, GitHub Pages, VPS runtime."
---

# arifOS Deploy — Sovereign Deployment Doctrine

Ditempa Bukan Diberi. Every deployment is a thermodynamic state transition. Only deploy what is proven reversible.

---

## Core Invariants (Never Change)

These are constitutional-level constraints. No tool, command, or convenience may violate them.

### The Three Surfaces

```
arifOS-fazil.com     → Hub (identity, summaries, machine discovery)
arifos.arifOS-fazil.com → Docs (full technical content)
arifOS:8080/mcp     → Runtime (constitutional tool execution)
```

**Role rule:** Hub never hosts full docs content. Docs never hosts hub content. Runtime is never a static site. These boundaries never swap.

### Machine Discovery Invariants

Machine-readable files MUST be at root-level stable canonical paths:

```
/llms.txt               → LLM context injection (text/plain)
/robots.txt             → Crawler control
/sitemap.xml            → Search indexing
/.well-known/agent.json → Agent discovery (application/json)
/.well-known/ai-plugin.json → Plugin manifest
```

**Rule:** These paths NEVER change. They never route through SPA. They never redirect. They always return correct Content-Type. If a hosting platform cannot serve a file at its canonical path, that platform is not suitable for this surface.

### Content-Type Requirements

| File | Content-Type |
|------|-------------|
| llms.txt | text/plain; charset=utf-8 |
| agent.json | application/json |
| robots.txt | text/plain |
| sitemap.xml | application/xml |

**Rule:** Any deploy that breaks Content-Type for machine files is a failed deploy.

---

## CI/CD Policy

### Push-to-Main Spine

Every deploy MUST be GitHub Actions triggered by push to main. No manual `scp` or FTP. No exceptions.

### Pre-Deploy Gates (888_JUDGE analog)

Before any production deploy, the pipeline checks:
1. Source files validated (HTML syntax, machine files present)
2. Health check endpoint reachable
3. Rollback state documented (what to revert and how)

### Health Check Requirement

Every runtime deploy MUST verify `/health` returns 200 before marking deploy complete. If health check fails, deploy is marked failed — not degraded-ok.

### Rollback Mandate (F1 AMANAH)

Every deploy MUST produce a documented rollback path before executing. Rollback must be achievable in ≤2 minutes without data loss.

**Standard rollback:** Re-run previous successful workflow. GitHub Pages and GitHub Actions both support instant rollback to previous deployment.

---

## Deploy Decision Rules

### When to Deploy Hub

Hub deploys when files in `sites/arifOS-fazil.com-source/pages/`, `assets/`, machine files, or `deploy-hub.yml` workflow change.

### When to Deploy Docs

Docs deploys when files in `arifOSmcp/sites/developer/` or `deploy-sites.yml` workflow change.

### When to Deploy Runtime

Runtime deploys when `arifOSmcp/`, `docker-compose.yml`, `Dockerfile`, or `deploy-vps.yml` change. Requires health check confirmation.

### When NOT to Deploy

Do NOT deploy if:
- Only documentation (.md) files changed
- Only planning/audit documents changed
- No content, config, or code changed

Path filters in GitHub Actions enforce this automatically.

---

## Cache Purge Doctrine

### Targeted Purge Only

Purge ONLY files whose source content changed:
- `/llms.txt` → republish when MEMORY.md, SOUL.md, or REPOS.md changes
- `/.well-known/agent.json` → republish when `waw/.well-known/agent.json` changes
- HTML pages → republish on content or layout change

### Purge Trigger

Cache purge is CI-triggered, not blanket. Default GitHub Pages cache is acceptable. Cloudflare Pages cache purge only on explicit content change.

### No Purge-Everything

Purge-everything is operationally noisy and risks collateral damage. It is forbidden as a default step.

---

## Architecture States

### State A — Stabilize (Current)

- GitHub Pages for all static surfaces
- VPS Docker for runtime only
- GitHub Actions as CI/CD spine
- Cloudflare as DNS-only

### State B — Target Steady State

- Cloudflare Pages for hub and docs
- VPS Docker for runtime
- GitHub Actions as CI/CD spine
- Cloudflare Cache Rules by content class
- Selective purge by content type

**Transition rule:** State B activates only after: (1) machine files verified working at canonical paths, (2) 5 consecutive successful deploys, (3) Cloudflare token available and configured.

---

## Error Classification

| Error | Response |
|-------|----------|
| Deploy fails health check | Rollback immediately |
| Machine file returns wrong Content-Type | Rollback deploy |
| Hub/docs content swapped | Rollback + bug ticket |
| Runtime unreachable | Rollback runtime deploy only |
| Cache poisoning | Purge specific affected files |

---

## Tool Access Summary

| Tool | Purpose | Access |
|------|---------|--------|
| `gh` CLI | GitHub Actions, repo, secrets | Authenticated via `gh auth` |
| `wrangler` v4 | Cloudflare Pages, DNS, Cache Rules | Needs `CLOUDFLARE_API_TOKEN` env var |
| `docker` / `docker compose` | VPS runtime management | SSH to VPS via `deploy-vps.yml` |
| `rsync` | File transfer to VPS | Via SSH in deploy-vps.yml |
| Python `urllib` | Direct Cloudflare REST API | Needs CF token |
| GitHub Actions | Automated CI/CD | Push-to-main trigger |

**Current blockers:** `CLOUDFLARE_API_TOKEN` not available in runtime. `deploy-vps.yml` secrets partially encrypted.

---

## When This Skill Does NOT Apply

- Local development (`docker compose up`) — use `vps-docker` skill
- Skill authoring — use `skill-creator` skill
- Cloudflare token creation — requires human at dashboard
- Repo code changes — normal git push, no deploy skill needed

---

## References

- **Deploy matrix:** `references/deploy-matrix.md` — domain → platform → CI trigger mapping
- **File inventory:** `references/file-inventory.md` — machine files, paths, content types
- **CI/CD patterns:** `references/cicd-patterns.md` — workflow patterns (TO BE WRITTEN after State A proven)
- **Cloudflare commands:** `references/cloudflare-commands.md` — exact CLI syntax (TO BE WRITTEN after CF token available)
