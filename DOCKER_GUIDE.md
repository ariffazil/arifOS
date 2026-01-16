# arifOS Docker Deployment Guide

Complete guide for running arifOS Constitutional Governance API in Docker containers.

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Building Images](#building-images)
- [Running Services](#running-services)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

---

## Quick Start

```bash
# 1. Clone repository
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# 2. Configure environment
cp .env.docker.example .env
# Edit .env with your settings

# 3. Start all services
docker-compose up

# 4. Access API
curl http://localhost:8000/health
```

**Access Points:**
- API: [http://localhost:8000](http://localhost:8000)
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Qdrant Dashboard: [http://localhost:6335/dashboard](http://localhost:6335/dashboard)

---

## Prerequisites

### Required
- **Docker**: v24.0+ ([Install](https://docs.docker.com/get-docker/))
- **Docker Compose**: v2.20+ (included with Docker Desktop)
- **Git**: For cloning repository

### System Requirements
| Service | CPU | Memory | Disk |
|---------|-----|--------|------|
| arifOS API | 0.5-2 cores | 512MB-4GB | 1GB |
| Qdrant | 0.25-2 cores | 256MB-2GB | 5GB+ |
| **Total** | **1+ cores** | **1GB+** | **10GB+** |

---

## Configuration

### Environment File

Create `.env` from template:

```bash
cp .env.docker.example .env
```

**Key settings:**

```bash
# API Configuration
ARIFOS_ENV=development          # development | production
ARIFOS_PORT=8000               # External API port
FLOOR_ENFORCEMENT_MODE=strict  # Constitutional enforcement

# Vector Database
QDRANT_HTTP_PORT=6333          # Qdrant HTTP API
QDRANT_WEB_PORT=6335           # Web dashboard
```

### Volume Mounts

Persistent data is stored in:

```
./ledger/      # Constitutional ledger (hash-chained audit trail)
./sessions/    # Agent session data
./logs/        # Application logs
```

These directories are automatically created on first run.

---

## Building Images

### Standard Build

```bash
# Build arifOS API image
docker build -t arifos-api:v47 .

# Tag for Registry (v47)
docker tag arifos-api:v47-local user/arifos-api:v47.0.0

# Or use docker-compose
docker-compose build
```

### Multi-Stage Build (Standard)
The `Dockerfile` is now configured with a robust multi-stage build as the standard:
- 40-60% smaller final image size
- Faster startup times
- Better layer caching
- Production-optimized
- Railway-compatible (no `VOLUME` directive)

### Build Arguments

```bash
docker build \
  --build-arg ARIFOS_VERSION=v47.0.0 \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --build-arg VCS_REF=$(git rev-parse --short HEAD) \
  -t arifos-api:v47 .
```

---

## Running Services

### All Services

```bash
# Start in foreground (see logs)
docker-compose up

# Start in background
docker-compose up -d

# Follow logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f arifos
```

### Individual Services

```bash
# Only arifOS + Qdrant (default)
docker-compose up arifos qdrant

# Include PostgreSQL
docker-compose --profile postgres up

# Include Redis
docker-compose --profile redis up

# All services
docker-compose --profile postgres --profile redis up
```

### Stop Services

```bash
# Stop without removing
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

---

## Architecture

### Service Topology

```
┌─────────────────────────────────────────────────────────────┐
│                        Host Machine                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌─────────────┐                  │
│  │ arifOS API   │◄────────┤   Qdrant    │                  │
│  │ :8000        │  Vector │ :6333/6335  │                  │
│  │              │  Search │             │                  │
│  └──────┬───────┘         └──────┬──────┘                  │
│         │                        │                          │
│         │                        │                          │
│  ┌──────▼────────┐        ┌──────▼──────┐                  │
│  │ Volumes:      │        │ Volumes:    │                  │
│  │ - ledger/     │        │ - storage/  │                  │
│  │ - sessions/   │        │             │                  │
│  │ - logs/       │        │             │                  │
│  └───────────────┘        └─────────────┘                  │
│                                                              │
│  ┌─────────────────────────────────────┐                   │
│  │ Optional Services (profiles)        │                   │
│  │ - PostgreSQL :5432 (ledger storage) │                   │
│  │ - Redis :6379 (caching)             │                   │
│  └─────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### Network Configuration

- **Network**: `arifos-network` (bridge)
- **Subnet**: `172.28.0.0/16`
- **DNS**: Automatic service discovery

Services communicate via internal hostnames:
- `arifos` → arifOS API
- `qdrant` → Vector database
- `postgres` → PostgreSQL (if enabled)
- `redis` → Redis (if enabled)

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Error: Bind for 0.0.0.0:8000 failed: port is already allocated

# Solution: Change port in .env
ARIFOS_PORT=8001
```

#### 2. Qdrant Connection Failed

```bash
# Error: Connection to qdrant:6333 refused

# Check Qdrant is running
docker-compose ps qdrant

# Check Qdrant logs
docker-compose logs qdrant

# Restart Qdrant
docker-compose restart qdrant
```

#### 3. Permission Denied (Volumes)

```bash
# Error: Permission denied: '/app/ledger'

# Fix ownership
sudo chown -R 1000:1000 ./ledger ./sessions ./logs
```

#### 4. Out of Memory

```bash
# Error: Killed (OOM)

# Increase Docker memory limit
# Docker Desktop: Settings → Resources → Memory → 4GB+

# Or adjust service limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Qdrant health
curl http://localhost:6333/health

# PostgreSQL health (if enabled)
docker exec arifos-postgres pg_isready -U arifos
```

### Inspecting Containers

```bash
# List running containers
docker-compose ps

# Enter arifOS container
docker exec -it arifos-api bash

# Enter Qdrant container
docker exec -it arifos-qdrant sh

# View container resource usage
docker stats
```

### Logs

```bash
# All services
docker-compose logs

# Last 100 lines
docker-compose logs --tail=100

# Follow in real-time
docker-compose logs -f

# Specific service
docker-compose logs -f arifos

# Since specific time
docker-compose logs --since 2024-01-16T10:00:00
```

---

---

## Railway Deployment (Cloud)

Railway.app does NOT support Docker `VOLUME` directives in the `Dockerfile`. Our unified v47 `Dockerfile` is pre-configured for Railway compatibility.

### Best Practices for Railway

1. **Volume Persistence**: Railway manages persistence via their dashboard.
   - Dashboard → Add Volume → Mount path: `/app/ledger`
2. **Environment Variables**: Add these in the Railway dashboard "Variables" tab, not in a `.env` file.
3. **Port**: Railway sets the `PORT` environment variable automatically.

### Railway Build Settings (if needed)

If you need to specify the build command manually:
- **Build Command**: `docker build -t arifos-api:v47 .`
- **Start Command**: `python scripts/arifos_sse_server.py`

---

## Production Deployment

### Best Practices

#### 1. Use Specific Versions

```bash
# Pin exact versions
image: arifos-api:v47.0.0
image: qdrant/qdrant:v1.7.4
```

#### 2. Enable Health Checks

Already configured in `docker-compose.yml`:

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "..."]
  interval: 30s
  timeout: 10s
  retries: 3
```

#### 3. Configure Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
    reservations:
      cpus: '0.5'
      memory: 512M
```

#### 4. Use Environment Variables

```bash
# Never hardcode secrets in docker-compose.yml
environment:
  - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}  # ✅ Good
  - POSTGRES_PASSWORD=changeme              # ❌ Bad
```

#### 5. Volume Backups

```bash
# Backup ledger
docker run --rm \
  -v arifos-ledger:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/ledger-$(date +%Y%m%d).tar.gz -C /data .

# Backup Qdrant
docker run --rm \
  -v arifos-qdrant-storage:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/qdrant-$(date +%Y%m%d).tar.gz -C /data .
```

#### 6. Monitoring

```bash
# Container metrics
docker stats

# Export metrics (Prometheus)
# Add prometheus-exporter service to docker-compose.yml
```

### Production Environment File

```bash
# .env.production
ARIFOS_ENV=production
FLOOR_ENFORCEMENT_MODE=strict
LOG_LEVEL=warning
ARIFOS_PORT=8000

# Use strong passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Resource limits
ARIFOS_CPU_LIMIT=4
ARIFOS_MEMORY_LIMIT=8G
```

### Deployment Steps

```bash
# 1. Update code
git pull origin main

# 2. Build new image
docker-compose build --no-cache

# 3. Backup data
./scripts/backup_volumes.sh

# 4. Stop services
docker-compose down

# 5. Start with new image
docker-compose up -d

# 6. Verify health
curl http://localhost:8000/health
docker-compose logs -f arifos
```

### Security Checklist

- [ ] Run as non-root user (✅ already configured)
- [ ] Use read-only file systems where possible
- [ ] Enable AppArmor/SELinux profiles
- [ ] Use secrets management (Docker secrets, Vault)
- [ ] Enable TLS/SSL (use reverse proxy like Nginx)
- [ ] Regular security updates (`docker-compose pull`)
- [ ] Monitor logs for suspicious activity
- [ ] Restrict network access (firewall rules)
- [ ] Enable audit logging
- [ ] Regular backups (automated)

---

## Advanced Usage

### Custom Entrypoint

Override CMD in docker-compose.yml:

```yaml
services:
  arifos:
    command: >
      uvicorn arifos_core.api.app:app
      --host 0.0.0.0
      --port 8000
      --workers 4
      --log-level debug
```

### Development Mode

Mount source code for live reloading:

```yaml
services:
  arifos:
    volumes:
      - ./arifos_core:/app/arifos_core
    command: >
      uvicorn arifos_core.api.app:app
      --host 0.0.0.0
      --port 8000
      --reload
```

### CI/CD Integration

```bash
# .github/workflows/docker.yml
- name: Build Docker image
  run: docker build -t arifos-api:${{ github.sha }} .

- name: Run tests in container
  run: |
    docker run --rm arifos-api:${{ github.sha }} pytest

- name: Push to registry
  run: |
    docker tag arifos-api:${{ github.sha }} registry.example.com/arifos-api:latest
    docker push registry.example.com/arifos-api:latest
```

---

## File Structure

```
arifOS/
├── Dockerfile                  # Unified multi-stage build
├── docker-compose.yml          # Service orchestration
├── .dockerignore              # Build context exclusions
├── .env.docker.example        # Environment template
├── DOCKER_GUIDE.md            # This file
├── arifos_core/               # Application code
├── L1_THEORY/                 # Constitutional canon
├── L2_PROTOCOLS/              # Constitutional protocols
├── ledger/                    # Persistent ledger (created)
├── sessions/                  # Session data (created)
└── logs/                      # Application logs (created)
```

---

## Constitutional Integration

All Docker operations respect arifOS's 12-floor constitutional governance:

- **F1 (Truth)**: Health checks verify system state
- **F2 (Clarity)**: Logs provide clear audit trails
- **F3 (Stability)**: Resource limits prevent destructive overload
- **F4 (Empathy)**: Non-root user protects host system
- **F5 (Humility)**: Health checks acknowledge uncertainty
- **F6 (Amanah)**: Volume mounts are reversible
- **F7 (RASA)**: Logs listen to system feedback
- **F8 (Tri-Witness)**: Multi-container validation
- **F9 (Anti-Hantu)**: Symbolic mode maintained
- **F10 (Ontology)**: Clear service boundaries
- **F11 (Command Auth)**: Explicit user control
- **F12 (Injection)**: Input validation in API layer

---

## Support

- **GitHub Issues**: https://github.com/ariffazil/arifOS/issues
- **Documentation**: https://github.com/ariffazil/arifOS/blob/main/README.md
- **Email**: arifbfazil@gmail.com

---

**Version**: v47.0.0
**Last Updated**: 2026-01-16
**Status**: SEALED

*Forged, not given — Truth must cool before it rules.*
