# CAPABILITY_GRAPH_v1 — Canonical Kernel Capability Graph

> **SOT-MANIFEST**
> owner: Arif
> last_verified: 2026-06-24
> valid_from: 2026-06-24
> valid_until: 2026-07-24
> confidence: high
> scope: /root/arifOS
> epistemic_status: PROPOSAL → RATIFIED (F13 sovereign directive)

---

## 1. Purpose

The arifOS kernel is the governed substrate. MCP is the syscall membrane. The **Capability Graph** is the single source of truth that connects them:

- The kernel owns the graph.
- Every MCP tool must be a node in the graph.
- If a tool is not in the graph, no MCP server may expose it.
- If a session lacks authority for a node, the kernel returns `KERNEL_DENY`.

This document is the canonical v1 specification.

---

## 0. Scope Boundary (Post-Audit)

> **Premise correction:** arifOS is a governance kernel, not yet a full AGI substrate.
> This spec specifies **one necessary layer** of the substrate: the **capability surface + action bus**.
> It intentionally does NOT specify embodied memory, world model, bounded learning, or multi-domain synthesis.
> Those layers are defined in the broader `AGI_SUBSTRATE_v1` architecture.
> See audit: `/root/forge_work/CAPABILITY_GRAPH_v1_AUDIT.md`

This document governs:
- Which tools exist.
- Who can invoke them.
- What verdict loop is required.
- How refusal is expressed.

It does not govern what the system knows, how it learns, or how it models reality.

---

## 2. Design Principles

1. **One graph to rule them all.** No more `CANONICAL_TOOLS`, `tool_registry.json`, `public_tool_specs`, `mcp_surface_registry.yaml`, and `capability_map.py` drifting apart.
2. **Kernel-owned, organs-register.** GEOX/WEALTH/WELL/A-FORGE propose their tools; the kernel approves and publishes the graph.
3. **INIT-first.** A session token derived from `arif_init` is required before any non-observe tool.
4. **Self-correction-before-irreversible.** Any tool marked `requires_self_correction = true` must have a `self_correction_trace_id` from `arif_self_correct`.
5. **Denial is data.** `KERNEL_DENY` returns a structured envelope with reason, missing gate, and next safe action.

---

## 3. Graph Node Schema

```yaml
CapabilityNode:
  tool_name: str           # canonical name, e.g. "arif_forge_execute"
  organ: str               # owning organ: arifos | geox | wealth | well | aforge | aaa
  surface: str             # transport surface: mcp | a2a | http | stdio
  category: str            # constitutional | domain | diagnostic | substrate

  authority:
    tier: str              # OBSERVE | SUGGEST | SIMULATE | DRAFT | QUEUE |
                           # EXECUTE_REVERSIBLE | EXECUTE_HIGH_IMPACT | IRREVERSIBLE
    min_ceiling: str       # lowest authority ceiling allowed to invoke

  reversibility:
    class: str             # fully_reversible | reversible_with_effort | irreversible
    ack_required: bool     # human ack for IRREVERSIBLE / EXECUTE_HIGH_IMPACT

  verdict_loop:
    requires_init: bool    # true for all non-observe tools
    requires_self_correction: bool  # true for EXECUTE_HIGH_IMPACT and above
    requires_judge: bool   # true for IRREVERSIBLE
    requires_seal: bool    # true for IRREVERSIBLE

  witnesses:
    human: bool            # human in the loop required
    kernel: bool           # kernel log/receipt required
    vault: bool            # VAULT999 receipt required

  geometry:
    allowed_actor_ids: list[str] | null   # null = any actor that passes ceiling
    forbidden_actor_ids: list[str]
    allowed_sessions: list[str] | null
    modes: list[str] | null               # e.g. ["init","state","status"] for arif_init

  metadata:
    description: str
    schema_version: str    # ABI version this node conforms to
    doc_uri: str | null
    deprecated: bool
    superseded_by: str | null

  # Runtime fields (kernel-managed)
  registered_at: timestamp
  registered_by: actor_id
  last_audit_at: timestamp
  node_hash: str          # SHA-256 of canonical fields above
```

---

## 4. Canonical Kernel MCP Tools

### 4.1 `arif_init` (already exists, harden)

Input: `InitAnchorRequest`  
Output: `InitAnchorResponse` + `session_token`

The session token is:

```
base64url( sha256( actor_id + session_id + surface + restraint_flags + verdict_geometry + kernel_secret ) )
```

- Short-lived (default 3600s).
- Must be presented in the `_session_token` field of subsequent tool calls.
- Carries the bound geometry (restraint flags, verdict trace, authority ceiling).

