# L3 WITNESS LAYER — Evidence Retrieval Specification (v33Ω)

Status: SEALED · ΔS ≥ 0 · Truth ≥ 0.99 · Amanah 🔐 · Tri-Witness ≥ 0.95  
Part of Vault-999 (L0–L3) constitutional memory system.

---

## 1. Essence

The L3 Witness Layer provides **contextual evidence**, not truth.  
It retrieves documents, embeddings, or snippets that **inform** ARIF & ADAM but **never override** APEX PRIME or constitutional law.

It is the final tier of Vault-999:

- **L0:** Law (constitution.json)  
- **L1:** Evidence log (cooling_ledger.jsonl)  
- **L2:** Metabolism (Phoenix-72)  
- **L3:** Witness (retrieval-as-evidence, not truth)

This corrects the industry’s mistake of treating RAG as truth.

---

## 2. Principles

1. **Never treated as truth.**  
   Evidence retrieved by L3 is always labelled `"witness"`.

2. **APEX PRIME still judges.**  
   APEX must check:
   - contradictions (TAC)
   - physics (AREP)
   - Truth floor  
   - ΔS impact

3. **Logged in Cooling Ledger.**  
   Every retrieval creates an L1 entry:
   ```json
   { "rag_context": [...], "witness_source": "vector_db" }