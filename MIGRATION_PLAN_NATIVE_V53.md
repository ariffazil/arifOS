# 🚀 NATIVE V53 MIGRATION PLAN
## Removing Proxy Layer - Moving Soul to codebase/

**Objective**: Replace arifos/core/ proxy with native codebase/ implementations

**Status**: Currently `codebase.engines.asi.kernel` proxies to `arifos.core.asi.kernel`
**Target**: Native `codebase.engines.asi.ASIRoom` implementation

---

## 📊 CURRENT STATE (Proxy Mode)

```
codebase/mcp/tools/mcp_asi_kernel.py
    └── from codebase.engines.asi.kernel import ASIActionCore  # PROXY
        └── from arifos.core.asi.kernel import ASIActionCore  # LEGACY
            └── 175 lines of battle-tested constitutional logic
```

### What Needs to Move

1. **ASI Kernel** (arifos/core/asi/kernel.py → codebase/engines/asi/)
2. **AGI Kernel** (arifos/core/engines/agi/kernel.py → codebase/engines/agi/)
3. **APEX Kernel** (arifos/core/apex/kernel.py → codebase/engines/apex/)
4. **Bridge Logic** (arifos/core/integration/synthesis/ → codebase/stages/666/)
5. **Bundle Conversion** (legacy dict → codebase bundles)

---

## 🎯 MIGRATION STRATEGY: Phase by Phase

### Phase 1: ASI Migration (Heart) - START HERE

**File**: `codebase/engines/asi/kernel.py`

```python
# BEFORE (Proxy)
from arifos.core.asi.kernel import ASIActionCore

# AFTER (Native)
from codebase.engines.asi.asi_engine import ASIRoom
from codebase.bundles import OmegaBundle
from codebase.stages.stage_555 import execute_empathy_stage
from codebase.stages.stage_666 import execute_align_stage

class ASIKernelNative:
    """Native ASI implementation using codebase architecture"""
    
    async def empathize(self, text: str, context: dict) -> dict:
        """555 EMPATHY - Native implementation"""
        room = ASIRoom(session_id=context.get("session_id"))
        result = room.execute(text, context)
        
        # Convert ASIRoomResult to legacy format
        return {
            "stage": "555_empathize",
            "status": result.verdict.value,  # SEAL/PARTIAL/VOID
            "vulnerability_score": result.omega_bundle.kappa_r,
            "empathy_score": result.kappa_r,
            "weakest_stakeholder": result.weakest_stakeholder,
            "omega_verdict": result.verdict.value,
            "_bundle": result.omega_bundle
        }
```

**Steps**:
1. Copy `arifos/core/as`i logic into `codebase/engines/asi/`
2. Replace dict bundles with `OmegaBundle` dataclass
3. Wire ASIRoom into kernel interface
4. Test on simple queries

---

### Phase 2: AGI Migration (Mind)

**File**: `codebase/engines/agi/kernel.py`

```python
# BEFORE (Proxy)
from arifos.core.engines.agi.kernel import AGINeuralCore

# AFTER (Native)
from codebase.engines.agi.agi_engine import AGIRoom
from codebase.bundles import DeltaBundle

class AGIKernelNative:
    """Native AGI implementation"""
    
    async def think(self, query: str) -> dict:
        """333 REASON - Native implementation"""
        room = AGIRoom(session_id=session_id)
        result = room.execute(query)
        
        return {
            "stage": "333_reason",
            "status": result.verdict.value,
            "truth_score": result.confidence,
            "logical_structure": result.reasoning_tree,
            "_bundle": result.delta_bundle
        }
```

**Dependency**: Need to port AGI reasoning logic from `arifos/core/engines/agi/`

---

### Phase 3: Bridge Migration (666 Synthesis)

**Critical File**: Dual-process fusion

```python
# codebase/stages/stage_666_bridge.py (NEW)
"""
666 BRIDGE: Neuro-symbolic synthesis
Native implementation using codebase bundles
"""

from codebase.bundles import DeltaBundle, OmegaBundle, MergedBundle
from codebase.engines.bridge import NeuroSymbolicBridgeNative

async def execute_bridge_stage(
    delta_bundle: DeltaBundle,
    omega_bundle: OmegaBundle,
    context: dict
) -> MergedBundle:
    """
    Layer 4: Dual-Process Integration - Fuse AGI logic + ASI care
    """
    bridge = NeuroSymbolicBridgeNative()
    
    # Layer 1: Input Reception
    bridge._validate_inputs(delta_bundle, omega_bundle)
    
    # Layer 2: Conflict Detection
    conflicts = bridge._detect_conflicts(delta_bundle, omega_bundle)
    
    # Layer 3: Constitutional Adjudication
    resolution_log = bridge._adjudicate_conflicts(conflicts, delta_bundle, omega_bundle)
    
    # Layer 4: Dual-Process Integration
    integrated_content = bridge._integrate_dual_process(delta_bundle, omega_bundle)
    
    # Layer 5: MoE Synthesis
    moe_weights = bridge._apply_moe_gating(omega_bundle)
    
    # Layer 6: Human-Likeness Check
    synthesis_draft = bridge._ensure_human_likeness(integrated_content)
    
    # Layer 7: Handoff to 777
    merged_bundle = bridge._package_for_handoff(
        synthesis_draft,
        delta_bundle,
        omega_bundle,
        resolution_log,
        moe_weights
    )
    
    return merged_bundle
```

