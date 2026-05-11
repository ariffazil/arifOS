# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Owner

**Arif Fazil** — non-coder sovereign architect. Directs AI agents; never writes code manually.
Explain simply. Confirm before destructive actions. No key rotation or production config edits.

---

## What Is GEOX

GEOX is the **Earth Witness organ** in the arifOS constitutional federation. It enforces physical reality constraints on every geoscience output — every interpretation must be thermodynamically possible, geospatially grounded, and consistent with evidence before it receives a SEAL.

**Core doctrine**: *DITEMPA BUKAN DIBERI* — Forged, not given.
**Core theory**: Theory of Anomalous Contrast (ToAC) — visual contrast ≠ physical reality. Every pixel transform chain must be audited.

---

## Repo Layout

```
GEOX/
  arifos/geox/           # Python package (arifos-geox)
    THEORY/              # Core ToAC taxonomy, governance policy, floor compliance
    ENGINE/              # ContrastSpace, AnomalyDetector, TransformRegistry
    governance/          # FloorEnforcer, AuditLogger, VerdictRenderer
    tools/               # Domain tools: seismic/, generic/, well_log, macrostrat
    schemas/             # Pydantic models (seismic_image, geox_schemas)
    renderers/           # Scene compiler, CIGVis adapter, export
  geox-gui/              # React 19 + TypeScript + Vite cockpit UI
    src/
      components/        # UI panels: MapPanel, SeismicPanel, WellLogPanel, ProspectPanel
      store/             # Zustand state slices
      pages/             # Cockpit layout
  geox_mcp_server.py     # Root-level FastMCP entrypoint (Smithery / Claude Desktop)
  arifos/geox/geox_mcp_server.py  # Internal FastMCP server (same tools, package-scoped)
  tests/                 # pytest test suite
  pyproject.toml         # Package config, dep groups, coverage config
```

---

## Architecture: THEORY → ENGINE → TOOLS → GOVERNANCE

| Layer | Purpose | Key files |
|-------|---------|-----------|
| **THEORY** | Defines ToAC taxonomy, transform catalog, conflation risk assessment, floor policies | `THEORY/contrast_theory.py`, `contrast_taxonomy.py`, `contrast_governance.py` |
| **ENGINE** | Processes seismic contrast space, detects anomalies, manages transform registry | `ENGINE/contrast_space.py`, `anomaly_detector.py`, `transform_registry.py` |
| **TOOLS** | Domain-specific tools: seismic line loading, attribute extraction, well-log, Macrostrat | `tools/seismic/`, `tools/well_log_tool.py`, `tools/macrostrat_tool.py` |
| **GOVERNANCE** | Floor enforcement (F1–F13), audit logging, verdict rendering, conflation reports | `governance/floor_enforcer.py`, `audit_logger.py`, `verdict_renderer.py` |

All MCP tools are decorated with `@contrast_governed_tool` which runs the full THEORY→ENGINE→GOVERNANCE pass before returning a verdict.

---

## Verdict System

| Verdict | Confidence | Action |
|---------|-----------|--------|
| `SEAL` | ≥ 0.80 | Auto-proceed |
| `PARTIAL` | ≥ 0.50 | Proceed with caveats |
| `SABAR` | ≥ 0.25 | Hold — gather more data |
| `VOID` | < 0.25 | Block — contradictions detected |

Constants: `GEOX_SEAL`, `GEOX_SABAR`, `GEOX_PARTIAL`, `GEOX_REVIEW`, `GEOX_HOLD`, `GEOX_BLOCK`, `GEOX_VOID` in `arifos/geox/__init__.py`.

---

## Python — Test, Lint, Type Check

Run from `/root/GEOX/`:

```bash
# Install in dev mode
pip install -e ".[dev]"

# Run all tests
pytest tests -q

# Single test
pytest tests -k "test_name" -q

# With coverage (must reach 65%)
pytest tests --cov=arifos.geox

# Lint
ruff check arifos/geox/

# Format
ruff format arifos/geox/

# Type check
mypy arifos/geox/
```

`asyncio_mode = auto` — all async tests work without decorators.
Many seismic/governance files are excluded from coverage (see `pyproject.toml [tool.coverage.run] omit`).

---

## MCP Server

```bash
# Run MCP server (stdio, for Claude Desktop / Smithery)
python geox_mcp_server.py

# FastMCP detects version automatically (2.x Horizon vs 3.x VPS)
# Entrypoint object: geox_mcp_server:mcp
```

Exposed tools: `geox_evaluate_prospect`, `geox_load_seismic_line`, `geox_query_memory`, `geox_health`.

---

## GUI (geox-gui)

```bash
cd geox-gui

# Dev server
npm run dev

# Type check
npm run typecheck

# Lint
npm run lint

# Build
npm run build
```

Stack: React 19, TypeScript, Vite, MapLibre GL 4, CesiumJS 1.114, D3 7, Zustand, Radix UI, Tailwind CSS.

The cockpit is a **single-screen geologist layout**: 2D map (MapLibre) + 3D terrain (Cesium) + seismic section + well-log panel + prospect governance badges. Governance badges must remain visible at all times — this is a constitutional constraint, not a style choice.

---

## Integration with arifOS

GEOX is a **federated co-agent** — it does not run standalone in production. It connects to the arifOS kernel at `https://arifosmcp.arif-fazil.com/mcp` for:
- `init_anchor` — session bootstrap before any evaluation
- `vault_ledger(seal)` — writes verdicts to VAULT999 on the VPS
- `engineering_memory` — stores/recalls geological evaluations in Qdrant

For standalone local dev, the MCP server runs without the kernel (graceful degradation — VAULT writes are skipped).

---

## Constitutional Floors Active in GEOX

| Floor | Rule | Effect |
|-------|------|--------|
| F1 Amanah | No irreversible action without a seal | Blocks writes until verdict ≥ PARTIAL |
| F2 Truth | τ ≥ 0.99 — no ungrounded claims | Coordinates + CRS required on all inputs |
| F4 Clarity | Units + coordinates mandatory | Rejects bare pixel values without physical proxy |
| F7 Humility | Uncertainty must be calibrated | Forces uncertainty band on every estimate |
| F9 Physics9 | No phantom geology | Physical grounding checks |
| F11 Authority | Provenance mandatory | Data source must be declared |
| F13 Sovereign | Human veto hook active | Prospect gate requires human confirmation |

---

## Key Docs in This Repo

| File | Purpose |
|------|---------|
| `README.md` | Full spec including ToAC theory, tool reference, tri-app architecture |
| `UNIFIED_ROADMAP.md` | Current and future milestones |
| `WIRING_GUIDE.md` | How to wire GEOX into arifOS / HuggingFace hub |
| `GEOX_SUCCESS_CRITERIA.md` | What "done" looks like for each feature |
| `HARDENED_SEAL.md` | Constitutional hardening checklist |
| `CHANGELOG.md` | Version history |
