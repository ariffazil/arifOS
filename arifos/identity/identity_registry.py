"""
identity_registry.py — Agent Identity Registry
════════════════════════════════════════════════

Maps agent_id → pubkey for all federation agents.
Loaded from agent-card.json files + identity.json files.
Provides lookup, registration, and verification functions.

Forged: 2026-07-29 — DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from .agent_identity import AgentIdentity

logger = logging.getLogger(__name__)

# Canonical agent directories
AGENTS_DIR = Path("/root/AAA/agents")
IDENTITY_DIR = Path("/root/arifOS/arifos/identity")


class IdentityRegistry:
    """Federation-wide agent identity registry.

    Maps agent_id to public key for signature verification.
    Loaded from agent identity files at startup.
    """

    def __init__(self, agents_dir: str | Path | None = None):
        self._agents_dir = Path(agents_dir or AGENTS_DIR)
        self._registry: dict[str, dict[str, Any]] = {}
        self._loaded = False

    # ── Load ────────────────────────────────────────────────────────────

    def load(self) -> "IdentityRegistry":
        """Load all agent identities from disk."""
        self._registry.clear()

        # Load from identity.json files in agents directories
        for agent_dir in self._agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue

            identity_file = agent_dir / "identity.json"
            if identity_file.exists():
                try:
                    with open(identity_file) as f:
                        data = json.load(f)
                    agent_id = data.get("agent_id", agent_dir.name)
                    self._registry[agent_id] = {
                        "agent_id": agent_id,
                        "actor_id": data.get("actor_id", f"{agent_id}/FI-???"),
                        "pubkey_hex": data.get("ed25519_pubkey_hex", ""),
                        "fingerprint": data.get("fingerprint", ""),
                        "capabilities": data.get("capabilities", []),
                        "max_blast_radius": data.get("max_blast_radius", "T2"),
                        "bound_to": data.get("bound_to", "arif-fazil/F13"),
                        "created_at": data.get("created_at", ""),
                    }
                    logger.info(f"Loaded identity: {agent_id}")
                except Exception as e:
                    logger.warning(f"Failed to load identity for {agent_dir.name}: {e}")

        # Also check legacy agent-card.json for agents without identity.json
        for agent_dir in self._agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            agent_id = agent_dir.name
            if agent_id not in self._registry:
                card_file = agent_dir / "agent-card.json"
                if card_file.exists():
                    try:
                        with open(card_file) as f:
                            card = json.load(f)
                        # Card has no pubkey — register without crypto identity
                        self._registry[agent_id] = {
                            "agent_id": agent_id,
                            "actor_id": card.get("id", agent_id),
                            "pubkey_hex": "",  # No key yet
                            "fingerprint": "",
                            "capabilities": card.get("capabilities", {}).get("actions", []),
                            "max_blast_radius": "T1",  # Conservative default
                            "bound_to": "arif-fazil/F13",
                            "created_at": card.get("metadata", {}).get("created", ""),
                            "needs_keygen": True,
                        }
                        logger.warning(f"Agent {agent_id} has no identity.json — needs keygen")
                    except Exception as e:
                        logger.warning(f"Failed to parse card for {agent_id}: {e}")

        self._loaded = True
        logger.info(f"IdentityRegistry loaded: {len(self._registry)} agents")
        return self

    # ── Query ────────────────────────────────────────────────────────────

    def lookup(self, agent_id: str) -> dict[str, Any] | None:
        """Look up an agent by ID. Returns registry entry or None."""
        if not self._loaded:
            self.load()
        return self._registry.get(agent_id)

    def get_pubkey(self, agent_id: str) -> str:
        """Get public key hex for an agent. Returns empty string if not found."""
        entry = self.lookup(agent_id)
        return entry["pubkey_hex"] if entry else ""

    def verify_agent_signature(
        self, agent_id: str, message: bytes | str, signature_hex: str
    ) -> bool:
        """Verify that a message was signed by a specific agent."""
        pubkey_hex = self.get_pubkey(agent_id)
        if not pubkey_hex:
            logger.warning(f"No pubkey for agent '{agent_id}' — cannot verify")
            return False
        return AgentIdentity.verify_signature(pubkey_hex, message, signature_hex)

    def has_key(self, agent_id: str) -> bool:
        """Check if an agent has a registered public key."""
        entry = self.lookup(agent_id)
        return bool(entry and entry.get("pubkey_hex"))

    def needs_keygen(self) -> list[str]:
        """List agent IDs that need Ed25519 key generation."""
        if not self._loaded:
            self.load()
        return [aid for aid, entry in self._registry.items() if entry.get("needs_keygen")]

    # ── Mutation ────────────────────────────────────────────────────────

    def register(self, identity: AgentIdentity) -> None:
        """Register or update an agent identity."""
        self._registry[identity.agent_id] = identity.to_registry_entry()
        logger.info(f"Registered: {identity.agent_id} ({identity.ed25519_pubkey_hex[:16]}…)")

    def register_from_dict(self, entry: dict[str, Any]) -> None:
        """Register from a raw dictionary."""
        agent_id = entry["agent_id"]
        self._registry[agent_id] = entry
        logger.info(f"Registered from dict: {agent_id}")

    # ── Export ──────────────────────────────────────────────────────────

    def to_verified_key_ids(self) -> dict[str, str]:
        """Export as VERIFIED_KEY_IDS format for governance_identity.py."""
        result: dict[str, str] = {}
        for agent_id, entry in self._registry.items():
            pubkey = entry.get("pubkey_hex", "")
            if pubkey:
                key_id = f"ed25519:sha256:{pubkey[:16]}"
                result[key_id] = agent_id
        return result

    def to_dict(self) -> dict[str, Any]:
        """Full registry as dictionary."""
        return {
            "version": "1.0.0",
            "agent_count": len(self._registry),
            "agents": self._registry,
        }

    def save_registry(self, path: str | Path | None = None) -> Path:
        """Persist registry to disk."""
        if path is None:
            path = IDENTITY_DIR / "agent_registry.json"
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Registry saved: {path} ({len(self._registry)} agents)")
        return path

    def __len__(self) -> int:
        return len(self._registry)

    def __contains__(self, agent_id: str) -> bool:
        return agent_id in self._registry

    def __repr__(self) -> str:
        return f"IdentityRegistry({len(self._registry)} agents)"
