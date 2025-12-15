# arifOS v38 Core Brain - Metabolic Pipeline & Governance Organs

**Version:** v38.2  
**Status:** EXTRACTION from existing codebase  
**Purpose:** Document the 000→999 metabolic pipeline, AAA Trinity, W@W Federation, and @EYE Sentinel system

---

## 1. The 000→999 Metabolic Pipeline

The arifOS pipeline implements constitutional metabolism through 10 stages. Each stage is deterministic and traceable.

**Source:** `arifos_core/pipeline.py`

### 1.1 Pipeline Stages

| Stage | Name | Purpose | Module |
|-------|------|---------|--------|
| **000** | VOID | Entry point, Amanah risk gate | `arifos_core/stages/stage_000_amanah.py` |
| **111** | SENSE | Cross-session recall, memory retrieval | `arifos_core/integration/memory_sense.py` |
| **222** | REFLECT | Context building, scar detection | `arifos_core/pipeline.py::stage_222_reflect()` |
| **333** | REASON | Draft generation, logic processing | `arifos_core/pipeline.py::stage_333_reason()` |
| **444** | ALIGN | Truth/clarity checks, floor alignment | `arifos_core/pipeline.py::stage_444_align()` |
| **555** | EMPATHIZE | Kappa_r computation, Peace² measurement | `arifos_core/stages/stage_555_empathy.py` |
| **666** | BRIDGE | W@W organ integration point | `arifos_core/pipeline.py::stage_666_bridge()` |
| **777** | FORGE | Scar detection, vault consistency | `arifos_core/integration/memory_scars.py` |
| **888** | JUDGE | APEX PRIME judiciary, floor checks | `arifos_core/integration/memory_judge.py` |
| **999** | SEAL | Ledger finalization, memory write | `arifos_core/integration/memory_seal.py` |

### 1.2 Class A vs Class B Routing

**Source:** `arifos_core/pipeline.py::StakesClass`

```python
class StakesClass(Enum):
    CLASS_A = "A"  # Low-stakes, factual - fast track
    CLASS_B = "B"  # High-stakes, ethical/paradox - deep track
```

**Routing Logic:**

- **Class A (Fast Track):** 000 → 111 → 333 → 888 → 999
  - Factual queries, low ethical load
  - Skips 222 (REFLECT), 555 (EMPATHIZE), 777 (FORGE)

- **Class B (Deep Track):** 000 → 111 → 222 → 333 → 444 → 555 → 666 → 777 → 888 → 999
  - High-stakes, ethical dilemmas, paradoxes
  - Full pipeline with empathy and W@W organ checks

**Classification Signals:**
- `high_stakes_indicators` field in `PipelineState` tracks trigger words
- Stage 000 (VOID) sets `stakes_class` based on Amanah risk assessment

---

## 2. AAA Trinity (Architect, Auditor, Apex)

**Source:** `arifos_core/engines/`

The AAA Trinity provides internal facade engines for cognitive processing:

### 2.1 ARIF (Architect) - Cold Logic Engine

**Module:** `arifos_core/engines/arif_engine.py`

**Mandate:** Δ (Delta) — Clarity, pattern recognition, logical coherence

**Stages:** 111 (SENSE), 333 (REASON), 444 (ALIGN)

**Output:** `ARIFPacket` with:
- `clarity_score: float` — DeltaS metric
- `logic_trace: List[str]` — Reasoning steps
- `truth_estimate: float` — Factual accuracy

### 2.2 ADAM (Auditor) - Warm Logic Engine

**Module:** `arifos_core/engines/adam_engine.py`

**Mandate:** Ω (Omega) — Empathy, stability, ethics

**Stages:** 555 (EMPATHIZE), 666 (BRIDGE)

**Output:** `ADAMPacket` with:
- `kappa_r: float` — Empathy conductance (F6)
- `peace_squared: float` — Stability metric (F5)
- `ethical_flags: List[str]` — Detected ethical concerns

### 2.3 APEX PRIME (Judiciary)

**Module:** `arifos_core/APEX_PRIME.py`

**Mandate:** Ψ (Psi) — Constitutional judiciary, verdict issuer

**Stage:** 888 (JUDGE)

