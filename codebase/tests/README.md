# arifOS Codebase Tests

**Location:** `codebase/tests/`  
**Purpose:** Tests for the v53 `codebase` architecture

---

## Test Structure

```
codebase/tests/
├── README.md                      # This file
├── __init__.py                    # Python package marker
├── test_micro_loop.py             # Micro-loop integration tests
├── test_infrastructure.py         # Infrastructure/deployment tests
└── test_mcp_server.py             # MCP server and tool tests
```

---

## Running Tests

### All Tests
```bash
python -m pytest codebase/tests/ -v
```

### Specific Test Files
```bash
# Micro-loop tests
python -m pytest codebase/tests/test_micro_loop.py -v

# Infrastructure tests (Railway, Docker, Redis, Cloudflare)
python -m pytest codebase/tests/test_infrastructure.py -v

# MCP server tests
python -m pytest codebase/tests/test_mcp_server.py -v
```

### With Specific Markers
```bash
# Only Railway tests
python -m pytest codebase/tests/test_infrastructure.py -v -m railway

# Only Docker tests
python -m pytest codebase/tests/test_infrastructure.py -v -m docker

# Only Redis tests
python -m pytest codebase/tests/test_infrastructure.py -v -m redis

# Only MCP tests
python -m pytest codebase/tests/test_mcp_server.py -v -m mcp
```

### Skip Slow/External Tests
```bash
# Skip infrastructure tests that require external services
python -m pytest codebase/tests/ -v -m "not railway and not docker"
```

---

## Test Categories

### 1. test_micro_loop.py
Tests the core micro-loop integration:
- End-to-end 000→999 loop
- Injection defense (F12)
- Vault persistence
- Merkle hashing

**Markers:** None (always runs)

### 2. test_infrastructure.py
Tests deployment infrastructure:
- **Railway:** Health checks, MCP endpoints, dashboard
- **Docker:** Container build, run, health
- **Redis:** Connection, SET/GET, session storage
- **Cloudflare:** DNS resolution, SSL certificates
- **Integration:** Full stack health check

**Markers:**
- `railway` - Railway.app deployment tests
- `docker` - Docker container tests  
- `redis` - Redis connection tests
- `dns` - DNS resolution tests
- `ssl` - SSL certificate tests
- `cloudflare` - Cloudflare proxy tests
- `mcp` - MCP endpoint tests
- `integration` - Full integration tests

### 3. test_mcp_server.py
Tests MCP server and 5 Trinity tools:
- `init_000` - Constitutional ignition
- `agi_genius` - AGI Mind Engine
- `asi_act` - ASI Heart Engine
- `apex_judge` - APEX Soul Engine
- `vault_999` - VAULT-999 Memory
- `trinity_loop` - Complete pipeline
- Metrics and dashboard endpoints

**Markers:**
- `mcp` - MCP server tests

---

## Environment Variables

Configure these to point to your infrastructure:

```bash
# Railway/Deployment
export RAILWAY_URL="https://arifos.arif-fazil.com"

# Redis
export REDIS_URL="redis://localhost:6379"
export REDIS_HOST="localhost"
export REDIS_PORT="6379"

# Docker
export DOCKER_IMAGE_NAME="arifos"
export DOCKER_CONTAINER_NAME="arifos-test"

# DNS
export DOMAIN_NAME="arifos.arif-fazil.com"
```

---

## Prerequisites

Install test dependencies:

```bash
pip install pytest pytest-asyncio httpx dnspython redis
```

Or use the project's dev dependencies:

```bash
pip install -e ".[dev]"
```

---

## Test Priorities

### Critical (Run First)
1. `test_micro_loop.py` - Core functionality
2. `test_mcp_server.py::TestMCPHealth` - Server availability

### Important (Run Before Deploy)
1. `test_infrastructure.py::TestRailwayDeployment` - Production health
2. `test_mcp_server.py::TestMCPTrinityLoop` - Full pipeline

### Optional (External Dependencies)
1. `test_infrastructure.py::TestDockerContainer` - Requires Docker
2. `test_infrastructure.py::TestRedisConnection` - Requires Redis
3. `test_infrastructure.py::TestCloudflareDNS` - Requires DNS

---

## Expected Results

### Local Development
```
codebase/tests/test_micro_loop.py::TestMicroLoop::test_end_to_end_loop PASSED
codebase/tests/test_micro_loop.py::TestMicroLoop::test_injection_defense PASSED
```

### Against Production (Railway)
```
codebase/tests/test_infrastructure.py::TestRailwayDeployment::test_railway_health_endpoint PASSED
codebase/tests/test_infrastructure.py::TestRailwayDeployment::test_railway_mcp_endpoint PASSED
codebase/tests/test_mcp_server.py::TestMCPHealth::test_mcp_server_health PASSED
```

---

## Adding New Tests

1. Create a new file: `test_<feature>.py`
2. Import from `codebase.*` (not `arifos.*`)
3. Use pytest markers for categorization
4. Add async support with `@pytest.mark.asyncio`

Example:
```python
import pytest
from codebase.my_module import MyClass

class TestMyFeature:
    def test_something(self):
        obj = MyClass()
        result = obj.do_something()
        assert result == expected
```

---

## Troubleshooting

### Import Errors
Make sure you're in the project root and have installed:
```bash
cd C:\Users\User\arifOS
pip install -e .
```

### Railway Tests Failing
- Check `RAILWAY_URL` environment variable
- Verify domain is accessible: `curl https://arifos.arif-fazil.com/health`
- Check Cloudflare proxy status (should be DNS-only for Railway)

### Docker Tests Failing
- Ensure Docker is running: `docker --version`
- Check disk space for image builds
- Try building manually: `docker build -t arifos:test .`

### Redis Tests Failing
- Start Redis locally: `redis-server`
- Or set `REDIS_URL` to your Redis instance
- Check connection: `redis-cli ping`

---

## CI/CD Integration

For GitHub Actions or similar:

```yaml
- name: Run Codebase Tests
  run: |
    python -m pytest codebase/tests/test_micro_loop.py -v
    
- name: Run Infrastructure Tests
  run: |
    python -m pytest codebase/tests/test_infrastructure.py -v -m railway
  env:
    RAILWAY_URL: https://arifos.arif-fazil.com
```

---

*DITEMPA BUKAN DIBERI*
