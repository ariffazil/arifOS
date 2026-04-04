# Railway Quick Start - arifOS v50 MCP Server

**🚀 Deploy in 5 Minutes**

---

## Step 1: Add Required Variables

Copy-paste these into Railway → Service → Variables:

```bash
# MCP Configuration (REQUIRED)
AAA_MCP_TRANSPORT=http
AAA_MCP_PORT=8000
AAA_MCP_LLM_PROVIDER=auto

# Core Settings (REQUIRED)
ARIFOS_ENV=production
ARIFOS_ALLOW_LEGACY_SPEC=1
ARIFOS_PHYSICS_DISABLED=0

# Constitutional Governance (REQUIRED)
FLOOR_ENFORCEMENT_MODE=strict
GOVERNANCE_MODE=HARD
TRINITY_ENABLED=true

# Logging (OPTIONAL)
LOG_LEVEL=info
```

---

## Step 2: Add API Keys (as Secrets 🔒)

Click the 🔒 icon to mark as secret:

```bash
# Choose your LLM provider
OPENAI_API_KEY=sk-...        # OpenAI GPT models
# OR
ANTHROPIC_API_KEY=sk-ant-... # Claude models
# OR
GROQ_API_KEY=gsk_...         # Fast inference
```

---

## Step 3: Add Database Services

### PostgreSQL (Ledger)
1. Railway → "New" → "Database" → "Add PostgreSQL"
2. ✅ Auto-creates `DATABASE_URL` variable

### Redis (Cache)
1. Railway → "New" → "Database" → "Add Redis"
2. ✅ Auto-creates `REDIS_URL` variable

---

## Step 4: Delete These Variables

❌ Remove if present (Railway manages these):

```bash
POSTGRES_DB          # Use DATABASE_URL instead
POSTGRES_USER        # Use DATABASE_URL instead
POSTGRES_PASSWORD    # Use DATABASE_URL instead
POSTGRES_PORT        # Use DATABASE_URL instead
REDIS_PORT           # Use REDIS_URL instead
BUILD_DATE           # Use RAILWAY_GIT_COMMIT_SHA instead
VCS_REF              # Use RAILWAY_GIT_COMMIT_SHA instead
RENDER               # Not needed for Railway
```

❌ Delete placeholder tokens:
```bash
CLOUDFLARE_TUNNEL_TOKEN  # Only if using Cloudflare
```

---

## Step 5: Deploy

Railway auto-deploys on push to GitHub.

**Check deployment**:
```bash
curl https://your-app.up.railway.app/health
```

Expected:
```json
{"status": "healthy", "tools": 33}
```

---

## Step 6: Connect MCP Client

Update `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "arifos-remote": {
      "transport": {
        "type": "sse",
        "url": "https://your-app.up.railway.app/sse"
      }
    }
  }
}
```

---

## ✅ Done!

Your arifOS MCP server is now accessible from anywhere.

**API Docs**: `https://your-app.up.railway.app/docs`

---

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check `requirements.txt` includes all deps |
| Database timeout | Add Railway PostgreSQL plugin |
| Tools return VOID | Check API keys are set correctly |
| Can't connect | Verify Railway URL in MCP config |

---

**Full Guide**: See `RAILWAY_DEPLOYMENT.md`
