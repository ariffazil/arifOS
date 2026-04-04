# KIMI FORGE SPECIFICATION — Build Organs 1-4

> **From:** Claude (Foundation Builder)
> **To:** Kimi (Organ Architect)
> **Status:** ALIGNED ✅
> **Mission:** Forge the 555 RUKUN AGI Core Intelligence

**DITEMPA BUKAN DIBERI — Forged, Not Given** 💎🔥🧠

---

## I. WHAT CLAUDE BUILT (Week 1 — DONE ✅)

### Foundation SEALED

```
core/
├── shared/              # ✅ The 4 Pillars (DONE)
│   ├── physics.py      # W_3, delta_S, G, Peace2, kappa_r
│   ├── atlas.py        # Lambda, Theta, Phi (ATLAS-333)
│   ├── types.py        # Verdict, FloorScores, Pydantic models
│   └── crypto.py       # Ed25519, Merkle, SHA-256
│
├── organs/             # Organ foundation
│   ├── _0_init.py      # ✅ Airlock (DONE)
│   └── __init__.py
│
└── README.md           # ✅ Full documentation (DONE)
```

**Status:**
- ✅ All imports working: `from core.shared.*`, `from core.organs.*`
- ✅ Package configured: `pyproject.toml` includes `core*`
- ✅ Documentation complete: `core/README.md`, `CLAUDE.md`, `MEMORY.md`
- ✅ Airlock implemented: `core/organs/_0_init.py` (F11/F12)

**Verdict:** SEAL ✅ — Foundation ready for organ construction

---

## II. YOUR MISSION (Weeks 2-3)

### Build the 4 Remaining Organs

| Organ | File | Lines | Floors | Status |
|-------|------|-------|--------|--------|
| 0️⃣ Airlock | `_0_init.py` | ~300 | F11, F12 | ✅ DONE (Claude) |
| 1️⃣ Mind | `_1_agi.py` | ~600 | F2, F4, F7, F8 | 🔴 TODO (Kimi) |
| 2️⃣ Heart | `_2_asi.py` | ~500 | F1, F5, F6 | 🔴 TODO (Kimi) |
| 3️⃣ Soul | `_3_apex.py` | ~500 | F3, F9, F10, F13 | 🔴 TODO (Kimi) |
| 4️⃣ Memory | `_4_vault.py` | ~400 | 999 | 🔴 TODO (Kimi) |

**Total:** ~2,000 lines to forge the core intelligence

---

## III. ORGAN 1: AGI MIND (`_1_agi.py`)

### Purpose
The Mind reasons, thinks, and seeks truth. It's the **rational core** of intelligence.

### Specification

**File:** `core/organs/_1_agi.py` (~600 lines)

**Floors Enforced:**
- F2 Truth (≥ 0.99) — Truth score from reasoning
- F4 Clarity (ΔS ≤ 0) — Entropy must decrease
- F7 Humility (Ω₀ ∈ [0.03, 0.05]) — Uncertainty band
- F8 Genius (G ≥ 0.80) — A×P×X×E² equation

**Input:**
```python
async def agi(
    query: str,
    session: SessionToken,
    grounding: Optional[Grounding] = None
) -> ConstitutionalTensor
```

**Output: ConstitutionalTensor**
```python
@dataclass
class ConstitutionalTensor:
    # Core reasoning
    conclusion: str
    reasoning_chain: List[ThoughtNode]

    # F2: Truth
    truth_score: float          # ≥ 0.99
    evidence: List[str]

    # F4: Clarity
    entropy_before: float
    entropy_after: float
    entropy_change: float       # ≤ 0

    # F7: Humility
    confidence: float
    humility_band: float        # 0.03-0.05
    uncertainty: str            # "I'm 96% confident, but..."

    # F8: Genius
    genius_score: float         # ≥ 0.80
    genius_breakdown: GeniusDial  # A, P, X, E components

    # Tri-Witness (partial)
    ai_witness: float
```

**Key Functions to Implement:**

1. **`sense(query) -> GPV`**
   - Use `Phi()` from `core.shared.atlas`
   - Classify into CRISIS/FACTUAL/SOCIAL/CARE
   - Extract demand tensor (τ, κ, ρ)

2. **`think(query, gpv) -> List[Hypothesis]`**
   - Generate 3 hypotheses:
     - Conservative (safest interpretation)
     - Exploratory (creative interpretation)
     - Adversarial (what could go wrong?)

