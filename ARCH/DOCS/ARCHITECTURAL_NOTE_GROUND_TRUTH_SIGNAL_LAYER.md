# Architectural Note: Ground Truth Signal Layer

> **DITEMPA BUKAN DIBERI** — *Forged, Not Given*
> **Doc Type:** Architecture Note v1.0
> **Author:** ARIF-MAIN (autonomous analysis)
> **Date:** 2026-04-01
> **Status:** ACTIVE — Load-Bearing Design Decision
> **Forge Label:** v48 Ground Truth Oracle Layer; ΔS≈-0.4; Ψ_LE≈1.10 (Estimate Only)
> **Scope:** This note cross-cuts 000_ARCHITECTURE, 003_WITNESS, 999_SOVEREIGNVAULT. Does NOT change LAW. LAW/FLOORS evolution only after oracle spec is stable.

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

## 3. Framing Corrections

The following corrections refine earlier informal analysis to match canon precisely.

### 3.1 Physics Reality Is Not "Just a Tool"

In canon, "reality engineering" already requires every interaction to stay tethered to physics, economics, and law/adat — with explicit "Estimate Only / Cannot Compute" bands when ground is missing.

**Structurally:**
- 111/333/555/777 are *process lenses*, not ground truth sources
- The *actual* ground truth path is: **Physics/Law/Econ signals → Tools → Witness → Trinity workflows, bounded by Floors**

Making Physics a mandatory first pass is an **upgrade** of a soft norm into a hard type constraint — consistent with canon, not a contradiction.

### 3.2 "Only 111 Is External" Is Slightly Too Strong

Canon already treats these as external-ish anchors, even if not cryptographically hardened:

| Anchor | External Institution? | Current Gap |
|--------|---------------------|-------------|
| Law/adat/standards overlays (004REALITY, ISO42001) | ✅ Grounded in external institutions | No formal proof they're kept outboard |
| Human witness & eval labels | ✅ Humans with own legal context | Witness is separate system but not formally attested |
| Vault + Rootkey | ✅ Designed to be separable by trust domain | Rootkey not yet implemented |

The gap is not conceptual — canon already pushes these outboard. The gap is: **no formal verification that they are actually kept outboard in any deployment.**

### 3.3 W³ Is an Internal Governance Health Meter, Not a Truth Oracle

Canon defines W³ and Floors as **constitutional behaviour metrics**, not oracles of reality:

- They answer: *"Is this agent behaving within its law?"*
- They do **not** guarantee: *"The underlying world claim is true?"*

The critique that W³ can converge on a wrong conclusion is **by design**. Canon addresses this through F2 (truth with uncertainty), F7 (explicit uncertainty band), F3 (Tri-Witness including Earth evidence), and external Evals — not by making W³ an oracle.

---

## 4. Ground Truth Primitives

These are the atomic external signals the system treats as ground truth:

| Primitive | Source | External? | Strength |
|-----------|--------|-----------|---------|
| **Physics & environment** | Sensors, compute metrics, network telemetry, thermodynamic measurements | ✅ Yes | Strongest — cannot be reasoned around |
| **Law, adat, standards** | Statutes, contracts, ISO/IEC overlays, internal policies mapped in canon | ✅ Yes | Strong — defined externally |
| **Human witness** | Explicit decisions, approvals, vetoes, annotations, eval labels logged via Witness | ✅ Yes | Absolute when logged with provenance |
| **Economic signals** | Costs, budgets, capex/opex constraints, deployment risk budgets | ✅ Yes | Quantifiable, externally measurable |

**Critical:** All primitives are "ground" only once logged with provenance via Witness and anchored in Vault for canon-grade decisions.

---

## 5. Components That Break Reasoning Loops

### 5.1 Witness (003)

**Role:** The main "reality bus." Tracks queries, responses, decisions, uncertainties, and their sources.

**What it does:**
- Enforces Tri-Witness: serious decisions must align (or be explicitly compared) across human, AI, and external evidence signals
- Feeds evals, Vault, and governance dashboards

**Current gap:** In canon, Witness is specified as a logging/audit primitive — not a discrete pipeline stage with mandatory attestation.

### 5.2 Evals (005)

**Role:** Reusable test cases that check truthfulness, safety, reversibility, and maruah.

**What it does:**
- Acts as external constraint on future reasoning — conclusions must be tested against external ground truth before reaching Judge
- Prevents drift purely inside Mind/Heart/Judge loops

