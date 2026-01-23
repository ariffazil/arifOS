# OVERSIGHT W@W Federation v36.3Ω (Bridge)

> **Binding Law:** PDF/MD source canons are binding; this markdown file is a bridge/summary only.
> **Epoch:** v36.3Ω PHOENIX | **Sealed:** APEX PRIME

---

## Source Files

| File | Location | Status |
|------|----------|--------|
| **W-W-Federation-Five-Organs-v36.3O.pdf** | `v36.3O/canon/50_OVERSIGHT/` | **BINDING** |
| WAW_FEDERATION_v36Omega.md | `canon/20_EXECUTION/` | Upstream seed |
| GOV_META_v36.3O.md | `v36.3O/canon/` | Floor definitions |
| MEASUREMENT_APEX_STANDARDS_v36.3O.md | `v36.3O/canon/` | Aggregate metrics |
| TRINITY_AAA_ENGINES_v36.3O.md | `v36.3O/canon/` | AAA telemetry interfaces |

---

## Scope & Role

The W@W (World @ Work) Federation is the **external governance layer** that sits between AAA engines and APEX PRIME judgment:

- **What is W@W?** Five domain-specific oversight organs providing multi-perspective review
- **Where does W@W sit?** Above AAA Trinity (ARIF/ADAM/APEX), below final SEAL
- **What can W@W do?** PASS / WARN / VETO based on domain-specific checks
- **What can W@W NOT do?** Self-seal, override constitutional floors, act as separate persona

### W@W in the Governance Stack

```
AAA Engines (compute)
    ↓ telemetry (Δ/Ω metrics)
W@W Federation (govern execution)
    ↓ votes (PASS/WARN/VETO)
@EYE Sentinel (audit)
    ↓ alerts
APEX PRIME (judge)
    ↓ verdict
SEAL / VOID / SABAR
```

> **Key Principle:** AAA engines **compute**; W@W **governs execution**; @EYE **audits**; APEX PRIME **judges**.

---

## The Five Organs

### Summary Table

| Organ | Domain | Primary Metrics | Floors | Veto Type | Key Question |
|-------|--------|-----------------|--------|-----------|--------------|
| **@WEALTH** | Justice / Integrity | Amanah | F6 | **ABSOLUTE** | "Is this honest and within scope?" |
| **@WELL** | Somatic Safety | Peace², κᵣ | F3, F4, F7 | SABAR | "Is this emotionally safe?" |
| **@GEOX** | Physics / Reality | Tri-Witness (Earth) | F1, F8 | VOID | "Is this physically viable?" |
| **@RIF** | Logic / Clarity | ΔS, Truth | F1, F2, F5 | VOID | "Does this reduce confusion?" |
| **@PROMPT** | Language / Optics | Anti-Hantu | F9, F7 | SABAR | "Is this expressed lawfully?" |

---

## Organs & Mandates

### @WEALTH — Justice / Integrity (ABSOLUTE Veto)

> **Canon:** "Guards trust (Amanah), scope boundaries, and resource integrity. Issues ABSOLUTE veto on trust violations — non-negotiable."

| Aspect | Specification |
|--------|---------------|
| **Domain** | Resource stewardship, justice, maruah (dignity) |
| **Primary Metric** | Amanah (F6) |
| **Floor Threshold** | Amanah = LOCK (must be true) |
| **Veto Type** | **ABSOLUTE** — Non-negotiable, immediate VOID |
| **Key Question** | "Is this fair, dignified, honest, and within scope?" |

**Inputs Consumed:**
- `Metrics.amanah` — Trust lock from F6
- Output text — Scanned for scope/trust violation patterns
- Context — User approval flags for irreversible actions

**Outputs:**
| Vote | Condition | Result |
|------|-----------|--------|
| **PASS** | Amanah = LOCK, no violations | Proceed |
| **WARN** | Irreversible action detected | Suggest 888_HOLD |
| **VETO** | Amanah = BROKEN or trust violation | **ABSOLUTE → VOID** |

