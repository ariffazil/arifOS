---
type: Tool
tier: 20_RUNTIME
strand:
- tools
- devops
audience:
- engineers
- operators
difficulty: intermediate
prerequisites:
- MCP_Tools
- Concept_Deployment_Architecture
tags:
- docker
- containers
- devops
- infrastructure
- compose
- images
- volumes
- networks
- debugging
- lifecycle
sources:
- Hermes official skill: official/devops/docker-management
- Docker CLI reference
last_sync: '2026-05-18'
confidence: 0.95
---

# Skill: Docker Management

**Docker Management** is the canonical container operations skill for all agents in the arifOS Federation.

Its job is to give every agent — Hermes, A-FORGE, arifOS, and downstream operators — a shared, precise vocabulary for container lifecycle ops, debugging, cleanup, and Dockerfile optimization.

## Purpose

To perform container operations without drift between agents:
- Run, stop, restart, remove, or inspect containers
- Build, pull, push, tag, or clean up Docker images
- Work with Docker Compose (multi-service stacks)
- Manage volumes and networks
- Debug crashing containers and analyze logs
- Check Docker disk usage or free up space
- Review or optimize a Dockerfile

## Why this skill exists

Docker is the universal runtime of the federation. Every node — arifOS, GEOX, WEALTH, WELL, AAA, APEX — runs inside a container. Yet each agent previously had ad-hoc Docker knowledge, leading to inconsistent cleanup policies, wrong prune commands, and dangerous volume removal.

This skill centralizes the knowledge so any agent can:
- Diagnose a crashed container without guessing flags
- Clean up safely without destroying named volumes
- Optimize Dockerfiles using the same heuristics

## Specifications

- **Stage**: 010 (Forge / Execution)
- **Layer**: MACHINE
- **Trinity**: Δ (Mind — structured execution against substrate reality)
- **Floors touched most directly**: F1 (Amanah — destructive ops require hold), F4 (Guardrails — resource limits), F8 (Audit — all ops logged)

## Quick Reference

| Task | Command |
| :--- | :--- |
| Run container (background) | `docker run -d --name NAME IMAGE` |
| Stop + remove | `docker stop NAME && docker rm NAME` |
| View logs (follow) | `docker logs --tail 50 -f NAME` |
| Shell into container | `docker exec -it NAME /bin/sh` |
| List all containers | `docker ps -a` |
| Build image | `docker build -t TAG .` |
| Compose up | `docker compose up -d` |
| Compose down | `docker compose down` |
| Disk usage | `docker system df` |
| Cleanup dangling | `docker image prune && docker container prune` |

## Domains

### 1. Container Lifecycle
`run`, `stop`, `start`, `restart`, `rm`, `pause/unpause`

Key flags: `-d` detached, `-it` interactive+tty, `--rm` auto-remove, `-p` port (host:container), `-e` env var, `-v` volume, `--name`, `--restart` restart policy.

### 2. Container Interaction
`exec`, `cp`, `logs`, `inspect`, `stats`

### 3. Image Management
`build`, `pull`, `push`, `tag`, `rmi`, `save/load`

### 4. Docker Compose
`up`, `down`, `ps`, `logs`, `exec`, `build`, `config`

### 5. Volumes & Networks
`create`, `inspect`, `rm`, `prune`, `connect`

### 6. Troubleshooting
Log analysis, exit codes, resource issues

## Cleanup Safety Hierarchy

| Aggression | Command | Data Risk |
| :--- | :--- | :--- |
| Safe | `docker container prune` | None (stopped containers only) |
| Safe | `docker image prune` | None (dangling images only) |
| Safe | `docker volume prune` | Low (unused volumes) |
| Caution | `docker system prune` | Medium (containers + images + networks) |
| **888_HOLD** | `docker system prune -a --volumes` | **High — named volumes destroyed** |

> **F1 Amanah**: Never run `docker system prune -a --volumes` without explicit human confirmation. Named volumes may contain irreplaceable data (Postgres, Qdrant, Vault999).

## Dockerfile Optimization

- **Multi-stage builds** — separate build environment from runtime
- **Layer ordering** — put dependencies before source code
- **Combine RUN commands** — fewer layers, smaller image
- **Use .dockerignore** — exclude `node_modules`, `.git`, `__pycache__`
- **Pin base image versions** — `node:20-alpine`, not `node:latest`
- **Run as non-root** — add `USER` instruction
- **Use slim/alpine bases** — `python:3.12-slim`, not `python:3.12`

## Pitfalls

| Problem | Cause | Fix |
| :--- | :--- | :--- |
| Container exits immediately | Main process finished or crashed | `docker logs NAME`, try `docker run -it --entrypoint /bin/sh IMAGE` |
| "port is already allocated" | Another process using that port | `docker ps` or `lsof -i :PORT` |
| "no space left on device" | Docker disk full | `docker system df`, then targeted prune |
| Can't connect to container | App binds to `127.0.0.1` inside container | App must bind to `0.0.0.0`, check `-p` mapping |
| Permission denied on volume | UID/GID mismatch host vs container | `--user $(id -u):$(id -g)` or fix permissions |
| Compose services can't reach each other | Wrong network or service name | Services use service name as hostname, check `docker compose config` |
| Build cache not working | Layer order wrong in Dockerfile | Put rarely-changing layers first |
| Image too large | No multi-stage build, no .dockerignore | Use multi-stage builds, add `.dockerignore` |

## Federation Context

All federation services run on the `arifos_core_network` Docker network:
- `arifosmcp` (arifOS kernel)
- `geox` (Earth coprocessor)
- `wealth-organ` (Capital engine)
- `well` (Vitality substrate)
- `aaa-a2a` (Control plane gateway)
- `apex-prime` (Constitutional verdict engine)
- `postgres`, `redis`, `nats`, `qdrant`, `vault999`

When debugging federation issues, always start with:
```bash
cd /root/compose
docker compose ps
docker compose logs -f <service>
```

## Related

- [[arifos_forge]] (Execution Bridge)
- [[arifos_vps_monitor]] (Hardware Telemetry)
- [[Concept_Deployment_Architecture]] (VPS vs Horizon Gateway)
- [[MCP_Tools]] (Tool surface architecture)
