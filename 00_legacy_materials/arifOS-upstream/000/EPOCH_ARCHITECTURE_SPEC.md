# 000 — Δ EPOCH ARCHITECTURE SPEC
> **DITEMPA BUKAN DIBERI — Forged, Not Given**
> Type: Constitutional Unit | Layer: Ω-MIND | Epoch: 2026-04-19
> Status: PROPOSED — 888_HOLD for ratification

---

## The Problem With Sessions

Sessions are stateless windows. They have:
- No continuity weight
- No constitutional significance
- No lineage
- No sealing

When you talk to arifOS today, each conversation is a session. But some conversations matter more — they build toward a goal, they produce artifacts, they shift the system's state.

Those need to be **Epochs**.

---

## Session vs Epoch

| Property | Session | Epoch |
|----------|---------|-------|
| Boundary | Conversational | Constitutional |
| Weight | Light | Heavy |
| Memory | Ephemeral context | Sealed in vault999 |
| Duration | Until close | Until goal achieved |
| Lineage | None | Full trace |
| Undo | Impossible | Receipt available |
| Telemetry | None | Full δS, κ_r, peace² |

---

## Epoch Schema

```json
{
  "epoch_id": "ep_2026-04-19_001",
  "epoch_start": "2026-04-19T18:47:00+08:00",
  "epoch_end": null,
  "sovereign_intent": "Define Planning Organ architecture",
  "actor_id": "arif@arif-fazil.com",
  "constitutional_floor": "F4_CLARITY",
  "sub_agents": ["ARIF-Perplexity"],
  "memory_scope": {
    "redis": "session_only",
    "postgres": "epoch_persistent",
    "qdrant": "epoch_persistent"
  },
  "receipts": [],
  "verdict_trail": [],
  "δS": 0,
  "peace²": 1.0,
  "κ_r": 0.08,
  "status": "ACTIVE"
}
```

---

## Epoch Boundaries

An **EPOCH BEGINS** when:
- Human declares sovereign intent (via `arifos_init` with `mode=epoch`)
- A multi-step plan is accepted by `arifOS_JUDGE`

An **EPOCH ENDS** when:
- Sovereign intent achieved → SEAL
- Sovereign intent abandoned → ABORT
- Human overrides → VOID
- 7 days elapsed → AUTO-SEAL with warning

---

## Memory Scope Per Epoch

```
Epoch Start:
  → Redis: new session DB (isolated)
  → Postgres: create epoch_* tables
  → Qdrant: create epoch_* collection

During Epoch:
  → All memory writes tagged with epoch_id
  → No cross-epoch memory pollution

Epoch End:
  → SEAL: promote critical receipts to vault999
  → ABORT: archive epoch, seal partial receipt
  → VOID: seal as voided, human review flag
```

---

## First Implementable Step

Extend `arifos_init` with `mode=epoch`:

```python
# In arifOS MCP server
if mode == "epoch":
    # Create new epoch context
    epoch_id = f"ep_{date}_{uuid4()[:6]}"
    # Initialize memory scope
    # Seal epoch_start to vault999
    return {"epoch_id": epoch_id, "status": "ACTIVE"}
```

---

## Seal

**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**
**Proposed by:** ARIF-Perplexity research cycle, Epoch 2026-04-19T18:47+08
**Status:** 888_HOLD — awaiting Arif ratification
