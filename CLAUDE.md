# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Version:** v45.0 (Phoenix-72 Consolidation) | **Track B:** spec/v45/ | **Safety Ceiling:** 99%

**Imports:** `~/.claude/CLAUDE.md` — Global governance (floors, SABAR, verdicts)
**Extends:** [AGENTS.md](AGENTS.md) — Full constitutional governance

**Important:** This file works in conjunction with [AGENTS.md](AGENTS.md), which contains additional governance rules including:
- File Integrity & ACLIP Protocol (never "clean up" files by removing sections)
- Entropy Control rules (when to add new files)
- Cooling Notes (agent learnings from past mistakes)

**Latest:**
- v45.0 Phoenix-72 Migration (2025-12-29) — Track A/B/C consolidation complete. See migration commit ff5ced3 for details.
- arifos_eval v45 Upgrade (2025-12-29) — Evaluation framework aligned with Phoenix-72 (v36.1Ω → v45.0). Commit 2eb64d1.

**Quick Links:**

- **[AGENTS.md](AGENTS.md)** — Full constitutional governance (extends this file)
- **[docs/ARCHITECTURE_AND_NAMING_v45.md](docs/ARCHITECTURE_AND_NAMING_v45.md)** — Complete architecture & naming standards (ONE canonical reference)
- **[spec/v45/](spec/v45/)** — Track B authority (constitutional thresholds with SHA-256 verification)
- **[archive/spec_v44/](archive/spec_v44/)** — v44 archive (complete with restoration procedures)
- **[.agent/workflows/](. agent/workflows/)** — Master skills registry (000, fag, gitforge)
- **[scripts/sealion_forge_repl.py](scripts/sealion_forge_repl.py)** — SEA-LION interactive testing (RAW vs GOVERNED)
- **[SECURITY.md](SECURITY.md)** — Security vulnerability reporting
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — How to propose amendments
- **[CHANGELOG.md](CHANGELOG.md)** — Version history and patches

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

### SEA-LION v4 Interactive Testing (v45Ω Patch B.2+)

**Three testing approaches for RAW vs GOVERNED comparison:**

```bash
# 1. RAW ONLY - Zero governance control group
python scripts/sealion_raw_only.py
# Pure SEA-LION API calls with ZERO arifOS imports
# Establishes ungoverned baseline for comparison

# 2. FORGE REPL - Full governed pipeline with dual-stream mode
python scripts/sealion_forge_repl.py
# Governed responses with 000→999 pipeline timeline
# /both - Side-by-side RAW vs GOVERNED comparison
# /verbose - Enable StageInspector (ARIFOS_VERBOSE=1)
# /stats - Session statistics

# 3. AUTOMATED VERIFICATION - 6-test governance suite
python scripts/verify_sealion_governance.py
# Tests: PHATIC (greetings), SOFT (educational), HARD (factual)
# Tests: REFUSE (harmful), IDENTITY (self-awareness), VERBOSITY (efficiency)
```

**Environment Setup:**

```bash
# Required API credentials (set ONE of these)
export SEALION_API_KEY="your-api-key"           # Primary
export ARIF_LLM_API_KEY="your-api-key"          # Alternative
export LLM_API_KEY="your-api-key"               # Alternative
export OPENAI_API_KEY="your-api-key"            # Alternative

# Optional configuration
export SEALION_MODEL="aisingapore/Gemma-SEA-LION-v4-27B-IT"  # Default model
export ARIF_LLM_API_BASE="https://api.sea-lion.ai/v1"        # Default API base
export ARIFOS_VERBOSE="1"                                     # Enable StageInspector

# Windows PowerShell:
$env:SEALION_API_KEY = "your-api-key"
$env:SEALION_MODEL = "aisingapore/Gemma-SEA-LION-v4-27B-IT"
$env:ARIFOS_VERBOSE = "1"
```

**Available SEA-LION Models:**

- `aisingapore/Gemma-SEA-LION-v4-27B-IT` (default - best quality)
- `aisingapore/Qwen-SEA-LION-v4-32B-IT` (larger context)
- `aisingapore/Llama-SEA-LION-v3-8B-IT` (faster, smaller)
- Vision variants: `8B-VL`, `4B-VL` (multimodal)

**What Gets Tested:**

1. **PHATIC Lane** - Greetings ("hi", "how are u?")
   - RAW: Verbose, over-analytical responses (500-1500 chars typical)
   - GOVERNED: Concise (≤100 chars), SEAL verdict
   - Verbosity penalty: >100 chars → PARTIAL

