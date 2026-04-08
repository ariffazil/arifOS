---
type: Concept
tags: [architecture, deployment, horizon, vps, gateway, infrastructure]
sources: [server.py, server_horizon.py]
last_sync: 2026-04-08
confidence: 1.0
---

# Concept: Deployment Architecture

The arifOS architecture is bifurcated into two distinct operational modes to balance performance, access, and sovereign control. This is the material implementation of the **Trinity / Air Gap** principle.

## 1. Horizon Mode (The Gateway Proxy)

**Horizon Mode** is a lightweight, high-availability proxy layer (typically running as `server_horizon.py` or behind a REST gateway).

- Role: Access Control & Translation.
- Function: Maps external REST/Webhook calls to internal MCP tool invocations.
- Constraints:
  - No full Constitutional Kernel (CCC) execution.
  - Uses `HORIZON_TO_V2_MAP` to translate legacy request formats to modern arifOS v2.
  - Low latency, high throughput.

- Analogy: The "Eyes and Ears" of the system.

## 2. VPS Mode (The Full Execution Kernel)

**VPS Mode** is the complete, sovereign instance of the arifOS kernel (running as the full `arifosmcp` stack).

- Role: Governance & Execution.
- Function: Executes the full Metabolic Pipeline (000-999).
- Constraints:
  - Strict Floor Enforcement (F1-F13).
  - Hard-stop verification via the `GovernanceEnforcer`.
  - Vault999 immutable sealing (PostgreSQL + Filesystem).

- Analogy: The "Brain and Heart" of the system.

---

## The Air Gap Bridge (BBB)

Communication between the Horizon and the VPS happens via a secure, audited protocol. In most deployments:

1. **Horizon** receives an "Intent."
2. **Horizon** selects the correct v2 tool (e.g., `arifos_init`).
3. **VPS Kernel** performs the actual "Metabolism."
4. **Horizon** returns the "Cooled Intelligence" to the user.

## Component Map

| Feature | Horizon Mode | VPS Mode |
| :--- | :--- | :--- |
| **Tool Map** | `HORIZON_TO_V2_MAP` (Active) | Canonical v2 Surface |
| **Safety Net** | Basic Rate Limiting | `GlobalPanicMiddleware` |
| **Enforcement** | Identity Verification | Full `GovernanceEnforcer` |
| **Persistence** | Session Cache (Redis) | Immutable Ledger (Postgres/File) |

---

## Related

- [[What-is-arifOS]]
- [[Concept_Architecture]]
- [[Concept_Governance_Enforcer]]
