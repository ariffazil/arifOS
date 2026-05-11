# deploy/ — arifOS Federation Deployment Manifest

## Purpose
This directory is the **canonical source of truth** for the arifOS Constitutional Federation deployment topology. It defines how all services are wired together in production.

## What's Here

| File/Dir | Role |
|----------|------|
| `docker-compose.yml` | Full federation stack definition — arifOS, WELL, GEOX, WEALTH, vault999, postgres, redis, qdrant, Caddy, etc. |
| `Caddyfile` | Reverse proxy configuration for `*.arif-fazil.com` domains |
| `vault999/` | VAULT999 sidecar — append-only constitutional ledger (FastAPI, port 8100) |
| `vault999-writer/` | VAULT999 writer service — seal event ingestion (FastAPI, port 5001) |
| `stack.charter.json` | Deployment epoch charter — tracks which version of each component is deployed |
| `machine-law/` | Legacy compose variant (historical) |

## Deployment Workflow

```
┌─────────────────────────────────────────────────────────┐
│ 1. EDIT: Modify files in this directory (arifOS/deploy/) │
│ 2. COMMIT: git commit in arifOS repo                     │
│ 3. SYNC:  rsync -av deploy/ root@VPS:/root/compose/       │
│ 4. DEPLOY: docker compose up -d (on VPS)                  │
└─────────────────────────────────────────────────────────┘
```

**IMPORTANT:** `/root/compose/` on the VPS is a **working deployment copy**. Do not edit files directly on the VPS — changes made there are not tracked by git. All edits must originate here in `arifOS/deploy/`.

## Image Tags
- `ghcr.io/ariffazil/arifos:<sha>` — built from arifOS repo
- `ghcr.io/ariffazil/well:<sha>` — built from WELL repo
- `ghcr.io/ariffazil/geox:<sha>` — built from GEOX repo
- `ghcr.io/ariffazil/wealth:<sha>` — built from WEALTH repo

Update `docker-compose.yml` image tags when a service is rebuilt.

## Compose Stack (on VPS at /root/compose/)

The VPS runs:
```bash
cd /root/compose
docker compose up -d        # deploy
docker compose pull          # pull latest images
docker compose logs -f      # follow logs
docker compose restart <svc># restart a service
```

## Health Endpoints
| Service | Endpoint |
|---------|----------|
| arifOS | http://localhost:8080/health |
| WELL | http://localhost:8083/health |
| GEOX | http://localhost:8081/health |
| WEALTH | http://localhost:8082/health |
| vault999 | http://localhost:8100/health |
| hermes-agent | http://localhost:3002/health |
| A-FORGE | http://localhost:7071/health |

## Agent Guidelines
- **Do not edit** `/root/compose/` files directly on VPS — those changes are untracked
- **All deployment changes** must be committed to `arifOS/deploy/` first
- **Rebuild services** by pushing new images, then updating the image tag in `docker-compose.yml` and syncing to VPS
- **DITEMPA BUKAN DIBERI** — intelligence is forged, not given. Build with intent.
