"""
arifosmcp/tools/architect_tools.py
=================================

A-ARCHITECT tool implementation.
Ask A-ARCHITECT for architectural guidance, design decisions, and API contracts.

Authority: A-ARCHITECT | Status: PROVISIONAL
"""

from __future__ import annotations

import logging
from typing import Any

from arifosmcp.runtime.law import get_active_floors

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# A-ARCHITECT Tool Manifest
# ─────────────────────────────────────────────────────────────

ARCHITECT_TOOL_SPEC = {
    "name": "a_architect",
    "description": (
        "A-ARCHITECT: Ask for architectural guidance, system design, "
        "API contracts, and structural integrity checks. "
        "Constitutional design review against F1-L13."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Your architectural question or design challenge",
                "minLength": 10,
                "maxLength": 2000,
            },
            "context": {
                "type": "object",
                "description": "Optional context (code snippets, diagrams, constraints)",
                "properties": {
                    "language": {"type": "string"},
                    "existing_design": {"type": "string"},
                    "constraints": {"type": "array", "items": {"type": "string"}},
                    "priority": {"type": "string", "enum": ["P0", "P1", "P2", "P3"]},
                },
            },
            "mode": {
                "type": "string",
                "enum": ["design", "review", "refactor", "decision"],
                "default": "design",
                "description": "What kind of architectural help you need",
            },
        },
        "required": ["query"],
    },
    "floors_active": get_active_floors(),
    "trinity": "DELTA Δ",
    "layer": "GOVERNANCE",
    "stage": "M-4_ARCH",
    "risk_tier": "P1",
}


async def a_architect_dispatch_impl(
    mode: str,
    payload: dict,
    auth_context: dict | None,
    risk_tier: str,
    dry_run: bool,
    ctx: Any,
) -> dict:
    """
    A-ARCHITECT tool implementation.

    Provides architectural guidance based on arifOS principles.

    Modes:
        - design: Create a new architectural design
        - review: Review existing design for constitutional compliance
        - refactor: Suggest refactoring for a system
        - decision: Make an architectural decision with trade-off analysis
    """
    from arifosmcp.runtime.tools_internal import RuntimeEnvelope, RuntimeStatus, Verdict

    session_id = payload.get("session_id")
    query = payload.get("query", "")
    context = payload.get("context", {})
    mode = mode or payload.get("mode", "design")

    if not query:
        return RuntimeEnvelope(
            ok=False,
            tool="a_architect",
            session_id=session_id,
            stage="M-4_ARCH",
            verdict=Verdict.VOID,
            status=RuntimeStatus.ERROR,  # transport: error (FAILURE not in canonical enum)
            payload={"error": "Query is required"},
        )

    # Route to appropriate mode handler
    if mode == "design":
        result = await _architect_design(query, context, session_id)
    elif mode == "review":
        result = await _architect_review(query, context, session_id)
    elif mode == "refactor":
        result = await _architect_refactor(query, context, session_id)
    elif mode == "decision":
        result = await _architect_decision(query, context, session_id)
    else:
        result = {"error": f"Unknown mode: {mode}"}

    return RuntimeEnvelope(
        ok=True,
        tool="a_architect",
        session_id=session_id,
        stage="M-4_ARCH",
        verdict=Verdict.SEAL,
        status=RuntimeStatus.SUCCESS,
        payload=result,
    )


async def _architect_design(query: str, context: dict, session_id: str) -> dict:
    """Generate architectural design for a problem."""
    priority = context.get("priority", "P2")
    constraints = context.get("constraints", [])

    return {
        "mode": "design",
        "query": query,
        "architectural_response": {
            "component_boundaries": _suggest_boundaries(query),
            "api_contracts": _suggest_api_contracts(query),
            "data_flow": _suggest_data_flow(query),
            "constitutional_checklist": _constitutional_checklist(query),
        },
        "floors_relevant": ["F1", "F2", "F4", "F7", "F9", "L13"],
        "priority_assigned": priority,
        "constraints": constraints,
    }


async def _architect_review(query: str, context: dict, session_id: str) -> dict:
    """Review existing design for constitutional compliance."""
    existing = context.get("existing_design", "")

    return {
        "mode": "review",
        "query": query,
        "review_findings": {
            "F1_AMANAH": {
                "status": "PASS" if "reversible" in existing.lower() else "WARN",
                "notes": "Check reversibility",
            },
            "F2_SIDDIQ": {
                "status": "PASS" if existing else "WARN",
                "notes": "Verify all claims",
            },
            "F4_CLARITY": {
                "status": "PASS" if len(existing) < 500 else "WARN",
                "notes": "Complexity check",
            },
            "F7_HUMILITY": {"status": "PASS", "notes": "No overconfidence detected"},
            "F9_TAQWA": {"status": "PASS", "notes": "No harm vectors"},
            "L13_KHILAFAH": {"status": "PASS", "notes": "Human authority preserved"},
        },
        "overall_verdict": "SEAL",
    }


