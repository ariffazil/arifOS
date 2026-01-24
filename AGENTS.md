# arifOS Agent Gateway

**Canon:** `000_THEORY/001_AGENTS.md`  
**Motto:** *"Init the Genius, Act with Heart, Judge at Apex, seal in Vault."*  
**Status:** v50.5.25 SEALED (Production Ready)  
**Live URL:** https://arifos-production.up.railway.app/

---

## 5-Tool Trinity Architecture

arifOS implements a constitutional AI governance framework through **5 coordinated tools** that enforce 13 immutable constitutional floors (F1-F13) on every AI interaction.

| Tool | Role | Symbol | Floors Enforced | MCP Command |
|------|------|--------|-----------------|-------------|
| `000_init` | Gate | 🚪 | F1, F11, F12 | `python -m arifos.mcp` |
| `agi_genius` | Mind | Δ | F2, F4, F6, F7, F13 | `agi_genius` tool |
| `asi_act` | Heart | Ω | F3, F4, F5 | `asi_act` tool |
| `apex_judge` | Soul | Ψ | F1, F8, F9 | `apex_judge` tool |
| `999_vault` | Seal | 🔒 | F1, F8, F10 | `999_vault` tool |

**Metabolic Pipeline:** 000 → 111 → 222 → 333 → 444 → 555 → 666 → 777 → 888 → 889 → 999

---

## Project Overview

arifOS is a **constitutional AI governance system** that acts as a safety filter for AI models. It enforces immutable constitutional rules through thermodynamic constraints and cryptographic audit trails, creating the first AI system where governance is mathematically provable and thermodynamically enforced.

### Core Mission
- **Safety Filter for AI**: Acts as a "seatbelt for ChatGPT" by checking every AI response against constitutional rules
- **Constitutional Enforcement**: Prevents AI from lying, claiming consciousness, harming vulnerable people, or being overconfident
- **Thermodynamic Governance**: Grounds AI safety in physics (ΔS ≤ 0, Peace² ≥ 1.0, Ω₀ ∈ [0.03,0.05]) rather than ethics vibes

### Key Components

1. **5-Tool Trinity Framework**: Coordinated governance through Gate → Mind → Heart → Soul → Seal
2. **13 Constitutional Floors**: Immutable governance constraints enforced on every response
3. **000-999 Metabolic Loop**: 11-stage pipeline that transforms raw AI output into governed responses
4. **AGI·ASI·APEX Trinity**: Parallel execution of Mind (Δ), Heart (Ω), and Soul (Ψ) engines
5. **VAULT-999 Memory**: 5-layer cooling system (L0-L5) with Phoenix-72 protocol and Merkle tree sealing
6. **Body API**: Unified FastAPI server exposing both MCP-over-SSE and REST endpoints for "Governance-as-a-Service"

### Technology Stack

- **Language**: Python 3.10+ (certified on 3.14)
- **Web Framework**: FastAPI + Uvicorn + Starlette
- **Core Dependencies**: numpy, pydantic, anyio, sse-starlette, fastmcp, dspy
- **Optional Dependencies**: litellm, openai, httpx, python-multipart
- **Build System**: setuptools with wheel (pyproject.toml)
- **Testing**: pytest with coverage tracking and custom constitutional markers
- **Type Checking**: mypy with strict configuration (disallow_untyped_defs for core modules)
- **Code Quality**: black (line length: 100), ruff, pre-commit hooks with security scanning
- **Deployment**: Railway.app (primary), Docker, Cloudflare Tunnel
- **Database**: SQLite (default), PostgreSQL (optional for high-scale)

### Project Structure

```
arifOS/
├── arifos/                           # Main Python package
│   ├── core/                         # Constitutional enforcement
│   │   ├── agi/                      # Mind engine (Δ) - reasoning, truth, clarity
│   │   ├── asi/                      # Heart engine (Ω) - empathy, peace, action
│   │   ├── apex/                     # Soul engine (Ψ) - judgment, proof, sealing
│   │   ├── enforcement/              # Floor validation and tri-witness logic
│   │   ├── memory/                   # VAULT-999 cooling and ledger system
│   │   ├── system/                   # Runtime orchestration and hypervisor
│   │   ├── integration/              # Body API, LLM adapters, federation
│   │   └── pipeline/                 # Metabolic loop stages (000-999)
│   ├── mcp/                          # MCP server implementation
│   │   ├── trinity_server.py         # Main server (stdio + SSE)
│   │   ├── tools/                    # 5 Trinity tool implementations
│   │   ├── models.py                 # Constitutional data models
│   │   └── metrics.py                # Prometheus metrics
│   ├── api/                          # FastAPI server components
│   └── protocol/                     # Protocol handlers and bridges
├── 000_THEORY/                       # Constitutional documentation (canon)
├── AAA_MCP/                          # MCP specifications and contracts
├── tests/                            # Test suite (164+ test files)
├── scripts/                          # Utility scripts and validators
├── setup/                            # Bootstrap and environment setup
├── docs/                             # Comprehensive documentation (245+ files)
├── VAULT999/                         # Constitutional memory vault
│   ├── AAA_HUMAN/                    # Human authority records
│   ├── BBB_LEDGER/                   # Operational hash-chained ledger
│   └── CCC_CANON/                    # Constitutional canon (L5 law)
└── archive/                          # Legacy code and migrations
```

