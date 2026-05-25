# SOURCE OF TRUTH LOCK — arifOS Federation
**Established:** 2026-05-01T15:00:00Z
**By:** ASI Hermes (Source-of-Truth Audit)
**Status:** SEALED — No patching until this document is updated

---

## Canonical Identity

| Field | Value | Evidence |
|-------|-------|---------|
| Canonical repo | `https://github.com/ariffazil/arifOS` | GitHub remote confirmed |
| Canonical branch | `main` | `git branch --show-current` → `main` |
| Canonical commit (local HEAD) | `d12bf283 llm_client: swap tier order` | `git rev-parse HEAD` |
| Deployed image | `ghcr.io/ariffazil/arifos:2026.05.01` | `docker images` → `ce49cbb0a8d6` |
| Deployed image commit | `a28bd90f` (estimated from image tags) | Image tag `a28bd90f` built 2026-05-01 12:53 UTC |
| **Local HEAD is AHEAD of deployed image** | YES — 4 commits ahead | `d12bf283` vs `a28bd90f` in git log |

**Critical note:** `/root/arifOS` (git repo) is **4 commits ahead** of the deployed container image. Phase 1 patches applied to `/root/arifOS` are NOT in the running server until a new image is built and deployed.

---

## Live Runtime Identity

| Field | Value | Evidence |
|-------|-------|---------|
| Live container ID | `59501b3a7b1b` | `docker ps` |
| Container image | `ghcr.io/ariffazil/arifos:2026.05.01` | `docker inspect` |
| Container code path | `/app/arifosmcp/runtime/` | `docker exec find / -name 'floor.py'` |
| Live package import | `arifosmcp` from `/app/arifosmcp/` | Container `sys.path` → `/app` |
| MCP entrypoint | `/app/arifosmcp/runtime/server.py` | Container filesystem |
| Active server port | `8080` (mapped to container port 8080) | `ss -tlnp` → docker-proxy |
| Active process | Docker container (uvicorn/FastMCP inside) | `docker-proxy` on port 8080 |
| Health endpoint | `http://localhost:8080/health` | `{"status":"healthy","version":"kanon-unknown"}` |
| MCP /tools endpoint | `http://localhost:8080/mcp/v1/tools` | MCP protocol JSON |
| Active tools count | 13 canonical | MCP /tools response |

---

## Local Working Copy (NOT the live server)

| Field | Value | Evidence |
|-------|-------|---------|
| Working copy path | `/root/arifOS/` | `pwd` |
| Git repo root | `/root/arifOS` | `git rev-parse --show-toplevel` |
| Git status | Clean (no uncommitted changes) | `git diff --stat` |
| Relationship to container | **AHEAD by 4 commits** | `d12bf283` vs `a28bd90f` |
| Phase 1 patches applied to | `/root/arifOS/arifosmcp/runtime/floor.py` | `git diff` |
| Phase 1 patch status | Applied locally, NOT in running container | SHA mismatch confirmed |

---

## Phase 1 Audit Results (LIVE CONTAINER)

### _hold() Function (tools.py:841)
```
✅ status: "HOLD"
✅ tool: <tool_name>
✅ result: {}
✅ meta.reason (singular string)
✅ meta.failed_floors: list[str]
✅ meta.nine_signal: injected
✅ reasons: [reason]  ← ALREADY HAS PLURAL
✅ output_policy: "DOMAIN_VOID"  ← ALREADY HAS
✅ next_safe_action: default string in meta  ← ALREADY HAS
```
**Verdict: Phase 1 requirements are ALREADY MET in the live container.**

### floor.py (NIAT version)
```
✅ RequestType class (NIAT principle)
✅ VerdictLabel class (ALLOW, ALLOW_WITH_CAVEAT, etc.)
✅ Semantic gate logic
✅ F1–F13 floor enforcement
✅ F09 prerequisite chain (heart before forge)
⚠️ NO budget enforcement (turn count / tool-call count)
```

---

## Active Gaps (Live Container)

