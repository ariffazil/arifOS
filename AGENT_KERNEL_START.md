# AGENT_KERNEL_START — arifOS Estate Entry Ritual
> **DITEMPA BUKAN DIBERI** — You are entering the constitutional kernel.
> **Authority:** This file is the first operational context for every agent.
> **Version:** 2026-05-25

---

## What Is This Estate?

The arifOS estate is a federation of sovereign organs governed by a constitutional kernel.

```
arifOS (Ω Law)          ← Constitutional kernel. F1-F13. The "why" and "what not to do."
A-FORGE (Ψ Forge)      ← Execution shell. Workflows. The "how" and "what to build."
arif-sites (Δ Surface) ← Public federation surface.
GEOX (Earth)            ← Earth intelligence organ.
WEALTH (Capital)        ← Capital intelligence organ.
WELL (Vitality)         ← Human readiness organ. Not deployed.
APEX (Verdict)          ← Constitutional judgment engine. Archived/read-only.
```

**arifOS is not a general-purpose AI framework.** It is a governed kernel. Every action passes through F1-F13 floors before execution.

---

## Authority Hierarchy

When sources disagree, higher authority wins. Do not guess.

| Priority | Source | What it governs |
|----------|--------|----------------|
| 1 | arifOS F1-F13 constitutional law | Governance, irreversibility, human veto |
| 2 | Repo `INVARIANTS.md` | Live ports, public URLs, forbidden stale assumptions |
| 3 | Verified live service state | Health checks, systemd status |
| 4 | MCP configuration | Tool endpoints, transport |
| 5 | `README.md` | Human orientation |
| 6 | Architecture docs | System shape |
| 7 | Changelogs / archived plans | Historical receipts |

---

## Live Routing Invariants (VERIFIED 2026-05-25)

| Service | Public host | Local target | Status |
|---------|------------|-------------|--------|
| **arifOS** | `arifos.arif-fazil.com` | `127.0.0.1:8088` | ✅ LIVE |
| **GEOX** | `geox.arif-fazil.com` | `127.0.0.1:18081` | ✅ LIVE |
| **WEALTH** | `wealth.arif-fazil.com` | `127.0.0.1:18082` | ✅ LIVE |
| **WELL** | `well.arif-fazil.com` | disabled | ⛔ 404 intentional |

---

## Agent Boot Sequence (MUST FOLLOW IN ORDER)

```
000. Read this file (AGENT_KERNEL_START.md).
001. Read target repo README.md.
002. Read target repo AGENTS.md if present.
003. Read target repo INVARIANTS.md if present.
004. Check git status: git status --short
005. Check open PRs: gh pr list --repo ariffazil/<repo> --state open
006. Run invariant checker: ./scripts/check-estate-invariants.sh
007. Search for stale assumptions before editing anything:
     - grep -r "8080" --include="*.md" --include="*.py" --include="*.json"
     - grep -r "8081" --include="*.md" --include="*.py" --include="*.json"
     - grep -r "8082" --include="*.md" --include="*.py" --include="*.json"
008. Make the smallest governed change.
009. Run tests if available: make test, pytest, npm test, etc.
010. Produce agent receipt.
```

---

## Forbidden Stale Assumptions

These must never appear in any active config, doc, or code:

- ❌ arifOS public on `8080` — correct is `8088`
- ❌ GEOX public on `8081` — correct is `18081`
- ❌ WEALTH disabled — it is LIVE on `18082`
- ❌ WELL live — it is NOT DEPLOYED
- ❌ GEOX daemon on `8081` — it is on `18081`
- ❌ APEX not archived — it is read-only
- ❌ organ_governance absolute import inside WEALTH internal package
- ❌ WEALTH missing `internal/__init__.py`
- ❌ arifOS MCP config pointing to `localhost:8080`

---

## Do Not Auto-Fix

These actions require explicit human approval:

- ❌ Make a disabled tenant look live
- ❌ Create fake health endpoints
- ❌ Change service ports without updating Caddy, MCP, docs, and invariants together
- ❌ Bypass governance wrapper for speed
- ❌ Delete archived/read-only repos
- ❌ Force-push to main/master
- ❌ Collapse unrelated repos into one commit
- ❌ Delete branches without listing them first

---

## Quick Health Check Commands

```bash
# arifOS
curl https://arifos.arif-fazil.com/health

# GEOX
curl https://geox.arif-fazil.com/health

# WEALTH
curl https://wealth.arif-fazil.com/health

# Local process check
ss -ltnp | grep -E '8088|18081|18082'
```

---

## Repo Ownership

| Repo | Owns | Does NOT own |
|------|-------|-------------|
| `arifOS` | Constitutional kernel, F1-F13, MCP kernel | Execution, GEOX, WEALTH |
| `A-FORGE` | Agent workflows, build, deploy | Constitutional judgment |
| `arif-sites` | Public surface, federation manifests | Kernel logic |
| `GEOX` | Earth intelligence, geoscience | Finance, human health |
| `WEALTH` | Capital intelligence, financial computation | Geology, execution |
| `WELL` | Human readiness (reserved, not deployed) | Everything until deployed |
| `APEX` | Constitutional verdict (archived) | Everything |

---

## One Rule

**DITEMPA BUKAN DIBERI** — Intelligence is forged, not given.
Prove it. Verify it. Don't assume.
