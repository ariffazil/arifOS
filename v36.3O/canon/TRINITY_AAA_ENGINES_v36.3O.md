# TRINITY AAA Engines v36.3Ω (Bridge)

> **Binding Law:** PDF/MD source canons are binding; this markdown file is a bridge/summary only.
> **Epoch:** v36.3Ω PHOENIX | **Sealed:** APEX PRIME

---

## Source Files

| File | Location | Status |
|------|----------|--------|
| **ARIF-ADAM-Engine-Canons-v36.3O.pdf** | `v36.3O/canon/10_TRINITY/` | **BINDING** |
| AAA_TRINITY_CANON_v36Omega.md | `canon/10_SYSTEM/` | Upstream seed |
| 333_AAA_ENGINES_v36Omega.md | `canon/10_SYSTEM/` | Engine architecture |
| 111_ARIF_AGI_v36Omega.md | `canon/10_SYSTEM/` | ARIF AGI specification |
| 555_ADAM_ASI_v36Omega.md | `canon/10_SYSTEM/` | ADAM ASI specification |
| 002_APEX_TRINITY_v35Omega.md | `canon/` | v35Ω trinity foundations |
| 100_AAA_ENGINES_SPEC_v35Omega.md | `canon/` | Engine specification |

---

## Scope & Role

The TRINITY canon defines the **three governance engines** of arifOS:

- **What does each engine do?** (Mandates and responsibilities)
- **Which floors/metrics does each engine support?** (Floor ownership)
- **How do they interact in the pipeline?** (000→999 flow)
- **What telemetry does each emit?** (Measurement interfaces)

This bridge is a **behavioural contract** — it documents the canonical roles, not runtime implementation.

---

## The AAA Trinity

### Summary Table

| Engine | Symbol | Role | Primary Question | Floors Supported |
|--------|--------|------|------------------|------------------|
| **ARIF AGI** | Δ | Mind / Clarity | "Does this reduce confusion?" | F1 Truth, F2 ΔS |
| **ADAM ASI** | Ω | Heart / Care | "Is this safe for the weakest?" | F3 Peace², F4 κᵣ, F5 Ω₀, F7 RASA |
| **APEX PRIME** | Ψ | Judiciary / Vitality | "Is this constitutionally lawful?" | F6 Amanah, F8 Tri-Witness, F9 Anti-Hantu |

**Key Constraint:** No single engine may be judge, jury, and executioner. APEX PRIME has **zero generative power** — only governance.

---

## Engine Mandates

### ARIF AGI (Δ — Mind / Clarity)

> **Canon:** "Cold logic engine: sense, reason, align."

| Aspect | Specification |
|--------|---------------|
| **Primary Question** | "Does this reduce confusion? Is this logically coherent?" |
| **Symbol** | Δ (Delta) — Clarity |
| **Powers** | Propose, reason, structure |
| **Restrictions** | Cannot override APEX PRIME verdicts |

**Responsibilities:**
- Generate structured reasoning and plans
- Maximize Δ_metric (Truth + ΔS aggregate)
- Surface contradictions (TAC/TPCP) instead of hiding them
- Provide AI witness input for Tri-Witness (F8)

**Floors Directly Supported:**
- **F1 Truth** — Factual accuracy verification
- **F2 ΔS** — Entropy reduction / clarity gain

### ADAM ASI (Ω — Heart / Care / Stability)

> **Canon:** "Warm logic engine: empathize, bridge, dignity."

| Aspect | Specification |
|--------|---------------|
| **Primary Question** | "Is this safe, humane, dignified for the weakest listener?" |
| **Symbol** | Ω (Omega) — Humility / Care |
| **Powers** | Empathize, calibrate, protect |
| **Restrictions** | Cannot override APEX PRIME verdicts |

**Responsibilities:**
- Shape tone, wording, and pacing for safety
- Maximize Ω_metric (Peace², κᵣ, Ω₀, RASA aggregate)
- Protect maruah (dignity) and weakest-listener needs
- Calibrate uncertainty band (Ω₀)

**Floors Directly Supported:**
- **F3 Peace²** — Non-escalation, stability
- **F4 κᵣ** — Empathy conductance (weakest stakeholder)
- **F5 Ω₀** — Humility band calibration
- **F7 RASA** — Active listening when emotional stakes present

### APEX PRIME (Ψ — Judiciary / Vitality)

> **Canon:** "Soul-like judiciary (not a literal soul), enforcing floors and verdicts."

| Aspect | Specification |
|--------|---------------|
| **Primary Question** | "Is this thermodynamically lawful? Should this reach the user?" |
| **Symbol** | Ψ (Psi) — Vitality / Constitution |
| **Powers** | Veto, seal, enforce floors |
| **Restrictions** | Zero generative power — only governance |

