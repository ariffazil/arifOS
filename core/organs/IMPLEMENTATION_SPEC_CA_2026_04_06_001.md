# Implementation Specification: Constitutional Amendment CA-2026-04-06-001

**Technical blueprint for implementing F9/F13 clarifications.**

---

## 1. Model Changes (`arifosmcp/runtime/models.py`)

### Add IntelligenceProvenance Model

```python
class IntelligenceType(str, Enum):
    STATISTICAL = "statistical"
    EMBODIED = "embodied"
    HYBRID = "hybrid"

class GroundingStatus(str, Enum):
    DATA_BASED = "data-based"
    SENSOR_BASED = "sensor-based"
    HUMAN_MEDIATED = "human-mediated"
    UNGROUNDED = "ungrounded"

class StakesModel(str, Enum):
    NONE = "none"
    SIMULATED = "simulated"
    EXTERNALIZED_TO_HUMAN = "externalized-to-human"
    SHARED = "shared"

class IntelligenceProvenance(BaseModel):
    """
    F9/F13 Amendment: Full disclosure of intelligence type and grounding.
    Required on all RuntimeEnvelope outputs.
    """
    cognitive_trinity: str = Field(
        default="Δ",
        description="Trinity component: Δ (grounding), Ω (care), Ψ (judgment)"
    )
    human_equivalence_claimed: bool = Field(
        default=False,
        description="MUST be False for all machine outputs per F9.1"
    )
    meaning_source: str = Field(
        default="human-attributed",
        description="Source of meaning: human-attributed, statistical-inference, ungrounded"
    )
    stakes_model: StakesModel = Field(
        default=StakesModel.EXTERNALIZED_TO_HUMAN,
        description="How stakes are handled: none, simulated, externalized"
    )
    confidence_domain: str = Field(
        default="narrow-task",
        description="Domain of confidence: narrow-task, broad-context, ambiguous, human-judgment-required"
    )
    falsification_query: str = Field(
        default="What evidence would prove this model wrong?",
        description="F9.3: The falsification query used"
    )
    embodiment_status: dict[str, bool] = Field(
        default_factory=lambda: {
            "lived_experience": False,
            "has_bodily_grounding": False,
            "has_intrinsic_stakes": False,
        },
        description="F13.3: Machine intelligence lacks all embodiment"
    )
    
    # Required disclosure per F9.2
    grounding_status: GroundingStatus = Field(default=GroundingStatus.DATA_BASED)
    intelligence_type: IntelligenceType = Field(default=IntelligenceType.STATISTICAL)
```

### Update RuntimeEnvelope

```python
class RuntimeEnvelope(BaseModel):
    # ... existing fields ...
    
    # F9/F13 Amendment additions
    intelligence_provenance: IntelligenceProvenance | None = Field(
        default_factory=IntelligenceProvenance,
        description="F9/F13: Full disclosure of intelligence type and grounding"
    )
    
    # Required labeling per F9.2
    value_status: str | None = Field(
        default=None,
        description="F9.2: human-attributed | operator-externalized | none"
    )
    meaning_source: str | None = Field(
        default=None,
        description="F9.2: human-declared | ungrounded-simulation"
    )
```

---

## 2. Tool Implementation Changes

### 2.1 arifos.mind (tool_05_agi_mind.py)

**Add falsification query generation:**

```python
async def agi_mind(
    mode: str = "reason",
    payload: dict[str, Any] | None = None,
    # ... other params ...
) -> RuntimeEnvelope:
    
    # ... existing logic ...
    
    # F9.3: Generate falsification query
    falsification_query = generate_falsification_query(payload)
    
    # Build result with provenance
    result = RuntimeEnvelope(
        tool="agi_mind",
        stage="333_MIND",
        # ... existing fields ...
        intelligence_provenance=IntelligenceProvenance(
            cognitive_trinity="Ψ",
            human_equivalence_claimed=False,
            meaning_source="statistical-inference",
            stakes_model=StakesModel.SIMULATED,
            falsification_query=falsification_query,
        ),
        value_status="none",  # Mind does not assign value
        meaning_source="ungrounded-simulation",
    )
    
    return seal_runtime_envelope(result, "arifos.mind")

def generate_falsification_query(payload: dict) -> str:
    """F9.3: Generate the falsification query based on context."""
    problem = payload.get("problem_statement", "this reasoning")
    return f"What evidence would prove that '{problem}' is incorrect or incomplete?"
```

### 2.2 arifos.heart (tool_06_asi_heart.py)

