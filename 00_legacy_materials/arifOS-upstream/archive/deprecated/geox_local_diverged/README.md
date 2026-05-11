# GEOX — Geological Intelligence Coprocessor for arifOS

> A governed, agentic geological intelligence coprocessor built on arifOS. **DITEMPA BUKAN DIBERI.**

GEOX is a **governed agentic system** — not a model, not a plugin — that translates physical Earth data into auditable geological insights through arifOS's Constitutional MCP kernel.

---

## Four-Plane Architecture

```
╔═════════════════════════════════════════════════════════════════╗
║  PLANE 4 ── GOVERNANCE                                         ║
║  Constitutional Floors: F1·F2·F4·F7·F11·F13                   ║
║  Risk Gating · Human Veto · Audit Ledger · Regulator Hook      ║
╠═════════════════════════════════════════════════════════════════╣
║  PLANE 3 ── LANGUAGE / AGENT  (arifOS kernel)                  ║
║                                                                 ║
║  000 INIT ──► 111 THINK ──► 333 EXPLORE ──► 555 HEART         ║
║       └──────────────────────────────────────────────►         ║
║               777 REASON ──► 888 AUDIT ──► 999 SEAL            ║
║                                                                 ║
║  GeoXAgent · agi_mind planner · vault_ledger                   ║
╠═════════════════════════════════════════════════════════════════╣
║  PLANE 2 ── PERCEPTION  (VLM Bridge)                           ║
║  SeismicVLMTool · EOFoundationModelTool                        ║
║  Rule: RGB ≠ truth · Multisensor confirmation required         ║
╠═════════════════════════════════════════════════════════════════╣
║  PLANE 1 ── EARTH  (Physical Reality)                          ║
║  Large Earth Models (LEM) · SimulatorTool                      ║
║  EarthModelTool · GeoRAGTool                                   ║
║  Units · Coordinates · Timestamps · Uncertainty bounds         ║
╚═════════════════════════════════════════════════════════════════╝
```

---

## Why GEOX is NOT a Model

| Property | ML Model | GEOX |
|---|---|---|
| Weights | Fixed parameters | No weights — tool orchestration |
| Output | Token probability | GeoInsight + provenance_chain |
| Auditability | Black box | Every step in vault_ledger |
| Governance | None | Constitutional Floors F1–F13 |
| Human veto | Not possible | F13 Sovereign — always active |
| Uncertainty | Softmax confidence | Calibrated [0.03–0.15] per F7 |
| Verification | Self-referential | External Earth tools required |

GEOX is an **agentic coprocessor**: it orchestrates tools (LEM, simulators, VLMs, RAG), enforces constitutional contracts at every stage, and seals outputs into an immutable audit ledger. The intelligence emerges from governance, not from parameters.

---

## First Principles

Three runtime contracts enforced at every invocation:

```python
# CONTRACT 1: Reality-First
# Any language claim about the physical Earth MUST be verified.
assert insight.predictions[i].verified_by != []          # ≥1 Earth tool
assert insight.predictions[i].units is not None           # F4 Clarity
assert 0.03 <= insight.predictions[i].uncertainty <= 0.15 # F7 Humility

# CONTRACT 2: Perception Bridge (Vision ≠ Truth)
assert vlm_insight.uncertainty >= 0.15                    # VLM floor
assert vlm_insight.confirmed_by_non_visual == True        # before status="supported"
# If not confirmed → risk_level bumped one tier

# CONTRACT 3: Governed Emergence
assert insight.provenance_chain != []                     # immutable trail
if insight.risk_level == "high":
    assert insight.human_signoff_required == True         # F13 veto
    assert pipeline_stage == "888 HOLD"
if insight.risk_level == "critical":
    assert regulator_notify_sent == True
assert vault_ledger.sealed == True                        # 999 SEAL
```

---

## Quick Start

### Install

```bash
pip install arifos-geox
# Optional: Qdrant memory backend
pip install "arifos-geox[qdrant]"
```

### Minimal Example — Evaluate a Prospect

```python
import asyncio
from arifos.geox.geox_agent import GeoXAgent, GeoXConfig
from arifos.geox.geox_schemas import GeoRequest, CoordinatePoint

async def main():
    config = GeoXConfig(
        agent_id="geox-001",
        risk_tolerance="medium",
        require_human_signoff_above="high",
    )
    agent = GeoXAgent(config=config)

    request = GeoRequest(
        query="Evaluate hydrocarbon prospectivity of Blok Selatan",
        basin="Malay Basin",
        location=CoordinatePoint(lat=5.2, lon=104.8),
        risk_tolerance="medium",
        requester_id="geo-analyst-001",
    )

    response = await agent.evaluate_prospect(request)

    print(f"Verdict  : {response.verdict}")            # SEAL | PARTIAL | SABAR | VOID
    print(f"Insights : {len(response.insights)}")
    print(f"Telemetry: {response.arifos_telemetry}")

asyncio.run(main())
```

---

## Repository Structure