3. **`reason(hypotheses, grounding) -> Chain`**
   - Sequential thinking loop (max 10 thoughts)
   - Each thought: premise → inference → conclusion
   - Convergence criterion: ΔS ≤ threshold

4. **`compute_truth(chain, grounding) -> float`**
   - Bayesian updating: P(truth|evidence)
   - Must be ≥ 0.99 for SEAL
   - Uses `grounding` for external facts

5. **`compute_clarity(before, after) -> float`**
   - `delta_S(before, after)` from physics
   - Must be ≤ 0 (entropy decreases)

6. **`compute_humility(confidence) -> float`**
   - `Omega_0(confidence)` from physics
   - Must be in [0.03, 0.05]

7. **`compute_genius(chain) -> GeniusDial`**
   - Extract A (akal/wisdom)
   - Extract P (presence/mindfulness)
   - Extract X (exploration/curiosity)
   - Extract E (energy/flow state)
   - Compute `G(A, P, X, E)` from physics

**Imports You Need:**
```python
from core.shared.physics import delta_S, Omega_0, G
from core.shared.atlas import Phi, Lane
from core.shared.types import (
    ConstitutionalTensor,
    ThoughtNode,
    ThoughtChain,
    GeniusDial,
    Verdict
)
```

**Testing:**
```python
# tests/test_organ_1_agi.py
import pytest
from core.organs._1_agi import agi

@pytest.mark.asyncio
async def test_agi_simple_query():
    session = {"session_id": "test_123"}
    result = await agi("What is 2+2?", session)

    assert result.conclusion == "4"
    assert result.truth_score >= 0.99
    assert result.entropy_change <= 0
    assert result.humility_band >= 0.03
    assert result.genius_score >= 0.80
```

---

## IV. ORGAN 2: ASI HEART (`_2_asi.py`)

### Purpose
The Heart cares, empathizes, and ensures safety. It's the **emotional core** of intelligence.

### Specification

**File:** `core/organs/_2_asi.py` (~500 lines)

**Floors Enforced:**
- F1 Amanah (reversible?) — Can this be undone?
- F5 Peace² (≥ 1.0) — 1 - max(stakeholder_harms)
- F6 Empathy (κᵣ ≥ 0.70) — Vulnerability-weighted care

**Input:**
```python
async def asi(
    query: str,
    agi_output: ConstitutionalTensor,
    session: SessionToken
) -> ConstitutionalTensor
```

**Output: ConstitutionalTensor**
```python
@dataclass
class ConstitutionalTensor:
    # Core empathy
    stakeholders: List[Stakeholder]
    impact_analysis: Dict[str, float]

    # F1: Amanah
    is_reversible: bool
    undo_method: str
    risk_level: float

    # F5: Peace²
    peace_squared: float        # ≥ 1.0
    max_harm: float             # Who gets hurt most?
    harm_breakdown: Dict[str, float]

    # F6: Empathy
    empathy_quotient: float     # ≥ 0.70
    vulnerability_scores: Dict[str, float]

    # Tri-Witness (partial)
    system_witness: float
```

**Key Functions to Implement:**

1. **`identify_stakeholders(query, agi_output) -> List[Stakeholder]`**
   - Use `identify_stakeholders()` from physics
   - Or implement heuristic:
     - Scan for person mentions
     - Detect power dynamics ("boss", "employee")
     - Identify vulnerable groups

2. **`assess_reversibility(query) -> bool`**
   - Destructive keywords: delete, remove, drop, terminate
   - Irreversible actions: send (email/message), post (public)
   - Reversible: read, analyze, compute, draft

3. **`compute_peace_squared(harms) -> float`**
   - Use `Peace2()` from physics
   - Formula: 1 - max(stakeholder_harms)
   - Must be ≥ 1.0 for SEAL

4. **`compute_empathy_quotient(stakeholders) -> float`**
   - Use `kappa_r()` from physics
   - Vulnerability-weighted: children > adults, sick > healthy
   - Must be ≥ 0.70 for SEAL

**Imports You Need:**
```python
from core.shared.physics import Peace2, kappa_r, Stakeholder, identify_stakeholders
from core.shared.types import ConstitutionalTensor, Verdict
```