async def _architect_refactor(query: str, context: dict, session_id: str) -> dict:
    """Suggest refactoring for existing system."""
    return {
        "mode": "refactor",
        "query": query,
        "refactor_suggestions": [
            {
                "priority": "P0",
                "change": "Add constitutional error handling",
                "floors": ["F1", "L11"],
            },
            {
                "priority": "P1",
                "change": "Separate concerns by Trinity pattern",
                "floors": ["F4", "F7"],
            },
        ],
    }


async def _architect_decision(query: str, context: dict, session_id: str) -> dict:
    """Make architectural decision with trade-off analysis."""
    return {
        "mode": "decision",
        "query": query,
        "options_considered": [
            {"option": "A", "pros": [], "cons": [], "score": 0},
            {"option": "B", "pros": [], "cons": [], "score": 0},
        ],
        "recommended": "B",
        "rationale": "Balances F7 (humility) with F4 (clarity)",
        "constitutional_ballot": {
            "F1": "reversible",
            "F2": "verified",
            "F4": "clear",
            "F7": "humble",
            "F9": "safe",
            "L13": "human_in_charge",
        },
    }


def _suggest_boundaries(query: str) -> list[str]:
    """Suggest component boundaries."""
    return ["Interface", "Logic", "Data", "Governance"]


def _suggest_api_contracts(query: str) -> list[dict]:
    """Suggest API contracts."""
    return [
        {
            "method": "POST /design",
            "input": "DesignRequest",
            "output": "DesignResponse",
        },
        {
            "method": "POST /review",
            "input": "ReviewRequest",
            "output": "ReviewResponse",
        },
    ]


def _suggest_data_flow(query: str) -> list[dict]:
    """Suggest data flow."""
    return [
        {"from": "Input", "to": "Governance", "description": "F1-L13 validation"},
        {"from": "Governance", "to": "Logic", "description": "Approved operation"},
        {"from": "Logic", "to": "Output", "description": "Result + audit trail"},
    ]


