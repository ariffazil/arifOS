# GEOX Unified Roadmap & TODO
**"DITEMPA BUKAN DIBERI" — Forged, Not Given.**

This document unifies the architectural goals, research recommendations, and technical requirements from the GEOX documentation suite into a single execution plan.

---

## 🎯 Current Status (Audit v0.1)
- **Architecture:** 4-Plane Stack (Governance, Language, Perception, Earth) defined.
- **Pipeline:** 000-999 (INIT to SEAL) framework implemented.
- **Governance:** F1-F13 Floors and 888 HOLD mechanism active.
- **Critical Gaps:** Broken packaging, mock tools, fragile regex validation, missing CI/CD.

---

## 🔨 Immediate TODO (The "Forge 1" Sprint)
*Focus: Foundation Hardening & Macrostrat Plumbing*

### 1. Technical Infrastructure
- [ ] **Fix Packaging:** Update `pyproject.toml` to match the actual `arifos/geox` directory structure (fix `src/` layout mismatch).
- [ ] **CLI Implementation:** Create `arifos/geox/cli.py` to satisfy the `geox` entrypoint.
- [ ] **Automated CI:** Setup GitHub Actions for:
    - `ruff check .` (Linting)
    - `mypy src/` (Type Safety)
    - `pytest tests/` (Unit/Integration Tests)
- [ ] **Clean Installs:** Ensure `pip install -e .` works without `sys.path` manipulation.

### 2. The Digital Crust (Macrostrat)
- [ ] **Macrostrat Adapter:** Implement `arifos/geox/geox_macrostrat.py`.
    - `macrostrat_context(lat, lon, radius)`: Fetch map polygons and units.
    - `macrostrat_column(lat, lon)`: Fetch synthetic stratigraphic columns.
- [ ] **F2 Truth Anchor:** Update `GeoXValidator` to use Macrostrat data as the "physical truth" for spatial queries.
- [ ] **Mandatory Provenance:** Enforce that any geological claim without a Macrostrat/Sensor citation is flagged as `SABAR` or `VOID`.

---

## 🗺️ Long-Term Roadmap

### Phase 2: Perception & Memory (Months 3–9)
*Goal: Move from mocks to real Earth perception.*
- [ ] **LEM Integration:** Wrap a real Earth Foundation Model (TerraFM or Prithvi-EO-2.0).
- [ ] **Continuous Memory:** Activate Qdrant backend for continuous vector embeddings.
- [ ] **Dual-Memory Pattern:** Implement `geox_retrieve_context` merging Discrete (Macrostrat) and Continuous (LEM) memory.
- [ ] **Schema-First Synthesis:** Replace regex-based extraction with Pydantic-first JSON generation from the LLM.

### Phase 3: Geology Adaptation (Months 9–18)
*Goal: Domain-specific fine-tuning and stratigraphic logic.*
- [ ] **Constraint Graph:** Build a stratigraphic ordering graph (Chronostratigraphy) to catch "impossible" vertical sequences.
- [ ] **Alignment Pipeline:** Intersect Macrostrat polygons with EO tiles for supervised training data.
- [ ] **Multi-Task Heads:** Predict unit classes, age bins, and lithology distributions with calibrated uncertainty.

### Phase 4: Verification & Governance (Months 18–24)
*Goal: Scientific rigor and deployment hardening.*
- [ ] **Benchmark Harness:** Evaluate against GEO-Bench and Copernicus-Bench.
- [ ] **Model Registry:** Full data lineage and "Model Cards" for auditability.
- [ ] **F13 Sovereign Dashboard:** A UI for the `888_JUDGE` (Arif) to monitor and sign-off on 888 HOLD states.

---

## 🛡️ Runtime Contracts (Invariant Reminders)
1. **Reality-First:** Language claims must be verified by Earth tools.
2. **Perception Bridge:** Vision (VLM) is not truth; requires sensor confirmation.
3. **Governed Emergence:** Every output must be sealed in the `vault_ledger`.

---
*Created: March 26, 2026*
*Status: DRAFT / Forge-Ready*
