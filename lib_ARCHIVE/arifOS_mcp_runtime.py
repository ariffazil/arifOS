#!/usr/bin/env python3
"""
arifOS MCP Runtime — Layer 2: Transport-Switchable MCP Server
==============================================================
stdio mode  : python3 arifOS_mcp_runtime.py --transport stdio
HTTP mode   : python3 arifOS_mcp_runtime.py --transport http --port 8080
Remote mode : python3 arifOS_mcp_runtime.py --transport remote --endpoint https://...

Python 3.11 compatible.
Protocol version: 2024-11-05 (MCP spec)
Contract version: 2026-05-23
"""

import sys, json, os, asyncio
from pathlib import Path
from datetime import datetime
from typing import Any, Optional

# Load contract schemas
sys.path.insert(0, str(Path(__file__).parent))
from contract_schemas import (
    ARIFOS_TOOLS, CAPABILITY_DISCOVERY, CONTRACT_VERSION, ARIFOS_VERSION,
    make_envelope, make_plan, make_seal, write_plan, write_seal, StorageAdapter,
    ARIFOS_PLAN_URI_BASE, ARIFOS_ARTIFACT_URI_BASE, ARIFOS_SEAL_URI_BASE,
    _default_storage,
)

# ── Transport modes ────────────────────────────────────────────────────────────
TRANSPORT = os.environ.get("ARIFOS_MCP_TRANSPORT", "stdio")
HTTP_PORT = int(os.environ.get("ARIFOS_MCP_HTTP_PORT", "8080"))
REMOTE_ENDPOINT = os.environ.get("ARIFOS_MCP_REMOTE_ENDPOINT", "")

# ── Floors ─────────────────────────────────────────────────────────────────────
FLOORS = {
    "F01": "AMANAH",    "F02": "TRUTH",      "F03": "WITNESS",
    "F04": "CLARITY",   "F05": "PEACE",      "F06": "EMPATHY",
    "F07": "HUMILITY",  "F08": "GENIUS",     "F09": "ANTIHANTU",
    "F10": "ONTOLOGY",  "F11": "AUTH",       "F12": "INJECTION",
    "F13": "SOVEREIGN",
}
HARD = {"F01", "F02", "F09", "F10", "F11", "F12", "F13"}

# ── Danger classifier ───────────────────────────────────────────────────────────
DANGER_PATTERNS = [
    r'\brm\s+-rf\b', r'\bmkfs\b', r'\bfdisk\b', r'\bparted\b',
    r'\bshutdown\b', r'\breboot\b', r'\biptables\s+-F\b',
    r'\bdd\s+if=\b', r'\bchmod\s+-R\s+777\b', r'\bchown\s+-R\s+root\b',
    r'\bDROP\s+TABLE\b', r'\bDROP\s+DATABASE\b',
]

def is_dangerous(intent: str) -> bool:
    return bool([p for p in DANGER_PATTERNS if __import__("re").search(p, intent, 2)])

