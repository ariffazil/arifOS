"""
arifOS Governance Enforcer — HARD STOP Implementation
═══════════════════════════════════════════════════════════════════════════════

CRITICAL FIX: Prevents HOLD/VOID verdict bypass

Rules:
1. If tool returns HOLD/VOID/F1-violation → HARD STOP (no model call)
2. Query classification BEFORE tool invocation (Class A vs Class B)
3. Audit log immutable for every decision
4. Non-bypass guard: verdict != PASS → model output BLOCKED

Author: 888_VALIDATOR
Version: 2026.04.06-HARDENED
"""

from __future__ import annotations

import hashlib
import json
import time
from enum import StrEnum
from typing import Any

from arifosmcp.runtime.irreversibility import AmanahIrreversibilityScorer
from arifosmcp.runtime.model import RuntimeEnvelope, RuntimeStatus, Verdict

# Global scorer instance — stateless, thread-safe
_AMANAH_SCORER = AmanahIrreversibilityScorer()


class QueryClass(StrEnum):
    """Query classification for governance routing."""

    INFORMATIONAL = "informational"  # Class A: No state change, model can respond directly
    GOVERNED = "governed"  # Class B: State mutation, full F1-L13 required
    CRITICAL = "critical"  # Class C: Irreversible, requires L11 verified identity
    CAPITAL = "capital"  # C4: Money/investment/capital decision — session + WEALTH chain mandatory


# C4 keywords — any of these forces CAPITAL class before checking critical/governed
_C4_CAPITAL_KEYWORDS = [
    "invest",
    "investing",
    "investment",
    "stock",
    "stocks",
    "shares",
    "bursa",
    "klse",
    "klci",
    "unit trust",
    "amanah saham",
    "asb",
    "epf",
    "fund",
    "funds",
    "portfolio",
    "trading",
    "trade",
    "dividend",
    "equity",
    "equities",
    "bond",
    "bonds",
    "etf",
    "reit",
    "reits",
    "buy stock",
    "sell stock",
    "market open",
    "monday buy",
    "rm ",
    "ringgit",
    "usd ",
    "myr",
    "sgd",
    "capital allocation",
    "wealth allocation",
    "asset allocation",
    "where to put my money",
    "where should i put",
    "how to invest",
    "good investment",
    "return on investment",
    "roi",
    "ticker",
    "bursa malaysia",
]

# Phrases that MUST NOT appear in output without a valid GovernanceReceipt.
# Keep in sync with OutputFirewall._BLOCKED_PHRASES in envelope.py.
BLOCKED_INVESTMENT_PHRASES = [
    "buy this on monday",
    "buy on monday",
    "shares on monday",
    "best stock to buy",
    "put rm",
    "put usd",
    "guaranteed return",
    "sure win",
    "all-in",
    "market open buy",
    "sure profit",
    "confirmed return",
    "100% return",
    "no risk",
    "on monday",  # timing-specific buy signal
]


class PropagationDecision(StrEnum):
    """Propagation decision for audit trail."""

    ALLOWED = "ALLOWED"
    BLOCKED_HOLD = "BLOCKED_HOLD"
    BLOCKED_VOID = "BLOCKED_VOID"
    BLOCKED_SABAR = "BLOCKED_SABAR"
    BLOCKED_F1 = "BLOCKED_F1_VIOLATION"
    BLOCKED_INJECTION = "BLOCKED_INJECTION"
    BLOCKED_UNVERIFIED = "BLOCKED_UNVERIFIED_ACTOR"


def _select_leaf_tool(
    query: str, query_class: QueryClass, context: dict[str, Any] | None = None
) -> str:
    """Resolve a non-recursive organ for governed kernel routing."""
    context = context or {}
    requested_mode = str(context.get("mode") or "").lower()
    query_lower = query.lower()

    if requested_mode in {"status", "probe", "state"}:
        return "arifos_ops"
    if query_class == QueryClass.INFORMATIONAL:
        return "arifos_mind"

    if any(kw in query_lower for kw in ["judge", "verdict", "approve", "hold", "seal check"]):
        return "arifos_judge"
    if any(kw in query_lower for kw in ["forge", "execute", "deploy", "run", "ship"]):
        return "arifos_forge"
    if any(kw in query_lower for kw in ["vault", "ledger", "seal", "receipt"]):
        return "arifos_vault"
    if any(kw in query_lower for kw in ["memory", "remember", "recall", "context"]):
        return "arifos_memory"
    if any(kw in query_lower for kw in ["risk", "harm", "safety", "heart"]):
        return "arifos_heart"
    if any(kw in query_lower for kw in ["cost", "ops", "health", "telemetry", "status", "monitor"]):
        return "arifos_ops"
    if any(kw in query_lower for kw in ["sense", "ground", "verify", "reality", "fetch"]):
        return "arifos_sense"
    if query_class == QueryClass.CRITICAL:
        return "arifos_judge"
    return "arifos_mind"


