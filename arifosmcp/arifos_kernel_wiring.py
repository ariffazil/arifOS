"""
arifOS OPA Kernel Wiring — Bridge OPA policy into arif_kernel_route.

This is the F8 LAW enforcement layer. Every tool call routed through
arif_kernel_route() will be evaluated against the OPA tool_policy before
the dispatch happens.

Constitutional binding:
- F8 LAW: Tool dispatch is gated by OPA
- F11 AUDIT: Every eval is traced
- F13 SOVEREIGN: arifOS always has override (True)
"""

from __future__ import annotations

import os

from .arifos_policy import OPABridge, PolicyInput, PolicyVerdict
from .abi.kernel_abi import evaluate_governance

# OPA endpoint per ADR-001 (localhost)
OPA_DEFAULT = os.environ.get("ARIFOS_OPA_ENDPOINT", "http://127.0.0.1:8181")
OPA_POLICY_DEFAULT = os.environ.get("ARIFOS_OPA_POLICY", "arifos/tool")


async def evaluate_tool_dispatch(
    actor_id: str,
    action_class: str,
    tool: str,
    session_id: str | None = None,
    resource: str | None = None,
    opa_endpoint: str | None = None,
    policy_path: str | None = None,
) -> PolicyVerdict:
    """
    Evaluate governance + OPA policy for a tool dispatch decision.

    Flow:
    1. Governance pre-filter (kernel_abi.evaluate_governance) — BLOCKED/HOLD/APPROVED
    2. If governance APPROVED → OPA policy evaluation

    Returns a PolicyVerdict. The caller (arif_kernel_route) decides whether
    to proceed based on `recommendation`:
    - ALLOW: dispatch
    - DENY: refuse (override is True, so sovereign can still proceed)
    - SABAR: ask for human review
    """
    # ── Governance pre-filter (runs BEFORE OPA) ──
    is_write = action_class in ("MATERIAL", "IRREVERSIBLE")
    gov_verdict = evaluate_governance(
        capability_id=tool,
        invoking_role=actor_id,
        is_write_operation=is_write,
    )

    if gov_verdict["verdict"] == "BLOCKED":
        try:
            from .abi.kernel_abi import _write_audit_event
            _write_audit_event(gov_verdict, session_id=session_id)
        except Exception:
            pass  # Audit must never crash governance
        return PolicyVerdict(
            recommendation="DENY",
            reason=gov_verdict["reason"],
            override=False,
        )
    if gov_verdict["verdict"] == "REQUIRES_HOLD":
        try:
            from .abi.kernel_abi import _write_audit_event
            _write_audit_event(gov_verdict, session_id=session_id)
        except Exception:
            pass  # Audit must never crash governance
        return PolicyVerdict(
            recommendation="SABAR",
            reason=gov_verdict["reason"],
            override=False,
        )

    # ── Governance APPROVED → proceed to OPA evaluation ──
    bridge = OPABridge(endpoint=opa_endpoint or OPA_DEFAULT)
    inp = PolicyInput(
        actor_id=actor_id,
        action_class=action_class,
        tool=tool,
        session_id=session_id,
        resource=resource,
    )
    verdict = await bridge.evaluate(policy_path or OPA_POLICY_DEFAULT, inp)
    await bridge.close()
    return verdict


def is_authorized(verdict: PolicyVerdict) -> bool:
    """Helper: True if recommendation is ALLOW or override is True."""
    return verdict.recommendation == "ALLOW" or verdict.override
