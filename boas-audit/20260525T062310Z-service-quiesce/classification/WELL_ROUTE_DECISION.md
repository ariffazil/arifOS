# WELL_ROUTE_DECISION.md
**Mission:** Plan WELL public route decision — retire, revive, or stub.
**Date:** 2026-05-25T07:00Z
**Rule:** Do not reload Caddy until Arif approves.

---

## Current State

| Property | Value |
|----------|-------|
| Public URL | `https://well.arif-fazil.com` |
| Caddy route | `reverse_proxy 127.0.0.1:8083` |
| Backend | **NONE** — nothing listening on 8083 |
| Public result | HTTP 525 (SSL handshake failed between Caddy and origin) |
| Local test | `curl 127.0.0.1:8083` → Connection refused |
| Docker | No `well` container running |
| systemd | No `well.service` defined |

**Classification: INTENTIONAL SHUTDOWN** — WELL backend intentionally offline.

---

## The Problem

Caddy is configured to route `well.arif-fazil.com` to a backend that does not exist. This produces:
- **525 errors** for any user trying to access WELL publicly
- **False expectation** — public route implies live service
- **Noise in logs** — failed proxy attempts

**BOAS invariant:** *"The public surface must not imply life where there is no living backend."*

---

## Three Options

### Option A: Retire WELL Public Route (RECOMMENDED — lowest entropy)

Remove/disable the `well.arif-fazil.com` route from Caddy until a backend exists.

**Files/services touched:**
- Edit `/root/arifOS/Caddyfile` — remove `well.arif-fazil.com` block (or comment it out)
- `caddy fmt --overwrite /root/arifOS/Caddyfile`
- `systemctl reload caddy`

**Expected public behavior:**
- `well.arif-fazil.com` → SSL cert still valid, but HTTP 404 or connection refused
- No more 525 errors (Caddy won't proxy to dead backend)
- No implied service

**Rollback command:**
```bash
# Restore well.arif-fazil.com block to /root/arifOS/Caddyfile
# systemctl reload caddy
```

**Risk:** LOW — removes broken route only. If WELL is revived later, route must be restored.

**Entropy delta:** NEGATIVE (reduces entropy — removes false positive)

**Recommendation:** ✓ RECOMMENDED if WELL backend is not imminent.

---

### Option B: Create/Start WELL Backend Service

Bring up the WELL MCP server on port 8083 as a systemd service.

**Files/services touched:**
- Ensure `WELL/server.py` or `WELL/src/server.py` exists and is runnable
- Create `/etc/systemd/system/well.service` (if not exists)
- `systemctl daemon-reload`
- `systemctl enable --now well.service`
- Verify `curl 127.0.0.1:8083/health` returns OK
- Update `/root/arifOS/Caddyfile` if port changed
- `systemctl reload caddy`

**Expected public behavior:**
- `well.arif-fazil.com/health` → `{"status": "healthy", ...}`

**Rollback command:**
```bash
systemctl stop well.service
systemctl disable well.service
# Caddy will start returning 525 again
```

**Risk:** MEDIUM — requires WELL codebase to be in valid state, service to start cleanly.

**Entropy delta:** POSITIVE (restores live service)

**Recommendation:** Only if WELL revival is imminent and codebase is verified healthy.

---

### Option C: Serve Explicit Inactive WELL Health Stub

Keep the Caddy route but replace the backend proxy with a static JSON response indicating WELL is intentionally offline.

**Files/services touched:**
- Create `/var/www/html/well/.well-known/mcp/server.json` with `{"status": "inactive", "reason": "WELL backend not yet active"}`
- OR modify Caddyfile to respond with static JSON instead of proxying
- `systemctl reload caddy`

**Caddyfile change:**
```
handle /health {
    respond /health {
        body '{"status": "inactive", "note": "WELL backend intentionally offline"}
    }
}
```

Or alternatively serve a static file:
```
handle_path /health {
    file_server /var/www/html/well/health.json
}
```

**Expected public behavior:**
- `well.arif-fazil.com/health` → `{"status": "inactive", ...}` (200 OK)
- Public surface says "inactive" not "dead"

**Rollback command:**
```bash
# Remove handle block or restore reverse_proxy
# systemctl reload caddy
```

**Risk:** LOW — no backend required, Caddy serves static response.

**Entropy delta:** NEUTRAL (documents inactive state clearly)

**Recommendation:** ✓ VIABLE if public-facing "inactive" message is preferred over 525 or 404.

---

## Comparison Table

| Criteria | Option A (Retire) | Option B (Revive) | Option C (Stub) |
|----------|-------------------|-------------------|-----------------|
| Complexity | LOW | HIGH | LOW |
| Public result | 404/refused | healthy | inactive JSON |
| 525 eliminated | ✓ YES | ✓ YES | ✓ YES |
| Backend required | NO | YES | NO |
| Reversibility | HIGH | MEDIUM | HIGH |
| Entropy delta | - (reduces) | + (restores) | 0 (documents) |
| Risk | LOW | MEDIUM | LOW |

---

## Recommendation

**Option A (Retire) is recommended** as the lowest-entropy path, because:
1. WELL backend does not exist
2. No `well.service` is defined
3. Reviving WELL would require building a new service from potentially stale code
4. Option C adds complexity (static stub) without much benefit over a clean 404

**Option A is the "strict truth" approach:** no route, no implied life.

---

## Pending Decision

| Item | Owner |
|------|-------|
| Approve Option A (retire WELL route) | Arif |
| Approve Option B (revive WELL backend) | Arif |
| Approve Option C (serve inactive stub) | Arif |
| Or: defer decision | Arif |

---

*Ditempa Bukan Diberi — Intelligence is forged, not given.*
