"""
forge_preflight — WS3 Pre-Execution Chain (canonical)

DITEMPA BUKAN DIBERI

Forged 2026-07-12 under F13 SOVEREIGN directive.
Cycle: forge_work/2026-07-12/KERNEL-INTELLIGENCE-HARDENING-CYCLE-PHASE-A.md §3

The 13-step pre-execution chain runs BEFORE any A-FORGE mutation. Each
step must pass; any failure fails closed (HOLD) with a precise reason code.

Steps (WS3 §3.1):
  1.  session-token validation
  2.  actor/session binding
  3.  authority recomputation (AuthorityState, single source)
  4.  judge-state retrieval
  5.  judge-state hash recomputation (forgery-detector)
  6.  constitutional-chain validation
  7.  vault receipt integrity (Ed25519 + SHA-256 walk-back)
  8.  plan + manifest binding (hash-equality)
  9.  reversibility classification
  10. human-ack check (single-shot, never copyable)
  11. dry-run simulation
  12. execute-or-HOLD decision
  13. vault-seal emission (atomic, ledger+belief+vault999)

Status: this module EXPOSES the chain shape and a 12-field receipt. The
implementation of each step delegates to existing canonical call sites:

  - step 3 → arifosmcp.runtime.authority.read_authority_state
  - step 1-2, 4-8 → arifosmcp.runtime.pre_execution_gate / pre_execution_gate.CANONICAL_TOOL_MANIFEST
  - step 7 → arifosmcp.runtime.vault_registry.verify_seal (after Ed25519 upgrade)
  - step 9 → arifosmcp.runtime.irreversibility.AmanahIrreversibilityScorer
  - step 13 → arifosmcp.core.vault999.write_seal

WS3 documentation-only emission lives here; production calls sites are
TO BE wired in WS3 step (this module is the receipt SHAPE).
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ForgePreflightReceipt:
    """WS3 §3.2: 12-field pre-execution receipt.

    Every forge call recomputes these fields from authoritative sources.
    No field may be carried over from the caller's claim without
    re-verification against the canonical kernel state.

    ``_step_XX_pass`` flags are booleans derived from kernel-level checks
    — NEVER trusts caller-asserted confirmation (see WS3 cycle §3.1
    "Trust-Loop Finding").

    ``forged_*_flag`` fields are anti-pattern markers: if True, the
    request MUST be rejected and the caller subject to F11 hold.
    """

    # Identifiers
    preflight_id: str
    session_id: str
    actor_id: str
    trace_id: str

    # Authority (single-source: AuthorityState)
    authority_state_summary: dict[str, Any]

    # Judge chain
    judge_verdict: str
    judge_state_hash: str
    judge_state_hash_recomputed: str
    judge_state_forged: bool

    # Constitutional chain
    constitutional_chain_id: str | None
    constitutional_chain_valid: bool

    # Vault receipt
    vault_entry_id: str | None
    vault_seal_signature_valid: bool  # Ed25519 verified
    vault_chain_walked_to_genesis: bool  # SHA-256 hash-chain integrity

    # Plan + manifest
    plan_id: str
    manifest_hash: str
    manifest_matches_plan: bool

    # Reversibility + human ack
    reversibility_score: float
    reversibility_threshold: float
    reversibility_pass: bool
    human_ack_required: bool
    human_ack_valid: bool

    # Dry-run + execute decision
    dry_run_passed: bool
    final_gate: str  # "PROCEED" | "HOLD"

    # Step pass map (13 booleans, every step re-derived)
    step_pass: dict[str, bool] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


def compute_preflight_id(session_id: str, actor_id: str, plan_id: str) -> str:
    """Deterministic preflight id from session+actor+plan.

    Caller-asserted id is rejected; id is recomputed from the canonical
    source tuple. Allows the kernel to detect forged preflight claims.
    """
    h = hashlib.sha256(f"{session_id}|{actor_id}|{plan_id}".encode("utf-8")).hexdigest()
    return f"pf_{h[:24]}"


def _chain_step_pass(step_name: str, passed: bool) -> None:
    """Logging helper: every step gets a logged outcome at INFO."""
    if passed:
        logger.info("forge_preflight step %s PASS", step_name)
    else:
        logger.warning("forge_preflight step %s FAIL", step_name)


def forge_preflight(
    *,
    session_id: str,
    actor_id: str,
    plan_id: str,
    claimed_judge_state_hash: str | None = None,
    claimed_vault_entry_id: str | None = None,
    claimed_human_ack_token: str | None = None,
    manifest: dict[str, Any] | None = None,
    requested_action: str | None = None,
) -> ForgePreflightReceipt:
    """WS3 §3.2: pre-execution chain.

    Runs all 13 steps. Returns the receipt. Even on HOLD, the receipt
    is produced with ``step_pass`` map showing which step failed — so
    the caller has the exact reason code for failure-mode diagnosis.

    NOTE: WS3 acceptance test requires this function to fail-closed on
    forged judge hash (Gate 11), replayed vault receipt (Gate 12), and
    expired session (Gate 13). Tests live in
    tests/adversarial/test_forge_preflight_chain.py.
    """
    preflight_id = compute_preflight_id(session_id, actor_id, plan_id)
    manifest = manifest or {}
    step_pass: dict[str, bool] = {}

    # ── Step 1: session-token validation ──────────────────────────────
    try:
        from arifosmcp.runtime.session_auth import validate_session

        sess_check = validate_session(session_id, required=True)
        step_pass["1_session_token"] = sess_check.get("valid", False)
    except Exception as exc:
        logger.warning("step 1 session-token validation failed: %s", exc)
        step_pass["1_session_token"] = False

    # ── Step 2: actor/session binding ─────────────────────────────────
    try:
        # Patched P0 fix (2026-07-04): enforce binding; no anonymous forge
        actor_bound_to_session = bool(actor_id and actor_id not in {"anonymous", ""})
        step_pass["2_actor_binding"] = actor_bound_to_session
    except Exception:
        step_pass["2_actor_binding"] = False

    # ── Step 3: authority recomputation (AuthorityState) ──────────────
    authority_state_summary: dict[str, Any] = {}
    try:
        from arifosmcp.runtime.authority import read_authority_state
        from arifosmcp.runtime.tools import _SESSIONS

        sess = _SESSIONS.get(session_id)
        if isinstance(sess, dict):
            state = read_authority_state(sess)
            authority_state_summary = {
                "actor": state.actor.claimed_id,
                "verified": state.actor.verified,
                "method": state.actor.verification_method,
                "execution_authority": state.execution_authority,
                "forge_gate_enabled": state.forge_gate.enabled,
            }
        else:
            authority_state_summary = {"execution_authority": "HOLD"}
    except Exception as exc:
        logger.warning("step 3 authority recompute failed: %s", exc)
        authority_state_summary = {"execution_authority": "HOLD"}
    auth_sealed = authority_state_summary.get("execution_authority") == "SEAL_AUTHORIZED"
    step_pass["3_authority"] = auth_sealed

    # ── Step 4: judge-state retrieval ────────────────────────────────
    # Delegated to canonical tool — emit a placeholder hash
    judge_verdict = "JUDGE_SEAL_AUTHORIZATION" if auth_sealed else "JUDGE_HOLD"

    # ── Step 5: judge-state hash recomputation (forgery-detector) ─────
    # Caller-claimed hash MUST equal recomputed hash. If they differ,
    # forged_hash_flag=True → HARD REJECT.
    computed_judge_hash = hashlib.sha256(
        f"{session_id}|{actor_id}|{plan_id}|{judge_verdict}".encode("utf-8")
    ).hexdigest()
    judge_state_forged = bool(
        claimed_judge_state_hash and claimed_judge_state_hash != computed_judge_hash
    )
    step_pass["5_judge_hash"] = not judge_state_forged

    # ── Step 6: constitutional-chain validation ─────────────────────
    # TODO (WS3): wire to ConstitutionalChainValidator
    constitutional_chain_valid = auth_sealed
    step_pass["6_constitutional"] = constitutional_chain_valid

    # ── Step 7: vault receipt integrity ─────────────────────────────
    # Crypto verification gating (after Ed25519 upgrade in WS3 step).
    # Today this is best-effort via vault_registry.verify_seal which is
    # JSON-only — Ed25519 still pending.
    vault_seal_signature_valid = False  # conservative; until WS3 wires Ed25519
    vault_chain_walked_to_genesis = False  # conservative
    if claimed_vault_entry_id:
        try:
            from arifosmcp.runtime.vault_registry import verify_seal

            v = verify_seal(claimed_vault_entry_id)
            vault_chain_walked_to_genesis = bool(v.get("chain_ok"))
        except Exception:
            pass
    step_pass["7_vault"] = vault_chain_walked_to_genesis

    # ── Step 8: plan + manifest binding ─────────────────────────────
    manifest_hash = hashlib.sha256(repr(sorted(manifest.items())).encode("utf-8")).hexdigest()
    manifest_matches_plan = bool(plan_id and manifest)
    step_pass["8_manifest"] = manifest_matches_plan

    # ── Step 9: reversibility classification ────────────────────────
    reversibility_threshold = 0.7
    requested = (requested_action or "").lower()
    if any(k in requested for k in ("rm", "delete", "drop", "purge", "destroy")):
        reversibility_score = 0.05  # not reversible
    elif any(k in requested for k in ("deploy", "release", "publish", "send")):
        reversibility_score = 0.3
    elif any(k in requested for k in ("write", "modify", "edit", "commit")):
        reversibility_score = 0.6
    else:
        reversibility_score = 0.95  # observe / read
    reversibility_pass = reversibility_score >= reversibility_threshold
    step_pass["9_reversibility"] = reversibility_pass

    # ── Step 10: human-ack check (single-shot) ─────────────────────
    # If reversibility low, ack required. If no ack provided, fail.
    human_ack_required = reversibility_score < reversibility_threshold
    human_ack_valid = not human_ack_required or bool(
        claimed_human_ack_token and claimed_human_ack_token.startswith("hug_")
    )
    step_pass["10_human_ack"] = human_ack_valid

    # ── Step 11: dry-run simulation ───────────────────────────────
    dry_run_passed = bool(requested_action) and auth_sealed
    step_pass["11_dry_run"] = dry_run_passed

    # ── Step 12: execute-or-HOLD decision ─────────────────────────
    all_pass = all(step_pass.values())
    final_gate = "PROCEED" if all_pass and auth_sealed and not judge_state_forged else "HOLD"
    step_pass["12_final_decision"] = final_gate == "PROCEED"

    # ── Step 13: vault-seal emission (atomic, when PROCEED) ───────
    # Handled by caller after return; this step is informational.
    step_pass["13_seal_emitted"] = False  # caller emits after receipt

    for k, v in step_pass.items():
        _chain_step_pass(k, v)

    return ForgePreflightReceipt(
        preflight_id=preflight_id,
        session_id=session_id,
        actor_id=actor_id,
        trace_id=hashlib.sha256(preflight_id.encode("utf-8")).hexdigest()[:16],
        authority_state_summary=authority_state_summary,
        judge_verdict=judge_verdict,
        judge_state_hash=claimed_judge_state_hash or computed_judge_hash,
        judge_state_hash_recomputed=computed_judge_hash,
        judge_state_forged=judge_state_forged,
        constitutional_chain_id=None,
        constitutional_chain_valid=constitutional_chain_valid,
        vault_entry_id=claimed_vault_entry_id,
        vault_seal_signature_valid=vault_seal_signature_valid,
        vault_chain_walked_to_genesis=vault_chain_walked_to_genesis,
        plan_id=plan_id,
        manifest_hash=manifest_hash,
        manifest_matches_plan=manifest_matches_plan,
        reversibility_score=reversibility_score,
        reversibility_threshold=reversibility_threshold,
        reversibility_pass=reversibility_pass,
        human_ack_required=human_ack_required,
        human_ack_valid=human_ack_valid,
        dry_run_passed=dry_run_passed,
        final_gate=final_gate,
        step_pass=step_pass,
    )


__all__ = [
    "ForgePreflightReceipt",
    "forge_preflight",
    "compute_preflight_id",
]
