"""REST routes package — moved from runtime/rest_routes.py on 2026-05-04."""

from arifosmcp.runtime.rest_routes.rest_routes import (
    _build_governance_status_payload,
    register_rest_routes,
)

__all__ = ["_build_governance_status_payload", "register_rest_routes"]
