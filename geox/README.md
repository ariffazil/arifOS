# GEOX — Geological Intelligence Coprocessor

> **⚠️ PRE-PRODUCTION STATUS** — MCP server under active development. API may change. Not for production use without human oversight.
>
> **DITEMPA BUKAN DIBERI** — Forged through verification, not assumed through generation.

---

## 🤔 What is GEOX? (For Humans)

**GEOX is a smart assistant for geologists.**

Imagine you have a junior geologist who:
- Never forgets physics or geology principles
- Can read seismic data, well logs, and satellite images
- Always shows their work (every calculation explained)
- Asks for help when uncertain
- Never makes up data

**GEOX is that junior geologist — but powered by AI, governed by strict rules.**

### For Professional Geologists
GEOX provides **governed, auditable geological prospect evaluation** through a Model Context Protocol (MCP) server. It doesn't replace your expertise — it amplifies it with:

- **Multi-source data fusion** (seismic, wells, satellite, gravity)
- **Constitutional constraints** (physics-based validation at every step)
- **Full provenance tracking** (every insight traceable to source data)
- **Human-in-the-loop governance** (you remain the final authority)

### For AI Agents
GEOX exposes a deterministic, schema-validated tool interface for geological evaluation. Key characteristics:

- **Pydantic v2 schemas** for all inputs/outputs ([`geox_schemas.py`](arifos/geox/geox_schemas.py))
- **7-stage pipeline** (000→111→333→555→777→888→999)
- **Tool registry pattern** ([`geox_tools.py`](arifos/geox/geox_tools.py))
- **Memory store** with Qdrant/JSONL backends ([`geox_memory.py`](arifos/geox/geox_memory.py))
- **Validator enforcement** of constitutional floors ([`geox_validator.py`](arifos/geox/geox_validator.py))

---

## 🏛️ Architecture Overview

### The Four Planes of GEOX

```
┌─────────────────────────────────────────────────────────────────────┐
│  PLANE 4 — GOVERNANCE (The Rules)                                  │
│  Constitutional Floors F1·F2·F4·F7·F9·F11·F13                     │
│  • Every claim must be Earth-verified (F2)                         │
│  • Uncertainty must be declared (F7)                               │
│  • Human veto always possible (F13)                                │
├─────────────────────────────────────────────────────────────────────┤
│  PLANE 3 — LANGUAGE/AGENT (The Brain)                              │
│                                                                     │
│   000 INIT → 111 THINK → 333 EXPLORE → 555 HEART                  │
│        └──────────────────────────────────────────►                 │
│                777 REASON → 888 AUDIT → 999 SEAL                   │
│                                                                     │
│  Each stage has entry/exit contracts. No skipping allowed.         │
├─────────────────────────────────────────────────────────────────────┤
│  PLANE 2 — PERCEPTION (The Senses)                                 │
│  • SeismicVLMTool — Vision-language for seismic interpretation     │
│  • WellLogTool — Electronic well log analysis ([`well_log_tool.py`](arifos/geox/tools/well_log_tool.py)) │
│  • SatelliteMonitor — EO data ingestion ([`satellite_monitor.py`](arifos/geox/tools/satellite_monitor.py)) │
│  • MacrostratTool — Stratigraphic database queries ([`macrostrat_tool.py`](arifos/geox/tools/macrostrat_tool.py)) │
├─────────────────────────────────────────────────────────────────────┤
│  PLANE 1 — EARTH (The Reality)                                     │
│  • Large Earth Models (LEM) — Physics-based simulation             │
│  • Unit conversions (meters, feet, seconds, years) ([`units.py`](arifos/geox/utils/units.py)) │
│  • Coordinate systems (WGS-84, local grids)                        │
│  • Uncertainty bounds (±X meters, ±Y million years)                │
└─────────────────────────────────────────────────────────────────────┘
```

### The 7-Stage Pipeline

| Stage | Name | Purpose | File |
|-------|------|---------|------|
| **000** | INIT | Validate request, check authority, initialize context | [`geox_init.py`](arifos/geox/geox_init.py) |
| **111** | THINK | Plan tool calls, select attribute families | [`geox_agent.py`](arifos/geox/geox_agent.py) |
| **333** | EXPLORE | Execute Earth tools, gather evidence | [`geox_tools.py`](arifos/geox/geox_tools.py) |
| **555** | HEART | VLM bridge — vision meets language | [`geox_agent.py`](arifos/geox/geox_agent.py) |
| **777** | REASON | Synthesize insights, calculate confidence | [`geox_agent.py`](arifos/geox/geox_agent.py) |
| **888** | AUDIT | Validate contracts, flag violations | [`geox_validator.py`](arifos/geox/geox_validator.py) |
| **999** | SEAL | Final verdict, immutable ledger entry | [`geox_reporter.py`](arifos/geox/geox_reporter.py) |

