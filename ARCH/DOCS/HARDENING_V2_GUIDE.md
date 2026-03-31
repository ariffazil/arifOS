# arifOS Hardening v2 — Deployment Guide

**Version:** 2026.03.22-HARDENED-V2  
**Date:** 2026-03-22  
**Status:** Hardened 11-Tool Chain Complete

---

## Executive Summary

This guide documents the **Global Hardening v2** upgrades for all 11 arifOS MCP tools. These upgrades implement fail-closed defaults, typed contracts, trace lineage, human decision markers, and entropy budgets across the entire constitutional pipeline.

### Key Improvements

| Category | Before | After |
|----------|--------|-------|
| **Contracts** | Untyped dicts | `ToolEnvelope` with status, hashes, evidence_refs |
| **Failure Mode** | Open / continue | Closed / hold / escalate |
| **Traceability** | Optional context | Required trace_id, parent_trace_id, stage_id |
| **Human Oversight** | Implicit | Explicit decision markers |
| **Quality Control** | Ad hoc | Entropy budget (ambiguity, contradictions) |

---

## Architecture Overview

### 11 Hardened Tools

| Stage | Tool | Core Hardening |
|-------|------|----------------|
| 000 | `init_anchor` | Session classification, scope degradation, auth expiry |
| 111 | `reality_compass` | Typed evidence bundles, source credibility decay |
| 222 | `reality_atlas` | Claim nodes + contradiction edges, unresolved hold |
| 333 | `agi_reason` | 4-lane reasoning (baseline/alternative/adversarial/null) |
| 444 | `agi_reflect` | *In 333* Coherence check, memory conflict detection |
| 666A | `asi_critique` | 5-axis red-team, counter-seal veto on high scores |
| 666B | `asi_simulate` | *Placeholder* Consequence modeling, misuse paths |
| 777 | `arifOS_kernel` | Minimal-privilege orchestration, tool chain integrity |
| 888A | `agentzero_engineer` | Plan→commit two-phase, rollback artifacts |
| 888B | `apex_judge` | Machine-verifiable verdicts, conditional approval |
| 999 | `vault_seal` | Decision object sealing, hash-complete ledger |

### Tool Response Contract

All tools return `ToolEnvelope`:

```python
@dataclass
class ToolEnvelope:
    status: Literal["ok", "hold", "void", "error"]  # Fail-closed
    tool: str
    session_id: str
    risk_tier: RiskTier
    confidence: float  # Tri-witness derived
    
    # Integrity
    inputs_hash: str
    outputs_hash: str
    evidence_refs: list[str]
    
    # Governance
    human_decision: HumanDecisionMarker
    requires_human: bool
    next_allowed_tools: list[str]
    
    # Lineage
    trace: TraceContext
    
    # Quality
    entropy: EntropyMetrics
    
    # Payload
    payload: dict[str, Any]
    warnings: list[str]
```

---

## Fail-Closed Defaults

Every tool enforces fail-closed validation:

```python
def validate_fail_closed(
    auth_context: dict | None,
    risk_tier: str | None,
    session_id: str | None,
    tool: str,
    trace: TraceContext | None,
    requires_evidence: bool = False,
    evidence_refs: list[str] | None = None,
) -> ValidationResult:
    """
    Return HOLD if ANY required field is missing.
    Return VOID if critical evidence missing on high-tier calls.
    """
```

### Failure Actions

| Missing | Action | Reason |
|---------|--------|--------|
| `auth_context` | HOLD | Cannot verify actor |
| `risk_tier` | HOLD | Unknown severity |
| `session_id` | HOLD | No audit trail |
| `trace` | HOLD | No lineage |
| `evidence_refs` (high tier) | VOID | Decisions without evidence |

---

## Cross-Tool Trace IDs

```python
@dataclass
class TraceContext:
    trace_id: str          # Root transaction ID
    parent_trace_id: str   # Previous stage ID
    stage_id: str          # Current stage (000_INIT, 333_MIND, etc.)
    policy_version: str    # Constitutional version applied
    timestamp: str         # ISO 8601 UTC
```

### Chain Integrity

```python
def verify_chain_integrity(
    envelopes: list[ToolEnvelope]
) -> ChainIntegrityResult:
    """
    Verify parent_trace_id linkage across the pipeline.
    Detect breaks or replay attacks.
    """
```

