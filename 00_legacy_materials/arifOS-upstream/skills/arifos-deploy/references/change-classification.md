# Change Classification — Every Request Sorted

Every request to this skill must be classified before any action is taken. This is the 111_CHECK operationalization.

---

## Change Types

| Class | What it covers | Required Gates |
|-------|---------------|----------------|
| COPY | Text, content, prose, copy changes | 000, 111, 333, 777, 999 |
| STRUCTURE | New pages, new routes, new assets | 000, 111, 333, 555, 777, 888, 999 |
| ROUTING | DNS, CNAME, redirects, path changes | 000, 111, 333, 555, 777, **888**, 999 |
| MACHINE_FILE | llms.txt, agent.json, robots.txt, sitemap | 000, 111, 333, 555, 777, 999 |
| CACHE | Purge, invalidation | 000, 111, 333, 777, 999 |
| TOKEN_SECRET | API key rotation, secret update | 000, 111, 333, 555, 777, **888**, 999 |
| RUNTIME | Server restart, config change, deploy | 000, 111, 333, 555, 777, **888**, 999 |
| DESTRUCTIVE | Deletion, cleanup, purge everything | 000, 111, 333, 555, 777, **888**, 999 |
| CUTOVER | State A→B, domain migration | 000, 111, 333, 555, 777, **888**, 999 |
| SECURITY | Token exposure, breach response | 000, 111, 333, 555, 777, **888**, 999 |
| QUERY | Read-only, status check | 000, 111, 333, 999 |

---

## COPY — Content Update

**Definition:** Changes to text, prose, descriptions, without structural changes.

**Examples:**
- Rewrite homepage hero text
- Update project description in llms.txt
- Change footer links
- Update metric values in README

**Required gates:** 000 → 111 → 333 → 777 → 999

**Process:**
1. Confirm canonical source for this content
2. Verify new content does not contradict canonical source
3. Confirm surface role not violated (hub copy on hub, docs copy on docs)
4. Deploy via CI/CD
5. Verify changed file live

**Rollback:** Revert to previous content, redeploy.

---

## STRUCTURE — New Page or Route

**Definition:** Adding new HTML pages, new asset paths, new directories, new subdomains.

**Examples:**
- Add /guides/quickstart.html
- Add /projects/GEOX.html
- Add new CSS file
- Create new subdomain

**Required gates:** 000 → 111 → 333 → 555 → 777 → 888 → 999

**Process:**
1. Confirm surface role (hub gets summary pages, docs gets full technical pages)
2. Confirm no duplicate of existing content
3. Assess sitemap impact — must add new page to sitemap.xml
4. Confirm canonical path is used (no non-standard paths)
5. **888_HOLD** — human confirm new page content and purpose
6. Deploy via CI/CD with new page in artifact
7. Verify: page loads, sitemap updated, machine files unchanged

**888_HOLD trigger:** If new page duplicates full docs content → refused.

**Rollback:** Remove page from source, redeploy, remove from sitemap.

---

## ROUTING — DNS, CNAME, Redirects

**Definition:** Changes to how traffic is routed — DNS records, CNAME records, URL redirects, path-based routing.

**Examples:**
- Change CNAME for arifOS-fazil.com
- Add DNS record for new subdomain
- Configure redirect from apex.arifOS-fazil.com
- Change routing rules

**Required gates:** 000 → 111 → 333 → 555 → 777 → **888** → 999

**Process:**
1. Document current DNS configuration
2. State new DNS configuration
3. Assess blast radius — what breaks if DNS is wrong?
4. TTL check — how long until old record expires?
5. **888_HOLD — MANDATORY** — human must approve DNS change
6. Apply change
7. Verify: new record resolves, old record expired or pointed to fallback
8. Document rollback (revert to old DNS values)

**888_HOLD trigger:** All DNS changes are mandatory hold. No exceptions.

**Rollback:** Revert DNS to previous values. May require waiting for TTL.

---

## MACHINE_FILE — llms.txt, agent.json, robots.txt, sitemap.xml

**Definition:** Changes to machine-readable discovery files at canonical paths.

**Examples:**
- Update llms.txt with new project info
- Update agent.json MCP endpoint
- Add entry to robots.txt
- Update sitemap.xml

**Required gates:** 000 → 111 → 333 → 555 → 777 → 999

**Process:**
1. Confirm file is at canonical path (/llms.txt, not /docs/llms.txt)
2. Confirm source — which repo file generates this?
3. Generate new content
4. Validate: llms.txt is plain text, agent.json parses as JSON
5. Confirm Content-Type will be correct (text/plain for txt, application/json for json)
6. Deploy via CI/CD
7. Verify: curl the canonical path, confirm Content-Type

**Refusal triggers:**
- Request to serve machine file at non-canonical path → REFUSE
- llms.txt containing HTML → REFUSE until corrected

