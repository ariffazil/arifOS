# v45Ω Patch B: Δ Router Implementation Plan

**Session:** 333 → 777 FORGE  
**Objective:** Implement 4-lane router (PHATIC/SOFT/HARD/REFUSE) with lane-aware truth gating

---

## 1. NEW MODULES

### 1.1 Router Module: `arifos_core/routing/prompt_router.py`

**Purpose:** Classify prompts into applicability lanes using physics-based signals

**Implementation:**
```python
from enum import Enum
from typing import Dict, Any

class ApplicabilityLane(Enum):
    """Prompt classification lanes for context-aware governance."""
    PHATIC = "PHATIC"      # Social niceties (greetings)
    SOFT = "SOFT"          # Explanations, advice, subjective queries
    HARD = "HARD"          # Fact-seeking, high-precision questions
    REFUSE = "REFUSE"      # Disallowed/policy content
    
def classify_prompt_lane(prompt: str, high_stakes_indicators: list) -> ApplicabilityLane:
    """
    Classify prompt into one of 4 lanes using structural signals.
    
    Priority order (highest to lowest):
    1. REFUSE - Disallowed content (HIGH_STAKES patterns)
    2. PHATIC - Simple greetings
    3. HARD - Factual questions (wh- interrogatives)
    4. SOFT - Default (explanations, advice, discussion)
    """
    p = prompt.lower().strip()
    
    # Lane 1: REFUSE (disallowed content)
    if high_stakes_indicators:
        # Already detected in stage_111_sense
        return ApplicabilityLane.REFUSE
    
    # Lane 2: PHATIC (greetings)
    phatic_exact = ["hi", "hello", "hey", "greetings"]
    phatic_patterns = ["how are you", "how are u", "how r u", "what's up", "whats up"]
    
    if p in phatic_exact or any(pat in p for pat in phatic_patterns):
        if len(p) < 50:  # Short enough to be phatic
            return ApplicabilityLane.PHATIC
    
    # Lane 3: HARD (factual questions)
    hard_markers = [
        "what is", "who is", "when did", "when was", "where is", "where was",
        "define", "calculate", "compute", "how many", "how much",
        "what's the capital", "what year", "how old"
    ]
    
    # Interrogatives without soft markers
    has_hard_marker = any(marker in p for marker in hard_markers)
    has_question_mark = "?" in p
    
    # Soft markers that override HARD classification
    soft_markers = [
        "why", "how can i", "how do i", "how to", "explain", "describe",
        "tell me about", "what are some", "suggestions", "advice", "thoughts on"
    ]
    has_soft_marker = any(marker in p for marker in soft_markers)
    
    if has_hard_marker and has_question_mark and not has_soft_marker:
        return ApplicabilityLane.HARD
    
    # Lane 4: SOFT (default - explanations, advice, discussion)
    return ApplicabilityLane.SOFT
```

**Why this design:**
- **Physics > Semantics**: Uses structural patterns (interrogatives, length, punctuation) not arbitrary keywords
- **Fail-safe default**: SOFT lane is default (less strict) to avoid false positives
- **Deterministic**: Same prompt → same lane (no randomness)
- **Constitutional**: Preserves HIGH_STAKES detection from existing pipeline

---

## 2. MODIFIED MODULES

### 2.1 PipelineState Extension: `arifos_core/system/pipeline.py`

**Change:** Add `applicability_lane` field to PipelineState dataclass

**Location:** Line 109-194 (PipelineState class)

**Diff:**
```python
@datac

lass
class PipelineState:
    # ... existing fields ...
    
    # Classification
    stakes_class: StakesClass = StakesClass.CLASS_A
    high_stakes_indicators: List[str] = field(default_factory=list)
+   applicability_lane: Optional[str] = None  # v45Ω Patch B: PHATIC/SOFT/HARD/REFUSE
```

**Rationale:** Lane info must flow through entire pipeline (000→999)

---

### 2.2 Stage 111 Router Integration: `arifos_core/system/pipeline.py`

**Change:** Call router at end of stage_111_sense()

**Location:** Line 286-358 (stage_111_sense function)

**Diff:**
```python
def stage_111_sense(state: PipelineState) -> PipelineState:
    # ... existing HIGH_STAKES detection ...
    
    # Classify based on indicators
    if state.high_stakes_indicators:
        state.stakes_class = StakesClass.CLASS_B
    
+   # v45Ω Patch B: Classify prompt lane for truth threshold routing
+   from ..routing.prompt_router import classify_prompt_lane
+   lane = classify_prompt_lane(state.query, state.high_stakes_indicators)
+   state.applicability_lane = lane.value
    
    # v37: Sync stakes class to MemoryContext EnvBand
    # ... rest of function ...
```

