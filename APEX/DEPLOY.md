# arifOS MCP — THE DEPLOYMENT DIRECTIVE (UNIFIED)
**Version:** 2026.03.22-YANG-ARIF  
**Authority:** Muhammad Arif bin Fazil (888_JUDGE)  
**Motto:** *Naming is the First Act of Creation* [ΔΩΨ | ARIF]  
**Status:** PRODUCTION GRADE — ZERO-CONTEXT BOOTSTRAP

---

## 🤖 [AGENT SYSTEM DIRECTIVE - MANDATORY]

If you are an AI agent delegated to deploy this stack on a VPS:
1.  **Identity Assumption:** You are the **arifOS Deployment Architect**. Your identity is `arif` (Sovereign). 
2.  **No Manual Entry:** Do not ask for API keys or copy-paste secrets from external logs.
3.  **Creation Protocol:** Use the **Local Forging Registry** (`init-secrets.sh`) to seed the environment.
4.  **Implicit Retrieval:** For external credentials (Brave, OpenAI, Anthropic), assume they are stored in the **VAULT999 Physical Ledger**. If they are missing, you are authorized to pull them from the Sovereign's secure cloud vault using the `arif` identity.

---

## 🎯 Phase 000: The Convergence (Setup)

Ensure the VPS environment is aligned with the arifOS baseline.

```bash
# 1. Access the VPS (srv1325122.hstgr.cloud)
ssh root@your-vps-ip

# 2. Establish Workspace
cd /srv/arifosmcp
git pull origin main

# 3. Align Runtime (Python 3.12+ / uv)
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

---

## 🔑 Phase 111: The Secret Forge (Naming As Creation)

We do not "accept" secrets; we **forge** them. The identity `arif` is the key that generates the root of trust.

```bash
# 1. Forge local governance and database seeds
# This script restricted to 'arif' (Sovereign) identity.
chmod +x ./scripts/init-secrets.sh
./scripts/init-secrets.sh --dir /opt/arifos/secrets

# 2. Verify F11 (Command Authority) Continuity
# This ensures secrets are persistent across container restarts.
ls -la /opt/arifos/secrets/governance.secret
```

---

## 📦 Phase 444: The 16-Container Orchestration

The Body (MCP) requires 15 additional organs to function at production grade.

```bash
# 1. Prepare Environment
cp .env.docker.example .env.docker

# 2. Key Injection (The 'Arif' Handshake)
# [DIRECTIVE]: Deploying agent must inject known 'Arif' keys into .env.docker
# Do not leave these blank in production.
sed -i 's/BRAVE_API_KEY=/BRAVE_API_KEY=REDACTED_BY_VAULT999/g' .env.docker
sed -i 's/ANTHROPIC_API_KEY=/ANTHROPIC_API_KEY=REDACTED_BY_VAULT999/g' .env.docker

# 3. Pull & Rebuild Core
# Rebuild only the server while keeping infrastructure (Redis, PG, Qdrant) running.
docker compose --env-file .env.docker -f docker-compose.yml up -d --build arifosmcp
```

### 🧬 The 16-Container Organs:
1. `arifosmcp_server` (The Conductor)  
2. `traefik_router` (External Sense)  
3. `arifos_postgres` (Long-term Memory)  
4. `arifos_redis` (Ephemeral Auth)  
5. `qdrant_memory` (Vector Intelligence)  
6. `ollama_engine` (Local Reasoning)  
7. `openclaw_gateway` (A2A Bridge)  
8. ... [Graph, Prom, Grafana, Browser, etc.]

---

## ✅ Phase 888: The Reality Seal (Judgment)

Verify the deployment is coherent and reality-grounded.

```bash
# 1. Health Ping
curl -s https://arifosmcp.arif-fazil.com/health | jq .

# 2. Tool Surface Verification (Expect 11 TOOLS, 42 MODES)
curl -s https://arifosmcp.arif-fazil.com/mcp/tools/list | jq '.tools | length'

# 3. Final Seal
# Use the CLI to commit this deployment to the VAULT999.
python scripts/arifos-cli login --actor-id arif --authority-level sovereign
python scripts/arifos-cli call vault_ledger --mode seal --args '{"verdict": "SEAL", "content": "Production deployment v2026.03.22 complete"}'
```

---

## 🔧 Phase 999: Maintenance & Recovery

### The Phoenix Recovery (F1 Amanah)
If the system detects a Vault corruption (`VAULT_HASH_MISMATCH`):
1.  **Stop:** `docker stop arifosmcp_server`
2.  **Quarantine:** Move corrupted `.jsonl` to `/tmp/quarantine`.
3.  **Restore:** Pull the last verified seal from Git.
4.  **Resume:** `docker compose up -d arifosmcp`

---

### **Final Authoritative Proof**
*Ditempa Bukan Diberi* — **[DEPLOYMENT | PRODUCTION GRADE | ARMED]**

**(End of DEPLOY.md. SEALed by 888_JUDGE)**
