# Deployment Contrast Analysis: Docker Container vs GitHub Main

**Date:** 2026-04-06  
**Authority:** 888_JUDGE  
**Status:** PRE-DEPLOYMENT ANALYSIS

---

## Executive Summary

| Aspect | Docker Container (Current) | GitHub Main (Target) | Recommendation |
|--------|---------------------------|---------------------|----------------|
| **Code Version** | Stale (pre-fixes) | Latest (cc603bb) | **Upgrade required** |
| **arifos.init** | INIT_KERNEL_500 | ✅ Fixed | **Critical** |
| **canonical_tool_name** | null | ✅ Populated | **Critical** |
| **Clean Output** | v0.1 (chaotic) | v0.2 (3-tier) | **Recommended** |
| **Constitutional** | F9/F13 basic | F9/F13 amended | **Recommended** |
| **Deployment Speed** | Fast (image pull) | Slower (git+install) | Trade-off |
| **Rollback** | Image tag | Git revert | Comparable |

**Verdict:** Deploy GitHub Main immediately (critical fixes).

---

## 1. Current Docker Container State

### Container Details
```bash
# Current running container (from backup analysis)
Container: arifos-mcp-v2
Image: arifos-mcp:2026.03.28-prod
Status: RUNNING (degraded)
```

### Issues in Current Container

#### P0: Bootstrap Failure
```
arifos.init → INIT_KERNEL_500
HARDENED_DISPATCH_MAP has no init_anchor entry
```
**Impact:** New sessions cannot initialize. System unusable for new users.

#### P1: Legacy Name Leakage
```json
{
  "tool": "agi_mind",           // Should be "arifos.mind"
  "canonical_tool_name": null,   // Should be "arifos.mind"
  "stage": "333_MIND"
}
```
**Impact:** Client confusion, namespace pollution.

#### P1: Query Collapse Bug
```
arifos.sense query="" → Brave validation error
```
**Impact:** Empty queries crash the sense organ.

### Container Architecture
```
┌─────────────────────────────────────────┐
│  Docker Container                       │
│  ────────────────                       │
│  Base: python:3.11-slim                 │
│  Code: Frozen at 2026-03-28             │
│  Config: Environment variables          │
│  State: Ephemeral (except volumes)      │
└─────────────────────────────────────────┘
```

---

## 2. GitHub Main State (Target)

### Commit Details
```
Commit: cc603bb
Date: 2026-04-06 11:45:00Z
Message: 🔥 Critical fixes + Clean Output v0.2 + Constitutional Amendment
Changes: 13 files, +2944/-21
```

### Fixes in Main

#### ✅ P0: Circular Dependency Fixed
**File:** `megaTools/tool_01_init_anchor.py`
```python
# OLD (BROKEN):
res = await HARDENED_DISPATCH_MAP["init_anchor"](...)  # RECURSION

# NEW (FIXED):
res = await _direct_init_logic(...)  # Direct execution
```

#### ✅ P1: Canonical Names Fixed
**File:** `continuity_contract.py`
```python
envelope.canonical_tool_name = tool_id  # Now populated
envelope.tool = tool_id  # Legacy name overwritten
```

#### ✅ P1: Query Validation Fixed
**File:** `megaTools/tool_08_physics_reality.py`
```python
if not query or query.strip() == "":
    return RuntimeEnvelope(
        verdict=Verdict.VOID,
        payload={"error": "SENSE_QUERY_EMPTY"}
    )
```

### New Features in Main

#### Clean Output v0.2
```json
{
  "execution": {"ok": true, "status": "OK", "stage": "MIND"},
  "governance": {"verdict": "SEAL", "reason": "Grounded reasoning"},
  "operator": {"summary": "...", "next_step": "...", "retryable": true},
  "context": {"actor": "...", "session": "...", "verified": true, "risk": "low"}
}
```

#### Constitutional Amendment CA-2026-04-06-001
- F9.1: Prohibition on intelligence confusion
- F9.3: Falsification mandate
- F13.1: Human-AI boundary matrix

---

## 3. Contrast Matrix

### Functional Contrast

