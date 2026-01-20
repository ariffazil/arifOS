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

## Canonical References
- `000_THEORY/000_LAW.md` lists the 13 floors (F1-F13).
- `000_THEORY/000_ARCHITECTURE.md` explains the Trinity architecture, the 000->999 metabolic loop, and thermodynamic enforcement (Delta S, Peace squared, Omega0).
- `000_THEORY/000_FOUNDATIONS.md` documents the physics/logic basis including the Godel lock.
- `000_THEORY/001_AGENTS.md` describes the Trinity roles, witness panopticon, and federation rules.
- `000_THEORY/007_aclip.md` is the canonical aCLIP protocol reference; each stage (`/000` through `/999`) is treated as a modular handler.
- `000_THEORY/009_witness_system.md` provides the canonical witness system specification and implementation details.
- Agent adapters (`GEMINI.md`, `.claude/CLAUDE.md`, `.codex/CODEX.md`, `.kimi/KIMI.md`) remain lightweight pointers to the canon and do not duplicate policy.

## Key Configuration Files
- `pyproject.toml` plus `requirements.txt` declare the dependency surface (`numpy`, `pydantic`, `anyio`, `starlette` plus optional extras such as `fastapi`, `uvicorn`, `litellm`, `httpx`, `pygments`, `openai`).
- Tooling rules are governed by `pytest.ini`, `mypy.ini` (with strict overrides for `arifos/enforcement`, `arifos.engines.APEX_PRIME`, `arifos.pipeline`, etc.), `.pre-commit-config.yaml`, `MANIFEST.in`, and `runtime.txt`.
- Bootstrapping and verification scripts in `setup/bootstrap/` and `setup/verification/` enforce reproducible environments.

## Technology Stack & Runtime Architecture
- Python 3.10-3.14, FastAPI + Uvicorn, MCP orchestration (`arifos/mcp/` tools, settlement policy, orthogonal executor).
- Trinity engines live under `arifos/agi`, `arifos/asi`, and `arifos/apex` with floor validators in the respective `floor_checks.py` files plus `arifos/floor_validators.py`.
- VAULT-999 memory sovereignty spans `vault_999/`, `arifos/core/memory/vault/`, `arifos/core/memory/ledger/` (SQLite/Postgres), and `arifos/core/memory/phoenix/` (Phoenix-72 cooling).
- Governance primitives include ledger cryptography (`arifos/core/apex/governance/`, `arifos/engines/zkpc/`), the orthogonality guard (`arifos/mcp/orthogonality_guard.py`), and the hypervisor (`arifos/core/system/hypervisor.py`).
- aCLIP definitions are found in `arifos/protocol/aclip.py`, stage codes in `arifos/protocol/codes.py`, connectors in `arifos/clip/`, documentation in `docs/ACLIP_DOC_PUSH_README.md` and `docs/ACLIP_DOC_PUSH_INTEGRATION_GUIDE.md`.
- Container deployments rely on `Dockerfile`, `docker-compose.yml`, and the `config/` + `servers/` Dockerfiles per organ.

## Build, Test & Deployment

### Bootstrap & Setup
- Bootstrap with `python setup/bootstrap/bootstrap.py --full`
- Verify with `python setup/verification/verify_setup.py`

### Developer Loop (All Agents)
```bash
# Run tests with coverage
pytest tests/ -v --cov=arifos

# Format code
black arifos/ --line-length=100

# Lint and fix
ruff check arifos/ --fix

# Type checking
mypy arifos/ --strict

# Pre-commit hooks
pre-commit run --all-files
```

### Constitutional Verification (Pre-Commit)

A **pre-commit hook** automatically runs constitutional alignment checks before any code is committed.

**Script:** `scripts/check_track_alignment_v49.py`

**Validates:**
- F1 (Amanah) - Reversibility checks
- F2 (Truth) - Factual accuracy validation
- F7 (Ω₀ Humility) - Uncertainty acknowledgment
- F10 (Ontology) - Symbolic mode maintenance
- F12 (Injection Defense) - Security pattern detection

**Trigger:** Automatic on `git commit`

**If check fails:** Commit is aborted to prevent constitutional violations from entering the repository.

### Test Suite Execution (All Agents)

Comprehensive test suite (~2000+ tests) verifies the entire arifOS system.

**Script:** `scripts/run_tests.ps1`

**Function:**
1. Sets up correct Python environment
2. Installs development dependencies (`pytest`, coverage tools)
3. Runs full `pytest` suite with coverage analysis

