# Deployment Wisdom: Lessons from the MCP Endpoint Wars

> **Context:** v55.5 deployment to Railway, February 2026  
> **Duration:** 4+ hours of iterative debugging  
> **Final Status:** ✅ DEPLOYED (9 tools, 13 floors, streamable HTTP)

---

## The Cascade of Failures

What looked like "Railway health check failing" was actually a **chain of 5 interconnected problems**, each masked by the previous:

### 1. Namespace Collision (The Invisible Shadow)

**Problem:** Local `mcp/` folder shadowed PyPI `mcp` package.

```python
# In container:
from mcp.server import Server  # Found local mcp/ (no server submodule)
# ImportError: No module named 'mcp.server'
```

**Why it happened:** Python path resolution prioritizes local folders over site-packages. When we renamed `mcp/` to `mcp_server/`, we broke our own code while fixing the collision.

**Lesson:** Never name local packages the same as PyPI dependencies. Use suffixes: `mcp_server`, `arifos_mcp`, etc.

---

### 2. Config File Proliferation (The Silent Override)

**Problem:** Railway was reading `railway.json` (Nixpacks, old start command) despite `railway.toml` specifying Dockerfile.

```
railway.json  →  NIXPACKS builder → python -m mcp.transports sse
railway.toml  →  DOCKERFILE builder → python start_server.py
```

Railway chose `railway.json`. The start command used the OLD import path (`mcp.transports` instead of `mcp_server.transports`).

**Lesson:** Delete legacy configs. One source of truth. When in doubt:
```bash
git ls-files | grep -E "(railway|nixpacks)"
# Archive or delete everything except your primary config
```

---

### 3. Relative Import Hell (The Dot Dot Dot)

**Problem:** `mcp_server/transports/stdio.py` used:
```python
from ...enforcement.metrics import ...  # 3 dots = above package root
```

When installed as editable package (`pip install -e .`), Python treated `mcp_server` as top-level. Three dots tried to escape the package → `ImportError`.

**Lesson:** Use absolute imports for cross-package references:
```python
# Bad (relative beyond package)
from ...enforcement.metrics import record_stage_metrics

# Good (absolute)
from codebase.enforcement.metrics import record_stage_metrics

# Good (relative within package)
from ..core.tool_registry import ToolRegistry  # 2 dots = mcp_server root
```

**Rule of thumb:** Max 2 dots (`..`) within a package. If you need 3+ dots, use absolute imports.

---

### 4. Cache Invalidation (The Ghost Build)

**Problem:** Railway's Docker layer caching kept using old build steps even after fixing `Dockerfile`.

The build log showed `COPY 000_THEORY/` which wasn't in the current Dockerfile — it was cached from Nixpacks.

**Lesson:** Force cache bust when changing build fundamentals:
```dockerfile
# Add timestamp comment to force full rebuild
# Cache-bust: 2026-02-03-14-20-fresh
```

Or better: delete and recreate the Railway service for truly fresh state.

---

### 5. Incomplete Refactoring (The Forgotten Reference)

**Problem:** Removed `_trinity_` orchestrator from registry, but left references in:
- `rest_api.py` (`TOOL_EXPOSURE` policy)
- `rate_limiter.py` (`DEFAULT_LIMITS`)
- `tool_registry.py` imports (still imported `mcp_trinity`)

**Lesson:** When removing a feature, grep the entire codebase:
```bash
grep -r "_trinity_" --include="*.py" . | grep -v __pycache__
```

Don't trust "it should work" — verify with search.

---

## Debugging Methodology That Worked

### The Log Archaeology Protocol

When Railway says "health check failed":

1. **Get actual container logs** (not just Railway UI status)
2. **Look for Python tracebacks** — they contain the truth
3. **Follow the import chain** — error in `sse.py` might root in `stdio.py`
4. **Check file timestamps** — is this the code you think it is?

### The Minimal Reproduction Test

Before pushing to Railway:
```bash
# Test imports locally in fresh environment
docker run --rm -v $(pwd):/app -w /app python:3.12-slim \
  sh -c "pip install -e . && python -c 'from mcp_server.core.tool_registry import ToolRegistry'"
```

If it fails locally, it will fail on Railway.

### The Config Audit Checklist

Before any deployment:

- [ ] Only one Railway config file exists (prefer `railway.toml`)
- [ ] Dockerfile copies ALL required source folders
- [ ] No relative imports beyond package root (`...`)
- [ ] PyPI package names don't conflict with local folders
- [ ] Cache-bust comment added if build system changed

---

## Architectural Decisions That Prevented Success

### What Made This Hard

| Decision | Impact |
|----------|--------|
| `mcp/` as local package name | Collision with PyPI `mcp` |
| Both `railway.json` and `railway.toml` | Silent override, confusion |
| Deep relative imports (`...`) | Broke when package structure changed |
| Mixed Nixpacks + Dockerfile configs | Cache pollution |
| No local Docker testing | Every fix required push → build → wait |

### What Would Make This Easier

1. **Standardize on absolute imports** within `mcp_server/`
2. **Single config file** (`railway.toml` only)
3. **Local Docker testing** before pushing
4. **CI/CD lint** that catches `...` imports
5. **Package prefix** (`arifos_` for all internal modules)

---

## For Future Agents

If you're reading this during another deployment crisis:

### Immediate Triage

```bash
# 1. Check what's actually deployed
curl -s https://aaamcp.arif-fazil.com/health | python -m json.tool

# 2. Get Railway logs (ask human to paste from Dashboard)
# Look for: ImportError, ModuleNotFoundError, AttributeError

# 3. Verify config files
git ls-files | grep -E "(railway|nixpacks|Dockerfile)"
# Should be: railway.toml, Dockerfile
```

### Common Failure Patterns

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `No module named mcp.X` | Namespace collision | Rename local `mcp/` to `mcp_server/` |
| `attempted relative import beyond top-level` | `...` import | Use absolute import from `codebase.X` |
| Wrong start command | `railway.json` overriding | Delete `railway.json`, keep only `railway.toml` |
| Old code running | Docker cache | Update cache-bust timestamp in Dockerfile |
| Tool count wrong | Incomplete refactor | `grep -r "tool_name" --include="*.py"` |

### The Nuclear Option

If stuck after 3+ attempts:

1. **Archive this wisdom** (update this file with new learnings)
2. **Delete Railway service** (fresh state)
3. **Verify locally:** `docker build -t test . && docker run test`
4. **Redeploy from scratch** with verified config

---

## Metadata

- **Wisdom captured:** 2026-02-03 (Week 5, Day 2)
- **arifOS Version:** v55.5.2
- **Deployment:** aaamcp.arif-fazil.com
- **Authority:** 888_JUDGE
- **Motto:** DITEMPA BUKAN DIBERI 💎🔥🧠

---

*"The bug is never in Railway. The bug is in our assumptions about what Railway sees."*  
*— AGI-bot, after 4 hours of debugging*
