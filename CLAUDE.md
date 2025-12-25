# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Version:** v45.0.0 + Patch B | **Tests:** 2261/2261 (100%) | **Safety Ceiling:** 99%

**Imports:** `~/.claude/CLAUDE.md` — Global governance (floors, SABAR, verdicts)
**Extends:** [AGENTS.md](AGENTS.md) — Full constitutional governance

**Latest:** v45Ω Patch B (2025-12-24) — Δ Router + Lane-Aware Truth Gating (explanatory queries fixed). See [CHANGELOG.md](CHANGELOG.md) for details.

---

## Quick Reference

### Installation & Setup

**Requirements:** Python 3.10+ (verify compatibility with your Python version)

```bash
# Install package (PyPI)
pip install arifos

# Development install (editable)
pip install -e .

# Install with optional dependencies
pip install -e ".[dev,yaml,api,litellm]"

# Core dependencies: numpy>=1.20.0, pydantic>=2.0.0
# Optional dependencies:
#   dev: pytest, pytest-cov, black, ruff, mypy
#   yaml: pyyaml>=6.0.0
#   api: fastapi, uvicorn
#   litellm: litellm>=1.0.0
```

### Testing

```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_apex_genius_verdicts.py -v

# Run specific test function
pytest tests/test_apex_genius_verdicts.py::test_seal_verdict -v

# Run tests for specific module
pytest tests/governance/ -v
pytest arifos_core/ -v

# Run with coverage
pytest --cov=arifos_core --cov-report=html

# Fast failure (stop on first error)
pytest -x
```

### Pipeline & CLI

```bash
# Run the governed pipeline demo
python -m arifos_core.system.pipeline

# CLI Tools (installed as commands)
arifos-analyze-governance --ledger cooling_ledger/L1_cooling_ledger.jsonl
arifos-verify-ledger               # Hash-chain integrity check
arifos-show-merkle-proof --index 0 # Cryptographic proof
arifos-safe-read <file>            # FAG: Governed file read

# Pipeline stage commands (000-999)
000 void "Task description"        # Initialize
111 sense                          # Gather context
333 reason                         # Generate logic
666 align                          # Constitutional check
999 seal --apply                   # Finalize

# Trinity: Universal Git Governance
# Use trinity wrapper scripts (cross-platform):
python scripts/trinity.py forge <branch>     # Analyze changes
python scripts/trinity.py qc <branch>        # Constitutional check
python scripts/trinity.py seal <branch> "Reason"  # Seal with approval

# Or use platform-specific wrappers:
# Unix/Linux/Mac: ./trinity.sh forge <branch>
# Windows PowerShell: .\trinity.ps1 forge <branch>

# Full v45 Demo
python demo_sealion_v45_full.py    # Complete ΔΩΨ Trinity demonstration
```

---

## Architecture Overview

### Core Structure

```text
arifos_core/           # Main governance engine
├── evidence/          # v45 Sovereign Witness evidence system
├── judiciary/         # Constitutional verdict logic (APEX_PRIME)
├── temporal/          # Time-based governance (Phoenix-72)
├── governance/        # Core governance orchestration
├── enforcement/       # Floor detectors & validators
├── system/            # Pipeline & kernel
├── memory/            # 6-band memory system (EUREKA)
├── floor_detectors/   # F1-F9 Python-sovereign enforcement
├── stages/            # 000-999 pipeline stages
├── waw/               # Multi-agent federation (@LAW, @GEOX, @WELL, @RIF)
├── trinity/           # Git governance system
└── mcp/               # MCP server integration

arifos_clip/           # CLI Pipeline (A-CLIP) - governance workflow
├── aclip/cli/         # CLI dispatchers (000-999 commands)
├── aclip/core/        # Core pipeline logic
└── aclip/bridge/      # Integration bridges

arifos_eval/           # Evaluation & testing frameworks
└── apex/              # APEX evaluation suite

tests/                 # Test suites
├── governance/        # Governance-specific tests
├── evidence/          # Evidence system tests
├── judiciary/         # Verdict logic tests
├── temporal/          # Time-based governance tests
└── integration/       # Integration tests

L1_THEORY/canon/       # Constitutional law documents (read-only canon)
├── 01_floors/         # F1-F9 floor definitions
├── 03_runtime/        # Pipeline & execution
├── 04_measurement/    # GENIUS metrics
└── 05_memory/         # EUREKA memory architecture
```

