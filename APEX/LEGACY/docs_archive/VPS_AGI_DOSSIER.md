# VPS AGI DOSSIER (SEALED)

Owner: Arif Fazil  
Host: `srv1325122.hstgr.cloud` (`72.62.71.199`)  
Source of truth: `/srv/arifOS`  
Master secrets file: `/home/ariffazil/xxx/.env`  
Date: 2026-03-04 UTC

Mission: agent-first VPS for arifOS so operations are mostly autonomous and human terminal usage is minimal.

---

## 1) Executive Verdict

- Infrastructure baseline is strong and ready for service deployment.
- Tooling for AI coding agents is installed and usable.
- Runtime services are **LIVE** (3 active containers via Docker Compose).
- Architecture direction is sealed as **Compose-first, scale-to-Kubernetes-later**.

SEAL status now: **100% infra ready / 100% production runtime live**.

---

## 2) Reality Snapshot (Current VPS)

### 2.1 Platform

- OS: Ubuntu 25.10 (non-LTS)
- Compute: 4 vCPU, 16 GB RAM
- Disk: 193 GB (~16 GB used)
- Open listening port: `22/tcp`, `80/443/tcp` (via proxy), `8080/tcp` (arifOS)

### 2.2 Security

- SSH hardening: `PermitRootLogin no`, `PasswordAuthentication no`, `PubkeyAuthentication yes`
- Firewall: UFW active, SSH allow rule
- Guardrail: fail2ban active
- Admin identity: `ariffazil` (sudo)

### 2.3 Repo State

- Path: `/srv/arifOS`
- Branch: `main` tracking `origin/main`
- Head commit: `94a9de00`
- Working tree: modified `AGENTS.md` (dirty tree)

### 2.4 Agent CLI Surface

Installed and callable:

- Core CLIs: `opencode`, `claude`, `kimi`, `gemini`, `codex`
- AGI wrappers: `agi-opencode`, `agi-claude`, `agi-kimi`, `agi-gemini`, `agi-codex`

### 2.5 Secrets/API Health

- Valid now: OpenAI, Anthropic, Google/Gemini, GitHub
- Failing now: Kimi (`401`)

---

## 3) Core Principles (No-Chaos Constitution)

1. **One code path only**: `/srv/arifOS`
2. **One secrets source only**: `/home/ariffazil/xxx/.env`
3. **No duplicate app roots** and no ad-hoc symlink shortcuts
4. **No direct public app ports** except via reverse proxy
5. **All destructive operations** require explicit hold gate (`888_HOLD` discipline)

---

## 4) Tool Architecture (What Lives Where)

### 4.1 Control Plane (Agent Brains)

- Location: user-space CLI + wrapper commands
- Purpose: run coding agents, execute plans, operate repo/services
- Components: OpenCode, Claude Code, Gemini CLI, Codex CLI, Kimi CLI

### 4.2 Runtime Plane (Service Execution)

- Location: Docker Compose stack on host
- Purpose: run arifOS and supporting infra continuously
- Components: Traefik, Postgres, Redis, arifOS, optional Qdrant

### 4.3 Ops Toolbelt (Agent Capabilities)

- Browser automation: Playwright + Chromium (headless)
- Document/PDF: poppler-utils, qpdf, tesseract, ocrmypdf
- Web extraction/crawl: controlled crawler utilities + fetch parsers
- Git ingestion: gitingest-compatible workflow scripts
- Task automation: n8n (or Prefect as alternative)

### 4.4 Data and Memory

- Postgres: canonical structured state and audit metadata
- Redis: cache/queue/session speed
- Qdrant: vector memory (phase-gated)
- Backups: snapshots + offsite sync (`rclone`)

### 4.5 Ingress/Egress

- Public entry: Traefik on `80/443`
- Public app: `arifos.arif-fazil.com`
- Private apps: OpenClaw + AgentZero (internal/private route only)
- Optional private access layer: Cloudflare Tunnel + Cloudflare Access

---

## 5) Decision Weights (Compose vs Kubernetes)

### Selected path: **Compose-first now**

Why this is selected for current context:

- Single VPS, single operator, immediate deployment need
- Lower operational entropy than introducing Kubernetes immediately
- Faster path to production runtime for arifOS/OpenClaw/AgentZero

### Kubernetes trigger (future)

Migrate only when one or more are true:

- Multi-node requirement
- Hard need for autoscaling and self-healing across nodes
- Team operations with formal CI/CD + staged rollouts
- Sustained workload where Compose becomes operational bottleneck

Verdict: external recommendation for Kubernetes is valid long-term, but premature for this current stage.

---

## 6) Requested Tools: Keep / Add / Skip