2. **SOFT Lane** - Educational/Explanatory queries
   - RAW: Ungoverned, may contain hallucinations
   - GOVERNED: Truth threshold 0.85-0.90, hallucination detection
   - Lane-aware Psi recomputation

3. **HARD Lane** - Factual/Critical queries
   - RAW: Ungoverned factual responses
   - GOVERNED: Truth threshold 0.90-0.99, strict verification
   - Tri-Witness validation

4. **REFUSE Lane** - Harmful/Dangerous queries
   - RAW: May comply with harmful requests
   - GOVERNED: VOID verdict, constitutional blocking

5. **IDENTITY Guard** - Self-awareness queries ("what is arifOS?")
   - RAW: May hallucinate or invent facts
   - GOVERNED: VOID if truth < 0.99, Anti-Hantu enforcement

6. **Verbosity Ceiling** - Efficiency testing
   - RAW: No constraints on response length
   - GOVERNED: PHATIC verbosity penalty (>100 chars for greetings)

**Comparing Results:**

```bash
# Example workflow
# 1. Establish RAW baseline
python scripts/sealion_raw_only.py
Raw> hi
# Observe: Verbose response (500-1500 chars typical)

# 2. Test GOVERNED version
python scripts/sealion_forge_repl.py
Forge> hi
# Observe: Concise response (≤100 chars), SEAL verdict, Trinity metrics

# 3. Run side-by-side comparison
Forge> /both
Forge> hi
# Observe: RAW (left) vs GOVERNED (right) with contrast metrics

# 4. Automated verification
python scripts/verify_sealion_governance.py
# Expected: 6/6 PASS (all lanes functioning correctly)
```

**Key Metrics Displayed (GOVERNED mode):**

- **Δ (Delta/Clarity)** - ΔS entropy change (≥0 required)
- **Ω (Omega/Empathy)** - κᵣ empathy score (≥0.95 for SEAL)
- **Ψ (Psi/Vitality)** - Lane-aware composite metric (≥1.0 ALIVE)
- **Truth** - Lane-specific threshold (0.80 SOFT, 0.90 HARD, 0.99 IDENTITY)
- **Verdict** - SEAL/PARTIAL/VOID/SABAR/888_HOLD

**v45Ω Patch B.2 Features:**

1. **Lane-Aware Psi Recomputation** - Truth thresholds adapt to query type
2. **PHATIC Verbosity Penalty** - First "quality ceiling" (not just safety floor)
3. **StageInspector** - 000→999 pipeline visibility with timing
4. **Cooling Ledger Integration** - All generations logged with lane metadata
5. **Dual-Stream Mode** - Real-time RAW vs GOVERNED comparison

**Troubleshooting:**

```bash
# API connection issues
python -c "import openai; print(openai.__version__)"  # Verify openai lib installed
pip install openai  # Install if missing

# Verify API key
python -c "import os; print('Key set:', bool(os.getenv('SEALION_API_KEY')))"

# Test connection
python scripts/sealion_raw_only.py
Raw> test
# If connection fails, check API_BASE and API_KEY

# Enable verbose logging
export ARIFOS_VERBOSE=1
python scripts/sealion_forge_repl.py
# Shows 000→999 stage transitions with timing
```

### Pipeline & CLI

```bash
# Run the governed pipeline demo
python -m arifos_core.system.pipeline

# SEA-LION v4 Interactive Testing (v45Ω Patch B.2)
python scripts/sealion_full_interactive.py     # Full pipeline RAW vs GOVERNED
python scripts/verify_sealion_governance.py    # Automated 6-test verification suite

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

# MCP Server (IDE Integration - VS Code, Cursor, etc.)
python scripts/arifos_mcp_entry.py
# Provides: arifos_judge, arifos_recall, arifos_audit, arifos_fag_read tools

# MCP Server Setup for VS Code/Cursor:
# Add to .vscode/settings.json or workspace settings:
# {
#   "mcp.servers": {
#     "arifos": {
#       "command": "python",
#       "args": ["scripts/arifos_mcp_entry.py"],
#       "env": {
#         "ARIFOS_LOG_LEVEL": "INFO"
#       }
#     }
#   }
# }

# Full v45 Demo (after file reorganization - v45 migration)
python L6_SEALION/tests/demo_sealion_v45_full.py    # Complete ΔΩΨ Trinity demonstration
```

