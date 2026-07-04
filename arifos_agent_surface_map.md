# arifOS Agent Surface Map

The canonical interface specification for arifOS Kernel. This bridges human-readable doctrine and machine-callable contracts.

## 1. MCP Tools (gated actions)
- **`arifos_init`**: Start session, anchor identity, and set authority level.
- **`arifos_observe`**: Ground decisions in reality (search, URL fetch, vitals).
- **`arifos_think`**: Structured reasoning, plan generation, and ethics critique.
- **`arifos_route`**: Metabolic intent-to-organ routing.
- **`arifos_judge`**: Constitutional verdict gate (SEAL/HOLD/VOID).
- **`arifos_act`**: Reversible action staging and validation.
- **`arifos_seal`**: Immutable VAULT999 anchoring.

## 2. MCP Resources (read-only doctrine/context)
- **`arifos://doctrine/floors`**: Constitutional floor index (F1–F13).
- **`arifos://registry/organs`**: Live organ metadata, ports, and boundaries.
- **`arifos://state/latest`**: Live telemetry and system state.
- **`arifos://receipts/latest`**: Recent sealed execution receipts.
- **`arifos://mcp/surface-map`**: This surface map.

## 3. A2A Agent Card
```yaml
agent_name: arifOS Kernel
role: constitutional governance router
exposes_internal_tools: false
modalities:
  - text
  - structured_json
  - receipt_summary
authority:
  default: observe_only
  mutation: requires_explicit_f13
```

## 4. FastMCP Build Rules
- **Strict schemas only**: Input schema must enforce `.strict()` (`additionalProperties: false`).
- **Boring tool descriptions**: Plain, action-oriented, zero poetic fluff.
- **Explicit freshness**: Outputs must include `verified_at`, `evidence_layer`, and `ttl_seconds` to reject stale data.