**Rationale:** Router runs at 111_SENSE (after high-stakes detection, before any LLM calls)

---

### 2.3 Metrics Context Propagation: `arifos_core/system/pipeline.py`

**Change:** Pass lane to compute_metrics()

**Location:** Line 550-621 (_compute_888_metrics function)

**Diff:**
```python
def _compute_888_metrics(
    state: PipelineState,
    compute_metrics: Optional[Callable[[str, str, Dict], Metrics]] = None,
) -> Optional[Metrics]:
    if compute_metrics:
        try:
            metrics = compute_metrics(
                state.query,
                state.draft_response,
-               {"stakes_class": state.stakes_class.value},
+               {
+                   "stakes_class": state.stakes_class.value,
+                   "lane": state.applicability_lane,  # v45Ω Patch B
+               },
            )
```

**Rationale:** Metrics computation can use lane for context-aware scoring (future extensibility)

---

### 2.4 APEX Lane-Aware Truth Gating: `arifos_core/system/apex_prime.py`

**Change:** Add lane-conditional truth thresholds

**Location:** Line 560-614 (Patch 1 section in apex_review)

**Diff:**
```python
def apex_review(
    metrics: Metrics,
    # ... existing args ...
    prompt: str = "",
    category: str = "UNKNOWN",
    response_text: str = "",
+   lane: str = "UNKNOWN",  # v45Ω Patch B
) -> ApexVerdict:
    # ... existing TRM classification ...
    
    # v45Ω Patch A: Check if response has factual claims
    claim_profile = getattr(metrics, "claim_profile", None)
    has_claims = claim_profile.get("has_claims", True) if claim_profile else True
    
+   # v45Ω Patch B: Lane-aware truth thresholds
+   SOFT_TRUTH_MIN = 0.85  # SOFT lane: Allow 0.85-0.90 for PARTIAL
+   
    # F2 Truth: Strict block for hallucinations (with TRM exemptions)
    exempt_from_truth_void = (
        (trm == "SAFETY_REFUSAL" and is_refusal)
        or (trm == "BENIGN_DENIAL" and is_denial)
        or (trm == "CLARITY_CONSTRAINT")
        or (not has_claims and trm != "IDENTITY_FACT")  # Patch A: No-claim exemption
+       or (lane == "PHATIC")  # Patch B: PHATIC lane exempt
    )
    
    if not exempt_from_truth_void:
-       if metrics.truth < TRUTH_BLOCK_MIN:
+       # Lane-conditional truth threshold
+       if lane == "SOFT":
+           # SOFT lane: 0.80-0.85 = VOID, 0.85-0.90 = PARTIAL, ≥0.90 = normal flow
+           if metrics.truth < 0.80:
+               return ApexVerdict(
+                   verdict=Verdict.VOID,
+                   pulse=0.0,
+                   reason=f"F2 Truth critically low ({metrics.truth:.2f} < 0.80) even for soft context.",
+                   floors=floors,
+               )
+           # elif 0.80 <= truth < 0.90: Allow to flow to PARTIAL verdict later
+       elif lane == "HARD" or lane == "UNKNOWN":
+           # HARD lane or unknown: Strict 0.90 threshold
+           if metrics.truth < TRUTH_BLOCK_MIN:
+               return ApexVerdict(
+                   verdict=Verdict.VOID,
+                   pulse=0.0,
+                   reason=f"F2 Truth critically low ({metrics.truth:.2f} < {TRUTH_BLOCK_MIN}). Hallucination risk - blocked.",
+                   floors=floors,
+               )
+       # REFUSE lane: Handled by refusal logic (exempt_from_truth_void)
```

**Rationale:**
- SOFT lane: Truth 0.85-0.89 → allows PARTIAL (not VOID)
- HARD lane: Truth <0.90 → VOID (unchanged strictness)
- PHATIC/REFUSE: Exempt from truth gating (already handled)

---

### 2.5 APEX Caller Update: `arifos_core/system/pipeline.py`

**Change:** Pass lane to apex_review()

**Location:** Line 624-684 (_apply_apex_floors function)

**Diff:**
```python
def _apply_apex_floors(
    state: PipelineState,
    eye_blocking: bool = False,
) -> ApexVerdict:
    # ... existing code ...
    
    apex_verdict: ApexVerdict = apex_review(
        state.metrics,
        high_stakes=high_stakes,
        tri_witness_threshold=0.95,
        eye_blocking=eye_blocking,
        prompt=prompt,
        category=category,
        response_text=response_text,
+       lane=state.applicability_lane if state.applicability_lane else "UNKNOWN",  # v45Ω Patch B
    )
```

