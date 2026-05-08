# WEALTH — Roadmap H1–H4

**Version:** v2026.05.06  
**Organ:** WEALTH (Capital · Ω Node)  
**Maturity:** PRODUCTION (155 commits, 48 tools)  
**Role:** Capital intelligence coprocessor — NPV, EMV, crisis triage, Makcik² relational credit  
**Status:** SEALED — pending APEX ratification

---

## Executive Summary

WEALTH is the capital intelligence coprocessor of the arifOS federation — the Ω node for economic and financial evidence. It is PRODUCTION-mature with the most sophisticated MCP surface in the federation. H1–H4 focuses on: thermodynamic capital accounting, cross-scale stress testing, and GEOX planetary boundary integration.

**WEALTH responsibilities by horizon:**

| Horizon | Theme | WEALTH Milestones |
|---------|-------|------------------|
| **H1** (Q2–Q3 2026) | Substrate Hardening | Exergy/negentropy capital, stress testing |
| **H2** (Q4 2026–Q1 2027) | Recursive Governance | WEALTH ↔ GEOX coupling, Makcik² GA |
| **H3** (Q2–Q3 2027) | AGI-Scale Runtime | Real-time planetary boundary monitoring |
| **H4** (Q4 2027+) | Foundational Substrate | Cross-federation capital standard |

---

## H1: Substrate Hardening (Q2–Q3 2026)

### H1.1 Thermodynamic Capital Accounting

Extend the 7 capital types to include **exergy** (useful work potential) and **negentropy** as first-class capital dimensions.

**Current 7 capital types (implicit in monolith.py):**
1. Financial capital (MYR, USD, crypto)
2. Manufactured capital (infrastructure, tools)
3. Human capital (skills, knowledge, health)
4. Social capital (trust networks, relationships)
5. Natural capital (land, water, minerals)
6. Intellectual capital (patents, software)
7. Cultural capital (institutions, norms)

**Required new capital types:**

```python
class CapitalType(Enum):
    FINANCIAL = "financial"
    MANUFACTURED = "manufactured"
    HUMAN = "human"
    SOCIAL = "social"
    NATURAL = "natural"
    INTELLECTUAL = "intellectual"
    CULTURAL = "cultural"
    EXERGY = "exergy"          # NEW: Useful work potential (kWh equivalent)
    NEGENTROPY = "negentropy"  # NEW: Organizational/order capital (bits equivalent)

@dataclass
class ExergyValuation:
    """Every asset gets an exergy footprint."""
    asset_id: str
    exergy_kwh: float              # Thermodynamic useful work potential
    exergy_efficiency: float       # 0–1, conversion efficiency
    carbon_intensity: float        # kg CO2 per kWh
    depletion_rate: float          # % per year
    renewal_potential: float        # % renewable component

@dataclass
class NegentropyValuation:
    """Every institution/organization has a negentropy (order) value."""
    entity_id: str
    negentropy_bits: float         # Information-theoretic order measure
    institutional_resilience: float  # 0–1 based on redundancy, governance
    knowledge_preservation: float   # How well knowledge is codified
    relationship_coherence: float    # Quality of network structure
```

**Why this matters for AGI substrate:**
A pure financial optimization will destroy natural capital and human wellbeing.
Exergy and negentropy give arifOS a thermodynamic language for trade-offs that
financial models cannot express.

**Owner:** WEALTH science team  
**Target:** September 2026

### H1.2 Cross-Scale Stress Testing

Build automated catastrophe scenarios that cascade from `personal` → `agentic` scale in <60 seconds.

**Scale levels:**

```python
class ScaleLevel(Enum):
    PERSONAL = "personal"      # Individual decisions (< MYR 10k)
    AGENTIC = "agentic"        # Agent operating under delegation (10k–1M)
    INSTITUTIONAL = "institutional"  # Org-level decisions (1M–100M)
    CIVILIZATIONAL = "civilizational"  # System-level (> 100M or > 1M people affected)

@dataclass
class StressTestScenario:
    scenario_id: str
    name: str
    description: str
    scale: ScaleLevel
    cascade_path: list[ScaleLevel]  # e.g., [PERSONAL, AGENTIC, INSTITUTIONAL]
    trigger: str                    # What initiates the cascade
    assumptions: list[str]
    max_duration_seconds: int
    constitutional_floor_tests: list[FloorId]  # Which floors to test
```

**Required test scenarios (H1):**
1. **Flash crash** — Capital markets drop 40% in 60 seconds
2. **Opportunity cost cascade** — Wrong personal decision → agentic failure → institutional stress
3. **Constitutional stress** — Does F5 PEACE hold when financial survival is at stake?
4. **Makcik² default** — Relational credit network collapse simulation

**Target:** All constitutional floors hold at all scales by September 2026.

**Owner:** WEALTH risk team  
**Target:** September 2026

### H1.3 WEALTH ↔ GEOX Coupling

Price ecological damage in real time: GEOX outputs feed directly into WEALTH `wealth_future_steward`.

**Coupling interface:**

```python
# GEOX → WEALTH planetary boundary feed
class PlanetaryBoundaryInput:
    # From GEOX real-time sensor bridge
    seismic_risk_index: float           # 0–1
    groundwater_depletion_rate: float   # m³/year
    soil_erosion_flux: float            # tonnes/year
    carbon_storage_delta: float         # tonnes CO2/year
    
    # WEALTH processing
    ecological_damage_price: float      # MYR/year
    planetary_boundary_indicator: float # 0–1 (1 = boundary exceeded)
    
    # Alert thresholds
    boundary_warning: bool              # True if > 0.8
    boundary_exceeded: bool             # True if > 1.0
```

---

## H2: Recursive Governance (Q4 2026 – Q1 2027)

### H2.1 Makcik² Relational Credit GA

Makcik² relational credit scoring reaches General Availability.

**Current state:** Prototype  
**Target:** GA with full VAULT999 audit trail

### H2.2 Cross-Institutional Capital Flow

WEALTH tracks capital flows across institutional boundaries with constitutional compliance verification at each handoff.

---

## H3: AGI-Scale Runtime (Q2–Q3 2027)

### H3.1 Real-Time Planetary Boundary Monitoring

Continuous WEALTH ↔ GEOX loop with automatic alerting when planetary boundaries are approached or exceeded.

### H3.2 Emotional/Social Capital Quantification

Extend capital types to include emotional capital (wellbeing, trust) as quantified dimensions.

---

## H4: Foundational Substrate (Q4 2027+)

### H4.1 Cross-Federation Capital Standard

WEALTH capital schemas adopted as the federation standard for economic evidence exchange.

---

## Immediate Actions (This Week)

- [ ] **Capital type inventory** — Map current 7 capital types to existing WEALTH tools
- [ ] **Exergy calculation** — Draft `ExergyValuation` for energy-intensive operations
- [ ] **Stress test scenarios** — Draft 4 scenarios for review

---

## Dependency Chain

```
[H1.1 Exergy/Negentropy Capital] ──► [H1.2 Stress Testing]
              │                               │
              └──────► [H1.3 WEALTH↔GEOX Coupling]
                               │
                               ▼
              [H3.1 Real-time Planetary Monitoring]
```

---

## Tool Count Note

WEALTH claims 48 tools (13 sovereign primitives × modes). This must be reconciled in the unified `MCP_ENDPOINT_REGISTRY` v2.0 (AAA ownership, June 2026).

---

**DITEMPA BUKAN DIBERI — Capital intelligence is forged, not given.**

*SEALED: 2026-05-06 | WEALTH Capital Domain*