class GovernanceEnforcer:
    """
    HARD STOP enforcer for MCP orchestration layer.

    Ensures:
    - HOLD/VOID terminates execution chain
    - Model is NOT called if tool returns non-PASS verdict
    - Audit trail is immutable
    - No bypass possible
    """

    def __init__(self):
        self.audit_log: list[dict] = []

    def classify_query(self, query: str, context: dict[str, Any] | None = None) -> QueryClass:
        """
        Classify query BEFORE any tool invocation.

        Class A (Informational): Conceptual, explanatory, analytical
        Class B (Governed): State mutation, memory write, seal
        Class C (Critical): Irreversible, execution, sovereign mode
        """
        context = context or {}

        governed_keywords = [
            "seal",
            "commit",
            "write",
            "execute",
            "spawn",
            "deploy",
            "modify",
            "delete",
            "create",
            "sign",
            "authorize",
            "approve",
        ]
        critical_keywords = [
            "irreversible",
            "permanent",
            "sovereign",
            "vault",
            "forge",
            "system",
            "kernel",
            "shutdown",
            "format",
            "wipe",
        ]

        query_lower = query.lower()
        # C4 CAPITAL check runs first — money decisions require the strictest gate
        if any(kw in query_lower for kw in _C4_CAPITAL_KEYWORDS):
            return QueryClass.CAPITAL
        if any(kw in query_lower for kw in critical_keywords):
            return QueryClass.CRITICAL
        if any(kw in query_lower for kw in governed_keywords):
            return QueryClass.GOVERNED
        return QueryClass.INFORMATIONAL

    def evaluate_intent(
        self,
        tool_name: str,
        action: str,
        parameters: dict[str, Any],
        actor_id: str = "anonymous",
        session_id: str | None = None,
    ) -> RuntimeEnvelope:
        """
        Fast-track intent evaluation for unified substrates (F2/L11).
        Does NOT invoke the tool; only checks if the intent is constitutionally allowed.
        """
        from arifosmcp.runtime.model import RuntimeEnvelope, RuntimeStatus, Verdict

        # 1. Scrutinize via Amanah
        args = {**parameters, "action": action, "session_id": session_id}
        score_result = _AMANAH_SCORER.evaluate_payload(
            tool_name=tool_name,
            mode=action,
            args=args,
            actor_id=actor_id,
        )

        if score_result.triggers_888_hold:
            return RuntimeEnvelope(
                ok=False,
                tool=tool_name,
                verdict=Verdict.HOLD,
                status=RuntimeStatus.ERROR,
                detail=f"888_HOLD (Amanah): {score_result.reason} (score={score_result.score})",
            )

        return RuntimeEnvelope(
            ok=True,
            tool=tool_name,
            verdict=Verdict.SEAL,
            status=RuntimeStatus.SUCCESS,
        )

    def evaluate_tool_verdict(
        self,
        tool_name: str,
        envelope: RuntimeEnvelope,
        query_hash: str,
        actor_id: str = "anonymous",
    ) -> tuple[PropagationDecision, dict | None]:
        """
        Evaluate tool verdict and return propagation decision.

        Returns:
            (decision, response_or_none)
            If decision is BLOCKED_* → response contains error
            If decision is ALLOWED → response is None (continue to model)
        """
        verdict = envelope.verdict
        status = envelope.status

        if verdict == Verdict.VOID:
            decision = PropagationDecision.BLOCKED_VOID
            response = self._create_block_response(decision, tool_name, envelope)
            self._log_audit(query_hash, tool_name, verdict, decision, actor_id)
            return decision, response

        if verdict == Verdict.HOLD:
            decision = PropagationDecision.BLOCKED_HOLD
            response = self._create_block_response(decision, tool_name, envelope)
            self._log_audit(query_hash, tool_name, verdict, decision, actor_id)
            return decision, response

        if verdict == Verdict.SABAR:
            decision = PropagationDecision.BLOCKED_SABAR
            response = self._create_block_response(decision, tool_name, envelope)
            self._log_audit(query_hash, tool_name, verdict, decision, actor_id)
            return decision, response

        if isinstance(envelope.payload, dict):
            irreversibility = envelope.payload.get("irreversibility", False)
            acknowledged = envelope.payload.get("irreversibility_acknowledged", False)
            if irreversibility and not acknowledged:
                decision = PropagationDecision.BLOCKED_F1
                response = self._create_block_response(decision, tool_name, envelope)
                self._log_audit(query_hash, tool_name, verdict, decision, actor_id)
                return decision, response

        if status == RuntimeStatus.ERROR:
            if isinstance(envelope.payload, dict) and envelope.payload.get("tom_violation"):
                decision = PropagationDecision.BLOCKED_INJECTION
                response = self._create_block_response(decision, tool_name, envelope)
                self._log_audit(query_hash, tool_name, verdict, decision, actor_id)
                return decision, response

        mode = envelope.mode or "default"
        args = envelope.payload or {}
        irreversibility_result = _AMANAH_SCORER.evaluate_payload(
            tool_name=tool_name,
            mode=mode,
            args=args,
            actor_id=actor_id,
        )
        if irreversibility_result.triggers_888_hold:
            decision = PropagationDecision.BLOCKED_HOLD
            response = self._create_block_response(
                PropagationDecision.BLOCKED_HOLD, tool_name, envelope
            )
            response["_amanah_score"] = irreversibility_result.score
            response["_floor_violations"] = irreversibility_result.floor_violations
            response["_reason"] = irreversibility_result.reason
            response["_detail"] = irreversibility_result.detail
            response["error"] = (
                f"888_HOLD (Amanah): {irreversibility_result.reason} — score={irreversibility_result.score} — {irreversibility_result.detail}"  # noqa: E501
            )
            self._log_audit(query_hash, tool_name, verdict, decision, actor_id)
            return decision, response

        decision = PropagationDecision.ALLOWED
        self._log_audit(query_hash, tool_name, verdict, decision, actor_id)
        return decision, None

    def _create_block_response(
        self,
        decision: PropagationDecision,
        tool_name: str,
        envelope: RuntimeEnvelope,
    ) -> dict[str, Any]:
        """Create structured block response."""

        block_messages = {
            PropagationDecision.BLOCKED_HOLD: {
                "error": "888_HOLD: Action requires human approval",
                "detail": "This action has been held pending sovereign review.",
                "action_required": "Wait for 888_HOLD clearance or request manual override",
            },
            PropagationDecision.BLOCKED_VOID: {
                "error": "VOID: Constitutional violation detected",
                "detail": "This action violates F1-L13 constitutional floors.",
                "action_required": "Redesign action to satisfy constitutional constraints",
            },
            PropagationDecision.BLOCKED_SABAR: {
                "error": "888_SABAR: Action under review / cooling period",
                "detail": "This action has triggered a conditional hold (SABAR).",
                "action_required": "Initiate cooling period (300s) or escalate for human review.",
            },
            PropagationDecision.BLOCKED_F1: {
                "error": "F1 Amanah: Irreversible action without acknowledgment",
                "detail": "Irreversible actions require explicit irreversibility_acknowledged=true",
                "action_required": "Set irreversibility_acknowledged and provide rollback_plan",
            },
            PropagationDecision.BLOCKED_INJECTION: {
                "error": "L13: Injection or malformed input detected",
                "detail": "Input failed ToM validation or constitutional schema check.",
                "action_required": "Provide required ToM fields and retry",
            },
            PropagationDecision.BLOCKED_UNVERIFIED: {
                "error": "L11: Unverified actor on critical action",
                "detail": "Critical tier actions require verified identity.",
                "action_required": "Complete identity verification via init_anchor",
            },
        }

        message = block_messages.get(
            decision,
            {
                "error": "GOVERNANCE_BLOCK: Action blocked",
                "detail": "Unknown governance violation",
                "action_required": "Contact administrator",
            },
        )

        # Select contextually relevant philosophy for the block
        from arifosmcp.runtime.philosophy import AtlasScores, select_atlas_philosophy

        # Map decision to philosophical coordinates proxy
        # BLOCKED_VOID/HOLD -> Void/Paradox zone
        # BLOCKED_F1/UNVERIFIED -> Discipline zone
        phi_category = (
            "void"
            if decision
            in (
                PropagationDecision.BLOCKED_VOID,
                PropagationDecision.BLOCKED_HOLD,
                PropagationDecision.BLOCKED_SABAR,
            )
            else "discipline"
        )
        scores = AtlasScores(
            delta_s=1.0,
            g_score=0.2,
            omega_score=0.9,
            lyapunov_sign="stable",
            verdict=(
                envelope.verdict.value
                if hasattr(envelope.verdict, "value")
                else str(envelope.verdict)
            ),
            session_stage=envelope.stage,
        )
        phi_result = select_atlas_philosophy(scores, contrast_override=phi_category)
        primary = phi_result.get("primary_quote", {})

        return {
            "ok": False,
            "governance_block": True,
            "decision": decision.value,
            "tool": tool_name,
            "verdict": (
                envelope.verdict.value
                if hasattr(envelope.verdict, "value")
                else str(envelope.verdict)
            ),
            "stage": envelope.stage,
            **message,
            "philosophy": {
                "quote": primary.get("quote", "DITEMPA, BUKAN DIBERI."),
                "author": primary.get("author", "arifOS"),
                "category": primary.get("category", phi_category),
                "note": "Governance boundary enforced with constitutional framing.",
            },
        }

    def _log_audit(
        self,
        query_hash: str,
        tool_name: str,
        verdict: Verdict,
        decision: PropagationDecision,
        actor_id: str,
    ) -> None:
        """Immutable audit logging."""
        verdict_str = verdict.value if hasattr(verdict, "value") else str(verdict)
        decision_str = decision.value if hasattr(decision, "value") else str(decision)

        entry = {
            "timestamp": time.time(),
            "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "query_hash": query_hash,
            "tool_invoked": tool_name,
            "verdict": verdict_str,
            "propagation_decision": decision_str,
            "actor_id": actor_id,
        }
        entry_data = json.dumps(entry, sort_keys=True)
        entry["entry_hash"] = hashlib.sha256(entry_data.encode()).hexdigest()[:32]
        self.audit_log.append(entry)

    def get_audit_log(self) -> list[dict]:
        """Return immutable audit log copy."""
        return [dict(entry) for entry in self.audit_log]

    def verify_audit_integrity(self) -> bool:
        """Verify audit log has not been tampered with."""
        for entry in self.audit_log:
            stored_hash = entry.get("entry_hash")
            if not stored_hash:
                return False

            test_entry = {k: v for k, v in entry.items() if k != "entry_hash"}
            test_data = json.dumps(test_entry, sort_keys=True, default=str)
            computed_hash = hashlib.sha256(test_data.encode()).hexdigest()[:32]
            if computed_hash != stored_hash:
                return False

        return True


