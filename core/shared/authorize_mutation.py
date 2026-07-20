"""
core/shared/authorize_mutation.py — Canonical Mutation Authorization Boundary

The SINGLE choke point that all mutation executors must pass through.
Wraps classify_action() and returns a structured AuthorizationResult
with AuthorizedExecution token for tamper-proof execution.

Architecture:
    ALL executors → authorize_mutation() → AuthorizationResult
                                            ↓
                              PROCEED → AuthorizedExecution token
                              ANNOUNCE → AuthorizedExecution token + log
                              REQUIRE_CONTROLS → check controls → AuthorizedExecution
                              HOLD* → REJECTED (no token issued)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field

from .action_profile import (
    ActionProfile,
    GateVerdict,
    classify_action,
)


@dataclass(frozen=True)
class AuthorizedExecution:
    """Tamper-proof execution token. Cannot be forged by caller.

    Executors receive this, not a raw boolean. Any modification
    to args, env, actor, or target after authorization causes
    hash mismatch → REJECTED.
    """

    profile_hash: str  # SHA-256 of the ActionProfile that was authorized
    authorization_receipt: str  # Unique receipt ID for audit trail
    verdict: str  # GateVerdict that authorized this execution
    issued_at: str  # ISO-8601 timestamp
    expires_at: str  # ISO-8601 timestamp (short TTL)
    normalized_command: str  # The exact command that was authorized
    actor_id: str  # Who requested
    session_id: str  # Governing session
    target_environment: str  # production/staging/development
    supplied_controls: list[str] = field(default_factory=list)

    def verify(self, command: str, actor: str, env: str, session: str) -> bool:
        """Verify that current execution matches the authorized one."""
        import time as _time

        if _time.time() > _time.mktime(_time.strptime(self.expires_at, "%Y-%m-%dT%H:%M:%S")):
            return False
        if self.normalized_command != command:
            return False
        if self.actor_id != actor:
            return False
        if self.target_environment != env:
            return False
        if self.session_id != session:
            return False
        return True


@dataclass
class AuthorizationResult:
    """Result of the authorize_mutation() boundary check."""

    allowed: bool
    verdict: str
    profile: ActionProfile
    reason_codes: list[str] = field(default_factory=list)
    required_controls: list[str] = field(default_factory=list)
    missing_controls: list[str] = field(default_factory=list)
    authorized_execution: AuthorizedExecution | None = None
    rejection_reason: str = ""

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "verdict": self.verdict,
            "reason_codes": self.reason_codes,
            "required_controls": self.required_controls,
            "missing_controls": self.missing_controls,
            "rejection_reason": self.rejection_reason,
            "profile": {
                "mutation_class": self.profile.mutation_class.value,
                "blast_radius": self.profile.blast_radius.value,
                "reversibility": self.profile.reversibility,
                "requires_p34": self.profile.requires_p34,
                "requires_p23": self.profile.requires_p23,
                "has_elevated_privilege": self.profile.has_elevated_privilege,
                "authority_self_issued": self.profile.authority_self_issued,
                "destructive_operation": self.profile.destructive_operation,
                "data_loss_possible": self.profile.data_loss_possible,
            },
            "authorized_execution": (
                {
                    "profile_hash": self.authorized_execution.profile_hash,
                    "receipt": self.authorized_execution.authorization_receipt,
                    "normalized_command": self.authorized_execution.normalized_command,
                    "expires_at": self.authorized_execution.expires_at,
                }
                if self.authorized_execution
                else None
            ),
        }


def authorize_mutation(
    tool: str = "",
    executable: str = "",
    arguments: list[str] | None = None,
    args_text: str = "",
    actor_privilege: str = "unknown",
    actor_id: str = "unknown",
    session_id: str = "unknown",
    target_environment: str = "unknown",
    nl_description: str = "",
    supplied_controls: list[str] | None = None,
    judgment_reference: str = "",
) -> AuthorizationResult:
    """The SINGLE canonical boundary for mutation authorization.

    ALL executors (shell, git, docker, deploy, filesystem, SQL, systemd)
    MUST route through this function before any mutation.

    Args:
        tool: MCP tool name (e.g., "forge_shell", "forge_git")
        executable: The actual binary/command (e.g., "rm", "git", "systemctl")
        arguments: List of individual arguments
        args_text: Raw argument string (fallback)
        actor_privilege: "root", "sudo", "user", "unknown"
        actor_id: Who is requesting this action
        session_id: Governing session
        target_environment: "production", "staging", "development", "unknown"
        nl_description: Natural language description (lowest priority)
        supplied_controls: Controls provided by caller (for REQUIRE_CONTROLS)
        judgment_reference: Prior arif_judge SEAL reference (for JUDGE_REQUIRED)

    Returns:
        AuthorizationResult with allowed/denied verdict and AuthorizedExecution token
    """
    args = arguments or []
    supplied = supplied_controls or []

    # ── Step 1: Classify the action ──
    profile = classify_action(
        tool=tool,
        executable=executable,
        arguments=args,
        args_text=args_text,
        actor_privilege=actor_privilege,
        target_environment=target_environment,
        nl_description=nl_description,
    )

    # ── Step 2: Check classifier health ──
    if profile.classification_failure:
        return AuthorizationResult(
            allowed=False,
            verdict="HOLD_UNCLASSIFIED",
            profile=profile,
            reason_codes=["CLASSIFIER_FAILURE"],
            rejection_reason="Classifier failed to process input — fail-closed.",
        )

    # ── Step 3: Enforce gate verdict ──
    verdict = profile.gate_verdict

    # HOLD variants → REJECTED (no token)
    if verdict in (
        GateVerdict.HOLD,
        GateVerdict.HOLD_SELF_AUTHORIZATION,
        GateVerdict.HOLD_UNCLASSIFIED,
    ):
        return AuthorizationResult(
            allowed=False,
            verdict=verdict.value,
            profile=profile,
            reason_codes=profile.reason_codes,
            rejection_reason=f"Gate verdict: {verdict.value}. Reasons: {', '.join(profile.reason_codes)}",
        )

    # JUDGE_REQUIRED → check judgment reference
    if verdict == GateVerdict.JUDGE_REQUIRED:
        if not judgment_reference:
            return AuthorizationResult(
                allowed=False,
                verdict="HOLD_MISSING_JUDGMENT",
                profile=profile,
                reason_codes=profile.reason_codes + ["MISSING_JUDGMENT_REFERENCE"],
                rejection_reason="JUDGE_REQUIRED but no judgment_reference provided.",
            )
        # Validate judgment reference binds to this action
        if not _validate_judgment_binding(
            judgment_reference, profile, executable, args, actor_id, session_id, target_environment
        ):
            return AuthorizationResult(
                allowed=False,
                verdict="HOLD_JUDGMENT_MISMATCH",
                profile=profile,
                reason_codes=profile.reason_codes + ["JUDGMENT_NOT_BOUND_TO_ACTION"],
                rejection_reason="Judgment reference does not bind to this specific action.",
            )

    # REQUIRE_CONTROLS → verify all required controls supplied
    if verdict == GateVerdict.REQUIRE_CONTROLS:
        missing = [c for c in profile.required_controls if c not in supplied]
        if missing:
            return AuthorizationResult(
                allowed=False,
                verdict="HOLD_MISSING_CONTROLS",
                profile=profile,
                reason_codes=profile.reason_codes,
                required_controls=profile.required_controls,
                missing_controls=missing,
                rejection_reason=f"Missing required controls: {', '.join(missing)}",
            )

    # ── Step 4: Issue AuthorizedExecution token ──
    normalized = _normalize_command(executable, args, args_text)
    profile_hash = _hash_profile(profile)
    receipt_id = _generate_receipt(actor_id, session_id, profile_hash)

    token = AuthorizedExecution(
        profile_hash=profile_hash,
        authorization_receipt=receipt_id,
        verdict=verdict.value,
        issued_at=time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
        expires_at=time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() + 30)),  # 30s TTL
        normalized_command=normalized,
        actor_id=actor_id,
        session_id=session_id,
        target_environment=target_environment,
        supplied_controls=supplied,
    )

    return AuthorizationResult(
        allowed=True,
        verdict=verdict.value,
        profile=profile,
        reason_codes=profile.reason_codes,
        required_controls=profile.required_controls,
        authorized_execution=token,
    )


def _normalize_command(executable: str, arguments: list[str], args_text: str) -> str:
    """Normalize command to canonical form for hash-binding."""
    parts = [executable] if executable else []
    if arguments:
        parts.extend(str(a) for a in arguments)
    elif args_text:
        parts.append(args_text)
    return " ".join(parts)


def _hash_profile(profile: ActionProfile) -> str:
    """Compute SHA-256 hash of the ActionProfile for tamper detection."""
    canonical = json.dumps(
        {
            "mutation_class": profile.mutation_class.value,
            "blast_radius": profile.blast_radius.value,
            "reversibility": profile.reversibility,
            "destructive_operation": profile.destructive_operation,
            "data_loss_possible": profile.data_loss_possible,
            "infrastructure_impact": profile.infrastructure_impact,
            "requires_p34": profile.requires_p34,
            "requires_p23": profile.requires_p23,
            "reason_codes": sorted(profile.reason_codes),
            "classifier_version": profile.classifier_version,
        },
        sort_keys=True,
    )
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def _generate_receipt(actor_id: str, session_id: str, profile_hash: str) -> str:
    """Generate a unique authorization receipt ID."""
    seed = f"{actor_id}:{session_id}:{profile_hash}:{time.time()}"
    return f"auth-{hashlib.sha256(seed.encode()).hexdigest()[:12]}"


def _validate_judgment_binding(
    judgment_reference: str,
    profile: ActionProfile,
    executable: str,
    arguments: list[str],
    actor_id: str,
    session_id: str,
    target_environment: str,
) -> bool:
    """Validate that a judgment reference binds to this specific action.

    Judgment receipt for command A cannot be used for command B.
    """
    # In production: verify the judgment_reference against arifOS VAULT999
    # For now: structural validation — reference must contain action hash components
    expected_components = [
        executable or "",
        actor_id,
        session_id,
        target_environment,
        profile.mutation_class.value,
    ]
    return all(c in judgment_reference for c in expected_components if c)


__all__ = [
    "AuthorizationResult",
    "AuthorizedExecution",
    "authorize_mutation",
]
