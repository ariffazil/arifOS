"""
codebase/vault/phoenix/__init__.py — Phoenix-72 Cooling System (v52.5.1-SEAL)

Truth stabilization through time-based cooling layers:
- L0: Hot (0h) - Active session
- L1: Warm (24h) - Daily cooling
- L2: Phoenix (72h) - Truth stabilization
- L3: Cool (7d) - Weekly reflection
- L4: Cold (30d) - Monthly canon
- L5: Frozen (365d+) - Constitutional law
"""

from codebase.vault.phoenix.phoenix72 import Phoenix72
from codebase.vault.phoenix.phoenix72_controller import Phoenix72Controller

__all__ = [
    "Phoenix72",
    "Phoenix72Controller",
]
