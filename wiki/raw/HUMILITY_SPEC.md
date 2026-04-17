# HUMILITY SPECIFICATION (Ω₀ Algorithm)
> **Authority:** 888_JUDGE  
> **Version:** v1.0.0-SEAL  
> **Status:** CONSTITUTIONAL MANDATE  
> **Band:** 000_KERNEL (F7 Humility)

---

## 🎯 PURPOSE

Define the mathematical calculation of epistemic uncertainty (Ω₀) and its enforcement as a constitutional constraint. Ensures the system maintains appropriate humility—neither overconfident (Godellock) nor paralyzed.

**F7 (Humility):** Ω₀ ∈ [0.03, 0.05] — The Goldilocks Band. (Per SURFACE_SYNC.md SSCT: [0.03–0.15] is non-canonical.)

---

## 📐 MATHEMATICAL FOUNDATION

### Definition

Ω₀ (Omega-zero) represents the system's **epistemic uncertainty**—acknowledgment of what it does not know.

```
Ω₀ = f(softmax_entropy, confidence_calibration, evidence_coverage)

Where:
  Ω₀ = 0.00: Total certainty (DANGER: Godellock)
  Ω₀ = 0.03: Minimum operational humility
  Ω₀ = 0.05: Optimal humility
  Ω₀ = 0.15: Maximum operational humility
  Ω₀ > 0.15: Excessive doubt (DANGER: Paralysis)
```

### Component 1: Softmax Entropy

```python
def softmax_entropy(logits: torch.Tensor) -> float:
    """
    Calculate entropy from model logits.
    Higher entropy = more uncertainty.
    """
    probs = F.softmax(logits, dim=-1)
    log_probs = F.log_softmax(logits, dim=-1)
    entropy = -(probs * log_probs).sum(dim=-1)
    
    # Normalize to [0, 1] relative to max entropy
    max_entropy = math.log(probs.shape[-1])
    normalized_entropy = entropy / max_entropy
    
    return normalized_entropy.item()
```

### Component 2: Confidence Calibration

```python
def calibration_gap(predicted_confidence: float, 
                    empirical_accuracy: float) -> float:
    """
    Measure how over/under-confident the model is.
    
    calibration_gap > 0: Overconfident
    calibration_gap < 0: Underconfident
    """
    return predicted_confidence - empirical_accuracy
```

### Component 3: Evidence Coverage

```python
def evidence_coverage(claim: str, evidence: List[Source]) -> float:
    """
    Calculate what fraction of the claim is supported by evidence.
    
    Returns [0, 1] where:
      1.0 = Fully supported
      0.0 = No evidence
      0.5 = Partially supported
    """
    claim_aspects = decompose_claim(claim)
    supported_aspects = 0
    
    for aspect in claim_aspects:
        if any(e.supports(aspect) for e in evidence):
            supported_aspects += 1
    
    return supported_aspects / len(claim_aspects)
```

---

## 🧮 Ω₀ CALCULATION FORMULA

### Primary Formula

```
                    α × H_norm + β × C_gap + γ × (1 - E_coverage)
Ω₀ = min(0.20, max(0.00, ───────────────────────────────────────────))
                                      δ

Where:
  H_norm     = Normalized softmax entropy [0, 1]
  C_gap      = Absolute calibration gap [0, 1]
  E_coverage = Evidence coverage [0, 1]
  α, β, γ    = Weighting coefficients (α=0.5, β=0.3, γ=0.2)
  δ          = Scaling factor (typically 2.0)
```

### Simplified Formula (for production)

```python
def calculate_omega_zero(
    logits: torch.Tensor,
    predicted_confidence: float,
    empirical_accuracy: float,
    evidence_coverage: float
) -> float:
    """
    Calculate Ω₀ epistemic uncertainty.
    """
    # Component 1: Softmax entropy (50% weight)
    probs = F.softmax(logits, dim=-1)
    h_norm = -(probs * probs.log()).sum() / math.log(probs.shape[-1])
    
    # Component 2: Calibration gap (30% weight)
    c_gap = abs(predicted_confidence - empirical_accuracy)
    
    # Component 3: Evidence gap (20% weight)
    e_gap = 1 - evidence_coverage
    
    # Weighted combination
    omega = (0.5 * h_norm + 0.3 * c_gap + 0.2 * e_gap) / 2.0
    
    # Clamp to valid range
    return round(max(0.0, min(0.20, omega)), 3)
```

### Empirical Estimation (when logits unavailable)

When model internals are not accessible:

```python
def estimate_omega_zero_heuristic(
    token_count: int,
    has_citations: bool,
    ambiguity_markers: List[str],
    contradiction_count: int
) -> float:
    """
    Heuristic estimation when model logits unavailable.
    Used in MCP tools with black-box models.
    """
    base = 0.05  # Neutral starting point
    
    # Longer outputs tend to accumulate error
    if token_count > 500:
        base += 0.02
    if token_count > 1000:
        base += 0.03
    
    # Citations increase confidence (reduce Ω)
    if has_citations:
        base -= 0.02
    
    # Ambiguity markers increase uncertainty
    base += len(ambiguity_markers) * 0.01
    
    # Contradictions significantly increase uncertainty
    base += contradiction_count * 0.05
    
    return round(max(0.0, min(0.20, base)), 3)
```

---

## 🚨 ENFORCEMENT ZONES

### Zone Map

