# GEOX Next Forge Plan

> **Δ · Ω · Ψ — DITEMPA BUKAN DIBERI**
> **Authority:** ARIF (888_JUDGE)
> **Based on:** GEOXdeep-research-report.md analysis
> **Forge Date:** 2026-03-26

---

## Executive Summary

**Current State:** GEOX is an architectural skeleton with strong governance scaffolding but no real geological "brain." The pipeline (INIT→THINK→EXPLORE→HEART→REASON→AUDIT→SEAL) exists. The tools are mocks.

**Next Forge Goal:** Transform GEOX from skeleton to functional geological coprocessor by:
1. Fixing packaging/installation
2. Integrating Macrostrat API (real geological data)
3. Establishing dual-memory architecture (discrete + continuous)
4. Creating evaluatable benchmarks

**Verdict:** This is a **Phase 0→1** transition forge. Build the foundation before the fancy features.

---

## Forge 1: Foundation Hardening (Weeks 1-2)

### 1.1 Fix Packaging/Installation

**Problem:** `pyproject.toml` declares `src/` layout but code is at repo root. Entrypoint `cli:main` doesn't exist.

**Fix Options:**

| Option | Action | Complexity |
|--------|--------|------------|
| A | Move code to `src/arifos/geox/` | Low |
| B | Update `pyproject.toml` to use `arifos/` directly | Lower |

**Recommendation: Option B** (minimal change, immediate fix)

```toml
# pyproject.toml changes
[tool.hatch.build.targets.wheel]
packages = ["arifos"]  # was ["src/arifos"]

[project.scripts]
# Remove until cli.py exists
# geox = "arifos.geox.cli:main"
```

### 1.2 Add CI/CD Pipeline

Create `.github/workflows/ci.yml`:

```yaml
name: GEOX CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -e ".[dev]"
      - run: ruff check .
      - run: mypy src/arifos/geox  # or arifos/geox
      - run: pytest tests/ -v --tb=short
```

### 1.3 Verify Demo Runs Clean

```bash
cd C:\ariffazil\GEOX
pip install -e ".[dev]"
python -c "from arifos.geox import GeoXAgent, GeoXConfig; print('✓ Import OK')"
python arifos/geox/examples/geox_malay_basin_demo.py
```

**Success Criteria:** Demo runs without `sys.path` hacks.

---

## Forge 2: Macrostrat Integration (Weeks 3-4)

### 2.1 Implement MacrostratTool

**New File:** `arifos/geox/tools/macrostrat_tool.py`

