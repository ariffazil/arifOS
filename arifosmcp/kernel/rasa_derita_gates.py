"""
rasa_derita_gates.py — Phase 3 enforcement helpers for RASA DERITA.

Internal kernel module. Zero new public MCP tools.

Gates:
  1. Causal cascade mandatory for L3+ / irreversible mutation
  2. Consent lease required for scoped mutate / cross-organ inference paths
  3. Schema load receipt (hash + validation_status + enforcement_mode)

Missing requirements → machine 888_HOLD (not advisory prose).

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

MODULE_ID = "RASA_DERITA"

# Modes / tiers that require causal cascade
_L3_MUTATION_MODES = frozenset(
    {
        "mutate",
        "forge",
        "write",
        "engineer",
        "generate",
        "commit",
        "deploy",
        "execute",
        "seal",
        "irreversible",
        "purge",
        "delete",
        "drop",
    }
)
_L3_TIERS = frozenset({"sovereign", "c4", "c5", "l3", "L3", "irreversible"})
_CONSENT_MODES = frozenset(
    {
        "mutate",
        "forge",
        "write",
        "engineer",
        "generate",
        "commit",
        "deploy",
        "infer",
        "profile",
        "store",
        "share",
    }
)


@dataclass(frozen=True)
class GateVerdict:
    """Machine verdict from a RASA DERITA gate."""

    passed: bool
    code: str  # PASS | 888_HOLD | VOID | SABAR
    gate: str
    reasons: tuple[str, ...] = field(default_factory=tuple)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "code": self.code,
            "gate": self.gate,
            "reasons": list(self.reasons),
            "details": dict(self.details),
            "module": MODULE_ID,
        }


def schema_load_receipt() -> dict[str, Any]:
    """Boot/health-visible receipt for the constitutional schema (no enforcement claim)."""
    try:
        from arifosmcp.schemas.constitutional import load_rasa_derita_schema

        result = load_rasa_derita_schema()
        return {
            "module_id": result.module_id,
            "schema_version": result.schema_version,
            "schema_hash": result.schema_hash,
            "loaded_at_path": result.loaded_at_path,
            "validation_status": result.validation_status,
            "enforcement_mode": "PARTIAL_CODEPATH",  # Phase 3: gates wired, not full organ SEAL
            "status": result.payload.get("status", "888_HOLD"),
            "phase": result.payload.get("phase", "PHASE3"),
            "probed_at": datetime.now(UTC).isoformat(),
        }
    except Exception as exc:
        logger.warning("rasa_derita schema load failed: %s", exc)
        return {
            "module_id": MODULE_ID,
            "validation_status": "UNAVAILABLE",
            "enforcement_mode": "NONE",
            "error": str(exc),
            "probed_at": datetime.now(UTC).isoformat(),
        }


def requires_causal_cascade(
    *,
    mode: str | None = None,
    action_tier: str | None = None,
    reversible: bool | None = None,
    blast_radius: str | None = None,
    ack_irreversible: bool = False,
) -> bool:
    """True when L3+ / irreversible mutation semantics apply."""
    m = (mode or "").strip().lower()
    tier = (action_tier or "").strip().lower()
    br = (blast_radius or "").strip().upper()
    if m in ("read", "r0", "observe", "audit_record_read", "r0_observe", "r0_observation", "query"):
        return False
    if ack_irreversible:
        return True
    if reversible is False:
        return True
    if m in _L3_MUTATION_MODES:
        return True
    if tier in {t.lower() for t in _L3_TIERS}:
        return True
    if br in {"HIGH", "CRITICAL", "FEDERATION", "EXTERNAL", "VPS"}:
        return True
    return False


def requires_consent_lease(
    *,
    mode: str | None = None,
    scopes: list[str] | None = None,
    cross_organ: bool = False,
) -> bool:
    m = (mode or "").strip().lower()
    if m in _CONSENT_MODES:
        return True
    if cross_organ:
        return True
    if scopes and any(s in {"infer", "store", "share", "profile", "actuate"} for s in scopes):
        return True
    return False


def validate_causal_cascade(cascade: Any) -> GateVerdict:
    """Enforce minimum cascade contract: ≥3 steps + recovery + reversibility + parties."""
    gate = "causal_cascade"
    if cascade is None:
        return GateVerdict(
            passed=False,
            code="888_HOLD",
            gate=gate,
            reasons=("Missing causal_cascade for L3+/irreversible mutation",),
        )
    if not isinstance(cascade, dict):
        return GateVerdict(
            passed=False,
            code="888_HOLD",
            gate=gate,
            reasons=("causal_cascade must be an object",),
        )

    reasons: list[str] = []
    steps = cascade.get("steps")
    if not isinstance(steps, list) or len(steps) < 3:
        reasons.append("causal_cascade.steps must have at least 3 entries (immediate/secondary/tertiary)")
    else:
        for i, step in enumerate(steps[:7], start=1):
            if not isinstance(step, dict):
                reasons.append(f"step[{i}] must be object")
                continue
            if not step.get("effect") and not step.get("description"):
                reasons.append(f"step[{i}] missing effect/description")
            if not step.get("affected_party") and not step.get("affected_parties"):
                reasons.append(f"step[{i}] missing affected_party")

    if not cascade.get("recovery_path") and not cascade.get("recovery"):
        reasons.append("missing recovery_path")
    if not cascade.get("reversibility"):
        reasons.append("missing reversibility estimate")
    if cascade.get("omission_consequence") in (None, ""):
        reasons.append("missing omission_consequence (what if we do nothing?)")

    if reasons:
        return GateVerdict(
            passed=False,
            code="888_HOLD",
            gate=gate,
            reasons=tuple(reasons),
            details={"step_count": len(steps) if isinstance(steps, list) else 0},
        )
    return GateVerdict(
        passed=True,
        code="PASS",
        gate=gate,
        reasons=("causal_cascade present and structurally complete",),
        details={"step_count": len(steps)},
    )


def validate_consent_lease(lease: Any, *, now: datetime | None = None) -> GateVerdict:
    """Enforce scoped, expiring, revocable consent lease."""
    gate = "consent_lease"
    if lease is None:
        return GateVerdict(
            passed=False,
            code="888_HOLD",
            gate=gate,
            reasons=("Missing consent_lease for scoped mutation/inference",),
        )
    if not isinstance(lease, dict):
        return GateVerdict(
            passed=False,
            code="888_HOLD",
            gate=gate,
            reasons=("consent_lease must be an object",),
        )

    reasons: list[str] = []
    for key in ("purpose", "scope", "expires_at", "revocable"):
        if key not in lease or lease.get(key) in (None, "", []):
            reasons.append(f"consent_lease missing {key}")

    scope = lease.get("scope")
    if scope is not None and not isinstance(scope, (list, tuple, set)):
        reasons.append("consent_lease.scope must be a list")

    # Expiry check
    expires_at = lease.get("expires_at")
    if isinstance(expires_at, str) and expires_at.strip():
        try:
            exp = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            ref = now or datetime.now(UTC)
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=UTC)
            if exp <= ref:
                reasons.append(f"consent_lease expired at {expires_at}")
        except ValueError:
            reasons.append(f"consent_lease.expires_at not ISO8601: {expires_at!r}")

    if lease.get("revoked") is True:
        reasons.append("consent_lease has been revoked")
        # Derived artifact propagation note
        prop = lease.get("revocation_propagation") or "THIS_ARTIFACT"
        reasons.append(f"revocation_propagation={prop} — derived artifacts must be constrained")

    if reasons:
        code = "888_HOLD"
        if any("expired" in r or "revoked" in r for r in reasons):
            code = "888_HOLD"
        return GateVerdict(
            passed=False,
            code=code,
            gate=gate,
            reasons=tuple(reasons),
        )
    return GateVerdict(
        passed=True,
        code="PASS",
        gate=gate,
        reasons=("consent_lease valid",),
        details={
            "purpose": lease.get("purpose"),
            "scope": list(lease.get("scope") or []),
            "expires_at": lease.get("expires_at"),
        },
    )


def extract_from_payload(payload: Any) -> dict[str, Any]:
    """Pull cascade/lease/mode fields from candidate, evidence, or manifest structures."""
    out: dict[str, Any] = {
        "causal_cascade": None,
        "consent_lease": None,
        "mode": None,
        "action_tier": None,
        "reversible": None,
        "blast_radius": None,
        "ack_irreversible": False,
        "cross_organ": False,
    }
    if payload is None:
        return out
    data: Any = payload
    if isinstance(payload, str):
        try:
            data = json.loads(payload)
        except Exception:
            return out
    if not isinstance(data, dict):
        return out

    out["causal_cascade"] = data.get("causal_cascade") or data.get("cascade")
    out["consent_lease"] = data.get("consent_lease") or data.get("lease")
    evidence = data.get("evidence")
    if isinstance(evidence, dict):
        out["causal_cascade"] = out["causal_cascade"] or evidence.get("causal_cascade")
        out["consent_lease"] = out["consent_lease"] or evidence.get("consent_lease")

    out["mode"] = data.get("mode") or data.get("action_type") or data.get("forge_mode")
    out["action_tier"] = data.get("action_tier") or data.get("tier")
    if "reversible" in data:
        out["reversible"] = bool(data.get("reversible"))
    out["blast_radius"] = data.get("blast_radius")
    out["ack_irreversible"] = bool(data.get("ack_irreversible", False))
    organs = data.get("organs") or data.get("organ_signals") or []
    if isinstance(organs, list) and len(organs) > 1:
        out["cross_organ"] = True
    if data.get("cross_organ"):
        out["cross_organ"] = True
    return out


def evaluate_mutation_gates(
    *,
    mode: str | None = None,
    action_tier: str | None = None,
    reversible: bool | None = None,
    blast_radius: str | None = None,
    ack_irreversible: bool = False,
    causal_cascade: Any = None,
    consent_lease: Any = None,
    cross_organ: bool = False,
    require_consent: bool | None = None,
) -> GateVerdict:
    """Composite gate for mutation paths. First failure wins (HOLD)."""
    reasons: list[str] = []
    details: dict[str, Any] = {"module": MODULE_ID}

    need_cascade = requires_causal_cascade(
        mode=mode,
        action_tier=action_tier,
        reversible=reversible,
        blast_radius=blast_radius,
        ack_irreversible=ack_irreversible,
    )
    need_consent = (
        require_consent
        if require_consent is not None
        else requires_consent_lease(mode=mode, cross_organ=cross_organ)
    )

    details["requires_causal_cascade"] = need_cascade
    details["requires_consent_lease"] = need_consent

    if need_cascade:
        cv = validate_causal_cascade(causal_cascade)
        details["causal_cascade"] = cv.to_dict()
        if not cv.passed:
            return GateVerdict(
                passed=False,
                code="888_HOLD",
                gate="rasa_derita_mutation",
                reasons=cv.reasons,
                details=details,
            )
        reasons.extend(cv.reasons)

    if need_consent:
        lv = validate_consent_lease(consent_lease)
        details["consent_lease"] = lv.to_dict()
        if not lv.passed:
            return GateVerdict(
                passed=False,
                code="888_HOLD",
                gate="rasa_derita_mutation",
                reasons=lv.reasons,
                details=details,
            )
        reasons.extend(lv.reasons)

    if not need_cascade and not need_consent:
        return GateVerdict(
            passed=True,
            code="PASS",
            gate="rasa_derita_mutation",
            reasons=("No L3 cascade/consent requirement for this action class",),
            details=details,
        )

    return GateVerdict(
        passed=True,
        code="PASS",
        gate="rasa_derita_mutation",
        reasons=tuple(reasons) or ("RASA DERITA mutation gates satisfied",),
        details=details,
    )


def evaluate_from_payload(
    payload: Any,
    *,
    mode: str | None = None,
    action_tier: str | None = None,
    ack_irreversible: bool = False,
    reversible: bool | None = None,
) -> GateVerdict:
    """Convenience: extract fields from candidate/manifest + evaluate."""
    fields = extract_from_payload(payload)
    return evaluate_mutation_gates(
        mode=mode or fields.get("mode"),
        action_tier=action_tier or fields.get("action_tier"),
        reversible=reversible if reversible is not None else fields.get("reversible"),
        blast_radius=fields.get("blast_radius"),
        ack_irreversible=ack_irreversible or bool(fields.get("ack_irreversible")),
        causal_cascade=fields.get("causal_cascade"),
        consent_lease=fields.get("consent_lease"),
        cross_organ=bool(fields.get("cross_organ")),
    )