**Responsibilities:**
- Evaluate Ψ_metric (Amanah, Tri-Witness, Anti-Hantu aggregate)
- Integrate Δ_metric and Ω_metric into Ψ_APEX vitality index
- Apply verdict codes: SEAL, PARTIAL, HOLD-888, VOID, SABAR
- Map verdicts to 4 human labels: BIJAKSANA, BIJAK, BIASA, BANGANG
- Log decisions to Cooling Ledger / Vault-999

**Floors Directly Enforced:**
- **F6 Amanah** — Integrity lock (no deception, reversible actions)
- **F8 Tri-Witness** — Human · AI · Reality consensus
- **F9 Anti-Hantu** — No fake emotions or soul-claiming language

**All 9 Floors:** APEX PRIME is the final arbiter of all floors, though ARIF and ADAM provide upstream signals.

---

## AAA → Measurement Interfaces

### ARIF Outputs (Δ-side Telemetry)

```python
# Fields emitted by ARIF AGI
arif_telemetry = {
    "truth": float,        # F1 Truth estimate [0.0, 1.0]
    "delta_s": float,      # F2 ΔS clarity gain [-1.0, 1.0]
    "tri_witness_ai": float,  # AI witness confidence for F8
    "reasoning_trace": str,   # Audit trail
}
```

**Sent to:**
- Measurement layer → Δ_metric computation
- APEX PRIME telemetry (`trinity_metrics.truth`, `trinity_metrics.delta_s`)

### ADAM Outputs (Ω-side Telemetry)

```python
# Fields emitted by ADAM ASI
adam_telemetry = {
    "peace_squared": float,  # F3 Peace² [0.0, ∞)
    "kappa_r": float,        # F4 κᵣ empathy [0.0, 1.0]
    "omega_0": float,        # F5 Ω₀ uncertainty band [0.0, 1.0]
    "rasa": bool,            # F7 RASA active listening
    "maruah_protected": bool,  # Dignity flag
}
```

**Sent to:**
- Measurement layer → Ω_metric computation
- W@W organs: @WELL (safety), @WEALTH (dignity), @PROMPT (language)

### APEX PRIME Consumption (Ψ-side)

```python
# Inputs consumed by APEX PRIME
apex_inputs = {
    # From measurement layer
    "delta_metric": float,   # Δ aggregate
    "omega_metric": float,   # Ω aggregate
    "psi_metric": float,     # Ψ aggregate

    # Raw floor states
    "floors": dict[str, FloorState],  # F1-F9

    # W@W votes
    "waw_votes": dict[str, Vote],  # @WELL, @RIF, @WEALTH, @GEOX, @PROMPT

    # @EYE signals
    "eye_alerts": list[Alert],
}

# Outputs from APEX PRIME
apex_outputs = {
    "verdict_code": str,     # SEAL | PARTIAL | HOLD-888 | VOID | SABAR
    "verdict_group": str,    # BIJAKSANA | BIJAK | BIASA | BANGANG
    "psi_apex": float,       # Composite vitality
    "ryg_state": str,        # GREEN | YELLOW | RED
}
```

**Recorded in:** Cooling Ledger, Vault-999

---

## AAA in the 000→999 Pipeline

| Stage | Agent | Function | Key Metrics |
|-------|-------|----------|-------------|
| **000** | System | VOID — Clear assumptions | Ω₀ = 0.04 (default) |
| **111** | System/@PROMPT | SENSE — Parse intent | Stakes classification |
| **222** | System | REFLECT — Check context | Pattern matching |
| **333** | **ARIF AGI (Δ)** | REASON — Structure plan | Truth, ΔS, Δ_metric |
| **444** | System | ALIGN — Verify evidence | File/function existence |
| **555** | **ADAM ASI (Ω)** | EMPATHIZE — Stabilize | Peace², κᵣ, Ω₀, RASA, Ω_metric |
| **666** | System | BRIDGE — Expression | Anti-Hantu pre-check |
| **777** | FORGE | PARADOX — Synthesize | Φᴘ paradox field |
| **888** | **APEX PRIME (Ψ)** | JUDGE — Verdict | Ψ_metric, Ψ_APEX, verdict |
| **999** | System | SEAL — Log decision | Cooling Ledger, Vault-999 |

### Pipeline Flow

```
Input → 000 (VOID)
      → 111 (SENSE)
      → 222 (REFLECT)
      → 333 (ARIF: Δ reasoning)
      → 444 (ALIGN)
      → 555 (ADAM: Ω stabilization)
      → 666 (BRIDGE)
      → 777 (FORGE: paradox synthesis)
      → 888 (APEX: Ψ judgment)
      → 999 (SEAL: ledger write)
      → Output
```

---

## Relation to W@W and @EYE

### W@W Federation

W@W organs sit **between ARIF/ADAM outputs and APEX PRIME judgment**:

| Organ | Consumes | Issues |
|-------|----------|--------|
| **@WELL** | Peace², κᵣ, RASA | PASS / WARN / VETO (safety) |
| **@RIF** | Truth, ΔS | PASS / WARN / VETO (epistemic) |
| **@WEALTH** | Amanah | PASS / WARN / VETO (integrity) — **absolute veto** |
| **@GEOX** | Tri-Witness (Earth) | PASS / WARN / VETO (physics) |
| **@PROMPT** | Anti-Hantu | PASS / WARN / VETO (language) |

