"""
arifosmcp/resources/wisdom_resources.py — Quote Registry MCP Resources

Exposes the provenance-typed quote registry as MCP resources.
Resources are read-only. Quotes are resources, not tools.

Resource URIs:
  arifos://wisdom/quotes/all              — All quotes
  arifos://wisdom/quotes/by-floor/{fid}   — Filter by constitutional floor
  arifos://wisdom/quotes/by-tradition/{t} — Filter by tradition
  arifos://wisdom/quotes/disputed         — Disputed attribution quotes
  arifos://wisdom/quotes/arifos-doctrine  — arifOS doctrine entries
  arifos://wisdom/quotes/prohibited-uses  — Prohibited use patterns

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
from typing import Any

from ..runtime.quote_registry import (
    C_DARK_CEILING,  # Layer A
    CANON_STATUS_TIERS,  # Layer C
    G_DEPLOY_THRESHOLD,  # Layer A
    compute_apex_fingerprint,  # Layer A
    compute_canon_status,  # Layer C
    get_disputed_quotes,
    get_doctrine,
    get_prohibited_uses,
    get_quotes_by_floor,
    get_quotes_by_tradition,
    load_registry,
)

logger = logging.getLogger(__name__)


def register_wisdom_resources(mcp) -> list[str]:
    """Register wisdom quote resources on an MCP server instance.

    Returns list of registered resource URIs.
    """
    registered: list[str] = []

    # ── All quotes ──────────────────────────────────────────────────────────
    @mcp.resource("arifos://wisdom/quotes/all")
    def wisdom_quotes_all() -> str:
        """Return all quotes from the canonical registry with provenance metadata."""
        reg = load_registry()
        quotes = reg.get("quotes", [])
        doctrine = reg.get("doctrine", [])

        result = {
            "_meta": reg.get("_meta", reg.get("_metadata", {})),
            "doctrine_count": len(doctrine),
            "quote_count": len(quotes),
            "doctrine": [
                {
                    "doctrine_id": d.get("doctrine_id"),
                    "name": d.get("name"),
                    "text": d.get("text"),
                    # v2: ratification_status; legacy: status.ratification
                    "ratification": d.get("ratification_status")
                    or (d.get("status") or {}).get("ratification"),
                }
                for d in doctrine
            ],
            "quotes": [_summarize_quote(q) for q in quotes],
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    registered.append("arifos://wisdom/quotes/all")

    # ── Single quote by id ──────────────────────────────────────────────────
    @mcp.resource("arifos://wisdom/quotes/{quote_id}")
    def wisdom_quote_by_id(quote_id: str) -> str:
        """Return a single quote by its canonical id (text hash or legacy id)."""
        reg = load_registry()
        quotes = reg.get("quotes", [])
        for q in quotes:
            qid = q.get("id") or q.get("quote_id")
            if qid == quote_id:
                return json.dumps(_summarize_quote(q), indent=2, ensure_ascii=False)
            # Also check legacy deprecated_ids
            v3 = q.get("_v3") or {}
            if quote_id in v3.get("deprecated_ids", []):
                result = _summarize_quote(q)
                result["_redirected_from"] = quote_id
                return json.dumps(result, indent=2, ensure_ascii=False)
        return json.dumps({"found": False, "quote_id": quote_id, "error": "not found"}, indent=2)

    registered.append("arifos://wisdom/quotes/{quote_id}")

    # ── By floor ────────────────────────────────────────────────────────────
    @mcp.resource("arifos://wisdom/quotes/by-floor/{floor_id}")
    def wisdom_quotes_by_floor(floor_id: str) -> str:
        """Return quotes mapped to a constitutional floor (e.g., F2, F7)."""
        result = get_quotes_by_floor(floor_id)
        return json.dumps(
            {"floor": floor_id, "count": len(result), "quotes": result},
            indent=2,
            ensure_ascii=False,
        )

    registered.append("arifos://wisdom/quotes/by-floor/{floor_id}")

    # ── By tradition ────────────────────────────────────────────────────────
    @mcp.resource("arifos://wisdom/quotes/by-tradition/{tradition}")
    def wisdom_quotes_by_tradition(tradition: str) -> str:
        """Return quotes from a specific tradition (e.g., islam, daoism, nusantara)."""
        result = get_quotes_by_tradition(tradition)
        return json.dumps(
            {"tradition": tradition, "count": len(result), "quotes": result},
            indent=2,
            ensure_ascii=False,
        )

    registered.append("arifos://wisdom/quotes/by-tradition/{tradition}")

    # ── Disputed ────────────────────────────────────────────────────────────
    @mcp.resource("arifos://wisdom/quotes/disputed")
    def wisdom_quotes_disputed() -> str:
        """Return all quotes with disputed attribution."""
        result = get_disputed_quotes()
        return json.dumps({"count": len(result), "quotes": result}, indent=2, ensure_ascii=False)

    registered.append("arifos://wisdom/quotes/disputed")

    # ── Doctrine ────────────────────────────────────────────────────────────
    @mcp.resource("arifos://wisdom/quotes/arifos-doctrine")
    def wisdom_doctrine() -> str:
        """Return arifOS doctrine entries (separated from inherited quotations)."""
        result = get_doctrine()
        return json.dumps({"count": len(result), "doctrine": result}, indent=2, ensure_ascii=False)

    registered.append("arifos://wisdom/quotes/arifos-doctrine")

    # ── Prohibited uses ─────────────────────────────────────────────────────
    @mcp.resource("arifos://wisdom/quotes/prohibited-uses")
    def wisdom_prohibited_uses() -> str:
        """Return all prohibited use patterns for quotations."""
        result = get_prohibited_uses()
        return json.dumps(
            {"count": len(result), "prohibited_uses": result}, indent=2, ensure_ascii=False
        )

    registered.append("arifos://wisdom/quotes/prohibited-uses")

    # ── Layer B: APEX fingerprint namespace ────────────────────────────────
    @mcp.resource("arifos://wisdom/fingerprint/{quote_id}")
    def wisdom_fingerprint(quote_id: str) -> str:
        """APEX fingerprint for a single quote.

        Returns G (multiplicative intelligence), C_dark (shadow term), per-organ
        scores, shadow_state, true_devil_risk, deploy_warrant.

        Federation contract: every quote carry deploy_warrant; only GOVERNED
        shadow state quotes may ride with verdicts.
        """
        reg = load_registry()
        quote = None
        for q in reg.get("quotes", []):
            if q.get("id") == quote_id or q.get("quote_id") == quote_id:
                quote = q
                break
        if quote is None:
            return json.dumps(
                {"found": False, "quote_id": quote_id, "error": "quote not found"},
                indent=2,
            )
        fingerprint = compute_apex_fingerprint(quote, intended_use="REFLECTION")
        return json.dumps(
            {
                "quote_id": quote_id,
                "speaker": (quote.get("attribution") or {}).get("speaker"),
                "apex_fingerprint": fingerprint,
                "thresholds": {
                    "G_DEPLOY_THRESHOLD": G_DEPLOY_THRESHOLD,
                    "C_DARK_CEILING": C_DARK_CEILING,
                },
            },
            indent=2,
            ensure_ascii=False,
        )

    registered.append("arifos://wisdom/fingerprint/{quote_id}")

    # ── Layer B: canon-status namespace ────────────────────────────────────
    @mcp.resource("arifos://wisdom/canon-status/{quote_id}")
    def wisdom_canon_status(quote_id: str) -> str:
        """Canon-status tier for a quote (Layer C).

        Tier ladder:
            DRAFT        — newly forged, not load-bearing
            PROVISIONAL  — ratified, ≥3 successful uses, no failures
            CANON_SEALED — appended to VAULT999 chain with sovereign signature

        Council entries (COUNCIL_*) are FORCED DRAFT regardless of in-registry
        hints. Promotion requires sovereign ratification via arif_judge → arif_seal.
        """
        reg = load_registry()
        quote = None
        for q in reg.get("quotes", []):
            if q.get("id") == quote_id or q.get("quote_id") == quote_id:
                quote = q
                break
        if quote is None:
            return json.dumps(
                {"found": False, "quote_id": quote_id, "error": "quote not found"},
                indent=2,
            )
        canon_status = compute_canon_status(quote)
        return json.dumps(
            {
                "quote_id": quote_id,
                "canon_status": canon_status,
                "tier_definition": {
                    "DRAFT": "Newly forged, not load-bearing. Default for council entries pending sovereign ratification.",
                    "PROVISIONAL": "Ratified. ≥3 successful uses, no failures. Manual promotion only.",
                    "CANON_SEALED": "Appended to VAULT999 chain. Irrevocable. Requires sovereign signature.",
                },
                "available_tiers": list(CANON_STATUS_TIERS),
                "promotion_path": "arif_judge → arif_seal → VAULT999 (sovereign ratification required)",
            },
            indent=2,
            ensure_ascii=False,
        )

    registered.append("arifos://wisdom/canon-status/{quote_id}")

    # ── Layer B: federation manifest ───────────────────────────────────────
    @mcp.resource("arifos://wisdom/contract")
    def wisdom_contract() -> str:
        """Federation contract for the wisdom/quote namespace.

        Single source of truth for cross-organ integration. Defines:
        - 7 APEX organs + multiplicative G formula
        - shadow_state taxonomy (Pillar VI)
        - canon_status tier ladder
        - stage binding (555_HEART | 999_RECEIPT only)
        - citation rules (prohibited: factual_evidence, verdict_authority)
        """
        return json.dumps(
            {
                "namespace": "arifos://wisdom",
                "owner": "arifOS",
                "canonical_source": "arifosmcp/data/quote_registry_v2.json",
                "apex_alignment": {
                    "formula": "G = Reality · Governance · Civilization · Execution · Memory · Witness · Meaning",
                    "invariance": "multiplicative — zero anywhere = collapse",
                    "shadow_formula": "C_dark = (1-confidence)·disputed + 0.3·fictional + 0.1·missing_prohibited + 0.2·fictional_in_receipt",
                    "shadow_states": {
                        "GOVERNED": "G ≥ 0.50 AND C_dark ≤ 0.30 — deploy_warrant=true",
                        "UNCHECKED": "0.30 < C_dark ≤ 0.50 — deploy with caution",
                        "HIDDEN": "C_dark > 0.50 — TRUE DEVIL risk, do not deploy",
                    },
                    "thresholds": {
                        "G_DEPLOY_THRESHOLD": G_DEPLOY_THRESHOLD,
                        "C_DARK_CEILING": C_DARK_CEILING,
                    },
                    "canon_seal": "2026-07-13",
                },
                "canon_status_tiers": list(CANON_STATUS_TIERS),
                "stage_binding": ["555_HEART", "999_RECEIPT"],
                "stage_forbidden": [
                    "000_INIT",
                    "111_OBSERVE",
                    "333_THINK",
                    "444_ROUTE",
                    "777_FORGE",
                    "888_AUDIT",
                ],
                "prohibited_uses": ["factual_evidence", "verdict_authority"],
                "sealed_council_ids": [],
                "draft_council_ids_count": 17,
                "draft_council_ids_pending_sovereign_ratification": True,
                "resources": [
                    "arifos://wisdom/quotes/all",
                    "arifos://wisdom/quotes/{quote_id}",
                    "arifos://wisdom/quotes/by-floor/{floor_id}",
                    "arifos://wisdom/quotes/by-tradition/{tradition}",
                    "arifos://wisdom/quotes/disputed",
                    "arifos://wisdom/quotes/arifos-doctrine",
                    "arifos://wisdom/quotes/prohibited-uses",
                    "arifos://wisdom/fingerprint/{quote_id}",
                    "arifos://wisdom/canon-status/{quote_id}",
                    "arifos://wisdom/contract",
                ],
            },
            indent=2,
            ensure_ascii=False,
        )

    registered.append("arifos://wisdom/contract")

    logger.info("Registered %d wisdom resources (Layer B contract namespace live)", len(registered))
    return registered


def _summarize_quote(q: dict) -> dict[str, Any]:
    """Create a safe summary of a quote for resource responses.

    v3: flat fields. Derives source_class, strips constant fields,
    renders display_label from speaker + popularized_by + confidence.
    Falls back to v2 nested format for compatibility.
    """
    # ── Primary: v3 flat fields ──
    text_str = str(q.get("text", "") or "")
    if isinstance(text_str, dict):
        text_str = str(text_str.get("canonical") or text_str.get("normalized") or "")
    language = q.get("language", "en")

    # speaker — flat v3 or nested v2 fallback
    speaker = q.get("speaker") or (q.get("attribution") or {}).get("speaker", "Unknown")

    # confidence — flat v3 or nested v2 fallback
    confidence = q.get("attribution_confidence") or (q.get("attribution") or {}).get(
        "attribution_confidence", 0.0
    )
    if isinstance(confidence, (int, float)):
        confidence = float(confidence)
    else:
        confidence = 0.0

    # source_class — derive from confidence (v3) or read nested (v2 fallback)
    attr = q.get("attribution") or {}
    source_class = attr.get("source_class", "")
    if not source_class and confidence:
        if confidence >= 0.95:
            source_class = "PRIMARY_VERIFIED"
        elif confidence >= 0.85:
            source_class = "SECONDARY_VERIFIED"
        elif confidence >= 0.70:
            source_class = "PARAPHRASE"
        elif confidence >= 0.50:
            source_class = "TRADITIONAL"
        elif confidence >= 0.30:
            source_class = "DISPUTED_ATTRIBUTION"
        else:
            source_class = "UNCERTAIN"

    # display_label — flat v3 or derived
    popularized_by = q.get("popularized_by")
    display_label = q.get("display_label", "")
    if not display_label:
        if popularized_by:
            display_label = f"{speaker}, quoted by {popularized_by}"
        else:
            display_label = speaker
    if confidence < 0.45:
        display_label += " (attribution uncertain)"
    elif confidence < 0.60 and source_class == "DISPUTED_ATTRIBUTION":
        display_label += " (attribution disputed)"

    # Traditions/tags/floors — flat v3 or nested v2 fallback
    cls_ = q.get("classification") or {}
    tradition = q.get("tradition") or cls_.get("tradition", [])
    tags = q.get("tags") or cls_.get("tags", [])
    floors = q.get("arifos_floors") or cls_.get("arifos_floors", [])
    dark = q.get("dark_modes") or cls_.get("dark_modes", [])

    # permitted_uses — flat v3 or nested v2 fallback
    usage = q.get("usage") or {}
    permitted = q.get("permitted_uses") or usage.get("permitted", [])

    result: dict[str, Any] = {
        "id": q.get("id", q.get("quote_id", "")),
        "text": text_str,
        "language": language,
        "speaker": speaker,
        "source_class": source_class,
        "attribution_confidence": confidence,
        "display_label": display_label,
        "tradition": tradition if isinstance(tradition, list) else [],
        "tags": tags if isinstance(tags, list) else [],
        "floors": floors if isinstance(floors, list) else [],
        "dark_modes": dark if isinstance(dark, list) else [],
        "permitted_uses": permitted if isinstance(permitted, list) else [],
    }
    if popularized_by:
        result["popularized_by"] = popularized_by
    return result
