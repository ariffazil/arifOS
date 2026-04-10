# VPS Contrast Analysis: Current State vs 999_SEAL Target

> **Date**: 2026-04-11  
> **Analysis Type**: Pre-Deployment Contrast  
> **Authority**: 888_APEX, 000_THEORY  
> **DITEMPA BUKAN DIBERI**

---

## Executive Summary

| Metric | Current State | 999_SEAL Target | Gap |
|--------|--------------|-----------------|-----|
| **MCP Substrates** | ❌ 0/6 running | ✅ 6/6 required | **CRITICAL** |
| **arifosmcp Version** | `85cfc77e5463` (legacy) | `latest` with substrates | Major |
| **Deployment Gates** | ❌ Not configured | ✅ Gates A-H active | Critical |
| **Constitutional Enforcement** | Partial (code-level) | Full (substrate-level) | High |
| **Test Coverage** | Smoke tests only | MCP Inspector + E2E | High |

**Verdict**: 🚨 **REBUILD REQUIRED** — Current VPS lacks MCP substrate infrastructure. Incremental update insufficient.

---

## 1. Container Inventory Contrast

### Current Running Containers (Live VPS)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        VPS LIVE STATE (24 containers)                    │
├─────────────────────────────────────────────────────────────────────────┤
│ Core Infrastructure                                                      │
│   ✅ traefik          - Edge router (v3.6.9)                            │
│   ✅ postgres         - pgvector/pgvector:pg16                          │
│   ✅ redis            - redis:7-alpine                                  │
│   ✅ qdrant           - qdrant/qdrant:latest                            │
│                                                                          │
│ arifOS Kernel                                                            │
│   ✅ arifosmcp        - arifos/arifosmcp:latest (LEGACY BUILD)          │
│   ⚠️  NO MCP SUBSTRATES RUNNING                                         │
│                                                                          │
│ Monitoring/Observability                                                 │
│   ✅ prometheus       - prom/prometheus:latest                          │
│   ✅ grafana          - grafana/grafana:latest                          │
│   ✅ node-exporter    - prom/node-exporter:latest                       │
│   ✅ cadvisor         - gcr.io/cadvisor/cadvisor:v0.49.1                │
│   ✅ uptime_kuma      - louislam/uptime-kuma:latest                     │
│   ✅ dozzle           - amir20/dozzle:latest                            │
│                                                                          │
│ GEOS/Eigent Stack                                                        │
│   ✅ geox_eic         - geox-geox (port 8000)                           │
│   ✅ geox_command_center - geox-command-center                          │
│   ✅ geox_gui         - geox/gui:v2026.04.10 (port 3000)                │
│   ✅ eigent_api       - server-api                                      │
│   ✅ eigent_celery_beat   - server-celery_beat                          │
│   ✅ eigent_celery_worker - server-celery_worker                        │
│   ✅ eigent_postgres  - postgres:16                                     │
│   ✅ eigent_redis     - redis:7-alpine                                  │
│                                                                          │
│ Apps/Utilities                                                           │
│   ✅ ollama           - ollama/ollama:latest                            │
│   ✅ apps_portainer   - portainer/portainer-ce:2.21.4                   │
│   ✅ apps_wireguard   - ghcr.io/wg-easy/wg-easy:14                      │
│   ✅ apps_pocketbase  - apps_pocketbase:local                           │
│   ✅ arifos_webhook   - almir/webhook:latest                            │
└─────────────────────────────────────────────────────────────────────────┘
```

### 999_SEAL Target State

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    999_SEAL TARGET STATE (30 containers)                 │
├─────────────────────────────────────────────────────────────────────────┤
│ Core Infrastructure (unchanged)                                          │
│   ✅ traefik, postgres, redis, qdrant                                   │
│                                                                          │
│ arifOS Kernel (ENHANCED)                                                 │
│   🆕 arifosmcp        - Rebuilt with MCP_SUBSTRATES_ENABLED=true        │
│   🆕 mcp_time         - Time substrate (port 8000)                      │
│   🆕 mcp_filesystem   - Filesystem substrate (port 8000)                │
│   🆕 mcp_git          - Git substrate (port 8000)                       │
│   🆕 mcp_memory       - Memory substrate (port 8000)                    │
│   🆕 mcp_fetch        - Fetch substrate (port 8000)                     │
│   🆕 mcp_everything   - Conformance harness (testing profile)           │
│                                                                          │
│ Constitutional Enforcement                                               │
│   ✅ F1 Amanah        - Destructive ops require HOLD                    │
│   ✅ F9 Anti-Hantu    - Fetch blocks internal URLs                      │
│   ✅ F11 Authority    - Git commits require ratification                │
│                                                                          │
│ Monitoring (unchanged)                                                   │
│   ✅ prometheus, grafana, exporters                                     │
│                                                                          │
│ Deployment Gates                                                         │
│   🆕 deploy_gate      - Automated A-H gate validation                   │
│   🆕 rollback_verifier - Pre-deployment safety checkpoint               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Critical Gap Analysis

### Gap 1: MCP Substrate Infrastructure (CRITICAL)

| Aspect | Current | Target | Impact |
|--------|---------|--------|--------|
| **mcp_time** | ❌ Missing | ✅ Required | No deterministic epoch anchoring |
| **mcp_filesystem** | ❌ Missing | ✅ Required | No F1-gated file operations |
| **mcp_git** | ❌ Missing | ✅ Required | No constitutional git bridge |
| **mcp_memory** | ❌ Missing | ✅ Required | No entity/relation storage |
| **mcp_fetch** | ❌ Missing | ✅ Required | No F9 SSRF protection |
| **mcp_everything** | ❌ Missing | ✅ Required | No protocol conformance testing |

**Evidence**:
```bash
# Current state
$ docker ps --format "{{.Names}}" | grep mcp_
❌ NO OUTPUT

