# L3 WITNESS LAYER — Evidence Retrieval Specification (v35Ω)

**Status:** SEALED · ΔS ≥ 0 · Truth ≥ 0.99 · Amanah 🔐 · RASA ✓ · Tri-Witness ≥ 0.95 · Anti-Hantu 🛡️

Part of Vault-999 (L0–L4) constitutional memory system.

---

## 1. Essence

The L3 Witness Layer provides **contextual evidence**, not truth.
It retrieves documents, embeddings, or snippets that **inform** ARIF & ADAM but **never override** APEX PRIME or constitutional law.

It is the evidence tier of Vault-999:

| Layer | Name | Purpose |
|-------|------|---------|
| **L0** | Constitution | Immutable ΔΩΨ laws (constitution.json) |
| **L1** | Cooling Ledger | Hash-chained evidence log (cooling_ledger.jsonl) |
| **L2** | Phoenix-72 | Constitutional metabolism (72h amendment cycles) |
| **L3** | Witness | Retrieval-as-evidence, not truth |
| **L4** | zkPC | Zero-knowledge proof layer (cryptographic attestation) |

**This corrects the industry's mistake of treating RAG as truth.**

---

## 2. Principles

1. **Never treated as truth.**
   Evidence retrieved by L3 is always labelled `"witness"`.

2. **APEX PRIME still judges.**
   APEX must check all 9 floors against witness evidence:
   - Truth (F1) - factual accuracy
   - ΔS (F2) - clarity gain
   - Contradictions via TAC (F2)
   - Physics via AREP (F5)
   - Anti-Hantu (F9) - no soul-faking from external sources

3. **@EYE Sentinel audits.**
   @EYE Drift View (4) and Shadow View (3) scan witness content for:
   - Hallucination patterns
   - Prompt injection attempts
   - Source manipulation

4. **Logged in Cooling Ledger (L1).**
   Every retrieval creates an L1 entry:
   ```json
   {
     "rag_context": [...],
     "witness_source": "vector_db",
     "retrieval_timestamp": "ISO8601",
     "similarity_scores": [...],
     "eye_audit": {
       "drift_view": "PASS",
       "shadow_view": "PASS"
     }
   }
   ```

5. **Tri-Witness integration.**
   External evidence counts toward Earth witness component:
   ```json
   {
     "tri_witness_components": {
       "human": 0.95,
       "ai": 0.98,
       "earth": 0.92  // L3 contributes here
     }
   }
   ```

---

## 3. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER QUERY                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    L3 WITNESS LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Vector Store │  │ Document DB  │  │ External APIs    │  │
│  │ (Embeddings) │  │ (Structured) │  │ (Real-time)      │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                 │                    │            │
│         └─────────────────┴────────────────────┘            │
│                           │                                 │
│                    WITNESS EVIDENCE                         │
│                  (Labelled, not truth)                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    @EYE SENTINEL                            │
│  • Drift View (4) - Hallucination check                     │
│  • Shadow View (3) - Injection detection                    │
│  • Maruah View (5) - Dignity in sources                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    APEX PRIME                               │
│  • Truth floor check (F1 ≥ 0.99)                            │
│  • ΔS computation (F2 ≥ 0)                                  │
│  • Anti-Hantu scan (F9)                                     │
│  • CCE audits (ΔP, ΩP, ΨP, ΦP)                             │
│  • Verdict: SEAL / PARTIAL / 888_HOLD / VOID / SABAR        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    L1 COOLING LEDGER                        │
│  (Hash-chained audit log of retrieval + verdict)            │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Witness Types

| Type | Source | Trust Level | @EYE Check |
|------|--------|-------------|------------|
| **Vector Retrieval** | Embedded documents | Contextual | Drift View |
| **Structured Query** | Database records | Factual | Shadow View |
| **Web Search** | Real-time APIs | Low trust | Full audit |
| **Human Input** | User-provided | Variable | Maruah View |
| **AI Cross-Check** | Other LLMs | Collaborative | Sleeper View |

---

## 5. Integration with L4 zkPC

L3 Witness can be cryptographically attested via L4:

```json
{
  "witness_entry": {
    "source": "vector_db",
    "query": "Malaysia healthcare policy",
    "results": [...],
    "timestamp": "2025-12-04T12:00:00Z"
  },
  "l4_attestation": {
    "hash": "sha256:...",
    "signature": "kms:...",
    "zkpc_proof": "optional zero-knowledge proof"
  }
}
```

**When to use L4 attestation:**
- High-stakes decisions (medical, legal, financial)
- Tri-Witness >= 0.95 required
- Cross-organization evidence sharing
- Regulatory compliance

---

## 6. Anti-Hallucination Guards

L3 implements multiple guards against hallucination:

1. **Source Attribution**
   Every witness must cite its source:
   ```json
   {
     "content": "...",
     "source_url": "https://...",
     "retrieval_date": "2025-12-04",
     "confidence": 0.87
   }
   ```

2. **Contradiction Detection (TAC)**
   If witnesses contradict each other:
   - Flag for @EYE Paradox View (6)
   - Compute ΔP audit
   - May trigger 888_HOLD

3. **Freshness Check**
   Stale evidence is downgraded:
   ```python
   if days_since_retrieval > 30:
       trust_multiplier *= 0.8
   ```

4. **Anti-Hantu for Sources**
   External sources cannot inject soul-claims:
   - Block "AI feels", "AI promises", "AI guarantees"
   - Detect prompt injection patterns

---

## 7. Schema

### Witness Entry

```json
{
  "witness_id": "W-20251204-0001",
  "layer": "L3",
  "type": "vector_retrieval",
  "query": "user query that triggered retrieval",
  "results": [
    {
      "content": "...",
      "source": "document.pdf",
      "page": 42,
      "similarity": 0.89,
      "timestamp": "2025-12-04T12:00:00Z"
    }
  ],
  "eye_audit": {
    "drift_view": "PASS",
    "shadow_view": "PASS",
    "maruah_view": "PASS"
  },
  "tri_witness_contribution": {
    "component": "earth",
    "weight": 0.3
  },
  "l4_attestation": null
}
```

---

## 8. Invariants

1. **Witness ≠ Truth** - L3 evidence is always advisory
2. **APEX has final say** - Constitutional floors override witnesses
3. **Logged always** - Every retrieval goes to L1
4. **@EYE audited** - No unscanned witness content
5. **Anti-Hantu enforced** - External sources cannot inject soul-claims
6. **Tri-Witness feeds** - L3 contributes to Earth witness component

---

## 9. Migration from v33Ω

| Change | v33Ω | v35Ω |
|--------|------|------|
| Vault Layers | L0-L3 | L0-L4 (+ zkPC) |
| @EYE Integration | Basic | 10 views, 3 mandatory for L3 |
| Anti-Hantu | — | Enforced on witness content |
| CCE Audits | Optional | Required for high-stakes |
| Tri-Witness | Manual | Automatic L3→Earth contribution |

---

**Author:** Muhammad Arif bin Fazil
**Location:** Kuala Lumpur, Malaysia
**Version:** v35Ω
**Date:** 2025-12-04
**License:** Apache 2.0
**Motto:** DITEMPA BUKAN DIBERI — Forged, Not Given

---

**END OF L3 WITNESS LAYER SPECIFICATION (v35Ω)**