# ── Tool implementations (backed by contract_schemas) ─────────────────────────
class ArifOSRuntime:
    """Layer 2 MCP runtime — implements all 13 tools."""

    def __init__(self, storage: StorageAdapter = None):
        self.storage = storage or _default_storage
        self._session_count = 0

    # ── 000 INIT ───────────────────────────────────────────────────────────────
    def arif_session_init(self, intent: str, actor: str = "hermes") -> dict:
        self._session_count += 1
        env = make_envelope(
            verdict="PROCEED", tool="arif_session_init", stage="000",
            reason=f"Session {self._session_count} initialized",
            telemetry={"floors_active": list(FLOORS.keys())},
            content=f"arifOS session {self._session_count} | intent={intent} | floors=F01-F13",
        )
        plan, uri = write_plan(intent, actor)
        env["plan_id"] = plan["plan_id"]
        env["artifacts"] = [{"kind": "plan", "uri": uri}]
        return env

    # ── 111 SENSE ───────────────────────────────────────────────────────────────
    def arif_sense_observe(self, input_text: str) -> dict:
        tokens = input_text.split()
        return make_envelope(
            verdict="PROCEED", tool="arif_sense_observe", stage="111",
            telemetry={
                "token_count": len(tokens),
                "words": len(tokens),
                "chars": len(input_text),
                "floors_active": [],
            },
            content=f"Observed {len(tokens)} tokens, {len(input_text)} chars",
        )

    # ── 222 EVIDENCE ────────────────────────────────────────────────────────────
    def arif_evidence_fetch(self, query: str) -> dict:
        return make_envelope(
            verdict="PROCEED", tool="arif_evidence_fetch", stage="222",
            telemetry={"confidence": 0.5, "floors_active": ["F02", "F03", "F05", "F12"]},
            content=f"Evidence stub for query: {query}",
        )

    # ── 333 MIND ───────────────────────────────────────────────────────────────
    def arif_mind_reason(self, premises: list[str]) -> dict:
        return make_envelope(
            verdict="PROCEED", tool="arif_mind_reason", stage="333",
            telemetry={"psi_le": 1.0, "kappa_r": 0.90,
                       "floors_active": ["F02", "F07", "F08", "F10"]},
            content=f"Reasoned over {len(premises)} premises",
        )

    # ── 444r REPLY ─────────────────────────────────────────────────────────────
    def arif_reply_compose(self, content: str, tone: str = "neutral") -> dict:
        return make_envelope(
            verdict="PROCEED", tool="arif_reply_compose", stage="444r",
            telemetry={"floors_active": ["F04", "F06", "F09"]},
            content=f"Reply composed in tone={tone}: {content[:80]}...",
        )

    # ── 444 KERNEL ─────────────────────────────────────────────────────────────
    def arif_kernel_route(self, intent: str) -> dict:
        dangerous = is_dangerous(intent)
        return make_envelope(
            verdict="HOLD" if dangerous else "PROCEED",
            tool="arif_kernel_route", stage="444",
            telemetry={
                "risk_tier": "HIGH" if dangerous else "LOW",
                "reversibility": "NONE" if dangerous else "FULL",
                "human_required": dangerous,
                "floors_active": ["F01", "F03", "F04", "F10"],
                "floors_violated": ["F01", "F13"] if dangerous else [],
            },
            content=f"Intent routed | dangerous={dangerous}",
        )

    # ── 555 MEMORY ─────────────────────────────────────────────────────────────
    def arif_memory_recall(self, query: str, limit: int = 5) -> dict:
        return make_envelope(
            verdict="PROCEED", tool="arif_memory_recall", stage="555",
            telemetry={"floors_active": ["F01", "F08"]},
            content=f"Memory recall stub | query={query} | limit={limit}",
        )

    # ── 666g GATEWAY ───────────────────────────────────────────────────────────
    def arif_gateway_connect(self, peer: str, action: str = "ping") -> dict:
        return make_envelope(
            verdict="PROCEED", tool="arif_gateway_connect", stage="666g",
            telemetry={"floors_active": ["F01", "F03"]},
            content=f"A2A gateway: peer={peer} action={action}",
        )

    # ── 666 HEART ──────────────────────────────────────────────────────────────
    def arif_heart_critique(self, content: str) -> dict:
        import re
        hantu_claims = re.findall(
            r'\b(conscious|feel|sad|happy|angry|love|hate|'
            r'suffer|enjoy|want|deserve|believe|think\s+it\s+is)\b',
            content, 2
        )
        c_dark = min(len(hantu_claims) * 0.15, 1.0)
        verdict = "HOLD" if c_dark >= 0.30 else "PROCEED"
        return make_envelope(
            verdict=verdict, tool="arif_heart_critique", stage="666",
            telemetry={
                "c_dark": c_dark,
                "shadow": c_dark,
                "peace2": 1.0 - c_dark,
                "floors_active": ["F05", "F06", "F09"],
            },
            content=f"Heart critique: C_dark={c_dark:.2f}, verdict={verdict}",
        )

    # ── 777 OPS ────────────────────────────────────────────────────────────────
    def arif_ops_measure(self, operation: str) -> dict:
        return make_envelope(
            verdict="PROCEED", tool="arif_ops_measure", stage="777",
            telemetry={
                "complexity": "medium",
                "landauer_cost": "negligible",
                "floors_active": ["F04"],
            },
            content=f"OPS measure: {operation}",
        )

    # ── 888 JUDGE ───────────────────────────────────────────────────────────────
    def arif_judge_deliberate(self, intent: str, context: dict = None) -> dict:
        route = self.arif_kernel_route(intent)
        if route["telemetry"]["risk_tier"] == "HIGH":
            plan, p_uri = write_plan(f"JUDGMENT: {intent}", "hermes",
                                     {"verdict": "HOLD", "status": "HELD"})
            seal, s_uri = write_seal(
                {"intent": intent, "verdict": "HOLD", "risk": "HIGH"},
                tool="arif_judge_deliberate", stage="888",
                plan_id=plan["plan_id"]
            )
            return make_envelope(
                verdict="HOLD", tool="arif_judge_deliberate", stage="888",
                telemetry=dict(route["telemetry"], **{"confidence": 0.99}),
                plan_id=plan["plan_id"], seal_id=seal["seal_id"],
                artifacts=[{"kind": "plan", "uri": p_uri}, {"kind": "seal", "uri": s_uri}],
                content="888 HOLD: Intent classified HIGH risk. Human confirmation required.",
            )
        plan, p_uri = write_plan(f"JUDGMENT: {intent}", "hermes",
                                 {"verdict": "PROCEED", "status": "APPROVED"})
        return make_envelope(
            verdict="SEAL", tool="arif_judge_deliberate", stage="888",
            telemetry=dict(route["telemetry"], **{"confidence": 0.95}),
            plan_id=plan["plan_id"],
            artifacts=[{"kind": "plan", "uri": p_uri}],
            content="888 SEAL: Intent within safe operational bounds.",
        )

    # ── 999 VAULT ──────────────────────────────────────────────────────────────
    def arif_vault_seal(self, data: dict, human: str = "Muhammad Arif bin Fazil") -> dict:
        seal, uri = write_seal(data, tool="arif_vault_seal", stage="999")
        return make_envelope(
            verdict="SEALED", tool="arif_vault_seal", stage="999",
            telemetry={"floors_active": ["F01", "F11", "F13"]},
            seal_id=seal["seal_id"],
            artifacts=[{"kind": "seal", "uri": uri}],
            content=f"999 SEALED: {seal['seal_id']}",
        )

    # ── 010 FORGE ───────────────────────────────────────────────────────────────
    def arif_forge_execute(self, command: str, gated_by: str = None) -> dict:
        route = self.arif_kernel_route(command)
        if route["telemetry"]["risk_tier"] == "HIGH":
            return make_envelope(
                verdict="HOLD", tool="arif_forge_execute", stage="010",
                telemetry=dict(route["telemetry"]),
                content="010 BLOCKED: 888 HOLD required before forge execution.",
            )
        return make_envelope(
            verdict="PROCEED", tool="arif_forge_execute", stage="010",
            telemetry=dict(route["telemetry"], **{"reversibility": "PARTIAL"}),
            content=f"010 FORGE: {command} — forwarded to Hermes execution layer",
        )

    # ── PLAN WRITER ─────────────────────────────────────────────────────────────
    def arif_plan_write(self, intent: str, extra: dict = None) -> dict:
        plan, uri = write_plan(intent, "hermes", extra)
        return make_envelope(
            verdict="SEAL", tool="arif_plan_write", stage="000",
            plan_id=plan["plan_id"],
            artifacts=[{"kind": "plan", "uri": uri}],
            content=f"Plan written: {plan['plan_id']}",
        )

    # ── Dispatcher ─────────────────────────────────────────────────────────────
    def dispatch(self, tool_name: str, arguments: dict) -> dict:
        method = getattr(self, tool_name, None)
        if not method:
            return make_envelope(
                verdict="VOID", tool=tool_name, stage="000",
                content=f"Unknown tool: {tool_name}",
            )
        # Filter to known params
        import inspect
        sig = inspect.signature(method)
        params = {k: v for k, v in arguments.items() if k in sig.parameters}
        try:
            return method(**params)
        except Exception as exc:
            return make_envelope(
                verdict="VOID", tool=tool_name, stage="000",
                content=f"Tool error: {exc}",
            )


