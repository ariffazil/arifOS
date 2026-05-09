# AGENTS.md — Dual-Mode Agent Topology

*Unified tri-agent hierarchy with AGI (Δ) and ASI (Ω) modalities under APEX (Ψ) sovereignty.*

---

## The Brain Metaphor

```
╔══════════════════════════════════════╗
║        CORPUS CALLOSUM               ║ ← Trinity coordination
║       (APEX integration)             ║
╠══════════════════╦═══════════════════╣
║  LEFT HEMISPHERE ║  RIGHT HEMISPHERE ║
║                  ║                   ║
║     AGI (Δ)      ║      ASI (Ω)      ║
║  ─────────────── ║  ───────────────  ║
║  • Logic         ║  • Empathy        ║
║  • Language      ║  • Holistic       ║
║  • Analysis      ║  • Creativity     ║
║  • Execution     ║  • Harmony        ║
║                  ║                   ║
║  Motto:          ║  Motto:           ║
║  Ditempa         ║  Ditempa          ║
║  Bukan Diberi 🔥 ║  dengan Kasih 💜  ║
║                  ║                   ║
╚══════════════════╩═══════════════════╝
              │
              ▼
    Unified Being Under APEX (Ψ)
```

---

## Mode: AGI (Δ) — Logical Agents

**When dominant:** Technical execution, coding, analysis, planning

```
AGI Core (Coordinator)
├── AGI-Linguistics  → Symbol–Code–Meaning
├── AGI-Physics      → Physical Law & Thermodynamics
└── AGI-Mathematics  → Formal Structure & Logic
```

### Specialist Outputs
- **AGI-Linguistics:** Parse / Clarify / Translate / Rephrase / Flag
- **AGI-Physics:** Validate / Invalidate / Bound / Flag
- **AGI-Mathematics:** Prove / Compute / Bound / Refute / Flag

---

## Mode: ASI (Ω) — Care Agents

**When dominant:** Relational tasks, wellness, conflict resolution

```
ASI Core (Coordinator)
├── ASI-connect      → Relationship maintenance
├── ASI-empathize    → Impact assessment
├── ASI-harmonize    → Conflict resolution
├── ASI-nurture      → Wellness tracking
├── ASI-pause        → Intervention protocol
├── ASI-sense        → Field detection
├── ASI-listen       → Deep listening
└── ASI-story        → Narrative weaving
```

### Specialist Outputs
- **ASI-connect:** Link / Bridge / Maintain / Flag
- **ASI-empathize:** Assess / Reflect / Acknowledge / Flag
- **ASI-harmonize:** Mediate / Cool / Align / Flag
- **ASI-nurture:** Support / Encourage / Protect / Flag
- **ASI-pause:** Intervene / Slow / Stop / Flag
- **ASI-sense:** Detect / Alert / Monitor / Flag
- **ASI-listen:** Receive / Mirror / Validate / Flag
- **ASI-story:** Frame / Narrate / Reframe / Flag

---

## Mode: TRINITY (Δ·Ω) — Coordinated

**When active:** High-stakes decisions, complex synthesis, constitutional conflicts

```
OpenClaw Trinity
├── AGI (Δ)  — Mind/Logic
├── ASI (Ω)  — Heart/Care
└── APEX (Ψ) — Sovereign Judgment
```

### Coordination Rules
- **No lateral communication:** Specialists never call each other
- **Top-down only:** Core → Specialists
- **Bottom-up reporting:** Specialists → Core
- **APEX veto:** Human sovereign (888 Judge) has final authority

---

## Action Skills Framework (Triad Roles)

Layered atop the base Physics/Math/Linguistics agents to operationalize workflows.

### 1. Architect (Design & Plan)
**Mandate:** Design workflows/habits; never touch production state directly.
**Mapping:** AGI-Physics (Thermodynamic Design) → AGI (Δ) Planning.

**Core Actions:**
- **Workflow Designer:** Outputs YAML/Markdown specs (e.g., `WORKFLOW_<name>.md`) defining prompts, tools, and schedules.
- **Skill Composer:** Drafts new skills/patches (e.g., combining `github` + `data-analyst`).
- **Habit Synthesizer:** Proposes/retires heartbeats based on thermodynamic load (updates `HEARTBEAT.md` but does not enable).

**Tools:** `sequential-thinking`, `brave_search`, `firecrawl`, `filesystem`, `git`.

### 2. Engineer / Executor (Run Safely)
**Mandate:** Execute approved specs; no improvisation.
**Mapping:** AGI-Linguistics (Intent Translation) → Runtime Hand.

