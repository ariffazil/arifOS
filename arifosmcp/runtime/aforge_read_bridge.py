"""Read-only client from the arifOS kernel to A-FORGE MCP on 127.0.0.1:7072.

The caller tool name is compared by equality with two literals. The name that
goes on the wire is the stored constant, never the caller string. A mismatch
on GET /health identity_hash or commit raises before any tools/call.
"""

from __future__ import annotations

import base64
import json
from http.client import HTTPConnection

from arifosmcp.runtime.federation_edges import _normalize_identity

HOST = "127.0.0.1"
PORT = 7072
ATTESTED_COMMIT_SHORT = "ef8bac3"
ATTESTED_COMMIT_FULL = "ef8bac39e9fced8401f9bf91085a1fcbea7d09f3"
ATTESTED_IDENTITY = "fb3c88911e6c3a53e91863ec0cb1908621d9083ea2fdea0503f84d19a003d5c4"

# A-FORGE re-signs this on every release (scripts/sign-release-attestation.mjs).
# The literal pins above are duplicated truth: correct only until A-FORGE ships
# again (measured 2026-11-28 — pin born 11-26 17:25, stale by 5 commits in 36h).
# The signed attestation is the organ's own word, so it is accepted alongside the
# literal; a verification failure falls back to the literal, never to "accept
# anything".
ATTESTATION_PATH = "/var/lib/aforge/release-attestation.json"
ATTESTATION_PUBKEY_PATH = "/etc/aforge/release-attestation.pub.pem"
MAX_ATTESTATION = 64 * 1024

# Keys are the only accepted caller strings. Values are the wire constants.
ALLOWLIST = {
    "forge_health_check": "forge_health_check",
    "forge_probe": "forge_probe",
}

PROTOCOL_VERSION = "2025-06-18"
MAX_BODY = 2 * 1024 * 1024
_REDIRECTS = frozenset({301, 302, 303, 307, 308})
_NONEMPTY_KEYS = ("status", "data", "commit", "tool_count", "organs", "identity_hash")


class AforgeReadHold(Exception):
    """Read bridge refused. Never a seal."""


def payload_is_empty(payload: object) -> bool:
    """True when the tool JSON has no evidence field worth wrapping."""
    if payload is None or payload == "" or payload == {} or payload == []:
        return True
    if not isinstance(payload, dict):
        return True
    for key in _NONEMPTY_KEYS:
        value = payload.get(key)
        if value is None or value == "" or value == {} or value == []:
            continue
        return False
    return True


