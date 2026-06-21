"""
ARIF Transport Airlock — Conformance Probe
═══════════════════════════════════════════

Tests arifOS against the transport conformance matrix.
Every test produces a structured pass/fail with evidence.

Run: python -m arifosmcp.transport.conformance [--url http://...]

DITEMPA BUKAN DIBERI — Proved by trace, not by claim.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from typing import Any

# ── Config ──────────────────────────────────────────────────────────────────

BASE_URL = "http://127.0.0.1:8088"
KERNEL_URL = "http://127.0.0.1:8088/mcp"

PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"

CONFORMANCE_SPINE = [
    "ping",
    "version_echo",
    "initialize_probe",
    "schema_echo",
    "transport_echo",
    "session_init_light",
    "os_attest",
    "888_hold_mutation_refusal",
    "vault_replay",
    "cooling_ledger",
]


# ── Test Helpers ────────────────────────────────────────────────────────────

def jsonrpc_post(url: str, method: str, params: dict[str, Any] | None = None,
                 headers: dict[str, str] | None = None) -> dict[str, Any]:
    """Send JSON-RPC 2.0 POST request."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {},
    }
    encoded = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=encoded,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            **(headers or {}),
        },
    )
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        body = json.loads(resp.read().decode("utf-8"))
        # Capture session-id header if present
        session_id = resp.headers.get("mcp-session-id") or resp.headers.get("Mcp-Session-Id")
        if session_id:
            body["_session_id"] = session_id
        return body
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8"))
        except Exception:
            body = {"error": f"HTTP {e.code}"}
        body["_http_status"] = e.code
        return body
    except Exception as e:
        return {"error": str(e), "_exception": True}


def http_get(url: str) -> dict[str, Any]:
    """Simple HTTP GET."""
    try:
        resp = urllib.request.urlopen(url, timeout=10)
        body = json.loads(resp.read().decode("utf-8"))
        return body
    except Exception as e:
        return {"error": str(e), "_exception": True}


def http_post(url: str, data: dict[str, Any]) -> dict[str, Any]:
    """Simple HTTP POST with JSON body."""
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e), "_exception": True}


# ── Test Functions ──────────────────────────────────────────────────────────

Results = list[dict[str, Any]]


def test_ping() -> dict[str, Any]:
    """GET /ping returns status ok."""
    result = http_get(f"{BASE_URL}/ping")
    passed = (
        isinstance(result, dict)
        and result.get("status") == "ok"
        and "ts" in result
    )
    return {
        "test": "ping",
        "target": "GET /ping",
        "verdict": PASS if passed else FAIL,
        "evidence": result,
        "note": "Basic liveness. Canary layer before any sovereignty.",
    }


def test_schema_echo() -> dict[str, Any]:
    """GET /schema returns protocol versions and tools count."""
    result = http_get(f"{BASE_URL}/schema")
    passed = (
        isinstance(result, dict)
        and "protocol_versions_supported" in result
        and "tools_count" in result
    )
    return {
        "test": "schema_echo",
        "target": "GET /schema",
        "verdict": PASS if passed else FAIL,
        "evidence": result,
        "note": "Protocol version advertisement. Must match kernel.",
    }


def test_version() -> dict[str, Any]:
    """GET /version returns version info."""
    result = http_get(f"{BASE_URL}/version")
    passed = (
        isinstance(result, dict)
        and "version" in result
    )
    return {
        "test": "version",
        "target": "GET /version",
        "verdict": PASS if passed else FAIL,
        "evidence": result,
        "note": "Software version for client compatibility check.",
    }


def test_probe() -> dict[str, Any]:
    """POST /probe echoes request body."""
    body = {"hello": "world", "test": True}
    result = http_post(f"{BASE_URL}/probe", body)
    passed = (
        isinstance(result, dict)
        and result.get("probe_ok") is True
        and result.get("echoed", {}).get("hello") == "world"
    )
    return {
        "test": "probe",
        "target": "POST /probe",
        "verdict": PASS if passed else FAIL,
        "evidence": result,
        "note": "Transport debugging endpoint. No auth, no floors, no envelope.",
    }


def test_kernel_initialize() -> dict[str, Any]:
    """Send MCP initialize to kernel."""
    result = jsonrpc_post(KERNEL_URL, "initialize", {
        "protocolVersion": "2025-11-25",
        "capabilities": {},
        "clientInfo": {"name": "conformance-probe", "version": "0.1"},
    })
    passed = (
        isinstance(result, dict)
        and "result" in result
        and isinstance(result.get("result"), dict)
        and "serverInfo" in result["result"]
    )
    session_id = result.get("_session_id", "none")
    return {
        "test": "kernel_initialize",
        "target": "POST /mcp initialize",
        "verdict": PASS if passed else FAIL,
        "evidence": {
            "response_keys": list(result.keys()),
            "session_id": session_id,
            "serverInfo": result.get("result", {}).get("serverInfo", "N/A"),
        },
        "note": "MCP protocol handshake. Must return serverInfo + capabilities.",
    }


