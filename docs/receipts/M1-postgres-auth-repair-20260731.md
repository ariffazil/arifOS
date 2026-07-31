# RECEIPT — M1 Postgres Auth Repair · 2026-07-31

> **M1 of Kernel Hardening Sprint** — T2, live degradation.

## WHAT WAS BROKEN

22 `password authentication failed for user "arifos_admin"` in the hour before
the fix. arifOS observe substrate was failing authentication against the
docker postgres backend, blocking any evidence queries that touched Postgres.

## ROOT CAUSE — credential drift, NOT pg_hba

The systemd EnvironmentFile `/root/.secrets/vault.flat.env` sets:
```
POSTGRES_URL=postgresql://arifos_admin:ArifPostgres2026!@127.0.0.1:5432/vault999
```

The actual `arifos_admin` role's stored scram-sha-256 verifier matched a
DIFFERENT password (`ArifPostgresVault2026!`). Cause: at some earlier point
the role was rotated with the "Vault" suffix but the config was updated to
the non-"Vault" form without re-rotating the role.

The previous `docker exec psql` "smoke tests" gave false confidence because
the unix-socket auth method is `local all all trust` (no password check at all).
The host TCP path hits `host all all all scram-sha-256` (catch-all) and
correctly rejects the mismatched password.

## THE FIX

Aligned role password to config (single source of truth: `vault.flat.env`):
```sql
ALTER USER arifos_admin WITH PASSWORD 'ArifPostgres2026!';
```

Constraint check: NO new user created, NO pg_hba edit, NO trust widened.

## ACCEPTANCE — measured at fix time

| Gate | Before | After |
|---|---|---|
| `journalctl -u arifos --since "1 hour ago" \| grep -c "password authentication failed"` | **22** | **0** (immediately post-restart) |
| Host TCP auth `psql -h 127.0.0.1 -U arifos_admin -d vault999` | FATAL | AUTH_OK |
| arifOS `arif_observe` via MCP `tools/call` | auth-failure exception | returns structured substrate verdict |
| Kernel handshake `version` | kanon-2026.07.31+0b03b5b | kanon-2026.07.31+0b03b5b (unchanged) |

Regression check: old password `ArifPostgresVault2026!` now correctly fails.
Rollback deploys under `deploy/rollback/20260729-100111/` that reference
`ArifPostgresVault2026!` are HISTORICAL snapshots — not live paths, not
re-run on this fix; archived in their `20260729-100111/` directory by design.

## 10-minute stability window

Post-fix journal count for the same grep at 10 minutes post-restart:
recorded in this sprint's final report.

DITEMPA BUKAN DIBERI.