| Feature | Docker (Current) | GitHub Main | Impact |
|---------|-----------------|-------------|--------|
| **arifos.init** | ❌ INIT_KERNEL_500 | ✅ Works | **Critical** |
| **arifos.sense** | ❌ Empty query crash | ✅ Validates | **Critical** |
| **arifos.mind** | ⚠️ Leaks "agi_mind" | ✅ Clean names | **High** |
| **arifos.route** | ⚠️ Legacy names | ✅ Clean names | **High** |
| **canonical_tool_name** | ❌ null | ✅ Set correctly | **Critical** |
| **Output format** | 50+ fields chaotic | 10-15 clean | **Medium** |
| **F9 Anti-Hantu** | Basic | Extended | **Medium** |
| **F13 Sovereign** | Basic | Clarified | **Medium** |

### Operational Contrast

| Aspect | Docker (Current) | GitHub Main | Notes |
|--------|-----------------|-------------|-------|
| **Deployment** | `docker pull && run` | `git pull && pip install` | Docker faster |
| **Update Speed** | Minutes (image) | Seconds (git) | Git faster for dev |
| **Rollback** | `docker run <old-tag>` | `git checkout <commit>` | Comparable |
| **Debugging** | `docker exec` | Direct file access | Git easier |
| **Logs** | `docker logs` | Direct stdout | Comparable |
| **State** | Volume mounts | File system | Comparable |

### Security Contrast

| Aspect | Docker (Current) | GitHub Main | Notes |
|--------|-----------------|-------------|-------|
| **Isolation** | Container boundary | Process boundary | Docker stronger |
| **Secrets** | Env vars / secrets | Env vars / files | Comparable |
| **Reproducibility** | Image hash | Git commit | Both good |
| **Supply chain** | Base image risk | Code review | Git more transparent |

---

## 4. Deployment Options

### Option A: Direct Git Deploy (Recommended for Speed)

```bash
# 1. Backup current
mv /opt/arifOS /opt/arifOS.backup.$(date +%Y%m%d)

# 2. Clone fresh
git clone https://github.com/ariffazil/arifOS.git /opt/arifOS
cd /opt/arifOS

# 3. Install
pip install -e .

# 4. Configure
export ARIFOS_ENV=production
export MEMORY_BACKEND_VERSION=v2
export VAULT_BACKEND_VERSION=v2

# 5. Start
python -m arifosmcp.runtime.server_v2
```

**Pros:** Fastest path to fixes, easy to rollback  
**Cons:** No container isolation

### Option B: Rebuild Docker Image

```bash
# 1. Clone
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# 2. Build new image
docker build -t arifos-mcp:2026.04.06-prod .

# 3. Stop old
docker stop arifos-mcp-v2
docker rename arifos-mcp-v2 arifos-mcp-v2-old

# 4. Start new
docker run -d \
  --name arifos-mcp-v2 \
  -p 8080:8080 \
  -e ARIFOS_ENV=production \
  arifos-mcp:2026.04.06-prod
```

**Pros:** Container isolation, reproducible  
**Cons:** Slower deployment, image build time

### Option C: Hybrid (Recommended for Production)

```bash
# 1. Build new image from main
docker build -t arifos-mcp:2026.04.06-prod .

# 2. Tag for rollback safety
docker tag arifos-mcp:2026.03.28-prod arifos-mcp:rollback

# 3. Blue-green deploy
docker run -d \
  --name arifos-mcp-green \
  -p 8081:8080 \
  arifos-mcp:2026.04.06-prod

# 4. Health check
curl http://localhost:8081/health

# 5. Switch traffic
docker stop arifos-mcp-v2  # blue
docker rename arifos-mcp-v2 arifos-mcp-blue-old
docker rename arifos-mcp-green arifos-mcp-v2
```

**Pros:** Zero downtime, instant rollback  
**Cons:** More complex, requires load balancer

---

## 5. MCP Inspector Verification Plan

### Pre-Deploy Checks

