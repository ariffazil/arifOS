# Real Intelligence Kernel (RIK) — Core Invariants

**Classification:** Constitutional Architecture
**Status:** ACTIVE
**Seal:** VAULT999

> "No GK → not an arifOS kernel."

## 1. Sovereignty Invariants
- **F13 Veto:** Human veto (F13) is mandatory on all irreversible or high-impact operations.
- **No Autonomous Runaways:** There shall be no closed-loop autonomous behavior. The Sovereign Interface (SI) must retain the physical/logical capability to stop the Execution Engine (EE) at any moment.

## 2. Temporal Invariants
- **Sessions vs. Epochs:** Shell sessions may be transient. Meaningful actions, however, must attach to an immutable Epoch.
- **The 999 SEAL:** Every Epoch must end with a canonical 999 SEAL JSON payload, taking the exact shape:
  `(epoch, dS, peace2, kappar, shadow, confidence, psile, verdict, witness, qdf)`.

## 3. Planning Invariants
- **No Direct Execution:** The pipeline `INTENT → EXECUTION` is forbidden. It must strictly flow as `INTENT → PLAN → EXECUTION`.
- **First-Class Plans:** Plans are first-class, persisted entities with a rigorous lifecycle: `DRAFT → PENDING → APPROVED → IN_EXECUTION → COMPLETED/ABORTED`.

## 4. Governance Kernel (GK) Invariant
- **The Absolute Hub:** All organs must call the Governance Kernel (GK) to classify operations (reversible vs. irreversible), check Floors, and emit telemetry. An architecture without this central GK checkpoint is mathematically not an arifOS kernel.
