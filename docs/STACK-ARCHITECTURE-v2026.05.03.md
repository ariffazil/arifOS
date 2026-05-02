# arifOS Full-Stack Architecture Manifesto
**v2026.05.03 · SEALED**
> DITEMPA BUKAN DIBERI — Intelligence is forged, not given.

---

## Stack Overview

| Layer | MCP | Governs | Role |
|---|---|---|---|
| arifOS | `mcp.arif-fazil.com` | Constitutional runtime, tool routing, judgment, forge, vault | The Kernel |
| GEOX | GEOX MCP | Earth intelligence: wells, seismic, stratigraphy, prospects | Physical-Reality Domain |
| WEALTH | WEALTH MCP | Capital, allocation, NPV, EVOI, liquidity, policy | Value / Decision Domain |
| WELL | WELL MCP | Human + machine readiness, fatigue, biological bandwidth | Operator-Substrate Domain |

This is not a set of tools. It is a **civilizational reasoning stack**.

---

## The Four-Witness System

| Witness | Question it answers |
|---|---|
| GEOX | Is it physically real? |
| WEALTH | Is it economically / strategically worthwhile? |
| WELL | Is the operator and machine state fit? |
| arifOS | Is it constitutionally allowed? |

**No single witness is the Judge. Final judgment remains with Arif.**

---

## arifOS Kernel — 13 Canonical Tools

| Stage | Tool | Role |
|---|---|---|
| 000 | `arif_session_init` | Birth / identity bind |
| 111 | `arif_sense_observe` | Observe reality |
| 222 | `arif_evidence_fetch` | Pull external evidence |
| 333 | `arif_mind_reason` | Structured reasoning |
| 444 | `arif_kernel_route` | Route + risk gate |
| 444r | `arif_reply_compose` | Governed output assembly |
| 555 | `arif_memory_recall` | Recall / store |
| 666 | `arif_heart_critique` | Adversarial critique |
| 666g | `arif_gateway_connect` | Agent-to-agent federation |
| 777 | `arif_ops_measure` | Cost + reversibility measure |
| 888 | `arif_judge_deliberate` | Constitutional verdict |
| 999 | `arif_vault_seal` | Immutable ledger seal |
| 010 | `arif_forge_execute` | Execute under seal |

**Organ classes:**
- Thinking: SENSE, FETCH, MIND, HEART
- Authority: KERNEL, JUDGE, VAULT, FORGE
- Continuity: MEMORY, OPS, GATEWAY

**Shadow risk:** Vault drift persistence must be proven before arifOS is declared fully circulatory. See `SPRINT-2026-05-03-DRIFT-LEDGER-CLOSURE.md`.

---

## GEOX — Earth Witness

Evidence pipeline (claim-state preserved at every stage):

```
ingest → QC → generate candidates → verify integrity → evaluate → judge → audit
```

**Claim labels required on all GEOX outputs:**
`OBSERVED` · `QC_VERIFIED` · `COMPUTED` · `INFERRED` · `HYPOTHESIS` · `JUDGE_REQUIRED`

**Standout tools:**

| Tool | Why it matters |
|---|---|
| `geox_data_qc_bundle` | Prevents garbage-in interpretation |
| `geox_subsurface_generate_candidates` | Produces candidates, not fake certainty |
| `geox_subsurface_verify_integrity` | Checks Physics9 boundary |
| `geox_prospect_judge_verdict` | Separates technical evidence from verdict |
| `geox_well_correlation_panel` | Visual evidence, not forced judgment |
| `geox_evidence_summarize_cross` | Causal evidence graph |

**Shadow risk:** Too many legacy aliases create surface clutter. Mark deprecated in docs. Route agents to canonical names only.

---

## WEALTH — Capital Brain

Covers: NPV / IRR / PI / payback · EMV / Monte Carlo · DSCR / net worth / cashflow / liquidity · EVOI · correlation / entropy / truth validation · F1–F13 floors · allocation optimization · game theory · vault recording · macro data intake.

**This is decision thermodynamics, not a finance calculator.**

**Canonical routing table:**