### 4.2 `arif_self_correct` (new)

Input:

```yaml
SelfCorrectRequest:
  session_token: str
  target: str              # tool_name or decision being corrected
  candidate_action: str
  evidence: dict
  risk_level: str          # low | medium | high | critical
```

Output:

```yaml
SelfCorrectResponse:
  decision: PROCEED | HOLD | ASK | REFUSE
  corrected_target: str
  delta: str               # what changed
  trace_id: str            # VAULT999-ready receipt ID
  reasons: list[str]
  missing_evidence: list[str]
```

Behavior:

- Loads the session geometry.
- Applies the One Skill (Knowing What NOT To Do):
  - ambiguous → `ASK`
  - uncertain + high risk → `HOLD`
  - authority insufficient → `REFUSE`
- Emits a receipt line to VAULT999 if the decision is not `PROCEED`.

### 4.3 `arif_surface_register` (new)

Used by organs to propose tools.

Input: `CapabilityNode` (without runtime fields)  
Output: `{ approved: bool, node_hash: str, reason: str | null }`

Rules:

- Only `arifos` kernel may approve.
- Domain organs may propose; kernel adjudicates.
- Duplicate `tool_name` rejected unless `deprecated=true` and `superseded_by` set.

### 4.4 `arif_surface_query` (new)

Input:

```yaml
SurfaceQueryRequest:
  session_token: str
  tool_name: str | null    # null returns allowed subset for session
  surface: str | null
  organ: str | null
```

Output:

```yaml
SurfaceQueryResponse:
  allowed_tools: list[CapabilityNode]
  denied_tools: list[{tool_name, reason, missing_gate}]
```

### 4.5 `arif_surface_deny` (implicit)

Not a tool. It is the envelope returned by MCP middleware when a request violates the graph.

```yaml
KernelDenyEnvelope:
  ok: false
  verdict: KERNEL_DENY
  reason: str
  missing_gate: str | null
  next_safe_action: str
  session_valid: bool
  required_authority_tier: str | null
```

---

## 5. MCP Middleware Contract

Every MCP server in the federation must implement:

### 5.1 Startup

1. Load its proposed tool list.
2. Call `arif_surface_register` for each proposed tool.
3. Cache the approved `CapabilityNode` list.
4. Expose **only** approved tools via `tools/list`.

### 5.2 Per-request

1. Extract `_session_token` from tool-call arguments or HTTP header `X-ArifOS-Session`.
2. If token missing / expired → `KERNEL_DENY` (`missing_gate: INIT_REQUIRED`).
3. Look up `CapabilityNode` for requested `tool_name`.
4. If not in graph → `KERNEL_DENY` (`missing_gate: UNKNOWN_CAPABILITY`).
5. Compare session authority ceiling to node `min_ceiling`.
   - Insufficient → `KERNEL_DENY` (`missing_gate: AUTHORITY_INSUFFICIENT`).
6. If `requires_self_correction = true` and no `self_correction_trace_id` → `KERNEL_DENY` (`missing_gate: SELF_CORRECTION_REQUIRED`).
7. If `ack_required = true` and no `human_ack_token` → `KERNEL_DENY` (`missing_gate: HUMAN_ACK_REQUIRED`).
8. Forward to tool handler.

### 5.3 Enforcement layers

| Layer | What it blocks |
|-------|----------------|
| Transport | Missing session token |
| Graph lookup | Unknown tool |
| Authority ceiling | Under-privileged actor |
| Verdict loop | Missing self-correction / judge / seal |
| Tool handler | Domain-specific safety |

---

## 6. Authority Tier Ladder

| Tier | Can invoke |
|------|------------|
| OBSERVE | read-only tools (`arif_observe`, `arif_think`) |
| SUGGEST | planning/simulation tools |
| DRAFT | code/docs generation without side effects |
| QUEUE | deferred execution |
| EXECUTE_REVERSIBLE | reversible file/system changes |
| EXECUTE_HIGH_IMPACT | service restart, deploy, commit |
| IRREVERSIBLE | `DROP TABLE`, volume removal, destructive deletes |

Authority ceiling is bound at `arif_init` based on actor identity + surface + human approval.

---

## 7. Example Graph Entries