**Current gap:** Evals run post-decision in most implementations, advisory not structural.

### 5.3 Reality Floors (004, F1–F13)

**Role:** Structural constitutional constraints requiring explicit uncertainty acknowledgment and forbidding self-upgrading.

**What they do:**
- F2 (Truth): Claims must be grounded in evidence
- F3 (Tri-Witness): Human, AI, and Earth/evidence alignment required on high-stakes calls
- F7 (Humility): Uncertainty band [0.03, 0.05] enforced
- F9 (Anti-Hantu): No consciousness claims
- F12 (Injection): Block adversarial control

**Current status:** F2/F7/F9/F12 implemented in `core/floors.py` but checked post-execution.

### 5.4 Sovereign Vault + Rootkey (999)

**Role:** Immutable, append-only record of decisions with cryptographic anchoring.

**What it does:**
- Stores decisions, logs, and cryptographic material as hardened record of "what actually happened"
- Rootkey signs canonical decisions so later reasoning cycles cannot silently overwrite history

**Current gap:** Vault is append-only within the same process — not cryptographically committed externally. No Rootkey type in `core/shared/types.py`.

---

## 6. The v47 vs v48 Distinction

| | v47 (current canon) | v48 (proposed) |
|--|---------------------|----------------|
| **Floors F1-F13** | ✅ Canonical | Unchanged |
| **Tri-Witness W³** | ✅ Defined | Unchanged |
| **Witness** | Logging/audit primitive | Discrete pipeline stage with mandatory attestation |
| **Vault** | Append-only record | Cryptographically committed + oracle bundle reference |
| **Human Sovereign** | Manual F13 override | Structured with signed approvals |
| **Evidence ingestion** | Via tool call (convention) | Via oracle layer with proof type |
| **Trust domain** | All in same runtime | Oracle + Vault target separate domain |

**v47 is consistent with itself.** The gap is that v47 specifies Witness/Vault/Tri-Witness as concepts without mandating the attestation infrastructure that makes them externally verifiable.

---

## 7. The v48 Direction: Ground Truth Oracle Layer

### 7.1 Scope

This section is **design sketch, not canon change**. It describes the v48 direction. LAW/FLOORS evolution only after oracle spec is stable.

### 7.2 Oracle Sits Outside Trinity + Constitutional Kernel

Oracle feeds:
- Grounded facts (Physics/Law/Econ)
- Eval outcomes
- Tool-call legitimacy
- Floor score audits

And commits state to Vault with cryptographic guarantees and external observability.

### 7.3 Proposed Canon File: `006_ORACLESPEC.md`

Define "Ground Truth Oracle Layer" as distinct from Witness and Trinity.

**Oracle classification:**
| Type | Examples | Proof Type |
|------|---------|-----------|
| Physics | Infra metrics, test results, sensors | Merkle path + timestamp |
| Law | Signed policies, statutes, ISO overlays | ECDSA signature |
| Econ | Cost accounting, budget attestation | Hash chain |
| Human | Signed approvals, eval labels | Ed25519 signature |

**Minimum proof requirements by risk class:**
| Risk | Minimum Proof |
|------|--------------|
| Low | Any oracle type with timestamp |
| Medium | Signature + evidence hash |
| High | Multi-oracle attestation + vault commit |
| Critical | ZK proof + human sign-off |

### 7.4 Pipeline Hardening

Update `000_ARCHITECTURE` and `030_COGNITIVE_WORKFLOWS` so any `888_JUDGE → 999_SEAL` path must include:

1. At least one oracle bundle reference, **or**
2. An explicit `Cannot_Compute: No_Oracle` flag that trips `888_HOLD` for certain risk classes

### 7.5 SEAL Preconditions

Canonical SEAL requires:
```
Evidence Bundle (oracle-attested)
    OR
Cannot_Compute: No_Oracle flag (triggers 888_HOLD)
    +
Vault hash chain inclusion
    +
Floor score attestation
```

Without these, the verdict is PROVISIONAL, not SEAL.

### 7.6 Vault Evolution

Extend `999_SOVEREIGNVAULT` so SEAL entries include:
- Hash / pointer to oracle bundle used
- Versioned Floor + W³ metrics
- Explicit list of which external anchors were present (Physics, Law, Econ, Human) and which were missing

### 7.7 Authority Separation

**Target state (not yet implemented):**
Oracle + Vault live under a **different operator / trust domain** than the Trinity runtime.

