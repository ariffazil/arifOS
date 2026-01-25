# AAA Cluster Deployment (v52.4.0)

Petronas Pattern: 3 Independent Towers with Crash Recovery

```
     APEX (Judge)
         |
    ┌────┴────┐
    │  ARIF   │  ← Heavy compute, may hang
    │ (Mind)  │
    └────┬────┘
         │
     AXIS (Spine)  ← Loop Bootstrap recovers crashed sessions
```

## Architecture

| Server | Role | Port | Transport | Dependencies |
|--------|------|------|-----------|--------------|
| AXIS | Authority & Memory | 8001 | SSE | pydantic, fastmcp |
| ARIF | Mind + Heart | 8002 | SSE | + litellm, dspy |
| APEX | Judge | 8003 | SSE | pydantic, fastmcp |

## File Structure

```
deploy/AAA/
├── AXIS/
│   ├── Dockerfile          # Optimized for session management
│   ├── server.py           # Production-ready AXIS server
│   ├── requirements.txt    # Minimal deps
│   └── railway.toml        # Railway config
├── ARIF/
│   ├── Dockerfile          # Heavy compute allocation
│   ├── server.py           # Production-ready ARIF server
│   ├── requirements.txt    # + LLM support
│   └── railway.toml
├── APEX/
│   ├── Dockerfile          # High isolation
│   ├── server.py           # Production-ready APEX server
│   ├── requirements.txt    # Minimal deps
│   └── railway.toml
├── docker-compose.cluster.yml
└── README.md
```

## Features

### JSON Structured Logging
All servers output JSON logs for Railway capture:
```json
{"timestamp": "2026-01-25T10:00:00Z", "level": "INFO", "service": "AXIS", "message": "..."}
```

### Loop Bootstrap (Crash Recovery)
If ARIF hangs/crashes mid-session:
1. AXIS detects orphaned session on next `000_init`
2. Auto-seals with `SABAR` verdict
3. New session starts with recovery context

### Health Checks
All servers expose `/health` (ping endpoint):
```bash
curl http://localhost:8001/health  # AXIS
curl http://localhost:8002/health  # ARIF
curl http://localhost:8003/health  # APEX
```

## Local Development

```bash
# Start the cluster
cd deploy/AAA
docker-compose -f docker-compose.cluster.yml up --build

# View logs (JSON structured)
docker-compose -f docker-compose.cluster.yml logs -f

# Test crash recovery
curl http://localhost:8001/axis_000_init    # Start session
docker kill arifos-arif                      # Simulate crash
docker-compose up arif                       # Restart
curl http://localhost:8001/axis_000_init    # Previous auto-recovered

# Stop cluster
docker-compose -f docker-compose.cluster.yml down
```

## Railway Deployment

Each server has its own `railway.toml`:

```bash
# Deploy from repo root
railway link
railway up --service axis
railway up --service arif
railway up --service apex
```

### ⚠️ CRITICAL: Volume Configuration Required

**Loop Bootstrap requires persistent storage.** Without it, crash recovery fails.

```bash
# Create and attach volume for AXIS (required!)
railway volume create sessions
railway volume attach sessions /app/arifos/mcp/sessions --service axis

# Optional: VAULT persistence
railway volume create vault
railway volume attach vault /app/VAULT999 --service axis
```

| Path | Purpose | Required? |
|------|---------|-----------|
| `/app/arifos/mcp/sessions` | `open_sessions.json` for crash recovery | **YES** |
| `/app/VAULT999` | Permanent constitutional storage | Recommended |

See: https://docs.railway.app/guides/volumes

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ARIFOS_ENV` | production | Environment mode |
| `ARIFOS_ROLE` | (required) | AXIS, ARIF, or APEX |
| `PORT` | 8001/2/3 | Server port |
| `ARIFOS_STRICT_TOKEN` | false | Enable token validation |

## Command Line

Each server.py supports `--transport`:

```bash
python server.py --transport sse    # Railway (default)
python server.py --transport stdio  # Local development
```

---

**DITEMPA BUKAN DIBERI**