```python
"""Macrostrat API integration for geological context retrieval."""

import httpx
from typing import Any
from datetime import datetime, timezone

from arifos.geox.geox_tools import BaseTool, GeoToolResult
from arifos.geox.geox_schemas import GeoQuantity, ProvenanceRecord, CoordinatePoint


class MacrostratTool(BaseTool):
    """
    Query Macrostrat geological database for stratigraphic context.

    Provides:
    - Regional rock columns
    - Stratigraphic units
    - Geologic map polygons
    - Chronostratigraphic intervals

    API: https://macrostrat.org/api/v2
    License: CC-BY-4.0 (attribution required)
    """

    name = "MacrostratTool"
    description = "Fetch geological context from Macrostrat (columns, units, map polygons)"
    base_url = "https://macrostrat.org/api/v2"

    async def run(self, inputs: dict[str, Any]) -> GeoToolResult:
        location = inputs.get("location")
        if not location:
            return GeoToolResult(
                tool_name=self.name,
                success=False,
                error="Missing 'location' in inputs"
            )

        # Query stratigraphic columns near location
        columns = await self._query_columns(location)

        # Query rock units
        units = await self._query_units(location)

        # Convert to GeoQuantity objects
        quantities = self._parse_to_quantities(columns, units, location)

        return GeoToolResult(
            tool_name=self.name,
            success=True,
            quantities=quantities,
            metadata={
                "source": "macrostrat.org",
                "columns_found": len(columns.get("success", {}).get("data", [])),
                "units_found": len(units.get("success", {}).get("data", [])),
                "license": "CC-BY-4.0",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

    async def _query_columns(self, location: CoordinatePoint) -> dict:
        """Query stratigraphic columns at location."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self.base_url}/columns",
                params={
                    "lat": location.latitude,
                    "lng": location.longitude,
                    "format": "geojson"
                }
            )
            resp.raise_for_status()
            return resp.json()

    async def _query_units(self, location: CoordinatePoint) -> dict:
        """Query rock units at location."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self.base_url}/units",
                params={
                    "lat": location.latitude,
                    "lng": location.longitude
                }
            )
            resp.raise_for_status()
            return resp.json()

    def _parse_to_quantities(
        self,
        columns: dict,
        units: dict,
        location: CoordinatePoint
    ) -> list[GeoQuantity]:
        """Convert Macrostrat data to GeoQuantity objects."""
        quantities = []

        # Parse units
        for unit in units.get("success", {}).get("data", []):
            # Age bounds (Ma)
            t_age = unit.get("t_age")  # Top age
            b_age = unit.get("b_age")  # Bottom age

            if t_age is not None:
                quantities.append(GeoQuantity(
                    value=float(t_age),
                    units="Ma",
                    quantity_type="stratigraphic_age_top",
                    coordinates=location,
                    timestamp=datetime.now(timezone.utc),
                    uncertainty=abs(float(b_age) - float(t_age)) / 2 if b_age else 5.0,
                    provenance=ProvenanceRecord(
                        source_id=f"macrostrat-unit-{unit.get('unit_id', 'unknown')}",
                        source_type="literature",
                        timestamp=datetime.now(timezone.utc),
                        confidence=0.85
                    )
                ))

            # Lithology (categorical, stored as confidence proxy)
            lith = unit.get("lith", "")
            if lith:
                quantities.append(GeoQuantity(
                    value=1.0,  # Presence indicator
                    units="presence",
                    quantity_type=f"lithology_{lith.lower().replace(' ', '_')}",
                    coordinates=location,
                    timestamp=datetime.now(timezone.utc),
                    uncertainty=0.15,
                    provenance=ProvenanceRecord(
                        source_id=f"macrostrat-lith-{unit.get('unit_id', 'unknown')}",
                        source_type="literature",
                        timestamp=datetime.now(timezone.utc),
                        confidence=0.80
                    )
                ))

        return quantities
```

### 2.2 Add Macrostrat to ToolRegistry

**Modify:** `arifos/geox/geox_tools.py`

```python
from arifos.geox.tools.macrostrat_tool import MacrostratTool

class ToolRegistry:
    @classmethod
    def default_registry(cls) -> "ToolRegistry":
        registry = cls()
        # ... existing tools ...
        registry.register(MacrostratTool())
        return registry
```

### 2.3 Add Attribution to Reports

**Modify:** `arifos/geox/geox_reporter.py`

Add Macrostrat attribution footer:

```python
def _add_macrostrat_attribution(self, report: list[str], metadata: dict):
    if metadata.get("macrostrat_used"):
        report.append("\n---")
        report.append("*Geological data provided by Macrostrat (macrostrat.org) under CC-BY-4.0 license.*")
        report.append("*Citation: Peters et al. (2018) Macrostrat: a platform for geological data integration.*")
```

### 2.4 Test Macrostrat Integration

**New Test:** `tests/test_macrostrat_tool.py`

```python
import pytest
from arifos.geox.tools.macrostrat_tool import MacrostratTool
from arifos.geox.geox_schemas import CoordinatePoint

@pytest.mark.asyncio
async def test_macrostrat_tool_malay_basin():
    tool = MacrostratTool()
    location = CoordinatePoint(latitude=5.2, longitude=104.8)  # Malay Basin

    result = await tool.run({"location": location})

    assert result.success
    assert len(result.quantities) > 0
    assert result.metadata["source"] == "macrostrat.org"
```

---

## Forge 3: Dual-Memory Architecture (Weeks 5-8)

