# arifOS Federation Memory Contract

> **Authority:** arifOS MCP Kernel · **Ratified:** 2026-06-03 · **Status:** ACTIVE
> **Motto:** DITEMPA BUKAN DIBERI — Forged, Not Given

This document is the **single source of truth** for how memory flows across the
arifOS Federation. Every organ (arifOS, GEOX, WEALTH, WELL, A-FORGE, AAA,
OpenClaw, APEX) MUST conform.

---

## 1. The 6-Layer Atlas (canonical)

```
L1 Ephemeral  → in-process token buffer, turn variables       (kernel-internal)
L2 Session    → AutoMemory, current thread, conversation      (Redis / JSON file)
L3 Associative→ semantic vectors, "what feels similar?"       (Qdrant, 1024-dim bge-m3)
L4 Relational → typed rows, audit, "what exactly happened?"   (Supabase / Postgres)
L5 Knowledge  → entities + relations, "who connects to whom?" (Graphiti / FalkorDB)
L6 Immutable  → hash-chained audit, "what is final?"         (VAULT999)
```

**Memory does not become truth until it has provenance.**
**Truth does not become final until sealed.**

---

## 2. The Single Interface: `arif_memory_recall`

Every federated organ that needs to remember MUST call:

```python
arifOS.arif_memory_recall(
    mode="store" | "recall" | "search" | "context" | "stats" | "audit" | "prune",
    ...
)
```

**This is the only path.** Organs do not write to Qdrant, Supabase, or Graphiti
directly. They call `arif_memory_recall(mode="store", ...)`, and the kernel
fans out to L3 + L4 + L5.

### Why one interface?

| Reason | Consequence |
|---|---|
| Constitutional floors (F1–F13) | Every write is gated once, not in every organ |
| Provenance chain | `actor_id` + `session_id` is mandatory on every store |
| Phoenix-72 tri-witness | Audit + cooldown + tri-witness applied uniformly |
| Federation lookup | Any agent can read any other agent's memory through the same query surface |
| Reversibility | A single rollback point if the contract changes |

---

## 3. The Three-Leg Federation Write

When `arif_memory_recall(mode="store", content=...)` is called, the kernel
fires three legs in sequence. Each leg is independent. **At least one must
succeed for `stored=True`.**

| Leg | Engine | Endpoint | Purpose | Failure mode |
|---|---|---|---|---|
| **L3** | Qdrant | `http://localhost:6333` (`arifos_memory` coll.) | semantic vector + payload | blocks `stored=True` |
| **L4** | Supabase | `aws-1-ap-southeast-1.pooler.supabase.com:6543` (`memory_store` table) | durable row + cross-refs | warn + continue |
| **L5** | Graphiti | `http://localhost:8000/mcp` (group_id=`af_forge`) | entity graph + relations | fire-and-forget |

### L3 (Qdrant) — required
- Embedding model: `bge-m3` (1024-dim) via Ollama
- Collection: `arifos_memory`
- Payload: full content + provenance + Phoenix-72 + F4 entity tags

### L4 (Supabase) — durable
- Connection: `ARIFOS_MEMORY_POSTGRES_URL` env var (Supabase pooler)
- Table: `memory_store` (13 columns: `id, tier, text, metadata, qdrant_id, session_id, entity_tags, distillation_status, distillation_metadata, valid_at, recorded_at, deleted_at, created_at`)
- pgbouncer-compatible: `statement_cache_size=0`
- Code: `arifosmcp/runtime/memory_store.py::_pg_write()`

### L5 (Graphiti) — enrich
- Bridge: `arifosmcp/runtime/l5_graphiti_bridge.py`
- group_id: `af_forge` (configurable via `GRAPHITI_GROUP_ID` env)
- Source: `json` (structured episode body)
- NEVER raises. NEVER blocks. Returns `{l5_status: "queued"|"skipped"|"error"}`

#### L5 worker status (2026-06-03, F2 TRUTH correction)

The bridge **queues** episodes to Graphiti MCP `add_memory`. However, the
downstream Graphiti worker is **neutralized** (888 Sovereign command — hardcoded
OpenAI dependencies create an API paradox; not auto-woken).

**Operational reality:**
- `l5_status: "queued"` means "in the queue" — **not** "in the graph"
- 888 injects L5 entities manually via raw Cypher to FalkorDB
- The bridge stays in place as a **forward-compatible substrate** — if 888
  re-enables the worker, queued episodes process automatically
- **Do NOT auto-wake, debug, or fix the Graphiti worker.** 888 owns this.

**For organ tools writing memory:** treat L5 as advisory only. The contract
guarantees L3 + L4 durability. L5 is enrichment-on-paper until further notice.

---

## 4. Cross-Organ Memory Rules

### R1 — Single write surface
All organs write memory through `arif_memory_recall(mode="store")`. No organ
writes directly to Qdrant, Supabase, or Graphiti.

### R2 — Mandatory provenance
Every store call MUST pass `actor_id` and `session_id`. F11 AUTH gate
hard-blocks stores without these.

```python
arif_memory_recall(
    mode="store",
    content="WEALTH computed NPV=$4.2M for prospect X",
    actor_id="wealth-engine",        # WAJIB
    session_id=current_session_id,   # WAJIB
    tier="canon",                    # sacred | canon | session | ephemeral
    tags=["wealth", "npv", "prospect_x"],
)
```

### R3 — Tier discipline

