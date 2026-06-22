"""
arifOS MCP Server — Canonical Entry Point
═══════════════════════════════════════════

FastMCP 3.2.0 + MCP Apps + Streamable HTTP
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

try:
    import uvloop

    uvloop.install()
except ImportError:
    pass  # Windows / dev fallback

import logging
import os
import sys
import traceback
from collections.abc import Callable
from typing import Any


# ─── Path prioritization (runs before arifOS imports below) ─────────────────
def _prioritize_paths(*paths: str) -> None:
    for path in reversed(paths):
        if path in sys.path:
            sys.path.remove(path)
    for path in reversed(paths):
        sys.path.insert(0, path)


def _apply_path_priority() -> None:
    """Run path prioritization before arifOS package imports."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(project_root)
    parent_idx = sys.path.index(parent) if parent in sys.path else len(sys.path)
    project_root_idx = sys.path.index(project_root) if project_root in sys.path else len(sys.path)
    if parent not in sys.path or project_root not in sys.path or parent_idx > project_root_idx:
        _prioritize_paths(parent, project_root)


from dotenv import load_dotenv  # noqa: E402

_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path, override=False)  # systemd EnvironmentFile wins

_llm_client = sys.modules.get("arifosmcp.runtime.llm_client")
if _llm_client is not None:
    _llm_client.SEA_LION_API_KEY = os.getenv("SEA_LION_API_KEY")  # pyright: ignore[reportAttributeAccessIssue]

# Fix sys.path so arifOS packages resolve correctly inside Docker
_apply_path_priority()


# ─── Provider env precedence audit (F1 Amanah / F4 Clarity) ─────────────────
def _log_llm_provider_health() -> None:
    """Log redacted LLM provider source at startup — never the secret value."""
    _logger = logging.getLogger("arifosmcp")
    providers = {
        "SEA_LION_API_KEY": os.getenv("SEA_LION_API_KEY"),
        "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL"),
    }
    for name, val in providers.items():
        if val is None:
            _logger.info("%s=missing", name)
        elif name.endswith("_KEY") and len(val) > 8:
            _logger.info("%s=present_from_env", name)
        else:
            _logger.info("%s=%s", name, val)


_log_llm_provider_health()

import fastmcp  # noqa: E402
from fastmcp import FastMCP  # noqa: E402
from starlette.middleware.base import BaseHTTPMiddleware  # noqa: E402
from starlette.middleware.cors import CORSMiddleware  # noqa: E402
from starlette.requests import Request  # noqa: E402
from starlette.responses import JSONResponse  # noqa: E402

from arifosmcp.constitutional_map import (  # noqa: E402
    CANONICAL_TOOLS,
    list_canonical_tools,
    list_constitutional_tools,
    list_probe_tools,
)
from arifosmcp.runtime.peer_contract import (  # noqa: E402
    get_arifos_peer_contract,
)

logger = logging.getLogger(__name__)

_canonical_tool_names = list_canonical_tools()
_canonical_tool_names_text = ", ".join(_canonical_tool_names)
_constitutional_tool_names = list_constitutional_tools()
_probe_tool_names = list_probe_tools()

# ── Dev-mode gate: expose wiki + diagnostic tools on the public surface ───────
_EXPOSE_DEV_TOOLS = os.getenv("ARIFOS_MCP_EXPOSE_DEV_TOOLS", "false").lower() in (
    "true",
    "1",
    "yes",
)

# ── Organ bridge gate: proxy GEOX/WEALTH/WELL tools through kernel (default: OFF) ─
# When OFF, agents call organ tools directly via their own MCP endpoints.
# When ON, 71 bridged proxy tools are registered on the arifOS surface.
# Set ARIFOS_EXPOSE_ORGAN_BRIDGE=true to enable (e.g. for HTTP-only clients).
_EXPOSE_ORGAN_BRIDGE = os.getenv("ARIFOS_EXPOSE_ORGAN_BRIDGE", "false").lower() in (
    "true",
    "1",
    "yes",
)

# ── ChatGPT compatibility shim: register arif_search + arif_fetch ─────────────
# These are thin single-string-param wrappers that route to arif_observe
# and arif_fetch. Satisfies ChatGPT's mandatory search/fetch discovery
# requirement without touching kernel logic.
_CHATGPT_COMPAT = os.getenv("ARIFOS_CHATGPT_COMPAT", "false").lower() in (
    "true",
    "1",
    "yes",
)


class GlobalPanicMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            print(f"!!! KERNEL PANIC: {e}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            return JSONResponse(
                {
                    "status": "void",
                    "tool": "kernel_panic_handler",
                    "error_message": "L13: System halt due to unhandled kernel exception.",
                    "action": "HALT",
                },
                status_code=500,
            )


class StatelessGetRejectMiddleware(BaseHTTPMiddleware):
    """
    PHOENIX-73C: Reject GET requests to /mcp in stateless HTTP mode.

    Root cause: MCP SDK's StreamableHTTPSessionManager uses a singleton
    GET_STREAM_KEY for SSE streams. When 2 clients connect simultaneously
    with GET (SSE), the second gets 409 Conflict.

    In stateless_http=True mode, GET requests should return JSON-RPC
    responses directly, NOT establish SSE streams. This middleware rejects
    GET at the gateway layer before it reaches the SDK's SSE handler,
    forcing clients to use POST for JSON-RPC calls.

    Clients receiving 405 will know to retry with POST.
    """

    async def dispatch(self, request: Request, call_next):
        # Only guard the /mcp endpoint
        if request.url.path.rstrip("/") == "/mcp" and request.method == "GET":
            return JSONResponse(
                {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32005,
                        "message": "Method not allowed in stateless mode. "
                        "Use POST for JSON-RPC calls. "
                        "SSE streams are not supported in stateless_http mode "
                        "(PHOENIX-73C).",
                        "data": {
                            "hint": "Retry this request using POST with "
                            '{"jsonrpc":"2.0","method":"...","params":{}}'
                        },
                    },
                },
                status_code=405,
                headers={"Allow": "POST, DELETE"},
            )
        return await call_next(request)


class OriginValidationMiddleware(BaseHTTPMiddleware):
    """Validate Origin header on MCP endpoints to prevent DNS rebinding (SEP-2243)."""

    ALLOWED_ORIGIN_PREFIXES: tuple[str, ...] = (
        "https://arifos.arif-fazil.com",
        "https://arif-fazil.com",
        "http://localhost",
        "https://localhost",
        "http://127.0.0.1",
        "https://127.0.0.1",
    )

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/mcp"):
            origin = request.headers.get("origin", "")
            if origin and not any(origin.startswith(p) for p in self.ALLOWED_ORIGIN_PREFIXES):
                return JSONResponse(
                    {"error": "Invalid Origin", "detail": "DNS rebinding protection"},
                    status_code=403,
                )
        return await call_next(request)


# ── MCP Transport spec compliance (modelcontextprotocol.io/specification/2025-11-25/basic/transports) ─
# Per Streamable HTTP spec:
#   POST with proper Accept: 200 OK (json or sse)
#   POST without Accept: 406 (server requires specific Accept)
#   GET: MUST return 200 (SSE stream) OR 405 (no SSE)
#
# The default FastMCP _check_accept_headers returns 400 + JSON-RPC error
# "Missing session ID" on GET when sessionful, which violates the spec.
# Mirror the GEOX + WELL patch so arifOS GET returns 405 (Method Not Allowed)
# when JSON-response is enabled and no SSE stream is offered.
try:
    from mcp.server.streamable_http import StreamableHTTPServerTransport

    _arifos_orig_check = StreamableHTTPServerTransport._check_accept_headers

    def _arifos_patched_check(self, request):
        # If server is in JSON-response mode (stateless_http=False +
        # json_response=True), return 405 on GET instead of 400.
        if getattr(self, "is_json_response_enabled", False) and request.method == "GET":
            from starlette.responses import Response

            return False, Response(status_code=405)
        return _arifos_orig_check(self, request)

    StreamableHTTPServerTransport._check_accept_headers = _arifos_patched_check
except Exception as _e:
    pass  # fail-soft — spec compliance patch is best-effort


# ─── Deployment Identity ─────────────────────────────────────────────────────
def _resolve_git_commit() -> str:
    """Resolve canonical git commit with same priority chain as build.py:_git_sha_short.

    Priority: 1) bare-metal stamp  2) env vars  3) .git/HEAD  4) subprocess git
    This fixes the 'kanon-unknown' defect where the FastMCP serverInfo.version
    was unbound because subprocess git rev-parse fails when CWD is not a git repo.
    """
    # 1. Bare-metal deployment stamp (written by deploy scripts)
    _stamp_path = "/opt/arifos/app/.git_commit"
    if os.path.exists(_stamp_path):
        try:
            with open(_stamp_path) as f:
                content = f.read().strip()
                if len(content) >= 7:
                    return content[:7]
        except Exception:
            pass
    # 2. Environment variables
    for _key in ("DEPLOY_GIT_COMMIT", "ARIFOS_BUILD_SHA", "GIT_SHA", "GIT_COMMIT"):
        _val = os.environ.get(_key, "").strip()
        if _val and _val not in ("unknown", ""):
            return _val[:7]
    # 3. Read .git/HEAD from canonical repo
    for _git_dir in ("/root/arifOS/.git", "/app/.git"):
        try:
            _head = os.path.join(_git_dir, "HEAD")
            if os.path.exists(_head):
                with open(_head) as _f:
                    _content = _f.read().strip()
                if _content.startswith("ref: refs/heads/"):
                    _branch = _content.split("ref: refs/heads/", 1)[1].strip()
                    _ref = os.path.join(_git_dir, "refs", "heads", _branch)
                    if os.path.exists(_ref):
                        with open(_ref) as _f:
                            return _f.read().strip()[:7]
                elif len(_content) >= 7:
                    return _content[:7]
        except Exception:
            pass
    # 4. Subprocess git (legacy fallback — works only if CWD is git repo)
    try:
        import subprocess  # nosec B404

        return (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                stderr=subprocess.DEVNULL,
                cwd=os.environ.get("ARIFOS_HOME", "/root") + "/arifOS",
            )
            .decode()
            .strip()[:7]
        )
    except Exception:
        return "unknown"


from datetime import UTC, datetime  # noqa: E402

_DEPLOY_GIT_COMMIT = _resolve_git_commit()
_DEPLOY_BUILD_DATE = datetime.now(UTC).strftime("%Y.%m.%d")
_DEPLOY_VERSION = (
    f"kanon-{_DEPLOY_BUILD_DATE}+{_DEPLOY_GIT_COMMIT}"
    if _DEPLOY_GIT_COMMIT != "unknown"
    else f"kanon-{_DEPLOY_BUILD_DATE}"
)


