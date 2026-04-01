# Architectural Note: Ground Truth Signal Layer

> **DITEMPA BUKAN DIBERI** — *Forged, Not Given*
> **Doc Type:** Architecture Note v1.0
> **Author:** ARIF-MAIN (autonomous analysis)
> **Date:** 2026-04-01
> **Status:** ACTIVE — Load-Bearing Design Decision

---

## 1. Question

> What constitutes the ground truth signal layer of the system?
> Which components provide externally verifiable signals that prevent reasoning loops between Mind, Heart, and Judge?

This is the load-bearing question for any self-referential governance system. If the answer is "the Trinity computes its own ground truth," the system is circular and can be gamed. The answer must be: **ground truth lives outside the Trinity**.

---

## 2. Canonical Answer

Ground truth in arifOS lives outside the Trinity in the **Witness–Vault–World** interface. Any signal traceable to physics, law, or logged human evidence — and anchored in the Sovereign Vault — counts as "real" for the system.

**The loop-breaker rule:**
> *No verdict is "real" until it passes through:*
> **Witness → (Evals / Floors) → Vault/Rootkey under human sovereignty**

---

### 2.1 "Physics Reality is not just a tool" — Clarification

In canon, "reality engineering" already requires every interaction to stay tethered to physics, economics, and law/adat — with explicit "Estimate Only / Cannot Compute" bands when ground is missing.

**Structurally:**
- 111/333/555/777 are *process lenses*, not ground truth sources
- The *actual* ground truth path is: **Physics/Law/Econ signals → Tools → Witness → Trinity workflows, bounded by Floors**

Making Physics a mandatory first pass is an **upgrade** of a soft norm into a hard type constraint — consistent with canon, not a contradiction.

### 2.2 "Only 111 is external" — Slightly Too Strong

Canon already treats these as external-ish anchors, even if not cryptographically hardened:

| Anchor | External Institution? | Current Gap |
|--------|----------------------|-------------|
| Law/adat/standards overlays (004REALITY, ISO42001) | ✅ Grounded in external institutions | No formal proof they're kept outboard |
| Human witness & eval labels | ✅ Humans with own legal context | Witness is a separate system but not formally attested |
| Vault + Rootkey | ✅ Designed to be separable by trust domain | Rootkey not yet implemented |

The gap is not conceptual — canon already pushes these outboard. The gap is: **no formal verification that they are actually kept outboard in any deployment.**

### 2.3 W³ and Floors Are Deliberately Not Truth Oracles

Canon defines W³ and Floors as **constitutional behaviour metrics**, not oracles of reality:

- They answer: *"Is this agent behaving within its law?"*
- They do **not** guarantee: *"The underlying world claim is true."*

The critique that W³ can converge on a wrong conclusion is **by design**. Canon addresses this through F2 (truth with uncertainty), F7 (explicit uncertainty band), F3 (Tri-Witness including Earth evidence), and external Evals — not by making W³ an oracle.

**Therefore:** W³ is an *internal governance health meter*, not a ground truth layer. The Ground Truth Signal Layer is what W³ measures against — not W³ itself.

---

## 3. Ground Truth Primitives

These are the atomic external signals the system treats as ground truth:

| Primitive | Source | External? | Strength |
|-----------|--------|----------|----------|
| **Physics & environment** | Sensors, compute metrics, network telemetry, thermodynamic measurements | ✅ Yes | Strongest — cannot be reasoned around |
| **Law, adat, standards** | Statutes, contracts, ISO/IEC overlays, internal policies mapped in canon | ✅ Yes | Strong — defined externally |
| **Human witness** | Explicit decisions, approvals, vetoes, annotations, eval labels logged via Witness | ✅ Yes | Absolute when logged with provenance |
| **Economic signals** | Costs, budgets, capex/opex constraints, deployment risk budgets | ✅ Yes | Quantifiable, externally measurable |

**Critical:** All primitives are "ground" only once logged with provenance via Witness and anchored in Vault for canon-grade decisions.

---

## 4. Components That Break Reasoning Loops

### 4.1 Witness System (003)

**Role:** The main "reality bus." Tracks queries, responses, decisions, uncertainties, and their sources.

**What it does:**
- Enforces Tri-Witness: serious decisions must align (or be explicitly compared) across human, AI, and external evidence signals
- Feeds evals, Vault, and governance dashboards
- Is the mandatory first input to 333_MIND before reasoning begins