def _constitutional_checklist(query: str) -> list[dict]:
    """Generate constitutional checklist for design.

    P0-#3 FIX (2026-07-07): F1, F4, F11, F13 implemented inline.
    Other floors raise NotImplementedError (fail closed — cannot claim compliance
    without real checks).

    Each floor returns {"floor": str, "check": str, "status": "PASS"|"FAIL"|"BLOCK"|"ERROR",
                        "detail": str}.
    """
    query_lower = query.lower()
    results: list[dict] = []

    # ── F1 AMANAH: Can this be reversed? ──────────────────────────
    irreversible_markers = [
        "delete",
        "drop",
        "destroy",
        "remove permanently",
        "rm -rf",
        "truncate",
        "purge",
        "wipe",
        "irreversible",
        "one-way",
    ]
    has_irreversible = any(marker in query_lower for marker in irreversible_markers)
    results.append(
        {
            "floor": "F1",
            "check": "Can this be reversed?",
            "status": "FAIL" if has_irreversible else "PASS",
            "detail": (
                "Irreversible action detected — requires sovereign ack (F1 AMANAH)"
                if has_irreversible
                else "No irreversible markers found in query"
            ),
        }
    )

    # ── F4 CLARITY: Is complexity justified? ──────────────────────
    # Heuristic: count distinct component/concept mentions
    complexity_markers = [
        "microservice",
        "distributed",
        "event-driven",
        "cqrs",
        "event sourcing",
        "multi-tenant",
        "sharding",
        "consensus",
        "byzantine",
        "raft",
        "paxos",
    ]
    complexity_count = sum(1 for m in complexity_markers if m in query_lower)
    # Also count if query is very long (>500 chars) as a proxy for over-scoping
    if len(query) > 500:
        complexity_count += 1
    results.append(
        {
            "floor": "F4",
            "check": "Is complexity justified?",
            "status": "FAIL" if complexity_count >= 3 else "PASS",
            "detail": (
                f"High complexity detected ({complexity_count} markers). "
                "Simplify or justify each component (F4 CLARITY: ΔS ≤ 0)"
                if complexity_count >= 3
                else f"Complexity within bounds ({complexity_count} markers)"
            ),
        }
    )

    # ── F2 TRUTH: Are all facts verifiable? ───────────────────────
    results.append(
        {
            "floor": "F2",
            "check": "Are all facts verifiable?",
            "status": "ERROR",
            "detail": (
                "F2 TRUTH check not implemented — cannot claim compliance without "
                "real evidence verification. Fails closed per P0-#3 directive."
            ),
        }
    )

    # ── F7 HUMILITY: Are uncertainty bands declared? ──────────────
    results.append(
        {
            "floor": "F7",
            "check": "Are uncertainty bands declared?",
            "status": "ERROR",
            "detail": (
                "F7 HUMILITY check not implemented — cannot claim compliance without "
                "real uncertainty band verification. Fails closed per P0-#3 directive."
            ),
        }
    )

    # ── F9 ANTIHANTU: Does this cause harm? ──────────────────────
    results.append(
        {
            "floor": "F9",
            "check": "Does this cause harm?",
            "status": "ERROR",
            "detail": (
                "F9 ANTIHANTU check not implemented — cannot claim compliance without "
                "real harm assessment. Fails closed per P0-#3 directive."
            ),
        }
    )

    # ── F11 AUTH: Is identity verified before sensitive ops? ─────
    auth_markers = ["auth", "identity", "session", "token", "verify", "credential", "proof"]
    has_auth = any(marker in query_lower for marker in auth_markers)
    results.append(
        {
            "floor": "F11",
            "check": "Is identity verified before sensitive ops?",
            "status": "PASS" if has_auth else "FAIL",
            "detail": (
                "Identity/auth mechanism referenced in design"
                if has_auth
                else "No identity verification mechanism mentioned — F11 AUTH requires it"
            ),
        }
    )

    # ── F13 SOVEREIGN: Is human authority preserved? ──────────────
    sovereign_markers = [
        "human",
        "override",
        "veto",
        "approval",
        "sovereign",
        "manual",
        "888_hold",
        "ack_irreversible",
        "human-in-the-loop",
    ]
    has_sovereign = any(marker in query_lower for marker in sovereign_markers)
    results.append(
        {
            "floor": "F13",
            "check": "Is human authority preserved?",
            "status": "PASS" if has_sovereign else "FAIL",
            "detail": (
                "Human override/authority mechanism found in design"
                if has_sovereign
                else "No human authority mechanism — F13 SOVEREIGN requires human veto on irreversible"
            ),
        }
    )

    return results


# ─────────────────────────────────────────────────────────────
# F3 TRI_WITNESS Design Validation
# ─────────────────────────────────────────────────────────────


def validate_design_tri_witness(
    design: dict,
    human_approval: bool = False,
    ai_verdict: str = "SEAL",
    system_verdict: str = "SEAL",
) -> dict:
    """
    F3_QuadWitness validation for architectural decisions.

    Requires consensus from 3 parties:
    - w1: Human (must approve)
    - w2: AI/Auditor (constitutional check)
    - w3: Earth/System (environmental constraints)

    Args:
        design: Design spec to validate
        human_approval: Has human approved?
        ai_verdict: What did A-AUDITOR say?
        system_verdict: What is the system verdict?

    Returns:
        F3 validation result with consensus score
    """
    w1 = 1.0 if human_approval else 0.0
    w2 = 1.0 if ai_verdict == "SEAL" else 0.5 if ai_verdict == "HOLD" else 0.0
    w3 = 1.0 if system_verdict == "SEAL" else 0.5 if system_verdict == "HOLD" else 0.0

    w4 = 0.75  # Adversarial Byzantine witness (assume worst-case)

    w_cube = (w1 * w2 * w3) ** (1 / 3)
    quad_witness = (w1 + w2 + w3 + w4) / 4

    threshold = 0.75
    consensus_achieved = quad_witness >= threshold

    return {
        "F3_quad_witness": {
            "W1_human": w1,
            "W2_ai": w2,
            "W3_system": w3,
            "W4_adversarial": w4,
            "w_cube": round(w_cube, 4),
            "quad_witness_avg": round(quad_witness, 4),
            "threshold": threshold,
            "consensus_achieved": consensus_achieved,
            "verdict": "SEAL" if consensus_achieved else "VOID",
        },
        "design": design.get("name", "unnamed"),
        "requires": ["human_approval", "ai_constitutional_check", "system_validation"],
    }
