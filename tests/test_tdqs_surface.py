"""Phase-3 CI gate — arifOS MCP surface parity + TDQS repair (2026-10-18, 333-AGI).

Falsifies the Glama name-only stub: asserts the tool SURFACE is full and honest
on every discovery path — sessioned handshake AND the bare (Glama) path — and
that the published-image surface matches the live kernel.

Run against the live kernel (default) or a container — the server MUST run with
ARIFOS_PUBLIC_SURFACE_MODE=forge_next_8 (the 8-verb ABI; public_agent hides forge/seal):
    ARIFOS_MCP_URL=http://127.0.0.1:8088/mcp pytest tests/test_tdqs_surface.py -q
    ARIFOS_MCP_URL=http://127.0.0.1:3299/mcp ARIFOS_MCP_URL_LIVE=http://127.0.0.1:8088/mcp ...

Exit non-zero if any assertion fails. A failing gate = the published surface is
still degraded; a PASSING gate on a known-broken image = the gate is wrong (fix
the gate first, per the Phase-3 falsifier).
"""

from __future__ import annotations

import json
import os
import urllib.request

MCP_URL = os.environ.get("ARIFOS_MCP_URL", "http://127.0.0.1:8088/mcp")
MCP_URL_LIVE = os.environ.get("ARIFOS_MCP_URL_LIVE", "")

# 8 canonical verbs. 888 is NOT a verb. forge + seal are hidden on the
# public_agent profile but MUST still be present on the full surface.
CANONICAL_8 = (
    "arif_init",  # 000
    "arif_observe",  # 111
    "arif_think",  # 333
    "arif_route",  # 444
    "arif_memory",  # 555
    "arif_judge",  # 666
    "arif_forge",  # 777
    "arif_seal",  # 999
)

# Verdict words must appear only as arif_judge / arif_seal OUTPUTS — never in a
# non-judge tool's status/description surface.
VERDICT_WORDS = ("SEAL", "HOLD", "VOID", "SABAR", "PARTIAL", "PROVISIONAL")
NON_JUDGE = tuple(n for n in CANONICAL_8 if n not in ("arif_judge", "arif_seal"))

MIN_DESC_LEN = 200
ANNOTATION_KEYS = ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint")

_HDRS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}


def _post(url: str, payload: dict, sid: str | None = None) -> tuple[str | None, dict]:
    hdrs = dict(_HDRS)
    if sid:
        hdrs["Mcp-Session-Id"] = sid
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=hdrs, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        sid_out = r.headers.get("Mcp-Session-Id") or sid
        raw = r.read(400000).decode()
    data = None
    for line in raw.splitlines():
        if line.startswith("data: "):
            data = json.loads(line[6:])
    if data is None and raw.strip().startswith("{"):
        data = json.loads(raw)
    return sid_out, data


