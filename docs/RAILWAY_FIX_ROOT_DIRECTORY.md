# Railway Deployment Fix: Root Directory Error

**Error**: `Failed to read app source directory - No such file or directory (os error 2)`

**Root Cause**: Railway is building from `arifos/core/` instead of repository root

---

## 🚨 The Problem

Your Railway logs show:
```
root directory set as 'https:/github.com/ariffazil/arifOS/tree/main/arifos/core'
```

This is **incorrect**. Railway is trying to build from a subdirectory that doesn't contain the necessary files.

---

## ✅ Quick Fix (2 minutes)

### **Step 1: Change Root Directory in Railway Dashboard**

1. Open [Railway Dashboard](https://railway.app/dashboard)
2. Select your **arifOS service**
3. Click **"Settings"** tab (⚙️ icon)
4. Find **"Root Directory"** or **"Source Directory"** setting
5. **Current value**: `arifos/core` ❌
6. **Change to**: `.` (or leave blank) ✅
7. Save (auto-saves)

### **Step 2: Commit Updated Configuration**

I've updated your `railway.json` to use a simpler start command:

```bash
# Commit the fixed railway.json
git add railway.json
git commit -m "fix: correct Railway deployment configuration"
git push origin main
```

Railway will automatically trigger a new deployment.

---

## 📋 What Was Changed

### **File: `railway.json`**

**Before** (using bash script):
```json
{
  "deploy": {
    "startCommand": "bash scripts/railway_start_mcp.sh"
  }
}
```

**After** (direct uvicorn command):
```json
{
  "deploy": {
    "startCommand": "uvicorn arifos.core.mcp.sse:app --host 0.0.0.0 --port $PORT"
  }
}
```

**Why**: Direct command is more reliable on Railway's Nixpacks builder.

---

## 🔍 Verification

After the fix, Railway logs should show:

```
✅ root directory set as 'https:/github.com/ariffazil/arifOS/tree/main'
✅ found 'Procfile'
✅ found 'requirements.txt' or 'pyproject.toml'
✅ installing Python dependencies...
✅ starting server: uvicorn arifos.core.mcp.sse:app
✅ Application started on http://0.0.0.0:$PORT
```

**Test deployment**:
```bash
curl https://your-app.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "mode": "SSE",
  "tools": 33,
  "framework": "FastAPI"
}
```

---

## 🎯 Why This Matters

### **Correct Structure** (Building from root ✅)
```
Repository Root (Railway builds here)
├── arifos/                    ← Python package
│   └── core/
│       └── mcp/
│           └── sse.py
├── Procfile                   ← Railway finds this ✅
├── requirements.txt           ← Railway finds this ✅
├── railway.json               ← Railway finds this ✅
└── pyproject.toml             ← Railway finds this ✅

Import works: arifos.core.mcp.sse ✅
```

### **Incorrect Structure** (Building from arifos/core/ ❌)
```
arifos/core/ (Railway builds here - WRONG)
├── mcp/
│   └── sse.py
├── (No Procfile) ❌
├── (No requirements.txt) ❌
└── (No railway.json) ❌

Import fails: arifos.core.mcp.sse ❌
Error: "Failed to read app source directory"
```

---

## 🛠️ Alternative Fix Methods

### **Method 1: Via Railway CLI** (If installed)

```bash
railway service root-directory .
railway up
```

### **Method 2: Via Railway API**

```bash
# Get service ID
SERVICE_ID="your-service-id"
PROJECT_ID="your-project-id"

# Update root directory
curl -X PATCH "https://backboard.railway.app/graphql/v2" \
  -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -d '{
    "query": "mutation { serviceUpdate(id: \"'$SERVICE_ID'\", input: { rootDirectory: \".\" }) { id } }"
  }'
```

### **Method 3: Redeploy from GitHub** (Nuclear option)

1. Delete current Railway service
2. Create new service from GitHub
3. **Do NOT set root directory** (leave blank = uses root)

---

## 📝 Checklist

After making the fix:

- [ ] Railway root directory changed to `.` or blank
- [ ] `railway.json` updated (commit pushed)
- [ ] New deployment triggered
- [ ] Deployment logs show success
- [ ] Health endpoint responds: `curl https://your-app.up.railway.app/health`
- [ ] MCP tools accessible via `/sse` endpoint

---

## 🚀 Expected Deployment Timeline

```
1. Change root directory in Railway Dashboard   → 30 seconds
2. Commit and push updated railway.json         → 1 minute
3. Railway auto-triggers deployment             → Automatic
4. Build completes (install deps)               → 2-3 minutes
5. Server starts                                → 10 seconds
6. Health check passes                          → 5 seconds

Total: ~5 minutes
```

---

## ⚠️ Common Mistakes to Avoid

| Mistake | Consequence |
|---------|-------------|
| Root directory set to `arifos/` | Missing `Procfile`, wrong imports |
| Root directory set to `arifos/core/` | Current error |
| Root directory set to `src/` | Doesn't exist in your repo |
| Forgot to push `railway.json` changes | Old start command used |

**Correct setting**: `.` or blank (uses repository root)

---

## 📞 If Still Failing

Check Railway logs for these specific errors:

**Error 1**: `ModuleNotFoundError: No module named 'arifos'`
- **Fix**: Ensure root directory is `.` not `arifos/core/`
- **Verify**: Railway logs should show installing from `pyproject.toml`

**Error 2**: `FileNotFoundError: Procfile not found`
- **Fix**: Root directory should be `.` not a subdirectory
- **Verify**: `Procfile` is at repository root

**Error 3**: `uvicorn: command not found`
- **Fix**: Ensure `uvicorn` in `requirements.txt` or `pyproject.toml`
- **Verify**: Check Railway build logs for dependency installation

**Error 4**: `Port already in use`
- **Fix**: Use Railway's `$PORT` variable (already in `railway.json`)
- **Verify**: Start command includes `--port $PORT`

---

## ✅ Success Indicators

When deployment succeeds, you'll see:

**Railway Logs**:
```
[Build] Installing dependencies from pyproject.toml
[Build] Installed arifos
[Deploy] Starting: uvicorn arifos.core.mcp.sse:app
[Deploy] INFO:     Started server process
[Deploy] INFO:     Uvicorn running on http://0.0.0.0:8000
[Health] /health returned 200 OK
```

**Test Command**:
```bash
curl https://your-app.up.railway.app/health
# {"status":"healthy","tools":33}
```

**MCP Client Connection**:
```bash
# In .claude/mcp.json
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

**Status**: Ready to deploy after root directory fix
**Next**: Follow Step 1 above → Wait for deployment → Test health endpoint
