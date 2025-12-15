# L7_DEMOS — Demos, Examples & Body API

**Layer:** L7 (Highest)
**Purpose:** Demonstrations, examples, and the FastAPI Body service
**License:** MIT (Demos are permissive)

---

## What Lives Here

| Directory | Contents |
|-----------|----------|
| `body_api/` | FastAPI Body service |
| `demos/` | GPT demos and showcases |
| `examples/` | Code samples and tutorials |
| `notebooks/` | Jupyter notebooks |

---

## Body API

The Body API is a minimal FastAPI service wrapping the governed pipeline.

### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Service health check |
| `/pipeline/run` | POST | Run governed pipeline |
| `/ledger/verify` | GET | Verify hash-chain integrity |
| `/memory/recall` | POST | Cross-session memory recall |
| `/metrics` | GET | Governance metrics |

### Running

```bash
# Install
pip install arifos

# Run Body API
uvicorn L7_DEMOS.body_api.arifos_api.app:app --reload
```

---

## Demos

| Demo | Purpose |
|------|---------|
| `hc_calculator/` | Human Capital Calculator with governance |
| `prompt_generator/` | Governed prompt generation |
| `anti_hantu_checker/` | F9 Anti-Hantu language checker |

---

## Dependency Rules

```
L7_DEMOS ← Users interact with demos
         → Imports from L3_KERNEL (arifos_core)
         → May use L4_MCP, L5_CLI, L6_SEALION
         → This is the HIGHEST layer — nothing imports from here
```

**Rule:** L7_DEMOS is for demonstration only. Production code belongs in lower layers.

---

## Examples

```python
# examples/basic_governance.py
from arifos_core import APEXPrime, Metrics

metrics = Metrics(
    truth=0.99,
    delta_s=0.15,
    peace_squared=1.2,
    kappa_r=0.96,
    omega_0=0.04,
    amanah=True,
)

judge = APEXPrime(use_genius_law=True)
verdict, genius = judge.judge_with_genius(metrics, energy=0.8)

print(f"Verdict: {verdict}")  # SEAL | PARTIAL | SABAR | VOID
```

---

## Notebooks

| Notebook | Purpose |
|----------|---------|
| `governance_walkthrough.ipynb` | Step-by-step governance tutorial |
| `floor_visualization.ipynb` | Visualize floor thresholds |
| `genius_law_demo.ipynb` | GENIUS LAW (G, C_dark, Ψ) demo |

---

**DITEMPA BUKAN DIBERI** — Learn by example, governed by law.