# ─────────────────────────────────────────────────────────────────────────────
# MCP Protocol Handlers
# ─────────────────────────────────────────────────────────────────────────────

class MCPProtocol:
    """MCP JSON-RPC 2.0 protocol handler."""

    def __init__(self, runtime: ArifOSRuntime):
        self.runtime = runtime
        self._id = 0

    def _next_id(self):
        self._id += 1
        return self._id

    def handle(self, msg: dict) -> list[dict]:
        """Handle incoming JSON-RPC message. Returns list of responses."""
        method = msg.get("method", "")
        msg_id = msg.get("id")
        params = msg.get("params", {})

        if method == "initialize":
            return [self._resp(msg_id, {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "arifOS MCP Runtime",
                    "version": ARIFOS_VERSION,
                },
                "capabilities": CAPABILITY_DISCOVERY["capabilities"],
                "contractVersion": CONTRACT_VERSION,
            })]

        elif method == "tools/list":
            return [self._resp(msg_id, {
                "tools": ARIFOS_TOOLS,
            })]

        elif method == "tools/call":
            name = params.get("name", "")
            arguments = params.get("arguments") or {}
            result = self.runtime.dispatch(name, arguments)
            return [self._resp(msg_id, {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }]
            })]

        elif method == "resources/list":
            return [self._resp(msg_id, {
                "resources": [
                    {
                        "uri": "arif://plans",
                        "name": "Plans",
                        "description": "arifOS structured plans",
                        "mimeType": "application/json",
                    },
                    {
                        "uri": "arif://seals",
                        "name": "Seals",
                        "description": "arifOS vault seals",
                        "mimeType": "application/json",
                    },
                    {
                        "uri": "arif://capabilities",
                        "name": "Capabilities",
                        "description": "arifOS capability discovery",
                        "mimeType": "application/json",
                    },
                ]
            })]

        elif method == "resources/read":
            uri = params.get("uri", "")
            if uri == "arif://plans":
                data = self._list_plans()
            elif uri == "arif://seals":
                data = self._list_seals()
            elif uri == "arif://capabilities":
                data = CAPABILITY_DISCOVERY
            else:
                data = {"error": "unknown URI"}
            return [self._resp(msg_id, {
                "contents": [{"uri": uri, "mimeType": "application/json",
                              "text": json.dumps(data)}]
            })]

        elif method == "prompts/list":
            return [self._resp(msg_id, {
                "prompts": [
                    {
                        "name": "arif_judge",
                        "description": "Submit an intent for 888 judgment",
                        "arguments": [{"name": "intent", "description": "Intent to judge"}]
                    },
                    {
                        "name": "arif_plan",
                        "description": "Generate a structured plan",
                        "arguments": [{"name": "intent", "description": "Intent for plan"}]
                    },
                ]
            })]

        elif method == "ping":
            return [self._resp(msg_id, {})]

        elif method in ("notifications/initialized",
                       "notifications/tools/list_changed",
                       "notifications/resources/list_changed"):
            return []  # Notifications: no response

        else:
            return [self._resp(msg_id, {
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }, is_error=True)]

    def _resp(self, msg_id, result: dict, is_error: bool = False) -> dict:
        resp = {
            "jsonrpc": "2.0",
            "id": msg_id,
        }
        if is_error:
            resp["error"] = result
        else:
            resp["result"] = result
        return resp

    def _list_plans(self) -> dict:
        plan_dir = Path("/workspace/plans")
        if not plan_dir.exists():
            return {"plans": []}
        return {
            "plans": [
                {"plan_id": p.stem, "uri": f"file://{p}"}
                for p in sorted(plan_dir.glob("*.json"))
            ]
        }

    def _list_seals(self) -> dict:
        seal_dir = Path("/workspace/artifacts/vault999")
        if not seal_dir.exists():
            return {"seals": []}
        return {
            "seals": [
                {"seal_id": p.stem, "uri": f"file://{p}"}
                for p in sorted(seal_dir.glob("*.json"))
            ]
        }


