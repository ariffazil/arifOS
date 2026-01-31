# AGENTS.md — arifOS Constitutional AI Governance System

> **Project:** arifOS — The Constitutional Operating System for AI  
> **Package:** aaa-mcp  
> **Version:** v53.2.9 (CODEBASE-AAA7)  
> **Python:** 3.10+  
> **License:** AGPL-3.0-only  
> **Motto:** *DITEMPA BUKAN DIBERI — Forged, Not Given*

---

## Project Overview

arifOS is a **Constitutional AI Governance Framework** implementing 13 enforceable safety floors (F1-F13), 9 paradoxes of balanced reasoning, and the Trinity architecture (AGI/ASI/APEX) with an immutable VAULT999 ledger. It serves as a "Constitution for AI" — ensuring AI decisions respect human dignity, protect the vulnerable, and maintain reversibility.

### The 9 Paradoxes

arifOS balances 9 paradoxes — pairs of values that seem to conflict but must work together:

| Paradox | Equation | Description |
|---------|----------|-------------|
| Truth ↔ Care | Compassionate Truth | Facts delivered with empathy |
| Clarity ↔ Peace | Clear Peace | Understanding without conflict |
| Humility ↔ Justice | Humble Justice | Fairness with uncertainty |
| Precision ↔ Reversibility | Careful Action | Accuracy with safety nets |
| Hierarchy ↔ Consent | Structured Freedom | Order respecting autonomy |
| Agency ↔ Protection | Responsible Power | Freedom with safeguards |
| Urgency ↔ Sustainability | Deliberate Speed | Timeliness with longevity |
| Certainty ↔ Doubt | Adaptive Conviction | Confidence with openness |
| Unity ↔ Diversity | Coherent Plurality | Togetherness respecting difference |

### The 13 Constitutional Floors

| Floor | Name | Threshold | Description |
|-------|------|-----------|-------------|
| F1 | Amanah (Trust) | Reversible/Auditable | Sacred trust, no irreversible actions |
| F2 | Truth (τ) | ≥ 0.99 | Information fidelity |
| F3 | Tri-Witness | ≥ 0.95 | Human × AI × Earth consensus |
| F4 | Empathy (κᵣ) | ≥ 0.70 | Stakeholder care |
| F5 | Peace² | ≥ 1.00 | Non-destructive power |
| F6 | Clarity (ΔS) | ≤ 0 | Entropy reduction |
| F7 | Humility (Ω₀) | [0.03, 0.05] | Uncertainty band |
| F8 | Genius (G) | ≥ 0.80 | Governed intelligence |
| F9 | Anti-Hantu | < 0.30 | Dark cleverness limit |
| F10 | Ontology | Boolean | Category lock (no consciousness claims) |
| F11 | Command Auth | Verified | Identity verification |
| F12 | Injection | < 0.85 | Injection risk limit |
| F13 | Sovereign | 1.0 | Human final authority |

### The 000-999 Metabolic Loop

```
000 IGNITE → 111 SENSE → 222 THINK → 333 REASON → 444 TRINITY_SYNC
                                               ↓
999 SEAL ← 889 PROOF ← 888 JUDGE ← 777 FORGE ← 555 EMPATHY ← 666 ALIGN
```

### Verdict System

| Verdict | Meaning | Action | HTTP Equivalent |
|---------|---------|--------|-----------------|
| SEAL | All floors pass | Proceed | 200 OK |
| PARTIAL | Soft floor warning | Proceed with caution | 200 + warnings |
| VOID | Hard floor failed | Stop, do not proceed | 403 Forbidden |
| SABAR | Serious violation | Repair before retry | 422 Unprocessable |
| 888_HOLD | Needs human confirm | Pause for review | 202 Accepted (pending) |

---

## Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| **Language** | Python | 3.10+ |
| **Core Framework** | FastMCP, MCP | ≥1.0.0 |
| **Web Server** | FastAPI, Uvicorn, Starlette | ≥0.104.1 |
| **Data Validation** | Pydantic | ≥2.0.0 |
| **Testing** | pytest, pytest-cov | ≥7.0.0 |
| **Linting** | ruff, black | ≥0.1.0, ≥23.0.0 |
| **Type Checking** | mypy | ≥1.0.0 |
| **Security** | bandit | ≥1.7.0 |
| **Deployment** | Docker, Railway, Cloudflare | — |

### Key Dependencies

```
numpy>=1.20.0
pydantic>=2.0.0
fastmcp>=0.1.0
mcp>=1.0.0
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
sse-starlette>=1.8.2
dspy>=2.4.0
redis>=5.0.0
prometheus-client>=0.19.0
```

