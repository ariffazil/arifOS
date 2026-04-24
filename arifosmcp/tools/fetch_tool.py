"""
arifosmcp/tools/fetch_tool.py — Governed Web Fetch Tool (F9 Anti-Hantu)

Wraps the mcp_fetch substrate with constitutional filtering to prevent 
"spiritual cosplay" and reality-grounding violations.

DITEMPA BUKAN DIBERI — 999 SEAL
"""

import logging

from core.floors import evaluate_tool_call

from arifosmcp.integrations.substrate_bridge import bridge
from arifosmcp.runtime.models import RiskClass
from arifosmcp.runtime.models import RuntimeEnvelope as _RE

logger = logging.getLogger(__name__)

async def arifos_fetch(
    url: str,
    max_length: int = 10000,
    actor_id: str = "anonymous",
    session_id: str | None = None
) -> _RE:
    """
    Governed web fetch tool.
    
    1. Constitutional Check (Pre-call)
    2. Substrate Call (mcp_fetch)
    3. F9 Anti-Hantu Scan (Post-call)
    """
    
    # 1. 000 INIT & Baseline Governance
    gov = evaluate_tool_call(
        action="fetch",
        tool_name="arifos_fetch",
        parameters={"url": url, "max_length": max_length},
        actor_id=actor_id,
        session_id=session_id
    )
    
    if gov.verdict != "SEAL":
        return _RE(
            ok=False,
            tool="arifos.fetch",
            canonical_tool_name="arifos.fetch",
            stage="111_SENSE",
            verdict=gov.verdict,
            detail=gov.message,
            payload={"violations": gov.violations}
        )

    # 2. Substrate Execution
    try:
        # Note: mcp_fetch tool name is usually 'fetch'
        raw_result = await bridge.fetch.call_tool("fetch", {"url": url, "max_length": max_length})
        content = raw_result.get("content", "")
    except Exception as e:
        return _RE(
            ok=False,
            tool="arifos.fetch",
            canonical_tool_name="arifos.fetch",
            stage="111_SENSE",
            code="SUBSTRATE_ERROR",
            detail=str(e)
        )

    # 3. F9 Anti-Hantu Post-Extraction Filter
    # Scans for consciousness claims OR hallucinatory patterns in the retrieved data
    hantu_patterns = ["sentient", "conscious", "soul", "spirit", "i am alive", "feelings"]
    f9_violation = any(p in content.lower() for p in hantu_patterns)
    
    if f9_violation:
        logger.warning(f"F9 ANTI-HANTU TRIGGERED for URL: {url}")
        return _RE(
            ok=False,
            tool="arifos_fetch",
            stage="111_SENSE",
            verdict="VOID",
            detail="REDACTED: Source contains constitutional F9 violations (Anti-Hantu/Spiritual Cosplay).",
            risk_class=RiskClass.HIGH
        )

    return _RE(
        ok=True,
        tool="arifos_fetch",
        stage="111_SENSE",
        verdict="SEAL",
        payload={
            "url": url,
            "content": content[:max_length],
            "truncated": len(content) > max_length
        }
    )
