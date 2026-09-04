"""
claim_ledger.py — arifOS Claim Ledger Engine
═══════════════════════════════════════════════

Phase 1: General claim ledger infrastructure for the federation.
Every claim has a falsification path. Every ledger is verifiable.

Modes:
  create   — Create a new claim ledger
  validate — Validate a claim against sources
  challenge — Challenge a claim with counter-evidence
  seal     — Seal a claim to VAULT999 (irreversible)
  attach   — Attach evidence to an existing claim
  query    — Query claims by domain, status, classification

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Claim Ledger storage root
LEDGER_ROOT = Path("/root/.local/share/arifos/claim_ledgers")

# Classification scheme (epistemic labels)
CLASSIFICATION_SCHEME = ["OBS", "OBS_PROJ", "DER", "INT", "SPEC"]

# Claim lifecycle statuses
CLAIM_STATUSES = ["proposed", "validated", "challenged", "falsified", "sealed"]


def _ensure_ledger_root() -> None:
    """Ensure ledger storage directory exists."""
    LEDGER_ROOT.mkdir(parents=True, exist_ok=True)


def _ledger_path(ledger_id: str) -> Path:
    """Get path to a ledger file."""
    return LEDGER_ROOT / f"{ledger_id}.json"


def _load_ledger(ledger_id: str) -> dict[str, Any] | None:
    """Load a ledger from disk."""
    path = _ledger_path(ledger_id)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to load ledger {ledger_id}: {e}")
        return None


def _save_ledger(ledger_id: str, ledger: dict[str, Any]) -> bool:
    """Save a ledger to disk."""
    _ensure_ledger_root()
    path = _ledger_path(ledger_id)
    try:
        path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception as e:
        logger.error(f"Failed to save ledger {ledger_id}: {e}")
        return False


def _compute_claim_hash(claim: dict[str, Any]) -> str:
    """Compute deterministic hash of a claim for tamper-evidence."""
    canonical = json.dumps(claim, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def create_ledger(
    ledger_id: str,
    source_article: str = "",
    verification_principle: str = "3 clicks to formula + counterargument",
    sovereign: str = "ARIF",
) -> dict[str, Any]:
    """
    Create a new claim ledger.

    Returns:
        dict with ledger_id, status, path
    """
    if _load_ledger(ledger_id):
        return {"status": "error", "reason": f"Ledger {ledger_id} already exists"}

    now = datetime.now(UTC).isoformat()
    ledger = {
        "ledger": {
            "id": ledger_id,
            "version": 1.0,
            "source_article": source_article,
            "claim_count": 0,
            "classification_scheme": CLASSIFICATION_SCHEME,
            "verification_principle": verification_principle,
            "created_at": now,
            "last_updated": now,
            "sovereign": sovereign,
        },
        "claims": [],
    }

    if _save_ledger(ledger_id, ledger):
        return {
            "status": "created",
            "ledger_id": ledger_id,
            "path": str(_ledger_path(ledger_id)),
        }
    return {"status": "error", "reason": "Failed to save ledger"}


def add_claim(
    ledger_id: str,
    claim_id: str,
    claim_text: str,
    classification: str,
    confidence: float,
    counterargument: str,
    source_documents: list[dict[str, Any]] | None = None,
    formula: str = "",
    falsification_conditions: list[str] | None = None,
    domain: str = "federation",
    evidence_refs: list[str] | None = None,
    linked_claims: list[str] | None = None,
) -> dict[str, Any]:
    """
    Add a claim to a ledger.

    INVARIANT: counterargument is REQUIRED — every claim must have a falsification path.

    Returns:
        dict with claim_id, status, hash
    """
    ledger = _load_ledger(ledger_id)
    if not ledger:
        return {"status": "error", "reason": f"Ledger {ledger_id} not found"}

    # Check for duplicate claim_id
    existing_ids = [c["claim_id"] for c in ledger["claims"]]
    if claim_id in existing_ids:
        return {"status": "error", "reason": f"Claim {claim_id} already exists in ledger"}

    # Validate classification
    if classification not in CLASSIFICATION_SCHEME:
        return {
            "status": "error",
            "reason": f"Invalid classification {classification}. Must be one of {CLASSIFICATION_SCHEME}",
        }

    # Validate confidence (F7 HUMILITY: cap at 0.97)
    if confidence > 0.97:
        confidence = 0.97

    # INVARIANT: counterargument required
    if not counterargument or counterargument.strip() == "":
        return {
            "status": "error",
            "reason": "counterargument is REQUIRED — every claim must have a falsification path",
        }

    now = datetime.now(UTC).isoformat()
    claim = {
        "claim_id": claim_id,
        "claim_text": claim_text,
        "classification": classification,
        "confidence": confidence,
        "source_documents": source_documents or [],
        "formula": formula,
        "counterargument": counterargument,
        "falsification_conditions": falsification_conditions or [],
        "last_verified": now,
        "domain": domain,
        "evidence_refs": evidence_refs or [],
        "linked_claims": linked_claims or [],
        "status": "proposed",
    }

    claim_hash = _compute_claim_hash(claim)
    claim["hash"] = claim_hash

    ledger["claims"].append(claim)
    ledger["ledger"]["claim_count"] = len(ledger["claims"])
    ledger["ledger"]["last_updated"] = now

    if _save_ledger(ledger_id, ledger):
        return {
            "status": "added",
            "claim_id": claim_id,
            "hash": claim_hash,
            "classification": classification,
            "confidence": confidence,
        }
    return {"status": "error", "reason": "Failed to save claim"}


def validate_claim(
    ledger_id: str,
    claim_id: str,
    verifier: str = "333-AGI",
) -> dict[str, Any]:
    """
    Validate a claim against its sources.

    Returns:
        dict with claim_id, status, validation_result
    """
    ledger = _load_ledger(ledger_id)
    if not ledger:
        return {"status": "error", "reason": f"Ledger {ledger_id} not found"}

    claim = next((c for c in ledger["claims"] if c["claim_id"] == claim_id), None)
    if not claim:
        return {"status": "error", "reason": f"Claim {claim_id} not found"}

    # Check hash integrity
    stored_hash = claim.get("hash")
    computed_hash = _compute_claim_hash({k: v for k, v in claim.items() if k != "hash"})
    hash_ok = stored_hash == computed_hash

    # Check source documents exist
    has_sources = len(claim.get("source_documents", [])) > 0

    # Check counterargument exists
    has_counterargument = bool(claim.get("counterargument"))

    validation_result = {
        "claim_id": claim_id,
        "hash_integrity": hash_ok,
        "has_sources": has_sources,
        "has_counterargument": has_counterargument,
        "classification": claim["classification"],
        "confidence": claim["confidence"],
        "verifier": verifier,
        "timestamp": datetime.now(UTC).isoformat(),
    }

    # Update claim status
    if hash_ok and has_sources and has_counterargument:
        claim["status"] = "validated"
        claim["last_verified"] = datetime.now(UTC).isoformat()
        validation_result["verdict"] = "VALID"
    else:
        validation_result["verdict"] = "NEEDS_ATTENTION"
        if not hash_ok:
            validation_result["issue"] = "hash_mismatch"
        elif not has_sources:
            validation_result["issue"] = "no_sources"
        elif not has_counterargument:
            validation_result["issue"] = "no_counterargument"

    # Save updated ledger
    ledger["ledger"]["last_updated"] = datetime.now(UTC).isoformat()
    _save_ledger(ledger_id, ledger)

    return validation_result


def challenge_claim(
    ledger_id: str,
    claim_id: str,
    challenge_text: str,
    challenger: str = "333-AGI",
    evidence_refs: list[str] | None = None,
) -> dict[str, Any]:
    """
    Challenge a claim with counter-evidence.

    Returns:
        dict with claim_id, status, challenge_result
    """
    ledger = _load_ledger(ledger_id)
    if not ledger:
        return {"status": "error", "reason": f"Ledger {ledger_id} not found"}

    claim = next((c for c in ledger["claims"] if c["claim_id"] == claim_id), None)
    if not claim:
        return {"status": "error", "reason": f"Claim {claim_id} not found"}

    # Update claim status
    claim["status"] = "challenged"
    claim["last_verified"] = datetime.now(UTC).isoformat()

    # Add challenge to metadata
    if "challenges" not in claim:
        claim["challenges"] = []
    claim["challenges"].append(
        {
            "challenge_text": challenge_text,
            "challenger": challenger,
            "evidence_refs": evidence_refs or [],
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )

    # Save updated ledger
    ledger["ledger"]["last_updated"] = datetime.now(UTC).isoformat()
    _save_ledger(ledger_id, ledger)

    return {
        "status": "challenged",
        "claim_id": claim_id,
        "challenge_count": len(claim["challenges"]),
    }


def seal_claim(
    ledger_id: str,
    claim_id: str,
    seal_id: str,
    sovereign: str = "ARIF",
) -> dict[str, Any]:
    """
    Seal a claim to VAULT999 (irreversible).

    Returns:
        dict with claim_id, status, seal_id
    """
    ledger = _load_ledger(ledger_id)
    if not ledger:
        return {"status": "error", "reason": f"Ledger {ledger_id} not found"}

    claim = next((c for c in ledger["claims"] if c["claim_id"] == claim_id), None)
    if not claim:
        return {"status": "error", "reason": f"Claim {claim_id} not found"}

    # Only validated claims can be sealed
    if claim["status"] not in ["validated", "challenged"]:
        return {
            "status": "error",
            "reason": f"Claim {claim_id} must be validated or challenged before sealing (current: {claim['status']})",
        }

    # Seal the claim
    claim["status"] = "sealed"
    claim["sealed_at"] = datetime.now(UTC).isoformat()
    claim["seal_id"] = seal_id

    # Save updated ledger
    ledger["ledger"]["last_updated"] = datetime.now(UTC).isoformat()
    _save_ledger(ledger_id, ledger)

    return {
        "status": "sealed",
        "claim_id": claim_id,
        "seal_id": seal_id,
        "sovereign": sovereign,
    }


def query_claims(
    ledger_id: str | None = None,
    domain: str | None = None,
    status: str | None = None,
    classification: str | None = None,
    min_confidence: float | None = None,
    max_confidence: float | None = None,
) -> dict[str, Any]:
    """
    Query claims across ledgers.

    Returns:
        dict with claims list and count
    """
    _ensure_ledger_root()
    results = []

    # Determine which ledgers to search
    if ledger_id:
        ledger = _load_ledger(ledger_id)
        ledgers = [ledger] if ledger else []
    else:
        ledgers = []
        for path in LEDGER_ROOT.glob("*.json"):
            try:
                ledgers.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue

    for ledger in ledgers:
        for claim in ledger.get("claims", []):
            # Apply filters
            if domain and claim.get("domain") != domain:
                continue
            if status and claim.get("status") != status:
                continue
            if classification and claim.get("classification") != classification:
                continue
            if min_confidence and claim.get("confidence", 0) < min_confidence:
                continue
            if max_confidence and claim.get("confidence", 1) > max_confidence:
                continue

            results.append(
                {
                    "ledger_id": ledger["ledger"]["id"],
                    "claim_id": claim["claim_id"],
                    "claim_text": claim["claim_text"],
                    "classification": claim["classification"],
                    "confidence": claim["confidence"],
                    "status": claim["status"],
                    "domain": claim.get("domain", "federation"),
                    "counterargument": claim.get("counterargument", ""),
                }
            )

    return {
        "claims": results,
        "count": len(results),
    }


def run_claim_ledger(
    mode: str,
    ledger_id: str | None = None,
    claim_id: str | None = None,
    claim_text: str | None = None,
    classification: str | None = None,
    confidence: float | None = None,
    counterargument: str | None = None,
    source_documents: list[dict[str, Any]] | None = None,
    formula: str | None = None,
    falsification_conditions: list[str] | None = None,
    domain: str | None = None,
    evidence_refs: list[str] | None = None,
    linked_claims: list[str] | None = None,
    challenge_text: str | None = None,
    challenger: str | None = None,
    seal_id: str | None = None,
    sovereign: str | None = None,
    source_article: str | None = None,
    verification_principle: str | None = None,
    verifier: str | None = None,
    min_confidence: float | None = None,
    max_confidence: float | None = None,
    status_filter: str | None = None,
) -> dict[str, Any]:
    """
    Main entry point for claim ledger operations.

    Modes:
      create   — Create a new claim ledger
      add      — Add a claim to a ledger
      validate — Validate a claim against sources
      challenge — Challenge a claim with counter-evidence
      seal     — Seal a claim to VAULT999 (irreversible)
      attach   — Attach evidence to an existing claim
      query    — Query claims by domain, status, classification
    """
    if mode == "create":
        if not ledger_id:
            return {"status": "error", "reason": "ledger_id required for create mode"}
        return create_ledger(
            ledger_id=ledger_id,
            source_article=source_article or "",
            verification_principle=verification_principle
            or "3 clicks to formula + counterargument",
            sovereign=sovereign or "ARIF",
        )

    elif mode == "add":
        if (
            not ledger_id
            or not claim_id
            or not claim_text
            or not classification
            or not counterargument
        ):
            return {
                "status": "error",
                "reason": "ledger_id, claim_id, claim_text, classification, and counterargument required for add mode",
            }
        return add_claim(
            ledger_id=ledger_id,
            claim_id=claim_id,
            claim_text=claim_text,
            classification=classification,
            confidence=confidence or 0.5,
            counterargument=counterargument,
            source_documents=source_documents,
            formula=formula or "",
            falsification_conditions=falsification_conditions,
            domain=domain or "federation",
            evidence_refs=evidence_refs,
            linked_claims=linked_claims,
        )

    elif mode == "validate":
        if not ledger_id or not claim_id:
            return {
                "status": "error",
                "reason": "ledger_id and claim_id required for validate mode",
            }
        return validate_claim(
            ledger_id=ledger_id,
            claim_id=claim_id,
            verifier=verifier or "333-AGI",
        )

    elif mode == "challenge":
        if not ledger_id or not claim_id or not challenge_text:
            return {
                "status": "error",
                "reason": "ledger_id, claim_id, and challenge_text required for challenge mode",
            }
        return challenge_claim(
            ledger_id=ledger_id,
            claim_id=claim_id,
            challenge_text=challenge_text,
            challenger=challenger or "333-AGI",
            evidence_refs=evidence_refs,
        )

    elif mode == "seal":
        if not ledger_id or not claim_id or not seal_id:
            return {
                "status": "error",
                "reason": "ledger_id, claim_id, and seal_id required for seal mode",
            }
        return seal_claim(
            ledger_id=ledger_id,
            claim_id=claim_id,
            seal_id=seal_id,
            sovereign=sovereign or "ARIF",
        )

    elif mode == "attach":
        if not ledger_id or not claim_id:
            return {"status": "error", "reason": "ledger_id and claim_id required for attach mode"}
        # Attach evidence to existing claim
        ledger = _load_ledger(ledger_id)
        if not ledger:
            return {"status": "error", "reason": f"Ledger {ledger_id} not found"}
        claim = next((c for c in ledger["claims"] if c["claim_id"] == claim_id), None)
        if not claim:
            return {"status": "error", "reason": f"Claim {claim_id} not found"}
        if evidence_refs:
            claim["evidence_refs"].extend(evidence_refs)
        if linked_claims:
            claim["linked_claims"].extend(linked_claims)
        claim["last_verified"] = datetime.now(UTC).isoformat()
        ledger["ledger"]["last_updated"] = datetime.now(UTC).isoformat()
        _save_ledger(ledger_id, ledger)
        return {
            "status": "attached",
            "claim_id": claim_id,
            "evidence_count": len(claim["evidence_refs"]),
            "linked_count": len(claim["linked_claims"]),
        }

    elif mode == "query":
        return query_claims(
            ledger_id=ledger_id,
            domain=domain,
            status=status_filter,
            classification=classification,
            min_confidence=min_confidence,
            max_confidence=max_confidence,
        )

    else:
        return {
            "status": "error",
            "reason": f"Unknown mode: {mode}. Use: create, validate, challenge, seal, attach, query",
        }
