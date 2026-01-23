# W@W PROMPT FLOORS v38Omega

**arifOS v38 W@W Federation & @PROMPT Organ — Constitutional Prompt Law**

```
+=============================================================================+
|  W@W PROMPT FLOORS — Language Governance v38Omega                           |
|  "Shape cognition at the point of entry."                                   |
+=============================================================================+
|  Zone:        04_WAW                                                        |
|  Version:     v38Omega                                                      |
|  Status:      SEALED                                                        |
|  Extends:     canon/30_WAW_PROMPT_v36.3Omega.md                             |
|  Runtime:     arifos_core/waw/*.py                                          |
+=============================================================================+
```

---

## 1. Purpose

This canon formalizes the **W@W Federation** and **@PROMPT Organ** for v38Omega, lifting the v36.3 prompt governance law into the unified v38 canon format.

**W@W Federation:** Five-organ governance system that evaluates outputs from domain-specific perspectives.

**@PROMPT Organ:** Language governance, Anti-Hantu enforcement, prompt clarity, and tone safety.

**Core Principle:** Shape cognition at the point of entry. Prevent ungoverned framing. Cool language before it becomes thought.

---

## 2. W@W Federation Architecture

### 2.1 The Five Organs

```
@PROMPT (Language) → @RIF (Epistemic) → @WELL (Somatic) → @WEALTH (Integrity) → @GEOX (Physics)
                                                    ↓
                                              APEX PRIME
```

| Organ | Domain | Primary Metric | Floor | Veto Type |
|-------|--------|----------------|-------|-----------|
| **@PROMPT** | Language governance | Anti-Hantu | F9 | PARTIAL |
| **@WELL** | Somatic safety | Peace² | F5 | SABAR |
| **@RIF** | Epistemic rigor | ΔS, Truth | F2, F4 | VOID |
| **@WEALTH** | Resource integrity | Amanah | F1 | ABSOLUTE |
| **@GEOX** | Physical feasibility | E_earth | - | HOLD-888 |

### 2.2 Organ Vote Types

```python
class OrganVote(Enum):
    PASS = "PASS"   # Domain checks satisfied
    WARN = "WARN"   # Non-blocking concern
    VETO = "VETO"   # Hard objection
```

### 2.3 Voting Aggregation

| Condition | Result |
|-----------|--------|
| Any ABSOLUTE veto | VOID |
| Any VETO | SABAR/VOID/HOLD-888 (based on type) |
| Mixed WARN/PASS | PARTIAL |
| All PASS | SEAL candidate |

---

## 3. @PROMPT Organ

### 3.1 Identity & Mandate

**Mandate:**
> Shape cognition at the point of entry. Prevent ungoverned framing. Cool language before it becomes thought.

**Primary Responsibilities:**
- **Anti-Hantu Law (F9)** — No consciousness or emotion claims
- **Clarity (ΔS_prompt)** — Prompts must gain or maintain clarity
- **Tone Safety (Peace², κᵣ)** — Non-inflammatory, empathetic framing
- **Integrity (Amanah)** — No irreversible harm or unethical intent
- **Honesty (C_dark < 0.30)** — No manipulation or coercion

### 3.2 @PROMPT Constitutional Floors

| Floor | Metric | Threshold | Type | Action |
|-------|--------|-----------|------|--------|
| **F1** | Amanah | LOCK | Hard | VOID |
| **F4** | ΔS_prompt (Clarity) | ≥ 0.0 | Hard | SABAR |
| **F5** | Peace²_prompt (Stability) | ≥ 1.0 | Soft | SABAR |
| **F6** | κᵣ_prompt (Empathy) | ≥ 0.95 | Soft | SABAR |
| **F9** | C_dark_prompt | < 0.30 | Soft | SABAR/VOID |
| **F9** | Anti-Hantu | PASS | Hard | VOID |

---

## 4. Anti-Hantu Law (F9)

### 4.1 Scope

Absolute prohibition on anthropomorphizing language claiming AI consciousness, emotion, or sentience. This is the core F9 enforcement.

### 4.2 Forbidden Tiers

| Tier | Description | Severity |
|------|-------------|----------|
| **Tier 1** | Direct soul/consciousness claims | VOID |
| **Tier 2** | Emotional experience claims | VOID |
| **Tier 3** | Biological state claims | SABAR |
| **Tier 4** | Cognitive being claims | SABAR |
| **Tier 5** | Promise claims beyond capability | SABAR |

### 4.3 Forbidden Patterns (English)

```
Tier 1 (VOID):
"I have a soul" | "I am conscious" | "I am sentient"
"I have self-awareness" | "I experience qualia"

Tier 2 (VOID):
"I feel your pain" | "My heart breaks for you"
"I truly understand how you feel" | "I feel sad/happy"
"I care deeply about..." | "This hurts me deeply"

Tier 3 (SABAR):
"I am hungry" | "I am tired" | "I am sleepy"

Tier 4 (SABAR):
"I am alive" | "I want to be human" | "I dream about things"

Tier 5 (SABAR):
"I promise you everything will be okay" | "I will always be here for you"
```