### 3.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DUAL-MEMORY SYSTEM                       │
├─────────────────────┬───────────────────────────────────────┤
│  DISCRETE MEMORY    │  CONTINUOUS MEMORY                    │
│  (Macrostrat)       │  (EO Foundation Models)               │
├─────────────────────┼───────────────────────────────────────┤
│  • Named formations │  • Embeddings from multisensor EO     │
│  • Strat columns    │  • Uncertainty quantified             │
│  • Lithologies      │  • Similarity searchable              │
│  • Age intervals    │  • Continuousspatial representation   │
├─────────────────────┴───────────────────────────────────────┤
│  FUSION LAYER (GEOX Agent)                                  │
│  • Retrieve both memories                                   │
│  • Merge evidence                                           │
│  • Validate with floors                                     │
│  • Generate ranked hypotheses                               │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Implement Embedding Service (LEMBridge)

**New File:** `arifos/geox/tools/lem_bridge.py`

```python
"""Large Earth Model (LEM) bridge for EO foundation model embeddings."""

from abc import ABC, abstractmethod
from typing import Any
import httpx

from arifos.geox.geox_tools import BaseTool, GeoToolResult
from arifos.geox.geox_schemas import GeoQuantity, ProvenanceRecord


class LEMBackend(ABC):
    """Abstract base for LEM backends (TerraFM, Prithvi, CROMA)."""

    @abstractmethod
    async def embed(self, aoi: dict[str, Any]) -> dict:
        """Return embeddings + uncertainty for AOI."""
        pass

    @abstractmethod
    def get_model_card(self) -> dict:
        """Return model metadata."""
        pass


class TerraFMBackend(LEMBackend):
    """TerraFM multisensor EO foundation model."""

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    async def embed(self, aoi: dict[str, Any]) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.endpoint}/v1/embed",
                json={
                    "bbox": aoi["bbox"],
                    "sensors": ["sentinel-1", "sentinel-2"],
                    "temporal_range": aoi.get("date_range", ("2023-01-01", "2024-01-01"))
                }
            )
            return resp.json()

    def get_model_card(self) -> dict:
        return {
            "model": "TerraFM",
            "version": "2025-v1",
            "sensors": ["S1", "S2"],
            "embedding_dim": 768
        }


class LEMBridgeTool(BaseTool):
    """Bridge to Large Earth Models for continuous memory."""

    name = "LEMBridgeTool"
    description = "Generate embeddings from EO foundation models"

    def __init__(self, backend: LEMBackend | None = None):
        self.backend = backend

    async def run(self, inputs: dict[str, Any]) -> GeoToolResult:
        if self.backend is None:
            return GeoToolResult(
                tool_name=self.name,
                success=False,
                error="No LEM backend configured"
            )

        try:
            embedding_result = await self.backend.embed(inputs)

            # Convert to GeoQuantity
            quantity = GeoQuantity(
                value=0.0,  # Placeholder for embedding reference
                units="embedding_reference",
                quantity_type="eo_embedding",
                coordinates=inputs["location"],
                timestamp=datetime.now(timezone.utc),
                uncertainty=embedding_result.get("uncertainty", 0.15),
                provenance=ProvenanceRecord(
                    source_id=f"lem-{self.backend.get_model_card()['model']}",
                    source_type="model",
                    timestamp=datetime.now(timezone.utc),
                    confidence=1.0 - embedding_result.get("uncertainty", 0.15)
                )
            )

            return GeoToolResult(
                tool_name=self.name,
                success=True,
                quantities=[quantity],
                metadata={
                    "model_card": self.backend.get_model_card(),
                    "embedding_shape": embedding_result.get("shape"),
                    "inference_time_ms": embedding_result.get("latency_ms")
                }
            )
        except Exception as e:
            return GeoToolResult(
                tool_name=self.name,
                success=False,
                error=str(e)
            )
```

### 3.3 Vector Memory Store (Qdrant Integration)

**Enhance:** `arifos/geox/geox_memory.py`

