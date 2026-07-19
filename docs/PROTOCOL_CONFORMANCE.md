# 🔒 arifOS — Protocol Conformance

> **Layer:** L1 ROOT · **Role:** Constitutional Kernel
> **Protocols:** MCP Server, JSON-RPC 2.0, SSE, Streamable HTTP, A2A Gateway, NATS, Well-Known, SEP-2127

## Supported Protocols

| Protocol | Status | Detail |
|----------|--------|--------|
| MCP Server | ✅ CONFORMANT | 8 canonical tools, tools/list, resources/list, prompts/list |
| JSON-RPC 2.0 | ✅ CONFORMANT | All MCP endpoints respond to JSON-RPC 2.0 |
| SSE | ✅ CONFORMANT | Legacy SSE transport at /sse |
| Streamable HTTP | ✅ CONFORMANT | POST /mcp with session management |
| A2A Gateway | ⚠️ PARTIAL | Gateway routes but no agent card serving |
| NATS | ✅ CONFORMANT | Event bus for 888_HOLD, cooling events |
| Well-Known | ✅ CONFORMANT | /.well-known/mcp/server.json |
| SEP-2127 | ✅ CONFORMANT | MCP server card endpoint |
| CloudEvents | ❌ GAP | No CloudEvents envelope for inter-organ events |
| OpenTelemetry | ❌ GAP | No OTel SDK wired (traces/metrics not exported) |

## MCP Tool Surface
- **Canonical tools:** 8 (arif_init, arif_observe, arif_think, arif_route, arif_memory, arif_judge, arif_forge, arif_seal)
- **ZEN-8 surface:** 8 public, 0 phantoms, 100% envelope compliance

## Gaps
1. **CloudEvents:** Events emitted to NATS don't use CloudEvents envelope
2. **OpenTelemetry:** No trace/metric export to OTel Collector
3. **A2A Agent Card:** Kernel should serve its own agent card per A2A spec

*DITEMPA BUKAN DIBERI*
