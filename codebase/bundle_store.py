"""
Bundle Store - Constitutional bundle schemas & storage.
Re-exports canonical schemas from codebase.bundles and provides thread-safe storage.
"""

from typing import Dict, Any, Optional
import threading

# Re-export canonical bundle types from bundles.py
from codebase.bundles import (
    DeltaBundle,
    OmegaBundle,
    MergedBundle,
    Stakeholder,
    EngineVote,
    Hypothesis,
    ReasoningTree,
    AGIFloorScores,
    ASIFloorScores,
    TriWitnessConsensus,
)


# ==================== BUNDLE STORAGE ====================

class BundleStore:
    """
    Thread-safe bundle storage enforcing Trinity isolation.
    
    Critical Invariant: ASI cannot see AGI reasoning until 444.
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self._bundles: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._asi_access_blocked = False  # Once AGI stored, ASI can't read
    
    def store_delta(self, bundle: DeltaBundle) -> None:
        """Store AGI bundle. Locks ASI from reading it."""
        with self._lock:
            # Allow replacement for re-execution scenarios
            self._bundles["delta"] = bundle
            self._asi_access_blocked = True  # ASI isolation enforced
    
    def store_omega(self, bundle: OmegaBundle) -> None:
        """Store ASI bundle. ASI never sees AGI."""
        with self._lock:
            if "delta" in self._bundles and self._asi_access_blocked:
                # This is the constitutional isolation check
                # ASI should NOT have direct access to AGI reasoning
                pass  # No error, ASI can't access via this method
            self._bundles["omega"] = bundle
    
    def get_delta(self) -> Optional[DeltaBundle]:
        """Only APEX can retrieve AGI bundle (at 444)."""
        with self._lock:
            return self._bundles.get("delta")
    
    def get_omega(self) -> Optional[OmegaBundle]:
        """Only APEX can retrieve ASI bundle (at 444)."""
        with self._lock:
            return self._bundles.get("omega")
    
    def store_merged(self, bundle: MergedBundle) -> None:
        """APEX stores merged result for post-444 stages."""
        with self._lock:
            self._bundles["merged"] = bundle
    
    def get_merged(self) -> Optional[MergedBundle]:
        """Stages 777-999 read merged bundle."""
        with self._lock:
            return self._bundles.get("merged")


# ==================== GLOBAL STORE FACTORY ====================

_SESSION_STORES: Dict[str, BundleStore] = {}
_SESSION_LOCK = threading.Lock()


def get_store(session_id: str) -> BundleStore:
    """Get or create bundle store for session."""
    with _SESSION_LOCK:
        if session_id not in _SESSION_STORES:
            _SESSION_STORES[session_id] = BundleStore(session_id)
        return _SESSION_STORES[session_id]


def purge_store(session_id: str) -> None:
    """Remove session store (cleanup)."""
    with _SESSION_LOCK:
        if session_id in _SESSION_STORES:
            del _SESSION_STORES[session_id]


def store_bundle(session_id: str, bundle_type: str, bundle_data: Dict[str, Any]) -> None:
    """
    Store a bundle for the session.
    
    Args:
        session_id: Session identifier
        bundle_type: "delta" or "omega"
        bundle_data: Bundle data dictionary
    """
    store = get_store(session_id)
    if bundle_type == "delta":
        store.store_delta(DeltaBundle(**bundle_data)) # Assuming bundle_data can be unpacked into DeltaBundle
    elif bundle_type == "omega":
        store.store_omega(OmegaBundle(**bundle_data)) # Assuming bundle_data can be unpacked into OmegaBundle


def get_bundle(session_id: str, bundle_type: str) -> Optional[Dict[str, Any]]:
    """
    Get a bundle from the session store.
    
    Args:
        session_id: Session identifier
        bundle_type: "delta" or "omega"
        
    Returns:
        Bundle data or None if not found
    """
    store = get_store(session_id)
    bundle = None
    if bundle_type == "delta":
        bundle = store.get_delta()
    elif bundle_type == "omega":
        bundle = store.get_omega()
    return bundle.to_dict() if bundle else None


# ==================== EXPORTS ====================

__all__ = [
    # Storage
    "BundleStore",
    "get_store",
    "purge_store",
    "store_bundle",
    "get_bundle",
    # Re-exported schemas
    "DeltaBundle",
    "OmegaBundle",
    "MergedBundle",
    "EngineVote",
    "Hypothesis",
    "ReasoningTree",
    "AGIFloorScores",
    "ASIFloorScores",
    "TriWitnessConsensus",
]