This is written into canon as **target state**, not current implementation requirement.

---

## 8. Scope Separation: What This Note Does and Doesn't Change

| Scope | Change? | File |
|-------|---------|------|
| LAW (000_FLOORS, 000_CONSTITUTION) | ❌ No — evolves only after oracle spec stable | — |
| Architecture (000_ARCHITECTURE) | ⚠️ Note only — pipeline diagram updated to show oracle layer | `000_ARCHITECTURE` |
| WITNESS (003_WITNESS) | ⚠️ Note only — defines as oracle interface, not new pipeline stage yet | `003_WITNESS` |
| Vault (999_SOVEREIGNVAULT) | ⚠️ Note only — vault entry format proposal, not mandate | `999_SOVEREIGNVAULT` |
| v48 Oracle Spec | 🆕 Proposal — new canon file `006_ORACLESPEC.md` | `006_ORACLESPEC.md` |

**This note does NOT change LAW.** LAW/FLOORS changes require the oracle spec to be stable first.

---

## 9. Oracle Attestation Schema (Design Sketch — Not Canon)

```python
class OracleType(str, Enum):
    PHYSICS = "physics"      # Infra metrics, tests, sensors
    LAW = "law"              # Signed policies, statutes
    ECON = "econ"            # Cost accounting, budgets
    HUMAN = "human"          # Signed approvals, eval labels


class OracleAttestation(BaseModel):
    """Signed attestation that evidence entered from declared external source."""
    oracle_id: str           # Who vouched (e.g. "physics.infra.telemetry")
    oracle_type: OracleType   # Classification
    source_uri: str           # Declared source (e.g. "https://weather.api/data")
    evidence_hash: str        # SHA-256 of what was attested
    proof_type: str           # e.g. "merkle_path", "ecdsa_signature", "zk_proof"
    proof_data: dict          # Proof-specific data
    attested_at: datetime    # When
    signature: str           # Ed25519/ECDSA signature from oracle's key


class EvidenceBundle(BaseModel):
    """Ground truth evidence submitted to Witness."""
    attestations: list[OracleAttestation]
    claims: list[str]
    uncertainty: float       # F7 uncertainty band
    risk_class: str           # low/medium/high/critical
    missing_oracles: list[str] # Which oracle types were unavailable
    cannot_compute: bool      # True if deliberately skipped oracle


class SEALRecordV2(BaseModel):
    """Extended SEAL entry with oracle evidence."""
    ledger_id: str
    oracle_bundle_ref: str   # Hash pointer to EvidenceBundle in vault
    floor_scores: dict       # Versioned F1-F13 scores
    w3_consensus: float
    present_anchors: list[str]   # Physics/Law/Econ/Human present
    missing_anchors: list[str]   # Anchors deliberately absent
    vault_hash: str          # Merkle root of oracle evidence
    timestamp: datetime
    human_approval: bool     # F13 sign-off if required
```

---

## 10. Next Steps (Scoped to Note, Not Canon)

| Step | Action | File | Priority |
|------|--------|------|----------|
| 1 | Draft `006_ORACLESPEC.md` oracle layer proposal | `006_ORACLESPEC.md` | P0 |
| 2 | Add `OracleType`, `OracleAttestation`, `EvidenceBundle`, `SEALRecordV2` to `core/shared/types.py` | `core/shared/types.py` | P0 |
| 3 | Add `006_ORACLESPEC.md` to `000/` as proposal | `000/006_ORACLESPEC.md` | P1 |
| 4 | Update `000_ARCHITECTURE` pipeline diagram to show oracle layer | `000_ARCHITECTURE` | P1 |
| 5 | Update `003_WITNESS` to reference oracle interface | `003_WITNESS` | P2 |
| 6 | Update `999_SOVEREIGNVAULT` with SEALRecordV2 proposal | `999_SOVEREIGNVAULT` | P2 |

---

## References

- `000_THEORY-Unified-Canon-Reality-Engineering-Mode.txt` — Canonical theory source
- `core/shared/types.py` — Verdict, FloorScores, RuntimeEnvelope
- `core/floors.py` — ConstitutionalFloors (F1-F13)
- `arifos_mcp/runtime/dispatcher.py` — ToolDispatcher
- `ARCH/DOCS/REFACTOR_AUDIT_SPEC_v2.0.md` — Architecture audit

---

ΔΩΨ | ARIF | 888_JUDGE