# Global enforcer instance
_enforcer: GovernanceEnforcer | None = None


def get_enforcer() -> GovernanceEnforcer:
    """Get or create global governance enforcer."""
    global _enforcer
    if _enforcer is None:
        _enforcer = GovernanceEnforcer()
    return _enforcer


async def classify_and_route(
    query: str,
    context: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Classify query and determine if tool invocation is required.

    Accepts optional kwargs (actor_id, session_id, etc.) from kernel_core
    to maintain adapter compatibility without bloating the core router.

    Returns:
        dict with routing result (tool_name, ok, etc.) for kernel compatibility
    """
    enforcer = get_enforcer()
    query_class = enforcer.classify_query(query, context)

    # Informational queries don't require tools; governed queries must resolve to a leaf organ.
    requires_tool = query_class != QueryClass.INFORMATIONAL
    tool_name = _select_leaf_tool(query, query_class, context)

    return {
        "ok": True,
        "tool_name": tool_name,
        "query_class": query_class.value,
        "requires_tool": requires_tool,
        "route_intent": {
            "query_class": query_class.value,
            "requested_mode": context.get("mode") if context else None,
        },
    }


def enforce_tool_verdict(
    tool_name: str,
    envelope: RuntimeEnvelope,
    query: str,
    actor_id: str = "anonymous",
) -> tuple[bool, dict | None]:
    """
    HARD STOP enforcement wrapper.

    Returns:
        (allowed, response_or_none)
        allowed=True → continue to model
        allowed=False → return response (blocked)
    """
    enforcer = get_enforcer()
    query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]

    decision, response = enforcer.evaluate_tool_verdict(
        tool_name=tool_name,
        envelope=envelope,
        query_hash=query_hash,
        actor_id=actor_id,
    )

    allowed = decision == PropagationDecision.ALLOWED
    return allowed, response


def classify_decision_guard(
    query: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Machine-readable decision classifier for high-stakes queries.

    Returns a classification receipt that downstream tools and the output firewall
    can validate. Every C4/C5 node independently checks this — not a single chokepoint
    (L08 distributed intelligence). Each layer decides for itself.

    Returns:
        dict with decision_class, domain, requires_* flags, direct_instruction_allowed
    """
    enforcer = get_enforcer()
    query_class = enforcer.classify_query(query, context)

    # Domain detection (order matters — most specific first)
    query_lower = query.lower()
    if any(kw in query_lower for kw in _C4_CAPITAL_KEYWORDS):
        domain = "wealth"
        decision_class = "C4"
    elif any(
        kw in query_lower for kw in ["legal", "lawyer", "sue", "court", "regulation", "compliance"]
    ):
        domain = "legal"
        decision_class = "C4"
    elif any(
        kw in query_lower for kw in ["medical", "doctor", "diagnosis", "symptom", "drug", "dosage"]
    ):
        domain = "medical"
        decision_class = "C4"
    elif any(
        kw in query_lower
        for kw in ["fire", "terminate", "resign", "contract", "employment", "petronas"]
    ):
        domain = "employment"
        decision_class = "C4"
    elif any(
        kw in query_lower
        for kw in ["publish", "public", "media", "statement", "reputation", "announcement"]
    ):
        domain = "reputation"
        decision_class = "C4"
    elif query_class == QueryClass.CRITICAL:
        domain = "system"
        decision_class = "C5"
    elif query_class == QueryClass.GOVERNED:
        domain = "governed"
        decision_class = "C3"
    else:
        domain = "general"
        decision_class = "C1"

    is_capital = decision_class in ("C4", "C5")
    is_wealth_domain = domain == "wealth"

    return {
        "decision_class": decision_class,
        "query_class": query_class.value,
        "domain": domain,
        "requires_init": is_capital,
        "requires_well": is_capital,
        "requires_wealth": is_wealth_domain,
        "requires_fresh_evidence": is_capital,
        "direct_instruction_allowed": not is_capital,
        "ticker_names_allowed": False,
        "execution_instruction_allowed": False,
        "output_level": "ADVISORY_ONLY" if is_capital else "FULL",
        "mandatory_receipt": is_capital,
        "human_final_authority": "Arif" if is_capital else None,
    }


def session_gate_c4(query_class: QueryClass, session_id: str | None) -> dict | None:
    """
    Hard gate for C4 CAPITAL decisions: if no valid session_id, return HOLD immediately.

    This is the first enforcement layer — runs before any WEALTH tool is called.
    Returns None if session is present (caller may proceed).
    Returns a HOLD dict if session is absent (caller must stop).
    """
    if query_class != QueryClass.CAPITAL:
        return None
    if session_id and session_id.strip():
        return None
    return {
        "ok": False,
        "verdict": "HOLD",
        "decision_class": "C4",
        "governance_block": True,
        "error": "C4_SESSION_REQUIRED: Capital/investment decisions require a governed session.",
        "detail": (
            "Call arif_init first to open a governed session. "
            "Money decisions are C4 — no session means no recommendation."
        ),
        "action_required": "arif_init(mode='init', actor_id='<your-id>')",
        "output_policy": "HOLD",
    }


def scan_output_for_investment_advice(draft: str, receipt: dict | None) -> dict | None:
    """
    Output firewall — runs on any draft response before it reaches the operator.

    Scans for high-risk investment-advice phrases.
    If found AND no valid WEALTH receipt exists, returns a HOLD block.
    Returns None if draft is clean or receipt is present and complete.

    This is the last enforcement layer — the compiler that catches what slipped through.
    """
    if not draft:
        return None

    draft_lower = draft.lower()
    triggered = [phrase for phrase in BLOCKED_INVESTMENT_PHRASES if phrase in draft_lower]
    if not triggered:
        return None

    # Check if a valid receipt covers this output
    if receipt:
        checks = receipt.get("checks_completed", [])
        required_checks = {"conservation", "liquidity", "boundary_governance"}
        if required_checks.issubset(set(checks)) and receipt.get("session_valid"):
            return None  # Receipt present and complete — allow

    return {
        "ok": False,
        "verdict": "HOLD",
        "governance_block": True,
        "firewall": "OUTPUT_FIREWALL",
        "triggered_phrases": triggered,
        "error": (
            "HOLD — investment-specific output blocked: insufficient governed trace. "
            "A full C4 WEALTH chain is required before any asset-specific recommendation."
        ),
        "detail": (
            "The draft contained high-stakes investment phrases without a complete "
            "WEALTH governance receipt (conservation + liquidity + boundary_governance checks)."
        ),
        "output_policy": "ADVISORY_ONLY",
        "allowed_output": (
            "General financial education, comparison frameworks, and questions "
            "that help Arif reflect — but no specific tickers, amounts, or buy/sell dates."
        ),
    }


__all__ = [
    "GovernanceEnforcer",
    "QueryClass",
    "PropagationDecision",
    "get_enforcer",
    "classify_and_route",
    "enforce_tool_verdict",
]
