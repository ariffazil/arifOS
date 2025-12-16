"""Runtime bootstrap for v42.1 spec binding."""

from __future__ import annotations

import logging
from typing import Dict, Any

from arifos_core.validators.spec_checker import validate_spec_binding, SpecValidationError

logger = logging.getLogger(__name__)

_BOOTSTRAP_PAYLOAD: Dict[str, Any] | None = None


class BootstrapError(RuntimeError):
    """Raised when runtime bootstrap fails."""


def ensure_bootstrap() -> Dict[str, Any]:
    """Validate spec binding once and cache the payload."""
    global _BOOTSTRAP_PAYLOAD
    if _BOOTSTRAP_PAYLOAD is not None:
        return _BOOTSTRAP_PAYLOAD
    try:
        payload = validate_spec_binding()
        _BOOTSTRAP_PAYLOAD = payload
        logger.info("Spec binding validated: %s", list(payload.get("spec_hashes", {}).keys()))
        return payload
    except SpecValidationError as exc:  # noqa: BLE001
        logger.error("Spec binding validation failed: %s", exc)
        raise BootstrapError(str(exc)) from exc


def get_bootstrap_payload() -> Dict[str, Any]:
    """Return cached bootstrap payload if available."""
    if _BOOTSTRAP_PAYLOAD is None:
        return {}
    return _BOOTSTRAP_PAYLOAD


__all__ = ["ensure_bootstrap", "get_bootstrap_payload", "BootstrapError"]