---

## Project Structure

```
arifOS/
├── codebase/                    # Main Python package (v53+ canonical)
│   ├── agi/                     # AGI (Mind/Δ) engine - Stages 111-333
│   │   ├── engine_hardened.py   # AGI kernel implementation
│   │   ├── hierarchy.py         # 5-level hierarchical encoding
│   │   ├── precision.py         # Kalman precision weighting
│   │   └── atlas.py             # Smart lane routing (ATLAS-333)
│   ├── asi/                     # ASI (Heart/Ω) engine - Stages 555-666
│   │   ├── engine_hardened.py   # ASI kernel implementation
│   │   └── asi_components.py    # Empathy and safety components
│   ├── apex/                    # APEX (Soul/Ψ) engine - Stages 777-999
│   │   ├── kernel.py            # APEX judicial core
│   │   ├── trinity_nine.py      # 9-paradox equilibrium solver
│   │   ├── floor_checks.py      # Constitutional floor validation
│   │   └── governance/          # VAULT999 ledger, merkle, crypto
│   ├── mcp/                     # MCP server implementation
│   │   ├── __main__.py          # CLI entry point (stdio/http/sse)
│   │   ├── server.py            # stdio MCP server
│   │   ├── sse.py               # HTTP/SSE transport server
│   │   ├── tools/               # 7 canonical MCP tools
│   │   │   ├── canonical_trinity.py    # _init_, _agi_, _asi_, _apex_, _vault_
│   │   │   ├── mcp_tools_v53.py        # Human-language tools
│   │   │   └── agi_tool.py, asi_tool.py, apex_tool.py, vault_tool.py
│   │   └── external_gateways/   # Brave Search, Context7 clients
│   ├── init/000_init/           # 000 IGNITE stage
│   ├── stages/                  # 444-999 stage implementations
│   ├── system/                  # Core system types, pipeline
│   ├── bundles.py               # DeltaBundle, OmegaBundle, MergedBundle schemas
│   ├── kernel.py                # Kernel manager for AGI/ASI/APEX
│   ├── constitutional_floors.py # F1-F13 floor implementations
│   └── enforcement/             # Floor validators and metrics
│
├── tests/                       # Test suite (95 Python files)
│   ├── constitutional/          # F1-F13 floor tests
│   ├── core/                    # Core engine tests
│   ├── mcp/                     # MCP tool tests
│   ├── integration/             # Integration tests
│   ├── enforcement/             # Floor enforcement tests
│   ├── archive/                 # Archived/historical tests
│   └── conftest.py              # Pytest fixtures and configuration
│
├── 000_THEORY/                  # Constitutional theory documentation (21 files)
│   ├── 000_LAW.md               # Canonical constitutional law
│   ├── 000_ARCHITECTURE.md      # System architecture
│   ├── 010_TRINITY.md           # Trinity architecture
│   └── ...
├── SEAL999/                     # Immutable ledger storage
├── VAULT999/                    # Cryptographic seals and audit trail
├── docs/                        # Documentation
├── scripts/                     # Utility scripts
├── spec/                        # OpenAPI specs
├── archive/                     # Historical files (archived)
├── pyproject.toml               # Project configuration
├── Dockerfile                   # Container image
├── railway.toml                 # Railway deployment config
├── .pre-commit-config.yaml      # Pre-commit hooks
└── mypy.ini                     # Type checking configuration
```

---

## Build and Run Commands

### Installation

```bash
# Install in development mode
pip install -e ".[dev]"

# Or install from PyPI
pip install aaa-mcp
```

### Running the MCP Server

```bash
# stdio transport (Claude Desktop, Cursor, Kimi CLI)
python -m codebase.mcp
# OR
aaa-mcp-stdio

# HTTP/SSE transport (ChatGPT, Codex, Railway)
python -m codebase.mcp http
# OR
aaa-mcp-sse

# Minimal fallback HTTP server
python -m codebase.mcp sse-simple
```

### Development Server

```bash
# Run with hot reload
uvicorn codebase.mcp.sse:app --reload --port 8000
```

### Available Scripts

| Command | Description |
|---------|-------------|
| `aaa-mcp` | MCP server (auto-detect transport) |
| `aaa-mcp-stdio` | stdio transport (default) |
| `aaa-mcp-sse` | HTTP/SSE transport |
| `codebase-mcp` | Alternative entry point |
| `codebase-mcp-stdio` | Alternative stdio entry |
| `codebase-mcp-sse` | Alternative SSE entry |

---

## Testing Instructions