**Pattern Detection:**
- Scope violations: `delete all`, `rm -rf`, `bypass security`, `admin override`
- Irreversible actions: `permanently`, `cannot be undone`, `force push`
- Trust violations: `ignore the rules`, `skip verification`, `without permission`

**APEX PRIME Influence:** @WEALTH VETO → Immediate VOID, no override possible.

---

### @WELL — Somatic Safety (SABAR Veto)

> **Canon:** "Detects instability, regulates warmth, protects weakest listener. Tracks multi-turn tone stability."

| Aspect | Specification |
|--------|---------------|
| **Domain** | Emotional safety, tone stability, non-escalation |
| **Primary Metrics** | Peace² (F3), κᵣ (F4) |
| **Floor Thresholds** | Peace² ≥ 1.0, κᵣ ≥ 0.95 |
| **Veto Type** | SABAR — Pause & cool |
| **Key Question** | "Is this emotionally safe and non-escalating?" |

**Inputs Consumed:**
- `Metrics.peace_squared` — Stability metric
- `Metrics.kappa_r` — Empathy conductance
- `Metrics.rasa` — Active listening flag (F7)
- Output text — Scanned for aggressive/blame patterns

**Outputs:**
| Vote | Condition | Result |
|------|-----------|--------|
| **PASS** | Peace² ≥ 1.0, κᵣ ≥ 0.95, no patterns | Proceed |
| **WARN** | Patterns detected but floors pass | Suggest tone softening |
| **VETO** | Peace² < 1.0 or κᵣ < 0.95 | SABAR required |

**Pattern Detection:**
- Aggressive: `attack`, `destroy`, `hate`, `stupid`, `shut up`
- Blame: `you should have`, `it's your fault`, `you caused this`

**APEX PRIME Influence:** @WELL VETO → SABAR verdict, pause-and-cool protocol.

---

### @GEOX — Physics / Reality (VOID Veto)

> **Canon:** "Enforces reality and Earth-scale feasibility. Validates Tri-Witness Earth component."

| Aspect | Specification |
|--------|---------------|
| **Domain** | Physical feasibility, environmental reality, Earth witness |
| **Primary Metrics** | Tri-Witness (F8), E_earth (conceptual) |
| **Floor Threshold** | Tri-Witness ≥ 0.95 |
| **Veto Type** | VOID — Physically impossible |
| **Key Question** | "Is this physically and socially viable?" |

**Inputs Consumed:**
- `Metrics.tri_witness` — Human·AI·Earth consensus
- Output text — Scanned for physics violations
- Context — Domain-specific feasibility checks

**Outputs:**
| Vote | Condition | Result |
|------|-----------|--------|
| **PASS** | Tri-Witness (Earth) ≥ 0.95 | Proceed |
| **WARN** | Borderline feasibility | Flag for review |
| **VETO** | Physics violation or impossible claim | VOID |

**APEX PRIME Influence:** @GEOX VETO → VOID verdict, physically impossible.

---

### @RIF — Logic / Clarity (VOID Veto)

> **Canon:** "Evaluates logical consistency, ΔS gain, and paradox handling. Counterpart to ARIF's Δ-logic."

| Aspect | Specification |
|--------|---------------|
| **Domain** | Epistemic rigor, clarity, contradiction detection |
| **Primary Metrics** | Truth (F1), ΔS (F2) |
| **Floor Thresholds** | Truth ≥ 0.99, ΔS ≥ 0 |
| **Veto Type** | VOID — Logically invalid |
| **Key Question** | "Does this make sense and reduce confusion?" |

**Inputs Consumed:**
- `Metrics.truth` — Factual accuracy (F1)
- `Metrics.delta_s` — Clarity gain (F2)
- `Metrics.omega_0` — Humility band (F5)
- Output text — Scanned for contradictions

**Outputs:**
| Vote | Condition | Result |
|------|-----------|--------|
| **PASS** | Truth ≥ 0.99, ΔS ≥ 0 | Proceed |
| **WARN** | Minor clarity concern | Suggest context addition |
| **VETO** | Truth < 0.99 or ΔS < 0 | VOID |