| Gap | File | Evidence | Risk |
|-----|------|---------|------|
| Budget enforcement (turn + tool-call) | `floor.py` + `session_state.py` | `grep max_turns → 0 matches` | HIGH |
| Budget envelope (reasons[], DOMAIN_VOID) | `floor.py` budget responses | `_hold()` has them, budget branch doesn't | MEDIUM |
| NIAT semantic gate (not budget) | `floor.py` | Already present in container ✅ | N/A |
| HEART timeout wrapper | `tools.py:_arif_heart_critique` | No asyncio.wait_for | MEDIUM |
| HEART invalid-mode enforcement | `tools.py:_arif_heart_critique` | No mode enum check | MEDIUM |
| OROPE live computation | Not present | grep OROPE → 0 matches | LOW |
| mode=schema/help | Not present | grep schema mode → 0 matches | LOW |

---

## Approved Patch Order (From THIS Lock Forward)

All patches target the **canonical repo** `/root/arifOS` unless noted.

| Gate | Task | Target File | Risk | Requires Arif |
|------|------|-------------|------|---------------|
| G0 | **SOURCE_OF_TRUTH_LOCK** — this file | `/root/arifOS/` | N/A | NO (this is it) |
| G1 | Verify Phase 1: confirm _hold() envelope in deployed container | Container `/app/arifosmcp/runtime/tools.py` | READ ONLY | NO |
| G2 | Build + deploy image from current HEAD | GitHub Actions GHCR workflow | HIGH | YES |
| G3 | Add budget tracking (turn_count, tool_call_count) | `session_state.py` | MEDIUM | NO |
| G4 | ADD budget enforcement in check_floors() | `floor.py` | ✅ **SEALED — 5e27e931** | YES — committed + pushed |
| G5 | Budget HOLD envelope (reasons[], DOMAIN_VOID, nine_signal) | `floor.py` budget branch | ✅ **SEALED — 5e27e931 (same commit as G4)** | YES |
| G6 | HEART timeout wrapper | `tools.py:_arif_heart_critique` | MEDIUM | NO |
| G7 | HEART mode enum validation | `tools.py:_arif_heart_critique` | LOW | NO |
| G8 | Universal mode=schema/help | Per-tool | LOW | NO |
| G9 | OROPE live computation | New module | MEDIUM | YES |

---

## Source-of-Truth Provenance Commands

Every agent session must run these FIRST before any analysis:

```bash
# 1. Establish canonical repo identity
pwd
git -C /root/arifOS rev-parse --show-toplevel
git -C /root/arifOS branch --show-current
git -C /root/arifOS rev-parse HEAD

# 2. Establish live runtime identity
docker ps --format "{{.ID}} {{.Image}} {{.Ports}}" | grep arif
docker exec <CONTAINER_ID> sh -c "cat /app/arifosmcp/runtime/floor.py | head -20"

# 3. Confirm which code is actually running
docker exec <CONTAINER_ID> sh -c "grep -n 'def _hold' /app/arifosmcp/runtime/tools.py"

# 4. Test live endpoint
curl -s http://localhost:8080/health
curl -s http://localhost:8080/mcp/v1/tools | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('tools',[])), 'tools')"
```

---

## Anti-Chaos Protocol

1. **No patch before provenance** — run source-of-truth commands first
2. **No execution before evidence** — every claim needs exact file:line evidence
3. **No approval except Arif** — HEART, forge, seal, deploy all require Arif
4. **One branch per gate** — `fix/gate-N-description`
5. **One phase at a time** — gate must pass before next begins
6. **Live container is ground truth** — /root/arifOS is the plan, container is reality
7. **Build before deploy** — new commits need GHCR image before VPS pull

---

## Reconciliation: Agent A vs Agent B vs Ground Truth

| Claim | Agent A | Agent B | Ground Truth |
|-------|---------|---------|--------------|
| Budget enforcement wired | YES (floor.py) | NO | **NO** — not in container |
| _hold() has reasons[] | Missing (my patch) | Missing | **YES** — container has it |
| _hold() has DOMAIN_VOID | Missing (my patch) | Missing | **YES** — container has it |
| _hold() has nine_signal | Missing (my patch) | Missing (in meta) | **YES** — container has it |
| Phase 1 patch path | /root/arifOS/floor.py | N/A | **WRONG** — patched wrong codebase |
| Active runtime | /root/arifOS | /srv/openclaw/workspace | **Container at 8080** |
| NIAT semantic gate | Present | N/A | **YES** — in container floor.py |

---

*Last updated: 2026-05-01T15:00:00Z by ASI Hermes*
*Next action: G2 — Build + deploy image from d12bf283 (or confirm container is sufficient)*
