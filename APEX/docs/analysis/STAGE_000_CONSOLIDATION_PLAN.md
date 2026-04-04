# STAGE_000_CONSOLIDATION_PLAN

Status: Draft (Phase 2)
Owner: Codex (Engineer)
Authority: ARIF (Handover SEAL)
Date: 2026-01-16

## Ontological Foundation (L1)
Reference: `L1_THEORY/canon/000_foundation/000_ONTOLOGY.md`

Stage 000 Trinity (Ontology):
- Sovereign Will: authority hierarchy + command auth (F11) + Amanah intent gate (F1)
- Metabolic Void: system reset + thermodynamic cooling (entropy pressure release)
- Kernel Gate: injection defense + reversibility / humility checks (F10-F12 pre-LLM)

BOP (Blowout Preventer) metaphor:
- BOP = the Kernel Gate. It stops pressure spikes (injection, irreversible actions) before the wellhead opens.
- Cooling = pressure relief valve (Metabolic Void).
- Authority chain = lockout mechanism (Sovereign Will).

## Current Implementations (Inventory)
- Runtime Stage 000:
  - `arifos_core/system/stages/stage_000_void.py`
- Amanah gate:
  - `arifos_core/enforcement/stages/stage_000_amanah.py`
- Agent Zero / MCP gate:
  - `arifos_core/stage_000_void/constitutional_gate.py`
  - `arifos_core/stage_000_void/injection_defense.py`
  - `arifos_core/stage_000_void/thermodynamics.py`
  - `arifos_core/stage_000_void/authority_manifest.py`
  - `arifos_core/stage_000_void/stage.py`
- Legacy pipeline:
  - `arifos_core/system/pipeline_legacy.py` (contains its own stage_000_void and calls stage_000_amanah)

## Identified Fixes (Required)
- Normalize injection pattern source to a single module.
- Fix `mcp_000_gate.py` to use returned dict keys (avoid dataclass assumptions).
- Align Stage 000 version strings to v47.0.0.

## Consolidation Strategy (Option B Alignment)
Canonical implementation target:
- `arifos_core/000_void/` as Kernel 000 (The Gate) per ontology.

Compatibility and risk control:
- Preserve MCP compatibility by keeping import shims in `arifos_core/stage_000_void/`.
- Keep runtime wrapper in `arifos_core/system/stages/stage_000_void.py` that delegates to canonical gate modules.
- Incremental refactor only; avoid breaking import paths used by legacy pipeline and MCP tools.

## Proposed Refactor Steps (Low Entropy)
1) Create `arifos_core/000_void/` and move (or mirror) gate modules:
   - constitutional_gate.py
   - injection_defense.py
   - thermodynamics.py
   - authority_manifest.py
2) Update `arifos_core/stage_000_void/` to re-export from `arifos_core/000_void/` (shim).
3) Update `arifos_core/system/stages/stage_000_void.py` to call canonical gate utilities:
   - injection defense
   - thermodynamic cooling
   - humility / reversibility checks
4) Update `arifos_core/enforcement/stages/stage_000_amanah.py`:
   - remove duplicate injection regex
   - reuse canonical injection gate or pass precomputed results
5) Fix MCP tool wrapper:
   - `arifos_core/mcp/tools/mcp_000_gate.py` uses dict keys from `ConstitutionalGate.assess_query`.
6) Align version strings to v47.0.0 and document in headers.

## Mapping to Ontology Trinity
- Sovereign Will:
  - authority_manifest.py
  - command auth checks in Stage000VOID
  - amanah scoring (stage_000_amanah.py)
- Metabolic Void:
  - thermodynamics.py
  - reset/init in Stage000VOID
- Kernel Gate (BOP):
  - injection_defense.py
  - constitutional_gate.py

## Success Criteria
- Single canonical Stage 000 gate at `arifos_core/000_void/`.
- MCP gate still works without API changes.
- Runtime Stage000VOID delegates to canonical gate.
- DS <= 0.0 maintained after each step (`python entropy_analysis_simple.py`).
- No new circular imports.

## Risks and Mitigations
- Risk: breaking imports used by MCP or legacy pipeline.
  - Mitigation: keep shims at old paths and update in small steps.
- Risk: drift between gate logic and runtime stage.
  - Mitigation: centralize gate functions in canonical package and reuse them.

## Notes
- This plan assumes no change to constitutional thresholds; only consolidation.
- Any creation of new numbered directories must map to the ontology and be documented.
