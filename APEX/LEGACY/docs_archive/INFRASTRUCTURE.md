# arifOS Production Infrastructure (Railway)

**Document:** Infrastructure Reality Description  
**Version:** v1.0  
**Status:** Working documentation  
**Last Updated:** 2026-02-02

---

## Platform Overview

**Platform:** Railway  
**Environment:** `production`  
**Execution Model:** Docker containers (real compute, real network, real storage)

### Critical Architectural Principle

> **Containers are ephemeral. Data services are persistent.**

This distinction determines how VAULT999 and all stateful components must be designed.

---

## Deployed Services

The production environment consists of **three live services**, all currently **ONLINE**:

### 1. arifOS Application Service

- **Type:** Docker container
- **Role:** Main application runtime (API / MCP / constitutional pipeline)
- **Domain:** `aaamcp.arif-fazil.com`
- **State:** Online and serving requests
- **Observability:** CPU, memory, network traffic, request rate, latency metrics enabled
- **Lifecycle:** Ephemeral — may be restarted, rescheduled, or scaled by Railway

**Implication:** Any state stored in container memory or filesystem **will be lost** on restart. All durable state must persist to external services.

---

### 2. PostgreSQL

- **Type:** Managed Postgres service (Railway)
- **State:** Online
- **Storage:** Persistent volume managed by Railway
- **Role:** Primary durable datastore for the application
- **Connection:** Via `DATABASE_URL` environment variable

**Suitable for:**
- Durable VAULT999 ledger persistence
- Transactional locking (multi-replica safety)
- Ordered, append-only seal storage
- Constitutional audit trail

**Not suitable for:**
- Caching (use Redis)
- Session state (ephemeral by design)

---

### 3. Redis

- **Type:** Managed Redis service
- **State:** Online
- **Role:** Fast in-memory cache / coordination layer
- **Durability:** **VOLATILE** — data may be lost on restart

**Suitable for:**
- Caching frequently accessed data
- Rate limiting counters
- Short-lived coordination (locks, semaphores)
- Temporary session storage

**Explicitly NOT for:**
- **VAULT999 storage** — never store seal entries in Redis
- Any data requiring durability or audit trail

---

## Runtime Characteristics (Observed)

From production metrics:

| Metric | Status |
|--------|--------|
| CPU | Low, stable utilization (no saturation) |
| Memory | Stable footprint (no leak behavior) |
| Network | Real ingress/egress consistent with live requests |
| Requests | Non-zero request volume observed |
| Error rate | ~0% (no visible failures) |
| Latency | p50/p90/p99 tracked; occasional spikes within operational range |

**Conclusion:** The system is live, serving traffic, and operating normally.

---

## Data Durability Matrix

| Component | Persistence | Survives Restart | Use For |
|-----------|-------------|------------------|---------|
| App Container | ❌ Ephemeral | ❌ No | Code execution only |
| Container Filesystem | ❌ Ephemeral | ❌ No | Temporary files only |
| PostgreSQL | ✅ Persistent | ✅ Yes | VAULT999, all durable state |
| Redis | ⚠️ Volatile | ❌ No | Cache, temporary coordination |

---

## VAULT999 Implications

Because the application container is **ephemeral**, VAULT999 **must**:

1. **Write to PostgreSQL**, not container filesystem
2. **Use database transactions** for concurrency control
3. **Assume concurrent writes** (multiple container instances possible)
4. **Never rely on in-memory state** for durability

**Correct flow:**
```
AI Caller → MCP Tool → PostgreSQL (durable) → Receipt returned
     ↑___________________________________________↓
               (verification via independent query)
```

**Incorrect flow:**
```
AI Caller → MCP Tool → Container Memory ❌ (lost on restart)
```

---

## Environment Variables

Required for production operation:

```bash
# Database (provided by Railway)
DATABASE_URL=postgresql://user:pass@host:5432/arifos

# Optional test database
TEST_DATABASE_URL=postgresql://user:pass@host:5432/arifos_test

# Vault backend selector
VAULT_BACKEND=postgres  # 'postgres' or 'filesystem' (legacy)
```

---

## Mental Model for Contributors

When working with arifOS production:

- **Railway provides execution** — the stage
- **Docker containers run logic** — the actors
- **Postgres provides durability** — the record
- **Code defines authority** — the rules
- **Humans define legitimacy** — the purpose

No part substitutes for another.

---

## Verification Commands

Check service health:

```bash
# Check Railway dashboard
railway status

# Check database connectivity
psql $DATABASE_URL -c "SELECT version();"

# Check vault table exists
psql $DATABASE_URL -c "\dt vault_*"

# Verify recent seals
psql $DATABASE_URL -c "SELECT COUNT(*), MAX(timestamp) FROM vault_ledger;"
```

---

## One-Line Summary

> *arifOS runs in Railway production as a Dockerized application with live Postgres and Redis services. The system is operational, observable, and serving real traffic. Containers are ephemeral; Postgres is the durable persistence layer suitable for VAULT999.*

---

**Constitutional Authority:** Muhammad Arif bin Fazil  
**Contact:** https://arifos.arif-fazil.com  
**Motto:** *DITEMPA BUKAN DIBERI — Forged, Not Given*
