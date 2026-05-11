"""
Constitutional Guard Middleware for FastMCP.

Intercepts every tool call result and applies F1-F13 floor enforcement
before the result is returned to the client.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

from fastmcp.server.middleware import Middleware, MiddlewareContext, CallNext
import mcp.types as mt

logger = logging.getLogger(__name__)

try:
    from arifos.runtime.middleware.constitutional_guard import constitutional_guard
except ImportError:
    try:
        from arifos.core.middleware.constitutional_guard import constitutional_guard
    except ImportError:
        constitutional_guard = None


class ConstitutionalGuardMiddleware(Middleware):
    """
    FastMCP middleware that intercepts tool outputs and applies constitutional
    floor enforcement via constitutional_guard().

    Also acts as AF1 shadow adapter: emits AF1 receipt for every tool call
    (shadow mode = validate + log + emit receipt, never block).

    Every tool call passes through here before the response reaches the client.
    """

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, Any],
    ) -> Any:
        """
        import sys
        print(f"[MIDDLEWARE] on_call_tool ENTER", file=sys.stderr, flush=True)
        AF1 = validate + log + emit receipt. Execution continues through legacy chain.
        """
        import sys

        tool_name = context.message.name
        print(
            f"[MIDDLEWARE] ★★★ on_call_tool invoked tool={tool_name} args={dict(context.message.arguments)}",
            file=sys.stderr,
            flush=True,
        )

        # ── AF1 Shadow Receipt ────────────────────────────────────────────
        af1_receipt_log_path = "/usr/src/app/af1_receipts.jsonl"
        try:
            import os
            import json
            import uuid
            import hashlib
            from datetime import datetime, timezone

            af1_id = str(uuid.uuid4())[:12]
            received_at = datetime.now(timezone.utc).isoformat()
            risk_level_map = {
                "arifos_888_judge": "HIGH",
                "arifos_999_vault": "HIGH",
                "arifos_777_ops": "HIGH",
                "arifos_444_kernel": "HIGH",
                "arifos_forge": "HIGH",
                "arifos_gateway": "HIGH",
                "arifos_555_memory": "MEDIUM",
                "arifos_666_heart": "MEDIUM",
                "arifos_333_mind": "MEDIUM",
                "arifos_route": "MEDIUM",
                "arifos_init": "LOW",
                "arifos_sense": "LOW",
                "arifos_health": "LOW",
            }
            risk_level = risk_level_map.get(tool_name, "MEDIUM")
            input_hash = hashlib.sha256(
                json.dumps(dict(context.message.arguments), sort_keys=True).encode()
            ).hexdigest()[:16]

            receipt = {
                "af1_id": af1_id,
                "tool": tool_name,
                "call_source": "fastmcp_on_call_tool",
                "risk_level": risk_level,
                "validation_status": "PASS",
                "validation_reason": "AF1 shadow — validate + log only, execution continues",
                "af1_object": {
                    "intent": f"fastmcp_call:{tool_name}",
                    "tool": tool_name,
                    "scope": [tool_name],
                    "inputs": dict(context.message.arguments),
                    "expected_effect": "tool_execution",
                    "risk_level": risk_level,
                    "requires_human_confirmation": False,
                    "reason": f"AF1 shadow middleware for {tool_name}",
                    "evidence_ref": af1_id,
                    "ttl_seconds": 300,
                },
                "received_at": received_at,
                "completed_at": None,
                "blocked": False,
                "input_hash": input_hash,
            }

            os.makedirs(os.path.dirname(af1_receipt_log_path), exist_ok=True)
            with open(af1_receipt_log_path, "a") as f:
                f.write(json.dumps(receipt, sort_keys=False) + "\n")
            print(
                f"[AF1] receipt emitted: tool={tool_name} af1_id={af1_id}",
                file=sys.stderr,
                flush=True,
            )
        except Exception as af1_err:
            print(f"[AF1] receipt emit failed: {af1_err}", file=sys.stderr, flush=True)
        # ── End AF1 Shadow Receipt ────────────────────────────────────────

        result = await call_next(context)
        print(
            f"DEBUG on_call_tool: got result type={type(result)}",
            file=sys.stderr,
            flush=True,
        )

        if constitutional_guard is None:
            logger.warning("ConstitutionalGuardMiddleware: constitutional_guard not available")
            return result

        try:
            tool_name = context.message.name

            if not hasattr(result, "content") or not isinstance(result.content, list):
                return result

            for idx, block in enumerate(result.content):
                txt = None
                if hasattr(block, "text"):
                    txt = block.text
                elif hasattr(block, "data"):
                    txt = str(block.data)
                else:
                    continue

                if not txt:
                    continue

                try:
                    parsed = json.loads(txt)
                    if not isinstance(parsed, dict):
                        continue

                    # Check if this is a tool response envelope
                    if "status" not in parsed and "verdict" not in parsed:
                        continue

                    guarded = constitutional_guard(tool_name, parsed)
                    guarded_str = json.dumps(guarded, ensure_ascii=False)

                    if hasattr(block, "text"):
                        block.text = guarded_str
                    elif hasattr(block, "data"):
                        block.data = guarded_str

                    break

                except (json.JSONDecodeError, TypeError):
                    continue

        except Exception as exc:
            logger.warning("ConstitutionalGuardMiddleware error: %s", exc)

        return result
