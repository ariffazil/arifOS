"""
Bridge: Binding arifOS.memory to arifOS.vault

Promotion rule:
- Memory is for use (mutable, revisable)
- Vault is for proof (immutable, judgment)
- Only consequential records get promoted

Promotion triggers:
- Creates/changes policy
- Affects trust, authority, safety
- Records human sovereign decision
- Closes consequential architecture
- Documents refusal/hold with governance impact
"""

from .promotion import PromotionBridge, PromotionCandidate

__all__ = ["PromotionBridge", "PromotionCandidate"]