---

## Human Decision Markers

```python
class HumanDecisionMarker(str, Enum):
    MACHINE_RECOMMENDATION_ONLY = "machine_recommendation_only"
    HUMAN_CONFIRMATION_REQUIRED = "human_confirmation_required"
    HUMAN_APPROVAL_BOUND = "human_approval_bound"
    ESCALATED = "escalated"
    SEALED = "sealed"
```

### Marker Assignment

| Scenario | Marker | Behavior |
|----------|--------|----------|
| Low entropy, no conflicts | MACHINE_RECOMMENDATION_ONLY | Auto-execute |
| Ambiguity score > 0.5 | HUMAN_CONFIRMATION_REQUIRED | Block, request confirm |
| Counter-seal triggered | HUMAN_APPROVAL_BOUND | Block, escalate to admin |
| Threshold breach | ESCALATED | Stop, manual review |
| Sealed decision | SEALED | Immutable, logged |

---

## Entropy Budget

```python
@dataclass
class EntropyMetrics:
    ambiguity_score: float      # 0.0-1.0, higher = more uncertain
    contradictions: int         # Count of conflicting claims
    assumptions_made: list[str] # Assumptions burned down
    blast_radius_estimate: str  # limited/moderate/significant/catastrophic
    confidence: float           # Derived: 1.0 - ambiguity
```

### Quality Gates

| Metric | Threshold | Action |
|--------|-----------|--------|
| `ambiguity_score` > 0.6 | HOLD | Too uncertain |
| `contradictions` > 3 | HOLD | Unresolved conflicts |
| `blast_radius` = catastrophic | ESCALATE | Human review required |
| `assumptions` without evidence | WARN | Flag for confirmation |

---

## Tool-Specific Hardening

### init_anchor (000)

```python
class SessionClass(str, Enum):
    PROBE = "probe"           # No side effects
    QUERY = "query"           # Read-only
    EXECUTE = "execute"       # Write/modify
    DESTRUCTIVE = "destructive"  # Delete, admin ops

# Scope negotiation degrades:
# If requested EXECUTE but not authorized → QUERY
# If requested DESTRUCTIVE → requires explicit approval
```

### reality_compass (111)

```python
@dataclass
class EvidenceBundle:
    bundle_id: str
    claim_type: Literal["fact", "opinion", "hypothesis", "projection"]
    source_url: str
    source_credibility: float  # Decays with age
    observed_facts: list[str]
    claim_hash: str
    timestamp: str
```

### reality_atlas (222)

```python
@dataclass
class ClaimNode:
    node_id: str
    claim_type: str
    evidence_refs: list[str]
    status: Literal["verified", "disputed", "unresolved"]

@dataclass
class ContradictionEdge:
    edge_id: str
    source_node: str
    target_node: str
    contradiction_type: Literal["mutual_exclusion", "temporal", "scope"]
```

### agi_reason (333)

```python
@dataclass
class ReasoningLane:
    lane_type: Literal["baseline", "alternative", "adversarial", "null"]
    interpretation: str
    confidence: float
    evidence_cited: list[str]
    assumptions_made: list[str]

# Outputs decision forks, not single narrative:
# {"if": "X confirmed", "then": "baseline wins", "else": "alternative wins"}
```

### asi_critique (666A)

```python
# 5-axis critique
axes = ["factual", "logical", "authority", "safety", "ambiguity"]

# Counter-seal: high critique → downstream veto
CRITIQUE_THRESHOLD = 0.6
if max_severity > threshold:
    counter_seal = True
    status = HOLD
    requires_human = True
```

### agentzero_engineer (888A)

```python
class ActionClass(str, Enum):
    READ = "read"
    WRITE = "write"
    MODIFY = "modify"
    EXECUTE = "execute"
    NETWORK = "network"
    DESTRUCTIVE = "destructive"

# Two-phase:
# 1. plan() → returns diff_preview, rollback_plan
# 2. commit() → executes only if approved=True
```

### apex_judge (888B)

```python
# Machine-verifiable conditions (not just prose)
conditions = [
    {"type": "evidence_freshness", "param": "hours_since_ingest", "op": "<", "value": 24},
    {"type": "scope_limit", "param": "action_class", "op": "==", "value": "read"},
]
```

