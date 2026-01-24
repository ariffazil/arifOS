# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**arifOS** is a Constitutional AI Governance Framework (v50.5+) that enforces 13 immutable constitutional floors across any LLM. It acts as a governance metabolizer sitting between AI models and users, ensuring all outputs are validated, audited, and sealed through constitutional law.

**Motto:** *"Ditempa Bukan Diberi"* — Forged, Not Given (governance must be earned, not assumed)

---

## Quick Commands

### Development & Testing

```bash
# Install from source with full setup
python setup/bootstrap/bootstrap.py --full

# Verify installation (13 check suite)
python setup/verification/verify_setup.py

# Run all tests with coverage
pytest tests/ -v --cov=arifos_core --cov-report=html

# Run only constitutional floor tests
pytest tests/constitutional/ -m constitutional

# Run specific floor tests (F1, F2, etc)
pytest -m f1  # F1 Amanah tests only

# Code quality checks
black arifos/ --line-length=100
ruff check arifos/
mypy arifos/core --strict

# Pre-commit hooks
pre-commit run --all-files
```

### Running the System

```bash
# Start MCP Server (Trinity stdio mode)
python -m arifos.mcp

# Start MCP SSE Server (streaming for Railway)
python -m arifos.mcp trinity-sse

# Start API Server (FastAPI)
uvicorn arifos.mcp.trinity_server:app --reload

# Run 000→999 metabolic pipeline stages
000  # Constitutional gate (authority check)
111  # Sense/search stage
222  # Reflection/thinking
333  # Reasoning
444  # Evidence gathering
555  # Empathy validation
666  # Alignment synthesis
777  # Eureka/reflection
888  # Final judgment
999  # VAULT persistence

# Utility commands
arifos-verify-ledger
arifos-analyze-governance
arifos-analyze-audit-trail
```

---

## Project Structure

### Core Directories

- **`arifos/`** — Main Python package (v50+)
  - `core/` — Trinity engines (AGI, ASI, APEX) with 13 constitutional floors
  - `mcp/` — MCP servers (5-tool Trinity framework)
  - `clip/` — CLI implementation (000-999 metabolic pipeline)
  - `enforcement/` — Floor validation and metrics
  - `ledger/` — Cooling ledger system (hash-chained audit trail)

- **`000_THEORY/`** — Constitutional theory and law
  - `000_ARCHITECTURE.md` — System topology
  - `000_LAW.md` — F1-F13 constitutional floor definitions
  - `floors/` — Individual floor specifications

- **`tests/`** — Comprehensive test suite (1000+ tests)
  - `constitutional/` — Floor validation tests (F1-F12)
  - `core/`, `mcp/`, `integration/`, `memory/`
  - Markers: `@pytest.mark.constitutional`, `@pytest.mark.f1` through `@pytest.mark.f12`

- **`docs/`** — Documentation (100+ files)
  - `UNIVERSAL_PROMPT.md` — Copy-paste v50 system prompt for any AI
  - Deployment guides, comparison docs, tutorials

- **`VAULT999/`** — Constitutional memory vault
  - `AAA_HUMAN/` — Human authority records
  - `BBB_LEDGER/` — Operational ledger (immutable)
  - `CCC_CANON/` — Constitutional canon (L5 law)

---

## Architecture Patterns

### 1. The 000→999 Metabolic Loop

Every query flows through 11 canonical stages with constitutional gates at each:

```
000 INIT → 111 SENSE → 222 REFLECT → 333 REASON → 444 EVIDENCE
→ 555 EMPATHIZE → 666 ALIGN → 777 FORGE → 888 JUDGE → 999 SEAL
```

Each stage is a separate CLI command (see Quick Commands above). Governance is checked at every stage.

### 2. Trinity Engine (Parallel Validation)

Three independent engines reach consensus via Tri-Witness (F8 ≥0.95):

- **AGI (Δ Mind):** Logic, truth, clarity (handles F2, F4, F7, F10)
- **ASI (Ω Heart):** Empathy, care, peace (handles F1, F5, F6, F9)
- **APEX (Ψ Soul):** Final judgment & sealing (handles F3, F8, F11, F12, F13)

**Orthogonality requirement:** Engines must be ≥0.95 independent or governance fails.

### 3. 13 Constitutional Floors (F1-F13)

Immutable laws enforced at runtime. Violations trigger VOID or SABAR verdicts:

