"""
VAULT999 MCP Resources — vault:// URI handler for transparency log proofs.
══════════════════════════════════════════════════════════════════════════

Exposes Merkle tree artifacts as read-only MCP resources:
  vault://log/checkpoint/latest
  vault://entry/{leaf_index}
  vault://proof/inclusion/{leaf_index}@{tree_size}
  vault://proof/consistency/{old_size}-{new_size}
  vault://report/{report_id}/version/{version_id}
  vault://timeline/{incident_id}

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import json
from typing import Any

from .merkle_log import MerkleTree
from .state_machine import IncidentStore


class VaultResources:
    """MCP resource handler for VAULT999 transparency log."""

    def __init__(self, store: IncidentStore, merkle: MerkleTree) -> None:
        self.store = store
        self.merkle = merkle

    def list_resources(self) -> list[dict[str, Any]]:
        """Return all available resource URIs."""
        resources: list[dict[str, Any]] = []

        # Checkpoint
        resources.append(
            {
                "uri": "vault://log/checkpoint/latest",
                "name": "Latest checkpoint",
                "description": "Most recent signed tree head for VAULT999 Merkle log",
                "mimeType": "application/json",
            }
        )

        # Entries
        for i in range(self.merkle.tree_size):
            resources.append(
                {
                    "uri": f"vault://entry/{i}",
                    "name": f"Log entry {i}",
                    "description": f"VAULT999 Merkle log entry at leaf index {i}",
                    "mimeType": "application/json",
                }
            )

        # Inclusion proofs
        tree_size = self.merkle.tree_size
        for i in range(tree_size):
            resources.append(
                {
                    "uri": f"vault://proof/inclusion/{i}@{tree_size}",
                    "name": f"Inclusion proof for leaf {i}",
                    "description": f"RFC 9162 inclusion proof for leaf {i} at tree size {tree_size}",
                    "mimeType": "application/json",
                }
            )

        # Consistency proof
        if tree_size > 1:
            resources.append(
                {
                    "uri": f"vault://proof/consistency/{tree_size - 1}-{tree_size}",
                    "name": f"Consistency proof {tree_size - 1}→{tree_size}",
                    "description": f"RFC 9162 consistency proof from size {tree_size - 1} to {tree_size}",
                    "mimeType": "application/json",
                }
            )

        # Report versions
        for incident in self.store.list_all():
            for version in incident.versions:
                resources.append(
                    {
                        "uri": f"vault://report/{incident.incident_id}/version/{version.version_id}",
                        "name": f"Report {version.version_id}",
                        "description": f"Sealed report version for {incident.title}",
                        "mimeType": "application/json",
                    }
                )

        # Timelines
        for incident in self.store.list_all():
            resources.append(
                {
                    "uri": f"vault://timeline/{incident.incident_id}",
                    "name": f"Timeline: {incident.title}",
                    "description": f"State transition timeline for {incident.incident_id}",
                    "mimeType": "application/json",
                }
            )

        return resources

    def read_resource(self, uri: str) -> dict[str, Any] | None:
        """Read a specific resource by URI. Returns None if not found."""
        # ── Checkpoints ──
        if uri == "vault://log/checkpoint/latest":
            cp = self.merkle.checkpoint()
            return {
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps(cp, indent=2),
            }

        # ── Entries ──
        if uri.startswith("vault://entry/"):
            try:
                leaf_index = int(uri.split("/")[-1])
            except (ValueError, IndexError):
                return None
            if leaf_index < 0 or leaf_index >= self.merkle.tree_size:
                return None
            leaf_hex = self.merkle.leaves[leaf_index].hex()
            return {
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps(
                    {
                        "leaf_index": leaf_index,
                        "leaf_hash": leaf_hex,
                        "tree_size": self.merkle.tree_size,
                    },
                    indent=2,
                ),
            }

        # ── Inclusion proofs ──
        if uri.startswith("vault://proof/inclusion/"):
            rest = uri.replace("vault://proof/inclusion/", "")
            try:
                parts = rest.split("@")
                leaf_index = int(parts[0])
                tree_size = int(parts[1]) if len(parts) > 1 else self.merkle.tree_size
            except (ValueError, IndexError):
                return None
            proof = self.merkle.inclusion_proof(leaf_index)
            if proof is None:
                return None
            return {
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps(proof, indent=2),
            }

        # ── Consistency proofs ──
        if uri.startswith("vault://proof/consistency/"):
            rest = uri.replace("vault://proof/consistency/", "")
            try:
                parts = rest.split("-")
                old_size = int(parts[0])
                new_size = int(parts[1]) if len(parts) > 1 else self.merkle.tree_size
            except (ValueError, IndexError):
                return None
            proof = self.merkle.consistency_proof(old_size, new_size)
            if proof is None:
                return None
            return {
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps(proof, indent=2),
            }

        # ── Report versions ──
        if uri.startswith("vault://report/"):
            rest = uri.replace("vault://report/", "")
            parts = rest.split("/version/")
            if len(parts) != 2:
                return None
            incident_id, version_id = parts
            incident = self.store.get(incident_id)
            if not incident:
                return None
            for v in incident.versions:
                if v.version_id == version_id:
                    return {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(v.to_dict(), indent=2),
                    }
            return None

        # ── Timelines ──
        if uri.startswith("vault://timeline/"):
            incident_id = uri.replace("vault://timeline/", "")
            incident = self.store.get(incident_id)
            if not incident:
                return None
            return {
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps(incident.to_dict(), indent=2),
            }

        return None
