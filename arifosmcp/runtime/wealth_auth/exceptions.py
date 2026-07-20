"""
Audit-4 structured error contract.

Every refusal returns the shape from /runtime/contracts/errors.schema.json.
Tool implementations catch these and emit the JSON body; they never construct
their own error shape.
"""

from __future__ import annotations

from typing import Any


def _error_envelope(
    code: str,
    message: str,
    *,
    required_action: str | None = None,
    requested_capability: str | None = None,
    retryable: bool = True,
    mutation_occurred: bool = False,
    trace_id: str | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "status": "HOLD" if retryable else "DENY",
        "error_code": code,
        "message": message,
        "retryable": retryable,
        "mutation_occurred": mutation_occurred,
    }
    if required_action is not None:
        out["required_action"] = required_action
    if requested_capability is not None:
        out["requested_capability"] = requested_capability
    if trace_id is not None:
        out["trace_id"] = trace_id
    if actor_id is not None:
        out["actor_id"] = actor_id
    if session_id is not None:
        out["session_id"] = session_id
    return out


class AuthError(Exception):
    """Base class. Tool code catches subclasses, not this one."""

    code: str = "INTERNAL_ERROR"
    retryable: bool = True

    def __init__(
        self,
        message: str,
        *,
        required_action: str | None = None,
        requested_capability: str | None = None,
        trace_id: str | None = None,
        actor_id: str | None = None,
        session_id: str | None = None,
        retryable: bool | None = None,
        mutation_occurred: bool = False,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.required_action = required_action
        self.requested_capability = requested_capability
        self.trace_id = trace_id
        self.actor_id = actor_id
        self.session_id = session_id
        self._retryable = retryable
        self.mutation_occurred = mutation_occurred

    def to_envelope(self) -> dict[str, Any]:
        return _error_envelope(
            self.code,
            self.message,
            required_action=self.required_action,
            requested_capability=self.requested_capability,
            trace_id=self.trace_id,
            actor_id=self.actor_id,
            session_id=self.session_id,
            retryable=self._retryable if self._retryable is not None else self.retryable,
            mutation_occurred=self.mutation_occurred,
        )


class SessionRequired(AuthError):
    code = "SESSION_REQUIRED"
    retryable = True


class TokenInvalid(AuthError):
    code = "TOKEN_INVALID"
    retryable = True


class TokenExpired(AuthError):
    code = "TOKEN_EXPIRED"
    retryable = True


class WrongAudience(AuthError):
    code = "WRONG_AUDIENCE"
    retryable = True


class CapabilityNotGranted(AuthError):
    code = "CAPABILITY_NOT_GRANTED"
    retryable = True


class ActorNotBound(AuthError):
    code = "ACTOR_NOT_BOUND"
    retryable = True


class ReplayDetected(AuthError):
    code = "REPLAY_DETECTED"
    retryable = False


class Revoked(AuthError):
    code = "REVOKED"
    retryable = False


class EvidenceInsufficient(AuthError):
    code = "EVIDENCE_INSUFFICIENT"
    retryable = True


class HumanRatificationRequired(AuthError):
    code = "HUMAN_RATIFICATION_REQUIRED"
    retryable = False
