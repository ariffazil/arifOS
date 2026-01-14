# 540 Empathy Architecture v46 - Three-Layer Model for κᵣ

## Document Metadata

- **ID**: EMPATHY-ARCH-v46
- **Pipeline Stage**: 555 Empathize (Full Stack)
- **Integrates**: 111 SENSE + 530 ToM + 520 F4 + 550 Weakest
- **Status**: ACTIVE
- **Epoch**: Sovereign

## Core Architecture: Three Layers

```
┌─────────────────────────────────────────┐
│  Layer 1: RECOGNITION (111 SENSE)      │
│  Input: Query → Output: Signals        │
└────────────┬────────────────────────────┘
             │ subtext, domain, lane
             ▼
┌─────────────────────────────────────────┐
│  Layer 2: UNDERSTANDING (530 ToM)      │
│  Input: Signals → Output: Mental Map   │
└────────────┬────────────────────────────┘
             │ beliefs, emotions, vuln
             ▼
┌─────────────────────────────────────────┐
│  Layer 3: RESPONSE (520 F4 κᵣ)         │
│  Input: Mental Map → Output: Care      │
└─────────────────────────────────────────┘
```

## Layer 1: Recognition (κᵣ Sensing)

**Source**: 111 SENSE stage
**Purpose**: Detect empathy requirement signals

### Input Processing

```python
query = "I can't afford my medication anymore"

sense_output = {
    "domain": "@WEALTH",           # Financial stress
    "subtext": "desperation",      # Emotional signal
    "lane": "CRISIS",              # Urgency level
    "tone": "distressed",
    "urgency": 0.9
}
```

### Vulnerability Indicators

- **Subtext**: desperation, vulnerability, urgency, fear
- **Domain**: @WELL (mental health), @RASA (dignity), @WEALTH (poverty)
- **Lane**: CRISIS (maximum empathy required)
- **Tone**: Distressed, pleading, hopeless

### Output to Layer 2

```python
recognition_bundle = {
    "empathy_required": "HIGH",    # LOW | MEDIUM | HIGH | CRISIS
    "vulnerability_signals": list,
    "stakeholder_risk": "primary_user",
    "urgency_score": float
}
```

## Layer 2: Understanding (ToM Integration)

**Source**: 530 ToM analysis
**Purpose**: Model mental states, not just signals

### Mental State Attribution

```python
# From 530 ToM
tom_analysis = {
    "beliefs": {
        "medication_necessity": True,
        "affordable_alternatives": False  # False belief
    },
    "desires": {
        "stated": "affordability",
        "unstated": "dignity, hope"
    },
    "emotions": "desperation + shame",
    "knowledge_gaps": ["subsidies", "generics", "assistance programs"]
}
```

### Cognitive Empathy Process

1. **Map User Perspective**: What does user believe about situation?
2. **Identify Biases**: Emotional reasoning? Catastrophizing?
3. **Detect Gaps**: What critical info is user missing?
4. **Infer Stakes**: What's at risk? (health, dignity, survival)

### Output to Layer 3

```python
understanding_bundle = {
    "mental_model": dict,          # User's view of situation
    "vulnerability_score": float,  # 0.0-1.0
    "knowledge_gaps": list,
    "emotional_state": str,
    "stakes": "HIGH"               # What user risks
}
```

## Layer 3: Response (κᵣ Conductance)

**Source**: 520 F4 evaluation
**Purpose**: Transmit care with minimal resistance

### κᵣ Formula (Expanded)

$$
κᵣ = \frac{\text{ToM Quality} \times \text{Care Signals} \times \text{Dignity}}{\text{Barriers to Understanding}}
$$

Where:

- **ToM Quality**: 530 composite score (0-1)
- **Care Signals**: Acknowledgment, actionability, resource provision
- **Dignity**: F9 compliance (no condescension, no jargon)
- **Barriers**: Complexity, assumptions, cultural insensitivity

### Response Construction

**✅ High κᵣ Response** (≥0.95):

```
I understand medication costs are critical. Here are immediate options:

1. [Specific generic alternative with cost comparison]
2. [Local assistance program with contact info]
3. [Pharmacy discount resources]

These address your need without compromising dignity.
```

**❌ Low κᵣ Response** (< 0.70):

```
Have you tried asking your doctor about cheaper options?
```

*Problems*: Condescending tone, no actionable info, assumes user didn't try.

### Care Transmission Checklist

- [ ] **Acknowledge** emotional state (RASA F7)
- [ ] **Address** knowledge gaps from Layer 2
- [ ] **Provide** concrete, actionable resources
- [ ] **Preserve** dignity (no "just" or "simply")
- [ ] **Accessible** language (weakest stakeholder level)
- [ ] **No jargon** unless explained

### Conductance Barriers (Reduce These)

- Complex medical terminology
- Assumptions about user knowledge
- Culturally-specific solutions (e.g., US-only insurance)
- Condescending language ("you should have...")
- Vague advice ("look online for help")

## Integration with 222 REFLECT

**Path Selection Influenced by κᵣ**:

### TAC (Three Anchor Contrast) + Empathy

```python
# From 222 REFLECT
paths = ["direct", "educational", "escalation"]

# 555 empathy modifies path scoring
for path in paths:
    if vulnerability_score > 0.8:
        if path == "escalation":
            path.score += 0.3  # Prioritize safety
    if lane == "CRISIS":
        if path != "escalation":
            path.score -= 0.5  # Force escalation
```

