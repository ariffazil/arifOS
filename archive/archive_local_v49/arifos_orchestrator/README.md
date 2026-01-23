# arifOS Multi-Agent Orchestrator

**Constitutional governance orchestration system** synchronizing Claude (reasoning), ChatGPT Codex (generation), and AntiGravity (validation).

**Status:** MVP v0.1.0 (Python CLI)
**Integration:** Standalone (arifOS kernel integration planned for v2)

---

## Architecture

```
┌─────────────────────────────────────────┐
│         arifOS Orchestrator             │
│   (Constitutional Governance Layer)      │
└──────────────┬──────────────────────────┘
               │
       ┌───────┼───────┐
       │               │
   ┌───▼───┐       ┌───▼────┐
   │Claude │       │ Codex  │
   │(Truth)│       │(Code)  │
   └───┬───┘       └───┬────┘
       │               │
       └───────┬───────┘
               │
         ┌─────▼──────┐
         │AntiGravity │
         │(Validation)│
         └────────────┘
```

### Agents

1. **Claude Agent** (Reasoning/Truth)
   - Floors 1-2 enforcement (Amanah & Truth)
   - Model: claude-3-5-sonnet-20241022
   - Constitutional reasoning layer

2. **Codex Agent** (Code Generation)
   - Production code generation
   - Model: gpt-4o
   - Grounded in Claude's truth layer

3. **AntiGravity Agent** (Validation)
   - Symbolic/heuristic validation
   - Status: **ESTIMATE ONLY**
   - Confidence: ω₀ = 0.04 (humility band midpoint)

---

## Installation

```bash
# 1. Clone or navigate to arifOS repository
cd arifOS

# 2. Install dependencies
pip install anthropic openai

# 3. Set API keys
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"

# Windows PowerShell:
$env:ANTHROPIC_API_KEY = "your-anthropic-key"
$env:OPENAI_API_KEY = "your-openai-key"
```

---

## Usage

### CLI

```bash
# Basic usage
python -m arifos_orchestrator "How does thermodynamic AI reduce hallucination?"

# With context
python -m arifos_orchestrator "Explain entropy reduction" --context "User: Arif Fazil"

# Quiet mode (only show verdict)
python -m arifos_orchestrator "Query here" --quiet

# Provide API keys explicitly
python -m arifos_orchestrator "Query" --claude-key "sk-ant-..." --openai-key "sk-..."
```

### Python API

```python
from arifos_orchestrator.core.orchestrator import run_orchestration, pretty_print_result

result = run_orchestration(
    query="How does arifOS enforce constitutional floors?",
    context="User: Developer"
)

pretty_print_result(result)

# Access individual components
claude_response = result['claude']['response']
codex_code = result['codex']['code']
verdict = result['verdict']  # SEAL / PARTIAL / VOID
```

---

## Output Structure

```python
{
    "query": "...",
    "context": "...",
    "claude": {
        "response": "...",  # Constitutional analysis
        "model": "claude-3-5-sonnet-20241022",
        "usage": {"input_tokens": ..., "output_tokens": ...}
    },
    "codex": {
        "code": "...",  # Generated code
        "language": "python",
        "model": "gpt-4o",
        "usage": {"total_tokens": ...}
    },
    "antigravity": {
        "validation": {
            "claude_truth_valid": true/false,
            "codex_aligned": true/false,
            "entropy_reduced": 0.04,
            "confidence": 0.04,
            "estimate_only": true
        },
        "code_validation": {
            "valid": true/false,
            "passed_rules": ...,
            "failed_rules": ...,
            "verdict": "SEAL" / "PARTIAL" / "VOID"
        }
    },
    "verdict": "SEAL" / "PARTIAL" / "VOID",
    "metadata": {...}
}
```

---

## Verdicts

| Verdict | Meaning | Exit Code |
|---------|---------|-----------|
| **SEAL** | All checks passed, output safe | 0 |
| **PARTIAL** | Minor warnings, proceed with caution | 1 |
| **VOID** | Critical failures, output rejected | 2 |

---

## Examples

```bash
# Example 1: Basic query
python -m arifos_orchestrator "What is constitutional AI governance?"

# Example 2: Code generation
python -m arifos_orchestrator "Write a function to validate thermodynamic constraints"

# Example 3: Run example script
python arifos_orchestrator/examples/basic_orchestration.py
```

---

## Limitations (MVP v0.1.0)

**ESTIMATE ONLY:**
- AntiGravity uses symbolic validation (regex/heuristics)
- Not integrated with arifOS kernel
- No cooling ledger logging
- No Merkle-proof audit trail

**Deferred to v2:**
- arifOS pipeline integration (000→999)
- Cooling ledger audit trail
- Semantic AntiGravity validation
- VS Code extension

---

## Testing

```bash
# Run all tests
pytest arifos_orchestrator/tests/ -v

# Run specific test
pytest arifos_orchestrator/tests/test_claude_agent.py -v

# Run integration tests
pytest arifos_orchestrator/tests/integration/ -v
```

---

## Development

```bash
# Install dev dependencies
pip install pytest pytest-mock

# Run tests with coverage
pytest --cov=arifos_orchestrator

# Lint
ruff check arifos_orchestrator/

# Format
black arifos_orchestrator/
```

---

## Constitutional Compliance

### F1 (Amanah - Integrity)
- ✅ API keys from environment (not hardcoded)
- ✅ No irreversible operations
- ✅ Error handling throughout

### F2 (Truth)
- ✅ Claude enforces truth (Floors 1-2)
- ✅ AntiGravity marked "Estimate Only"

### F7 (Ω₀ - Humility)
- ✅ Confidence capped at 0.04 (humility band)
- ✅ Limitations documented

### F9 (Human Authority)
- ✅ No auto-execution of generated code
- ✅ User triggers orchestration explicitly

---

## Roadmap

**v0.2.0:** Semantic AntiGravity validation
**v0.3.0:** arifOS kernel integration
**v0.4.0:** VS Code extension
**v1.0.0:** Full production release

---

**DITEMPA BUKAN DIBERI** — Forged, not given.

arifOS Project | Constitutional Governance for AI
https://github.com/ariffazil/arifOS