---

## 🚀 Quick Start

### Installation

```bash
# From PyPI (when published)
pip install arifos-geox

# With Qdrant memory backend
pip install "arifos-geox[qdrant]"

# Development install from source
git clone https://github.com/ariffazil/GEOX.git
cd GEOX
pip install -e ".[dev]"
```

### Running the MCP Server

```bash
# STDIO mode (for Claude Desktop, etc.)
python server.py

# HTTP mode (for Prefect Horizon, webhooks)
python server.py --host 0.0.0.0 --port 8100

# With logging
python server.py --log-level debug
```

### Testing Health

```bash
# Check if server is alive
curl http://localhost:8100/health

# List available tools
curl http://localhost:8100/mcp/tools
```

---

## 🛠️ Available Tools

### 1. `geox_evaluate_prospect`

**Full geological prospect evaluation pipeline.**

```python
{
    "query": "Evaluate hydrocarbon prospectivity",
    "prospect_name": "Bunga Raya",
    "latitude": 5.2,
    "longitude": 104.8,
    "depth_m": 2500,
    "basin": "Malay Basin",
    "play_type": "stratigraphic",
    "available_data": ["seismic_3d", "well_logs"],
    "risk_tolerance": "medium",
    "requester_id": "arif.fazil@petronas.com"
}
```

**Returns:**
```python
{
    "verdict": "PARTIAL",  # SEAL | PARTIAL | SABAR | VOID
    "confidence_aggregate": 0.87,
    "human_signoff_required": True,
    "insights": [...],
    "arifos_telemetry": {...}
}
```

### 2. `geox_query_memory`

**Query past geological evaluations.**

```python
{
    "query": "carbonate buildup",
    "basin": "Malay Basin",
    "limit": 5
}
```

### 3. `geox_health`

**Server health and readiness check.**

```bash
curl http://localhost:8100/health
```

**Returns:**
```python
{
    "status": "healthy",
    "version": "0.4.0",
    "tool_registry": {...},
    "memory_store": {...},
    "constitutional_floors": ["F1", "F2", "F4", "F7", "F9", "F11", "F13"]
}
```

---

## 📋 The Verdict System

GEOX returns one of four verdicts:

| Verdict | Meaning | When Used |
|---------|---------|-----------|
| **SEAL** ✅ | Full confidence, all contracts satisfied | All floors passed, uncertainty within bounds |
| **PARTIAL** ⚠️ | Partial confidence, some gaps | Missing data but reasonable inference possible |
| **SABAR** ⏸️ | Insufficient data, needs more work | Critical gaps, cannot proceed without more data |
| **VOID** ❌ | Invalid request or system error | Malformed input, authority failure, or crash |

**Human signoff is required for:**
- PARTIAL verdicts with risk_level = "high"
- All SEAL verdicts on critical infrastructure
- Any 888 AUDIT contract violation

---

## 📐 Constitutional Floors (The Rules)

Every GEOX evaluation must satisfy these floors:

| Floor | Name | Rule | Enforcement |
|-------|------|------|-------------|
| **F1** | Amanah | No irreversible actions without SEAL | Pipeline blocks at 888 if unverified |
| **F2** | Truth ≥ 0.99 | All claims Earth-verified | LEM/simulator cross-check required |
| **F4** | Clarity | Units + coordinates mandatory | Pydantic validation rejects missing units |
| **F7** | Humility | Uncertainty ∈ [0.03, 0.15] | Confidence band enforced at 777 REASON |
| **F9** | Anti-Hantu | No hallucinated geology | VLM outputs require non-visual confirmation |
| **F11** | Authority | Requester authorized at 000 | Invalid credentials → VOID |
| **F13** | Sovereign | Human veto always possible | 888_JUDGE can halt any stage |

---

## 📁 Repository Structure

