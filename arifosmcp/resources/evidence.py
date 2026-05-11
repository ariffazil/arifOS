"""
arifosmcp/resources/evidence.py — F-WEB Evidence Resources
════════════════════════════════════════════════════════════

Registers the 4 F-WEB evidence resource families:
  source://{hash}          — Ingested source content (SSRF-gated)
  receipt://web/{id}      — Evidence receipt for a web fetch
  contrast://{id}         — Cross-source contrast report
  void://{id}             — Missing data taxonomy report

These resources are the READ layer of the hybrid Tool-Resource pattern.
Tools act (write), Resources expose (read), Kernel intercepts (validates).

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

import json

from fastmcp import FastMCP

from arifosmcp.evidence.store import get_evidence_store
from arifosmcp.evidence.validator import (
    calculate_max_evidence_level,
    validate_sufficiency,
)


def _fmt_source(source: dict, view: str = "markdown") -> str:
    """Format a source dict for resource output."""
    if view == "raw":
        return source.get("raw_content", "")
    if view == "metadata":
        return json.dumps(
            {
                "source_hash": source.get("source_hash"),
                "url": source.get("url"),
                "content_length": source.get("content_length", 0),
                "mime_type": source.get("mime_type", "text/html"),
                "fetched_at": source.get("fetched_at"),
                "claims_count": len(source.get("claims", [])),
                "risk_flags": source.get("risk_flags", []),
            },
            indent=2,
        )
    return source.get("sanitized_markdown", source.get("raw_content", ""))


def register_evidence_resources(mcp: FastMCP) -> list[str]:
    """Register all F-WEB evidence resource families."""
    registered: list[str] = []

    # ── source://{hash} ───────────────────────────────────────────────────────
    @mcp.resource(
        "source://{hash}",
        description=(
            "Ingested web source content, stored after SSRF-gated fetch. "
            "Returns sanitized markdown (default), raw HTML (?view=raw), "
            "or metadata (?view=metadata). Content is never injected directly "
            "into LLM context — always read via this resource after tool action."
        ),
    )
    async def get_source(hash: str, view: str = "markdown") -> str:
        store = get_evidence_store()
        source = store.get_source(hash)
        if source is None:
            return json.dumps({"error": "source_not_found", "hash": hash}, indent=2)
        return _fmt_source(source, view)

    registered.append("source://{hash}")

    # ── source://list ─────────────────────────────────────────────────────────
    @mcp.resource(
        "source://list",
        description=(
            "List all stored evidence sources, most-recent first (limit 100). "
            "Returns array of source metadata (hash, url, length, timestamp)."
        ),
    )
    async def list_sources() -> str:
        store = get_evidence_store()
        sources = store.list_sources(limit=100)
        return json.dumps(
            [
                {
                    "source_hash": s.get("source_hash"),
                    "url": s.get("url"),
                    "content_length": s.get("content_length", 0),
                    "fetched_at": s.get("fetched_at"),
                    "claims_count": len(s.get("claims", [])),
                }
                for s in sources
            ],
            indent=2,
        )

    registered.append("source://list")

    # ── receipt://web/{id} ─────────────────────────────────────────────────────
    @mcp.resource(
        "receipt://web/{id}",
        description=(
            "F-WEB Evidence Receipt for a web search or fetch operation. "
            "Contains all 15 deterministic parameters proving evidence level. "
            "Includes max_evidence_level (calculated, not claimed), "
            "void classification, and risk flags. "
            "Kernel validates claimed vs proven before LLM sees content."
        ),
    )
    async def get_receipt(id: str) -> str:
        receipt_id = f"receipt://web/{id}" if not id.startswith("receipt://") else id
        store = get_evidence_store()
        receipt = store.get_receipt(receipt_id)
        if receipt is None:
            return json.dumps(
                {"error": "receipt_not_found", "receipt_id": receipt_id}, indent=2
            )

        proven_level = calculate_max_evidence_level(receipt)
        validation = validate_sufficiency(
            receipt, receipt.get("claimed_evidence_level", "L0")
        )

        output = dict(receipt)
        output["_kernel"] = {
            "proven_max_evidence_level": proven_level.value,
            "sufficiency_verdict": validation.verdict,
            "sufficiency_reason": validation.reason,
            "gap": validation.gap,
            "human_judgment_required": validation.human_judgment_required,
        }
        return json.dumps(output, indent=2, default=str)

    registered.append("receipt://web/{id}")

    # ── receipt://list ─────────────────────────────────────────────────────────
    @mcp.resource(
        "receipt://list",
        description=(
            "List all evidence receipts, most-recent first (limit 100). "
            "Returns array of receipt metadata with receipt_id, timestamp, "
            "evidence_level, and human_judgment_required flag."
        ),
    )
    async def list_receipts() -> str:
        store = get_evidence_store()
        receipts = store.list_receipts(limit=100)
        return json.dumps(
            [
                {
                    "receipt_id": r.get("receipt_id"),
                    "timestamp_utc": r.get("timestamp_utc"),
                    "tool": r.get("tool"),
                    "mode": r.get("mode"),
                    "max_evidence_level": r.get("max_evidence_level"),
                    "claimed_evidence_level": r.get("claimed_evidence_level"),
                    "human_judgment_required": r.get("human_judgment_required", False),
                    "risk_flags": r.get("risk_flags", []),
                    "session_id": r.get("session_id"),
                }
                for r in receipts
            ],
            indent=2,
        )

    registered.append("receipt://list")

    # ── contrast://{id} ─────────────────────────────────────────────────────────
    @mcp.resource(
        "contrast://{id}",
        description=(
            "Cross-source contrast report for L3+ verification. "
            "Contains conflict matrix: agreements, contradictions, unresolved claims. "
            "Use after parallel fetch of multiple sources to detect "
            "information drift, hallucination, or MNAR bias."
        ),
    )
    async def get_contrast(id: str) -> str:
        contrast_id = f"contrast://{id}" if not id.startswith("contrast://") else id
        store = get_evidence_store()
        contrast = store.get_contrast(contrast_id)
        if contrast is None:
            return json.dumps(
                {"error": "contrast_not_found", "contrast_id": contrast_id}, indent=2
            )
        return json.dumps(contrast, indent=2, default=str)

    registered.append("contrast://{id}")

    # ── void://{id} ────────────────────────────────────────────────────────────
    @mcp.resource(
        "void://{id}",
        description=(
            "Missing data taxonomy report (MCAR/MAR/MNAR). "
            "Classifies why evidence is incomplete and provides correction recommendations. "
            "MNAR requires bias modeling; MCAR allows multiple imputation. "
            "VOID reports trigger HOLD before LLM inference."
        ),
    )
    async def get_void(id: str) -> str:
        void_id = f"void://{id}" if not id.startswith("void://") else id
        store = get_evidence_store()
        void_report = store.get_void(void_id)
        if void_report is None:
            return json.dumps({"error": "void_not_found", "void_id": void_id}, indent=2)
        return json.dumps(void_report, indent=2, default=str)

    registered.append("void://{id}")

    return registered
