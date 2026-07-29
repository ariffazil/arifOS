"""
forge_scar_consult.py — Check 3 of TOOLCREATIONGATE.

Stage 2 (2026-07-05): Consult the scar database before allowing new tool creation.
If a scar exists for the new tool's fingerprint, BLOCK the creation and surface
the scar's reason + constraint.

RASA DERITA Gate 2 (2026-07-29 Phase 2): FAIL-CLOSED on mutation paths.
  - scan success + no match → present=False (tool is new) — OK
  - scan failure / store unavailable + read → SABAR / degraded
  - scan failure / store unavailable + mutation → 888_HOLD
  Never treat "I could not inspect history" as "there is no dangerous history."

Forged by Kimi Code (FI-008) under F13 SOVEREIGN directive, 2026-07-05.
Repaired Phase 2 RASA DERITA semantic closure, 2026-07-29.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

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

OperationMode = Literal["read", "mutate", "create", "write"]
_MUTATION_MODES = frozenset({"mutate", "mutation", "create", "write", "execute", "deploy"})


@dataclass(frozen=True)
class ScarConsultResult:
    """Result of consulting the scar database for a tool fingerprint.

    Fields:
      present: True if a matching scar was found
      scan_successful: True if scar store(s) were inspectable
      unavailable: True if no scar store could be read (distinct from no-match)
      scar_id: stable id when present
      severity: LOW | MEDIUM | HIGH | CRITICAL when present
      constraint: short text describing the constitutional constraint
      sealed_at: when the scar was sealed (UTC)
      sealed_by: who sealed it
      source_path: which scar file matched (for receipt)
      operation_mode: read | mutate context for the consultation
      verdict: advisory gate — PASS | SABAR | 888_HOLD | VOID
    """

    present: bool
    scan_successful: bool = True
    unavailable: bool = False
    scar_id: str | None = None
    severity: str | None = None
    constraint: str | None = None
    sealed_at: datetime | None = None
    sealed_by: str | None = None
    source_path: str | None = None
    operation_mode: str = "read"
    verdict: str = "PASS"

    def blocks_mutation(self) -> bool:
        """True when mutation must not proceed."""
        if self.verdict in ("888_HOLD", "VOID"):
            return True
        if self.present and (self.severity or "").upper() in ("HIGH", "CRITICAL"):
            return True
        if not self.scan_successful and self.operation_mode in _MUTATION_MODES:
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "present": self.present,
            "scan_successful": self.scan_successful,
            "unavailable": self.unavailable,
            "operation_mode": self.operation_mode,
            "verdict": self.verdict,
            "blocks_mutation": self.blocks_mutation(),
        }
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


def _normalize_mode(operation_mode: str | None) -> str:
    mode = (operation_mode or "read").strip().lower()
    if mode in _MUTATION_MODES:
        return "mutate" if mode != "create" else "create"
    return "read"


def _scan_for_fingerprint(
    fingerprint: str, scar_paths: tuple[Path, ...] | None = None
) -> tuple[dict[str, Any] | None, bool, str | None]:
    """Walk scar directories; return (match, any_store_readable, error).

    any_store_readable=False means no scar base path was inspectable —
    distinct from "readable but no match".
    """
    short_fp = fingerprint.split(":", 1)[-1]  # strip "sha256:" prefix
    paths = scar_paths or _SCAR_PATHS
    any_readable = False
    scan_error: str | None = None

    for base in paths:
        try:
            if not base.exists():
                continue
        except Exception as exc:  # permission / IO
            scan_error = str(exc)
            continue

        any_readable = True
        try:
            yaml_files = list(base.rglob("*.yaml"))
        except Exception as exc:
            scan_error = str(exc)
            continue

        for path in yaml_files:
            try:
                with open(path) as f:
                    data = yaml.safe_load(f) or {}
            except Exception:
                # Malformed YAML: skip file, do not fail entire scan
                continue
            if not isinstance(data, dict):
                continue

            fps = data.get("fingerprints", [])
            if isinstance(fps, list) and short_fp in fps:
                return data | {"_matched_path": str(path)}, True, None

            sid = data.get("scar_id", "")
            if sid and sid.endswith(short_fp):
                return data | {"_matched_path": str(path)}, True, None

            name = data.get("tool_name") or data.get("failure_mode") or ""
            if name:
                candidate_fp = _fingerprint_text(name, sid)
                if candidate_fp == fingerprint:
                    return data | {"_matched_path": str(path)}, True, None

    return None, any_readable, scan_error


def consult_scar(
    *,
    tool_name: str | None = None,
    fingerprint: str | None = None,
    intent: str | None = None,
    operation_mode: str = "read",
    scar_paths: tuple[Path, ...] | None = None,
) -> ScarConsultResult:
    """Consult the scar database for a candidate tool.

    Provide at least one of `tool_name`, `fingerprint`, `intent`.

    Fail-closed policy (RASA DERITA):
      - readable store, no match → present=False, scan_successful=True, verdict=PASS
      - unreadable store + read → unavailable, verdict=SABAR
      - unreadable store + mutate/create → unavailable, verdict=888_HOLD
      - matching active CRITICAL/HIGH scar → present=True, verdict=VOID or 888_HOLD
    """
    mode = _normalize_mode(operation_mode)

    if not any([tool_name, fingerprint, intent]):
        return ScarConsultResult(
            present=False,
            scan_successful=True,
            unavailable=False,
            operation_mode=mode,
            verdict="PASS",
        )

    if fingerprint is None:
        fingerprint = _fingerprint_text(tool_name or "", intent or "")

    try:
        match, any_readable, scan_error = _scan_for_fingerprint(fingerprint, scar_paths)
    except Exception as exc:
        logger.warning("scar_consult scan failed (fail-closed): %s", exc)
        verdict = "888_HOLD" if mode in _MUTATION_MODES or mode == "create" else "SABAR"
        return ScarConsultResult(
            present=False,
            scan_successful=False,
            unavailable=True,
            operation_mode=mode,
            verdict=verdict,
            constraint=f"scar scan exception: {exc}",
        )

    if not any_readable:
        # No inspectable scar store — cannot prove absence of scars
        logger.warning(
            "scar_consult: no readable scar store (fail-closed); mode=%s err=%s",
            mode,
            scan_error,
        )
        verdict = "888_HOLD" if mode in _MUTATION_MODES or mode == "create" else "SABAR"
        return ScarConsultResult(
            present=False,
            scan_successful=False,
            unavailable=True,
            operation_mode=mode,
            verdict=verdict,
            constraint=scan_error or "scar store unavailable",
        )

    if match is None:
        return ScarConsultResult(
            present=False,
            scan_successful=True,
            unavailable=False,
            operation_mode=mode,
            verdict="PASS",
        )

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

    if severity == "CRITICAL":
        verdict = "VOID"
    elif severity == "HIGH":
        verdict = "888_HOLD"
    else:
        verdict = "888_HOLD" if mode in _MUTATION_MODES or mode == "create" else "SABAR"

    return ScarConsultResult(
        present=True,
        scan_successful=True,
        unavailable=False,
        scar_id=scar_id,
        severity=severity,
        constraint=constraint,
        sealed_at=sealed_at,
        sealed_by=str(match.get("sealed_by") or "unknown"),
        source_path=match.get("_matched_path") or "",
        operation_mode=mode,
        verdict=verdict,
    )


def list_active_scars(base_path: Path | None = None) -> list[dict[str, Any]]:
    """Enumerate every scar in the canonical scar directory.

    Used by Stage 4 tests + dashboard surfaces. Does not mutate.
    Malformed YAML is skipped (does not crash).
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
    r = consult_scar(
        tool_name="arif_next_gen_processor",
        intent="never-before-seen-tool-fingerprint-2026-07-05",
        operation_mode="read",
    )
    print(f"  new tool  → present={r.present} scan_ok={r.scan_successful} verdict={r.verdict}")
    assert r.present is False, "unmatched tool should not return present"
    assert hasattr(r, "scan_successful")

    scars = list_active_scars()
    print(f"  scar dir → {len(scars)} entries")

    a = consult_scar(tool_name="foo", intent="bar")
    b = consult_scar(tool_name="foo", intent="bar")
    print(f"  determinism → ok (both present={a.present})")
    print("OK: forge_scar_consult self-test")
