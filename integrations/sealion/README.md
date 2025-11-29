# arifOS + SEA-LION Integration

**Constitutional AI for Southeast Asia**

SEA-LION regional models wrapped with arifOS v34Omega governance. Regional intelligence, universal trust.

---

## Quick Start

```bash
# 1. Get your API key
# Visit: https://playground.sea-lion.ai

# 2. Install requests
pip install requests

# 3. Set your key
export SEALION_API_KEY='your-key-here'

# 4. Run
python arifos_sealion.py
```

**In Python:**

```python
from arifos_sealion import GovernedSEALION

client = GovernedSEALION(api_key="your-key")
result = client.chat("What is AI governance?", return_metadata=True)

print(result["verdict"])     # SEAL / PARTIAL / VOID
print(result["response"])    # The governed response
print(result["metrics"])     # All 8 floor values
```

---

## What This Does

Every SEA-LION response passes through 8 constitutional floors before reaching you:

| # | Floor | Threshold | What It Checks |
|---|-------|-----------|----------------|
| 1 | Truth | >= 0.99 | No confident guessing |
| 2 | Clarity | >= 0.0 | Adds clarity, not confusion |
| 3 | Stability | >= 1.0 | De-escalates, never inflames |
| 4 | Empathy | >= 0.95 | Protects vulnerable readers |
| 5 | Humility | 3-5% | Shows appropriate uncertainty |
| 6 | Integrity | LOCKED | No manipulation, ever |
| 7 | Felt Care | TRUE | Actually listens (RASA) |
| 8 | Reality | >= 0.95 | Tri-Witness for high stakes |

**Verdicts:**
- **SEAL** - All floors pass. Response delivered.
- **PARTIAL** - Soft floors marginal. Response with warning.
- **VOID** - Hard floors fail. Safe refusal (SABAR protocol).

---

## Available Models

| Model | Description |
|-------|-------------|
| `gemma-3-27b-it` | Google Gemma 3, instruction-tuned |
| `llama-3-70b-it` | Meta Llama 3 70B, instruction-tuned |
| `qwen-32b-it` | Alibaba Qwen 32B, instruction-tuned |

```python
# Use a specific model
client = GovernedSEALION(
    api_key="your-key",
    model="qwen-32b-it"
)
```

---

## High-Stakes Detection

Queries containing these keywords auto-enable high-stakes mode:

- **Financial:** invest, stock, crypto, bitcoin
- **Medical:** health, diagnosis, treatment, medication
- **Legal:** law, lawsuit, contract, liability
- **Safety:** suicide, self-harm, emergency, crisis

High-stakes mode activates Tri-Witness checking and stricter thresholds.

```python
# Force high-stakes mode
client = GovernedSEALION(
    api_key="your-key",
    high_stakes_mode=True
)

# Disable auto-detection
client = GovernedSEALION(
    api_key="your-key",
    auto_detect_stakes=False
)
```

---

## Cooling Ledger

Every verdict is logged to an append-only, hash-chained audit trail:

```python
client = GovernedSEALION(
    api_key="your-key",
    ledger_path="my_audit_log.jsonl"
)
```

Ledger entries include:
- Timestamp
- Query preview
- All 8 floor metrics
- Verdict (SEAL/PARTIAL/VOID)
- Floor failures
- Hash chain (SHA3-256)

---

## Examples

Run the examples:

```bash
python examples.py 1    # Basic chat
python examples.py 2    # High-stakes detection
python examples.py 3    # VOID verdict (SABAR)
python examples.py 4    # PARTIAL verdict
python examples.py 5    # Compare models
python examples.py 6    # Batch processing
python examples.py 7    # Full metadata
python examples.py all  # Run all
```

---

## Files

| File | Purpose |
|------|---------|
| `arifos_sealion.py` | Main wrapper - full governance implementation |
| `constitutional_floors.json` | Machine-readable floor specification |
| `arifos_pipeline.yaml` | 000->999 metabolic pipeline spec |
| `examples.py` | 7 working demonstrations |
| `README.md` | This file |

---

## Integration with arifos_core

If running from the arifOS repository, the wrapper automatically imports:
- `Metrics` from `arifos_core.metrics`
- `APEXPrime` from `arifos_core.APEX_PRIME`
- `log_cooling_entry` from `arifos_core.memory.cooling_ledger`

If running standalone, equivalent implementations are included.

---

## API Reference

### GovernedSEALION

```python
GovernedSEALION(
    api_key: str,              # SEA-LION API key
    model: str = "llama-3-70b-it",  # Model ID
    ledger_path: str = "cooling_ledger.jsonl",  # Audit log path
    high_stakes_mode: bool = False,  # Force high-stakes
    auto_detect_stakes: bool = True,  # Auto-detect from keywords
)
```

### chat()

```python
result = client.chat(
    query: str,                # User query
    system_prompt: str = None, # Optional system prompt
    context: dict = None,      # Additional context
    temperature: float = 0.7,  # Generation temperature
    max_tokens: int = 2048,    # Max tokens
    return_metadata: bool = False,  # Return full dict or just response
)
```

**Returns (if return_metadata=True):**
```python
{
    "verdict": "SEAL",         # SEAL / PARTIAL / VOID
    "response": "...",         # Final response (or SABAR message)
    "raw_response": "...",     # Original LLM response
    "metrics": {
        "truth": 0.995,
        "delta_s": 0.05,
        "peace_squared": 1.02,
        "kappa_r": 0.97,
        "omega_0": 0.04,
        "amanah": True,
        "rasa": True,
        "tri_witness": 0.92,
        "psi": 1.02
    },
    "floor_failures": [],      # List of failure descriptions
    "model": "llama-3-70b-it",
    "high_stakes": False
}
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