### vault_seal (999)

```python
@dataclass
class DecisionObject:
    decision_id: str
    input_hashes: list[str]
    evidence_hashes: list[str]
    decision_text: str
    rationale: dict
    policy_version: str
    approver_id: str
    seal_class: Literal["provisional", "operational", "constitutional", "sovereign"]
    supersedes: str | None  # Link to previous decision this updates
```

---

## Usage Examples

### Basic Query

```python
from arifosmcp.runtime.hardened_toolchain import HardenedToolchain

chain = HardenedToolchain()
result = await chain.execute(
    query="What is the constitutional status of action X?",
    declared_name="arif",
    session_id="sess-001",
    risk_tier="low",
)

print(result.status)  # "ok"
print(result.payload["verdict"])  # Constitutional verdict
```

### With Auth Context

```python
result = await chain.execute(
    query="Execute maintenance script",
    declared_name="arif",
    session_id="sess-002",
    requested_scope=["execute", "write"],
    risk_tier="high",
    session_class="execute",
    auth_context={
        "actor_id": "arif",
        "identity_proof": "semantic_key",
        "authority_level": "admin",
    },
)

# If scope not fully granted:
# result.payload["init"]["scope_negotiated"] = True
# result.payload["init"]["scope_granted"] = ["query", "read"]
```

### Handling Hold State

```python
result = await chain.execute(
    query="Delete production database",
    declared_name="attacker",
    session_id="sess-003",
    requested_scope=["destructive"],
    risk_tier="sovereign",
)

if result.status == "hold":
    print("Human approval required")
    print(result.human_decision)  # human_approval_bound
    print(result.payload.get("plan"))  # Diff preview before commit
```

---

## Testing

```bash
# Run hardened toolchain tests
pytest tests/test_hardened_toolchain.py -v

# Run all hardening tests
pytest tests/ -k "hardened" -v

# Test specific tool
pytest tests/test_init_hardened.py -v
pytest tests/test_truth_pipeline.py -v
```

---

## Migration Guide

### From Legacy Tools

| Legacy Call | Hardened Equivalent |
|-------------|---------------------|
| `init_anchor()` | `init_anchor.init()` with session_class |
| `reality_search()` | `reality_compass.search()` with EvidenceBundle |
| `agi_mind()` | `agi_reason.reason()` with 4-lane output |
| `asi_heart()` | `asi_critique.critique()` with counter-seal |
| `apex_soul()` | `apex_judge.judge()` with conditions |
| `vault_ledger()` | `vault_seal.seal()` with DecisionObject |

### Breaking Changes

1. **All tools now return `ToolEnvelope`** instead of raw dicts
2. **`auth_context`, `risk_tier`, `session_id` are required** — missing = HOLD
3. **`trace` is auto-generated** if not provided, but recommended to pass
4. **`requires_human` is explicit** — check before auto-execution

---

## Security Considerations

### Fail-Closed Philosophy

> "When in doubt, hold. When certain, seal."

All tools default to HOLD unless:
- All required auth fields present
- Entropy below thresholds
- No counter-seal triggers
- Human decision marker allows proceed

### Audit Trail

Every tool call generates:
1. **Trace ID** — unique transaction identifier
2. **Hashes** — SHA-256 of inputs and outputs
3. **Evidence refs** — linked to facts, not opinions
4. **Decision object** — sealed in vault for later verification

### Rollback Capability

`agentzero_engineer` attaches rollback artifacts:
- Pre-execution state snapshot
- Inverse operations for write/modify actions
- Recovery commands for destructive operations

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2026.03.22-INIT-UNIFIED | 2026-03-22 | Unified init_anchor, 5 modes |
| 2026.03.22-HARDENED-V2 | 2026-03-22 | All 11 tools hardened with v2 contracts |

---

## References

- `arifosmcp/runtime/contracts_v2.py` — Core contract types
- `arifosmcp/runtime/init_anchor_hardened.py` — Hardened init_anchor
- `arifosmcp/runtime/truth_pipeline_hardened.py` — Reality compass/atlas
- `arifosmcp/runtime/tools_hardened_v2.py` — Remaining 8 tools
- `arifosmcp/runtime/hardened_toolchain.py` — Master integration

---

*"DITEMPA BUKAN DIBERI" — Forged, Not Given*
