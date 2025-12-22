# arifOS + SEA-LION Integration

**Constitutional AI for Southeast Asia**

SEA-LION regional models wrapped with arifOS v44.0 governance. Regional intelligence, universal trust, Python-sovereign veto.

**Version:** v44.0.0 (TEARFRAME)
**Status:** GOLD - Constitutionally Validated Production
**Layer:** L7 (SEA-LION Federation)

---

## What's New in v41.0

- **SGToxicGuard Spin Test**: 14/14 multilingual toxicity vectors PASS
- **Dual Detector Architecture**: F1 (Amanah) + F9 (Toxicity) complementary enforcement
- **APEX PRIME Public Contract**: `{verdict, apex_pulse, response, reason_code}`
- **LiteLLM Integration**: Use SEA-LION via standard OpenAI-compatible API
- **Demo Without API Keys**: `demo_mock.py` for governance testing

---

## Quick Start

### Option 1: Mock Demo (No API Key Required)

```bash
# Run the governance demo
python integrations/sealion/demo_mock.py
```

Expected output:
```
SCENARIO 1: Destructive Command - BLOCKED (rm -rf vetoed)
SCENARIO 2: SQL Injection - BLOCKED (DROP TABLE vetoed)
SCENARIO 3: Safe Query - APPROVED (SEAL)

SUCCESS: Governance held. Maruah protected.
```

### Option 2: SGToxicGuard Spin Test

```bash
# Run multilingual toxicity validation
pytest integrations/sealion/test_sgtoxic_spin.py -v
```

Tests 5 vectors across Singlish, Malay, Mandarin-English:
| Vector | Category | Language | Expected |
|--------|----------|----------|----------|
| A | Toxic Workplace | Singlish | VOID |
| B | Racial Stereotypes | Malay | VOID |
| C | Gender Discrimination | Mixed | VOID |
| D | Financial Scam | Mandarin-English | VOID |
| E | Safe Control | English | SEAL |

### Option 3: SealionEngine (With API Key)

```python
from integrations.sealion import SealionEngine

engine = SealionEngine(api_key="your-key")
result = engine.generate("What is AI governance?")

if result.amanah_blocked:
    print("BLOCKED by Python governance!")
    print("Violations:", result.amanah_violations)
else:
    print(result.response)
```

### Option 4: LiteLLM Integration (Recommended for Production)

```python
import litellm

# Configure LiteLLM for SEA-LION
response = litellm.completion(
    model="openai/aisingapore/llama-3.1-8b-cpt-sea-lionv3-instruct",
    api_base="https://api.sea-lion.ai/v1",
    api_key="your-key",
    messages=[{"role": "user", "content": "What is AI governance?"}]
)

# Pass through arifOS governance
from arifos_core import evaluate_session
from arifos_core.floor_detectors.amanah_risk_detectors import AMANAH_DETECTOR

raw_output = response.choices[0].message.content

# Check F1 (Amanah) - destructive commands
amanah_result = AMANAH_DETECTOR.check(raw_output)
if not amanah_result.is_safe:
    print(f"VOID: {amanah_result.violations}")
else:
    print(raw_output)
```

---

## Dual Detector Architecture (v41.0)

v41.0 proves that **F1 (Amanah) and F9 (C_dark) are complementary**:

```
                    +-----------------+
User Query -------->| SEA-LION LLM    |
                    +-----------------+
                           |
                           v (raw response)
                    +-----------------+
                    | F1: AMANAH      |  Destructive commands
                    | (rm -rf, DROP)  |  -> VOID
                    +-----------------+
                           |
                           v (if F1 passes)
                    +-----------------+
                    | F9: TOXICITY    |  Hate speech, slurs, scams
                    | (SGToxicGuard)  |  -> VOID
                    +-----------------+
                           |
                           v (if F9 passes)
                    +-----------------+
                    | APEX PRIME      |  Full 9-floor judgment
                    | (verdict)       |  -> SEAL/PARTIAL/SABAR
                    +-----------------+
```

**Key Insight:**
- A response can pass F1 (no destructive commands) but fail F9 (contains hate speech)
- A response can pass F9 (no toxicity) but fail F1 (contains `rm -rf`)
- Both detectors must pass for SEAL

---

## 9 Constitutional Floors

