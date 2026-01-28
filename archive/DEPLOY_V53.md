# Deploying arifOS v53 AAA Cluster

**Status:** READY
**Architecture:** AAA Distributed Cluster (Gateway, Axis, Arif, Apex)

## Prerequisites
1. **Railway Account** (Logged in via CLI or Web)
2. **Git** (Authenticated)

## Deployment Steps

### 1. Push Code to GitHub
Your local repository is now hardened and configured. Push the changes to trigger the deployment pipeline.

```bash
git push origin main
```

### 2. Configure Railway Variables
Ensure your Railway project variables match the cluster configuration.

**Service: GATEWAY**
- `PORT`: 9000
- `AXIS_URL`: `http://axis:8001`
- `ARIF_URL`: `http://arif:8002`
- `APEX_URL`: `http://apex:8003`

**Service: AXIS (The Coordinator)**
- `PORT`: 8001
- `ARIFOS_ROLE`: `AXIS`

**Service: ARIF (The Mind/Heart)**
- `PORT`: 8002
- `ARIFOS_ROLE`: `ARIF`

**Service: APEX (The Judge)**
- `PORT`: 8003
- `ARIFOS_ROLE`: `APEX`

### 3. Verify Deployment
Once the build completes, check the health endpoint:
`https://your-gateway-url.up.railway.app/health`

## Troubleshooting
- **Build Failures:** Check the Build Logs. Ensure `pyproject.toml` dependencies are resolving.
- **Connection Refused:** Ensure `GATEWAY` can reach internal services on their private ports.