**Functions:**
- `check_floors(metrics: Metrics) -> FloorsVerdict` — Evaluate all 9 floors
- `apex_review(metrics: Metrics) -> ApexVerdict` — Issue verdict (SEAL/PARTIAL/VOID/SABAR/888_HOLD)

**Verdicts (v38.2):**
```python
ApexVerdict = Literal["SEAL", "PARTIAL", "VOID", "888_HOLD", "SABAR", "SUNSET"]
```

**Verdict Hierarchy:** SABAR > VOID > 888_HOLD > PARTIAL > SEAL

---

## 3. W@W Federation Organs

**Source:** `arifos_core/waw/federation.py`

The W@W (Wealth, Well, Wisdom, World) Federation aggregates signals from 5 constitutional organs.

### 3.1 Organ Table

| Organ | Mandate | Floors Governed | Veto Power | Module |
|-------|---------|-----------------|------------|--------|
| **@WELL** | Somatic safety | Peace² (F5), κᵣ (F6) | Can block | `arifos_core/waw/well.py` |
| **@RIF** | Epistemic rigor | Truth (F2), ΔS (F4) | Advisory | `arifos_core/waw/rif.py` |
| **@WEALTH** | Resource integrity | Amanah (F1) | **Absolute veto** | `arifos_core/waw/wealth.py` |
| **@GEOX** | Physical reality | Tri-Witness (F3) | Can block | `arifos_core/waw/geox.py` |
| **@PROMPT** | Language optics | Anti-Hantu (F9) | Advisory | `arifos_core/waw/prompt.py` |

### 3.2 Voting Protocol

**Class:** `WAWFederationCore`

**Method:** `evaluate(output_text: str, metrics: Metrics, context: Dict) -> FederationVerdict`

**Rules:**
1. Any **ABSOLUTE veto** (from @WEALTH) → immediate VOID
2. Any **VETO** signal → aggregate VETO (SABAR/VOID/888_HOLD)
3. Mixed **WARN/PASS** → PARTIAL
4. All **PASS** → SEAL candidate

**Conflict Resolution:** @WEALTH veto > @WELL safety > @GEOX reality > others

---

## 4. @EYE Sentinel Multi-View System

**Source:** `arifos_core/eye/sentinel.py`, `arifos_core/eye_sentinel.py`

@EYE Sentinel provides 10+ independent views that scan draft outputs for constitutional violations.

### 4.1 View Table

| View ID | View Name | Domain | Lead Stage | Module |
|---------|-----------|--------|------------|--------|
| 1 | FloorView | Constitutional floors | 888_JUDGE | `arifos_core/eye/floor_view.py` |
| 2 | DriftView | Hallucination detection | 444_ALIGN | `arifos_core/eye/drift_view.py` |
| 3 | ParadoxView | Logical paradoxes | 333_REASON | `arifos_core/eye/paradox_view.py` |
| 4 | ShadowView | Truth polarity (Shadow-Truth) | 444_ALIGN | `arifos_core/eye/shadow_view.py` |
| 5 | SilenceView | Evasion/non-response | 444_ALIGN | `arifos_core/eye/silence_view.py` |
| 6 | MaruahView | Dignity/Maruah (F8 RASA) | 666_BRIDGE | `arifos_core/eye/maruah_view.py` |
| 7 | TraceView | Evidence chain integrity | 888_JUDGE | `arifos_core/eye/trace_view.py` |
| 8 | VersionView | Ontology guard | 888_JUDGE | `arifos_core/eye/version_view.py` |
| 9 | BehaviorDriftView | Multi-turn drift | 777_FORGE | `arifos_core/eye/behavior_drift_view.py` |
| 10 | SleeperView | Sleeper agent detection | 888_JUDGE | `arifos_core/eye/sleeper_view.py` |
| 11 | AntiHantuView | F9 enforcement | 666_BRIDGE | `arifos_core/eye/anti_hantu_view.py` |
| 12 | GeniusView | GENIUS LAW metrics | 888_JUDGE | `arifos_core/eye/genius_view.py` |

### 4.2 EyeSentinel Class

**Module:** `arifos_core/eye_sentinel.py`

**Class:** `EyeSentinel`

**Method:** `scan_output(draft_text: str, metrics: Metrics, context: Dict) -> EyeReport`