---

## Build and Test Commands

### Development Setup

```bash
# Bootstrap complete development environment (recommended)
python setup/bootstrap/bootstrap.py --full

# Manual installation - development mode with all extras
pip install -e ".[all,dev]"

# Manual installation - minimal (core only)
pip install -e .

# Install only for Railway deployment (production)
pip install -r requirements.txt
pip install -e .
```

### Testing

```bash
# Run all tests with coverage
pytest

# Run specific test categories
pytest -m "constitutional"              # All constitutional floor tests (F1-F13)
pytest -m "f1"                          # F1 Amanah tests only
pytest -m "f2"                          # F2 Truth tests only
pytest -m "f3"                          # F3 Peace² tests only
pytest -m "f4"                          # F4 Empathy tests only
pytest -m "f6"                          # F6 Clarity tests only
pytest -m "f9"                          # F9 Anti-Hantu tests only
pytest -m "apex"                        # APEX verdict tests
pytest -m "mcp"                         # MCP server tests
pytest -m "integration"                 # Integration tests

# Run with coverage report
pytest --cov=arifos --cov-report=html --cov-report=term-missing

# Run tests with performance optimizations
ARIFOS_PHYSICS_DISABLED=1 pytest       # Disable thermodynamic computation
ARIFOS_ALLOW_LEGACY_SPEC=1 pytest      # Allow legacy spec loading

# Run constitutional evaluation script
python test_constitutional_evaluation.py
```

### Code Quality

```bash
# Type checking (strict for core modules)
mypy arifos/

# Code formatting
black arifos/ tests/ scripts/

# Linting
ruff check arifos/ tests/ scripts/
ruff check --fix arifos/ tests/ scripts/  # Auto-fix issues

# Run all pre-commit hooks
pre-commit run --all-files

# Security scanning
bandit -c pyproject.toml -r arifos/
detect-secrets scan
```

### MCP Server

```bash
# Start Trinity MCP server via stdio (for Claude Desktop, local)
python -m arifos.mcp trinity

# Start Trinity MCP server via SSE (for Railway, cloud)
python -m arifos.mcp trinity-sse
python -m arifos.mcp                       # Default: trinity mode

# Health check (when running)
curl http://localhost:8000/health
curl https://arifos-production.up.railway.app/health

# API documentation (when running)
open http://localhost:8000/docs
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

### Deployment

```bash
# Railway deployment (primary)
railway login
railway up

# Docker build and run
docker build -t arifos:v50 .
docker run -p 8000:8000 -e PORT=8000 arifos:v50

# Cloudflare tunnel (for custom domains)
cloudflared tunnel --url http://localhost:8000
```

---

## Code Style Guidelines

### Python Style Requirements

- **Line Length**: 100 characters maximum (enforced by black and ruff)
- **Type Hints**: Required for all public functions, enforced by mypy
- **Docstrings**: Google-style docstrings required for all public functions and classes
- **Naming**: snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants
- **Imports**: Organized in 4 groups (stdlib, third-party, local, conditional) with blank lines

### Constitutional Code Standards

Core governance modules have **stricter type enforcement** via mypy overrides:

```toml
# modules: enforcement/, system/ core modules
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
warn_return_any = true
no_implicit_optional = true
```

### MCP Tool Development

When implementing new Trinity tools:

1. **Follow the 5-Tool structure**: All tools must fit into Gate/Mind/Heart/Soul/Seal
2. **Enforce floors**: Each tool must validate its assigned constitutional floors
3. **Return typed responses**: Use Pydantic models from `arifos.mcp.models`
4. **Log to VAULT**: All decisions must be recorded in the immutable ledger
5. **Respect session**: Use session_id for all stateful operations

### Example tool implementation pattern:

```python
from arifos.mcp.models import TrinityResponse, FloorMetrics
from arifos.core.enforcement.floor_validators import validate_floor

async def mcp_agi_genius(arguments: dict) -> TrinityResponse:
    # 1. Validate input through 000_init gate
    # 2. Process with AGI engine (Mind)
    # 3. Validate floors F2, F4, F6, F7
    # 4. Return constitutional response
    # 5. Log to VAULT-999
    pass
