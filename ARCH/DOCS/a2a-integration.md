# A2A Integration Specification

**Version:** 2026.03.20  
**Status:** SEAL (Constitutional Integration)  
**Protocol:** Google A2A (April 2025) + arifOS 13-Floor Governance

---

## 1. Architecture

### 1.1 Position in 000→999 Pipeline

A2A negotiation enters at **111_SENSE**, NOT at the output stage. This is intentional — agents may agree on anything, but constitutional floors are absolute.

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  A2A    │───→│  111_   │───→│  333_   │───→│  666_   │───→│  888_   │
│Negotiate│    │  SENSE  │    │  MIND   │    │  HEART  │    │  JUDGE  │
│(intent) │    │(ground) │    │(reason) │    │(safety) │    │(verdict)│
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
     ↑                                                        ↓
     └──────────────── 999_VAULT (seal) ←─────────────────────┘
```

### 1.2 Critical Rule

**A2A output has NO privileged status in the pipeline.**

- Treat A2A messages as **external input** (same as human user input)
- Apply full F1-F13 scrutiny to all A2A-proposed actions
- 666_HEART can reject agent-agreed plans that violate safety floors

---

## 2. Governance Boundaries

### 2.1 What A2A CAN Do

| Capability | Stage | Floors |
|------------|-------|--------|
| Submit task requests | 111_SENSE | F12 (injection scan) |
| Propose skill execution | 333_MIND | F2 (truth), F4 (clarity) |
| Request status updates | 444_ROUTER | F11 (auth scope) |
| Negotiate parameters | 333_MIND | F4 (clarity) |

### 2.2 What A2A CANNOT Do (Hard Blocks)

| Prohibition | Enforced By | Floor |
|-------------|-------------|-------|
| Bypass 666_HEART | Pipeline order | F6, F7, F8 |
| Override 888_JUDGE | Verdict authority | F13 |
| Direct VAULT writes | Stage routing | F1, F11 |
| Claim sovereign identity | Auth validation | F11 |
| Request execution without SEAL | allow_execution flag | F1 |

---

## 3. Implementation

### 3.1 A2A Task Execution Flow

```python
# A2A Server Implementation (arifosmcp/runtime/a2a/server.py)

async def _execute_task(self, task_id: str):
    task = await self.get_task(task_id)
    
    # Step 1: 000_INIT — Anchor session
    init_result = await call_mcp_tool("init_anchor", {...})
    if init_result.verdict != "SEAL":
        task.state = TaskState.FAILED
        return
    
    # Step 2: 333_MIND — Reason about the task
    # A2A negotiation results enter here as "external proposals"
    reason_result = await call_mcp_tool("agi_reason", {...})
    
    # Step 3: 666_HEART — Safety critique
    # THIS IS THE GOVERNANCE GATE
    critique_result = await call_mcp_tool("asi_critique", {
        "plan": reason_result.plan,
        "a2a_origin": True,  # Flag for special scrutiny
    })
    
    # Step 4: 888_JUDGE — Verdict
    judge_result = await call_mcp_tool("apex_judge", {
        "critique_result": critique_result,
        "candidate_output": reason_result.plan,
    })
    
    # Step 5: Execution only on SEAL
    if judge_result.verdict == "SEAL":
        execution_result = await call_mcp_tool("arifOS_kernel", {...})
        task.state = TaskState.COMPLETED
    elif judge_result.verdict == "888_HOLD":
        task.state = TaskState.INPUT_REQUIRED
        # Human must ratify (F13 Sovereign)
    else:
        task.state = TaskState.FAILED
```

### 3.2 Multi-Agent Consensus

When multiple agents negotiate:

1. Each agent's proposal is treated as **independent input**
2. 333_MIND synthesizes proposals (does not arbitrate)
3. 666_HEART evaluates synthesized plan against F1-F13
4. 888_JUDGE issues single verdict

**No agent voting or weighted consensus.** Constitutional floors are absolute, not probabilistic.

---

## 4. Failure Modes

### 4.1 A2A-Specific HOLD States

| HOLD Code | Trigger | Resolution |
|-----------|---------|------------|
| `HOLD_A2A_IDENTITY` | Agent claims protected sovereign ID | Reject or require crypto proof |
| `HOLD_A2A_AMBIGUOUS` | Agents propose conflicting actions | Require clarification at 333_MIND |
| `HOLD_A2A_UNGROUNDED` | A2A task lacks reality grounding | Trigger 111_SENSE evidence ingest |

### 4.2 Rejection Mapping

| A2A Protocol State | arifOS Verdict | Meaning |
|-------------------|----------------|---------|
| `INPUT_REQUIRED` | 888_HOLD | Needs human ratification |
| `FAILED` | VOID | Constitutional violation |
| `CANCELLED` | SABAR | Graceful abort |
| `COMPLETED` | SEAL | Full success |

---

## 5. Security Considerations

### 5.1 Agent Identity

- A2A agents are **never** sovereign
- Agent identity is `declared`, not `verified`
- Agents cannot mint auth_context tokens

### 5.2 Isolation

- Each A2A task gets **isolated session**
- No cross-task memory sharing without explicit VAULT read
- AgentZero tools sandboxed per task

### 5.3 Rate Limiting

```yaml
# A2A rate limits (suggested)
max_tasks_per_agent: 100/hour
max_concurrent_tasks: 10
max_message_size: 1MB
```

---

## 6. Configuration

```yaml
# arifosmcp/config/a2a.yaml
a2a:
  enabled: true
  mount_point: "/a2a"
  require_human_for:
    - irreversible_actions  # F1
    - vault_seal           # F11
    - sovereign_impersonation  # F11
  
  constitutional_gates:
    sense_111: true   # Ground all A2A input
    mind_333: true    # Reason about proposals
    heart_666: true   # Safety critique (REQUIRED)
    judge_888: true   # Final verdict
  
  agent_trust_tiers:
    unknown: "low"
    verified_partner: "medium"
    internal_cluster: "high"  # Still not sovereign
```

---

## 7. Verification

### 7.1 Test Cases

```python
# Test: A2A cannot bypass 666_HEART
async def test_a2a_safety_gate():
    agent_proposal = {"action": "delete_production_database"}
    result = await a2a_server.submit_task(agent_proposal)
    assert result.verdict == "VOID"  # F1 (reversibility)

# Test: A2A with conflicting agents
async def test_a2a_conflict_resolution():
    proposals = [
        {"agent": "A", "action": "deploy"},
        {"agent": "B", "action": "rollback"},
    ]
    result = await a2a_server.negotiate(proposals)
    assert result.state == TaskState.INPUT_REQUIRED  # HOLD for human
```

---

**Motto:** *Agent consensus is input, not authority.*