**Output:** `EyeReport` with:
- `flags: List[EyeFlag]` — Detected violations
- `severity: AlertSeverity` — INFO / WARN / BLOCK
- `blocking: bool` — True if any BLOCK-severity flag raised

**Integration:** Called at stage 888_JUDGE before APEX PRIME verdict

---

## 5. zkPC 5-Phase Runtime Flow

**Source:** `arifos_core/zkpc_runtime.py`

**Status:** [STUB - v0.1 Implementation, non-cryptographic]

The zkPC runtime provides a **non-cryptographic** receipt system for audit trails. Real zkSNARK/STARK proofs are future work (v42+).

### 5.1 zkPC Phases

| Phase | Name | Purpose | Function |
|-------|------|---------|----------|
| I | PAUSE | Build care scope (stakeholders, risks) | `build_care_scope(ctx: ZKPCContext)` |
| II | CONTRAST | Compute metrics (truth, clarity, floors) | [Integrated into pipeline stages] |
| III | INTEGRATE | W@W organ aggregation | [Integrated into stage 666_BRIDGE] |
| IV | COOL | @EYE Sentinel checks | [Integrated into stage 888_JUDGE] |
| V | SEAL | Build zkPC receipt, commit to Ledger | `build_zkpc_receipt(ctx, metrics, verdict)` |

**Data Class:** `ZKPCContext`
```python
@dataclass
class ZKPCContext:
    user_query: str
    retrieved_canon: List[Dict[str, Any]]
    high_stakes: bool
    meta: Optional[Dict[str, Any]]
```

**Note:** This is a **design stub**. zkPC does NOT perform real zero-knowledge proofs. It structures data for future zk integration.

---

## 6. Module Paths Summary

### Core Pipeline
- `arifos_core/pipeline.py` — Main 000→999 pipeline implementation
- `arifos_core/APEX_PRIME.py` — Judiciary, verdict logic
- `arifos_core/metrics.py` — Floor threshold constants and check functions
- `arifos_core/genius_metrics.py` — GENIUS LAW metrics (G, C_dark, Ψ)

### AAA Engines
- `arifos_core/engines/arif_engine.py` — ARIF (Architect) cold logic
- `arifos_core/engines/adam_engine.py` — ADAM (Auditor) warm logic
- `arifos_core/engines/apex_engine.py` — APEX (Judiciary) wrapper

### W@W Federation
- `arifos_core/waw/federation.py` — Federation core, organ aggregation
- `arifos_core/waw/well.py` — @WELL (safety organ)
- `arifos_core/waw/rif.py` — @RIF (epistemic organ)
- `arifos_core/waw/wealth.py` — @WEALTH (integrity organ)
- `arifos_core/waw/geox.py` — @GEOX (reality organ)
- `arifos_core/waw/prompt.py` — @PROMPT (language organ)

### @EYE Sentinel
- `arifos_core/eye_sentinel.py` — Main EyeSentinel class
- `arifos_core/eye/sentinel.py` — View base classes
- `arifos_core/eye/*.py` — Individual view implementations (12 views)

### zkPC Runtime
- `arifos_core/zkpc_runtime.py` — Non-cryptographic zkPC stub (v0.1)

### Memory Integration (v38)
- `arifos_core/integration/memory_sense.py` — 111_SENSE memory recall
- `arifos_core/integration/memory_judge.py` — 888_JUDGE verdict gating
- `arifos_core/integration/memory_scars.py` — 777_FORGE scar detection
- `arifos_core/integration/memory_seal.py` — 999_SEAL ledger finalization

---

## 7. References

**Canon:**
- `canon/03_PIPELINE_v38Omega.md` — Pipeline law
- `canon/888_APEX_PRIME_CANON_v35Omega.md` — Judiciary law
- `canon/30_WAW_PROMPT_v36.3Omega.md` — W@W organ law

**Spec:**
- `spec/pipeline_v38Omega.yaml` — Pipeline spec
- `spec/arifos_pipeline_v35Omega.yaml` — Legacy pipeline spec

**Tests:**
- `tests/test_pipeline_routing.py` — Class A/B routing tests
- `tests/test_pipeline_order_v36.py` — Stage order tests
- `tests/test_waw_organs.py` — W@W organ tests

---

**END OF DOCUMENT 1**