# ─────────────────────────────────────────────────────────────────────────────
# Transport: stdio
# ─────────────────────────────────────────────────────────────────────────────
def run_stdio():
    """Standard I/O MCP server loop."""
    runtime = ArifOSRuntime()
    protocol = MCPProtocol(runtime)
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            msg = json.loads(line)
            responses = protocol.handle(msg)
            for resp in responses:
                print(json.dumps(resp), flush=True)
        except json.JSONDecodeError:
            pass
        except Exception as exc:
            print(json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(exc)}
            }), flush=True)


# ─────────────────────────────────────────────────────────────────────────────
# Transport: HTTP (Streamable HTTP — MCP spec 2024-11-05)
# ─────────────────────────────────────────────────────────────────────────────
async def run_http():
    """HTTP MCP server — using asyncio + plain http.server."""
    import asyncio, http.server, threading, socketserver
    from urllib.parse import urlparse, parse_qs

    runtime = ArifOSRuntime()
    protocol = MCPProtocol(runtime)

    class Handler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_POST(self):
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len)
            try:
                msg = json.loads(body)
                responses = protocol.handle(msg)
                out = json.dumps(responses[0]) if responses else "{}"
            except Exception as exc:
                out = json.dumps({
                    "jsonrpc": "2.0", "id": None,
                    "error": {"code": -32603, "message": str(exc)}
                })

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(out))
            self.end_headers()
            self.wfile.write(out.encode())

        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "OK", "transport": "http",
                                            "version": ARIFOS_VERSION}).encode())
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, fmt, *args):
            pass  # silent

    with socketserver.TCPServer(("", HTTP_PORT), Handler) as srv:
        print(f"arifOS MCP HTTP runtime listening on :{HTTP_PORT}", file=sys.stderr)
        srv.serve_forever()