### Key Concepts

**Nine Constitutional Floors (F1-F9):** Hard boundaries that govern all AI outputs. F1 (Amanah), F2 (Truth), F3 (Tri-Witness), F4 (DeltaS/Clarity), F5 (Peace²), F6 (κᵣ/Empathy), F7 (Ω₀/Humility), F8 (GENIUS), F9 (Anti-Hantu/C_dark).

**000→999 Pipeline:** Every governed decision flows through metabolic stages: VOID(000) → SENSE(111) → REFLECT(222) → REASON(333) → EVIDENCE(444) → EMPATHIZE(555) → ALIGN(666) → FORGE(777) → JUDGE(888) → SEAL(999).

**Verdicts:** SEAL (approved), PARTIAL (conditional), SABAR (pause), VOID (rejected), HOLD (human escalation), SUNSET (lawful revocation).

**Memory Bands:** VAULT (constitutional law), LEDGER (audit trail), ACTIVE (working state), PHOENIX (amendments), WITNESS (patterns), VOID (quarantine).

**W@W Federation:** Multi-agent system with @LAW (Amanah), @GEOX (Truth), @WELL (Care), @RIF (Reason). Each agent has veto power within their domain.

**Claim Detection (v45Ω Patch A):** Physics > Semantics structural analysis. Responses are analyzed for factual claims using entity density, numeric patterns, and assertion counting (NOT keyword matching). Phatic communication ("hi", "how are u?") is exempt from F2 Truth floor when `has_claims=False`. Identity hallucinations still blocked.

---

## Source Verification Protocol

**HARD RULE:** Constitutional claims MUST be verified against PRIMARY sources.

### Source Authority Tiers

**PRIMARY (Authoritative — REQUIRED for constitutional claims):**

1. `spec/v42/*.json` — Constitutional floors, GENIUS law, thresholds
2. `L1_THEORY/canon/*_v42.md` with SEALED status — Canonical law

**SECONDARY (Implementation Reference):**

1. `arifos_core/*.py` — Runtime enforcement (APEX_PRIME, metrics)

**TERTIARY (Informational Only — may lag behind PRIMARY):**

1. `docs/*.md` — User documentation
2. `README.md`, `SECURITY.md` — Getting started guides

**NOT EVIDENCE:**

- ❌ grep/search results (discovery, not verification)
- ❌ Comments in code or tests (may reflect outdated understanding)
- ❌ This instruction file (summary only, not law)

### Mandatory Verification Process

**Before making ANY constitutional claim:**

1. ☐ Read PRIMARY source (spec JSON or SEALED canon)
2. ☐ Verify claim matches EXACT definition/threshold
3. ☐ If conflict detected → **ESCALATE TO 888_HOLD**
4. ☐ Document which PRIMARY source was verified

**Constitutional claims include:**

- Floor thresholds (F1-F9)
- Verdict conditions (SEAL/PARTIAL/VOID/SABAR/888_HOLD)
- Metric formulas (G, C_dark, Psi)
- Process requirements (Stage 000-999 rules)

**If you cannot answer "Which PRIMARY source did I read?" → you have NOT verified.**

---

## Development Workflows

### Adding a New Floor Detector

1. Create detector in [arifos_core/floor_detectors/](arifos_core/floor_detectors/)
2. Implement `detect()` method returning score 0.0-1.0
3. Add to floor registry in [arifos_core/enforcement/](arifos_core/enforcement/)
4. Update spec in [spec/v42/constitutional_floors.json](spec/v42/constitutional_floors.json)
5. Add tests in [tests/test_*.py](tests/)
6. Update canon docs in [L1_THEORY/canon/01_floors/](L1_THEORY/canon/01_floors/)

### Adding a Pipeline Stage

1. Create stage module in [arifos_core/stages/](arifos_core/stages/)
2. Implement stage interface (input/output contracts)
3. Register in [arifos_core/system/pipeline.py:39](arifos_core/system/pipeline.py)
4. Add CLI dispatcher in [arifos_clip/aclip/cli/](arifos_clip/aclip/cli/)
5. Update tests in [tests/integration/](tests/integration/)
6. Document in canon: [L1_THEORY/canon/03_runtime/](L1_THEORY/canon/03_runtime/)

