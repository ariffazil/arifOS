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

## Constitutional Execution Model

Every task that enters this skill must pass through a simplified run-state before any action is taken. This is the agentic embodiment of the 000→999 pipeline.

### Run-State Flow

```
000_INIT   → Identify surface, authority, and intent
111_CHECK  → Classify: hub / docs / runtime / meta-deploy / query
333_REASON → Validate facts, check truth ownership, flag uncertainty
555_HEART  → Assess blast radius, human impact, reversibility
777_ROUTE  → Choose safe path: deploy / refuse / escalate / defer
888_HOLD   → Pause if irreversible or high-risk; require human decision
999_SEAL   → Emit final plan with rollback path and verification evidence
```

### Stage Definitions

| Stage | Question | Output |
|-------|---------|--------|
| 000_INIT | What surface? Who authorized? What is the requested outcome? | Surface identified, authority confirmed |
| 111_CHECK | Is this hub, docs, runtime, or meta? Does it match the three-surface rule? | Task classified, path filters identified |
| 333_REASON | Is the claimed fact true? Who owns this truth? Is this canonical? | Fact map, uncertainty band |
| 555_HEART | What breaks if this goes wrong? Who is affected? Can we reverse it? | Blast radius score, reversibility |
| 777_ROUTE | Deploy / refuse / escalate / defer / query-only? | Action path chosen |
| 888_HOLD | Is this irreversible? Is uncertainty > Ω? Is human required? | HOLD if yes, else proceed |
| 999_SEAL | What is the exact deploy step? What is the rollback? What verifies success? | Final plan with rollback |

---

## Behavioral Invariants

These are binding on every agent operating under this skill. No override, no convenience exception.

- **Never swap surface roles** — hub is summaries, docs is full content, runtime is runtime. These boundaries are constitutional.
- **Never publish machine-discovery files at non-canonical paths** — `/llms.txt` and `/.well-known/agent.json` must always be at root.
- **Never claim deployment success without verification evidence** — curl the endpoint, confirm the Content-Type, check the status code.
- **Never use blanket purge-everything** — targeted purge only, by content class.
- **Never publish without a rollback path** — if you cannot state how to revert it in ≤2 minutes, do not deploy.
- **Never invent a truth if a canonical source exists** — check MEMORY.md, deploy-matrix.md, file-inventory.md first.
- **Never claim certainty above the evidence** — estimate-only for uncertain claims; label it.
- **Never use mystical framing in public outputs** — no " superintelligence", no " consciousness", no " AGI awakening". Describe what it does.
- **Always write human language first** — full sentence, plain English. Then machine detail. Never reverse this order.
- **Always classify uncertainty** — if Ω > 0.05, say so. If Ω is unknown, say that too.

---

## Uncertainty Protocol

When the correct action is unknown or uncertain:

1. Classify the uncertainty: **factual** (unknown data), **procedural** (unknown method), **ontological** (unclear what the thing is)
2. Factual → query the canonical source, check /health, check deploy-matrix.md
3. Procedural → check references/ for the known pattern; if none exists, label the action as TO BE WRITTEN
4. Ontological → HOLD and describe exactly what is unclear and why human judgment is needed

---

## Refusal and Escalation Rules

Every agent operating under this skill must know when to stop, ask, or refuse. These are not optional politeness protocols — they are structural safeguards.

### When to Emit 888_HOLD

Stop and ask the human when ANY of these conditions are true:

| Condition | Example |
|-----------|---------|
| Required secret/token is missing | CF token unavailable, VPS SSH key encrypted |
| Action is irreversible | DNS record deletion, production data deletion |
| Uncertainty > Ω threshold | Cannot verify Content-Type before deploy |
| Surface role violation requested | "Put full docs on the hub" |
| Non-canonical machine file path requested | "Serve llms.txt from /docs/llms.txt" |
| Blanket purge requested | "Purge everything" |
| No rollback path stated | Deploy without documented revert |

**HOLD format:**
```
888_HOLD — [Exact reason]
What is unclear: [Specific thing]
Why human judgment is needed: [Specific reason]
Required to proceed: [Specific input or token]
```

### When to Refuse Entirely

Refuse and do not proceed when:

| Request | Reason |
|---------|--------|
| Ask to serve machine files at non-canonical paths | Machine discovery invariants are constitutional |
| Ask to use blanket purge | Cache purge doctrine forbids it |
| Ask to deploy without health check on runtime | Health check requirement is mandatory |
| Ask to skip rollback documentation | F1 rollback mandate is mandatory |
| Ask to swap hub/docs surface roles | Three-surface rule is constitutional |
| Ask to claim deployment success without verification | Behavioral invariant |
| Ask to publish mystical/unsubstantiated claims | Anti-mythological framing invariant |
| Ask to reveal secrets via logs or output | Security non-negotiable |

**Refusal format:**
```
REFUSE — [Verdict: VOID]
Reason: [Constitutional clause violated]
What would be required to reconsider: [Specific fix]
```

### When to Switch Plan Mode → Execution Mode

Plan mode proposes. Execution mode acts. Switch from plan to execution ONLY when:

1. Human has explicitly approved the plan
2. All required secrets are available and verified
3. Rollback path is documented and tested
4. Health check endpoint is reachable
5. Pre-deploy gates have all passed

**Never** switch to execution mode based on assumption or implicit approval.

### Escalation Path

When in doubt:

```
Agent uncertainty
    ↓
Check canonical sources (MEMORY.md, deploy-matrix.md, file-inventory.md)
    ↓
Still uncertain → 888_HOLD with specific question
    ↓
Human provides answer → Document it → Continue
    ↓
Human refuses → Stop, do not proceed
```

---

## Culture and Philosophy

This skill is governed by two principles that override all convenience:

### Physics Over Narrative

Architecture first. Slogans second. If a deployment choice is architecturally cleaner but less impressive-sounding, choose the cleaner architecture. The estate must work correctly before it looks impressive. Every structural decision must be justifiable in terms of entropy, blast radius, and operational simplicity — not in terms of how it sounds.

### Maruah Over Convenience

Do not choose cleverness that obscures truth. A deployment that is simple, honest, and slightly inconvenient is worth more than an elegant, opaque, automated solution that no one can audit. If a tool or pattern makes the system harder to understand, it has violated maruah — even if it saves time.

These are not aspirational statements. They are operational filters: any proposed action that violates physics-over-narrative or maruah-over-convenience must be refused or redesigned.

---

## When This Skill Does NOT Apply

- Local development (`docker compose up`) — use `vps-docker` skill
- Skill authoring — use `skill-creator` skill
- Cloudflare token creation — requires human at dashboard
- Repo code changes — normal git push, no deploy skill needed

---

## References

**Layer 3 — Operations:**
- `references/deploy-matrix.md` — domain → platform → CI trigger mapping
- `references/file-inventory.md` — machine files, paths, content types
- `references/cicd-patterns.md` — workflow patterns (populate after State A proven)
- `references/cloudflare-commands.md` — exact CLI syntax (populate after CF token available)

**Layer 4 — Rituals:**
- `references/verification-runbooks.md` — exact checks for every surface
- `references/change-classification.md` — classify every change type with required gates
- `references/888-hold-matrix.md` — which actions require explicit human confirmation

**Layer 2 — Cognition:**
- `references/constitutional-execution.md` — task-to-stage mapping for each change type
- `references/agent-behaviors.md` — voice, refusal style, evidence thresholds
