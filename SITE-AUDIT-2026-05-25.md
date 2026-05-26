# arifOS Observatory Site Audit
**Date:** 2026-05-25  
**Agent:** kimi-code-cli  
**Scope:** arif-fazil.com / arifos.arif-fazil.com public surface  
**Method:** Live endpoint probing vs site claims  

---

## My Error Acknowledged

In my initial PHOENIX-73D preflight, I ran `ss -tlnp | grep -E "18001|3001|3002|8088"` and concluded only port 8088 was listening. **This was incomplete.** I missed ports 18081, 18082, 18083, 18000, 7071, 8100, 5001, and 18789 because I didn't scan the full `ss` output or probe systematically.

**Corrected finding:** Services run via **systemd**, not Docker. Docker has 0 containers. But 12+ systemd services are active and healthy.

---

## Ground Truth: What Is Actually Listening

| Service | Site Claims | Actual Port | Status | Process |
|---------|-------------|-------------|--------|---------|
| arifOS MCP | 8088 | **8088** | ✅ Healthy | python (pid 1055416) |
| GEOX | 8081 | **18081** | ✅ Healthy | python3 (pid 4117) |
| WEALTH | 8082 | **18082** | ✅ Healthy | python3 (pid 460032) |
| WELL | 8083 | **18083** | ✅ Healthy | python3 (pid 974661) |
| vault999 | 8100 | **8100** | ✅ Healthy | python3 (pid 985778) |
| vault999-writer | 5001 | **5001** | ✅ Healthy | python3 (pid 986031) |
| A-FORGE bridge | 7071 | **7071** | ✅ Healthy | node |
| OpenClaw gateway | — | **18789** | ✅ Healthy | node (pid 804118) |
| OpenClaw secondary | — | **8787** | ✅ Healthy | node (same pid) |
| federation-webhook | — | **18000** | ✅ Healthy | python3 (pid 1081) |
| Ollama | 11434 | **11434** | ✅ Healthy | ollama (pid 812466) |
| Caddy | 80/443 | **80/443** | ✅ Healthy | caddy (pid 1136) |
| Hermes ASI | 3002 (as hermes-agent) | **N/A** | ✅ Running (Telegram bot) | systemd: hermes-asi-gateway |
| arifosd | — | **N/A** | ✅ Running | systemd: arifosd |
| **AAA A2A** | **3001** | **NONE** | ❌ **NOT LISTENING** | Code exists but service down |
| **APEX** | **3002** | **NONE** | ❌ **NOT LISTENING** | Code exists but service down |
| **Redis** | **6379** | **NONE** | ❌ **NOT LISTENING** | No process, no socket |
| **Postgres** | **5432** | **NONE** | ❌ **NOT LISTENING** | No process, no socket |
| **Qdrant** | **6333** | **NONE** | ❌ **NOT LISTENING** | No process, no socket |
| **NATS** | **4222** | **NONE** | ❌ **NOT LISTENING** | No process, no socket |
| **Loki** | **3100** | **NONE** | ❌ **NOT LISTENING** | No process, no socket |
| **Grafana** | **3000** | **NONE** | ❌ **NOT LISTENING** | Not even returning 503 |

---

## Critical Site Discrepancies

### 1. Port Mapping Errors (HIGH)

The Observatory lists GEOX/WEALTH/WELL on ports 8081/8082/8083. **Actual ports are 18081/18082/18083.**

This is a **Caddy reverse-proxy mismatch**. Caddy exposes these organs on `geox.arif-fazil.com:443`, `wealth.arif-fazil.com:443`, `well.arif-fazil.com:443` — but the site incorrectly labels the internal backend ports as 8081/8082/8083 instead of 18081/18082/18083.

**Impact:** Operators trying to curl `localhost:8081` will get connection refused. The `stack_health_probe` (which correctly probes 18081/18082/18083) will succeed, but manual debugging using site docs will fail.

### 2. Overclaimed Health (HIGH)

Six services marked "Healthy" or "Degraded" in the Federation Status table are **completely absent** from the runtime:

| Service | Site Claim | Reality |
|---------|-----------|---------|
| AAA A2A | 3001 Healthy | **No listener** — code at `/root/AAA/a2a-server/server.js` not running |
| hermes-agent | 3002 Healthy | **No listener** — Hermes runs as Telegram bot (systemd), not HTTP on 3002 |
| Redis | 6379 Healthy | **No process, no socket** |
| Postgres | 5432 Healthy | **No process, no socket** |
| Qdrant | 6333 Healthy | **No process, no socket** |
| NATS | 4222 Healthy | **No process, no socket** |
| Loki | 3100 Healthy | **No process, no socket** |
| Grafana | 3000 Degraded | **No process** — site claims "HTTP 503" but it's not even listening |

**Impact:** The Observatory overstates federation resilience. If an operator trusts the site and assumes Redis/Postgres are warm, they will be surprised when MCP memory features fail.

### 3. WELL Score Inconsistency (MEDIUM)

