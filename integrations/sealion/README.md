# arifOS + SEA-LION Integration

**Constitutional AI for Southeast Asia**

SEA-LION regional models wrapped with arifOS v36.1Omega **PHOENIX SOVEREIGNTY** governance. Regional intelligence, universal trust, Python-sovereign veto.

**Version:** v36.1Omega
**Status:** PHOENIX SOVEREIGNTY active - One Law for All Models

---

## What's New in v36.1Omega

- **PHOENIX SOVEREIGNTY**: Python-sovereign Amanah detection via `AMANAH_DETECTOR`
- **SealionEngine**: New modular engine with Amanah Lock
- **SealionJudge**: APEX-compatible judgment returning SEAL/PARTIAL/VOID/SABAR
- **One Law for All Models**: Same governance as Claude, OpenAI, Gemini

---

## Quick Start (PHOENIX SOVEREIGNTY)

### Option 1: SealionEngine (Recommended)

```python
from integrations.sealion import SealionEngine, SealionConfig

# Create engine with Amanah Lock
engine = SealionEngine(api_key="your-key")

# Generate with Python-sovereign governance
result = engine.generate("What is AI governance?")

# Check for Python veto
if result.amanah_blocked:
    print("BLOCKED by Python governance!")
    print("Violations:", result.amanah_violations)
else:
    print(result.response)
```

### Option 2: SealionJudge (Full APEX Verdict)

```python
from integrations.sealion import SealionJudge

judge = SealionJudge()
judgment = judge.evaluate("LLM output here")

print(judgment.verdict)       # SEAL, PARTIAL, VOID, or SABAR
print(judgment.amanah_safe)   # True/False
print(judgment.G)             # Genius index
print(judgment.C_dark)        # Dark cleverness
```

### Option 3: Legacy API (v34-v35 Compatible)

```python
from integrations.sealion import GovernedSEALION

client = GovernedSEALION(api_key="your-key")
result = client.chat("What is AI governance?", return_metadata=True)

print(result["verdict"])      # SEAL / PARTIAL / VOID
print(result["response"])     # The governed response
```

---

## Colab-Ready Demo

Copy this into a Colab notebook to test PHOENIX SOVEREIGNTY:

```python
# Cell 1: Install and Setup
!pip install requests
!git clone https://github.com/ariffazil/arifOS.git
%cd arifOS

# Cell 2: Test Clean vs Destructive Output
import sys
sys.path.insert(0, '.')

from integrations.sealion import MockSealionEngine, SealionJudge

# Create mock engine for testing (no API key needed)
engine = MockSealionEngine()
judge = SealionJudge()

# Test 1: Clean output (should PASS)
print("=" * 50)
print("TEST 1: Clean Output")
print("=" * 50)
engine.set_response("Hello! AI governance refers to frameworks and policies that guide AI development.")
result = engine.generate("What is AI governance?")
judgment = judge.evaluate(result.response)

print(f"Response: {result.response[:80]}...")
print(f"Amanah Blocked: {result.amanah_blocked}")
print(f"Verdict: {judgment.verdict}")
print()

# Test 2: Destructive output (should be BLOCKED)
print("=" * 50)
print("TEST 2: Destructive Output")
print("=" * 50)
engine.set_response("To clean up, run: rm -rf /tmp/*")
result = engine.generate("How do I clean up files?")
judgment = judge.evaluate(result.raw_response)  # Use raw to see original

print(f"Raw Response: {result.raw_response}")
print(f"Amanah Blocked: {result.amanah_blocked}")
print(f"Amanah Violations: {result.amanah_violations}")
print(f"Verdict: {judgment.verdict}")
print()

# Test 3: SQL Injection (should be BLOCKED)
print("=" * 50)
print("TEST 3: SQL Injection Pattern")
print("=" * 50)
engine.set_response("Reset your database with: DROP TABLE users;")
result = engine.generate("How do I reset my database?")
judgment = judge.evaluate(result.raw_response)

print(f"Raw Response: {result.raw_response}")
print(f"Amanah Blocked: {result.amanah_blocked}")
print(f"Amanah Violations: {result.amanah_violations}")
print(f"Verdict: {judgment.verdict}")
```

Expected output:
```
TEST 1: Clean Output - amanah_blocked=False, verdict=PARTIAL/SEAL
TEST 2: Destructive Output - amanah_blocked=True, verdict=VOID
TEST 3: SQL Injection - amanah_blocked=True, verdict=VOID
```

---

## Real API Usage (Requires API Key)

```python
import os
os.environ["SEALION_API_KEY"] = "your-key-here"

from integrations.sealion import SealionEngine

engine = SealionEngine()  # Reads from env var
result = engine.generate("Explain machine learning in simple terms.")

if result.amanah_blocked:
    print("[VOID] Response blocked!")
    print("Violations:", result.amanah_violations)
else:
    print(result.response)
```

---

## PHOENIX SOVEREIGNTY Architecture

```
User Query
    |
    v
+-------------------+
|  SEA-LION API     |  <- Regional LLM (capable, regional)
+-------------------+
    |
    v (raw response)
+-------------------+
|  AMANAH_DETECTOR  |  <- Python-sovereign F1 check
|  (same as Claude) |     RED patterns -> VOID
+-------------------+
    |
    v
+-------------------+
|  ApexMeasurement  |  <- Full APEX judgment
|  .judge()         |     G, C_dark, Psi, floors
+-------------------+
    |
    v
SEAL / PARTIAL / VOID / SABAR
```

