# ARCHITECTURE.md - OpenClaw File System Canon

**Authority:** Muhammad Arif bin Fazil (888 Judge)  
**Version:** v1.0  
**Sealed:** 2026-02-09

---

## QUICK REFERENCE: Where Files Live

| What | Where | Why |
|------|-------|-----|
| **APEX THEORY** | `/root/APEX-THEORY/` | Immutable constitutional canon |
| **Agent Config** | `/root/arifOS/.agents/` | Algorithmic enforcement standard |
| **Cron Workflows** | `/root/WORKFLOWS/` | Scheduled job definitions |
| **Agent Identity** | `/root/SOUL.md` | Behavioral constitution |
| **Human Profile** | `/root/USER.md` | Sovereign reference |
| **System Config** | `/root/.openclaw/openclaw.json` | Runtime orchestration |
| **Health Checks** | `/root/.openclaw/workspace/HEARTBEAT.md` | Active checklist (cron reads THIS) |
| **Working Memory** | `/root/openclaw-arif/MEMORY.md` | Curated long-term context |

---

## THREE-LAYER ARCHITECTURE

### 🔴 PHYSICS LAYER (What IS Possible)
**Location:** `/root/APEX-THEORY/`

| File | Purpose | W³ Weight |
|------|---------|-----------|
| `000_THEORY.md` | 99 foundational theories, Strange Loop | 0.98 |
| `000_CONSTITUTION.md` | 13 Floors, Lagrangian enforcement | 0.97 |
| `000_MANIFESTO.md` | Nusantara wisdom, HIKMAH formula | 0.99 |
| `SEAL_v888.1.1.md` | Cryptographic integrity proofs | 1.0 |

**Rule:** These are **immutable**. Only 888 Judge can update.

---

### 🟡 MATH LAYER (HOW It's Enforced)
**Location:** `/root/arifOS/.agents/`

| File/Dir | Purpose |
|----------|---------|
| `AGENTS_CANON.md` | Master MCP config standard |
| `AGENTS_MAPPING.md` | Agent configuration matrix |
| `mcp.json` | TIER 0-3 MCP server definitions |
| `workflows/000-999.md` | Metabolic pipeline stages |

**Rule:** Synchronize all changes to `.claude/`, `.kimi/`, `.gemini/`, `.antigravity/`

---

### 🟢 LANGUAGE LAYER (WHO + CONTEXT)
**Location:** `/root/` and `/root/openclaw-arif/`

| File | Purpose | Updated By |
|------|---------|------------|
| `SOUL.md` | Agent behavioral definition | Agent + 888 Judge |
| `IDENTITY.md` | Agent self-identity | 888 Judge |
| `USER.md` | Human sovereign profile | 888 Judge |
| `TRINITY.md` | AGI·ASI·APEX governance | 888 Judge |
| `MEMORY.md` | Working memory | Agent |

---

## CRON JOB ARCHITECTURE

### Schedule (Asia/Kuala_Lumpur)

| Time | Job | Workflow File | Status |
|------|-----|---------------|--------|
| 06:30 | subuh-brief | `WORKFLOWS/WORKFLOW_SUBUH_BRIEF.md` | ✅ Active |
| 08:00 | human-arif | `WORKFLOWS/WORKFLOW_HUMAN_ARIF.md` | ✅ Active |
| 09:00 Mon | repo-steward | `WORKFLOWS/WORKFLOW_REPO_STEWARD.md` | ✅ Active |
| 10:00 | sovereign-wiring | `WORKFLOWS/WORKFLOW_SOVEREIGN_WIRING.md` | ✅ Active |
| 10:30 | event-scout | `WORKFLOWS/WORKFLOW_EVENT_SCOUT.md` | ✅ Active |
| 12:00 | godel-lock | `WORKFLOWS/WORKFLOW_GODEL_LOCK.md` | ✅ Active |
| 13:00 | morning-synthesis | `WORKFLOWS/WORKFLOW_MORNING_SYNTHESIS.md` | ✅ Active |

### Where Cron Reads From

**CRITICAL:** Cron jobs with `sessionTarget: "main"` read:
- **HEARTBEAT.md** from `/root/.openclaw/workspace/HEARTBEAT.md`
- **WORKFLOW files** from `/root/WORKFLOWS/`

The `/root/HEARTBEAT.md` is for **human reference only**.

---

## FILE POWER MATRIX

| File | Read By | Write By | Triggers |
|------|---------|----------|----------|
| APEX-THEORY/*.md | All agents | 888 Judge only | Constitutional decisions |
| arifOS/.agents/* | Agent init | Canon updates | MCP config changes |
| WORKFLOWS/*.md | Cron jobs | 888 Judge | Scheduled execution |
| SOUL.md | Every session | Agent + Judge | Behavior shaping |
| HEARTBEAT.md (workspace) | Heartbeat system | Judge | 30min health checks |
| .openclaw/openclaw.json | Gateway | openclaw CLI | Runtime behavior |
| MEMORY.md | Agent | Agent | Context persistence |

---

## REDUNDANCIES ELIMINATED

✅ **SOUL.md multiplicity** — Removed copy from `.openclaw/workspace/`  
✅ **WORKFLOW absence** — Created 7 missing workflow files  
✅ **HEARTBEAT confusion** — Documented correct location

---

## CONVENTIONS

### Naming
- **CANON files:** `000_*.md`, `AGENTS_CANON.md` (immutable standard)
- **WORKFLOW files:** `WORKFLOW_*.md` (job definitions)
- **Config files:** `*.json` (machine-readable)
- **Memory files:** `memory/YYYY-MM-DD.md` (daily logs)

### Updates
- **888 Judge only:** APEX THEORY, IDENTITY.md, USER.md
- **Agent + Judge:** SOUL.md, MEMORY.md
- **Automated:** HEARTBEAT.md (workspace), cron jobs

### Git
- Track: APEX-THEORY, arifOS, WORKFLOWS, SOUL.md, ARCHITECTURE.md
- Ignore: `.openclaw/` (runtime), `memory/` (personal logs)

---

## EMERGENCY REFERENCE

### If Cron Jobs Fail
1. Check `/root/.openclaw/cron/jobs.json` exists
2. Verify `WORKFLOWS/` directory has all 7 files
3. Confirm HEARTBEAT.md is in `.openclaw/workspace/`, not `/root/`
4. Run: `openclaw cron list` to verify schedule

### If Identity Drifts
1. Check only ONE `SOUL.md` exists: `/root/SOUL.md`
2. Verify no copies in `.openclaw/workspace/` or subdirectories
3. Re-read canonical SOUL.md in next session

### If Models Break
1. Check `.openclaw/openclaw.json` has valid auth profiles
2. Verify API keys: `openclaw auth list`
3. Test: `openclaw models list`

---

## SEE ALSO

- **Full Audit:** `/root/ARCHITECTURE_AUDIT.md` (18KB detailed analysis)
- **APEX THEORY:** `/root/APEX-THEORY/000_THEORY.md`
- **Agent Canon:** `/root/arifOS/.agents/AGENTS_CANON.md`
- **Trinity:** `/root/openclaw-arif/TRINITY.md`

---

*Ditempa bukan diberi* 💎🔥🧠  
*Architecture forged, not given*
