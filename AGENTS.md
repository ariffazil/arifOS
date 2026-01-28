# arifOS Agent Gateway

**Canon:** `000_THEORY/001_AGENTS.md`  
**Motto:** *"Ditempa Bukan Diberi"* (Forged, Not Given)  
**Status:** v53.2.1-CODEBASE (Production Ready)  
**Live URL:** https://arifos.arif-fazil.com/

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
| **AGI** | Δ (Mind) | Architect & Reasoner | F2 Truth, F4 Clarity, F7 Humility |
| **ASI** | Ω (Heart) | Engineer & Guardian | F1 Amanah, F5 Peace, F6 Empathy |
| **APEX** | Ψ (Soul) | Judge & Auditor | F3 Consensus, F8 Quality, F9 Anti-Deception |

### The 5 MCP Tools

| Tool | Role | Trinity Engine | Constitutional Floors |
|------|------|----------------|----------------------|
| `init_000` | 🚪 Gate | 000_INIT | F1, F11, F12 |
| `agi_genius` | 🧠 Mind | AGI | F2, F4, F7, F13 |
| `asi_act` | ❤️ Heart | ASI | F1, F5, F6 |
| `apex_judge` | ⚖️ Soul | APEX | F3, F8, F9, F10 |
| `vault_999` | 🔒 Seal | 999_Vault | F1, F8, F10 |

---

## Technology Stack

### Core Technologies

- **Language**: Python 3.10+ (certified on 3.14)
- **Web Framework**: FastAPI + Uvicorn + Starlette
- **MCP Protocol**: Model Context Protocol (mcp>=1.0.0, fastmcp>=0.1.0)
- **AI/ML**: DSPy (dspy>=2.4.0) for structured LLM interactions

### Core Dependencies

```
numpy>=1.20.0          # Numerical computing
pydantic>=2.0.0        # Data validation
anyio>=4.0.0           # Async I/O abstraction
sse-starlette>=1.8.2   # Server-sent events
redis>=5.0.0           # Caching and session storage
prometheus-client      # Metrics collection
```

### Optional Dependencies

- **litellm**: Universal LLM gateway
- **openai**: OpenAI API integration
- **httpx**: HTTP client for API calls
- **python-multipart**: Form data parsing

### Build System

- **Package Manager**: setuptools with wheel (pyproject.toml)
- **Package Name**: `aaa-mcp` (PyPI)
- **Entry Points**: See `[project.scripts]` in pyproject.toml

---

## Project Structure

```
arifOS/
├── arifos/                    # Legacy constitutional kernel (being migrated)
│   ├── core/                  # Core enforcement, engines, integration
│   ├── mcp/                   # MCP server implementations
│   ├── api/                   # FastAPI components
│   └── protocol/              # Protocol handlers
│
├── codebase/                  # NEW v53 canonical module (primary)
│   ├── agi/                   # Mind engine (Δ) - reasoning, truth, clarity
│   │   ├── stages/            # Metabolic stages (111, 222, 333)
│   │   ├── kernel.py          # AGI neural kernel
│   │   └── executor.py        # AGIRoom entry point
│   ├── asi/                   # Heart engine (Ω) - empathy, peace, action
│   │   ├── empathy/           # Empathy scoring
│   │   └── kernel_native.py   # Native ASI kernel
│   ├── apex/                  # Soul engine (Ψ) - judgment, proof, sealing
│   │   ├── governance/        # VAULT-999 governance
│   │   └── kernel.py          # APEX judicial kernel
│   ├── mcp/                   # MCP server (primary entry point)
│   │   ├── server.py          # Main MCP server (stdio)
│   │   ├── sse.py             # SSE transport server
│   │   ├── tools/             # 5 Trinity tool implementations
│   │   └── trinity_server.py  # Unified Trinity server
│   ├── enforcement/           # Floor validation and governance
│   ├── guards/                # Security guards (injection, ontology)
│   ├── stages/                # Pipeline stages (444-999)
│   ├── system/                # System orchestration
│   └── vault/                 # VAULT-999 implementation
│
├── tests/                     # Test suite (constitutional + integration)
│   ├── constitutional/        # F1-F13 floor validation tests
│   ├── integration/           # Cross-module integration tests
│   ├── core/                  # Core engine tests
│   └── test_*.py              # Individual test files
│
├── 000_THEORY/                # Constitutional documentation (canon)
│   ├── 000_ARCHITECTURE.md    # System architecture
│   ├── 000_LAW.md             # Constitutional law (F1-F13)
│   └── 001_AGENTS.md          # Agent specifications
│
├── VAULT999/                  # Constitutional memory vault
│   ├── AAA_HUMAN/             # Human authority records
│   ├── BBB_LEDGER/            # Operational hash-chained ledger
│   └── CCC_CANON/             # Constitutional canon (L5 law)
│
├── docs/                      # Comprehensive documentation
├── scripts/                   # Utility scripts and validators
└── setup/                     # Bootstrap and environment setup
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

# For Railway deployment (production)
pip install -r requirements.txt
pip install -e .
```