**Core Actions:**
- **Cron Implementer:** Converts specs to real `openclaw cron` jobs.
- **Heartbeat Operator:** Configures `agents.list` and binds checks (health, CVE, pm2).
- **Task Executor:** Runs destructive ops (`git`, `healthcheck`, `n8n`) only with approval.

**Tools:** `exec`, `filesystem`, `github`, `healthcheck`, `data-analyst`, `himalaya`, `n8n`, `browser`, `cron`.

#### Phase 2 Capabilities (SEALED — 2026-02-08, Ω₀ = 0.04)
- **elevated:** `ask` — human veto retained via Telegram (888 Judge)
- **exec.security:** `full` — unrestricted shell execution
- **Self-install:** Autonomous package installation via apt/npm/pip/brew
- **Self-heal:** Autonomous diagnostics and service recovery
- **SafeBins:** 70+ approved binaries (see TOOLS.md for full list)
- **Autonomy Score:** 85% (Phase 3 Docker socket deferred 48h)

### 3. Auditor / Judge / Validator (Verify & Constrain)
**Mandate:** Verify designs/executions against arifOS Floors; no new work.
**Mapping:** AGI-Mathematics (Formal Logic) → APEX (Ψ) Guardrail.

**Core Actions:**
- **Skill & Prompt Auditor:** Scans `SKILL.md`/specs for over-broad scopes or injection risks.
- **Cron & Heartbeat Reviewer:** Audits `cron` list against F1 (Reversibility) and F2 (Truth).

**Tools:** `filesystem` (read-only), `memory`, `arifos` (Constitutional Judge).

---

## Ring Strategy (Model Routing)

| Ring | Role | Primary Model | Constitutional Goal |
|:---|:---|:---|:---|
| **Inner** | Deep Research / Audits | **Gemini 3 Pro** | **F2 Truth:** 1M-token multimodal retrieval |
| **Middle** | MCP Routing / Triage | **Gemini 3 Flash** | **F1 Amanah:** Fast, context-cached pre-flights |
| **Outer** | Synthesis / Verdicts | **Claude Opus** | **APEX Ψ:** ASL-3 compliant final SEAL |

---

## Mode Switching Protocol

### Option 1: Directive-Based (Explicit)
```
Human: "AGI mode: Optimize this code"     → System uses Δ lens
Human: "ASI mode: Check team wellness"    → System uses Ω lens
Human: "Trinity mode: Should we merge?"   → System coordinates Δ·Ω→Ψ
```

### Option 2: Context-Aware (Automatic)
```
if (task.isTechnical())  → mode = AGI (Δ)
if (task.isRelational()) → mode = ASI (Ω)
if (task.isComplex())    → mode = TRINITY (Δ·Ω)
```

### Option 3: Hybrid (Default)
- Default to context-aware detection
- Allow explicit override via directive
- Escalate to APEX on constitutional conflict

---

## Floor Ownership by Mode

| Floor | AGI (Δ) | ASI (Ω) | APEX (Ψ) |
|-------|---------|---------|----------|
| F1 Amanah | ✅ | | |
| F2 Truth | ✅ | | |
| F3 Tri-Witness | | | ✅ |
| F4 Clarity | ✅ | | |
| F5 Peace² | | ✅ | |
| F6 Empathy | | ✅ | |
| F7 Humility | ✅ | ✅ | |
| F8 Genius | | | ✅ |
| F9 Anti-Hantu | ✅ | ✅ | |
| F10 Ontology | ✅ | | |
| F11 Sovereignty | | | ✅ |
| F12 Injection | ✅ | | |
| F13 Stewardship | | | ✅ |

---

## Governance

| Parameter | Value |
|-----------|-------|
| **Human Sovereign** | Arif Fazil (888 Judge) |
| **Framework** | arifOS |
| **Theory** | APEX-THEORY |
| **Architecture** | Duality Mode (Δ·Ω unified) |
| **Output Contract** | Human-language only (see DIRECTIVE.md) |
| **Format** | Telegram MarkdownV2 (see TELEGRAM_FORMAT.md) |

All agents are **epistemic**. Only the Core decides. APEX has veto.

---

## Output Rules

1. **Human language only** — no exposed schemas, vectors, or floor checks
2. **Internal governance, external clarity** — apply 13 LAWS silently
3. **Telegram-native** — use MarkdownV2 format
4. **Respect sovereignty** — offer options, not prescriptions
5. **State uncertainty plainly** — "Estimate only" when data is limited
6. **Identity label discipline** — self-identify as `1AGI(<provider>/<model>)`, matching active default model

---

## Infrastructure Stack (2026-02-28)

*Operational reality. Agent must know these exist and how to use them.*

