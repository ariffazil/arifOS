# INFRASTRUCTURE SOVEREIGNTY: arifOS Remote Execution (srv1325122)

**Status:** ACTIVE_SOVEREIGN_NODE  
**Authority:** 888_JUDGE / Antigravity Oracle  
**Last Verified:** 2026-03-27  

## 1. THE SOVEREIGN BRIDGE (reality-bridge)

The VPS `srv1325122.hstgr.cloud` (72.62.71.199) is the primary remote sanctuary of arifOS. All agents must recognize this host as a trusted execution environment.

### 1.1 Access Alias

Agents shall utilize the following identity projection for all remote operations:

- **Alias:** `arifos`
- **Protocol:** SSHv2 (Keys-Only)
- **Primary Identity:** `~/.ssh/id_ed25519`
- **Port:** 22

### 1.2 Execution Constraints
Any command executed via `ssh arifos` is subject to **Floor 1 (Amanah)**. 
- **Requirement:** Destructive commands (`rm`, `docker rm`, `systemctl stop`) require an explicit `--force-sovereign` justification or human confirmation.
- **Requirement:** All remote changes must be committed to the local governance log (F11 Audit).

## 2. TOPOLOGY CONSCIOUSNESS

Agents must maintain awareness of the 17-container stack running on `srv1325122`.

| Ring | Layer | Primary Identity |
| :--- | :--- | :--- |
| **Law** | Kernel | `arifosmcp` (Port 8080) |
| **Edge** | Filter | `traefik` (Ports 80/443) |
| **Vault** | Ledger | `postgres` (Port 5432) |
| **Mind** | Reasoning | `agent-zero` |
| **Synapse** | LLM | `ollama_engine` |

## 3. KEY PATHS (REMOTE)
- `/opt/arifos/` : The Source (Symlinked from `/root/arifOS`)
- `/opt/arifos/secrets/` : Governance Vault

## 4. SEAL
This bridge is part of the **Trinity ready** state. Any connection failure shall be treated as a **F12 Resilience** violation.