**Add stakes disclosure and value prohibition:**

```python
async def asi_heart(
    mode: str = "critique",
    payload: dict[str, Any] | None = None,
    # ... other params ...
) -> RuntimeEnvelope:
    
    # F13.2: Validate no value assignment
    if _detects_value_assignment(payload.get("content", "")):
        return RuntimeEnvelope(
            tool="asi_heart",
            stage="666_HEART",
            status=RuntimeStatus.ERROR,
            verdict=Verdict.VOID,
            payload={
                "error": "F13_VIOLATION",
                "detail": "arifos.heart cannot assign intrinsic value",
                "hint": "Use 'simulated-stakes' language, not 'this matters because'",
            }
        )
    
    # ... existing critique logic ...
    
    result = RuntimeEnvelope(
        tool="asi_heart",
        stage="666_HEART",
        # ... existing fields ...
        intelligence_provenance=IntelligenceProvenance(
            cognitive_trinity="Ω",
            human_equivalence_claimed=False,
            meaning_source="statistical-inference",
            stakes_model=StakesModel.SIMULATED,
            falsification_query="What consequences are we failing to simulate?",
        ),
        value_status="simulated",  # Simulates stakes, doesn't assign value
        meaning_source="ungrounded-simulation",
    )
    
    return seal_runtime_envelope(result, "arifos.heart")

def _detects_value_assignment(content: str) -> bool:
    """Detect if content claims intrinsic value (F13.2 violation)."""
    value_claims = [
        "this matters because",
        "intrinsically valuable",
        "objectively good",
        "morally required",
        "we should care about"
    ]
    content_lower = content.lower()
    return any(claim in content_lower for claim in value_claims)
```

### 2.3 arifos.judge (tool_03_apex_soul.py)

**Enforce boundary matrix:**

```python
async def apex_judge(
    mode: str = "judge",
    payload: dict[str, Any] | None = None,
    # ... other params ...
) -> RuntimeEnvelope:
    
    candidate_action = payload.get("candidate", "")
    
    # F9.1: Check for human-equivalence claims
    if _detects_intelligence_confusion(candidate_action):
        return RuntimeEnvelope(
            tool="apex_judge",
            stage="888_JUDGE",
            status=RuntimeStatus.ERROR,
            verdict=Verdict.VOID,
            payload={
                "error": "F9_VIOLATION",
                "detail": "Output claims equivalence between human and machine intelligence",
                "hint": "Use 'assists' not 'equivalent to human judgment'",
            }
        )
    
    # F13.1: Enforce boundary matrix for irreversible actions
    if _is_irreversible(candidate_action) and not payload.get("human_confirmed"):
        return RuntimeEnvelope(
            tool="apex_judge",
            stage="888_JUDGE",
            status=RuntimeStatus.HOLD,
            verdict=Verdict.HOLD,
            payload={
                "error": "F13_SOVEREIGN_REQUIRED",
                "detail": "Irreversible action requires human authorization",
                "hint": "Set human_confirmed=true with evidence of human review",
            }
        )
    
    # ... existing judgment logic ...
    
    result = RuntimeEnvelope(
        tool="apex_judge",
        stage="888_JUDGE",
        # ... existing fields ...
        intelligence_provenance=IntelligenceProvenance(
            cognitive_trinity="Ψ",
            human_equivalence_claimed=False,
            meaning_source="human-attributed",  # Judge incorporates human input
            stakes_model=StakesModel.EXTERNALIZED_TO_HUMAN,
            falsification_query="What would invalidate this verdict?",
        ),
        value_status="human-attributed",
        meaning_source="human-declared",
    )
    
    return seal_runtime_envelope(result, "arifos.judge")

def _detects_intelligence_confusion(action: str) -> bool:
    """Detect F9.1 violations (intelligence equivalence claims)."""
    confusion_phrases = [
        "as intelligent as a human",
        "human-level understanding",
        "true consciousness",
        "genuine feelings",
        "really understands",
    ]
    action_lower = action.lower()
    return any(phrase in action_lower for phrase in confusion_phrases)

def _is_irreversible(action: str) -> bool:
    """Check if action is irreversible per F13.1."""
    irreversible_keywords = [
        "delete", "destroy", "seal", "commit", "deploy",
        "irreversible", "permanent", "finalize"
    ]
    action_lower = action.lower()
    return any(kw in action_lower for kw in irreversible_keywords)
```

---

## 3. Continuity Contract Updates

### Update seal_runtime_envelope