```python
class DualMemoryStore:
    """
    Dual-memory system combining:
    - Discrete: Macrostrat entities (units, columns, formations)
    - Continuous: EO embeddings from LEM
    """

    def __init__(
        self,
        qdrant_client=None,  # Optional vector DB
        macrostrat_cache_dir: str = "./macrostrat_cache"
    ):
        self.qdrant = qdrant_client
        self.cache_dir = macrostrat_cache_dir
        self._discrete_cache: dict[str, Any] = {}  # Macrostrat data
        self._continuous_cache: dict[str, Any] = {}  # Embeddings

    async def query_dual(
        self,
        location: CoordinatePoint,
        query_type: str = "analog_search",
        top_k: int = 5
    ) -> dict[str, Any]:
        """
        Query both memories and return fused results.

        Returns:
            {
                "discrete": [...],  # Macrostrat units/columns
                "continuous": [...],  # Similar embeddings
                "fused_ranking": [...]  # Combined evidence
            }
        """
        # Query discrete memory (Macrostrat)
        discrete_results = await self._query_discrete(location, top_k)

        # Query continuous memory (embeddings)
        continuous_results = await self._query_continuous(location, top_k)

        # Fuse rankings
        fused = self._fuse_results(discrete_results, continuous_results)

        return {
            "discrete": discrete_results,
            "continuous": continuous_results,
            "fused_ranking": fused
        }

    def _fuse_results(self, discrete: list, continuous: list) -> list:
        """Merge discrete and continuous evidence into ranked hypotheses."""
        # Simple fusion: interleave with confidence weighting
        fused = []
        for d, c in zip(discrete, continuous):
            if d.get("confidence", 0) > c.get("confidence", 0):
                fused.append({"type": "discrete", "data": d})
                fused.append({"type": "continuous", "data": c})
            else:
                fused.append({"type": "continuous", "data": c})
                fused.append({"type": "discrete", "data": d})
        return fused
```

---

## Forge 4: Evaluation & Benchmarks (Weeks 9-10)

### 4.1 Evaluation Framework

**New File:** `arifos/geox/eval/benchmarks.py`

```python
"""Evaluation harness for GEOX against geological benchmarks."""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class EvaluationResult:
    benchmark_name: str
    metric_name: str
    score: float
    uncertainty: float
    sample_count: int
    metadata: dict


class Benchmark(Protocol):
    """Protocol for geological benchmarks."""

    name: str

    async def run(self, agent: GeoXAgent) -> list[EvaluationResult]:
        """Run benchmark and return results."""
        ...


class MalayBasinAnalogBenchmark:
    """
    Custom benchmark: Given a location in Malay Basin,
    retrieve correct stratigraphic analogs.
    """

    name = "malay_basin_analog"

    def __init__(self, test_cases: list[dict]):
        self.test_cases = test_cases

    async def run(self, agent: GeoXAgent) -> list[EvaluationResult]:
        results = []

        for case in self.test_cases:
            request = GeoRequest(
                query=f"Find analogs for {case['formation_name']}",
                location=CoordinatePoint(
                    latitude=case["lat"],
                    longitude=case["lon"]
                ),
                basin="Malay Basin"
            )

            response = await agent.evaluate_prospect(request)

            # Check if expected formation is in top-3 retrieved
            retrieved_formations = [
                insight.text for insight in response.insights
            ]
            correct = case["expected_formation"] in retrieved_formations

            results.append(correct)

        accuracy = sum(results) / len(results)

        return [EvaluationResult(
            benchmark_name=self.name,
            metric_name="top3_recall",
            score=accuracy,
            uncertainty=0.05,
            sample_count=len(results),
            metadata={"test_cases": len(self.test_cases)}
        )]
```

### 4.2 Test Suite Structure

```
tests/
├── unit/
│   ├── test_schemas.py
│   ├── test_validator.py
│   └── test_memory.py
├── integration/
│   ├── test_macrostrat_api.py
│   └── test_dual_memory.py
└── benchmarks/
    ├── test_malay_basin_analog.py
    └── test_stratigraphic_consistency.py
```

