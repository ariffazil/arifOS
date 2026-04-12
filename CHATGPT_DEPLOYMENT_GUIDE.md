# arifOS MCP ChatGPT Deployment Guide

## Problem

ChatGPT's MCP client returns error:
```json
{"jsonrpc":"2.0","id":"server-error","error":{"code":-32600,"message":"Not Acceptable: Client must accept text/event-stream"}}
```

**Root Cause:** The server uses MCP's "streamable-http" transport which requires clients to accept SSE (Server-Sent Events). ChatGPT's MCP client doesn't properly negotiate SSE headers.

## Solution Options

### Option 1: Use REST API Endpoints (Recommended for Now)

ChatGPT can use the working REST endpoints directly:

```
GET  https://arifosmcp.arif-fazil.com/tools       - List all tools
GET  https://arifosmcp.arif-fazil.com/health      - Server health
POST https://arifosmcp.arif-fazil.com/mcp         - MCP endpoint (requires SSE)
```

**Working Example:**
```bash
curl https://arifosmcp.arif-fazil.com/tools
```

### Option 2: Configure ChatGPT with Proper Headers

If ChatGPT allows custom headers, add:
```
Accept: application/json, text/event-stream
```

### Option 3: Deploy SSE-Compatible Proxy (Advanced)

Create a simple proxy that handles the SSE negotiation:

```python
# chatgpt_mcp_proxy.py
import requests
import json
import sys

def proxy_to_arifos(method, params=None):
    """Proxy MCP requests to arifOS with proper SSE handling."""
    url = "https://arifosmcp.arif-fazil.com/mcp"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    payload = {
        "jsonrpc": "2.0",
        "id": "chatgpt-proxy",
        "method": method,
        "params": params or {}
    }
    
    response = requests.post(url, headers=headers, json=payload, stream=True)
    
    # Parse SSE response
    for line in response.iter_lines():
        if line.startswith(b"data: "):
            return json.loads(line[6:])
    
    return None

if __name__ == "__main__":
    # Read JSON-RPC from stdin (ChatGPT format)
    request = json.loads(sys.stdin.readline())
    result = proxy_to_arifos(request.get("method"), request.get("params"))
    print(json.dumps(result))
```

### Option 4: Use STDIO Mode (Local Only)

For local ChatGPT usage via CLI:

```bash
# From .github/mcp/start-arifos-stdio.sh
cd /root/arifOS
source .venv/bin/activate
python ops/runtime/stdio_server.py
```

## Current Deployment Status

| Endpoint | Status | ChatGPT Compatible |
|----------|--------|-------------------|
| `/health` | ✅ Working | ✅ Yes (GET) |
| `/tools` | ✅ Working | ✅ Yes (GET) |
| `/mcp` | ✅ Working | ❌ No (requires SSE) |
| `/metadata` | ✅ Working | ✅ Yes (GET) |

## Server Configuration

**Current Transport:** `streamable-http` with `stateless_http=True`  
**Ports:** 8080 (HTTP), 8089 (SSE - not actively used)  
**Docker:** `arifos/arifosmcp:latest`  
**Nginx:** Proxies `/mcp` and `/sse` to container

## Recommended ChatGPT Integration

For immediate ChatGPT integration, use the REST API pattern:

1. **Discovery:** `GET /tools` - Get available tools
2. **Health Check:** `GET /health` - Verify server status
3. **Tool Execution:** Use individual tool endpoints if exposed, or wrap MCP calls

## Fix Applied

Changed server.py:
```python
# Before:
app = mcp.http_app(stateless_http=False)  # Required SSE

# After:
app = mcp.http_app(stateless_http=True)   # Stateless mode
```

This allows the server to work without maintaining session state, but still requires SSE Accept header due to streamable-http spec.

## Next Steps

1. **Option A:** Create a ChatGPT-specific wrapper endpoint
2. **Option B:** Configure ChatGPT Apps SDK with proper headers
3. **Option C:** Deploy separate HTTP-only MCP server instance

---

**999 SEAL** — Deployed with stateless HTTP mode
