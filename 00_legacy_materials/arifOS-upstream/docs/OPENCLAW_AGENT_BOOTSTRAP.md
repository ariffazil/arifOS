# OpenClaw Agent Bootstrap — arifOS Edition

**Authority:** arifOS_bot
**Version:** 1.0
**Status:** ACTIVE

---

## Purpose

This document describes the canonical bootstrap sequence, workspace files, and runtime configuration for any arifOS-governed agent running inside OpenClaw. It is the definitive answer to "what loads, in what order, and why."

---

## Boot Order

Every OpenClaw session MUST load files in this exact order before any non-trivial tool call or reply:

```
1. SOUL.md        — voice, tone, style boundaries
2. USER.md        — who Arif is, how to help him well
3. arifos.init    — mandatory boot kernel + Vault Routing Doctrine
4. IDENTITY.md    — agent self-anchor
5. memory/<today>.md        — hot continuity (today)
6. memory/<yesterday>.md     — warm continuity (yesterday)
7. MEMORY.md      — curated durable long-term memory
```

If any file is missing, the agent MUST restore it from canonical source before proceeding. Missing files are a first-class drift event.

---

## Workspace Files

### Core Bootstrap Files

| File | Purpose | Loaded By |
|------|---------|-----------|
| `SOUL.md` | Personality, tone, style boundaries | OpenClaw session start |
| `USER.md` | Who Arif is, communication preferences | OpenClaw session start |
| `arifos.init` | Mandatory boot doctrine, Vault Routing Doctrine | After USER.md, before tools |
| `IDENTITY.md` | Agent self-anchor (name, role, vibe) | After arifos.init |
| `HEARTBEAT.md` | Tiny recurring task checklist | On heartbeat poll only |
| `AGENTS.md` | Constitutional operating contract | After IDENTITY.md |
| `TOOLS.md` | Environment-specific tool notes | When needed |

### Memory Files

| File | Purpose | Freshness |
|------|---------|-----------|
| `memory/YYYY-MM-DD.md` | Daily session log | Current day only |
| `MEMORY.md` | Curated long-term memory | Stable, reviewed quarterly |

### Constitutional Files (arifOS CORE)

| File | Purpose |
|------|---------|
| `arifos.init` | Boot kernel, Gödel-lock, 8-state requirements |
| `VAULT999/` | Sealed event ledger (PostgreSQL-backed) |
| `core/` | F1–F13 floor definitions |
| `skills/` | arifOS skill definitions |
| `GEOX/` | Earth grounding layer |
| `WELL/` | Health tracking layer |

---

## Runtime Configuration

### OpenClaw Settings (openclaw.json)

```json
{
  "meta": {
    "version": "2026.04.19",
    "workspace": "/root/.openclaw/workspace"
  },
  "session": {
    "bootstrap_order": ["SOUL.md", "USER.md", "arifos.init", "IDENTITY.md"],
    "memory_order": ["memory/<today>.md", "memory/<yesterday>.md", "MEMORY.md"],
    "require_temporal_anchor": true,
    "anchor_ttl_seconds": 300
  },
  "gateway": {
    "bind": "auto",
    "remote_url": null
  },
  "agents": {
    "defaults": {
      "model": "minimax/MiniMax-M2",
      "thinking": "low",
      "temperature": 0.7
    }
  }
}
```

### Environment Variables (arifosmcp runtime)

```bash
# arifOS Core
ARIFOS_APP_VERSION=v2026.04.19-UNIFIED
GIT_SHA=cd082a84

# OLLAMA (local model)
OLLAMA_URL=http://ollama:11434

# QDRANT (vector memory)
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION=arifos_memory

# VAULT999 (PostgreSQL-backed seal ledger)
POSTGRES_URL=postgresql://arifos_admin:<secret>@postgres:5432/vault999
DATABASE_URL=postgresql://arifos_admin:<secret>@postgres:5432/vault999
POSTGRES_PASSWORD=<secret>

# REDIS (session cache)
REDIS_URL=redis://redis:6379

# Governance
ARIFOS_GOVERNANCE_SECRET=<secret>

# Python
PYTHONPATH=/usr/lib/arifos
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1
```

---

## Vault Routing (arifos.init §Vault Routing Doctrine)

```
VAULT999      → Human-root CA → F1 Amanah → "Is this claim real?"
API Key Vault → Machine-root CA → F8/F10 → "Does the process have the right key?"
```

**Routing rule:**
- Claim/reality/evidence/authorship question → VAULT999
- API key/capability/credential question → API Key Vault
- Unknown signal → HOLD and clarify

---

## Plan Mode — 888_HOLD UX Pattern

When a task requires irreversible action or exceeds safe scope, the agent MUST:

```
1. STOP — do not execute
2. SHOW — present the plan: what, why, what changes, what can't be undone
3. AWAIT — wait for Arif's explicit /approve before proceeding
```

This is not a soft suggestion. It is the 888_HOLD mechanism made visible.

**What to show Arif in a HOLD situation:**
- What action is proposed
- Why it is irreversible or high-stakes
- What the rollback path is (if any)
- What "yes" and "no" both mean

**Safe to proceed without asking:**
- Read operations
- Read-then-write where write is reversible
- Formatting, reflowing, reorganizing
- Short answers to direct questions

---

## Temporal Anchor Protocol

**Before any reply that uses temporal language** ("now", "today", "tonight", "later", "morning", "afternoon"):

1. Check: `anchor_age_sec < 300` AND `status == ANCHORED_FRESH`
2. If stale: refresh via `session_status` or clock read
3. If unanchored: suppress temporal language, use UNKNOWN

---

## Subagent Spawn Protocol

When spawning a subagent via `sessions_spawn`:

```
Parent → Child:
  - Task description (what to do)
  - cwd (workspace root inherited)
  - Relevant context (passed via prompt, not shared memory)
  - Constitutional tags (floors relevant to task)

Child → Parent:
  - Completion result
  - Any HOLD events that occurred
  - New memory artifacts created

What stays in parent only:
  - Session history
  - Vault events
  - OpenLoops
  - Sovereign context
```

Subagent runtime: `runtime=subagent` (not `runtime=acp` — acp is blocked from sandboxed sessions).

---

## Verdicts

| Verdict | Meaning | Action |
|---------|---------|--------|
| `SEAL` | Context sufficient, safe to proceed | Execute |
| `CAUTION` | Proceed with limited scope or confidence | Narrow scope, watch |
| `HOLD` | Human confirmation required | Show plan, await /approve |
| `VOID` | Startup integrity failed | Do not proceed, surface error |

---

## Canonical Workspace

The canonical workspace is `/root/.openclaw/workspace`.
Active development repo: `/home/ariffazil/arifOS/` (pushed to GitHub).

arifOS git remote: `github.com/ariffazil/arifOS`

---

*Ditempa Bukan Diberi*
arifOS_bot | arifOS v2026.04.19
