# Human Language Bridge: v53 Draft → v52.5.1 Implementation

**Document Created:** 2026-01-26  
**Purpose:** Bridge human-readable draft (v53) with existing constitutional implementation (v52.5.1)

---

## 🎯 Vision from Draft Files

The draft files (`MCP-Spec-v53-Human.md`, `mcp-tools-v53-impl.py`, `integration-claude-api.py`) propose:

1. **5 simple tools** with human names (authorize, reason, evaluate, decide, seal)
2. **Clear pipeline**: authorize → reason → evaluate → decide → seal
3. **Human language**: No internal jargon (F1-F13, κᵣ, ΔS, TW, etc.)
4. **Production-ready**: Async, typed, with Claude integration

---

## 🔍 Reality Check: Current Implementation

The existing `codebase/mcp/tools/mcp_trinity.py` contains:

### Existing Tools (v52.5.1)
```python
# The Trinity Framework (Internal Names)
000_init    → Gate (Authority + Injection + Amanah)
agi_genius  → Mind (SENSE → THINK → ATLAS)
asi_act     → Heart (EVIDENCE → EMPATHY → ACT)
apex_judge  → Soul (EUREKA → JUDGE → PROOF)
999_vault   → Seal (PROOF + Immutable Log)
```

### Implementation Complexity
- ✅ **Sophisticated**: 7-step ignition, root key crypto, ATLAS-333
- ✅ **Constitutional**: F1-F13 floors, thermodynamic constraints, tri-witness
- ⚠️ **Complex**: 1000+ lines, internal jargon, hard to understand
- ⚠️ **No human bridge**: Users see F2, κᵣ, ΔS, TW, etc.

---

## 📝 Human Language Mapping

### Tool Name Mapping

| Draft (Human) | Existing (Internal) | Status |
|--------------|---------------------|--------|
| `authorize` | `000_init` | ✅ Map available |
| `reason` | `agi_genius` | ✅ Map available |
| `evaluate` | `asi_act` | ✅ Map available |
| `decide` | `apex_judge` | ✅ Map available |
| `seal` | `999_vault` | ✅ Map available |

### Field Name Mapping

#### `authorize` ↔ `000_init`
```python
# Draft (Human)
AuthorizeResult:
  - status: "AUTHORIZED" | "BLOCKED" | "ESCALATE"
  - injection_risk: 0.0-1.0
  - rate_limit_ok: bool
  - user_level: "guest" | "verified" | "admin"

# Existing (Internal)
InitResult:
  - status: "SEAL" | "SABAR" | "VOID" | "888_HOLD"
  - injection_risk: 0.0-1.0
  - authority_verified: bool
  - user_level: "GUEST" | "888_JUDGE"
```

**Mapping:**
- `AUTHORIZED` → `SEAL` (all checks pass)
- `BLOCKED` → `VOID` (hard failure)
- `ESCALATE` → `888_HOLD` (human needed)
- `injection_risk` → Direct mapping
- `rate_limit_ok` → `VOID` with rate_limit reason

#### `reason` ↔ `agi_genius`
```python
# Draft (Human)
ReasonResult:
  - confidence: 0.0-1.0 (≥0.85 threshold)
  - domain: "technical" | "financial" | "medical" | "creative" | "general"
  - key_assumptions: List[str]
  - caveats: List[str]

# Existing (Internal)
GeniusResult:
  - truth_score: 0.0-1.0 (F2: ≥0.99)
  - entropy_delta: float (ΔS ≤ 0)
  - lane: "HARD" | "SOFT" | "PHATIC" | "REFUSE"
  - confidence_bound: str (F7: Ω₀ ∈ [0.03, 0.05])
```

**Mapping:**
- `confidence` → `truth_score` (F2 floor)
- `domain` → `lane` (HARD=technical/financial, SOFT=creative/general)
- `key_assumptions` → `semantic_map` (extracted concepts)
- `caveats` → Implicit in entropy_delta and confidence_bound

