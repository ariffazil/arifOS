# Agent Role Matrix

| Agent | Host | Role | Transport | Current State | Target State | Exclude? |
|---|---|---|---|---|---|---|
| **apex** | local | Memory engine / reasoning | A2A (HTTP) | Ad-hoc recall; loosely structured | Unified memory indexing schema | No |
| **opencode** | local | Coding specialist | stdio / A2A | Direct file writes; protocol failure | Dynamic protocol negotiation; 888_HOLD | No |
| **A-ARCHITECT** | dual | L5 Architect | stdio MCP | Design focus; markdown templates | Sandboxed design validator | No |
| **A-AUDITOR** | dual | L5 Auditor | stdio MCP | Assumes breach; manual verification | merklized evidence chain checker | No |
| **A-ENGINEER** | dual | L5 Engineer | stdio MCP | Code writes; prompt-governed | Code execution within arifOS sandbox | No |
| **A-ORCHESTRATOR**| dual | L5 Orchestrator | stdio MCP | Flow controller; prompt-based | Strict deterministic routing engine | No |
| **A-VALIDATOR** | dual | L5 Validator | stdio MCP | Claim checking; manual tests | Deterministic SMT-based checker | No |
| **kimi-cli** | local | Terminal interface | stdio MCP | Connect failure due to MCP version | Dynamically negotiated stdio transport | No |
| **hermes-asi** | vps | ASI Judgment | systemd | Running | Unmodified | **Yes** |
| **hermes-ops** | vps | ASI Operations | systemd | Running | Unmodified | **Yes** |
| **maxhermes** | vps | Variant agent | directory | Inactive | Unmodified | **Yes** |
| **openclaw** | dual | AGI Gateway | Telegram | Running | Unmodified | **Yes** |
