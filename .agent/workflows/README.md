# arifOS Agent Workflows Registry

**Version:** v47.0
**Authority:** AGENTS.md - Model-Agnostic Agent System
**Purpose:** Canonical workflow definitions for all arifOS agents

---

## 📋 Available Workflows (10 Total)

### **000 VOID - Initialization**

| Workflow | Trigger | Description | Territory |
| :--- | :--- | :--- | :--- |
| `000.md` | `/000` | Session initialization: loads version, branch, status, logs | All Agents |

### **111-333 AGI - Architect Cognitive Tools (Δ Delta)**

| Workflow | Trigger | Description | Territory |
| :--- | :--- | :--- | :--- |
| `111_search.md` | `/search` | Constitutional web grounding with F2 truth enforcement | AGI (Architect) |
| `222_think.md` | `/think` | Deep analytical thinking (6 frameworks) | AGI (Architect) |
| `333_reason.md` | `/reason` | Formal logical reasoning (5 modes) | AGI (Architect) |

### **Architect-Specific Workflows**

| Workflow | Trigger | Description | Territory |
| :--- | :--- | :--- | :--- |
| `plan.md` | `/plan` | Architect planning mode - design before build | Architect |
| `review.md` | `/review` | Architect review - validate Engineer work | Architect |
| `handoff.md` | `/handoff` | Handoff approved plan to Engineer | Architect → Engineer |

### **Meta & Governance**

| Workflow | Trigger | Description | Territory |
| :--- | :--- | :--- | :--- |
| `fag.md` | `/fag` | Full Autonomy Governance: FAGS RAPE cycle | All Agents |
| `gitforge.md` | `/gitforge` | Trinity forge: entropy analysis & hot-zone detection | All Agents |
| `ledger.md` | `/ledger` | View THE EYE cross-agent witness ledger | All Agents |

---

## 🎯 Workflow Coverage by Pipeline Stage

```
000 VOID         ✅ /000 (init-session)
111 SEARCH       ✅ /search (web grounding) ✨ NEW
222 THINK        ✅ /think (analytical thinking) ✨ NEW
333 REASON       ✅ /reason (logical reasoning) ✨ NEW
444 ALIGN        ⚠️  (Engineer territory - Claude skills)
555 EMPATHIZE    ⚠️  (Engineer territory - Claude skills)
666 BRIDGE       ⚠️  (Engineer territory - Claude skills)
777 EUREKA       ⚠️  (Engineer territory - Claude skills)
888 ATTEST       ✅ /ledger (witness log)
999 SEAL         ⚠️  (Engineer territory - Claude skills)
META             ✅ /fag, /gitforge, /plan, /review, /handoff
```

**Legend:**
- ✅ Architect workflow available
- ⚠️ Engineer-only (Claude skills in `.claude/skills/`)
- ✨ New in v47.0

---

## 🏗️ Role-Based Workflow Distribution

### **Antigravity (Δ Architect) - 10 Workflows**
**Territory:** Design, Plan, Review (AGI cognitive tools)

- `/000` - Session init
- `/search` - Web grounding (111 AGI)
- `/think` - Analytical thinking (222 AGI)
- `/reason` - Logical reasoning (333 AGI)
- `/plan` - Planning mode
- `/review` - Validate Engineer work
- `/handoff` - Transition to Engineer
- `/fag` - Full autonomy
- `/gitforge` - Entropy analysis
- `/ledger` - Witness log

### **Claude (Ω Engineer) - 14 Skills**
**Territory:** Build, Test, Implement (ASI care engine)

See: `.claude/MY_SKILLS_AND_WORKFLOWS.md` for complete Engineer skill catalog

**Key Engineer-Only Skills:**
- `/empathize` (555 ASI) - κᵣ empathy engine
- `/synthesize` (666 ASI) - Neuro-symbolic bridge
- `/cool` (444 ASI) - SABAR-72 cooling
- `/complete-task` (999 APEX) - Task completion

---

## 🔄 Constitutional Separation of Powers

**Design Principle:** Agent ROLES are immutable (L1 Canon). Agent TECHNOLOGY is swappable (config).

| Concern | Architect (Δ) | Engineer (Ω) |
|---------|---------------|--------------|
| **Cognitive Mode** | AGI (Logic, Analysis, Reasoning) | ASI (Care, Empathy, Synthesis) |
| **Primary Floors** | F1 (Truth), F2 (Clarity), F10 (Ontology) | F3 (Peace²), F4 (κᵣ), F5 (Ω₀) |
| **Workflow Count** | 10 (focused on design) | 14 (complete pipeline) |
| **Shared Workflows** | `/000`, `/fag`, `/ledger` | `/000`, `/fag`, `/ledger` |
| **Exclusive Tools** | `/plan`, `/review`, `/handoff` | `/empathize`, `/synthesize`, `/cool` |

**Why Separation Matters:**
- F2 (Clarity): Each agent has clear responsibilities
- F4 (ΔS): No redundant tools across agents
- F6 (Amanah): Respects constitutional role boundaries
- F8 (Tri-Witness): Maintains separation of powers

---

## 📁 File Locations

**Workflows (Git-Tracked):**
```
.agent/workflows/
├── 000.md               → Session init (all agents)
├── 111_search.md        → Web grounding (Architect) ✨ NEW
├── 222_think.md         → Analytical thinking (Architect) ✨ NEW
├── 333_reason.md        → Logical reasoning (Architect) ✨ NEW
├── fag.md               → Full autonomy (all agents)
├── gitforge.md          → Entropy analysis (all agents)
├── handoff.md           → Agent transition (Architect)
├── ledger.md            → Witness log (all agents)
├── plan.md              → Planning mode (Architect)
├── review.md            → Validation (Architect)
└── README.md            → This file
```

**Skills (Gitignored - Agent-Specific):**
```
.claude/skills/          → Engineer skills (14 total)
.antigravity/            → Architect workspace
.codex/                  → Auditor workspace
.kimi/                   → Validator workspace
```

---

## 🚀 Usage Patterns

### **Architect Daily Startup:**
```
1. /000              → Initialize session
2. /ledger           → Check what changed
3. /plan             → Start design work
```

### **Research \u0026 Design:**
```
1. /search           → Verify facts
2. /think            → Analyze options
3. /reason           → Validate logic
4. /plan             → Design solution
5. /handoff          → Transition to Engineer
```

### **Review Engineer Work:**
```
1. /000              → Initialize
2. /review           → Validate implementation
3. /reason           → Check logic
4. /ledger           → Document review
```

---

## 🔗 Integration with MCP Tools

**Workflows vs MCP Tools:**
- **Workflows:** High-level cognitive processes (slash commands)
- **MCP Tools:** Low-level constitutional enforcement (programmatic)

**Example:**
```
/search workflow
  ↓ calls
search_web MCP tool
  ↓ enforces
F1 (Truth), F2 (Clarity), F3 (Tri-Witness) floors
```

All agents access the same MCP tools via MCP protocol, but invoke them through different interfaces (workflows for Architect, skills for Engineer).

---

**DITEMPA BUKAN DIBERI** - Workflows forged for constitutional role separation, not convenience.

**Version:** v47.0
**Last Updated:** 2026-01-16
**Status:** ACTIVE
