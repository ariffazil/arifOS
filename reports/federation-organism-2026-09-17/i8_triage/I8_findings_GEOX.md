# I8 Triage — GEOX

> **Cycle:** federation-organism-2026-09-17
> **Rule:** I8 — specialist organ must namespacify SEAL/HOLD/VOID/SABAR
> **Mode:** READ-ONLY TRIAGE — no mutation proposed

**Findings for GEOX: 83**

| Classification | Count |
|---|---|
| LIKELY_TEST | 0 |
| LIKELY_AUDIT_TOOL | 0 |
| LIKELY_SCHEMA | 1 |
| NEEDS_REVIEW | 82 |

## LIKELY_SCHEMA (1)

> **Likely schema definition.** Schema-level mention; vocabulary may be intentional for cross-organ reference.

### `GEOX/src/geox_core/schemas/claim_envelope.py`

- ! L406: `verdict = "HOLD"`

## NEEDS_REVIEW (82)

> **These need human review.** The static rule cannot distinguish between a real bug, a fixture using the term deliberately, or a comment that references the term. Sovereign triage required.

### `GEOX/geox/core/basin_charge.py`

- ! L339: `vault_receipt=make_vault_receipt("geox_time4d_verify_timing", payload, verdict="HOLD" if hold_enforced else "SEAL"),`

### `GEOX/geox/core/petro_ensemble.py`

- ! L338: `verdict = "HOLD" if hold_enforced else "SEAL"`

### `GEOX/geox/core/volumetrics.py`

- ! L182: `verdict="HOLD" if hold_enforced else "SEAL",`

### `GEOX/geox/services/las_ingestor.py`

- ! L776: `verdict="HOLD" if suitability == "void" else "SEAL",`

### `GEOX/geox/skills/subsurface/asset_memory_tool.py`

- ! L49: `"vault_receipt": make_vault_receipt("geox_memory_recall_asset", payload, verdict="SEAL" if records else "QUALIFY"),`

### `GEOX/geox/skills/subsurface/petro/las_ingest.py`

- ! L22: `"geox_ingest_las", manifest, verdict="HOLD" if manifest["qcfail_count"] > 0 else "SEAL"`
- ! L44: `"vault_receipt": make_vault_receipt("geox_ingest_las", {"refusal": str(ref)}, verdict="VOID"),`

### `GEOX/geox/skills/subsurface/prospect/evaluate.py`

- ! L100: `verdict = "HOLD"`
- ! L158: `risk_verdict = "SEAL"`
- ! L160: `risk_verdict = "HOLD"`
- ! L162: `risk_verdict = "VOID"`
- ! L224: `verdict = "HOLD"`
- ! L234: `verdict = "SEAL"`

### `GEOX/skills/subsurface/asset_memory_tool.py`

- ! L49: `"vault_receipt": make_vault_receipt("geox_memory_recall_asset", payload, verdict="SEAL" if records else "QUALIFY"),`

### `GEOX/skills/subsurface/petro/las_ingest.py`

- ! L22: `"geox_ingest_las", manifest, verdict="HOLD" if manifest["qcfail_count"] > 0 else "SEAL"`
- ! L44: `"vault_receipt": make_vault_receipt("geox_ingest_las", {"refusal": str(ref)}, verdict="VOID"),`

### `GEOX/skills/subsurface/prospect/evaluate.py`

- ! L100: `verdict = "HOLD"`
- ! L158: `risk_verdict = "SEAL"`
- ! L160: `risk_verdict = "HOLD"`
- ! L162: `risk_verdict = "VOID"`
- ! L224: `verdict = "HOLD"`
- ! L234: `verdict = "SEAL"`

### `GEOX/src/geox_core/apex_envelope.py`

- ! L89: `verdict = "SEAL" if G >= 0.80 else ("SABAR" if G >= 0.50 else "HOLD")`

### `GEOX/src/geox_core/apex_envelope_geox.py`

- ! L78: `verdict = "VOID" if f13_halt else ("SEAL" if G >= 0.80 else ("SABAR" if G >= 0.50 else "HOLD"))`

### `GEOX/src/geox_core/benchmarks/geox_001_well_seismic_truth.py`

- ! L940: `verdict = "HOLD"`
- ! L967: `verdict = "HOLD"`

### `GEOX/src/geox_core/core/basin_charge.py`

- ! L339: `vault_receipt=make_vault_receipt("geox_time4d_verify_timing", payload, verdict="HOLD" if hold_enforced else "SEAL"),`

### `GEOX/src/geox_core/core/petro_ensemble.py`

- ! L338: `verdict = "HOLD" if hold_enforced else "SEAL"`

### `GEOX/src/geox_core/core/volumetrics.py`

- ! L182: `verdict="HOLD" if hold_enforced else "SEAL",`

### `GEOX/src/geox_core/engines/seismic/mistie_engine.py`

- ! L193: `verdict = "HOLD"`
- ! L196: `verdict = "SEAL"`

### `GEOX/src/geox_core/geology/fault_seal.py`

- ! L77: `status="HOLD", errors=["Throw must be > 0 meters"],`