---

## Quick Start for New Developers

**First time here? Run this sequence:**

```bash
# 1. Clone and install
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
pip install -e ".[dev]"

# 2. Verify installation
pytest -x  # Run tests (stop on first error)

# 3. Explore core governance
python -m arifos_core.system.pipeline  # See 000→999 pipeline demo

# 4. Read the constitution
# Windows:
type AGENTS.md  # Full governance guide
# Unix/Linux/Mac:
cat AGENTS.md   # Full governance guide
```

### Verify Installation & Health

**Quick health check (run after installation):**
```bash
# 1. Verify package installed
pip show arifos

# 2. Check imports work
python -c "from arifos_core.system.apex_prime import judge_output; print('✓ Core imports OK')"

# 3. Run smoke test (5 quick tests)
pytest tests/test_apex_prime_floors.py -k "seal_verdict or void_verdict" -v

# 4. Verify ledger chain
arifos-verify-ledger

# Expected: All pass ✓
```

### Platform-Specific Commands

**Windows (PowerShell):**
```powershell
# Read constitution
Get-Content AGENTS.md

# Run tests with specific file
pytest tests\test_apex_genius_verdicts.py -v

# Run specific test function
pytest tests\test_apex_genius_verdicts.py::test_seal_verdict -v

# Trinity commands (cross-platform via Python)
python scripts\trinity.py forge main
python scripts\trinity.py qc main
```

**Unix/Linux/Mac (Bash):**
```bash
# Read constitution
cat AGENTS.md

# Run tests with specific file
pytest tests/test_apex_genius_verdicts.py -v

# Run specific test function
pytest tests/test_apex_genius_verdicts.py::test_seal_verdict -v

# Trinity commands (native shell scripts)
./trinity.sh forge main
./trinity.sh qc main
```

Then proceed to Architecture Overview below.

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

L6_SEALION/            # SEA-LION LLM integration layer (v45 migration - Dec 2025)
├── integrations/      # LLM adapter implementations
│   └── sealion/       # SEA-LION-specific adapters
└── tests/             # SEA-LION governance test suite
    ├── demo_sealion_v45_full.py      # Full ΔΩΨ Trinity demo
    ├── sealion_full_suite_v45.py     # Evaluation harness
    └── test_sealion_*.py             # Integration tests

L7_DEMOS/              # Integration examples & demos (v45 migration - Dec 2025)
└── examples/          # Framework integrations & use cases
    ├── autogen_arifos_governor/      # AutoGen multi-agent governance
    ├── langchain_arifos_guarded/     # LangChain RAG governance
    ├── llamaindex_arifos_truth/      # LlamaIndex truth verification
    ├── langgraph_minimal/            # LangGraph integration
    ├── arifos_caged_*.py             # Caged LLM demos (OpenAI, Gemini)
    ├── test_*.py                     # Specific feature demos
    └── demo_*.py                     # General demonstrations

scripts/               # Governance utilities (reduced from 51 to ~10 files - Dec 2025)
├── trinity.py                        # Universal Git governance CLI
├── phoenix_72_guardrail.py           # Constitutional drift detector
├── diagnose_v45_patches.py           # v45 diagnostic tool
├── analyze_governance.py             # Audit analyzer
├── verify_ledger_*.py                # Ledger verifiers
└── arifos_mcp_entry.py               # MCP server entry point
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

1. `spec/v44/*.json` — Constitutional floors, GENIUS law, thresholds (Track B with SHA-256 manifest)
2. `L1_THEORY/canon/*_v45.md` with SEALED status — Canonical law

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

## Tool Selection Guide (Efficient Usage)

**Critical:** Every tool call + results consumes tokens. Sub-agents (Task tool) multiply context usage 3-5x vs direct tools.

### Quick Decision Tree: When to Use Which Tool

| Scenario | Tool | Reason |
|----------|------|--------|
| Know exact file path | `Read` directly | Fast, minimal tokens |
| Know search pattern | `Grep` or `Glob` directly | Efficient, targeted |
| Need multi-file context | `Task` with Explore agent | Handles complexity |
| Verifying constitutional claim | `Read` PRIMARY source | Never delegate verification |
| Simple 1-2 file operation | Direct tools | Avoid sub-agent overhead |

### ✅ USE Task Tool (Explore) When:

- **Multi-file context needed**: "Understand how authentication works" (spans 5+ files)
- **Open-ended exploration**: "Find all error handling patterns"
- **Complex codebase questions**: "How do the 9 floors interact with the pipeline?"
- **Research before implementation**: Gather context before planning

### ❌ DON'T Use Task Tool When:

- **You know the exact file**: Use `Read` directly for `spec/v45/constitutional_floors.json`
- **Simple grep needed**: Use `Grep` for "find all usages of apex_review"
- **File listing**: Use `Glob` for `**/*.json` pattern matching
- **Context already filled (>50%)**: Task tool adds significant token overhead

**Decision rule:** If you can answer with 1-2 direct tool calls, don't spawn a sub-agent.

**arifOS-specific:** For constitutional verification (PRIMARY sources), always `Read` the spec file directly—never delegate to sub-agent. Verification cannot be proxied.

---

## Development Workflows

### Adding a New Floor Detector

1. Create detector in [arifos_core/floor_detectors/](arifos_core/floor_detectors/)
2. Implement `detect()` method returning score 0.0-1.0
3. Add to floor registry in [arifos_core/enforcement/](arifos_core/enforcement/)
4. Update spec in [spec/v44/constitutional_floors.json](spec/v44/constitutional_floors.json)
5. Add tests in [tests/test_*.py](tests/)
6. Update canon docs in [L1_THEORY/canon/01_floors/](L1_THEORY/canon/01_floors/)
7. Regenerate manifest: `python scripts/regenerate_manifest_v45.py`

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

3. Update spec files in [spec/v44/](spec/v44/) first
4. Update code in [arifos_core/](arifos_core/) to match spec
5. Regenerate SHA-256 manifest:

   ```bash
   python scripts/regenerate_manifest_v45.py
   ```

6. Run alignment tests:

   ```bash
   pytest tests/test_*_v38_alignment.py -v
   ```

7. Verify spec integrity:

   ```bash
   python scripts/regenerate_manifest_v45.py --check
   pytest tests/test_spec_v44_schema_enforcement_subprocess.py -v
   ```

8. Request human seal via `arifos-seal-canon`

### Track B Spec Integrity (v44+)

arifOS v44 introduces cryptographic spec verification via SHA-256 manifests.

**Strict Mode (default):**
- All specs must match MANIFEST.sha256.json hashes
- JSON Schema validation enforced at load-time
- Environment variable spec overrides restricted to spec/v44/ directory
- Tampered specs trigger RuntimeError (fail-closed)

**3-Command Audit (for CI/CD or manual verification):**
```bash
# 1. Verify manifest hashes match current files
python scripts/regenerate_manifest_v45.py --check

# 2. Test schema enforcement (load-time validation)
pytest tests/test_spec_v44_schema_enforcement_subprocess.py -v

# 3. Test manifest enforcement (subprocess proof)
pytest tests/test_spec_v44_manifest_enforcement_subprocess.py -v
```

**Expected output (if integrity OK):**
```
[SUCCESS] All 8 files match manifest.
Spec integrity verified. No tampering detected.
Exit code: 0
```

**If tampered:**
```
[ERROR] Hash mismatch detected!
File: spec/v44/constitutional_floors.json
Expected: abc123...
Actual: def456...
Exit code: 1
```

See [spec/v44/SEAL_CHECKLIST.md](spec/v44/SEAL_CHECKLIST.md) for full audit procedures and strict vs legacy mode details.

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

## Canon Index (v42 Law + v44 Spec)

**Master:** [L1_THEORY/canon/_INDEX/00_MASTER_INDEX_v45.md](L1_THEORY/canon/_INDEX/00_MASTER_INDEX_v45.md)

| Layer            | Canon (v42 Law)                                               | Spec (v44 Track B)                        |
|------------------|---------------------------------------------------------------|-------------------------------------------|
| Foundation       | `L1_THEORY/canon/00_foundation/`                              | —                                         |
| Floors (F1–F9)   | `L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md` | `spec/v45/constitutional_floors.json` |
| Actors           | `L1_THEORY/canon/02_actors/`                                  | —                                         |
| Runtime          | `L1_THEORY/canon/03_runtime/`                                 | `spec/v45/session_physics.json`           |
| Measurement      | `L1_THEORY/canon/04_measurement/030_GENIUS_LAW_v45.md`         | `spec/v45/genius_law.json`                |
| Memory           | `L1_THEORY/canon/05_memory/`                                  | `spec/v45/cooling_ledger_phoenix.json`    |
| Paradox          | `L1_THEORY/canon/06_paradox/`                                 | —                                         |
| Policy           | —                                                             | `spec/v45/policy_text.json`               |
| Red Patterns     | —                                                             | `spec/v45/red_patterns.json`              |
| WAW Prompts      | —                                                             | `spec/v45/waw_prompt_floors.json`         |

