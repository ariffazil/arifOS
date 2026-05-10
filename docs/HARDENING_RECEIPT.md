# HARDENING_RECEIPT.md — arifOS Federation

## 1. Before/After Endpoint Visibility Matrix

| Endpoint | Before (Public) | After (Public) | After (Authed) |
| :--- | :--- | :--- | :--- |
| `/health` | Full Vitals + Hashes | Redacted (Online only) | Full Vitals |
| `/tools.json` | Full Registry | 401 Unauthorized | Full Registry |
| `/capability` | Full Provider Map | 401 Unauthorized | Full Provider Map |
| `/metrics/json`| Internal Telemetry | 401 Unauthorized | Internal Telemetry |

## 2. Before/After Header Checks

**Route:** `https://arifos.arif-fazil.com/`

| Header | Before | After |
| :--- | :--- | :--- |
| `Content-Security-Policy` | MISSING | Strict (Self only) |
| `Permissions-Policy` | MISSING | Restricted (All null) |
| `Strict-Transport-Security`| 15552000 | 15552000 |
| `X-Frame-Options` | DENY | DENY |

## 3. High Impact Risk Summary

*   **Risk:** Edge-level auth gating for `/tools` may break internal observatory dashboards if the browser does not provide the `Authorization` header.
*   **Mitigation:** The dashboard JS must be updated to include the `ARIFOS_API_KEY` in its fetch calls.
*   **Rollback:** Revert `Caddyfile` to the `2026-04-27` version and run `docker exec caddy caddy reload`.

---
*🪙 Red Team Hardening Sealed | 2026-04-30 | DITEMPA BUKAN DIBERI*
