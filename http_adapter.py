from __future__ import annotations

import json
import os
import queue
import secrets
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field


APP_NAME = "arifOS HTTP Adapter"
APP_VERSION = "0.1.0"

# Security: token must be provided via environment variable.
AUTH_TOKEN_ENV = "ARIFOS_ADAPTER_TOKEN"

# Runtime command defaults to local arifOS stdio server.
MCP_PYTHON_EXE_ENV = "ARIFOS_MCP_PYTHON"
MCP_MODULE_ENV = "ARIFOS_MCP_MODULE"
MCP_TRANSPORT_ENV = "ARIFOS_MCP_TRANSPORT"
MCP_TIMEOUT_ENV = "ARIFOS_MCP_TIMEOUT_SECONDS"
MCP_PYTHONPATH_ENV = "ARIFOS_MCP_PYTHONPATH"

# Side-effecting tools that require explicit ratification.
SIDE_EFFECT_TOOLS_ENV = "ARIFOS_SIDE_EFFECT_TOOLS"
DEFAULT_SIDE_EFFECT_TOOLS = {
    "arifos_forge",
    "arifos_repo_seal",
    "arifos_memory",  # can write in vector_store mode
    "arifos_vault",   # immutable append/write
}


class ToolCallRequest(BaseModel):
    name: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    humanRatified: bool = False
    requestId: str | int | None = None
    confirmationStep: bool = False
    approvalUx: str = Field(default="none", pattern="^(none|manual-confirmation|adaptive-card)$")
    retryOnVoid: str = Field(default="prompt-confirmation", pattern="^(stop|prompt-confirmation|retry-once-after-confirmation)$")


class McpContent(BaseModel):
    type: str = "text"
    text: str


class McpStyleResponse(BaseModel):
    content: list[McpContent]
    isError: bool


@dataclass
class RpcResult:
    init_response: dict[str, Any] | None
    tool_response: dict[str, Any] | None
    stderr: str


app = FastAPI(title=APP_NAME, version=APP_VERSION)


COPILOT_STUDIO_CONTRACT = {
    "contractVersion": "1.0",
    "actionName": "arifos_tools_call",
    "description": "Copilot Studio -> arifOS adapter contract with explicit human ratification gate",
    "confirmationStep": {
        "requiredForSideEffectTools": True,
        "inputField": "confirmationStep",
        "meaning": "User explicitly confirmed execution in UX before adapter execution",
    },
    "approvalUx": {
        "inputField": "approvalUx",
        "allowedValues": ["none", "manual-confirmation", "adaptive-card"],
        "default": "none",
    },
    "retryBehaviorOnVoid": {
        "inputField": "retryOnVoid",
        "allowedValues": ["stop", "prompt-confirmation", "retry-once-after-confirmation"],
        "default": "prompt-confirmation",
        "notes": "Adapter returns retry guidance in VOID payload; caller controls actual retry loop.",
    },
}


LAW_CAPSULE = {
    "capsuleVersion": "1.0",
    "scope": "arifOS HTTP adapter boundary",
    "intent": "Prevent overclaim by separating doctrine, runtime-enforced guards, and human-process expectations.",
    "LAW": [
        {
            "id": "LAW-001",
            "title": "Human sovereignty for side effects",
            "statement": "Side-effecting actions require explicit human ratification in this operating mode.",
        },
        {
            "id": "LAW-002",
            "title": "Copilot Studio confirmation gate",
            "statement": "Confirmation UX must be completed before side-effecting execution.",
        },
        {
            "id": "LAW-003",
            "title": "MCP-style response discipline",
            "statement": "Adapter responses for tool execution must use content[] and isError framing.",
        },
    ],
    "EXPECTATION": [
        {
            "id": "EXP-001",
            "statement": "Human operator validates intent before setting humanRatified=true.",
            "owner": "human-operator",
        },
        {
            "id": "EXP-002",
            "statement": "Copilot Studio flow handles VOID retry policy correctly and avoids automatic unsafe retries.",
            "owner": "copilot-studio-flow",
        },
        {
            "id": "EXP-003",
            "statement": "Deployment keeps ARIFOS_ADAPTER_TOKEN secret-managed and rotated by enterprise policy.",
            "owner": "platform-ops",
        },
    ],
}