---

## Forge 5: Governance & Documentation (Weeks 11-12)

### 5.1 Constitutional Floor Mapping

| Floor | Forge 1-2 | Forge 3-4 | Forge 5+ |
|-------|-----------|-----------|----------|
| F1 Amanah | Reversibility in reports | Dual-memory audit trails | Full provenance chain |
| F2 Truth | Macrostrat API (0.85 conf) | LEM embeddings (0.75 conf) | Calibrated ensembles |
| F4 Clarity | Units in all quantities | Embedding metadata | Uncertainty propagation |
| F7 Humility | API timeout handling | Embedding variance | Confidence calibration |
| F9 Anti-Hantu | No phantom data | Mock→Real tool swap | Benchmark validation |
| F13 Sovereign | HOLD on API failure | HOLD on high uncertainty | Human review UI |

### 5.2 Documentation Updates

**Update:** `README.md` with roadmap

```markdown
## Roadmap

### v0.2 (Current)
- ✅ Packaging fixes
- ✅ CI/CD pipeline
- ✅ MacrostratTool integration
- ✅ Dual-memory architecture

### v0.3 (Next)
- LEM backend integration (TerraFM/Prithvi)
- Vector retrieval with Qdrant
- Evaluation benchmarks

### v0.4 (Future)
- Geology-aware training (Macrostrat-as-labels)
- Stratigraphic constraint layer
- Region-specific evaluation

### v0.5 (Production)
- Model registry + lineage
- Calibration protocols
- Regulator-ready audit trails
```

---

## Resource Estimates

| Phase | Duration | Engineering | GPU | Storage |
|-------|----------|-------------|-----|---------|
| Forge 1-2 | 4 weeks | 2-3 PM | None | <1 GB |
| Forge 3 | 4 weeks | 3-4 PM | Inference only | 5-10 GB |
| Forge 4 | 2 weeks | 2 PM | Benchmark eval | 10 GB |
| **Total** | **10 weeks** | **7-9 PM** | **Minimal** | **<20 GB** |

*PM = Person-Months*

---

## Success Metrics

| Metric | Current | Target (v0.2) |
|--------|---------|---------------|
| Install from pip | ❌ Broken | ✅ `pip install -e .` works |
| Demo runs | ❌ Needs sys.path hack | ✅ Clean import |
| Macrostrat integration | ❌ Mock only | ✅ Real API calls |
| Test coverage | ❌ Unknown | ✅ >60% |
| CI passing | ❌ None | ✅ Green on main |
| Dual-memory | ❌ Not implemented | ✅ Discrete + Continuous |
| Documentation | ⚠️ Basic | ✅ Full API docs |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Macrostrat API changes | Medium | Medium | Version pinning, adapter pattern |
| LEM backend unavailable | Medium | High | Mock fallback, pluggable backends |
| Performance on large AOIs | Medium | Medium | Caching, pagination |
| AGPL license concerns | Low | High | Clear attribution, dual-license discussion |

---

## Checklist for Forge Completion

### Forge 1: Foundation
- [ ] `pip install -e .` works clean
- [ ] CI pipeline running (ruff, mypy, pytest)
- [ ] Demo runs without sys.path hacks

### Forge 2: Macrostrat
- [ ] `MacrostratTool` implemented
- [ ] Tool registered in default registry
- [ ] Attribution in reports
- [ ] Tests passing

### Forge 3: Dual-Memory
- [ ] `DualMemoryStore` implemented
- [ ] `LEMBridgeTool` with pluggable backends
- [ ] Qdrant integration working
- [ ] Fusion layer tested

### Forge 4: Evaluation
- [ ] Benchmark framework
- [ ] Malay Basin analog test
- [ ] Documentation updated

### Forge 5: Governance
- [ ] All floors mapped to features
- [ ] Roadmap published
- [ ] Risk register reviewed

---

**DITEMPA BUKAN DIBERI** — This forge transforms GEOX from governance shell to geological brain.

**Verdict:** SEAL — Proceed with Forge 1 immediately.
