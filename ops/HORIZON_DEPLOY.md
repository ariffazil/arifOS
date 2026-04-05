# Horizon Deployment Package

**Generated:** 2026-04-03  
**Commit:** 7fe0f26  
**Status:** READY FOR DEPLOY

## Quick Deploy (UI)

1. Go to: https://horizon.prefect.io
2. Sign in with GitHub
3. Click "New Deployment"
4. Select: `ariffazil/arifOS`
5. Branch: `main`
6. Entrypoint: `server.py:mcp`
7. Port: `8000`

## Environment Variables

```bash
ARIFOS_DEPLOYMENT=horizon
ARIFOS_VPS_URL=https://arifosmcp.arif-fazil.com
ARIFOS_VERSION=2026.03.25
ARIFOS_ENABLE_CORS=true
ARIFOS_RATE_LIMIT_ENABLED=true
ARIFOS_RATE_LIMIT_CAPACITY=120
ARIFOS_RATE_LIMIT_REFILL_PER_SEC=2.0
```

## Verification Checklist

After deploy, verify:

- [ ] `https://<your-app>.fastmcp.app/health` returns 200
- [ ] `https://<your-app>.fastmcp.app/metadata` shows tool counts
- [ ] `mode` is "horizon_gateway"
- [ ] `upstream_vps.status` is "reachable"

## Expected Response Examples

### /health
```json
{
  "status": "ok",
  "mode": "horizon_gateway",
  "version": "2026.03.25",
  "entrypoint": "server.py:mcp",
  "tool_policy": {
    "public": 21,
    "authenticated": 9,
    "sovereign_only": 12
  },
  "upstream_vps": {
    "status": "reachable"
  }
}
```

### /metadata
```json
{
  "gateway": {
    "name": "arifOS Horizon Gateway",
    "entrypoint": "server.py:mcp"
  },
  "tool_policy": {
    "counts": { "public": 21, "authenticated": 9, "sovereign_only": 12 }
  }
}
```

## Custom Domain (Optional)

To use `horizon.arif-fazil.com`:
1. In Horizon UI → Settings → Domain
2. Add custom domain
3. Set CNAME in Cloudflare: `horizon.arif-fazil.com` → `<auto>.fastmcp.app`

## Troubleshooting

If deploy fails:
1. Check `server.py` imports without errors: `python3 -c "from server import mcp"`
2. Verify `fastmcp.json` is valid JSON
3. Ensure `ARIFOS_DEPLOYMENT=horizon` is set
