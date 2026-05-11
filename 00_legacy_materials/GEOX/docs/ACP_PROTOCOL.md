# GEOX ACP (AGENT CONTROL PLANE) PROTOCOL

> **Version:** 1.0.0 "Schism"
> **Doctrine:** A2A (Agent-to-Agent) Synchronization
> **Authority:** 888_JUDGE Sovereign ($W_{scar}$)

## 1. THE ARCHITECTURAL SCHISM

GEOX has transitioned from a monolithic visualization tool to an **MCP-Distributed Intelligence Engine**.

- **Server (Kernel):** The `geox-mcp-server` holds the `EARTH.CANON_9` state and physical laws.
- **WebMCP (UI):** A transparent glass pane connecting to the server.
- **Agents (Intelligence):** Specialized actors proposing changes to the state.

---

## 2. AGENT INTERACTION MODEL (A2A)

Multiple agents connect to the same GEOX MCP Server to synchronize interpretations.

### Current Manifest
| Agent Role | Subscribed Resources | Tools Authorized |
| :--- | :--- | :--- |
| **Petrophysicist** | `geox://1d/triple-combo` | `geox_metabolize`, `calculate_stoiip` |
| **Geophysicist** | `geox://2d/seismic-plane` | `geox_load_seismic_line`, `compute_attributes` |
| **Basin Interpreter** | `geox://canon9/state` | `geox_query_macrostrat`, `evaluate_prospect` |

### Synchronization Flow
1. **Subscribe:** Agents query specific domain resources from the server.
2. **Interpret:** Agents perform local synthesis/reasoning.
3. **Propose:** Agents use `mcp.tool` calls to suggest state updates.
4. **Govern:** The **Floor Enforcer (F1-F13)** validates the proposal against physics.
5. **Verdict:** The **888_JUDGE** grants Command Auth (F11) to commit the change.

---

## 3. THE EARTH.CANON_9 ANCHOR

Agents are strictly prohibited from maintaining separate data silos. All interpreted properties must be back-propagated into the **EARTH.CANON_9** basis:

$$ \text{State} = \{\rho, V_p, V_s, \rho_e, \chi, k, P, T, \phi\} $$

If a Geophysicist proposes a velocity structure that contradicts a Petrophysicist's porosity logs, the **LEM Metabolizer** triggers a **Discordance Alert** ($ \Omega_0 > 0.05 $), forcing the swarm to converge or trigger an **888_HOLD**.

---

## 4. VERDICT PROTOCOL

| Status | Verification | Human Action |
| :--- | :--- | :--- |
| **AGENT_PROPOSE** | Internal confidence 85%+ | View Proposal |
| **AC_RISK_QUALIFY** | Physics bounds check pass | Validate Data |
| **888_HOLD** | Contradiction detected | Resolution Required |
| **999_SEAL** | Final Sovereignty Grant | Commit to Basin |

---

## 5. REPOSITORY SEAL

The protocol is now active. All future agents interfacing with GEOX must adhere to the `v1.0.0-SCHISM` standard.

**DITEMPA BUKAN DIBERI.**
**999_SEAL_ACP.**