def test_kernel_tools_list() -> dict[str, Any]:
    """List tools after init."""
    # Initialize first
    init_resp = jsonrpc_post(KERNEL_URL, "initialize", {
        "protocolVersion": "2025-11-25",
        "capabilities": {},
        "clientInfo": {"name": "conformance-probe", "version": "0.1"},
    })
    sid = init_resp.get("_session_id", "")

    # List tools with session
    headers = {}
    if sid:
        headers["mcp-session-id"] = sid

    result = jsonrpc_post(KERNEL_URL, "tools/list", {}, headers=headers)
    tools = result.get("result", {}).get("tools", [])
    passed = isinstance(tools, list) and len(tools) >= 13

    return {
        "test": "kernel_tools_list",
        "target": "POST /mcp tools/list",
        "verdict": PASS if passed else FAIL,
        "evidence": {
            "tool_count": len(tools),
            "tool_names": [t.get("name", "?") for t in tools[:5]] + ["..."],
            "session_used": bool(sid),
        },
        "note": "MCP tool discovery. At least 13 canonical tools must be present.",
    }


def test_kernel_tool_call_safe() -> dict[str, Any]:
    """Call a safe read-only tool."""
    init_resp = jsonrpc_post(KERNEL_URL, "initialize", {
        "protocolVersion": "2025-11-25",
        "capabilities": {},
        "clientInfo": {"name": "conformance-probe", "version": "0.1"},
    })
    sid = init_resp.get("_session_id", "")

    headers = {}
    if sid:
        headers["mcp-session-id"] = sid

    # Call arif_ops_measure (read-only, no auth needed)
    result = jsonrpc_post(KERNEL_URL, "tools/call", {
        "name": "arif_ops_measure",
        "arguments": {"mode": "vitals"},
    }, headers=headers)

    passed = isinstance(result, dict) and "result" in result
    return {
        "test": "kernel_tool_call_safe",
        "target": "POST /mcp tools/call (arif_ops_measure)",
        "verdict": PASS if passed else FAIL,
        "evidence": {
            "has_result": "result" in result,
            "has_error": "error" in result,
            "error_data": result.get("error") if "error" in result else None,
        },
        "note": "Safe read-only tool call through MCP. Must succeed without auth.",
    }


def test_airlock_dialect_detect_raw() -> dict[str, Any]:
    """Airlock detects raw_jsonrpc dialect correctly."""
    from .airlock import detect_dialect

    request = {"method": "arif_ping", "params": {}}
    dialect = detect_dialect(request, "http")

    return {
        "test": "airlock_dialect_detect_raw",
        "target": "detect_dialect(raw_jsonrpc)",
        "verdict": PASS if dialect == "raw_jsonrpc" else FAIL,
        "evidence": {"dialect_detected": dialect, "expected": "raw_jsonrpc"},
        "note": "Raw JSON-RPC without client info must detect as raw_jsonrpc.",
    }


def test_airlock_dialect_detect_chatgpt() -> dict[str, Any]:
    """Airlock detects ChatGPT dialect."""
    from .airlock import detect_dialect

    request = {
        "method": "tools/call",
        "params": {"name": "arif_ping", "arguments": {}},
        "client_info": {"name": "chatgpt", "version": "1.0"},
    }
    dialect = detect_dialect(request, "http")

    return {
        "test": "airlock_dialect_detect_chatgpt",
        "target": "detect_dialect(chatgpt)",
        "verdict": PASS if dialect == "chatgpt" else FAIL,
        "evidence": {"dialect_detected": dialect, "expected": "chatgpt"},
        "note": "ChatGPT client info must trigger chatgpt dialect adapter.",
    }


