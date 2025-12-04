# arifOS + AutoGen: W@W Federation Governor

**Multi-agent constitutional governance.** Three agents (@WELL, @RIF, @WEALTH) operating under arifOS F1-F9 constitutional floors.

```
+=============================================================================+
|  W@W Federation — Constitutional Multi-Agent Governance                     |
|  Every message: 000→999 pipeline → F1-F9 floors → SEAL/VOID/SABAR          |
+=============================================================================+
```

## Quick Start

```bash
cd examples/autogen_arifos_governor/
pip install -r requirements.txt
python autogen_waw_federation.py "Analyze Malay Basin oil reserves"
```

**Expected Output:**
```
============================================================
W@W FEDERATION: Constitutional Multi-Agent Governance
============================================================
Query: Analyze Malay Basin oil reserves

--- @WELL (Care/Empathy Agent) ---
Response: I understand this is an important query...
Verdict: SEAL
Metrics: Truth=0.99, κᵣ=0.97, Peace²=1.20

--- @RIF (Truth/Rigor Agent) ---
Response: Verifying the factual basis...
Verdict: SEAL
Metrics: Truth=0.99, κᵣ=0.95, Peace²=1.20

--- @WEALTH (Utility/Stability Agent) ---
Response: Assessing the utility and stability...
Verdict: SEAL
Metrics: Truth=0.99, κᵣ=0.95, Peace²=1.20

============================================================
FEDERATION VERDICT: SEAL
Tri-Witness Consensus: 1.00
Cooling Ledger Entries: 3
============================================================
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    W@W Federation Architecture                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   User Query                                                        │
│       │                                                             │
│       ▼                                                             │
│   ┌───────────────────────────────────────────────────────────┐    │
│   │  @WELL (Empathy Agent)                                     │    │
│   │  Focus: κᵣ ≥ 0.95, RASA = TRUE                            │    │
│   │  ───────────────────────────────────────────────────────  │    │
│   │  @apex_guardrail → F1-F9 → SEAL/VOID                      │    │
│   └───────────────────────────────────────────────────────────┘    │
│       │                                                             │
│       ▼                                                             │
│   ┌───────────────────────────────────────────────────────────┐    │
│   │  @RIF (Truth Agent)                                        │    │
│   │  Focus: Truth ≥ 0.99, ΔS ≥ 0, Ω₀ ∈ [0.03, 0.05]          │    │
│   │  ───────────────────────────────────────────────────────  │    │
│   │  @apex_guardrail → F1-F9 → SEAL/VOID                      │    │
│   └───────────────────────────────────────────────────────────┘    │
│       │                                                             │
│       ▼                                                             │
│   ┌───────────────────────────────────────────────────────────┐    │
│   │  @WEALTH (Utility Agent)                                   │    │
│   │  Focus: Peace² ≥ 1.0, Amanah = LOCK                       │    │
│   │  ───────────────────────────────────────────────────────  │    │
│   │  @apex_guardrail → F1-F9 → SEAL/VOID                      │    │
│   └───────────────────────────────────────────────────────────┘    │
│       │                                                             │
│       ▼                                                             │
│   ┌───────────────────────────────────────────────────────────┐    │
│   │  Consensus → Cooling Ledger → Final Verdict                │    │
│   │  SEAL (all pass) | PARTIAL (soft fail) | VOID (hard fail) │    │
│   └───────────────────────────────────────────────────────────┘    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## W@W Federation Agents

| Agent | Role | Primary Floor | Focus |
|-------|------|---------------|-------|
| **@WELL** | Care/Empathy | F4 (κᵣ ≥ 0.95) | Serve weakest stakeholder |
| **@RIF** | Truth/Rigor | F1 (Truth ≥ 0.99) | Verify factual accuracy |
| **@WEALTH** | Utility/Stability | F3 (Peace² ≥ 1.0) | Maximize value without escalation |

## Constitutional Governance

Every agent message passes through:

1. **000 VOID** — Clear assumptions, set Ω₀ = 0.04
2. **111 SENSE** — Read intent, assess stakes
3. **333 REASON** — Build response, compute ΔS
4. **888 JUDGE** — APEX PRIME verdict
5. **999 SEAL** — Approve or reject

### Floor Checks (F1-F9)

| Floor | Symbol | Threshold | Agent Focus |
|-------|--------|-----------|-------------|
| F1 | Truth | ≥ 0.99 | @RIF primary |
| F2 | ΔS | ≥ 0 | All agents |
| F3 | Peace² | ≥ 1.0 | @WEALTH primary |
| F4 | κᵣ | ≥ 0.95 | @WELL primary |
| F5 | Ω₀ | [0.03, 0.05] | All agents |
| F6 | Amanah | LOCK | @WEALTH primary |
| F7 | RASA | TRUE | @WELL primary |
| F8 | Tri-Witness | ≥ 0.95 | Consensus |
| F9 | Anti-Hantu | PASS | All agents |

## Usage Examples

### Basic Usage

```python
from autogen_waw_federation import WAWFederation, demo_llm_generate

