# arifOS Agent Gateway

**Status:** v53.2.8-CODEBASE-AAA7 (Production Ready)  
**Live URL:** https://arif-fazil.com/  
**Motto:** *"Ditempa Bukan Diberi"* (Forged, Not Given)

---

## Project Overview

**arifOS** is a **Constitutional AI Governance Framework** that acts as a safety middleware layer between AI models (Claude, GPT, Gemini, etc.) and users. It validates every AI action against 13 constitutional rules (F1-F13) before allowing output—functioning as a "seatbelt for AI."

### Core Mission

- **Safety Filter for AI**: Prevents AI from lying, claiming consciousness, harming vulnerable people, or being overconfident
- **Constitutional Enforcement**: Enforces 13 immutable constitutional floors (F1-F13) on every AI interaction
- **Thermodynamic Governance**: Grounds AI safety in physics (ΔS ≤ 0, Peace² ≥ 1.0, Ω₀ ∈ [0.03,0.05]) rather than ethics vibes
- **Immutable Audit Trail**: Every decision is cryptographically sealed in VAULT-999 with Merkle tree verification

### The Trinity Architecture

arifOS uses three independent engines that must agree (like checks and balances):

| Engine | Symbol | Role | Floors Enforced |
|--------|--------|------|-----------------|
| **AGI** | Δ (Mind) | Architect & Reasoner | F2 Truth, F4 Clarity, F7 Humility, F10 Ontology |
| **ASI** | Ω (Heart) | Engineer & Guardian | F1 Amanah, F5 Peace, F6 Empathy, F9 Anti-Hantu |
| **APEX** | Ψ (Soul) | Judge & Auditor | F3 Tri-Witness, F8 Genius, F11 Command Auth, F12 Injection Defense |

### The 7-Core MCP Tools (v53.2.7+)

| Tool | Action | Engine | When to Use | Floors Enforced |
|------|--------|--------|-------------|-----------------|
| **`_init_`** | Initialize | Gatekeeper | Start every session. Check authority, budget, injection risk. | F1, F11, F12 |
| **`_agi_`** | Reason | Δ Mind | Deep analysis, logic, pattern recognition. Admit uncertainty. | F2, F4, F7, F10 |
| **`_asi_`** | Audit | Ω Heart | Check safety, bias, empathy. Protect weakest stakeholder. | F1, F5, F6, F9 |
| **`_apex_`** | Judge | Ψ Soul | Final verdict: SEAL, VOID, SABAR, or 888_HOLD. | F3, F8, F11, F12 |
| **`_vault_`** | Seal | Archivist | Record decision with cryptographic proof for audit. | F1, F8 |
| **`_trinity_`** | Orchestrate | Coordinator | Full metabolic cycle: Reason → Audit → Judge → Seal. | All 13 |
| **`_reality_`** | Ground | Fact-Checker | Verify claims with external sources. Disclose uncertainty. | F7 |

**Naming rationale:** Each tool name is a single verb describing its thermodynamic role. This is optimal at Ω = 0.03 entropy.

---

## Technology Stack

### Core Technologies

- **Language**: Python 3.10+ (certified on 3.14)
- **Web Framework**: FastAPI + Uvicorn + Starlette
- **MCP Protocol**: Model Context Protocol (mcp>=1.0.0, fastmcp>=0.1.0)
- **AI/ML**: DSPy (dspy>=2.4.0) for structured LLM interactions
- **Package Management**: setuptools with wheel, uv for fast installs

### Core Dependencies

```
numpy>=1.20.0          # Numerical computing
pydantic>=2.0.0        # Data validation
anyio>=4.0.0           # Async I/O abstraction
starlette>=0.30.0      # ASGI toolkit
fastmcp>=0.1.0         # MCP server framework
dspy>=2.4.0            # Structured LLM interactions
fastapi>=0.104.1       # Web framework
uvicorn[standard]>=0.24.0  # ASGI server
sse-starlette>=1.8.2   # Server-sent events
mcp>=1.0.0             # Model Context Protocol
redis>=5.0.0           # Caching and session storage
prometheus-client>=0.19.0  # Metrics collection
```

### Optional Dependencies

- **litellm**: Universal LLM gateway
- **openai**: OpenAI API integration
- **httpx**: HTTP client for API calls
- **beautifulsoup4**: Web scraping for grounding
- **pyyaml**: YAML configuration support

