# Minda — Micro arifOS Cognition Substrate

> **v0.1 — Advisory only. Generates ranked plans with confidence bands BEFORE Judge.**
> **ART may recommend. Judge authorizes. Vault witnesses.**
> **DITEMPA BUKAN DIBERI — Mind forged, not granted.**

---

## What is Minda?

**Minda** is the cognition substrate of arifOS. It sits at the **333-REASON** stage of
the 000-999 pipeline, BEFORE `arif_judge_deliberate` (888). Its only job is to:

1. **Sense** — fold new observations into a Bayesian belief
2. **Think** — generate candidate tool-chain plans
3. **Simulate** — rollout each plan over a horizon
4. **Score** — multi-objective utility with F1-F13 constraints
5. **Propose** — return ranked plans + confidence band + hold_888 flag

Minda **never executes**. It advises. The Judge authorizes. The Vault witnesses.

## The Gap Minda Fills

| Stage | arifOS today | What minda adds |
|---|---|---|
| 111 SENSE | `arif_sense_observe` (raw facts) | **Bayesian belief update** (confidence + provenance) |
| 333 REASON | `arif_mind_reason` (LLM reasoning) | **Plan generation + trajectory simulation** (search over futures) |
| 333 REASON | (none) | **Multi-objective expected utility** (F1-F13 as constraints) |
| 555 ROUTE | `arif_kernel_route` (pick tool) | **Ranked plans with confidence bands** (not just a single pick) |
| 888 JUDGE | `arif_judge_deliberate` (constitutional verdict) | (consumes minda output as one input) |

The 3 missing pieces from the v3.1 framework: **Bayesian update + trajectory simulation + expected utility**.

## Architecture (8 modules)

```
arifosmcp/core/minda/
├── __init__.py        # Public exports
├── service.py         # MindaService — the orchestrator
├── belief.py          # Bayesian posterior (F2 TRUTH: explicit confidence)
├── generator.py       # Candidate plan generation (3 canonical patterns)
├── rollout.py         # Trajectory simulation (horizon-damped)
├── utility.py         # Multi-objective expected utility (F6 MARUAH hard floor)
├── constraints.py     # F1-F13 → constraint mapping (doctrinal table)
├── schemas.py         # Pydantic v2 models (input/output contracts)
└── config.py          # Weights + thresholds
```

## Usage

```python
from arifosmcp.core.minda import MindaService, MindConfig, ThinkRequest

service = MindaService(MindConfig())

req = ThinkRequest(
    intent="Deploy new recursive agent tooling service to production",
    context={"env": "prod", "team": "forge"},
    observations={
        "build_passing": True,
        "auth_verified": False,
        "deploy_window_open": True,
    },
)

response = service.think(req)

print(f"Best plan:  {response.best_plan_id}")
print(f"Score:      {response.score:.2f}")
print(f"Confidence: [{response.confidence_band[0]:.2f}, {response.confidence_band[1]:.2f}]")
print(f"888_HOLD:   {response.hold_888}  ({response.hold_reason})")
print()
for i, plan in enumerate(response.ranked):
    print(f"  #{i+1} {plan.plan_id:25s} score={plan.score:6.2f}  hold={plan.hold_888}")
```

**Output:**
```
Best plan:  reason_then_search
Score:      1.07
Confidence: [0.97, 1.17]
888_HOLD:   False  (None)

  #1 reason_then_search       score=  1.07  hold=False
  #2 observe_more             score=  1.00  hold=False
  #3 forge_now                score= -0.34  hold=True
```

The forge plan triggers 888_HOLD (irreversible). The mind picks `reason_then_search` (reversible, high info gain).

## F1-F13 Mapping

| Floor | How it becomes a check in minda |
|---|---|
| **F1 AMANAH** | Irreversible plan → `hold_888=True`. Reversibility is a property of `ToolAction.reversible`. |
| **F2 TRUTH** | Confidence bands on every output (`(low, high)` tuple, never point estimate). |
| **F3 WITNESS** | Provenance labels per observation (`OBS`/`DER`/`INT`/`SPEC`). |
| **F4 CLARITY** | Outcome `info_gain` is a positive utility term (encourages clarity). |
| **F5 PEACE** | `risk` is a negative utility term (heavily weighted, `w_risk=1.4`). |
| **F6 EMPATHY** | `maruah` is a positive utility term. Below `MARUAH_HARD_FLOOR=0.4` → `-inf`. |
| **F7 HUMILITY** | Confidence capped at `0.99` (never reaches `1.0`). |
| **F8 GENIUS** | `info_gain` rewards learning; `cost` penalizes waste. |
| **F9 ANTIHANTU** | Minda is documented as a **TOOL**, not a mind. No consciousness claims. |
| **F10 ONTOLOGY** | Same as F9 — AI-only ontology. |
| **F11 AUTH** | Caller identity is required upstream (gated by arifOS session). |
| **F12 INJECTION** | Input sanitization is upstream (`arif_sense_observe` enforces 5× patterns). |
| **F13 SOVEREIGN** | Human veto is absolute. Minda never self-executes; Judge + 888_HOLD are the only authority. |

## Configuration

```python
from arifosmcp.core.minda import MindConfig

# Conservative defaults (used if you don't pass a config)
config = MindConfig()  # w_maruah=1.2, w_risk=1.4, irreversible_hold=True

# Or tune per org / per agent
config = MindConfig(
    w_maruah=2.0,         # dignity even more weighted
    w_risk=2.0,           # risk more penalized
    irreversible_hold=True,  # always 888_HOLD on irreversible
)
```

## Tests

```bash
cd /root/arifOS && PYTHONPATH=. python3 -m pytest tests/test_minda.py -v
```

## What's NOT in v0.1 (deferred)

- **LLM-driven candidate generation** — v0.1 is fixed 3-pattern. Future: use the LLM to generate goal-conditioned plans.
- **Pareto frontier** — v0.1 is linear weighted sum. Future: lexicographic ordering for hard constraints.
- **Bayesian Monte Carlo** — v0.1 is deterministic with uncertainty penalty. Future: actual sampling over the belief distribution.
- **Multi-agent mind** — v0.1 is single-agent. Future: coordinated minds for sub-agent delegation.
- **MCP tool wrapper** — v0.1 is a Python class. Future: `arif_minda_think` as a registered MCP tool.

## Heritage

- **AGI/ASI decision theory** (AIXI, expected utility, Bayesian planning)
- **OODA loop** (Observe → Orient → Decide → Act)
- **arifOS F1-F13 floors** (constitutional constraint layer)
- **ART tool reflex** (`arifosmcp.runtime.art.py`, the cousin reflex at the call level)
- **arifos-agent-doctrine** (the philosophical half of the two-skill architecture)

## Doctrine (binding)

> **Minda advises. Judge authorizes. Vault witnesses.**
>
> Intelligence without governance is dangerous. Governance without cognition is blind.
> The mind is forged. The reflex disciplines. The doctrine constrains. The vault remembers.
>
> DITEMPA BUKAN DIBERI — Mind forged, not granted.
