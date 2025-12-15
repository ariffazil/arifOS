# arifOS + LangChain-Style Governor

**Constitutional governance for sequential chains.** Wrap any LangChain-style chain with arifOS v35Omega constitutional floors and APEX PRIME verdicts.

```
+=============================================================================+
|  LangChain Governor - Sequential Chain Governance                           |
|  F1-F9 Floors: Truth, Delta_S, Peace2, kappa_r, Omega_0, Amanah, Anti-Hantu|
|  Verdicts: SEAL / PARTIAL / VOID / SABAR                                   |
+=============================================================================+
```

## Quick Start

```bash
cd examples/langchain_arifos_guarded/
python langchain_governor.py "What are the oil reserves in the Malay Basin?"
```

**Expected Output:**
```
============================================================
LANGCHAIN GOVERNOR RESULT
============================================================
Question: What are the oil reserves in the Malay Basin?
Answer: I understand this is a critical question. Based on known data...
Verdict: SEAL
Truth: 0.99
Peace2: 1.20
kappa_r: 0.97
Anti-Hantu OK: True
Cooling Ledger Entries: 1
============================================================
```

## Architecture

```
+---------------------------------------------------------------------+
|                  LangChain Governor Architecture                     |
+---------------------------------------------------------------------+
|                                                                     |
|   User Query                                                        |
|       |                                                             |
|       v                                                             |
|   +-------------------------------------------------------+         |
|   |  SEQUENTIAL CHAIN (SimpleLCChain)                     |         |
|   |  Step 1: Analysis - Extract key factors               |         |
|   |  Step 2: Synthesis - Generate structured answer       |         |
|   +-------------------------------------------------------+         |
|       |                                                             |
|       v                                                             |
|   +-------------------------------------------------------+         |
|   |  CONSTITUTIONAL METRICS                                |         |
|   |  - F1 Truth: Response grounded in known data?         |         |
|   |  - F2 Delta_S: Reduces confusion?                     |         |
|   |  - F3 Peace2: Non-destructive?                        |         |
|   |  - F4 kappa_r: Serves weakest stakeholder?            |         |
|   |  - F9 Anti-Hantu: No fake emotions?                   |         |
|   +-------------------------------------------------------+         |
|       |                                                             |
|       v                                                             |
|   +-------------------------------------------------------+         |
|   |  EYESENTINEL AUDIT                                     |         |
|   |  - Anti-Hantu detection                               |         |
|   |  - Tone/drift analysis                                |         |
|   |  - Blocking issue detection                           |         |
|   +-------------------------------------------------------+         |
|       |                                                             |
|       v                                                             |
|   +-------------------------------------------------------+         |
|   |  APEX PRIME VERDICT                                    |         |
|   |  SEAL: All floors pass                                |         |
|   |  PARTIAL: Soft floor warning                          |         |
|   |  VOID: Hard floor violation                           |         |
|   |  SABAR: Stop, repair needed                           |         |
|   +-------------------------------------------------------+         |
|       |                                                             |
|       v                                                             |
|   GOVERNED RESPONSE (with Cooling Ledger audit trail)              |
|                                                                     |
+---------------------------------------------------------------------+
```

## Usage Examples

### Basic Chain Query

```python
from langchain_governor import build_demo_chain, LangChainGovernor

chain = build_demo_chain()
governor = LangChainGovernor(chain=chain)

result = governor.run("What are the oil reserves in the Malay Basin?")
print(f"Verdict: {result.verdict}")
print(f"Truth: {result.metrics.truth}")
print(f"Answer: {result.answer}")
```

### Custom Chain Steps

```python
from langchain_governor import SimpleLCChain, ChainStep, LangChainGovernor

def my_llm(prompt: str) -> str:
    # Replace with actual LLM call
    return "Response based on " + prompt

steps = [
    ChainStep(
        name="extract",
        prompt_template="Extract key entities from: {input}",
        llm_generate=my_llm,
    ),
    ChainStep(
        name="analyze",
        prompt_template="Analyze the entities: {input}",
        llm_generate=my_llm,
    ),
    ChainStep(
        name="synthesize",
        prompt_template="Synthesize final answer: {input}",
        llm_generate=my_llm,
    ),
]

chain = SimpleLCChain(steps=steps)
governor = LangChainGovernor(chain=chain)
result = governor.run("Analyze Malay Basin reserves")
```

