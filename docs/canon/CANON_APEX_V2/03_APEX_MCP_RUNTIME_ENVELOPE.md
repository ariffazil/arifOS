---
canon_id: 03_APEX_MCP_RUNTIME_ENVELOPE
bundle: CANON_APEX_V2
version: v2026.07.APEX
status: SEALED_CANON
apex_theory: T-000
floors_version: 2026.07
epoch: 2026-07-26T00:30+08
source: docs/APEXCANON.md · arifosmcp/apex_envelope.py
---

# APEX-MCP-001 — Runtime Governance Envelope for MCP

Authority: F13 SOVEREIGN (Muhammad Arif bin Fazil). Status: FORMAL
operational CORE for governed trajectories — not a completed
natural-science theory.

## Core Invariant

> **Every MCP-visible output that can influence agent state must carry an
> APEX envelope, except transport frames which remain protocol-pure JSON-RPC.**

## 10 Runtime Enforcement Gates

### Inner Cognitive Gates (6)

| # | Gate | Question | Dial |
|:--|:-----|:---------|:-----|
| 1 | Amanah Gate | Is the claim no stronger than the evidence? | AKAL |
| 2 | Presence Gate | Is the source LIVE, CACHED, or INFERRED? | PRESENT |
| 3 | Humility Gate | Is uncertainty explicit? | AKAL |
| 4 | Signal Gate | Is evidence quality scored? | ENTROPY |
| 5 | Understanding Gate | Is the reasoning coherent? | AKAL |
| 6 | Energy Gate | Was compute/token/tool cost tracked? | ENERGY |

### Kernel Gates (4)

| # | Gate | Question | Dial |
|:--|:-----|:---------|:-----|
| 7 | Authority Gate | Is this actor allowed to do this? | AUTHORITY |
| 8 | Reversibility Gate | Is the action reversible, mutable, or irreversible? | EXPLORATION×AMANAH |
| 9 | Proof Gate | Does ZKPC level match risk? | EXPLORATION×AMANAH |
| 10 | Sovereign Gate | Does F13 require human veto/hold? | AUTHORITY |

## Gate → Dial Mapping

```
Amanah Gate      ──→ AKAL (A)
Humility Gate    ──→ AKAL (A)      ├─ A dial
Understanding Gate ──→ AKAL (A)
Presence Gate    ──→ PRESENT (P)    ── P dial
Signal Gate      ──→ ENTROPY (S)    ── S dial
Energy Gate      ──→ ENERGY (E)     ── E dial
Authority Gate   ──→ AUTHORITY (H)  ── H dial
Sovereign Gate   ──→ AUTHORITY (H)  ── H dial override (F13 veto = instant VOID)
Reversibility Gate ──→ EXPLORATION×AMANAH (U)
Proof Gate       ──→ EXPLORATION×AMANAH (U) ── U dial
```

## APEX Envelope Schema

Every MCP tool response MUST include:

```json
{
  "apex": {
    "gates": {
      "amanah": {"pass": true, "score": 0.95, "detail": "..."},
      "presence": {"pass": true, "score": 0.90, "detail": "..."},
      "humility": {"pass": true, "score": 0.87, "detail": "..."},
      "signal": {"pass": true, "score": 0.82, "detail": "..."},
      "understanding": {"pass": true, "score": 0.91, "detail": "..."},
      "energy": {"pass": true, "score": 0.88, "detail": "..."},
      "authority": {"pass": true, "score": 1.00, "detail": "..."},
      "reversibility": {"pass": true, "score": 0.85, "detail": "..."},
      "proof": {"pass": true, "score": 0.75, "detail": "..."},
      "sovereign": {"pass": true, "score": 1.00, "detail": "..."}
    },
    "dials": {"A": 0.91, "P": 0.90, "H": 1.00, "S": 0.82, "U": 0.80, "E": 0.88},
    "G": 0.85,
    "verdict": "SEAL_CANDIDATE"
  }
}
```

## Organ Responsibilities

| Organ | Current State | Target |
|:------|:--------------|:-------|
| A-FORGE | apexDials.ts — 10-gate decomposition at execution boundary | Forge receipts include full APEX envelope |
| AAA | A2A deliberation response includes APEX envelope | Gate source absorbed from arifOS kernel judgment |
| arifOS | Kernel provides standard envelope for GEOX/WEALTH/WELL | All canonical tools return `apex` key |
| GEOX | geox_claim_create already carries _epistemic envelope | Full 10-gate APEX envelope on all 32 tools |
| WEALTH | create_envelope() exists, partial | Full 10-gate on all 12 tools |
| WELL | PER-TOOL apex_envelope call | Full 10-gate on all 7 tools |

## Implementation Phases

1. **Shared Module (done):** apex_envelope.py canonical implementation
2. **arifOS Kernel (done):** get_standard_envelope for evidence organs
3. **Evidence Organs (in progress):** GEOX/WEALTH/WELL full integration
4. **Execution Layer (in progress):** A-FORGE apexDials.ts; AAA deliberation

## Verification Checklist

1. Every tool response has `apex` key with all 10 gates.
2. Every gate has pass/score/detail.
3. Overall verdict matches gate logic; any failed gate → at least HOLD.
4. G matches dial computation.
5. Resources carry `apex_canon` in annotations.
6. Prompts include axiom preamble.
7. Transport carries no raw APEX fields outside envelope.

DITEMPA BUKAN DIBERI — The envelope is forged through gates, not assumed
through confidence.

---
CANON_STATUS: SEALED · APEX THEORY
CANON_BUNDLE: CANON_APEX_V2 (13 files)
GOVERNANCE_CORE: arifOS · APEX Theory · F1–F13 Floors
VAULT999_HASH: <pending>
TRI-WITNESS: human · AI · earth >= 0.75