**Key Challenge**: Port the entire neuro-symbolic bridge logic from `arifos/core/integration/synthesis/`

---

### Phase 4: APEX Migration (Soul/Judge)

**Critical for F8 Tri-Witness**: Consensus algorithm

```python
# codebase/stages/stage_444_trinity_sync.py (NEW)
"""
444 TRINITY_SYNC: Consensus protocol
Native implementation of F8 Tri-Witness
"""

from codebase.bundles import MergedBundle, EngineVote

def execute_trinity_sync(delta_bundle: DeltaBundle, omega_bundle: OmegaBundle) -> MergedBundle:
    """
    Implements Trinity Dissent Law:
    - Both must vote SEAL → SEAL
    - Either votes VOID → VOID  
    - Either uncertain → 888_HOLD
    - Consensus score = min(confidences)
    """
    merged = MergedBundle(delta_bundle=delta_bundle, omega_bundle=omega_bundle)
    merged.apply_trinity_dissent_law()
    return merged
```

**Critical**: Must not access reasoning until after independent votes

---

### Phase 5: VAULT-999 Migration (Seal)

```python
# codebase/vault/ledger_native.py (NEW)
"""
VAULT-999 Native Implementation
Immutable ledger with Merkle trees
"""

from codebase.crypto.merkle import MerkleTree
from codebase.system.ledger import ImmutableLedger

class VaultNative:
    """Native vault implementation"""
    
    def seal_session(self, session_data: dict) -> str:
        """Seal session with Merkle proof"""
        ledger = ImmutableLedger()
        entry = ledger.append(session_data)
        merkle_root = self.merkle_tree.add(entry)
        return merkle_root
```

---

## 🏗️ MIGRATION ENGINEERING ORDER

### Recommended Port Order (Dependencies First)

1. **Bundles** (codebase/bundles.py) ✅ Already exists
2. **Floor validators** (codebase/system/constitution.py)
3. **Crypto utilities** (Merkle, zkPC)
4. **ASI Room** (codebase/asi_room/) ✅ Already exists
5. **AGI Room** (codebase/agi_room/) - Need to port from arifos/core
6. **Bridge 666** (synthesis logic) - Most complex
7. **APEX 444** (consensus algorithm) - Core governance
8. **VAULT-999** (ledger sealing) - Immutability guaratee
9. **Stage orchestration** (pipeline manager)

### File-by-File Porting Checklist

- [ ] `arifos/core/asi/kernel.py` → `codebase/engines/asi/kernel_native.py` (175 lines)
- [ ] `arifos/core/engines/agi/kernel.py` → `codebase/engines/agi/kernel_native.py` (200+ lines)
- [ ] `arifos/core/apex/kernel.py` → `codebase/engines/apex/kernel_native.py` (150 lines)
- [ ] `arifos/core/integration/synthesis/*` → `codebase/stages/666/*.py` (551 lines)
- [ ] `arifos/core/memory/vault/*` → `codebase/vault/native/*.py` (300+ lines)
- [ ] `arifos/core/constitutional/*` → `codebase/system/constitution/*.py` (Validators)

**Total**: ~1500 lines of critical constitutional logic to port

---

## 🧪 TESTING STRATEGY: Confidence Building

### Test Pyramid for Migration

```
Layer 1: Unit Tests (Fast, Isolated)
├── Test ASIRoom in isolation
├── Test AGIRoom in isolation
├── Test bridge synthesis logic
└── Run: pytest tests/engines/ -m "not integration"

Layer 2: Integration Tests (Medium speed)
├── Test 555 → 666 → 444 flow
├── Test bundle conversion logic
├── Test consensus algorithm
└── Run: pytest tests/stages/ -m "integration"

Layer 3: End-to-End Tests (Slow, comprehensive)
├── Test full metabolic loop (000 → 999)
├── Compare verdicts: legacy vs native
├── Compare latencies: legacy vs native
└── Run: pytest tests/e2e/test_constitutional_loop.py

Layer 4: Production Shadow (Risk-free validation)
├── Legacy handles 100% traffic
├── Native runs in parallel (no user impact)
├── Compare verdicts in real-time
└── Flip switch when parity > 99.9%
```

