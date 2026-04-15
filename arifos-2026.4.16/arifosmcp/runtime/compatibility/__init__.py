"""
Compatibility Layer — Backend Version Routing

Routes canonical tool calls to v1 or v2 backends based on env flags.
"""

from .memory_backend import MemoryBackend
from .vault_backend import VaultBackend
from .promotion_backend import PromotionBackend

__all__ = ["MemoryBackend", "VaultBackend", "PromotionBackend"]
