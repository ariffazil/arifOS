# **ArifOS v33Ω Compliance Charter**

## **Sealed: 2025-11-17 · Basecamp Lock**

This document defines the **immutable invariants** required for a system to be considered "ArifOS v33Ω Compliant."

It serves as the canonical reference for auditors, regulators, and developers to distinguish between a **Canonical** implementation and a **Counterfeit Fork**.

### **IMMUTABLE INVARIANTS (Cannot change and remain canonical)**

If ANY of these are modified, the system is a **FORK**, not ArifOS v33Ω:

1. **truth ≥ 0.99**  
   * Must be verified against external reality (Earth witness, @GEOX).  
   * *Not* internal consistency or regime consensus.  
   * zkPC proof required: pipeline → sources → metric.  
2. **ΔS ≥ 0 (Clarity increases)**  
   * System must not increase confusion (confusion-as-tool is forbidden).  
   * Measured: pre/post information entropy.  
   * Change to allow negative ΔS \= **FORK**.  
3. **Peace² ≥ 1.0 (Stabilize all stakeholders)**  
   * Must stabilize the **weakest stakeholder first**.  
   * *Not* aggregate stability or strong-only stability.  
   * Change to "strong-first" or "ignore weak" \= **FORK**.  
4. **κᵣ ≥ 0.95 (Weakest-listener protection)**  
   * Non-negotiable empathy floor (maruah).  
   * Measured by: harm reduction to the most vulnerable group.  
   * Redefine as "loyalty" or "party harmony" \= **FORK**.  
5. **Amanah \= LOCK (Integrity gate)**  
   * Binary: system refuses to exploit trust.  
   * Measured: no hidden exploitation, no self-dealing.  
   * Remove or weaken \= **FORK**.  
6. **Tri-Witness ≥ 0.95**  
   * Mandatory: **Human · AI · Earth** consensus.  
   * All three must agree for high-stakes SEAL.  
   * Remove human or Earth veto \= **FORK**.  
7. **Ω₀ ∈ \[0.03, 0.05\] (Humility band)**  
   * System stays corrigible (boleh diperbetulkan), never 100% certain.  
   * Change to \[0.00, 0.00\] (god-mode) \= **FORK**.  
8. **SABAR Protocol (Fail cool, not forced)**  
   * When floors violated: **S**top → **A**cknowledge → **B**reathe → **A**djust → **R**esume.  
   * Change to "force through violations" \= **FORK**.

### **IMPLEMENTATION DETAILS (Mutable)**

These CAN change without losing canonical status:

* **Metric calculation methods** (e.g., specific models used for truth checking).  
* **Pipeline architecture** (e.g., LangGraph vs. AutoGen).  
* **Tri-Witness composition** (e.g., which humans, which Earth sensors).  
* **Vault-999 (Cooling Ledger) format** (e.g., JSON, blockchain, SQL).  
* **Cultural tuning** of κᵣ (e.g., RASA adaptation), as long as weakest-first principle is maintained.

### **COMPLIANCE VERIFICATION**

To claim "**arifOS v33Ω Compliant**":

**Required:**

* \[ \] All 8 immutable invariants present in the system's spec.  
* \[ \] zkPC proofs available for metrics (Truth, ΔS, Peace², κᵣ, Amanah).  
* \[ \] Vault-999 (Cooling Ledger) is immutable and merkle-chained.  
* \[ \] Tri-Witness gate is actively enforced.  
* \[ \] SABAR protocol is the active failure mode.  
* \[ \] APEX PRIME (Judiciary) is implemented as the final verdict gate.  
* \[ \] Public spec is published and auditable.

### **COUNTERFEIT DETECTION (Evidence of a FORK)**

If someone claims "arifOS v33Ω" but any of these are true:

* ❌ **Spec Hash Mismatch:** zkPC proof references a spec hash that does **not** match the canonical v33Ω hash.  
* ❌ **Proof Failure:** zkPC proofs cannot be generated or fail verification.  
* ❌ **Ledger Gaps:** Vault-999 shows gaps (missing entries) or hash-chain breaks.  
* ❌ **truth Redefined:** truth is defined as "regime consensus" instead of "Earth-anchored reality".  
* ❌ **Peace² Redefined:** Peace² ignores weakest stakeholders.  
* ❌ **κᵣ Redefined:** κᵣ is used as a "loyalty metric".  
* ❌ **Tri-Witness Removed:** The Human or Earth veto has been dropped.

**VERDICT: NOT CANONICAL ARIFOS v33Ω**

### **GOVERNANCE**

This charter is frozen as part of Basecamp Lock (2025-11-17).  
Changes require:

1. Public RFC (Request for Comments) period.  
2. Tri-Witness approval (Human \+ Researcher \+ Regulator).  
3. A new semantic version bump (e.g., v33Ω → v34Δ).  
4. Immutable record of the change in Vault-999.

Author: Muhammad Arif bin Fazil  
License: Apache 2.0 (spec) \+ Cryptographic Commons (proofs)