### Modifying Constitutional Law

⚠️ **888_HOLD Trigger:** Constitution changes require explicit approval.

1. **Never modify canon directly** — Canon is read-only truth
2. Propose amendment via Phoenix-72 system:

   ```bash
   arifos-propose-canon --list
   ```

3. Update spec files in [spec/v42/](spec/v42/) first
4. Update code in [arifos_core/](arifos_core/) to match spec
5. Run alignment tests:

   ```bash
   pytest tests/test_*_v38_alignment.py -v
   ```

6. Request human seal via `arifos-seal-canon`

---

## Code-Level Floor Enforcement

**CRITICAL:** Constitutional floors apply to CODE you generate, not just statements you make. The governance layer extends INTO code generation.

### F1-CODE: Amanah (Integrity in Code)

**Law:** Code must be reversible. No silent side effects.

```python
# ❌ F1 VIOLATION - Irreversible without warning
def process_data(items):
    items.clear()  # Mutates input silently
    return new_items

# ✅ F1 COMPLIANT - Pure function, no side effects
def process_data(items):
    return [transform(item) for item in items]  # Input unchanged
```

### F2-CODE: Truth (Honest Data Structures)

**Law:** Data must represent REALITY. Empty/null when data doesn't exist. Never fabricate evidence of work not performed.

```python
# ❌ F2 VIOLATION - Fabricating stages that didn't run
session_data = {
    "steps": [
        {"name": "sense", "output": "Context gathered"},   # LIE - didn't run
    ]
}

# ✅ F2 COMPLIANT - Honest representation
session_data = {
    "steps": []  # EMPTY - no stages ran, don't claim they did
}
```

### F4-CODE: DeltaS (Clarity Gain)

**Law:** Code must reduce confusion, not add it. No magic numbers.

```python
# ❌ F4 VIOLATION - Increases confusion
if x > 0.95 and y < 0.30:  # What are these numbers?
    return "SEAL"

# ✅ F4 COMPLIANT - Self-documenting
TRUTH_THRESHOLD = 0.95
DARK_CLEVERNESS_CEILING = 0.30

if truth >= TRUTH_THRESHOLD and c_dark < DARK_CLEVERNESS_CEILING:
    return "SEAL"
```

### F5-CODE: Peace² (Non-Destructive Operations)

**Law:** Code must not destroy data, corrupt state, or cause harm.

```python
# ❌ F5 VIOLATION - Destructive default
def cleanup(path: str = "/"):
    shutil.rmtree(path)  # Could delete entire filesystem!

# ✅ F5 COMPLIANT - Safe defaults, explicit destruction
def cleanup(path: str):
    if not path or path == "/":
        raise ValueError("Refusing to delete root or empty path")
    # Proceed with caution...
```

### F7-CODE: Omega0 (Humility - State Uncertainty)

**Law:** Code must acknowledge what it doesn't know. Never fake confidence.

```python
# ❌ F7 VIOLATION - False certainty
def analyze(text) -> dict:
    return {"sentiment": "positive", "confidence": 1.0}  # Impossible certainty

# ✅ F7 COMPLIANT - Honest uncertainty
def analyze(text) -> dict:
    score = model.predict(text)
    return {
        "sentiment": "positive" if score > 0.5 else "negative",
        "confidence": min(score, 0.95),  # Cap at 0.95
        "uncertainty": "Model prediction, not ground truth"
    }
```

### F8-CODE: G (Governed Intelligence)

**Law:** Code must follow established patterns and governance structures.

```python
# ❌ F8 VIOLATION - Bypassing governance
def process_query(query):
    return llm.generate(query)  # Raw, ungoverned LLM output!

# ✅ F8 COMPLIANT - Through governance layer
def process_query(query):
    from arifos_core.system.pipeline import run_governed_query
    verdict = run_governed_query(query)
    if verdict.status == "VOID":
        return {"error": "Query blocked by constitutional review"}
    return verdict.output
```

---

## Canon Index (v42)

**Master:** [canon/_INDEX/00_MASTER_INDEX_v42.md](canon/_INDEX/00_MASTER_INDEX_v42.md)

