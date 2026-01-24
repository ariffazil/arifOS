"""
Authority Model for arifOS–MCP Cognition
==========================================

An "Authority" is a binding of:
  - Agent/User Identity (△)
  - Scope (which Floors they can exercise)
  - Cost Budget (tokens, latency, compute)
  - Tri-Witness Requirement (how many F3 observers needed)

Authority is NOT permission. Permission is negative (you CAN'T).
Authority is positive (you MUST, and we MEASURE).

DITEMPA BUKAN DIBERI - Forged v50.4
"""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set


class AuthorityLevel(Enum):
    """Degrees of authority in constitutional cognition."""
    SANDBOX = 0      # Only F7 (Humility) + F9 (Anti-Hantu); no state change
    OBSERVER = 1     # F2 (Truth) + F4 (Clarity); read-only, high observability
    AGENT = 2        # F5 (Peace) + F1 (Amanah); can modify state, logged
    SOVEREIGN = 3    # F6 (Ijma) + F11 (Auth); can authorize other actors, costs recorded
    ARBITER = 4      # F10 (Ontology) + all Floors; meta-level policy changes (rare)
    EXTRA_SOVEREIGN = 99  # HUMAN_SOVEREIGN_VETO: Outside all formal floors; Can override any SEAL/VOID.

@dataclass
class Authority:
    """
    A Constitutional Authority Covenant.

    Attributes:
        agent_id (str): Δ identity (user/model/system).
        level (AuthorityLevel): Which Floors can this agent exercise?
        scope_floors: Set[str] Explicit Floor set. E.g., {"F1", "F2", "F5"}.
        cost_budget: Dict {"tokens": 10000, "latency_ms": 5000, "vault_ops": 100}
        tri_witness_threshold (int): How many F3 observers needed before exec?
        issued_by (str): Who/what authorized this? (e.g., "arif@seri-kembangan", "genesis")
        issued_at (str): ISO8601 timestamp.
        expires_at (str): ISO8601; None if eternal.
        covenant_hash (str): Merkle-signed proof of this authority.
    """
    agent_id: str
    level: AuthorityLevel
    scope_floors: Set[str]
    cost_budget: Dict
    tri_witness_threshold: int
    issued_by: str
    issued_at: str
    expires_at: Optional[str] = None
    covenant_hash: Optional[str] = None

    def sign(self) -> str:
        """Produce immutable Merkle proof of this authority covenant."""
        payload = {
            "agent_id": self.agent_id,
            "level": self.level.name,
            "scope_floors": sorted(list(self.scope_floors)),
            "cost_budget": self.cost_budget,
            "tri_witness_threshold": self.tri_witness_threshold,
            "issued_by": self.issued_by,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
        }
        # Use simple json dump with sort_keys for consistent hashing
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        self.covenant_hash = hashlib.sha256(payload_json.encode()).hexdigest()
        return self.covenant_hash

    def can_invoke_tool(self, tool_name: str, required_floor: str) -> bool:
        """Check if this authority can invoke a tool requiring a specific Floor."""
        # Simple floor check
        if required_floor not in self.scope_floors:
            return False

        # Level check (heuristic map of floor -> level)
        # F7, F9 -> SANDBOX (0)
        # F2, F4 -> OBSERVER (1)
        # F1, F5 -> AGENT (2)
        # F6, F11 -> SOVEREIGN (3)
        # F10 -> ARBITER (4)

        needed_level_val = 0
        if required_floor in ["F6", "F11"]:
            needed_level_val = 3
        elif required_floor in ["F1", "F5"]:
            needed_level_val = 2
        elif required_floor in ["F2", "F4"]:
            needed_level_val = 1

        return self.level.value >= needed_level_val

    def can_afford(self, cost: Dict) -> bool:
        """Check if this authority's budget can afford an action."""
        for key, value in cost.items():
            if key in self.cost_budget and value > self.cost_budget[key]:
                return False
        return True

class AuthorityRegistry:
    """
    Immutable registry of all authorities issued in this arifOS instance.
    Backed by Vault (write-once).
    """
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.authorities: Dict[str, Authority] = {}

    def register(self, authority: Authority) -> str:
        """
        Issue a new authority. Returns the covenant_hash.
        This operation is irreversible and logged to Vault.
        """
        authority.sign()

        # In-memory dedupe check
        if authority.covenant_hash in self.authorities:
             return authority.covenant_hash

        self.authorities[authority.covenant_hash] = authority

        # Persist to Vault (F1 Amanah: immutable record)
        self._write_to_vault(authority)

        return authority.covenant_hash

    def _write_to_vault(self, authority: Authority):
        """Write authority to vault_path/authorities/{covenant_hash}.json"""
        import os
        auth_dir = os.path.join(self.vault_path, "authorities")
        os.makedirs(auth_dir, exist_ok=True)

        file_path = os.path.join(auth_dir, f"{authority.covenant_hash}.json")

        # Skip if exists (Immutable)
        if os.path.exists(file_path):
            return

        with open(file_path, "w") as f:
            json.dump({
                "agent_id": authority.agent_id,
                "level": authority.level.name,
                "scope_floors": sorted(list(authority.scope_floors)),
                "cost_budget": authority.cost_budget,
                "tri_witness_threshold": authority.tri_witness_threshold,
                "issued_by": authority.issued_by,
                "issued_at": authority.issued_at,
                "expires_at": authority.expires_at,
                "covenant_hash": authority.covenant_hash,
            }, f, indent=2)

    def lookup(self, agent_id: str) -> Authority:
        """Retrieve the current active authority for an agent."""
        # Search backwards through history; return most recent valid one
        # Note: In a real system with many authorities, this would be indexed map {agent_id: [auths]}
        # For v1 with small scale, linear scan of cache is acceptable

        candidates = [a for a in self.authorities.values() if a.agent_id == agent_id]
        if not candidates:
             raise ValueError(f"No active authority found for {agent_id}")

        # Sort by issue date descending
        candidates.sort(key=lambda a: a.issued_at, reverse=True)

        now = datetime.now().isoformat()

        for auth in candidates:
             if auth.expires_at is None or auth.expires_at > now:
                 return auth

        raise ValueError(f"No active non-expired authority found for {agent_id}")
