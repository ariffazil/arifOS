# arifOS MCP → Prefect Horizon Configuration

## 🔴 HARD-REQUIRED (4 Variables)

| Key | Description | How to Generate |
|-----|-------------|-----------------|
| `ARIFOS_API_KEY` | API auth at HTTP edge | `openssl rand -hex 32` |
| `ARIFOS_GOVERNANCE_SECRET` | F11 continuity anchor | `openssl rand -hex 32` |
| `DATABASE_URL` | PostgreSQL connection for Vault-999 | See below |
| `REDIS_URL` | Redis session cache | `redis://host:6379/0` |

### Example Values

```env
ARIFOS_API_KEY=7a289dd5b7eb63881e3c2c206cf5ab4bc7a992f90b1cfc0095a678e16fb6d4f8
ARIFOS_GOVERNANCE_SECRET=7ef08be152ef74496c5af2d8c11f91f7eeea9e021ec5f3e4f0f6ea3dc10767f1
DATABASE_URL=postgresql://arifos_admin:postgres-secret-2026@arifos_postgres:5432/arifos_vault
REDIS_URL=redis://redis:6379/0
```

**⚠️ CRITICAL:** `ARIFOS_GOVERNANCE_SECRET` must **never change** — it signs all governance tokens.

## 🟡 STRONGLY RECOMMENDED

| Key | Value | Purpose |
|-----|-------|---------|
| `ARIFOS_VERSION` | `2026.03.25` | Version tag |
| `ARIFOS_PUBLIC_TOOL_PROFILE` | `public` | Tool exposure level |
| `ARIFOS_ML_FLOORS` | `1` | Enable SBERT scoring |
| `AAA_MCP_TRANSPORT` | `http` | HTTP transport mode |
| `STORAGE_ENCRYPTION_KEY` | (base64) | Payload encryption |
| `PYTHONUNBUFFERED` | `1` | Safer logging |

## 🟢 LLM PROVIDERS (Set what you use)

Add your actual API keys for providers you want to use:

- `ANTHROPIC_API_KEY` — Claude models
- `OPENAI_API_KEY` — GPT models  
- `GEMINI_API_KEY` — Google Gemini
- `HF_TOKEN` — HuggingFace
- `KIMI_API_KEY` — Moonshot
- `VENICE_API_KEY` — Venice AI
- `OPENROUTER_API_KEY` — OpenRouter

## 🔵 VECTOR MEMORY

```env
QDRANT_URL=http://qdrant:6333
VECTOR_SIZE=1024
```

## 🟣 OPTIONAL: WEB SEARCH

```env
BRAVE_API_KEY=your_key_here
JINA_API_KEY=your_key_here
PPLX_API_KEY=your_key_here
FIRECRAWL_API_KEY=your_key_here
```

## 🚀 Deployment

1. Go to: `https://horizon.prefect.io/arifos/servers/arifOS/settings/environment-variables`
2. Add the 4 hard-required variables (mark secrets as Sensitive)
3. Add your LLM provider keys
4. Deploy from VPS:

```bash
cd /root/arifOS
prefect cloud login
prefect work-pool create arifos-pool --type prefect:managed
prefect deploy --prefect-file prefect.yaml
```

**ΔΩΨ | DITEMPA BUKAN DIBERI**
