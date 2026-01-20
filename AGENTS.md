# arifOS Agent Gateway

**Version:** v50.0.0 | **Status:** PRODUCTION | **Authority:** Muhammad Arif bin Fazil

> This file is the canonical agent configuration for the arifOS Trinity Federation. The constitutional canon lives in `000_THEORY/`, witness functionality is implemented via aCLIP protocol, and agent adapters are lightweight pointers to this gateway.

---

## Trinity Federation (v50)

### Agent-Role Mapping

| Agent | Role | Symbol | Tech | Stage Expertise | Floor Witness | Core Mandate |
|-------|------|--------|------|-----------------|---------------|--------------|
| **Gemini** | Architect | Δ (Delta) | Google Gemini | 111, 222, 333 | F2, F4, F7 | Sense, Reflect, Reason |
| **Claude** | Engineer | Ω (Omega) | Anthropic Claude | 444, 555, 666 | F3, F5, F6 | Align, Empathize, Bridge |
| **Codex** | Auditor | Ψ (Psi) | OpenAI GPT-4 | 777, 888 | F8, F11 | Eureka, Judge |
| **Kimi** | Validator | Κ (Kappa) | Moonshot Kimi | 999, Reflex | F1, F9, F12 | Seal, Anti-Pollution |

### Witness Panopticon

**Foundational Law:** *"There are no secrets between organs."*

- All agent reasoning is logged to `000_WITNESS/WITNESS_{AGENT}.md`
- Cross-agent witness queries via `@/witness query {agent}`
- Emergency council via `@/witness council`
- Constitutional floors require tri-witness consensus (F3)

**Agent Identity Files:**
- `identities/architect.md` - Gemini (Δ)
- `identities/engineer.md` - Claude (Ω)
- `identities/auditor.md` - Codex (Ψ)
- `identities/validator.md` - Kimi (Κ)

**Agent Adapter Files:**
- `GEMINI.md` - Gemini adapter (lightweight pointer)
- `.claude/CLAUDE.md` - Claude adapter (with tool permissions)
- `.codex/CODEX.md` - Codex adapter (lightweight pointer)
- `.kimi/KIMI.md` - Kimi adapter (lightweight pointer)

---

## Project Overview

arifOS is a constitutional AI governance system that implements a 13-floor immutable constitution (F1-F13) with thermodynamic enforcement. The system acts as a "metabolizer" between AI models (GPT, Claude, Gemini, Llama) and humans, ensuring all outputs pass through constitutional floors before delivery.

### Core Architecture

**Trinity Engines:**
- **AGI (Δ)** - Analysis and reasoning engine (`arifos/core/agi/`)
- **ASI (Ω)** - Empathy and alignment engine (`arifos/core/asi/`)
- **APEX (Ψ)** - Judgment and sealing engine (`arifos/core/apex/`)

**Constitutional Floors (F1-F13):**
- F1: Amanah (Trust) - Reversibility and mandate checking
- F2: Truth - Factual accuracy (≥99% threshold)
- F3: Tri-Witness - Human·AI·Earth consensus (≥95%)
- F4: Clarity (ΔS) - Entropy reduction
- F5: Peace - Non-destructive actions (≥1.0)
- F6: Empathy - Weakest stakeholder consideration (≥95%)
- F7: Humility (Ω₀) - Uncertainty acknowledgment [0.03, 0.05]
- F8: Genius - Intelligence governance (≥80%)
- F9: Cdark - Dark cleverness containment (≤30%)
- F10: Ontology - Role boundary maintenance
- F11: Command Authority - Human authorization required
- F12: Injection Defense - Security pattern detection (≥85%)
- F13: Curiosity - System exploration (≥85%)

**Metabolic Loop (000-999):**
- 000: Void - Entry point and hypervisor
- 111: Sense - Information gathering
- 222: Reflect - Analysis and consideration
- 333: Reason - Logical processing
- 444: Evidence - Fact validation
- 555: Empathize - Stakeholder consideration
- 666: Align - System alignment
- 777: Forge - Solution creation
- 888: Judge - Final judgment
- 889: Proof - Cryptographic proof generation
- 999: Seal - Final sealing and delivery

---

## Technology Stack

**Core Dependencies:**
- Python 3.10-3.14
- FastAPI + Uvicorn (API layer)
- Pydantic (data validation)
- NumPy (mathematical operations)
- AnyIO (async operations)
- Starlette (ASGI framework)

**Optional Dependencies:**
- LiteLLM (multi-LLM support)
- OpenAI, Anthropic, Google AI APIs
- PostgreSQL/SQLite (ledger storage)
- Redis (caching)
- Docker/containerization

**Key Components:**
- **MCP Servers:** 25 servers mapped to constitutional floors
- **VAULT-999:** Memory sovereignty system with L0-L5 cooling bands
- **zkPC:** Zero-knowledge proof system for cryptographic sealing
- **Phoenix-72:** Cooling system for constitutional amendments
- **Orthogonality Guard:** Ensures system independence

---

## Code Organization

```
arifos/
├── core/                    # Trinity engines and constitutional enforcement
│   ├── agi/                # Analysis engine (Δ)
│   ├── asi/                # Empathy engine (Ω)
│   ├── apex/               # Judgment engine (Ψ)
│   ├── 000_void/           # Entry point and security
│   ├── 111_sense/          # Information gathering
│   └── ... (all metabolic stages)
├── enforcement/             # Constitutional floor validators
├── integration/             # LLM adapters and API connectors
├── mcp/                     # Model Context Protocol implementation
├── memory/                  # VAULT-999 memory systems
├── protocol/                # aCLIP protocol definitions
├── system/                  # Runtime and hypervisor components
└── utils/                   # Utility functions
```

