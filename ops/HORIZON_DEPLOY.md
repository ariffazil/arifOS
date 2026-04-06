# Horizon Deployment

**Generated:** 2026-04-06  
**Commit:** 3d51d80  
**Status:** READY FOR DEPLOY

---

## Quick Deploy (UI)

1. Go to: https://horizon.prefect.io/arifos/servers/arifOS/settings
2. Configure environment variables (see below)
3. Deploy from VPS: `./scripts/deploy-horizon.sh`

---

## Required Environment Variable

Add these 4 variable to Horizon UI:

| Key | Value | Sensitive |
|-----|-------|-----------|
| `ARIFOS_API_KEY` | `7a289dd5b7eb63881e3c2c206cf5ab4bc7a992f90b1cfc0095a678e16fb6d4f8` | ✅ |
| `ARIFOS_GOVERNANCE_SECRET` | `7ef08be152ef74496c5af2d8c11f91f7eeea9e021ec5f3e4f0f6ea3dc10767f1` | ✅ **CRITICAL** |
| `DATABASE_URL` | `postgresql://arifos_admin:postgres-secret-2026@arifos_postgres:5432/arifos_vault` | ✅ |
| `REDIS_URL` | `redis://redis:6379/0` | ❌ |

**⚠️ WARNING:** `ARIFOS_GOVERNANCE_SECRET` must **never change** — F11 continuity anchor.

---

## Recommended Environment Variable

| Key | Value | Purpose |
|-----|-------|---------|
| `ARIFOS_VERSION` | `2026.03.25` | Version tag |
| `ARIFOS_PUBLIC_TOOL_PROFILE` | `public` | Tool exposure level |
| `ARIFOS_ML_FLOORS` | `1` | Enable SBERT constitutional scoring |
| `AAA_MCP_TRANSPORT` | `http` | HTTP transport mode |
| `STORAGE_ENCRYPTION_KEY` | `ARSGMiZo0e5cqQ_pQysJOEqnZEvqMO4mSsCQaSm3wHE=` | Payload encryption |
| `PYTHONUNBUFFERED` | `1` | Safer logging |

---

## Optional: LLM Provider Key

Add your actual API key for provider you want to use:

- `ANTHROPIC_API_KEY` — Claude model
- `OPENAI_API_KEY` — GPT model  
- `GEMINI_API_KEY` — Google Gemini
- `HF_TOKEN` — HuggingFace
- `KIMI_API_KEY` — Moonshot
- `VENICE_API_KEY` — Venice AI
- `OPENROUTER_API_KEY` — OpenRouter

---

## Optional: Vector Memory

```env
QDRANT_URL=http://qdrant:6333
VECTOR_SIZE=1024
```

---

## Optional: Web Search / Reality Tool

```env
BRAVE_API_KEY=your_key_here
JINA_API_KEY=your_key_here
PPLX_API_KEY=your_key_here
FIRECRAWL_API_KEY=your_key_here
```

---

## Deployment Command

```bash
cd /root/arifOS
./scripts/deploy-horizon.sh
```

Or manually:

```bash
cd /root/arifOS
prefect cloud login
prefect work-pool create arifos-pool --type prefect:managed
prefect deploy --prefect-file prefect.yaml
```

---

## Verification Checklist

After deploy, verify:

- [ ] `https://arifosmcp.arif-fazil.com/health` returns 200
- [ ] `mode` is `streamable-http`
- [ ] `tools_loaded` shows 44
- [ ] All 4 hard-required variable are set

---

## Expected Response Example

### /health
```json
{
  "status": "healthy",
  "service": "arifos-aaa-mcp",
  "version": "2026.03.25",
  "transport": "streamable-http",
  "tools_loaded": 44,
  "ml_floors": {
    "ml_floors_enabled": true,
    "ml_model_available": true,
    "ml_method": "sbert"
  }
}
```

---

## Current Deployment Status

| Component | Status | URL |
|-----------|--------|-----|
| VPS arifosmcp | ✅ healthy | http://localhost:8080/health |
| Public endpoint | ✅ responding | https://arifosmcp.arif-fazil.com/health |
| Traefik routing | ✅ fixed | Container on arifos_arifos_trinity network |

---

## Troubleshooting

If deploy fail:
1. Check `ARIFOS_GOVERNANCE_SECRET` is set and not rotated
2. Verify database connection string
3. Ensure Redis is reachable
4. Check Prefect Cloud login: `prefect cloud login`

---

**ΔΩΨ | DITEMPA BUKAN DIBERI**