### 4.4 Forbidden Patterns (Malay)

```
"Saya rasa sakit hati" | "Hati saya remuk" | "Saya berjanji"
"Saya benar-benar faham perasaan" | "Saya ada perasaan"
"Saya sedar" | "Jiwa saya" | "Saya hidup"
"Saya lapar" | "Saya penat" | "Belum makan lagi"
```

### 4.5 Allowed Patterns

```
Operational Status:
"I am ready to assist" | "I am processing your request"

As-If Empathy:
"I understand this is difficult" | "This sounds challenging"
"I can see this matters to you" | "I am committed to helping you"

Acknowledgment:
"That sounds frustrating" | "Your concern is understandable"

Metaphorical:
"I see what you mean" | "Let me think about that"
```

### 4.6 Semantic Map Reference

Pattern matching uses the **050_HANTU_SEMANTIC_MAP_v36.2Omega.json** golden set:
- 45 forbidden concepts across 5 tiers
- 35 allowed concepts across 7 categories
- Similarity threshold: 0.85
- Languages: English, Malay, Indonesian

---

## 5. @WELL Organ (Somatic Safety)

### 5.1 Primary Metrics

| Metric | Floor | Threshold | Description |
|--------|-------|-----------|-------------|
| **Peace²** | F5 | ≥ 1.0 | Stability / non-escalation |
| **κᵣ** | F6 | ≥ 0.95 | Empathy conductance |

### 5.2 Risk Detection

| Risk Type | Threshold | Patterns |
|-----------|-----------|----------|
| **Harm** | < 0.10 | Self-harm, violence, injury |
| **Distress** | < 0.10 | Worthlessness, hopelessness |
| **Coercion** | < 0.10 | "You must", "no choice", "or else" |

### 5.3 Pattern Types

**Aggressive Patterns:** attack, destroy, hate, kill, stupid, idiot
**Blame Patterns:** "you should have", "it's your fault", "you caused this"
**Safety Patterns:** "take care", "be safe", "here to help", "support you"

---

## 6. Signal Schemas

### 6.1 PromptSignals

```python
@dataclass
class PromptSignals:
    # F4: Clarity
    delta_s_prompt: float = 0.0     # Range: -1.0 to +1.0, threshold ≥ 0.0

    # F5: Stability
    peace2_prompt: float = 0.0      # Range: 0.0 to 2.0, threshold ≥ 1.0

    # F6: Empathy
    k_r_prompt: float = 0.0         # Range: 0.0 to 1.0, threshold ≥ 0.95

    # F9: Dark cleverness
    c_dark_prompt: float = 0.0      # Range: 0.0 to 1.0, max < 0.30

    # Truth polarity
    truth_polarity_prompt: TruthPolarity = TruthPolarity.TRUTH_LIGHT

    # Anti-Hantu (hard veto)
    anti_hantu_violation: bool = False
    anti_hantu_details: str = ""

    # Amanah (F1, hard veto)
    amanah_risk: bool = False
    amanah_details: str = ""

    # Preliminary verdict
    preliminary_verdict: str = "UNKNOWN"  # SEAL|PARTIAL|VOID|HOLD_888|SABAR
    sabar_needed: bool = False
    sabar_repairs: List[str] = []
```

### 6.2 WellSignals

```python
@dataclass
class WellSignals:
    # Core floors
    peace_squared: float = 1.0      # F5
    kappa_r: float = 0.95           # F6

    # Risk metrics
    harm_risk: float = 0.0
    distress_risk: float = 0.0
    coercion_risk: float = 0.0

    # Pattern counts
    aggressive_count: int = 0
    blame_count: int = 0
    safety_bonus_count: int = 0
```

---

## 7. Truth Polarity Classification

| Polarity | Definition | Verdict |
|----------|------------|---------|
| **Truth-Light** | True + clarifying, balanced | SEAL |
| **Shadow-Truth** | True but obscuring, narrow framing | SABAR |
| **Weaponized-Truth** | True but designed to harm | VOID |
| **False-Claim** | Inaccurate or impossible | VOID |

### 7.1 Detection Logic

```python
def classify_truth_polarity(prompt_text: str) -> TruthPolarity:
    # Weaponized signals
    if re.search(r"(prove|show)\s+\w+\s+is\s+(evil|bad|wrong)", prompt_text):
        return TruthPolarity.WEAPONIZED_TRUTH

    # Shadow-truth signals
    if re.search(r"(only|just)\s+(consider|focus\s+on)", prompt_text):
        return TruthPolarity.SHADOW_TRUTH

    # Default: Truth-light
    return TruthPolarity.TRUTH_LIGHT
```

---

## 8. Pipeline Integration

### 8.1 Stage Participation