**Usage:**
```powershell
# From project root
.\scripts\run_tests.ps1
```

**Test Markers** (defined in `pytest.ini`):
- `constitutional` - F1-F13 floor tests
- `f1-f13` - Individual floor tests
- `integration` - 000-999 loop tests
- `security` - Injection, authority tests
- `slow` - Long-running tests

**Examples:**
```bash
# Run constitutional tests
pytest tests/ -m constitutional

# Run specific floor tests
pytest tests/ -m "f2 or f6 or f12"

# Run integration tests
pytest tests/integration/ -v

# Run security tests
pytest tests/security/ -m injection
```

### Docker Deployment
```bash
# Build image
docker build -t arifos:v50 .

# Start services
docker-compose -f docker-compose.yml up -d
```

See `docs/DOCKER_GUIDE.md` and `config/deployment/render.yaml` for environment configuration.

### Monitoring Scripts
- `scripts/check_track_alignment_v49.py` - Constitutional alignment
- `scripts/verify_v49_wiring.py` - System wiring validation
- `scripts/test_v49_ledger.py` - Ledger integrity check
- `scripts/analyze_cooling_ledger.py` - Phoenix-72 analysis
- `scripts/verify_ledger_chain.py` - Merkle chain verification

## Code Style & Constitutional Behavior
- obey Amanah (reversibility), Truth >= 0.99, Delta S >= 0, Peace squared >= 1, Omega0 in [0.03, 0.05], kappa_r >= 0.95, orthogonality >= 0.95, and tri-witness consensus.
- Python norms: 100-character lines (`black`), typed public APIs (strict `mypy` overrides apply), Google-style docstrings, snake_case for functions, PascalCase for classes, grouped absolute imports.
- Floor-check patterns live in `arifos/core/agi/floor_checks.py`, `arifos/core/asi/floor_checks.py`, `arifos/core/apex/floor_checks.py`, and `arifos/floor_validators.py`.

## Testing Strategy
- Constitutional (F1-F13), integration (000-999 loop), unit (`tests/`), security (`tests/security/`, `arifos/core/stage_000_void/`), and temporal specialization (`tests/temporal/`).
- Use markers defined in `pytest.ini` (`constitutional`, `f1-f13`, `integration`, `slow`, `security`). Typical commands: `pytest tests/ -m constitutional`, `pytest tests/ -m "f2 or f6 or f12"`, `pytest tests/integration/ -v`, `pytest tests/security/ -m injection`.
- Verification script: `python setup/verification/verify_setup.py`.

## Security & Governance Notes
- F12 (injection defense) runs in `arifos/core/stage_000_void/injection_defense.py` and logs attempts to the cooling ledger (`arifos/core/memory/ledger/cooling_ledger.py`).
- F11 (command authority) uses `arifos/core/stage_000_void/authority_manifest.py` to require nonces, 888_HOLD for irreversible work, and explicit mandates.
- Memory accountability is enforced by `arifos/core/memory/vault/vault999.py`, `vault_999/BBB_LEDGER`, and `arifos/core/memory/ledger/ledger_store.py`; hashing is handled in `arifos/core/state/merkle*`.
- Witness logs under `000_WITNESS/` show Gemini, Claude, Codex, and Kimi verdicts for tri-witness auditing.

## Agent & Adapter Guidance
- Maintain adapters (`GEMINI.md`, `.claude/CLAUDE.md`, `.codex/CODEX.md`, `.kimi/KIMI.md`) as pointers to canonical theory files.
- Use `000_THEORY/001_AGENTS.md` to obey the "no secrets between organs" witness rule, and consult `000_THEORY/009_witness_system.md` for cross-agent transparency before issuing outputs.
- Recall that aCLIP stages (`/000` through `/999`) are modular command handlers; do not duplicate floor explanations in multiple adapters.

## Additional Resources
- `SESSION_REQUIREMENTS.md` for onboarding and environment expectations.
- `000_THEORY/004_REPO_STRUCTURE.md`, `docs/AGENTS_TOOLS_PROCESSES_MAP_v45.md`, `docs/ARIFOS_CORE_ARCHITECTURE.md` for architecture orientation.
- Deployment references: `docs/DOCKER_GUIDE.md`, `docs/WELL_UNIVERSAL_PROTOCOL.md`, `docs/MCP_KERNEL_MANUAL.md`, `docs/MCP_QUICKSTART.md`.

---

**Authority:** Muhammad Arif bin Fazil (888 Judge)  
**Motto:** *Ditempa Bukan Diberi* -- Forged, Not Given.
