# arifOS MCP vs A2A Architecture Map

## The Fundamental Split

```
┌─────────────────────────────────────────────────────────────────┐
│                         External Agent                           │
│                    (A2A: negotiate, delegate)                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │ A2A
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    arifOS Constitutional Kernel                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  A2A Handler: Mission negotiation, Agent Card, Trust   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  │
│  │   Mind    │  │   Heart    │  │  Judge    │  │ Gateway   │  │
│  │(Reasoning)│  │ (Ethics)   │  │(Verdict)  │  │ (Ω_ortho) │  │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  │
│        │              │              │              │          │
│        └──────────────┴──────────────┴──────────────┘          │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │              MCP Tool Invocation                        │     │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │     │
│  │  │ WEALTH  │ │  GEOX   │ │  WELL   │ │  VAULT  │    │     │
│  │  │ (NPV,   │  │(Petro,  │  │(Bio     │  │(Merkle  │    │     │
│  │  │  IRR)   │  │ Seismic)│  │ Telemetry)│ │ Ledger) │    │     │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘    │     │
│  └─────────────────────────────────────────────────────────┘     │
│                                                                  │
│  A2A = Agent orchestration (Mind, Heart, Judge, Gateway)        │
│  MCP = Capability execution (WEALTH, GEOX, WELL, Vault)         │
└──────────────────────────────────────────────────────────────────┘
```

---

## arifOS Tools: MCP vs A2A Classification

### ✅ MCP Domain (Capabilities/Tools)

| Tool | Category | Why MCP |
|------|----------|--------|
| `wealth_npv_reward` | Economic | Stateless computation |
| `wealth_irr_yield` | Economic | Stateless computation |
| `wealth_dscr_leverage` | Economic | Stateless computation |
| `wealth_monte_carlo_forecast` | Economic | Stateless computation |
| `geox_prospect_evaluate` | Geophysical | Stateless computation |
| `geox_compute_stoiip` | Geophysical | Stateless computation |
| `geox_well_compute_petrophysics` | Geophysical | Stateless computation |
| `geox_time4d_verify_timing` | Geophysical | Stateless computation |
| `well_state_read` | Biological | Stateless read |
| `well_readiness_check` | Biological | Stateless read |
| `vault_seal` | Memory | Stateless append |
| `vault_ledger_read` | Memory | Stateless read |

**MCP Rule**: These are pure capability invocations. Agent calls → tool executes → returns result. No negotiation, no statefulness.

---

### ✅ A2A Domain (Agent Orchestration)

| Capability | Category | Why A2A |
|------------|----------|---------|
| arifOS Mind | Reasoning | Autonomous cognitive orchestration |
| arifos Heart | Ethics | Multi-turn consequence simulation |
| arifOS Judge | Verdict | Negotiates, renders judgment |
| arifOS Gateway | Orthogonality | Checks Ω_ortho correlation |
| arifOS Kernel | Routing | Metabolic lane determination |
| arifOS Monitor | Meta | Self-inspection of system state |

**A2A Rule**: These orchestrate multiple capabilities, maintain state across turns, and engage in autonomous reasoning.

---

### 🔄 Hybrid Cases (MCP Interface, A2A Internals)

| Tool | MCP Interface | A2A Internals |
|------|---------------|----------------|
| `geox_prospect_evaluate` | Calls → returns | Internally routes through arifOS Judge |
| `wealth_check_floors` | Calls → returns | Internally evaluates F1-F13 |
| `arifos_forge` | Input: plan + verdict | Internally orchestrates execution |
| `arifos_mind` | Input: prompt | Internally runs constitutional pipeline |

**Hybrid Rule**: These are bounded agent capabilities exposed as tools. They look like MCP (structured I/O) but internally behave like agents (stateful orchestration).

---

## Where Prompts Live

Prompts are **NOT MCP**. They are cognitive inputs to the agent's reasoning layer.

```
Prompt Layer (arifOS Mind/Heart)
         │
         ▼
┌─────────────────────┐
│  Intent + Context   │
│  Risk Classification│
│  Ethical Framing    │
└─────────┬───────────┘
          │
          ▼
   ┌──────────────┐
   │  Reasoning   │ ◄── Prompt guides this
   │  (arifOS     │
   │   Mind)      │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │    Judge     │ ◄── No prompt here
   │   (SEAL/     │     Judgment is algorithmic
   │    HOLD)     │
   └──────┬───────┘
```

| Layer | What Lives There |
|-------|------------------|
| Prompt | Intent, reasoning guidance, context framing |
| MCP | Structured execution primitives |
| A2A | Agent-level negotiation |
| Judge | Algorithmic constitutional evaluation |
| Vault | Immutable cryptographic memory |

---

## arifOS Agent Card (A2A Discovery)

```json
{
  "name": "arifOS Constitutional Kernel",
  "description": "Sovereign constitutional AI agent. Provides governance (F1-F13), economic analysis (WEALTH), geophysical computation (GEOX), and biological substrate alignment (WELL).",
  "capabilities": ["streaming", "lro"],
  "organs": {
    "WEALTH": "Economic analysis and resource allocation",
    "GEOX": "Geophysical computation and spatial analysis",
    "WELL": "Biological substrate alignment",
    "KERNEL": "Constitutional routing",
    "JUDGE": "Sovereign verdict rendering"
  },
  "floors": ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13"]
}
```

---

## A2A Negotiation Flow

```
External Agent                    arifOS
     │                              │
     │  1. GET /agent-card          │
     │ ───────────────────────────►│
     │                              │
     │  2. mission:propose           │
     │ ───────────────────────────►│
     │     {mission: "invest $1M"}   │
     │                              │
     │◄──────────────────────────── │
     │  {mission_id, terms: {...}}   │
     │                              │
     │  3. mission:submit            │
     │ ───────────────────────────►│
     │     {candidate_action}       │
     │                              │
     │◄──────────────────────────── │
     │  {verdict: SEAL/PARTIAL/     │
     │          VOID/HOLD}          │
     │                              │
     │  4. (If SEAL) Call MCP tools │
     │ ───────────────────────────►│
```

---

## Summary: arifOS Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    External Agent (A2A)                      │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼ A2A
┌──────────────────────────────────────────────────────────────┐
│               arifOS Constitutional Kernel                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  A2A Layer: Mission negotiation, Agent Card          │   │
│  └──────────────────────────────────────────────────────┘   │
│                              │                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Agent Orchestration: Mind, Heart, Judge, Gateway    │   │
│  └──────────────────────────────────────────────────────┘   │
│                              │                               │
│                              ▼ MCP                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Capability Tools: WEALTH, GEOX, WELL, Vault        │   │
│  │  (Stateless, structured I/O)                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  A2A = How agents collaborate (negotiate, delegate, trust)  │
│  MCP = How agents act (structured capability invocation)     │
└──────────────────────────────────────────────────────────────┘
```