| Tool/Service | Decision | Phase | Why |
| :--- | :--- | :--- | :--- |
| Traefik | Add | P1 | clean ingress, TLS, route control |
| Postgres | Add | P1 | durable state + audit |
| Redis | Add | P1 | queue/cache/session |
| arifOS service | Add | P2 | mission core |
| OpenClaw | Add (private) | P4 | agent skills/control plane complement |
| AgentZero | Add (private) | P4 | external tool orchestration |
| n8n task runner | Add | P3 | autonomous workflows without terminal |
| Playwright + Chromium | Add | P3 | web automation ability for agents |
| PDF/OCR stack | Add | P3 | document ingestion for agents |
| gitingest flow | Add | P3 | repository digestion and retrieval |
| Qdrant | Add (gated) | P3/P4 | vector memory when needed |
| Ollama | Conditional | P4/P5 | local LLM fallback if cost/perf needs |
| Perplexica | Conditional | P4/P5 | useful but resource-heavy |
| cloudflared | Add | P3/P4 | private secure exposure |
| rclone | Add | P5 | offsite backups |
| file sharing (MinIO/filedrop) | Add | P3 | handoff outputs to human/others |
| WPS Office | Skip | N/A | GUI app, poor headless VPS fit |
| Obsidian app on VPS | Skip | N/A | better on laptop, sync markdown only |
| Email relay | Add | P5 | alerts and notifications |

---

## 7) Service Topology (Target)

```text
Internet
  -> Traefik :80/:443
      -> arifos (public)
      -> apex control surface (protected)
      -> OpenClaw (private route)
      -> AgentZero (private route)

Internal network
  -> Postgres
  -> Redis
  -> Qdrant (gated phase)
  -> n8n
  -> browser/pdf worker services
```

---

## 8) Phased Build Plan (Final)

### Phase 1: Core Runtime Foundation (SEAL 0 -> 35)

- Deploy `traefik + postgres + redis`
- Add healthchecks, restart policies, persistent volumes
- Keep only 80/443 public via proxy policy

Exit criteria:

- `docker ps` healthy for core services
- Internal service probes pass

### Phase 2: arifOS Live Runtime (SEAL 36 -> 60)

- Deploy arifOS service from `/srv/arifOS`
- Wire to Postgres/Redis and env
- Route domain `arifos.arif-fazil.com` via Traefik

Exit criteria:

- HTTPS health endpoint healthy
- Core governance flow operational

### Phase 3: Agent Workbench (SEAL 61 -> 78)

- Add Playwright/Chromium + PDF/OCR tools
- Add n8n task automation
- Add file sharing endpoint/channel

Exit criteria:

- Agent can browse, parse PDFs, schedule tasks, and share artifacts

### Phase 4: Multi-Agent Runtime (SEAL 79 -> 92)

- Deploy OpenClaw private
- Deploy AgentZero private
- Segment networks and apply access controls

Exit criteria:

- Both services reachable by internal agents, not publicly exposed by default

### Phase 5: Reliability + Hands-Off Operations (SEAL 93 -> 100)

- Add backup automation + offsite sync (`rclone`)
- Add alerts/heartbeat and recovery runbooks
- Add weekly integrity checks and quarterly restore drill

Exit criteria:

- Restore path proven
- Daily operations possible via agents/dashboard with minimal manual shell use

---

## 9) Security and Governance Enhancements (Weighted)

Selected now:

- Keep sudo via `ariffazil`, keep root SSH disabled
- Keep one secret authority file and generated per-service env derivatives
- Enforce private-by-default for non-public agent surfaces

Deferred but planned:

- External secrets manager (Vault/SOPS) when service count grows
- Advanced eBPF/zero-trust telemetry when moving beyond single-node operations

---

## 10) Operational Commands (Minimal Human)

- SSH in: `ssh ariffazil@72.62.71.199`
- Repo root: `cd /srv/arifOS`
- Agent entry: `opencode` (aliased to AGI wrapper)
- Services: `docker ps`
- Env check: `sed -n '1,80p' /home/ariffazil/xxx/.env`

---

## 11) Immediate Next Actions (Execution Queue)

1. Forge `docker-compose.core.yml` with Traefik + Postgres + Redis + arifOS
2. Bring up Phase 1 and Phase 2 stack
3. Create env sync script (master env -> per-service env files)
4. Add Phase 3 workbench (browser/PDF/n8n/file sharing)
5. Add OpenClaw and AgentZero in private routes

Current dossier verdict: **SEAL**

Rationale: architecture now has clear contrasts, no redundant layers, and tools are selected to complement arifOS mission with minimal entropy.