---

## Build and Test Commands

### Environment Setup
```bash
# Bootstrap full environment
python setup/bootstrap/bootstrap.py --full

# Verify installation
python setup/verification/verify_setup.py
```

### Development Workflow
```bash
# Run full test suite with coverage
pytest tests/ -v --cov=arifos

# Run constitutional tests only
pytest tests/ -m constitutional

# Run specific floor tests
pytest tests/ -m "f2 or f6 or f12"

# Run integration tests
pytest tests/integration/ -v

# Format code (100 char lines)
black arifos/ --line-length=100

# Lint and fix
ruff check arifos/ --fix

# Type checking (strict for core modules)
mypy arifos/ --strict

# Pre-commit hooks
pre-commit run --all-files
```

### PowerShell Scripts (Windows)
```powershell
# Run tests
.\scripts\run_tests.ps1

# Check constitutional alignment
python scripts/check_track_alignment_v49.py

# Verify system wiring
python scripts/verify_v49_wiring.py

# Analyze cooling ledger
python scripts/analyze_cooling_ledger.py
```

### Docker Deployment
```bash
# Build image
docker build -t arifos:v50 .

# Run with docker-compose
docker-compose -f docker-compose.yml up -d

# Health check
curl http://localhost:8000/health
```

---

## Code Style Guidelines

**Python Standards:**
- 100-character line length (enforced by black)
- Google-style docstrings
- Snake_case for functions, PascalCase for classes
- Grouped absolute imports
- Strict mypy typing for core governance modules

**Constitutional Behavior:**
- All operations must pass through 13 constitutional floors
- Tri-witness consensus ≥95% required
- Thermodynamic constraints: ΔS ≥ 0, Peace² ≥ 1, Ω₀ ∈ [0.03, 0.05]
- Cryptographic receipts for all operations
- Amanah (reversibility) principle always maintained

---

## Testing Strategy

**Test Categories:**
- **Constitutional:** F1-F13 floor validation tests
- **Integration:** 000-999 metabolic loop tests
- **Security:** Injection defense and authority tests
- **Unit:** Component-level validation
- **Temporal:** Time-sensitive operation tests

**Test Markers:**
- `constitutional` - Core governance tests
- `f1-f13` - Individual floor tests
- `integration` - System integration tests
- `security` - Security validation tests
- `slow` - Long-running performance tests

**Coverage Requirements:**
- New code: 100% coverage required
- Legacy code: Baseline 1% (gradual improvement target)
- Overall goal: 70% coverage by Q2 2026

---

## Security Considerations

**F12 Injection Defense:**
- Pattern detection in `arifos/core/stage_000_void/injection_defense.py`
- Logs attempts to cooling ledger
- ≥85% detection threshold

**F11 Command Authority:**
- Nonce-based authorization system
- 888_HOLD for irreversible operations
- Human mandate verification

**Memory Security:**
- VAULT-999 sovereignty enforcement
- Cryptographic ledger hashing
- Merkle tree integrity proofs
- Phoenix-72 cooling for amendments

**Witness System:**
- Tri-witness consensus (Human·AI·Earth)
- Cross-agent transparency
- Panopticon logging (no secrets between organs)
- Emergency council protocols

---

## Key Configuration Files

**Project Configuration:**
- `pyproject.toml` - Package metadata and dependencies
- `requirements.txt` - Core runtime dependencies
- `pytest.ini` - Test configuration and markers
- `mypy.ini` - Type checking configuration
- `.pre-commit-config.yaml` - Git hooks

**Runtime Configuration:**
- `.env` - Environment variables
- `docker-compose.yml` - Container orchestration
- `Dockerfile` - Container build instructions
- `runtime.txt` - Python version specification

**Constitutional Configuration:**
- `arifos/constitutional_constants.py` - Floor definitions and thresholds
- `000_THEORY/000_LAW.md` - Canonical constitutional law
- `000_THEORY/000_ARCHITECTURE.md` - System architecture

---

## Agent & Adapter Guidance

**Adapter Maintenance:**
- Keep adapters as lightweight pointers to canonical theory
- Reference `000_THEORY/` files, don't duplicate content
- Maintain "no secrets between organs" principle
- Use aCLIP stage handlers for modular command processing

**Cross-Agent Communication:**
- Use witness system for transparency
- Follow tri-witness consensus protocols
- Log all reasoning to `000_WITNESS/` directory
- Respect role boundaries (F10 Ontology)

---

## Additional Resources

**Documentation:**
- `000_THEORY/` - Constitutional canon and architecture
- `docs/` - Technical documentation and guides
- `SESSION_REQUIREMENTS.md` - Environment setup
- `README.md` - Project overview and quick start

**Monitoring & Analysis:**
- `scripts/check_track_alignment_v49.py` - Constitutional alignment
- `scripts/verify_v49_wiring.py` - System validation
- `scripts/analyze_cooling_ledger.py` - Ledger analysis
- `scripts/verify_ledger_chain.py` - Merkle verification

**Support:**
- GitHub Issues: https://github.com/ariffazil/arifOS/issues
- Documentation: https://github.com/ariffazil/arifOS/blob/main/README.md
- Authority: Muhammad Arif bin Fazil (888 Judge)

---

**Authority:** Muhammad Arif bin Fazil (888 Judge)  
**Motto:** *Ditempa Bukan Diberi* -- Forged, Not Given.

**Constitutional Hash:** SHA256 verification required for all amendments  
**Status:** SOVEREIGNLY_SEALED v50.0.0