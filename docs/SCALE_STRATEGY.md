# arifOS Scale Strategy: The Migration Protocol

**Authority:** 888_JUDGE_VRF.4e83c9222b5e9f1efa336e08d288f67345cf8354 (Sealed Audit)
**Status:** SEALED (v52)

> **Core Principle:** "Entropy reduction ($\Delta S < 0$) is the primary goal. Capability is secondary."

---

## I. The Trigger System (When to Scale)
We operate under a "Stay Monolith" policy until **measurable pain** triggers a migration.

| Trigger | Threshold | Measurement Source | Required Action |
|---------|-----------|--------------------|-----------------|
| **Traffic** | > 100 req/sec (sustained) | Cloud Run Metrics | Split to Microservices |
| **Users** | > 500 concurrent | Auth0 / Session Logs | Multi-tenant Cluster |
| **Memory** | > 1GB VAULT | Container RAM usage | External DB (Phase 2) |
| **Latency** | > 2000ms (p99) | Trace logs | Parallel Engine Execution |
| **Failure** | > 1% Error Rate | 5xx Status Codes | Fault Isolation |

**Current Status (Q1 2026):**
- Traffic: <10 req/sec (GREEN)
- Users: 1 (GREEN)
- Strategy: **Constitutional Monolith (Phase 1)**

---

## II. The Migration Phases

### Phase 1: Constitutional Monolith (Current)
**Optimized for:** Sovereign User, Low Latency, Low Entropy.
- **Architecture:** Single Docker Container (`arifos/core` + `sse_adapter`)
- **State:** In-memory / Cloud Storage Stub
- **Transport:** Internal Function Calls

### Phase 2: Hybrid Persistence (Q2 2026)
**Optimized for:** Data Safety.
- **Trigger:** Production Usage / Container Restarts
- **Change:** Externalize `VAULT-999` to Cloud Firestore/PostgreSQL.
- **Architecture:** Monolith + Remote DB.

### Phase 3: The AAA Cluster (Microservices)
**Optimized for:** Scale & Multi-tenancy.
- **Trigger:** >100 req/sec.
- **Change:** Split `arifos-agi`, `arifos-asi`, `arifos-apex` into separate services.
- **Transport:** gRPC / Mesh.
- **Risk:** High Entropy (+200% complexity).

---

## III. Anti-Patterns (Forbidden)
1.  **Premature Splitting:** Creating microservices before hitting 100 req/sec.
2.  **Resume-Driven Development:** Adding Kubernetes for <10 users.
3.  **Entropy Leak:** Decentralizing the "Truth" (VAULT) without Raft/Paxos consensus.

**Verdict:** We build for the *current* reality, not the *imagined* future.
