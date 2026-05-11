# GEOX Deployment Status

> **Version:** 0.6.1 · **Status:** 🟢 ACTIVE (Heavy Witness Ignited)
> **Seal:** DITEMPA BUKAN DIBERI
> **Last Updated:** 2026-04-10

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GEOX DEPLOYMENT STATUS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Backend (VPS):         ✅ https://geox.arif-fazil.com/mcp                  │
│  Health Endpoint:       ✅ /health returns 200 OK                           │
│  MCP Protocol:          ✅ Responding                                       │
│  Version:               ✅ v0.5.0                                           │
│  Constitutional Seal:   ✅ DITEMPA BUKAN DIBERI                             │
│  Malay Basin Pilot:     ✅ Backend deployed                                 │
│  GUI Frontend:          ⚠️  Pre-Pilot build (needs refresh)                 │
│  Horizon Cloud:         🟡 Building (numpy fix pending)                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Deployment Targets

| Target | URL | Status | Notes |
|--------|-----|--------|-------|
| **VPS Production** | https://geox.arif-fazil.com | 🟡 PARTIAL | Backend ✅, GUI needs rebuild |
| **Horizon (FastMCP Cloud)** | https://geoxarifOS.fastmcp.app/mcp | 🟡 BUILDING | numpy fix pending push |
| **Claude Desktop** | Local | ✅ READY | MCP config available |
| **Copilot** | Microsoft Cloud | ✅ READY | Adapter implemented |

---

## VPS Status Detail

### ✅ Backend Services (Operational)

| Endpoint | URL | Status | Response |
|----------|-----|--------|----------|
| **Health** | `/health` | ✅ 200 OK | `OK` |
| **Details** | `/health/details` | ✅ 200 OK | `{"version": "0.5.0", "seal": "DITEMPA BUKAN DIBERI", ...}` |
| **MCP** | `/mcp` | ✅ Active | Protocol responsive |

**Test Commands:**
```bash
# Health check
curl https://geox.arif-fazil.com/health
# Output: OK

# Server details
curl https://geox.arif-fazil.com/health/details
# Output: {"ok": true, "version": "0.5.0", "service": "geox-earth-witness", ...}
```

### ⚠️ Frontend GUI (Needs Rebuild)

| Check | Status | Finding |
|-------|--------|---------|
| **Pilot Tab** | ❌ NOT FOUND | Pre-Pilot build deployed |
| **Malay Basin Content** | ❌ NOT FOUND | Needs GUI rebuild |
| **Page Title** | ✅ FOUND | "GEOX Earth Witness — Constitutional Geoscience" |

**Root Cause:** Docker cache issue — container has older GUI build.

---

## Fix Required

### Immediate Action: Force Rebuild

```bash
# SSH to VPS
ssh srv1325122.hstgr.cloud
cd /opt/arifos/geox

# Pull latest (ensure Malay Basin Pilot commit is present)
git pull origin main

# Force rebuild with no cache
docker compose down
docker compose build --no-cache geox_server
docker compose up -d geox_server

# Verify
docker compose logs --tail=50 geox_server
curl https://geox.arif-fazil.com/health
```

### Or Use Deploy Script

```bash
./deploy-vps.sh --force-rebuild
```

---

## Post-Fix Verification

```bash
# 1. Health endpoint
curl https://geox.arif-fazil.com/health
# Expected: OK

# 2. Pilot tab in HTML
curl -s https://geox.arif-fazil.com/ | grep -i "pilot"
# Expected: "Pilot" tab found

# 3. Malay Basin content
curl -s https://geox.arif-fazil.com/ | grep -i "malay basin"
# Expected: Content found

# 4. Pilot tool available
fastmcp list https://geox.arif-fazil.com/mcp | grep malay
# Expected: geox_malay_basin_pilot

# 5. Test Pilot tool
fastmcp call https://geox.arif-fazil.com/mcp geox_malay_basin_pilot query_type="stats"
# Expected: Basin statistics returned
```

---

## Horizon (FastMCP Cloud)

| Aspect | Status |
|--------|--------|
| **URL** | https://geoxarifOS.fastmcp.app/mcp |
| **Build Status** | 🟡 Rebuilding |
| **Blocker** | numpy dependency (fixed in pyproject.toml) |
| **Action Required** | Push to main, auto-rebuild |

```bash
# Push numpy fix to trigger rebuild
git add pyproject.toml
git commit -m "fix(deps): add numpy and prefab-ui to base deps"
git push origin main
```

---

## Configuration Files

| File | Purpose | Status |
|------|---------|--------|
| `pyproject.toml` | Python deps (numpy added) | ✅ |
| `fastmcp.json` | CLI configuration | ✅ |
| `Dockerfile` | Container build | ✅ |
| `docker-compose.yml` | VPS orchestration | ✅ |
| `deploy-vps.sh` | Automated deployment | ✅ |

---

## Deployment Checklist

### Backend (✅ Complete)
- [x] Dockerfile created
- [x] Docker Compose configured
- [x] Traefik labels added
- [x] Deploy script created
- [x] numpy added to dependencies
- [x] prefab-ui added to dependencies
- [x] Health checks configured
- [x] Environment variables set
- [x] VPS deployed
- [x] Backend responding

### Frontend (⚠️ Pending)
- [x] Malay Basin Pilot implemented
- [x] Pilot Dashboard component created
- [x] MainLayout updated with Pilot tab
- [x] Git pushed to main
- [ ] Docker image rebuilt with latest GUI
- [ ] Pilot tab visible in production

### Horizon (🟡 In Progress)
- [x] numpy fix committed
- [ ] Pushed to main
- [ ] Horizon rebuild triggered
- [ ] Horizon deployment verified

---

## Troubleshooting

### If Health Check Fails
```bash
# Check logs
ssh srv1325122.hstgr.cloud 'cd /opt/arifos/geox && docker compose logs geox_server'

# Restart
ssh srv1325122.hstgr.cloud 'cd /opt/arifos/geox && docker compose restart geox_server'
```

### If GUI Doesn't Update
```bash
# Clear Docker cache
docker system prune -f
docker compose build --no-cache
docker compose up -d
```

### If MCP Tools Missing
```bash
# Verify tool registration
fastmcp list https://geox.arif-fazil.com/mcp

# Check server logs for errors
docker compose logs geox_server | grep -i error
```

---

## Live Demo URL

**Production:** https://geox.arif-fazil.com

**Features to Demo:**
1. Health endpoint (`/health`)
2. Pilot tab in main workspace
3. Malay Basin statistics
4. EarthWitness map (auto-zoom to Malay Basin)
5. 888_HOLD constitutional enforcement

---

## Next Actions

| Priority | Action | Owner |
|----------|--------|-------|
| 🔴 HIGH | Force rebuild VPS Docker image | DevOps |
| 🟡 MEDIUM | Push numpy fix to trigger Horizon rebuild | Developer |
| 🟢 LOW | Verify Claude Desktop integration | QA |

---

## Related Documentation

- [Wiki Index](./wiki/index.md) — Complete Source of Truth
- [999_SEAL](./wiki/90_AUDITS/999_SEAL.md) — Constitutional state
- [FASTMCP CLI Guide](./wiki/80_INTEGRATION/FASTMCP_CLI_GUIDE.md) — CLI operations
- [Deployment Checklist](./DEPLOYMENT_CHECKLIST.md) — Detailed checklist

---

*Last verified: 2026-04-09 01:37 UTC*
*Constitutional State: DITEMPA BUKAN DIBERI — 999 SEAL*