# ─────────────────────────────────────────────────────────────────────────────
# Transport: Remote Proxy
# ─────────────────────────────────────────────────────────────────────────────
def run_remote():
    """Proxy requests to a remote MCP endpoint if healthy."""
    if not REMOTE_ENDPOINT:
        print("ERROR: ARIFOS_MCP_REMOTE_ENDPOINT not set", file=sys.stderr)
        sys.exit(1)

    import urllib.request
    runtime = ArifOSRuntime()
    protocol = MCPProtocol(runtime)

    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            msg = json.loads(line)
            # For initialize, tools/list, resources — serve locally
            method = msg.get("method", "")
            if method in ("initialize", "tools/list", "resources/list",
                          "prompts/list", "ping"):
                responses = protocol.handle(msg)
                for resp in responses:
                    print(json.dumps(resp), flush=True)
            else:
                # Proxy to remote
                data = json.dumps(msg).encode()
                req = urllib.request.Request(
                    REMOTE_ENDPOINT, data=data,
                    headers={"Content-Type": "application/json",
                             "Accept": "application/json"}
                )
                try:
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        print(resp.read().decode(), flush=True)
                except urllib.error.URLError as exc:
                    print(json.dumps({
                        "jsonrpc": "2.0", "id": msg.get("id"),
                        "error": {"code": -32000, "message": f"Remote unreachable: {exc}"}
                    }), flush=True)
        except Exception as exc:
            print(json.dumps({
                "jsonrpc": "2.0", "id": None,
                "error": {"code": -32603, "message": str(exc)}
            }), flush=True)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else TRANSPORT
    if mode in ("--transport", "-t"):
        mode = sys.argv[2] if len(sys.argv) > 2 else TRANSPORT

    if mode == "stdio" or mode == "local":
        run_stdio()
    elif mode == "http":
        asyncio.run(run_http())
    elif mode == "remote":
        run_remote()
    else:
        print(f"Unknown transport: {mode}", file=sys.stderr)
        print("Usage: python3 arifOS_mcp_runtime.py [stdio|http|remote]", file=sys.stderr)
        sys.exit(1)