```
GEOX/
├── README.md                    ← You are here (source of truth)
├── server.py                    ← MCP server entry point (THE ONLY SERVER)
├── pyproject.toml               ← Dependencies, build config
│
├── arifos/                      ← Package source
│   └── geox/
│       ├── __init__.py
│       ├── geox_agent.py        ← Main agent orchestrator
│       ├── geox_schemas.py      ← Pydantic models (GeoRequest, GeoResponse, etc.)
│       ├── geox_tools.py        ← Tool registry base
│       ├── geox_validator.py    ← Constitutional floor enforcement
│       ├── geox_memory.py       ← Memory store (Qdrant/JSONL)
│       ├── geox_reporter.py     ← Report generation
│       ├── geox_init.py         ← 000 INIT stage
│       ├── base_tool.py         ← Tool interface definition
│       ├── cli.py               ← Command-line interface
│       │
│       ├── tools/               ← Specific tool implementations
│       │   ├── well_log_tool.py      ← LAS file analysis
│       │   ├── macrostrat_tool.py    ← Stratigraphic database
│       │   ├── satellite_monitor.py  ← EO data
│       │   ├── petrophysics_tool.py  ← Petrophysical calculations
│       │   └── lem_bridge.py         ← Large Earth Model interface
│       │
│       ├── utils/               ← Utilities
│       │   ├── units.py         ← Unit conversions
│       │   ├── time_utils.py    ← Temporal calculations
│       │   └── provenance.py    ─ Provenance tracking
│       │
│       └── examples/            ← Usage examples
│           └── geox_malay_basin_demo.py
│
├── tests/                       ← Test suite
│   ├── test_schemas.py
│   ├── test_validator.py
│   └── test_end_to_end_mock.py
│
├── knowledge/                   ← Knowledge base
│   ├── 001_INDICES.md
│   └── meta_trilemma_theorem.md
│
└── ops/                         ← Operations
    └── k8s/
        └── geox-deployment.yaml
```

---

## 🔌 MCP Integration

GEOX implements the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) for AI agent interoperability.

### For Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "geox": {
      "command": "python",
      "args": ["/path/to/GEOX/server.py"]
    }
  }
}
```

### For arifOS

GEOX registers as a single MCP tool within the arifOS constitutional kernel:

```python
# arifOS dispatches to GEOX
result = await mcp_client.call_tool(
    "geox_evaluate_prospect",
    {
        "query": "Evaluate prospect",
        "prospect_name": "Bunga Raya",
        "latitude": 5.2,
        "longitude": 104.8,
        "basin": "Malay Basin",
        "play_type": "stratigraphic",
        "risk_tolerance": "medium",
        "requester_id": "arif.fazil"
    }
)
```

---

## 🧪 Development

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=arifos.geox --cov-report=term-missing

# Specific test
pytest tests/test_validator.py -v
```

### Linting

```bash
ruff check arifos/geox
ruff format arifos/geox
mypy arifos/geox
```

### Adding a New Tool

1. Create tool class in `arifos/geox/tools/my_tool.py`
2. Inherit from `BaseTool` ([`base_tool.py`](arifos/geox/base_tool.py))
3. Implement `execute()` method with proper schema
4. Register in `ToolRegistry.default_registry()`
5. Add tests in `tests/test_tools.py`

---

## ⚠️ Limitations & Known Issues

### Current Limitations

1. **Memory backend**: Default is in-memory JSONL. Qdrant integration tested but not production-hardened.
2. **VLM tools**: Require external API keys (OpenAI, Anthropic). Not bundled.
3. **LEM interface**: Mock implementations only. Real physics simulators require proprietary licenses.
4. **Seismic I/O**: No SEG-Y, LAS, or PBDS readers included. Use external libraries.

### Known Issues

- **server.py**: HTTP transport requires `uvicorn`. Falls back to minimal asyncio if unavailable.
- **Validation**: Some edge cases in coordinate system conversions not fully tested.
- **Performance**: Not optimized for high-throughput. Designed for careful, deliberate evaluations.

### Roadmap

- [ ] Production-harden Qdrant backend
- [ ] Add SEG-Y seismic reader
- [ ] Implement real LEM bridge (PyLith, ASPECT)
- [ ] Add 2D/3D visualization tools
- [ ] Multi-language support (Bahasa Malaysia)

---

## 📜 License

**AGPL-3.0** — See [LICENSE](LICENSE)

If you use GEOX in a service, you must open-source your modifications.

---

## 👤 Author

**Muhammad Arif bin Fazil**
- PETRONAS Exploration
- ariffazil@gmail.com
- GitHub: [@ariffazil](https://github.com/ariffazil)

---

## 🙏 Acknowledgments

- **arifOS Trinity**: The constitutional kernel that governs GEOX
- **MCP Protocol**: Anthropic's Model Context Protocol
- **PETRONAS**: For supporting open geological intelligence

---

> *"DITEMPA BUKAN DIBERI"* — Forged, not given. Every geological insight is earned through verification, not assumed through generation.