| Tier | TTL | Use case | Prunable? |
|---|---|---|---|
| `sacred` | ∞ | constitutional doctrine, F-floor definitions, sealed verdicts | NO (F06 immunity) |
| `canon` | 90d | organ decisions, project outcomes, validated insights | yes (with reason) |
| `session` | 24h | current session continuity, scratch context | yes (auto) |
| `ephemeral` | 1h | in-flight variables, transient state | yes (auto) |

### R4 — Read-with-context
Recalls MUST pass `context="canon"` or `context="high_stakes"` when the
recall is feeding a SEAL/SABAR/VOID decision. This triggers SABAR Stage 2A
advisory metadata.

### R5 — Cross-organ search namespace
Tag with `[organ]_[domain]_[key]`. Example:
- `wealth_npv_prospect_x`
- `geox_porosity_field_a`
- `well_homeostasis_arif`

### R6 — Graphiti isolation
Cross-organ entities live in `group_id="af_forge"`. Personal/anonymous
entities use a separate group_id. Never mix personal PII into `af_forge`.

---

## 5. Failure Mode Matrix

| L3 Qdrant | L4 Supabase | L5 Graphiti | Result | Action |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | `stored=true, l5_status=queued` | normal — all legs live |
| ✅ | ✅ | ❌ | `stored=true, l5_status=skipped` | normal — durable wins, graph deferred |
| ✅ | ❌ | ✅ | `stored=true, l5_status=queued, pg_ok=false` | DEGRADED — durable leg missing, repair |
| ✅ | ❌ | ❌ | `stored=true, l5_status=skipped` | DEGRADED — durable leg missing, repair |
| ❌ | * | * | `stored=false, error=qdrant_write_failed` | FATAL — semantic leg dead, repair immediately |

**Repair protocol** (DEGRADED state):
1. Re-run `arif_memory_recall(mode="store", ...)` after fixing the failed leg
2. Check `arif_memory_recall(mode="audit")` for the escalation queue
3. If a memory exists in L3 but not L4, run backfill (Phoenix-72 import mode)

---

## 6. Phoenix-72 Tri-Witness

Every store fires the Phoenix-72 audit band. It computes:
- **tri-witness** (human + AI + earth) — must sum to ≥ 1.0
- **ψ-utility** (information value)
- **anti-hantu flag** (F9 — no consciousness/feeling claims)
- **cooldown expiry** (anti-contradiction window)

If the F9 anti-hantu flag triggers, the store is auto-downgraded to
`phoenix_state=contradiction_hold` and queued for sovereign review.

---

## 7. Memory Wire — Cross-Organ Pattern

```python
# In any organ's tool (WEALTH, GEOX, WELL, A-FORGE, AAA):
async def some_tool(...):
    # 1. Compute something
    result = compute_stuff(...)

    # 2. Remember it (ONE call, fans out to L3+L4+L5)
    await arif_memory_recall(
        mode="store",
        content=f"{organ}: computed {result}",
        actor_id=organ_name,         # "wealth" | "geox" | "well" | ...
        session_id=current_session,
        tier="canon",
        tags=[organ, domain, result_key],
    )

    # 3. Recall prior context for THIS organ
    prior = await arif_memory_recall(
        mode="search",
        query=f"{organ} {domain}",
        actor_id=organ_name,
        session_id=current_session,
    )

    return result
```

---

## 8. The 7th Wall — Sovereign Boundary

The contract is the constitution. It is **not** a 7th memory layer.

The 7th "wall" is the **sovereign boundary** (F13). It sits OUTSIDE the
memory substrate. It decides what is sacred, what is canon, what is voided,
what is sealed to L6. The sovereign never reads memory directly — the
sovereign reads VAULT999 (L6), which is the *only* finality surface.

Memory is FOR the organs. VAULT999 is FOR the sovereign.

---

## 9. Verification Commands

```bash
# L3 health
curl -s http://localhost:6333/collections/arifos_memory | python3 -m json.tool

# L4 health (Supabase pooler)
psql "$(grep ARIFOS_MEMORY_POSTGRES_URL /etc/arifos/arifos.env | cut -d= -f2- | tr -d \"'\\)" \
  -c "SELECT count(*), max(recorded_at) FROM memory_store;"

# L5 health
curl -s http://localhost:8000/health
curl -s -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" -H "Accept: text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}}' \
  -D /tmp/h && \
  curl -s -X POST http://localhost:8000/mcp \
    -H "Content-Type: application/json" -H "Accept: text/event-stream" \
    -H "mcp-session-id: $(grep -i mcp-session-id /tmp/h | awk '{print $2}' | tr -d \\r)" \
    -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_status","arguments":{}}}'

# All three together (via arifOS MCP)
curl -s -X POST http://localhost:8088/mcp \
  -H "Content-Type: application/json" -H "Accept: text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}}' \
  -D /tmp/h2 && \
  curl -s -X POST http://localhost:8088/mcp \
    -H "Content-Type: application/json" -H "Accept: text/event-stream" \
    -H "mcp-session-id: $(grep -i mcp-session-id /tmp/h2 | awk '{print $2}' | tr -d \\r)" \
    -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"arif_memory_recall","arguments":{"mode":"stats"}}}'
```

---

## 10. Change Protocol

This contract is **constitutional**. Any change to:
- The 6-layer atlas
- The single-interface rule
- Tier TTLs
- Cross-organ rules (R1–R6)
- The failure matrix

…requires **explicit sovereign ratification** per the F13 doctrine. Cosmetic
wording, new examples, additional cross-references are Tier 1 (autonomous).

---

**DITEMPA BUKAN DIBERI — One substrate. One interface. Many organs.**

*Arif Fazil, F13 SOVEREIGN · arifOS Federation · 2026-06-03*
