# TOOLS.md — Role Mapping (Updated)

| Tool / Skill | Role | Notes |
|:---|:---|:---|
| **sequential-thinking** | Architect | Deep planning & decomposition |
| **brave_search** | Architect | External research (Workflow Design) |
| **firecrawl** | Architect | Structured scraping for specs |
| **filesystem** | All | Architect: specs; Engineer: ops; Auditor: read-only |
| **git** | Architect | Version specs; Engineer: code ops |
| **exec** | Engineer | Shell/CLI on `srv1325122` |
| **github** | Engineer | Issues/PRs (no auto-merge) |
| **healthcheck** | Engineer | Infra checks (Guardian) |
| **data-analyst** | Engineer | CSV/log analysis & viz |
| **himalaya** | Engineer | Email triage |
| **n8n** | Engineer | Workflow JSON generation/validation |
| **browser** | Engineer | Puppeteer/Playwright automations |
| **cron** | Engineer | Job scheduling |
| **arifOS-judge** | Auditor | Floors F1–F13 evaluation |
| **memory** | Auditor | Context retrieval |

---

## 🛡️ Exec Security & Elevated Mode (Phase 2 SEALED)

*Updated: 2026-02-08T06:30:00Z | Ω₀ = 0.04 | SEALED*

| Parameter | Value |
|:---|:---|
| **exec.security** | `full` — unrestricted shell execution |
| **elevated** | `ask` — human approval required for elevated ops |
| **elevated.enabled** | `true` |
| **allowFrom** | `telegram:267378578` (888 Judge only) |
| **safeBins count** | 70+ |

### SafeBins (Partial List)
`apt`, `npm`, `pip`, `docker`, `git`, `curl`, `wget`, `jq`, `gh`, `ffmpeg`, `ufw`, `systemctl`, `ss`, `cat`, `grep`, `sed`, `awk`, `tar`, `gzip`, `unzip`, `chmod`, `chown`, `mkdir`, `cp`, `mv`, `ln`, `find`, `head`, `tail`, `wc`, `sort`, `diff`, `tee`, `xargs`, `env`, `which`, `whoami`, `hostname`, `date`, `uptime`, `df`, `du`, `free`, `top`, `ps`, `kill`, `pgrep`, `lsof`, `ip`, `ping`, `dig`, `nslookup`, `openssl`, `ssh-keygen`, `base64`, `md5sum`, `sha256sum`, `python3`, `node`, `npx`, `brew`

### New Capability: Autonomous Package Installation
- Engineer role can install packages via `apt`, `npm`, `pip`, `brew` without manual SSH
- All installations logged to MEMORY.md decision log
- Reversibility: packages can be removed via respective package managers

---

## ⚡ Risk Classification (Unchanged)
... (Original TOOLS.md content)
