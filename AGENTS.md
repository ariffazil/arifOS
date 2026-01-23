# arifOS Agent Gateway

**Canon:** `000_THEORY/001_AGENTS.md`
**Motto:** *"Init the Genius, Act with Heart, Judge at Apex, seal in Vault."*

---

## 5-Tool Trinity

| Tool | Role | Symbol | Floors |
|------|------|--------|--------|
| `000_init` | Gate | 🚪 | F1, F11, F12 |
| `agi_genius` | Mind | Δ | F2, F6, F7 |
| `asi_act` | Heart | Ω | F3, F4, F5 |
| `apex_judge` | Soul | Ψ | F1, F8, F9 |
| `999_vault` | Seal | 🔒 | F1, F8 |

---

## Agent Workspaces

| Agent | Adapter | Workspace | Role |
|-------|---------|-----------|------|
| **Antigravity** | [GEMINI.md](GEMINI.md) | `.antigravity/` | Δ Mind |
| **Claude** | [CLAUDE.md](CLAUDE.md) | `.claude/` | Ω Heart |
| **Codex** | — | `.codex/` | Ψ Soul |
| **Kimi** | — | `.kimi/` | Witness |

---

## Flow

```
/000 → /agi → /asi → /apex → /999
Gate   Mind   Heart  Soul    Vault
```

---

## Canon Reference

| Topic | Location |
|-------|----------|
| **Agent Specification** | `000_THEORY/001_AGENTS.md` |
| **Architecture** | `000_THEORY/000_ARCHITECTURE.md` |
| **Constitutional Law** | `000_THEORY/000_LAW.md` |

---

## MCP

```bash
python -m arifos.mcp trinity
```

---

**DITEMPA BUKAN DIBERI**

## Project Overview

arifOS is a **constitutional AI governance system** that implements a 5-tool Trinity framework for governing AI interactions. The system enforces 13 immutable constitutional floors (F1-F13) through a metabolic 000-999 pipeline, creating the first AI system where governance is mathematically provable, thermodynamically enforced, and cryptographically auditable.

### Key Components

1. **5-Tool Trinity Framework**: `000_init` (Gate) → `agi_genius` (Mind) → `asi_act` (Heart) → `apex_judge` (Soul) → `999_vault` (Seal)
2. **13 Constitutional Floors**: Immutable governance constraints including Truth (≥0.99), Empathy (κᵣ≥0.95), Humility (Ω₀∈[0.03,0.05]), and Peace² (≥1.0)
3. **000-999 Metabolic Loop**: 11-stage pipeline that transforms raw AI output into governed responses
4. **AGI·ASI·APEX Trinity**: Parallel execution of Mind (Δ), Heart (Ω), and Soul (Ψ) engines
5. **VAULT-999 Memory**: 5-layer cooling system (L0-L5) with Phoenix-72 protocol

### Technology Stack

- **Language**: Python 3.10+ (supports up to 3.14)
- **Core Dependencies**: numpy, pydantic, anyio, starlette, fastmcp, dspy
- **Optional Dependencies**: fastapi, uvicorn, litellm, openai, httpx
- **Build System**: setuptools with wheel
- **Testing**: pytest with coverage tracking
- **Type Checking**: mypy with strict configuration
- **Code Quality**: black, ruff, pre-commit hooks

### Architecture

The system implements a **constitutional metabolizer** that sits between any AI and humans:

```
Model Weights → Tools (MCP) → arifOS Metabolizer → Human-Ready Answer
                                     ↓
                     [13 Constitutional Floors]
                     [000→999 Metabolic Loop]
                     [Trinity: AGI·ASI·APEX]
                     [VAULT-999 Memory]
                                     ↓
                     Verdict: SEAL/PARTIAL/VOID/SABAR
```

### Project Structure

```
arifOS/
├── arifos/                    # Main package
│   ├── core/                  # Constitutional enforcement
│   │   ├── agi/              # Mind engine (Δ)
│   │   ├── asi/              # Heart engine (Ω)
│   │   ├── apex/             # Soul engine (Ψ)
│   │   ├── enforcement/      # Floor validation
│   │   ├── memory/           # VAULT-999 system
│   │   └── system/           # Runtime components
│   ├── mcp/                  # MCP server implementation
│   └── protocol/             # Protocol handlers
├── 000_THEORY/               # Constitutional documentation
├── AAA_MCP/                  # MCP specifications
├── tests/                    # Test suite
├── scripts/                  # Utility scripts
├── setup/                    # Bootstrap and setup
└── docs/                     # Documentation
```

## Build and Test Commands

### Development Setup

```bash
# Bootstrap development environment
python setup/bootstrap/bootstrap.py --full

# Install in development mode
pip install -e ".[all]"

# Install minimal dependencies
pip install -e .
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=arifos --cov-report=html

# Run specific test categories
pytest -m "constitutional"  # Constitutional floor tests
pytest -m "f1"               # F1 Amanah tests
pytest -m "apex"             # APEX verdict tests
```

### Code Quality