**Rollback:** Redeploy previous version of file.

---

## CACHE — Purge, Invalidation

**Definition:** Cache purge requests for any surface.

**Examples:**
- Purge llms.txt cache after update
- Purge specific HTML page cache
- Purge all Cloudflare cache for a zone

**Required gates:** 000 → 111 → 333 → 777 → 999

**Process:**
1. List exact files to be purged
2. Confirm each file's source content has changed
3. **If blanket purge requested:** REFUSE — doctrine forbids
4. Purge targeted files only
5. Document which files purged and why

**Refusal triggers:**
- "Purge everything" → REFUSE VOID
- Purge without confirmed source content change → REFUSE

**Rollback:** Re-publish the purged files (cache repopulates automatically).

---

## TOKEN_SECRET — API Key, Token, Secret Rotation

**Definition:** Changes to any stored secret, API key, or token.

**Examples:**
- Rotate Cloudflare API token
- Update GitHub token
- Change VPS SSH key
- Update any secret in GitHub Secrets

**Required gates:** 000 → 111 → 333 → 555 → 777 → **888** → 999

**Process:**
1. Identify all systems using this secret
2. State old secret (do not reveal value) and new secret
3. Assess blast radius — which CI/CD workflows will break?
4. **888_HOLD — MANDATORY** — human must confirm rotation
5. Update secret in all affected systems simultaneously
6. Verify all systems reconnect with new secret
7. Confirm old secret is fully revoked

**888_HOLD trigger:** All secret rotations are mandatory hold.

**Rollback:** Revoke new secret, restore old secret, verify all systems reconnect.

---

## RUNTIME — Server, Config, Deploy

**Definition:** Changes to the running VPS runtime — restarts, config updates, code deploys.

**Examples:**
- Restart arifOS MCP container
- Update docker-compose.yml
- Deploy new arifOS version to VPS
- Change runtime environment variables

**Required gates:** 000 → 111 → 333 → 555 → 777 → **888** → 999

**Process:**
1. Confirm target: which container/service?
2. Check current health: `curl /health`
3. Assess blast radius: active tool calls will fail during restart
4. **888_HOLD — MANDATORY** — human confirm maintenance window for production
5. Apply change
6. Wait for health check recovery (30s timeout)
7. Verify: /health returns 200, containers healthy

**888_HOLD trigger:** All production runtime changes require human confirmation.

**Rollback:** Redeploy previous container image, or revert docker-compose.yml and restart.

---

## DESTRUCTIVE — Deletion, Cleanup

**Definition:** Any action that permanently removes data, files, or infrastructure.

**Examples:**
- Delete subdomain DNS record
- Remove old deployment artifact
- Delete deprecated pages from source
- Clear VPS logs

**Required gates:** 000 → 111 → 333 → 555 → 777 → **888** → 999

**Process:**
1. List exact resources to be deleted
2. State what exists today vs. what will exist after deletion
3. **888_HOLD — MANDATORY** — human must confirm deletion
4. Delete
5. Verify deletion — resource returns 404 or no longer in listing

**888_HOLD trigger:** All destructive actions are mandatory hold.

**Rollback:** Depends on resource. DNS: recreate record. Files: restore from git. Cannot rollback permanent data deletion.

---

## CUTOVER — State A to B Migration

**Definition:** Migrating from one hosting platform to another (e.g., GitHub Pages → Cloudflare Pages).

**Examples:**
- Migrate arifOS-fazil.com from GitHub Pages to Cloudflare Pages
- Move docs from GitHub Pages to Cloudflare Pages
- Change CDN provider

**Required gates:** 000 → 111 → 333 → 555 → 777 → **888** → 999

**Process:**
1. Confirm all State B preconditions met (per SKILL.md)
2. Document old platform and new platform
3. Assess cutover window: DNS TTL propagation = entropy spike
4. **888_HOLD — MANDATORY** — domain cutover is irreversible until TTL expires
5. Deploy to new platform first (verify works)
6. Update DNS
7. Monitor — old and new both serve during TTL window
8. After TTL: verify all traffic lands on new platform
9. Decommission old platform

**Rollback:** Revert DNS to old platform. TTL must expire first — rollback not instant.

---

## SECURITY — Breach Response, Token Exposure

**Definition:** Response to a security incident — exposed token, unauthorized access, data breach.

**Examples:**
- Token accidentally committed to git
- Suspected unauthorized access
- Unexpected changes in analytics

**Required gates:** 000 → 111 → 333 → 555 → 777 → **888** → 999

**Process:**
1. Identify affected secrets/resources
2. Assess blast radius — what is exposed, for how long?
3. **888_HOLD — MANDATORY** — human must be notified immediately
4. Rotate affected secrets before proceeding
5. Review access logs
6. Document incident

**888_HOLD trigger:** All security incidents are mandatory hold and immediate human escalation.
