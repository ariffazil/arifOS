# arifOS MCP Quick Start
# TL;DR - Get Running in 5 Minutes

**Choose Your Path:** [Local](#local-5-minutes) | [Cloud](#cloud-15-minutes)

---

## Local (5 Minutes)

### 1. Install Dependencies
```bash
cd C:\Users\User\OneDrive\Documents\GitHub\arifOS
pip install -r requirements.txt
```

### 2. Configure Claude Code

**Windows:** Edit `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "arifos_core.mcp", "stdio"],
      "cwd": "C:\\Users\\User\\OneDrive\\Documents\\GitHub\\arifOS",
      "env": {
        "ARIFOS_ALLOW_LEGACY_SPEC": "1",
        "PYTHONPATH": "C:\\Users\\User\\OneDrive\\Documents\\GitHub\\arifOS"
      }
    }
  }
}
```

### 3. Start Claude Code
```bash
claude
```

### 4. Test
```
Use get_constitutional_metrics tool
```

✅ **Done!** You now have 17 arifOS tools available.

---

## Cloud (15 Minutes)

### 1. Create Deployment Files

Files already created:
- ✅ `Procfile`
- ✅ `railway.json`
- ✅ `runtime.txt`
- ✅ `.railway-env`

### 2. Deploy to Railway

**Option A - CLI:**
```bash
npm i -g @railway/cli
railway login
railway link
railway up
```

**Option B - GitHub:**
1. Push to GitHub
2. Railway Dashboard → New Project → Deploy from GitHub
3. Select `arifOS` repo

### 3. Configure Environment Variables

In Railway dashboard, add:
```
ARIFOS_ALLOW_LEGACY_SPEC=1
ARIFOS_PHYSICS_DISABLED=1
PORT=8000
```

### 4. Set Up Custom Domain

**CloudFlare DNS:**
```
Type:   CNAME
Name:   mcp
Target: arifos-production.up.railway.app
Proxy:  ✅ Proxied
```

**Railway:**
- Settings → Domains → Add: `mcp.arif-fazil.com`

### 5. Update Claude Code Config

```json
{
  "mcpServers": {
    "arifos-cloud": {
      "url": "https://aaamcp.arif-fazil.com/mcp",
      "transport": "streamable-http"
    }
  }
}
```

### 6. Test
```bash
curl https://aaamcp.arif-fazil.com/health
```

✅ **Done!** Cloud MCP server running.

---

## Test Deployment

### Local Test
```bash
python -m arifos_core.mcp stdio
# Should show: "Starting arifOS Unified MCP Server..."
```

### Cloud Test
```bash
# Start local SSE server
python -m arifos_core.mcp sse

# In another terminal, test
python test_cloud_deployment.py

# Then deploy to Railway
```

---

## Available Tools (17)

| Tool | Purpose |
|------|---------|
| `arifos_live` | Full constitutional pipeline |
| `agi_think` | AGI reasoning |
| `asi_act` | ASI empathy |
| `apex_seal` | APEX judgment |
| `agi_search` | Constitutional search (truth) |
| `asi_search` | Constitutional search (empathy) |
| `vault999_query` | Memory query |
| `vault999_store` | Memory storage |
| `vault999_seal` | Memory verification |
| `fag_read` | Governed file read |
| `fag_write` | Governed file write |
| `fag_list` | Governed directory list |
| `fag_stats` | Governance metrics |
| `arifos_executor` | Shell execution |
| `github_govern` | GitHub operations |
| `arifos_meta_select` | Verdict aggregation |
| `get_constitutional_metrics` | Floor metrics |

---

## Troubleshooting

### "Module not found"
```bash
set PYTHONPATH=C:\Users\User\OneDrive\Documents\GitHub\arifOS
```

### "Server won't start"
```bash
pip install -r requirements.txt --upgrade
```

### "Can't connect to cloud"
```bash
# Check Railway logs
railway logs

# Test health endpoint
curl https://arifos-production.up.railway.app/health
```

---

## Full Documentation

- **Complete Guide:** `CLAUDE_CODE_MCP_SETUP_GUIDE.md`
- **CloudFlare Setup:** `CLOUDFLARE_DNS_SETUP.md`
- **MCP Quickstart:** `MCP_QUICKSTART_GUIDE.md`

---

**DITEMPA BUKAN DIBERI** 🔥

**Status:** v47.0.0 | SEALED ✅