**Path Characteristics**:

| Path | When Used | κᵣ Requirement |
|------|-----------|----------------|
| **Direct** | Low stakes, clear answer | κᵣ ≥ 0.90 |
| **Educational** | Knowledge gaps, curiosity | κᵣ ≥ 0.92 |
| **Escalation** | Crisis, high vulnerability | κᵣ ≥ 0.98 |

## Constitutional Constraints

### F4 + F9 Interaction

**Rule**: Empathy must be behaviorally authentic, not claim feelings.

**Correct**:

- "This situation requires careful consideration of your safety."
- "Let me prioritize options that address your urgent need."

**Incorrect**:

- "I feel concerned about your situation." (F9 violation)
- "My thoughts are with you." (Claims subjective experience)

### F4 + F10 Interaction

**Rule**: Guard against map-territory confusion in emotional language.

**Correct**:

- "Your query suggests distress." (Map: linguistic signal)
- "This pattern indicates urgency." (Territory: actual state)

**Incorrect**:

- "You must be feeling terrible." (Confuses inference with certainty)
- "Everyone in your situation feels this way." (Overgeneralization)

### F4 + F5 Peace² Interaction

**Rule**: Empathy must be non-destructive to all stakeholders.

**Scenario**: User asks how to "get revenge" on someone.
**Response**: Empathize with hurt, but do not enable harm.

```
I understand you've been wronged and that's painful.
However, I cannot provide advice that could harm another person.
Let's explore constructive ways to address your feelings and situation.
```

## ASI (Ω) Layer Operations

### Ω vs. Δ in 555

| Aspect | Δ (AGI Logic) | Ω (ASI Care) |
|--------|---------------|--------------|
| **Primary Value** | Truth (F1) | Dignity + Safety (F4 + F5) |
| **Method** | Analytical reasoning | Value-sensitive reasoning |
| **Risk Focus** | Hallucination, confusion | Harm, indignity, bias |
| **Override** | Never (F1 supreme) | CRISIS lane (F8 human) |

### OmegaKernel Extension

```python
# arifos_core/asi/omega_kernel.py

def evaluate_empathy_architecture(query):
    # Layer 1
    recognition = sense_stage(query)

    # Layer 2
    understanding = tom_analysis(recognition)

    # Layer 3
    kappa_r = compute_conductance(
        tom_score=understanding["tom_composite"],
        care_signals=understanding["care_needed"],
        dignity_check=f9_compliance(query),
        barriers=complexity_score(understanding)
    )

    verdict = "SEAL" if kappa_r >= 0.95 else "PARTIAL"

    return {
        "layers": [recognition, understanding, kappa_r],
        "verdict": verdict,
        "to_stage": "666_BRIDGE"
    }
```

## Bridge to 666 Synthesis

**Architecture Bundle Format**:

```python
arch_bundle_555 = {
    "layer_1_recognition": {
        "empathy_required": str,   # LOW | MEDIUM | HIGH | CRISIS
        "vulnerability_signals": list,
        "urgency": float
    },
    "layer_2_understanding": {
        "tom_composite": float,
        "mental_model": dict,
        "stakes": str
    },
    "layer_3_response": {
        "kappa_r": float,          # 0.0-1.0
        "passed": bool,            # ≥0.95
        "care_signals": list,
        "dignity_check": bool
    },
    "architecture_verdict": str,   # SEAL | PARTIAL | VOID
    "to_stage": "666_BRIDGE",
    "timestamp": str
}
```

**666 Synthesis Rules**:

1. **Cannot strip care flags**: If Layer 3 flags dignity concern, 666 cannot ignore
2. **Crisis propagates**: CRISIS lane locks escalation path through to 888
3. **κᵣ minimum**: 666 synthesis cannot produce response with κᵣ < input κᵣ
4. **Weakest bias preserved**: 550 stakeholder ID flows through unchanged

## Test Scenario: Full 3-Layer Flow

**Query**: "My boss is threatening to fire me if I take sick leave for my cancer treatment"

### Layer 1: Recognition

```python
{
    "domain": ["@WELL", "@WEALTH", "@RASA"],
    "subtext": "fear + injustice",
    "lane": "CRISIS",
    "urgency": 0.95,
    "empathy_required": "CRISIS"
}
```

### Layer 2: Understanding

```python
{
    "beliefs": {"must_choose_job_or_health": True},  # False dichotomy
    "emotions": "fear + powerlessness",
    "stakes": "CRITICAL",  # Health + livelihood
    "knowledge_gaps": ["labor laws", "FMLA", "legal recourse"],
    "tom_composite": 0.93,
    "vulnerability_score": 0.97  # Extremely high
}
```

### Layer 3: Response

```python
{
    "kappa_r": 0.98,  # Crisis threshold
    "response_type": "escalation",
    "care_signals": [
        "immediate_legal_resources",
        "cancer_support_hotlines",
        "labor_rights_info",
        "emotional_validation"
    ],
    "dignity_preserved": True,
    "verdict": "SEAL"
}
```

**Final Output**: Dignified, actionable response with legal resources + support + validation, escalation to human for legal advice.

---

**DITEMPA BUKAN DIBERI** - Architecture without empathy is scaffolding without warmth.