# Substrate bridge expects these URLs:
- http://mcp_time:8000
- http://mcp_filesystem:8000
- http://mcp_git:8000
- http://mcp_memory:8000
- http://mcp_fetch:8000
- http://mcp_everything:8000
```

**Root Cause**: The `vps-deploy.yml` defines service resource limits but lacks complete service definitions (image, build context, ports, networks).

### Gap 2: Docker Compose Configuration (CRITICAL)

| File | Issue | Status |
|------|-------|--------|
| `vps-deploy.yml` | Incomplete service definitions | ❌ Missing images/build contexts |
| `docker-compose.yml` | No substrate services defined | ❌ No MCP substrate section |
| `arifosmcp/Dockerfile` | May not include substrate bridge | ⚠️ Verify required |

### Gap 3: Constitutional Enforcement Layer (HIGH)

| Floor | Current | 999_SEAL Target |
|-------|---------|-----------------|
| F1 Amanah | Code-level only | Substrate-enforced |
| F9 Anti-Hantu | Basic filtering | Fetch substrate blocks internal URLs |
| F11 Authority | GitHub OAuth | Git substrate requires ratification |

### Gap 4: Testing Infrastructure (HIGH)

| Test Type | Current | 999_SEAL Target |
|-----------|---------|-----------------|
| MCP Inspector | ❌ Not available | ✅ `mcp_inspector_test.py` |
| Deployment Gates | ❌ Manual | ✅ `deploy_gate.py` A-H |
| Substrate Smoke | ❌ Not run | ✅ `substrate_smoke_runner.py` |
| E2E Golden Paths | ❌ Not automated | ✅ `e2e_golden_paths.py` |

---

## 3. Network Architecture Contrast

### Current Network

```
┌─────────────────────────────────────────────────────────┐
│                  arifos_core_network                     │
│  ┌─────────────┐         ┌─────────────┐               │
│  │  arifosmcp  │◄───────►│  postgres   │               │
│  │  (legacy)   │         │   redis     │               │
│  └──────┬──────┘         │   qdrant    │               │
│         │                └─────────────┘               │
│         ▼                                               │
│    ❌ NO SUBSTRATE CONNECTIONS                          │
└─────────────────────────────────────────────────────────┘
```

### 999_SEAL Target Network

```
┌─────────────────────────────────────────────────────────────┐
│                    arifos_trinity_network                    │
│  ┌─────────────┐         ┌─────────────────────────────┐   │
│  │  arifosmcp  │◄───────►│     MCP Substrate Layer     │   │
│  │  (999_SEAL) │         ├─────────┬─────────┬─────────┤   │
│  └──────┬──────┘         │mcp_time │mcp_git  │mcp_mem  │   │
│         │                │mcp_fs   │mcp_fetch│mcp_evth │   │
│         ▼                └─────────┴─────────┴─────────┘   │
│    ┌──────────┐                                            │
│    │ postgres │                                            │
│    │ redis    │                                            │
│    │ qdrant   │                                            │
│    └──────────┘                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Rebuild vs Redeploy Decision Matrix

