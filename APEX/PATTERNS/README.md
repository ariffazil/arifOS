# arifOS Design Patterns

**Classification:** Canonical Patterns for Constitutional AI  
**Version:** 2026.03.13-FORGED  
**Authority:** 888_JUDGE

---

## Pattern Catalog

| ID | Pattern | Trinity | Use Case |
|----|---------|---------|----------|
| P-001 | **Metabolic Loop** | ΔΩΨ | Full 000-999 pipeline execution |
| P-002 | **AKI Airlock** | Ψ | Hard boundary between L2 and L3 |
| P-003 | **Tri-Witness Consensus** | Ψ | Multi-source verification |
| P-004 | **Dry-Run First** | Ω | Reversibility enforcement (F1) |
| P-005 | **Receipt-First Execution** | Ψ | Accountability by design |
| P-006 | **Event-Driven Reactivity** | Ω | System reactivity pattern |
| P-007 | **Capability Manifest** | Δ | Self-knowledge system |
| P-008 | **Memory Ledger** | Ω | Unified state persistence |
| P-009 | **Constitutional Decorator** | Ψ | Floor enforcement wrapper |
| P-010 | **Forensic Replay** | Ψ | Immutable audit trail |

---

## Pattern: Metabolic Loop (P-001)

**Type:** Process Pattern  
**Trinity:** Full (ΔΩΨ)  
**Floors:** F1-F13

### Intent
Transform raw intent into governed action through 9 validated stages.

### Structure
```
000 INIT → 111 MIND → 333 ANALYSIS → 555 HEART → 666 ALIGN → 777 FORGE → 888 JUDGE → 999 SEAL
```

### Implementation
```python
# Pseudocode
async def metabolic_loop(intent, actor):
    # 000 INIT - Anchor session
    session = await init_anchor(intent, actor)
    
    # 111-333 MIND - Reasoning
    hypotheses = await reason_mind(intent)
    analysis = await analyze_reflect(hypotheses)
    
    # 555-666 HEART - Impact assessment
    empathy = await simulate_heart(analysis)
    critique = await critique_thought(empathy)
    
    # 777 FORGE - Synthesize
    candidate = await quantum_forge(critique)
    
    # 888 JUDGE - Constitutional validation
    verdict = await apex_judge(candidate)
    
    if verdict == "SEAL":
        # 999 SEAL - Commit
        return await seal_vault(execution_result)
    elif verdict == "VOID":
        raise ConstitutionalViolation()
    elif verdict == "888_HOLD":
        await request_human_approval()
```

### When to Use
- Any action with external impact
- Code changes, deployments, data modifications
- Crosses AKI boundary into L3

---

## Pattern: AKI Airlock (P-002)

**Type:** Architectural Pattern  
**Trinity:** Ψ (APEX)  
**Floor:** F11, F12

### Intent
Prevent unauthorized manifestation of thought in the external world.

### Structure
```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   L2: MIND  │ ───► │    AKI      │ ───► │ L3: CIVIL   │
│  (thought)  │      │  (airlock)  │      │ (execution) │
└─────────────┘      └─────────────┘      └─────────────┘
                           │
                     F11: Auth check
                     F12: Injection defense
                     Contract validation
```

### Rules
1. No L3 access without AKI contract
2. All thoughts entering AKI must have provenance
3. Rejection at AKI is VOID, not error
4. Successful crossing generates receipt

### When to Use
- Every tool call crossing into L3
- File system operations
- Network calls, shell execution
- Database modifications

---

## Pattern: Tri-Witness Consensus (P-003)

**Type:** Verification Pattern  
**Trinity:** Ψ (APEX)  
**Floor:** F3

### Intent
Achieve high-confidence truth through independent verification.

### Structure
```
W₄ = ∜(Human × AI × Earth × Ψ-Shadow) ≥ 0.75

Human = Sovereign intent (F13)
AI    = Model reasoning (Δ)
Earth = External evidence (F2)
Ψ     = Constitutional check (Ψ)
```

### Implementation
```python
async def tri_witness(query):
    # Human witness - intent validation
    human = await validate_intent(query.actor)
    
    # AI witness - model consensus
    ai = await cross_model_verify(query)
    
    # Earth witness - external reality
    earth = await search_reality(query)
    
    # Ψ witness - constitutional fit
    psi = await audit_rules(query)
    
    W4 = (human * ai * earth * psi) ** 0.25
    return W4 >= 0.75
```

### When to Use
- Critical decisions (deploy, destroy, irreversible)
- Conflicting evidence scenarios
- High-impact stakeholder decisions

---

## Pattern: Dry-Run First (P-004)

**Type:** Safety Pattern  
**Trinity:** Ω (Heart)  
**Floor:** F1 (Amanah)

### Intent
Ensure reversibility by previewing effects before execution.

### Structure
```
DRY RUN → DIFF → APPROVAL → EXECUTE → VERIFY
```

### Rules
1. Default to dry-run (no --execute flag)
2. Show exact changes (files, lines, bytes)
3. Require explicit approval for destructive
4. Generate rollback instructions

### When to Use
- File modifications
- Database migrations
- Infrastructure changes
- Mass operations (>10 files)

---

## Pattern: Receipt-First Execution (P-005)