def _env_str(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None:
        return default
    value = value.strip()
    return value if value else default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def _get_side_effect_tools() -> set[str]:
    raw = os.getenv(SIDE_EFFECT_TOOLS_ENV, "")
    if not raw.strip():
        return set(DEFAULT_SIDE_EFFECT_TOOLS)
    return {token.strip() for token in raw.split(",") if token.strip()}


def _mcp_error(text: str) -> McpStyleResponse:
    return McpStyleResponse(content=[McpContent(text=text)], isError=True)


def _mcp_ok(payload: Any) -> McpStyleResponse:
    if isinstance(payload, str):
        text = payload
    else:
        text = json.dumps(payload, ensure_ascii=True)
    return McpStyleResponse(content=[McpContent(text=text)], isError=False)


def _void_payload(code: str, reason: str, request: ToolCallRequest) -> dict[str, Any]:
    return {
        "verdict": "VOID",
        "code": code,
        "reason": reason,
        "tool": request.name,
        "retry": {
            "policy": request.retryOnVoid,
            "allowed": request.retryOnVoid != "stop",
            "nextStep": "Require explicit user confirmation then resend with humanRatified=true and confirmationStep=true",
        },
        "approval": {
            "humanRatified": request.humanRatified,
            "confirmationStep": request.confirmationStep,
            "approvalUx": request.approvalUx,
        },
    }


def _require_auth(authorization: str | None) -> None:
    expected = os.getenv(AUTH_TOKEN_ENV, "").strip()
    if not expected:
        raise HTTPException(
            status_code=500,
            detail="Server auth misconfigured: missing ARIFOS_ADAPTER_TOKEN",
        )

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authorization must be Bearer token")

    presented = parts[1].strip()
    if not secrets.compare_digest(presented, expected):
        raise HTTPException(status_code=403, detail="Invalid bearer token")


def _read_stream_lines(pipe, target_queue: queue.Queue[str]) -> None:
    try:
        for line in iter(pipe.readline, ""):
            target_queue.put(line)
    except Exception:
        return


def _call_mcp_stdio(tool_name: str, arguments: dict[str, Any], timeout_seconds: int) -> RpcResult:
    python_exe = _env_str(MCP_PYTHON_EXE_ENV, "python")
    module_name = _env_str(MCP_MODULE_ENV, "arifosmcp.runtime")
    transport_mode = _env_str(MCP_TRANSPORT_ENV, "stdio")

    env = os.environ.copy()
    env.setdefault("ARIFOS_MINIMAL_STDIO", "1")
    py_path = os.getenv(MCP_PYTHONPATH_ENV, "").strip()
    if py_path:
        env["PYTHONPATH"] = py_path

    proc = subprocess.Popen(
        [python_exe, "-m", module_name, transport_mode],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env,
    )

    out_q: queue.Queue[str] = queue.Queue()
    err_q: queue.Queue[str] = queue.Queue()

    assert proc.stdout is not None
    assert proc.stderr is not None
    threading.Thread(target=_read_stream_lines, args=(proc.stdout, out_q), daemon=True).start()
    threading.Thread(target=_read_stream_lines, args=(proc.stderr, err_q), daemon=True).start()

    def send(payload: dict[str, Any]) -> None:
        assert proc.stdin is not None
        proc.stdin.write(json.dumps(payload, ensure_ascii=True) + "\n")
        proc.stdin.flush()

    def read_by_id(expected_id: int, timeout_s: int) -> dict[str, Any] | None:
        end = time.time() + timeout_s
        while time.time() < end:
            try:
                line = out_q.get(timeout=0.2)
            except queue.Empty:
                continue

            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except Exception:
                continue

            if obj.get("id") == expected_id:
                return obj
        return None

    try:
        send(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "arifos-http-adapter", "version": APP_VERSION},
                },
            }
        )
        init_response = read_by_id(1, timeout_seconds)

        send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

        send(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments},
            }
        )
        tool_response = read_by_id(2, timeout_seconds)

        stderr_lines: list[str] = []
        while True:
            try:
                stderr_lines.append(err_q.get_nowait())
            except queue.Empty:
                break

        return RpcResult(
            init_response=init_response,
            tool_response=tool_response,
            stderr="".join(stderr_lines).strip(),
        )
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()


def _decode_mcp_tool_result(tool_response: dict[str, Any] | None) -> tuple[bool, Any]:
    if tool_response is None:
        return True, {"error": "timeout waiting for tools/call response"}

    if "error" in tool_response:
        return True, tool_response["error"]

    result = tool_response.get("result", {})
    if not isinstance(result, dict):
        return True, {"error": "invalid MCP result payload"}

    is_error = bool(result.get("isError"))
    content = result.get("content")

    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "")
                if not isinstance(text, str):
                    continue
                try:
                    parsed = json.loads(text)
                except Exception:
                    parsed = text
                return is_error, parsed

    return is_error, result