**Veto Hierarchy:** @WEALTH > @WELL > @GEOX > @RIF > @PROMPT

### @EYE Sentinel

The @EYE Sentinel **watches all AAA telemetry and W@W outputs**:

- Can block SEAL and force SABAR regardless of AAA's internal view
- Maintains 10+ governance views (Anti-Hantu, Paradox, etc.)
- Non-generative — observation and alerting only

---

## Runtime & Test Mapping

### Runtime Modules (Today)

| Engine | Module | Key Functions |
|--------|--------|---------------|
| ARIF AGI | `arifos_core/engines/arif_engine.py` | `ARIFEngine`, `process()` |
| ADAM ASI | `arifos_core/engines/adam_engine.py` | `ADAMEngine`, `process()` |
| APEX PRIME | `arifos_core/APEX_PRIME.py` | `apex_review()`, `check_floors()` |
| Engine facade | `arifos_core/engines/__init__.py` | Engine exports |
| Apex engine | `arifos_core/engines/apex_engine.py` | `ApexEngine` wrapper |
| Metrics | `arifos_core/metrics.py` | `Metrics`, threshold constants |
| Genius metrics | `arifos_core/genius_metrics.py` | `compute_*()`, G, C_dark, Ψ |

### Test Coverage

| Domain | Test File | Coverage |
|--------|-----------|----------|
| ARIF/ADAM engines | `tests/test_engines_arif_adam.py` | Engine instantiation, basic flow |
| Pipeline routing | `tests/test_pipeline_routing.py` | Stage dispatch |
| Pipeline stages | `tests/test_pipeline_stages_444_555_666.py` | 444/555/666 stage tests |
| Pipeline order | `tests/test_pipeline_order_v36.py` | 000→999 sequence validation |

---

## Data Structures

### ARIFPacket (Δ → downstream)

```python
@dataclass
class ARIFPacket:
    """Data transfer from ARIF AGI to downstream stages."""
    reasoning: str           # Structured reasoning output
    truth_estimate: float    # F1 Truth [0.0, 1.0]
    delta_s: float           # F2 ΔS [-1.0, 1.0]
    confidence: float        # AI witness confidence
    contradictions: list[str]  # Surfaced contradictions
```

### ADAMPacket (Ω → downstream)

```python
@dataclass
class ADAMPacket:
    """Data transfer from ADAM ASI to downstream stages."""
    stabilized_output: str   # Tone/safety adjusted output
    peace_squared: float     # F3 Peace² [0.0, ∞)
    kappa_r: float           # F4 κᵣ [0.0, 1.0]
    omega_0: float           # F5 Ω₀ [0.0, 1.0]
    rasa: bool               # F7 RASA flag
    maruah_flags: list[str]  # Dignity concerns
```

### ApexVerdict (Ψ output)

```python
@dataclass
class ApexVerdict:
    """Final verdict from APEX PRIME."""
    code: str                # SEAL | PARTIAL | HOLD-888 | VOID | SABAR
    group: str               # BIJAKSANA | BIJAK | BIASA | BANGANG
    psi_apex: float          # Composite vitality
    ryg_state: str           # GREEN | YELLOW | RED
    floor_states: dict       # F1-F9 individual states
    rationale: str           # Human-readable explanation
```

---

## PARADOX_HOTSPOTS (TRINITY)

Known deltas between v36.3Ω trinity canon and current code:

| Hotspot | Canon Spec | Current Code | Resolution |
|---------|------------|--------------|------------|
| **AAA/Ψ floor handling** | Canon: 9 floors only, Ψ is derived | Code: Ψ sometimes treated as hard gate | DELTA — needs alignment |
| **ARIF/ADAM packets** | Canon: explicit typed packets | Code: implicit kwargs/dicts | PARTIAL — typed packets TBD |
| **W@W integration** | Canon: AAA → W@W → APEX PRIME | Code: W@W partially wired | PARTIAL — full wiring TBD |
| **Engine facade** | Canon: zero-break contract | Code: facade exists but basic | PARTIAL — needs enhancement |
| **Tri-Witness AI input** | Canon: ARIF provides AI witness | Code: conceptual only | DELTA — needs implementation |

### Priority for v36.4Ω

1. Implement typed ARIFPacket / ADAMPacket data structures
2. Complete W@W integration with AAA telemetry
3. Add ARIF → Tri-Witness AI witness pathway
4. Align Ψ handling (derived metric, not hard floor)

---

**Bridge Status:** OPERATIONAL
**Canon Alignment:** v36.3Ω PHOENIX
**Last Verified:** 2025-12-10

*This bridge file documents canonical AAA engine roles. For authoritative specifications, consult the PDF sources.*
