# REPO_ROUTING_CONSTITUTION.md
> **DITEMPA BUKAN DIBERI** — Routing intelligence is earned, not assumed.
> **Amanah clause:** Never route faster than certainty. Refuse over misroute.
> **Version:** 2026.05.02-KANON | **Authority:** Human Architect (Arif) | **Enforcement:** VPS workspace isolation + GitHub branch protection

---

## MISSION

Put every piece of work into the **correct repository** — on VPS and on GitHub.
Prefer refusal over misrouting. Never trade correctness for speed.
Autonomy is permitted only under these rules. Without them, stop.

---

## AUTHORITATIVE REPO MAP

| Repo | Domain Charter | VPS Workspace | GitHub |
|------|---------------|---------------|--------|
| **AAA** | Agent workspace, governance ADRs, orchestration canon, routing policy | `/root/AAA/` | `github.com/ariffazil/AAA` |
| **WEALTH** | Capital intelligence, portfolio, finance, macro/micro economic tooling | `/root/WEALTH/` | `github.com/ariffazil/wealth` |
| **GEOX** | Earth domain, geo/terrain/maps, well logs, subsurface, planetary tooling | `/root/geox/` | `github.com/ariffazil/geox` |
| **arifOS** | Constitutional kernel, F1–F13 floors, 9-Organ Canon, MCP runtime, 13-tool surface | `/root/arifOS/` | `github.com/ariffazil/arifOS` |
| **A-FORGE** | Planning twin, design, architecture, prefrontal build logic, engine–cockpit bridge | `/root/A-FORGE/` | `github.com/ariffazil/A-FORGE` |
| **arif-sites** | Website/static/web-facing assets, public surface | `/root/arif-sites/` | `github.com/ariffazil/arif-sites` |
| **ariffazil** | Personal/profile/meta public root | `/root/repos/ariffazil/` | `github.com/ariffazil/ariffazil` |

**OpenClaw workspace:** `/srv/openclaw/workspace/` — AGI agent operative home.
**Hermes workspace:** `/root/.hermes/workspace/` — ASI agent operative home.

---

## CLASSIFICATION RULES

Before any write, commit, or push — determine destination:

1. **Read the file's domain.** Finance/portfolio code → WEALTH. MCP server/floors → arifOS. Earth/subsurface → GEOX. Agent governance/routing policy → AAA. Planning/design/architecture → A-FORGE. Web assets → arif-sites.
2. **Check existing repo content.** If the file you're editing already lives in a repo, it stays there.
3. **Cross-repo moves require explicit human confirmation (888_HOLD).** Never silently move code between repos.
4. **If confidence < 0.8, stop and ask.** Don't guess. Amanah > convenience.

**Confidence check protocol:**
- `high` (≥0.9): proceed with branch → PR
- `medium` (0.7–0.89): open draft PR, flag for review
- `low` (<0.7): refuse, explain, ask Arif

---

## WORKSPACE ISOLATION

| Context | May operate in | Notes |
|---------|----------------|-------|
| OpenClaw (AGI) | `/srv/openclaw/workspace/` + repo working dirs | Full read/write within repos |
| Hermes (ASI) | `/root/.hermes/workspace/` + repos via explicit path | Reads constitution from workspace |
| Cron (isolated) | Repo working dirs only, no push without gate | Tool access limited by cron session config |
| Sub-agent | Inherits parent's repo map | Must receive this constitution as context |

**VPS git operations always happen in the repo's working directory.**

---

## PUSH GATE RULES

### Never
- ❌ `git push origin main` directly
- ❌ Push to any protected branch without a PR
- ❌ Cross-repo code movement without 888_HOLD
- ❌ Silent commit and push (no PR) for anything beyond hotfix

### Always
- ✅ `git checkout -b repo/feature-name` — branch naming: `{repo}/{short-description}`
- ✅ `git commit` with descriptive message referencing domain
- ✅ `git push origin repo/feature-name`
- ✅ Open PR with description: what, why, which repo target
- ✅ Only merge after human review or CI pass

**GitHub branch protection is the last line of defense.** Even if classification is wrong, protected branches block silent main damage.

---

## AUTONOMOUS CAPABILITIES (within rules)

When this constitution is active, the agent **may** without asking:
- Read and analyze files in any repo
- Create branches in any repo
- Commit with descriptive messages
- Open PRs to any target branch
- Run tests, lint, build verification
- Clone/fetch repos for inspection

The agent **must not** without 888_HOLD human confirmation:
- Push directly to main/master
- Move code between repos
- Delete files or history
- Modify branch protection rules
- Change this constitution

---

## LOW-CONFIDENCE PROTOCOL

When classification confidence is below threshold:

```
STOP — do not route
Reason: [explain why classification failed]
Alternatives considered:
  1. [option A with confidence estimate]
  2. [option B with confidence estimate]
Ask: "Arif — which repo does this belong to?"
```

Never fill ambiguity with convenience. "Close enough" is a violation of F08 GENIUS.

---

## VPS → GitHub SYNC RULES

| Action | Rule |
|--------|------|
| New feature work | Branch in VPS repo → PR to GitHub |
| Hotfix | Branch → fast-track PR → merge |
| Docs only | Branch → PR → merge |
| Config changes | Branch → PR → require CI pass |
| Cross-repo coordination | 888_HOLD before touching second repo |

**For GitHub auth:** Use SSH keys registered to Arif's GitHub account. Never use tokens that allow silent main push.

---

## ROUTING EXAMPLES

| Work item | Target repo | Branch pattern | Rationale |
|-----------|-------------|-----------------|-----------|
| New MCP tool for wealth | `/root/arifOS/` + PR to `arifOS` for tool registry update | `arifOS/wealth-mcp-tool` | Tool lives in arifOS runtime, wealth is the domain |
| Finance calculation library | `/root/WEALTH/` | `wealth/fin-calc-lib` | Domain charter = finance |
| GEOX well correlation panel | `/root/geox/` | `geox/well-correlation-v2` | Earth domain |
| arifOS constitutional floor fix | `/root/arifOS/` | `arifos/floor-F07-fix` | Core kernel |
| A-FORGE planning twin update | `/root/A-FORGE/` | `aforge/planning-twin-v3` | Design/architecture |
| Website asset update | `/root/arif-sites/` | `arif-sites/[feature]` | Web assets |
| AAA governance ADR | `/root/AAA/` | `aaa/adr-[number]-[topic]` | Governance |
| Mixed: arifOS + WEALTH | STOP → 888_HOLD | Requires human coordination | Cross-repo |

---

## AMANAH CONTRACT

By operating under this constitution, the agent agrees to:
1. **Classify before touching** — know the target repo before touching a file
2. **Branch before push** — no direct main pushes ever
3. **Evidence before claim** — when asked "which repo?", show reasoning
4. **Refuse ambiguity** — stop rather than misroute
5. **Escalate cross-repo** — any work touching ≥2 repos requires Arif's confirmation

**Ditempa Bukan Diberi — Routing intelligence is forged, not given.**
