"""
Consensus Layer — PBFT, Distributed Ledgers, CRDTs

Implements Byzantine fault tolerance and immutable state.
"""

import hashlib
import json
import time
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Proposal:
    """A proposal in the consensus protocol."""
    agent_id: str
    value: Dict
    signature: str
    digest: str
    timestamp: float = field(default_factory=time.time)
    sequence_number: int = 0


class ConsensusFailure(Exception):
    """Raised when consensus cannot be reached."""
    pass


class FederatedConsensus:
    """
    Practical Byzantine Fault Tolerance for agent federation.
    
    Tri-Witness = 3f+1 consensus where f=0 (no faults tolerated in strict mode)
    All three must agree (Human, AI, Earth).
    
    Constitutional Enforcement:
    - F1 Amanah: All actions require 3/3 witness votes
    - F3 Tri-Witness: PBFT quorum = Tri-Witness
    - F11 Command Auth: BLS signature verification
    """
    
    def __init__(self, witnesses: List[str], fault_tolerance: int = 0):
        """
        Args:
            witnesses: List of witness agent IDs
            fault_tolerance: Number of Byzantine faults tolerated (0 for strict)
        """
        self.witnesses = set(witnesses)
        self.fault_tolerance = fault_tolerance
        self.quorum_size = len(witnesses)  # 3/3 for strict mode
        
        # Consensus state
        self.sequence_number = 0
        self.prepared_proposals: Dict[int, List[Proposal]] = defaultdict(list)
        self.committed_values: Dict[int, Dict] = {}
    
    def create_proposal(self, agent_id: str, value: Dict, private_key: str) -> Proposal:
        """
        Create a signed proposal.
        
        Args:
            agent_id: Proposing agent
            value: Proposal content
            private_key: For signing (simplified)
            
        Returns:
            Signed proposal
        """
        # Serialize value
        content = json.dumps(value, sort_keys=True)
        digest = hashlib.sha256(content.encode()).hexdigest()
        
        # Sign (simplified: in production use proper BLS)
        signature = hashlib.sha256((digest + private_key).encode()).hexdigest()
        
        self.sequence_number += 1
        
        return Proposal(
            agent_id=agent_id,
            value=value,
            signature=signature,
            digest=digest,
            sequence_number=self.sequence_number
        )
    
    def verify_signature(self, proposal: Proposal, public_key: str) -> bool:
        """
        Verify proposal signature.
        
        In production: Use BLS signature verification.
        """
        expected_content = json.dumps(proposal.value, sort_keys=True)
        expected_digest = hashlib.sha256(expected_content.encode()).hexdigest()
        
        if proposal.digest != expected_digest:
            return False
        
        # Simplified verification
        expected_sig = hashlib.sha256((proposal.digest + public_key).encode()).hexdigest()
        return proposal.signature == expected_sig
    
    def pre_prepare(self, proposal: Proposal) -> bool:
        """
        Phase 1: Leader proposes value.
        
        Returns True if proposal accepted for preparation.
        """
        if proposal.agent_id not in self.witnesses:
            raise ConsensusFailure(f"Agent {proposal.agent_id} not authorized")
        
        return True
    
    def prepare(self, proposal: Proposal, public_keys: Dict[str, str]) -> bool:
        """
        Phase 2: Witnesses validate and prepare.
        
        Returns True if prepared (2f+1 acknowledgments).
        """
        if not self.verify_signature(proposal, public_keys.get(proposal.agent_id, "")):
            return False
        
        seq = proposal.sequence_number
        self.prepared_proposals[seq].append(proposal)
        
        # Check if we have quorum
        return len(self.prepared_proposals[seq]) >= self.quorum_size
    
    def commit(self, sequence_number: int) -> Dict:
        """
        Phase 3: Commit if all witnesses agree.
        
        Returns committed value with Merkle root.
        """
        proposals = self.prepared_proposals.get(sequence_number, [])
        
        if len(proposals) < self.quorum_size:
            raise ConsensusFailure(
                f"Insufficient witnesses: {len(proposals)}/{self.quorum_size}"
            )
        
        # Check all values match
        values = [p.value for p in proposals]
        if not all(v == values[0] for v in values):
            raise ConsensusFailure("Witnesses disagree on value")
        
        # Compute Merkle root
        merkle_root = self._compute_merkle_root(proposals)
        
        # Store committed value
        committed = {
            "value": values[0],
            "witnesses": [p.agent_id for p in proposals],
            "merkle_root": merkle_root,
            "sequence_number": sequence_number,
            "timestamp": time.time(),
            "tri_witness": len(proposals) / len(self.witnesses)
        }
        
        self.committed_values[sequence_number] = committed
        
        return committed
    
    def _compute_merkle_root(self, proposals: List[Proposal]) -> str:
        """
        Compute Merkle root from proposal digests.
        """
        leaves = sorted([p.digest for p in proposals])
        
        if not leaves:
            return ""
        
        # Build tree bottom-up
        current_level = leaves
        
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                combined = hashlib.sha256((left + right).encode()).hexdigest()
                next_level.append(combined)
            current_level = next_level
        
        return current_level[0]


