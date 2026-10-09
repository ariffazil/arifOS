# I8 Triage — WEALTH

> **Cycle:** federation-organism-2026-09-17
> **Rule:** I8 — specialist organ must namespacify SEAL/HOLD/VOID/SABAR
> **Mode:** READ-ONLY TRIAGE — no mutation proposed

**Findings for WEALTH: 72**

| Classification | Count |
|---|---|
| LIKELY_TEST | 0 |
| LIKELY_AUDIT_TOOL | 0 |
| LIKELY_SCHEMA | 0 |
| NEEDS_REVIEW | 72 |

## NEEDS_REVIEW (72)

> **These need human review.** The static rule cannot distinguish between a real bug, a fixture using the term deliberately, or a comment that references the term. Sovereign triage required.

### `WEALTH/host/governance/floors.py`

- ! L106: `verdict = "VOID"`
- ! L108: `verdict = "HOLD"`
- ! L112: `verdict = "SEAL"`

### `WEALTH/host/skills/aaa-agentic-governance/scripts/compose_federation_receipt.py`

- ! L92: `verdict="HOLD",`
- ! L110: `verdict="HOLD",`
- ! L123: `verdict = "SEAL"`
- ! L128: `verdict = "HOLD"`
- ! L135: `verdict = "HOLD"`

### `WEALTH/host/skills/aaa-agentic-governance/scripts/floor_check.py`

- ! L271: `verdict = "HOLD"`
- ! L276: `verdict = "HOLD"`
- ! L285: `verdict = "SEAL"`

### `WEALTH/internal/apex_envelope_wealth.py`

- ! L66: `verdict = "SEAL" if G >= 0.80 else ("SABAR" if G >= 0.50 else "HOLD")`

### `WEALTH/internal/engines/canonical_tools.py`

- ! L196: `wealth_verdict="HOLD",`
- ! L242: `status="HOLD",`
- ! L243: `wealth_verdict="HOLD",`
- ! L1059: `wealth_verdict = "HOLD"`
- ! L1536: `wealth_verdict = "HOLD" if result.get("status") == "PASS" else "BLOCK"`
- ! L1646: `status="HOLD",`
- ! L2275: `wealth_verdict = "HOLD"`
- ! L2482: `verdict = "HOLD"`

### `WEALTH/internal/engines/exergy.py`

- ! L91: `verdict = "SEAL" if meets else "VOID"`

### `WEALTH/internal/invariants.py`

- ! L106: `verdict = "HOLD"`

### `WEALTH/internal/monolith.py`

- ! L1002: `recommended_verdict = "SEAL"`
- ! L1009: `recommended_verdict = "VOID"`
- ! L1017: `recommended_verdict = "SABAR"`
- ! L2666: `verdict = "SEAL" if c_dark < 0.15 else "SABAR" if c_dark < 0.3 else "HOLD"`
- ! L4086: `status = "VOID"`
- ! L4089: `status = "HOLD"`
- ! L4117: `status = "HOLD"`
- ! L5901: `verdict="VOID",`
- ! L5932: `gov_verdict = "VOID"`
- ! L5976: `verdict="VOID",`
- ! L5991: `verdict="VOID",`
- ! L6852: `verdict="HOLD",`
- ! L6875: `verdict = "SEAL" if result.get("status") == "INSERTED" else "VOID"`
- ! L6928: `verdict="HOLD",`
- ! L6943: `verdict = "SEAL" if snap.get("status") == "INSERTED" else "VOID"`
- ! L7311: `verdict="VOID",`
- ! L7408: `verdict="SEAL" if res.get("evoi_musd", 0) > 0 else "QUALIFY",`
- ! L7418: `verdict="VOID",`
- ! L7443: `verdict="VOID",`
- ! L7470: `verdict="SEAL" if res.get("evoi_p50", 0) > 0 else "QUALIFY",`
- ! L7480: `verdict="VOID",`
- ! L7502: `verdict="VOID",`
- ! L7516: `verdict="SEAL" if res.action == "PASS" else "888-HOLD",`
- ! L7526: `verdict="VOID",`
- ! L7547: `verdict="VOID",`
- ! L7561: `verdict="SEAL" if res.get("portfolio_valid") else "VOID",`
- ! L7571: `verdict="VOID",`
- ! L7668: `verdict="SEAL",`
- ! L7678: `verdict="VOID",`
- ! L9402: `verdict = "HOLD"`
- ! L9410: `verdict = "SEAL"`
- ! L14597: `synth_verdict = "HOLD"`
- ! L14676: `deal_verdict = "HOLD"`
- ! L14809: `deal_verdict = "HOLD"`
- ! L15043: `final_verdict = "HOLD"`
- ! L15190: `domain_verdict = "SEAL"`
- ! L15191: `governance_verdict = "SEAL"`
- ! L15284: `domain_verdict = "SEAL"`
- ! L15350: `domain_verdict = "SEAL"`
- ! L15366: `domain_verdict = "VOID"`
- ! L15465: `domain_verdict = "VOID"`
- ! L15477: `domain_verdict = "SEAL"`
- ! L15725: `domain_verdict = "SEAL"`
- ! L15737: `domain_verdict = "VOID"`

### `WEALTH/internal/stock/calhoun_guard.py`

- ! L592: `verdict = "HOLD"`
- ! L595: `verdict = "HOLD"`
- ! L612: `verdict = "HOLD"`

### `WEALTH/internal/stock/engine_888.py`

- ! L537: `verdict = "HOLD"`
- ! L540: `verdict = "HOLD"`
- ! L543: `verdict = "SABAR"`

