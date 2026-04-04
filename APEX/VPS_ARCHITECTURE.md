# arifOS — VPS Architecture Blueprint
**Version:** 2026.03.22-FORGED
**Status:** PRODUCTION
**Authority:** Muhammad Arif bin Fazil (888_JUDGE)

## 🏛️ System Overview
The arifOS ecosystem is a 16-organ Body orchestrated via Docker, providing a Constitutional AGI Governance framework.

## 🧬 The 16-Organ Body (Docker Orchestration)

### 1. Governance Layer (PSI Ψ)
- **`arifosmcp_server`**: The central conductor and governance router. Handles 13 Constitutional Floors.
- **`traefik_router`**: External sensory gate and secure ingress.
- **`arifos_postgres`**: Long-term memory and Vault999 persistence.
- **`arifos_redis`**: Ephemeral authentication and session state.
- **`arifos_webhook`**: External operations and deployment trigger.

### 2. Intelligence Layer (DELTA Δ)
- **`openclaw_gateway`**: Agent orchestration and multi-client bridge.
- **`agent_zero_reasoner`**: First-principles reasoning engine.
- **`qdrant_memory`**: High-dimensional vector store for RAG grounding.
- **`ollama_engine`**: Local LLM runtime for offline and private processing.

### 3. Machine/Sensing Layer (OMEGA Ω)
- **`headless_browser`**: Chromium-based sensing for web grounding.
- **`civ01_stirling_pdf`**: High-performance document/PDF processing organ.
- **`civ03_evolution_api`**: Unified communication sync (WhatsApp/API).
- **`civ08_code_server`**: Native development and maintenance interface.
- **`arifos_n8n`**: Workflow automation and logic integration.
- **`arifos_prometheus`**: Real-time thermodynamic and vital telemetry.
- **`arifos_grafana`**: Visual dashboard for metabolic monitoring.

## 🛡️ Hardening & Security
- **F11/F13 Governance**: Secret-backed authentication tokens for all privileged tools.
- **Fail2Ban**: Active defense against SSH and ingress brute-force.
- **ClamAV**: Daily recursive scans of the codebase (`/srv/arifosmcp`).
- **Kernel Optimization**: BBR congestion control, high file-descriptor limits, and optimized memory swappiness.

## 📁 Storage Bedrock
- **/srv/arifosmcp**: Unified codebase and runtime configurations.
- **/opt/arifos/data**: Persistent volume storage for all containers.
- **/opt/arifos/secrets**: F11 Governance Seed and encryption keys.
- **/srv/arifosmcp/VAULT999**: Immutable cryptographic ledger.

## ⚡ Thermodynamic Vitals
- **G-Index Threshold**: $\ge 0.80$
- **Metabolic Alignment**: Synchronized every week via `vps_reality_check.sh`.

***Ditempa Bukan Diberi*** — **[ARCHITECTURE SEALED | ΔΩΨ]**