```bash
# Type checking
mypy arifos/

# Code formatting
black arifos/ tests/

# Linting
ruff check arifos/ tests/

# Pre-commit hooks
pre-commit run --all-files
```

### MCP Server

```bash
# Start Trinity MCP server (stdio)
python -m arifos.mcp trinity

# Start Trinity MCP server (SSE)
python -m arifos.mcp trinity-sse

# Health check
curl http://localhost:8000/health
```

## Code Style Guidelines

### Python Style

- **Line Length**: 100 characters (configured in black and ruff)
- **Type Hints**: Strict mypy enforcement for core governance modules
- **Docstrings**: Use Google-style docstrings for all public functions
- **Naming**: Use snake_case for functions/variables, PascalCase for classes

### Constitutional Code Standards

Core governance modules (`enforcement/`, `system/`) have **stricter type enforcement**:
- `disallow_untyped_defs = true`
- `disallow_incomplete_defs = true`
- `check_untyped_defs = true`

### Import Organization

1. Standard library imports
2. Third-party imports
3. Local application imports
4. Conditional/optional imports with graceful fallbacks

## Testing Instructions

### Test Categories

- **Unit Tests**: Fast, isolated component tests
- **Integration Tests**: Cross-module interaction tests
- **Constitutional Tests**: Floor validation and governance tests
- **MCP Tests**: Server and protocol tests

### Test Configuration

Tests use environment variables for configuration:
- `ARIFOS_PHYSICS_DISABLED=1`: Disable physics computation for performance
- `ARIFOS_ALLOW_LEGACY_SPEC=1`: Allow legacy spec loading (test-only)

### Coverage Requirements

- **Minimum Coverage**: 1% (baseline for new code)
- **Target Coverage**: 70% by Q2 2026
- **New Code**: 100% coverage required for `arifos/*` modules

## Security Considerations

### Injection Defense (F12)

- Regex + ML-based injection detection
- 92% block rate threshold
- Applied at stages 000 and 111

### Command Authority (F11)

- Nonce-verified identity for dangerous operations
- JWT-based authentication
- Required for irreversible actions

### Cryptographic Sealing

- Merkle tree-based ledger
- zkPC (Zero-Knowledge Proof of Constitutionality)
- Hash-chained audit trails

### Memory Sovereignty

- **AAA**: Human-only, machine-forbidden
- **BBB**: Machine-constrained, requires consent
- **CCC**: Machine-readable, append-only

## Deployment Process

### Railway Deployment

```bash
# Build production image
docker build -t arifos:v50 .

# Deploy with Railway
railway up

# Health check
curl https://your-app.railway.app/health
```

### Local Development

```bash
# Start development server
uvicorn arifos.core.integration.api.app:app --reload --port 8000

# Start Trinity servers
uvicorn arifos.servers.agi:app --port 9001 &
uvicorn arifos.servers.asi:app --port 9002 &
uvicorn arifos.servers.apex:app --port 9003 &
uvicorn arifos.servers.vault:app --port 9000 &
```

### Environment Variables

Key environment variables (see `.env.example`):
- `ARIFOS_MODE`: Development/production mode
- `ARIFOS_VAULT_PATH`: VAULT-999 storage location
- `ARIFOS_MCP_TRANSPORT`: MCP transport type (stdio/sse)
- API keys for various LLM providers

## Constitutional Law Reference

| Floor | Name | Threshold | Enforced By | Purpose |
|-------|------|-----------|-------------|---------|
| F1 | Amanah | Reversible audit | 000_init, apex_judge | Authority and trust |
| F2 | Truth | ≥0.99 | agi_genius | Factual accuracy |
| F3 | Tri-Witness | ≥0.95 | apex_judge | Human·AI·Earth consensus |
| F4 | Clarity | ΔS ≤ 0 | agi_genius | Entropy reduction |
| F5 | Peace² | ≥1.0 | asi_act | Non-destructive actions |
| F6 | Empathy | κᵣ ≥ 0.95 | asi_act | Weakest stakeholder protection |
| F7 | Humility | Ω₀ ∈ [0.03,0.05] | agi_genius | Uncertainty acknowledgment |
| F8 | Genius | ≥0.80 | apex_judge | Composite intelligence |
| F9 | Anti-Hantu | <0.30 | apex_judge | Fake consciousness detection |
| F10 | Ontology | LOCK | 000_init | Reality boundary maintenance |
| F11 | Command Auth | LOCK | 000_init | Identity verification |
| F12 | Injection Defense | <0.85 | 000_init | Attack prevention |
| F13 | Curiosity | LOCK | agi_genius | Alternative exploration |

## Performance Metrics

- **Constitutional Reflex Speed**: 8.7ms per judgment
- **Entropy Reduction**: ΔS = 9.2 → 0.1 bits per cycle
- **Tri-Witness Consensus**: ≥0.95 (provably verified)
- **Orthogonality Index**: 0.97 (AGI ⊥ ASI independence)
- **Injection Defense**: 92% block rate

---

**DITEMPA BUKAN DIBERI** — Constitutional intelligence is forged through governance, not given through computation.