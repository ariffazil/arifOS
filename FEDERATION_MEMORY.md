# arifOS Federation Memory Architecture — Live Map
> **Canonical Source:** `ariffazil/arifOS:FEDERATION_MEMORY.md`
> **Authority:** arifOS F13 SOVEREIGN (Muhammad Arif bin Fazil)
> **Last Verified:** 2026-05-27 by Hermes ASI
> **Valid From:** 2026-05-27
> **Rule:** SOT state. All agents must read this for memory layer ground truth. Stale summaries in other docs must point here.

---

## The 6-Layer Federation Memory Architecture (Atlas Compass)

```
Layer  Name          Engine         Status   Role
─────  ────────────  ────────────   ──────   ─────────────────────────────
 L1    Ephemeral     Redis          ✅ Live  now
 L2    Session       Redis          ✅ Live  session
 L3    Associative   Qdrant         ✅ Live  similar (864 vectors)
 L4    Relational    Supabase       ⚠️ Hold  official records (shelves exist, flow minimal)
 L5    Knowledge     Graphiti       ⚠️ Hold  relationships (partial)
 L6    Immutable     VAULT999       ✅ Live  forever (16,859 lines)
```

### Live Counts & Milestone 2 Gate (as of 2026-06-02)

| Layer | Store | Count | Phase 1 Verdict |
|-------|-------|-------|-----------------|
| L1/L2 | Redis | - | Live |
| L3 | Qdrant | 864 vectors | Live |
| L4 | Supabase Cloud | shelves exist | Shelves built. Workers not filing yet. |
| L5 | Graphiti | partial | - |
| L6 | VAULT999 | 16,859 lines | Active |

### Supabase Cloud — Phase 1 Domain (L4)

*Naming convention: `arifosmcp_*` not `s000.*` — same intent, different namespace.*
*See the full integration rule: [SUPABASE_MCP_CONTRACT.md](file:///root/arifOS/docs/contracts/SUPABASE_MCP_CONTRACT.md).*

**Structured Tables (Shelves Built):**
- `arifosmcp_tool_calls`
- `arifosmcp_approval_tickets`
- `arifosmcp_floor_rules`
- `arifosmcp_memory_policy`
- `arifosmcp_memory_contract`
- `arifosmcp_sessions`
- `arifosmcp_canon_records`
- `arifosmcp_daily_roots`
- `arifosmcp_portfolio_snapshots`
- `arifosmcp_transactions`
- `arifosmcp_well_states`
- `arifosmcp_agent_telemetry`
- `mcp_prompt_versions` (planned)
- `mcp_resources` (planned)
- `mcp_manifest_snapshots` (planned)

**VAULT L4/L6 FACET:**
- `vault_sealed_events` (1,338 rows — actual L6 mirror)
- `vault_outcomes` (12,269+ rows)
- `vault_seals` (61 rows — legacy)
- `vault_shim_hits` (2 rows)

> **Milestone 2 Integration Gap:** arifOS MCP and federation organs must write receipts via the shared organ adapter (fail-soft). Do not connect Supabase to MCPs as a router.

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
