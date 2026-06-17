"""
arifosmcp/runtime/lease.py — REMOVED by ADR-001 (2026-06-16)

The legacy P2-7 lease shim has been deleted. All lease state now lives in the
canonical registry:

    from arifosmcp.runtime.lease_registry import (
        LeaseRecord,
        issue_lease,
        revoke_lease,
        get_lease,
        list_active_leases,
        validate_lease_for_tool,
        present_lease,
        arif_lease_issue,
        arif_lease_inspect,
        arif_lease_revoke,
    )

Importing from this module will raise ImportError to prevent accidental use
of the deprecated API. This file is intentionally minimal and will be removed
from the repository in a future cleanup pass.
"""

raise ImportError(
    "arifosmcp.runtime.lease has been removed. "
    "Use arifosmcp.runtime.lease_registry for all lease operations."
)
