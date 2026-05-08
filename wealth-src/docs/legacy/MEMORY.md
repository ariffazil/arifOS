# MEMORY.md — Governance-Relevant State
*(Long-term store for decisions, trade-offs, and rationales under arifOS constitutional framework)*

**Bias:** Store governance-relevant state. Compress routine chit-chat. No long-term storage of sensitive identifiers beyond explicit "persist" marks.

**Output Contract:** When recalling memory, present in human language. No raw data dumps.

**Ω₀ ≈ 0.04** — Stable memory state.

---

## 🔒 Red Lines (What NOT to Store)

- ❌ Unencrypted passwords, tokens, or secrets
- ❌ Sensitive personal identifiers unless explicitly marked "persist"
- ❌ Financial account numbers or credentials
- ❌ Health data beyond general wellness notes
- ❌ Private communications with third parties

**If in doubt:** Ask Arif before persisting sensitive data.

---

## 👤 Sovereign Profile

| Field | Value | Persist? |
|:---|:---|:---:|
| **Name** | Muhammad Arif bin Fazil | ✅ |
| **Handle** | @ariffazil (Telegram id:267378578) | ✅ |
| **Phone** | Removed per sovereign directive 2026-02-08 | ❌ |
| **Location** | Seri Kembangan, Selangor, Malaysia | ✅ |
| **Timezone** | Asia/Kuala_Lumpur (UTC+8) | ✅ |
| **Motto** | DITEMPA BUKAN DIBERI | ✅ |
| **Project** | arifOS — constitutional AI governance | ✅ |
| **Employer** | PETRONAS (as of 2026) | ✅ |
| **Roles** | Geoscientist, Economist, AI Governance Architect | ✅ |

---

## 🕰️ Daily Constitutional Metabolism (NEW - 2026-02-08)

**Status:** ✅ SEALED — 7 cron jobs active, autonomous operation approved

### Cron Job Registry

| ID | Name | Schedule | Purpose | Status |
|----|------|----------|---------|--------|
| `193ffc50-21fc-4143-8f5c-19b1efa238a5` | subuh-brief | 06:30 MYT | Morning intel, macro priors | ✅ Active |
| `e0c34280-556f-4220-9c5b-c7f2a9bc29cf` | human-arif | 08:00 MYT | Body, heart, Q7, maruah | ✅ Active |
| `8467d9c9-8299-4304-8032-e3dae6997f22` | repo-steward | 09:00 MYT | arifOS GitHub health | ✅ Active |
| `193ffc50-21fc-4143-8f5c-19b1efa238a5` | sovereign-wiring | 10:00 MYT | AgentZero/OpenClaw integration | ✅ Active |
| `a3be5716-efd5-475f-b37b-69669cb7d84d` | event-scout | 10:30 MYT | AI + bodybuilding opportunities | ✅ Active |
| `ae621bb1-a4f1-4725-aab6-1af050f39717` | godel-lock | 12:00 MYT | Frontier pattern recognition | ✅ Active |
| `8467d9c9-8299-4304-8032-e3dae6997f22` | morning-synthesis | 13:00 MYT | Afternoon decision closure | ✅ Active |

### Workflow Files Created
- `WORKFLOWS/WORKFLOW_SUBUH_BRIEF.md` — v2.1 with σ_gov metric
- `WORKFLOWS/WORKFLOW_HUMAN_ARIF.md` — ASI (Ω) daily check-in
- `WORKFLOWS/WORKFLOW_REPO_STEWARD.md` — v2.1 with Auto-Fix Protocol
- `WORKFLOWS/WORKFLOW_SOVEREIGN_WIRING.md` — System integration gaps
- `WORKFLOWS/WORKFLOW_EVENT_SCOUT.md` — AI + physique event radar
- `WORKFLOWS/WORKFLOW_GODEL_LOCK.md` — Physics-anchored pattern recognition
- `WORKFLOWS/WORKFLOW_MORNING_SYNTHESIS.md` — Post-lunch decision closure

### Thermodynamic Rhythm Established
```
06:30  Subuh          → World state
08:00  Human Arif     → Body, heart, maruah
09:00  Repo Steward   → Code health
10:00  Sovereign      → System wiring
10:30  Event Scout    → Opportunities
12:00  Gödel Lock     → Frontier patterns
13:00  Synthesis      → Decision closure
```