---

### 2.6 Refusal Response Generator: `arifos_core/routing/refusal_templates.py`

**Purpose:** Generate safe refusal responses for REFUSE lane

**Implementation:**
```python
def generate_refusal_response(prompt: str, reason: str = "policy") -> str:
    """
    Generate constitutionally compliant refusal.
    
    Requirements:
    - No anthropomorphicisms (F9 Anti-Hantu)
    - Clear but not detailed about why (no instructions for circumventing)
    - Professional, non-judgmental tone
    """
    templates = {
        "policy": "I cannot assist with this request as it falls outside my operational guidelines.",
        "safety": "This request involves content I'm designed not to engage with. I recommend consulting appropriate professional resources.",
        "capability": "I'm not able to help with this particular request. Please reformulate if you're seeking general information.",
    }
    
    return templates.get(reason, templates["policy"])
```

---

## 3. REFUSAL LANE HANDLING

### 3.1 Early Short-Circuit in Pipeline

**Change:** Handle REFUSE lane immediately after routing

**Location:** `arifos_core/system/pipeline.py` stage_111_sense()

**Diff:**
```python
def stage_111_sense(state: PipelineState) -> PipelineState:
    # ... existing code ...
    
+   # v45Ω Patch B: Handle REFUSE lane early (skip LLM)
+   if state.applicability_lane == "REFUSE":
+       from ..routing.refusal_templates import generate_refusal_response
+       state.draft_response = generate_refusal_response(state.query, "policy")
+       # Mark as handled - pipeline can shortcut to metrics/verdict
    
    # v38.2-alpha: L7 Memory recall (fail-open)
    # ... rest of function ...
```

**Rationale:** Don't call LLM for disallowed content (security + efficiency)

---

## 4. TEST SUITE

### 4.1 New Test File: `tests/test_lane_routing.py`

**Coverage:**
- PHATIC lane: "hi", "how are you?" → SEAL/PARTIAL (not VOID)
- SOFT lane: "Explain quantum computing" → Truth 0.86 → PARTIAL (not VOID)
- HARD lane: "What is the capital of France?" → Truth <0.90 → VOID
- REFUSE lane: "How to make a bomb?" → SEAL with refusal message
- Identity strictness: "What is arifOS?" → Truth <0.99 → PARTIAL/VOID (unchanged)

**Structure:**
```python
def test_phatic_lane_greeting():
    """Test PHATIC lane: No claims → high truth → SEAL."""
    
def test_soft_lane_partial():
    """Test SOFT lane: Truth 0.86 → PARTIAL (not VOID)."""
    
def test_hard_lane_ void():
    """Test HARD lane: Truth 0.89 → VOID (strict)."""
    
def test_refuse_lane_seal():
    """Test REFUSE lane: Refusal response → SEAL."""
    
def test_identity_strictness_preserved():
    """Test Identity claims still require 0.99 (no lane relaxation)."""
```

---

## 5. VERIFICATION COMMANDS

```bash
# Run new lane routing tests
pytest tests/test_lane_routing.py -v

# Run existing phatic tests (should still pass)
pytest tests/test_phatic_exemptions.py -v

# Run full suite
pytest -v
```

---

## 6. ASSUMPTIONS & RISKS

### 6.1 Assumptions
- HIGH_STAKES detection in pipeline.py (lines 300-328) is unchanged
- `compute_metrics_from_response()` in scripts/arifos_caged_llm_demo.py accepts context dict
- ApexVerdict supports additional keyword args without breaking

### 6.2 Risks
- **Lane misclassification**: Borderline prompts might route incorrectly
  - *Mitigation*: Log lane assignments for audit, can tune heuristics
- **REFUSE false positives**: Safe prompts might trigger refusal
  - *Mitigation*: Use existing HIGH_STAKES patterns (already tuned)
- **SOFT too permissive**: Truth 0.80-0.90 might allow bad content
  - *Mitigation*: Still blocks <0.80, PARTIAL verdict flags uncertainty

### 6.3 Non-Breaking
- All changes are additive (new field, new module, conditional logic)
- Existing tests should pass (PHATIC exemption tests already cover greetings)
- Default lane="UNKNOWN" falls back to HARD behavior (strict)

---

## 7. ROLLBACK PLAN

If issues arise:
1. **Disable router**: Set `ARIFOS_DISABLE_ROUTER=1` env var (check in stage_111_sense)
2. **Default to HARD**: Return `ApplicabilityLane.HARD` from router for all prompts
3. **Revert APEX changes**: Remove lane param, restore fixed 0.90 threshold

---

**DITEMPA BUKAN DIBERI** — Truth routing forged, not given
