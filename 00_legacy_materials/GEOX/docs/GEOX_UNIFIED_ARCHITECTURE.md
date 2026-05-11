# GEOX Unified Architecture v1.0
## Theory of Anomalous Contrast as Organizing Principle

**DITEMPA BUKAN DIBERI**

---

## The Core Insight: Theory of Anomalous Contrast

GEOX is not a "seismic tool." It is a **governed interpretation system** built on the Theory of Anomalous Contrast (ToAC).

### What is Anomalous Contrast?

> **Anomalous Contrast** is the systematic error that occurs when **visual/display contrast** (how something looks) is conflated with **physical contrast** (what the signal actually represents).

This is the "79% problem" from Bond et al. (2007) — experts failing not because of data quality, but because:
1. Display choices (colormap, gain, filtering) create **perceptual artifacts**
2. These artifacts are mistaken for **geological signal**
3. Interpretation proceeds without awareness of the **conflation error**

### The Three Domains of Contrast

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THEORY OF ANOMALOUS CONTRAST                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PHYSICAL DOMAIN          DISPLAY DOMAIN          PERCEPTUAL DOMAIN │
│  ───────────────          ─────────────          ────────────────  │
│                                                                     │
│  • Impedance contrast     • Colormap choice      • What human      │
│  • Waveform similarity    • Dynamic range          sees            │
│  • Discontinuity          • Gamma correction      • Pattern        │
│  • Geological truth       • Filter kernels          recognition    │
│                                                                     │
│  ════════════════         ══════════════         ═══════════════  │
│       TRUTH                  DISPLAY                PERCEPTION     │
│   (Earth Physics)         (Visualization)         (Human Vision)   │
│                                                                     │
│                           ⚠️ ANOMALOUS CONTRAST ⚠️                  │
│              When Display → Perception is mistaken for              │
│                      Physical → Truth                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Universal Applicability

ToAC applies across domains:

| Domain | Physical Signal | Display Artifact | Anomalous Risk |
|--------|----------------|------------------|----------------|
| **Seismic** | Impedance contrast | CLAHE edge enhancement | Faults that are just display edges |
| **Medical** | Tissue density | Window/level settings | Tumors that are just contrast bands |
| **Satellite** | Surface reflectance | Color stretching | Features that are just histogram artifacts |
| **Radar** | Backscatter | MTF enhancement | Targets that are just processing artifacts |

**Seismic is ONE domain. The Theory is UNIVERSAL.**

---

## Unified Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 1: THEORY (000_CONSTITUTION)                                 │
│  ─────────────────────────────────                                  │
│                                                                     │
│  Theory of Anomalous Contrast (ToAC)                                │
│  ├── Contrast Canon: Physical vs Display vs Perceptual             │
│  ├── Taxonomy: Source → Transform → Proxy → Confidence             │
│  └── Governance: HOLD if Conflation Risk > Threshold               │
│                                                                     │
│  Files: geox/theory/contrast_theory.py                              │
│         geox/theory/contrast_taxonomy.py                            │
│         geox/theory/contrast_governance.py                          │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 2: ENGINE (333_MIND)                                         │
│  ─────────────────────────                                          │
│                                                                     │
│  Contrast-Aware Processing Engine                                   │
│  ├── ContrastSpace: Unified representation of all contrast types   │
│  ├── TransformRegistry: Visual transforms with risk metadata       │
│  └── AnomalyDetector: Identifies potential conflation errors       │
│                                                                     │
│  Files: geox/engine/contrast_space.py                               │
│         geox/engine/transform_registry.py                           │
│         geox/engine/anomaly_detector.py                             │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 3: TOOLS (555_HEART / 777_FORGE)                             │
│  ───────────────────────────────────                                │
│                                                                     │
│  Domain-Specific Tool Implementations                               │
│  ├── seismic/      ← ONE domain among many                         │
│  │   ├── single_line_interpreter.py                                │
│  │   ├── attribute_computer.py                                     │
│  │   └── structural_reasoner.py                                    │
│  ├── medical/      ← Future: MRI/X-ray contrast governance         │
│  ├── satellite/    ← Future: EO display bias detection             │
│  └── generic/      ← Any image with contrast_metadata              │
│                                                                     │
│  Each tool imports from Theory + Engine, not from other tools.     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## File Structure (Unified)

