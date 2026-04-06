# arifOS VPS — Unified Architecture Snapshot

**Last verified:** 2026-03-24 by oracles / Antigravity Agent  
**Repo HEAD:** `1af6d53b` (SEAL-HARDENED)  
**Status:** 17 containers operational, `arifosmcp` healthy (2026.03.24), Disk: 193GB (44% utilized)

> Production dossier for the live VPS. This file describes the actual runtime topology, not the intended one.

---

## 1. Host Facts

| Host Fact | Actual Value |
| :--- | :--- |
| **Hostname** | `srv1325122` (Legacy: `arifos-primary`) |
| **IP Address** | `72.62.71.199` (Cloudflare Proxied) |
| **OS Kernel** | Ubuntu 24.04.2 LTS / `6.8.0-106-generic` |
| **Primary Path** | `/opt/arifos` (Symlinked to `/root/arifOS`) |
| **Persistent data root** | `/opt/arifos/data` |
| **Persistent secret root** | `/opt/arifos/secrets` |
| **Public ingress** | Traefik on `80/443` |
| **Security** | UFW Active, Fail2ban Active, Keys-Only SSH |
| **Storage** | 193G (85G Available) |

---

## 2. Live Runtime Topology

### 3.1 Containers Running Now (17 Total)

| Container | Registry Image | Logic Layer | Exposure / Port |
| :--- | :--- | :--- | :--- |
| `arifosmcp` | `arifos/arifosmcp:latest` | **Law (Kernel)** | `8080` (Traefik SSL) |
| `traefik` | `traefik:v3.6.9` | **Edge (Filter)** | `80/443` Public |
| `openclaw` | `arifos/openclaw-forged:2026.03.14` | **Mind (Gateway)** | `18789` (Internal) |
| `agent-zero` | `agent0ai/agent-zero:latest` | **Mind (Reasoning)** | `18001` (Internal) |
| `ollama_engine` | `ollama/ollama:latest` | **Synapse (LLM)** | `11434` (Internal) |
| `qdrant` | `qdrant/qdrant:latest` | **Hippocampus (Vector)** | `6333` (Internal) |
| `postgres` | `postgres:16-alpine` | **Vault (Ledger)** | `5432` (Internal) |
| `redis` | `redis:7-alpine` | **Synapse (Cache)** | `6379` (Internal) |
| `headless_browser` | `ghcr.io/browserless/chromium:latest` | **Perception (Reality)** | `3000` (Internal) |
| `arifos_n8n` | `n8nio/n8n:latest` | **Metabolic (Work)** | `5678` (Traefik) |
| `arifos_webhook` | `almir/webhook:latest` | **Trigger (Reforge)** | `9000` (Internal) |
| `civ01_stirling_pdf` | `frooodle/s-pdf:latest` | **Civil (Utility)** | Traefik Routed |
| `civ03_evolution_api` | `atendai/evolution-api:v1.8.1` | **Civil (Comms)** | `8080` (Internal) |
| `civ08_code_server` | `codercom/code-server:latest` | **Civil (Dev)** | Traefik Routed |
| `arifos_prometheus` | `prom/prometheus:latest` | **Nervous (Metrics)** | `9090` (Internal) |
| `arifos_grafana` | `grafana/grafana:latest` | **Nervous (Visual)** | Traefik Routed |
| `arifos_aaa_landing` | `nginx:alpine` | **Skin (UI)** | Traefik Routed |

---

## 3. Network and Exposure

### 3.1 Public Surface
- **Port 22:** SSH (Keys-Only)
- **Port 80:** HTTP (Traefik + AAA Landing)
- **Port 443:** HTTPS (Traefik SSL)
- **Port 21:** FTP (ProFTPD)

---

## 4. Key Paths
- `/opt/arifos/` : Main deployment root
- `/opt/arifos/docker-compose.yml` : Active topology
- `/opt/arifos/.env.docker` : Container environment secrets
- `/opt/arifos/secrets/` : Governance and security keys