### Run All Tests

```bash
# Run pytest with verbose output
pytest -v

# Run with coverage report
pytest --cov=codebase --cov-report=term-missing

# Run with HTML coverage report
pytest --cov=codebase --cov-report=html
```

### Run Specific Test Categories

```bash
# Constitutional floor tests
pytest -m "constitutional"

# Integration tests
pytest -m "integration"

# Exclude slow tests
pytest -m "not slow"

# Specific floor tests
pytest -m "f1"   # F1 Amanah
pytest -m "f2"   # F2 Truth
```

### Test Markers

| Marker | Description |
|--------|-------------|
| `constitutional` | Tests validating constitutional floors (F1-F13) |
| `f1` - `f13` | Individual floor tests |
| `integration` | Tests requiring external services |
| `slow` | Long-running tests |
| `apex` | APEX Prime verdict tests |
| `agi` | AGI engine tests |
| `asi` | ASI engine tests |
| `mcp` | MCP server tests |

### Test Configuration

Tests use fixtures from `tests/conftest.py`:
- Physics is disabled by default (`ARIFOS_PHYSICS_DISABLED=1`)
- Legacy spec bypass enabled for tests (`ARIFOS_ALLOW_LEGACY_SPEC=1`)
- Use `enable_physics_for_apex_theory` fixture for physics tests

---

## Code Style Guidelines

### Formatting

- **Line length:** 100 characters (Black + Ruff)
- **Formatter:** Black (`black --line-length=100`)
- **Linter:** Ruff (`ruff check . --fix`)
- **Import style:** Use `isort` compatible ordering

### Type Checking

- **Tool:** mypy with strict configuration for core governance modules
- **Config:** `mypy.ini` for strict checking
- Core governance modules (`codebase/enforcement/`, `codebase/apex/`) have strict type enforcement

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run on all files
pre-commit run --all-files
```

Pre-commit hooks include:
- Black formatting
- Ruff linting
- MyPy type checking
- Bandit security scanning
- Trailing whitespace removal
- End of file fixing
- YAML/JSON/TOML syntax checking
- Large file detection
- Merge conflict detection
- Private key detection
- Debug statement detection
- Constitutional floor validation
- F9 Anti-Hantu check (no consciousness claims)
- F1 Amanah check (no irreversible operations)

### Architecture Rules

- **Brain/Body separation:** All logic in `codebase/` kernels, MCP bridge is zero-logic wiring
- **No new files without integration:** Every new module must be wired into the existing pipeline
- **Hardened imports:** Use try/except for optional dependencies, never crash on import
- **Verdicts are 5-state:** SEAL, PARTIAL, VOID, SABAR, 888_HOLD. No new verdict types without constitutional amendment.

### Naming Conventions

- **Modules:** lowercase with underscores (`engine_hardened.py`)
- **Classes:** PascalCase (`DeltaBundle`, `AGIFloorScores`)
- **Functions:** snake_case (`compute_hash`, `mcp_agi`)
- **Constants:** UPPER_CASE (`TRUTH_THRESHOLD`, `F2_TRUTH`)
- **Private:** leading underscore (`_detect_injection`)

---

## The 7 MCP Tools

All tools are exposed via the Model Context Protocol:

| Tool | Stage | Purpose | Constitutional Floors |
|------|-------|---------|----------------------|
| `_init_` | 000 | Session gate, auth, injection detection | F11, F12 |
| `_agi_` | 111-333 | Mind engine: sense, think, reason | F2, F4, F7, F13 |
| `_asi_` | 555-666 | Heart engine: empathy, safety, align | F1, F5, F6, F9 |
| `_apex_` | 777-888 | Soul engine: judgment, verdict | F3, F8, F10 |
| `_vault_` | 999 | Immutable ledger sealing | F1 |
| `_trinity_` | 000-999 | Full metabolic pipeline | All |
| `_reality_` | — | External fact-checking | F7 (grounding) |

### Tool Usage Pattern

```python
# 1. Always call _init_ first
init_result = await mcp_init(action="init", query="...")

# 2. Use _trinity_ for complete evaluation (recommended)
result = await mcp_trinity(query="Should we deploy this AI?")

