"""
arifOS core — Explanatory-Class Gate (claim_kernel bridge)
═══════════════════════════════════════════════════════════════════════════════

THE MISSING TERM IN THE MUTATION EXPRESSION
-------------------------------------------
The kernel's own authority doctrine states:

    CanMutate = AuthorityGranted AND ScopeMatches AND TargetPermitted
                AND BoundaryActive

Confidence appears nowhere in that expression. Neither does JUSTIFICATION —
what KIND of claim is being used as the reason. That absence is what lets a
true, moving, entirely unfalsifiable sentence (NARRATIVE) sit upstream of a
write and be cited as if it were a cause.

This module supplies exactly that missing term, mechanically:

    CanMutate = ... AND JustificationClassIn(ACTION_ELIGIBLE_CLASSES)

THE LAW (claim_kernel, /root/AAA/lib/claim_kernel):
    A NARRATIVE-class claim may be true, valuable and worth reading and still
    carry zero explanatory power. It may be PUBLISHED, but it may never be the
    SOLE JUSTIFICATION for a mutation. UNCLASSIFIED fails closed.

WHAT THIS MODULE IS NOT
-----------------------
It is NOT a second taxonomy. `claim_kernel` owns the vocabulary
(MEASURED / MECHANISM / PATTERN / NARRATIVE / UNCLASSIFIED) and the checks.
This module imports it, calls it, and translates its verdict into the kernel's
error idiom (reasons list + fail-closed boolean). If claim_kernel is
unreachable this gate CLOSES (eligible=False) and says so — an unverifiable
justification is not a verified one.

WHERE IT IS WIRED
-----------------
`arifosmcp/runtime/v2_envelope.py` → `_apply_mutation_justification_gate`,
called from `build_v2_envelope`, the single point every canonical tool
response (arif_judge SEAL, arif_forge mutation, arif_seal) passes through
before its `can_mutate` flag is published. The gate can only DOWNGRADE
can_mutate — it never grants it.

Declaration paths (any one is sufficient; first found wins):
    1. response["claim_class"]            — top level
    2. response["meta"]["claim_class"]    — judge meta
    3. response["result"]["claim_class"]  — judge result
    4. response["result"]["evidence"]["claim_class"] / response["evidence"][...]
    5. session epistemic axis — `epistemic_state.record_claim_class()`

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Any

logger = logging.getLogger(__name__)

GATE_ID = "claim_class_gate/v1"

# ── claim_kernel resolution ──────────────────────────────────────────────────
# The federation ships claim_kernel as a plain package at /root/AAA/lib.
# ARIFOS_CLAIM_KERNEL_PATH overrides the search root for other hosts/images.
KERNEL_PATH_ENV = "ARIFOS_CLAIM_KERNEL_PATH"
DEFAULT_KERNEL_PATH = "/root/AAA/lib"

KERNEL_AVAILABLE = False
KERNEL_ERROR: str | None = None

# Populated from claim_kernel on successful import. Left EMPTY when the kernel
# is unreachable — deliberately not hard-coded here, because a second copy of
# the vocabulary in this file is exactly the drift the kernel warns about.
CLAIM_CLASSES: tuple[str, ...] = ()
ACTION_ELIGIBLE_CLASSES: tuple[str, ...] = ()
SCHEMA: str | None = None
UNCLASSIFIED = "UNCLASSIFIED"

_action_eligible = None


def _resolve_kernel_path() -> str:
    return os.environ.get(KERNEL_PATH_ENV) or DEFAULT_KERNEL_PATH


def _import_claim_kernel() -> None:
    """Import claim_kernel, adding its search root to sys.path if needed."""
    global KERNEL_AVAILABLE, KERNEL_ERROR
    global CLAIM_CLASSES, ACTION_ELIGIBLE_CLASSES, SCHEMA, UNCLASSIFIED, _action_eligible

    path = _resolve_kernel_path()
    try:
        if path and path not in sys.path:
            sys.path.insert(0, path)
        from claim_kernel import (  # type: ignore[import-not-found]
            ACTION_ELIGIBLE_CLASSES as _ELIGIBLE,
            CLAIM_CLASSES as _CLASSES,
            SCHEMA as _SCHEMA,
            UNCLASSIFIED as _UNCLASSIFIED,
            action_eligible as _eligible_fn,
        )

        CLAIM_CLASSES = tuple(_CLASSES)
        ACTION_ELIGIBLE_CLASSES = tuple(_ELIGIBLE)
        SCHEMA = str(_SCHEMA)
        UNCLASSIFIED = str(_UNCLASSIFIED)
        _action_eligible = _eligible_fn
        KERNEL_AVAILABLE = True
        KERNEL_ERROR = None
    except Exception as exc:  # pragma: no cover - depends on host layout
        KERNEL_AVAILABLE = False
        KERNEL_ERROR = f"{type(exc).__name__}: {exc}"
        logger.warning(
            "claim_class_gate: claim_kernel unreachable at %r (%s) — gate FAILS CLOSED",
            path,
            KERNEL_ERROR,
        )


_import_claim_kernel()


# ── Helpers ──────────────────────────────────────────────────────────────────


def available() -> bool:
    """True when claim_kernel is importable and authoritative right now."""
    return KERNEL_AVAILABLE and _action_eligible is not None


def kernel_status() -> dict[str, Any]:
    """Probe receipt for the kernel binding — safe to surface in any response."""
    return {
        "gate": GATE_ID,
        "kernel_available": available(),
        "kernel_error": KERNEL_ERROR,
        "kernel_path": _resolve_kernel_path(),
        "schema": SCHEMA,
        "claim_classes": list(CLAIM_CLASSES),
        "action_eligible_classes": list(ACTION_ELIGIBLE_CLASSES),
    }


def normalise_class(declared: Any) -> str:
    """Upper/strip a declared class. Membership is decided by claim_kernel."""
    if declared is None:
        return UNCLASSIFIED
    text = str(declared).upper().strip()
    return text or UNCLASSIFIED


def _deny(reasons: list[str], declared: str, **extra: Any) -> dict[str, Any]:
    """Fail-closed verdict shape. Never raises."""
    out: dict[str, Any] = {
        "gate": GATE_ID,
        "kernel_available": available(),
        "kernel_error": KERNEL_ERROR,
        "schema": SCHEMA,
        "declared": declared,
        "class": declared,
        "eligible": False,
        "allowed_for_mutation": False,
        "reasons": reasons,
        "class_verdict": None,
        "baseline_verdict": None,
    }
    out.update(extra)
    return out


def evaluate(
    claim_text: str | None,
    declared_class: str | None = None,
    *,
    evidence: dict[str, Any] | None = None,
    session_id: str | None = None,
    source: str | None = None,
    record: bool = True,
) -> dict[str, Any]:
    """Evaluate whether a claim may justify a mutation. NEVER raises.

    Returns a dict carrying the full claim_kernel verdict. `allowed_for_mutation`
    is the mutation-authorisation term; it is False whenever:
      * claim_kernel is unreachable (fail-closed), or
      * the class is undeclared / unrecognised (UNCLASSIFIED), or
      * the declared class is not in ACTION_ELIGIBLE_CLASSES, or
      * claim_kernel's own reasons are non-empty (baseline missing, lint disagrees).

    Side effect (when record=True and session_id given): records axis 2 into the
    session epistemic state alongside reality_class.
    """
    declared = normalise_class(declared_class)
    # Snapshot of the caller's declaration before the NK gate may reassign it —
    # the vocabulary-coercion check below must judge what the CALLER sent.
    declared_input = declared

    if not available():
        out = _deny(
            [
                "CLAIM_CLASS_GATE_UNAVAILABLE: claim_kernel unreachable — "
                f"justification class unverifiable ({KERNEL_ERROR or 'import failed'}). "
                "Fail-closed: an unverified justification may not authorise a mutation."
            ],
            declared,
        )
        if record and session_id:
            _record(session_id, declared, claim_text, source)
        return out

    try:
        result = _action_eligible(str(claim_text or ""), declared)  # type: ignore[misc]
        reasons = list(result.get("reasons", []) or [])
        eligible = bool(result.get("eligible", False))
        # NEGATIVE_KNOWLEDGE Gate (Computational VOID_t)
        try:
            from arifosmcp.core.negative_knowledge_gate import evaluate_negative_knowledge
            nk_res = evaluate_negative_knowledge(claim_text, declared, evidence=evidence)
            if not nk_res["passed"]:
                reasons.extend(nk_res["reasons"])
                eligible = False
                declared = nk_res["downgraded_class"]
        except Exception:
            pass

        # ── B2 · vocabulary coercion must be EXPLICIT (2026-09-22) ──────────
        # claim_kernel's classify() silently normalises any class outside
        # claim_kernel/v1 to UNCLASSIFIED. If this receipt echoes the raw input
        # in `class` while its own `reasons` quote the kernel's coerced class,
        # ONE receipt carries two truths (observed e-a26871f2, 2026-09-20:
        # class=OBSERVATION beside "class=UNCLASSIFIED is not action-eligible").
        # The kernel's class wins — the coercion is stated, never smoothed.
        if declared_input not in CLAIM_CLASSES:
            _kernel_class = (result.get("class_verdict") or {}).get(
                "declared"
            ) or UNCLASSIFIED
            reasons.insert(
                0,
                f"DECLARED_CLASS_OUT_OF_VOCABULARY: {declared_input!r} is not in "
                f"claim_kernel/v1 {list(CLAIM_CLASSES)} — classified as "
                f"{_kernel_class} (fail-closed).",
            )
            resolved_class = _kernel_class
        else:
            # In-vocabulary: legacy semantics preserved — post-NK declared.
            resolved_class = declared

        out = {
            "gate": GATE_ID,
            "kernel_available": True,
            "kernel_error": None,
            "schema": result.get("schema", SCHEMA),
            "declared": declared,
            "class": resolved_class,
            "inferred": (result.get("class_verdict") or {}).get("inferred"),
            "agree": (result.get("class_verdict") or {}).get("agree"),
            "has_baseline": (result.get("baseline_verdict") or {}).get("has_baseline"),
            "eligible": eligible,
            "allowed_for_mutation": eligible,
            "reasons": reasons,
            "class_verdict": result.get("class_verdict"),
            "baseline_verdict": result.get("baseline_verdict"),
            "source": source,
        }
        if "nk_res" in locals() and not nk_res.get("passed"):
            out["void_entry"] = nk_res.get("void_entry")
        if record and session_id:
            _record(session_id, out.get("class") or declared, claim_text, source)
        return out
    except Exception as exc:  # claim_kernel internal error → fail closed
        logger.warning("claim_class_gate: contribution check raised: %s", exc)
        out = _deny(
            [f"CLAIM_CLASS_GATE_ERROR: {type(exc).__name__}: {exc}. Fail-closed."],
            declared,
        )
        if record and session_id:
            _record(session_id, declared, claim_text, source)
        return out


def _record(
    session_id: str, declared: str, claim_text: str | None, source: str | None
) -> None:
    """Best-effort write of axis 2 into the session epistemic record."""
    try:
        from arifosmcp.core.epistemic_state import record_claim_class

        record_claim_class(session_id, declared, claim_text=claim_text, source=source)
    except Exception as exc:  # never let the witness break the caller
        logger.debug("claim_class_gate: epistemic record skipped: %s", exc)


def gate_mutation(
    claim_text: str | None,
    declared_class: str | None = None,
    *,
    session_id: str | None = None,
    source: str | None = None,
) -> dict[str, Any]:
    """Thin alias of `evaluate` — named for the mutation-authorisation use site."""
    return evaluate(claim_text, declared_class, session_id=session_id, source=source)
