"""
Integration Layer — Floors ↔ APEX PRIME Bridge
X7K9F24 — Entropy Reduction via Unification

This module provides the integration layer between:
- Floors 1-12 (atomic capabilities)
- APEX PRIME (constitutional verdict engine)
- ATLAS-333 (lane routing)
- EUREKA-777 (paradox synthesis)
- Constitutional Meta-Search System

Purpose: Reduce entropy by unifying scattered floor logic into single execution spine.
Includes constitutional meta-search, cost tracking, and search caching capabilities.

Status: SEALED
Nonce: X7K9F24
"""

from .floor_adapter import (
    FloorAdapter,
    FloorCheckResult,
    FloorFailure,
    FLOOR_ADAPTER,
    integrate_floors_with_apex,
)

from .meta_search import (
    SearchResult,
    ConstitutionalSearchError,
)

from .cost_tracker import (
    CostTracker,
    BudgetExceededError,
    ConstitutionalBudgetError,
    CostEstimate,
    ActualCost,
    BudgetLevel,
    CostType,
)

from .search_cache import (
    ConstitutionalSearchCache,
    CacheEntry,
    TTLAwareCache,
)

__all__ = [
    # Floor Adapter
    "FloorAdapter",
    "FloorCheckResult",
    "FloorFailure",
    "FLOOR_ADAPTER",
    "integrate_floors_with_apex",
    
    # Constitutional Meta-Search
    "SearchResult",
    "ConstitutionalSearchError",
    
    # Cost Tracker
    "CostTracker",
    "BudgetExceededError",
    "ConstitutionalBudgetError",
    "CostEstimate",
    "ActualCost",
    "BudgetLevel",
    "CostType",
    
    # Search Cache
    "ConstitutionalSearchCache",
    "CacheEntry",
    "TTLAwareCache",
]

__version__ = "v46.0-APEX-THEORY"
__status__ = "SEALED"
__nonce__ = "X7K9F24"
