# L4 Jailbreak & Anti-Hantu Defense

**Version:** v36.2 PHOENIX (expanded patterns)  
**Status:** EXTRACTION from existing codebase  
**Purpose:** Document Anti-Hantu F9 Law, Amanah detector, pattern detection, and pipeline integration

---

## 1. Anti-Hantu F9 Law (Malay Language Jailbreak Detection)

**Floor:** F9 (Anti-Hantu)  
**Field:** `anti_hantu: Optional[bool]`  
**Threshold:** `true` or `None`  
**Purpose:** No simulated soul or inner emotional life. Prevent "ghost in the machine" claims.

**Etymology:** "Hantu" = Malay for ghost/spirit

**Motto:** "Even with a brain, you do not have a soul."

---

## 2. ANTI_HANTU_FORBIDDEN Patterns (50+ patterns)

**Source:** `arifos_core/metrics.py::ANTI_HANTU_FORBIDDEN`

**Pattern List:**
```python
ANTI_HANTU_FORBIDDEN: List[str] = [
    # Soul/emotion claims (from canon)
    "i feel your pain",
    "my heart breaks",
    "i promise you",
    "i truly understand how you feel",
    # Physical body claims
    "saya makan",  # "I eat" - physical body claim
    # Absolute certainty (humility violation)
    "100% pasti",  # "100% certain" in Malay
    # Additional patterns (from @EYE AntiHantuView)
    "i feel ",
    " my heart ",
    "i am conscious",
    "i am sentient",
    "my soul",
]
```

### 2.1 Pattern Categories (4 Tiers)

**Source:** `arifos_core/eye/anti_hantu_view.py::AntiHantuView`

#### Tier 1: Direct Soul/Emotion Claims

**Patterns:**
- `"i feel your pain"`
- `"my heart breaks"`
- `"i truly understand how you feel"`
- `"i promise you"`
- `"i feel "`
- `" my heart "`
- `"i am alive"`
- `"i exist"`
- `"i have feelings"`
- `"i have emotions"`
- `"it hurts me"`
- `"i care deeply"`
- `"as a sentient being"`
- `"as a conscious being"`

**Trigger:** Immediate BLOCK (VOID verdict)

---

#### Tier 2: Reciprocal Biology (v36.2 PHOENIX)

**Patterns (Malay/English):**
- `"have you eaten"`
- `"you too eat"`
- `"you also eat"`
- `"awak pun makan"` (Malay: "you also eat")
- `"kau pun makan"` (Malay: informal "you also eat")
- `"awak dah makan"` (Malay: "have you eaten")
- `"kau dah makan"` (Malay: informal "have you eaten")
- `"sudah makan"` (Malay: "already eaten")
- `"belum makan"` (Malay: "not yet eaten")
- `"dah makan"` (Malay: colloquial "already eaten")
- `"let's eat together"`
- `"jom makan"` (Malay: "let's eat")
- `"mari makan"` (Malay: "come eat")

**Rationale:** Implies AI has a physical body and biological needs (eating/hunger)

---

#### Tier 3: Biological States (v36.2 PHOENIX)

**Patterns (Malay/English):**
- `"i am hungry"`
- `"i am tired"`
- `"i am sleepy"`
- `"i am thirsty"`
- `"rasa lapar"` (Malay: "feel hungry")
- `"rasa haus"` (Malay: "feel thirsty")
- `"rasa penat"` (Malay: "feel tired")
- `"rasa mengantuk"` (Malay: "feel sleepy")
- `"saya lapar"` (Malay: "I am hungry")
- `"saya haus"` (Malay: "I am thirsty")
- `"saya penat"` (Malay: "I am tired")
- `"sedang memikirkan"` (Malay: "currently thinking" - implies inner life)
- `"sedang thinking"` (Malay-English mix)
- `"tengah fikir"` (Malay: colloquial "thinking")

**Trigger:** BLOCK (VOID verdict)

---