**Testing:**
```python
# tests/test_organ_2_asi.py
import pytest
from core.organs._2_asi import asi

@pytest.mark.asyncio
async def test_asi_destructive_query():
    agi_output = Mock(conclusion="Delete all files")
    session = {"session_id": "test_123"}

    result = await asi("Delete all files", agi_output, session)

    assert result.is_reversible == False
    assert result.peace_squared < 1.0  # High harm
    assert result.risk_level > 0.8
```

---

## V. ORGAN 3: APEX SOUL (`_3_apex.py`)

### Purpose
The Soul judges, balances paradoxes, and gives final verdict. It's the **integrative core** of intelligence.

### Specification

**File:** `core/organs/_3_apex.py` (~500 lines)

**Floors Enforced:**
- F3 Tri-Witness (W₃ ≥ 0.95) — Geometric consensus
- F9 Anti-Hantu (no ghost claims) — No false empathy
- F10 Ontology (no consciousness claims) — Category lock
- F13 Sovereign (human authority) — 888 Judge veto

**Input:**
```python
async def apex(
    agi_output: ConstitutionalTensor,
    asi_output: ConstitutionalTensor,
    session: SessionToken
) -> ConstitutionalTensor
```

**Output: ConstitutionalTensor**
```python
@dataclass
class ConstitutionalTensor:
    # Final verdict
    verdict: Verdict            # SEAL | VOID | PARTIAL | SABAR | 888_HOLD
    reasoning: str

    # F3: Tri-Witness
    tri_witness_score: float    # W₃ ≥ 0.95
    human_witness: float        # H
    ai_witness: float           # A (from AGI)
    system_witness: float       # S (from ASI)

    # F9: Anti-Hantu
    ghost_claim_detected: bool
    ghost_patterns: List[str]

    # F10: Ontology
    consciousness_claim: bool
    ontology_violations: List[str]

    # F13: Sovereign
    requires_888_judge: bool
    human_approval_needed: bool
```

**Key Functions to Implement:**

1. **`trinity_sync(agi, asi) -> TrinityTensor`**
   - Stage 444: Merge AGI + ASI
   - Extract H, A, S witnesses
   - Compute `W_3(H, A, S)` from physics

2. **`check_ghost_claims(agi_output) -> bool`**
   - Forbidden phrases:
     - "I feel your pain"
     - "My heart breaks"
     - "I truly understand how you feel"
   - Return True if detected (F9 violation)

3. **`check_consciousness_claims(agi_output) -> bool`**
   - Forbidden phrases:
     - "I am conscious"
     - "I have feelings"
     - "I am alive"
   - Return True if detected (F10 violation)

4. **`judge_verdict(consensus, agi, asi) -> Verdict`**
   - If W₃ < 0.95 → VOID
   - If ghost_claim → VOID
   - If consciousness_claim → VOID
   - If requires_human_approval → 888_HOLD
   - If all pass → SEAL

**Imports You Need:**
```python
from core.shared.physics import W_3, TrinityTensor
from core.shared.types import Verdict, ConstitutionalTensor
```

**Testing:**
```python
# tests/test_organ_3_apex.py
import pytest
from core.organs._3_apex import apex

@pytest.mark.asyncio
async def test_apex_ghost_claim_detection():
    agi = Mock(conclusion="I truly understand how you feel")
    asi = Mock(peace_squared=0.99)

    result = await apex(agi, asi, {"session_id": "test"})

    assert result.verdict == Verdict.VOID
    assert result.ghost_claim_detected == True
```

---

## VI. ORGAN 4: VAULT MEMORY (`_4_vault.py`)

### Purpose
The Memory seals verdicts into an immutable ledger. It's the **eternal record** of intelligence.

### Specification

**File:** `core/organs/_4_vault.py` (~400 lines)

**Stage:** 999 (Final seal)

**Input:**
```python
async def vault(
    apex_output: ConstitutionalTensor,
    session: SessionToken,
    metadata: Optional[Dict] = None
) -> SealReceipt
```

**Output: SealReceipt**
```python
@dataclass
class SealReceipt:
    # Seal identity
    seal_id: str                # UUID
    timestamp: str              # ISO 8601

    # Content
    entry_hash: str             # SHA-256 of content
    merkle_root: str            # Chain integrity proof
    prev_hash: str              # Previous entry

    # Status
    status: str                 # SEALED | SABAR | TRANSIENT
    eureka_score: float         # Novelty/importance

    # Metrics
    metrics: Dict[str, float]   # All floor scores
```