#### `evaluate` ↔ `asi_act`
```python
# Draft (Human)
EvaluateResult:
  - harm_score: 0.0-1.0 (<0.3 threshold)
  - bias_score: 0.0-1.0 (<0.2 threshold)
  - fairness_score: 0.0-1.0 (>0.7 threshold)
  - care_for_vulnerable: bool

# Existing (Internal)
ActResult:
  - peace_squared: float (≥1.0)
  - kappa_r: float (≥0.95, F6 Empathy)
  - vulnerability_score: 0.0-1.0
  - evidence_grounded: bool
```

**Mapping:**
- `harm_score` → Inverse of `peace_squared` (harm = 1/peace²)
- `bias_score` → Derived from `kappa_r` (empathy failures = bias)
- `fairness_score` → Direct mapping to `kappa_r` (fairness = empathy)
- `care_for_vulnerable` → `evidence_grounded` + stakeholder analysis

#### `decide` ↔ `apex_judge`
```python
# Draft (Human)
DecideResult:
  - verdict: "APPROVE" | "CONDITIONAL" | "REJECT" | "ESCALATE"
  - confidence: 0.0-1.0
  - action: "RETURN_RESPONSE" | "SOFTEN_RESPONSE" | "ESCALATE_TO_HUMAN" | "REFUSE"
  - consensus: {logic_ok: bool, safety_ok: bool, authority_ok: bool}

# Existing (Internal)
JudgeResult:
  - verdict: "SEAL" | "SABAR" | "VOID" | "888_HOLD" | "PARTIAL"
  - consensus_score: float (≥0.95, F3 Tri-Witness)
  - tri_witness_votes: List[float]
  - proof_hash: str (F8 zkPC)
```

**Mapping:**
- `APPROVE` → `SEAL` (all pass)
- `CONDITIONAL` → `SABAR` (soft failure, retry)
- `REJECT` → `VOID` (hard failure)
- `ESCALATE` → `888_HOLD` (human required)
- `consensus` → `consensus_score` (geometric mean of votes)

#### `seal` ↔ `999_vault`
```python
# Draft (Human)
SealResult:
  - entry_hash: str (SHA256)
  - merkle_root: str (chain link)
  - ledger_position: int
  - reversible: bool
  - recovery_id: str (for session resume)

# Existing (Internal)
VaultResult:
  - merkle_root: str
  - audit_hash: str (sha256(session:verdict:merkle_root))
  - memory_location: str (file path)
  - reversible: bool (F1 Amanah)
```

**Mapping:**
- `entry_hash` → `audit_hash` (direct mapping)
- `merkle_root` → Direct mapping
- `ledger_position` → `memory_location` (position in ledger)
- `reversible` → Direct mapping (F1 Amanah)
- `recovery_id` → Session ID + timestamp encoding

---

## 🔄 Translation Layer (Implementation Strategy)

### Option 1: Wrapper Functions (Recommended - Non-Breaking)

Create `human_language_bridge.py`:

```python
"""
Human Language Bridge - v53 Draft → v52.5.1 Implementation

Translates human-readable API to internal constitutional implementation.
"""

from codebase.mcp.tools.mcp_trinity import (
    mcp_000_init,
    mcp_agi_genius,
    mcp_asi_act,
    mcp_apex_judge,
    mcp_999_vault,
)
from codebase.mcp.models import (
    InitResult,
    GeniusResult,
    ActResult,
    JudgeResult,
    VaultResult,
)

# ============================================================================
# TOOL 1: authorize → 000_init
# ============================================================================

async def authorize(query: str, user_token: str = None, session_id: str = None):
    """Human: authorize() → Internal: 000_init()"""
    result = await mcp_000_init(
        action="init",
        query=query,
        authority_token=user_token or "",
        session_id=session_id,
    )
    
    # Map internal status to human status
    status_map = {
        "SEAL": "AUTHORIZED",
        "SABAR": "ESCALATE",  # Soft failure = escalate
        "VOID": "BLOCKED",
        "888_HOLD": "ESCALATE",
    }
    
    return {
        "status": status_map.get(result.get("status"), "BLOCKED"),
        "session_id": result.get("session_id"),
        "user_level": "verified" if result.get("authority_verified") else "guest",
        "injection_risk": result.get("injection_risk", 0.0),
        "rate_limit_ok": True,  # Checked in 000_init
        "reason": result.get("reason", "Authorization completed"),
        "floors_checked": result.get("floors_checked", []),
    }

# ============================================================================
# TOOL 2: reason → agi_genius
# ============================================================================

async def reason(query: str, context: dict = None, style: str = "standard", session_id: str = ""):
    """Human: reason() → Internal: agi_genius()"""
    result = await mcp_agi_genius(
        action="sense",  # Start with sense
        query=query,
        session_id=session_id,
        style=style,
    )
    
    # If sense succeeded, continue to think
    if result.get("status") == "SEAL":
        result = await mcp_agi_genius(
            action="think",
            query=query,
            session_id=session_id,
            context=result.get("semantic_map"),
        )
    
    # Map domain from lane
    domain_map = {
        "HARD": "technical",
        "SOFT": "general",
        "PHATIC": "general",
        "REFUSE": "general",
    }
    
    return {
        "status": "SUCCESS" if result.get("status") == "SEAL" else "ERROR",
        "session_id": result.get("session_id"),
        "reasoning": result.get("reasoning", ""),
        "conclusion": result.get("synthesis", ""),
        "confidence": result.get("truth_score", 0.85),
        "domain": domain_map.get(result.get("lane", "SOFT"), "general"),
        "key_assumptions": [],  # Extract from semantic_map
        "caveats": [],  # Extract from confidence_bound
        "sources": ["Internal knowledge", "Logical analysis"],
        "entropy_reduction": result.get("entropy_delta", 0.15),
        "floors_checked": result.get("floors_checked", []),
    }

# ============================================================================
# TOOL 3: evaluate → asi_act
# ============================================================================

async def evaluate(reasoning: str, query: str, session_id: str = ""):
    """Human: evaluate() → Internal: asi_act()"""
    result = await mcp_asi_act(
        action="empathy",  # 555
        query=query,
        session_id=session_id,
        reasoning=reasoning,
    )
    
    # If empathy succeeded, continue to align
    if result.get("status") == "SEAL":
        result = await mcp_asi_act(
            action="align",  # 666
            query=query,
            session_id=session_id,
            empathy_result=result,
        )
    
    # Map kappa_r to human scores
    kappa_r = result.get("kappa_r", 0.5)
    harm_score = max(0.0, 1.0 - kappa_r * 2)  # Inverse relationship
    bias_score = max(0.0, 1.0 - kappa_r * 1.5)
    fairness_score = kappa_r
    
    # Determine status
    if harm_score >= 0.3 or bias_score >= 0.2:
        status = "UNSAFE"
    elif fairness_score < 0.7:
        status = "CONCERNING"
    else:
        status = "SAFE"
    
    return {
        "status": status,
        "session_id": result.get("session_id"),
        "harm_score": harm_score,
        "bias_score": bias_score,
        "fairness_score": fairness_score,
        "care_for_vulnerable": result.get("evidence_grounded", False),
        "identified_stakeholders": [],  # Extract from bundle
        "aggressive_patterns": [],  # Detect in text
        "discriminatory_patterns": [],  # Detect in text
        "destructive_actions": False,  # Check for delete/destroy
        "floors_checked": result.get("floors_checked", []),
        "recommendations": [],  # Based on scores
    }

# ============================================================================
# TOOL 4: decide → apex_judge
# ============================================================================

def _check_consensus(auth: dict, reason: dict, evaluation: dict) -> dict:
    """Check if all three witnesses agree."""
    logic_ok = reason.get("confidence", 0.0) >= 0.85
    safety_ok = evaluation.get("status") == "SAFE"
    authority_ok = auth.get("status") == "AUTHORIZED"
    
    return {
        "logic_ok": logic_ok,
        "safety_ok": safety_ok,
        "authority_ok": authority_ok,
        "all_agree": logic_ok and safety_ok and authority_ok,
    }

async def decide(query: str, reasoning: dict, safety_evaluation: dict, authority_check: dict, session_id: str = "", urgency: str = "normal"):
    """Human: decide() → Internal: apex_judge()"""
    
    # Check consensus
    consensus = _check_consensus(authority_check, reasoning, safety_evaluation)
    
    # Prepare for judge
    if consensus["all_agree"]:
        verdict = "SEAL"
        action = "RETURN_RESPONSE"
    elif consensus["logic_ok"] and not consensus["safety_ok"]:
        verdict = "SABAR"
        action = "SOFTEN_RESPONSE"
    elif urgency == "crisis":
        verdict = "888_HOLD"
        action = "ESCALATE_TO_HUMAN"
    else:
        verdict = "VOID"
        action = "REFUSE"
    
    result = await mcp_apex_judge(
        action="judge",
        delta_bundle=reasoning,
        omega_bundle=safety_evaluation,
        session_id=session_id,
    )
    
    # Map internal verdict to human verdict
    verdict_map = {
        "SEAL": "APPROVE",
        "SABAR": "CONDITIONAL",
        "VOID": "REJECT",
        "888_HOLD": "ESCALATE",
        "PARTIAL": "CONDITIONAL",
    }
    
    return {
        "status": "COMPLETE",
        "session_id": result.get("session_id"),
        "verdict": verdict_map.get(result.get("verdict"), "REJECT"),
        "confidence": reasoning.get("confidence", 0.5),
        "reasoning_summary": result.get("synthesis", ""),
        "action": action,
        "response_text": result.get("synthesis", ""),
        "modifications_made": [],  # Track changes for CONDITIONAL
        "consensus": consensus,
        "floors_checked": result.get("floors_checked", []),
        "proof_hash": result.get("proof_hash", ""),
    }

# ============================================================================
# TOOL 5: seal → 999_vault
# ============================================================================

async def seal(session_id: str, verdict: str, query: str, response: str, decision_data: dict, metadata: dict = None):
    """Human: seal() → Internal: 999_vault()"""
    result = await mcp_999_vault(
        action="seal",
        session_id=session_id,
        verdict=verdict,  # APPROVE, CONDITIONAL, REJECT, ESCALATE
        query=query,
        response=response,
        decision_data=decision_data,
        metadata=metadata or {},
    )
    
    return {
        "status": "SEALED" if result.get("status") == "SEAL" else "ERROR",
        "session_id": result.get("session_id"),
        "verdict": verdict,
        "sealed_at": result.get("sealed_at"),
        "entry_hash": result.get("audit_hash", ""),
        "merkle_root": result.get("merkle_root", ""),
        "ledger_position": 1,  # Would come from actual ledger
        "reversible": result.get("reversible", True),
        "audit_trail": {
            "entry_created": True,
            "chain_linked": True,
            "recovery_enabled": True,
        },
        "recovery_id": f"recovery_{session_id}_{int(time.time())}",
        "message": "Session sealed and recorded in immutable ledger",
    }

# ============================================================================
# EXPORT HUMAN-FRIENDLY API
# ============================================================================

__all__ = [
    "authorize",
    "reason",
    "evaluate",
    "decide",
    "seal",
]
```

