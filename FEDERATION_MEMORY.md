# arifOS Federation Memory Architecture — Live Map
> **Canonical Source:** `ariffazil/arifOS:FEDERATION_MEMORY.md`
> **Authority:** arifOS F13 SOVEREIGN (Muhammad Arif bin Fazil)
> **Last Verified:** 2026-05-27 by Hermes ASI
> **Valid From:** 2026-05-27
> **Rule:** SOT state. All agents must read this for memory layer ground truth. Stale summaries in other docs must point here.

---

## The 6-Layer Federation Memory Architecture

```
Layer  Name          Engine         Status   Purpose
─────  ────────────  ────────────    ──────   ─────────────────────────────
 L1    Ephemeral     Hermes L2       ✅ Live  Turn-by-turn, session RAM
 L2    Session       Hermes state   ✅ Live  FTS5 full-text, 30-day retain
                           .db
 L3    Associative   Qdrant         ⚠️ Lean  Semantic search, 10 pts total
                           (Docker)           (was 42 in stale doc)
 L4    Relational    Postgres       ❌ DOWN  Durable records, schema inactive
                           (Docker)           DB up but nothing writing
 L5    Knowledge     Graphiti MCP  ✅ Live  Entity graph, temporal links
                           (Docker)           Accessible via arifOS MCP
 L6    Immutable     VAULT999       ✅       Hash-chained append-only truth
                           (Files)    Healthy  16,794 total entries
```

### Live Counts (as of 2026-05-27)

| Layer | Store | Count | Source |
|-------|-------|-------|--------|
| L3 | Qdrant `arif_evidence` | 1 pt | `curl 127.0.0.1:6333/collections` |
| L3 | Qdrant `arifos_memory` | 9 pts | same |
| L3 | **Total** | **10 pts** | stale docs said 42 |
| L4 | Postgres | empty | nothing writing to it |
| L5 | Graphiti | active, not remotely queryable | accessible via arifOS MCP only |
| L6 | VAULT999 | 16,794 lines across 4 files | `wc -l /root/arifOS/VAULT999/*.jsonl` |

### VAULT999 File Breakdown

```
SEALED_EVENTS.jsonl   1,338 entries  — witnessed constitutional events
outcomes.jsonl        15,348 entries — judgment outcomes
shim_hits.jsonl           2 entries  — gateway shim events
vault999.jsonl          106 entries  — core ledger
─────────────────────────────────────────────────────────
Total                16,794 lines
```

---

### Port Map

| Service | Address | Port | Access |
|---------|---------|------|--------|
| Qdrant | `127.0.0.1` | 6333 | localhost Docker proxy |
| PostgreSQL | `0.0.0.0` | 5432 | Docker-managed |
| Redis | `0.0.0.0` | 6379 | Docker-managed |
| Ollama | `127.0.0.1` | 11434 | localhost |
| Graphiti MCP | container net | 8080 | arifOS MCP bridge only |
| VAULT999 | `/root/arifOS/VAULT999/` | — | file system, all agents |

---

## Agent Access Map

```
Agent          L1/L2       L3 Qdrant    L4 Postgres  L5 Graphiti   L6 VAULT999
────────────   ─────────   ──────────   ──────────   ──────────   ──────────
arifOS MCP (Ω)  ✅ via     ✅ R/W       ❌ blocked   ✅ R/W via    ✅ R/W
                session              DB down        arifOS MCP    ack_irrevers
                                   ──────────────────────────────   ible write
Hermes ASI      ✅ native  ❌           ❌            ❌            ✅ seal
(Telegram)      L1/L2                                                         events only
AAA Cockpit     ✅ via     ❌           ❌            ✅ telemetry   ❌
                            A2A                       via broker
WELL            ✅ own     ✅           ❌            ❌            ✅ own
                state                                                         outcomes only
WEALTH          ✅         ✅           ❌            ❌            ✅ ledger
                                                                          append
GEOX            ✅         ✅           ❌            ❌            ❌
A-FORGE         ✅         ❌           ❌            ❌            ❌
OpenCode/       ✅ full    ✅ via       ❌            ✅ via        ✅ via
Kimi             L2        arifOS                  arifOS       arifOS
```

**Note:** `arifOS MCP` (port 8088) is the gateway all agents use to reach L3/L5/L6. Direct Qdrant/Postgres access from outside Docker is not exposed.

---

## Hermes ASI Private Memory

Distinct from federation memory. Not shared across agents.

```
MEMORY.md   — 2,200 char bounded snapshot, prompt-injected, zero latency
USER.md     — user profile, preferences, corrections
state.db    — FTS5 full-text session transcript, 30-day auto-prune
```

---

## Federation Memory Broker Plugin

**Location:** `/root/.hermes/plugins/federation-memory-broker/`

- Polls Hermes `state.db` every 60s
- Writes telemetry to Redis key: `federation:hermes:session_telemetry`
- Exposes `federation_get_hermes_telemetry()` via A2A for AAA cockpit
- **Status:** Plugin installed but Redis keys not populating — broker loop may not be active. Telemetry only, not critical path.

---

## Known Discrepancies vs. Stale Docs

| Claim in old docs | Actual state | Corrected |
|-------------------|-------------|-----------|
| Qdrant "42 vectors" | 10 pts total (2 collections) | ✅ update doc |
| PostgreSQL "62 records" | Empty, nothing writing | ✅ correct |
| VAULT999 "14,786 entries" | 16,794 lines total | ✅ correct |
| L4 relational | DB up (33h) but schema inactive | ✅ note as DOWN |
| Graphiti | Running (35h, healthy) but not remotely queryable | ✅ clarify |

---

## DITEMPA BUKAN DIBERI

Memory ground truth comes from live probes, not from cached summaries.
Every agent must verify before acting on memory-layer claims.

**Version:** 1.0 | **Sealed:** 2026-05-27 | **Authority:** arifOS F13 SOVEREIGN