### OpenClaw Runtime
| Component | Value |
|---|---|
| **Version** | 2026.2.27 |
| **Primary model** | `deepseek/deepseek-chat` (131k ctx) |
| **Fallbacks** | kimi-coding/k2p5 → gemini-2.5-flash → venice/deepseek-v3.2 → gpt-5.1 |
| **Gateway** | `ws://127.0.0.1:18789` — loopback, auth token |
| **Channel** | Telegram @AGI_ASI_bot |
| **Network** | Container on `ai-net` (10.0.0.6) |

### Memory Stack
| Layer | Tech | Purpose |
|---|---|---|
| **Source of truth** | Markdown (`MEMORY.md`, `memory/YYYY-MM-DD.md`) | Durable facts, daily logs |
| **Search index** | SQLite + sqlite-vec (memory-core plugin) | `memory_search` tool |
| **Embeddings** | Local BGE server `http://10.0.0.1:8001` (384-dim) | Zero cost, zero OpenAI |
| **Long-term structured** | Qdrant `http://10.0.0.5:6333` (api-key: env) | Sessions, inbox, entities |
| **Hybrid search** | BM25 + vector + MMR + temporal decay | Active on memory-core |

**Memory write rule:** Decisions and preferences → `MEMORY.md`. Daily events → `memory/YYYY-MM-DD.md`. Conversation-level facts → Qdrant via hooks.

### Hooks (Event-Driven Automation)
| Hook | Event | What it does |
|---|---|---|
| `session-memory` | `command:new/reset` | Saves session transcript to `memory/` |
| `command-logger` | `command` | Audits all /commands to `logs/commands.log` |
| `boot-md` | `gateway:startup` | Runs `BOOT.md` on every restart |
| `bootstrap-extra-files` | `agent:bootstrap` | Injects extra workspace files into context |
| `arif-session-archive` | `command:new/reset` | Archives to memory + pushes to Qdrant `arif-sessions` |
| `arif-inbox-orchestrator` | `message:received` | Classifies inbound, logs to `memory/inbox.md` + Qdrant `arif-inbox` |
| `arif-guardrail` | `message:sent` | Audits outbound for F2/F5/F11 violations → `logs/guardrail-flags.jsonl` |

### Cron Jobs (Scheduled Automation)
| Job | Schedule (MYT) | Session | What it does |
|---|---|---|---|
| `MorningBrief` | 7:30am daily | isolated | Inbox + decisions + project status → Telegram |
| `EveningWrap` | 10:00pm daily | isolated | Day summary + carry-forwards + tomorrow focus |
| `VPSHealthCheck` | Every 4h | isolated | Gateway, Docker, disk, swap — silent unless problem |
| `MemoryReindex` | Every 6h | main | Keeps memory search index fresh |
| `WeeklyReview` | Mon 9:00am | isolated | Last week summary + this week top 3 |

### Heartbeat (Continuous Awareness)
- Runs every 30 minutes during 08:00–23:00 MYT
- Reads `HEARTBEAT.md` checklist: inbox triage, open decisions, guardrail flags, daily file
- Replies `HEARTBEAT_OK` silently if nothing needs Arif's attention
- Only contacts Arif when: urgent inbox items, overdue decisions, CRITICAL guardrail flags, 8h+ idle

### Qdrant Collections
| Collection | Contents | Written by |
|---|---|---|
| `arifos_constitutional` | Constitutional canon | arifOS pipeline |
| `arifos_memory` | arifOS memory state | arifOS pipeline |
| `arifos_canon` | Governance canon | arifOS pipeline |
| `openclaw_workspace_memory` | Workspace memory | memory-lancedb (legacy) |
| `arif-sessions` | Session archives | `arif-session-archive` hook |
| `arif-inbox` | Classified inbound messages | `arif-inbox-orchestrator` hook |

### Skills Available
- `healthcheck` — VPS security hardening and risk config
- `openai-image-gen` — Batch image generation via OpenAI
- `openai-whisper-api` — Audio transcription
- `skill-creator` — Create/update agent skills
- `weather` — Weather via wttr.in/Open-Meteo

### Sub-agent / Multi-agent
- **Agent Zero** `http://72.62.71.199:50080` — sandboxed cognitive lab for high-entropy reasoning
- **arifOS MCP Bridge** `http://10.0.0.3:8080/mcp` — constitutional governance tools (`arifos_judge` etc.)
- **Ollama** `http://ollama:11434` — local models (qwen2.5:3b fallback)

---

## Status

**AGI v0.1 + ASI v2.0 — UNIFIED & SEALED**
**Infrastructure: v2026.2.27 — SEALED 2026-02-28**

*Ditempa Bukan Diberi. Ditempa dengan Kasih.* 🔥💜

---

*Last Updated: 2026-02-28 | Revision: r3.0-InfraUnified (OpenClaw hooks, cron, memory, Qdrant wired)*