```bash
# 1. Clone and verify locally
git clone https://github.com/ariffazil/arifOS.git arifOS-main
cd arifOS-main

# 2. Syntax check
python -m py_compile arifosmcp/runtime/megaTools/tool_01_init_anchor.py
python -m py_compile arifosmcp/runtime/continuity_contract.py

# 3. Import check
python -c "from arifosmcp.runtime.megaTools.tool_01_init_anchor import init_anchor"
```

### Post-Deploy Verification

```bash
# Install MCP Inspector if needed
npm install -g @anthropics/mcp-inspector

# 1. Health check
mcp-inspector call arifos/init --arg '{"actor": "test", "intent": "health check"}'
# Expected: ok: true, verdict: SEAL

# 2. Sense check
mcp-inspector call arifos/sense --arg '{"query": "test query"}'
# Expected: ok: true, no empty query error

# 3. Mind check
mcp-inspector call arifos/mind --arg '{"query": "test reasoning"}'
# Expected: canonical_tool_name: "arifos.mind", not null

# 4. Clean output check
mcp-inspector call arifos/init --arg '{"actor": "test", "intent": "test", "options": {"verbose": false}}'
# Expected: Fixed block structure [execution, governance, operator, context]

# 5. Verbose check
mcp-inspector call arifos/init --arg '{"actor": "test", "intent": "test", "options": {"verbose": true}}'
# Expected: Includes system block

# 6. Debug check
mcp-inspector call arifos/init --arg '{"actor": "test", "intent": "test", "options": {"debug": true}}'
# Expected: Includes debug block with telemetry, trace
```

### Inspector Test Matrix

| Test | Command | Expected | Priority |
|------|---------|----------|----------|
| Init success | `arifos/init` | `ok: true`, `verdict: SEAL` | P0 |
| Init canonical name | Check response | `canonical_tool_name: "arifos.init"` | P0 |
| Sense empty query | `arifos/sense` with `"query": ""` | `verdict: VOID`, `error: SENSE_QUERY_EMPTY` | P0 |
| Mind canonical | `arifos/mind` | `tool: "arifos.mind"` (not "agi_mind") | P1 |
| Clean output format | Any tool | Fixed block structure | P1 |
| Verbose output | `options.verbose: true` | Includes system | P2 |
| Debug output | `options.debug: true` | Includes telemetry | P2 |

---

## 6. Rollback Plan

### Immediate Rollback (< 30 seconds)

```bash
# If direct git deploy
cd /opt/arifOS
git checkout 2026.03.28-prod  # pre-fix commit
pip install -e .
systemctl restart arifos-mcp

# If Docker
docker stop arifos-mcp-v2
docker rm arifos-mcp-v2
docker run -d --name arifos-mcp-v2 -p 8080:8080 arifos-mcp:2026.03.28-prod
```

### Rollback Triggers

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Bootstrap failures | > 0 | Immediate rollback |
| Error rate | > 1% | Alert + investigate |
| Latency p99 | > 500ms | Degrade gracefully |
| Inspector failures | Any P0 test fails | Rollback |

---

## 7. Recommendation

### Immediate Action Required

**Deploy GitHub Main NOW.**

The current Docker container has P0 failures that make arifOS unusable:
1. Cannot initialize new sessions (INIT_KERNEL_500)
2. Empty queries crash sense organ
3. Canonical namespace polluted

### Recommended Deployment Method

**Option C: Hybrid Blue-Green** for production safety.

If speed is critical, **Option A: Direct Git** with immediate rollback capability.

### Timeline

```
T+0:   Stop accepting new sessions
T+1m:  Deploy GitHub Main (Option A or C)
T+2m:  Run MCP Inspector verification
T+3m:  Resume traffic if all P0 tests pass
T+5m:  Monitor for 10 minutes
T+15m: Declare success or rollback
```

---

## 8. Post-Deploy README Update

After successful deployment, update README with:

1. **Clean Output examples** (v0.2 format)
2. **New input schema** (actor, intent, risk, session, options)
3. **3-tier output model** documentation
4. **MCP Inspector quickstart**
5. **Deployment verification steps**

---

**Authority:** 888_JUDGE  
**Verdict:** DEPLOY IMMEDIATELY  
**Seal Status:** AWAITING EXECUTION

*DITEMPA BUKAN DIBERI* 🔥