def _as_count(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _signed_release_commit() -> str | None:
    """release_commit from A-FORGE's ed25519-signed attestation, verified.

    None means "cannot be read or cannot be trusted"; the caller then falls
    back to the compiled literal. Never raises.
    """
    try:
        with open(ATTESTATION_PATH, "rb") as fh:
            raw = fh.read(MAX_ATTESTATION + 1)
        with open(ATTESTATION_PUBKEY_PATH, "rb") as fh:
            pub_pem = fh.read(MAX_ATTESTATION + 1)
    except OSError:
        return None
    if len(raw) > MAX_ATTESTATION or len(pub_pem) > MAX_ATTESTATION:
        return None
    try:
        from cryptography.hazmat.primitives.serialization import load_pem_public_key

        attestation = json.loads(raw.decode("utf-8"))
        if not isinstance(attestation, dict):
            return None
        signature = base64.b64decode(attestation.get("signature") or "", validate=True)
        body = {key: value for key, value in attestation.items() if key != "signature"}
        payload = json.dumps(body, separators=(",", ":")).encode("utf-8")
        load_pem_public_key(pub_pem).verify(signature, payload)
    except Exception:
        return None
    commit = attestation.get("release_commit")
    if not isinstance(commit, str):
        return None
    commit = commit.strip()
    return commit if len(commit) >= 7 else None


def _allowed_commits() -> tuple[set[str], set[str]]:
    """(short prefixes, full commits) this bridge will accept."""
    short = {ATTESTED_COMMIT_SHORT}
    full = {ATTESTED_COMMIT_FULL}
    signed = _signed_release_commit()
    if signed is not None:
        short.add(signed[:7])
        if len(signed) >= 40:
            full.add(signed)
    return short, full


def _commit_matches(raw: object) -> str | None:
    if not isinstance(raw, str):
        return None
    commit = raw.strip()
    short, full = _allowed_commits()
    if len(commit) == 7:
        return commit if commit in short else None
    if commit in full:
        return commit
    return None


def _release_from_health(health: dict) -> dict:
    identity = _normalize_identity(health.get("identity_hash"))
    if identity != ATTESTED_IDENTITY:
        raise AforgeReadHold("identity mismatch")
    commit = _commit_matches(health.get("commit"))
    if commit is None:
        commit = _commit_matches(health.get("deployed_commit"))
    if commit is None:
        observed = health.get("commit")
        if not observed:
            observed = health.get("deployed_commit")
        short, _full = _allowed_commits()
        raise AforgeReadHold(f"commit mismatch: observed={observed!r} expected={sorted(short)}")
    tool_count = _as_count(health.get("tool_count"))
    if tool_count is None:
        tool_count = _as_count(health.get("tools_listed"))
    status = health.get("status")
    return {
        "commit": commit,
        "identity_hash": identity,
        "tool_count": tool_count,
        "status": status if isinstance(status, str) else None,
    }


def _unwrap(raw: bytes, content_type: str) -> dict:
    if len(raw) > MAX_BODY:
        raise AforgeReadHold("body cap")
    text = raw.decode("utf-8", errors="replace").strip()
    ctype = (content_type or "").lower()
    if "text/event-stream" in ctype or text.startswith("data:") or "\ndata:" in text:
        data_lines = [line[5:].lstrip() for line in text.splitlines() if line.startswith("data:")]
        if not data_lines:
            raise AforgeReadHold("empty sse")
        chosen = data_lines[-1]
        if chosen.strip() == "[DONE]" and len(data_lines) > 1:
            chosen = data_lines[-2]
        text = chosen.strip()
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AforgeReadHold("non-JSON text") from exc
    if not isinstance(obj, dict):
        raise AforgeReadHold("non-JSON text")
    return obj


def _headers(method: str) -> dict[str, str]:
    headers = {
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": PROTOCOL_VERSION,
    }
    if method == "POST":
        headers["Content-Type"] = "application/json"
    return headers


def _roundtrip(
    conn: HTTPConnection, method: str, path: str, body: dict | None, timeout: float
) -> dict:
    conn.timeout = timeout
    payload = None if body is None else json.dumps(body).encode("utf-8")
    conn.request(method, path, body=payload, headers=_headers(method))
    response = conn.getresponse()
    status = response.status
    raw = response.read(MAX_BODY + 1)
    ctype = response.getheader("Content-Type") or ""
    if status in _REDIRECTS:
        raise AforgeReadHold(f"redirect {status}")
    if status != 200:
        raise AforgeReadHold(f"http {status}")
    parsed = _unwrap(raw, ctype)
    if parsed.get("error"):
        raise AforgeReadHold("jsonrpc error")
    return parsed


def _tool_payload(rpc: dict) -> dict:
    result = rpc.get("result")
    if not isinstance(result, dict):
        raise AforgeReadHold("missing content")
    if result.get("isError") is True:
        raise AforgeReadHold("isError")
    content = result.get("content")
    if not isinstance(content, list) or not content:
        raise AforgeReadHold("missing content")
    text = None
    for item in content:
        if isinstance(item, dict) and item.get("type") == "text":
            text = item.get("text")
            break
    if not isinstance(text, str) or not text.strip():
        raise AforgeReadHold("missing content")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AforgeReadHold("non-JSON text") from exc
    if payload_is_empty(payload):
        raise AforgeReadHold("empty payload")
    if not isinstance(payload, dict):
        raise AforgeReadHold("empty payload")
    return payload


def _read_pinned(conn: HTTPConnection, wire: str) -> dict:
    health = _roundtrip(conn, "GET", "/health", None, 8)
    release = _release_from_health(health)
    _roundtrip(
        conn,
        "POST",
        "/mcp",
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "arifos-kernel-aforge-read", "version": "0"},
            },
        },
        8,
    )
    rpc = _roundtrip(
        conn,
        "POST",
        "/mcp",
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": wire, "arguments": {}},
        },
        25,
    )
    return {"payload": _tool_payload(rpc), "release": release, "wire_tool": wire}


def read_tool(tool_name: str) -> dict:
    """Call one allowlisted observe tool. Raises AforgeReadHold on any miss."""
    wire = ALLOWLIST.get(tool_name) if isinstance(tool_name, str) else None
    if wire is None or wire != tool_name:
        raise AforgeReadHold(f"allowlist: {tool_name!r} is not a kernel read tool")
    conn = None
    try:
        conn = HTTPConnection(HOST, PORT, timeout=8)
        return _read_pinned(conn, wire)
    except AforgeReadHold:
        raise
    except Exception as exc:
        raise AforgeReadHold(f"connection error: {type(exc).__name__}") from exc
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