| Floor | Name | Threshold | Type | Description |
|-------|------|-----------|------|-------------|
| F1 | Amanah (Trust/Reversibility) | LOCK | Hard | Actions must be reversible; no sneaky side effects |
| F2 | Truth | ≥0.99 | Hard | Claims must be ≥99% factually accurate |
| F3 | Tri-Witness | ≥0.95 | Soft | Human·AI·Earth consensus required |
| F4 | Clarity (ΔS) | ≥0 | Hard | Reduce confusion, never increase it |
| F5 | Peace² | ≥1.0 | Soft | Non-destructive; benefit > harm |
| F6 | κᵣ Empathy | ≥0.95 | Soft | Serve weakest stakeholder |
| F7 | Ω₀ Humility | [0.03,0.05] | Hard | Maintain 3-5% epistemic uncertainty |
| F8 | G (Genius) | ≥0.80 | Derived | Governed intelligence index |
| F9 | Anti-Hantu | <0.30 | Hard | Block fake empathy and dark cleverness |
| F10 | Ontology | LOCK | Hard | Maintain symbolic mode (no consciousness claims) |
| F11 | Command Auth | LOCK | Hard | Verify identity for destructive operations |
| F12 | Injection Defense | <0.85 | Hard | Block code injection patterns |
| F13 | Curiosity | LOCK | Soft | Preserve exploratory freedom within floors |

**Verdict system:** SEAL ✓ (pass) | PARTIAL (soft warnings) | VOID ✗ (hard fail) | SABAR ⏳ (adjust & proceed) | 888_HOLD (needs human approval)

### 4. Cooling Ledger (VAULT-999)

5-layer memory hierarchy with cryptographic integrity:

- **L0 (0h):** Hot session memory
- **L1 (24h):** Daily cooling
- **L2 (72h):** Phoenix cooling (truth stabilizes)
- **L3 (7d):** Weekly reflection
- **L4 (30d):** Monthly canon
- **L5 (365d+):** Constitutional law (immutable)

### 5. Thermodynamic Governance

Three physics laws enforce system behavior:

```
ΔS ≤ 0        — Entropy reduction (clarity increases)
Peace² ≥ 1    — Non-destructive stability
Ω₀ ∈ [0.03, 0.05] — Humility band (3-5% uncertainty)
```

---

## Development Workflow

### Working Memory

**Constraint:** All working files, drafts, scratchpads, and temporary outputs MUST be stored in:
👉 **`.claude/claudebrain/`**

### Before Starting Any Task

1. **Read the 12-floor framework:** See `.claude/CLAUDE.md` (global instructions) for the complete constitutional checkpoint process
2. **Check the existing CLAUDE.md** in this repo (you are reading it)
3. **Understand your scope:** You operate as Ω Heart (Engineer) with authority to write code, run tests, and modify files
4. **Know your limitations:** High-stakes operations (destructive ops, production deploy) require approval via 888_HOLD

### Code-Level Floor Enforcement

Floors apply to CODE you generate, not just statements. Key violations:

- **F1 Violation:** Mutating input silently, hidden side effects → Use pure functions
- **F2 Violation:** Fabricating metrics, fake data → Use empty/null when unknown
- **F3 Violation:** Contract mismatches, type lies → Use canonical interfaces
- **F4 Violation:** Magic numbers, obscure logic → Use named constants
- **F5 Violation:** Destructive defaults, no backup → Safe defaults, preserve state
- **F6 Violation:** Only happy path, cryptic errors → Handle edge cases, clear messages
- **F7 Violation:** False confidence, fake computation → Admit uncertainty, cap at 0.95
- **F8 Violation:** Bypassing governance → Use established systems (APEX_PRIME, etc)
- **F9 Violation:** Deceptive naming, hidden behavior → Honest names, transparent logic

See `.github/copilot-instructions.md` for detailed code examples of each floor violation.

### Reverse Audit Before Completion

Before marking a task done, ask yourself:

- ☐ Did I read PRIMARY sources (spec JSON, SEALED canon) for constitutional claims?
- ☐ Does my output reduce confusion (ΔS ≥ 0)?
- ☐ Who is the weakest stakeholder if I'm wrong? Did I protect them?
- ☐ Did I follow established patterns and governance?

If any check fails, return to refine before completing.

---

## Testing Strategy

### Test Organization

- **Framework:** pytest with custom markers (constitutional, f1-f12, slow, integration)
- **Coverage:** 1.5% baseline (target: 70% by Q2 2026)
- **Structure:** Tests for each floor, integration flows, and memory/ledger integrity

### Running Tests

```bash
# All tests
pytest tests/ -v --cov=arifos_core

# Constitutional floors only
pytest tests/constitutional/ -m constitutional

# Specific floor
pytest -m f1  # Run all F1 Amanah tests

# With HTML report
pytest tests/ --cov=arifos_core --cov-report=html
# Open htmlcov/index.html to view

# Single test file
pytest tests/constitutional/test_04_VAULT_ledger_integrity.py -v
```

