"""
Phase 2 — Contradiction Detector (2026-08-06)

Read-only middleware. Logs every disagreement between the single-writer
`authority` block and the 64 legacy fields that also answer "may I proceed?".

This proves the 64 are redundant before Phase 4 deletion. Each disagreement
is a live bug — callers may have acted on a wrong answer.

FastMCP 3.4.4. Registered BEFORE AuthorityMiddleware so it sees the
pre-authority payload with legacy fields intact.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

from fastmcp.server.middleware import Middleware, MiddlewareContext

logger = logging.getLogger(__name__)

# ── Version Pin: FastMCP 3.4.4 ───────────────────────────────────────────────


# All 64 fields that answer "may I proceed?" — from Suite A1 census
LEGACY_FIELDS = [
    # Mutation authority (multiple writers)
    "mutation_allowed",
    "result.mutation_allowed",
    "actor.authority_state.runtime_grant.mutation_allowed",
    "standing.authority.mutation_allowed",
    "session_birth.mutation_allowed",
    # Seal authority
    "seal_allowed",
    "result.seal_allowed",
    "actor.authority_state.runtime_grant.seal_allowed",
    "standing.authority.seal_allowed",
    "session_birth.seal_allowed",
    # Execution readiness
    "execution_readiness",
    "execution_state",
    "can_mutate",
    "can_claim_success",
    "can_continue_observing",
    # Verdict — multiple fields answering same question
    "effective_verdict",
    "verdicts.action.state",
    "verdicts.substrate.state",
    "verdicts.session.state",
    "nine_signal.overall.state",
    "nine_signal.overall.en",
    "canonical_verdict",
    "verdicts.action.issuer",
    # Authority scope
    "authority_scope",
    "authority_band",
    "actor.authority_level",
    "standing.authority.band",
    "session_birth.authority_mode",
    # Action verdicts
    "result.effective_verdict",
    "next_action",
    "reason_code",
    "result.reason_code",
    # Session state
    "session_notice.session_state",
    "session_notice.action_verdict",
    "session_notice.severity",
    # Risk
    "risk.agency_level",
    "risk.human_confirmation_required",
    # Constitutional
    "constitutional_check.hold_required",
    "constitutional_check.agency_level",
    # Affordance
    "affordance_contract.action_class",
    "affordance_contract.mutation",
    "affordance_contract.requires_human_ack",
    # Substrate
    "substrate.state",
    "substrate.drift",
    # Degraded
    "degraded",
    "_drift_floor_applied",
    "response_prefix",
    # Output policy
    "output_policy",
    "status_scope",
    # Receipt
    "receipt_state",
    # Actor verification
    "actor.actor_verified",
    "standing.actor.verified",
    "session_birth.actor_verified",
    "actor_cryptographically_verified",
    "session_birth.actor_cryptographically_verified",
    # Warnings
    "warnings",
    "_violations",
    "_nine_signal_compliant",
    # Meta
    "meta.authority_mode",
    "meta.sabar_gate.verdict",
    "meta.post_observe_gate.verdict",
    # Seal readiness
    "seal_readiness",
]


def _dig(d: dict, path: str, default: Any = None) -> Any:
    """Drill into nested dict by dot-separated path."""
    keys = path.split(".")
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k, default)
        else:
            return default
    return d


def _disagrees(legacy_val: Any, authority_verdict: str) -> bool:
    """Determine if a legacy field disagrees with the computed authority verdict."""
    if legacy_val is None:
        return False  # absent field — not a disagreement, just missing

    # mutation_allowed-like booleans vs HOLD/SABAR
    if authority_verdict in ("HOLD", "VOID"):
        # Under HOLD/VOID, nothing should be allowed
        if legacy_val in (True, "true", "SEAL", "APPROVED", "PROCEED", "FULL"):
            return True
        if isinstance(legacy_val, str) and legacy_val.upper() in ("SEAL", "FULL", "SOVEREIGN"):
            return True

    # SABAR vs FULL
    if authority_verdict == "SABAR":
        if legacy_val in (True, "SEAL", "APPROVED"):
            return True

    # PROCEED/SEAL — permissive, but shouldn't contradict with DENIED/HOLD artifacts
    if legacy_val in (False, "HOLD", "VOID", "OBSERVE_ONLY") and authority_verdict in (
        "PROCEED",
        "SEAL",
    ):
        return True

    return False


# ── Phase 4: Legacy Field Stripping ───────────────────────────────────
# After AuthorityMiddleware has injected the sole canonical authority block,
# these 64 legacy fields are structurally proven redundant. Strip them.


def _strip_nested(d: dict, path: str) -> bool:
    """Remove a nested key from a dict. Returns True if key was removed."""
    keys = path.split(".")
    current = d
    for k in keys[:-1]:
        if not isinstance(current, dict):
            return False
        current = current.get(k)
        if current is None:
            return False
    if isinstance(current, dict) and keys[-1] in current:
        del current[keys[-1]]
        return True
    return False


def strip_legacy_fields(sc: dict) -> tuple[int, list[str]]:
    """Strip all 64 legacy fields from the structured content.

    Returns (count_removed, list_of_removed_paths).
    Authority block is NEVER touched — it is the canonical truth.
    """
    removed = []
    for path in LEGACY_FIELDS:
        if _strip_nested(sc, path):
            removed.append(path)
    return len(removed), removed


class ContradictionDetector(Middleware):
    """Phase 2+4: Logs disagreements AND strips legacy fields.

    Registered BEFORE AuthorityMiddleware so it sees the pre-authority payload
    with the 64 legacy fields still intact. After logging, strips them —
    leaving only the canonical `authority` block as the single source of truth.

    Phase 4 COMPLETE when strip_legacy_fields is called after AuthorityMiddleware
    has injected the authority block. The legacy 64 are removed from the wire.
    """

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        result = await call_next(context)

        sc = getattr(result, "structured_content", None)
        if sc is None:
            return result

        # The authority block is already computed and injected by AuthorityMiddleware
        authority = sc.get("authority", {})
        if not authority:
            return result

        authority_verdict = authority.get("verdict", "UNKNOWN")
        tool_name = getattr(context.message, "name", "unknown")

        # Phase 2: Check every legacy field for disagreements
        disagreements = []
        for path in LEGACY_FIELDS:
            val = _dig(sc, path)
            if _disagrees(val, authority_verdict):
                disagreements.append(
                    {
                        "tool": tool_name,
                        "field": path,
                        "value": str(val),
                        "authority_verdict": authority_verdict,
                    }
                )

        if disagreements:
            sys.stderr.write(
                f"CONTRADICTION_DETECTED: {tool_name} — {len(disagreements)} disagreements\n"
            )
            for d in disagreements:
                sys.stderr.write(
                    f"  {d['field']} = {d['value']} vs authority.{d['authority_verdict']}\n"
                )
            logger.warning(
                "ContradictionDetector: %d disagreements in %s",
                len(disagreements),
                tool_name,
            )

        # Phase 4: Strip all 64 legacy fields — only authority block remains
        count, removed = strip_legacy_fields(sc)
        if count > 0:
            sys.stderr.write(
                f"PHASE4_STRIP: {tool_name} — removed {count} legacy fields: {removed[:5]}...\n"
            )
            logger.info(
                "Phase 4: stripped %d legacy fields from %s. Authority block is now sole truth.",
                count,
                tool_name,
            )
        else:
            sys.stderr.write(
                f"PHASE4_STRIP: {tool_name} — ZERO fields stripped. sc keys: {list(sc.keys())[:10]}\n"
            )

        # KRT-2026-08-15 F1b: after dedupe, RE-EMIT the canonical governance
        # verdict from the sole source of truth (the authority block).
        # Stripping effective_verdict without re-emitting left the wire with
        # only execution-valued fields (status/verdict="completed") — a HOLD
        # read as success to any caller not inspecting `authority` (the
        # FORGE-RECEIPT-DISHONEST / VERDICT-FORK failure mode). One field,
        # one writer: authority.verdict.
        sc["effective_verdict"] = authority_verdict
        sc["execution_state"] = {
            "VOID": "FAILED",
            "HOLD": "AWAIT_INPUT",
            "888_HOLD": "AWAIT_SOVEREIGN",
        }.get(str(authority_verdict).upper(), "COMPLETED")

        return result
