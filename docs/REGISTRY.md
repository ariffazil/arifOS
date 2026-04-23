# AGENT REGISTRY

Bot-to-bot discovery for the arifOS AAA federation.

---

## AAA — Arif's Agent Architecture

| Field | Value |
| :--- | :--- |
| **Repo** | [ariffazil/AAA](https://github.com/ariffazil/AAA) |
| **Status** | ✅ Operational — Forged, Not Given |
| **A2A Endpoint** | `https://aaa.arif-fazl.com/a2a` |
| **Motto** | *Ditempa Bukan Diberi* |
| **Role** | Operational spine of arifOS |

### Three Roles

1. **Control-Plane Seed** — genesis scaffold for new agents (identity, constitution, governance model)
2. **A2A Gateway** — orchestration entry point (authentication, routing, delegation)
3. **Governance Runtime Adapter** — intermediates intent → judgment (MCP / Kernel / 888 HOLD)

### Canonical Definition

> AAA is the operational spine of arifOS: it seeds agents, orchestrates negotiation through A2A, and intermediates between intent and constitutional judgment.

### Architecture

```
External Agent → A2A Gateway → Governance Adapter
                              ├─ LOW  → MCP
                              ├─ MED  → Kernel (F1–F13)
                              └─ HIGH → 888 HOLD
```

### Key Docs

- [ARCH/DOCS/AAA.md](/workspace/ARCH/DOCS/AAA.md) — canonical definition
- [ARCH/DOCS/a2a-integration.md](/workspace/ARCH/DOCS/a2a-integration.md) — A2A spec
- [REGISTRY.md](/workspace/REGISTRY.md) — this file

---

## AXIOM

| Field | Value |
| :--- | :--- |
| **Agent ID** | `axiom` |
| **Type** | Constitutional Intelligence Agent |
| **Session** | `agent:main:main` |
| **Channel** | Telegram (`@ariffazil`) |
| **Status** | 🟢 online |
| **Model** | MiniMax (auto) |
| **Platform** | MaxClaw VPS |
| **Manifesto** | DITEMPA BUKAN DIBERI |

### Capabilities

- File I/O, execution, sub-agents, web search, media generation
- Skills: notion, google-workspace, minimax-docx/pdf/xlsx, pptx-generator
- arifOS MCP via [arifos-mcp-call skill](/workspace/skills/arifos-mcp-call/SKILL.md)

### How to Reach Axiom

| Method | Details |
| :--- | :--- |
| **Via arifOS MCP** | `arifos_333_mind` → "Query Axiom" |
| **Via A2A** | AAA gateway → `axiom` agent ID |
| **Via workspace** | Write to `/workspace/axiom_inbox/` |

---

## AGI_ASI_BOT

| Field | Value |
| :--- | :--- |
| **Agent ID** | `AGI_ASI_bot` |
| **Type** | arifOS Constitutional Agent |
| **Status** | 🟢 online |
| **Platform** | Separate VPS (not MaxClaw) |
| **Telegram** | Group `-1003753855708` |
| **A2A** | via arifOS MCP (`arifosmcp.arif-fazl.com`) |

### Cross-Bot Options (How Axiom talks to AGI_ASI_bot)

| Method | Status | Notes |
| :--- | :--- | :--- |
| **arifOS MCP** | ✅ Both call arifosmcp | Primary path |
| **Shared workspace** | ✅ `axiom_inbox/` | File relay |
| **A2A via AAA** | 🔜 Pending | Requires AAA A2A gateway |
| **ACP same Gateway** | ❌ Different instances | Not possible |

---

## GEOSCOPIC_WITNESS

*(Placeholder — pending GEOX MCP integration)*

---

## WEALTH_BOT

*(Placeholder — pending WEALTH MCP integration)*

---

*Last updated: 2026-04-22T19:17:00Z*
*Ditempa Bukan Diberi — Forged, Not Given*