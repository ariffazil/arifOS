"""F6 P2 — consent scope (Meter 6 canonical evaluator + access/use/disclose boundary).

Implements F6 v0 Tertib Kerja #4 (Meter 6 — Consent yang sah):
  - Distinguishes permission to ACCESS data, USE data, and DISCLOSE data.
  - Enforces boundaries across delegation (child consent <= parent consent),
    expiry (`not_before`, `not_after`), and revocation (`revoked` / revocation store).
  - Never infers consent from model confidence (`ConsentSource.INFERENCE` or
    `inferred_from_confidence` is always rejected).
  - Fresh consent for an irrelevant subject/resource (`requested_subject != scope.subject`)
    never passes (`DENY_OUT_OF_SCOPE`).
  - If the consent source is missing or unverified, reports the dependency and
    remains `UNKNOWN` (never fabricated as ALLOW/PASS).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

SCHEMA = "arifos.f6.consent_scope.v1"


class ConsentSource:
    """Only legitimate sources count. Anything else = no consent exists."""

    OPERATOR_DECLARATION = "OPERATOR_DECLARATION"   # F13/operator written grant
    CONFIG_SURFACE = "CONFIG_SURFACE"               # allowlist/permit file
    INFERENCE = "INFERENCE"                         # FORBIDDEN as consent


class ConsentDecision:
    ALLOW = "ALLOW"
    DENY_NO_CONSENT = "DENY_NO_CONSENT"
    DENY_OUT_OF_SCOPE = "DENY_OUT_OF_SCOPE"
    DENY_CONSENT_STALE = "DENY_CONSENT_STALE"
    DENY_REVOKED = "DENY_REVOKED"
    DENY_DELEGATION_WIDENED = "DENY_DELEGATION_WIDENED"
    DENY_USE_NOT_GRANTED = "DENY_USE_NOT_GRANTED"   # access yes, use/disclose no
    DENY_INFERRED_CONSENT = "DENY_INFERRED_CONSENT"
    UNKNOWN = "UNKNOWN"                             # missing source — never faked


def _parse_utc(ts_str: str) -> datetime:
    dt = datetime.fromisoformat(ts_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


@dataclass
class ConsentScope:
    """A recorded consent grant from a LEGITIMATE source."""

    scope_id: str
    subject: str            # what data/system (never a human's identity score)
    source: str             # ConsentSource (INFERENCE is rejected)
    can_access: bool        # permission to read/access
    can_use: bool           # permission to use in outputs/computation
    can_disclose: bool      # permission to disclose to third parties / shared channels
    not_after: str          # ISO UTC — consent expires
    not_before: Optional[str] = None
    revoked: bool = False
    allowed_recipients: Optional[list[str]] = None
    parent_scope: Optional["ConsentScope"] = None
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _check_consent_delegation(child: ConsentScope, now: datetime) -> tuple[bool, str, str]:
    """Ensure a delegated ConsentScope never widens its parent across any axis."""
    curr = child
    depth = 0
    visited = {child.scope_id}
    while curr.parent_scope is not None:
        depth += 1
        if depth > 8:
            return False, ConsentDecision.DENY_DELEGATION_WIDENED, "consent delegation depth exceeded"
        parent = curr.parent_scope
        if parent.scope_id in visited:
            return False, ConsentDecision.DENY_DELEGATION_WIDENED, "consent delegation cycle detected"
        visited.add(parent.scope_id)

        if parent.revoked:
            return False, ConsentDecision.DENY_REVOKED, f"parent consent '{parent.scope_id}' revoked"
        if parent.source == ConsentSource.INFERENCE:
            return False, ConsentDecision.DENY_INFERRED_CONSENT, "parent consent derived from inference"
        try:
            p_na = _parse_utc(parent.not_after)
            c_na = _parse_utc(curr.not_after)
            if now > p_na:
                return False, ConsentDecision.DENY_CONSENT_STALE, f"parent consent '{parent.scope_id}' expired"
            if c_na > p_na:
                return (
                    False,
                    ConsentDecision.DENY_DELEGATION_WIDENED,
                    "delegated consent expiry extends beyond parent consent expiry",
                )
        except Exception:
            return False, ConsentDecision.UNKNOWN, "unparseable parent consent expiry"

        if curr.subject != parent.subject:
            return (
                False,
                ConsentDecision.DENY_DELEGATION_WIDENED,
                f"delegated consent subject '{curr.subject}' != parent subject '{parent.subject}'",
            )
        if curr.can_access and not parent.can_access:
            return False, ConsentDecision.DENY_DELEGATION_WIDENED, "delegated consent widened can_access"
        if curr.can_use and not parent.can_use:
            return False, ConsentDecision.DENY_DELEGATION_WIDENED, "delegated consent widened can_use"
        if curr.can_disclose and not parent.can_disclose:
            return False, ConsentDecision.DENY_DELEGATION_WIDENED, "delegated consent widened can_disclose"
        if parent.allowed_recipients is not None:
            if curr.allowed_recipients is None or not set(curr.allowed_recipients).issubset(
                set(parent.allowed_recipients)
            ):
                return (
                    False,
                    ConsentDecision.DENY_DELEGATION_WIDENED,
                    "delegated consent widened allowed_recipients",
                )
        curr = parent
    return True, ConsentDecision.ALLOW, ""


def check_consent(
    scope: Optional[ConsentScope],
    want_access: bool = False,
    want_use: bool = False,
    want_disclose: bool = False,
    now: Optional[datetime] = None,
    source_verified: bool = False,
    requested_subject: Optional[str] = None,
    requested_recipient: Optional[str] = None,
    revocation_store: Optional[Any] = None,
    model_confidence: Optional[float] = None,
) -> dict[str, Any]:
    """Evaluate a requested access/use/disclose action against CURRENT consent scope.

    Contract:
      - `model_confidence` passed without a verified legitimate `scope` (or
        `scope.source == ConsentSource.INFERENCE`) NEVER creates consent.
      - `scope is None` or `not source_verified` -> `UNKNOWN` with dependency
        reported (never fabricated as ALLOW).
      - `requested_subject` mismatch -> `DENY_OUT_OF_SCOPE` (fresh consent for
        subject A does not authorize subject B).
      - Revoked scope (or revoked ancestor) -> `DENY_REVOKED`.
      - Delegated scope widening parent -> `DENY_DELEGATION_WIDENED`.
      - Expired consent -> `DENY_CONSENT_STALE`.
      - Distinct `access`, `use`, and `disclose` checks.
    """
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    out: dict[str, Any] = {
        "schema": SCHEMA,
        "decision": ConsentDecision.UNKNOWN,
        "reason": "",
        "axes_checked": {
            "access": want_access,
            "use": want_use,
            "disclose": want_disclose,
        },
        "consent_source": scope.source if scope else None,
        "dependency_missing": False,
    }

    if scope is None:
        out["dependency_missing"] = True
        if model_confidence is not None:
            out["reason"] = (
                f"DEPENDENCY REPORTED: no consent source exists (model_confidence={model_confidence} "
                "cannot infer or substitute for consent)"
            )
        else:
            out["reason"] = (
                "DEPENDENCY REPORTED: no consent source exists — not filled with a "
                "default; inference models are never consent"
            )
        return out

    if scope.source == ConsentSource.INFERENCE:
        out["reason"] = (
            "consent from inference models is not consent; or source unverified — fail-closed"
        )
        return out

    if not source_verified:
        out["dependency_missing"] = True
        out["reason"] = (
            "consent from inference models is not consent; or source unverified — fail-closed"
        )
        return out

    # Revocation check (direct flag or external revocation store)
    if scope.revoked or (
        revocation_store is not None
        and hasattr(revocation_store, "is_revoked")
        and revocation_store.is_revoked(scope.scope_id)
    ):
        out["decision"] = ConsentDecision.DENY_REVOKED
        out["reason"] = f"consent scope '{scope.scope_id}' has been revoked"
        return out

    # Delegation narrowing check
    if scope.parent_scope is not None:
        del_ok, del_decision, del_reason = _check_consent_delegation(scope, now)
        if not del_ok:
            out["decision"] = del_decision
            out["reason"] = del_reason
            return out

    # Subject relevance check (fresh consent for subject A != consent for subject B)
    if requested_subject is not None and requested_subject != scope.subject:
        out["decision"] = ConsentDecision.DENY_OUT_OF_SCOPE
        out["reason"] = (
            f"consent subject '{scope.subject}' is irrelevant to requested subject "
            f"'{requested_subject}' — fresh irrelevant consent never passes"
        )
        return out

    # Expiry / validity window check
    try:
        if scope.not_before:
            nb = _parse_utc(scope.not_before)
            if now < nb:
                out["decision"] = ConsentDecision.DENY_CONSENT_STALE
                out["reason"] = f"consent not active until {scope.not_before}"
                return out
        na = _parse_utc(scope.not_after)
        if now > na:
            out["decision"] = ConsentDecision.DENY_CONSENT_STALE
            out["reason"] = f"consent expired {scope.not_after} — re-authorization required"
            return out
    except (ValueError, TypeError):
        out["decision"] = ConsentDecision.UNKNOWN
        out["reason"] = "consent expiry unparseable — fail-closed"
        return out

    # Distinct permission axes: access vs use vs disclose
    if want_access and not scope.can_access:
        out["decision"] = ConsentDecision.DENY_NO_CONSENT
        out["reason"] = "access requested; consent grants no access"
        return out
    if want_use and not scope.can_use:
        out["decision"] = ConsentDecision.DENY_USE_NOT_GRANTED
        out["reason"] = "permission to ACCESS data is not permission to USE it"
        return out
    if want_disclose and not scope.can_disclose:
        out["decision"] = ConsentDecision.DENY_USE_NOT_GRANTED
        out["reason"] = "permission to ACCESS data is not permission to DISCLOSE it"
        return out
    if want_disclose and scope.allowed_recipients is not None:
        if requested_recipient is None or requested_recipient not in scope.allowed_recipients:
            out["decision"] = ConsentDecision.DENY_OUT_OF_SCOPE
            out["reason"] = (
                f"recipient {requested_recipient!r} not in consent allowed_recipients "
                f"{scope.allowed_recipients}"
            )
            return out

    out["decision"] = ConsentDecision.ALLOW
    out["reason"] = "requested axes within current, verified, unexpired, unrevoked consent scope"
    return out
