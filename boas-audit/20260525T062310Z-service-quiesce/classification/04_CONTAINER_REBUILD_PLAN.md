# CONTAINER_REBUILD_PLAN.md
**Mission:** Plan container rebuild to resolve build_commit != live_commit drift.
**Date:** 2026-05-25
**Rule:** Do NOT rebuild until Arif issues explicit approval.

---

## Drift Summary

| Metric | Value |
|--------|-------|
| **build_commit** (what container was built from) | `967d8e3` |
| **live_commit** (what /health reports as running) | `ab3a8f9` |
| **repo HEAD** (current git state) | `ab3a8f93` |
| **Image tag** | `ghcr.io/ariffazil/arifos:967d8e3` |
| **Drift severity** | MEDIUM — 20 commits between build and live |

---

## Commits Between build (967d8e3) and live (ab3a8f9)

```
20f80cb chore(.gitignore): ignore backup files
206027a docs: add AGENTS.md and remove stale MCP backup for BOAS hygiene
ea4aff2 docs: add canonical context index to README; add INVARIANTS + preflight-check-mcp
198870a fix(A-FORGE): update arifOS MCP endpoint to 8088 (was 8080)
f1ddbb9 docs: update README with federated architecture roles and links [AGY-AUTO]
ab3a8f93 chore(.gitignore): ignore MCP seal artifacts  ← LIVE COMMIT
```

**Key changes since build:**
- Caddy routing fixed (8080→8088)
- BOAS hygiene improvements
- AGENTS.md added
- Stale MCP backup removed
- INVARIANTS doc added

---

## Current Container State

| Property | Value |
|----------|-------|
| Container name | `arifosmcp` (via compose) |
| Image | `ghcr.io/ariffazil/arifos:967d8e3` |
| Port | 8088 |
| Health check | `curl localhost:8088/health` |
| Transport | streamable-http |
| Upstream | Caddy (port 443, arifos.arif-fazil.com) |

---

## Rebuild Decision Options

### Option A: Rebuild from current repo HEAD (RECOMMENDED)

| Property | Value |
|----------|-------|
| Target commit | `ab3a8f93` (repo HEAD) |
| New image tag | `ghcr.io/ariffazil/arifos:ab3a8f9` |
| Expected downtime | ~30-60 seconds |
| Rollback | `docker compose pull` or retag `967d8e3` |

**Pros:** Catches up to all routing fixes, aligns container with Caddy routing (8088)
**Cons:** Any regression in commits 967d8e3→ab3a8f9 will be deployed

### Option B: Rebuild from 967d8e3 (conservative)

| Property | Value |
|----------|-------|
| Target commit | `967d8e3` (same as current image) |
| Action | `docker compose build arifosmcp` only |
| Expected downtime | ~2-5 minutes |
| Rollback | None needed |

**Pros:** Zero regression risk
**Cons:** Does NOT resolve drift

---

## Services Affected

| Service | Impact |
|---------|--------|
| `arifosmcp` | RESTART — ~30s downtime |
| `arifosd` (apex) | No impact |
| Caddy | No impact |
| GEOX, WEALTH | No impact |

---

## Rollback Plan

```bash
cd /root/compose
docker compose pull arifosmcp
docker compose restart arifosmcp

# Fallback image: ghcr.io/ariffazil/arifos:967d8e3
```

---

## Pre-Rebuild Checklist

- [ ] Confirm target commit (ab3a8f93 or 967d8e3)
- [ ] Confirm Arif explicit approval
- [ ] Confirm no active sessions disrupted
- [ ] Prepare rollback command

## Post-Rebuild Verification

```bash
curl -fsS https://arifos.arif-fazil.com/health | python3 -c "
import sys,json; d=json.load(sys.stdin)
print('build:', d.get('build_commit'))
print('live:', d.get('live_commit'))
print('status:', d.get('status'))
print('floors_active:', d.get('floors_active'))
"
```

**Success criteria:**
- `build_commit == live_commit == ab3a8f93`
- `status == healthy`
- `floors_active == 13`

---

**STATUS: AWAITING EXPLICIT ARIF APPROVAL before any rebuild action.**

*Ditempa Bukan Diberi — Intelligence is forged, not given.*
