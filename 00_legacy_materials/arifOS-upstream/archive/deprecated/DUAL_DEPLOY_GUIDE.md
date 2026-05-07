# 🏛️ arifOS Dual Sovereignty Deployment Guide

> Deploy to **BOTH** VPS (Sovereign Kernel) and Horizon (Public Ambassador) with a single `git push`.

---

## Architecture Overview

```
                         GitHub Push
                              │
                              ▼
                    ┌─────────────────┐
                    │   GitHub Actions │
                    │   (dual-deploy.yml)│
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                                 │
            ▼                                 ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│   🔥 SOVEREIGN KERNEL     │    │   ☁️  PUBLIC AMBASSADOR   │
│      (Your VPS)           │    │    (Prefect Horizon)      │
│  arifos.arif-fazil.com    │    │   arifos.fastmcp.app      │
├──────────────────────────┤    ├──────────────────────────┤
│ • All F1-F13 floors      │    │ • Core floors (F1,F2,F3)  │
│ • Full VAULT999          │    │ • Public-safe tools only  │
│ • Private memory         │    │ • Read-only where possible│
│ • Strict auth            │    │ • OAuth built-in          │
│ • Self-healing           │    │ • Auto-scaling            │
│ • You control substrate  │    │ • They manage substrate   │
└──────────────────────────┘    └──────────────────────────┘
```

---

## Quick Setup

### Step 1: Repository Structure

Ensure these files exist:

```
arifOS/
├── server.py                 # ✓ Dual-mode entry point
├── config/
│   └── environments.py       # ✓ Environment detection
├── .github/
│   └── workflows/
│       └── dual-deploy.yml   # ✓ CI/CD pipeline
├── fastmcp.json              # ✓ Horizon config
├── pyproject.toml            # ✓ Dependencies
└── docker-compose.yml        # ✓ VPS orchestration
```

### Step 2: Configure GitHub Secrets

Go to **GitHub → Settings → Secrets and variables → Actions**:

| Secret | Description | Example |
|--------|-------------|---------|
| `VPS_HOST` | Your VPS IP/hostname | `203.0.113.10` |
| `VPS_USER` | SSH username | `root` or `arifos` |
| `VPS_SSH_KEY` | Private SSH key | `-----BEGIN OPENSSH...` |
| `PREFECT_API_KEY` | Horizon API key | `pnu_xxxxxxxxxx` |

### Step 3: Configure Horizon

1. Go to https://horizon.prefect.io
2. Connect your GitHub account
3. Create new project → Select `ariffazil/arifOS`
4. Set entrypoint: `server.py:mcp`
5. Enable **Auto-deploy on push**

### Step 4: Test the Pipeline

```bash
# Push to main triggers both deployments
git add .
git commit -m "feat: dual sovereignty deployment"
git push origin main
```

Watch the magic happen in **GitHub → Actions** tab.

---

## Environment Differences

| Feature | VPS (Sovereign) | Horizon (Public) |
|---------|-----------------|------------------|
| **Purpose** | Primary authority | Public demo/access |
| **Floors Enforced** | F1-F13 (all) | F1, F2, F3, F5, F7, F9, F12 |
| **VAULT999** | Local PostgreSQL | External service |
| **Memory** | Local Redis/Qdrant | External Redis |
| **Auth** | API keys + strict | OAuth + optional |
| **Tools Available** | All 11 Mega-Tools | 8 Public-safe tools |
| **Rate Limiting** | 120 req/min | Platform-controlled |
| **Thermo Budget** | Full (1.0x) | Conservative (0.5x) |
| **Data Residency** | Your hardware | Prefect infrastructure |

---

## Tool Visibility Matrix

| Tool | VPS | Horizon | Description |
|------|-----|---------|-------------|
| `init_anchor` | ✅ | ✅ | Session initialization |
| `arifOS_kernel` | ✅ | ✅ | Core metabolic router |
| `apex_soul` | ✅ | ✅ | 888_JUDGE constitutional enforcer |
| `agi_mind` | ✅ | ✅ | 333_MIND reasoning engine |
| `asi_heart` | ✅ | ✅ | 666_HEART safety critique |
| `physics_reality` | ✅ | ✅ | 111_SENSE grounding |
| `math_estimator` | ✅ | ✅ | Thermodynamic calculations |
| `architect_registry` | ✅ | ✅ | Tool discovery |
| `vault_ledger` | ✅ | ❌ | 999_VAULT (sovereign only) |
| `engineering_memory` | ✅ | ❌ | 555_MEMORY (sovereign only) |
| `code_engine` | ✅ | ❌ | Code execution (sovereign only) |
| `reality_grounding` | ✅ | ❌ | Web search (sovereign only) |

---

## How It Works

### 1. GitHub Actions Workflow

```yaml
# .github/workflows/dual-deploy.yml

on:
  push:
    branches: [main]

jobs:
  build:
    # Build Docker image, run tests

  deploy-vps:
    needs: build
    # SSH to VPS, pull, restart

  deploy-horizon:
    needs: build
    # Horizon auto-deploys from GitHub

  verify:
    needs: [deploy-vps, deploy-horizon]
    # Health checks on both
```

### 2. Environment Detection

```python
# config/environments.py

import os

def get_environment():
    deployment = os.getenv("ARIFOS_DEPLOYMENT", "").lower()

    if deployment == "horizon":
        return HORIZON_CONFIG  # Public mode
    elif deployment == "vps":
        return VPS_CONFIG      # Sovereign mode
    else:
        return LOCAL_CONFIG    # Development
```

