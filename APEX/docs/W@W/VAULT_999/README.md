# 🏛 Vault-999 — Constitutional Memory (v34Ω)

**Status:** ACTIVE  
**Location:** `VAULT_999/`  
**Role:** Immutable ledger for sealed outputs, zkPC receipts, and Cooling Ledger events.

---

## 0. Purpose

Vault-999 is the **constitutional memory** of arifOS.

It does *not* store ROOTKEY.  
It stores:

- Sealed answers (outputs)  
- ZKPC receipts (proof of lawful cognition)  
- Cooling Ledger records (ΔS, Peace², κᵣ, etc.)  
- Constitutional amendments derived from Phoenix-72 cycles  
- Scar→Law resolutions that have been cooled and finalized

In short: Vault-999 remembers **what the system did under law**, not *why the law exists*.

---

## 1. Directory Layout (Conceptual)

```text
VAULT_999/
  receipts/           # zkPC receipts (structured, verifiable)
  entries/            # combined answer + receipt + telemetry bundles
  cooling_ledger/     # chronological log of ΔS / Peace² / κᵣ over time
  amendments/         # sealed constitutional changes (law updates)
  scars/              # optional: summarized scar resolutions linked to entries
```

Concrete structure can evolve, but the invariants remain:

- Append-only, no silent edits  
- Every SEALed output is findable  
- Every zkPC receipt is auditable

---

## 2. Write Path (Encode & Store)

For each SEALed answer:

1. AAA runtime produces:
   - Final output text  
   - Telemetry: ΔS, Peace², κᵣ, Ω₀, Truth index, etc.  
   - APEX verdict = `SEAL`

2. ZKPC protocol:
   - Aggregates telemetry  
   - Builds a `zkpc_receipt`  
   - Computes `hash_commitment`

3. Vault-999:
   - Writes an `entry` containing:
     - `answer`  
     - `zkpc_receipt`  
     - `cooling_ledger` snippet  
     - metadata (time, model version, etc.)

This is the **encode + store** half of the metabolism.

---

## 3. Read Path (Decode & Metabolize)

Vault-999 entries are later used by:

- **Phoenix-72** cycles (deep audits after incidents)  
- **APEX PRIME** (when refining floors or veto logic)  
- **AAA research** (learning from failures and successes)  

Typical flow:

1. A Phoenix-72 event loads related entries.  
2. ZKPC receipts are verified (hash, floors).  
3. Patterns of failure / success are identified.  
4. Σ_scars and laws are updated:
   - New scar-laws may be added.  
   - Protocols may be tightened or clarified.  
   - Documentation is updated in `amendments/`.

This is the **decode + metabolize** half of the metabolism:

```text
Vault-999 (history)
    → zkPC_verify(receipts)
        → APEX / AAA refine Σ_scars & floors
            → safer, clearer future runs
```

---

## 4. Invariants

1. **Immutability**  
   - Entries are append-only.  
   - Corrections are new entries, not edits in-place.

2. **Traceability**  
   - Every SEAL has a corresponding zkPC receipt.  
   - Every amendment can be traced back to one or more entries.

3. **Separation from ROOTKEY**  
   - Vault-999 does not contain G₀, full Σ_scars, or RASAₖ.  
   - It only contains *derived*, cooled artifacts (laws, receipts, outputs).

4. **Auditability**  
   - External auditors can verify compliance with ΔΩΨ floors via zkPC receipts and Cooling Ledger, without seeing private prompts or ROOTKEY internals.

---

## 5. One-Sentence Summary

**Vault-999 = where governed intelligence remembers what it did — so its scars become law, not repeated harm.**