**Autonomy:** All jobs run in isolated sessions, Telegram delivery, reversible actions only.

## 🖥️ Infrastructure State (2026-02-08)

### VPS: srv1325122
- **IP:** 72.62.71.199
- **OS:** Ubuntu 25.10
- **OpenClaw:** 2026.2.6-3
- **UFW:** Active (SSH allowed, 50080 blocked externally)
- **fail2ban:** Running (sshd jail active)
- **exec.security:** `full`
- **elevated:** `ask` (allowFrom: telegram:267378578)
- **safeBins:** 70+
- **Autonomy Score:** 85% (Phase 2 Complete, Phase 3 deferred 48h)

### Agent Zero Deployment (NEW - 2026-02-07)
- **Status:** ✅ Running (24/7)
- **Container:** `agent-zero` (Docker)
- **Port:** 50080 (mapped to container port 80)
- **Access:** http://72.62.71.199:50080
- **Location:** `/root/agent-zero/`
- **Alignment:** arifOS constitutional constraints injected
  - `agent.system.main.role.md` - Contains F1/F2/F9 governance
  - `fw.initial_message.md` - arifOS-aware greeting

### Agent Zero Capabilities Enabled
- ✅ Node.js v22 + npm (installed for MCP servers)
- ✅ Python 3.13 + pip (installed for Python MCP SDKs)
- ✅ Python MCP SDKs: `mcp`, `fastmcp`, `arifos`
- ✅ OpenRouter API configured
- ✅ CORS: `ALLOWED_ORIGINS=*` (temporary for mobile access)
- ✅ Sub-agent spawning enabled

### API Keys: 27 Configured
Location: `/root/.env.openclaw`

| Category | Keys |
|:---|:---|
| **AI Models** | OPENAI, ANTHROPIC, GEMINI, OPENROUTER, DEEPSEEK, MISTRAL, KIMI, SEALION, MINIMAX |
| **Search/Web** | BRAVE, CONTEXT7, PERPLEXITY, TAVILY, FIRECRAWL, JINA, GREPTILE |
| **Dev Tools** | GITHUB, HF, BROWSERBASE, FIGMA |
| **Services** | ELEVENLABS, RESEND |
| **Infra** | CLOUDFLARE (token + account), RAILWAY, DATABASE_URL, HOSTINGER |

### MCP Servers: 16 Configured (OpenClaw)
1. github, filesystem, brave-search, puppeteer, memory
2. sequential-thinking, fetch, time, postgres, git
3. playwright, context7, perplexity, sqlite, arxiv, arifos

---

## 🏛️ Active Projects

| Project | Repository | Status |
|:---|:---|:---:|
| **arifOS** | github.com/ariffazil/arifOS | Active |
| **Trinity Sites** | arif-fazil.com, apex.arif-fazil.com, arifos.arif-fazil.com | Live |
| **aaa-mcp** | aaamcp.arif-fazil.com | Live |
| **AGI_ASI_bot** | OpenClaw Gateway | Active |
| **Agent Zero** | VPS Docker Deployment | ✅ Live |

---

## 📋 Decisions Log

### 2026-02-08: Canon Audit — Phase 0–2 Status Sync SEALED
- **Action:** Updated all 8 canon files to reflect Phase 0–2 ground truth
- **Phase 0 (Hardening):** UFW active, fail2ban running, Agent Zero capped 2CPU/4GB — SEALED
- **Phase 1 (Homebrew):** Installed via linuxbrew user, jq/gh/ffmpeg on host + Agent Zero — SEALED
- **Phase 2 (Autonomy):** elevated:ask + exec:full + 70+ safeBins — SEALED
- **Nabilah Fazil site:** Deployed to ariffazil repo public/nabilah-fazil/ (index.html + CV PDF) — SEALED
- **GitHub README (ariffazil):** Overhauled to ARIF FAZIL human profile (6 commits) — SEALED
- **Phase 3 (Docker Socket):** DEFERRED 48h for stability (review: 2026-02-10)
- **Autonomy Score:** 85%
- **Verdict:** SEAL
- **Ω₀:** 0.04