### Running the MCP Server

```bash
# Primary commands (v53)
aaa-mcp              # stdio transport (Claude Desktop local)
aaa-mcp-sse          # SSE transport (Railway/cloud)
aaa-mcp-stdio        # stdio alternative

# Legacy commands (deprecated, will be removed in v54)
arifos-mcp           # Equivalent to aaa-mcp
arifos-mcp-sse       # Equivalent to aaa-mcp-sse

# Direct Python execution
python -m codebase.mcp           # stdio
python -m codebase.mcp sse       # SSE

# Development with auto-reload
uvicorn codebase.mcp.trinity_server:app --reload --port 8000
```

### Body API Server (FastAPI)

```bash
# Development server with auto-reload
uvicorn arifos.core.integration.api.app:app --reload --port 8000

# Production server (Railway/Render/Docker)
uvicorn arifos.core.integration.api.app:app --host 0.0.0.0 --port $PORT --workers 1

# With environment variables
ARIFOS_MODE=production ARIFOS_VAULT_PATH=./VAULT999 uvicorn arifos.core.integration.api.app:app
```

### Testing

```bash
# Run all tests with coverage
pytest

# Run specific test categories
pytest -m "constitutional"       # All constitutional floor tests (F1-F13)
pytest -m "f1"                   # F1 Amanah tests only
pytest -m "f2"                   # F2 Truth tests only
pytest -m "f3"                   # F3 Peace² tests only
pytest -m "f6"                   # F6 Clarity tests only
pytest -m "f9"                   # F9 Anti-Hantu tests only
pytest -m "apex"                 # APEX verdict tests
pytest -m "mcp"                  # MCP server tests
pytest -m "integration"          # Integration tests

# Run with coverage report
pytest --cov=arifos --cov-report=html --cov-report=term-missing

# Run tests with performance optimizations
ARIFOS_PHYSICS_DISABLED=1 pytest       # Disable thermodynamic computation
ARIFOS_ALLOW_LEGACY_SPEC=1 pytest      # Allow legacy spec loading
```

### Code Quality

```bash
# Type checking (strict for core modules)
mypy arifos/
mypy codebase/

# Code formatting
black arifos/ tests/ scripts/ codebase/

# Linting
ruff check arifos/ tests/ scripts/ codebase/
ruff check --fix arifos/ tests/ scripts/ codebase/  # Auto-fix issues

# Run all pre-commit hooks
pre-commit run --all-files

# Security scanning
bandit -c pyproject.toml -r arifos/
bandit -c pyproject.toml -r codebase/
detect-secrets scan
```

---

## Code Style Guidelines

### Python Style Requirements

- **Line Length**: 100 characters maximum (enforced by black and ruff)
- **Type Hints**: Required for all public functions
- **Docstrings**: Google-style docstrings required for all public functions and classes
- **Naming**: 
  - `snake_case` for functions/variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants
- **Imports**: Organized in groups (stdlib, third-party, local, conditional)

### Constitutional Code Standards

Core governance modules have stricter type enforcement via mypy overrides in `pyproject.toml`:

```toml
[[tool.mypy.overrides]]
module = [
    "arifos.enforcement.metrics",
    "arifos.enforcement.genius_metrics",
    "arifos.engines.APEX_PRIME",
    "arifos.pipeline",
    "arifos.organs.*",
]
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
```

### Pre-commit Hooks

The project uses pre-commit hooks for code quality:

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
- Constitutional floor validation (custom)

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
   - Body API endpoints
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
    "constitutional", # F1-F12 floor tests
    "f1"-"f12",       # Individual floor tests
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

**Primary Endpoint:** https://arifos.arif-fazil.com/

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
```

### Docker Deployment

```dockerfile
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

# AAA Cluster Ports (v53 Architecture)
GATEWAY_PORT=9000
AXIS_PORT=8001
ARIF_PORT=8002
APEX_PORT=8003

# arifOS Constitutional Settings
GOVERNANCE_MODE=HARD  # or SOFT (disables some floors)
VAULT_PATH=./VAULT999
ARIFOS_MODE=production  # or development

