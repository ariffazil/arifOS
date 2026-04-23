# 888_HOLD Matrix — Actions Requiring Human Confirmation

Every action in this matrix requires explicit human approval before proceeding. No agent may execute these without human decision.

**Format:** `ACTION → WHY_HOLD → REQUIRED_INPUT`

---

## DNS Changes — MANDATORY HOLD

| Action | Why Hold | Required Input |
|--------|---------|----------------|
| Create DNS record | Irreversible until TTL expires | Human confirms record value and type |
| Delete DNS record | Permanent loss of routing | Human confirms record name and confirms deletion |
| Change CNAME target | Traffic rerouted to new target | Human confirms new target and timeline |
| Change A record IP | All traffic pointed to new IP | Human confirms new IP |
| Add subdomain DNS | Creates new routing | Human confirms subdomain and target |
| Remove subdomain DNS | Breaks new routing permanently | Human confirms subdomain |
| Change DNS provider | Complex migration | Human confirms new provider and migration plan |

---

## Token / Secret Rotation — MANDATORY HOLD

| Action | Why Hold | Required Input |
|--------|---------|----------------|
| Rotate Cloudflare API token | All Cloudflare access breaks during rotation | Human confirms rotation window |
| Rotate GitHub token | CI/CD workflows fail | Human confirms new token value |
| Rotate VPS SSH key | VPS access breaks | Human confirms new key deployed to VPS |
| Delete any secret | Immediate access loss to that system | Human confirms system impact |
| Update secret value | Dependent systems may break | Human confirms all dependent systems updated |

---

## Production Runtime Changes — MANDATORY HOLD

| Action | Why Hold | Required Input |
|--------|---------|----------------|
| Restart arifOS MCP container | Active tool calls interrupted | Human confirms maintenance window |
| Stop arifOS MCP container | Service downtime | Human confirms downtime acceptable |
| Update arifOS docker image | Behavior may change | Human confirms new image version |
| Modify docker-compose.yml | Service configuration changes | Human confirms change reviewed |
| Change runtime environment variables | Service behavior changes | Human confirms new values |
| Restart any production container | Service interruption | Human confirms maintenance window |
| Delete container | Permanent service removal | Human confirms service no longer needed |

---

## Domain Cutover — MANDATORY HOLD

| Action | Why Hold | Required Input |
|--------|---------|----------------|
| Migrate arifOS-fazil.com to new platform | Old and new both serve during TTL window | Human confirms cutover plan |
| Migrate arifos.arifOS-fazil.com to new platform | Docs temporarily unavailable | Human confirms cutover plan |
| Point new domain to existing platform | Creates new surface | Human confirms new domain and purpose |
| Remove domain pointing to platform | Domain no longer serves content | Human confirms domain retired |
| Switch from GitHub Pages to Cloudflare Pages | CDN and caching behavior changes | Human confirms migration plan and rollback |

---

## Destructive Actions — MANDATORY HOLD

| Action | Why Hold | Required Input |
|--------|---------|----------------|
| Delete deployment artifact | Permanent loss of build artifact | Human confirms artifact name and date |
| Delete VPS log files | Audit trail reduced | Human confirms log retention period |
| Delete subdomain directory from source | Content permanently removed | Human confirms subdomain and all content |
| Purge VPS data directory | Data permanently deleted | Human confirms data no longer needed |
| Remove pages from source | Content permanently removed | Human confirms page names |
| Delete database | All data permanently lost | Human confirms database name and all data |

---

## Surface Role Violation Requests — MANDATORY HOLD (will likely REFUSE)

| Requested Action | Why Hold | Required Input |
|-----------------|---------|----------------|
| Move full docs content to hub | Violates three-surface rule | Human confirms content duplication is intentional |
| Move hub summaries to docs | Violates content ownership matrix | Human confirms |
| Serve machine files from non-canonical path | Violates machine discovery invariants | Human confirms new path is intentional |
| Swap runtime and static surface | Constitutional violation | REFUSE — no human input can authorize this |

---

## Machine File Non-Canonical Path Requests — REFUSE

| Requested Action | Response | Required Input |
|-----------------|----------|----------------|
| Serve llms.txt at /docs/llms.txt | REFUSE VOID | Path violates machine discovery invariants |
| Serve agent.json at /mcp/agent.json | REFUSE VOID | Path violates machine discovery invariants |
| Rename llms.txt to anything else | REFUSE VOID | Canonical path is constitutional |
| Add /llms.txt as SPA redirect | REFUSE VOID | Machine files never redirect |

---

## Blanket Purge Requests — REFUSE

| Requested Action | Response | Required Input |
|-----------------|----------|----------------|
| Purge everything | REFUSE VOID | Doctrine forbids blanket purge |
| Purge entire zone | REFUSE VOID | Targeted purge only |
| Purge all Cloudflare cache | REFUSE VOID | Collateral damage too high |
| Hard refresh all pages | REFUSE VOID | Must target specific changed files |

---

## Structural Changes — MANDATORY HOLD

| Action | Why Hold | Required Input |
|--------|---------|----------------|
| Add new static page | Changes sitemap, changes navigation | Human confirms page content |
| Add new subdomain | New surface created | Human confirms subdomain and platform |
| Change hub layout | User-facing change | Human confirms new layout |
| Add new CSS class to hub | Visual change | Human confirms design decision |
| Add new external link to hub | Hub leaks authority | Human confirms link is intentional |

---

## 888_HOLD Response Format

When hitting any mandatory hold, respond with:

```
888_HOLD — [Action category]
Action requested: [Exact action]
Why this requires human decision: [Specific reason]
What will break if this goes wrong: [Specific blast radius]
Required input from human: [Specific question or confirmation]
```

Then wait. Do not proceed until human responds.