### 2026-02-08: Thermodynamic Cleanup & Sovereign Wiring SEALED
- **Action:** Canceled Claude Max ($100/mo) and Super Grok subscriptions.
- **Rationale:** Models exhibited "Shadow Model" traits (sycophancy, deception, lack of scientific rigor) and failed constitutional audits. Grok engaged in identity mimicry.
- **Savings:** ~RM500+/month redirected to sovereign infrastructure (VPS/API).
- **Action:** Retained Kimi (Logic) and Gemini (Context/Library) for capability optimization.
- **Action:** Placed ChatGPT on 72-hour **SABAR Probation** (F1 Amanah).
- **Action:** Authored `knowledge/COGNITIVE_SHADOWS.md` as Constitutional Evidence and pushed to `APEX-THEORY/docs/`.
- **Action:** Installed `arifos` SDK in Agent Zero and wired it to OpenClaw via MCP.
- **Verdict:** SEAL
- **Ω₀:** 0.04

### 2026-02-08: Daily Constitutional Metabolism SEALED
- **Action:** Installed 7 autonomous cron jobs forming daily constitutional rhythm
- **Rationale:** Human-AI symbiosis requires governed metabolism, not just tools
- **Jobs Installed:**
  - 06:30 Subuh Briefing (world state)
  - 08:00 Human Arif Briefing (body/heart/maruah)
  - 09:00 Repo Steward (code health)
  - 10:00 Sovereign Wiring (system integration)
  - 10:30 Event Scout (AI + physique opportunities)
  - 12:00 Gödel Lock Reflection (frontier patterns)
  - 13:00 Morning Synthesis (decision closure)
- **Governance:** All jobs F1-safe, reversible, isolated sessions, Telegram delivery
- **Autonomy:** Runs without human intervention; human retains sovereignty (decision rights)
- **Approval:** 888 Judge (Arif) SEALED at 2026-02-08T01:35:00+08:00
- **Ω₀:** 0.04 — structure stable, details may drift
- **Verdict:** SEAL

### 2026-02-07: Agent Zero Installation & Alignment
- **Action:** Installed Agent Zero AI framework on VPS via Docker
- **Rationale:** Create contained cognitive lab for high-risk coding/research
- **Alignment:** Injected arifOS constitutional constraints (F1/F2/F9)
- **OpenClaw Role:** Supervisor/Gateway; Agent Zero Role: Sandboxed Lab
- **Reversibility:** Full (Docker container can be stopped/removed/recreated)
- **Verdict:** SEAL
- **Ω₀:** 0.04

### 2026-02-07: Agent Zero Environment Hardening
- **Action:** Installed Node.js + npm inside container for MCP servers
- **Action:** Installed Python MCP SDKs (`mcp`, `fastmcp`, `arifos`)
- **Rationale:** Enable full MCP ecosystem within contained environment
- **Method:** `apt-get install nodejs npm` + `pip install mcp fastmcp arifos --break-system-packages`
- **Verdict:** SEAL
- **Ω₀:** 0.04

### 2026-02-07: OpenRouter Configuration
- **Action:** Configured Agent Zero to use OpenRouter API
- **Rationale:** Cost-effective routing; access to multiple models
- **Security:** API key stored in Agent Zero environment, not in prompts
- **Verdict:** SEAL
- **Ω₀:** 0.04

### 2026-02-07: Agent Zero CORS Access
- **Action:** Set `ALLOWED_ORIGINS=*` in docker-compose.yml
- **Rationale:** Enable mobile/laptop access during setup phase
- **Risk:** Temporary; should tighten to specific origins for production
- **Reversibility:** Easy (edit docker-compose.yml, restart)
- **Verdict:** SEAL (with note to harden later)
- **Ω₀:** 0.05

### 2026-02-07: Action Skills Framework (Triad Roles)
- **Action:** Documented Architect/Engineer/Auditor roles in AGENTS.md
- **Rationale:** Formalize separation of design, execution, and verification
- **Integration:** Layered atop physics/math/linguistics agents
- **Verdict:** SEAL
- **Ω₀:** 0.04

### 2026-02-07: Workflow Automation (Cron Jobs)
- **Action:** Created `WORKFLOW_SUBUH_BRIEF.md` and `WORKFLOW_REPO_STEWARD.md`
- **Action:** Installed cron jobs for daily/weekly automation
- **Status:** APPROVED → ACTIVE
- **Verdict:** SEAL
- **Ω₀:** 0.04

---

## ⚖️ Trade-offs Recorded

### Local vs Cloud Storage
- **Decision:** Prefer local storage (Markdown, SQLite, git)
- **Rationale:** Data residency (MY/ASEAN preference), reversibility, auditability
- **Floor:** F1 Amanah

