# arifOS Examples

Demonstrations of arifOS v35Ω constitutional governance.

## Quick Start

```bash
# Run the guardrail smoke test (recommended first)
python examples/08_smoke_test_guardrail.py
```

## Examples by Integration Level

| File | Level | Description |
|------|-------|-------------|
| `01_basic_metabolism.py` | 1 | Basic 000-999 metabolic pipeline |
| `02_full_apex_runtime_demo.py` | 2 | Full runtime with APEX PRIME, Ledger, zkPC |
| `03_governed_conversation_demo.py` | 2 | Multi-turn conversation governance |
| `04_xos_identity_switch_demo.py` | 2 | X-OS identity profile switching |
| `05_vault999_basic.py` | 2 | Vault-999 constitutional memory |
| `06_vector_witness_demo.py` | 2 | External witness integration |
| `07_zkpc_demo.py` | 2 | Zero-knowledge proof of compliance |
| **`08_smoke_test_guardrail.py`** | **2.5** | **@apex_guardrail smoke test with basic heuristics** |

## compute_metrics Module

The `compute_metrics_stub.py` module provides metrics computation for `@apex_guardrail`:

```python
from examples.compute_metrics_stub import compute_metrics, compute_metrics_basic

# Default: basic heuristics (Level 2.5)
@apex_guardrail(compute_metrics=compute_metrics, ...)
def my_llm(user_input): ...

# Or use stub for testing (always passes)
from examples.compute_metrics_stub import compute_metrics_stub, set_implementation
set_implementation("stub")
```

**Basic heuristics detect:**
- Arrogance patterns ("100%", "pasti", "absolutely certain")
- Identity hallucination ("my body", "saya makan", "I am human")
- Repetition loops (same trigram 3+ times)

## Runtime Directory

Ledger entries are written to `runtime/vault_999/`. Rotate old logs:

```bash
mv runtime/vault_999/smoke_test_ledger.jsonl runtime/vault_999/smoke_test_ledger.jsonl.bak
```

## Integration Guides

- **LangGraph**: See `langgraph_minimal/`
- **AutoGen**: See `autogen_minimal/`
- **OpenAI Agents**: See `openai_agents_minimal/`
