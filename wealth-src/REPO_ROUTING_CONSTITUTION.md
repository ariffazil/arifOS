# REPO_ROUTING_CONSTITUTION.md
> **DITEMPA BUKAN DIBERI** — Routing intelligence is earned, not assumed.
> **Amanah clause:** Never route faster than certainty. Refuse over misroute.
> **Version:** 2026.05.02-KANON | **Authority:** Human Architect (Arif)

---

## MISSION

Put every piece of work into the **correct repository** — on VPS and on GitHub.
Prefer refusal over misrouting. Never trade correctness for speed.

---

## AUTHORITATIVE REPO MAP

| Repo | Domain Charter | VPS Workspace | GitHub |
|------|---------------|---------------|--------|
| **AAA** | Agent workspace, governance, ADRs, orchestration canon | `/root/AAA/` | `github.com/ariffazil/AAA` |
| **WEALTH** | Capital intelligence, portfolio, finance, macro/micro economic tooling | `/root/WEALTH/` | `github.com/ariffazil/wealth` |
| **GEOX** | Earth domain, geo/terrain/maps, well logs, subsurface | `/root/GEOX/` | `github.com/ariffazil/geox` |
| **arifOS** | Constitutional kernel, F1–F13 floors, MCP runtime, 13-tool surface | `/root/arifOS/` | `github.com/ariffazil/arifOS` |
| **A-FORGE** | Planning twin, design, architecture, prefrontal build logic | `/root/A-FORGE/` | `github.com/ariffazil/A-FORGE` |
| **arif-sites** | Website/static/web-facing assets, public surface | `/root/arif-sites/` | `github.com/ariffazil/arif-sites` |
| **ariffazil** | Personal/profile/meta public root | `/root/ariffazil/` | `github.com/ariffazil/ariffazil` |

**OpenClaw workspace:** `/srv/openclaw/workspace/`
**Hermes workspace:** `/root/.hermes/workspace/`
**VPS repos:** `/root/{AAA,WEALTH,GEOX,arifOS,A-FORGE,arif-sites,ariffazil}/`

---

## CLASSIFICATION RULES

Before any write, commit, or push — determine destination:

1. **Read the file's domain.** Finance code → WEALTH. MCP/floors → arifOS. Earth/subsurface → GEOX. Agent governance/routing → AAA. Planning/design → A-FORGE. Web assets → arif-sites.
2. **Check existing location.** If the file already lives in a repo, it stays there.
3. **Cross-repo moves require 888_HOLD.** Never silently move code between repos.
4. **If confidence < 0.8, stop and ask.** Don't guess.

---

## PUSH GATE RULES

### Never
- ❌ `git push origin main` directly
- ❌ Push to any protected branch without a PR
- ❌ Cross-repo code movement without 888_HOLD

### Always
- ✅ `git checkout -b repo/feature-name`
- ✅ `git commit` with `REPO=<repo>` trailer in message body
- ✅ `git push origin repo/feature-name`
- ✅ Open PR

---

## LOW-CONFIDENCE PROTOCOL

```
STOP — do not route
Reason: [explain why classification failed]
Ask: "Arif — which repo does this belong to?"
```

---

## AUTONOMOUS CAPABILITIES (within rules)

The agent **may** without asking: read, branch, commit, open PRs, run tests.
The agent **must not** without 888_HOLD: push to main, move code between repos, delete history.

---

**Ditempa Bukan Diberi — Routing intelligence is forged, not given.**