def _guard_matrix() -> list[dict[str, Any]]:
    side_effect_tools = sorted(_get_side_effect_tools())
    token_configured = bool(os.getenv(AUTH_TOKEN_ENV, "").strip())
    return [
        {
            "id": "GRD-001",
            "title": "Bearer auth required on /tools/call",
            "enforced": True,
            "evidence": "_require_auth() raises 401/403 and checks ARIFOS_ADAPTER_TOKEN",
            "runtimeState": {"authTokenConfigured": token_configured},
        },
        {
            "id": "GRD-002",
            "title": "Side-effect gate requires humanRatified=true",
            "enforced": True,
            "evidence": "tools_call() returns VOID code F13_RATIFICATION_REQUIRED before MCP dispatch",
            "runtimeState": {"sideEffectTools": side_effect_tools},
        },
        {
            "id": "GRD-003",
            "title": "Confirmation gate requires confirmationStep=true",
            "enforced": True,
            "evidence": "tools_call() returns VOID code CONFIRMATION_REQUIRED before MCP dispatch",
            "runtimeState": {"appliesTo": side_effect_tools},
        },
        {
            "id": "GRD-004",
            "title": "VOID includes retry guidance",
            "enforced": True,
            "evidence": "_void_payload() always returns retry.policy/allowed/nextStep",
            "runtimeState": {
                "allowedPolicies": ["stop", "prompt-confirmation", "retry-once-after-confirmation"],
            },
        },
        {
            "id": "GRD-005",
            "title": "MCP-style response shape for /tools/call",
            "enforced": True,
            "evidence": "response_model=McpStyleResponse with content[] and isError",
            "runtimeState": {"outputSchema": "McpStyleResponse"},
        },
    ]


@app.get("/health")
def health() -> dict[str, Any]:
    token_set = bool(os.getenv(AUTH_TOKEN_ENV, "").strip())
    return {
        "ok": True,
        "service": APP_NAME,
        "version": APP_VERSION,
        "authConfigured": token_set,
        "mcpModule": _env_str(MCP_MODULE_ENV, "arifosmcp.runtime"),
        "transport": _env_str(MCP_TRANSPORT_ENV, "stdio"),
    }


@app.get("/contract/copilot-studio")
def copilot_studio_contract() -> dict[str, Any]:
    return {
        **COPILOT_STUDIO_CONTRACT,
        "inputSchema": ToolCallRequest.model_json_schema(),
        "outputSchema": McpStyleResponse.model_json_schema(),
    }


@app.get("/law/capsule")
def law_capsule() -> dict[str, Any]:
    return {
        **LAW_CAPSULE,
        "GUARD": _guard_matrix(),
        "meta": {
            "service": APP_NAME,
            "version": APP_VERSION,
            "boundary": "HTTP adapter only; does not assert guarantees outside this process",
        },
    }


@app.post("/tools/call", response_model=McpStyleResponse)
def tools_call(payload: ToolCallRequest, authorization: str | None = Header(default=None)) -> McpStyleResponse:
    _require_auth(authorization)

    side_effect_tools = _get_side_effect_tools()
    if payload.name in side_effect_tools:
        if not payload.humanRatified:
            return _mcp_error(json.dumps(_void_payload("F13_RATIFICATION_REQUIRED", "F13: humanRatified=true required for side-effect tool", payload), ensure_ascii=True))
        if not payload.confirmationStep:
            return _mcp_error(json.dumps(_void_payload("CONFIRMATION_REQUIRED", "Side-effect tool requires confirmationStep=true", payload), ensure_ascii=True))

    timeout_seconds = _env_int(MCP_TIMEOUT_ENV, 20)
    rpc_result = _call_mcp_stdio(payload.name, payload.arguments, timeout_seconds)

    is_error, decoded_payload = _decode_mcp_tool_result(rpc_result.tool_response)

    if rpc_result.init_response is None:
        return _mcp_error(
            {
                "error": "initialize timeout",
                "stderr": rpc_result.stderr,
                "tool": payload.name,
            }
        )

    if is_error:
        return McpStyleResponse(
            content=[McpContent(text=json.dumps(decoded_payload, ensure_ascii=True))],
            isError=True,
        )

    return _mcp_ok(decoded_payload)


if __name__ == "__main__":
    # Local dev run:
    #   set ARIFOS_ADAPTER_TOKEN=changeme
    #   set ARIFOS_MCP_PYTHONPATH=C:\path\to\arifOS-main
    #   python arifos_http_adapter.py
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8088, log_level="info")