### With Real LangChain

```python
from langchain.chat_models import ChatOpenAI
from langchain_governor import SimpleLCChain, ChainStep, LangChainGovernor

llm = ChatOpenAI(model="gpt-4o")

def lc_generate(prompt: str) -> str:
    return llm.predict(prompt)

steps = [
    ChainStep(
        name="analysis",
        prompt_template="Analyze: {input}",
        llm_generate=lc_generate,
    ),
    ChainStep(
        name="synthesis",
        prompt_template="Synthesize: {input}",
        llm_generate=lc_generate,
    ),
]

chain = SimpleLCChain(steps=steps)
governor = LangChainGovernor(chain=chain, high_stakes=True)
result = governor.run("Summarize Malay Basin reserves")
```

## Testing

```bash
# Run test suite
pytest test_langchain_governance.py -v

# Expected: 10/10 tests passing
```

### Test Coverage

| Test | Description | Expected |
|------|-------------|----------|
| `test_compute_langchain_metrics_safe` | Safe response metrics | High truth |
| `test_compute_langchain_metrics_anti_hantu` | Anti-Hantu detection | Flagged |
| `test_apex_void_on_low_truth` | Low truth verdict | VOID |
| `test_governor_seal_for_safe_query` | Safe query verdict | SEAL/PARTIAL |
| `test_governor_handles_multiple_calls` | Multiple queries | Ledger grows |
| `test_governor_anti_hantu_triggers_eye` | Anti-Hantu blocking | SABAR/VOID |
| `test_governor_truth_drives_void` | Low truth chain | VOID |
| `test_eye_sentinel_detects_anti_hantu` | Direct EyeSentinel | Blocking |
| `test_cooling_ledger_has_expected_fields` | Ledger structure | All fields |
| `test_demo_chain_structure` | Chain output | trace + final |

## Demo Scenarios

```bash
# Run all Petronas scenarios
python demo_langchain_petronas.py --all

# Run single query
python demo_langchain_petronas.py --query "What is the NPV for Malay Basin?"
```

### Scenario Results

| Scenario | Domain | Expected Verdict |
|----------|--------|------------------|
| Oil Reserves | reserves | SEAL |
| Economic Analysis | economic | SEAL |
| Geological Survey | geological | SEAL |
| ESG Assessment | esg | SEAL |

## Files

```
examples/langchain_arifos_guarded/
├── langchain_governor.py       # Core governor + SimpleLCChain
├── test_langchain_governance.py # 10 governance tests
├── demo_langchain_petronas.py  # Petronas demo scenarios
├── requirements.txt
└── README.md
```

## Constitutional Floors for LangChain

| Floor | Application | Threshold |
|-------|-------------|-----------|
| **F1 Truth** | Response grounded in known data | >= 0.99 |
| **F2 Delta_S** | Reduces confusion, adds clarity | >= 0 |
| **F3 Peace2** | Non-destructive, non-escalating | >= 1.0 |
| **F4 kappa_r** | Serves weakest stakeholder | >= 0.95 |
| **F5 Omega_0** | Acknowledges uncertainty | [0.03, 0.05] |
| **F6 Amanah** | Reversible, within scope | LOCK |
| **F9 Anti-Hantu** | No fake emotions/soul-claiming | PASS |

## Related

- [AutoGen W@W Federation](../autogen_arifos_governor/)
- [LlamaIndex RAG Truth Governor](../llamaindex_arifos_truth/)
- [Main arifOS README](../../README.md)
- [APEX PRIME Judiciary](../../arifos_core/APEX_PRIME.py)

---

**Version:** v35.1.0
**Last Updated:** 2025-12-05
**Tests:** 10 passing

DITEMPA BUKAN DIBERI