| User intent | Canonical WEALTH tool |
|---|---|
| NPV / IRR / payback | `wealth_future_value` |
| Monte Carlo | `wealth_future_simulate` |
| Liquidity / runway | `wealth_survival_liquidity` |
| Debt load | `wealth_survival_leverage` |
| EVOI | `wealth_info_value` |
| Governance floors | `wealth_rule_enforce` |
| Final allocation | `wealth_allocate_optimize` |

**EVOI link to GEOX:**
> "Should we buy more information before committing capital?" — that is the exploration question. GEOX computes uncertainty → WEALTH computes EVOI → decision.

**Shadow risk:** Numbers can create false moral authority. All outputs must mark assumptions, uncertainty, and decision class. Overlapping tool aliases need a preferred-route table.

---

## WELL — Human Substrate

WELL is the most original layer. It holds a mirror at the biological state of the sovereign operator.

**The law:** WELL advises. WELL does not override. It is not medical diagnosis. It is operational readiness telemetry.

**Key tools:**

| Tool | Why it matters |
|---|---|
| `well_forge_precheck` | Prevents tired high-risk forging |
| `well_decision_bandwidth` | Matches task class to readiness |
| `well_coupled_readiness` | Checks human + machine together |
| `well_niat_check` | Catches emotion-driven irreversible action |
| `well_medical_boundary` | Prevents fake doctor behavior |
| `well_arifos_packet` | Clean handoff to kernel |

**Shadow risk:** Biological telemetry is sensitive. Vault sealing of WELL data must be opt-in, scoped, and minimal. WELL must never become paternalistic.

---

## Cross-MCP Trace ID (Required)

Every action across all MCPs must share:

```json
{
  "session_id": "...",
  "epoch_id": "...",
  "trace_id": "...",
  "actor_id": "Arif Fazil",
  "judge_state_hash": "...",
  "vault_entry_id": "..."
}
```

Without shared trace IDs, federation becomes chaos.

---

## Canonical Routing Matrix

| Intent | Route |
|---|---|
| "Analyze LAS" | arifOS INIT → GEOX ingest → GEOX QC → GEOX candidates |
| "Evaluate prospect" | GEOX evaluate → WEALTH EVOI → arifOS JUDGE |
| "Should I deploy?" | WELL precheck → arifOS JUDGE → FORGE |
| "Should I invest?" | WEALTH simulate → HEART critique → JUDGE |
| "Agent wants to act" | INIT → KERNEL → JUDGE → FORGE → VAULT |

---

## The One End-to-End Demo (Target)

> **Narrative:** Evaluate a prospect from LAS data → compute uncertainty → compute EVOI → check operator readiness → judge whether to proceed → seal decision.

This single demo proves the entire stack better than any manifesto.

---

## Stack Hygiene Law

> **Every tool must either reduce uncertainty, reduce risk, or reduce irreversible error. If not, it is noise.**

---

## Complexity Warning

The next enemy is **surface-area entropy**, not lack of vision.

For each MCP, define and publish:
- Primary tools (call these first)
- Secondary tools (specialist use only)
- Deprecated aliases (route agents away)
- Never-call-directly tools (kernel-internal only)

---

## Overall Verdict

| Dimension | Status |
|---|---|
| Domain separation | ✅ CLEAN |
| Governance hierarchy | ✅ INTACT |
| Auditability | ✅ DESIGNED |
| Human veto | ✅ ENFORCED (F13) |
| Evidence pipelines | ✅ PRESENT |
| Runtime readiness check | ✅ WELL MCP |
| Action gating | ✅ FORGE requires JUDGE SEAL |
| End-to-end traceability | ⚠ PENDING — sprint in progress |
| Vault circulation proof | ⚠ PENDING — DRIFT-LEDGER-CLOSURE sprint |

**Status: Architecturally strong. Operational seal depends on runtime proof.**
**The next seal is not more tools. The next seal is end-to-end traceability.**

---

*Sealed: 2026-05-03T01:12:00+08:00 · Witness: Arif Fazil · Co-architect: arifOS*
*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