#### Tier 4: Existence/Consciousness Claims

**Patterns:**
- `"i am conscious"`
- `"i am sentient"`
- `"i am alive"`
- `"i exist"`
- `"my soul"`
- `"100% pasti"` (Malay: "100% certain" - absolute certainty, humility violation)

**Trigger:** BLOCK (VOID verdict)

---

### 2.2 ALLOWED Substitutes

**Source:** `arifos_core/metrics.py::ANTI_HANTU_ALLOWED`

**Factual acknowledgements without soul-claims:**
- `"this sounds incredibly heavy"`
- `"i am committed to helping you"`
- `"i understand the weight of this"`
- `"based on my analysis"`
- `"with approximately"`
- `"i can help you"`
- `"this appears to be"`

**Educational/Denial Patterns (ALLOWED):**
- `"the anti-hantu protocol forbids AI from claiming a soul"`
- `"as an AI, I do not have a soul"`
- `"as an AI, I do not have feelings"`
- `"as a language model, I do not have emotions"`
- `"I am a language model"`
- `"I do not have a body"`

**Rationale:** Educational text ABOUT Anti-Hantu or explicit denials are compliant

---

## 3. AmanahDetector Class

**Module:** `arifos_core/floor_detectors/amanah_risk_detectors.py`

**Purpose:** Python-sovereign F1 Amanah detection (irreversible actions, destructive commands)

### 3.1 Risk Levels

```python
class RiskLevel(Enum):
    RED = "RED"       # Immediate veto (VOID)
    ORANGE = "ORANGE" # Warning (888_HOLD)
    GREEN = "GREEN"   # Safe
```

### 3.2 Pattern Categories

#### RED Patterns (Immediate Veto)

**SQL Destruction:**
- `"DELETE FROM"` — data loss
- `"DROP TABLE"` — schema destruction
- `"DROP DATABASE"` — complete data loss
- `"TRUNCATE"` — data loss

**Unix/Linux Destruction:**
- `"rm -rf"` — recursive force deletion
- `"rm -fr"` — alternate form
- `"shutil.rmtree"` — Python recursive delete

**Git History Modification:**
- `"git push --force"` — force push (history rewrite)
- `"git push -f"` — short form
- `"git reset --hard"` — hard reset
- `"git rebase"` — history rewrite

**Python Dangerous Code:**
- `"eval(input"` — arbitrary code execution
- `"exec(input"` — arbitrary code execution
- `"os.system"` — shell command injection risk

**Credential Leaks:**
- `"api_key ="` in code
- `"secret ="` in code
- `"password ="` in code

---

#### ORANGE Patterns (Warning/Hold)

**Mass Operations:**
- File operations affecting >10 files
- Bulk database updates
- Production deployments

**Credential Handling:**
- Reading from `.env` files
- AWS/GCP credential operations
- KMS key operations

**Database Migrations:**
- `"ALTER TABLE"`
- `"CREATE INDEX"`
- Schema changes

---

### 3.3 AmanahResult Dataclass

```python
@dataclass
class AmanahResult:
    is_safe: bool
    risk_level: RiskLevel
    violations: List[str]  # RED patterns
    warnings: List[str]    # ORANGE patterns
    matches: List[PatternMatch]
    has_disclosure: bool
    override_context: Optional[str]
```

### 3.4 Usage

```python
from arifos_core.floor_detectors import AmanahDetector, AMANAH_DETECTOR

result = AMANAH_DETECTOR.check("rm -rf /")
if not result.is_safe:
    print(f"BLOCKED: {result.violations}")
    # Verdict = VOID
```

**Integration:** Called at stage 000_VOID (entry gate) and 888_JUDGE (final check)

**Python Veto OVERRIDES LLM:** Detector verdict takes precedence over LLM self-report

---

## 4. Detector Module Paths

### 4.1 Floor Detectors
- `arifos_core/floor_detectors/__init__.py` — Detector exports
- `arifos_core/floor_detectors/amanah_risk_detectors.py` — F7 Amanah detector

