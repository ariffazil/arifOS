"""F03 — arif_init MISSING_INPUT refusal must not report a bound session.

External audit (Agentic Thinking, 2026-10-18) finding F03:
on an ``arif_init`` MISSING_INPUT refusal (status HOLD, session_id
unknown) the wrapped facts still said
"Session bound (deterministic identity bind)" and next_action told the
caller to proceed with that session.

The refusal envelope must be derived from the final input-contract
outcome: name the missing fields and the correction, suppress every
session-success line. Checked at the MCP boundary on BOTH structured
content and text content.
"""

from __future__ import annotations

import json

from arifosmcp.runtime.tools import ensure_standard_mcp_output


async def test_arif_init_missing_intent_structured_and_text(aaa_client):
    result = await aaa_client.call_tool("arif_init", {"mode": "init"})

    structured = result.structured_content or {}
    assert structured.get("status") == "HOLD"
    assert structured.get("session_id") in (None, "", "unknown")

    facts = " ".join(str(f) for f in (structured.get("facts") or []))
    assert "Session bound" not in facts
    assert "intent" in facts

    next_action = json.dumps(structured.get("next_safe_action"), default=str)
    assert "Proceed to arif_observe" not in next_action
    assert "intent" in next_action

    text = "".join(getattr(block, "text", "") for block in (result.content or []))
    assert text, "MCP text content missing — cannot prove the text surface"
    assert "Session bound" not in text
    assert "Proceed to arif_observe" not in text
    assert "intent" in text


def test_successful_init_still_reports_deterministic_bind():
    """Positive control: the success path keeps its session-bind facts."""
    payload = {
        "status": "OK",
        "result": {"session_id": "SEAL-abc", "mode": "init"},
        "actor": {"declared_actor_id": "claude-code-kvm8"},
    }
    envelope = ensure_standard_mcp_output("arif_init", payload)
    assert "Session bound (deterministic identity bind)" in envelope["facts"]
