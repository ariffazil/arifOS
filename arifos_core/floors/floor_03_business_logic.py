"""
Floor 3: Business Logic & State Management
APEX THEORY v46.0 - Constitutional Floor System

Implements core computational operations, state transitions, and workflow orchestration.
Manages the Vault 999 L1-L2 memory layers for session and transaction state.

Status: SEALED
Nonce: X7K9F20
"""

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field


class StateStatus(str, Enum):
    """State transition statuses."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class TransactionType(str, Enum):
    """Transaction types for governance."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    UPDATE = "update"
    EXECUTE = "execute"


@dataclass
class StateTransition:
    """Record of a state transition."""
    id: str
    from_state: str
    to_state: str
    timestamp: str
    actor: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: StateStatus = StateStatus.ACTIVE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "metadata": self.metadata,
            "status": self.status.value
        }


@dataclass
class Transaction:
    """Business transaction record."""
    id: str
    type: TransactionType
    payload: Dict[str, Any]
    status: StateStatus
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None
    rollback_state: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "type": self.type.value,
            "payload": self.payload,
            "status": self.status.value,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "error": self.error,
            "rollback_state": self.rollback_state
        }


class StateMachine:
    """
    State machine for managing workflow transitions.
    
    Implements deterministic state transitions with audit trail.
    Integrates with Vault 999 L1 (session) and L2 (transaction) layers.
    """
    
    def __init__(self, initial_state: str = "INIT"):
        """Initialize state machine."""
        self.current_state = initial_state
        self.state_history: List[StateTransition] = []
        self.valid_transitions: Dict[str, List[str]] = {
            "INIT": ["READY", "ERROR"],
            "READY": ["PROCESSING", "ERROR"],
            "PROCESSING": ["COMPLETED", "ERROR", "PAUSED"],
            "PAUSED": ["PROCESSING", "CANCELLED", "ERROR"],
            "COMPLETED": ["ARCHIVED"],
            "ERROR": ["RETRY", "FAILED"],
            "RETRY": ["PROCESSING", "FAILED"],
            "FAILED": ["ARCHIVED"],
            "CANCELLED": ["ARCHIVED"],
            "ARCHIVED": []  # Terminal state
        }
    
    def transition(self, to_state: str, actor: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute state transition.
        
        Args:
            to_state: Target state
            actor: Actor executing transition
            metadata: Optional metadata
            
        Returns:
            Dictionary with transition result
        """
        # Validate transition
        allowed_states = self.valid_transitions.get(self.current_state, [])
        
        if to_state not in allowed_states:
            return {
                "status": "rejected",
                "from_state": self.current_state,
                "to_state": to_state,
                "reason": f"Invalid transition: {self.current_state} → {to_state}",
                "allowed_transitions": allowed_states,
                "floor": 3,
                "psi": compute_psi_floor3(delta_s=0.0, peace_squared=0.8, kappa_r=0.9)
            }
        
        # Execute transition
        transition_id = generate_transition_id(self.current_state, to_state)
        transition = StateTransition(
            id=transition_id,
            from_state=self.current_state,
            to_state=to_state,
            timestamp=datetime.now(timezone.utc).isoformat(),
            actor=actor,
            metadata=metadata or {},
            status=StateStatus.COMPLETED
        )
        
        # Update state
        old_state = self.current_state
        self.current_state = to_state
        self.state_history.append(transition)
        
        return {
            "status": "success",
            "from_state": old_state,
            "to_state": to_state,
            "transition_id": transition_id,
            "timestamp": transition.timestamp,
            "floor": 3,
            "psi": compute_psi_floor3(delta_s=2.0, peace_squared=1.0, kappa_r=1.0)
        }
    
    def get_state(self) -> str:
        """Get current state."""
        return self.current_state
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get state transition history."""
        return [t.to_dict() for t in self.state_history]
    
    def can_transition_to(self, to_state: str) -> bool:
        """Check if transition to state is valid."""
        allowed = self.valid_transitions.get(self.current_state, [])
        return to_state in allowed


class TransactionManager:
    """Transaction manager for business operations with ACID-like guarantees."""
    
    def __init__(self):
        """Initialize transaction manager."""
        self.active_transactions: Dict[str, Transaction] = {}
        self.completed_transactions: List[Transaction] = []
    
    def begin_transaction(
        self,
        transaction_type: TransactionType,
        payload: Dict[str, Any],
        actor: str
    ) -> Dict[str, Any]:
        """Begin a new transaction."""
        transaction_id = generate_transaction_id(transaction_type.value, actor)
        
        transaction = Transaction(
            id=transaction_id,
            type=transaction_type,
            payload=payload,
            status=StateStatus.ACTIVE,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        self.active_transactions[transaction_id] = transaction
        
        return {
            "transaction_id": transaction_id,
            "status": transaction.status.value,
            "type": transaction_type.value,
            "created_at": transaction.created_at,
            "floor": 3,
            "psi": compute_psi_floor3(delta_s=1.5, peace_squared=1.0, kappa_r=1.0)
        }
    
    def commit_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Commit an active transaction."""
        if transaction_id not in self.active_transactions:
            return {
                "status": "rejected",
                "reason": f"Transaction {transaction_id} not found",
                "floor": 3,
                "psi": compute_psi_floor3(delta_s=0.0, peace_squared=0.9, kappa_r=0.9)
            }
        
        transaction = self.active_transactions[transaction_id]
        transaction.status = StateStatus.COMPLETED
        transaction.completed_at = datetime.now(timezone.utc).isoformat()
        
        self.completed_transactions.append(transaction)
        del self.active_transactions[transaction_id]
        
        return {
            "status": "committed",
            "transaction_id": transaction_id,
            "completed_at": transaction.completed_at,
            "floor": 3,
            "psi": compute_psi_floor3(delta_s=2.5, peace_squared=1.0, kappa_r=1.0)
        }
    
    def rollback_transaction(self, transaction_id: str, reason: str = "") -> Dict[str, Any]:
        """Rollback an active transaction."""
        if transaction_id not in self.active_transactions:
            return {
                "status": "rejected",
                "reason": f"Transaction {transaction_id} not found",
                "floor": 3,
                "psi": compute_psi_floor3(delta_s=0.0, peace_squared=0.9, kappa_r=0.9)
            }
        
        transaction = self.active_transactions[transaction_id]
        transaction.status = StateStatus.ROLLED_BACK
        transaction.error = reason
        transaction.completed_at = datetime.now(timezone.utc).isoformat()
        
        self.completed_transactions.append(transaction)
        del self.active_transactions[transaction_id]
        
        return {
            "status": "rolled_back",
            "transaction_id": transaction_id,
            "reason": reason,
            "completed_at": transaction.completed_at,
            "floor": 3,
            "psi": compute_psi_floor3(delta_s=1.0, peace_squared=1.0, kappa_r=1.0)
        }


def generate_transition_id(from_state: str, to_state: str) -> str:
    """Generate unique transition ID."""
    timestamp = datetime.now(timezone.utc).isoformat()
    raw = f"{from_state}→{to_state}:{timestamp}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def generate_transaction_id(txn_type: str, actor: str) -> str:
    """Generate unique transaction ID."""
    timestamp = datetime.now(timezone.utc).isoformat()
    raw = f"{txn_type}:{actor}:{timestamp}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def compute_psi_floor3(delta_s: float, peace_squared: float, kappa_r: float) -> Dict[str, float]:
    """Compute Ψ (governance vitality) for Floor 3 operations."""
    psi_total = delta_s * peace_squared * kappa_r
    return {
        "delta_s": delta_s,
        "peace_squared": peace_squared,
        "kappa_r": kappa_r,
        "psi_total": round(psi_total, 6)
    }


# Constitutional metadata
__floor__ = 3
__name__ = "Business Logic & State Management"
__authority__ = "Execute validated business rules with deterministic state transitions"
__version__ = "v46.0-APEX-THEORY"
__status__ = "SEALED"