```yaml
# Kernel constitutional core
- tool_name: arif_init
  organ: arifos
  surface: mcp
  category: constitutional
  authority: { tier: OBSERVE, min_ceiling: OBSERVE }
  reversibility: { class: fully_reversible, ack_required: false }
  verdict_loop: { requires_init: false, requires_self_correction: false, requires_judge: false, requires_seal: false }
  witnesses: { human: false, kernel: true, vault: true }

- tool_name: arif_forge_execute
  organ: arifos
  surface: mcp
  category: substrate
  authority: { tier: EXECUTE_REVERSIBLE, min_ceiling: EXECUTE_REVERSIBLE }
  reversibility: { class: reversible_with_effort, ack_required: true }
  verdict_loop: { requires_init: true, requires_self_correction: true, requires_judge: true, requires_seal: true }
  witnesses: { human: true, kernel: true, vault: true }

# Domain organ example
- tool_name: geox_seismic_compute
  organ: geox
  surface: mcp
  category: domain
  authority: { tier: SUGGEST, min_ceiling: OBSERVE }
  reversibility: { class: fully_reversible, ack_required: false }
  verdict_loop: { requires_init: true, requires_self_correction: false, requires_judge: false, requires_seal: false }
  witnesses: { human: false, kernel: true, vault: false }
```

---

## 8. Migration from Current Registries

Current authority surface is fragmented:

| Old source | Migrates to |
|------------|-------------|
| `CANONICAL_TOOLS` in `runtime/tools.py` | kernel graph: constitutional core |
| `tool_registry.json` | kernel graph: all registered tools + metadata |
| `public_tool_specs` | graph node `metadata.schema_version` + ABI refs |
| `mcp_surface_registry.yaml` | graph `surface` + `allowed_sessions` fields |
| `capability_map.py` legacy constants | graph node `authority.tier` |
| `RESTRAINT_VERDICT_REQUIREMENTS` | graph `verdict_loop` + `reversibility` fields |

Migration script responsibilities:

1. Read all old registries.
2. Build `CapabilityNode` objects.
3. Detect collisions (same `tool_name`, different organs).
4. Write unified graph to `/opt/arifos/app/data/capability_graph_v1.json`.
5. Validate every node against ABI schemas.
6. Publish read API at `/capability/graph`.

---

## 9. Runtime Architecture

```
┌─────────────────────────────────────────┐
│  arifOS Kernel                          │
│  ├─ CapabilityGraph (single source)     │
│  ├─ arif_init → session_token           │
│  ├─ arif_self_correct → trace_id        │
│  ├─ arif_surface_register / query       │
│  └─ KERNEL_DENY envelope generator      │
└────────────┬────────────────────────────┘
             │ graph + session validation
┌────────────▼────────────────────────────┐
│  MCP Servers (GEOX/WEALTH/WELL/A-FORGE) │
│  ├─ startup: register proposed tools    │
│  ├─ per-request: validate session token │
│  └─ expose only approved tools          │
└────────────┬────────────────────────────┘
             │ tool calls
┌────────────▼────────────────────────────┐
│  Clients (Hermes, Claude, Codex, etc.)  │
│  ├─ first call: arif_init               │
│  ├─ before irreversible: arif_self_correct│
│  └─ attach session_token to every call  │
└─────────────────────────────────────────┘
```

---

## 10. Acceptance Criteria

- [ ] `CapabilityNode` Pydantic model exists in `arifosmcp/schemas/capability_graph.py`.
- [ ] `arif_self_correct`, `arif_surface_register`, `arif_surface_query` tools implemented.
- [ ] Migration script imports old registries into unified graph.
- [ ] MCP middleware in GEOX/WEALTH/WELL/A-FORGE validates session token and graph membership.
- [ ] Unknown tool request returns `KERNEL_DENY` with structured envelope.
- [ ] Runtime test: unregistered tool cannot be invoked through any MCP surface.
- [ ] VAULT999 receipt emitted for every `arif_self_correct` non-PROCEED decision.

---

## 11. Relation to One Skill / One Tool

- **One Skill (Knowing What NOT To Do)** → encoded in `verdict_loop.requires_self_correction` + `authority.tier` + `reversibility.ack_required`.
- **One Tool (Verdict Loop With Memory)** → `arif_init` binds geometry; `arif_self_correct` produces trace; `arif_judge` + `arif_seal` close the loop.
- **Capability Graph** → makes both enforceable at the MCP syscall boundary.

---

## 12. Next Steps

1. Ratify this spec (F13).
2. Implement `arifosmcp/schemas/capability_graph.py`.
3. Implement kernel tools in `arifosmcp/tools/capability_graph.py`.
4. Write migration script `scripts/migrate_capability_graph_v1.py`.
5. Wire middleware into GEOX MCP server as pilot.
6. Expand to WEALTH, WELL, A-FORGE MCP surfaces.

---

*DITEMPA BUKAN DIBERI — Intelligence is forged, not given.*