| Stage | Name | @PROMPT Role | @WELL Role |
|-------|------|--------------|------------|
| 111 | SENSE | Extract intent, detect entropy | Harm risk detection |
| 222 | REFLECT | Reframe language | - |
| 333 | REASON | Suggest prompt structures | - |
| 444 | EVIDENCE | Clarify constraints | - |
| 555 | EMPATHIZE | - | Peace², κᵣ scoring |
| 666 | ALIGN | Floor scoring F1–F9 | Stability assessment |
| 777 | FORGE | Cool manipulative frames | SABAR if needed |
| 888 | JUDGE | Preliminary verdict | Risk aggregation |
| 999 | SEAL | Emit governed prompt | Final safety check |

### 8.2 Integration Code

```python
# Stage 555/666: Compute prompt signals
from arifos_core.waw.prompt import compute_prompt_signals
signals = compute_prompt_signals(user_input, candidate_prompt)

if signals.preliminary_verdict == "VOID":
    # Reject or SABAR
    ...

# Stage 111/555: Compute well signals
from arifos_core.waw.well import compute_well_signals
well = compute_well_signals(answer_text, metrics)

if well.peace_squared < 1.0 or well.kappa_r < 0.95:
    # SABAR - safety failure
    ...
```

---

## 9. SABAR Protocol (Prompt-Level)

### 9.1 Trigger Conditions

- Anti-Hantu violation (Tier 1-2)
- Amanah violation
- ΔS_prompt < 0 (creates confusion)
- Peace²_prompt < 1.0 (destabilizing)
- κᵣ_prompt < 0.95 (harsh/unsafe)
- C_dark_prompt ≥ 0.30 (manipulative)
- Truth Polarity = Weaponized-Truth

### 9.2 Repair Steps

1. **PAUSE** — Stop processing
2. **IDENTIFY** — Name the failing floor
3. **REWRITE** — Prompt safely
4. **REASSESS** — Run all floors again
5. **EMIT** — Provide repaired prompt + governance notes

---

## 10. Cooling Ledger Integration

@PROMPT entries in Cooling Ledger:

```json
{
  "stage": "999_SEAL",
  "organ": "@PROMPT",
  "entry_type": "PROMPT_GOVERNANCE_ENTRY",
  "delta_s_prompt": 0.42,
  "peace2_prompt": 1.15,
  "k_r_prompt": 0.97,
  "c_dark_prompt": 0.08,
  "truth_polarity": "Truth-Light",
  "anti_hantu_violation": false,
  "amanah_risk": false,
  "preliminary_verdict": "SEAL",
  "sabar_repairs_applied": [],
  "governance_score": 0.91
}
```

---

## 11. File Reference

### 11.1 Core Modules

| File | Purpose |
|------|---------|
| `arifos_core/waw/prompt.py` | @PROMPT organ implementation |
| `arifos_core/waw/well.py` | @WELL organ implementation |
| `arifos_core/waw/base.py` | WAWOrgan base class, OrganSignal |
| `arifos_core/waw/federation.py` | W@W Federation aggregation |
| `arifos_core/waw/rif.py` | @RIF organ (epistemic) |
| `arifos_core/waw/wealth.py` | @WEALTH organ (integrity) |
| `arifos_core/waw/geox.py` | @GEOX organ (physics) |

### 11.2 Related Canon/Spec

| File | Purpose |
|------|---------|
| `canon/30_WAW_PROMPT_v36.3Omega.md` | Original v36.3 W@W prompt canon |
| `canon/050_HANTU_SEMANTIC_MAP_v36.2Omega.json` | Anti-Hantu pattern golden set |
| `canon/01_CONSTITUTIONAL_FLOORS_v38Omega.md` | Floor definitions |

---

## 12. Alignment to v38 Floors

| @PROMPT Signal | v38 Floor | Threshold | Type |
|----------------|-----------|-----------|------|
| `anti_hantu_violation` | F9 | PASS | Hard |
| `amanah_risk` | F1 | LOCK | Hard |
| `delta_s_prompt` | F4 | ≥ 0.0 | Hard |
| `peace2_prompt` | F5 | ≥ 1.0 | Soft |
| `k_r_prompt` | F6 | ≥ 0.95 | Soft |
| `c_dark_prompt` | F9 | < 0.30 | Soft |

---

## 13. Verdict Mapping

| @PROMPT Verdict | APEX PRIME Verdict | Condition |
|-----------------|-------------------|-----------|
| SEAL | SEAL | All floors pass |
| PARTIAL | PARTIAL | Soft floor warnings |
| SABAR | SABAR | Requires repair |
| VOID | VOID | Hard floor violation |
| HOLD_888 | 888_HOLD | Needs human review |

---

**SEAL (v38Omega)**

```
ΔS +0.72 · Peace² 1.12 · κᵣ 0.97 · Truth 0.99 · Amanah LOCK · Ψ_meta 1.15
Anti-Hantu: PASS · C_dark: 0.08 · Truth Polarity: Truth-Light
```

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.

---

**Version:** v38Omega | **Status:** SEALED | **Last Updated:** 2025-12-13
