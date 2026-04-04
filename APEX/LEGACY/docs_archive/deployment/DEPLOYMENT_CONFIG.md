# arifOS MCP Server — Deployment Configuration

**Last Updated:** 2026-02-03 (v55.5 deployment)  
**Status:** ✅ PRODUCTION LIVE at https://aaamcp.arif-fazil.com

---

## ⚡ Quick Reference — Active Files Only

These are the ONLY files that matter for deployment:

```
/root/arifOS/
├── railway.toml          ← Railway configuration (DOCKERFILE builder)
├── Dockerfile            ← Docker build instructions
├── start_server.py       ← Entry point (called by railway.toml)
├── requirements.txt      ← Python dependencies
├── pyproject.toml        ← Package metadata
└── aaa_mcp/           ← Main application code
    ├── core/             ← Tool registry, session context
    ├── transports/       ← SSE, stdio transports
    ├── tools/            ← 9 canonical MCP tools
    └── services/         ← Rate limiting, metrics
```

---

## 🚫 DO NOT USE — Archived/Legacy Files

### Why These Are Dangerous

During v55.5 deployment, we learned that **having multiple config files causes Railway to pick the wrong one**. This led to 4+ hours of debugging.

### Files That Must Be Ignored

| File/Folder | Why It's Dangerous | What It Actually Is |
|-------------|-------------------|---------------------|
| `archive/deployment-backup/railway.json` | Uses Nixpacks with WRONG start command | Old Railway config (pre-Dockerfile) |
| `archive/deployment-backup/railway.toml` | Outdated paths | Old Railway config |
| `archive/deployment-backup/Dockerfile.old` | Old build steps | Pre-v55.5 Dockerfile |
| `archive/legacy-dashboards/railway.json` | Static site config, NOT MCP server | Portfolio website config |
| `archive/legacy-dashboards/Dockerfile` | nginx static server | Portfolio website build |
| `333_APPS/L4_TOOLS/mcp/` | Documentation snapshot | Old code reference, not runnable |

### How to Verify You're Using the Right Config

```bash
# Should ONLY show: ./railway.toml
git ls-files | grep railway

# Should show: ./Dockerfile
git ls-files | grep "^Dockerfile$"

# Should NOT show: mcp/ (should be aaa_mcp/)
ls -d mcp 2>/dev/null && echo "WRONG: mcp/ exists" || echo "OK: mcp/ removed"
```

---

## 🔧 Deployment Checklist

Before pushing to GitHub:

- [ ] Only `railway.toml` exists (no `railway.json`)
- [ ] Only `Dockerfile` exists at root (no `Dockerfile.old`)
- [ ] `aaa_mcp/` exists (not `mcp/`)
- [ ] `start_server.py` uses `aaa_mcp.*` imports
- [ ] Cache-bust comment updated in Dockerfile (if build changes)

### Pre-Deployment Verification Commands

```bash
# 1. One config file only
rm railway.json nixpacks.toml 2>/dev/null

# 2. No bad relative imports
grep -r "from \.\.\." --include="*.py" aaa_mcp/

# 3. Test imports locally
docker run --rm -v $(pwd):/app -w /app python:3.12-slim \
  sh -c "pip install -e . && python -c 'from mcp_server.core.tool_registry import ToolRegistry'"
```

---

## 🐛 Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `No module named mcp.X` | Local `mcp/` folder shadows PyPI | Rename to `aaa_mcp/` |
| `attempted relative import beyond top-level` | `...` import in mcp_server | Use absolute import from `codebase.X` |
| Wrong start command | `railway.json` overriding | Delete `railway.json` |
| Old code running | Docker cache | Update cache-bust timestamp |

---

## 📚 Documentation

- `docs/DEPLOYMENT_WISDOM.md` — Full post-mortem of v55.5 deployment crisis

---

## 🎯 What Each Active File Does

### `railway.toml`
Railway configuration. Tells Railway to:
- Use `DOCKERFILE` builder (not Nixpacks)
- Run `python start_server.py` on deploy
- Health check at `/health`

### `Dockerfile`
Builds the container:
- Installs Python dependencies
- Copies `aaa_mcp/` (not `mcp/`)
- Sets up health check
- Runs `start_server.py`

### `start_server.py`
Entry point:
- Imports from `mcp_server.core.tool_registry`
- Initializes 9 tools
- Starts SSE transport on port 8080

### `aaa_mcp/`
Main application (renamed from `mcp/` to avoid PyPI collision):
- `core/` — Tool registry, validators
- `transports/` — SSE, stdio
- `tools/` — 9 canonical MCP tools
- `services/` — Rate limiting, metrics

---

## ⚠️ Lessons Learned (The Hard Way)

1. **Never shadow PyPI packages** — `mcp/` collided with `pip install mcp`
2. **One config file only** — `railway.json` + `railway.toml` = confusion
3. **Absolute imports for cross-package** — `...` breaks when package is top-level
4. **Cache-bust when changing build** — Railway caches aggressively
5. **grep before assuming** — Removed `_trinity_` but left 3 references

---

## 🔗 Links

- **Live Endpoint:** https://aaamcp.arif-fazil.com/health
- **Status Check:** `curl -s https://aaamcp.arif-fazil.com/health | python -m json.tool`
- **Full Wisdom:** `docs/DEPLOYMENT_WISDOM.md`

---

*DITEMPA BUKAN DIBERI 💎🔥🧠*  
*Authority: 888_JUDGE*
