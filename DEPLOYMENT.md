# Deployment — arifOS Kernel

## Prerequisites

- Docker 24+ and Docker Compose v2
- 2 CPU cores, 4GB RAM minimum
- Linux host (Ubuntu 22.04+ recommended)
- Ports: `8088` (kernel MCP), `8088/webmcp` (local console)

## Quick Start

```bash
# Clone and deploy
git clone https://github.com/arif-fazil/arifOS.git
cd arifOS
docker compose up -d

# Verify
curl http://localhost:8088/health
```

## Federation Deployment

The arifOS kernel is the central governance organ. It must be deployed before
any execution organs (A-FORGE) or domain organs (GEOX, WEALTH, WELL).

### Docker Compose (Single Node)

```yaml
services:
  arifos-kernel:
    image: arifazil/arifos-kernel:latest
    ports:
      - "8088:8088"
    volumes:
      - vault999:/var/lib/vault999
      - ./config:/etc/arifos:ro
    environment:
      - ARIFOS_FLOOR_COUNT=13
      - ARIFOS_VAULT_PATH=/var/lib/vault999
    restart: unless-stopped

volumes:
  vault999:
```

### Multi-Node Federation

See the [Federation Architecture](docs/ARCHITECTURE_FEDERATION.md) guide for
deploying across multiple nodes with Tailscale mesh networking.

## Configuration

All configuration is passed via environment variables or `/etc/arifos/config.yaml`.
Secrets must be mounted as volumes — never baked into images.

## Health Checks

| Endpoint | Description | No Auth |
|----------|-------------|---------|
| `GET /health` | Kernel liveness | ✅ |
| `GET /health/tools` | MCP tool availability | ✅ |
| `GET /health/floors` | Constitutional floor status | ✅ |
| `GET /webmcp` | Web MCP console | ✅ (localhost) |

## Upgrading

```bash
git pull origin main
docker compose pull
docker compose up -d --force-recreate
```

The kernel is stateless except for VAULT999. The vault volume must be preserved
across upgrades.

## Troubleshooting

```bash
# View kernel logs
docker compose logs arifos-kernel --tail=100

# Check VAULT999 integrity
curl http://localhost:8088/health/vault

# Verify constitutional floors
curl http://localhost:8088/health/floors
```
