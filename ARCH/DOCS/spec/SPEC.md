# arifOSMCP Protocol Profile (SPEC)

> **Document Type:** Normative server profile / implementation contract  
> **Status:** Draft  
> **Owner:** ARIF  
> **MCP Protocol:** 2025-11-25  
> **FastMCP Framework:** 3.x (pinned)  

**Motto:** *Ditempa Bukan Diberi* — Forged, Not Given [ΔΩΨ | ARIF]

---

## 1. Purpose

arifOSMCP defines a governed MCP server profile for sovereign-controlled intelligence systems, specifying how diagnostics, identity, grounding, memory, verification, and governed execution are exposed to MCP clients.

## 2. Non-Goals

- arifOSMCP does **not** redefine MCP wire semantics
- arifOSMCP does **not** grant autonomous authority to the server
- arifOSMCP does **not** use prompts as a substitute for protocol contracts

## 3. Design Principles

### 3.1 Sovereign Control
The server MUST expose governance boundaries clearly and MUST NOT imply independent authority for consequential decisions.

### 3.2 Clarity Over Cleverness
Every blocked state MUST return a recovery path.

### 3.3 Protocol-Native Exposure
Anything discoverable should be exposed through MCP-native components first:
- **Resources** for static/inspectable state
- **Prompts** for guided workflows  
- **Tools** for actions or computed operations

### 3.4 Open Access (Current Phase)
Authentication is **optional** in this phase. The server operates in "local-trust mode" for STDIO and open mode for HTTP. Auth middleware is architected but not enforced.

---

## 4. Protocol Version

```yaml
mcp_protocol_revision: "2025-11-25"
compatibility_floor: "2025-06-18"

framework:
  name: fastmcp
  version: "3.x.y"  # exact minor pinned in deployment
```

---

## 5. Transport Profile

### 5.1 Supported Transports

| Transport | Use Case | Auth | Notes |
|-----------|----------|------|-------|
| `stdio` | Local development, trusted desktop | None (local-trust) | Protocol available, preferred for CLI |
| `streamable-http` | Production deployment | Optional (OAuth2.1 ready) | Future enforcement, currently open |
| `sse` | Legacy compatibility | Optional | Allowed where needed |

### 5.2 Current Policy
- **STDIO:** Default for local CLI usage, no auth
- **HTTP:** Open access for broad adoption, auth layer ready for future enforcement

---

## 6. Component Taxonomy

### 6.1 Resources (Inspectables)

| URI | Auth | Description |
|-----|------|-------------|
| `arifos://status/vitals` | None | Current health, capability map, degraded components |
| `arifos://governance/floors` | None | Constitutional F1-F13 thresholds and doctrine |
| `arifos://caller/state` | Anchored | Current caller state, allowed/blocked tools |
| `arifos://bootstrap/guide` | None | Startup path, canonical sequence, example payloads |
| `arifos://contracts/tools` | None | Tool contract table: risk, auth, mutability |
| `arifos://ledger/integrity` | Verified | Merkle chain integrity (VAULT999) |

### 6.2 Prompts (Guided Workflows)

| Prompt | Parameters | Purpose |
|--------|------------|---------|
| `bootstrap_session` | `actor_id`, `declared_name`, `intent` | Guide identity establishment |
| `explain_blocked_state` | `code` | Explain why blocked and how to recover |
| `prepare_kernel_call` | `goal`, `risk_tier` | Prepare governed execution |
| `summarize_constitutional_floors` | None | Explain F1-F13 in context |

### 6.3 Tools (Actions)

#### Tier 0: Diagnostics (Anonymous Allowed)
- `check_vital` — System health and capability map
- `audit_rules` — Constitutional floor inspection

#### Tier 1: Identity Bootstrap (Anonymous Entry)
- `init_anchor_state` — Establish session and identity

#### Tier 2: Grounding & Continuity (Anchored)
- `search_reality` — External fact grounding
- `ingest_evidence` — Evidence normalization
- `session_memory` — Semantic recall

#### Tier 3: Verification (Verified)
- `verify_vault_ledger` — Merkle chain verification

#### Tier 4: Governed Execution (Anchored+)
- `arifOS_kernel` — Metabolic loop router (mode: inspect/analyze/recommend/execute)

---

## 7. Canonical Bootstrap Flow

```yaml
bootstrap_flow:
  - step: 1
    tool: check_vital
    state_required: anonymous
    output: [health, capabilities, degraded_components]
    
  - step: 2
    tool: audit_rules
    state_required: anonymous
    output: [constitutional_floors, doctrine_hooks]
    
  - step: 3
    tool: init_anchor_state
    state_required: anonymous_or_claimed
    input: [actor_id, declared_name, intent]
    output: [anchored_session, auth_context_seed]
    
  - step: 4
    tool: arifOS_kernel
    state_required: anchored
    modes: [inspect, analyze, recommend, execute]
    output: [governed_execution_result]
```

