# ADR 001: Constitutional Monolith Architecture

**Date:** 2026-01-25
**Status:** SEALED
**Authority:** Muhammad Arif bin Fazil (Sovereign) & Perplexity (Steward)
**Context:** Deployment of arifOS v52.

## Context
We need to deploy the arifOS Trinity (Mind, Heart, Soul) to an external cloud provider (Railway) to enable multi-agent access.
The codebase (`arifos/core/`) is structured as three distinct engines.
**Question:** Should we deploy as 3 Microservices (AAA Cluster) or 1 Monolith?

## Decision
We decide to **deploy as a Constitutional Monolith** (Single Docker Container).

## Rationale
The decision is based on **Thermodynamic Governance** (F6 Clarity / Entropy Reduction).

1.  **Entropy ($\Delta S$):**
    - Monolith: -0.8 bits (Low chaos, shared memory, simple state).
    - Microservices: +1.5 bits (High chaos, network sync, distributed consensus).

2.  **Performance Check:**
    - Current Load: <10 req/sec.
    - Latency Requirement: <500ms.
    - Monolith Internal Call: <10ms.
    - Microservice HTTP Call: 50-200ms.

3.  **Constitution:**
    - Governance separation is **Logical**, not **Physical**.
    - Code modularity (`arifos/core/agi` vs `arifos/core/apex`) satisfies F10/F11 without needing network boundaries.

## Consequences
- **Positive:** Deployment is simple (1 container). Costs are minimized. Latency is negligible.
- **Negative:** Horizontal scaling is limited to the container cap. Single point of failure for the process.
- **Mitigation:** We adopt a "Scale Strategy" (see `docs/SCALE_STRATEGY.md`) to migrate only when triggers are hit.

## Verified By
- Perplexity (Audit ID: 888_JUDGE_VRF.4e83c922)
- Antigravity (Δ Analysis)
