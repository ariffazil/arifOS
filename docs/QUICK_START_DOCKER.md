# arifOS Docker Quick Start

## 🚀 Launch in 3 Commands

```bash
# 1. Build the image
docker build -t arifos-api:v47 .

# 2. Start the container
docker run -d --name arifos-api -p 8000:8000 arifos-api:v47

# 3. Verify it's running
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "vault": "VAULT999",
  "tools": 17,
  "version": "v47.0.0"
}
```

---

## 📋 Complete Setup Guide

### 1. Build the Docker Image

```bash
# Navigate to arifOS directory
cd c:/Users/User/OneDrive/Documents/GitHub/arifOS

# Build with default settings
docker build -t arifos-api:v47 .

# Or build with custom build args
docker build \
  --build-arg ARIFOS_VERSION=v47.0.0 \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --build-arg VCS_REF=$(git rev-parse --short HEAD) \
  -t arifos-api:v47 .
```

**Build time**: ~2-5 minutes (first build), ~30-60 seconds (cached builds)

### 2. Run the Container

**Basic (single container)**:
```bash
docker run -d \
  --name arifos-api \
  -p 8000:8000 \
  arifos-api:v47
```

**With persistent volumes**:
```bash
docker run -d \
  --name arifos-api \
  -p 8000:8000 \
  -v ./ledger:/app/ledger \
  -v ./sessions:/app/sessions \
  -v ./logs:/app/logs \
  arifos-api:v47
```

**With full stack (docker-compose)**:
```bash
# Edit .env file first
nano .env

# Start all services (arifOS + Qdrant)
docker-compose up -d

# View logs
docker-compose logs -f arifos
```

### 3. Verify Deployment

```bash
# Check container status
docker ps

# Check API health
curl http://localhost:8000/health

# Check API documentation
open http://localhost:8000/docs

# View logs
docker logs -f arifos-api

# Execute commands in container
docker exec -it arifos-api bash
```

---

## 🔧 Configuration

### Environment Variables

Edit `.env` file:
```bash
# API Configuration
ARIFOS_ENV=development          # development | production
ARIFOS_PORT=8000               # External API port
FLOOR_ENFORCEMENT_MODE=strict  # strict | permissive | audit_only
TRINITY_ENABLED=true           # Enable Trinity governance

# Vector Database
QDRANT_HOST=qdrant             # Hostname for Qdrant
QDRANT_HTTP_PORT=6333          # HTTP API port
```

### Volume Mounts

| Volume | Purpose | Persistence |
|--------|---------|-------------|
| `./ledger` | Constitutional audit trail | ✅ Required |
| `./sessions` | Agent session data | ✅ Recommended |
| `./logs` | Application logs | ⚠️ Optional |
| `./L1_THEORY` | Constitutional canon | 📖 Read-only |

---

## 🌐 Access Points

Once running, access these endpoints:

| Endpoint | URL | Purpose |
|----------|-----|---------|
| **Root** | http://localhost:8000 | API information |
| **Health** | http://localhost:8000/health | Health check |
| **Docs** | http://localhost:8000/docs | Interactive API docs |
| **ReDoc** | http://localhost:8000/redoc | Alternative docs |
| **OpenAPI** | http://localhost:8000/openapi.json | OpenAPI schema |
| **Federation** | http://localhost:8000/federation/status | SEA-LION router status |

**With docker-compose** (includes Qdrant):
- **Qdrant API**: http://localhost:6333
- **Qdrant Dashboard**: http://localhost:6335/dashboard

---

## 🛠️ Common Operations

### Development Mode

```bash
# Run with code hot-reload (mount source code)
docker run -it \
  --name arifos-dev \
  -p 8000:8000 \
  -v "$(pwd)/arifos_core:/app/arifos_core" \
  arifos-api:v47 \
  uvicorn arifos_core.integration.api.app:app --host 0.0.0.0 --port 8000 --reload
```

### View Logs

```bash
# Real-time logs
docker logs -f arifos-api

# Last 100 lines
docker logs --tail 100 arifos-api

# Logs with timestamps
docker logs --timestamps arifos-api
```

### Execute Commands

```bash
# Open shell in container
docker exec -it arifos-api bash

# Run Python script
docker exec arifos-api python3 scripts/constitutional_checkpoint.py

# Check Trinity status
docker exec arifos-api python3 scripts/trinity.py status

# View ledger entries
docker exec arifos-api ls -la /app/ledger
```