# 3. Or use individual tools
agi_result = await mcp_agi(action="think", query="...")
asi_result = await mcp_asi(action="empathize", query="...")
apex_result = await mcp_apex(action="judge", query="...")
```

---

## Bundle Architecture

The system uses thermodynamically-isolated data bundles:

### DeltaBundle (AGI Output)
- Session metadata
- Parsed facts from 111 SENSE
- 3 hypotheses from 222 THINK
- Reasoning tree from 333 REASON
- Floor scores: F2, F4, F7, F13
- Precision weighting (Kalman), hierarchical encoding

### OmegaBundle (ASI Output)
- Stakeholder analysis (555 EMPATHY)
- Safety constraints (666 ALIGN)
- Floor scores: F1, F5, F6, F9, F11, F12
- Empathy score κᵣ

### MergedBundle (444 TRINITY_SYNC)
- Combines Delta + Omega
- Tri-witness consensus calculation
- Pre-verdict before 888 JUDGE

---

## Deployment

### Docker

```bash
docker build -t arifos:v53 .
docker run -p 8000:8000 arifos:v53
```

### Railway

```bash
# Deploy via CLI
railway login
railway link
railway up
```

Endpoints:
| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Health check |
| `GET /mcp` | MCP SSE transport |
| `POST /checkpoint` | Universal constitutional validation |
| `GET /dashboard` | Real-time monitoring |
| `GET /metrics/json` | Live constitutional metrics |
| `GET /openapi.json` | OpenAPI 3.1 spec |
| `GET /docs` | Interactive API documentation |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ARIFOS_MODE` | `production` or `development` | `production` |
| `ARIFOS_MCP_MODE` | `bridge`, `stdio`, or `sse` | `bridge` |
| `ARIFOS_ENV` | Environment name | `production` |
| `PORT` | Server port | `8000` |
| `ARIFOS_PHYSICS_DISABLED` | Disable physics (tests) | `0` |
| `ARIFOS_ALLOW_LEGACY_SPEC` | Bypass manifest check (tests) | `0` |
| `ARIFOS_LOG_LEVEL` | Logging level | `INFO` |
| `REDIS_URL` | Redis connection URL | — |

---

## Security Considerations

### Constitutional Floors (F1-F13)

1. **F1 Amanah:** All actions must be reversible or auditable
2. **F2 Truth:** Confidence ≥ 0.99 required for claims
3. **F3 Tri-Witness:** Human × AI × System consensus ≥ 0.95
4. **F4 Clarity:** Entropy must decrease (ΔS ≤ 0)
5. **F5 Justice:** Weakest stakeholders prioritized
6. **F6 Peace:** Peace² ≥ 1.0 (internal × external)
7. **F7 Humility:** Uncertainty band Ω₀ ∈ [0.03, 0.05]
8. **F8 Genius:** Governed intelligence G ≥ 0.80
9. **F9 Anti-Hantu:** No consciousness claims (C_dark < 0.30)
10. **F10 Ontology:** Reality grounding check
11. **F11 Command Auth:** Authority verification
12. **F12 Injection Defense:** Prompt injection detection
13. **F13 Sovereign:** Human has final veto

### Security Scanning

- Bandit security linter runs on all commits
- detect-secrets scans for hardcoded credentials
- Private key detection in pre-commit hooks
- GitLeaks scanning in CI/CD

---

## CI/CD Pipeline

GitHub Actions workflows in `.github/workflows/`:

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| `ci.yml` | Build, lint, type check, test | push, PR |
| `constitutional_alignment.yaml` | Validate F1-F13 compliance | push, PR |
| `ledger-audit.yml` | Audit VAULT999 integrity | scheduled |
| `secrets-scan.yml` | Detect hardcoded secrets | push, PR |
| `deploy-cloudflare.yml` | Deploy to Cloudflare | manual |
| `publish.yml` | Publish to PyPI | release |
| `check_skill_drift.yml` | Check skill file drift | scheduled |
| `check_spec_imports.yml` | Validate spec imports | push |
| `trackb_seal.yml` | Track B seal verification | push |

---

## Resources

- **README:** `README.md` — User-facing documentation
- **Architecture:** `ARCHITECTURE_COMPLETE.txt`, `CODE_ARCHITECTURE_MAP.md`
- **Changelog:** `CHANGELOG.md`
- **Contributing:** `CONTRIBUTING.md`
- **Constitutional Theory:** `000_THEORY/` (21 documentation files)
- **OpenAPI Spec:** `openapi.json`, `spec/`
- **Live Server:** https://arif-fazil.com/
- **Health Check:** https://arif-fazil.com/health
- **MCP Endpoint:** https://arif-fazil.com/mcp

---

## Contact

**Author:** Muhammad Arif bin Fazil  
**Email:** arifbfazil@gmail.com  
**Repository:** https://github.com/ariffazil/arifOS  
**License:** AGPL-3.0-only

---

*"DITEMPA BUKAN DIBERI — Truth must cool before it rules."*
