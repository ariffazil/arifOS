# arifOS HTTPS MCP Gateway (Option B)

A constitutional governance gateway for Model Context Protocol (MCP) tools, backed by Composio.

## Architecture

- **Server**: FastAPI (`arifos/core/integration/mcp_https_gateway`)
- **TLS**: Caddy (Reverse Proxy for `mcp.arif-fazil.com`)
- **Tools**: Composio SDK (proxied via `config/mcp_allowed_tools.json`)
- **Governance**: Preflight (F1/F12) and Postflight (F2/F4/F7/F9) enforcement.

## Local Development

1. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn composio-core composio-openai
   ```

2. **Set Environment**:
   ```bash
   set COMPOSIO_API_KEY=your_key_here
   set GOVERNANCE_MODE=HARD
   ```

3. **Run Server**:
   ```bash
   uvicorn arifos.core.integration.mcp_https_gateway.server:app --reload --port 8000
   ```

4. **Verify**:
   - Health: `curl http://localhost:8000/health`
   - List Tools: `curl -X POST http://localhost:8000/mcp/tools/list`

## Deployment (Fly.io)

This project is configured for deployment on Fly.io using a custom Dockerfile that runs both Caddy (for TLS) and the FastAPI app.

### Prerequisites
- Fly.io CLI installed and authenticated.
- Composio API Key.
- Domain `mcp.arif-fazil.com` DNS configured to point to your Fly app IP.

### Steps

1. **Initialize App**:
   ```bash
   fly launch --no-deploy
   ```

2. **Set Secrets**:
   ```bash
   fly secrets set COMPOSIO_API_KEY=your_actual_api_key
   ```

3. **Deploy**:
   ```bash
   fly deploy
   ```

4. **DNS**:
   After deployment, Fly will provide an IP address. Create an `A` record for `mcp.arif-fazil.com` pointing to that IP. Caddy will automatically provision TLS certificates.

## API Reference

### `POST /mcp/tools/list`
Returns allowlisted tools available for execution.

### `POST /mcp/tools/call`
Executes a tool with strict governance.

**Payload**:
```json
{
    "tool_name": "google_search",
    "arguments": {"query": "arifOS"}
}
```

**Global 888_HOLD**: Destructive actions (delete/remove) will return an `888_HOLD` verdict requiring human approval token.