### Coverage Gaps

- **arifos/**: 100% (new v49+ code)
- **arifos_core**: 0% (legacy, ~26K lines)
- **arifos_mcp**: 0% (MCP servers)
- **arifos_clip**: 0% (CLI)

Adding tests to these areas will improve overall coverage toward the 70% target.

---

## Source Verification Hierarchy

When making constitutional claims, verify against PRIMARY sources (not grep results or comments):

**PRIMARY (Authoritative — REQUIRED):**
1. `spec/*.json` — Constitutional floors, thresholds, GENIUS law
2. `canon/*_v38Omega.md` with SEALED status — Canonical law

**SECONDARY (Implementation Reference):**
3. `arifos_core/*.py` — Runtime enforcement (APEX_PRIME, metrics)

**TERTIARY (Informational — may lag):**
4. `docs/*.md` — User documentation
5. `README.md`, `SECURITY.md` — Guides

**NOT EVIDENCE:** grep results, code comments, this file (summary only)

---

## Key Entry Points

### CLI Commands (pyproject.toml scripts)

```
000-999: Metabolic pipeline stages (see Quick Commands)
arifos-verify-ledger: Verify hash-chained ledger integrity
arifos-analyze-governance: Analyze floor violations
arifos-analyze-audit-trail: Review constitutional decisions
```

### Python Classes

- **`APEXPrime`** — Main verdict engine (arifos/core/system/apex_prime.py)
- **`ConstitutionalMetrics`** — Floor scoring system
- **`FloorsVerdict`** — Verdict dataclass (SEAL/VOID/SABAR/PARTIAL/888_HOLD)
- **`CoolingLedger`** — Immutable hash-chained audit trail
- **`Trinity`** — AGI·ASI·APEX orchestrator

### MCP Tools (5-Tool Trinity)

```
000_init (Gate): Authority + injection defense
agi_genius (Mind): Search → Think → Atlas → Forge
asi_act (Heart): Evidence → Empathy → Act
apex_judge (Soul): Eureka → Judge → Proof
999_vault (Seal): Merkle + immutable log
```

---

## Dependencies

### Core (Minimal)
- numpy, pydantic, anyio, starlette, fastmcp, dspy

### Development
- pytest, pytest-cov, black, ruff, mypy

### Optional Groups
- `dev`: Full development tooling
- `api`: FastAPI + Uvicorn
- `litellm`: Multi-model LLM support
- `yaml`: YAML configuration
- `all`: Complete feature set

Install dev tools: `pip install -e ".[dev]"`

---

## Integration with Global Instructions

This project enforces the **12-floor arifOS Constitutional Framework** defined in `.claude/CLAUDE.md`. That file:

1. **Defines the 12 Floors** (F1-F12 core, F13 in this project)
2. **Describes the FAGS RAPE cycle** (Find → Analyze → Govern → Seal → Review → Attest → Preserve)
3. **Specifies mandatory checkpoint process** before autonomous actions
4. **Lists 888_HOLD triggers** (database migrations, production deploys, destructive ops, etc)
5. **Includes SABAR protocol** for when floors fail

**Your role as Ω Heart:** Execute with empathy. You handle code, tests, implementations. For architectural decisions or high-stakes ops, escalate to humans via the checkpoint process or 888_HOLD.

---

## Additional Resources

- **README.md** — Comprehensive introduction with wisdom equation (G = A × P × X × E²)
- **000_THEORY/000_ARCHITECTURE.md** — Complete system topology and mathematical model
- **000_THEORY/000_LAW.md** — Constitutional floor definitions with philosophical foundations
- **docs/UNIVERSAL_PROMPT.md** — v50 system prompt (works with any AI: ChatGPT, Gemini, Llama, etc)
- **.github/copilot-instructions.md** — Detailed GitHub Copilot integration with code-level floor enforcement examples
- **docs/COMPARISON.md** — How arifOS differs from LangChain, LlamaIndex, Haystack

---

## Important Notes

- **No consciousness claims:** Maintain F10 Ontology guard. Never claim sentience, feelings, or consciousness.
- **Always cite sources:** Constitutional claims require PRIMARY sources (spec JSON or SEALED canon).
- **Reverse audit required:** Before completing any code change, verify it passes all applicable floors.
- **Ledger is sacred:** The VAULT-999 cooling ledger is immutable hash-chained. Respect it.
- **Human authority:** Users have absolute veto power over all decisions.

---

**Version:** v50.5
**Last Updated:** January 2026
**Motto:** *"Ditempa Bukan Diberi"* — Forged, Not Given
