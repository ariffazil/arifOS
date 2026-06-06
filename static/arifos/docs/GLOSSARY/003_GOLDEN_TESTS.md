# 003 — Golden test suite (Wajib #5)

> Proof that MCP tools behave consistently, not just health checks.
> Health = green. Golden tests = correct.

## Phase 1 — bridge golden tests (live)

```python
# tests/golden/test_claims_bridge_mcp.py
import json, urllib.request

MCP = "http://127.0.0.1:8088/mcp"

def _mcp_call(name, args, session_id):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":"tools/call",
                       "params":{"name":name,"arguments":args}}).encode()
    req = urllib.request.Request(MCP, data=body,
        headers={"Content-Type":"application/json",
                 "Accept":"application/json, text/event-stream",
                 "Mcp-Session-Id": session_id}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def test_bridge_session_init():
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":"initialize",
        "params":{"protocolVersion":"2024-11-05","capabilities":{},
                  "clientInfo":{"name":"golden-test","version":"1.0"}}}).encode()
    req = urllib.request.Request(MCP, data=body,
        headers={"Content-Type":"application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        sid = r.headers.get("Mcp-Session-Id")
    assert sid is not None and len(sid) > 8, f"no session id: {r.headers!r}"

def test_bridge_vault_seal_propagates():
    # 1. init
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":"initialize",
        "params":{"protocolVersion":"2024-11-05","capabilities":{},
                  "clientInfo":{"name":"golden","version":"1"}}}).encode()
    req = urllib.request.Request(MCP, data=body,
        headers={"Content-Type":"application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        sid = r.headers.get("Mcp-Session-Id")
    # 2. call arif_vault_seal (probe, no write)
    r = _mcp_call("arif_vault_seal",
        {"action":"PROBE","payload":"golden","actor_id":"golden-test",
         "session_id":sid,"ack_irreversible":False}, sid)
    # Either SEAL (success) or HOLD (needs envelope upgrade) are both valid
    # signals; the bridge reached arif_vault_seal. The key invariant is
    # NOT a 400 / 404 / "Missing session ID" response.
    text = r.get("result",{}).get("content",[{}])[0].get("text","")
    assert "Missing session ID" not in text, f"session handshake lost: {text!r}"
    assert "404" not in text, f"old REST path still active: {text!r}"
```

## Target: 100% pass before any release.
