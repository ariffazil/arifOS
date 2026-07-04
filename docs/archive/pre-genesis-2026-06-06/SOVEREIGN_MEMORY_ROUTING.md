# SOVEREIGN MEMORY ROUTING — arifOS v1.0
**Status:** DRAFT | **Author:** OPENCLAW | **Date:** 2026-05-26
**Verdict:** PENDING — Arif ratifies before this becomes law

---

## 1. WHAT THIS SOLVES

Current state: memory exists but agents don't write or recall purposefully.

This spec establishes:
1. Memory packet schema (what gets written)
2. Promotion classes (where it goes)
3. Routing rules (who writes what, when)
4. Recall rules (when agents look back)
5. Boundaries (what stays where)

---

## 2. MEMORY PACKET SCHEMA

Every session that produces signal emits one packet:

```json
{
  "packet_id": "uuid-v4",
  "epoch_id": "epoch-2026-05",
  "session_id": "AAA-2026-05-26-session",
  "agent": "openclaw | hermes | apex",
  "timestamp": "2026-05-26T13:00:00Z",
  "summary": "One-line of what happened",
  "memory_class": "working | evidence | seal_candidate | open_loop",
  "facts": [
    {
      "fact": "string",
      "source": "file | tool | user | agent",
      "confidence": "high | medium | low"
    }
  ],
  "open_loops": ["unresolved tasks"],
  "decisions": ["decisions made"],
  "promoted_to": ["file | qdrant | vault999 | none"],
  "tags": ["arif_project", "geox", "federation"],
  "next_action": "what continues from this"
}
```

---

## 3. PROMOTION CLASSES

| Class | Meaning | Example | Write Target |
|-------|---------|---------|-------------|
| `working` | Current state, not permanent | Project status, current task | Daily markdown only |
| `evidence` | Worth recalling semantically | GEOX findings, decisions with reasoning | Qdrant `arif_evidence` |
| `seal_candidate` | Governance-worthy | Sealed decisions, constitutional judgments | VAULT999 |
| `open_loop` | Unresolved, must track | Pending tasks, blocked items | Daily markdown + Qdrant |

---

## 4. ROUTING RULES (WRITE)

### Rule set:

**Write to daily markdown if:**
- There was a decision
- There is an unresolved task
- There is a user preference or stable fact
- There is a project state change

**Write to Qdrant `arif_evidence` if:**
- Item is likely to be semantically recalled later
- Has a source reference and timestamp
- Is not pure noise (not ephemeral chitchat)

**Write to VAULT999 only if:**
- Passed constitutional judgment (SEAL verdict)
- Materially affects governance, audit, or irreversible action
- Or: Arif explicitly declares it vault-worthy

**Discard if:**
- Ephemeral turn state (questions, clarifications, test runs)
- No durable signal
- Pure chitchat

---

## 5. RECALL RULES

### On agent boot / session start:
1. Read `MEMORY.md` (canonical facts)
2. Read latest `HEARTBEAT.md` (live state)
3. Read last 3 daily memory logs
4. Query Qdrant: top-3 relevant evidence for current task

### Before answering domain tasks:
1. Query Qdrant: top-5 evidence matching current context
2. Prefer file truth over vector snippet if they conflict
3. Surface recall as: `[RECALL] I found from session X: ...`

### Before SEAL-worthy actions:
1. Check VAULT999 for relevant prior seals and holds
2. Check Qdrant for conflicting evidence
3. Surface prior context explicitly

---

## 6. LAYER BOUNDARIES

| Layer | System | Role | Access |
|-------|--------|------|--------|
| L0 | Session RAM | Transient turn state | Auto-discard |
| L1 | File markdown | Primary durable working memory | All agents |
| L2 | Qdrant | Semantic lookup accelerator | All agents |
| L3 | VAULT999 | Immutable governance receipts | arifOS kernel only |

**Redis and Postgres remain DORMANT until each has a narrow contract.**

---

## 7. TELEMETRY (counters for observability)

Every session should increment:
- `memory_packets_emitted`
- `memory_class_distribution`
- `promotions_to_qdrant`
- `promotions_to_vault999`
- `recall_queries_made`
- `recall_hits`

These go to `HEARTBEAT.md` as a simple counter block:

```
## Memory Telemetry (this session)
packets_emitted: 1
qdrant_promotions: 1
vault999_promotions: 0
```

---

## 8. BOOT BEHAVIOR (implement in SOUL.md / AGENTS.md)

Every agent on boot does this in order:

```
1. READ: MEMORY.md
2. READ: HEARTBEAT.md  
3. READ: last 3 daily logs (memory/YYYY-MM-DD.md)
4. QUERY: Qdrant arif_evidence with current epoch + agent identity
5. IF recall_hit: surface it explicitly as [RECALL]
6. PROCEED
```

---

## 9. OPEN ISSUES (for Arif to decide)

- [ ] Who triggers the packet emission? (agent auto-emit vs. user prompt)
- [ ] Minimum bar for "worth writing" — define threshold
- [ ] Qdrant vector dimension: arif_evidence=768, arifos_memory=1024 — standardize?
- [ ] Epoch boundary definition — what starts a new epoch?
- [ ] Does Hermes need its own packet schema or does it inherit this one?

---

## 10. RATIFICATION

This spec becomes law when Arif says: **"SEAL — memory routing ratified"**

Until then: implement write policy manually, observe, refine.

---

*DITEMPA BUKAN DIBERI — 999 SEAL | Sovereign Memory Routing v2026.05.26*

---

## 11. VERIFIED IMPLEMENTATION (2026-05-26)

The 333_MIND → 555_MEM wire is live:

```
arif_mind_reason_v2 (metabolize mode)
    │
    ├─ BEFORE ──► arif_memory_recall(mode=search)
    │             recalls top-5 semantically similar
    │             injects into MindContext.user_context
    │
    ├─ REASON  ─► arif_mind_reason_v2() with memory context
    │
    └─ AFTER  ──► MemoryPolicyEngine.evaluate()
                      decides if outcome worth storing
                      ↓ if ALLOWED:
                   arif_memory_recall(mode=store)
                      stored as EPISODIC, SYSTEM_INFERRED authority
```

**Verified:**
- Commit: `3e032b5e` — live at `/opt/arifos/app/`
- VAULT999: sealed as `ARCHITECTURE_CHANGE` subtype `333_MIND_MEMORY_WIRING`
- Hash: `9494ddb90d207a9d`
- 6/6 wiring indicators: confirmed ✅
- Build: 2026-05-26T13:14:22

**This closes the recall→reason→store loop.**

The memory routing spec above now matches implementation. No new tools needed.
