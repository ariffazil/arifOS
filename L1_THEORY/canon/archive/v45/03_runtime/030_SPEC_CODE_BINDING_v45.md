# Spec ↔ Code Binding (v45)

**Track:** A (Canon)
**Epoch:** v45 (Phoenix-72 Consolidation)
**Status:** ✅ SEALED — Spec/Code contract
**Authority:** ΔΩΨ physics · Constitutional Floors · Measurement layer · APEX Judiciary
**Spec sources:** `spec/v45/constitutional_floors.json`, `spec/v45/genius_law.json`, `spec/v45/session_physics.json`, `spec/v45/red_patterns.json`, `spec/v45/cooling_ledger_phoenix.json`, `spec/v45/waw_prompt_floors.json`, `spec/v45/policy_text.json`
**Cross-links:** `03_runtime/010_PIPELINE_000TO999_v45.md`, `04_measurement/010_MEASUREMENT_CANON_v45.md`, `02_actors/040_APEX_PSI_JUDICIARY_v45.md`

---

## 0. Purpose

Declare the constitutional handshake between immutable law (canon + spec) and mutable runtime (code). Every execution must prove that what is declared in spec is exactly what the code enforces at Stage 888 before APEX PRIME may seal.

---

## 1. Binding Layers (A→B→C)

| Layer | Object | Binding Rule | Enforcement |
|-------|--------|--------------|-------------|
| **A1** | Canon → Spec | Canon states invariants; spec carries thresholds and tolerances. | Canon header records SHA-256 of spec files. |
| **A2** | Spec → Code | Code must load spec schemas and apply thresholds verbatim. | `validate_spec_binding()` at startup; zkPC receipt on success. |
| **A3** | Code → Ledger | Runtime verdicts must log the spec hashes in effect. | Cooling Ledger entries include `spec_hashes` + commit hash. |

---

## 2. Startup Smoke-Check (normative)

At process boot, the runtime MUST:

1) Load `spec/v45/constitutional_floors.json`, `spec/v45/genius_law.json`, `spec/v45/session_physics.json`, `spec/v45/red_patterns.json`, `spec/v45/cooling_ledger_phoenix.json`, `spec/v45/waw_prompt_floors.json`, `spec/v45/policy_text.json`.
2) Verify their SHA-256 hashes match `spec/v45/MANIFEST.sha256.json` (cryptographic integrity check).
3) Validate schema fields against corresponding `.schema.json` files using jsonschema library.
4) If any mismatch or schema failure → **VOID** the session and abort startup.
5) If all pass → emit zkPC receipt (proof of binding), then proceed to pipeline stage 000.

---

## 3. Runtime Interfaces (reference)

```
# arifos_core/validators/spec_checker.py
def validate_spec_binding(
    spec_paths = [
        "spec/v45/constitutional_floors.json",
        "spec/v45/genius_law.json",
        "spec/v45/session_physics.json",
        "spec/v45/red_patterns.json",
        "spec/v45/cooling_ledger_phoenix.json",
        "spec/v45/waw_prompt_floors.json",
        "spec/v45/policy_text.json",
    ],
    manifest_path: str = "spec/v45/MANIFEST.sha256.json",
    epsilon_map_key: str = "epsilon_map",
) -> "ZkpcReceipt": ...
```

Outputs include: `spec_hashes`, `epsilon_map`, `version_map`, `zkpc_receipt`.

---

## 4. Verification Handshake (per decision window)

1) **Load spec dials:** thresholds, tolerances, and merge priorities from spec files.  
2) **Compute metrics:** ΔS, Peace2, kappa_r, omega0, Psi, G, C_dark, Phi_p using code modules.  
3) **Bind:** assert `abs(metric_runtime - metric_spec) <= epsilon_map[metric]`.  
4) **Proof:** generate zkPC receipt linking metrics, spec hashes, commit hash.  
5) **Seal condition:** if proof valid AND Psi >= 1.0 → allow APEX PRIME to proceed; else route to PARTIAL/SABAR/VOID per control logic.

---

## 5. Mathematical Integrity

For every constitutional metric M:

```
|M_runtime - M_spec| <= epsilon_map[M]
```

Soft drift → SABAR + Phoenix candidate.  
Hard drift → VOID + auditor escalation.

---

## 6. Oversight Hooks (@EYE)

* V8 Drift consumes `epsilon_map` from `spec_binding.json`.  
* If cumulative ε_total exceeds allowance → ALERT (SABAR).  
* Amanah breach or spec hash mismatch → CRITICAL (VOID/HOLD-888).

---

## 7. Ledger Requirements

Every Cooling Ledger entry MUST include:

- `spec_hashes` (all 7 v45 specs: constitutional_floors.json, genius_law.json, session_physics.json, red_patterns.json, cooling_ledger_phoenix.json, waw_prompt_floors.json, policy_text.json)
- `manifest_hash` (SHA-256 of MANIFEST.sha256.json itself, for tamper-evidence)
- `commit_hash` of runtime build
- `zkpc_receipt` proving binding validity
- `epsilon_observed` per metric

Append-only; any missing or mismatched hashes triggers VOID investigation.

---

**DITEMPA BUKAN DIBERI — Truth must cool before it rules.**