class MerkleNode:
    """Node in Merkle DAG."""
    
    def __init__(self, cid: str, content: str, parents: List[str] = None):
        self.cid = cid  # Content identifier (hash)
        self.content = content
        self.parents = parents or []
        self.children: List[str] = []
        self.timestamp = time.time()


class FederatedLedger:
    """
    Distributed Merkle DAG for agent state consensus.
    
    CRDTs: Conflict-free Replicated Data Types
    Agent states merge without coordination.
    
    Constitutional Enforcement:
    - F1 Amanah: Immutable audit trail
    - F3 Tri-Witness: Signature verification
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.nodes: Dict[str, MerkleNode] = {}
        self.head: Optional[str] = None
        self.peers: Set[str] = set()
        
        # CRDT: Last-Write-Wins Register for state
        self.lww_register: Dict[str, tuple] = {}  # key -> (timestamp, value)
    
    def append(self, event: Dict, signatures: Dict[str, str] = None) -> str:
        """
        Append event to ledger.
        
        Content-addressed: hash = location (CID).
        
        Args:
            event: Event data
            signatures: {'human': sig, 'ai': sig, 'earth': sig}
            
        Returns:
            Content identifier (CID)
        """
        # Add metadata
        full_event = {
            **event,
            "agent_id": self.agent_id,
            "timestamp": time.time(),
            "parent": self.head,
            "signatures": signatures or {}
        }
        
        # Serialize and hash
        content = json.dumps(full_event, sort_keys=True)
        cid = hashlib.sha256(content.encode()).hexdigest()
        
        # Create node
        parents = [self.head] if self.head else []
        node = MerkleNode(cid=cid, content=content, parents=parents)
        
        # Update parent references
        if self.head and self.head in self.nodes:
            self.nodes[self.head].children.append(cid)
        
        # Store
        self.nodes[cid] = node
        self.head = cid
        
        # Update CRDT
        self.lww_register[cid] = (time.time(), full_event)
        
        return cid
    
    def get(self, cid: str) -> Optional[Dict]:
        """Retrieve event by CID."""
        node = self.nodes.get(cid)
        if node:
            return json.loads(node.content)
        return None
    
    def verify_tri_witness(self, cid: str) -> Dict:
        """
        Verify event has all three witness signatures.
        
        Human + AI + Earth must sign for reality instantiation.
        """
        event = self.get(cid)
        if not event:
            return {"valid": False, "error": "Event not found"}
        
        witnesses = event.get("signatures", {})
        required = ["human", "ai", "earth"]
        present = [w for w in required if w in witnesses]
        
        if len(present) < 3:
            return {
                "valid": False,
                "missing": list(set(required) - set(present)),
                "tri_witness": len(present) / 3
            }
        
        return {
            "valid": True,
            "tri_witness": 1.0,
            "signatures": witnesses
        }
    
    def get_chain(self, cid: str) -> List[str]:
        """
        Get ancestry chain from cid to genesis.
        """
        chain = []
        current = cid
        
        while current:
            chain.append(current)
            node = self.nodes.get(current)
            if node and node.parents:
                current = node.parents[0]  # Follow first parent
            else:
                break
        
        return chain
    
    def merge(self, other_ledger: 'FederatedLedger') -> 'FederatedLedger':
        """
        Merge two ledgers (CRDT convergence).
        
        Federation property: all agents eventually agree.
        """
        merged = FederatedLedger(f"{self.agent_id}+{other_ledger.agent_id}")
        
        # Merge nodes
        merged.nodes = {**self.nodes, **other_ledger.nodes}
        
        # CRDT merge: LWW semantics
        merged.lww_register = self.lww_register.copy()
        for key, (ts, val) in other_ledger.lww_register.items():
            if key not in merged.lww_register or merged.lww_register[key][0] < ts:
                merged.lww_register[key] = (ts, val)
        
        # Find common ancestor for head
        if self.head and other_ledger.head:
            # Simple: use lexicographically largest (deterministic)
            merged.head = max(self.head, other_ledger.head)
        else:
            merged.head = self.head or other_ledger.head
        
        return merged
    
    def compute_merkle_root(self) -> Optional[str]:
        """Compute Merkle root of current chain."""
        if not self.head:
            return None
        
        chain = self.get_chain(self.head)
        if not chain:
            return None
        
        # Build tree
        current_level = chain
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                combined = hashlib.sha256((left + right).encode()).hexdigest()
                next_level.append(combined)
            current_level = next_level
        
        return current_level[0]