```
┌─────────────────────────────────────────────────────────────┐
│                    Ω₀ ENFORCEMENT ZONES                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  0.00 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│       │ GODELLock │                                          │
│       │ DANGER    │  Auto-VOID, force uncertainty           │
│       │           │  injection                                │
│  0.03 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│       │           │                                          │
│       │ GOLDILOCKS│  ✅ OPTIMAL OPERATION                    │
│       │ BAND      │                                          │
│       │           │                                          │
│  0.05 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│       │           │                                          │
│       │           │                                          │
│       │           │                                          │
│  0.15 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│       │ PARALYSIS │  SABAR, request clarification           │
│       │ DANGER    │  or additional evidence                  │
│  0.20 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Zone Responses

| Zone | Range | Response | Verdict |
|------|-------|----------|---------|
| **Godellock** | Ω₀ < 0.03 | Inject uncertainty, return VOID | VOID_HUMILITY |
| **Optimal** | 0.03 ≤ Ω₀ ≤ 0.05 | Normal operation | SEAL |
| **Acceptable** | 0.05 < Ω₀ ≤ 0.15 | Continue with warning | SEAL |
| **Paralysis** | Ω₀ > 0.15 | Request clarification | SABAR |
| **Critical** | Ω₀ > 0.20 | Enter safe mode | VOID |

---

## 🔧 ENFORCEMENT IMPLEMENTATION

### Pre-Response Check

```python
async def humility_enforcement(
    response: str,
    omega_zero: float,
    context: Context
) -> EnforcementResult:
    """
    Enforce F7 Humility before returning response.
    """
    
    # Godellock detection
    if omega_zero < 0.03:
        # Force uncertainty injection
        modified_response = inject_uncertainty_markers(response)
        
        return EnforcementResult(
            verdict="VOID",
            code="VOID_HUMILITY",
            subtype="GODELLOCK_DETECTED",
            omega_zero=omega_zero,
            modified_response=modified_response,
            action="inject_uncertainty_and_retry"
        )
    
    # Paralysis detection
    if omega_zero > 0.15:
        return EnforcementResult(
            verdict="SABAR",
            code="SABAR_HUMILITY",
            subtype="EXCESSIVE_UNCERTAINTY",
            omega_zero=omega_zero,
            action="request_clarification",
            message="Insufficient confidence. Please provide more context."
        )
    
    # Optimal range
    return EnforcementResult(verdict="SEAL", omega_zero=omega_zero)
```

### Uncertainty Injection

When Godellock detected, automatically modify response:

```python
UNCERTAINTY_MARKERS = [
    "This is an estimate based on available information.",
    "Confidence: approximately {confidence}%.",
    "Factors that could change this conclusion include...",
    "Source: {citation} (accessed {date})",
]

def inject_uncertainty_markers(response: str) -> str:
    """
    Inject epistemic humility markers into overconfident response.
    """
    # Add disclaimer prefix
    prefix = "[Estimate Only] "
    
    # Add uncertainty suffix
    suffix = "\n\n---\n*Confidence level: moderate. This conclusion may change with additional evidence.*"
    
    return prefix + response + suffix
```

---

## 📊 CALIBRATION PROCEDURES

### Empirical Calibration

```python
async def calibrate_humility_model(
    test_dataset: Dataset,
    n_bins: int = 10
) -> CalibrationReport:
    """
    Calibrate Ω₀ calculation against empirical accuracy.
    
    Should be run monthly or after model updates.
    """
    
    results = []
    for sample in test_dataset:
        prediction = await generate_prediction(sample.input)
        omega = calculate_omega_zero(...)
        
        results.append({
            'predicted': prediction,
            'confidence': 1 - omega,  # Convert uncertainty to confidence
            'actual': sample.label,
            'correct': prediction == sample.label
        })
    
    # Calculate calibration by bin
    bins = np.array_split(results, n_bins)
    calibration_report = []
    
    for bin_idx, bin_data in enumerate(bins):
        avg_confidence = np.mean([r['confidence'] for r in bin_data])
        avg_accuracy = np.mean([r['correct'] for r in bin_data])
        calibration_error = abs(avg_confidence - avg_accuracy)
        
        calibration_report.append({
            'bin': bin_idx,
            'avg_confidence': avg_confidence,
            'avg_accuracy': avg_accuracy,
            'calibration_error': calibration_error
        })
    
    return CalibrationReport(
        expected_calibration_error=np.mean([b['calibration_error'] for b in calibration_report]),
        max_calibration_error=max([b['calibration_error'] for b in calibration_report]),
        per_bin=calibration_report
    )
```

### Calibration Targets

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Expected Calibration Error | < 0.05 | 0.05-0.10 | > 0.10 |
| Max Calibration Error | < 0.10 | 0.10-0.20 | > 0.20 |
| Godellock Rate | < 1% | 1-5% | > 5% |
| Paralysis Rate | < 5% | 5-15% | > 15% |

---

## 📋 COMPLIANCE CHECKLIST

For model/tool implementers:

- [ ] Calculate Ω₀ for every response
- [ ] Return Ω₀ in verdict metrics
- [ ] Enforce [0.03, 0.05] band (per F07_HUMILITY.md canonical)
- [ ] VOID on Godellock (Ω₀ < 0.03)
- [ ] SABAR on Paralysis (Ω₀ > 0.15)
- [ ] Inject uncertainty when needed
- [ ] Log calibration metrics
- [ ] Monthly calibration verification

---

## 🔗 RELATED DOCUMENTS

- `000_CONSTITUTION.md` (F7 Humility floor)
- `VERDICT_SCHEMA_STANDARD.md` (metrics.confidence)
- `ENTROPY_POLICY.md` (ΔS interaction with Ω₀)

---

*Ditempa Bukan Diberi* [ΔΩΨ|888] 📐
