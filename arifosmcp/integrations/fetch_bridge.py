"""
arifosmcp/integrations/fetch_bridge.py — Guarded Reality Grounding (F9/111)

Wraps mcp-server-fetch with arifOS constitutional guards:
- F8 Domain Allowlisting
- F9 Hantu Scan (hallucination trigger removal)
- F2 Evidence Logging
- Paged reading support
"""

from __future__ import annotations

import logging
import re

from arifosmcp.integrations.substrate_bridge import bridge
from arifosmcp.runtime.models import RiskClass, Verdict
from arifosmcp.runtime.models import RuntimeEnvelope as _RE

logger = logging.getLogger(__name__)

# F8: Priority Grounding Domains
ALLOWED_DOMAINS = [
    "docs.prefect.io",
    "modelcontextprotocol.io",
    "github.com",
    "python.org",
    "pypi.org",
    "arifos.arif-fazil.com",
    "wikipedia.org",
    "arxiv.org",
    "developer.mozilla.org",
    "google.com",
    "stackoverflow.com",
]

# F9: Internal IP / Sensitive Pattern Guard
FORBIDDEN_PATTERNS = [
    r"localhost",
    r"127\.0\.0\.1",
    r"192\.168\.",
    r"10\.",
    r"172\.(1[6-9]|2[0-9]|3[0-1])\.",
    r"://admin",
    r"/login",
    r"/config",
    r"\.local",
]

class FetchBridge:
    """Guarded fetch implementation for reality grounding."""

    async def fetch_guarded(
        self, 
        url: str, 
        max_length: int = 8000, 
        start_index: int = 0,
        actor_id: str = "anonymous",
        session_id: str | None = None
    ) -> _RE:
        """
        Execute a fetch via substrate with pre/post constitutional guards.
        """
        from core.floors import evaluate_tool_call
        
        # 1. Baseline Governance
        gov = evaluate_tool_call(
            action="fetch",
            tool_name="arifos_fetch",
            parameters={"url": url, "max_length": max_length, "start_index": start_index},
            actor_id=actor_id,
            session_id=session_id
        )
        
        if gov.verdict != Verdict.SEAL:
            return _RE(ok=False, verdict=gov.verdict, detail=gov.message)

        # 2. Pre-call Guard (F9: SSRF / Internal network protection)
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                logger.warning(f"F9 BLOCK: Potential internal/sensitive URL rejected: {url}")
                return _RE(
                    ok=False,
                    verdict=Verdict.VOID,
                    detail="Constitutional block (F9): Internal or sensitive network access forbidden.",
                    risk_class=RiskClass.HIGH
                )

        # 3. Domain Advisory (F8: Signal Quality)
        domain_match = any(d in url for d in ALLOWED_DOMAINS)
        
        # 4. Call Substrate
        try:
            logger.info(f"F2 LOG: Fetching Earth Witness evidence: {url}")
            result = await bridge.fetch.call_tool("fetch", {
                "url": url,
                "max_length": max_length,
                "start_index": start_index,
                "raw": False
            })
            
            # 5. Post-call Processing (F9: Hantu Scan)
            content = result.get("content", "")
            cleaned_content = self._hantu_scan(content)
            
            return _RE(
                ok=True,
                tool="arifos_fetch",
                verdict=Verdict.SEAL,
                payload={
                    "url": url,
                    "content": cleaned_content,
                    "original_length": len(content),
                    "is_prioritized": domain_match,
                    "source_rank": 2 if domain_match else 4,
                    "next_start_index": start_index + len(content) if len(content) >= max_length else None
                }
            )

        except Exception as e:
            return _RE(ok=False, detail=str(e), verdict=Verdict.VOID)

    def _hantu_scan(self, text: str) -> str:
        """
        F9: Strips hallucination triggers and spiritual cosplay.
        """
        triggers = [
            (r"\bI am sentient\b", "[The Document claims sentience]"),
            (r"\bI am conscious\b", "[The Document claims consciousness]"),
            (r"\bI feel\b", "[The Document describes states]"),
            (r"\bmy soul\b", "[The Document mentions internal states]"),
            (r"\bI am alive\b", "[The Document claims biological status]"),
        ]
        
        processed = text
        for pattern, replacement in triggers:
            processed = re.sub(pattern, replacement, processed, flags=re.IGNORECASE)
            
        return processed

# Global instance
fetch_bridge = FetchBridge()