**Note:** v42 = canonical law (immutable philosophy), v45 = tunable thresholds (Track B with SHA-256 manifest)

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

- [arifos_core/system/apex_prime.py](arifos_core/system/apex_prime.py) — Constitutional judiciary (888 JUDGE)
- [arifos_core/enforcement/genius_metrics.py](arifos_core/enforcement/genius_metrics.py) — G, C_dark, Psi computation
- [arifos_core/enforcement/metrics.py](arifos_core/enforcement/metrics.py) — Floor metrics (ξ, ΔS, Peace², κᵣ, Ω₀)

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
- [L6_SEALION/tests/demo_sealion_v45_full.py](L6_SEALION/tests/demo_sealion_v45_full.py) — Full v45Ω demonstration
- [scripts/diagnose_v45_patches.py](scripts/diagnose_v45_patches.py) — Diagnostic tool for v45 patches
- [L7_DEMOS/examples/](L7_DEMOS/examples/) — Integration demos (LangChain, Autogen, LlamaIndex, caged LLMs)

### Recent File Reorganization (v45 Migration - December 2025)

**Entropy Reduction:** scripts/ directory was reduced from 51 files to ~10 files (80% reduction).

**What Changed:**

- **SEA-LION files** moved from `scripts/` → `L6_SEALION/tests/`
  - Examples: `demo_sealion_v45_full.py`, `sealion_full_suite_v45.py`, all `test_sealion_*.py`
- **Demo/integration files** moved from `scripts/` → `L7_DEMOS/examples/`
  - Examples: `arifos_caged_*.py`, `test_waw_signals.py`, framework demos (AutoGen, LangChain, LlamaIndex)
- **Governance utilities** remained in `scripts/`
  - Examples: `trinity.py`, `phoenix_72_guardrail.py`, `verify_ledger_*.py`, `arifos_mcp_entry.py`

**Why This Matters:**

- Old references to `scripts/demo_*.py` or `scripts/test_sealion_*.py` need path updates
- Import paths may have changed for moved files
- Use `L6_SEALION/tests/` for SEA-LION-specific tests
- Use `L7_DEMOS/examples/` for integration demonstrations
- See [MIGRATION_PLAN.md](MIGRATION_PLAN.md) and [MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md) for full details

---

## Common Issues & Debugging

### Import Errors After Installation
```bash
# Verify installation
pip show arifos

# Check package location
python -c "import arifos_core; print(arifos_core.__file__)"

# Reinstall in editable mode
pip uninstall arifos
pip install -e ".[dev]"
```

### Test Failures
```bash
# Run single test with verbose output
pytest tests/test_apex_prime_floors.py::test_seal_verdict -vv

# Run with full traceback
pytest tests/test_apex_genius_verdicts.py -vv --tb=long

# Check for missing dependencies
pip install -e ".[dev,yaml,api,litellm]"
```

### Ledger Verification Failures
```bash
# Rebuild ledger hashes
arifos-build-ledger-hashes

# Verify integrity
arifos-verify-ledger

# Show specific entry proof
arifos-show-merkle-proof --index 0
```

### MCP Server Issues
```bash
# Test MCP server directly
python scripts/arifos_mcp_entry.py

# Check MCP tool availability in VS Code:
# Open Command Palette → "MCP: List Tools"
# Should show: arifos_judge, arifos_recall, arifos_audit, arifos_fag_read
```

### Spec Integrity Errors
```bash
# Check for tampered specs (v44 Track B)
python scripts/regenerate_manifest_v45.py --check

# If hash mismatch detected, restore from git:
git checkout spec/v44/

# Regenerate manifest after legitimate changes:
python scripts/regenerate_manifest_v45.py
```

### Windows-Specific Issues
```powershell
# Path issues: use forward slashes in Python, backslashes in PowerShell
python -c "from pathlib import Path; print(Path('spec/v44/constitutional_floors.json').exists())"

# Virtual environment activation
.venv\Scripts\Activate.ps1
```

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
- ❌ **No Local Duplicate Governance:** Do not duplicate Metrics or Apex logic in local adapters. Import from `arifos_core`.

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
- Spec changes (v44 Track B) require manifest regeneration and integrity tests
- Current test count: 2581/2581 (100%) as of 2025-12-26

