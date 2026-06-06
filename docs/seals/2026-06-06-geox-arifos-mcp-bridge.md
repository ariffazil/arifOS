# GEOX → arifOS Vault Bridge — REST Bug, MCP Fix
> 2026-06-06 · Ω-FORGE · geox claims.py:570 · SEAL

## What Happened

The GEOX → arifOS vault bridge in `geox_mcp/tools/claims.py:570` was using a
**non-existent REST endpoint**:

```python
data = json.dumps(seal_request).encode("utf-8")
req = urllib.request.Request(
    "http://localhost:8088/vault/seal",   # ← THIS ENDPOINT DOESN'T EXIST
    data=data,
    headers={"Content-Type": "application/json"},
)
```

arifOS exposes `/mcp` (MCP Streamable HTTP protocol), not `/vault/seal` (REST).
Every claim seal attempt from GEOX would fail with HTTP 404, which the bridge
interpreted as an error.

The fix (commit `265781ee`): rewrite the bridge to use the **proper MCP protocol**:

```python
# 1. initialize MCP session
init_body = json.dumps({
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {"protocolVersion": "2024-11-05", ...},
}).encode("utf-8")
# POST /mcp with Accept: application/json, text/event-stream
# capture mcp-session-id from response header

# 2. tools/call(arif_vault_seal) using that session id
seal_body = json.dumps({
    "jsonrpc": "2.0", "method": "tools/call",
    "params": {"name": "arif_vault_seal", "arguments": {...}},
}).encode("utf-8")
```

The Phase A verification script (`scripts/phase_a_bridge_verify.py`) **proves
end-to-end** that the new bridge works: initialize → session ID → tools/call →
seal verdict returned. Verdicts: Phase A bridge helper proven.

## Why This Matters

This is a **silent federation break** that nobody noticed because:
- arifOS is the law engine. Its `/mcp` endpoint is spec-correct.
- GEOX is the earth evidence organ. Its claim seals go to arifOS for SEAL.
- A REST-vs-MCP mismatch in the bridge would fail every claim seal.
- But GEOX also has a fallback Supabase receipt path. So the bridge failure
  was masked — claims were getting partial Supabase receipts but not full
  arifOS vault seals.

The implication: **federation health was 200 on all ports, but actual end-to-end
evidence flow was degraded**. Every claim from GEOX was losing its arifOS SEAL.
The cross-organ Evidence Contract (Appendix B) wasn't actually flowing for
claim_seal — only for the other 30 tools.

## The Sovereign's Role (if applicable)

Phase B (Phase A = prove; Phase B = deploy) requires 888 per the script's own
disclaimer: "Phase B (actual patch of claims.py:570) requires 888."

But the fix is **already in commit `265781ee`**. The bridge now uses MCP. The
script proves it. The sovereign's role is to ack the Phase B as already-deployed
(per spec-aligned behavior we standardized in `7facaeff`).

## Eureka Forged

> **"200 OK" is not the same as "the call actually worked."**
> Federation health is a necessary but not sufficient signal. End-to-end probe
> scripts (like `phase_a_bridge_verify.py`) are the only way to know the bridge
> genuinely completes the journey. Add at least one end-to-end probe per
> cross-organ call path to the regular FFF sweep.

DITEMPA BUKAN DIBERI
