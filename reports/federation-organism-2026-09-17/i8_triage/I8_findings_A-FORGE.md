# I8 Triage — A-FORGE

> **Cycle:** federation-organism-2026-09-17
> **Rule:** I8 — specialist organ must namespacify SEAL/HOLD/VOID/SABAR
> **Mode:** READ-ONLY TRIAGE — no mutation proposed

**Findings for A-FORGE: 22**

| Classification | Count |
|---|---|
| LIKELY_TEST | 0 |
| LIKELY_AUDIT_TOOL | 0 |
| LIKELY_SCHEMA | 0 |
| NEEDS_REVIEW | 22 |

## NEEDS_REVIEW (22)

> **These need human review.** The static rule cannot distinguish between a real bug, a fixture using the term deliberately, or a comment that references the term. Sovereign triage required.

### `A-FORGE/apa/core/act_executor.py`

- ! L166: `verdict="SEAL",`
- ! L346: `verdict="HOLD" if not ok else "SEAL",`

### `A-FORGE/bridges/graph_bridge.py`

- ! L216: `verdict="HOLD", error=f"unknown_path: {p}"), 404)`
- ! L225: `verdict="HOLD", error=f"invalid_json: {e}"), 400)`
- ! L231: `verdict="HOLD", error=f"unknown_verb: {verb}"), 400)`
- ! L245: `verdict="HOLD", error=str(e)[:400]), 500)`

### `A-FORGE/bridges/gws_backend.py`

- ! L120: `verdict="HOLD",`
- ! L156: `return envelope(connector, verb, False, None, verdict="HOLD", error=err_msg)`
- ! L163: `verdict="HOLD",`
- ! L172: `verdict="VOID",`

### `A-FORGE/bridges/gws_bridge.py`

- ! L156: `verdict="VOID",`
- ! L167: `verdict="VOID",`

### `A-FORGE/domain/orchestration/arifFlow_adapter.py`

- ! L498: `verdict="HOLD",`

### `A-FORGE/services/sequential-thinking/server.py`

- ! L301: `verdict="VOID", epistemic_tag="SPEC", confidence=1.0,`
- ! L307: `verdict="VOID", epistemic_tag="SPEC", confidence=1.0,`
- ! L313: `verdict="VOID", epistemic_tag="SPEC", confidence=1.0,`
- ! L342: `verdict="VOID", epistemic_tag="SPEC", confidence=1.0,`
- ! L372: `verdict = "SEAL"`
- ! L530: `verdict="SEAL",`
- ! L562: `return _arifos_envelope(data, verdict="SEAL", epistemic_tag="OBS", confidence=0.99,`
- ! L582: `return _arifos_envelope(data, verdict="SEAL", epistemic_tag="OBS",`
- ! L607: `return _arifos_envelope(data, verdict="SEAL", epistemic_tag="OBS",`

