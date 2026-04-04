# arifOS VPS Architecture Snapshot (Redacted)

Generated: 2026-03-21
Scope: High-level architecture, service layout, and data paths. Secrets are omitted.

## Purpose
This snapshot documents the VPS architecture and configuration layout for auditability and recovery.
It intentionally excludes raw credentials, tokens, and private keys.

## Host
- OS: Ubuntu 25.10
- Role: AI agent platform (OpenClaw + arifosmcp stack)

## Core services (Docker)
Source of truth: `/srv/arifosmcp/docker-compose.yml`

Key services:
- `openclaw_gateway` (OpenClaw gateway)
- `arifosmcp_server` (arifOS MCP server)
- `agent_zero_reasoner`
- `ollama_engine`
- `qdrant_memory`
- `arifos_postgres`
- `arifos_redis`
- `traefik_router`
- `headless_browser`
- `arifos_grafana`
- `arifos_prometheus`
- `arifos_n8n`
- `arifos_webhook`

## Network
- Docker network: `arifos_trinity`
- External network: `arifosmcp_arifos_trinity`

## Data paths (host)
- OpenClaw state: `/opt/arifos/data/openclaw/`
  - Active config: `/opt/arifos/data/openclaw/openclaw.json`
  - Workspace: `/opt/arifos/data/openclaw/workspace/`
  - Logs: `/opt/arifos/data/openclaw/logs/`
  - Models/tools/bin: `/opt/arifos/data/openclaw/bin/`
- arifOS codebase: `/srv/arifosmcp/`
- arifOS data: `/opt/arifos/data/core/`
- Postgres data: `/opt/arifos/data/postgres/`
- Redis data: `/opt/arifos/data/redis/`
- Qdrant data: `/opt/arifos/data/qdrant/`
- Ollama models: `/opt/arifos/data/ollama/`
- Grafana data: `/opt/arifos/data/grafana/`
- Prometheus data: `/opt/arifos/data/prometheus/`

## Access and routing (redacted)
- Public HTTP/HTTPS via Traefik
- Service ports are defined in `/srv/arifosmcp/docker-compose.yml`
- Internal service URLs (container network):
  - arifosmcp: `http://arifosmcp:8080`
  - agent_zero: `http://agent_zero_reasoner:80`
  - qdrant: `http://qdrant_memory:6333`

## Backup
- Workspace repo: `git@github.com:ariffazil/openclaw-workspace.git`
- Backup script: `/opt/arifos/data/openclaw/workspace/scripts/backup-to-github.sh`
- Scheduled by OpenClaw cron: `midnight-workspace-backup`

## Security posture (redacted)
- OpenClaw Control UI: disabled
- Sandbox: off (full exec capability enabled)
- Config permissions: `openclaw.json` and `openclaw.json.secure` set to 600

## Notes
- This file should be updated whenever services, ports, or data paths change.
- Do not store credentials in this file.