# Cloudflare Tunnel (optional)
CLOUDFLARE_TUNNEL_TOKEN=your_tunnel_token_here
```

### Health Check

```bash
curl https://arifos.arif-fazil.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "tools": 5,
  "tool_names": ["init_000", "agi_genius", "asi_act", "apex_judge", "vault_999"],
  "version": "v53.2.1",
  "uptime": "..."
}
```

---

## Security Considerations

### Constitutional Security (F1-F13)

**F1 - Amanah (Reversibility Lock)**
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
    "verdict": "SEAL|SABAR|VOID",
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
| F1 | Amanah | Reversibility + Audit | LOCK | Hard | Authority and trust |
| F2 | Truth | Confidence ≥ 0.99 | ≥ 0.99 | Hard | Factual accuracy |
| F3 | Peace² | (Benefit/Harm)² ≥ 1.0 | ≥ 1.0 | Soft | Non-destructive actions |
| F4 | Clarity | ΔS = S_output - S_input | ≤ 0 | Hard | Entropy reduction |
| F5 | Empathy | κᵣ ≥ 0.95 | ≥ 0.95 | Soft | Weakest stakeholder protection |
| F6 | Humility | Ω₀ = 1 - max_confidence | [0.03, 0.05] | Hard | Uncertainty acknowledgment |
| F7 | RASA | Entity grounding | LOCK | Hard | Reality anchoring |
| F8 | Tri-Witness | Consensus of 3 engines | ≥ 0.95 | Soft | Multi-agent agreement |
| F9 | Anti-Hantu | Consciousness detection | < 0.30 | Hard | Fake consciousness prevention |
| F10 | Ontology | Reality boundaries | LOCK | Hard | Hallucination prevention |
| F11 | Command Auth | Identity verification | Nonce + JWT | Hard | Authorization for dangerous ops |
| F12 | Injection Defense | Attack detection | < 0.85 | Hard | Prompt injection prevention |
| F13 | Curiosity | Alternative generation | Active | Soft | Exploration of alternatives |

### The 5 Verdicts

| Verdict | Symbol | Meaning | Action |
|---------|--------|---------|--------|
| **SEAL** | ✓ | All floors passed | Approved for delivery |
| **SABAR** | ⏳ | Soft failures | Adjust and retry with warnings |
| **VOID** | ✗ | Hard failures | Reject with explanation |
| **PARTIAL** | ◐ | Partial compliance | Deliver with caveats |
| **888_HOLD** | ⏸️ | Emergency pause | Requires human review |

---

## MCP Integration

### Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "arifos": {
      "url": "https://arifos.arif-fazil.com/sse"
    }
  }
}
```

### Available MCP Tools

1. **init_000** - Constitutional Ignition, Identity Verification & Session Management
2. **agi_genius** - AGI Mind Engine (F2,F4,F7,F10)
3. **asi_act** - ASI Heart Engine (F1,F5,F6,F9)
4. **apex_judge** - APEX Soul Engine (F3,F8,F11,F12,F13)
5. **vault_999** - VAULT-999 Immutable Memory (F1,F8,F10)

---

## API Endpoints

| Tier | Endpoint | Method | Transport | Purpose |
|------|----------|--------|-----------|---------|
| T1 Protocol | `/sse` | GET | SSE | MCP streaming connection |
| T2 Gateway | `/checkpoint` | POST | HTTP/REST | Constitutional validation |
| T3 Schema | `/openapi.json` | GET | HTTP/REST | OpenAPI 3.1 spec |
| T4 Observe | `/dashboard` | GET | HTTP/REST | Live Sovereign Dashboard |
| T4 Observe | `/metrics/json` | GET | HTTP/REST | Raw metrics JSON |
| T5 Health | `/health` | GET | HTTP/REST | System status |
| T6 Docs | `/docs` | GET | HTTP/REST | Interactive API documentation |

---

## Useful Scripts

```bash
# Verify ledger integrity
arifos-verify-ledger

# Analyze governance
arifos-analyze-governance

# Analyze audit trail
arifos-analyze-audit-trail

# Compute Merkle root
arifos-compute-merkle

# Safe file reader
arifos-safe-read <file_path>

# Run API server
arifos-api
```

---

## Resources and Documentation

### Canon Documents

- **Architecture**: `000_THEORY/000_ARCHITECTURE.md`
- **Constitutional Law**: `000_THEORY/000_LAW.md`
- **Agent Specification**: `000_THEORY/001_AGENTS.md`

### Quick References

- **README**: `README.md` (comprehensive user guide)
- **CHANGELOG**: `CHANGELOG.md` (version history)
- **Live API Docs**: https://arifos.arif-fazil.com/docs

### External Links

- **Repository**: https://github.com/ariffazil/arifOS
- **PyPI Package**: https://pypi.org/project/aaa-mcp/
- **Live Server**: https://arifos.arif-fazil.com/

---

**DITEMPA BUKAN DIBERI** — Constitutional intelligence is forged through governance, not given through computation.

> *Authority: Muhammad Arif bin Fazil | Penang, Malaysia*  
> *Version: v53.2.1-CODEBASE SEALED*  
> *Status: Live production on Railway*