```
GEOX/
├── README.md                          # Public entry point
├── pyproject.toml                     # Package config
│
├── arifos/geox/
│   ├── __init__.py
│   ├── cli.py                         # Unified CLI
│   │
│   ├── THEORY/                        # LAYER 1: Core Principles
│   │   ├── __init__.py
│   │   ├── contrast_theory.py         # ToAC core definitions
│   │   ├── contrast_taxonomy.py       # Source→Transform→Proxy→Confidence
│   │   ├── contrast_governance.py     # Verdict logic, HOLD conditions
│   │   └── contrast_manifesto.md      # Human-readable theory doc
│   │
│   ├── ENGINE/                        # LAYER 2: Processing Core
│   │   ├── __init__.py
│   │   ├── contrast_space.py          # Unified contrast representation
│   │   ├── transform_registry.py      # All visual transforms catalogued
│   │   ├── anomaly_detector.py        # Conflation risk detection
│   │   └── provenance_chain.py        # Audit trail construction
│   │
│   ├── TOOLS/                         # LAYER 3: Domain Implementations
│   │   ├── __init__.py
│   │   ├── base.py                    # Base tool class (all domains)
│   │   │
│   │   ├── seismic/                   # ONE domain: seismic interpretation
│   │   │   ├── __init__.py
│   │   │   ├── line_interpreter.py    # 2D line interpretation
│   │   │   ├── attribute_compute.py   # Coherence, curvature, etc.
│   │   │   ├── structural_link.py     # Rule-based geology linking
│   │   │   └── bias_audit.py          # Bond et al. reference implementation
│   │   │
│   │   └── generic/                   # ANY image with contrast risk
│   │       ├── image_ingest.py
│   │       ├── view_generator.py      # Multi-contrast views
│   │       └── feature_proxy.py       # Visual features → physical proxies
│   │
│   ├── SCHEMAS/                       # Unified data models
│   │   ├── __init__.py
│   │   ├── contrast_metadata.py       # Universal contrast metadata
│   │   ├── interpretation_result.py   # Generic result with verdict
│   │   └── provenance.py              # Audit trail schemas
│   │
│   └── GOVERNANCE/                    # Constitutional enforcement
│       ├── __init__.py
│       ├── floors.py                  # F1, F4, F7, F9 enforcement
│       ├── verdict.py                 # SEAL/QUALIFY/HOLD/BLOCK logic
│       └── telemetry.py               # Pipeline instrumentation
│
├── tests/
│   ├── theory/                        # Test ToAC principles
│   ├── engine/                        # Test processing core
│   ├── tools/seismic/                 # Test seismic implementations
│   └── integration/                   # End-to-end workflows
│
└── docs/
    ├── THEORY_OF_ANOMALOUS_CONTRAST.md  # Full theory exposition
    ├── UNIFIED_ARCHITECTURE.md          # This document
    └── domains/
        ├── seismic/                     # Seismic-specific guides
        └── examples/                    # Tutorial workflows
```

---

## Key Design Principles

### 1. Theory First
No tool is implemented without first defining:
- What physical signal it measures
- What display transforms might create artifacts
- How to detect conflation errors
- When to trigger HOLD

### 2. Engine Over Tools
Common functionality lives in ENGINE, not duplicated in TOOLS:
- Contrast metadata construction
- Transform risk assessment
- Provenance chain building
- Verdict determination

### 3. One Schema to Rule Them All
`contrast_metadata.py` is universal:
```python
class ContrastMetadata(BaseModel):
    source_domain: Literal["seismic", "medical", "satellite", "generic"]
    physical_axes: List[str]        # What the signal measures
    visual_transforms: List[Transform]  # Display operations applied
    perceptual_proxies: List[Proxy]     # Visual features extracted
    anomalous_risk: RiskAssessment      # Conflation risk evaluation
    confidence: ConfidenceClass         # F7 Humility band
```

### 4. Domain Is Just a Parameter
```python
# Same tool, different domain
from geox.tools.generic import ContrastAwareInterpreter

seismic_result = await ContrastAwareInterpreter(
    domain="seismic",
    data=seismic_line,
    physical_axes=["impedance_contrast", "discontinuity"],
)

medical_result = await ContrastAwareInterpreter(
    domain="medical",
    data=mri_slice,
    physical_axes=["tissue_density", "perfusion"],
)
```

