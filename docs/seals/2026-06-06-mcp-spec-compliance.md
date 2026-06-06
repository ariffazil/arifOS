# MCP Spec Compliance — arifOS GET /mcp
> 2026-06-06 · Ω-FORGE · arifOS MCP runtime · SEAL

## What Happened

The MCP Streamable HTTP transport spec
(https://modelcontextprotocol.io/specification/2025-11-25/basic/transports) requires:

> "The server MUST either return `Content-Type: text/event-stream` in response to this HTTP
> GET, or else return HTTP 405 Method Not Allowed, indicating that the server does not offer
> an SSE stream at this endpoint."

Before this fix, arifOS GET `/mcp` returned **400** with a JSON-RPC error
`"Bad Request: Missing session ID"`. This is a spec violation: 400 is reserved for
malformed requests, not for "no SSE stream offered."

The fix mirrors the GEOX + WELL pattern: monkey-patch
`mcp.server.streamable_http.StreamableHTTPServerTransport._check_accept_headers` so
that on GET (when `is_json_response_enabled` is True, meaning no SSE offered), the
server returns 405 instead of 400.

## Why This Matters

The federation is **the** public MCP surface of arifOS. External clients (Cursor,
Claude Desktop, MCP Inspector) hit these endpoints. Wrong status codes cause:
- Confusing client errors (`Missing session ID` looks like a client bug, not a server
  protocol decision)
- Spec-compliance failures (Caddy, Cloudflare, and other intermediaries may proxy or
  rewrite based on status)
- Untestable contract drift (test suites asserting "200 on POST with Accept, 405 on
  GET" would fail)

The patch makes arifOS **spec-aligned** at the source level. Three other organs
(GEOX, WELL, AAA) were already spec-aligned.

## Live Status

| Organ | POST + Accept | GET | Spec |
|-------|---------------|-----|------|
| arifOS | 200 ✓ | 400 → **405** (next deploy) | source fixed in 7facaeff, live build predates patch |
| GEOX   | 200 ✓ | 405 ✓ | compliant |
| WEALTH | 200 ✓ | 200 (informational) | spec-allowed |
| WELL   | 200 ✓ | 405 ✓ | compliant |

The arifOS image rebuild is **F13 territory** per AGENTS.md ("Production deployment
without verified build + test pass"). Source patch in commit `7facaeff`; live deploy
awaits sovereign ack.

## Eureka Forged

> **The spec is the contract, not the README.**
> When a public surface is documented as "compliant with X" but the implementation
> emits 400 + JSON-RPC error on GET, the implementation is wrong, not the doc.
> Always verify against the canonical spec, not against behavior observed in
> production clients that have learned to work around the bug.

DITEMPA BUKAN DIBERI
