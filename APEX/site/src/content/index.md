# arifOS: Constitutional AI Governance

arifOS is a thermodynamic constitutional framework for AI governance, built on the 13 LAWS (9 Floors + 2 Mirrors + 2 Walls). It implements a dual-hemisphere architecture with AGI (Δ) for logic and ASI (Ω) for care, unified under APEX (Ψ) sovereignty.

## How It Works (60 seconds)

Your query enters → Processed through 5 MCP tools (000_init, 222_reason, 555_validate, 888_audit, 999_seal)
System records → Seals outcome in VAULT999, an immutable ledger you can audit later.

### How It Runs (MCP Substrate)
- arifOS is implemented as an MCP server exposing tools, resources, and prompts via the Model Context Protocol.
- It is model-agnostic: any compliant LLM host (ChatGPT-style app, Claude-style desktop, IDE, or your own orchestrator) can connect over MCP without code changes.
- All capabilities are defined with JSON Schema contracts and strict uncertainty bounds (Ω₀), so different models can reason over the same governance layer.

### arifOS Governance MCP Tools

| Tool | Role |
| ------------ | ----------------------------------------------------------- |
| 000_init | Initialize a new governance session (context & identities). |
| 222_reason | Cognitive processing and truth assessment. |
| 555_validate | Empathy and stakeholder impact assessment. |
| 888_audit | Final governance verdict (SEAL / SABAR / VOID / HOLD). |
| 999_seal | Cryptographically seal and log the decision in VAULT999. |

Full schemas, auth scopes, and safety notes are documented in the arifOS MCP Capability Catalog.

### Sovereign in the Loop
- arifOS explicitly models four roles: Host (LLM app), Client (MCP adapter), Server (arifOS governance engine), and Sovereign (human 888 Judge).
- The Sovereign always has final veto; irreversible actions require human approval and a sealed audit record (VAULT999).

Every arifOS MCP deployment is scored with an arifOS Forge Index (AFI), a 0–1 metric of spec alignment, universality, security, auditability, and composability. Higher AFI means a more "forged", less brittle governance substrate.