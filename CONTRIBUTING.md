# Contributing to ArifOS

ArifOS is a **constitutional governance spec**.  
Certain parts are **frozen** by design.

---

## 1. Constitutional vs Non-Constitutional Files

### Constitutional Artifacts (Do NOT change floors/physics lightly)

- `README.md` (ΔΩΨ, AAA, W@W, floors, pipeline)
- `spec/arifos_runtime_v33Omega.yaml`
- `spec/APEX_PRIME.yaml`
- `docs/WAW_OVERVIEW.md`
- `docs/governance/DECISION_2025-11-16_BASECAMP.md`

You may:

- Fix typos and formatting  
- Improve wording for clarity (without changing meaning)

You may **not** (without version bump + public log):

- Change floor thresholds  
- Change ΔΩΨ laws  
- Change AAA roles  
- Add/remove W@W organs  
- Change 000–999 semantics  

### Implementation Artifacts (Safe to evolve)

- `examples/`  
- `spec/cooling_ledger.schema.json` (may add non-breaking fields)  
- `docs/diagrams.md`  
- `arifos_core/` code  

---

## 2. Governance Rules for Changing the Constitution

If you believe the physics or floors need to change:

1. Open an issue labeled `governance`  
2. Propose a version bump (e.g. v34Δ)  
3. Document in `CHANGELOG.md`  
4. Wait for explicit acceptance by steward(s)  

---

## 3. Using "Powered by ArifOS"

To claim **"Powered by ArifOS"**, you must:

- Implement all 8 floors  
- Have 000–999 style pipeline with VOID default  
- Record Cooling Ledger entries for sealed decisions  
- Implement SABAR and Tri-Witness  
- Respect AAA & W@W role separation  

Otherwise use: **"Inspired by ArifOS"**.

---

See [LICENSE](LICENSE) for legal terms.
