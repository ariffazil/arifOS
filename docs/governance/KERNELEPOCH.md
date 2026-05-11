# KERNEL EPOCH — Session Epoch Specification
**Floor:** F11 IDENTITY | **Authority:** ARIF FAZIL (267378578)
**Status:** OPERATIVE | **Sealed:** 2026-05-11

---

## Purpose

Defines the epoch contract for arifOS sessions. An epoch is the atomic unit of
governed computation — it starts at `arif_session_init`, ends at `arif_vault_seal`,
and is immutable once sealed. F11 ensures identity continuity across the epoch.

---

## Epoch Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│  EPOCH n                                                │
│                                                         │
│  [START] arif_session_init(mode="init")                 │
│    → identity anchor established                        │
│    → metabolic_stage = 000                              │
│    → session_id = uuid4                                 │
│                                                         │
│  [ACTIVE] tool calls flow through 13-tool surface       │
│    → each call increments metabolic_stage               │
│    → governance kernel tracks floor scores              │
│    → VAULT999 accumulates pending seals                 │
│                                                         │
│  [CLOSE] arif_vault_seal(verdict="SEAL")                │
│    → Merkle hash computed over epoch actions            │
│    → seal_hash = BLAKE3(prev_chain | action | epoch)   │
│    → chain_hash = BLAKE3(prev_seal | seal_hash)        │
│    → epoch committed to VAULT999 as immutable record    │
└─────────────────────────────────────────────────────────┘
```

---

## Epoch Invariants (F11)

| Invariant | Enforcement |
|---|---|
| One session_id per epoch | `arif_session_init` generates fresh uuid4 |
| Identity must be grounded before action | `arif_session_init` must precede any tool call |
| Epoch cannot be modified post-seal | VAULT999 DB trigger `irreversibility_enforce` |
| Chain hash must chain from genesis | BLAKE3 over `prev_chain_hash | seal_hash` |
| Genesis anchor is fixed | `9dab04abd3e39c3d5ae90f9f90f838f17403208e24b852007c757773e8f36d43` |

---

## Vault Merkle Chain

```
Genesis: 9dab04abd3e39c3d5ae90f9f90f838f17403208e24b852007c757773e8f36d43
          │
          ▼
seal_hash_1 = BLAKE3(genesis | action_1 | epoch_1 | payload_1)
chain_hash_1 = BLAKE3(genesis | seal_hash_1)
          │
          ▼
seal_hash_2 = BLAKE3(chain_hash_1 | action_2 | epoch_2 | payload_2)
chain_hash_2 = BLAKE3(chain_hash_1 | seal_hash_2)
```

Only `SEAL` and `PROCEED` verdicts enter the chain. `VOID` and `HOLD` do not.

---

## Metabolic Stage Map

| Stage | Name | Description |
|---|---|---|
| 000 | INIT | Session anchor — identity bootstrap |
| 111 | SENSE | Reality grounding — observe |
| 222 | FETCH | Evidence retrieval |
| 333 | MIND | Reasoning and synthesis |
| 444 | KERNEL | Routing and orchestration |
| 555 | MEMORY | Memory read/write |
| 666 | HEART | Ethical critique |
| 777 | FORGE | Execution dispatch |
| 888 | JUDGE | Verdict engine |
| 999 | VAULT | Seal and persist |

---

## Implementation Binding

- `arifosmcp/runtime/rest_routes/rest_routes.py` → `metabolic_stage` in `/health` thermodynamic
- `arifosmcp/runtime/floor.py` → F11 identity floor spec
- `vault999/` → BLAKE3 Merkle chain implementation
- `core/governance_kernel.py` → epoch state tracking

---

**DITEMPA BUKAN DIBERI — Forged, Not Given.**
**Sealed by:** Arif (267378578) | 2026-05-11