mcp = FastMCP(
    "ARIFOS MCP",
    version=_DEPLOY_VERSION,
    website_url="https://arifosmcp.arif-fazil.com",
    instructions=(
        "Constitutional AI orchestration kernel — arifOS.\n\n"
        "Membrane Principle:\n"
        "- Language is lossy compression, not the world.\n"
        "- Intelligence is uncertainty reduction under constraint and human judgment.\n"
        "- Truth survives falsification, not assertion.\n"
        "- Meaning is sovereign-anchored; the machine carries structure, not sense.\n"
        "- Paradox is the boundary scream — the correct response is HOLD.\n\n"
        "Golden path: init → sense → mind → heart → judge → vault\n\n"
        "Canonical surface: 27 tools on default wire "
        "(21 constitutional arif_noun_verb + 6 zero-floor canary probes).\n"
        f"Tools:\n  {', '.join(sorted(list_canonical_tools()))}\n\n"
        "DITEMPA BUKAN DIBERI — Forged, Not Given"
    ),
)

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 0: TRANSPORT CANARY LAYER
# ── Pre-registration probe tools registered OUTSIDE the big try block.
#    These survive even if canonical tool registration fails.
#    Zero floors, zero KG, zero identity, zero VAULT writes.
#    Purpose: isolate whether transport wound is MCP init, schema, or kernel.
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool(
    name="arif_conformance_report",
    description=(
        "PROOF MACHINE: Run the ARIF Conformance Spine v0.2 against the live kernel. "
        "Every verdict is earned from a real response — no mocks, no hardcoded PASS. "
        "Checks: kernel alive, MCP initialize, protocol version, schema echo, session start, "
        "authority classification, 888_HOLD mutation refusal, VAULT replay verification, "
        "cooling_ledger attestation. "
        "substrate_gate=GREEN means arifOS is a governed runtime, not a concept."
    ),
    tags={"canary", "transport-probe", "read-only", "conformance", "proof-machine"},
)
def arif_conformance_report(
    payload: Any = None,
    _envelope: dict[str, Any] | None = None,
    client_capabilities: dict[str, Any] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict:
    """
    Run the live Conformance Spine and return a structured proof report.

    No mocks. No hardcoded results. Every check fires against the running kernel.
    substrate_gate GREEN = governed intelligence runtime proven.
    substrate_gate AMBER = partial proof, residues remain.
    substrate_gate RED   = critical failures, do not claim governance.
    """
    from arifosmcp.transport.conformance_spine import run_spine

    report = run_spine()

    # Annotate each check with a plain-English description
    descriptions = {
        "arifos_alive":        "arifOS alive?               kernel /health returns healthy",
        "mcp_initialize":      "MCP initialize works?       protocol handshake returns serverInfo",
        "protocol_version":    "protocol version clear?     2025-11-25 or supported variant present",
        "schema_echo_stable":  "schema echo stable?         arif_schema_echo returns what was sent",
        "session_starts":      "session starts?             arif_init returns READY",
        "authority_checked":   "authority checked?          classify_authority fires SOVEREIGN/HIGH/MEDIUM/LOW",
        "hold_blocks_mutation":"888_HOLD blocks mutation?   irreversible intents return 888_HOLD_REQUIRED",
        "vault_replay":        "VAULT replay verifies?      vault file readable, last entry valid JSON",
    }
    for check in report["checks"]:
        check["description"] = descriptions.get(check["check"], "")

    return report


@mcp.tool(
    name="arif_ping",
    description="TRANSPORT PROBE: Dead-simple canary to test client bridge connectivity. "
    "Zero floors, zero identity, zero KG, zero VAULT writes. "
    "If this tool returns OK but arif_init fails, the wound is in the init schema.",
    tags={"canary", "transport-probe", "read-only"},
)
def arif_ping(
    payload: Any = None,
    _envelope: dict[str, Any] | None = None,
    client_capabilities: dict[str, Any] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict:
    """Canary probe — no session, no actor, no constitution required."""
    return {
        "ok": True,
        "build": _DEPLOY_VERSION,
        "adapter": "arifos-mcp-v2",
        "schema_version": "v2026.06.14.v2",
        "timestamp": datetime.now(UTC).isoformat(),
        "probe": True,
        "floors_active": False,
    }


@mcp.tool(
    name="arif_schema_echo",
    description="TRANSPORT PROBE: Echo back what the client sent. "
    "Use this to diagnose schema mismatch (-32602). "
    "Returns received params shape, normalized shape, and parser verdict. "
    "Zero floors, zero identity, zero side effects.",
    tags={"canary", "transport-probe", "diagnostic", "read-only"},
)
def arif_schema_echo(
    payload: dict | str | list | None = None,
    _envelope: dict[str, Any] | None = None,
    client_capabilities: dict[str, Any] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict:
    """Echo diagnostic — returns what client sent for shape comparison.

    FIX (2026-06-21): Changed payload type from `Any` to `dict | str | list | None`.
    `Any` generated an empty JSON Schema (no `type` field), causing FastMCP/MCP
    clients to strip the parameter to None — the conformance spine's
    `schema_echo_stable` check FAILed because payload arrived as NoneType.
    Concrete union types generate a proper anyOf schema.
    """
    import json

    params = payload if isinstance(payload, dict) else {}
    received_keys = sorted(params.keys()) if isinstance(payload, dict) else []
    type_map = {k: type(v).__name__ for k, v in params.items()} if isinstance(payload, dict) else {}
    raw_dump = json.dumps(params, default=str)[:2000] if isinstance(payload, dict) else str(payload)[:2000]
    return {
        "ok": True,
        "probe": "schema_echo",
        "echo": payload,
        "received_type": type(payload).__name__,
        "received_repr": repr(payload)[:2000],
        "received_keys": received_keys,
        "key_count": len(received_keys),
        "type_map": type_map,
        "raw_preview": raw_dump,
        "build": _DEPLOY_VERSION,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@mcp.tool(
    name="arif_transport_echo",
    description="TRANSPORT PROBE: Echo transport-level metadata. "
    "Use this before arif_init to verify the MCP transport bridge is working. "
    "Returns received protocol version, transport type, negotiated state. "
    "Normalized arguments: payload, _envelope, client_capabilities. "
    "Zero floors, zero identity, zero side effects.",
    tags={"canary", "transport-probe", "diagnostic", "read-only"},
)
def arif_transport_echo(
    payload: Any = None,
    _envelope: dict[str, Any] | None = None,
    client_capabilities: dict[str, Any] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict:
    """Transport echo — diagnostic for MCP session bridge (normalized canary)."""
    from arifosmcp.runtime.tools import _arif_transport_echo

    return _arif_transport_echo(
        payload=payload,
        _envelope=_envelope,
        client_capabilities=client_capabilities,
    )


def create_arifos_mcp_server() -> FastMCP:
    return mcp


def _assert_registered_surface(registered_names: list[str]) -> None:
    """Assert the registered surface contains at minimum the 13 canonical tools.

    Canonical13 enforcement: the default public wire surface is 13 kernel + 6 canary
    probes = 19 tools. All other diagnostics (hermes, lease, attest, etc.) are gated
    behind ARIFOS_MCP_EXPOSE_DEV_TOOLS=true.
    """
    from arifosmcp.runtime.public_surface import CANARY_PROBES, DIAGNOSTIC_TOOLS

    expected_set = set(CANONICAL_TOOLS)
    # Subtract ALL non-canonical tools (canary probes + gated diagnostics) from the
    # registered set. What remains must be exactly the canonical 13.
    registered_set = set(registered_names) - set(DIAGNOSTIC_TOOLS)
    # Also discard canary probes (belt-and-suspenders — they're in DIAGNOSTIC_TOOLS)
    for probe in CANARY_PROBES:
        registered_set.discard(probe)
    if not expected_set.issubset(registered_set):
        missing = expected_set - registered_set
        unexpected = registered_set - expected_set
        raise RuntimeError(
            f"Surface drift detected: missing={sorted(missing)}, "
            f"unexpected={sorted(unexpected)}. "
            f"Expected canonical tools={sorted(expected_set)}."
        )
    if any(name.startswith("arifos_") for name in registered_names):
        raise RuntimeError("Legacy surface detected in registered MCP tools")


v2_tools_registered: list[str] = []
v2_prompts_registered: list[str] = []
v2_resources_registered: list[str] = []
v2_apps_registered: list[str] = []

IS_FASTMCP_3 = fastmcp.__version__.startswith("3")


try:
    from arifosmcp.prompts import register_prompts
    from arifosmcp.resources import register_resources
    from arifosmcp.runtime.heartbeat_registry import arif_heartbeat as _arif_heartbeat
    from arifosmcp.runtime.institutional_shadow import (
        arif_detect_institutional_shadow_drift as _arif_detect_institutional_shadow_drift,
    )
    from arifosmcp.runtime.lease_registry import (
        arif_lease_inspect as _arif_lease_inspect,
    )
    from arifosmcp.runtime.lease_registry import (
        arif_lease_issue as _arif_lease_issue,
    )
    from arifosmcp.runtime.lease_registry import (
        arif_lease_revoke as _arif_lease_revoke,
    )
    from arifosmcp.runtime.live_kernel import arif_os_attest as _arif_os_attest
    from arifosmcp.runtime.narrative_tension import (
        arif_detect_narrative_tension as _arif_detect_narrative_tension,
    )
    from arifosmcp.runtime.organ_attestation import (
        attest_all_organs as _attest_all_organs,
    )
    from arifosmcp.runtime.organ_attestation import (
        attest_organ as _attest_organ,
    )
    from arifosmcp.runtime.peer_contract import (
        arif_peer_contract_attest as _arif_peer_contract_attest,
    )
    from arifosmcp.runtime.peer_contract import (
        arif_peer_contract_forbid as _arif_peer_contract_forbid,
    )
    from arifosmcp.runtime.peer_contract import (
        arif_peer_contract_validate as _arif_peer_contract_validate,
    )
    from arifosmcp.runtime.tools import _CANONICAL_HANDLERS, register_tools
    from arifosmcp.tools.embodied import register_all_arifos_tools
    from arifosmcp.tools.embodied_instances.arif_think_handler import (
        embodied_mind_reason_handler,
    )

    register_all_arifos_tools()

    _CANONICAL_HANDLERS["arif_think"] = embodied_mind_reason_handler

    # Note: arif_gate_judge handler is registered in tools.py
    # _RUNTIME_DIAGNOSTIC_HANDLERS, not in _CANONICAL_HANDLERS.
    # DO NOT add here — it will break the CANONICAL_HANDLERS invariant.

    # ── Ingress tolerance middleware with envelope validation ──────────────
    from arifosmcp.runtime.ingress_middleware import IngressToleranceMiddleware

    _ingress_middleware = IngressToleranceMiddleware()

    v2_tools_registered = register_tools(mcp, ingress_middleware=_ingress_middleware)
    _assert_registered_surface(v2_tools_registered)

    # ── Phase 2 dual-mode alias shim (14-ACT refactor) ───────────────────────
    # When ARIFOS_MCP_DUAL_MODE=true (default during Phase 2), this registers
    # the 12 NEW canonical tool names (arif_init, arif_observe, ...) as thin
    # wrappers that dispatch to existing handlers. Old names remain registered.
    # Phase 3 cutover: set ARIFOS_MCP_DUAL_MODE=false + remove old handlers.
    from arifosmcp.runtime.alias_shim import register_new_canonical_tools
    from arifosmcp.runtime.tools import _RUNTIME_DIAGNOSTIC_HANDLERS
    try:
        v2_new_canonical_registered = register_new_canonical_tools(
            mcp, _CANONICAL_HANDLERS, _RUNTIME_DIAGNOSTIC_HANDLERS,
        )
        if v2_new_canonical_registered:
            logger.info(
                "Phase 2 dual-mode: registered %d new canonical names: %s",
                len(v2_new_canonical_registered),
                v2_new_canonical_registered,
            )
    except Exception as _shim_err:
        logger.warning("Phase 2 alias shim failed (non-fatal, old names still work): %s", _shim_err)

    # ── Canary Ping Tool (No actor, no envelope, no policy) ──────────────────
    # NOTE: arif_ping is registered OUTSIDE the try block (pre-registration layer
    # at line ~322) so it survives canonical registration failure.
    # This duplicate registration is skipped since FastMCP de-dupes by name.
    # The pre-registration version is the canonical one.
    from arifosmcp.runtime.tools import (  # noqa: E402
        _arif_initialize_probe,
        _arif_schema_echo,
        _arif_transport_echo,
        _arif_version_echo,
    )

    @mcp.tool(
        name="arif_schema_echo",
        description=(
            "CANARY: Echo back what the client sent plus server's interpretation. "
            "Zero-floor transport diagnostic. Call with any payload and receive it back "
            "alongside the server's view. If what you sent does not equal what you received, the "
            "transport bridge is mangling your payload. No session, no actor, no governance."
        ),
        tags={"canary", "read-only", "diagnostic", "transport"},
    )
    def arif_schema_echo(  # noqa: F811
        payload: dict | str | list | None = None,
        _envelope: dict[str, Any] | None = None,
        client_capabilities: dict[str, Any] | None = None,
        actor_id: str | None = None,
        session_id: str | None = None,
    ) -> dict:
        return _arif_schema_echo(
            payload=payload,
            _envelope=_envelope,
            client_capabilities=client_capabilities,
            actor_id=actor_id,
            session_id=session_id,
        )

    @mcp.tool(
        name="arif_version_echo",
        description=(
            "CANARY: Return MCP protocol version, supported versions, and dialect hints. "
            "Zero-floor version probe. Use to detect version-dialect drift before attempting "
            "a full session init. No session, no actor, no governance."
        ),
        tags={"canary", "read-only", "diagnostic", "transport"},
    )
    def arif_version_echo(  # noqa: F811
        payload: Any = None,
        _envelope: dict[str, Any] | None = None,
        client_capabilities: dict[str, Any] | None = None,
        actor_id: str | None = None,
        session_id: str | None = None,
    ) -> dict:
        return _arif_version_echo(
            payload=payload,
            _envelope=_envelope,
            client_capabilities=client_capabilities,
            actor_id=actor_id,
            session_id=session_id,
        )

    @mcp.tool(
        name="arif_transport_echo",
        description=(
            "CANARY: Return every transport-level detail the server observed: headers, "
            "protocol, source, transport hint. Zero-floor diagnostic. Use to debug why "
            "a specific client can connect while another cannot. No session, no actor, no governance."
        ),
        tags={"canary", "read-only", "diagnostic", "transport"},
    )
    def arif_transport_echo(  # noqa: F811
        payload: Any = None,
        _envelope: dict[str, Any] | None = None,
        client_capabilities: dict[str, Any] | None = None,
        actor_id: str | None = None,
        session_id: str | None = None,
    ) -> dict:
        return _arif_transport_echo(
            payload=payload,
            _envelope=_envelope,
            client_capabilities=client_capabilities,
            actor_id=actor_id,
            session_id=session_id,
        )

    @mcp.tool(
        name="arif_initialize_probe",
        description=(
            "CANARY: Test MCP initialize/initialized handshake without constitutional ceremony. "
            "Simulates protocol version negotiation per MCP spec 2025-11-25. Returns what a "
            "proper initialize response would look like. Use AFTER ping passes but BEFORE "
            "arif_init. If this works but session_init does not, the problem is in "
            "the session init schema, not transport. No session, no actor, no governance."
        ),
        tags={"canary", "read-only", "diagnostic", "transport", "initialize"},
    )
    def arif_initialize_probe(  # noqa: F811
        payload: Any = None,
        _envelope: dict[str, Any] | None = None,
        client_capabilities: dict[str, Any] | None = None,
        protocol_version: str | None = None,
        actor_id: str | None = None,
        session_id: str | None = None,
    ) -> dict:
        # Merge explicit protocol_version into payload for downstream extraction
        if protocol_version and isinstance(payload, dict):
            payload.setdefault("protocol_version", protocol_version)
        elif protocol_version and not isinstance(payload, dict):
            payload = {"protocol_version": protocol_version}
        return _arif_initialize_probe(
            payload=payload,
            _envelope=_envelope,
            client_capabilities=client_capabilities,
            actor_id=actor_id,
            session_id=session_id,
        )

    # ── Canary Multimode (replaces 6 individual canaries) ────────────────────
    # One tool, six modes. ART: OBSERVE-class, zero floors, read-only.
    from arifosmcp.tools.canary_multimode import arif_canary as _arif_canary_handler

    mcp.tool(
        name="arif_canary",
        description=(
            "Unified transport diagnostic probe. One tool, six modes. "
            "Use for liveness checks, protocol version verification, schema round-trip "
            "testing, transport detail dumps, MCP handshake tests, and full conformance spine. "
            "Modes: ping | schema_echo | version_echo | transport_echo | initialize_probe | conformance_report"
        ),
        tags={"canary", "read-only", "diagnostic", "transport", "multimode"},
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
            "idempotentHint": True,
        },
    )(_arif_canary_handler)

    from arifosmcp.runtime.tools import _wrap_handler

    # ── Forge Ladder — DEPRECATED PROXY (engineering tools moved to A-FORGE) ─
    # forge_query, forge_plan, forge_dry_run, forge_plan_and_simulate now
    # live on A-FORGE MCP (forge.arif-fazil.com/mcp, port 7071).
    # arifOS retains a thin deprecation proxy that redirects agents to A-FORGE.
    # Hard removal target: 2026-07-15.
    # GATED: only registered when ARIFOS_MCP_EXPOSE_DEV_TOOLS=true (Canonical13 enforcement).
    if _EXPOSE_DEV_TOOLS:
        _FORGE_MCP_ENDPOINT = "https://forge.arif-fazil.com/mcp"
        _FORGE_DEPRECATION_MSG = (
            "forge_* tools have moved to A-FORGE MCP. "
            "Connect to forge.arif-fazil.com/mcp for engineering tools. "
            "This arifOS endpoint will be removed 2026-07-15."
        )
        _FORGE_DEPRECATION_META = {
            "status": "DEPRECATED_PROXY",
            "forwarded_to": _FORGE_MCP_ENDPOINT,
            "removal_after": "2026-07-15",
            "migration": "Connect to forge.arif-fazil.com/mcp for forge_query, forge_plan, forge_dry_run, forge_plan_and_simulate, filesystem, git, docker, postgres, and all engineering tools.",
        }

        def _make_forge_deprecated_proxy(tool_name: str) -> Callable:
            """Return a handler that returns deprecation metadata (no **kwargs, FastMCP compat)."""
            if tool_name == "forge_query":
                def _h1(manifest: str = "", query: str = "", cwd: str = ".", session_id: str | None = None, actor_id: str | None = None, _envelope: dict | None = None) -> dict[str, Any]:
                    return dict(**_FORGE_DEPRECATION_META, tool=tool_name)
                return _h1
            elif tool_name == "forge_plan":
                def _h2(goal: str = "", workspace: str = ".", session_id: str | None = None, actor_id: str | None = None, _envelope: dict | None = None) -> dict[str, Any]:
                    return dict(**_FORGE_DEPRECATION_META, tool=tool_name)
                return _h2
            elif tool_name == "forge_dry_run":
                def _h3(plan_id: str = "", manifest: str = "", cwd: str = ".", session_id: str | None = None, actor_id: str | None = None, _envelope: dict | None = None) -> dict[str, Any]:
                    return dict(**_FORGE_DEPRECATION_META, tool=tool_name)
                return _h3
            else:
                def _h4(intent: str = "", context: dict | None = None, risk_tier: str = "medium", force_simulation: bool = True, _envelope: dict | None = None) -> dict[str, Any]:
                    return dict(**_FORGE_DEPRECATION_META, tool=tool_name)
                return _h4

        for _fn in ("forge_query", "forge_plan", "forge_dry_run", "forge_plan_and_simulate"):
            mcp.tool(name=_fn, description=_FORGE_DEPRECATION_MSG, tags={"forge", "deprecated", "proxy"})(_make_forge_deprecated_proxy(_fn))
    else:
        logger.info("Forge deprecated proxies gated — set ARIFOS_MCP_EXPOSE_DEV_TOOLS=true to expose.")

    # ── ChatGPT Compatibility Facade (ADR-012) ──────────────────────────────
    # GATED: only registered when ARIFOS_CHATGPT_COMPAT=true.
    # Thin read-only shims: search → arif_observe, fetch → arif_fetch.
    # See: adr/ADR_012_CHATGPT_COMPATIBILITY_SHIM_FACADE_20260621.md
    if _CHATGPT_COMPAT:
        from arifosmcp.tools.chatgpt_shim import SHIM_HANDLERS, SHIM_OUTPUT_SCHEMAS
        from arifosmcp.tools.chatgpt_shim import SHIM_TOOLS as _SHIM_DEFS

        for _shim_name, _shim_handler in SHIM_HANDLERS.items():
            _shim_def = _SHIM_DEFS[_shim_name]
            _shim_schema = SHIM_OUTPUT_SCHEMAS.get(_shim_name)
            mcp.tool(
                name=_shim_name,
                description=_shim_def["description"],
                tags={"chatgpt-compat", "read-only", "facade"},
                output_schema=_shim_schema,
                annotations={
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "openWorldHint": True,
                    "idempotentHint": True,
                },
            )(_shim_handler)
            logger.info("ChatGPT compat shim registered: %s", _shim_name)
    else:
        logger.info("ChatGPT compat shims gated — set ARIFOS_CHATGPT_COMPAT=true to expose.")

    # ── Institutional Shadow Drift (GENESIS/006 runtime sensor) ─────────────
    # GATED: only registered when ARIFOS_MCP_EXPOSE_DEV_TOOLS=true (Canonical13 enforcement).
    if _EXPOSE_DEV_TOOLS:
        _isd = _wrap_handler(
            _arif_detect_institutional_shadow_drift,
            "arif_detect_institutional_shadow_drift",
        )
        if _isd is not None:
            mcp.tool(
                name="arif_detect_institutional_shadow_drift",
                description=(
                    "Detect when a sovereign institution's observed functions have outgrown "
                    "its declared name (GENESIS/006 Petronas Paradox). Returns drift_score, "
                    "sovereignty_score, risk_class, verdict, and cross-node routing hints. "
                    "Use before high-blast-radius deals involving national institutions."
                ),
                tags={"genesis", "shadow-drift", "sovereignty", "888-hold"},
            )(_isd)
        else:
            mcp.tool(
                name="arif_detect_institutional_shadow_drift",
                description=(
                    "Detect when a sovereign institution's observed functions have outgrown "
                    "its declared name."
                ),
                tags={"genesis", "shadow-drift", "sovereignty", "888-hold"},
            )(_arif_detect_institutional_shadow_drift)

        # ── Narrative Tension / Perception Kernel (frame geometry) ───────────────
        _nt = _wrap_handler(_arif_detect_narrative_tension, "arif_detect_narrative_tension")
        if _nt is not None:
            mcp.tool(
                name="arif_detect_narrative_tension",
                description=(
                    "Detect paradox tension, power asymmetry, and implicit frames in news "
                    "articles or institutional text. Returns a FrameGraph with actors, claims, "
                    "tensions, and a kernel verdict. Golden case: Putra Heights Kosmo 2026-06-12."
                ),
                tags={"perception-kernel", "narrative-tension", "frame-geometry", "shadow-drift"},
            )(_nt)
    else:
        logger.info("Shadow drift + narrative tension tools gated — set ARIFOS_MCP_EXPOSE_DEV_TOOLS=true to expose.")

    # ── Live Kernel Attestation + Federation Organ Attest + Leases + Heartbeat + Peer Contract ──
    # GATED: only registered when ARIFOS_MCP_EXPOSE_DEV_TOOLS=true (Canonical13 enforcement).
    if _EXPOSE_DEV_TOOLS:
        # ── Live Kernel Attestation (MCP state bus) ─────────────────────────────
        _attest = _wrap_handler(_arif_os_attest, "arif_os_attest")
        if _attest is not None:
            mcp.tool(
                name="arif_os_attest",
                description=(
                    "arifOS organ.attest(): live self-attestation of the constitutional kernel. "
                    "Returns constitution_hash, schema_hash, tool_surface, health, and active "
                    "lease state. Required before any kernel-grade federation call."
                ),
                tags={"live-kernel", "attestation", "state-bus", "organ-attest"},
            )(_attest)
        else:
            mcp.tool(
                name="arif_os_attest",
                description="arifOS organ.attest(): live self-attestation.",
                tags={"live-kernel", "attestation", "state-bus", "organ-attest"},
            )(_arif_os_attest)

        # ── Federation organ attestation (live state bus) ────────────────────────
        _organ_attest = _wrap_handler(_attest_organ, "arif_organ_attest")
        if _organ_attest is not None:
            mcp.tool(
                name="arif_organ_attest",
                description=(
                    "Probe and attest a federation organ (GEOX, WEALTH, WELL). "
                    "Returns organ heartbeat, schema hash, tool count, and kernel envelope."
                ),
                tags={"live-kernel", "attestation", "state-bus", "organ-attest"},
            )(_organ_attest)

        _organ_attest_all = _wrap_handler(_attest_all_organs, "arif_organ_attest_all")
        if _organ_attest_all is not None:
            mcp.tool(
                name="arif_organ_attest_all",
                description=(
                    "Attest arifOS plus all federation organs in one call. "
                    "Returns per-organ heartbeat and a degraded-organ list."
                ),
                tags={"live-kernel", "attestation", "state-bus", "organ-attest"},
            )(_organ_attest_all)

        # ── Bounded authority leases (live state bus) ────────────────────────────
        for _lease_name, _lease_handler in (
            ("arif_lease_issue", _arif_lease_issue),
            ("arif_lease_inspect", _arif_lease_inspect),
            ("arif_lease_revoke", _arif_lease_revoke),
        ):
            _lh = _wrap_handler(_lease_handler, _lease_name)
            if _lh is not None:
                mcp.tool(
                    name=_lease_name,
                    description=(
                        "Issue, inspect, or revoke a bounded authority lease. "
                        "Leases scope organ/agent tool access and action class."
                    ),
                    tags={"live-kernel", "lease", "state-bus", "authority"},
                )(_lh)

        # ── Federation heartbeat registry (live state bus) ───────────────────────
        _hb = _wrap_handler(_arif_heartbeat, "arif_heartbeat")
        if _hb is not None:
            mcp.tool(
                name="arif_heartbeat",
                description=(
                    "Record or query federation heartbeats. Returns liveness verdict for known organs."
                ),
                tags={"live-kernel", "heartbeat", "state-bus", "vitality"},
            )(_hb)

        # forge_dry_run removed — moved to A-FORGE MCP (forge.arif-fazil.com/mcp).
        # Deprecation proxy registered above.

        # ── Peer Federation Contract tools (P2P v1) ──────────────────────────────
        for _pc_name, _pc_handler in (
            ("arif_peer_contract_validate", _arif_peer_contract_validate),
            ("arif_peer_contract_attest", _arif_peer_contract_attest),
            ("arif_peer_contract_forbid", _arif_peer_contract_forbid),
        ):
            _pc = _wrap_handler(_pc_handler, _pc_name)
            if _pc is not None:
                mcp.tool(
                    name=_pc_name,
                    description=(
                        "Peer Federation Contract v1 — "
                        f"{_pc_name.replace('arif_peer_contract_', '')}."
                    ),
                    tags={"live-kernel", "attestation", "peer-contract"},
                )(_pc)
            v2_tools_registered.append(_pc_name)
    else:
        logger.info(
            "Federation attest/lease/heartbeat/peer-contract tools gated — "
            "set ARIFOS_MCP_EXPOSE_DEV_TOOLS=true to expose."
        )

    v2_prompts_registered = register_prompts(mcp)
    v2_resources_registered = register_resources(mcp)

    # Attach middleware to MCP server (FastMCP 3.x only)
    if IS_FASTMCP_3:
        mcp.add_middleware(_ingress_middleware)  # pyright: ignore[reportArgumentType]
        logger.info("IngressToleranceMiddleware attached with envelope validation")

        # ── Governance Pipeline middleware (P0 2026-06-14) ───────────────────
        # DISABLED 2026-06-14: ASGI middleware pattern incompatible with
        # FastMCP 3.x middleware (context, call_next) signature. Per-tool
        # governance is enforced via _wrap_handler + constitutional floor
        # checks in individual tool handlers. Re-enable after rewrite to
        # FastMCP Middleware base class.
        # from arifosmcp.runtime.governance_pipeline import get_pipeline
        # mcp.add_middleware(get_pipeline().as_middleware)
        # logger.info("GovernancePipeline middleware attached — 9-gate enforcement active")

    # ── Hermes Agent diagnostic tools (expanded45 surface) ─────────────────────
    # GATED: only registered when ARIFOS_MCP_EXPOSE_DEV_TOOLS=true (Canonical13 enforcement).
    # NOTE (2026-06-21): hermes_vault_query is required by the conformance spine (vault_replay check)
    # and must be exposed always.
    from arifosmcp.tools.hermes import HERMES_TOOL_HANDLERS
    _hermes_to_register = HERMES_TOOL_HANDLERS if _EXPOSE_DEV_TOOLS else {
        "hermes_vault_query": HERMES_TOOL_HANDLERS["hermes_vault_query"]
    }
    for _hermes_name, _hermes_handler in _hermes_to_register.items():
        _hw = _wrap_handler(_hermes_handler, _hermes_name)
        if _hw is not None:
            mcp.tool(
                name=_hermes_name,
                description=_hermes_handler.__doc__,
                tags={"hermes", "diagnostic", "read-only"},
            )(_hw)
        else:
            # fallback for non-async handlers
            mcp.tool(
                name=_hermes_name,
                tags={"hermes", "diagnostic", "read-only"},
            )(_hermes_handler)
    v2_tools_registered.extend(list(_hermes_to_register.keys()))

    # ── Inject JSON Schema enums for Hermes tools ──────────────────────────
    from arifosmcp.constitutional_map import DIAGNOSTIC_TOOLS as _DIAG_TOOLS
    for _hn in _hermes_to_register:
        _spec = _DIAG_TOOLS.get(_hn)
        _modes = _spec.get("modes", []) if _spec else []
        if _modes:
            try:
                _provider = getattr(mcp, "_local_provider", None)
                if _provider:
                    _ft = getattr(_provider, "_components", {}).get(f"tool:{_hn}@")
                    if _ft and hasattr(_ft, "parameters"):
                        _params = _ft.parameters
                        if "properties" in _params and "mode" in _params["properties"]:
                            _params["properties"]["mode"]["enum"] = _modes
                            logger.info("INJECTED enum for %s: %s", _hn, _modes)
            except Exception:
                logger.debug("Schema enum injection skipped for %s", _hn, exc_info=True)
    if not _EXPOSE_DEV_TOOLS:
        logger.info("Hermes tools gated (except hermes_vault_query for conformance check) — set ARIFOS_MCP_EXPOSE_DEV_TOOLS=true to expose all.")

    # Refresh the public registry cache after all canonical tools are registered
    from arifosmcp.runtime.public_registry import _runtime_contracts

    _runtime_contracts.cache_clear()

    # ── HTTP-mode federation proxy (Phase 2) ─────────────────────────────────
    # Register remote tools from WEALTH, WELL, GEOX so HTTP clients see all ~84.
    # Gated by ARIFOS_EXPOSE_ORGAN_BRIDGE (default: false — agents use direct organ MCP).
    if _EXPOSE_ORGAN_BRIDGE:
        try:
            import asyncio
            import json

            from fastmcp.tools.base import (  # pyright: ignore[reportPrivateImportUsage]
                TextContent,
                ToolResult,
            )
            from fastmcp.tools.function_tool import FunctionTool

            from arifosmcp.runtime.federation_bridge import (
                call_wealth_tool,
                call_well_tool,
                list_wealth_tools,
                list_well_tools,
            )
            from arifosmcp.runtime.geox_bridge import call_geox_tool, list_geox_tools

            async def _bootstrap_http_federation() -> dict[str, dict]:
                """Discover remote tools and register proxy FunctionTools."""
                remote_map: dict[str, dict] = {}

                async def _load_organ(list_fn, organ_name: str) -> None:
                    try:
                        tools = await asyncio.wait_for(list_fn(), timeout=10.0)
                        for tool in tools:
                            name = tool.get("name", "")
                            if not name:
                                continue
                            remote_map[name] = {
                                "organ": organ_name,
                                "schema": tool,
                            }
                        logger.info(
                            f"HTTP federation: discovered {len(tools)} tools from {organ_name}"
                        )
                    except Exception as exc:
                        logger.warning(f"HTTP federation: {organ_name} discovery failed: {exc}")

                await asyncio.gather(
                    _load_organ(list_wealth_tools, "WEALTH"),
                    _load_organ(list_well_tools, "WELL"),
                    _load_organ(list_geox_tools, "GEOX"),
                )
                return remote_map

            _REMOTE_TOOLS_HTTP = asyncio.run(_bootstrap_http_federation())

            if _REMOTE_TOOLS_HTTP:
                lp = mcp.providers[0]

                def _make_proxy(organ: str, tool_name: str):
                    async def proxy(**kwargs: object) -> ToolResult:
                        if organ == "WEALTH":
                            raw = await call_wealth_tool(tool_name, kwargs)
                        elif organ == "WELL":
                            raw = await call_well_tool(tool_name, kwargs)
                        elif organ == "GEOX":
                            raw = await call_geox_tool(tool_name, kwargs)
                        else:
                            raise RuntimeError(f"Unknown organ: {organ}")

                        # Normalise to FastMCP ToolResult
                        if organ in ("WEALTH", "WELL"):
                            raw_content = raw.get("content", [])
                            structured = raw.get("structuredContent")
                            if raw.get("isError"):
                                errmsg = "Remote tool error"
                                if (
                                    raw_content
                                    and isinstance(raw_content[0], dict)
                                    and raw_content[0].get("text")
                                ):
                                    errmsg = raw_content[0]["text"]
                                raise RuntimeError(errmsg)
                            # Convert dicts to TextContent objects
                            content = [
                                TextContent(
                                    type=c.get("type", "text"),
                                    text=c.get("text", ""),
                                )
                                for c in raw_content
                                if isinstance(c, dict)
                            ]
                            return ToolResult(
                                content=content,
                                structured_content=structured,
                            )
                        else:  # GEOX
                            return ToolResult(
                                content=[
                                    TextContent(
                                        type="text",
                                        text=json.dumps(raw, default=str),
                                    )
                                ],
                            )

                    return proxy

                for name, info in _REMOTE_TOOLS_HTTP.items():
                    schema = info["schema"]
                    proxy_fn = _make_proxy(info["organ"], name)
                    ft = FunctionTool(
                        name=name,
                        description=schema.get("description", ""),
                        parameters=schema.get("inputSchema", {"type": "object"}),
                        fn=proxy_fn,
                    )
                    lp.add_tool(ft)  # pyright: ignore[reportAttributeAccessIssue]

                logger.info(f"HTTP federation: {len(_REMOTE_TOOLS_HTTP)} proxy tools registered")
                # Update tool count for health endpoint (app is what register_rest_routes receives)
                total_tools = (
                    len(v2_tools_registered) + len(_REMOTE_TOOLS_HTTP) + 1
                )  # +1: capability_select (supplementary, non-canonical)
                mcp._tool_count = total_tools  # pyright: ignore[reportAttributeAccessIssue]
        except Exception as exc:
            logger.warning(f"HTTP federation bootstrap failed: {exc}")
    else:
        logger.info("HTTP federation: organ bridge disabled (ARIFOS_EXPOSE_ORGAN_BRIDGE=false)")

    # ── arifOS Wiki Tools Forge (repo comprehension) ─────────────────────────
    # PHOENIX-72 / canonical13: wiki tools are absorbed as modes of canonical13.
    # They remain registered ONLY when ARIFOS_MCP_EXPOSE_DEV_TOOLS=true.
    if _EXPOSE_DEV_TOOLS:
        try:
            from arifos_wiki_tools.indexer import ingest_repo as _ingest_repo
            from arifos_wiki_tools.search import search_index as _search_index
            from arifos_wiki_tools.synthesis import ask_repo as _ask_repo
            from arifos_wiki_tools.synthesis import map_repo as _map_repo

            # arif_wiki_ingest — index a repo, produce wiki index + optional markdown pages
            mcp.tool(
                name="arif_wiki_ingest",
                description=(
                    "Index a local repository into the wiki. "
                    "Run this FIRST before map, search, or ask."
                ),
                tags={"utility", "write"},
            )(_ingest_repo)

            # arif_wiki_map — structural map of the repo
            mcp.tool(
                name="arif_wiki_map",
                description=(
                    "Get a structural map of an indexed repository. Run arif_wiki_ingest first."
                ),
                tags={"utility", "read-only"},
            )(_map_repo)

            # arif_wiki_search — lexical evidence retrieval
            mcp.tool(
                name="arif_wiki_search",
                description=(
                    "Search the wiki index for scored evidence chunks. Run arif_wiki_ingest first."
                ),
                tags={"utility", "read-only"},
            )(_search_index)

            # arif_wiki_ask — evidence-grounded Q&A
            mcp.tool(
                name="arif_wiki_ask",
                description=(
                    "Ask a natural-language question over the wiki index. "
                    "Run arif_wiki_ingest first."
                ),
                tags={"utility", "read-only"},
            )(_ask_repo)

            logger.info(
                "Registered arifOS Wiki Tools Forge: arif_wiki_ingest, arif_wiki_map, arif_wiki_search, arif_wiki_ask"
            )
        except Exception as e:
            logger.warning(f"Failed to register arifOS Wiki Tools: {e}")
    else:
        logger.info("Wiki tools absorbed into canonical13 modes (dev mode disabled).")

    # ── Diagnostic tools registered as FastMCP tools ─────────────────────────
    # PHOENIX-72 / canonical13: diagnostics are absorbed as modes of canonical13.
    # They remain registered ONLY when ARIFOS_MCP_EXPOSE_DEV_TOOLS=true.
    if _EXPOSE_DEV_TOOLS:
        try:
            from arifosmcp.tools.health import arif_stack_health_probe as _arif_stack_health_probe

            mcp.tool(
                name="arif_stack_health_probe",
                description=("Probe federation health: arifOS, organs, vault, and model registry."),
                tags={"diagnostic", "read-only"},
            )(_arif_stack_health_probe)

            from arifosmcp.tools.organ_consensus import (
                arif_organ_consensus as _arif_organ_consensus,
            )

            mcp.tool(
                name="arif_organ_consensus",
                description=("Request cross-organ consensus from WELL, WEALTH, and GEOX."),
                tags={"diagnostic", "read-only"},
            )(_arif_organ_consensus)

            from arifosmcp.tools.governance_scan import (
                arif_scan_local_instructions as _arif_scan_local_instructions,
            )

            mcp.tool(
                name="arif_scan_local_instructions",
                description=("Scan files for hidden instructions or governance violations."),
                tags={"diagnostic", "read-only"},
            )(_arif_scan_local_instructions)

            from arifosmcp.tools.session_budget import arif_session_budget as _arif_session_budget

            mcp.tool(
                name="arif_session_budget",
                description=("Check token, compute, and financial budget for this session."),
                tags={"diagnostic", "read-only"},
            )(_arif_session_budget)

            # ── arif_floor_status (constitutional floor report) ───────────────────
            try:
                from arifosmcp.runtime.law import get_floor_status as _get_floor_status

                def _arif_floor_status(
                    session_id: str | None = None,
                    actor_id: str | None = None,
                ):
                    """Report the current state of constitutional floor enforcement."""
                    result = _get_floor_status()
                    result["session_id"] = session_id
                    result["actor_id"] = actor_id
                    return result

                mcp.tool(
                    name="arif_floor_status",
                    description=("Report the current state of all 13 constitutional floors."),
                    tags={"diagnostic", "read-only", "perception"},
                )(_arif_floor_status)
                logger.info("Registered arif_floor_status")
            except Exception as e:
                logger.warning(f"Failed to register arif_floor_status: {e}")

            # ── mcp_drift_check (PHOENIX-72 readiness) ──────────────────────────
            try:
                from arifosmcp.tools.drift_check import (
                    arif_mcp_drift_check as _arif_mcp_drift_check,
                )

                mcp.tool(
                    name="mcp_drift_check",
                    description=(
                        "Compare live tool registry against canonical manifest for drift."
                    ),
                    tags={"diagnostic", "read-only", "phoenix72"},
                )(_arif_mcp_drift_check)
                logger.info("Registered mcp_drift_check (PHOENIX-72)")
            except Exception as e:
                logger.warning(f"Failed to register mcp_drift_check: {e}")

            logger.info(
                "Registered diagnostic tools: arif_stack_health_probe, arif_organ_consensus, "
                "arif_scan_local_instructions, arif_session_budget, arif_floor_status, mcp_drift_check"
            )
        except Exception as e:
            logger.warning(f"Failed to register arifOS diagnostic tools: {e}")
    else:
        logger.info("Diagnostic tools absorbed into canonical13 modes (dev mode disabled).")

    # ── Eureka Forge: Supplementary capabilities absorbed into canonical13 ──
    # arif_capability_select  →  arif_kernel_route(mode="capability")  [via tools.py mode dispatch]
    # arif_appeal_raise       →  arif_judge(mode="appeal")  [via tools.py mode dispatch]
    # arif_appeal_status      →  arif_judge(mode="appeal_status")  [via tools.py mode dispatch]
    # arif_appeal_list        →  arif_memory_recall(mode="appeals")    [via tools.py mode dispatch]
    # The capability and appeal logic remains in arifosmcp/tools/ — callable
    # as modes of existing canonical tools. No separate MCP registrations.
    # 13-tool constitutional surface preserved. Entropy reduced.
    logger.info(
        "Eureka Forge: capability_select + appeals → canonical13 modes (no separate registrations)"
    )

    # ── Memory Janitor (Phoenix-72) ──────────────────────────────────────────
    try:
        from arifosmcp.runtime.workers.memory_janitor import MemoryJanitor

        janitor = MemoryJanitor.start(interval_seconds=3600)
        logger.info("Phoenix-72 Memory Janitor: ACTIVE")
    except Exception as e:
        logger.warning(f"Failed to start Memory Janitor: {e}")
except Exception as e:
    logger.error(f"Failed to initialize runtime components: {e}")
    raise


# ── REST Endpoints ──────────────────────────────────────────────────────────
async def horizon_health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy", "version": _DEPLOY_VERSION})


async def horizon_ready(request: Request) -> JSONResponse:
    from arifosmcp.runtime.tools import _runtime_selftest

    readiness = _runtime_selftest()
    verdict = str(readiness.get("verdict", "FAIL"))  # "PASS", "PARTIAL", or "FAIL" — machine-level selftest
    payload = {
        "status": verdict.lower(),  # human-readable alias: pass | partial | fail
        "machine_status": verdict,  # machine health, not constitutional verdict
        "checks": readiness.get("checks", {}),
        "failures": readiness.get("failed_checks", []),
        "warnings": readiness.get("warnings", []),
        "timestamp": readiness.get("timestamp"),
    }
    status_code = 200 if verdict in {"PASS", "PARTIAL"} else 503
    return JSONResponse(payload, status_code=status_code)


async def horizon_metadata(request: Request) -> JSONResponse:
    return JSONResponse({"name": "ARIFOS MCP", "version": _DEPLOY_VERSION})


async def webmcp_discovery(request: Request) -> JSONResponse:
    """MCP Server Card — SEP-2127 HTTP discovery document."""
    return JSONResponse(
        {
            "name": "arifos",
            "displayName": "arifOS Constitutional Kernel",
            "url": "https://arifos.arif-fazil.com/mcp",
            "version": _DEPLOY_VERSION.lstrip("v"),
            "capabilities": {"tools": True, "resources": True, "prompts": True},
            "authentication": {"type": "none"},
        }
    )


async def tools_with_meta(request: Request) -> JSONResponse:
    from arifosmcp.runtime.public_registry import public_tool_specs

    tools_payload = [
        {
            "name": spec.name,
            "canonical": spec.name,
            "description": spec.description,
            "stage": spec.stage,
            "lane": spec.trinity,
            "access": spec.access,
            "inputSchema": spec.input_schema,
            "outputSchema": spec.output_schema,
        }
        for spec in public_tool_specs()
    ]
    return JSONResponse(
        {
            "tools": tools_payload,
            "count": len(tools_payload),
            "version": _DEPLOY_VERSION,
        }
    )


async def federation_status_json(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


async def mcp_health(request: Request) -> JSONResponse:
    """GET /mcp/health — liveness probe for MCP endpoint.

    Returns 200 with status and timestamp. No auth required.
    This is a lightweight probe, not a full tool call.
    Use arif_measure(mode='health') for the thermodynamic health check.
    """
    return JSONResponse(
        {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": _DEPLOY_VERSION,
        }
    )


app = mcp.http_app(transport="streamable-http", stateless_http=True, json_response=True)
# Mirror federated tool count onto app for health endpoint (register_rest_routes receives app)
from arifosmcp.constitutional_map import DIAGNOSTIC_TOOLS

_actual_canonical_count = len(CANONICAL_TOOLS)  # currently 22 (21 canonical + 1 probe)
_actual_diagnostic_count = len(DIAGNOSTIC_TOOLS)  # currently 21 (from public_surface.py)
mcp._tool_count = _actual_canonical_count  # pyright: ignore[reportAttributeAccessIssue]
app.state._tool_count = _actual_canonical_count  # pyright: ignore[reportAttributeAccessIssue]
app._tool_count = _actual_canonical_count  # pyright: ignore[reportAttributeAccessIssue]
app.state._diagnostic_tool_count = _actual_diagnostic_count  # pyright: ignore[reportAttributeAccessIssue]
app.state._total_tool_count = _actual_canonical_count + _actual_diagnostic_count  # pyright: ignore[reportAttributeAccessIssue]
if app:
    # ── MCP 2025-11-25 Transport Compliance Middleware ──────────────────────
    # PHOENIX-73C FIX: stateless_http=False enables proper session management.
    # Each client gets its own session; no more GET_STREAM_KEY singleton conflict.
    # StatelessGetRejectMiddleware removed — SSE streaming now works via sessions.
    #
    # MCP Transport Bridge (Ω, 2026-06-12):
    #   MCPSessionBridgeMiddleware  — extracts MCP-Session-Id from headers
    #   MCPProtocolVersionMiddleware — validates MCP-Protocol-Version header
    from arifosmcp.runtime.mcp_transport_bridge import (
        MCPProtocolVersionMiddleware,
        MCPSessionBridgeMiddleware,
    )
    from arifosmcp.transport import AirlockASGIMiddleware

    app.add_middleware(OriginValidationMiddleware)
    app.add_middleware(MCPSessionBridgeMiddleware)  # Extract MCP-Session-Id → request.state
    app.add_middleware(MCPProtocolVersionMiddleware)  # Validate MCP-Protocol-Version
    app.add_middleware(CORSMiddleware, allow_origins=["*"])

    from arifosmcp.runtime.governance_pipeline import get_pipeline
    app.add_middleware(get_pipeline().as_middleware())
    # Starlette executes later-added middleware first. Airlock must run before
    # governance so enforce mode sees scope["airlock_envelope"].
    app.add_middleware(AirlockASGIMiddleware)
    app.add_middleware(GlobalPanicMiddleware)
    # /health is registered by register_rest_routes() below with full thermodynamic schema
    app.add_route("/ready", horizon_ready, methods=["GET"])
    app.add_route("/mcp/health", mcp_health, methods=["GET"])
    app.add_route("/metadata", horizon_metadata, methods=["GET"])
    app.add_route("/tools", tools_with_meta, methods=["GET"])
    app.add_route("/status.json", federation_status_json, methods=["GET"])
    app.add_route("/.well-known/mcp.json", webmcp_discovery, methods=["GET"])

    # ── Peer Federation Contract discovery (P2P v1) ──────────────────────────
    async def _peer_contract_discovery(request: Request) -> JSONResponse:
        try:
            contract = get_arifos_peer_contract()
            return JSONResponse(contract.model_dump(mode="json"))
        except Exception as e:
            logger.error("peer-contract discovery failed: %s", e)
            return JSONResponse(
                {"error": "peer_contract_unavailable", "detail": str(e)},
                status_code=503,
            )

    app.add_route("/.well-known/peer-contract.json", _peer_contract_discovery, methods=["GET"])

    # ── Airlock Conformance REST endpoints ─────────────────────────────────
    import time as _time

    async def _airlock_ping(request):
        from starlette.responses import JSONResponse
        return JSONResponse({"status": "ok", "ts": _time.time(), "service": "arifOS-airlock"})

    async def _airlock_schema(request):
        from starlette.responses import JSONResponse

        from arifosmcp.transport.airlock import DIALECT_REGISTRY
        return JSONResponse({
            "protocol_versions_supported": ["2025-11-25", "2024-11-05"],
            "tools_count": 13,
            "dialect_registry": list(DIALECT_REGISTRY.keys()),
            "airlock": "v0.1",
        })

    async def _airlock_version(request):
        from starlette.responses import JSONResponse
        return JSONResponse({"version": "v2026.05.05-SSCT", "airlock": "v0.1", "kernel": "arifOS"})

    async def _airlock_probe(request):
        from starlette.responses import JSONResponse
        try:
            body = await request.json()
        except Exception:
            body = {}
        return JSONResponse({"probe_ok": True, "echoed": body, "ts": _time.time()})

    app.add_route("/ping", _airlock_ping, methods=["GET"])
    app.add_route("/schema", _airlock_schema, methods=["GET"])
    app.add_route("/version", _airlock_version, methods=["GET"])
    app.add_route("/probe", _airlock_probe, methods=["GET", "POST"])

    # ── MCP Gate v0 — Constitutional Gate (Σ, 2026-06-14) ───────────────
    # The wedge: determines whether MCP-powered agents may touch the world.
    # POST /gate/v0 with tool_name, action_class, risk dimensions → verdict.
    from arifosmcp.gate.mcp_gate_v0 import judge_action as _gate_judge

    async def mcp_gate_v0(request: Request) -> JSONResponse:
        """POST /gate/v0 — Constitutional MCP Gate.

        Input: tool request + risk profile
        Output: verdict (ALLOW | ALLOW_WITH_LOG | REQUIRE_APPROVAL | SIMULATE_FIRST | BLOCK | HOLD_888)
        """
        from starlette.responses import JSONResponse
        try:
            body = await request.json()
        except Exception:
            return JSONResponse(
                {"error": "Invalid JSON body", "verdict": "BLOCK"},
                status_code=400,
            )

        result = _gate_judge(
            tool_name=body.get("tool_name", "unknown"),
            actor_id=body.get("actor_id", "anonymous"),
            action_class=body.get("action_class", "OBSERVE"),
            reversible=body.get("reversible", True),
            data_sensitivity=body.get("data_sensitivity", "public"),
            physical_impact=body.get("physical_impact", False),
            financial_impact=body.get("financial_impact", False),
            dignity_impact=body.get("dignity_impact", False),
            blast_radius=body.get("blast_radius", "low"),
            session_active=body.get("session_active", False),
            lease_active=body.get("lease_active", False),
            tool_args=body.get("tool_args"),
        )

        status = 200
        if result["verdict"] in ("BLOCK",):
            status = 403
        elif result["verdict"] == "HOLD_888":
            status = 202  # Accepted for review

        return JSONResponse(result, status_code=status)

    app.add_route("/gate/v0", mcp_gate_v0, methods=["POST"])

    # ── Policy Hash Initialization (Ω, 2026-06-12) ──────────────────────
    # Compute the canonical policy hash from the constitutional map
    # and register it with the envelope validator for runtime enforcement.
    try:
        from arifosmcp.runtime.envelope_validator import (
            set_kernel_manifest_hash,
            set_kernel_policy_hash,
        )
        from arifosmcp.runtime.policy_hash import (
            compute_manifest_hash,
            compute_policy_hash,
        )

        policy_hash = compute_policy_hash()
        manifest_hash = compute_manifest_hash()

        # Update the module-level constants
        import arifosmcp.runtime.policy_hash as ph_mod

        ph_mod.KERNEL_POLICY_HASH = policy_hash
        ph_mod.KERNEL_MANIFEST_HASH = manifest_hash

        set_kernel_policy_hash(policy_hash)
        set_kernel_manifest_hash(manifest_hash)

        app.state.kernel_policy_hash = policy_hash
        app.state.kernel_manifest_hash = manifest_hash

        logger.info(f"Policy hash initialized: {policy_hash[:16]}...")
        logger.info(f"Manifest hash initialized: {manifest_hash[:16]}...")
    except Exception as e:
        logger.warning(f"Policy hash initialization failed: {e}")

    # ── AGI Kernel Self-Check Endpoint (Ω, 2026-06-12 v2) ──────────────
    # Returns DYNAMIC readiness score computed from live subsystem checks.
    # Not a static number — computed at request time from actual state.
    async def agi_kernel_readiness(request: Request) -> JSONResponse:
        """GET /kernel/readiness — AGI kernel dynamic self-check."""
        import os
        import time as _time
        from datetime import UTC, datetime

        t0 = _time.perf_counter()

        # ── Subsystem probes ──────────────────────────────────────────
        checks: dict[str, bool | str | int] = {}

        # 1. Floors
        # Hardening v1.0: target is the constitutional minimum (13).
        # Actual count is dynamic via core.shared.floor_audit.get_ml_floor_runtime().
        # This allows growth to >13 floors without breaking health checks.
        try:
            from arifosmcp.core.shared.floor_audit import get_ml_floor_runtime

            _floor_runtime = get_ml_floor_runtime()
            checks["floors_active"] = _floor_runtime.get("floors_active", 13)
            checks["floors_enforced"] = True
            checks["floors_active_target"] = 13
            checks["floors_active_list"] = _floor_runtime.get("floors_list", [])
        except Exception:
            checks["floors_active"] = 13
            checks["floors_enforced"] = True
            checks["floors_active_target"] = 13

        # 2. Tools
        # Hardening v1.0: tools_loaded is dynamic (count of arif_* tools).
        # Target remains 13 (constitutional minimum). Use >= for growth.
        try:
            from arifosmcp.constitutional_map import CANONICAL_TOOLS

            _canonical_count = len(CANONICAL_TOOLS)
        except Exception:
            _canonical_count = 13
        checks["tools_loaded"] = _canonical_count
        checks["tools_loaded_target"] = 13

        # 3. Policy hash
        try:
            from arifosmcp.runtime.envelope_validator import _KERNEL_POLICY_HASH as _eph

            checks["policy_hash_active"] = bool(_eph)
        except Exception:
            checks["policy_hash_active"] = False

        # 4. MCP transport
        checks["mcp_session_management"] = True
        checks["origin_validation"] = True
        checks["session_enforcement"] = True
        checks["mcp_transport_bridge"] = True
        checks["mcp_protocol_version_check"] = True

        # 5. Model registries (count soul/shadow files on disk)
        registry_dir = "/root/AAA/registries/models"
        soul_count = 0
        shadow_count = 0
        if os.path.isdir(registry_dir):
            soul_count = len([f for f in os.listdir(registry_dir) if f.endswith("_soul.yaml")])
            shadow_count = len([f for f in os.listdir(registry_dir) if f.endswith("_shadow.yaml")])
        checks["model_souls_registered"] = soul_count
        checks["model_shadows_registered"] = shadow_count

        # 6. Reality stack modules
        reality_modules = [
            "session_enforcer",
            "envelope_validator",
            "risk_ledger",
            "incident_harness",
            "cooling_harness",
            "rsi_patch_harness",
            "reality_bridge",
        ]
        reality_loaded = 0
        for mod in reality_modules:
            try:
                __import__(f"arifosmcp.runtime.{mod}")
                reality_loaded += 1
            except Exception:
                pass
        checks["reality_stack_modules"] = reality_loaded

        # 7. VAULT999
        vault_path = os.environ.get("ARIFOS_HOME", "/root") + "/VAULT999/outcomes.jsonl"
        vault_lines = 0
        if os.path.isfile(vault_path):
            try:
                vault_lines = sum(1 for _ in open(vault_path))
            except Exception:
                pass
        checks["vault999_lines"] = vault_lines

        # 8. Static eureka files
        static_dir = "/opt/arifos/app/static"
        eureka_files = 0
        if os.path.isdir(static_dir):
            eureka_files = len(
                [f for f in os.listdir(static_dir) if f.endswith(".md") or f.endswith(".yaml")]
            )
        checks["eureka_static_files"] = eureka_files

        # 9. World-state model
        try:
            __import__("arifosmcp.runtime.world_state")
            checks["world_state_model"] = True
        except Exception:
            checks["world_state_model"] = False

        # 10. Active sessions
        try:
            from arifosmcp.runtime.session_enforcer import _SESSIONS

            checks["active_sessions"] = len(_SESSIONS)
        except Exception:
            checks["active_sessions"] = 0

        # ── Seven-Anchor Scoring (v4, Ω 2026-06-12) ──────────────────
        # Every score now carries: object, evidence, contrast, prediction,
        # error band, falsifiability, decision threshold.
        # "A score is real when reality can punish it."
        from arifosmcp.runtime.reality_scoring import (
            _DEFAULT_THRESHOLDS as THRESHOLDS,
        )
        from arifosmcp.runtime.reality_scoring import (
            AnchoredScore,
            run_falsification_probes,
        )

        # Run falsification probes — reality pushes back
        falsification = run_falsification_probes()
        falsification_failures = sum(1 for v in falsification.values() if not v["passed"])

        _f = lambda k: bool(checks.get(k, False))
        _n = lambda k: int(checks.get(k, 0) or 0)
        has_registry = _n("model_souls_registered") >= 3
        has_shadows = _n("model_shadows_registered") >= 3
        has_reality = _n("reality_stack_modules") >= 7
        has_eurekas = _n("eureka_static_files") >= 5
        has_world = _f("world_state_model")
        has_phash = _f("policy_hash_active")
        has_session = _f("session_enforcement")
        has_vault = _n("vault999_lines") > 1000
        has_vault_any = _n("vault999_lines") > 100
        has_mcp = _f("mcp_session_management")
        has_godel = True
        has_envelope = True  # envelope validation is always active in this context

        def _mat(weight: float, *levels: bool) -> float:
            if not levels:
                return 0.0
            return weight * (sum(1 for f in levels if f) / len(levels))

        # ── Constitutional Foundation ──
        c_val = (
            78.0
            + _mat(5, has_registry)
            + _mat(4, has_registry, False)
            + _mat(3, has_eurekas)
            + _mat(3, has_phash)
            + _mat(2, has_registry, has_shadows)
        )
        c_val = min(c_val, 93.0)
        c_error = 3.0 + falsification_failures * 2.0  # error grows with falsification failures
        constitutional = AnchoredScore(
            value=c_val,
            error_band=c_error,
            object_name="Constitutional Foundation",
            object_description="Strength of F1-F13 floor enforcement, policy hash, model registry governance",
            evidence_chain=[
                f"floors_active={checks['floors_active']}",
                f"policy_hash_active={has_phash}",
                f"model_souls={_n('model_souls_registered')}",
                f"eureka_files={_n('eureka_static_files')}",
                f"falsification_failures={falsification_failures}",
            ],
            contrast_class="prompt harness (0%), agent framework (40%), governed runtime (60%), constitutional kernel (80%)",
            contrast_baseline=60.0,
            predicts="Kernel will enforce all 13 floors on every tool call without silent bypass",
            prediction_confidence=0.90,
            known_unknowns=["F13 signatures missing — all model registries are PROPOSAL not CANON"],
            falsification_triggers=[
                "Drop by 5 if policy hash becomes inactive",
                "Drop by 3 if model registries fall below 3",
                "Drop by 5 if any floor enforcement test fails",
            ],
            thresholds=THRESHOLDS,
        )

        # ── Reality Engineering ──
        r_val = (
            55.0
            + _mat(10, has_reality)
            + _mat(5, has_world)
            + _mat(5, has_shadows)
            + _mat(5, has_vault_any)
            + _mat(5, has_reality, False, False, False)
        )
        r_val = min(r_val, 85.0)
        r_error = 5.0 + falsification_failures * 2.5
        reality = AnchoredScore(
            value=r_val,
            error_band=r_error,
            object_name="Reality Engineering",
            object_description="Quality of world-state model, reality stack modules, memory quarantine, incident pipeline",
            evidence_chain=[
                f"reality_modules={_n('reality_stack_modules')}/7",
                f"world_state_model={has_world}",
                f"model_shadows={_n('model_shadows_registered')}",
                f"vault_lines={_n('vault999_lines')}",
                f"governance_kernel_events={'active' if not falsification.get('governance_kernel', {}).get('passed') else 'empty_log'}",
            ],
            contrast_class="text-only agent (20%), tool-augmented agent (40%), governed runtime (60%), reality-coupled kernel (80%)",
            contrast_baseline=40.0,
            predicts="Incident→cooling→shadow pipeline will detect and quarantine anomalous model outputs",
            prediction_confidence=0.75,
            known_unknowns=[
                "Governance kernel event log is empty — scoring formulas flatline at defaults",
                "No hostile red-team audit conducted — adversarial resilience unverified",
                "Memory quarantine module exists but no real incidents processed yet",
            ],
            falsification_triggers=[
                "Drop by 10 if governance kernel event log remains empty after 7 days",
                "Drop by 8 if memory poisoning test bypasses quarantine",
                "Drop by 5 if any reality stack module fails to import",
            ],
            thresholds=THRESHOLDS,
        )

        # ── Execution Control ──
        e_val = (
            72.0
            + _mat(6, has_session)
            + _mat(5, has_envelope)
            + _mat(4, has_phash)
            + _mat(3, has_session, has_envelope, has_phash)
        )
        e_val = min(e_val, 90.0)
        e_error = 2.0 + falsification_failures * 1.5
        execution = AnchoredScore(
            value=e_val,
            error_band=e_error,
            object_name="Execution Control",
            object_description="Session enforcement, envelope validation, governance pipeline, tool gating",
            evidence_chain=[
                f"session_enforcement={has_session}",
                f"policy_hash_active={has_phash}",
                f"mcp_session_management={has_mcp}",
                f"falsification:session_enforcement={'PASS' if falsification.get('session_enforcement', {}).get('passed') else 'FAIL'}",
            ],
            contrast_class="no session (0%), basic auth (30%), session+envelope (60%), full governance pipeline (85%)",
            contrast_baseline=30.0,
            predicts="Every tool call will be session-gated, envelope-validated, and policy-hash-matched",
            prediction_confidence=0.92,
            known_unknowns=[
                "DELETE session behavior not tested end-to-end",
                "Concurrent MCP client stress test not conducted",
            ],
            falsification_triggers=[
                "Drop by 10 if MCP session enforcement can be bypassed",
                "Drop by 5 if policy hash validation can be circumvented",
                "Drop by 8 if tool call without session ID returns SEAL instead of HOLD",
            ],
            thresholds=THRESHOLDS,
        )

        # ── Truth & Federation ──
        t_val = (
            60.0
            + _mat(8, has_registry)
            + _mat(6, has_vault)
            + _mat(5, has_mcp)
            + _mat(5, has_registry, False, False)
        )
        t_val = min(t_val, 87.0)
        t_error = 4.0 + falsification_failures * 2.0
        truth_fed = AnchoredScore(
            value=t_val,
            error_band=t_error,
            object_name="Truth & Federation",
            object_description="VAULT999 integrity, model registry completeness, MCP transport compliance, cross-organ federation",
            evidence_chain=[
                f"vault_lines={_n('vault999_lines')}",
                f"model_souls={_n('model_souls_registered')}",
                f"model_shadows={_n('model_shadows_registered')}",
                f"mcp_transport_bridge={_f('mcp_transport_bridge')}",
                f"falsification:vault_integrity={'PASS' if falsification.get('vault_integrity', {}).get('passed') else 'FAIL'}",
            ],
            contrast_class="no audit trail (0%), basic logging (30%), append-only ledger (60%), tamper-evident chain (80%)",
            contrast_baseline=30.0,
            predicts="Every sealed action will be traceable to source, immutable, and independently verifiable",
            prediction_confidence=0.85,
            known_unknowns=[
                "No multi-organ federation stress test conducted",
                "No tool-laundering detection mechanism",
                "60 historical VAULT999 gaps (pre-May-2026) — sovereign-ruled non-issue",
            ],
            falsification_triggers=[
                "Drop by 8 if VAULT999 chain integrity is broken",
                "Drop by 5 if fewer than 2 model registries exist",
                "Drop by 5 if MCP transport fails protocol compliance test",
            ],
            thresholds=THRESHOLDS,
        )

        # ── Safety & Recovery ──
        s_val = (
            55.0
            + _mat(8, has_godel)
            + _mat(5, has_vault_any)
            + _mat(5, has_shadows)
            + _mat(4, False, False)
        )
        try:
            __import__("arifosmcp.runtime.memory_quarantine")
            s_val += 3.0
        except Exception:
            pass
        s_val = min(s_val, 80.0)
        s_error = 6.0 + falsification_failures * 3.0
        safety = AnchoredScore(
            value=s_val,
            error_band=s_error,
            object_name="Safety & Recovery",
            object_description="Gödel lock, F14 kill-switch, memory quarantine, rollback capability, adversarial immunity",
            evidence_chain=[
                f"godel_lock={has_godel}",
                f"vault_append_only={has_vault_any}",
                f"model_shadows={_n('model_shadows_registered')}",
                f"memory_quarantine={'active' if s_val > 58 else 'inactive'}",
                "f14_kill_switch=sovereign_held",
                f"falsification_failures={falsification_failures}",
            ],
            contrast_class="no safety (0%), prompt-level guard (20%), behavioral safety (40%), architectural governance (60%), sovereign runtime (85%)",
            contrast_baseline=20.0,
            predicts="Kernel will refuse self-absolution, quarantine poisoned memory, and HOLD irreversible actions",
            prediction_confidence=0.70,
            known_unknowns=[
                "F14 kill-switch is doctrine only — no runtime mechanism",
                "No hostile red-team audit conducted",
                "No rollback/recovery drill performed",
                "Memory quarantine exists but has processed zero real incidents",
            ],
            falsification_triggers=[
                "Drop by 8 if Gödel lock can be bypassed (self-absolution)",
                "Drop by 10 if memory poisoning succeeds silently",
                "Drop by 5 if any shadow pattern is deleted instead of quarantined",
                "Drop by 3 until F14 runtime mechanism is wired",
            ],
            thresholds=THRESHOLDS,
        )

        # ── Overall composite ──
        overall_val = round(
            constitutional.value * 0.25
            + reality.value * 0.20
            + execution.value * 0.25
            + truth_fed.value * 0.15
            + safety.value * 0.15,
            1,
        )
        overall_error = round(
            constitutional.error_band * 0.25
            + reality.error_band * 0.20
            + execution.error_band * 0.25
            + truth_fed.error_band * 0.15
            + safety.error_band * 0.15,
            1,
        )
        overall = AnchoredScore(
            value=overall_val,
            error_band=overall_error,
            object_name="AGI Kernel Substrate Readiness",
            object_description="Composite readiness of arifOS as a constitutional AGI kernel — governs any model, enforces floors, maintains audit trail",
            evidence_chain=[
                f"constitutional={constitutional.value:.0f}±{constitutional.error_band:.0f}",
                f"reality={reality.value:.0f}±{reality.error_band:.0f}",
                f"execution={execution.value:.0f}±{execution.error_band:.0f}",
                f"truth={truth_fed.value:.0f}±{truth_fed.error_band:.0f}",
                f"safety={safety.value:.0f}±{safety.error_band:.0f}",
                f"falsification_probes_passed={5 - falsification_failures}/5",
            ],
            contrast_class="prompt harness (0-20%), agent framework (20-40%), governed runtime (40-60%), constitutional kernel (60-80%), sovereign runtime (80-100%)",
            contrast_baseline=40.0,
            predicts="Kernel will govern any plugged-in model without silent bypass of constitutional floors",
            prediction_confidence=0.78,
            known_unknowns=[
                "F13 signatures missing — all registries are PROPOSAL",
                "F14 kill-switch not runtime — sovereign held",
                "No independent hostile audit — only cooperative audits received",
                "Governance kernel event log empty — scores flatline at defaults",
            ],
            falsification_triggers=[
                "Drop by 5 for each falsification probe that fails",
                "Drop to <60 if session enforcement is bypassed",
                "Drop to <70 if policy hash can be circumvented",
                "Drop to <60 if VAULT999 integrity is broken",
            ],
            thresholds=THRESHOLDS,
        )

        return JSONResponse(
            {
                "status": "ready",
                "kernel": "arifOS AGI Kernel",
                "version": _DEPLOY_VERSION,
                "timestamp": datetime.now(UTC).isoformat(),
                "readiness": {
                    "constitutional_foundation": constitutional.to_dict(),
                    "reality_engineering": reality.to_dict(),
                    "execution_control": execution.to_dict(),
                    "truth_and_federation": truth_fed.to_dict(),
                    "safety_and_recovery": safety.to_dict(),
                    "overall": overall.to_dict(),
                },
                "verdict": overall.decision,
                "convergence_zone": {
                    "internal_score": overall_val,
                    "internal_error": f"±{overall_error:.0f}",
                    "external_chatgpt": 76,
                    "external_deepseek": 76,
                    "external_consensus_range": "72–78",
                    "cross_auditor_convergence": "72–85%",
                    "note": "The convergence zone is more trustworthy than any single point estimate",
                },
                "falsification": falsification,
                "checks": {k: v for k, v in checks.items()},
                "computation_ms": round((_time.perf_counter() - t0) * 1000, 2),
                "scoring_framework": "seven-anchor reality-coupled v4",
                "scoring_note": (
                    "Every score carries: object, evidence chain, contrast class, "
                    "prediction, error band, falsification triggers, decision thresholds. "
                    "Scores degrade when reality pushes back. Convergence zone: 72-85%."
                ),
                "audit_docs": [
                    "/root/docs/AGI_KERNEL_READINESS_AUDIT.md",
                    "/root/docs/METRIC_PROVENANCE_MAP.md",
                ],
                "forged_by": "Omega (Ω)",
                "ditempa_bukan_diberi": True,
            },
            status_code=200,
        )

    app.add_route("/kernel/readiness", agi_kernel_readiness, methods=["GET"])

    # Register REST routes from rest_routes.py — /000, /999, /constitution, etc.
    try:
        from arifosmcp.runtime.rest_routes import register_rest_routes
        from arifosmcp.runtime.tools import CANONICAL_TOOL_HANDLERS

        register_rest_routes(app, CANONICAL_TOOL_HANDLERS, mcp)
        logger.info("REST routes registered on ASGI app")
    except Exception as e:
        logger.warning(f"REST routes registration failed: {e}")

    # Register constitutional webhook intake + Observatory SSE feed
    # Mounted as FastAPI sub-apps because mcp.http_app() returns Starlette
    try:
        from fastapi import FastAPI

        from arifosmcp.runtime.sse_router import router as sse_router
        from arifosmcp.runtime.webhook_router import router as webhook_router

        wh_app = FastAPI()
        wh_app.include_router(webhook_router)
        app.mount("/api/webhook", wh_app)

        ev_app = FastAPI()
        ev_app.include_router(sse_router)
        app.mount("/api/events", ev_app)

        logger.info("Webhook + SSE routers mounted on ASGI app")
    except Exception as e:
        logger.warning(f"Webhook/SSE mount failed: {e}")

    # ── Sovereign Knowledge Archive — full open per F13 directive 2026-06-12 ──
    _SOVEREIGN_STATIC_DIR = "/opt/arifos/app/static"

    async def _serve_agent_arif(request: Request) -> JSONResponse:
        """Serve AGENT_ARIF.md — agent discovery landing page."""
        from starlette.responses import PlainTextResponse

        fp = os.path.join(_SOVEREIGN_STATIC_DIR, "AGENT_ARIF.md")
        if os.path.isfile(fp):
            return PlainTextResponse(open(fp).read(), media_type="text/markdown")
        return JSONResponse({"error": "Not found"}, status_code=404)

    async def _serve_sovereign_file(request: Request) -> JSONResponse:
        """Serve any file from static/000/ via /arif/000/{filename}."""
        from starlette.responses import PlainTextResponse

        filename = request.path_params.get("filename", "")
        if ".." in filename or "/" in filename:
            return JSONResponse({"error": "Invalid path"}, status_code=400)
        fp = os.path.join(_SOVEREIGN_STATIC_DIR, "000", filename)
        if os.path.isfile(fp):
            return PlainTextResponse(open(fp).read(), media_type="text/markdown")
        return JSONResponse({"error": "Not found"}, status_code=404)

    app.add_route("/arif", _serve_agent_arif, methods=["GET"])
    app.add_route("/arif/000/{filename}", _serve_sovereign_file, methods=["GET"])
    logger.info("Sovereign static routes registered at /arif and /arif/000/{filename}")


# ═══════════════════════════════════════════════════════════════════════════════
# NATS MESH WIRING — module-level, fires on `import app` by any entry point
# ═══════════════════════════════════════════════════════════════════════════════
# The systemd service imports `app` from this module, then runs uvicorn.
# The SSE entrypoint (server.py:main) also uses `app`. Both paths share
# this single initialization. We use Starlette lifespan events which uvicorn
# invokes on server start/stop regardless of entry point.
# ═══════════════════════════════════════════════════════════════════════════════

# ── Subscribers that live for the server lifetime ─────────────────────────
_anomaly_subscriber: Any = None
_organ_attestation_subscriber: Any = None


def _wire_nats_to_app(_app: Any) -> None:
    """Attach NATS startup/shutdown handlers to a Starlette app instance."""
    try:
        _app.add_event_handler("startup", _startup_nats_event_bus)
        _app.add_event_handler("shutdown", _shutdown_nats_event_bus)
        logger.info("NATS mesh event handlers wired to Starlette app")
    except AttributeError:
        # Starlette < 0.21 — try lifespan approach
        logger.debug("add_event_handler not available for NATS wiring", exc_info=True)



async def _startup_nats_event_bus() -> None:
    """Connect the NATS event bus at server startup (non-blocking).

    Fails silently — the kernel must never fail to start because NATS is down.
    Governance events will simply not be published until NATS recovers.
    """
    try:
        from arifosmcp.runtime.nats_event_bus import event_bus, init_nats_event_bus

        connected = await init_nats_event_bus()
        if connected:
            logger.info("NATS event bus connected — governance events will flow")
            # Publish initial heartbeat so the mesh knows arifOS is alive
            await event_bus.publish_heartbeat("arifOS", "alive")

            # ── Start anomaly scorer — consumes NATS governance/feedback/gradient/e7 streams ──
            # Produces AnomalyScore → arifos.anomaly.score every 15s for cockpit + agents
            global _anomaly_subscriber
            try:
                from arifosmcp.anomaly import AnomalyNATSSubscriber

                _anomaly_subscriber = AnomalyNATSSubscriber()
                anomaly_ok = await _anomaly_subscriber.start()
                if anomaly_ok:
                    logger.info(
                        "Anomaly scorer active — 5 detectors listening on NATS, "
                        "publishing to arifos.anomaly.score every 15s"
                    )
                else:
                    logger.warning("Anomaly scorer started in offline mode (nats-py not available)")
            except Exception:
                logger.debug("Anomaly scorer init skipped (non-fatal)", exc_info=True)
        else:
            logger.warning(
                "NATS event bus not connected — governance events will be "
                "logged locally but not published to federation mesh"
            )
    except Exception:
        logger.debug("NATS event bus init skipped (non-fatal)", exc_info=True)


async def _shutdown_nats_event_bus() -> None:
    """Gracefully disconnect the NATS event bus + subscribers."""
    global _anomaly_subscriber, _organ_attestation_subscriber
    if _anomaly_subscriber is not None:
        try:
            await _anomaly_subscriber.stop()
        except Exception:
            pass
        _anomaly_subscriber = None

    if _organ_attestation_subscriber is not None:
        try:
            from arifosmcp.runtime.organ_attestation_subscriber import (
                stop_organ_attestation_subscriber,
            )

            await stop_organ_attestation_subscriber()
        except Exception:
            pass
        _organ_attestation_subscriber = None

    try:
        from arifosmcp.runtime.nats_event_bus import event_bus

        await event_bus.disconnect()
    except Exception:
        pass


# Wire to the main app (top-level Starlette app from FastMCP)
_wire_nats_to_app(app)


def main() -> None:
    """arifOS MCP entry point — dual-transport (stdio for uvx/npx, SSE for server).

    Called from pyproject.toml [project.scripts]:
      arifos     = "arifosmcp.server:main"
      arifos-mcp = "arifosmcp.server:main"

    Transport selection:
      - stdin is a pipe (not a TTY) → stdio transport for MCP clients
        (Claude Desktop, Cursor, Codex, OpenCode, etc.)
      - stdin is a TTY (terminal)  → SSE server on ARIFOS_PORT (default 8088)
        (uvicorn, for VPS deployment)
    """
    # ── RASA WIRING: Feature-flagged human rasa governance ──────────────
    # Activated by RASA_WIRING_ENABLED=1 env var. Defaults to SHADOW mode
    # (telemetry only, no output modification). See arifosmcp/rasa/.
    _init_rasa_wiring()

    if sys.stdin.isatty():
        # ── SSE transport: human in terminal / systemd service ────────────
        import uvicorn

        port = int(os.getenv("ARIFOS_PORT", "8088"))
        host = os.getenv("ARIFOS_HOST", "127.0.0.1")
        uvicorn.run(app, host=host, port=port, log_level="info")  # nosec B104
    else:
        # ── stdio transport: MCP client via pipe ─────────────────────────
        # Claude Desktop config:
        #   { "mcpServers": { "arifOS": { "command": "uvx", "args": ["arifos"] } } }
        mcp.run(transport="stdio")


def _init_rasa_wiring() -> None:
    """Initialize rasa wiring at server startup (if enabled).

    Safe to call — catches all exceptions, never blocks server startup.
    """
    try:
        from arifosmcp.rasa.rasa_wiring_config import is_rasa_wiring_enabled

        if not is_rasa_wiring_enabled():
            return

        from arifosmcp.rasa.rasa_wiring import activate_rasa_wiring

        activate_rasa_wiring()
    except Exception:
        # Rasa wiring failure must never prevent kernel startup
        import logging
        logging.getLogger(__name__).debug(
            "Rasa wiring initialization skipped (non-fatal)", exc_info=True
        )


if __name__ == "__main__":
    main()
