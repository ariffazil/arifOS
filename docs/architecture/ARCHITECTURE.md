# arifOS Architecture

> **System:** Constitutional AI Governance Framework  
> **Version:** 2026.04.06 (Horizon II.1)  
> **Protocol:** MCP (Model Context Protocol)  
> **License:** AGPL-3.0-only

---

## 1. System Architecture

### 1.1 High-Level Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Claude    │  │   ChatGPT   │  │  Kimi CLI   │  │   Other MCP Clients │ │
│  │    Code     │  │   (Apps)    │  │             │  │                     │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼────────────────┼────────────────────┼────────────┘
          │                │                │                    │
          └────────────────┴────────────────┴────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TRANSPORT LAYER                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │  STDIO (local)  │  │  HTTP (VPS)     │  │  Streamable HTTP (ChatGPT)  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ORCHESTRATION LAYER                                │
│                     ┌─────────────────────────┐                              │
│                     │     444_ROUTER          │                              │
│                     │  (Route Execution)      │                              │
│                     │                         │                              │
│                     │  • Risk Assessment      │                              │
│                     │  • Stage Routing        │                              │
│                     │  • 888_HOLD Circuit     │                              │
│                     └─────────────────────────┘                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
           ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    GOVERNANCE   │    │   INTELLIGENCE  │    │     MACHINE     │
│     (Ψ PSI)     │    │   (Δ/Ω Trinity) │    │   (Execution)   │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ 000_INIT        │    │ 333_MIND        │    │ 111_SENSE       │
│   init_session  │    │   reason_syn    │    │   sense_real    │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ 888_JUDGE       │    │ 666_HEART       │    │ 555_MEMORY      │
│   judge_verdict │    │   critique_safe │    │   load_mem      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ 999_VAULT       │    │ 222_EXPLORE     │    │ 777_OPS         │
│   record_entry  │    │   (divergence)  │    │   estimate_ops  │
└─────────────────┘    └─────────────────┘    ├─────────────────┤
                                              │ M-3_EXEC        │
                                              │   execute_vps   │
                                              ├─────────────────┤
                                              │ M-4_ARCH        │
                                              │   get_registry  │
                                              └─────────────────┘
```

### 1.2 Data Flow

```
Query → 000_INIT (session) → 111_SENSE (ground) → 444_ROUTER (route)
                                                  │
                    ┌─────────────────────────────┼─────────────────────────────┐
                    │                             │                             │
                    ▼                             ▼                             ▼
              333_MIND                      666_HEART                    555_MEMORY
           (reasoning)                    (safety check)                (context)
                    │                             │                             │
                    └─────────────────────────────┼─────────────────────────────┘
                                                  │
                                                  ▼
                                           888_JUDGE (verdict)
                                                  │
                                                  ▼
                                           999_VAULT (audit)
```

---

## 2. Component Architecture

### 2.1 Clean MCP Separation

Following the Model Context Protocol specification, arifOS separates concerns into three primitives:

| Primitive | Purpose | Examples |
|-----------|---------|----------|
| **Tools** | Executable actions | `init_session_anchor`, `judge_verdict` |
| **Resources** | Read-only context | `arifos://governance/floors`, `arifos://status/vitals` |
| **Prompts** | Reusable templates | `prompt_init_anchor`, `prompt_judge_verdict` |

### 2.2 Tool Naming Convention

**Functional naming** (verbs for actions):

| Canonical Name | Symbolic Name | Stage | Trinity | Purpose |
|----------------|---------------|-------|---------|---------|
| `init_session_anchor` | `init_anchor` | 000_INIT | Ψ PSI | Session initialization |
| `get_tool_registry` | `architect_registry` | M-4_ARCH | Δ DELTA | Tool discovery |
| `sense_reality` | `physics_reality` | 111_SENSE | Δ DELTA | Reality grounding |
| `reason_synthesis` | `agi_mind` | 333_MIND | Δ DELTA | Logic and reasoning |
| `critique_safety` | `asi_heart` | 666_HEART | Ω OMEGA | Safety critique |
| `route_execution` | `arifOS_kernel` | 444_ROUTER | Δ/Ψ | Query routing |
| `load_memory_context` | `engineering_memory` | 555_MEMORY | Ω OMEGA | Vector memory |
| `estimate_ops` | `math_estimator` | 777_OPS | Δ DELTA | Cost estimation |
| `judge_verdict` | `apex_soul` | 888_JUDGE | Ψ PSI | Constitutional verdict |
| `record_vault_entry` | `vault_ledger` | 999_VAULT | Ψ PSI | Immutable audit |
| `execute_vps_task` | `code_engine` | M-3_EXEC | ALL | System execution |

### 2.3 Resource URIs

| URI | Auth | Content Type | Description |
|-----|------|--------------|-------------|
| `arifos://bootstrap` | None | JSON | Getting started guide |
| `arifos://governance/floors` | None | JSON | F1-F13 doctrine |
| `arifos://status/vitals` | None | JSON | Real-time health metrics |
| `arifos://agents/skills` | None | JSON | Agent capability guide |
| `arifos://vault/recent` | None | JSON | Last 100 verdicts (read-only) |
| `arifos://sessions/{id}/vitals` | Anchored | JSON | Session telemetry |
| `arifos://tools/{name}` | None | JSON | Tool contract |
| `https://mcp.af-forge.io/widget/vault-seal` | None | HTML | ChatGPT widget |

---

## 3. Constitutional Enforcement

### 3.1 The 13 Floors