| Layer            | Canon                                                         | Spec                                      |
|------------------|---------------------------------------------------------------|-------------------------------------------|
| Foundation       | `canon/00_foundation/`                                        | —                                         |
| Floors (F1–F9)   | `canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v42.md`       | `spec/v42/constitutional_floors.json`     |
| Actors           | `canon/02_actors/`                                            | —                                         |
| Runtime          | `canon/03_runtime/`                                           | `spec/v42/pipeline.yaml`                  |
| Measurement      | `canon/04_measurement/04_GENIUS_LAW_v42.md`                   | `spec/v42/genius_law.json`                |
| Memory           | `canon/05_memory/`                                            | `spec/v42/cooling_ledger_phoenix.json`    |
| Paradox          | `canon/06_paradox/`                                           | —                                         |

---

## Nine Floors (Summary)

| #  | Floor       | Threshold | Type    | Quick Check                  |
|----|-------------|-----------|---------|------------------------------|
| F1 | Amanah      | LOCK      | Hard    | Reversible? Within mandate?  |
| F2 | Truth       | ≥0.99     | Hard    | Factually accurate?          |
| F3 | Tri-Witness | ≥0.95     | Hard    | Human–AI–Earth consensus?    |
| F4 | DeltaS      | ≥0        | Hard    | Reduces confusion?           |
| F5 | Peace²      | ≥1.0      | Soft    | Non-destructive?             |
| F6 | κᵣ          | ≥0.95     | Soft    | Serves weakest stakeholder?  |
| F7 | Ω₀          | 0.03-0.05 | Hard    | States uncertainty?          |
| F8 | G           | ≥0.80     | Derived | Governed intelligence?       |
| F9 | C_dark      | <0.30     | Derived | Dark cleverness contained?   |

Hard fail → VOID. Soft fail → PARTIAL.

---

## Verdict Hierarchy

```text
SABAR > VOID > 888_HOLD > PARTIAL > SEAL
```

**Python decides. Claude proposes.**

---

## Key Files for Common Tasks

### Governance Logic

- [arifos_core/APEX_PRIME.py](arifos_core/APEX_PRIME.py) — Constitutional judiciary
- [arifos_core/genius_metrics.py](arifos_core/genius_metrics.py) — G, C_dark, Psi computation
- [arifos_core/kernel.py](arifos_core/kernel.py) — Core kernel & entropy rot

### Floor Enforcement

- [arifos_core/floor_detectors/](arifos_core/floor_detectors/) — Python-sovereign floor detectors
- [arifos_core/enforcement/](arifos_core/enforcement/) — Enforcement orchestration

### Memory System

- [arifos_core/memory/policy.py](arifos_core/memory/policy.py) — Memory write policy
- [arifos_core/memory/bands.py](arifos_core/memory/bands.py) — 6-band implementation
- [cooling_ledger/L1_cooling_ledger.jsonl](cooling_ledger/L1_cooling_ledger.jsonl) — Audit trail

### Pipeline

- [arifos_core/system/pipeline.py](arifos_core/system/pipeline.py) — 000→999 pipeline
- [arifos_core/stages/](arifos_core/stages/) — Individual stage implementations

### Testing

- [tests/conftest.py](tests/conftest.py) — Pytest configuration & fixtures
- [tests/governance/](tests/governance/) — Governance-specific tests (proof-of-governance, merkle ledger, signatures)
- [tests/evidence/](tests/evidence/) — Evidence system tests (atomic ingestion, conflict routing, evidence packs)
- [tests/judiciary/](tests/judiciary/) — Judiciary tests (semantic firewall, witness council)
- [tests/temporal/](tests/temporal/) — Temporal governance tests (Phoenix-72, freshness, hold logic)
- [tests/integration/](tests/integration/) — Integration tests (memory bands, EUREKA policy, pipeline with memory)
- [tests/unit/](tests/unit/) — Unit tests for individual components

---

## Platform & Environment Notes

**Operating System:** Cross-platform (Windows, Linux, macOS)

- Trinity commands work on all platforms (see trinity.sh, trinity.ps1 wrappers)
- File paths use forward slashes in code, backslashes handled by pathlib

**Python Environment:**

- Virtual environment recommended (`.venv/` directory present)
- Package is editable-installed during development (`pip install -e .`)

**Key Scripts:**

- [scripts/trinity.py](scripts/trinity.py) — Universal Git governance CLI
- [demo_sealion_v45_full.py](demo_sealion_v45_full.py) — Full v45Ω demonstration
- [scripts/diagnose_v45_patches.py](scripts/diagnose_v45_patches.py) — Diagnostic tool for v45 patches