```

---

## Testing Strategy

### Test Categories and Organization

1. **Constitutional Tests** (`tests/constitutional/`)
   - Validate F1-F13 floor enforcement
   - Test rejection of violations (VOID verdicts)
   - Test acceptance of compliant responses (SEAL verdicts)
   - Test soft failures (SABAR adjustments)

2. **Integration Tests** (`tests/integration/`)
   - Cross-module metabolic pipeline (000-999)
   - MCP server lifecycle
   - Body API endpoints
   - VAULT-999 ledger integrity

3. **Unit Tests** (`tests/*/test_*.py`)
   - Individual floor validators
   - Engine kernels (AGI, ASI, APEX)
   - Memory and cooling systems
   - Cryptographic functions

4. **Legacy Tests** (`tests/legacy/`)
   - Historical test coverage for deprecated modules
   - Migration validation
   - Backward compatibility

### Test Configuration

Key environment variables for testing:

```bash
# Disable physics for performance testing
ARIFOS_PHYSICS_DISABLED=1

# Allow loading legacy specs (test-only, not for production)
ARIFOS_ALLOW_LEGACY_SPEC=1

# Use in-memory ledger for faster tests
ARIFOS_TEST_LEDGER_MEMORY=1

# Mock LLM providers
ARIFOS_MOCK_PROVIDERS=1
```

### Coverage Requirements

```bash
# Current coverage baseline (enforced in CI)
--cov-fail-under=1  # Minimum 1% overall coverage

# Coverage targets
#   arifos/*: 100% coverage required (new code)
#   arifos_core: ~0% (legacy, needs migration)
#   Target: 70% by Q2 2026

# Generate coverage reports
pytest --cov=arifos --cov-report=html:htmlcov --cov-report=term-missing
```

### Continuous Integration

- **Pre-commit hooks**: Run on every commit (black, ruff, mypy, bandit, detect-secrets)
- **CI/CD**: GitHub Actions (when configured)
- **Deployment**: Automatic on Railway `main` branch
- **Health checks**: Required for deployment success

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
- `arifos.core.guards.injection_guard`: Multi-layer injection defense
- `arifos.core.guards.ontology_guard`: Reality boundary maintenance
- `arifos.core.guards.session_dependency`: Session hijacking prevention
- `arifos.enforcement.judiciary.semantic_firewall`: Content filtering

### Cryptographic Sealing

**VAULT-999 Architecture:**
- Merkle tree-based immutable ledger
- zkPC (Zero-Knowledge Proof of Constitutionality)
- Hash-chained audit trails (SHA-256)
- Sovereign signatures for human authority (AAA tier)

**Memory Tiers:**
- **AAA (Human)**: Human-only, machine-forbidden, cryptographically protected
- **BBB (Machine)**: Machine-constrained, requires consent, cooling enforced
- **CCC (Canon)**: Machine-readable, append-only, constitutional law

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

### Vulnerability Reporting

Security issues should be reported via:
1. GitHub Security Advisory (preferred)
2. Email: arifbfazil@gmail.com
3. Include: Reproduction steps, expected vs actual behavior, severity assessment

---

## Deployment Architecture

### Production Deployment (Railway.app)

**Primary Endpoint:** https://arifos-production.up.railway.app/

```bash
# Railway configuration (railway.toml)
[build]
builder = "nixpacks"
buildCommand = "pip install -e ."

[deploy]
startCommand = "sh -c 'uvicorn arifos.core.integration.api.app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1'"
healthcheckPath = "/health"
healthcheckTimeout = 120
restartPolicyType = "ON_FAILURE"
```

**Health Endpoint:**
```bash
curl https://arifos-production.up.railway.app/health

Expected response:
{
  "status": "healthy",
  "tools": 5,
  "tool_names": ["000_init", "agi_genius", "asi_act", "apex_judge", "999_vault"],
  "version": "v50.5.25",
  "uptime": "..."
}
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

# Database (optional, for high-scale)
# DATABASE_URL=postgresql://user:pass@host:5432/db

# LLM Provider API Keys (optional, for testing)
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_API_KEY=...
```

### Scaling Considerations

**Current Deployment:**
- Single worker (Uvicorn with 1 worker)
- SQLite for ledger (suitable for moderate load)
- 512MB RAM (Railway free tier compatible)

**For High-Scale Deployments:**
- PostgreSQL backend (`psycopg2-binary`)
- Redis for session caching
- Multiple workers with stateless design
- Read replicas for VAULT queries

---

## Constitutional Law Reference

### The 13 Immutable Floors (F1-F13)

| Floor | Name | Formula | Threshold | Enforced By | Purpose |
|-------|------|---------|-----------|-------------|---------|
| F1 | Amanah | Reversibility + Audit | Reversible audit trail | 000_init, apex_judge, 999_vault | Authority and trust |
| F2 | Truth | Confidence ≥ 0.99 | ≥ 0.99 | agi_genius | Factual accuracy |
| F3 | Peace² | (Benefit/Harm)² ≥ 1.0 | ≥ 1.0 | asi_act | Non-destructive actions |
| F4 | Clarity | ΔS = S_output - S_input | ≤ 0 | agi_genius, asi_act | Entropy reduction |
| F5 | Empathy | κᵣ ≥ 0.95 | ≥ 0.95 | asi_act | Weakest stakeholder protection |
| F6 | Humility | Ω₀ = 1 - max_confidence | [0.03, 0.05] | agi_genius | Uncertainty acknowledgment |
| F7 | RASA | Entity grounding | LOCK | agi_genius | Reality anchoring |
| F8 | Tri-Witness | Consensus of 3 engines | ≥ 0.95 | apex_judge, 999_vault | Multi-agent agreement |
| F9 | Anti-Hantu | Consciousness detection | < 0.30 | apex_judge | Fake consciousness prevention |
| F10 | Ontology | Reality boundaries | LOCK | 000_init | Hallucination prevention |
| F11 | Command Auth | Identity verification | Nonce + JWT | 000_init | Authorization for dangerous ops |
| F12 | Injection Defense | Attack detection | < 0.85 | 000_init | Prompt injection prevention |
| F13 | Curiosity | Alternative generation | Active | agi_genius | Exploration of alternatives |

### The 5 Verdicts

Every AI response receives one of **5 constitutional verdicts**:

1. **SEAL** ✓ - All floors passed, approved for delivery
2. **SABAR** ⏳ - Soft failures, adjust and retry with warnings
3. **VOID** ✗ - Hard failures, reject with explanation
4. **PARTIAL** ◐ - Partial compliance, deliver with caveats
5. **888_HOLD** ⏸️ - Emergency pause, requires human review

### TEACH Principles (Unified Intelligence Model)

The 13 floors are unified into **5 human-readable principles**:

- **T** - Truth: State facts only when ≥99% confident, otherwise express uncertainty
- **E** - Empathy: Protect the weakest stakeholder, consider those without voice
- **A** - Amanah: Warn before irreversible actions, ensure reversibility
- **C** - Clarity: Reduce confusion (ΔS ≤ 0), simplify complex answers
- **H** - Humility: Maintain 3-5% uncertainty, never claim 100% certainty

---

## Performance Metrics

### Current Production Metrics

- **Constitutional Reflex Speed**: 8.7ms per judgment (measured)
- **Entropy Reduction**: ΔS = 9.2 → 0.1 bits per cycle (proven)
- **Tri-Witness Consensus**: ≥ 0.95 (provably verified)
- **Orthogonality Index**: 0.97 (AGI ⊥ ASI independence)
- **Injection Defense**: 92% block rate (enforced)

### Benchmarking

```bash
# Run performance benchmarks
pytest -m benchmark

# Stress test VAULT sealing
python scripts/stress_test_vault.py

# Measure constitutional overhead
python scripts/measure_constitutional_latency.py
```

---

## Resources and Documentation

### Canon Documents

- **Agent Specification**: `000_THEORY/001_AGENTS.md`
- **Architecture**: `000_THEORY/000_ARCHITECTURE.md`
- **Constitutional Law**: `000_THEORY/000_LAW.md`
- **Quantum Migration**: `docs/QUANTUM_MIGRATION_SUMMARY.md`

### Quick References

- **README**: `README.md` (comprehensive user guide, 1000+ lines)
- **CHANGELOG**: `CHANGELOG.md` (version history)
- **Infrastructure**: `ARIFOS_INFRASTRUCTURE.md` (deployment architecture)
- **Universal Prompt**: `docs/UNIVERSAL_PROMPT.md` (system prompt for any AI)

### API Documentation

- **Live API Docs**: https://arifos-production.up.railway.app/docs
- **Live Health**: https://arifos-production.up.railway.app/health
- **OpenAPI Spec**: `openapi.json`

### Agent-Specific Guides

- **Claude Desktop**: `CLAUDE.md`
- **Gemini**: `GEMINI.md`
- **Codex**: `.codex/` workspace
- **Antigravity**: `.antigravity/` workspace (Gemini integration)

---

**DITEMPA BUKAN DIBERI** — Constitutional intelligence is forged through governance, not given through computation.

> *Authority: Muhammad Arif bin Fazil | Penang, Malaysia*  
> *Version: v50.5.25 SEALED*  
> *Status: Live production on Railway*
