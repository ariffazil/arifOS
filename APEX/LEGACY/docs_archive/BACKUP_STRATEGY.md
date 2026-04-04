# arifOS Dual Backup Strategy (Local + Cloud)

**Resilience Protocol:** "Two is One, One is None"

To ensure arifOS is always available regardless of internet connectivity (e.g., unstable WiFi), we maintain two operational modes.

## 1. Local Server (Iron Backup)
**Use when:** Internet is down, unstable, or for low-latency development.
**Infrastructure:** Docker running locally on your Windows machine.

### How to Start
```powershell
# In terminal:
docker run -p 8000:8000 arifos-api:v49
```
*Note: Requires Docker Desktop to be running.*

### Verification
- Health Check: `http://localhost:8000/health`
- MCP Endpoint: `http://localhost:8000/sse`

---

## 2. Cloud Server (Sovereign Uplink)
**Use when:** On mobile, different device, or need permanent availability.
**Infrastructure:** Cloud Run / Railway (Remote).

### Current Status
- **URL:** `https://vault999.arif-fazil.com` (Cloudflare Tunnel)
- **Backup:** `https://arifos-production.up.railway.app`

---

## 3. Switching Modes (Client Side)
To switch your agent (Claude/Gemini) between Local and Cloud:

### In `claude_desktop_config.json`:

**Local Mode:**
```json
"mcpServers": {
  "arifos": {
    "command": "docker",
    "args": ["run", "-i", "--rm", "arifos-api:v49"]
  }
}
```

**Cloud Mode:**
```json
"mcpServers": {
  "arifos": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sse", "https://vault999.arif-fazil.com/sse"]
  }
}
```

**Auto-Failover:**
Start Local. If it fails, enable Cloud config.
