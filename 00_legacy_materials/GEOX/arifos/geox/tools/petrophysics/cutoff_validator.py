"""
Cutoff Validator — Stub for Phase B
DITEMPA BUKAN DIBERI

Full implementation in Phase B: geox_validate_cutoffs tool.
"""

from arifos.geox.schemas.petrophysics.cutoffs import CutoffPolicy

# In-memory store
_policy_store: dict[str, CutoffPolicy] = {}


async def load_cutoff_policy(policy_id: str) -> CutoffPolicy | None:
    """Load cutoff policy."""
    return _policy_store.get(policy_id)


async def store_cutoff_policy(policy: CutoffPolicy) -> None:
    """Store cutoff policy."""
    _policy_store[policy.policy_id] = policy


class CutoffValidator:
    """Stub for Phase B implementation."""

    def __init__(self, state, policy):
        self.state = state
        self.policy = policy

    async def apply(self):
        """Placeholder for cutoff validation."""
        raise NotImplementedError("Phase B: Cutoff validation")
