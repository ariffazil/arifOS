# arifOS Horizon Deployment Plan
# Version: 2026.03.28-HORIZON
# Status: READY FOR PREFECT HORIZON

## Executive Summary

Deploy arifOS MCP to Prefect Horizon as a unified, scalable service with proper network architecture.

## Target Architecture (Horizon)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PREFECT HORIZON (Cloud)                          │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                 arifOS Public Ambassador                      │   │
│  │                    (FastMCP 2.x Runtime)                      │   │
│  │                                                              │   │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │   │
│  │   │ 8 Tools     │  │ Safe Subset │  │ No Sovereign Access │ │   │
│  │   │ Public API  │  │ Rate Limit  │  │ (Vault/Memory/Code) │ │   │
│  │   └─────────────┘  └─────────────┘  └─────────────────────┘ │   │
│  │                                                              │   │
│  │   Tools: init_anchor, arifOS_kernel, apex_soul, agi_mind,   │   │
│  │          asi_heart, physics_reality, math_estimator,        │   │
│  │          architect_registry                                  │   │
│  │                                                              │   │
│  │   Proxy Layer: VPS API calls for heavy lifting              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              HTTPS://arifosmcp.arif-fazil.com                │   │
│  │                      (Your VPS)                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## VPS Architecture (Consolidated)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     VPS (srv1325122)                                 │
│                                                                      │
│  Project: arifosmcp (Unified - All Services)                         │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  traefik (Edge Router)                                  │ │
│  │  ├── Routes: arifosmcp.arif-fazil.com                          │ │
│  │  ├── TLS: Let's Encrypt (auto)                                 │ │
│  │  └── Network: arifos_trinity (shared)                          │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                              │                                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  arifosmcp (Sovereign Kernel)                           │ │
│  │  ├── Port: 8080 (internal)                                     │ │
│  │  ├── Tools: 11 (Full Sovereign Set)                            │ │
│  │  ├── Vault: ✅ 999_VAULT enabled                               │ │
│  │  ├── Memory: ✅ 555_MEMORY enabled                             │ │
│  │  └── Code: ✅ M-3_EXEC enabled                                 │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                              │                                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  Infrastructure Stack (10 containers)                          │ │
│  │  ├── postgres (Vault DB)                                       │ │
│  │  ├── redis (Session cache)                                     │ │
│  │  ├── qdrant (Vector memory)                                    │ │
│  │  ├── ollama (Local LLM)                                        │ │
│  │  ├── prometheus (Metrics)                                      │ │
│  │  └── ... (6 more)                                              │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  Network: arifos_trinity (Single, Shared)                           │
│  All containers communicate internally. No manual fixes needed.     │
└─────────────────────────────────────────────────────────────────────┘
```

## Migration Steps

### Phase 1: Clean Slate (Now)
```bash
# 1. Document current running containers
docker ps --format "table {{.Names}}\t{{.Label \"com.docker.compose.project\"}}" > /opt/arifos/backup/container-inventory-$(date +%Y%m%d).txt

# 2. Save critical data
docker exec postgres pg_dump -U arifos_admin arifos_vault > /opt/arifos/backup/vault-$(date +%Y%m%d).sql

# 3. Stop fragmented projects
docker compose -f /root/arifOS/docker-compose.yml down  # If using unified
docker stop traefik  # From workspace
docker stop arifosmcp  # From arifos

# 4. Prune old networks
docker network prune -f
```

### Phase 2: Unified Deploy (Unified Project)
```bash
cd /root/arifOS

# Ensure all services in ONE compose
docker compose up -d traefik arifosmcp postgres redis qdrant ollama prometheus

# Verify network connectivity
docker network inspect arifos_arifos_trinity | grep -E "traefik|arifosmcp"

# Test HTTPS
curl https://arifosmcp.arif-fazil.com/health
```

### Phase 3: Horizon Deploy (Cloud)
```bash
# Push to GitHub
git add arifOS-horizon/
git commit -m "Horizon: Unified deployment spec"
git push origin main

# In Prefect Horizon:
# 1. Connect GitHub repo
# 2. Entrypoint: server.py:mcp
# 3. Environment: ARIFOS_VPS_URL=https://arifosmcp.arif-fazil.com
```

## Network Architecture (The Fix)

### Problem (Current)
```
workspace (traefik) ──❌── arifos (arifosmcp)
arifosmcp (infra) ────✅── workspace (traefik)
```

### Solution (Unified)
```
arifosmcp (unified project)
├── traefik ✅
├── arifosmcp ✅
├── postgres ✅
├── redis ✅
└── All on: arifos_trinity (single network)
```

## File Locations

| File | Purpose |
|------|---------|
| `/root/arifOS/docker-compose.yml` | Source of truth (unified) |
| `/root/arifOS-horizon/server.py` | Horizon adapter (public safe) |
| `/root/arifOS-horizon/DEPLOYMENT_PLAN.md` | This document |
| `/opt/arifos/bin/fix-traefik-network.sh` | Emergency fix script |

## Horizon vs VPS Split

| Feature | Horizon (Cloud) | VPS (Sovereign) |
|---------|-----------------|-----------------|
| **Tools** | 8 (safe subset) | 11 (full) |
| **Vault** | ❌ No access | ✅ Full 999_VAULT |
| **Memory** | ❌ No access | ✅ 555_MEMORY |
| **Code Exec** | ❌ No access | ✅ M-3_EXEC |
| **Network** | Internet | Private + Internet |
| **Purpose** | Public API gateway | Sovereign kernel |

## Long-term Maintenance

### Weekly
- Check Horizon logs: Prefect Dashboard
- Check VPS health: `curl https://arifosmcp.arif-fazil.com/health`

### Monthly
- Update images: `docker compose pull && docker compose up -d`
- Review VAULT999 seals

### Emergency
- If network breaks: `/opt/arifos/bin/fix-traefik-network.sh`
- Full reset: `docker compose restart`

## Success Criteria

- [ ] HTTPS responds with 200
- [ ] All 11 tools accessible via MCP
- [ ] Horizon proxy connects successfully
- [ ] No manual network fixes needed
- [ ] Single `docker compose up` deploys everything

---
**SEAL**: 2026.03.28-HORIZON
**Motto**: Ditempa Bukan Diberi