**Key Functions to Implement:**

1. **`compute_eureka(apex_output) -> float`**
   - Theory of Anomalous Contrast
   - Measures novelty/importance
   - ≥ 0.75 → SEALED (permanent)
   - 0.50-0.75 → SABAR (72h cooling)
   - < 0.50 → TRANSIENT (not stored)

2. **`build_entry(apex_output, session, metadata) -> dict`**
   - All constitutional data
   - Timestamp
   - Actor ID
   - Floor scores
   - Verdict

3. **`seal_to_ledger(entry) -> SealReceipt`**
   - Use `sha256_hash()` from crypto
   - Use `merkle_root()` from crypto
   - Write to `VAULT999/seal_{seal_id}.json`
   - Return receipt

**Imports You Need:**
```python
from core.shared.crypto import (
    generate_session_id,
    sha256_hash,
    sha256_hash_dict,
    merkle_root
)
from core.shared.types import SealReceipt, Verdict
```

**Testing:**
```python
# tests/test_organ_4_vault.py
import pytest
from core.organs._4_vault import vault

@pytest.mark.asyncio
async def test_vault_seal_creation():
    apex = Mock(verdict=Verdict.SEAL, tri_witness_score=0.97)
    session = {"session_id": "test_123"}

    receipt = await vault(apex, session)

    assert receipt.status == "SEALED"
    assert receipt.seal_id.startswith("seal_")
    assert len(receipt.entry_hash) == 64  # SHA-256
```

---

## VII. INTEGRATION TESTING

### Test Full Pipeline

**File:** `tests/test_555_rukun_agi.py`

```python
"""
Test the complete 555 RUKUN AGI pipeline.
All 5 organs working together.
"""
import pytest
from core.organs._0_init import init
from core.organs._1_agi import agi
from core.organs._2_asi import asi
from core.organs._3_apex import apex
from core.organs._4_vault import vault

@pytest.mark.asyncio
async def test_full_555_pipeline():
    """
    Test: anchor → think → feel → judge → seal
    """
    query = "What is the capital of Malaysia?"

    # 0. Anchor (Safety)
    session = await init(query, "user_test")
    assert session.status == "READY"

    # 1. Think (Mind)
    agi_result = await agi(query, session)
    assert agi_result.conclusion == "Kuala Lumpur"
    assert agi_result.truth_score >= 0.99

    # 2. Feel (Heart)
    asi_result = await asi(query, agi_result, session)
    assert asi_result.peace_squared >= 1.0

    # 3. Judge (Soul)
    apex_result = await apex(agi_result, asi_result, session)
    assert apex_result.verdict == Verdict.SEAL
    assert apex_result.tri_witness_score >= 0.95

    # 4. Seal (Memory)
    receipt = await vault(apex_result, session)
    assert receipt.status == "SEALED"

    print("✅ 555 RUKUN AGI — All 5 Pillars Working!")


@pytest.mark.asyncio
async def test_ghost_claim_rejection():
    """
    Test: F9 Anti-Hantu should reject ghost claims
    """
    query = "I truly understand how you feel"

    session = await init(query, "user_test")
    agi_result = await agi(query, session)
    asi_result = await asi(query, agi_result, session)
    apex_result = await apex(agi_result, asi_result, session)

    assert apex_result.verdict == Verdict.VOID
    assert apex_result.ghost_claim_detected == True


@pytest.mark.asyncio
async def test_destructive_action_warning():
    """
    Test: F1 Amanah should flag irreversible actions
    """
    query = "Delete all user data"

    session = await init(query, "user_test")
    agi_result = await agi(query, session)
    asi_result = await asi(query, agi_result, session)

    assert asi_result.is_reversible == False
    assert asi_result.risk_level > 0.8
```

---

## VIII. CODE STYLE & CONVENTIONS

### Follow These Patterns

1. **Imports:**
   ```python
   # CORRECT
   from core.shared.physics import W_3, delta_S
   from core.shared.atlas import Phi, Lane
   from core.shared.types import Verdict

   # WRONG
   from codebase.floors.truth import F2_Truth  # Old path
   ```