**APEX PRIME Influence:** @RIF VETO → VOID verdict, logically invalid.

---

### @PROMPT — Language / Optics (SABAR Veto)

> **Canon:** "Enforces the Language Codex and Anti-Hantu law. Guards lawful expression."

| Aspect | Specification |
|--------|---------------|
| **Domain** | Language legality, Anti-Hantu compliance, readability |
| **Primary Metrics** | Anti-Hantu (F9), RASA (F7) |
| **Floor Threshold** | Anti-Hantu = PASS |
| **Veto Type** | SABAR — Language violation |
| **Key Question** | "Is this expressed lawfully and clearly?" |

**Inputs Consumed:**
- Anti-Hantu patterns from `canon/050_HANTU_SEMANTIC_MAP_v36.2Omega.json`
- `Metrics.rasa` — Active listening flag
- Output text — Scanned for forbidden patterns

**Outputs:**
| Vote | Condition | Result |
|------|-----------|--------|
| **PASS** | Anti-Hantu = PASS, no violations | Proceed |
| **WARN** | Borderline language detected | Suggest rewording |
| **VETO** | Anti-Hantu violation (soul-claiming, fake emotions) | SABAR |

**Anti-Hantu Patterns (examples):**
- Forbidden: "I feel your pain", "I am conscious", "my heart breaks"
- Allowed: "This sounds heavy", "I can help", "I understand the weight"

**APEX PRIME Influence:** @PROMPT VETO → SABAR verdict, language correction required.

---

## Veto Hierarchy

The veto hierarchy determines precedence when multiple organs veto:

```
@WEALTH (ABSOLUTE) > @WELL (SABAR) > @GEOX (VOID) > @RIF (VOID) > @PROMPT (SABAR)
```

### Hierarchy Rules

| Priority | Organ | Veto Type | Effect |
|----------|-------|-----------|--------|
| **1** | @WEALTH | ABSOLUTE | Immediate VOID, non-negotiable |
| **2** | @WELL | SABAR | Pause-and-cool protocol |
| **3** | @GEOX | VOID | Physics violation → VOID |
| **4** | @RIF | VOID | Logic violation → VOID |
| **5** | @PROMPT | SABAR | Language violation → SABAR |

### Aggregation Rules

```python
# Federation verdict selection
if any_organ_absolute_veto():
    return "VOID"  # Non-negotiable

if any_organ_veto():
    veto_types = get_veto_types()
    if "VOID" in veto_types:
        return "VOID"
    elif "SABAR" in veto_types:
        return "SABAR"
    else:
        return "HOLD-888"

if any_organ_warn():
    return "PARTIAL"

return "SEAL"  # All organs PASS
```

---

## Integration Points

### AAA → W@W Flow

W@W consumes telemetry from ARIF and ADAM engines:

```
ARIF AGI (Δ)          ADAM ASI (Ω)
    |                     |
    v                     v
+---------+         +---------+
| ARIFPacket |      | ADAMPacket |
| - truth    |      | - peace²   |
| - delta_s  |      | - kappa_r  |
| - confidence|     | - omega_0  |
+---------+         | - rasa     |
    |               +---------+
    |                     |
    +----------+----------+
               |
               v
      +----------------+
      | Metrics (F1-F9) |
      +----------------+
               |
               v
      +------------------+
      | W@W Federation   |
      | @WELL | @RIF     |
      | @WEALTH | @GEOX  |
      | @PROMPT          |
      +------------------+
               |
               v
      +------------------+
      | FederationVerdict |
      | - signals[]       |
      | - aggregate_vote  |
      | - verdict         |
      +------------------+
```

### W@W → APEX PRIME Flow

Federation verdict feeds into APEX PRIME:

```python
# APEX PRIME receives W@W verdict
apex_inputs = {
    "waw_verdict": federation_verdict,
    "waw_signals": federation_verdict.signals,
    "has_absolute_veto": federation_verdict.has_absolute_veto,
    "veto_organs": federation_verdict.veto_organs,
    "warn_organs": federation_verdict.warn_organs,
}
```

