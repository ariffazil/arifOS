"""
CONSTITUTIONAL STATE MANAGEMENT

SessionState persists across metabolic stages (000→999).
The only source of truth for session-level data.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime, timezone


class SessionStore:
    """In-memory session store (L0 hot storage)."""

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize in-memory store."""
        self._memory: Dict[str, "SessionState"] = {}

    def get(self, session_id: str) -> Optional["SessionState"]:
        """Retrieve session state."""
        return self._memory.get(session_id)

    def put(self, state: "SessionState", persist: bool = False) -> None:
        """Store session state in memory."""
        self._memory[state.session_id] = state

    def delete(self, session_id: str) -> None:
        """Remove session from memory."""
        self._memory.pop(session_id, None)


@dataclass
class SessionState:
    """
    Immutable session state container for constitutional metabolism.

    Each stage returns a NEW instance (immutable update pattern).
    """

    session_id: str
    current_stage: int = 0  # 000-999
    delta_bundle: Optional[Dict[str, Any]] = None  # AGI output
    omega_bundle: Optional[Dict[str, Any]] = None  # ASI output
    floor_scores: Dict[str, float] = field(default_factory=dict)
    merkle_root: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_stage(self, stage: int) -> "SessionState":
        """Transition to new stage (returns new immutable instance)."""
        return SessionState(
            session_id=self.session_id,
            current_stage=stage,
            delta_bundle=self.delta_bundle,
            omega_bundle=self.omega_bundle,
            floor_scores=self.floor_scores.copy(),
            merkle_root=self.merkle_root,
            created_at=self.created_at,
            last_updated=datetime.now(timezone.utc),
        )

    def set_floor_score(self, floor_id: str, score: float) -> "SessionState":
        """Set constitutional floor score (returns new instance)."""
        new_scores = self.floor_scores.copy()
        new_scores[floor_id] = score

        return SessionState(
            session_id=self.session_id,
            current_stage=self.current_stage,
            delta_bundle=self.delta_bundle,
            omega_bundle=self.omega_bundle,
            floor_scores=new_scores,
            merkle_root=self.merkle_root,
            created_at=self.created_at,
            last_updated=datetime.now(timezone.utc),
        )

    def store_delta(self, data: Dict[str, Any]) -> "SessionState":
        """Store AGI reasoning bundle (returns new instance)."""
        return SessionState(
            session_id=self.session_id,
            current_stage=self.current_stage,
            delta_bundle=data,
            omega_bundle=self.omega_bundle,
            floor_scores=self.floor_scores.copy(),
            merkle_root=self.merkle_root,
            created_at=self.created_at,
            last_updated=datetime.now(timezone.utc),
        )

    def store_omega(self, data: Dict[str, Any]) -> "SessionState":
        """Store ASI safety bundle (returns new instance)."""
        return SessionState(
            session_id=self.session_id,
            current_stage=self.current_stage,
            delta_bundle=self.delta_bundle,
            omega_bundle=data,
            floor_scores=self.floor_scores.copy(),
            merkle_root=self.merkle_root,
            created_at=self.created_at,
            last_updated=datetime.now(timezone.utc),
        )
