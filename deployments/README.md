# arifOS Deployment Guide

> **Version**: 2026.04.11  
> **Authority**: 000_THEORY, 888_APEX  
> **DITEMPA BUKAN DIBERI**

## Quick Start

```bash
# Test locally with MCP Inspector
python arifosmcp/evals/mcp_inspector_test.py --all

# Run full deployment gate tests
python arifosmcp/evals/deploy_gate.py

# Deploy to VPS
./deployments/deploy.sh vps

# Deploy to Horizon
./deployments/deploy.sh horizon

# Test only (no deployment)
./deployments/deploy.sh test
```

## MCP Inspector Testing

### Using the Test Harness

```bash
# Test all substrates
python arifosmcp/evals/mcp_inspector_test.py --all

# Test specific substrate
python arifosmcp/evals/mcp_inspector_test.py --substrate fetch

# Output for MCP Inspector CLI
python arifosmcp/evals/mcp_inspector_test.py --all --inspector
```

### Using Official MCP Inspector

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Test arifOS main server
npx @modelcontextprotocol/inspector python -m arifosmcp.runtime.server

# Test with stdio transport
npx @modelcontextprotocol/inspector python arifosmcp/evals/mcp_inspector_test.py --stdio
```

## Deployment Configurations

### VPS Production (`vps-deploy.yml`)

- **Target**: Hostinger VPS (Ubuntu 22.04)
- **Resources**: 2 CPU, 2GB RAM limits
- **Monitoring**: Prometheus + Grafana (optional)
- **SSL**: Traefik + Let's Encrypt

```bash
# Deploy to VPS
docker-compose -f docker-compose.yml -f deployments/vps-deploy.yml up -d

# With monitoring
docker-compose -f docker-compose.yml -f deployments/vps-deploy.yml --profile monitoring up -d
```

### Horizon Edge (`horizon-deploy.yml`)

- **Target**: Secondary/Edge server
- **Resources**: 1 CPU, 1GB RAM limits
- **Sync**: Automatic sync with parent VPS
- **Mode**: Lightweight, read-optimized

```bash
# Deploy to Horizon
docker-compose -f docker-compose.yml -f deployments/horizon-deploy.yml up -d

# With sync agent
docker-compose -f docker-compose.yml -f deployments/horizon-deploy.yml --profile sync up -d
```

## MCP Substrate Services

All 6 MCP substrates are configured in `docker-compose.yml`:

| Service | Port | Purpose | Constitutional Floor |
|---------|------|---------|---------------------|
| `mcp_time` | 8000 | Time/zone operations | F3 Alignment |
| `mcp_filesystem` | 8000 | File read/write | F1 Amanah, F8 Domain |
| `mcp_git` | 8000 | Repository operations | F2 Integrity, F13 Trace |
| `mcp_memory` | 8000 | Knowledge graph | F3 Truth |
| `mcp_fetch` | 8000 | URL fetching | F9 Reality Grounding |
| `mcp_everything` | 8000 | Protocol conformance | Testing only |

## Environment Variables

```bash
# Enable/disable substrates
MCP_SUBSTRATES_ENABLED=true

# Custom substrate URLs (for external hosting)
MCP_TIME_URL=http://mcp_time:8000
MCP_FILESYSTEM_URL=http://mcp_filesystem:8000
MCP_GIT_URL=http://mcp_git:8000
MCP_MEMORY_URL=http://mcp_memory:8000
MCP_FETCH_URL=http://mcp_fetch:8000
MCP_EVERYTHING_URL=http://mcp_everything:8000

# Timeout configuration
MCP_SUBSTRATE_TIMEOUT=30.0

# Deployment mode
VPS_MODE=1
HORIZON_MODE=1
ARIFOS_DEPLOYMENT=vps|horizon|dev
```

## Testing Matrix

| Test Type | Command | Purpose |
|-----------|---------|---------|
| Unit | `pytest tests/` | Code unit tests |
| MCP Inspector | `python arifosmcp/evals/mcp_inspector_test.py --all` | Protocol conformance |
| Breach | `python -m arifosmcp.evals.breach_test_runner` | Constitutional floors |
| Smoke | `python arifosmcp/evals/substrate_smoke_runner.py` | Substrate health |
| E2E | `python arifosmcp/evals/e2e_golden_paths.py` | End-to-end scenarios |
| Deploy Gate | `python arifosmcp/evals/deploy_gate.py` | Gates A-H |

## Troubleshooting

### Substrate Health Check

```python
from arifosmcp.integrations.substrate_bridge import bridge
import asyncio

async def check():
    health = await bridge.get_global_health()
    print(json.dumps(health, indent=2))

asyncio.run(check())
```

### Common Issues

1. **Substrate shows "DOWN"**
   - Check Docker container: `docker-compose ps mcp_fetch`
   - Check logs: `docker-compose logs mcp_fetch`
   - Verify network: `docker network inspect arifos_core_network`

2. **MCP Inspector connection refused**
   - Ensure substrates are running: `docker-compose up -d mcp_time mcp_fetch ...`
   - Check firewall rules
   - Verify URLs in substrate_bridge.py

3. **Tool execution fails**
   - Check tool name matches substrate's available tools
   - Verify arguments format
   - Review substrate logs for errors

## Deployment Checklist

- [ ] MCP Inspector tests pass
- [ ] Deployment gates A-H pass
- [ ] Docker images built and tagged
- [ ] Environment variables configured
- [ ] SSL certificates ready (Let's Encrypt)
- [ ] Rollback point created
- [ ] Monitoring enabled (optional)
- [ ] Human ratification (production)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      arifOS Trinity                          │
│                   (MIND / JUDGE / VAULT)                     │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
    ┌──────────▼──────────┐      ┌───────────▼────────────┐
    │  Substrate Bridge   │      │   Constitutional       │
    │  (HTTP/SSE clients) │      │   Enforcement (F1-F13) │
    └──────────┬──────────┘      └────────────────────────┘
               │
    ┌──────────┼──────────┬──────────┬──────────┬──────────┐
    ▼          ▼          ▼          ▼          ▼          ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│ time  │ │filesystem│ │  git  │ │memory │ │ fetch │ │everything│
└───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘
   8000      8000      8000      8000      8000      8000
```

## Support

- **Issues**: Check `arifosmcp/VAULT999` for logs
- **Wiki**: See `wiki/pages/MCP_Tools.md`
- **Constitution**: See `000/CONSTITUTION.md`

---

**999_SEAL_ALIVE**  
**DITEMPA BUKAN DIBERI**