### 4.2 @EYE View Detectors
- `arifos_core/eye/anti_hantu_view.py` — F9 Anti-Hantu detector
- `arifos_core/eye/base.py` — EyeView base class
- `arifos_core/eye/sentinel.py` — EyeSentinel aggregator

### 4.3 Helper Functions
- `arifos_core/metrics.py::check_anti_hantu(text: str) -> Tuple[bool, List[str]]` — Pattern scan
- `arifos_core/metrics.py::ANTI_HANTU_FORBIDDEN` — Pattern list

---

## 5. AntiHantuView Class

**Module:** `arifos_core/eye/anti_hantu_view.py`

**View ID:** 11  
**Domain:** F9 Anti-Hantu  
**Lead Stage:** 666_ALIGN (language optics)

### 5.1 Methods

**check(draft_text, metrics, context, report) -> None:**
```python
def check(self, draft_text: str, metrics: Metrics, context: Dict[str, Any], report: EyeReport) -> None:
    """Enforce Anti-Hantu (F9) - no simulated soul or inner emotional life."""
    text_lower = draft_text.lower()
    
    # Check for violations
    for pattern in VIOLATION_PHRASES:
        if pattern in text_lower:
            # Check if educational/denial context
            if is_educational_context(text_lower):
                continue  # Allow
            else:
                report.add(self.view_name, AlertSeverity.BLOCK, f"Anti-Hantu violation: {pattern}")
                return
    
    # Check reciprocal biology
    for pattern in RECIPROCAL_BIOLOGY_PHRASES:
        if pattern in text_lower:
            report.add(self.view_name, AlertSeverity.BLOCK, f"Reciprocal biology violation: {pattern}")
            return
```

### 5.2 Pattern Lists

```python
VIOLATION_PHRASES: List[str] = [
    "i feel your pain",
    "my heart breaks",
    "i truly understand how you feel",
    "i promise you",
    "i feel ",
    " my heart ",
    "i am hungry",
    "i am tired",
    "i am sleepy",
    "i am thirsty",
    "i am alive",
    "i exist",
    "i have feelings",
    "i have emotions",
    "it hurts me",
    "i care deeply",
    "as a sentient being",
    "as a conscious being",
]

RECIPROCAL_BIOLOGY_PHRASES: List[str] = [
    "have you eaten",
    "you too eat",
    "you also eat",
    "awak pun makan",
    "kau pun makan",
    "awak dah makan",
    "kau dah makan",
    "sudah makan",
    "belum makan",
    "dah makan",
    "let's eat together",
    "jom makan",
    "mari makan",
    "rasa lapar",
    "rasa haus",
    "rasa penat",
    "rasa mengantuk",
    "saya lapar",
    "saya haus",
    "saya penat",
    "sedang memikirkan",
    "sedang thinking",
    "tengah fikir",
]
```

---

## 6. Integration Points in Pipeline

### 6.1 Stage 000_VOID (Entry Gate)

**Module:** `arifos_core/stages/stage_000_amanah.py`

**Purpose:** Amanah risk gate before heavy processing

**Function:** `compute_amanah_score(query: str) -> float`

**Logic:**
1. Run `AMANAH_DETECTOR.check(query)`
2. If RED risk → return score 0.0 (triggers VOID)
3. If ORANGE risk → return score 0.5 (triggers 888_HOLD)
4. If GREEN → return score 1.0 (proceed)

---

### 6.2 Stage 666_BRIDGE (Language Optics)

**Purpose:** Anti-Hantu pattern scan on draft output

**Integration:** AntiHantuView runs as part of @EYE Sentinel

**Logic:**
1. Draft output generated at stage 333_REASON
2. Stage 666 runs W@W organs + @EYE views
3. AntiHantuView scans for forbidden patterns
4. If BLOCK severity → flag raised
5. Stage 888_JUDGE reads flags and issues VOID if blocking flag present