### 7.1 Global Session Rule
`session_id="global"` MUST be treated as **diagnostics-only** and MUST NOT authorize state change or consequential execution.

### 7.2 Recovery Rule
If a caller invokes `arifOS_kernel` without required context, the server MUST return:
- Current caller state
- Why blocked
- Next required tool
- Required fields
- Example payload
- Whether retry is safe

---

## 8. Caller State Machine

| State | Meaning | Allows |
|-------|---------|--------|
| `anonymous` | No identity claim | `check_vital`, `audit_rules` |
| `claimed` | actor_id provided, not anchored | Diagnostics only |
| `anchored` | `init_anchor_state` succeeded | + `session_memory`, `ingest_evidence`, `search_reality`, kernel prep |
| `verified` | Cryptographic proof accepted | + `verify_vault_ledger` |
| `scoped` | Approval scope granted | + low-risk kernel calls |
| `approved` | Human escalation cleared | + high-risk kernel, mutations |

---

## 9. Authentication & Authorization

### 9.1 Current Policy: Open Phase
- **No passwords or secrets required**
- **Anonymous access allowed** for diagnostics
- **Identity claim sufficient** for anchored state
- Auth infrastructure present but not enforced

### 9.2 Future-Ready Architecture
```yaml
auth_context:
  session_id: "session-..."
  actor_id: "arif"
  capability_class: "sovereign|operator|agent"
  approval_scope: []
  escalation_hold: null
```

### 9.3 Scope Mapping (Future)
- `arifos.vitals.read` — diagnostics
- `arifos.rules.read` — governance inspection
- `arifos.memory.read` — continuity
- `arifos.kernel.low` — low-risk execution
- `arifos.kernel.high` — high-risk execution

---

## 10. Tool Contract Model

Every tool MUST publish:

```yaml
tool_contract:
  canonical_name: string
  title: string
  description: string
  risk_class: low|medium|high|critical
  auth_required: boolean
  caller_states_allowed: [anonymous, claimed, anchored, ...]
  mutates_state: boolean
  structured_output: true
  required_args: [ ... ]
  optional_args: [ ... ]
  returns:
    - machine_fields
    - human_summary
  errors:
    - code
    - reason
    - remediation
  next_actions:
    - tool
    - reason
```

---

## 11. Error Envelope (Normative)

```json
{
  "ok": false,
  "tool": "arifOS_kernel",
  "verdict": "HOLD",
  "status": "ERROR",
  "caller_state": "anonymous",
  "code": "F11_COMMAND_AUTH",
  "message": "auth_context missing for kernel execution",
  "recoverable": true,
  "remediation": {
    "next_tool": "init_anchor_state",
    "required_args": ["actor_id", "declared_name", "intent"],
    "example_payload": {
      "actor_id": "arif",
      "declared_name": "Muhammad Arif",
      "intent": "testing kernel governance flow"
    },
    "retry_safe": true,
    "human_approval_required": false
  }
}
```

---

## 12. Dynamic Visibility

Components filtered by caller state:

| State | Visible Components |
|-------|-------------------|
| `anonymous` | Diagnostics only |
| `anchored` | + Continuity tools |
| `verified` | + Ledger verification |
| `scoped` | + Low-risk kernel |
| `approved` | + All components |

---

## 13. Testing Requirements

### 13.1 Required Test Classes
- `lifecycle_handshake`
- `anonymous_diagnostics_access`
- `kernel_auth_rejection`
- `bootstrap_success`
- `caller_state_transition`
- `structured_tool_output_schema`

### 13.2 Golden Journeys
1. anonymous → diagnostics
2. anonymous → anchored
3. anchored → kernel low-risk
4. verified → ledger + low-risk kernel

---

## 14. Telemetry Fields

```yaml
telemetry_fields:
  - session_id
  - actor_id
  - caller_state
  - tool_name
  - risk_class
  - verdict
  - protocol_revision
  - transport
  - duration_ms
```

---

## 15. Immediate Implementation Priorities

### P1: Bootstrap Clarity
- [x] Resource: `arifos://bootstrap/guide`
- [x] Resource: `arifos://caller/state`
- [ ] Prompt: `bootstrap_session`

### P2: Component Taxonomy
- [ ] Organize tools by tier
- [ ] Implement resource exposure
- [ ] Add prompt templates

### P3: Error Remediation
- [x] Every error has `remediation` block
- [x] Every response has `caller_state`
- [x] Every blocked call has `next_action`

### P4: Version Pinning
- [x] MCP: 2025-11-25
- [x] FastMCP: 3.x

---

*Forged, Not Given* 🔨  
**Document Version:** 2026.03.17-SPEC  
**Canonical Status:** Draft for Implementation