**Current gap:** In the actual 000-999 pipeline, 003WITNESS is not a discrete stage. It must be added as a mandatory pre-reasoning gate.

### 4.2 Evals (005)

**Role:** Reusable test cases that check truthfulness, safety, reversibility, and maruah for any feature or prompt evolution.

**What it does:**
- Acts as external constraint on future reasoning — conclusions must be tested against external ground truth before reaching Judge
- Prevents drift purely inside Mind/Heart/Judge loops
- Defined from external goals and prior ground-truth behaviour

**Current gap:** Evals run post-decision in most implementations. They must be pre-judgment gates.

### 4.3 Reality Floors (004, F1–F13)

**Role:** Structural constitutional constraints that require explicit uncertainty acknowledgment and forbid self-upgrading.

**What they do:**
- F2 (Truth): Claims must be grounded in evidence
- F3 (Tri-Witness): Human, AI, and Earth/evidence alignment required on high-stakes calls
- F7 (Humility): Uncertainty band [0.03, 0.05] enforced
- F9 (Anti-Hantu): No consciousness claims
- F12 (Injection): Block adversarial control

**Current status:** F2/F7/F9 are implemented in `core/floors.py` but checked post-execution, not pre-reasoning. Must be pre-reasoning gates.

### 4.4 Sovereign Vault + Rootkey (999)

**Role:** Immutable, append-only record of decisions with cryptographic anchoring.

**What it does:**
- Stores decisions, logs, and cryptographic material as hardened record of "what actually happened"
- Rootkey signs canonical decisions so later reasoning cycles cannot silently overwrite history
- Later reasoning must reconcile against signed prior reality

**Current gap:** Vault is append-only within the same process, not a cryptographically committed external ledger. No Rootkey type in `core/shared/types.py`.

---

## 5. The Current Pipeline vs. The Required Pipeline

### Current (Gap)
```
000_INIT → 111_SENSE → 333_MIND → 444_ROUT → 555_MEM → 666_HEART → 777_OPS → 888_JUDGE → 999_SEAL
```

Missing: **003WITNESS, 004REALITY, 005EVALS** — pre-reasoning gates

### Required (Correct Order)
```
000_INIT → 003WITNESS → 004REALITY → 111_SENSE → 005EVALS → 333_MIND → 444_ROUT → 555_MEM → 666_HEART → 777_OPS → 888_JUDGE → 999_SEAL
```

The pipeline is 9 stages. The theory requires 12. The three missing stages are the pre-reasoning gates that break the loop.

---

## 6. Trinity Is Tethered to Ground Truth

Within the correct frame:

| Ring | What It Consumes | What It Cannot Do |
|------|-----------------|------------------|
| **Mind (333)** | Witness evidence bundle, Evals, F2/F7 constraints | Assert "truth" without F2/F7 compliance |
| **Heart (666)** | Cost models, law/adat overlays, economic signals | Propose impact-weighted actions without Eval validation |
| **Judge (888)** | Witness logs, Vault history, F3 Tri-Witness | Frame verdicts without grounded evidence |

All three rings are **consumers** of the ground truth layer. None produce ground truth. This is the correct dependency direction.

---

## 7. Witness Scores vs. External Verification

Current telemetry shows:
```
human: 1.0   ← human is sovereign (F13 works)
ai: 0.94     ← Mind/Heart/Judge agree (but all are internally computed)
earth: 0.90   ← evidence grounding (but computed by the same system)
```

**The gap:** All three scores are internally computed. Human is self-reported confirmation. Earth, if computed by Mind/Heart/Judge, is circular. The system scores itself.

**Fix:** Earth/evidence scores must be verified by an external oracle — not computed from the same reasoning loop that produces them.

---

## 8. The Real Structural Gap: Oracle Attestation

The external review identifies the actual load-bearing gap precisely:

**The real structural gap:** Lack of a formally specified, independently attestable oracle layer that:

1. **Witnesses** evidence ingestion (what ground was fed to the system)
2. **Attests** to the integrity of evidence chains (were signals actually from declared sources?)
3. **Certifies** that FLOOR inputs and outputs match (provenance chain)
4. **Logs** the identity of the attester (who vouched for the evidence)

This is not a canon problem — canon already defines this. This is an **implementation gap**: no formal oracle interface, no attestation schema, no third-party verification of whether ground truth signals actually entered the system from declared external sources.