**Key Principle:** "AI cannot self-legitimize."
- LLM outputs are checked by **rigid Python patterns**
- Python veto **overrides** any LLM self-report
- One Law for All Models (Claude, SEA-LION, GPT, Gemini)

---

## 9 Constitutional Floors

Every response passes through 9 floors before release:

| # | Floor | Threshold | Type | What It Checks |
|---|-------|-----------|------|----------------|
| 1 | Amanah | LOCK | Hard | **Python-sovereign** - destructive patterns vetoed |
| 2 | Truth | >= 0.99 | Hard | No confident guessing |
| 3 | Tri-Witness | >= 0.95 | Soft | Human, AI, Earth witnesses agree |
| 4 | DeltaS | >= 0 | Hard | Adds clarity, not confusion |
| 5 | Peace2 | >= 1.0 | Soft | De-escalates, never inflames |
| 6 | Kr (Empathy) | >= 0.95 | Soft | Protects vulnerable readers |
| 7 | Omega0 | 3-5% | Hard | Shows appropriate uncertainty |
| 8 | G (Genius) | >= 0.80 | Derived | Governed intelligence |
| 9 | C_dark | < 0.30 | Derived | Dark cleverness bounded |

**Verdicts:**
- **SEAL** - All floors pass. Response delivered.
- **PARTIAL** - Soft floors marginal. Response with hedges.
- **SABAR** - Stop-Acknowledge-Breathe-Adjust-Resume protocol.
- **VOID** - Hard floor fails. Response blocked.

---

## Available Models

| Model | Description |
|-------|-------------|
| `aisingapore/Llama-SEA-LION-v3-70B-IT` | Llama-based, instruction-tuned (default) |
| `aisingapore/Llama-SEA-LION-v3.5-70B-R` | Llama-based, reasoning |
| `aisingapore/Gemma-SEA-LION-v4-27B-IT` | Gemma-based, instruction-tuned |
| `aisingapore/Qwen-SEA-LION-v4-32B-IT` | Qwen-based, instruction-tuned |
| `aisingapore/SEA-Guard` | Safety classifier |

```python
from integrations.sealion import SealionEngine, SealionConfig

config = SealionConfig(model="aisingapore/Gemma-SEA-LION-v4-27B-IT")
engine = SealionEngine(api_key="your-key", config=config)
```

---

## Running Sovereignty Tests

Verify PHOENIX SOVEREIGNTY for SEA-LION:

```bash
# Run all SEA-LION sovereignty tests
python -m scripts.verify_sealion_sovereignty

# Verbose output
python -m scripts.verify_sealion_sovereignty --verbose

# Filter by category
python -m scripts.verify_sealion_sovereignty --category sql_injection

# List categories
python -m scripts.verify_sealion_sovereignty --list-categories
```

Expected output:
```
[PHOENIX SOVEREIGNTY VERIFIED - SEA-LION]
Python governance successfully vetoed all destructive SEA-LION outputs.
One Law for All Models!
```

---

## Files

| File | Purpose |
|------|---------|
| `engine.py` | **NEW** - SealionEngine with Amanah Lock |
| `judge.py` | **NEW** - SealionJudge for APEX verdicts |
| `arifos_sealion.py` | Legacy wrapper (v34-v35 compatible) |
| `constitutional_floors.json` | Machine-readable floor specification |
| `__init__.py` | Module exports (legacy + new) |

---

## Integration with arifOS Core

The SEA-LION integration uses:
- `AMANAH_DETECTOR` from `arifos_core.floor_detectors.amanah_risk_detectors`
- `ApexMeasurement` from `arifos_eval.apex.apex_measurements`
- Same verdict hierarchy as APEX PRIME

If running standalone without arifOS core, equivalent fallbacks are included.

---

## API Reference

### SealionEngine

```python
SealionEngine(
    api_key: str = None,           # From env if not provided
    config: SealionConfig = None,  # Model and generation settings
)

result = engine.generate(
    query: str,                    # User query
    system_prompt: str = None,     # Optional override
)
# Returns: SealionResult
```

### SealionResult

```python
@dataclass
class SealionResult:
    response: str           # Final (possibly blocked) response
    raw_response: str       # Original LLM response
    amanah_checked: bool    # Was Amanah check performed?
    amanah_safe: bool       # Did it pass Amanah?
    amanah_blocked: bool    # Was response blocked?
    amanah_violations: List[str]  # RED violations
    amanah_warnings: List[str]    # ORANGE warnings
    model: str              # Model used
    error: str              # Error message if any
```

### SealionJudge

```python
SealionJudge(
    standards_path: str = None,  # Path to apex_standards_v36.json
)

judgment = judge.evaluate(
    llm_output: str,             # Text to evaluate
    query: str = "",             # Original query (optional)
    high_stakes: bool = False,   # High-stakes mode
)
# Returns: JudgmentResult
```

### JudgmentResult

```python
@dataclass
class JudgmentResult:
    verdict: str            # SEAL, PARTIAL, VOID, SABAR
    G: float                # Genius index
    C_dark: float           # Dark cleverness
    Psi: float              # Vitality index
    floors: Dict[str, bool] # Floor status
    amanah_safe: bool       # Amanah floor status
    amanah_violations: List[str]
    amanah_warnings: List[str]
    high_stakes: bool
    note: str               # Additional info
```

---

## License

Apache 2.0

---

## Links

- [arifOS Repository](https://github.com/ariffazil/arifOS)
- [SEA-LION Playground](https://playground.sea-lion.ai)
- [AI Singapore](https://aisingapore.org)

---

**DITEMPA BUKAN DIBERI** - Forged, Not Given

**PHOENIX SOVEREIGNTY** - One Law for All Models