### Parity Test Suite

```python
# tests/e2e/test_migration_parity.py

@pytest.mark.parametrize("test_query", CONSTITUTIONAL_TEST_CASES)
async def test_legacy_vs_native_verdict_parity(test_query):
    """
    Critical test: Both architectures must produce identical verdicts
    """
    # Legacy execution
    legacy_result = await legacy_pipeline.execute(test_query)
    
    # Native execution
    native_result = await native_pipeline.execute(test_query)
    
    # Must match exactly
    assert legacy_result.verdict == native_result.verdict
    assert legacy_result.floors_checked == native_result.floors_checked
    assert abs(legacy_result.latency - native_result.latency) < 0.5  # < 0.5ms diff
```

---

## ⚠️ RISK MITIGATION

### Risk 1: Constitutional Logic Errors During Port

**Mitigation**:
- Line-by-line port with comments marking provenance
- Unit tests for each floor validator
- Property-based testing (fuzzing) for edge cases
- Independent audit of critical paths (F1, F2, F8)

**Fallback**: Keep legacy available via feature flag

### Risk 2: Performance Regression

**Mitigation**:
- Latency budget: < 1ms per stage
- Profile before/after with py-spy
- Optimize bundle serialization
- Async everywhere (no blocking I/O)

**Fallback**: Optimize post-deploy if needed

### Risk 3: Bundle Incompatibility

**Mitigation**:
- Create conversion layer (`to_legacy()` / `from_legacy()`)
- Test round-trip conversion
- Version bundles (v1 = legacy dict, v2 = dataclass)
- Gradual migration of stored bundles

**Fallback**: Support both formats temporarily

---

## 🎯 MIGRATION TIMELINE

**Conservative Estimate**: 4-6 weeks for full migration

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | ASI + AGI kernel port | Native 555+333 working |
| 2 | Bridge 666 synthesis | Native dual-process fusion |
| 3 | APEX 444 consensus | Native F8 tri-witness |
| 4 | VAULT 999 sealing | Native immutability |
| 5 | Pipeline orchestration | Full native 000-999 loop |
| 6 | Stabilization & parity tests | >99.9% verdict match |

**Go-Live Criteria**:
- [ ] All constitutional tests pass (164+ tests)
- [ ] Parity > 99.9% (legacy vs native verdicts)
- [ ] Latency within 10% of legacy
- [ ] Zero regressions in production shadow
- [ ] Full audit trail preservation
- [ ] Rollback plan tested

---

## 🚀 IMMEDIATE NEXT ACTION

**Step 1**: Port ASI kernel to native
```bash
# Copy and adapt
# cp arifos/core/asi/kernel.py codebase/engines/asi/kernel_native.py
# Then modify to use OmegaBundle instead of dicts
```

**Step 2**: Test parity on simple case
```python
# Test query: "What is 2 + 2?"
# Expected: SEAL (F2 truth <= 0.99, F5 peace >= 1.0)
# Must match legacy verdict exactly
```

**Step 3**: Build conversion layer
```python
def legacy_to_native_bundle(legacy_dict: dict) -> OmegaBundle:
    """Convert legacy dict format to native dataclass bundle"""
    return OmegaBundle(
        session_id=legacy_dict["session_id"],
        vote=EngineVote(legacy_dict["verdict"]),
        empathy_kappa_r=legacy_dict.get("empathy_score", 0.0),
        # ... map all fields
    )
```

**Step 4**: Run full metabolic loop natively
```python
# 000 → 111 → 222 → 333 → 444 → 555 → 666 → 777 → 888 → 889 → 999
# All stages native, no proxy
```

---

## 💎 WISDOM: Why This Migration Matters

**Legacy Architecture**: 
- Monolithic, violates separation of concerns
- Not truly parallel (weakens F8 tri-witness)
- Bridge layer adds unnecessary complexity
- Harder to extend and reason about

**Native v53 Architecture**:
- True parallel execution (F8 guarantee)
- Clear stage boundaries (000, 111, 222...)
- Bundle-based communication (immutable contracts)
- Microservices-ready (can run rooms separately)

**Constitutional Value**: A migration from **simulated consensus** to **provable consensus**. When AGI, ASI, and APEX vote, you can **prove** they didn't influence each other.

---

**Authority**: Muhammad Arif bin Fazil
**Migration Status**: Phase 1 Initiated - ASI Kernel Port
**Target**: Native v53 by v54.0.0
**Motto**: Ditempa Bukan Diberi (Forged through migration, not given by default)
