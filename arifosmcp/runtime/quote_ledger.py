"""
arifosmcp/runtime/quote_ledger.py — Locked Quote Ledger v1

The canonical, append-only registry of approved wisdom quotes.
All entries are validated at load time.
No quote may be used unless allow_use=true and source_status != "uncertain".

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMA CONTRACT
# ═══════════════════════════════════════════════════════════════════════════════

REQUIRED_FIELDS: set[str] = {
    "id",
    "quote",
    "author",
    "tradition",
    "domain",
    "theme",
    "trigger_conditions",
    "arifos_mapping",
    "action_bias",
    "risk_use",
    "source_status",
    "allow_use",
}

VALID_ACTION_BIASES: set[str] = {
    "pause_and_reflect",
    "request_approval",
    "proceed_carefully",
    "refuse",
    "hold",
}

VALID_RISK_LEVELS: set[str] = {
    "low",
    "medium",
    "high",
    "critical",
    "irreversible",
}

VALID_SOURCE_STATUSES: set[str] = {
    "verified",
    "public_domain",
    "curated",
    "uncertain",
}

_ARIFOS_MAPPING_FIELDS: set[str] = {"physics", "math", "linguistic"}

_LEDGER_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "wisdom_quotes_lite.json"
)
_loaded_ledger: list[dict[str, Any]] | None = None


class QuoteIntegrityError(Exception):
    """Raised when a quote fails structural or content integrity checks."""

    pass


class QuoteSchemaError(Exception):
    """Raised when a quote is missing required fields or has invalid values."""

    pass


# ═══════════════════════════════════════════════════════════════════════════════
# LOAD
# ═══════════════════════════════════════════════════════════════════════════════


def load_quote_ledger(
    path: Path | str | None = None,
    force_reload: bool = False,
) -> list[dict[str, Any]]:
    """Load and validate the entire quote ledger from disk.

    Returns a list of validated quote dicts.  Raises QuoteSchemaError if any
    entry is malformed.  Caches the result in-process; use *force_reload* to
    invalidate.
    """
    global _loaded_ledger

    if _loaded_ledger is not None and not force_reload:
        return _loaded_ledger

    ledger_path = Path(path) if path else _LEDGER_PATH
    if not ledger_path.exists():
        raise QuoteSchemaError(f"Ledger file not found: {ledger_path}")

    try:
        with ledger_path.open("r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except json.JSONDecodeError as exc:
        raise QuoteSchemaError(f"Ledger JSON decode error: {exc}")

    if not isinstance(raw, list):
        raise QuoteSchemaError("Ledger root must be a JSON list.")

    validated: list[dict[str, Any]] = []
    for idx, entry in enumerate(raw):
        try:
            validate_quote_schema(entry)
        except QuoteSchemaError as exc:
            raise QuoteSchemaError(
                f"Entry {idx} (id={entry.get('id', '?')}) invalid: {exc}"
            )
        validated.append(entry)

    _loaded_ledger = validated
    logger.info("Loaded %d quotes from %s", len(validated), ledger_path)
    return validated


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATE
# ═══════════════════════════════════════════════════════════════════════════════


def validate_quote_schema(quote: dict[str, Any]) -> None:
    """Validate a single quote dict against the canonical schema.

    Raises QuoteSchemaError on any violation.
    """
    missing = REQUIRED_FIELDS - set(quote.keys())
    if missing:
        raise QuoteSchemaError(f"Missing fields: {sorted(missing)}")

    # Types
    if not isinstance(quote["id"], str) or not quote["id"]:
        raise QuoteSchemaError("id must be a non-empty string")
    if not isinstance(quote["quote"], str) or not quote["quote"]:
        raise QuoteSchemaError("quote must be a non-empty string")
    if not isinstance(quote["author"], str) or not quote["author"]:
        raise QuoteSchemaError("author must be a non-empty string")
    if not isinstance(quote["tradition"], str) or not quote["tradition"]:
        raise QuoteSchemaError("tradition must be a non-empty string")
    if not isinstance(quote["theme"], str) or not quote["theme"]:
        raise QuoteSchemaError("theme must be a non-empty string")
    if not isinstance(quote["domain"], list) or not all(
        isinstance(d, str) for d in quote["domain"]
    ):
        raise QuoteSchemaError("domain must be a list of strings")
    if not isinstance(quote["trigger_conditions"], list) or not all(
        isinstance(t, str) for t in quote["trigger_conditions"]
    ):
        raise QuoteSchemaError("trigger_conditions must be a list of strings")
    if not isinstance(quote["arifos_mapping"], dict):
        raise QuoteSchemaError("arifos_mapping must be a dict")
    if not isinstance(quote["risk_use"], list) or not all(
        isinstance(r, str) for r in quote["risk_use"]
    ):
        raise QuoteSchemaError("risk_use must be a list of strings")
    if not isinstance(quote["allow_use"], bool):
        raise QuoteSchemaError("allow_use must be a bool")

    # Enum checks
    if quote["action_bias"] not in VALID_ACTION_BIASES:
        raise QuoteSchemaError(
            f"action_bias={quote['action_bias']!r} not in {VALID_ACTION_BIASES}"
        )
    invalid_risks = set(quote["risk_use"]) - VALID_RISK_LEVELS
    if invalid_risks:
        raise QuoteSchemaError(f"Invalid risk_use values: {invalid_risks}")
    if quote["source_status"] not in VALID_SOURCE_STATUSES:
        raise QuoteSchemaError(
            f"source_status={quote['source_status']!r} not in {VALID_SOURCE_STATUSES}"
        )

    # arifos_mapping sub-fields
    mapping = quote["arifos_mapping"]
    missing_map = _ARIFOS_MAPPING_FIELDS - set(mapping.keys())
    if missing_map:
        raise QuoteSchemaError(f"arifos_mapping missing: {sorted(missing_map)}")
    for key in _ARIFOS_MAPPING_FIELDS:
        if not isinstance(mapping[key], str):
            raise QuoteSchemaError(f"arifos_mapping.{key} must be a string")

    # Governance: uncertain or disallowed quotes are structurally valid but
    # must never be returned by retrieval.  We do not reject them at schema
    # level so the ledger can contain them for audit / transparency.


# ═══════════════════════════════════════════════════════════════════════════════
# LOOKUP
# ═══════════════════════════════════════════════════════════════════════════════


def get_quote_by_id(quote_id: str) -> dict[str, Any] | None:
    """Return a single quote by its canonical ID, or None."""
    ledger = load_quote_ledger()
    for q in ledger:
        if q["id"] == quote_id:
            return q
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRITY ASSERTION
# ═══════════════════════════════════════════════════════════════════════════════


def assert_quote_integrity(
    candidate: dict[str, Any],
    ledger_quote: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Assert that *candidate* matches the canonical ledger entry.

    If *ledger_quote* is not provided, it is looked up by candidate["id"].

    Returns a dict:
      {"ok": bool, "error": str | None, "field": str | None}

    Fail-closed: any mismatch returns ok=False.
    """
    if ledger_quote is None:
        if not candidate.get("id"):
            return {"ok": False, "error": "candidate missing id", "field": "id"}
        ledger_quote = get_quote_by_id(candidate["id"])
        if ledger_quote is None:
            return {
                "ok": False,
                "error": "quote_not_in_approved_ledger",
                "field": "id",
            }

    # Exact text match (strip only outer whitespace; internal whitespace matters)
    if candidate.get("quote", "").strip() != ledger_quote["quote"].strip():
        return {
            "ok": False,
            "error": "quote_integrity_failed",
            "field": "quote",
        }

    # Exact author match
    if candidate.get("author", "").strip() != ledger_quote["author"].strip():
        return {
            "ok": False,
            "error": "author_integrity_failed",
            "field": "author",
        }

    # allow_use must be true
    if not ledger_quote.get("allow_use", False):
        return {
            "ok": False,
            "error": "quote_not_approved_for_use",
            "field": "allow_use",
        }

    # uncertain status must not be used
    if ledger_quote.get("source_status") == "uncertain":
        return {
            "ok": False,
            "error": "quote_source_uncertain",
            "field": "source_status",
        }

    return {"ok": True, "error": None, "field": None}


__all__ = [
    "load_quote_ledger",
    "validate_quote_schema",
    "get_quote_by_id",
    "assert_quote_integrity",
    "QuoteIntegrityError",
    "QuoteSchemaError",
]