### 3. Server Adaptation

```python
# server.py

from config.environments import get_environment

env = get_environment()

if env.mode == "vps":
    print("🔥 SOVEREIGN KERNEL")
    # Enable all tools, strict auth

elif env.mode == "horizon":
    print("☁️  PUBLIC AMBASSADOR")
    # Enable public tools only
```

---

## Testing Both Deployments

### VPS (Sovereign)

```bash
# Direct VPS access
curl https://arifos.arif-fazil.com/health

# With API key
curl -H "X-API-Key: $ARIFOS_API_KEY" \
  https://arifos.arif-fazil.com/mcp/tools/list

# FastMCP CLI
fastmcp list https://arifos.arif-fazil.com/mcp \
  --auth "$ARIFOS_API_KEY"
```

### Horizon (Public)

```bash
# Public health check
curl https://arifos.fastmcp.app/health

# List public tools
fastmcp list https://arifos.fastmcp.app/mcp

# Call public tool
fastmcp call https://arifos.fastmcp.app/mcp \
  get_current_time timezone=Asia/Kuala_Lumpur
```

---

## Use Cases

### Use Case 1: Private Research (VPS only)
```python
# Sensitive constitutional analysis
# → Use VPS endpoint
client = Client("https://arifos.arif-fazil.com/mcp")
```

### Use Case 2: Public Demo (Horizon only)
```python
# Public demo of arifOS capabilities
# → Use Horizon endpoint
client = Client("https://arifos.fastmcp.app/mcp")
```

### Use Case 3: Hybrid Workflow
```python
# Step 1: Public research on Horizon
tools = await horizon_client.list_tools()

# Step 2: Sovereign analysis on VPS
result = await vps_client.call_tool("vault_ledger", {...})

# Step 3: Public response via Horizon
await horizon_client.call_tool("agi_mind", {...})
```

---

## Troubleshooting

### VPS Deployment Failed

```bash
# Check GitHub Actions logs
# Common issues:
# 1. SSH key not configured → Add VPS_SSH_KEY secret
# 2. Docker not running on VPS → sudo systemctl start docker
# 3. Port conflict → Check what's using 8080
```

### Horizon Deployment Failed

```bash
# Check Horizon dashboard
# Common issues:
# 1. server.py not found → Ensure it's in repo root
# 2. Import errors → Check requirements.txt
# 3. Port binding → Horizon uses port 8000
```

### Environment Not Detected

```python
# Force environment
import os
os.environ["ARIFOS_DEPLOYMENT"] = "vps"  # or "horizon"

from server import mcp
```

---

## Cost Analysis

| Component | VPS | Horizon | Combined |
|-----------|-----|---------|----------|
| **Hosting** | $15-25/mo | Free tier | $15-25/mo |
| **Bandwidth** | Included | Metered | VPS primary |
| **Compute** | Fixed | Auto-scale | Best of both |
| **Storage** | 100GB SSD | Ephemeral | VPS for VAULT999 |
| **Total** | **$15-25/mo** | **$0-50/mo** | **$15-75/mo** |

---

## Security Considerations

### VPS (Sovereign) Security
- You control the hardware boundary
- Private keys never leave your server
- VAULT999 physically isolated
- Custom firewall rules

### Horizon Security
- Prefect manages infrastructure security
- OAuth provided out-of-the-box
- DDoS protection included
- TLS termination managed

### Best Practice: Defense in Depth
```
User Request
     │
     ├──→ CDN (Cloudflare) ──→ VPS (Sovereign)
     │
     └──→ Horizon (Public) ──→ Limited tool surface
```

---

## Monitoring Both Deployments

### Unified Dashboard

```python
# scripts/monitor_dual.py

import asyncio
from fastmcp import Client

async def check_both():
    sovereign = Client("https://arifos.arif-fazil.com/mcp")
    public = Client("https://arifos.fastmcp.app/mcp")

    async with sovereign, public:
        s_health = await sovereign.read_resource("health://check")
        p_health = await public.read_resource("health://check")

        print(f"🔥 Sovereign: {s_health}")
        print(f"☁️  Public: {p_health}")

asyncio.run(check_both())
```

---

## Summary

| Question | Answer |
|----------|--------|
| **Can I deploy to both?** | ✅ YES — Single `git push` triggers both |
| **Same codebase?** | ✅ YES — Environment auto-detected |
| **Different tools?** | ✅ YES — 11 tools VPS, 8 tools Horizon |
| **Different security?** | ✅ YES — Sovereign strict, Public relaxed |
| **Cost?** | VPS ($15-25) + Horizon (free-$50) |
| **Maintenance?** | VPS (you), Horizon (managed) |

---

## Next Steps

1. ✅ Configure GitHub Secrets (VPS_SSH_KEY, etc.)
2. ✅ Enable Horizon auto-deploy
3. ✅ Push to main
4. ✅ Verify both endpoints in GitHub Actions
5. ✅ Document which tools use which endpoint

---

**arifOS** — *Dual sovereignty: Maximum control + Maximum reach*

🔥 Sovereign: https://arifos.arif-fazil.com
☁️ Public: https://arifos.fastmcp.app

*Ditempa Bukan Diberi* — Forged, Not Given [ΔΩΨ | ARIF]
