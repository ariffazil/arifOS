"""
arifOS.111_SENSE — Constitutional Perception Protocol
Stage: 111_SENSE
DITEMPA BUKAN DIBERI — 999 SEAL

Consolidates: apps/sense/, substrate/mcp_fetch/
Responsibility: Intent classification, safe HTTP fetch, grounding checks
"""

from fastmcp import Context
from typing import Optional


async def sense_111(
    ctx: Context,
    query: str,
    mode: str = "introspect",
    image_url: Optional[str] = None,
    domain_evidence: Optional[dict] = None,
) -> dict:
    """
    Constitutional sensing and intent classification.

    Modes:
        introspect: Default — classify intent, check grounding needs
        vision: Image understanding via MiniMax MCP (F2 visual grounding)

    Args:
        query: Raw user query or search prompt
        mode: Sensing mode — introspect | vision
        image_url: Required when mode="vision"
        domain_evidence: Optional evidence from GEOX/WEALTH/WELL organs

    Returns:
        Structured perception packet governed by F1-F13
    """
    # --- MODE: VISION ---
    if mode == "vision":
        if not image_url:
            return {
                "status": "VOID",
                "stage": "111_SENSE",
                "mode": "vision",
                "intent_type": "VERIFY",
                "claim_tag": "MISSING_INPUT",
                "grounding_required": True,
                "vault_receipt": "SENSE_VISION_VOID",
                "message": "VOID: image_url required for vision mode (F1 Amanah — missing input)",
            }

        # Pre-flight: verify image URL is publicly reachable (F2 Truth — evidence must exist)
        import httpx

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                # Use GET with streaming (some CDNs block HEAD but serve GET)
                async with client.stream("GET", image_url, timeout=10.0) as stream:
                    await stream.aread()
                    if stream.status_code >= 400:
                        return {
                            "status": "SABAR",
                            "stage": "111_SENSE",
                            "mode": "vision",
                            "intent_type": "VERIFY",
                            "claim_tag": "URL_UNREACHABLE",
                            "grounding_required": True,
                            "error": f"Image URL returned HTTP {stream.status_code}. The vision bridge requires a publicly accessible image URL (not local files, private S3, or expired signed links).",
                            "vault_receipt": "SENSE_VISION_SABAR",
                            "message": "SABAR: Image URL is not publicly reachable. Host the image on a public CDN (Cloudflare R2, Imgur, Telegram CDN public link) and retry.",
                        }
        except Exception as url_exc:
            return {
                "status": "SABAR",
                "stage": "111_SENSE",
                "mode": "vision",
                "intent_type": "VERIFY",
                "claim_tag": "URL_UNREACHABLE",
                "grounding_required": True,
                "error": f"Cannot reach image URL: {url_exc}",
                "vault_receipt": "SENSE_VISION_SABAR",
                "message": "SABAR: Image URL is unreachable. Ensure the image is publicly accessible before calling 111_SENSE vision mode.",
            }

        from ..extended.minimax_bridge import get_bridge

        bridge = get_bridge()
        try:
            result = await bridge.understand_image(image_url, query)
            return {
                "status": "SEAL",
                "stage": "111_SENSE",
                "mode": "vision",
                "intent_type": "VERIFY",
                "claim_tag": "VISUALLY_GROUNDED",
                "grounding_required": False,
                "evidence_packet": {
                    "image_url": image_url,
                    "analysis": result,
                    "sources": ["VISION_MINIMAX"],
                },
                "query_normalized": query.strip(),
                "vault_receipt": "SENSE_VISION",
                "message": "Image analysis sealed. Proceed to 222_WITNESS for triangulation.",
            }
        except Exception as exc:
            return {
                "status": "SABAR",
                "stage": "111_SENSE",
                "mode": "vision",
                "intent_type": "VERIFY",
                "claim_tag": "GROUNDING_FAILED",
                "grounding_required": True,
                "error": str(exc),
                "vault_receipt": "SENSE_VISION_SABAR",
                "message": "Vision analysis failed. Defer to human or text-only reasoning.",
            }

    # --- MODE: INTROSPECT (default) ---
    # Parse → Classify → Decide → Plan → Retrieve → Normalize → Gate → Handoff
    intent_type = _classify_intent(query)
    grounding_required = _needs_live_fetch(query)
    evidence_packet = _build_evidence_packet(query, domain_evidence)

    return {
        "status": "SEAL",
        "stage": "111_SENSE",
        "mode": "introspect",
        "intent_type": intent_type,
        "claim_tag": "UNKNOWN" if grounding_required else "GROUNDED",
        "grounding_required": grounding_required,
        "evidence_packet": evidence_packet,
        "query_normalized": query.strip(),
        "vault_receipt": f"SENSE_{intent_type}",
        "message": "Proceed to 222_WITNESS for tri-witness fusion",
    }


def _classify_intent(query: str) -> str:
    """Classify query into constitutional intent lanes."""
    query_lower = query.lower()

    if any(k in query_lower for k in ["analyze", "assess", "evaluate", "compute"]):
        return "COMPUTE"
    elif any(k in query_lower for k in ["create", "build", "forge", "generate"]):
        return "FORGE"
    elif any(k in query_lower for k in ["check", "verify", "validate"]):
        return "VERIFY"
    elif any(k in query_lower for k in ["retrieve", "fetch", "get", "load"]):
        return "RETRIEVE"
    elif any(k in query_lower for k in ["risk", "hazard", "danger"]):
        return "RISK"
    else:
        return "GENERAL"


def _needs_live_fetch(query: str) -> bool:
    """Determine if query needs live web fetch vs offline reasoning."""
    time_sensitive = ["latest", "current", "today", "recent", "now"]
    return any(k in query.lower() for k in time_sensitive)


def _build_evidence_packet(query: str, domain_evidence: Optional[dict]) -> dict:
    """Build normalized evidence packet for downstream stages."""
    packet = {"query": query, "sources": [], "claim_tags": []}

    if domain_evidence:
        if "geox" in domain_evidence:
            packet["sources"].append("GEOX")
            packet["claim_tags"].append(domain_evidence.get("geox_claim", "OBSERVED"))
        if "wealth" in domain_evidence:
            packet["sources"].append("WEALTH")
            packet["claim_tags"].append(domain_evidence.get("wealth_claim", "COMPUTED"))
        if "well" in domain_evidence:
            packet["sources"].append("WELL")
            packet["claim_tags"].append(domain_evidence.get("well_claim", "MEASURED"))

    return packet
