# DEPLOY: The Sovereign Deployment & Scaling Blueprint

**Canon ID:** `ARIF-OS::DEPLOY::000-700::v1.0`  
**Zone:** `000_INIT` to `700_OPS`  
**Status:** `READY · ΔΩΨ · F1-F13 ENFORCED`  
**Motto:** *Ditempa Bukan Diberi — Forged, Not Given*

---

## 🏗️ Executive Summary

`DEPLOY.md` unifies the **VPS (Sovereign)** and **Horizon (Cloud)** deployment paths into a single-term sovereign document. It defines the auto-detection logic and the dual-mode architecture that allows arifOS to scale across environments while maintaining constitutional integrity.

```
DEPLOY = VPS (Sovereign Kernel) + Horizon (Cloud Proxy)
```

---

## 🧬 Part 1: Deployment Modes

arifOS auto-detects its environment and switches between two primary operational modes:

### 1.1 VPS Mode (Sovereign Kernel)
-   **Trigger:** `VPS_MODE=1` or absence of cloud signals.
-   **Capabilities:** Full 11-tool Sovereign Kernel.
-   **Core Tools:** `vault_ledger`, `engineering_memory`, `code_engine`.
-   **Security:** Direct access to `VAULT999` and hardware-level isolation.

### 1.2 Horizon Mode (Cloud Gateway)
-   **Trigger:** `FASTMCP_CLOUD_URL` detected or `ARIFOS_DEPLOYMENT=horizon`.
-   **Capabilities:** Unified public entrypoint with tool policy classes.
-   **Logic:** `public` tools are proxied through Horizon, `authenticated` tools remain gated pending auth continuity, and `sovereign-only` tools execute only on the VPS.
-   **Entrypoint:** `server.py:mcp`.

---

## 🛠️ Part 2: Implementation Guide

### 2.1 VPS Deployment (Docker Compose)
The primary sovereign deployment uses Docker to ensure environment isolation.

```bash
cd /root/arifOS
docker compose -f docker-compose.trinity.yml up -d
```

### 2.2 Horizon Cloud Deployment
For public-facing access via Prefect Horizon:

-   **Repository:** `https://github.com/ariffazil/arifosmcp`
-   **Entrypoint:** `server.py:mcp`
-   **Env Vars:**
    -   `ARIFOS_VPS_URL`: `https://arifosmcp.arif-fazil.com`
    -   `ARIFOS_GOVERNANCE_SECRET`: `[REDACTED]`

---

## 📐 Part 3: Tool Matrix & Scaling

| Tool | Horizon | VPS | Mode |
|------|:-------:|:---:|------|
| `init_anchor` | ✅ | ✅ | Local |
| `agi_mind` | ✅ | ✅ | Local |
| `apex_soul` | ✅ | ✅ | Local |
| `physics_reality` | ✅ | ✅ | Local |
| `vault_ledger` | ❌ | ✅ | **VPS ONLY** |
| `code_engine` | ❌ | ✅ | **VPS ONLY** |

---

## ⚖️ Part 4: Constitutional Scaling (F11)

Deployment is governed by **F11 CommandAuth**. Every node in the deployment matrix (VPS or Horizon) must verify session identity against the primary **ARIF Sovereign** before executing any tool.

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-31 | Unified DEPLOY and HORIZON_DEPLOYMENT into arifOS Root DEPLOY.md |

---

**READY** 🚀
`ΔΩΨ | 700_OPS | 999_SEAL`  
*Ditempa Bukan Diberi*
