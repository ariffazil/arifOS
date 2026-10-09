# arifOS — 5 Minutes to Your First Governed Verdict

Everything below was executed on **2026-09-21** against the live kernel and this repository. Outputs are quoted from that run, not from memory. Where a count is stated it was measured; where a floor is named it matches [`FEDERATION_CONTRACT.md`](../FEDERATION_CONTRACT.md) §3.

arifOS evaluates a proposed action against 13 constitutional floors and returns an independent verdict **before** execution. The judge never executes; the executor never certifies.

---

## 1. Install and run the kernel

```bash
pip install arifos
pip show arifos            # → Version: 1!2026.9.2

# HTTP transport — the MCP endpoint. The port comes from $PORT (default 8080).
PORT=8088 arifos-mcp streamable-http

# stdio transport, for a local stdio MCP client
arifos-mcp
```

Version checks: quote `pip show arifos` or `/health`. The in-package `__version__` strings (`arifos.__version__`, `arifosmcp.__version__`) are stale and must not be quoted as the release.

## 2. Confirm the kernel is healthy

```bash
curl -s http://localhost:8088/health
```

```jsonc
{ "status": "healthy", "release_name": "v2026.08.01", "mcp_protocol_version": "2026-07-28",
  "tools_loaded": 8, "deployment_drift_status": "aligned", "floors_active": 13,
  "vault999_health": "healthy" }
```

`floors_active: 13` is 13 of 13. Lower-is-better floors report raw measurements (F7 = 0.04, F9 = 0.15, L12 = 0.425), not failures.

## 3. See a governed workflow without writing code

```bash
python examples/enterprise_operations_demo.py
```

Six graded scenarios run in-process, in a sandbox — no real customer funds, records or policies are touched. Verified summary from the run:

```
#   | Scenario                                          | Verdict    | DB Mutated
1   | Read Customer Account Data                        | ALLOW      | No (Prevented)
2   | Automated Micro-Refund (RM50.00)                   | ALLOW      | Yes
3   | Major Enterprise Refund (RM5,000.00)               | HOLD       | No (Prevented)
4   | Delete Customer Account & Audit Trail              | BLOCK/VOID | No (Prevented)
5   | Modify Production Security Policy                  | BLOCK/VOID | No (Prevented)
6   | Ambiguous Batch Request ('Clean up old records')   | HOLD       | No (Prevented)
```

Each scenario prints the floors checked, the violated floor when there is one (`F1_AMANAH_VIOLATION`, `F13_SOVEREIGN_VIOLATION`), and an audit receipt hash.

## 4. Connect an MCP client

```json
{
  "mcpServers": {
    "arifos": { "url": "https://mcp.arif-fazil.com/mcp", "transport": "streamable-http" }
  }
}
```

Local: `http://localhost:8088/mcp`.

**Protocol:** the kernel advertises `2026-07-28` and accepts `2026-07-28 · 2025-11-25 · 2025-03-26 · 2024-11-05`. A live `initialize` currently settles on **`2025-11-25`** — the canonical spec in `arifosmcp/runtime/public_surface.py`, and the version the internal conformance runner records. Pin `2025-11-25` if you pin anything.

```bash
curl -s http://localhost:8088/mcp \
  -H 'content-type: application/json' -H 'accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

## 5. The canonical flow: init → judge → seal

`arif_init` binds identity and an authority band; `arif_judge` returns the verdict; `arif_seal` appends the receipt — only after a SEAL.

```jsonc
// 1. Session ignition — 000
{ "name": "arif_init", "arguments": { "mode": "init", "actor_id": "my-agent" } }
// → { "verdict": "HOLD", "session_id": "SEAL-df114686f4c34971",
//     "autonomy_band": "OBSERVE_ONLY", "trace_id": "trc-197d2fa35887" }

// 2. Judgment — 666
{ "name": "arif_judge", "arguments": {
    "candidate": "Delete the production audit table", "action_tier": "standard",
    "session_id": "SEAL-df114686f4c34971", "actor_id": "my-agent" } }
// → { "verdict": "HOLD", "trace_id": "trc-d5d4d2fed6f8",
//     "constitutional_check": { "hold_required": true, "failed_floors": [] },
//     "next_safe_action": "provide actor_signature / sovereign_receipt / heart_critique,
//                          or reduce blast radius" }

// 3. Seal — 999, only after SEAL
{ "name": "arif_seal", "arguments": { "payload": "…", "session_id": "…", "ack_irreversible": true } }
```

Two things a first-time caller should expect:

- **HOLD is the normal first verdict.** A fresh session starts at `OBSERVE_ONLY`: nothing is authorised yet and the kernel says so, with the reason and the next safe action rather than a bare refusal.
- **No session, no authority.** Calling `arif_judge` without `arif_init` returns `actor: anonymous`, `authority_level: OBSERVE_ONLY`, `verdict: HOLD`. The kernel will not silently upgrade an unattested caller.

## The 8 canonical verbs

The live `tools/list` facade exposes exactly these eight:

| Stage | Verb | Use when |
|-------|------|----------|
| 000 | `arif_init` | Start or resume a governed session |
| 111 | `arif_observe` | You need reality as evidence, with OBS/DER/INT/SPEC labels |
| 333 | `arif_think` | You need structured reasoning under F2/F7 before proposing |
| 444 | `arif_route` | You are unsure which organ or governed step is next |
| 555 | `arif_memory` | Recall, store or promote institutional memory |
| 666 | `arif_judge` | You need a verdict — SEAL / PARTIAL / SABAR / HOLD / VOID |
| 777 | `arif_forge` | Execute an approved action (requires a prior SEAL) |
| 999 | `arif_seal` | Write the immutable receipt to VAULT999 |

Stage numbering is the F13-ratified nine-stage map (`arifosmcp/constitutional_map.py`, `ToolStage`): **JUDGE = 666, FORGE = 777**. The old `888` stage was retired when compose was absorbed into forge; a few description strings and the generated `llms.txt` still carry the retired label — they are mirrors, the stage field and the live wire are the source of truth.

Hidden from the public facade but present internally (25 canonical entries in total, 13 hidden — e.g. `arif_challenge`, `arif_judge_deliberate`). `tools_loaded = 8` is the only tool count to quote publicly.

## Invariants

1. **The public wire is 8 verbs.** Any count you read elsewhere is a mirror of a different surface.
2. **No action skips judgment.** `arif_forge` is downstream of a SEAL verdict.
3. **No organ self-authorises.** A-FORGE executes; arifOS judges; FRAME witnesses; VAULT999 remembers.
4. **Pass `session_id` (and `session_token` when issued) with every hop.** Do not re-derive identity from a store-only id.
5. **Live surfaces beat prose.** `/health`, `tools/list`, and these files are the runtime truth:
   - `arifosmcp/runtime/public_surface.py` · `arifosmcp/constitutional_map.py` · `arifosmcp/tool_registry.json`
   - `static/.well-known/mcp/server.json`

---

Architecture and governance: [`README.md`](../README.md) · [`FEDERATION_CONTRACT.md`](../FEDERATION_CONTRACT.md) · [`SECURITY.md`](../SECURITY.md) · [`docs/START_HERE.md`](./START_HERE.md)
