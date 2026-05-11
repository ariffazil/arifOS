# Constitutional Execution — Task-to-Stage Mapping

Every task type maps to a mandatory stage subset. Skipping a mandatory stage is a 888_HOLD event.

---

## Change Types and Required Stages

| Change Type | Mandatory Stages | Optional Stages |
|------------|-----------------|-----------------|
| Copy/content update | 000, 111, 333, 777, 999 | — |
| Structure (new page, new route) | 000, 111, 333, 555, 777, 888, 999 | — |
| Routing (DNS, CNAME, redirect) | 000, 111, 333, 555, 777, **888**, 999 | — |
| Machine file (llms.txt, agent.json) | 000, 111, 333, 555, 777, 999 | — |
| Cache purge | 000, 111, 333, 777, 999 | 555 |
| DNS change | 000, 111, 333, 555, 777, **888**, 999 | — |
| Token/secret change | 000, 111, 333, 555, 777, **888**, 999 | — |
| Runtime restart | 000, 111, 333, 555, 777, **888**, 999 | — |
| Production runtime destructive | 000, 111, 333, 555, 777, **888**, 999 | — |
| Domain cutover | 000, 111, 333, 555, 777, **888**, 999 | — |
| State A → B migration | 000, 111, 333, 555, 777, **888**, 999 | — |
| Query / read-only | 000, 111, 333, 999 | — |
| Skill authoring | 000, 111, 333, 777, 999 | — |

---

## Stage Requirements by Change Type

### Copy / Content Update

```
000_INIT   → Confirm: which surface? what file?
111_CHECK  → Hub or docs. Static file only.
333_REASON → Is source canonical? Has content changed?
777_ROUTE → If hub: validate HTML, validate machine files unchanged
999_SEAL  → Push, confirm live, verify Content-Type via curl
```

### Structure (New Page or Route)

```
000_INIT   → What page? Which surface?
111_CHECK  → Hub or docs. Not runtime. Not a third surface.
333_REASON → Does this duplicate existing content? Is path canonical?
555_HEART  → How will this affect sitemap? Will crawlers index it correctly?
777_ROUTE  → If machine file: check invariants first. If HTML: validate structure.
888_HOLD   → If duplicate of docs content on hub: STOP
999_SEAL   → Add to sitemap if hub page. Document rollback (remove page + redeploy).
```

### Machine File Publish

```
000_INIT   → Which file? Which surface?
111_CHECK  → Must be hub surface. Must be at root.
333_REASON → Source canonical? Generated from correct source files?
555_HEART  → What breaks if this file is wrong? AI agents will read it.
777_ROUTE  → Must serve at /llms.txt or /.well-known/agent.json — canonical path only
999_SEAL   → Verify Content-Type: text/plain for llms.txt, application/json for agent.json
```

### Cache Purge

```
000_INIT   → What files? Why?
111_CHECK  → Purge only files whose content changed — never blanket
333_REASON → Is targeted purge available? Or is blanket the only option?
777_ROUTE  → If blanket: REFUSE. If targeted: proceed.
999_SEAL   → Document exactly which files purged and why
```

### DNS Change

```
000_INIT   → Which record? Which domain?
111_CHECK  → DNS. Cloudflare or GitHub Pages CNAME.
333_REASON → What does this record currently point to?
555_HEART  → Is this production? What breaks if DNS is wrong?
777_ROUTE  → If Cloudflare Pages CNAME: check State A/B status
888_HOLD   → MANDATORY. DNS changes are irreversible. Human must confirm.
999_SEAL   → Document old value, new value, rollback steps (revert DNS to old value)
```

### Token / Secret Rotation

```
000_INIT   → Which secret? Where used?
111_CHECK  → GitHub Secrets, Cloudflare, or VPS
333_REASON → Current value is encrypted. Rotation must preserve access.
555_HEART  → If CF token: wrangler and CI/CD will break immediately
888_HOLD   → MANDATORY. Token rotation breaks active tooling.
999_SEAL   → Document which systems need new token after rotation
```

### Runtime Restart

```
000_INIT   → Which service? arifOS MCP server?
111_CHECK  → Runtime surface only
333_REASON → Why restart? Health check failing? Config change?
555_HEART  → Active tool calls will fail during restart
888_HOLD   → If production runtime: MANDATORY. Human must confirm maintenance window.
999_SEAL   → Health check after restart: curl /health → 200 within 30s
```

### State A → B Migration (Cloudflare Pages)

```
000_INIT   → Which surface(s)? Hub, docs, or both?
111_CHECK  → Static surface migration. Runtime stays on VPS.
333_REASON → Is Cloudflare token available? Have all State B preconditions been met?
555_HEART  → During cutover: brief window where old and new both serve. Entropy spike.
888_HOLD   → MANDATORY. Domain cutover is irreversible until DNS TTLs expire.
999_SEAL   → Document: old platform, new platform, DNS TTL, rollback window, verification steps
```

---

## Stage Checkpoints

Before any 999_SEAL, these checkpoints must all be green:

- [ ] Source files exist and are syntactically valid
- [ ] Machine files are at canonical paths
- [ ] Content-Type for machine files is correct
- [ ] Rollback path is documented and achievable in ≤2 minutes
- [ ] Health check endpoint is reachable (runtime changes only)
- [ ] No surface role violation
- [ ] No blanket purge
- [ ] No missing required secret
