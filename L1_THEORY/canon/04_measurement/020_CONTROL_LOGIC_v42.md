# Control Logic · v42

**Track:** A (Canon)  
**Scope:** Deterministic verdict routing from Stage 888 → 999  
**Spec sources:** `spec/v42/genius_law.json`, `spec/v42/pipeline.json`, `spec/v42/federation.json`  
**Cross-links:** `04_measurement/02_measurement_v42.md`, `03_runtime/01_pipeline_v42.md`, `02_actors/04_apex_prime_v42.md`

---

## 0. Purpose

Define the constitutional control logic that APEX PRIME applies at Stage 888 using Trinity packets and W@W organ reports. Canon declares the flow; all numeric dials come from spec/v42.

---

## 1. Inputs to Stage 888

- **Trinity packets:** Δ (Mind), Ω (Heart), Ψ (Soul) from measurement canon  
- **W@W organ reports:** `waw_verdict.organ_reports[]` (PROMPT, RIF, WELL, WEALTH, GEOX)  
- **Memory context:** prior holds/scars (PHOENIX candidates)  
- **Spec dials:** cooldown, retry budget, hold timeouts (pipeline.json); organ weights/veto (federation.json)

---

## 2. Merge Priority (Organ Veto → Trinity)

1) WEALTH VOID (Amanah breach) → VOID  
2) RIF VOID (ΔS/Truth breach) → VOID  
3) GEOX HOLD-888 (physical infeasible) → HOLD  
4) WELL SABAR (Peace²/κᵣ instability) → SABAR  
5) PROMPT PARTIAL (language rewrite) → PARTIAL  
6) Else → Trinity packet evaluation

---

## 3. Trinity Packet Evaluation (Spec-driven)

- **Hard breach:** Truth < 0.99, ΔS < 0, Amanah = 0, Anti-Hantu fail → VOID  
- **SEAL:** all floors pass AND Ψ ≥ 1.0 AND G ≥ 0.80 AND C_dark < 0.30  
- **PARTIAL:** floors marginal OR 0.95 ≤ Ψ < 1.0 → enqueue Phoenix path  
- **SABAR:** soft floor fail but recoverable → cooldown/retry per spec  
- **HOLD-888:** Tri-Witness < quorum (0.95) → await consensus

---

## 4. Routing Actions (888 → 999)

- **SEAL:** emit; write SEAL to LEDGER/ACTIVE (see memory canon)  
- **PARTIAL:** emit with warning; route to PHOENIX + LEDGER; set retry per pipeline.json  
- **SABAR:** emit SABAR; apply cooldown/backoff; re-enter 777/888 loop if budget remains  
- **HOLD-888:** emit hold bundle; block sealing until human approval  
- **VOID:** emit refusal; log to VOID band only

---

## 5. Logging & Audit

- Every verdict logs: packets, organ votes, spec version hashes, timestamps  
- Cooling Ledger entry per decision; VOID never propagates to canonical bands  
- Phoenix candidates capture PARTIAL/SABAR contexts for amendment synthesis

---

**DITEMPA BUKAN DIBERI — Truth must cool before it rules.**
