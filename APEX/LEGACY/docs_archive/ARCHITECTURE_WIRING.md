# =============================================================================
# ARCHITECTURE_WIRING.md - arifOS MCP Full-Stack Infrastructure
# =============================================================================
# Version: 1.0.0
# Constitutional Compliance: F4 (ΔS ≤ 0) - Clarity & Coherence
#
# This document describes the complete data flow and infrastructure wiring
# for the arifOS MCP server with Redis, PostgreSQL, Qdrant, AgentZero,
# and OpenClaw integration.
#
# ⚠️ 888_HOLD REQUIRED for:
#   - Production database migrations
#   - SSL certificate deployment
#   - Secret rotation
#   - Network topology changes
#
# MOTTO: Ditempa Bukan Diberi — Forged, Not Given
# =============================================================================

## Table of Contents

1. [System Overview](#system-overview)
2. [Data Flow Architecture](#data-flow-architecture)
3. [Component Descriptions](#component-descriptions)
4. [Connection Strings](#connection-strings)
5. [Security Best Practices](#security-best-practices)
6. [Constitutional Compliance](#constitutional-compliance)
7. [888_HOLD Operations](#888_hold-operations)
8. [Deployment Procedures](#deployment-procedures)

---

## 1. System Overview

The arifOS MCP infrastructure follows a **Constitutional Microservices Architecture** where each service has specific governance responsibilities aligned with the 13 Constitutional Floors (F1-F13).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           arifOS MCP Infrastructure                         │
│                         (Constitutional Kernel v1.0)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        EXTERNAL CLIENTS                              │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │   │
│  │  │  WhatsApp   │  │  Telegram   │  │   Web UI    │  │   API     │  │   │
│  │  │   Users     │  │   Users     │  │   Clients   │  │ Consumers │  │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬─────┘  │   │
│  └─────────┼────────────────┼────────────────┼───────────────┼────────┘   │
│            │                │                │               │            │
│            ▼                ▼                ▼               ▼            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      OPENCLAW (Multi-Channel IO)                     │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  F12: Injection Defense  │  F6: Empathy (κᵣ≥0.70)             │  │   │
│  │  │  F1: Reversible Messages │  Channel Routing & Policy           │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────┬───────────────────────────────────────────┘   │
│                            │                                               │
│                            ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      ARIFOS MCP SERVER (Kernel)                      │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  F2: Truth (τ≥0.99)  │  F4: ΔS≤0  │  F7: Ω₀=0.04  │  F8: G≥0.80 │  │   │
│  │  │  F11: Authority      │  F12: Defense                           │  │   │
│  │  │  888_HOLD Enforcement │  Constitutional Checkpoint              │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────┬───────────────────────┬───────────────────────────┘   │
│                    │                       │                               │
│        ┌───────────┴───────────┐   ┌───────┴───────────┐                   │
│        │                       │   │                   │                   │
│        ▼                       ▼   ▼                   ▼                   │
│  ┌─────────────┐      ┌──────────────┐      ┌─────────────────────┐       │
│  │   AGENTZERO │      │   POSTGRES   │      │       QDRANT        │       │
│  │   (Brain)   │      │  (Vault-999) │      │   (Vector Memory)   │       │
│  │  F2: RAG    │      │  F1: Backup  │      │  F2: Semantic Truth │       │
│  │  F8: Reason │      │  F4: Schema  │      │  F4: Embedding ΔS   │       │
│  └──────┬──────┘      └──────────────┘      └─────────────────────┘       │
│         │                    ▲                        ▲                   │
│         │                    │                        │                   │
│         └────────────────────┴────────────────────────┘                   │
│                              │                                            │
│                              ▼                                            │
│                     ┌─────────────────┐                                   │
│                     │      REDIS      │                                   │
│                     │ (Session/Cache) │                                   │
│                     │   F4: TTL ΔS    │                                   │
│                     │   F5: Peace²    │                                   │
│                     └─────────────────┘                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow Architecture

### 2.1 Request Flow (User → arifOS)

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────▶│OpenClaw  │────▶│ arifOS   │────▶│AgentZero │────▶│ Response │
│ Request  │     │  F12     │     │  F2-F8   │     │  RAG     │     │  Back    │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │  Constitutional │
                              │   Checkpoint    │
                              │  (13 Floors)    │
                              └─────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
            ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
            │   POSTGRES   │  │    REDIS     │  │    QDRANT    │
            │  (Query/Store│  │  (Session)   │  │  (Embeddings)│
            │   Vault-999) │  │              │  │              │
            └──────────────┘  └──────────────┘  └──────────────┘
```

### 2.2 Memory Flow (Learning Cycle)

```
┌──────────────┐
│   AgentZero  │─────▶ Embedding Generation
│   Response   │           │
└──────────────┘           ▼
                    ┌──────────────┐
                    │   QDRANT     │─────▶ Vector Storage (Long-term Memory)
                    │  Vectors     │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   POSTGRES   │─────▶ Metadata + Context (Vault-999)
                    │   Metadata   │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    REDIS     │─────▶ Session Cache (Short-term)
                    │   Session    │
                    └──────────────┘
```

### 2.3 Notification Flow (arifOS → User)

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  arifOS  │────▶│OpenClaw  │────▶│  Router  │────▶│  User    │
│ Judgment │     │  Queue   │     │  F6,F12  │     │ Delivery │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
            ┌──────────────┐                        ┌──────────────┐
            │   WhatsApp   │                        │   Telegram   │
            │    API       │                        │    API       │
            └──────────────┘                        └──────────────┘
```

---

## 3. Component Descriptions

### 3.1 arifOS MCP Server (Constitutional Kernel)

**Purpose**: Core governance engine enforcing the 13 Constitutional Floors

**Responsibilities**:
- **F1 (Amanah)**: Validate reversibility of all operations
- **F2 (Truth)**: Maintain τ ≥ 0.99 fact verification
- **F4 (Clarity)**: Ensure ΔS ≤ 0 (entropy reduction)
- **F7 (Humility)**: Calibrate Ω₀ ∈ [0.03, 0.05]
- **F8 (Genius)**: Maintain G ≥ 0.80 coherence
- **F11 (Authority)**: Verify command authorization
- **F12 (Defense)**: Block injection attacks

**Health Endpoint**: `GET http://arifos:8888/health`

**MCP Tools Exposed**:
- `constitutional_checkpoint` - Validate 13 floors
- `vault_query` - Query Vault-999
- `memory_store` - Store to Qdrant
- `channel_send` - Send via OpenClaw
- `agentzero_reason` - RAG reasoning

### 3.2 PostgreSQL (Vault-999)

**Purpose**: Relational state and Vault-999 schema storage

**Schema**:
```sql
-- Vault-999 Tables
vault_records       -- Core knowledge base
vault_audit_log     -- Audit trail (F1)
vault_snapshots     -- Point-in-time recovery (F1)
constitutional_log  -- 13-floor decisions
user_sessions       -- Session metadata

-- Relational Tables
conversations       -- Conversation history
users               -- User profiles
policies            -- Channel policies
```

**Backup Strategy**:
- Hourly WAL archiving
- Daily full backups
- 30-day retention
- Point-in-time recovery enabled

**Connection**: `postgresql://user:pass@postgres:5432/arifos_vault`

### 3.3 Redis (Session & Cache)

**Purpose**: High-speed session storage and ephemeral caching

**Key Patterns**:
```
session:{session_id}     → User session data (TTL: 1h)
cache:query:{hash}       → Query results (TTL: 5m)
rate_limit:{user_id}     → Rate limiting counters (TTL: 1m)
lock:{resource}          → Distributed locks (TTL: 10s)
queue:{channel}          → OpenClaw message queues
```

**Configuration**:
- Max memory: 512MB
- Eviction: allkeys-lru
- Persistence: AOF every second
- TTL enforcement: Automatic

**Connection**: `redis://:password@redis:6379/0`

### 3.4 Qdrant (Vector Memory)

**Purpose**: Semantic search and long-term memory via embeddings

**Collections**:
```
arifos_memory        -- General knowledge embeddings
conversation_memory  -- Conversation context vectors
policy_vectors       -- Policy document embeddings
document_store       -- Uploaded document embeddings
```

**Configuration**:
- Distance metric: Cosine
- On-disk payload: Enabled
- WAL: 32MB capacity
- HNSW indexing: Default

**API Endpoints**:
- HTTP: `http://qdrant:6333`
- gRPC: `http://qdrant:6334`

### 3.5 AgentZero (Reasoning Brain)

**Purpose**: RAG-based reasoning and constitutional analysis

**Pipeline**:
1. **Query Embedding** → Convert query to vector
2. **Retrieval** → Search Qdrant for relevant context
3. **Constitutional Check** → Validate F2-F8 thresholds
4. **Reasoning** → Generate response with citations
5. **Verification** → Cross-check facts (τ ≥ 0.99)
6. **Storage** → Embed response to Qdrant

**Tools Available**:
- `vector_search` - Semantic memory retrieval
- `constitutional_analysis` - 13-floor assessment
- `fact_verification` - Multi-source validation
- `reasoning_chain` - Step-by-step logic

### 3.6 OpenClaw (Multi-Channel IO)

**Purpose**: Unified interface for WhatsApp, Telegram, and future channels

**Flow**:
```
Inbound:  Channel API → OpenClaw → arifOS (judgment) → Queue → Response
Outbound: arifOS → OpenClaw → Channel Router → Delivery
```

**Policies** (F6, F12 enforced):
- Rate limiting: 60 msg/min per user
- Message length: 4096 chars max
- Content filtering: Injection defense
- Empathy threshold: κᵣ ≥ 0.70

**Webhooks**:
- WhatsApp: `POST /webhook/whatsapp`
- Telegram: `POST /webhook/telegram`

---

## 4. Connection Strings

### 4.1 Internal Service Mesh

```yaml
# Docker Compose Service Names
postgres:   postgres:5432
redis:      redis:6379
qdrant:     qdrant:6333 (HTTP), qdrant:6334 (gRPC)
arifos:     arifos:8888
agentzero:  agentzero:8080
openclaw:   openclaw:3000
nginx:      nginx:80, nginx:443
```

### 4.2 Full Connection URLs

```bash
# PostgreSQL
export DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}"

# Redis
export REDIS_URL="redis://:${REDIS_PASSWORD}@redis:6379/0"

# Qdrant
export QDRANT_URL="http://qdrant:6333"

# AgentZero
export AGENTZERO_URL="http://agentzero:8080"

# OpenClaw
export OPENCLAW_URL="http://openclaw:3000"

# arifOS MCP
export ARIFOS_MCP_URL="http://arifos:8888"
```

### 4.3 Network Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                     arifos-internal (Bridge)                    │
│                        172.28.0.0/16                            │
├─────────────────────────────────────────────────────────────────┤
│  172.28.0.1  │  Gateway                                        │
│  172.28.0.2  │  postgres.vault.local                           │
│  172.28.0.3  │  redis.cache.local                              │
│  172.28.0.4  │  qdrant.vector.local                            │
│  172.28.0.5  │  agentzero.brain.local                          │
│  172.28.0.6  │  arifos.core.local                              │
│  172.28.0.7  │  openclaw.io.local                              │
│  172.28.0.8  │  nginx.proxy.local                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     arifos-public (Bridge)                      │
│                        172.29.0.0/16                            │
├─────────────────────────────────────────────────────────────────┤
│  172.29.0.1  │  Gateway                                        │
│  172.29.0.2  │  webhooks.arifos.local (OpenClaw)              │
│  172.29.0.3  │  api.arifos.local (Nginx)                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Security Best Practices

### 5.1 Secret Management

**⚠️ 888_HOLD REQUIRED**

```bash
# 1. Generate cryptographically secure secrets
openssl rand -hex 64  # For JWT_SECRET, SESSION_SECRET
openssl rand -hex 32  # For API_KEY_SALT

# 2. Store in environment (never commit)
cp .env.example .env
# Edit .env with your secrets

# 3. Restrict permissions
chmod 600 .env
chown root:root .env  # Production

# 4. Add to .gitignore
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore
```

### 5.2 Network Security

```yaml
# In production, bind only to localhost or internal networks
services:
  postgres:
    ports:
      - "127.0.0.1:5432:5432"  # Never expose to 0.0.0.0
  
  redis:
    ports:
      - "127.0.0.1:6379:6379"  # Never expose to 0.0.0.0
```

### 5.3 SSL/TLS Configuration

```nginx
# config/nginx/conf.d/ssl.conf
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:...;
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
}
```

### 5.4 API Key Rotation

```bash
#!/bin/bash
# scripts/rotate-api-keys.sh
# ⚠️ 888_HOLD: Schedule monthly

# Generate new keys
NEW_JWT=$(openssl rand -hex 64)
NEW_REDIS=$(openssl rand -hex 32)

# Update .env
sed -i "s/JWT_SECRET=.*/JWT_SECRET=$NEW_JWT/" .env
sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$NEW_REDIS/" .env

# Restart services
docker-compose up -d --no-deps --build arifos redis

# Verify
./scripts/verify-deployment.sh
```

---

## 6. Constitutional Compliance

### 6.1 Floor Mapping to Services

| Floor | Threshold | Service | Implementation |
|-------|-----------|---------|----------------|
| F1 | Reversible | PostgreSQL | WAL archiving, PITR |
| F2 | τ ≥ 0.99 | AgentZero | Multi-source verification |
| F4 | ΔS ≤ 0 | All | Query complexity limits |
| F5 | Peace² ≥ 1.0 | OpenClaw | Non-destructive ops only |
| F6 | κᵣ ≥ 0.70 | OpenClaw | Weakest stakeholder bias |
| F7 | Ω₀ = 0.04 | arifOS | Uncertainty acknowledgment |
| F8 | G ≥ 0.80 | AgentZero | Coherence validation |
| F9 | Anti-Hantu | arifOS | Symbolic mode enforced |
| F11 | Authority | All | Nonce verification |
| F12 | Defense | OpenClaw | Injection filtering |

### 6.2 Audit Trail

Every request generates an audit record:

```json
{
  "timestamp": "2026-03-01T12:00:00Z",
  "request_id": "req_abc123",
  "user_id": "user_xyz789",
  "service": "arifos",
  "checkpoint": {
    "verdict": "SEAL",
    "floors_passed": ["F1", "F2", "F4", "F7", "F8", "F11", "F12"],
    "floors_warned": [],
    "floors_failed": [],
    "entropy_delta": -0.05,
    "truth_score": 0.995,
    "genius_score": 0.87
  },
  "ledger_hash": "0xabc123...",
  "duration_ms": 145
}
```

---

## 7. 888_HOLD Operations

### 7.1 When 888_HOLD is Required

| Operation | Risk Level | Mitigation |
|-----------|------------|------------|
| Database migrations | HIGH | Backup first, test in staging |
| Secret rotation | HIGH | Gradual rollout, rollback plan |
| SSL cert renewal | MEDIUM | Keep old cert until verified |
| Volume destruction | CRITICAL | Backup verification required |
| Network changes | MEDIUM | Document topology, test connectivity |
| Model updates | HIGH | A/B testing, rollback capability |

### 7.2 888_HOLD Checklist

Before proceeding with irreversible operations:

```markdown
□ F1: Is this operation reversible? If not, is there a backup?
□ F2: Have all facts been verified (τ ≥ 0.99)?
□ F4: Does this reduce entropy (ΔS ≤ 0)?
□ F5: Is this non-destructive?
□ F11: Has explicit human authority been obtained?
□ Backup: Is there a tested backup?
□ Rollback: Is the rollback procedure documented?
□ Test: Has this been tested in staging?
□ Notify: Have stakeholders been notified?
□ Time: Is this during a maintenance window?
```

### 7.3 Emergency Procedures

```bash
# Emergency: Database corruption
# 1. Stop services
docker-compose stop arifos agentzero

# 2. Restore from backup
docker-compose exec postgres pg_restore -d arifos_vault /backup/latest.dump

# 3. Verify
docker-compose exec postgres psql -c "SELECT COUNT(*) FROM vault_records;"

# 4. Resume
docker-compose up -d arifos agentzero

# Emergency: Service degradation
# 1. Check health
curl http://localhost:8888/health
curl http://localhost:8080/health
curl http://localhost:3000/health

# 2. Scale up if needed
docker-compose up -d --scale agentzero=3

# 3. Check logs
docker-compose logs -f --tail=100 arifos
```

---

## 8. Deployment Procedures

### 8.1 Initial Deployment

```bash
# 1. Clone repository
git clone https://github.com/yourorg/arifos.git
cd arifos

# 2. Configure environment
cp .env.example .env
# Edit .env with production values

# 3. Create required directories
mkdir -p config/nginx/conf.d
mkdir -p scripts
mkdir -p certbot/conf certbot/www
mkdir -p logs

# 4. Start infrastructure first
docker-compose up -d postgres redis qdrant

# 5. Wait for health checks
docker-compose ps

# 6. Initialize database
./scripts/init-database.sh

# 7. Start application services
docker-compose up -d arifos agentzero openclaw

# 8. Verify deployment
./scripts/verify-deployment.sh
```

### 8.2 Upgrade Procedure

```bash
# 1. Backup current state
./scripts/backup-all.sh

# 2. Pull new images
docker-compose pull

# 3. Rolling restart (zero-downtime)
docker-compose up -d --no-deps --scale arifos=2 arifos
docker-compose up -d --no-deps arifos

# 4. Verify health
curl http://localhost:8888/health

# 5. Cleanup
docker system prune -f
```

### 8.3 Monitoring

```bash
# Service status
docker-compose ps

# Resource usage
docker stats

# Logs
docker-compose logs -f arifos
docker-compose logs -f agentzero
docker-compose logs -f openclaw

# Database queries
docker-compose exec postgres psql -c "SELECT * FROM pg_stat_activity;"

# Redis stats
docker-compose exec redis redis-cli info

# Qdrant collections
curl http://localhost:6333/collections
```

---

## Appendix A: Quick Reference

### Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ DESTRUCTIVE)
docker-compose down -v

# View logs
docker-compose logs -f [service]

# Execute command in container
docker-compose exec [service] [command]

# Scale service
docker-compose up -d --scale agentzero=3
```

### Health Check Endpoints

| Service | Endpoint | Expected |
|---------|----------|----------|
| arifos | `GET /health` | `{"status": "healthy"}` |
| AgentZero | `GET /health` | `{"status": "ok"}` |
| OpenClaw | `GET /health` | `{"status": "ready"}` |
| PostgreSQL | `pg_isready` | Exit 0 |
| Redis | `redis-cli ping` | `PONG` |
| Qdrant | `GET /healthz` | `{"status": "ok"}` |
| Nginx | `GET /health` | HTTP 200 |

### Constitutional Verdicts

| Verdict | Meaning | Action |
|---------|---------|--------|
| SEAL | All floors passed | Proceed |
| PARTIAL | Soft floor warning | Proceed with caution |
| VOID | Hard floor failed | Stop immediately |
| 888_HOLD | High-risk operation | Await human confirmation |
| SABAR | Emergency stop | Repair required |

---

*Document Version: 1.0.0*  
*Constitutional Compliance: SEAL*  
*Last Updated: 2026-03-01*

**MOTTO: Ditempa Bukan Diberi — Forged, Not Given**