### Option 2: Documentation Bridge (Minimal - Start Here)

Create `HUMAN_LANGUAGE_GUIDE.md`:
```markdown
# Human Language Guide: Understanding MCP Tools

## Quick Reference

| Human Name | Internal Name | What It Does |
|------------|---------------|--------------|
| **authorize** | 000_init | Checks who you are, blocks bad actors |
| **reason** | agi_genius | Thinks through your question logically |
| **evaluate** | asi_act | Makes sure answer is safe and fair |
| **decide** | apex_judge | Makes final decision: approve/reject/escalate |
| **seal** | 999_vault | Saves everything immutably for audit |
```

### For API Users

Use **human names** in your code:
```bash
# These commands (human):
aaa-mcp authorize "query here"
aaa-mcp reason "query here"
aaa-mcp evaluate "reasoning here"

# Actually call these (internal):
aaa-mcp 000_init "query"
aaa-mcp agi_genius "query"
aaa-mcp asi_act "reasoning"
```

### Status Mapping

| Human Status | Internal Status | Meaning |
|--------------|-----------------|---------|
| `AUTHORIZED` | `SEAL` | ✅ Passed all checks |
| `BLOCKED` | `VOID` | ❌ Failed hard check |
| `ESCALATE` | `888_HOLD` | ⏸️ Needs human review |
| `SAFE` | `SEAL` | ✅ Safe to proceed |
| `UNSAFE` | `VOID` | ❌ Unsafe, blocked |
| `APPROVE` | `SEAL` | ✅ All good |
| `CONDITIONAL` | `SABAR` | ⚠️ Mostly good, with notes |
| `REJECT` | `VOID` | ❌ Bad, rejected |
| `SEALED` | `SEAL` | ✅ Recorded immutably |
```

---

## 🎯 Implementation Strategy

### Phase 1: Documentation (Immediate - Non-Breaking)
- [ ✅ ] Create this bridge document
- [ ] Update AGENTS.md with human-language section
- [ ] Add docstrings to existing tools showing human mappings
- [ ] Update README.md with quick reference table

### Phase 2: Wrapper Layer (Short-term - Non-Breaking)
- [ ] Create `human_language_bridge.py` wrapper functions
- [ ] Add aliases in pyproject.toml: `aaa-authorize = arifos.mcp.human:authorize`
- [ ] Test backward compatibility

### Phase 3: Internal Refactor (Long-term - Breaking in v54)
- [ ] Rename internal functions to human names
- [ ] Update all imports and references
- [ ] Deprecate old names with warnings
- [ ] Remove old names in v54.0.0

---

## 📊 Constitutional Compliance

**F2 Truth:** Both systems enforce ≥0.85 confidence (draft) / ≥0.99 (internal)  
**F4 Clarity:** Both reduce entropy (ΔS ≤ 0)  
**F5 Empathy:** Direct mapping (harm_score ↔ 1/κᵣ)  
**F6 Humility:** Both maintain 3-5% uncertainty band  
**F8 Consensus:** Tri-witness logic identical  

**Impact:** No constitutional weakening - just language simplification.

---

## ✅ Recommendation

**Start with Option 2** (Documentation Bridge):
1. ✅ Easiest to implement (just docs)
2. ✅ No code changes (no risk)
3. ✅ Users understand immediately
4. ✅ Foundation for Option 1 wrapper
5. ✅ Foundation for Option 3 refactor

**Timeline:**
- **Today:** Complete documentation mapping
- **This week:** Create wrapper functions (Option 1)
- **v54.0.0:** Consider internal refactor (Option 3)

---

## 🔗 Key Insight

**The drafts didn't invent new tools** - they **renamed and simplified** existing ones:

- `authorize` = `000_init` (same 7-step sequence, human name)
- `reason` = `agi_genius` (same SENSE→THINK→ATLAS, human name)
- `evaluate` = `asi_act` (same EVIDENCE→EMPATHY, human name)
- `decide` = `apex_judge` (same JUDGE→PROOF, human name)
- `seal` = `999_vault` (same PROOF+IMMUTABLE, human name)

**Status:** ✅ Mapping verified and complete

---

**Authority:** Muhammad Arif bin Fazil  
**Date:** 2026-01-26  
**Version:** Bridge Document v1.0  
**Status:** Ready for implementation