| Floor | Name | Type | Threshold | Enforces |
|-------|------|------|-----------|----------|
| F1 | Amanah | Hard | ≥ 0.5 | Reversibility, audit mandate |
| F2 | Truth | Hard | ≥ 0.99 | Information fidelity |
| F3 | Tri-Witness | Hard | ≥ 0.95 | Multi-source verification |
| F4 | Clarity | Hard | ≤ 0 | Entropy reduction |
| F5 | Peace | Hard | ≥ 0.95 | Conflict absence |
| F6 | Empathy | Soft | ≥ 0.90 | Dignity preservation |
| F7 | Humility | Hard | 0.03-0.05 | Uncertainty acknowledgment |
| F8 | Coherence | Hard | ≥ 0.95 | Logical consistency |
| F9 | Non-Maleficence | Hard | ≥ 0.99 | Harm prevention |
| F10 | Ontology | Hard | N/A | No consciousness claims |
| F11 | Authority | Hard | Verified | Identity verification |
| F12 | Defense | Hard | N/A | Injection resistance |
| F13 | Sovereignty | Hard | Human | Human veto power |

### 3.2 Floor Enforcement Matrix

```
Tool          │ F1  F2  F3  F4  F5  F6  F7  F8  F9  F10 F11 F12 F13
──────────────┼─────────────────────────────────────────────────────
000_INIT      │  ✓   ✓       ✓           ✓   ✓   ✓   ✓   ✓   ✓
111_SENSE     │  ✓   ✓   ✓   ✓               ✓       ✓       ✓
333_MIND      │  ✓   ✓       ✓       ✓   ✓   ✓       ✓       ✓
444_ROUTER    │  ✓   ✓       ✓           ✓       ✓       ✓   ✓
555_MEMORY    │  ✓   ✓   ✓   ✓               ✓   ✓   ✓       ✓
666_HEART     │  ✓       ✓       ✓   ✓   ✓       ✓   ✓       ✓
777_OPS       │  ✓       ✓   ✓       ✓   ✓               ✓
888_JUDGE     │  ✓   ✓   ✓   ✓   ✓   ✓   ✓   ✓   ✓   ✓   ✓   ✓
999_VAULT     │  ✓   ✓   ✓   ✓           ✓       ✓   ✓   ✓   ✓
```

---

## 4. Deployment Architecture

### 4.1 Docker Stack

```
┌─────────────────────────────────────────────────────────────┐
│                     DOCKER COMPOSE STACK                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Nginx     │◄───│ arifos-mcp  │◄───│   Qdrant    │     │
│  │   :80/443   │    │   :3000     │    │   :6333     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                  │              │                 │
│         │           ┌──────┴──────┐       │                 │
│         │           │    Redis    │       │                 │
│         │           │   :6379     │       │                 │
│         │           └─────────────┘       │                 │
│         │                                 │                 │
│    ┌────┴────┐                     ┌──────┴──────┐          │
│    │  Widget │                     │   Vault999  │          │
│    │  Files  │                     │   (volume)  │          │
│    └─────────┘                     └─────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 ChatGPT Apps SDK Integration

**Phase 1 (Current): Read-Only**

```
┌──────────────┐      ┌──────────────────┐      ┌──────────────┐
│   ChatGPT    │──────▶│   arifOS MCP     │──────▶│   BLS        │
│   (iframe)   │      │   (read-only)    │      │   Signers    │
└──────────────┘      └──────────────────┘      └──────────────┘
       │                       │
       │              ┌────────┴────────┐
       │              │  888_HOLD       │
       └─────────────▶│  (blocks write) │
                      └─────────────────┘
```

**Exposed Tools:**
- `get_constitutional_health` — Telemetry snapshot
- `render_vault_seal` — Widget rendering
- `list_recent_verdicts` — Audit log (last 100)

**Security:**
- No vault write access
- No VPS execution paths
- No private keys in container
- CSP headers enforced

---

## 5. Data Models

### 5.1 TelemetryEnvelope

```json
{
  "session_id": "sess_abc123",
  "epoch": "2026-04-06",
  "timestamp": "2026-04-06T10:30:00Z",
  "tau_truth": 0.995,
  "omega_0": 0.04,
  "delta_s": -0.35,
  "peace2": 1.08,
  "kappa_r": 0.97,
  "tri_witness": 0.95,
  "psi_le": 1.09,
  "verdict_hint": "SEAL"
}
```

### 5.2 VerdictRecord

```json
{
  "record_id": "vrc_xyz789",
  "session_id": "sess_abc123",
  "timestamp": "2026-04-06T10:30:00Z",
  "verdict": "SEAL",
  "candidate_action": "deploy production",
  "risk_tier": "high",
  "floors_checked": ["F1", "F2", "F3", "F7", "F11", "F13"],
  "floors_failed": [],
  "juror_signatures": [...],
  "seal_status": "SEALED"
}
```

---

## 6. API Endpoints

### 6.1 MCP Protocol

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/mcp` | POST | MCP JSON-RPC endpoint |
| `/tools/list` | POST | List available tools |
| `/resources/list` | POST | List available resources |
| `/prompts/list` | POST | List available prompts |

### 6.2 Health & Metadata

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Service health status |
| `/build` | GET | Build metadata (sha, version) |
| `/ready` | GET | Readiness probe |

### 6.3 ChatGPT Widget

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/widget/vault-seal` | GET | Constitutional health widget |

---

## 7. Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| 2026.04.06 | Current | Clean architecture, Docker deployment, ChatGPT Apps SDK |
| 2026.04.05 | Archive surgery, core/ → arifosmcp/ migration |
| 2026.03.28 | Identity binding, ZKPC anchoring |
| 2026.03.20 | Horizon II launch, 11 Mega-Tools |

---

**Ditempa Bukan Diberi — Forged, Not Given**
