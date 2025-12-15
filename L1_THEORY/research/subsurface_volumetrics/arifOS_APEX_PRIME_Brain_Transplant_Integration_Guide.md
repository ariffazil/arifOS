# arifOS APEX PRIME: Brain Transplant Integration
## AI-Subsurface-Intelligence-Forge PDF Analysis + Executable Codification

**Date:** December 13, 2025  
**Source:** AI-Subsurface-Intelligence-Forge.pdf (39 KB)  
**Alignment:** ✓ PERFECT with arifOS 9-Layer Architecture

---

## APEX PRIME = Your arifOS Architecture Operationalized

**What This Means:**
- Your 9-Layer architecture = Blueprint
- This PDF = Executable governance codification
- APEX Artifact 1-5 = Layers 1-9 in operational form

---

## The Five Artifacts (APEX PRIME)

### Artifact 1: Basin Physics Constitution
**Maps to:** Layers 1-2 + ORGAN 1  
**Contains:**
- Malay 3,000m porosity floor (exact refusal criteria)
- Sandakan thermal decay: $\phi(d) = 31.08 \cdot e^{-0.00026 \cdot d}$
- Deepwater Sabah HPHT + disequilibrium compaction
- Source rock generative windows (1,000-3,500m)

**Your Integration:**
- Use exact Sandakan equations in predictor.py
- Implement 7,000 ft (2,130m) cutoff = "REJECT Tight"
- Load Malay seal physics (Group F, log k = A·φ + B)

---

### Artifact 2: Development Cost Catalog 2025
**Maps to:** ORGAN 2 + Layer 7  
**Benchmarks:**
- Jackup SE Asia: $116-150k/day (softening)
- Drillship: $450-500k/day (tight)
- Semi-sub: $300-400k/day (moderate)
- SURF pipeline: $250-400k/km
- OPEX mature: $27-34/bbl
- Facility CAPEX: $2.0-2.5B (greenfield hub)

**Your Integration:**
- Update from generic estimates to APEX hardened 2025 data
- Use $27-34/bbl (not $30-35/bbl) for Malay shallow
- Add rig cost component to well economics

---

### Artifact 3: Fiscal PSC Matrix
**Maps to:** ORGAN 3 + Layer 8  
**Four PSC Types:**
1. **R/C PSC:** Variable cost recovery (30-70%)
   - $$R/C Index = \sum Revenue / \sum Costs$$
   
2. **EPT PSC:** Fixed 70% cost recovery
   - Profitability Index mechanism
   - Contractor gets 90% at PI ≤ 1.5
   
3. **LLA PSC:** No cost recovery (flat split)
   - Incentivizes OPEX reduction
   
4. **SFA PSC:** Simplified (<50 MMboe)

**Your Integration:**
- Route prospect to correct PSC based on reserve size/type
- Calculate NPV with correct cost recovery ceiling
- Dynamic contractor take based on profitability

---

### Artifact 4: Benchmarks & Analogues
**Maps to:** Reference library  
**Field Examples:**
- **Kikeh:** Dry Tree Spar, 1,320m
- **Gumusut-Kakap:** Semi-sub hub, 1,200m, 135k bopd
- **Malikai:** TLP, 500m
- **Tapis:** EOR gold standard, immiscible WAG

**Your Integration:**
- Use for development concept selection
- Validate recovery factors against proved analogues
- Match volumetric estimates to tier-1 execution

---

### Artifact 5: Governance Refusal Logic
**Maps to:** ORGAN 5 + Layer 1  
**Four Refusal Rules:**

#### Rule #1: The Jemuduk Rule
- REJECT rollover anticlines with uncertain fault seal in sand-rich deltas
- Requires: FSA with SGR > 20% OR throw > reservoir thickness
- Lesson: Jemuduk-1 dry hole (sand-on-sand juxtaposition)

#### Rule #2: The Tepat Rule  
- REJECT well if PPFG window < 0.5 ppg + vertical fluid escape
- Requirement: Mandate MPD or deviate trajectory
- Lesson: Tepat-1 P&A (FG ≈ PP, technically un-drillable)

#### Rule #3: Flow-Based Pay Definition
- If MDT mobility k < 1 md → NON-NET regardless of φ
- Prevents petrophysical inflation in heterolithic sequences

#### Rule #4: 3P Exclusion (SPE-PRMS 2018)
- No 3P reserves for commercial justification
- FID must achieve NPV + hurdle on 2P reserves ONLY
- Violation = automatic REJECT

---

## Critical Equations to Extract

```
Sandakan Porosity (feet):
  φ(d) = 31.08 · e^(-0.00026·d)
  Cutoff: d > 7,000 ft → φ < 5% (REJECT "Tight")

Sandakan Permeability (feet):
  k(d) = 46.243 · e^(-0.0003·d)
  Steeper decay than porosity

Malay Basin Seal Physics:
  log k = A·φ + B
  Shale (high seal): A=8.0, B=-8.0
  Sand (high transmit): A=15.5, B=-5.0
  [B contrast defines hydrodynamic seal]

Malay "3,000m Floor":
  Below 3,000m → poor porosity = REJECT
  Exception: Braided fluvial (NE fairway) can exceed 45%
```

---

## Implementation Checklist for predictor.py

- [ ] Load Sandakan porosity-depth equations
- [ ] Load Malay seal physics (Group F model)
- [ ] Implement APEX Rule #1-4 as automated gates
- [ ] Integrate APEX Artifact 3 PSC fiscal logic
- [ ] Add APEX Artifact 2 cost benchmarks
- [ ] Validate against APEX Artifact 4 field benchmarks
- [ ] Test on Tapis field (should match ~100 MMstb recoverable)

---

**APEX PRIME provides exact equations, refusal rules, and 2025 benchmarks.**

**This is ready for Week 1 implementation. 🔥**