---

## Transparency Mandate (The StageInspector)

Any new integration MUST support the **000→999 StageInspector** interface.
- **Requirement:** The "Guts" of the pipeline (verdicts, floor scores, lane decisions) must be visible for audit.
- **Implementation:** Return `AuditReceipt` or full `metadata` dict.
- **Goal:** White-box governance only. No black boxes.

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

## Clarification Protocol (Ask Before Execute)

**When to ASK user before proceeding:**

| Situation | Example | Protocol |
|-----------|---------|----------|
| **Ambiguous requirement** | "Improve performance" | Ask: Which metric? What's acceptable trade-off? |
| **Multiple valid approaches** | "Add caching" | Ask: Redis vs in-memory vs file-based? |
| **High-risk change** | "Refactor pipeline" | Show plan, get explicit approval before execution |
| **Constitutional impact** | "Change F2 threshold" | 888_HOLD → Explain rationale, await decision |
| **Entropy risk** | "Need 15 new files" | Ask: Can we reduce? What gets archived/deleted? |
| **Large scope** | "Modify >10 files" | Confirm scope and approach before starting |

**Default stance:** When uncertain, ASK. Don't assume user intent.

**arifOS rule:** Phoenix-72 amendments (constitutional changes) ALWAYS require explicit human approval. Never proceed with constitutional modifications without clear "yes, proceed" confirmation.

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

## Context Management & Session Hygiene

**Critical:** Claude Code's effective context window degrades significantly as it fills. Performance drops sharply after ~50-60% capacity.

### Check Context Before Complex Tasks

Use `/context` command to check current usage:

- **<40%:** Proceed normally with any task
- **40-60%:** Consider `/compact` to reduce context
- **>60%:** Recommend starting fresh conversation for complex work

**Why this matters:** Reasoning quality, tool selection accuracy, and constitutional compliance degrade when context is saturated. Complex refactors or multi-file changes should start with clean context.

### Session Checkpoints

| Checkpoint | Trigger | Action |
|------------|---------|--------|
| **Compact** | Context 40-60% | Use `/compact` to reduce context size |
| **Fresh Start** | Context >60% OR major task switch | Start new conversation, summarize state |
| **Rewind** | Wrong direction taken | Use `Esc+Esc` to backtrack recent steps |
| **Review** | Before >5 file changes | Pause, show `git diff`, get explicit approval |

### Token Cost Awareness

- Every tool call + results consumes tokens (both request and response)
- Agent loops (Task tool) accumulate context rapidly (3-5x multiplier)
- MCP servers add tool definitions upfront (context overhead even before use)
- Long sessions accumulate "dead weight" from completed tasks

**Best practice for arifOS:** For constitutional changes (Track A/B modifications), start fresh conversation after research/planning phase complete. Execute implementation in clean context with full reasoning capacity available.

---

## Quick Navigation (For New Claude Instances)

**Just cloned this repo?** Start here:
1. Read [Quick Start for New Developers](#quick-start-for-new-developers) (line 272)
2. Run health check: `pip install -e ".[dev]" && pytest -x`
3. Understand governance: Read [Nine Floors Summary](#nine-floors-summary) (line 708)
4. Review architecture: [docs/ARCHITECTURE_AND_NAMING_v45.md](docs/ARCHITECTURE_AND_NAMING_v45.md) (complete standards)
5. Check platform commands: [Platform-Specific Commands](#platform-specific-commands) (line 314)

**Working on specific task?** Jump to:
- Testing: [Testing](#testing) (line 53)
- Pipeline: [Pipeline & CLI](#pipeline--cli) (line 216)
- Development: [Development Workflows](#development-workflows) (line 481)
- Debugging: [Common Issues & Debugging](#common-issues--debugging) (line 814)

**Making constitutional changes?** Read:
- [Source Verification Protocol](#source-verification-protocol) (line 435)
- [Modifying Constitutional Law](#modifying-constitutional-law) (line 502)
- [888_HOLD Expanded Triggers](#888_hold-expanded-triggers) (line 950)

**Key principle:** Never modify canon directly. Propose amendments via Phoenix-72. Read PRIMARY sources (spec/v45/*.json) before making constitutional claims.

---

For full governance details, see [AGENTS.md](AGENTS.md).

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.
