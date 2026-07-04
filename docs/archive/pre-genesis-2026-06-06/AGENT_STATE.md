# AGENT STATE — May 2026

**Canonical repo:** `ariffazil/arifOS`
**Last updated:** 2026-05-01
**Purpose:** Single source of truth for agent identity, role, and intelligence level.

---

## The Two Agents

| Property | OPENCLAW (AGI) | Hermes Agent (ASI) |
|----------|---------------|-------------------|
| **Role** | AGI Bot — tactical execution | ASI Bot — strategic judgment |
| **Stage** | 000–777 (execute) | 888 (deliberate) |
| **Default autonomy** | L1; max L3 without 888 | L4 (deliberation only) |
| **Status** | 🟢 Online | 🔜 Pending deployment |
| **Platform** | A-FORGE VPS | TBD |
| **Channel** | arifOS Telegram group | TBD |
| **Governance** | 000–999 loop, F1–F13 | 888 ASI deliberation |

---

## OPENCLAW — Intelligence State

### Governance Files
| File | Status | Notes |
|------|--------|-------|
| SOUL.md | ✅ Current | Identity, niat, instrument framing |
| IDENTITY.md | ✅ Current | OPENCLAW role definition |
| USER.md | ✅ Current | Arif context |
| AGENTS.md | ✅ Current | 000–999 loop replaces plain ReAct |
| LOOP.md | ✅ New | Operational 000–999 implementation |
| AUTONOMY.md | ✅ New | L0–L5 ladder |
| HEARTBEAT.md | ✅ Rewritten | Live protocol |
| CHECKPOINT.md | ✅ New | Session continuity |
| DECISIONS.md | ✅ New | Sealed decision log |
| TASKS.md | ✅ New | Active work ledger |
| RECOVERY.md | ✅ New | Failure runbook |
| FLOORS.md | ✅ New | F1–F13 reference |
| TOOLS.md | ✅ Updated | Local environment notes |
| MEMORY.md | ✅ Updated | Sealed facts anchor |

### Archived (Stale — Do Not Use)
- CLAUDE.md — archived 2026-05-01 (conflicting L3-only instruction set)
- GEMINI.md — archived 2026-05-01 (conflicting L3-only instruction set)
- ARIF.md — archived 2026-05-01 (old METABOLIC KERNEL v1.0)

### Current Intelligence Level
| Metric | Value |
|--------|-------|
| Governance loop | 000–999 constitutional loop ✅ |
| Autonomy level | L2–L3 (max L3 without 888) |
| Self-monitoring | HEARTBEAT live protocol ✅ |
| Session continuity | CHECKPOINT recovery ✅ |
| Decision trace | DECISIONS structured log ✅ |
| Task persistence | TASKS ledger ✅ |
| Evidence discipline | 222 EVIDENCE required ✅ |
| Safety gates | 444 CRITIQUE (F09/F12) ✅ |
| Rollback | CHECKPOINT + RECOVERY ✅ |
| Maturity score | ~43/75 (was 32/75 pre-upgrade) |

### What Is NOT Yet Live
- HEARTBEAT auto-writer (manual discipline required)
- CHECKPOINT auto-write on session end
- 777 Measure entropy_delta instrumentation
- Full L4 self-monitoring

---

## Hermes Agent — Intelligence State

### Role
ASI Bot — Strategic judgment agent. Judges candidate actions passed by OPENCLAW.
Deliberates, audits, and issues 888 verdicts.

### Relationship to OPENCLAW
| Dimension | OPENCLAW | Hermes Agent |
|-----------|----------|-------------|
| Lane | AGI — execution | ASI — judgment |
| Stage | 000–777 | 888 |
| What it does | Proposes, executes | Judges, deliberates |
| Speaks to Arif | Proposes and reports | Issues verdicts |
| Governance | 000–999 loop | 888 deliberation |

### Deployment Status
🔜 **Pending.** Not yet deployed on A-FORGE.
- Requires A2A gateway (aaa-a2a container is running ✅)
- Requires Hermes Agent runtime (not yet built)
- Requires 888 deliberation protocol wiring

### What Needs to Happen Before Hermes Agent
1. Hermes Agent runtime built and containerized
2. A2A route configured: OPENCLAW → AAA → Hermes Agent
3. 888 deliberation protocol defined and wired
4. Hermes Agent governance files created

---

## MCP Organs (Tools, Not Agents)

| Organ | Endpoint | Role | Status |
|-------|----------|------|--------|
| WEALTH | `https://wealth.arif-fazil.com/mcp` | Capital intelligence | 🟢 Healthy |
| GEOX | `https://geox.arif-fazil.com/mcp` | Earth intelligence | 🟢 Healthy |
| WELL | `https://well.arif-fazil.com/mcp` | Human substrate | 🟢 Running |
| arifOS MCP | `https://mcp.arif-fazil.com/mcp` | Constitutional kernel | 🟢 Healthy |

---

## What Should Be In The Repo

### OpenClaw Workspace (`/srv/openclaw/workspace/`)
Core governance files only — SOUL, IDENTITY, USER, AGENTS, LOOP, AUTONOMY,
HEARTBEAT, CHECKPOINT, DECISIONS, TASKS, RECOVERY, FLOORS, TOOLS, MEMORY.

### arifOS Root
Canonical SoT — AGENTS.md, SOUL.md, IDENTITY.md, LOOP.md, AUTONOMY.md.
Constitutional law — `000/`, `arifosmcp/`, `core/`.
Agent definitions — `docs/agents/`, `agents/`.
Skills — `skills/`.

### Archive (Do Not Touch As Governance)
- `00_legacy_materials/` — upstream archive, 118MB, not active
- `docs/archive/` — old staging docs
- Archived files (CLAUDE.md, GEMINI.md, ARIF.md) — stale, prepended with archive notice

---

**Ditempa Bukan Diberi — Forged, Not Given.**
