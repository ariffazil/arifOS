# arifOS v45 Architecture (Sovereign Witness)

**Status:** ACTIVE | **Version:** v45.0.0

---

## 1. High-Level Diagram

```mermaid
graph TD
    User([User / Agent]) --> L5_CLI[L5_CLI / Tools]
    L5_CLI --> Pipeline[arifos_core/system/pipeline.py]
    
    subgraph "Track C: arifos_core (Runtime)"
        Pipeline --> Judges[system/apex_prime.py]
        Judges --> Gov[governance/Ledger & FAG]
        Judges --> Metrics[enforcement/Metrics]
        
        Pipeline --> Adapters[adapters/ (Providers)]
        Adapters --> EXT_LLM[External LLMs (Claude/Gemini/SEALION)]
    end
    
    subgraph "Track A: L1_THEORY (Law)"
        Canon[canon/ (Read-Only Rules)] -.-> Judges
    end
    
    subgraph "Track B: Spec (Config)"
        Spec[spec/v45/ (Tunable Thresholds)] -.-> Metrics
    end
    
    Gov --> CoolingLedger[(Cooling Ledger)]
    Gov --> Vault999[(Vault 999)]
```

## 2. Core Modules

### A. System (`arifos_core/system/`)
The metabolic engine.
- **`pipeline.py`**: The 000->999 stage runner.
- **`apex_prime.py`**: The Judiciary (APEX Engine) that renders verdicts.

### B. Governance (`arifos_core/governance/`)
The enforcement layer.
- **`fag.py`**: File Access Governance (Read-Only filesystem checks).
- **`ledger.py`**: Merkle-proofed audit trail logging.

### C. Enforcement (`arifos_core/enforcement/`)
The measurement layer.
- **`metrics.py`**: Thermodynamics (ΔS, Peace², κᵣ).
- **`genius_metrics.py`**: Composite scores (Psychohistory, C_dark).

### D. Adapters (`arifos_core/adapters/`)
Concrete provider implementations.
- `llm_claude.py`
- `llm_sealion.py`
- `llm_openai.py`

### E. Integration (`arifos_core/integration/`)
Internal ports and abstract interfaces.
- Wiring for memory, evaluation suites, and experimental bridges.

## 3. Directory Layout Standards

See `docs/NAMING_CONVENTION_v45.md` for strict file placement rules.
