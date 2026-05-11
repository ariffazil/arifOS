# SECRET_ROTATION.md
## arifOS — Secret Rotation Procedure

> **888_HOLD approval is required before any secret rotation begins.**
> This document describes the procedure only. Do NOT rotate secrets without
> explicit 888_HOLD authorization.

---

## Overview

Rotatable secrets in the arifOS stack:

| Secret | Service | Env var / Config key |
|--------|---------|---------------------|
| PostgreSQL password | `postgres` | `POSTGRES_PASSWORD` |
| Qdrant API key | `qdrant` | `QDRANT_API_KEY` |
| Redis password | `redis` | `REDIS_PASSWORD` |

---

## Principles

1. **DITEMPA BUKAN DIBERI** — Every rotation is a deliberate act, not routine drift.
2. **No downtime by design** — Use blue/green or dual-write windows.
3. **Rollback is always possible** — Keep the previous secret valid for ≥1 rotation cycle.
4. **Audit every step** — Log who approved, when, and what the old/new values are
   (hash only in logs, never plain text).

---

## Pre-rotation Checklist (888_HOLD-C)

```
[ ] 888_HOLD approval received (C-level sign-off)
[ ] Change window scheduled (off-peak preferred)
[ ] Rollback plan reviewed and acknowledged
[ ] New secret generated (use: `openssl rand -base64 32` or equivalent)
[ ] Old secret stored as ROTATION_HOLD (do NOT delete until next rotation)
[ ] All dependent services identified and restart plan confirmed
[ ] On-call contact confirmed for post-rotation monitoring window
```

---

## Step-by-Step: PostgreSQL Password Rotation

### 1. Generate new secret

```bash
NEW_PASS=$(openssl rand -base64 32)
echo "New postgres password (plain — handle with care): $NEW_PASS"
```

### 2. Update PostgreSQL (dual-write window)

Connect to the postgres primary as superuser and set the new password
while keeping the old one valid:

```sql
-- Keep old password valid for rollback window
ALTER USER arifos WITH PASSWORD '<NEW_PASSWORD>';
-- Flush privileges
SELECT pg_reload_conf();
```

### 3. Update consumer services (zero-downtime rollout)

For each service that connects to postgres (`arifosmcp`, prefect workers, etc.):

```bash
# Rollout new env var via your config manager (Ansible / K8s / envchain)
export POSTGRES_PASSWORD="<NEW_PASSWORD>"
systemctl restart <service-name>
```

### 4. Verify connectivity

```bash
PGPASSWORD="<NEW_PASSWORD>" psql -h localhost -U arifos -d arifos -c "SELECT 1;"
```

### 5. Confirm old secret can be revoked (next cycle)

After one full rotation cycle with no errors:
```sql
-- Only after confirmed stability
ALTER USER arifos WITH PASSWORD '<OLD_PASSWORD>';
```

---

## Step-by-Step: Qdrant API Key Rotation

### 1. Generate new key

```bash
NEW_KEY=$(openssl rand -hex 32)
```

### 2. Update Qdrant (if supported) or load balancer ACL

Qdrant does not natively support dual keys. The procedure depends on deployment:

**Option A — In-place (brief outage acceptable):**
```bash
# Update via Qdrant config / environment
QDRANT_API_KEY="<NEW_KEY>"
# Restart Qdrant service
sudo systemctl restart qdrant
```

**Option B — Blue/green (preferred):**
```bash
# Deploy new Qdrant instance with new key
# Point load balancer to new instance
# Verify all writers are healthy
# Decommission old instance
```

### 3. Update consumer services

```bash
export QDRANT_API_KEY="<NEW_KEY>"
systemctl restart <service-name>
```

### 4. Verify

```bash
curl -H "api-key: <NEW_KEY>" http://localhost:6333/collections
```

---

## Step-by-Step: Redis Password Rotation

### 1. Generate new password

```bash
NEW_REDIS_PASS=$(openssl rand -base64 24)
```

### 2. Update Redis config (dual-write)

Edit `/etc/redis/redis.conf` or equivalent:

```
requirepass <NEW_PASSWORD>
```

Send SIGHUP to reload (or `CONFIG SET requirepass <NEW_PASSWORD>`).

### 3. Update consumer services

```bash
export REDIS_PASSWORD="<NEW_PASSWORD>"
systemctl restart <service-name>
```

### 4. Verify

```bash
redis-cli -a "<NEW_PASSWORD>" ping
```

---

## Rollback Plan

| Step | Action |
|------|--------|
| R1 | Revert env var to old secret in all consumer services |
| R2 | Restart all affected services |
| R3 | Verify `pg_isready`, Redis `PING`, Qdrant health endpoint |
| R4 | If Qdrant was fully replaced: re-point load balancer to old instance |
| R5 | Log rollback in incident tracker with 888_HOLD reference |

---

## Post-Rotation

- [ ] Update secrets in password manager (arifOS vault / 1Password)
- [ ] Archive old secret hash in `secrets/rotation-log/` (never plain text)
- [ ] Notify stakeholders of rotation completion
- [ ] Close 888_HOLD ticket

---

## Emergency Contacts

| Service | On-call |
|---------|---------|
| Postgres | @ DBA on-call |
| Qdrant | @ infra on-call |
| Redis | @ infra on-call |

---

*Last reviewed: 2026-04-19*
*Owner: arifOS engineering*
*888_HOLD policy: non-negotiable*