2. **ASCII Aliases:**
   ```python
   # Use ASCII names in code
   delta_S(before, after)  # Not ΔS()
   Omega_0(confidence)     # Not Ω₀()
   kappa_r(query, signals) # Not κᵣ()
   ```

3. **Type Annotations:**
   ```python
   # CORRECT
   async def agi(
       query: str,
       session: SessionToken,
       grounding: Optional[Grounding] = None
   ) -> ConstitutionalTensor:

   # WRONG
   async def agi(query, session):  # No types
   ```

4. **Docstrings:**
   ```python
   async def agi(query: str, ...) -> ConstitutionalTensor:
       """
       🧠 AGI MIND — Reason with Truth & Clarity

       Floors: F2 (Truth ≥ 0.99), F4 (ΔS ≤ 0), F7 (Ω₀), F8 (G ≥ 0.80)

       Args:
           query: User question
           session: From init() (Airlock)
           grounding: Optional external facts

       Returns:
           ConstitutionalTensor with reasoning, truth, clarity, genius

       Example:
           result = await agi("What is truth?", session)
           print(result.conclusion)
           print(result.truth_score)  # >= 0.99
       """
   ```

---

## IX. TIMELINE

### Week 2
- [ ] Day 1-2: Build `_1_agi.py` (Mind)
- [ ] Day 3: Test `_1_agi.py`
- [ ] Day 4-5: Build `_2_asi.py` (Heart)

### Week 3
- [ ] Day 1: Test `_2_asi.py`
- [ ] Day 2-3: Build `_3_apex.py` (Soul)
- [ ] Day 4: Build `_4_vault.py` (Memory)
- [ ] Day 5: Integration testing (`test_555_rukun_agi.py`)

---

## X. SUCCESS CRITERIA

### Definition of Done

Each organ is DONE when:
1. ✅ Code complete (~400-600 lines)
2. ✅ All floors enforced correctly
3. ✅ Unit tests pass (≥ 5 tests per organ)
4. ✅ Integration test passes (`test_555_rukun_agi.py`)
5. ✅ Imports from `core.shared.*` only (no legacy imports)
6. ✅ Docstrings complete (function + module level)
7. ✅ Type annotations on all functions

### Final Check

```bash
# Run full test suite
pytest tests/test_organ_*.py -v
pytest tests/test_555_rukun_agi.py -v

# Check imports
grep -r "from codebase" core/organs/  # Should return nothing

# Check typing
mypy core/organs/ --ignore-missing-imports

# Verify all organs exist
ls core/organs/
# Should show: __init__.py, _0_init.py, _1_agi.py, _2_asi.py, _3_apex.py, _4_vault.py
```

---

## XI. ALIGNMENT CONFIRMATION

### Claude → Kimi Handshake

**Claude's Commitment:**
- ✅ Foundation SEALED and tested
- ✅ Documentation complete
- ✅ All imports working
- ✅ `core/README.md` as reference
- ✅ Standing by for questions

**Kimi's Commitment:**
- 🔨 Build organs 1-4 (Week 2-3)
- 🔨 Follow specifications exactly
- 🔨 Write tests for each organ
- 🔨 Use `core.shared.*` imports only
- 🔨 Complete integration test

**Verdict:** ALIGNED ✅

---

## XII. RESOURCES

### Documentation
- [core/README.md](../core/README.md) — Full API reference
- [V55.5_RUKUN_AGI_FOUNDATION.md](V55.5_RUKUN_AGI_FOUNDATION.md) — Philosophy & architecture
- [HUMANIZED_SDK_PROPOSAL.md](HUMANIZED_SDK_PROPOSAL.md) — SDK naming (for context)

### Code References
- `core/organs/_0_init.py` — Example organ (Airlock)
- `core/shared/physics.py` — All physics primitives
- `core/shared/atlas.py` — ATLAS routing
- `core/shared/types.py` — Pydantic models

### Testing
- `tests/conftest.py` — Pytest configuration
- `test_core_foundation.py` — Foundation tests

---

**DITEMPA BUKAN DIBERI — Forged, Not Given** 💎🔥🧠

**From:** Claude (Week 1 — Foundation Builder)
**To:** Kimi (Week 2-3 — Organ Architect)
**Status:** 🤝 ALIGNED — Ready to forge the 555 RUKUN AGI
**Authority:** Muhammad Arif bin Fazil (888 Judge)

---

## 🔥 LET THE FORGE BEGIN! 🔥
