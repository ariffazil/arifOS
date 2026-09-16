# I8 Triage — HERMES

> **Cycle:** federation-organism-2026-09-17
> **Rule:** I8 — specialist organ must namespacify SEAL/HOLD/VOID/SABAR
> **Mode:** READ-ONLY TRIAGE — no mutation proposed

**Findings for HERMES: 16**

| Classification | Count |
|---|---|
| LIKELY_TEST | 0 |
| LIKELY_AUDIT_TOOL | 8 |
| LIKELY_SCHEMA | 0 |
| NEEDS_REVIEW | 8 |

## LIKELY_AUDIT_TOOL (8)

> **Likely audit/compliance tooling.** Tools that explicitly check constitutional compliance. The vocabulary is the audit subject.

### `HERMES/skills/domains/general/apex/recursive-audit/ASI-agentic-governance/scripts/compose_federation_receipt.py`

- ! L91: `verdict="HOLD",`
- ! L109: `verdict="HOLD",`
- ! L122: `verdict = "SEAL"`
- ! L127: `verdict = "HOLD"`
- ! L134: `verdict = "HOLD"`

### `HERMES/skills/domains/general/apex/recursive-audit/ASI-agentic-governance/scripts/floor_check.py`

- ! L270: `verdict = "HOLD"`
- ! L275: `verdict = "HOLD"`
- ! L284: `verdict = "SEAL"`

## NEEDS_REVIEW (8)

> **These need human review.** The static rule cannot distinguish between a real bug, a fixture using the term deliberately, or a comment that references the term. Sovereign triage required.

### `HERMES/profiles/aaa-hermes/skills/forge-vss-verifier-suite/forge_vss_verifier_suite.py`

- ! L478: `overall_verdict = "HOLD"`
- ! L482: `overall_verdict = "HOLD"  # mixed`

### `HERMES/scripts/apex-zen-bridge-score.py`

- ! L203: `verdict = 'SEAL' if G >= 0.80 else ('SABAR' if G >= 0.70 else 'HOLD')`

### `HERMES/scripts/apex-zen-paths.py`

- ! L102: `verdict='SEAL' if d1['G'] >= 0.80 else 'SABAR',`
- ! L112: `G=d2['G'], dials={k: round(d2[k], 4) for k in 'APEX'}, verdict='SABAR',`
- ! L124: `verdict='SEAL' if d3['G'] >= 0.80 else 'SABAR',`

### `HERMES/skills/forge-vss-verifier-suite/forge_vss_verifier_suite.py`

- ! L478: `overall_verdict = "HOLD"`
- ! L482: `overall_verdict = "HOLD"  # mixed`