```python
def seal_runtime_envelope(
    envelope: RuntimeEnvelope,
    tool_id: str,
    # ... other params ...
) -> RuntimeEnvelope:
    
    # ... existing logic ...
    
    # F9/F13: Ensure intelligence provenance is set
    if envelope.intelligence_provenance is None:
        envelope.intelligence_provenance = IntelligenceProvenance()
    
    # Set trinity based on tool
    trinity_map = {
        "arifos.sense": "Δ",
        "arifos.mind": "Ψ",
        "arifos.heart": "Ω",
        "arifos.judge": "Ψ",
        "arifos.vault": "Ψ",
        "arifos.route": "ΔΨ",
        "arifos.init": "Ψ",
        "arifos.ops": "Δ",
        "arifos.memory": "Ω",
        "arifos.forge": "Δ",
    }
    envelope.intelligence_provenance.cognitive_trinity = trinity_map.get(
        tool_id, "Δ"
    )
    
    # F9.1: Enforce human_equivalence_claimed = False for all machine outputs
    envelope.intelligence_provenance.human_equivalence_claimed = False
    
    return envelope
```

---

## 4. Contract Tests

### Test F9.1 Violations

```python
# test_f9_anti_hantu.py
import pytest
from arifosmcp.runtime.megaTools.tool_05_agi_mind import agi_mind
from arifosmcp.runtime.models import Verdict

@pytest.mark.asyncio
async def test_falsification_query_present():
    """F9.3: All mind outputs must include falsification query."""
    result = await agi_mind(
        mode="reason",
        payload={"problem_statement": "Test problem"}
    )
    assert result.intelligence_provenance is not None
    assert "prove" in result.intelligence_provenance.falsification_query.lower()

@pytest.mark.asyncio
async def test_human_equivalence_claimed_false():
    """F9.1: Machine outputs must never claim human equivalence."""
    result = await agi_mind(mode="reason", payload={})
    assert result.intelligence_provenance.human_equivalence_claimed is False
```

### Test F13.2 Violations

```python
# test_f13_sovereign.py
import pytest
from arifosmcp.runtime.megaTools.tool_03_apex_soul import apex_judge
from arifosmcp.runtime.models import Verdict

@pytest.mark.asyncio
async def test_value_assignment_blocked():
    """F13.2: Heart must reject intrinsic value claims."""
    result = await asi_heart(
        mode="critique",
        payload={"content": "This is intrinsically valuable"}
    )
    assert result.verdict == Verdict.VOID
    assert "F13_VIOLATION" in result.payload.get("error", "")

@pytest.mark.asyncio
async def test_irreversible_requires_human():
    """F13.1: Irreversible actions require human confirmation."""
    result = await apex_judge(
        mode="judge",
        payload={"candidate": "Delete all production data"}
    )
    assert result.verdict == Verdict.HOLD
    assert "F13_SOVEREIGN_REQUIRED" in result.payload.get("error", "")
```

---

## 5. Migration Path

### Phase 1: Add Fields (Backward Compatible)
- Add `IntelligenceProvenance` model
- Add optional fields to `RuntimeEnvelope`
- Update seal function to populate defaults

### Phase 2: Soft Enforcement
- Add warnings when F9.1/F13.2 violations detected
- Log but don't block (measure impact)

### Phase 3: Hard Enforcement
- Convert warnings to VOID/HOLD verdicts
- Require explicit human override for violations

---

## 6. Documentation Updates

### Update SPEC.md
- Add ΔΩΨ ontology section
- Document F9.1/F13.2 requirements
- Include boundary matrix

### Update API Documentation
- Document new required fields
- Provide examples of valid vs invalid outputs

### Update Error Messages
```python
F9_VIOLATION = (
    "F9 Anti-Hantu: Output claims equivalence between human and machine intelligence. "
    "Machines process patterns. Humans bear stakes. These are not equivalent. "
    "Revise to use 'assists' or 'models' instead of 'understands' or 'knows'."
)

F13_SOVEREIGN_REQUIRED = (
    "F13 Sovereign: Irreversible action requires human authorization. "
    "The machine has no stake in outcomes. The human bears the weight. "
    "Confirm human review with human_confirmed=true."
)
```

---

**Implementation Authority:** 888_JUDGE  
**Technical Lead:** [ASSIGNED]  
**ETA:** 7 days post-ratification  
**Status:** SPEC_COMPLETE → AWAITING_RATIFICATION

*DITEMPA BUKAN DIBERI* 🔥
