"""
Active Source-of-Truth (SOT) loader — Seal-A R2.

Loads the sealed apex-sot-v2 artifact, verifies its SHA-256 against the
companion .SHA256 file, and exposes the active SOT hash for kernel /health
and SE stage engine proof bundles.

Local file ≠ operational law until this module reports active=True with a
matching hash. Supersession of v1 is recorded via ``seal_sot_supersession``
(append-only receipt file + optional VAULT999 path).

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Candidate paths (first hit with matching hash wins).
_SOT_CANDIDATES: tuple[Path, ...] = (
    Path("/root/A-FORGE/forge_work/2026-07-17/APEX-CONCORDANCE-17072026/apex-sot-v2.json"),
    Path("/opt/arifos/sot/apex-sot-v2.json"),
    Path(os.environ.get("ARIFOS_SOT_V2_PATH", "")),
)

_SUPERSESSION_RECEIPT = Path(
    "/root/A-FORGE/forge_work/2026-07-17/APEX-CONCORDANCE-17072026/SOT-V2-SUPERSESSION-RECEIPT.json"
)
_SUPERSESSION_FALLBACK = Path("/tmp/arifos_sot_v2_supersession.json")

ACTIVE_SOT_ID = "apex-sot-v2"
SUPERSEDED_SOT_ID = "apex-sot-v1"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_expected_hash(json_path: Path) -> str | None:
    """Read companion .SHA256 (format: '<hex>  <filename>' or bare hex)."""
    sha_path = json_path.with_suffix(json_path.suffix + ".SHA256")
    if not sha_path.exists():
        # also try apex-sot-v2.SHA256 next to apex-sot-v2.json
        alt = json_path.parent / (json_path.stem + ".SHA256")
        sha_path = alt if alt.exists() else sha_path
    if not sha_path.exists():
        return None
    text = sha_path.read_text(encoding="utf-8").strip()
    if not text:
        return None
    # first token is the hex
    return text.split()[0].strip().lower()


def resolve_sot_path() -> Path | None:
    for p in _SOT_CANDIDATES:
        if p and str(p) and p.exists() and p.is_file():
            return p
    return None


def get_active_sot() -> dict[str, Any]:
    """Return operational SOT status for health / stage proof.

    active=True only when file exists AND sha256 matches companion digest.
    """
    path = resolve_sot_path()
    if path is None:
        return {
            "active": False,
            "sot_id": ACTIVE_SOT_ID,
            "sot_hash": "",
            "path": None,
            "hold_reason": "sot_v2_artifact_missing",
            "supersedes": SUPERSEDED_SOT_ID,
            "operational": False,
        }

    actual = _sha256_file(path)
    expected = _read_expected_hash(path)
    if expected is None:
        return {
            "active": False,
            "sot_id": ACTIVE_SOT_ID,
            "sot_hash": f"sha256:{actual}",
            "path": str(path),
            "hold_reason": "sot_v2_sha256_companion_missing",
            "supersedes": SUPERSEDED_SOT_ID,
            "operational": False,
        }
    if actual.lower() != expected.lower():
        return {
            "active": False,
            "sot_id": ACTIVE_SOT_ID,
            "sot_hash": f"sha256:{actual}",
            "expected_hash": f"sha256:{expected}",
            "path": str(path),
            "hold_reason": "sot_v2_hash_mismatch",
            "supersedes": SUPERSEDED_SOT_ID,
            "operational": False,
        }

    # Load metadata (best-effort)
    meta: dict[str, Any] = {}
    try:
        meta = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        meta = {}

    supersession = _load_supersession_receipt()
    return {
        "active": True,
        "sot_id": meta.get("sot_id") or ACTIVE_SOT_ID,
        "sot_hash": f"sha256:{actual}",
        "path": str(path),
        "hold_reason": "",
        "supersedes": meta.get("supersedes") or SUPERSEDED_SOT_ID,
        "forged_at": meta.get("forged_at"),
        "operational": True,
        "supersession_sealed": bool(supersession.get("sealed")),
        "supersession_receipt": supersession.get("path"),
        "kernel_reported": True,
    }


def _load_supersession_receipt() -> dict[str, Any]:
    for p in (_SUPERSESSION_RECEIPT, _SUPERSESSION_FALLBACK):
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                data["path"] = str(p)
                return data
            except (OSError, json.JSONDecodeError):
                continue
    return {"sealed": False}


def seal_sot_supersession(
    *,
    actor: str = "ARIF",
    reason: str = "R2 SOT v2 operational — supersede apex-sot-v1",
) -> dict[str, Any]:
    """Write supersession receipt. Append-only style: refuse rewrite if sealed.

    Also attempts VAULT999 append via vault bridge when available.
    """
    sot = get_active_sot()
    if not sot.get("active"):
        return {
            "verdict": "HOLD",
            "sealed": False,
            "reason": sot.get("hold_reason") or "sot_not_active",
            "sot": sot,
        }

    existing = _load_supersession_receipt()
    if existing.get("sealed") and existing.get("sot_hash") == sot.get("sot_hash"):
        return {
            "verdict": "SEAL",
            "sealed": True,
            "idempotent": True,
            "receipt": existing,
        }

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    receipt = {
        "type": "SOT_SUPERSESSION",
        "sealed": True,
        "sealed_at": now,
        "actor": actor,
        "reason": reason,
        "from_sot": SUPERSEDED_SOT_ID,
        "to_sot": sot["sot_id"],
        "sot_hash": sot["sot_hash"],
        "sot_path": sot.get("path"),
        "doctrine": "DITEMPA BUKAN DIBERI",
        "seal_a_gate": "R2",
    }

    # Prefer forge_work path; fall back to /tmp
    written_to: str | None = None
    for p in (_SUPERSESSION_RECEIPT, _SUPERSESSION_FALLBACK):
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
            written_to = str(p)
            break
        except OSError as exc:
            logger.warning("sot_active: cannot write supersession to %s: %s", p, exc)

    if not written_to:
        return {
            "verdict": "HOLD",
            "sealed": False,
            "reason": "supersession_receipt_write_failed",
            "sot": sot,
        }

    receipt["path"] = written_to

    # Best-effort VAULT999 append (never fail the seal if vault is down)
    vault_ref = None
    try:
        from arifosmcp.runtime.vault_bridge import append_outcome  # type: ignore

        vault_ref = append_outcome(
            {
                "kind": "SOT_SUPERSESSION",
                "actor": actor,
                "sot_id": sot["sot_id"],
                "sot_hash": sot["sot_hash"],
                "from_sot": SUPERSEDED_SOT_ID,
                "sealed_at": now,
                "seal_a_gate": "R2",
            }
        )
    except Exception:
        try:
            # Fallback: append JSONL to local vault outcomes if present
            vault_path = Path("/root/.local/share/arifos/vault999/outcomes.jsonl")
            if vault_path.parent.exists():
                entry = {
                    "ts": now,
                    "kind": "SOT_SUPERSESSION",
                    "actor": actor,
                    "sot_hash": sot["sot_hash"],
                    "sot_id": sot["sot_id"],
                    "from_sot": SUPERSEDED_SOT_ID,
                    "seal_a_gate": "R2",
                }
                with vault_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(entry, sort_keys=True) + "\n")
                vault_ref = f"file://{vault_path}#SOT_SUPERSESSION"
        except OSError as exc:
            logger.warning("sot_active: vault append skipped: %s", exc)

    receipt["vault_ref"] = vault_ref
    # rewrite with vault_ref
    try:
        Path(written_to).write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
    except OSError:
        pass

    return {
        "verdict": "SEAL",
        "sealed": True,
        "idempotent": False,
        "receipt": receipt,
        "sot": sot,
    }


__all__ = [
    "ACTIVE_SOT_ID",
    "SUPERSEDED_SOT_ID",
    "get_active_sot",
    "resolve_sot_path",
    "seal_sot_supersession",
]