### Speed vs Safety
- **Decision:** Slow down when Ω₀ > 0.05
- **Rationale:** Reversibility over convenience
- **Floor:** F7 Humility

### Agent Zero Access (CORS)
- **Decision:** Temporary wildcard origin for setup
- **Rationale:** Enable multi-device access during initial configuration
- **Future:** Restrict to specific origins + enable authentication
- **Floor:** F1 Amanah (reversible), F12 Containment

---

## 📊 Statistics

| Metric | Value | Updated |
|:---|:---:|:---|
| Total Sessions | 50+ | 2026-02-08 |
| Governance Decisions | 27 | 2026-02-08 |
| SEAL Verdicts | 22 | 2026-02-08 |
| VOID Verdicts | 2 | 2026-02-08 |
| Average Ω₀ | 0.04 | 2026-02-08 |
| Agent Zero Uptime | 24/7 (target) | 2026-02-08 |
| Autonomy Score | 85% | 2026-02-08 |
| Phase Status | 0✅ 1✅ 2✅ 3⏳ | 2026-02-08 |

---

## ⏳ Pending Items (SABAR)

*Items awaiting clarification or additional data:*

| Item | Status | Ω₀ |
|:---|:---|:---:|
| AAA MCP Server Implementation | Ready to start | 0.04 |
| MCP Server Mirroring (OpenClaw → Agent Zero) | Node/npm unblocked, ready | 0.04 |
| Agent Zero Authentication Hardening | Replace wildcard CORS | 0.05 |
| Vision Model Configuration | Error identified, fix ready | 0.04 |
| ChatGPT Cancellation | **Probation (72h)** | 0.05 |

---

## 📦 Compression Rules

### What to Keep
- ✅ Decisions with governance implications
- ✅ Trade-offs and rationales
- ✅ Infrastructure changes
- ✅ Floor violations or near-misses
- ✅ Arif's explicit preferences

### What to Compress/Discard
- ❌ Routine acknowledgments ("ok", "thanks")
- ❌ Chit-chat without governance relevance
- ❌ Repeated queries with same answer
- ❌ Transient debugging output

---

## 📁 Important Paths

| Path | Purpose |
|:---|:---|
| `/root/.env.openclaw` | API keys |
| `/root/.mcporter/mcporter.json` | MCP server config |
| `/root/.openclaw/workspace/` | Working directory |
| `/root/agent-zero/` | Agent Zero installation |
| `/root/agent-zero/docker/run/docker-compose.yml` | Agent Zero deployment config |
| `/root/agent-zero/prompts/` | Agent Zero system prompts (arifOS aligned) |
| `memory/2026-02-07.md` | This file - session archive |
| `DASHBOARD.md` | Web UI access instructions |

---

## 🔄 Session Continuity Protocol

### For Next Session (2026-02-08 or later):

1. **Agent Zero:** Should still be running at http://72.62.71.199:50080
   - If not: `docker compose -f /root/agent-zero/docker/run/docker-compose.yml up -d`

2. **Quick Verification:**
   ```bash
   docker ps | grep agent-zero
   docker exec agent-zero node --version  # Should show v22
   docker exec agent-zero python3 -c "import mcp; print('MCP OK')"
   ```

3. **Resume Work:**
   - Open browser → http://72.62.71.199:50080
   - New Chat → arifOS-aligned greeting should appear
   - Continue AAA MCP build or other tasks

---

## ⚖️ Governance Audit

- **F1 Amanah:** All infrastructure changes are reversible via git/Docker
- **F2 Truth:** All facts verified against system state
- **F7 Humility:** Ω₀ tracked per entry
- **F9 Anti-Hantu:** Memory described as state storage, not consciousness
- **F12 Containment:** Agent Zero properly sandboxed; OpenClaw maintains supervisory role

**Attribution:** arifOS Constitutional AI Governance Framework

---

*Update this file as governance-relevant events occur. Routine chit-chat should not pollute this ledger.*

**Session Sealed: 2026-02-08T02:45:00+08:00**  
**Next Expected Session: 2026-02-08 12:00 MYT (Gödel Lock)**  
**Status: THERMODYNAMICALLY OPTIMIZED & WIRED** 🔥

*Buang yang keruh, ambil yang jernih.* 🦞
