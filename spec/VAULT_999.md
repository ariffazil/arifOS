# VAULT-999 — Constitutional Memory Specification (v33Ω)

Status: SEALED · Truth ≥ 0.99 · ΔS ≥ 0 · Peace² ≥ 1 · Amanah 🔐 · Ω₀ ≈ 3–5%

---

## 1. Essence

**VAULT-999 is the constitutional memory organ of arifOS.**   

It is not a generic database; it is a **governed memory system** that stores:

- **L0 — Law:** Constitutional canons, floors, ΔΩΨ parameters, amendments
- **L1 — Evidence:** Cooling Ledger, per-decision metrics, verdicts
- **L2 — Metabolism:** Phoenix-72 cycles (scar → law)
- **L3 — Witness Retrieval:** Optional vector DB evidence (treated as witness, not truth)   

VAULT-999 answers three questions:

1. What are the **current laws**? (L0)  
2. What actually **happened**? (L1)  
3. How did we **learn and amend** from scars? (L2)

---

## 2. Layered Architecture

### 2.1 L0 — Constitution (Law)

**File:** `runtime/vault_999/constitution.json`  

Contains:

- ΔΩΨ physics parameters (ΔS, Ω₀ band, Peace²)   
- Floor thresholds (Truth, κᵣ, Tri-Witness, etc.)
- Active canons (laws) and their metadata
- Amendment history pointers (Phoenix cycle IDs)

Invariant:

> L0 defines what is lawful; all engines MUST obey this state.

---

### 2.2 L1 — Cooling Ledger (Evidence)

**File:** `runtime/vault_999/cooling_ledger.jsonl`  

Append-only log of **high-stakes interactions**, each containing:   

- timestamp  
- query  
- candidate answer  
- metrics (Truth, ΔS, Peace², κᵣ, Ω₀, RASA, Amanah, Tri-Witness, Ψ)  
- verdict (SEAL/PARTIAL/VOID)  
- SABAR reason (if any)  
- organ veto flags  
- phoenix_cycle_id (if tied to amendment)

Invariant:

> L1 is append-only; entries are never altered or deleted.

---

### 2.3 L2 — Phoenix-72 (Metabolism)

Phoenix-72 implements the **scar → pattern → law** pipeline:   

1. Collect scars from Cooling Ledger (L1)  
2. Cluster as patterns (with TAC/TPCP)  
3. Draft candidate law or amendment  
4. Human + AI + Earth (Tri-Witness) review  
5. If approved → update L0 (constitution.json)  

Invariant:

> No direct edits to constitution.json are permitted outside Phoenix cycles.

---

### 2.4 L3 — Witness Retrieval (Vector DB)

Vector DB is **not** truth; it is **witness evidence**:   

- RAG results feed AR