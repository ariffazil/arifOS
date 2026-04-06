# ChatGPT Actions Deployment Package

This package targets ChatGPT Custom GPT Actions using arifOS via REST (not MCP).

## Public endpoints

- OpenAPI schema: `GET /openapi.json`
- Health probe: `GET /health`
- Action endpoint: `POST /checkpoint`

## Expected base URL

- Production: `https://arifosmcp.arif-fazil.com`

## Quick verification

```bash
curl -fsS https://arifosmcp.arif-fazil.com/health
curl -fsS https://arifosmcp.arif-fazil.com/openapi.json
curl -fsS -X POST https://arifosmcp.arif-fazil.com/checkpoint \
  -H "Content-Type: application/json" \
  -d '{"task":"Explain photosynthesis","mode":"full"}'
```

## Optional auth

If `ARIFOS_API_KEY` is set in deployment, include:

```bash
-H "Authorization: Bearer <ARIFOS_API_KEY>"
```

## CORS

Default allowed origins now include:

- `https://chat.openai.com`
- `https://chatgpt.com`

Override via `ARIFOS_ALLOWED_ORIGINS` if needed.