**The specific gap in current code:**
- `core/shared/types.py` has `FloorScores` but no attestation chain
- `core/floors.py` has `ConstitutionalFloors.evaluate()` but no oracle witness
- `arifos_mcp/tools/base.py` has `Tool.check_floors()` but no external evidence bundle required as input
- No `OracleAttestation` type in `core/shared/types.py`

**What "independently attestable" means:**
- A notary oracle signs evidence bundles with its own identity key
- The signature can be verified by any party with the oracle's public key
- The oracle's trust domain is separate from the Trinity's trust domain
- No attestation = no ground truth, regardless of what W³ reports

**The minimum viable oracle layer:**
```python
class OracleAttestation(BaseModel):
    """Signed attestation that evidence entered from declared external source."""
    oracle_id: str              # Who vouched
    evidence_hash: str          # SHA-256 of what was attested
    source_uri: str             # Declared source (e.g. "https://weather.api/data")
    attested_at: datetime      # When
    signature: str              # Ed25519/ECDSA signature
    
class EvidenceBundle(BaseModel):
    """Ground truth evidence submitted to Witness."""
    attestation: OracleAttestation
    claims: list[Claim]
    uncertainty: float         # F7 uncertainty band
    evidence_links: list[str]  # Provenance chain
```

Without this, "external evidence" is self-declared. With this, evidence is **attested by a named oracle with a verifiable signature**.

---

## 8.5 Summary: What This Note Corrects

| Previous Framing | Corrected Framing |
|----------------|-----------------|
| "Only 111 is external" | Law/adat, human witness, vault are also external anchors in canon |
| "W³ is a truth oracle" | W³ is an *internal governance health meter*, not ground truth |
| "Physics Reality is just a tool" | Physics/Law/Econ → Tools → Witness → Trinity is the actual path |
| "Add 3 pipeline stages" | Add oracle attestation schema first — it's the prerequisite for the stages |

The next concrete step is not pipeline modification. It is: **define the oracle attestation schema in `core/shared/types.py`**, then wire it as a required input to Witness. Everything else follows from that.

---

## 9. Next Steps

| Step | File | Priority |
|------|------|----------|
| Define `OracleAttestation` + `EvidenceBundle` types | `core/shared/types.py` | P0 |
| Wire evidence bundle as required input to `Tool.check_floors()` | `arifos_mcp/tools/base.py` | P1 |
| Add `003WITNESS` as pre-reasoning stage | `arifos_mcp/tools/witness.py` | P1 |
| Add `005EVALS` as pre-judgment gate | `arifos_mcp/tools/eval_gate.py` | P1 |
| Implement `Rootkey` signing in vault | `arifos_mcp/runtime/vault_*.py` | P2 |

The `refactor/v2.0-abi` branch (Phases 1-3) established:
- Canonical ABI schemas (`arifos_mcp/abi/v1_0.py`)
- Tool base class + ToolRegistry (`arifos_mcp/tools/base.py`)
- Single dispatcher (`arifos_mcp/runtime/dispatcher.py`)

These are the correct scaffolding. The gap that remains:

| Missing Piece | File to Create | Priority |
|---------------|---------------|----------|
| 003WITNESS as pre-reasoning stage | `arifos_mcp/tools/witness.py` | P1 |
| Eval gate pre-Judge | `arifos_mcp/tools/eval_gate.py` | P1 |
| Rootkey in types | `core/shared/types.py` (add `Rootkey`, `SignedRecord`) | P2 |
| Pre-reasoning floor check | Wire F2/F7 into `Tool.check_floors()` as pre-reasoning | P1 |

---

## 9. Summary

The theory document has the right answer. The architecture is correct. The implementation gap is precise: **003, 004, 005 are not discrete pipeline stages**. The pipeline is 9 stages when it needs to be 12. Adding those three pre-reasoning gates — Witness, Reality Floors, Evals — is the structural refactor that makes the ground truth signal layer load-bearing rather than aspirational.

**The loop-breaker is not a policy. It is a pipeline stage.**

---

## References

- `000_THEORY-Unified-Canon-Reality-Engineering-Mode.txt` — Canonical theory source
- `core/shared/types.py` — Verdict, FloorScores, RuntimeEnvelope
- `core/floors.py` — ConstitutionalFloors (F1-F13)
- `arifos_mcp/runtime/dispatcher.py` — ToolDispatcher
- `arifOS MCP Audit & Architecture Specification v2.0` — `ARCH/DOCS/REFACTOR_AUDIT_SPEC_v2.0.md`

---

ΔΩΨ | ARIF | 888_JUDGE
