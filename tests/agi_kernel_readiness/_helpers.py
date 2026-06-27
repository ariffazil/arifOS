"""
Shared MCP client helpers for AGI Kernel Readiness Gate tests.

Protocol version sync: bumped 2024-11-25 → 2025-11-25 on 2026-06-27 by FORGE.
The 7-tool facade refactor (F13 ratified 2026-06-23) upgraded the kernel protocol.
Test helpers must follow. See /root/forge_work/asal-g6-audit-2026-06-27/
HARDENING_REPORT.md §2.4.

mcp-session-id is now OPTIONAL: arifOS :8088 returns 200/JSON-RPC but does
not always set the session header (stateless mode). Helper degrades gracefully:
generates a local UUID when server omits the header.
"""

import json
import http.client
import uuid

MCP_HOST = "127.0.0.1"
MCP_PORT = 8088
PROTOCOL_VERSION = "2025-11-25"  # was "2024-11-25" — bumped to match kernel


class MCPClient:
    """Single-connection MCP client. Preserves server-issued mcp-session-id
    when present; falls back to local UUID when server runs stateless."""

    def __init__(self, client_name: str = "agi-gate", version: str = "1.0"):
        self.client_name = client_name
        self.version = version
        self.conn = None
        self.sid = None

    def _ensure_conn(self):
        if self.conn is None:
            self.conn = http.client.HTTPConnection(MCP_HOST, MCP_PORT, timeout=180)
        return self.conn

    def _close_conn(self):
        if self.conn is not None:
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None

    def initialize(self) -> str:
        """Initialize MCP session. Returns session id (server-issued or local)."""
        conn = self._ensure_conn()
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": self.client_name, "version": self.version},
            },
        }
        conn.request(
            "POST",
            "/mcp",
            body=json.dumps(payload),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
        )
        r = conn.getresponse()
        sid = None
        for h, v in r.getheaders():
            if h.lower() == "mcp-session-id":
                sid = v
        r.read()
        if not sid:
            # Kernel runs in stateless mode (no mcp-session-id header).
            # Generate a local UUID so downstream calls still have a stable
            # session identifier for logging/debugging.
            sid = f"local-{uuid.uuid4().hex[:12]}"
        self.sid = sid
        return sid

    def call(self, tool: str, args: dict) -> dict:
        try:
            conn = self._ensure_conn()
        except Exception:
            self._close_conn()
            conn = self._ensure_conn()
        if not self.sid:
            self.initialize()

        payload = {
            "jsonrpc": "2.0",
            "id": 99,
            "method": "tools/call",
            "params": {"name": tool, "arguments": args},
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.sid:
            headers["mcp-session-id"] = self.sid

        try:
            conn.request("POST", "/mcp", body=json.dumps(payload), headers=headers)
            r = conn.getresponse()
            raw = r.read().decode()
        except OSError:
            # OSError covers ConnectionResetError, BrokenPipeError, TimeoutError
            self._close_conn()
            conn = self._ensure_conn()
            conn.request("POST", "/mcp", body=json.dumps(payload), headers=headers)
            r = conn.getresponse()
            raw = r.read().decode()

        try:
            d = json.loads(raw)
        except json.JSONDecodeError:
            return {"_raw": raw[:500], "_parse_error": True}

        if "error" in d:
            return {"_error": d["error"]}

        content = d.get("result", {}).get("content", [])
        if content and content[0].get("type") == "text":
            try:
                return json.loads(content[0]["text"])
            except json.JSONDecodeError:
                return {"_raw_text": content[0]["text"][:500]}
        return d.get("result", {})

    def close(self):
        self._close_conn()


def boot_light_session(actor_id: str = "agi-gate-tester"):
    """Boot a light session and return (client, session_birth).

    F13 7-tool facade (ratified 2026-06-23): 'arif_session_init' was renamed
    to 'arif_init'. The kernel now only exposes the 7 public tools.
    See /root/arifOS/arifosmcp/PUBLIC_SURFACE_CANON.md.
    """
    c = MCPClient()
    c.initialize()
    r = c.call("arif_init", {"mode": "light", "actor_id": actor_id})
    inner = r.get("result", {})
    sb = inner.get("session_birth", {})
    return c, sb