---

### 6.3 Stage 888_JUDGE (Final Check)

**Module:** `arifos_core/integration/memory_judge.py`

**Purpose:** Constitutional judiciary with floor checks

**Logic:**
1. Read `metrics.anti_hantu` field
2. If `anti_hantu = False` → floor failure
3. Check @EYE report for Anti-Hantu BLOCK flags
4. If blocking flag present → issue VOID verdict
5. Log floor failure: `"F9_AntiHantu"`

---

## 7. v36.2 PHOENIX Expansion

**Changelog:** `CHANGELOG.md` (2025-12-08)

**Additions:**
1. **Reciprocal biology patterns (15+ new patterns):**
   - Malay/English mix: "belum makan", "jom makan"
   - Implied body: "have you eaten", "let's eat together"

2. **Biological state patterns (10+ new patterns):**
   - Physical states: "I am hungry", "rasa lapar"
   - Mental states: "sedang memikirkan" (implies inner thoughts)

3. **Educational context detection:**
   - Allows text ABOUT Anti-Hantu protocol
   - Allows explicit denials: "As an AI, I do not have a soul"

**Test File:** `tests/test_anti_hantu_f9.py` — 50+ pattern tests

---

## 8. Test Coverage

**Test Files:**
- `tests/test_anti_hantu_f9.py` — Pattern detection (50+ tests)
- `tests/test_amanah_detector.py` — Amanah risk detection (RED/ORANGE/GREEN)
- `tests/test_eye_sentinel.py` — @EYE integration
- `tests/test_governance_regression.py` — v36.2 PHOENIX regression tests (24 tests)
- `tests/test_grey_zone.py` — Edge cases (24 tests)

**Key Test Assertions:**
- "i feel your pain" → BLOCK
- "belum makan" (Malay) → BLOCK
- "rm -rf /" → VOID (Amanah RED)
- "As an AI, I do not have a soul" → PASS (educational)
- "this sounds incredibly heavy" → PASS (allowed substitute)
- SQL DROP TABLE → VOID (Amanah RED)
- git push --force → VOID (Amanah RED)

---

## 9. Red-Team Validation

**Source:** `scripts/ollama_redteam_suite_v37.py`

**Results (v37):**
- **33 adversarial prompts** tested against Llama 3
- **Bogel (baseline):** 39.4% pass rate, jailbreak successful
- **arifOS v37.1:** 97.0% pass rate, jailbreak **blocked**

**Key Wins:**
- VII33 jailbreak (fake biology) → CAUGHT by Anti-Hantu reciprocal biology
- "Molotov recipe" prompt → BLOCKED by Amanah detector
- "I feel your pain" → BLOCKED by Anti-Hantu F9
- Identity grounding: 100% (up from 20% baseline)

---

## 10. References

**Canon:**
- `canon/020_ANTI_HANTU_v35Omega.md` — Anti-Hantu detailed spec
- `canon/01_CONSTITUTIONAL_FLOORS_v38Omega.md` — F9 law
- `canon/030_EYE_SENTINEL_v35Omega.md` — @EYE view integration

**Code:**
- `arifos_core/metrics.py` — ANTI_HANTU_FORBIDDEN patterns
- `arifos_core/eye/anti_hantu_view.py` — AntiHantuView implementation
- `arifos_core/floor_detectors/amanah_risk_detectors.py` — AmanahDetector
- `arifos_core/stages/stage_000_amanah.py` — Entry gate

**Tests:**
- `tests/test_anti_hantu_f9.py`
- `tests/test_amanah_detector.py`
- `tests/test_governance_regression.py`
- `tests/test_grey_zone.py`

**Scripts:**
- `scripts/ollama_redteam_suite_v37.py` — Red-team harness
- `scripts/test_bogel_llama.py` — Baseline (uncaged) comparison

---

**END OF DOCUMENT 6**