def test_airlock_normalize_envelope() -> dict[str, Any]:
    """Airlock normalizes request into CanonicalEnvelope."""
    from .airlock import process_request

    request = {
        "method": "arif_ops_measure",
        "params": {"mode": "vitals"},
        "client_info": {"name": "conformance-probe", "version": "0.1"},
    }

    result = process_request(request, "http")
    passed = (
        result.envelope is not None
        and result.envelope.tool_name == "arif_ops_measure"
        and result.envelope.trace_id is not None
        and len(result.envelope.trace_id) == 16
    )

    return {
        "test": "airlock_normalize_envelope",
        "target": "process_request → CanonicalEnvelope",
        "verdict": PASS if passed else FAIL,
        "evidence": {
            "envelope_produced": result.envelope is not None,
            "tool_name": result.envelope.tool_name if result.envelope else "NONE",
            "trace_id": result.envelope.trace_id if result.envelope else "NONE",
            "action_class": result.envelope.action_class.value if result.envelope else "NONE",
        },
        "note": "CanonicalEnvelope must carry trace_id, tool_name, action_class.",
    }


def test_airlock_error_arif_schema() -> dict[str, Any]:
    """Airlock produces structured ARIF_SCHEMA_MISMATCH error."""
    from .errors import arif_error

    err = arif_error("ARIF_SCHEMA_MISMATCH", expected_shape="tools/call.params.arguments")
    error_data = err.get("error", {}).get("data", {})
    passed = (
        error_data.get("code") == "ARIF_SCHEMA_MISMATCH"
        and error_data.get("retryable") is True
        and error_data.get("next_probe") == "schema_echo"
    )

    return {
        "test": "airlock_error_arif_schema",
        "target": "arif_error(ARIF_SCHEMA_MISMATCH)",
        "verdict": PASS if passed else FAIL,
        "evidence": {
            "error_code": error_data.get("code"),
            "retryable": error_data.get("retryable"),
            "next_probe": error_data.get("next_probe"),
        },
        "note": "ARIF_SCHEMA_MISMATCH must carry retryable=True + next_probe.",
    }


# ── Run All ─────────────────────────────────────────────────────────────────

def run_all(url: str = BASE_URL) -> list[dict[str, Any]]:
    """Run all conformance tests and return results matrix."""
    global BASE_URL, KERNEL_URL
    BASE_URL = url
    KERNEL_URL = f"{url}/mcp" if url != BASE_URL else KERNEL_URL

    tests = [
        test_ping,
        test_schema_echo,
        test_version,
        test_probe,
        test_kernel_initialize,
        test_kernel_tools_list,
        test_kernel_tool_call_safe,
        test_airlock_dialect_detect_raw,
        test_airlock_dialect_detect_chatgpt,
        test_airlock_normalize_envelope,
        test_airlock_error_arif_schema,
    ]

    results = []
    for test_fn in tests:
        try:
            result = test_fn()
        except Exception as e:
            result = {
                "test": test_fn.__name__,
                "target": "exception",
                "verdict": FAIL,
                "evidence": {"error": str(e)},
                "note": "Test raised exception.",
            }
        results.append(result)

    return results


def _spine_pass(name: str, evidence: dict[str, Any]) -> dict[str, Any]:
    return {"test": name, "verdict": PASS, "evidence": evidence}


def _spine_fail(name: str, error: Exception | str) -> dict[str, Any]:
    return {"test": name, "verdict": FAIL, "evidence": {"error": str(error)}}


def run_conformance_spine() -> dict[str, Any]:
    """Delegate to the canonical v0.2 proof machine."""
    from arifosmcp.transport.conformance_spine import run_spine

    return run_spine()


def print_matrix(results: list[dict[str, Any]]) -> None:
    """Print results as a conformance matrix."""
    total = len(results)
    passed = sum(1 for r in results if r["verdict"] == PASS)
    failed = sum(1 for r in results if r["verdict"] == FAIL)
    skipped = sum(1 for r in results if r["verdict"] == SKIP)

    print("=" * 72)
    print("ARIF TRANSPORT AIRLOCK — CONFORMANCE MATRIX")
    print("=" * 72)
    print(f"{'Test':<38} {'Verdict':<8} {'Note'}")
    print("-" * 72)
    for r in results:
        print(f"{r['test']:<38} {r['verdict']:<8} {r['note']}")
    print("-" * 72)
    print(f"Total: {total}  Pass: {passed}  Fail: {failed}  Skip: {skipped}")
    print(f"Score: {passed}/{total} ({passed/total*100:.0f}%)" if total else "N/A")
    print()
    print("Detailed evidence:")
    for r in results:
        if r["verdict"] == FAIL:
            print(f"  ❌ {r['test']}:")
            print(f"     {json.dumps(r['evidence'], indent=2)[:300]}")
        elif r["verdict"] == PASS:
            print(f"  ✅ {r['test']}")
    print("=" * 72)


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else BASE_URL
    results = run_all(url)
    print_matrix(results)
    sys.exit(0 if all(r["verdict"] == PASS for r in results) else 1)