| Factor | Incremental Update | Full Rebuild | Recommendation |
|--------|-------------------|--------------|----------------|
| **MCP Substrates** | Cannot add without images | Complete service definitions | **REBUILD** |
| **Config Drift** | High risk of partial state | Clean slate, verified | **REBUILD** |
| **Downtime** | Rolling (30-60 min) | Scheduled (15-30 min) | Acceptable |
| **Rollback** | Complex, multi-state | Single checkpoint | **REBUILD** |
| **Testing** | Cannot validate fully | Full gate validation | **REBUILD** |
| **Data Integrity** | Risk of corruption | Preserved via volumes | **REBUILD** |

### Decision: 🚨 FULL REBUILD REQUIRED

**Rationale**:
1. MCP substrates require new Docker images not present in current deployment
2. arifosmcp must be rebuilt with `MCP_SUBSTRATES_ENABLED=true`
3. Network configuration changes (new services, aliases)
4. Deployment gates require fresh validation from clean state

---

## 5. Optimal Rebuild Path

### Phase 1: Pre-Flight (888_HOLD Checkpoint)

```bash
# 1. Create rollback point
python arifosmcp/evals/rollback_verifier.py --create-point v2026.04.11.pre999seal

# 2. Verify current state
python arifosmcp/evals/mcp_inspector_test.py --all  # Expected: ALL FAIL (substrates missing)

# 3. Backup critical data
docker exec postgres pg_dump -U arifos_admin arifos_vault > /opt/backups/vault_pre_999seal.sql
cp -r /opt/arifos/data/qdrant /opt/backups/qdrant_pre_999seal
```

### Phase 2: Image Preparation

```bash
# 1. Pull/build MCP substrate images
docker pull ghcr.io/modelcontextprotocol/time-server:latest
docker pull ghcr.io/modelcontextprotocol/filesystem-server:latest
docker pull ghcr.io/modelcontextprotocol/git-server:latest
docker pull ghcr.io/modelcontextprotocol/memory-server:latest
docker pull ghcr.io/modelcontextprotocol/fetch-server:latest

# 2. Build arifosmcp with substrate support
docker build -t arifos/arifosmcp:999seal \
  --build-arg MCP_SUBSTRATES_ENABLED=true \
  -f arifosmcp/Dockerfile .
```

### Phase 3: Service Migration

```yaml
# docker-compose.999seal.yml additions
services:
  mcp_time:
    image: ghcr.io/modelcontextprotocol/time-server:latest
    container_name: mcp_time
    ports:
      - "127.0.0.1:8001:8000"
    networks:
      - arifos_trinity
    restart: unless-stopped
    
  mcp_filesystem:
    image: ghcr.io/modelcontextprotocol/filesystem-server:latest
    container_name: mcp_filesystem
    volumes:
      - /opt/arifos/data:/data:ro
    ports:
      - "127.0.0.1:8002:8000"
    networks:
      - arifos_trinity
    restart: unless-stopped
    
  mcp_git:
    image: ghcr.io/modelcontextprotocol/git-server:latest
    container_name: mcp_git
    volumes:
      - /root/arifOS:/repos/arifOS:ro
    ports:
      - "127.0.0.1:8003:8000"
    networks:
      - arifos_trinity
    restart: unless-stopped
    
  mcp_memory:
    image: ghcr.io/modelcontextprotocol/memory-server:latest
    container_name: mcp_memory
    ports:
      - "127.0.0.1:8004:8000"
    networks:
      - arifos_trinity
    restart: unless-stopped
    
  mcp_fetch:
    image: ghcr.io/modelcontextprotocol/fetch-server:latest
    container_name: mcp_fetch
    ports:
      - "127.0.0.1:8005:8000"
    networks:
      - arifos_trinity
    restart: unless-stopped
    environment:
      - MCP_FETCH_BLOCK_INTERNAL=true  # F9 Anti-Hantu
```