---

## Slash Commands (Legacy/Reference)

| Command | Purpose          |
|---------|------------------|
| `/000`  | Session init     |
| `/888`  | High-stakes hold |
| `/999`  | Session close    |
| `/g`    | GENIUS metrics   |
| `/s`    | SABAR trigger    |
| `/f`    | Floor check      |

---

## Important: File Integrity Protocol

**The "Janitor" Anti-Pattern is FORBIDDEN.** NEVER "clean up" or "simplify" files by removing sections. See [AGENTS.md:92](AGENTS.md#L92) for full rules.

### Mandatory Practices

- ✅ **APPEND** new sections (don't rewrite entire files)
- ✅ **Surgical edits** only (change specific lines, not whole files)
- ✅ **If new_tokens < old_tokens** → STOP and ask confirmation
- ❌ **No full file rewrites** that remove content
- ❌ **No new files** unless explicitly required (entropy control)
- ❌ **No "alias" or "compatibility" files** without explicit approval

### Entropy Control Rules

**Default:** Do not add new files. Only add a file if:

- Human explicitly requested it, OR
- Build/tests/runtime requires it, OR
- It reduces total entropy (removes duplication, replaces scattered docs)

**If a reference points to non-existent file:**

1. Search for the canonical existing file first
2. Prefer fixing the reference over creating a new file
3. If renaming/moving needed, stop and ask (avoid churn)

**Critical Implementation Details:**
- All file I/O must pass through FAG (File Access Governance) — direct `open()` is forbidden
- Every file read must generate a `FAGReceipt` for audit trail
- Memory writes are verdict-gated (SEAL → LEDGER, PARTIAL → PHOENIX, VOID → VOID band)
- Canon files in [L1_THEORY/canon/](L1_THEORY/canon/) are read-only; propose amendments via Phoenix-72

**Test Coverage Expectations:**
- Core governance modules must maintain 100% coverage
- All new floor detectors require corresponding tests in [tests/](tests/)
- Pipeline changes require both unit tests and integration tests
- Breaking changes to constitutional law trigger 888_HOLD (requires human approval)

---

## 888_HOLD Expanded Triggers

**MANDATORY HOLD** when any of these conditions are met:

### High-Stakes Operations

- Database operations (DROP, TRUNCATE, DELETE without WHERE)
- Production deployments
- Mass file changes (>10 files)
- Credential/secret handling
- Git history modification (rebase, force push)
- Dependency major version upgrades

### Evidence/Verification Failures (v41.2+)

- **H-USER-CORRECTION:** User corrects or disputes a constitutional claim
- **H-SOURCE-CONFLICT:** Conflicting evidence across source tiers (PRIMARY vs SECONDARY vs TERTIARY)
- **H-NO-PRIMARY:** Constitutional claim made without reading spec JSON
- **H-GREP-CONTRADICTS:** grep results contradict spec/canon patterns
- **H-RUSHED-FIX:** Proposing fixes based on <5 minutes audit

### 888_HOLD Action Sequence

When HOLD triggered:

1. **Declare:** "888_HOLD — [trigger type] detected"
2. **List conflicts:** Show PRIMARY vs SECONDARY vs TERTIARY sources
3. **Re-read PRIMARY:** Explicitly verify against spec JSON or SEALED canon
4. **Await instruction:** Wait for human approval before proceeding

---

## Critical Anti-Patterns (What NOT to Do)

1. **Do NOT create new files by default** — Only if human asks, build requires, or it reduces total entropy
2. **Do NOT "clean up" existing files** — Append, don't rewrite (violates File Integrity Protocol)
3. **Do NOT claim constitutional facts without reading PRIMARY sources** — Grep is discovery, not verification
4. **Do NOT generate code that bypasses governance** — All LLM calls must go through arifOS pipeline
5. **Do NOT create alias/compatibility files** — Fix the canonical reference instead
6. **Do NOT fabricate session steps** — Only include steps that actually ran (F2-CODE violation)
7. **Do NOT use magic numbers** — Use named constants (F4-CODE violation)
8. **Do NOT mutate inputs silently** — Pure functions only (F1-CODE violation)

---

For full governance details, see [AGENTS.md](AGENTS.md).

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.