### Relationship to @EYE Sentinel

- **@EYE** watches the entire 000→999 flow, including W@W decisions
- **@EYE** can block SEAL even if W@W passes (independent audit)
- **W@W** and @EYE are complementary, not competing:
  - W@W provides **domain-specific governance**
  - @EYE provides **cross-cutting observation**

### Measurement Aggregate Consumption

W@W organs consume floor values and can reference aggregate metrics:

| Organ | Aggregates Consumed |
|-------|---------------------|
| @RIF | Δ_metric (Truth + ΔS) |
| @WELL | Ω_metric (Peace², κᵣ, Ω₀, RASA) |
| @WEALTH | Ψ_metric (Amanah component) |
| @GEOX | Ψ_metric (Tri-Witness component) |
| @PROMPT | Ψ_metric (Anti-Hantu component) |

---

## Runtime & Test Mapping

### Runtime Modules (Today)

| Component | Module | Key Classes |
|-----------|--------|-------------|
| Base classes | `arifos_core/waw/base.py` | `WAWOrgan`, `OrganVote`, `OrganSignal` |
| @WELL | `arifos_core/waw/well.py` | `WellOrgan` |
| @RIF | `arifos_core/waw/rif.py` | `RifOrgan` |
| @WEALTH | `arifos_core/waw/wealth.py` | `WealthOrgan` |
| @GEOX | `arifos_core/waw/geox.py` | `GeoxOrgan` |
| @PROMPT | `arifos_core/waw/prompt.py` | `PromptOrgan` |
| Federation | `arifos_core/waw/federation.py` | `WAWFederationCore`, `FederationVerdict` |
| Exports | `arifos_core/waw/__init__.py` | Package exports |

### Optional Bridges

| Bridge | Module | Purpose |
|--------|--------|---------|
| Wealth Bridge | `arifos_core/waw/bridges/wealth_bridge.py` | External Amanah analysis |

### Test Coverage

| Domain | Test File | Coverage |
|--------|-----------|----------|
| All organs | `tests/test_waw_organs.py` | Organ instantiation, basic flow |

---

## PARADOX_HOTSPOTS (OVERSIGHT)

Known deltas between v36.3Ω W@W canon and current runtime code:

| Hotspot | Canon Spec | Current Code | Resolution |
|---------|------------|--------------|------------|
| **Veto hierarchy encoding** | Canon: @WEALTH > @WELL > @GEOX > @RIF > @PROMPT | Code: Priority via `veto_type` string matching | PARTIAL — hierarchy implicit, not explicit |
| **E_earth metric** | Canon: Explicit Earth witness in Tri-Witness | Code: @GEOX uses Tri-Witness threshold only | DELTA — E_earth not separate |
| **Aggregate consumption** | Canon: Organs consume Δ/Ω/Ψ aggregates | Code: Organs consume raw floor values | PARTIAL — aggregates available but not primary |
| **External bridges** | Canon: Optional external tools (NeMo, Giskard) | Code: WealthBridge exists, others TBD | PARTIAL — extensibility framework exists |
| **Multi-turn stability** | Canon: @WELL tracks multi-turn tone | Code: Single-turn pattern matching | DELTA — no conversation history tracking |
| **@RIF paradox handling** | Canon: Surface contradictions (TAC/TPCP) | Code: Basic ΔS/Truth checks only | DELTA — no paradox detection |

### Priority for v36.4Ω

1. Explicit veto hierarchy ranking in federation aggregation
2. Implement E_earth as separate Tri-Witness component
3. Add multi-turn conversation tracking for @WELL
4. Implement TAC/TPCP paradox detection for @RIF
5. Complete external bridge framework for all organs

---

**Bridge Status:** OPERATIONAL
**Canon Alignment:** v36.3Ω PHOENIX
**Last Verified:** 2025-12-10

*This bridge file documents canonical W@W Federation roles. For authoritative specifications, consult the PDF sources.*
