"""
Compatibility Layer — Backend Version Routing

Routes canonical tool calls to v1 or v2 backends based on env flags.
"""

from .memory_backend import MemoryBackend
from .promotion_backend import PromotionBackend
from .vault_backend import VaultBackend

__all__ = ["MemoryBackend", "VaultBackend", "PromotionBackend"]