### `GEOX/src/geox_core/seismic_cognition.py`

- ! L1027: `verdict="HOLD",`
- ! L1068: `verdict.verdict = "HOLD"`
- ! L1077: `verdict.verdict = "SEAL"`

### `GEOX/src/geox_core/services/las_ingestor.py`

- ! L776: `verdict="HOLD" if suitability == "void" else "SEAL",`

### `GEOX/src/geox_core/skills/subsurface/asset_memory_tool.py`

- ! L49: `"vault_receipt": make_vault_receipt("geox_memory_recall_asset", payload, verdict="SEAL" if records else "QUALIFY"),`

### `GEOX/src/geox_core/skills/subsurface/petro/las_ingest.py`

- ! L22: `"geox_ingest_las", manifest, verdict="HOLD" if manifest["qcfail_count"] > 0 else "SEAL"`
- ! L44: `"vault_receipt": make_vault_receipt("geox_ingest_las", {"refusal": str(ref)}, verdict="VOID"),`

### `GEOX/src/geox_core/skills/subsurface/prospect/evaluate.py`

- ! L100: `verdict = "HOLD"`
- ! L158: `risk_verdict = "SEAL"`
- ! L160: `risk_verdict = "HOLD"`
- ! L162: `risk_verdict = "VOID"`
- ! L224: `verdict = "HOLD"`
- ! L234: `verdict = "SEAL"`

### `GEOX/src/geox_core/telemetry/geox_telemetry.py`

- ! L75: `emitter.emit_ac_risk_result(verdict="SEAL", ac_risk=0.08)`

### `GEOX/src/geox_mcp/domain/seismic_interpret/bundle.py`

- ! L477: `governance_status="HOLD" if (all_unmeasured or image_only) else "QUALIFY",`

### `GEOX/src/geox_mcp/epistemic/contradiction_ontology.py`

- ! L294: `verdict = "VOID"`
- ! L296: `verdict = "HOLD"`

### `GEOX/src/geox_mcp/organ_governance.py`

- ! L654: `governance_verdict: "SEAL" | "HOLD" | "SABAR" | "VOID" | "ADVISORY"`
- ! L702: `governance_verdict="SEAL",`
- ! L713: `governance_verdict="HOLD",`
- ! L1188: `verdict = "HOLD"  # fail-closed default`
- ! L1208: `verdict = "HOLD"`

### `GEOX/src/geox_mcp/tools/_register.py`

- ! L221: `verdict="HOLD",`

### `GEOX/src/geox_mcp/tools/abduction.py`

- ! L837: `execution_status = "HOLD"`
- ! L838: `verdict = "VOID"`

### `GEOX/src/geox_mcp/tools/analog_atlas.py`

- ! L494: `verdict = "HOLD"`
- ! L501: `verdict = "HOLD"`

### `GEOX/src/geox_mcp/tools/biostrat_calibrate.py`

- ! L236: `verdict = "VOID" if is_falsified else "HOLD"`
- ! L239: `verdict = "HOLD"`

### `GEOX/src/geox_mcp/tools/contrast_views.py`

- ! L600: `verdict = "HOLD"`

### `GEOX/src/geox_mcp/tools/data.py`

- ! L410: `verdict="SEAL",`

### `GEOX/src/geox_mcp/tools/deep_time/vector.py`

- ! L354: `verdict = "HOLD"`

### `GEOX/src/geox_mcp/tools/evidence_reason.py`

- ! L694: `execution_status = "HOLD"`
- ! L695: `verdict = "VOID"`

### `GEOX/src/geox_mcp/tools/feature_joint_info.py`

- ! L152: `verdict = "SEAL"`
- ! L158: `verdict = "HOLD"`

### `GEOX/src/geox_mcp/tools/native_segy.py`

- ! L257: `status = "HOLD"`

### `GEOX/src/geox_mcp/tools/provenance_gpts.py`

- ! L164: `governance_verdict = "SEAL" if epistemic == "OBSERVED" else "HOLD" if epistemic == "UNKNOWN" else "PARTIAL"`
- ! L254: `governance_verdict = "HOLD"`
- ! L268: `governance_verdict = "SEAL"`
- ! L274: `governance_verdict = "SEAL"`

### `GEOX/src/geox_mcp/tools/seismic_well_tie.py`

- ! L640: `execution_status = "HOLD" if vel_result.hold else "SUCCESS"`

### `GEOX/src/geox_mcp/tools/spatial_block.py`

- ! L277: `verdict = "VOID"`
- ! L280: `verdict = "HOLD"`
- ! L286: `verdict = "SEAL"`

### `GEOX/src/geox_mcp/tools/stratigraphy.py`

- ! L96: `governance_status="VOID",`
- ! L133: `governance_status="VOID",`
- ! L166: `governance_status="VOID",`

### `GEOX/src/geox_mcp/tools/well_1d_surface.py`

- ! L162: `verdict="HOLD" if d.get("fail_closed") or not residual_ok else "SEAL",`
- ! L233: `verdict = "HOLD"`

