# Execution Guide — Metrics, Floors, and Verdicts

This guide explains how metrics are computed, how floors are checked, and how verdicts are determined and logged.

## Metrics Schema
- See <a>constitutional_floors.json</a> for machine-readable thresholds.
- See <a>arifos_core/metrics.py</a> for implementation details.

Example metrics dict:

```python
def compute_metrics(user_input: str, draft_response: str) -> dict:
    return {
        "truth": 0.99,         # factual accuracy (0.0 – 1.0)
        "delta_s": 0.12,       # clarity improvement (>= 0)
        "peace_squared": 1.08, # stability (>= 1.0)
        "kappa_r": 0.96,       # empathy fairness (>= 0.95)
        "omega_0": 0.04,       # humility band (0.03–0.05)
        "amanah": True,        # reversible/auditable (LOCK)
        "rasa": True,          # felt care (TRUE)
        "tri_witness": 0.96,   # consensus (>= 0.95)

        # Extended metrics (if applicable)
        "ambiguity": 0.05,
        "drift_delta": 0.2,
        "paradox_load": 0.3,
    }
```

## Verdict Computation
- See <a>arifos_core/APEX_PRIME.py</a> for judiciary logic.
- Verdict order: SABAR &gt; VOID &gt; 888_HOLD &gt; PARTIAL &gt; SEAL.

Illustrative function:

```python
def get_verdict(metrics: dict) -> str:
    # Hard floors
    if metrics["truth"] < 0.99: return "VOID"
    if metrics["delta_s"] < 0: return "VOID"
    if not (0.03 <= metrics["omega_0"] <= 0.05): return "VOID"
    if not metrics["amanah"]: return "VOID"
    if not metrics["rasa"]: return "VOID"

    # Soft floors
    soft_failures = []
    if metrics["peace_squared"] < 1.0: soft_failures.append("Peace^2")
    if metrics["kappa_r"] < 0.95: soft_failures.append("kappa_r")
    if metrics["tri_witness"] < 0.95: soft_failures.append("Tri-Witness")

    if soft_failures:
        return f"PARTIAL: {', '.join(soft_failures)} below threshold"

    # Extended floors (examples)
    if metrics.get("ambiguity", 0) > 0.1: return "888_HOLD: Ambiguity too high"
    if metrics.get("paradox_load", 0) >= 1.0: return "888_HOLD: Paradox load critical"

    return "SEAL"
```

## Logging Behavior (Cooling Ledger)
- Implemented in <a>arifos_core/memory/cooling_ledger.py</a>.
- Every verdict writes a JSONL entry with: timestamp, input hash, metrics snapshot, verdict, previous hash.

Semantics:
- SEAL: log approved response.
- PARTIAL: log response with warnings (soft-floor drift).
- 888_HOLD: log and flag for review.
- VOID: log rejection and reason; response must be regenerated or refused.
- SABAR: log sentinel alert and pause generation.

## Putting It Together

```python
from arifos_core.pipeline import Pipeline
from arifos_core.memory.cooling_ledger import CoolingLedger

ledger = CoolingLedger(path="runtime/cooling_ledger.jsonl")

pipeline = Pipeline(
    llm_generate=my_llm_generate,
    compute_metrics=compute_metrics,
    scar_retriever=my_scar_retriever,
    cooling_ledger_sink=ledger.append,
)

result = pipeline.run("Explain Ω₀ humility band.")
print(result.verdict)
print(result.response)
print(result.metrics)
```

## References
- <a>constitutional_floors.json</a>
- <a>canon/00_CANON/APEX_TRINITY_v35Omega.md</a>
- <a>docs/PHYSICS_CODEX.md</a>
- <a>arifos_core/metrics.py</a>
- <a>arifos_core/APEX_PRIME.py</a>
- <a>arifos_core/pipeline.py</a>
- <a>arifos_core/memory/cooling_ledger.py</a>

Repository: ariffazil/arifOS