def _tools_list_sessioned(url: str = MCP_URL) -> list[dict]:
    """Full MCP handshake — the well-behaved client path."""
    sid, init = _post(url, {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                   "clientInfo": {"name": "tdqs-gate", "version": "1"}},
    })
    assert init and "result" in init, f"initialize failed: {init}"
    _post(url, {"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)
    _, data = _post(url, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, sid)
    if "error" in (data or {}):
        raise AssertionError(f"tools/list returned error: {data['error']}")
    return data["result"]["tools"]


def _tools_list_bare(url: str = MCP_URL) -> list[dict] | dict:
    """The Glama/scanner path: no session, no version header, bare tools/list."""
    _, data = _post(url, {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
    return (data or {}).get("result", {}).get("tools", [])


def _arif_init_surface_hash(url: str = MCP_URL) -> str | None:
    sid, init = _post(url, {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                   "clientInfo": {"name": "tdqs-gate", "version": "1"}},
    })
    _post(url, {"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)
    _, data = _post(url, {
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": "arif_init", "arguments": {"intent": "TDQS surface gate probe", "requested_authority": "OBSERVE_ONLY"}},
    }, sid)
    try:
        text = data["result"]["content"][0]["text"]
        payload = json.loads(text) if text.strip().startswith("{") else {}
    except Exception:
        payload = {}

    def _find(d):
        if isinstance(d, dict):
            for k, v in d.items():
                if k == "surface_hash" or k == "tool_surface_hash_start":
                    return str(v)
                found = _find(v)
                if found:
                    return found
        elif isinstance(d, list):
            for item in d:
                found = _find(item)
                if found:
                    return found
        return None

    return _find(payload)


def test_surface_has_exactly_canonical_names():
    tools = _tools_list_sessioned()
    names = {t["name"] for t in tools}
    missing = [n for n in CANONICAL_8 if n not in names]
    assert not missing, f"missing canonical tools: {missing}"
    assert "arif_888" not in names and "888_judge" not in names


def test_bare_discovery_path_is_not_name_only():
    """Glama's scanner path must yield the honest surface, not a stub."""
    tools = _tools_list_bare()
    assert isinstance(tools, list) and tools, "bare tools/list returned no tools (discovery dead)"
    by_name = {t["name"]: t for t in tools}
    for name in CANONICAL_8:
        if name not in by_name:
            continue  # public profile may hide forge/seal; sessioned test covers them
        t = by_name[name]
        desc = t.get("description", "")
        assert desc != t["name"], f"bare path {name}: description == name (name-only stub)"
        assert len(desc) >= MIN_DESC_LEN, f"bare path {name}: description too short ({len(desc)}ch)"


def test_every_tool_has_quality_description():
    for t in _tools_list_sessioned():
        name, desc = t["name"], t.get("description", "")
        assert desc != name, f"{name}: description == name (name-only stub)"
        assert len(desc) >= MIN_DESC_LEN, f"{name}: description too short ({len(desc)}ch)"
        _d = desc.lower()
        _names_sibling = any(sib in desc for sib in CANONICAL_8 if sib != name)
        assert ("use" in _d) or ("prefer" in _d) or _names_sibling, (
            f"{name}: no use/prefer guidance and no sibling named"
        )
        # TDQS (d)+(e): auth + returns guidance
        assert ("auth" in _d) or ("session" in _d), f"{name}: no auth/session guidance"
        assert "return" in _d, f"{name}: no returns guidance"


def test_every_tool_has_annotations_closed_schema_and_output_schema():
    for t in _tools_list_sessioned():
        name = t["name"]
        ann = t.get("annotations") or {}
        sch = t.get("inputSchema") or {}
        assert any(k in ann for k in ANNOTATION_KEYS), f"{name}: no MCP annotations"
        assert sch.get("additionalProperties") is False, (
            f"{name}: inputSchema additionalProperties must be False"
        )
        props = sch.get("properties") or {}
        assert len(props) >= 1, f"{name}: inputSchema has zero properties (stub shape)"
        assert t.get("outputSchema"), f"{name}: outputSchema missing (TDQS Phase-2)"


def test_no_verdict_words_on_non_judge_surface():
    for t in _tools_list_sessioned():
        if t["name"] not in NON_JUDGE:
            continue
        desc = t.get("description", "")
        for w in VERDICT_WORDS:
            assert f" {w} " not in f" {desc} ", (
                f"{t['name']}: verdict word {w} leaks into description"
            )


def test_no_888_judge_vocab():
    for t in _tools_list_sessioned():
        desc = t.get("description", "")
        title = t.get("title", "") or ""
        assert "888" not in desc, f"{t.get('name')}: '888' leaks into description"
        assert "888 JUDGE" not in title, f"{t.get('name')}: '888 JUDGE' in title"


def test_surface_hash_parity():
    """Empty-env/image surface must match the live kernel's reported hash."""
    mine = _arif_init_surface_hash()
    if not MCP_URL_LIVE:
        # Single-endpoint mode: at minimum the hash must exist (surface is
        # hashed at all) — parity needs two endpoints.
        assert mine, "arif_init did not report a surface hash"
        return
    live = _arif_init_surface_hash(MCP_URL_LIVE)
    assert live, "live arif_init did not report a surface hash"
    assert mine == live, f"surface hash mismatch: container={mine} live={live}"
