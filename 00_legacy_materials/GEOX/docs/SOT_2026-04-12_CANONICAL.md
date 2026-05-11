# GEOX State of the Tree (SOT) — 2026-04-12 (Post-Refactor)

> **Canonical reference for GEOX repository state after Anti-Chaos Refactor**
> **Seal:** DITEMPA BUKAN DIBERI
> **Version:** v2.1.0-MULTI-PLANE
> **Architecture:** Multi-Plane Contract (Contract / Control / Execution / Domain / Governance)

---

## Repository Architecture (New SOT)

The repository has been restructured to enforce a strict separation of concerns across functional planes.

| Plane | Path | Responsibility |
|-------|------|----------------|
| **Contract** | `contracts/` | **Single Source of Truth.** Tool names, schemas, enums, artifacts. |
| **Control** | `control_plane/` | **Registry & Discovery.** FastMCP server, App manifests, Dashboard routing. |
| **Execution** | `execution_plane/` | **Governed Worker.** VPS runtime, heavy compute, sovereign logic. |
| **Domain** | `domain/` | **Scientific Logic.** Pure geological/physical math and reasoning. |
| **Governance** | `governance/` | **Constitutional Logic.** F1-F13 floors, 888_HOLD logic. |
| **Compatibility**| `compatibility/` | **Quarantine.** Legacy aliases and deprecated shims. |

---

## Tool Registry & Contract (Verified)

| Canonical Tool Name | Dimension | Status |
|---------------------|-----------|--------|
| `prospect_evaluate` | Prospect | ✅ FULL PARITY |
| `well_compute_petrophysics` | Well | ✅ FULL PARITY |
| `earth3d_load_volume` | Earth3D | ✅ FULL PARITY |
| `map_transform_coordinates` | Map | ✅ FULL PARITY |
| `physics_judge_verdict` | Physics | ✅ FULL PARITY |

**Naming Law:** `<dimension>_<action>` (e.g., `well_qc_logs`).
**Return Law:** Standardized Artifact Envelope with `execution_status`, `tool_class`, and `governance_status`.

---

## MCP Apps Readiness (Verified)

The following apps are declared in the Control Plane (`control_plane/fastmcp/manifests/`):
- ✅ `prospect-ui`
- ✅ `well-desk`
- ✅ `section-canvas`
- ✅ `earth-volume`
- ✅ `chronos-history`
- ✅ `judge-console`
- ✅ `map-layer`

---

## Recent Transitions (2026-04-12)

1.  **Restructured Repo:** Moved from flat `registries/` to 5-plane architecture.
2.  **Contract Unification:** Centralized `contracts/enums/statuses.py` as the universal response envelope.
3.  **Alias Quarantine:** Moved `geox_` prefixed tools to the compatibility layer.
4.  **App Manifests:** Created JSON manifests for all dashboard-ready applications.

---

## Action Items

- [ ] Update top-level `README.md` to reflect **Multi-Plane Architecture**.
- [ ] Rebuild Docker images to reflect the new internal folder structure.
- [ ] Deprecate old `geox_unified*.py` scripts in favor of `control_plane/` and `execution_plane/` entrypoints.