Site displays: `Ψ_v = 0.59`  
Live endpoint (`localhost:18083/health`): `"well_score": 0.0`

The site appears to be using the arifOS **vitality_index** (0.5946) instead of the WELL organ's own `well_score`. This conflates two different metrics.

### 4. Trinity Witness Mismatch (MEDIUM)

Site displays:
- Human Witness: 0.50
- AI Witness: 0.85
- Earth Witness: 0.00

Live endpoint (`localhost:8088/health`):
- Human: 0.42
- AI: 0.32
- Earth: 0.26

Site values are **stale or hardcoded**. The live endpoint shows a more balanced (but lower-confidence) distribution.

### 5. Floor Score Display Is Misleading (MEDIUM)

Site shows:
- F1 AMANAH: 0.50
- F9 ANTIHANTU: 0.00
- F12 INJECTION: 0.42

These are **not** the canonical floor enforcement scores. The health endpoint reports:
- All 13 floors active
- No floors violated
- Floor enforcement: active

The site appears to be displaying **thermodynamic or confidence metrics** labeled as floor scores, which is confusing. F9=0.00 looks like a floor breach when it is not.

### 6. Langfuse Contradiction (MEDIUM)

Site displays:
- Status page: "Langfuse: NOT_WIRED"
- Capability map: "Langfuse Tracing: enabled"
- /api/status text: "Langfuse traced"

**Reality:** `langfuse_tracing: { status: "NOT_WIRED", reason: "sdk_not_installed" }`

The site simultaneously claims Langfuse is enabled and not wired. This is a **copy inconsistency** across page sections.

### 7. "6/13 floors" Display (LOW)

The site header shows `6/13 floors` with a yellow indicator.  
**Reality:** All 13 floors are active. No floors violated.

This appears to be a **UI state bug** — possibly counting only "hard" floors or using a stale metric.

### 8. "3 Organs · 13 Tools" Undercount (LOW)

The site hero says "3 Organs · 13 Tools" for arifOS.  
The federation actually has 4+ organs (GEOX, WEALTH, WELL, AAA) and 70+ total tools. This is technically correct for the arifOS kernel alone, but the phrasing is ambiguous on a federation page.

---

## What the Site Gets Right

| Claim | Verified |
|-------|----------|
| arifOS 8088 Healthy | ✅ Correct |
| 13 canonical tools loaded | ✅ Correct |
| VAULT999 Healthy | ✅ Correct |
| Runtime drift: FALSE | ✅ Correct |
| Build commit: 341ccc6 | ✅ Correct |
| Ollama 11434 Up | ✅ Correct |
| Caddy 80/443 serving | ✅ Correct |
| A-FORGE 7071 Healthy | ✅ Correct |
| Observatory static content | ✅ Correct |
| CORS blocking organ discovery | ✅ Correct (noted as known gap) |
| /canon/ seed content only | ✅ Correct |
| F2 Truth threshold 0.99 | ✅ Correct |
| Tau confidence 0.990 | ✅ Correct |
| Entropy ΔS +0.000 | ✅ Correct |
| Peace² 0.500 | ✅ Correct |

---

## Root Causes

1. **Hardcoded port numbers in site HTML** — The Observatory appears to be a static HTML file with hardcoded port values (8081/8082/8083) that predate the 18081/18082/18083 migration.
2. **Static health table** — The Federation Status table may be generated at build time, not dynamically queried from `/health` endpoints.
3. **Capability map copy drift** — Different sections of the page were edited at different times, creating contradictions (Langfuse enabled vs NOT_WIRED).
4. **Missing service monitoring** — Redis/Postgres/Qdrant/NATS/Loki/Grafana are not actually probed; their "Healthy" status is assumed or cached.

---

## Recommendations

### Immediate (Phase 1)
1. **Fix port labels** — Change GEOX/WEALTH/WELL from 8081/8082/8083 to 18081/18082/18083, OR remove port numbers and just list domains.
2. **Fix Langfuse copy** — Standardize on "NOT_WIRED" everywhere.
3. **Fix floor count** — Change "6/13 floors" to "13/13 floors active".
4. **Fix WELL score** — Display WELL's own `well_score` (0.0) or label it clearly as vitality_index.
5. **Fix Trinity witnesses** — Pull from live `/health` endpoint or label as "example values".

### Short-term (Phase 2)
6. **Dynamic health table** — Replace static Federation Status table with JavaScript that fetches `/health` from each organ at page load.
7. **Honest service status** — Mark Redis/Postgres/Qdrant/NATS/Loki/Grafana as "Not Running" instead of "Healthy/Degraded" if they are absent.
8. **Start AAA A2A** — The A2A server (`/root/AAA/a2a-server/server.js`) exists and has Hermes registered now, but the service is not running.

### Medium-term (Phase 3)
9. **Unify capability map** — Single source of truth for capability status, derived from live `/health` + `stack_health_probe`.
10. **Floor score clarity** — If displaying thermodynamic metrics, label them as such (e.g., "F1 Confidence: 0.50") rather than implying floor breach.

---

*DITEMPA BUKAN DIBERI*
