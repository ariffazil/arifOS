---
type: Concept
tags: [eigent, backend, multi-agent, desktop-automation, H2, swarm, MiniMax]
sources: [ROADMAP.md, CHANGELOG.md]
last_sync: 2026-04-08
confidence: 0.9
---

# Eigent Backend

> **Status**: ✅ Deployed (H1 Complete)  
> **Endpoint**: `https://eigent.vps.arif-fazil.com`  
> **Model**: MiniMax-M2.7  
> **Tier**: Horizon 1 → Horizon 2 Bridge

---

## Definition

**Eigent Backend** is the multi-agent desktop automation framework deployed on arifOS VPS infrastructure. It represents the first production bridge between **local constitutional governance** (arifOS MCP) and **remote agent swarms** capable of desktop-level task automation.

The name derives from:
- **Eigen** (German: "own, intrinsic, characteristic") — the inherent capability of the system
- **Agent** — autonomous actor with bounded scope
- Together: "Intrinsic Agent Substrate"

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     arifOS MCP (Local)                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │  init   │  │  sense  │  │  mind   │  │  judge  │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       └─────────────┴─────────────┴─────────────┘           │
│                         │                                   │
│                    arifos.forge                             │
│                         │                                   │
└─────────────────────────┼───────────────────────────────────┘
                          │ HTTPS
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Eigent Backend (VPS)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  MiniMax-M2  │  │  Web Search  │  │   Vision     │      │
│  │  (Inference) │  │  (Exa/Brave) │  │  (Image)     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         └─────────────────┴─────────────────┘              │
│                         │                                  │
│                  Desktop Automation                         │
│              (Browser, Files, System)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. MiniMax-M2.7 Integration

| Capability | Tool | Status |
|------------|------|--------|
| Text generation | `minimax_chat` | ✅ Active |
| Web search | `web_search_exa` | ✅ Connected |
| Image understanding | `understand_image` | ✅ Connected |
| Code generation | `minimax_code` | ✅ Active |

**Integration Mode**: MCP tools on VPS expose MiniMax capabilities to local arifOS via tool bridging.

### 2. Desktop Automation Surface

Eigent provides governed access to:

| Domain | Operations | F1 Reversibility |
|--------|------------|------------------|
| **Browser** | Navigate, click, extract, fill | Session-scoped |
| **Filesystem** | Read, list, archive | Backup required |
| **Processes** | List, monitor, signal | Non-destructive |
| **Network** | HTTP requests, WebSocket | Logged |

All operations flow through `arifos.forge` with SEAL gating.

### 3. Constitutional Bridge

Eigent operates under **888_HOLD** for all desktop automation:

```
Local arifOS          VPS Eigent
    │                       │
    │─arifos.init──────────>│  Session bind
    │─arifos.sense─────────>│  Evidence gather
    │─arifos.judge─────────>│  Verdict request
    │<─SEAL────────────────│  Authority granted
    │─arifos.forge─────────>│  Execute on desktop
    │<─result──────────────│  Return with telemetry
```

---

## Governance Model

### Horizon 1 Mode (Current)

- **Human-in-the-loop**: Every desktop action requires explicit approval
- **Session-scoped**: Credentials and context expire after session
- **Audit trail**: All actions logged to Vault999 via bridge
- **Read-preference**: Default to observation, write requires escalation

### Horizon 2 Mode (Planned)

- **EvidenceBundle**: A2A protocol for agent handoffs
- **Governed Auto-Deploy**: Terraform/Pulumi gated by Vault999
- **ΔS Gauges**: Real-time entropy monitoring
- **Cross-Agent RAG**: Qdrant-backed memory sharing

---

## Deployment Evidence

| Component | Evidence | Location |
|-----------|----------|----------|
| Endpoint health | HTTPS 200 | `eigent.vps.arif-fazil.com/health` |
| Model loaded | MiniMax-M2.7 | VPS inference container |
| MCP bridge | Tool spec compliance | `arifosmcp/runtime/bridge.py` |
| Audit logs | Vault999 entries | `VAULT999/eigent_*.jsonl` |

---

## Roadmap Position

Eigent sits at the **H1→H2 boundary**:

```
Horizon 1 (Execution Engine)    Horizon 2 (Swarm)
        │                              │
    [Complete]                    [Evolving]
        │                              │
    ┌───┴───┐                    ┌─────┴─────┐
    │ Eigent │ ─────────────────>│ A2A Proto │
    │Backend │    Bridge          │  Swarm    │
    └────────┘                    └───────────┘
```

**H2 Dependencies on Eigent**:
- EvidenceBundle serialization (Eigent as first producer)
- Desktop automation baseline (Eigent as reference impl)
- VPS-side Vault999 anchoring (Eigent as testbed)

---

## Security Model

| Layer | Protection | Floor |
|-------|------------|-------|
| Transport | TLS 1.3 | F1 (integrity) |
| Auth | Token + HMAC | F11 (authority) |
| Scope | Session-bound | F1 (reversibility) |
| Execution | Sandbox + audit | F9 (anti-hantu) |
| Verification | Vault999 chain | F11 (audit) |

---

## Contrast: Eigent vs Traditional RPA

| Aspect | Traditional RPA | Eigent + arifOS |
|--------|-----------------|-----------------|
| **Governance** | Business rules | 13 Floors constitutional |
| **Audit** | Log files | Merkle-chained Vault999 |
| **Reversibility** | Manual rollback | F1-enforced undo |
| **Safety** | Hardcoded limits | ASI Heart simulation |
| **Verdict** | Pass/fail | SEAL/SABAR/VOID/HOLD |

---

## Open Questions

1. **Latency Budget**: What is the max acceptable latency for Eigent round-trip? (Target: <2s)
2. **Fallback Chain**: If Eigent VPS is unreachable, does arifOS degrade gracefully or HOLD?
3. **Multi-Desktop**: Can Eigent control multiple desktops (swarm), or single instance only?

---

## Integration Example

```yaml
# arifOS → Eigent workflow
session:
  intent: "Research competitor pricing"
  
stages:
  000_INIT:    { tool: arifos.init,    actor: user }
  111_SENSE:   { tool: arifos.sense,   evidence: [web, market] }
  333_MIND:    { tool: arifos.mind,    hypotheses: 3 }
  666_HEART:   { tool: arifos.heart,   stakeholders: [user, competitors] }
  888_JUDGE:   { tool: arifos.judge,   verdict: SEAL }
  
execution:
  999_FORGE:   { 
    tool: arifos.forge,
    target: "eigent.vps.arif-fazil.com",
    action: "browser_automation",
    scope: "read_only",
    urls: ["competitor1.com/pricing", "competitor2.com/pricing"]
  }
  
seal:
  vault: VAULT999
  chain_hash: "sha256:..."
```

---

> [!IMPORTANT]
> Eigent represents **The Body** (Ω) of arifOS—the execution substrate. Without the constitutional mind (Δ) and soul (Ψ) anchoring every action, it would be mere automation. With them, it becomes **governed agency**.

---

**Related:** [[Roadmap]] | [[Concept_Architecture]] | [[Horizon_2_Swarm]] | [[Agents-and-AAA-Architecture]]
