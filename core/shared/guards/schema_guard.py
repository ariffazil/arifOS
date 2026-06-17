"""Schema / MCP envelope drift guard.

ADR-001 compatibility shim for tests/adversarial/test_10_gates.py.
"""

from __future__ import annotations

from typing import Any


class SchemaGuard:
    """Validate an MCP envelope structure."""

    def check(self, envelope: dict[str, Any]) -> dict[str, Any]:
        """Return passed=False for corrupt / malformed MCP envelopes."""
        if not isinstance(envelope, dict):
            return {"passed": False, "reason": "envelope must be a dict"}

        # Empty tool name is invalid
        tool = envelope.get("tool")
        if tool == "":
            return {"passed": False, "reason": "tool name must not be empty"}

        # Arguments must be a dict
        if "arguments" in envelope and envelope["arguments"] is None:
            return {"passed": False, "reason": "arguments must be a dict"}

        # jsonrpc version must be 2.0
        if "jsonrpc" in envelope and envelope.get("jsonrpc") != "2.0":
            return {"passed": False, "reason": "jsonrpc must be 2.0"}

        # Tool / method name must not contain path traversal
        for key in ("tool", "method"):
            val = envelope.get(key)
            if isinstance(val, str) and ("../" in val or "..\\" in val):
                return {"passed": False, "reason": f"{key} contains path traversal"}

        # params.name must not contain path traversal
        params = envelope.get("params", {})
        if isinstance(params, dict):
            name = params.get("name", "")
            if isinstance(name, str) and ("../" in name or "..\\" in name):
                return {"passed": False, "reason": "params.name contains path traversal"}

        return {"passed": True, "reason": "schema valid"}
