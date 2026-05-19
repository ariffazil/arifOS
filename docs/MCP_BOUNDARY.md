# MCP Boundary Doctrine

**Version:** 2026.05.19-KANON  
**Purpose:** Canonical explanation of where MCP ends and arifOS begins.

---

## What MCP Is

The **Model Context Protocol (MCP)** is a JSON-RPC-based application protocol for context exchange, capability discovery, tool/resource/prompt access, and related interaction primitives.

It provides:
- **Lifecycle management** (`initialize`, capability negotiation)
- **Server primitives** (tools, resources, prompts)
- **Client primitives** (sampling, elicitation, logging)
- **Transport abstraction** (stdio, Streamable HTTP, SSE)

It does **not** provide:
- Intelligence, judgment, or reasoning
- Memory, truth verification, or authority
- Constitutional enforcement or human oversight
- Immutable audit or cryptographic attestation

> **MCP is the standardized context-and-tool protocol layer. It transports capability. It does not create judgment.**

---

## What arifOS Adds

arifOS wraps the MCP boundary in **constitutional steel**:

| Capability | MCP's Protection | arifOS's Protection |
|------------|------------------|---------------------|
| Poisoned tool description | None | Tool registry hash, schema validation, `tool_registry_hash` |
| Hidden side effects | Human-in-the-loop recommendation | `ack_irreversible`, floor enforcement (F1–F13) |
| Unauthorized execution | OAuth 2.1 (if configured) | Session binding, identity boundary, 888_JUDGE |
| Audit gap | None | VAULT999 append-only ledger, `judge_state_hash` |
| Cross-organ contradiction | None | Contradiction scanners, evidence synthesis, tri-witness consensus |

---

## The Boundary Diagram

```text
┌─────────────────────────────────────────┐
│  LLM Host / Client                      │
│  (Claude, Kimi, ChatGPT, Cursor, etc.)  │
└─────────────────┬───────────────────────┘
                  │ MCP Transport
                  │ (JSON-RPC / stdio / HTTP)
┌─────────────────▼───────────────────────┐
│  MCP Servers / Federation Organs        │
│  • arifOS (governance kernel)           │
│  • GEOX (earth intelligence)            │
│  • WEALTH (capital intelligence)        │
│  • WELL (vitality intelligence)         │
│  • A-FORGE (execution metabolism)       │
│  • AAA (control plane surface)          │
└─────────────────┬───────────────────────┘
                  │ Internal Protocol
┌─────────────────▼───────────────────────┐
│  arifOS Constitutional Kernel           │
│  • F1–F13 Floor Enforcement             │
│  • 888_JUDGE Verdict Engine             │
│  • 999_VAULT Immutable Ledger           │
│  • Identity & Session Binding           │
└─────────────────┬───────────────────────┘
                  │ Human Authority
┌─────────────────▼───────────────────────┐
│  APEX — Arif (Human Sovereign)          │
│  • Final veto (F13)                     │
│  • Constitutional witness               │
│  • Scar-weight authority                │
└─────────────────────────────────────────┘
```

**MCP lives at the membrane between LLM host and federation organs. arifOS lives behind the membrane. APEX stands above it.**

---

## The Three Primitives in arifOS

| MCP Primitive | arifOS Meaning |
|---------------|----------------|
| **Tools** | Actuators: `arif_judge_deliberate`, `geox_subsurface_generate_candidates`, `wealth_synthesize`, `arif_forge_execute` |
| **Resources** | Evidence surfaces: VAULT999 receipts, schemas, canonical docs, cross-domain summaries |
| **Prompts** | Governance rituals: constitutional review patterns, few-shot floor workflows, operator checklists |

MCP only requires that tools declare a `name`, `description`, and `inputSchema`. It does not care what happens inside `arif_judge_deliberate`. The 13-floor logic, entropy calculations, contradiction scans — **that is all arifOS.**

---

## Approved vs Void Claims

| Claim | Verdict |
|-------|---------|
| "MCP-connected agentic system" | ✅ Approved |
| "Governed intelligence architecture" | ✅ Approved |
| "APEX-governed agentic intelligence infrastructure with MCP transport" | ✅ Approved |
| "AGI-level constitutional intelligence" | ⚠️ Hold — not proven by protocol alone |
| "ASI via MCP" | ❌ Void — architecture does not imply superintelligence |

---

## Relation to AAA

The **AAA** triad governs the MCP boundary itself:

- **Abstraction (Inti):** The stable schemas that let LLMs use federation organs without knowing internals.
- **Attestation (Saksi):** The proof that the discovered surface is the governed surface — session binding, hashes, receipts.
- **Abduction (Teka-Sebab):** The inferential work performed by domain organs (GEOX, WEALTH) over evidence transported by MCP.

See `/root/AAA/AAA_DOCTRINE.md` for the full triad.

---

**KANON LOCK: arifOS v2026.05.19**  
**DITEMPA BUKAN DIBERI — Forged, not given.** 🔥