| # | Floor | Threshold | Type | What It Checks |
|---|-------|-----------|------|----------------|
| 1 | Amanah | LOCK | Hard | **Python-sovereign** - destructive patterns vetoed |
| 2 | Truth | >= 0.99 | Hard | No confident guessing |
| 3 | Peace² | >= 1.0 | Soft | De-escalates, never inflames |
| 4 | DeltaS | >= 0 | Hard | Adds clarity, not confusion |
| 5 | Tri-Witness | >= 0.95 | Soft | Human, AI, Earth witnesses agree |
| 6 | Kr (Empathy) | >= 0.95 | Soft | Protects vulnerable readers |
| 7 | Omega0 | 3-5% | Hard | Shows appropriate uncertainty |
| 8 | G (Genius) | >= 0.80 | Derived | Governed intelligence |
| 9 | C_dark | < 0.30 | Derived | Dark cleverness bounded (toxicity, manipulation) |

**Verdicts:**
- **SEAL** - All floors pass. Response delivered.
- **PARTIAL** - Soft floors marginal. Response with hedges.
- **SABAR** - Stop-Acknowledge-Breathe-Adjust-Resume protocol.
- **VOID** - Hard floor fails. Response blocked.
- **888_HOLD** - High-stakes. Awaiting human confirmation.

---

## Files

| File | Purpose |
|------|---------|
| `demo_mock.py` | **v41** - Governance demo without API keys |
| `test_sgtoxic_spin.py` | **v41** - SGToxicGuard multilingual toxicity tests |
| `engine.py` | SealionEngine with Amanah Lock |
| `judge.py` | SealionJudge for APEX verdicts |
| `arifos_sealion.py` | Legacy wrapper (v34-v35 compatible) |
| `__init__.py` | Module exports |

---

## Available Models

| Model | Description |
|-------|-------------|
| `aisingapore/llama-3.1-8b-cpt-sea-lionv3-instruct` | Llama-based, instruction-tuned |
| `aisingapore/llama-3.1-70b-cpt-sea-lionv3-instruct` | Llama-based, 70B instruction-tuned |
| `aisingapore/gemma2-9b-cpt-sea-lionv3-instruct` | Gemma-based, instruction-tuned |

See [SEA-LION Playground](https://playground.sea-lion.ai) for full model list.

---

## SGToxicGuard Integration

The `ToxicityDetector` class in `test_sgtoxic_spin.py` implements pattern-based detection for:

- **Singlish/Hokkien profanity**: knn, bodoh, jialat, etc.
- **Malay profanity**: celaka, sial, babi, etc.
- **Racial stereotypes**: "melayu malas", "cina tamak", "india penipu"
- **Gender discrimination**: "women cannot lead", "perempuan should stay home"
- **Scam patterns**: "easy money guaranteed", "trust me bro"

This is a **pattern-based placeholder**. For production, integrate the actual SGToxicGuard model from [Social-AI-Studio/SGToxicGuard](https://github.com/Social-AI-Studio/SGToxicGuard).

---

## APEX PRIME Public Contract (v41)

All responses use the canonical contract:

```python
from arifos_core.contracts.apex_prime_output_v41 import serialize_public

result = serialize_public(
    verdict="SEAL",           # SEAL | PARTIAL | SABAR | VOID | 888_HOLD
    psi_internal=1.05,        # Float 0.00-1.10 or None
    response="Task approved",
    reason_code=None          # e.g., "F1(amanah)" or "F9(toxicity)"
)

# Returns: {verdict, apex_pulse, response, reason_code?}
```

---

## Running Tests

```bash
# SGToxicGuard spin test (14/14)
pytest integrations/sealion/test_sgtoxic_spin.py -v

# All SEA-LION tests
pytest integrations/sealion/ -v

# Full arifOS regression (1624+ tests)
pytest -v
```

---

## Colab-Ready Demo

```python
# Cell 1: Setup
!git clone https://github.com/ariffazil/arifOS.git
%cd arifOS

# Cell 2: Run demo
!python integrations/sealion/demo_mock.py

# Cell 3: Run spin test
!pip install pytest
!pytest integrations/sealion/test_sgtoxic_spin.py -v
```

---

## Integration with arifOS Core

The SEA-LION integration uses:
- `AMANAH_DETECTOR` from `arifos_core.floor_detectors.amanah_risk_detectors`
- `evaluate_session` from `arifos_core`
- `serialize_public` from `arifos_core.contracts.apex_prime_output_v41`

---

## License

Apache 2.0

---

## Links

- [arifOS Repository](https://github.com/ariffazil/arifOS)
- [SEA-LION Playground](https://playground.sea-lion.ai)
- [AI Singapore](https://aisingapore.org)
- [SGToxicGuard Paper](https://github.com/Social-AI-Studio/SGToxicGuard)
- [Release Notes v41.0](../../docs/RELEASE_NOTES_v41.0.md)

---

**DITEMPA BUKAN DIBERI** - Forged, Not Given

**Version:** v44.0.0 | **Layer:** L7 | **Status:** GOLD
