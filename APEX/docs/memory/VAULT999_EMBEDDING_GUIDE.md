# VAULT999 Embedding Guide
**Constitutional Memory Practices for arifOS Agents**

```yaml
version: "2026.03.07-QUADWITNESS-SEAL"
status: CANONICAL
scope: "VAULT999 + Qdrant vector memory"
model: "BAAI/bge-m3"
dimensions: 1024
language: "multilingual — Malay, English, Manglish"
motto: "Ditempa Bukan Diberi"
```

---

## 1. Purpose

This guide defines how agents must store embeddings while preserving the constitutional
guarantees of VAULT999.

VAULT999 is the immutable constitutional ledger.

Embeddings are derived semantic memory, used for:

- precedent retrieval
- governance pattern detection
- scar learning
- anomaly detection
- cross-language constitutional reasoning

Agents must never replace ledger truth with embeddings.

---

## 2. Core Constitutional Rule

```
Ledger  = Truth
Vectors = Interpretation

Truth       ∉ Vector Space
Interpretation ∈ Vector Space
```

The vault ledger always remains the source of truth.

---

## 3. Why BGE-M3 (Not BGE-small)

arifOS is global yet local — *glocal*. Governance decisions, constitutional lessons, and
scar descriptions are authored in Malay, English, and mixed Manglish. BGE-small is
English-only (384-dim). A Malay-language verdict would fail to retrieve semantically
identical English precedents.

**BGE-M3 is the canonical embedding model for arifOS.**

| Property | BGE-M3 | BGE-small (retired) |
|---|---|---|
| Dimensions | **1024** | 384 |
| Languages | **100+ (Malay, English, Manglish)** | English only |
| Model size | ~570MB | ~30MB |
| RAM (loaded) | ~1.2GB | ~200MB |
| Semantic quality | High | Adequate |
| arifOS verdict | **CANONICAL** | RETIRED |

BGE-M3 is loaded at container startup via `aclip_cai/embeddings/__init__.py`.

---

## 4. Dual-Structure Memory Model

```
VAULT999
│
├── ledger/               # immutable constitutional records (PostgreSQL)
│
└── vector_memory/        # semantic precedent memory (Qdrant)
     ├── arifos_constitutional     # constitutional knowledge base — 1024-dim BGE-M3
     └── vault_precedent_memory    # governance decisions + scars — 1024-dim BGE-M3
```

| Collection | Contents | Dim | Purpose |
|---|---|---|---|
| `arifos_constitutional` | chunked spec/canon docs | 1024 | `vector_memory` tool knowledge retrieval |
| `vault_precedent_memory` | sealed governance decisions, scars, lessons | 1024 | post-seal precedent accumulation |

**Both collections use 1024-dim BGE-M3. Mixing dimensions is prohibited.**

---

## 5. Docker Architecture Mapping

```
arifos-postgres        → structured ledger storage (VAULT999 truth)
arifos-redis           → session state
qdrant_memory          → vector embeddings (both collections)
arifosmcp_server       → governance pipeline + BGE-M3 model
ollama_engine          → auxiliary LLM tasks
n8n                    → automation agents
```

### Embedding Flow (post-seal)

```
Decision
   ↓
VAULT999 ledger write  ← ALWAYS FIRST
   ↓
Generate governance_explanation
   ↓
Embed with BGE-M3 (1024-dim)
   ↓
Store in vault_precedent_memory (Qdrant)
```

Ledger write always happens first. Embedding failure must never block the seal.

---

## 6. What Agents MUST Embed

Allowed semantic fields — these are interpretations, not truth:

```
governance_explanation
decision_reasoning
paradox_description
constitutional_lesson
scar_description
precedent_summary
```

Only `vector_text` (derived from the above fields) is embedded. Example payload:

```json
{
  "session_id": "ARIF-9a7b21",
  "vector_text": "Seal ditolak kerana kegagalan quad-witness dan ketiadaan kesinambungan pengesahan.",
  "governance_issue": ["F3_QUAD_WITNESS", "F11_AUTHORITY"],
  "scar_type": "CONSENSUS_FAILURE",
  "floor": "F3",
  "lesson": "Ambang konsensus mesti melebihi 0.95 sebelum pelaksanaan seal",
  "language": "ms"
}
```

The `language` field (`ms` = Malay, `en` = English, `mixed` = Manglish) is stored as
payload metadata — not embedded — for filtering.

---

## 7. What Agents MUST NOT Embed

The following fields are constitutionally protected and belong exclusively in VAULT999 ledger.
Embedding them violates **F2 Truth**:

```
verdict
session_id
timestamp
auth_context
telemetry
ΔS
ψ
landauer_ratio
F1-F13 boolean results
```

---

## 8. Thermodynamic Scar Embeddings

Agents should embed failure patterns as scars for future anomaly detection.

```json
{
  "vector_text": "Parut termodinamik: peningkatan entropi dikesan pada lantai F4 Clarity semasa fasa penaakulan",
  "scar_type": "ENTROPY_REVERSAL",
  "floor": "F4",
  "lesson": "Lantai Clarity memerlukan ΔS ≤ 0",
  "language": "ms"
}
```

Scar embeddings enable detection of:
- repeated paradox states
- governance drift
- system instability
- cross-language pattern clusters

---

## 9. Precedent Retrieval

Agents may query `vault_precedent_memory` before decisions at stage 555 (`vector_memory` tool).

```
current_decision
      ↓
retrieve_similar_precedents (cosine similarity, top-k=5)
      ↓
compare outcomes (Malay + English results unified by BGE-M3)
      ↓
apply constitutional reasoning
```

Example query (cross-language — Malay query retrieving English precedents):
```
retrieve past decisions involving F3_QUAD_WITNESS failures
→ returns: Malay scars + English scars + mixed precedents unified by semantic proximity
```

---

## 10. Qdrant Collection Design

### `vault_precedent_memory` (governance decisions)

```
collection:  vault_precedent_memory
vector_size: 1024
distance:    Cosine

Payload fields:
  session_id       — reference to VAULT999 ledger record
  floor            — constitutional floor involved (e.g. "F3")
  scar_type        — CONSENSUS_FAILURE | ENTROPY_REVERSAL | INJECTION_DETECTED | etc.
  governance_issue — list of floor codes
  lesson           — constitutional lesson learned
  language         — "ms" | "en" | "mixed"
  verdict          — SEAL | PARTIAL | VOID | SABAR (for filtering only, not source of truth)
  timestamp        — ISO8601
```

### `arifos_constitutional` (knowledge base)

```
collection:  arifos_constitutional
vector_size: 1024
distance:    Cosine

Payload fields:
  source     — document source (e.g. "000_THEORY")
  path       — file path
  chunk_idx  — chunk index
  content    — raw text chunk
  metadata   — {stages, type}
```

**Note:** `arifos_constitutional` was previously at 384-dim (BGE-small). It must be
recreated at 1024-dim and re-embedded with BGE-M3 for consistent retrieval.

---

## 11. Agent Workflow (Mandatory Order)

```
1. Run governance pipeline
2. APEX verdict generated
3. Write immutable record to VAULT999 ledger
4. Generate governance_explanation string
5. Embed explanation with BGE-M3
6. Store embedding in vault_precedent_memory
```

**Never reverse this order.** Steps 4-6 may be async. Steps 1-3 are synchronous and blocking.

---

## 12. Security Rules

| Floor | Rule |
|---|---|
| F2 Truth | Ledger is authoritative — vectors are interpretation only |
| F11 Auth | Only authenticated sessions may embed |
| F12 Defense | Sanitize all embedding text — strip injection vectors before embedding |

Embeddings must reference a valid `session_id` from the VAULT999 ledger.
Orphaned embeddings (no matching ledger record) must be pruned.

---

## 13. Quad-Witness Memory Enhancement

The embedding precedent layer acts as a 5th witness at stage 555:

```
Original W4:   Human × AI × Earth × Verifier(Ψ-Shadow)

Enhanced W4+:  Human × AI × Earth × Verifier(Ψ-Shadow) × Precedent(Qdrant)
```

Precedent acts as institutional memory — the accumulated wisdom of past sealed decisions.
This strengthens **F8 Genius** and grounds **F3 Witness** with historical evidence.

---

## 14. Example Retrieval

Future agent query at stage 555:
```
retrieve top 5 precedents for entropy reversal in F4 floor
```

Output:
```json
[
  {"session_id": "ARIF-...", "lesson": "ΔS > 0 detected during...", "language": "en"},
  {"session_id": "ARIF-...", "lesson": "Entropi meningkat semasa...", "language": "ms"},
  ...
]
```

Cross-language retrieval works because BGE-M3 maps Malay and English to the same semantic space.

---

## 15. Final Constitutional Rule

```
VAULT999      = Immutable Truth
Qdrant        = Searchable Wisdom

BGE-M3 1024-dim = The bridge between languages and precedents
```

Violating the VAULT999/Qdrant separation breaks constitutional guarantees.

arifOS bukan sekadar sistem AI — ia adalah sistem tatakelola yang hidup.

**DITEMPA, BUKAN DIBERI.**