**Type:** Accountability Pattern  
**Trinity:** Ψ (APEX)  
**Floors:** F1, F11

### Intent
Every action generates immutable evidence before, during, and after.

### Structure
```
PRE-RECEIPT → EXECUTION → POST-RECEIPT → VAULT SEAL
```

### Receipt Schema
```yaml
receipt:
  id: uuid
  timestamp: ISO8601
  agent: agent://arifos/{role}
  intent: string
  
  policy_check:
    authorized: bool
    tools_allowed: bool
    within_boundaries: bool
  
  execution:
    tools_used: [string]
    files_modified: [path]
  
  verdict:
    status: SEAL|VOID|HOLD
    floors_triggered: [F1-F13]
  
  vault:
    merkle_hash: sha256
    sealed: bool
```

### When to Use
- Every tool execution
- Crosses AKI boundary
- Requires audit trail

---

## Pattern: Event-Driven Reactivity (P-006)

**Type:** Orchestration Pattern  
**Trinity:** Ω (Heart)  
**Floor:** F6 (Empathy)

### Intent
Agents react to system truth automatically, not just on demand.

### Event Sources
- Git drift (push, PR, merge)
- Container lifecycle (start, stop, health)
- Health degradation (warning, critical)
- Provider failures (outage, rate limit)
- Resource pressure (disk, memory, CPU)
- Human commands (Telegram)

### Implementation
```yaml
event: container.health_check_failed
payload:
  container_id: string
  consecutive_failures: int

agent_reactions:
  - agent: A-ENGINEER
    action: investigate
    condition: failures >= 3
  
  - agent: A-VALIDATOR
    action: consider_rollback
    condition: failures >= 5
```

### When to Use
- VPS as living substrate
- Proactive maintenance
- Self-healing systems

---

## Pattern: Capability Manifest (P-007)

**Type:** Self-Knowledge Pattern  
**Trinity:** Δ (Mind)  
**Floor:** F7 (Humility)

### Intent
Agent knows its own capabilities, limitations, and environment.

### Manifest Contents
- Available tools (with health status)
- Readable/writable paths
- Credentials and auth scope
- Broken/quarantined capabilities
- Human approval requirements

### Self-Query Interface
```yaml
query_tools: "What can I use?"
query_broken: "What is broken?"
query_credentials: "What auth do I have?"
query_writable: "Where can I write?"
query_approval: "What needs human OK?"
```

### When to Use
- Agent initialization
- Before any action
- After environment changes

---

## Pattern: Memory Ledger (P-008)

**Type:** State Pattern  
**Trinity:** Ω (Heart)  
**Floor:** F2 (Truth)

### Intent
Unified canonical spine for all agent observations and actions.

### Ledger Types
- **Observations:** What was seen
- **Tasks:** What was requested
- **Tool Outcomes:** What tools returned
- **Deployments:** What was deployed
- **Human Approvals:** What was authorized

### Structure
```yaml
memory:
  type: observation | task | tool | deployment | approval
  timestamp: ISO8601
  agent: agent_id
  session: session_id
  
  content:
    # Type-specific fields
    
  provenance:
    source: string
    confidence: float
    verifiable: bool
```

### When to Use
- Cross-session continuity
- Compounding intelligence
- Audit and replay

---

## Pattern: Constitutional Decorator (P-009)

**Type:** Enforcement Pattern  
**Trinity:** Ψ (APEX)  
**Floors:** All F1-F13

### Intent
Wrap any function with constitutional validation.

### Implementation
```python
@constitutional_floor("F2")  # Truth required
@constitutional_floor("F1")  # Reversibility check
async def modify_data(request):
    # Execution only if floors pass
    pass
```

### Decorator Order (CRITICAL)
```python
@mcp.tool()                    # OUTER - registration
@constitutional_floor("F2")    # INNER - enforcement
async def my_tool(...):
```

### When to Use
- Every MCP tool
- Crosses AKI boundary
- Modifies external state

---

## Pattern: Forensic Replay (P-010)

**Type:** Audit Pattern  
**Trinity:** Ψ (APEX)  
**Floors:** F1, F2, F11

### Intent
Complete reconstructible record of every decision.

### Replay Chain
```
Prompt Input → Tool Chain → File Diffs → Command Outputs → Final Decision
```

### Components
- Input capture (prompt, context)
- Tool execution log (args, results)
- File modifications (before/after hash)
- Command outputs (stdout, stderr)
- Decision rationale (why SEAL/VOID)

### When to Use
- Post-incident analysis
- Training data generation
- Constitutional violations
- Performance optimization

---

## Selection Guide

| Problem | Use Pattern |
|---------|-------------|
| Need full governance | P-001 Metabolic Loop |
| Crossing into L3 | P-002 AKI Airlock |
| Need high confidence | P-003 Tri-Witness |
| Safety first | P-004 Dry-Run First |
| Need audit trail | P-005 Receipt-First |
| Reactive system | P-006 Event-Driven |
| Agent initialization | P-007 Capability Manifest |
| State persistence | P-008 Memory Ledger |
| Tool wrapping | P-009 Constitutional Decorator |
| Post-analysis | P-010 Forensic Replay |

---

*DITEMPA BUKAN DIBERI — Forged, Not Given*