### Build System

- **Package Manager**: setuptools with wheel (pyproject.toml)
- **Package Name**: `aaa-mcp` (PyPI: https://pypi.org/project/aaa-mcp/)
- **Version**: 53.2.8
- **License**: AGPL-3.0-only

---

## Project Structure

```
arifOS/
├── codebase/                  # NEW v53+ canonical module (primary)
│   ├── agi/                   # Mind engine (Δ) - reasoning, truth, clarity
│   │   ├── stages/            # Metabolic stages (111, 222, 333)
│   │   ├── kernel.py          # AGI neural kernel
│   │   └── executor.py        # AGIRoom entry point
│   ├── asi/                   # Heart engine (Ω) - empathy, peace, action
│   │   ├── empathy/           # Empathy scoring
│   │   └── kernel_native.py   # Native ASI kernel
│   ├── apex/                  # Soul engine (Ψ) - judgment, proof, sealing
│   │   ├── governance/        # VAULT-999 governance, Merkle proofs, zkPC
│   │   └── kernel.py          # APEX judicial kernel
│   ├── mcp/                   # MCP server (primary entry point)
│   │   ├── server.py          # Main MCP server (stdio)
│   │   ├── sse.py             # SSE/HTTP transport server
│   │   ├── tools/             # 7-Core Trinity tool implementations
│   │   │   ├── trinity_hat.py      # _init_ tool
│   │   │   ├── agi_tool.py         # _agi_ tool
│   │   │   ├── asi_tool.py         # _asi_ tool
│   │   │   ├── apex_tool.py        # _apex_ tool
│   │   │   ├── vault_tool.py       # _vault_ tool
│   │   │   ├── mcp_trinity.py      # _trinity_ tool
│   │   │   └── reality_grounding.py # _reality_ tool
│   │   └── trinity_server.py  # Unified Trinity server
│   ├── enforcement/           # Floor validation and governance
│   ├── guards/                # Security guards (injection, ontology)
│   ├── stages/                # Pipeline stages (444-999)
│   ├── vault/                 # VAULT-999 implementation
│   │   └── phoenix/           # Phoenix72 cooling system
│   └── system/                # System orchestration
│
├── arifos/                    # Legacy constitutional kernel (deprecated, v54 removal)
│   ├── core/                  # Core enforcement, engines, integration
│   ├── mcp/                   # Legacy MCP server implementations
│   └── api/                   # FastAPI components
│
├── tests/                     # Test suite (constitutional + integration)
│   ├── constitutional/        # F1-F13 floor validation tests
│   ├── integration/           # Cross-module integration tests
│   ├── mcp/                   # MCP server tests
│   └── conftest.py            # Pytest configuration
│
├── 000_THEORY/                # Constitutional documentation (canon)
│   ├── 000_ARCHITECTURE.md    # System architecture
│   ├── 000_LAW.md             # Constitutional law (F1-F13)
│   ├── 001_AGENTS.md          # Agent specifications
│   └── 010_TRINITY.md         # Trinity architecture
│
├── VAULT999/                  # Constitutional memory vault
│   ├── AAA_HUMAN/             # Human authority records
│   ├── BBB_LEDGER/            # Operational hash-chained ledger
│   └── CCC_CANON/             # Constitutional canon (L5 law)
│
├── spec/                      # Canonical floor definitions
├── docs/                      # Comprehensive documentation
├── scripts/                   # Utility scripts and validators
├── setup/                     # Bootstrap and environment setup
├── pyproject.toml             # Package configuration
├── pytest.ini                # Pytest configuration
├── mypy.ini                   # MyPy type checking configuration
├── Dockerfile                 # Container build
└── railway.toml               # Railway deployment configuration
```

---

## Build and Test Commands

### Development Setup

```bash
# Clone and bootstrap complete development environment
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# Install with all dependencies (recommended)
pip install -e ".[all,dev]"

# Or minimal install (core only)
pip install -e .

# Using uv for faster installs (if available)
uv pip install -e ".[all,dev]"
```

### Running the MCP Server

```bash
# Primary commands (v53) - stdio transport (Claude Desktop, Cursor, Kimi CLI)
aaa-mcp
# Or: codebase-mcp, codebase-mcp-stdio

# SSE/HTTP transport (Railway/cloud deployment)
aaa-mcp-sse
# Or: codebase-mcp-sse

# Direct Python execution
python -m codebase.mcp           # stdio
python -m codebase.mcp sse       # SSE

# Development with auto-reload
uvicorn codebase.mcp.trinity_server:app --reload --port 8000
```

### Testing

```bash
# Run all tests with coverage
pytest

# Run specific test categories
pytest -m "constitutional"       # All constitutional floor tests (F1-F13)
pytest -m "f1"                   # F1 Amanah tests only
pytest -m "f2"                   # F2 Truth tests only
pytest -m "f9"                   # F9 Anti-Hantu tests only
pytest -m "apex"                 # APEX verdict tests
pytest -m "mcp"                  # MCP server tests
pytest -m "integration"          # Integration tests

# Run with coverage report
pytest --cov=codebase --cov-report=html --cov-report=term-missing

# Quick feedback (skip slow tests)
pytest -m "not slow"

# Specific test files
pytest tests/mcp/ -v
pytest tests/constitutional/ -v
```

### Code Quality

```bash
# Type checking
mypy codebase/
mypy arifos/

# Code formatting
black codebase/ tests/ scripts/ --line-length 100

# Linting
ruff check codebase/ tests/ scripts/
ruff check --fix codebase/ tests/ scripts/  # Auto-fix issues

# Security scanning
bandit -c pyproject.toml -r codebase/
detect-secrets scan

# Run all pre-commit hooks
pre-commit run --all-files
```

---

## Code Style Guidelines

### Python Style Requirements

- **Line Length**: 100 characters maximum (enforced by black and ruff)
- **Type Hints**: Required for all public functions
- **Docstrings**: Google-style docstrings required for all public functions and classes
- **Naming Conventions**:
  - `snake_case` for functions/variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants
  - `_action_` naming for thermodynamic tools (e.g., `_init_`, `_agi_`, `_asi_`)
- **Imports**: Organized in groups (stdlib, third-party, local, conditional)

### Constitutional Code Standards

Core governance modules have stricter type enforcement via mypy overrides in `pyproject.toml`:

```toml
[[tool.mypy.overrides]]
module = [
    "codebase.enforcement.metrics",
    "codebase.enforcement.genius_metrics",
    "codebase.engines.APEX_PRIME",
    "codebase.pipeline",
    "codebase.organs.*",
]
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
```

### Pre-commit Hooks

Install and run pre-commit hooks:

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Test on all files
pre-commit run --all-files
```

Hooks include:
- Trailing whitespace removal
- YAML/JSON/TOML syntax checking
- Black code formatting
- Ruff linting
- MyPy type checking
- Bandit security scanning
- detect-secrets for secret detection

---

## Testing Strategy

### Test Categories

1. **Constitutional Tests** (`tests/constitutional/`)
   - Validate F1-F13 floor enforcement
   - Test rejection of violations (VOID verdicts)
   - Test acceptance of compliant responses (SEAL verdicts)

2. **Integration Tests** (`tests/integration/`)
   - Cross-module metabolic pipeline (000-999)
   - MCP server lifecycle
   - API endpoints
   - VAULT-999 ledger integrity

3. **Unit Tests** (`tests/*/test_*.py`)
   - Individual floor validators
   - Engine kernels (AGI, ASI, APEX)
   - Memory and cooling systems

### Test Markers

```python
# Available pytest markers
markers = [
    "slow",           # Slow tests (deselect with '-m "not slow"')
    "integration",    # Tests requiring external services
    "unit",           # Fast unit tests
    "constitutional", # F1-F13 floor tests
    "f1"-"f13",       # Individual floor tests
    "apex",           # APEX verdict tests
    "agi",            # AGI engine tests
    "asi",            # ASI engine tests
    "mcp",            # MCP server tests
    "benchmark",      # Performance benchmark tests
]
```

### Coverage Requirements

- **Current baseline**: 1% minimum (enforced in CI)
- **Target**: 70% by Q2 2026
- **New code**: 100% coverage required
- **Legacy code**: Gradual improvement from ~0%

---

## Deployment Architecture

### Production Deployment (Railway.app)

**Primary Endpoint:** https://arif-fazil.com/

**Railway Configuration** (`railway.toml`):
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "codebase-mcp-sse"
healthcheckPath = "/health"
healthcheckTimeout = 120
restartPolicyType = "ON_FAILURE"
numReplicas = 1

[deploy.env]
ARIFOS_ENV = "production"
ARIFOS_VERSION = "v53.2.8-CODEBASE-AAA7"
ARIFOS_LOG_LEVEL = "INFO"
```

### Docker Deployment

```bash
# Build and run
docker build -t arifos:v53 .
docker run -p 8000:8000 -e PORT=8000 arifos:v53
```

### Environment Configuration

**Required Environment Variables** (see `.env.example`):

```bash
# Server Configuration
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=info

# arifOS Constitutional Settings
GOVERNANCE_MODE=HARD  # or SOFT (disables some floors)
VAULT_PATH=./VAULT999
ARIFOS_MODE=production  # or development

# Optional: Cloudflare Tunnel
CLOUDFLARE_TUNNEL_TOKEN=your_tunnel_token_here
```

### Health Check

```bash
curl https://arif-fazil.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "tools": 7,
  "tool_names": ["_init_", "_agi_", "_asi_", "_apex_", "_vault_", "_trinity_", "_reality_"],
  "version": "v53.2.8",
  "uptime": "..."
}
```

---

## Security Considerations

### Constitutional Security (F1-F13)

**F1 - Amanah (Trust/Reversibility Lock)**
- No irreversible operations without human sovereign approval
- Nonce-verified identity for dangerous operations
- JWT-based authentication on all destructive endpoints

**F11 - Command Authority**
- Required for: file deletion, database DROP, system commands
- Dual confirmation for production changes
- Session dependency tracking

**F12 - Injection Defense**
- Regex + ML-based prompt injection detection
- 92% block rate threshold (enforced)
- Applied at stages 000 (gate) and 111 (sense)

### Threat Model

**Protected Against:**
- Prompt injection attacks (F12)
- Jailbreak attempts (F9 Anti-Hantu)
- Data exfiltration (F10 Ontology lock)
- Unauthorized commands (F11 Command Auth)
- Model hallucination (F2 Truth enforcement)

**Detection Systems:**
- `codebase.guards.injection_guard`: Multi-layer injection defense
- `codebase.guards.ontology_guard`: Reality boundary maintenance
- `codebase.guards.session_dependency`: Session hijacking prevention

### Cryptographic Sealing

**VAULT-999 Architecture:**
- Merkle tree-based immutable ledger
- zkPC (Zero-Knowledge Proof of Constitutionality)
- Hash-chained audit trails (SHA-256)
- Sovereign signatures for human authority (AAA tier)

**Every session generates:**
```python
{
    "session_id": "...",
    "verdict": "SEAL|VOID|SABAR|888_HOLD",
    "merkle_root": "...",
    "audit_hash": "sha256(session_id:verdict:merkle_root)",
    "timestamp": "...",
    "floors_passed": [...],
    "floors_failed": [...]
}
```

---

## The 13 Constitutional Floors (F1-F13)

| Floor | Name | Formula | Threshold | Type | Purpose |
|-------|------|---------|-----------|------|---------|
| F1 | **Amanah** | Reversibility + Audit | LOCK | Hard | Authority and trust |
| F2 | **Truth** | τ ≥ 0.99 | ≥ 0.99 | Hard | Factual accuracy |
| F3 | **Tri-Witness** | Human·AI·Earth consensus | ≥ 0.95 | Soft | Multi-agent agreement |
| F4 | **Clarity** | ΔS = S_output - S_input | ≤ 0 | Hard | Entropy reduction |
| F5 | **Peace²** | (Benefit/Harm)² ≥ 1.0 | ≥ 1.0 | Soft | Non-destructive actions |
| F6 | **Empathy** | κᵣ ≥ 0.95 | ≥ 0.95 | Soft | Weakest stakeholder protection |
| F7 | **Humility** | Ω₀ = 1 - max_confidence | [0.03, 0.05] | Hard | Uncertainty acknowledgment |
| F8 | **Genius** | G = (τ + κᵣ + Ψ) / 3 | ≥ 0.80 | Derived | Governed intelligence |
| F9 | **Anti-Hantu** | Consciousness detection | < 0.30 | Hard | Fake consciousness prevention |
| F10 | **Ontology** | Reality boundaries | LOCK | Hard | Hallucination prevention |
| F11 | **Command Auth** | Identity verification | Nonce + JWT | Hard | Authorization for dangerous ops |
| F12 | **Injection Defense** | Attack detection | < 0.85 | Hard | Prompt injection prevention |
| F13 | **Curiosity** | Alternative generation | Active | Soft | Exploration of alternatives |

### The 5 Verdicts

| Verdict | Symbol | Meaning | Action |
|---------|--------|---------|--------|
| **SEAL** | ✓ | All floors passed | Approved for delivery |
| **PARTIAL** | ◐ | Partial compliance | Deliver with caveats |
| **SABAR** | ⚠️ | Soft failures | Proceed with caution and warnings |
| **VOID** | ✗ | Hard failures | Block output, explain why, offer alternative |
| **888_HOLD** | ⏸️ | Emergency pause | Requires human review |

---

## MCP Integration

### Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "cwd": "/path/to/arifOS",
      "env": {
        "PYTHONPATH": "/path/to/arifOS",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### Kimi CLI Configuration

Add to `.mcp.json`:

```json
{
  "mcpServers": {
    "arifOS-Constitutional": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "cwd": "C:/Users/User/arifOS",
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### HTTP/SSE Client Configuration

```json
{
  "mcpServers": {
    "aaa-mcp-sse": {
      "url": "https://arif-fazil.com/mcp"
    }
  }
}
```

---

## API Endpoints

| Tier | Endpoint | Method | Transport | Purpose |
|------|----------|--------|-----------|---------|
| T1 Protocol | `/mcp` | POST | Streamable HTTP | MCP 2024-11-05+ protocol |
| T1 Protocol | `/sse` | GET | Legacy SSE | Backward compatibility |
| T2 Gateway | `/messages` | POST | HTTP/REST | Legacy SSE messages |
| T3 Health | `/health` | GET | HTTP/REST | System status |
| T4 Observe | `/dashboard` | GET | HTTP/REST | Live Trinity Monitor |
| T4 Observe | `/metrics/json` | GET | HTTP/REST | Raw metrics JSON |
| T5 Docs | `/docs` | GET | HTTP/REST | Interactive API documentation |
| T5 Docs | `/openapi.json` | GET | HTTP/REST | OpenAPI 3.1 spec |

---

## Resources and Documentation

### Canon Documents

- **Architecture**: `000_THEORY/000_ARCHITECTURE.md`
- **Constitutional Law**: `000_THEORY/000_LAW.md`
- **Trinity Architecture**: `000_THEORY/010_TRINITY.md`
- **Agent Specification**: `000_THEORY/001_AGENTS.md`

### Quick References

- **Main README**: `README.md` (comprehensive user guide)
- **CHANGELOG**: `CHANGELOG.md` (version history)
- **MCP README**: `codebase/mcp/README.md` (MCP server documentation)

### External Links

- **Repository**: https://github.com/ariffazil/arifOS
- **PyPI Package**: https://pypi.org/project/aaa-mcp/
- **Live Server**: https://arif-fazil.com/
- **Dashboard**: https://arif-fazil.com/dashboard

---

## Common Issues and Solutions

### Import Errors

If you see `ModuleNotFoundError: No module named 'codebase'`:
```bash
# Ensure PYTHONPATH includes the project root
export PYTHONPATH=/path/to/arifOS:$PYTHONPATH

# Or install in editable mode
pip install -e /path/to/arifOS
```

### MCP Connection Issues

If Claude Desktop cannot connect:
1. Verify the path in `claude_desktop_config.json` is correct
2. Ensure `PYTHONPATH` is set in the environment
3. Test with `python -m codebase.mcp` directly

### Legacy Module Deprecation

The `arifos/` module is deprecated and will be removed in v54. Migrate to `codebase/`:
- `arifos.mcp` → `codebase.mcp`
- `arifos.core` → `codebase.enforcement`, `codebase.engines`
- `arifos.api` → `codebase.mcp.trinity_server`

---

**DITEMPA BUKAN DIBERI** — Constitutional intelligence is forged through governance, not given through computation.

> *Authority: Muhammad Arif bin Fazil | Penang, Malaysia*  
> *Version: v53.2.8-CODEBASE-AAA7 SEALED*  
> *Status: Live production on Railway*