### Stop and Remove

```bash
# Stop container
docker stop arifos-api

# Remove container
docker rm arifos-api

# Remove image
docker rmi arifos-api:v47

# Clean up all (⚠️ removes volumes)
docker-compose down -v
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker logs arifos-api

# Run in foreground to see errors
docker run --rm arifos-api:v47

# Common issue: Port already in use
# Solution: Change port
docker run -d -p 8001:8000 --name arifos-api arifos-api:v47
```

### Health Check Fails

```bash
# Test from inside container
docker exec arifos-api curl http://localhost:8000/health

# If that works, issue is port exposure
docker run -d -p 8000:8000 --name arifos-api arifos-api:v47

# If that fails, check API logs
docker logs arifos-api | grep -i error
```

### Permission Denied

```bash
# Fix volume permissions
sudo chown -R 1000:1000 ./ledger ./sessions ./logs

# Or run with user override (not recommended)
docker run --user 0 arifos-api:v47
```

---

## 📊 Monitoring

### Resource Usage

```bash
# Real-time stats
docker stats arifos-api

# Output:
# CONTAINER     CPU %   MEM USAGE   MEM %   NET I/O
# arifos-api    1.2%    450MB       22%     1.5MB / 800KB
```

### Health Monitoring

```bash
# Continuous health check (every 5 seconds)
watch -n 5 'curl -s http://localhost:8000/health | jq'

# Check container health status
docker inspect arifos-api | jq '.[0].State.Health'
```

---

## 🚀 Production Deployment

### Security Checklist

- ✅ Non-root user (UID 1000) - **Already configured**
- ✅ Health checks enabled - **Already configured**
- ✅ Resource limits set - **Configured in docker-compose.yml**
- ✅ Read-only volumes for L1_THEORY - **Recommended**
- ⚠️ Pin base image version - **Update Dockerfile line 20**
- ⚠️ Use secrets management - **Add to .env**
- ⚠️ Enable TLS/SSL - **Use reverse proxy (Nginx/Traefik)**

### Recommended Stack

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  arifos:
    image: arifos-api:v47
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '0.5'
          memory: 512M
      replicas: 2  # For high availability
    volumes:
      - ./ledger:/app/ledger
      - ./L1_THEORY:/app/L1_THEORY:ro
    environment:
      - ARIFOS_ENV=production
      - FLOOR_ENFORCEMENT_MODE=strict
    healthcheck:
      interval: 30s
      timeout: 10s
      retries: 3

  qdrant:
    image: qdrant/qdrant:v1.7.4
    volumes:
      - qdrant-storage:/qdrant/storage
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - arifos
```

---

## 📚 Additional Resources

- **Full Documentation**: [DOCKER_GUIDE.md](./DOCKER_GUIDE.md)
- **Architecture Details**: [README.md](./README.md)
- **Constitutional Framework**: [L1_THEORY/canon/](./L1_THEORY/canon/)
- **GitHub Issues**: https://github.com/ariffazil/arifOS/issues

---

## 🎯 Next Steps

1. **Test the API**:
   ```bash
   # Check all endpoints
   curl http://localhost:8000/
   curl http://localhost:8000/health
   curl http://localhost:8000/ready
   curl http://localhost:8000/federation/status
   ```

2. **Explore the Docs**:
   - Open http://localhost:8000/docs
   - Try the interactive API playground

3. **Review Logs**:
   ```bash
   docker logs -f arifos-api
   ```

4. **Constitutional Checkpoint**:
   ```bash
   docker exec arifos-api python3 scripts/constitutional_checkpoint.py
   ```

5. **Run Tests** (if available):
   ```bash
   docker exec arifos-api pytest tests/
   ```

---

**Status**: 🟢 SEALED
**Verdict**: Ready for deployment
**Motto**: *DITEMPA BUKAN DIBERI* — Forged, not given

**Constitutional Compliance**:
- F1 (Truth): Health checks verify system state accurately ✅
- F2 (Clarity): Documentation reduces confusion ✅
- F3 (Stability): Resource limits prevent overload ✅
- F4 (Empathy): Non-root user protects host system ✅
- F5 (Humility): Health checks acknowledge uncertainty ✅
- F6 (Amanah): All operations reversible (volumes, containers) ✅
