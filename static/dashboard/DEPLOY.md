# Dynamic Dashboard Deployment

## Overview
This dashboard auto-reflects your MCP server deployment by polling the `/health` and `/build` endpoints.

## Deployment Options

### Option 1: Static Hosting (Recommended)
Deploy to any static host (Cloudflare Pages, Vercel, GitHub Pages, Nginx):

```bash
# Copy dashboard to web root
sudo cp -r /root/arifOS/static/dashboard/* /var/www/arifosmcp/

# Or for Cloudflare Pages
npx wrangler pages deploy static/dashboard --project-name=arifosmcp
```

**CORS Required:** The dashboard fetches from `https://mcp.a-forge.io`. Add CORS headers:

```nginx
# In Nginx config for mcp.a-forge.io
location /health {
    add_header Access-Control-Allow-Origin "https://arifosmcp.arif-fazil.com" always;
    add_header Access-Control-Allow-Methods "GET" always;
}

location /build {
    add_header Access-Control-Allow-Origin "https://arifosmcp.arif-fazil.com" always;
    add_header Access-Control-Allow-Methods "GET" always;
}
```

### Option 2: Integrated with MCP Server
Serve dashboard from the MCP server itself:

```python
# Add to arifosmcp/runtime/server.py
from starlette.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="static/dashboard", html=True), name="dashboard")
```

Then access at `https://mcp.a-forge.io/`

### Option 3: Docker Compose (Full Stack)
Update `deployments/a-forge/docker-compose.yml`:

```yaml
services:
  dashboard:
    image: nginx:alpine
    volumes:
      - ../../static/dashboard:/usr/share/nginx/html:ro
    ports:
      - "80:80"
    depends_on:
      - arifos-mcp
```

## Configuration

Edit `index.html` to change:
- `MCP_BASE_URL` — Point to your MCP server
- `REFRESH_INTERVAL` — Auto-refresh frequency (default: 30s)

## Endpoints Used

| Endpoint | Data | Update Frequency |
|----------|------|------------------|
| `/health` | Status, mode, upstream | 30 seconds |
| `/build` | Version, SHA, tools | 30 seconds |

## Security Notes

- Dashboard is read-only (no write operations)
- CORS must be configured on MCP server
- No authentication required for public dashboard
- Sensitive data (secrets, private keys) never exposed