```
geox/
├── README.md                        ← you are here
├── pyproject.toml                   ← build config, AGPL-3.0
├── LICENSE
├── docs/
│   ├── GEOX-architecture.md         ← four-plane stack, data flow
│   ├── contracts.md                 ← three runtime contracts
│   └── governance_playbook.md       ← operational governance
├── src/
│   └── arifos/
│       └── geox/
│           ├── __init__.py
│           ├── geox_schemas.py      ← Pydantic v2 data models
│           ├── geox_validator.py    ← Earth→Language contract enforcement
│           ├── geox_agent.py        ← GeoXAgent orchestrator
│           ├── geox_tools.py        ← EarthModelTool, SimulatorTool, VLM tools
│           ├── geox_memory.py       ← GeoMemoryStore (Qdrant / JSONL)
│           ├── geox_reporter.py     ← Markdown + JSON audit reports
│           └── config_geox.yaml     ← default configuration
└── tests/
    ├── test_schemas.py              ← Pydantic model validation tests
    ├── test_validator.py            ← Earth→Language contract tests
    └── test_end_to_end_mock.py      ← full pipeline (no external APIs)
```

---

## arifOS Integration

```
arifOS Constitutional MCP Kernel
│
├── agi_mind (planner)
│   └── dispatches: geox_evaluate_prospect (MCP tool)
│                           │
│                           ▼
│              ┌─────────────────────────┐
│              │      GeoXAgent          │
│              │  000 INIT (validate)    │
│              │  111 THINK (plan tools) │
│              │  333 EXPLORE (call LEM) │
│              │  555 HEART (VLM bridge) │
│              │  777 REASON (validate)  │
│              │  888 AUDIT (sign-off)   │
│              │  999 SEAL (ledger)      │
│              └─────────┬───────────────┘
│                        │ GeoResponse
├── vault_ledger ◄────────┘ (immutable audit sink)
├── GeoMemoryStore ◄──────── (Qdrant / HF JSONL)
└── F13 Sovereign ◄────────── (human veto hook, always active)
```

GEOX registers as a single MCP tool (`geox_evaluate_prospect`) inside arifOS. The kernel's AAA architecture (Architect · Auditor · Agent) wraps every GEOX call:

- **Architect** (111 THINK): Plans which Earth tools to invoke
- **Agent** (333–555): Executes tool calls, collects GeoQuantity objects
- **Auditor** (888 AUDIT): Validates contracts, flags violations, triggers HOLD

---

## Governance Table

| Risk Level | Geological Example | Actions |
|---|---|---|
| `low` | Regional basin screening, public data | Auto-seal, no hold |
| `medium` | Prospect ranking, mixed data sources | Uncertainty review required |
| `high` | Resource estimation for drilling decision | **888 HOLD** · human_signoff_required=True |
| `critical` | Regulatory filing, reserve certification | **888 HOLD** · regulator_notify · legal_review |

**F13 Sovereign veto**: Arif (888_JUDGE) may halt any GEOX action at any stage. Veto is logged immutably in vault_ledger regardless of current pipeline stage.

---

## Constitutional Floor Compliance

| Floor | Name | GEOX Enforcement |
|---|---|---|
| F1 | Amanah (Reversibility) | No irreversible actions without SEAL |
| F2 | Truth ≥ 0.99 | All claims must be Earth-verified |
| F4 | Clarity | Units + coordinates required on every GeoQuantity |
| F7 | Humility | Uncertainty ∈ [0.03, 0.15] enforced by Pydantic |
| F8 | Governed Intelligence | Tool registry gated by config whitelist |
| F9 | Anti-Hantu | No hallucinated geology — LEM/sim verification required |
| F11 | Authority | Requester authorization checked at 000 INIT |
| F12 | Injection Guard | GeoRequest inputs sanitized before tool dispatch |
| F13 | Sovereign | Human veto hook active at all stages |

---

## Contributing

1. Fork and create a feature branch from `main`
2. All new tools must implement the `GeoTool` interface (see `geox_tools.py`)
3. New tools require ≥1 integration test in `tests/`
4. Run `ruff check .` and `mypy src/` before opening a PR
5. Constitutional Floor compliance must be maintained — see `docs/contracts.md`

---

## License

**AGPL-3.0** — see [LICENSE](LICENSE).

GEOX is free software. Any service that uses GEOX to provide geological analysis must open-source its modifications under the same terms.

---

## arifOS Telemetry Footer

Every GEOX response carries a structured telemetry block:

```json
{
  "arifos_telemetry": {
    "kernel_version": "arifOS-0.9.0",
    "agent_id": "geox-001",
    "pipeline_stages": ["000 INIT","111 THINK","333 EXPLORE","555 HEART","777 REASON","888 AUDIT","999 SEAL"],
    "floors_checked": ["F1","F2","F4","F7","F8","F9","F11","F12","F13"],
    "verdict": "PARTIAL",
    "hold_triggered": false,
    "human_signoff_required": false,
    "vault_ledger_id": "vl-2024-geo-00421",
    "sealed_at": "2024-11-15T08:42:17Z",
    "tool_calls": 4,
    "tokens_used": 1847
  }
}
```

> *"DITEMPA BUKAN DIBERI"* — Forged, not given. Every geological insight is earned through verification, not assumed through generation.
