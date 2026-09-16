# I8 Triage — WELL

> **Cycle:** federation-organism-2026-09-17
> **Rule:** I8 — specialist organ must namespacify SEAL/HOLD/VOID/SABAR
> **Mode:** READ-ONLY TRIAGE — no mutation proposed

**Findings for WELL: 119**

| Classification | Count |
|---|---|
| LIKELY_TEST | 0 |
| LIKELY_AUDIT_TOOL | 0 |
| LIKELY_SCHEMA | 0 |
| NEEDS_REVIEW | 119 |

## NEEDS_REVIEW (119)

> **These need human review.** The static rule cannot distinguish between a real bug, a fixture using the term deliberately, or a comment that references the term. Sovereign triage required.

### `WELL/internal/apex_envelope_well.py`

- ! L85: `verdict = "SEAL"`
- ! L87: `verdict = "SABAR"`
- ! L89: `verdict = "HOLD"`

### `WELL/loop/recovery_v1.py`

- ! L162: `final_verdict = "HOLD"`
- ! L191: `final_verdict = "SEAL" if ok else "HOLD"`
- ! L203: `final_verdict = "SEAL"`
- ! L206: `final_verdict = "HOLD"`

### `WELL/server.py`

- ! L1286: `verdict = "HOLD"`
- ! L1290: `verdict = "HOLD"`
- ! L1294: `verdict = "HOLD"`
- ! L2482: `coupled_verdict = "HOLD"`
- ! L3185: `status = "HOLD" if status != "VOID" else "VOID"`
- ! L3726: `status="HOLD",`
- ! L4456: `status="HOLD",`
- ! L6389: `status = "HOLD"`
- ! L6393: `status = "HOLD"`
- ! L6398: `status = "HOLD"`
- ! L6405: `status = "HOLD"`
- ! L6637: `status="HOLD",`
- ! L9678: `verdict="SEAL" if res.get("ok") else "HOLD",`
- ! L9694: `verdict="SEAL" if (well_ok and deps["all_ok"]) else "HOLD",`
- ! L9712: `verdict="SEAL" if all_ok else "HOLD",`
- ! L9720: `verdict="VOID",`
- ! L9754: `verdict="SEAL" if res.get("ok") else "HOLD",`
- ! L9768: `verdict="HOLD",`
- ! L9789: `verdict="SEAL" if not res.get("boundary_violated") else "HOLD",`
- ! L9809: `verdict="SEAL" if not bnd.get("boundary_violated") else "HOLD",`
- ! L9822: `verdict="VOID",`
- ! L9882: `verdict="SEAL" if res.get("evidence_quality") == "STRONG" else "HOLD",`
- ! L9905: `verdict="SEAL"`
- ! L9915: `verdict="VOID",`
- ! L9973: `verdict="HOLD" if any_risk else "SEAL",`
- ! L9988: `verdict="SEAL" if res.get("m_well_verdict") == "HEALTHY" else "HOLD",`
- ! L10008: `verdict="SEAL"`
- ! L10027: `verdict="SEAL"`
- ! L10042: `verdict="HOLD",`
- ! L10055: `verdict="SEAL"`
- ! L10072: `verdict="SEAL"`
- ! L10089: `verdict="SEAL"`
- ! L10104: `verdict="HOLD",`
- ! L10113: `verdict="SEAL"`
- ! L10129: `verdict="VOID",`
- ! L10175: `verdict="SEAL" if lane == "APEX" else "PROVISIONAL",`
- ! L10207: `verdict="SEAL",`
- ! L10233: `verdict="SEAL",`
- ! L10257: `verdict="VOID",`
- ! L10288: `verdict="SEAL",`
- ! L10298: `verdict="SEAL",`
- ! L10308: `verdict="SEAL",`
- ! L10321: `verdict="SEAL",`
- ! L10329: `verdict="VOID",`
- ! L10362: `verdict="HOLD",`
- ! L10383: `verdict="HOLD" if risk else "SEAL",`
- ! L10409: `verdict="SEAL",`
- ! L10428: `verdict="SEAL" if res.get("status") == "PRESERVED" else "HOLD",`
- ! L10450: `verdict="HOLD" if attacks else "SEAL",`
- ! L10474: `verdict="SEAL" if maruah_score >= 0.7 else "HOLD",`
- ! L10482: `verdict="VOID",`
- ! L10532: `verdict="SEAL" if res.get("forge_mode") != "paused" else "HOLD",`
- ! L10542: `verdict="SEAL"`
- ! L10556: `verdict="HOLD",`
- ! L10565: `verdict="SEAL" if not res.get("w6_triggered") else "HOLD",`
- ! L10575: `verdict="HOLD",`
- ! L10586: `verdict="SEAL",`
- ! L10594: `verdict="VOID",`
- ! L10643: `verdict="SEAL"`
- ! L10657: `verdict="HOLD",`
- ! L10668: `verdict="SEAL" if res.get("readiness") == "ADVISORY_READY" else "HOLD",`
- ! L10679: `verdict="SEAL"`
- ! L10691: `verdict="VOID",`
- ! L10725: `verdict="SEAL" if res.get("ok") else "HOLD",`
- ! L10736: `verdict="SEAL" if res.get("ok") else "HOLD",`
- ! L10747: `verdict="SEAL" if deps.get("vault_path_writable") else "HOLD",`
- ! L10757: `verdict="SEAL" if res.get("ok") else "HOLD",`
- ! L10768: `verdict="VOID",`
- ! L10801: `verdict="SEAL" if res.get("ok") else "HOLD",`
- ! L10812: `verdict="SEAL" if res.get("ok") else "HOLD",`
- ! L10822: `verdict="HOLD",`
- ! L10833: `verdict="SEAL" if res.get("ok") else "HOLD",`
- ! L10843: `verdict="SEAL" if res.get("ok") else "HOLD",`
- ! L10851: `verdict="VOID",`
- ! L10881: `verdict="SEAL" if h.get("verdict") in ("PASS", "WELL_PASS") else "HOLD",`
- ! L10896: `verdict="SEAL",`
- ! L10911: `verdict="SEAL" if pkt.get("ok") else "HOLD",`
- ! L10920: `verdict="SEAL",`
- ! L10941: `verdict="VOID",`
- ! L11149: `verdict="SEAL"`
- ! L11161: `verdict="SEAL" if res.get("consent_active") else "HOLD",`
- ! L11171: `verdict="SEAL",`
- ! L11183: `verdict="SEAL",`
- ! L11212: `verdict="VOID",`
- ! L11250: `verdict="HOLD",`
- ! L11264: `verdict="HOLD",`
- ! L11493: `verdict="HOLD",`
- ! L11505: `verdict="HOLD",`
- ! L11692: `verdict = "HOLD"`
- ! L11933: `verdict="HOLD",`
- ! L15041: `verdict="VOID",`
- ! L15082: `verdict="VOID",`
- ! L15365: `verdict="HOLD",`
- ! L15417: `verdict = "SEAL"`
- ! L15421: `verdict = "SEAL"`
- ! L15425: `verdict = "HOLD"`
- ! L15429: `verdict = "VOID"`
- ! L15592: `verdict="HOLD",  # medical queries always HOLD -- never auto-SEAL`
- ! L15636: `verdict="HOLD",`
- ! L15748: `verdict = "SEAL"`
- ! L15751: `verdict = "SEAL"`
- ! L15754: `verdict = "HOLD"`
- ! L15757: `verdict = "VOID"`
- ! L15902: `verdict = "SABAR"`
- ! L16000: `verdict = "SABAR"`
- ! L16030: `verdict = "SABAR"`
- ! L17540: `verdict="SEAL"`
- ! L17723: `verdict="SEAL" if g["g_well_verdict"] != "FRAGMENTED" else "HOLD",`

### `WELL/src/server.py`

- ! L269: `verdict="SEAL" if state.get("well_score", 0) > 60 else "HOLD",`

### `WELL/well_mcp/prompts/well_judge.py`

- ! L65: `- emit reflection with verdict="SABAR"`
- ! L70: `- emit reflection with verdict="HOLD"`
- ! L75: `- emit reflection with verdict="VOID"`

