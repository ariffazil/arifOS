"""
vault999.py — VAULT-999 constitutional memory organ (L0) for arifOS v35Ω.

Responsibilities:
- Load and expose constitution (laws, floors, physics)
- Provide read-only access to floors and laws at runtime
- Coordinate safe updates via Phoenix-72 (scar → law)

Specification:
- See spec/VAULT_999.md for full semantics.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class VaultConfig:
    """
    Configuration for Vault-999.

    vault_path: path to constitution.json (L0)
    """
    vault_path: Path = Path("runtime/vault_999/constitution.json")


class VaultInitializationError(Exception):
    """Raised when the Vault cannot be initialized or loaded."""


class Vault999:
    """
    VAULT-999 — L0 Constitutional Memory.

    Pattern:
        vault = Vault999(VaultConfig())
        floors = vault.get_floors()
        laws = vault.get_laws()
    """

    def __init__(self, config: Optional[VaultConfig] = None):
        self.config = config or VaultConfig()
        self._constitution: Dict[str, Any] = {}
        self._load_or_initialize()

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _load_or_initialize(self) -> None:
        """
        Load constitution.json if exists; otherwise initialize a minimal one.
        """
        path = self.config.vault_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            try:
                with path.open("r", encoding="utf-8") as f:
                    self._constitution = json.load(f)
            except Exception as e:  # pragma: no cover
                raise VaultInitializationError(f"Failed to load constitution: {e}") from e
        else:
            # Initialize with a minimal constitution structure
            self._constitution = {
                "version": "35.1.0",
                "epoch": "35Ω",
                "physics": {
                    "delta_S_min": 0.0,
                    "peace_squared_min": 1.0,
                    "omega_band": {"min": 0.03, "max": 0.05},
                },
                "floors": {
                    "truth_min": 0.99,
                    "kappa_r_min": 0.95,
                    "tri_witness_min": 0.95,
                    "rasa_required": True,
                    "amanah_lock": True,
                },
                "laws": [],
                "amendments": [],
            }
            self._save()

    def _save(self) -> None:
        """
        Persist current constitution to disk.

        Note: In production, this should only be called by controlled Phoenix-72
        workflows, not ad-hoc at runtime.
        """
        with self.config.vault_path.open("w", encoding="utf-8") as f:
            json.dump(self._constitution, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def get_constitution(self) -> Dict[str, Any]:
        """Return the full constitution dict."""
        return self._constitution

    def get_floors(self) -> Dict[str, Any]:
        """Return floors object (thresholds & flags)."""
        return self._constitution.get("floors", {})

    def get_physics(self) -> Dict[str, Any]:
        """Return physics object (ΔΩΨ settings)."""
        return self._constitution.get("physics", {})

    def get_laws(self, status: Optional[str] = "ACTIVE") -> List[Dict[str, Any]]:
        """
        Return list of laws. If status provided, filter by status.
        """
        laws = self._constitution.get("laws", [])
        if status is None:
            return laws
        return [law for law in laws if law.get("status") == status]

    def list_amendments(self) -> List[Dict[str, Any]]:
        """Return all amendments."""
        return self._constitution.get("amendments", [])

    # ------------------------------------------------------------------ #
    # Phoenix-72 Integration (L2)
    # ------------------------------------------------------------------ #

    def apply_amendment(self, amendment: Dict[str, Any]) -> None:
        """
        Apply a new amendment into the constitution.

        WARNING:
            This should only be invoked by a Phoenix-72 workflow with
            proper audit trail and Tri-Witness oversight.
        """
        amendments = self._constitution.setdefault("amendments", [])
        amendments.append(amendment)
        self._save()

    def record_gitseal_approval(
        self,
        version: str,
        bundle_hash: str,
        commit_hash: str,
        human_authority: str,
        entropy_delta: float,
    ) -> None:
        """
        Record /gitseal approval in constitutional memory.

        This creates an amendment entry tracking the sealed release,
        integrating Trinity governance with Vault-999 canonical memory.

        Args:
            version: Semantic version (e.g. "43.0.1")
            bundle_hash: Bundle hash from /gitseal
            commit_hash: Git commit hash
            human_authority: Name of approving authority
            entropy_delta: ΔS from /gitforge analysis

        Note:
            Called by Trinity seal.py after successful APPROVE.
        """
        amendment = {
            "id": f"gitseal_{version}",
            "type": "GITSEAL_APPROVAL",
            "version": version,
            "bundle_hash": bundle_hash,
            "commit_hash": commit_hash,
            "human_authority": human_authority,
            "entropy_delta": entropy_delta,
            "applied_at": amendment_timestamp(),
        }
        amendments = self._constitution.setdefault("amendments", [])
        amendments.append(amendment)

        # Update entropy baseline
        physics = self._constitution.setdefault("physics", {})
        physics["last_entropy_delta"] = entropy_delta
        physics["last_sealed_version"] = version

        self._save()

    def update_floors(self, new_floors: Dict[str, Any], phoenix_id: str) -> None:
        """
        Update floors via a Phoenix cycle.

        Records the amendment and updates floors atomically.
        """
        self._constitution["floors"] = new_floors
        amend = {
            "id": phoenix_id,
            "type": "FLOOR_UPDATE",
            "applied_at": amendment_timestamp(),
            "details": {"floors": new_floors},
        }
        amendments = self._constitution.setdefault("amendments", [])
        amendments.append(amend)
        self._save()


def amendment_timestamp() -> str:
    """Return ISO-8601 timestamp for amendments."""
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()