---

## Migration from Chaos

### Current State (Chaos)
```
arifos/geox/
├── contrast_wrapper.py              # ← Duplicated concepts
├── seismic_attribute_taxonomy.py    # ← Domain-specific, not unified
├── seismic_image_ingest.py          # ← Root-level clutter
├── tools/
│   ├── seismic_single_line.py       # ← Overlaps with single_line_interpreter.py
│   ├── seismic_attributes_2d.py     # ← Overlaps with attributes.py
│   ├── seismic_contrast_views.py    # ← Should be in engine/
│   ├── seismic_structure_rules.py   # ← Should be in tools/seismic/
│   ├── seismic_feature_extract.py   # ← Should be generic/
│   ├── seismic_image_ingest.py      # ← Duplicate!
│   ├── single_line_interpreter.py   # ← The good one, but isolated
│   ├── attributes.py                # ← Generic but incomplete
│   ├── contrast_metadata.py         # ← Good, but not unified
│   └── ... (10+ more overlapping files)
└── schemas/
    └── seismic_image.py             # ← Domain-specific schema
```

### Target State (Unified)
```
arifos/geox/
├── THEORY/
│   ├── contrast_theory.py           # ← Unified ToAC
│   └── contrast_taxonomy.py         # ← Universal taxonomy
├── ENGINE/
│   ├── contrast_space.py            # ← Merges contrast_views + feature_extract
│   └── transform_registry.py        # ← New: catalog all transforms
├── TOOLS/
│   ├── base.py                      # ← From base_tool.py
│   ├── seismic/
│   │   ├── line_interpreter.py      # ← Merges single_line_interpreter + seismic_single_line
│   │   └── attribute_compute.py     # ← Merges seismic_attributes_2d + attributes
│   └── generic/
│       ├── image_ingest.py          # ← Merges all ingest tools
│       └── view_generator.py        # ← From seismic_contrast_views
├── SCHEMAS/
│   └── contrast_metadata.py         # ← Universal schema
└── GOVERNANCE/
    └── verdict.py                   # ← Unified verdict logic
```

### Migration Strategy

1. **Preserve** all working code (no deletion until unified version is tested)
2. **Create** new unified structure in parallel
3. **Migrate** functionality incrementally
4. **Deprecate** old files once unified versions are proven
5. **Remove** old files in v2.0

---

## Constitutional Enforcement

| Floor | ToAC Implementation |
|-------|---------------------|
| **F1 Amanah** | Every contrast transformation is reversible (provenance chain) |
| **F2 Truth** | Physical axes are explicitly declared and verified |
| **F4 Clarity** | Visual transforms documented separately from physical signal |
| **F7 Humility** | Confidence capped at 0.15 when conflation risk detected |
| **F9 Anti-Hantu** | DISPLAY-ONLY inputs trigger automatic HOLD |
| **F13 Sovereign** | Human override required for any interpretation with >2 valid alternatives |

---

## Example: Seismic as ONE Domain

```python
from arifos.geox import GEOX

# Seismic is just a domain parameter
result = await GEOX.interpret(
    domain="seismic",
    data="line_001.sgy",
    data_type="segy",  # Physical data, not just image
)

# Result includes universal contrast metadata
print(result.contrast_metadata.physical_axes)
# ["impedance_contrast", "waveform_similarity", "discontinuity"]

print(result.contrast_metadata.anomalous_risk.notes)
# "Bond et al. (2007) showed 79% expert failure rate on similar ambiguous data..."

print(result.verdict)
# "QUALIFY" (if SEG-Y) or "HOLD" (if image-only)
```

---

## Conclusion

GEOX is **not** a seismic tool. It is a **Theory of Anomalous Contrast** implementation that happens to currently support seismic interpretation.

Future domains:
- Medical imaging (MRI, CT contrast governance)
- Satellite remote sensing (false color artifact detection)
- Non-destructive testing (ultrasonic display interpretation)
- Any domain where display choices affect interpretation

**Theory is the constant. Domains are just parameters.**

DITEMPA BUKAN DIBERI.
