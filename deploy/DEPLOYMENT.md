# AAA MCP Deployment Guide (v50.5.24)

**arifOS Constitutional AI Governance Framework**

---

## Deployment Options

| Method | Transport | Use Case |
|--------|-----------|----------|
| Claude Desktop | stdio | Local development |
| Railway/Heroku | SSE | Production web |
| Docker | stdio/SSE | Containerized |

---

## Option 1: Claude Desktop (Local)

### Prerequisites

1. Python 3.10+
2. Claude Desktop installed
3. arifOS cloned locally

### Step 1: Clone and Install

```bash
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
pip install -e .
```

### Step 2: Test MCP Server

```bash
# Verify tools work
python -c "
import asyncio
from arifos.mcp.trinity_server import TOOLS

async def test():
    result = await TOOLS['000_init'](action='validate', query='test')
    print('000_init:', result.get('status'))

asyncio.run(test())
"
```

Expected output: `000_init: SEAL`

### Step 3: Configure Claude Desktop

**Location of config file:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Add this configuration:**

```json
{
  "mcpServers": {
    "arifos-aaa": {
      "command": "python",
      "args": ["-m", "arifos.mcp"],
      "cwd": "/absolute/path/to/arifOS",
      "env": {
        "PYTHONPATH": "/absolute/path/to/arifOS"
      }
    }
  }
}
```

**Important:** Replace `/absolute/path/to/arifOS` with your actual path.

### Step 4: Restart Claude Desktop

1. Quit Claude Desktop completely
2. Relaunch Claude Desktop
3. Check the MCP icon in the toolbar shows "arifos-aaa" connected

### Step 5: Verify Tools Available

In Claude Desktop, you should see these 5 tools:
- `000_init` - Gate (Authority + Injection Defense)
- `agi_genius` - Mind (SENSE → THINK → ATLAS → FORGE)
- `asi_act` - Heart (EVIDENCE → EMPATHY → ACT)
- `apex_judge` - Soul (EUREKA → JUDGE → PROOF)
- `999_vault` - Seal (Merkle + Immutable Log)

---

## Option 2: Railway (Production SSE)

### Prerequisites

1. Railway account (https://railway.app)
2. GitHub repository connected

### Step 1: Create Railway Project

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init
```

### Step 2: Configure Environment

Set these environment variables in Railway dashboard:

```
PORT=8000
AAA_MCP_PORT=8000
PYTHONUNBUFFERED=1
```

### Step 3: Deploy

```bash
# Deploy from git
railway up

# Or link to GitHub for auto-deploy
railway link
```

### Step 4: Verify Deployment

```bash
# Check health endpoint
curl https://your-app.railway.app/health

# Expected response:
# {"status": "healthy", "tools": 5, "server": "arifOS-Trinity-v50.5.0"}
```

### Step 5: Connect to Claude Desktop (Remote SSE)

```json
{
  "mcpServers": {
    "arifos-aaa-remote": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic/mcp-client-sse",
        "https://your-app.railway.app/sse"
      ]
    }
  }
}
```

---

## Option 3: Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

EXPOSE 8000

CMD ["python", "-m", "arifos.mcp", "trinity-sse"]
```

### Build and Run

```bash
# Build
docker build -t arifos-aaa-mcp .

# Run SSE mode (for web)
docker run -p 8000:8000 arifos-aaa-mcp

# Test
curl http://localhost:8000/health
```

---

## Final Testing Checklist

### Local (Claude Desktop)

- [ ] `pip install -e .` completes without errors
- [ ] `python -m arifos.mcp` starts without errors
- [ ] Claude Desktop shows "arifos-aaa" in MCP connections
- [ ] Can call `000_init` tool from Claude Desktop
- [ ] Can call `agi_genius` tool from Claude Desktop
- [ ] Can call `asi_act` tool from Claude Desktop
- [ ] Can call `apex_judge` tool from Claude Desktop
- [ ] Can call `999_vault` tool from Claude Desktop

### Remote (Railway/SSE)

- [ ] Railway deployment succeeds
- [ ] `/health` endpoint returns 200
- [ ] `/docs` endpoint shows API documentation
- [ ] SSE connection establishes successfully
- [ ] Tools respond through SSE transport

---

## Troubleshooting

### "Module not found" errors

```bash
# Ensure package is installed
pip install -e .

# Verify import works
python -c "from arifos.mcp.trinity_server import TOOLS; print(TOOLS.keys())"
```

### "Connection refused" in Claude Desktop

1. Check the path in `claude_desktop_config.json` is absolute
2. Verify Python is in PATH
3. Check Claude Desktop logs: `~/Library/Logs/Claude/`

### SSE connection fails

1. Verify the PORT environment variable is set
2. Check Railway logs for errors
3. Ensure `/health` endpoint responds

### Tool returns "VOID" unexpectedly

1. Check query for injection patterns
2. Verify session_id is passed correctly
3. Check for floor violations in response

---

## Support

- GitHub Issues: https://github.com/ariffazil/arifOS/issues
- Documentation: https://github.com/ariffazil/arifOS/blob/main/arifos/mcp/README.md

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given.
