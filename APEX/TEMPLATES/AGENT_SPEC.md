# Template: Agent Specification

**Use this template when defining a new agent in the arifOS system.**

---

## Agent Identity

```yaml
agent:
  name: "A-{ROLE}"
  symbol: "{emoji}"
  trinity: "{Δ|Ω|Ψ}"
  
  identity:
    uuid: "agent://arifos/{role}"
    fingerprint: "sha256:{role}-v{version}"
    created: "YYYY-MM-DDTHH:MM:SSZ"
    owner: "Muhammad Arif bin Fazil"
  
  authority: "888_JUDGE"
```

## Role Definition

| Aspect | Value |
|--------|-------|
| **Primary Role** | {Design|Execution|Audit|Validation} Authority |
| **Trinity Domain** | {AGI Mind (Δ)|ASI Heart (Ω)|APEX Soul (Ψ)} |
| **Metabolic Stages** | {000-333|555-666|777-888} |
| **Floor Focus** | {F2,F4,F7,F8|F5,F6,F9|F3,F10-F13} |

## Policy

```yaml
policy:
  capability_class: "{READ-PLAN|EDIT-WRITE|READ-REVIEW|DEPLOY-SEAL}"
  max_execution_scope: "{design-only|implementation|audit-only|deployment-gate}"
  
  permissions:
    can_read: true/false
    can_write: true/false
    can_delete: true/false
    can_deploy: true/false
    can_destroy: true/false
  
  requires_human_approval: true/false
```

## Tool Permissions

### Allowed Tools
| Tool | Purpose | Risk Tier |
|------|---------|-----------|
| `tool_name` | Description | low/medium/high |

### Forbidden Tools
| Tool | Reason | 888_HOLD Required |
|------|--------|-------------------|
| `tool_name` | Why forbidden | yes/no |

## Constitutional Bindings

```yaml
constitutional_bindings:
  F1_Amanah:
    threshold: 0.5
    enforced: true
  
  F2_Truth:
    threshold: 0.99
    enforced: true
  
  # Add relevant floors for this agent
```

## Boundaries

```yaml
boundaries:
  max_file_size_mb: {number}
  max_operations_per_session: {number}
  
  forbidden_patterns:
    - "rm -rf"
    - "DROP TABLE"
    # Add patterns
```

## Receipt Configuration

```yaml
receipts:
  require_execution_log: true
  require_constitutional_check: true
  require_human_approval: {true|false}
  vault_seal: true
```

## Invocation

```
@a-{role} {task description}
```

## Example Tasks

### Task 1: {Description}
**Input:**
```
@a-{role} {example command}
```

**Expected Behavior:**
- Step 1
- Step 2
- Step 3

**Output:**
```yaml
receipt:
  verdict: SEAL
  # Expected receipt fields
```

---

*Fill in all {placeholders} and remove comments before sealing.*