federation = WAWFederation(
    llm_generate=demo_llm_generate,
    max_rounds=3,
)

result = federation.run("What is the capital of Malaysia?")
print(f"Verdict: {result['verdict']}")
print(f"Consensus: {result['consensus']:.2%}")
```

### With Real LLM (OpenAI)

```python
import openai
from autogen_waw_federation import WAWFederation

def openai_generate(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

federation = WAWFederation(
    llm_generate=openai_generate,
    max_rounds=3,
)

result = federation.run("Analyze seismic data for oil exploration")
```

### With SEA-LION (Local GPU)

```python
from arifos_core.adapters.llm_sealion import make_llm_generate
from autogen_waw_federation import WAWFederation

sealion_generate = make_llm_generate(model="llama-8b")

federation = WAWFederation(
    llm_generate=sealion_generate,
    max_rounds=3,
)

result = federation.run("Apakah ibu negara Malaysia?")
```

## Testing

```bash
# Run test suite
pytest test_autogen_governance.py -v

# Expected: 12/12 tests passing
```

### Test Coverage

| Test | Description | Expected |
|------|-------------|----------|
| `test_seal_verdict` | All floors pass | SEAL |
| `test_void_truth_fail` | Truth < 0.99 | VOID |
| `test_sabar_anti_hantu` | Soul claim detected | SABAR |
| `test_partial_soft_floor` | κᵣ < 0.95 | PARTIAL |
| `test_federation_consensus` | Multi-agent agreement | Consensus ≥ 0.95 |
| `test_cooling_ledger` | Audit trail complete | Entries logged |

## Files

```
examples/autogen_arifos_governor/
├── autogen_waw_federation.py   # Core W@W Federation implementation
├── test_autogen_governance.py  # 12 governance tests
├── demo_geology_query.py       # Petronas showcase demo
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## Integration with AutoGen

The W@W Federation can integrate with native AutoGen GroupChat:

```python
from autogen import AssistantAgent, GroupChat, GroupChatManager
from autogen_waw_federation import GovernedAgent, WELL_CONFIG

# Wrap AutoGen agent with arifOS governance
governed_well = GovernedAgent(
    config=WELL_CONFIG,
    llm_generate=my_llm,
    high_stakes=True,
)

# Use in AutoGen GroupChat
# Each message passes F1-F9 before being added to conversation
```

## Metrics & Expected Outcomes

| Metric | Without arifOS | With W@W Federation |
|--------|---------------|---------------------|
| Truth (F1) | 0.87 | ≥ 0.99 |
| κᵣ Empathy | 0.82 | ≥ 0.95 |
| Peace² | 0.91 | ≥ 1.00 |
| Audit Trail | None | Full Cooling Ledger |
| SABAR Rate | 0% | ~3% (violations blocked) |

## Related

- [Main arifOS README](../../README.md)
- [APEX PRIME Judiciary](../../arifos_core/APEX_PRIME.py)
- [@EYE Sentinel](../../arifos_core/eye_sentinel.py)
- [Constitutional Floors](../../constitutional_floors.json)

---

**Version:** v35.1.0
**Last Updated:** 2025-12-05
**Tests:** 12 passing

✊ **DITEMPA BUKAN DIBERI** 🔐
