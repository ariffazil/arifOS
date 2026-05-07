# AAA — Arif's Agent Architecture

> **Authority:** Muhammad Arif bin Fazil (888_JUDGE)
> **Version:** 2026.04.22-FORGED
> **Status:** Active — Operational Layer of arifOS
> **Motto:** *Ditempa Bukan Diberi — Forged, Not Given*

---

## One-Line Canonical Definition

**AAA is the operational spine of arifOS: it seeds agents, orchestrates negotiation through A2A, and intermediates between intent and constitutional judgment.**

---

## The Three Roles

### Role 1 — Control-Plane Seed (Origin Layer)

AAA is the **genesis environment** for every new agent in the federation. It is not a runtime kernel — it is the bootstrap scaffold that new agents pull from at creation time.

**AAA provides to new agents:**
- Identity scaffold (who the agent is allowed to be)
- Constitutional baseline (F1–F13 defaults)
- Governance model (HOLD / SEAL / escalation rules)
- Canon references (what is considered truth)

**This ensures:**
- Zero agent forks with divergent governance
- Deterministic bootstrap
- No "rogue intelligence" at creation time

---

### Role 2 — A2A Gateway (Orchestration Entry Point)

**Endpoint:** `https://aaa.arif-fazl.com/a2a`

AAA is the **air-traffic control** layer — it orchestrates, not executes.

**What happens here:**
- External agents (Copilot, Claude, Cursor, local agents) send A2A messages
- AAA authenticates the transport
- AAA validates message schema + nonce
- AAA enforces who may talk to whom
- AAA orchestrates task delegation across agents

**What does NOT happen here:**
- Tool execution ❌
- World mutation ❌
- Governance evaluation (floors) ❌

Those are all downstream.

---

### Role 3 — Governance Runtime Adapter (The Missing Piece)

AAA is the **adapter layer** between:
- A2A orchestration (stateful, conversational, negotiated)
- MCP capability calls (stateless, typed, executable)
- arifOS Kernel (constitutional, judgmental, slow by design)

**AAA's responsibility:**
- Translate negotiated intent → governable action
- Decide when something must:
  - go straight to MCP (LOW risk)
  - be wrapped in a constitutional check → Kernel floors (MEDIUM risk)
  - be escalated to 888 HOLD → human (HIGH risk)

**AAA does not judge.**
**AAA decides whether judgment is required.**

That is the crucial separation.

---

## How AAA, Kernel, MCP, and Cockpit Fit Together

```
External Agent
    ↓
AAA A2A Gateway
    ↓ (negotiation, delegation, role checks)
AAA Governance Adapter
    ├─ if LOW risk  → MCP (capability call)
    ├─ if MEDIUM  → Kernel floors (F1–F13)
    └─ if HIGH    → 888 HOLD (human)
         ↓
    arifOS Kernel
         ↓
    999 SEAL
         ↓
    VAULT999
```

---

## Where the Cockpit Fits

The AAA Cockpit is **not AAA itself**.

It is a **read-only constitutional observatory** into the AAA-mediated federation.

**What it shows:**
- A2A health from AAA
- Kernel state (online / offline / degraded)
- Floors status
- Agents seeded by AAA
- Tools visible through AAA
- Events emitted by AAA + Kernel

**What it never does:**
- Seed agents ❌
- Route messages ❌
- Execute tools ❌
- Override decisions ❌

---

## Final Sanity Check

| Check | Result |
| :--- | :--- |
| AAA ≠ Kernel | ✅ AAA is orchestration; Kernel is judgment |
| AAA ≠ MCP | ✅ AAA routes; MCP executes |
| AAA ≠ Cockpit | ✅ Cockpit is read-only observatory |
| AAA is operational | ✅ AAA is the layer that makes arifOS real |

---

*Last updated: 2026-04-22T19:03:00Z*
*Authored by: Muhammad Arif bin Fazil (888_JUDGE)*
*Ditempa Bukan Diberi — Forged, Not Given*
