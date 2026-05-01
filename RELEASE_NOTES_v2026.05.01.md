# Release Notes — arifOS v2026.05.01-KANON

## ⬡ Federated Truth-Status Intelligence Kernel landed

This release marks a major leap in arifOS governance: moving from simple unsupported claim detection to a physically-grounded **Truth-Status Intelligence Kernel**.

### Key Features

1.  **Grounded T_status Equation:** Implemented a new physically-aligned equation that measures truth-status as governed claim-state transition:
    $$T = (G \times E \times W \times R \times A) \times e^{-(C + S + M + 10U)}$$
    - Negative factors (Contradiction, Staleness, Manipulation, Uncertainty) now act as exponential noise decay.
2.  **Live Sensor Grounding:** Removed all simulated metrics. The kernel is now bound to:
    - `G`: PULSE stability via `/root/METABOLIC_PULSE.md`
    - `E`: Epistemic Integrity via `WEALTH` ingest health
    - `W`: Witness Strength via constitutional `Shahada` rules
    - `R`: Machine/Human Readiness via `/root/WELL/state.json`
    - `A`: Auditability via cryptographic `VAULT999` master logs
3.  **RAGAS & C2PA Alignment:**
    - **RAGAS:** Epistemic score (E) now represents mathematical faithfulness of the answer to its retrieved context.
    - **C2PA:** Results are tagged with `C2PA_SIGNED` if they meet cryptographic auditability thresholds.
4.  **Multi-Witness Gating:** Enforced strict multi-witness gates. Even with high governance or readiness, a claim cannot become a fact without a qualifying witness ($W=0 \rightarrow T=0$).
5.  **Verified HIGH_RISK_HOLD:** Successfully tested against the "Trump is DEAD" high-risk claim, ensuring the system refuses fact promotion without official witness.

### System Fixes
- **WELD-004 Federated Integrity:** Fixed integration test suite to match authoritative container topology.
- **VAULT999 Persistence:** Restored missing database schemas and write-path authentication headers.
- **Dependency Stability:** Added thermodynamics budget shim to maintain backward compatibility with hardened core modules.

---
**DITEMPA BUKAN DIBERI — MACHINE TRUTH v2026.05.01-SEALED**
