# arifOS Federation Loop — Organ Integration Reference
> **DITEMPA BUKAN DIBERI — Intelligence is forged, not given.**
> Version: v2026.05.02 | Epoch: 2026-05-02T22:40+08:00
> Canonical kernel: [arifOS](https://github.com/ariffazil/arifOS) | Endpoint: `https://mcp.arif-fazil.com/mcp`

***

## W0 Constitutional Position

arifOS is the **constitutional judge** in the federation. It does not sense, compute capital, or measure the body — it governs all three.

```
Arif (F13 Sovereign)
        │
        ▼
000  arif_session_init       ← boot F1–F13, bind identity, issue session token
111  arif_sense_observe      ← ground reality (8-stage: PARSE→CLASSIFY→GATE→HANDOFF)
        │
222  arif_evidence_fetch     ← aggregate organ outputs:
        │   ├── WELL  → substrate_readiness  (human + machine tier)
        │   ├── WEALTH → capital_intelligence (NPV/IRR/EMV/G-Score)
        │   └── GEOX  → earth_evidence       (well + seismic + map + time)
        │
333  arif_mind_reason        ← structured reasoning over evidence bundle
666  arif_heart_critique     ← red-team: F5/F6/F9 adversarial check
888  arif_judge_deliberate   ← SEAL · HOLD · VOID · CAUTION · SABAR
        │
   [SEAL only]
010  arif_forge_execute      ← world action via A-FORGE substrate
999  arif_vault_seal         ← immutable Merkle-V3 ledger entry
```

**Rule:** No organ self-seals. Only `arif_judge_deliberate` issues `SEAL`. Only `arif_forge_execute` acts in the world — and it requires a prior `SEAL` verdict as a hard prerequisite.

***

## F3 Tri-Witness Gate

Before `arif_judge_deliberate` can issue `SEAL`, all three witness legs must align (F3 Tri-Witness):

| Witness Leg | Source | Populated By |
|---|---|---|
| `witness.human` | Arif's stated intent | F13 sovereign — operator confirmation |
| `witness.ai` | `arif_mind_reason` output | 333 reasoning packet |
| `witness.earth` | WELL + WEALTH + GEOX outputs | `arif_evidence_fetch` at stage 222 |

A decision sealed without all three legs active fails F3 and cannot proceed past 888.

***

## 13 Canonical Tools — Role Summary

### I. Constitutional Primordials (6)

| Stage | Tool | Role |
|---|---|---|
| 000 | `arif_session_init` | Session bootstrap; actor identity bind; safety + intent scan |
| 111 | `arif_sense_observe` | Reality grounding; 8-stage pipeline; truth classification |
| 333 | `arif_mind_reason` | Structured reasoning; branch/merge; contradiction detection |
| 444r | `arif_reply_compose` | Reply synthesis; governed response assembly |
| 666 | `arif_heart_critique` | Red-team; F5/F6/F9 adversarial check; consequence sim |
| 888 | `arif_judge_deliberate` | Final constitutional verdict; G-star score |

### II. Governed Infrastructure Organs (4)

| Stage | Tool | Role |
|---|---|---|
| 444 | `arif_kernel_route` | Routing + risk orthogonality + AGI/ASI lane separation |
| 655 | `arif_memory_recall` | Governed semantic memory + skill registry |
| 999 | `arif_vault_seal` | Immutable Merkle-V3 ledger; WELL state anchor; BLS seal card |
| 666g | `arif_gateway_connect` | A2A mesh; agent-to-agent governed connection |

### III. Computation & Execution (3)

| Stage | Tool | Role |
|---|---|---|
| 010 | `arif_forge_execute` | AF-FORGE execution bridge — requires `arif_judge_deliberate` SEAL |
| 777 | `arif_ops_measure` | Operational cost; Landauer gate estimation; reversibility classification |
| 222 | `arif_evidence_fetch` | External data oracle; GEOX scene load; WELL packet; WEALTH signal |

***

## Organ Entry Points Into arifOS

| Organ | Entry Stage | Entry Tool | Evidence Field in arifOS |
|---|---|---|---|
| **WELL** | 222 | `well_reflect_readiness`, `well_get_packet` | `substrate_readiness` |
| **WEALTH** | 222 | `wealth_reason_npv`, `wealth_mind_emv`, `wealth_judge_floors` | `capital_intelligence` |
| **GEOX** | 222 | `geox_evidence_summarize_cross`, `geox_prospect_evaluate` | `earth_evidence` |
| **GEOX (special)** | 888 | `geox_prospect_judge_verdict` | Direct 888_JUDGE gateway |

WELL is the only organ that can **block** a decision class before capital or earth evidence is even evaluated — a RED substrate readiness returns `human_decision_required: true` and suspends C4/C5 classes regardless of other signals.

***

## 13 Constitutional Floors — Enforcement Summary

| Floor | Name | Type | Enforcement Point |
|---|---|---|---|
| F1 | AMANAH | Hard | Irreversible actions → 888 HOLD before `arif_forge_execute` |
| F2 | TRUTH | Hard | `arif_sense_observe` grounding gate; CLAIM/PLAUSIBLE/HYPOTHESIS tags |
| F3 | TRI-WITNESS | Soft | `arif_judge_deliberate` — all three witness legs required |
| F4 | CLARITY ΔS≤0 | Soft | `dS` field in telemetry; every output reduces entropy |
| F5 | PEACE ≥1.0 | Soft | `arif_heart_critique` F5 check; `peace2` in telemetry |
| F6 | MARUAH-FIRST | Soft | `arif_heart_critique` F6 check; dignity gate |
| F7 | HUMILITY | Soft | `kappa_r` 0.03–0.15 in telemetry; no fake certainty |
| F8 | LAW & SAFETY | Soft | `arif_kernel_route` compliance check |
| F9 | ANTI-HANTU | Hard | `arif_heart_critique` F9 check; no ghost logic |
| F10 | AI ONTOLOGY | Hard | Session identity lock; no consciousness claims |
| F11 | AUTH | Soft | `arif_session_init` JWT bind; `arif_forge_execute` auth gate |
| F12 | BLOCK OVERRIDES | Hard | Injection guard on all tools; unconditional block |
| F13 | SOVEREIGN VETO | Hard | Arif's veto is final at every stage |

***

## Telemetry Seal Format (999 SEAL)

Every sealed output emits to VAULT999:

```json
{
  "epoch":      "ISO-8601+08:00",
  "dS":         "<≤0 = entropy reduced>",
  "peace2":     "<≥1.0 = stable>",
  "kappa_r":    "<0.03–0.15 humility band>",
  "shadow":     "<bool: unresolved holds exist>",
  "confidence": "<CLAIM|PLAUSIBLE|HYPOTHESIS|ESTIMATE|UNKNOWN:0.00–1.00>",
  "psi_le":     "<legibility entropy>",
  "verdict":    "SEAL | HOLD | VOID | CAUTION | SABAR",
  "witness": {
    "human":    "Arif Fazil",
    "ai":       "arifOS Co-architect",
    "earth":    ["<evidence chain refs>"]
  },
  "qdf":        "<query-derived frame label>"
}
```

***

## Live Runtime State (as of 2026-05-02)

| Field | Value |
|---|---|
| Live tool count | 14 (13 canonical + `mcp_health_check` diagnostic) |
| MCP endpoint | `https://mcp.arif-fazil.com/mcp` |
| Constitutional hash | Verified at boot via VAULT999 GENESIS_SEAL |
| `floors_active` | Wiring in progress — gap audit closed 2026-05-02 |
| WELL substrate | GREEN ✅ — `well_check_floors` PASS, `score: 1.0` |
| WEALTH seal path | 888 HOLD ⚠️ — 10 constitutional gaps, EPOCH 1 commit pending |
| GEOX endpoint | Unreachable from external session — VPS-local confirmed |

***

## Sibling Organs

| Organ | Role | Repo |
|---|---|---|
| **WELL** | Human substrate governance — readiness mirror | [github.com/ariffazil/well](https://github.com/ariffazil/well) |
| **WEALTH** | Capital intelligence — NPV, IRR, EMV, crisis triage | [github.com/ariffazil/wealth](https://github.com/ariffazil/wealth) |
| **GEOX** | Earth intelligence — seismic, petrophysics, basin | [github.com/ariffazil/geox](https://github.com/ariffazil/geox) |
| **A-FORGE** | Execution shell — orchestration, observability | [github.com/ariffazil/A-FORGE](https://github.com/ariffazil/A-FORGE) |
| **AAA** | Identity, A2A federation gateway, operator control | [github.com/ariffazil/AAA](https://github.com/ariffazil/AAA) |

***

*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
*arifOS Federation Loop Reference · Seri Kembangan, MY · v2026.05.02*