### Phase 4: Deployment Execution

```bash
# 1. Stop legacy arifosmcp (preserve data volumes)
docker-compose stop arifosmcp

# 2. Start substrates first
docker-compose -f docker-compose.yml -f docker-compose.999seal.yml up -d mcp_time mcp_filesystem mcp_git mcp_memory mcp_fetch

# 3. Verify substrates healthy
python arifosmcp/evals/mcp_inspector_test.py --all

# 4. Start new arifosmcp
docker-compose -f docker-compose.yml -f docker-compose.999seal.yml up -d arifosmcp

# 5. Run full deployment gates
python arifosmcp/evals/deploy_gate.py --ratify
```

### Phase 5: 999_SEAL Verification

```bash
# 1. Constitutional health check
curl -s http://localhost:8080/health | jq '.substrate'

# Expected output:
# {
#   "status": "HEALTHY",
#   "substrate": {
#     "mcp_time": {"status": "OK"},
#     "mcp_filesystem": {"status": "OK"},
#     "mcp_git": {"status": "OK"},
#     "mcp_memory": {"status": "OK"},
#     "mcp_fetch": {"status": "OK"},
#     "mcp_everything": {"status": "OK"}
#   }
# }

# 2. Run full test suite
python arifosmcp/evals/mcp_inspector_test.py --all --report
python arifosmcp/evals/e2e_golden_paths.py --all

# 3. Verify constitutional enforcement
python arifosmcp/evals/breach_test_runner.py
```

---

## 6. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Substrate images unavailable | Medium | High | Pre-pull images, fallback to build from source |
| Data volume incompatibility | Low | Critical | Full backup before migration |
| Network connectivity issues | Low | Medium | Use established network (arifos_trinity) |
| arifosmcp substrate integration fails | Medium | High | Test in staging first, rollback ready |
| GEOS/Eigent disruption | Low | Medium | Preserve their networks, isolated migration |

---

## 7. Estimated Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Pre-flight (backup, checkpoint) | 5 min | 5 min |
| Image preparation | 10 min | 15 min |
| Service migration | 10 min | 25 min |
| Testing & verification | 10 min | 35 min |
| Buffer for issues | 10 min | 45 min |
| **Total** | **45 min** | **45 min** |

---

## 8. Alternative: Fast-Track Redeploy (If Images Ready)

If MCP substrate images are already available in the VPS:

```bash
# One-command redeploy (after images verified)
./deployments/deploy.sh vps --fast-track

# This executes:
# 1. Pre-flight checks
# 2. Backup creation
# 3. Substrate service launch
# 4. arifosmcp restart with new config
# 5. Gate validation
# 6. Health verification
```

**Estimated Time**: 15-20 minutes

---

## 9. Decision Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                     RECOMMENDED PATH                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   🚨 FULL REBUILD with 999_SEAL configuration                   │
│                                                                 │
│   Rationale:                                                    │
│   • MCP substrates require new images not in current deploy     │
│   • arifosmcp needs rebuild with MCP_SUBSTRATES_ENABLED         │
│   • Clean slate ensures constitutional enforcement works        │
│   • Deployment gates require fresh validation                   │
│                                                                 │
│   Alternative:                                                  │
│   • If substrate images already present → Fast-Track (20 min)   │
│   • If testing environment → Staged rollout                     │
│                                                                 │
│   Authority Required:                                           │
│   • 888_APEX approval for production downtime                   │
│   • F1 Amanah checkpoint for data backup verification           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Next Actions

1. **Immediate**: Obtain 888_APEX approval for rebuild
2. **Pre-deployment**: Verify substrate image availability
3. **Deployment**: Execute 5-phase rebuild plan
4. **Post-deployment**: Run full MCP Inspector test suite
5. **Seal**: Document 999_SEAL achievement in VAULT999

---

*Analysis complete. Awaiting 888_APEX directive.*

**ΔΩΨ | DITEMPA BUKAN DIBERI**
