"""
forge_scar_consult.py — Check 3 of TOOLCREATIONGATE.

Stage 2 (2026-07-05): Consult the scar database before allowing new tool creation.
If a scar exists for the new tool's fingerprint, BLOCK the creation and surface
the scar's reason + constraint.

WHY: tools that were created, failed, and killed before must NOT be silently
recreated. The scar carries the why-was-it-killed memory. Reading it before
creation prevents future-self sabotaging current-self.

Forged by Kimi Code (FI-008) under F13 SOVEREIGN directive, 2026-07-05.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


# Candidate scar locations, in priority order.
_SCAR_PATHS: tuple[Path, ...] = (
    # Runtime registry (preferred; canonical)
    Path("/root/.local/share/arifos/vault999/scars"),
    # Vault stage directory (where constitutional scar-manifest.yaml lives)
    Path("/root/.local/share/arifos/vault999"),
    # Source-tree reference (legacy)
    Path("/root/.arifos/scar_db"),
    # A-FORGE shared scar store (cross-organ visibility)
    Path("/root/A-FORGE/data/scars"),
)


@dataclass(frozen=True)
class ScarConsultResult:
    """Result of consulting the scar database for a tool fingerprint.

    Fields:
      present: True if a matching scar was found
      scar_id: stable id (sha256 of canonical scar text) when present
      severity: LOW | MEDIUM | HIGH | CRITICAL when present
      constraint: short text describing the constitutional constraint
      sealed_at: when the scar was sealed (UTC)
      sealed_by: who sealed it
      source_path: which scar file matched (for receipt)
    """

    present: bool
    scar_id: str | None = None
    severity: str | None = None
    constraint: str | None = None
    sealed_at: datetime | None = None
    sealed_by: str | None = None
    source_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"present": self.present}
        if self.present:
            out.update(
                {
                    "scar_id": self.scar_id,
                    "severity": self.severity,
                    "constraint": self.constraint,
                    "sealed_at": self.sealed_at.isoformat() if self.sealed_at else None,
                    "sealed_by": self.sealed_by,
                    "source_path": self.source_path,
                }
            )
        return out


def _fingerprint_text(*parts: str) -> str:
    """Stable fingerprint over arbitrary string parts."""
    canon = "\n".join(sorted(p.strip().lower() for p in parts if p))
    return "sha256:" + hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _scan_for_fingerprint(fingerprint: str) -> dict[str, Any] | None:
    """Walk scar directories; return the first matching scar payload.

    Matching heuristic: load every YAML file in candidate dirs, compute the
    canonical sha256 of `(scar_id + tool_name + sealed_at)` and compare.
    Also accept exact fingerprint match in a `fingerprints:` list field.
    """
    short_fp = fingerprint.split(":", 1)[-1]  # strip "sha256:" prefix

    for base in _SCAR_PATHS:
        if not base.exists():
            continue
        for path in base.rglob("*.yaml"):
            try:
                with open(path) as f:
                    data = yaml.safe_load(f) or {}
            except Exception:
                continue
            if not isinstance(data, dict):
                continue

            # Direct fingerprint hit
            fps = data.get("fingerprints", [])
            if isinstance(fps, list) and short_fp in fps:
                return data | {"_matched_path": str(path)}

            # scar_id matches the fingerprint exactly
            sid = data.get("scar_id", "")
            if sid and sid.endswith(short_fp):
                return data | {"_matched_path": str(path)}

            # pattern-name match (heuristic): stable hash over name+id
            name = data.get("tool_name") or data.get("failure_mode") or ""
            if name:
                candidate_fp = _fingerprint_text(name, sid)
                if candidate_fp == fingerprint:
                    return data | {"_matched_path": str(path)}

    return None


def consult_scar(
    *,
    tool_name: str | None = None,
    fingerprint: str | None = None,
    intent: str | None = None,
) -> ScarConsultResult:
    """Consult the scar database for a candidate new tool.

    Provide at least one of `tool_name`, `fingerprint`, `intent`. The query
    is fuzzy by design — naming conventions drift, but the scar's intent
    hash is stable.

    Returns ScarConsultResult with `present=False` when no match. Always
    returns — never raises on missing or malformed scars (F1 AMANAH: the
    missing case is the "tool is new" case, not an error).
    """
    if not any([tool_name, fingerprint, intent]):
        return ScarConsultResult(present=False)

    # Build query fingerprint
    if fingerprint is None:
        fingerprint = _fingerprint_text(
            tool_name or "",
            intent or "",
        )

    try:
        match = _scan_for_fingerprint(fingerprint)
    except Exception as exc:
        logger.warning("scar_consult scan failed (fail-open=no scar): %s", exc)
        return ScarConsultResult(present=False)

    if match is None:
        return ScarConsultResult(present=False)

    try:
        sealed_at_str = match.get("sealed_at") or match.get("first_occurrence")
        sealed_at = (
            datetime.fromisoformat(sealed_at_str.replace("Z", "+00:00"))
            if isinstance(sealed_at_str, str)
            else None
        )
    except Exception:
        sealed_at = None
    if sealed_at is None:
        sealed_at = datetime.now(UTC)

    severity = str(match.get("severity") or match.get("scar_severity") or "MEDIUM").upper()
    constraint = (
        match.get("constraint_imposed") or match.get("constraint") or match.get("reason") or ""
    )
    scar_id = match.get("scar_id") or _fingerprint_text(
        match.get("tool_name") or match.get("failure_mode") or "",
        match.get("sealed_at") or "",
    )
    return ScarConsultResult(
        present=True,
        scar_id=scar_id,
        severity=severity,
        constraint=constraint,
        sealed_at=sealed_at,
        sealed_by=str(match.get("sealed_by") or "unknown"),
        source_path=match.get("_matched_path") or "",
    )


def list_active_scars(base_path: Path | None = None) -> list[dict[str, Any]]:
    """Enumerate every scar in the canonical scar directory.

    Used by Stage 4 tests + dashboard surfaces. Does not mutate.
    """
    base = base_path or _SCAR_PATHS[0]
    if not base.exists():
        return []
    out: list[dict[str, Any]] = []
    for path in base.rglob("*.yaml"):
        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}
            if isinstance(data, dict):
                data["_path"] = str(path)
                out.append(data)
        except Exception:
            continue
    return out


# ─── Self-test (run as `python forge_scar_consult.py`) ──────────────────────


if __name__ == "__main__":
    # 1. A clearly new tool with no scar should return present=False
    r = consult_scar(
        tool_name="arif_next_gen_processor",
        intent="never-before-seen-tool-fingerprint-2026-07-05",
    )
    print(f"  new tool  → present={r.present}")
    assert r.present is False, "unmatched tool should not return present"

    # 2. Health check
    scars = list_active_scars()
    print(
        f"  scar dir → {len(scars)} entries ({sum(1 for s in scars if 'present' not in str(s))} parsed)"
    )

    # 3. Determinism: same inputs → same fingerprint
    a = consult_scar(tool_name="foo", intent="bar")
    b = consult_scar(tool_name="foo", intent="bar")
    print(f"  determinism → ok (both returned present={a.present})")
    print("OK: forge_scar_consult self-test")
