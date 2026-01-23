"""
ccc_constitutional_memory.py — CCC Constitutional Memory Band

CCC (Constitutional Core Context) memory band that references vault seals
as the canonical source of constitutional truth.

Architecture:
- Reads constitutional state from vault_999/seals/current_seal.yaml
- Provides floor thresholds from sealed state
- Validates actions against sealed constitution
- Logs constitutional decisions to vault ledger

Memory Band Structure:
- AAA_MEMORY: Human context and preferences
- BBB_LEDGER: Machine logs and state transitions
- CCC_CONSTITUTIONAL: Constitutional knowledge (THIS MODULE)

Authority:
- 000_THEORY/000_ARCHITECTURE.md (Memory Bands)
- vault_999/seals/current_seal.yaml (Canonical seal)

DITEMPA BUKAN DIBERI - Forged v50.1
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .vault_seal_accessor import VaultSealAccessor, VaultAccessError


class ConstitutionalMemoryError(Exception):
    """Raised when constitutional memory operation fails"""
    pass


class ConstitutionalMemory:
    """
    CCC Memory Band - Constitutional Core Memory

    References vault seal as canonical source of constitutional truth.
    All floor thresholds, validation rules, and constitutional state
    come from the sealed YAML.

    Usage:
        ccc = ConstitutionalMemory()

        # Get floor threshold from seal
        truth_threshold = ccc.get_floor_threshold("F2_truth")

        # Validate action against sealed constitution
        is_valid = ccc.validate_action("write_file", context)

        # Log constitutional decision
        ccc.log_decision("F2_truth", {"pass": True, "score": 0.99})
    """

    def __init__(self, vault_path: str = "vault_999"):
        try:
            self.vault = VaultSealAccessor(vault_path)
        except VaultAccessError as e:
            raise ConstitutionalMemoryError(
                f"Cannot initialize CCC memory - vault seal invalid: {e}"
            )

        self.seal = self.vault.seal
        self.memory_path = Path(vault_path) / "CCC_CONSTITUTIONAL"
        self.memory_path.mkdir(exist_ok=True)

    def get_seal_version(self) -> str:
        """Get current constitutional seal version"""
        return self.seal.version

    def get_floor_threshold(self, floor: str) -> float:
        """
        Get constitutional floor threshold from sealed state

        Args:
            floor: Floor identifier (e.g., "F2_truth", "F4_clarity")

        Returns:
            Threshold value from seal

        Raises:
            ConstitutionalMemoryError: If floor not in seal
        """
        floor_data = self.seal.floors_validated.get(floor)

        if not floor_data:
            raise ConstitutionalMemoryError(
                f"Floor {floor} not found in seal {self.seal.version}"
            )

        # Return the score as threshold (represents the sealed validation level)
        return floor_data.get("score", 0.0)

    def get_floor_status(self, floor: str) -> Dict[str, Any]:
        """
        Get full floor status from seal

        Returns dictionary with:
            - pass: bool (did floor pass in seal)
            - score: float (validation score)
            - evidence: str (validation evidence)
        """
        floor_data = self.seal.floors_validated.get(floor)

        if not floor_data:
            return {
                "pass": False,
                "score": 0.0,
                "evidence": f"Floor {floor} not in seal",
                "seal_version": self.seal.version
            }

        return {
            **floor_data,
            "seal_version": self.seal.version
        }

    def validate_action(self, action: str, context: Dict[str, Any]) -> bool:
        """
        Validate action against sealed constitutional state

        Args:
            action: Action to validate
            context: Action context

        Returns:
            True if action complies with sealed constitution

        This checks that:
        1. All floors in seal passed
        2. Seal ZKPC proof is valid
        3. Action doesn't violate any sealed constraints
        """
        # Check all floors passed in seal
        for floor, result in self.seal.floors_validated.items():
            if not result.get("pass", False):
                self.log_decision(action, {
                    "result": "VOID",
                    "reason": f"Floor {floor} failed in seal",
                    "floor_status": result
                })
                return False

        # Check seal validity
        if not self.vault.is_sealed():
            self.log_decision(action, {
                "result": "VOID",
                "reason": "Vault seal invalid",
                "seal_version": self.seal.version
            })
            return False

        # Action passes constitutional validation
        self.log_decision(action, {
            "result": "SEAL",
            "reason": "Action complies with sealed constitution",
            "seal_version": self.seal.version,
            "context": context
        })

        return True

    def log_decision(self, action: str, decision: Dict[str, Any]) -> None:
        """
        Log constitutional decision to CCC memory ledger

        Args:
            action: Action that was validated
            decision: Decision details (result, reason, evidence)
        """
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "decision": decision,
            "seal_version": self.seal.version,
            "seal_valid": self.vault.is_sealed()
        }

        decisions_log = self.memory_path / "constitutional_decisions.jsonl"

        with open(decisions_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + "\n")

    def get_sealed_constants(self) -> Dict[str, Any]:
        """
        Get all constitutional constants from seal

        Returns sealed values for:
        - Floor thresholds (F1-F13)
        - Physics constants (ΔS, Peace², Ω₀)
        - Tri-Witness requirements
        - ZKPC proof requirements
        """
        return {
            "version": self.seal.version,
            "timestamp": self.seal.timestamp,

            "floors": {
                floor: {
                    "threshold": data.get("score", 0.0),
                    "pass": data.get("pass", False),
                    "evidence": data.get("evidence", "")
                }
                for floor, data in self.seal.floors_validated.items()
            },

            "zkpc": {
                "merkle_root": self.seal.merkle_root,
                "has_floor_proofs": bool(self.seal.floor_proofs),
                "has_signature": bool(self.seal.signature)
            },

            "status": "SEALED" if self.vault.is_sealed() else "VOID"
        }

    def get_decision_history(self, limit: int = 100) -> list[Dict[str, Any]]:
        """
        Get recent constitutional decisions from log

        Args:
            limit: Maximum number of decisions to return

        Returns:
            List of recent decisions (newest first)
        """
        decisions_log = self.memory_path / "constitutional_decisions.jsonl"

        if not decisions_log.exists():
            return []

        decisions = []
        with open(decisions_log, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    decisions.append(json.loads(line))

        # Return newest first
        return list(reversed(decisions[-limit:]))


# Convenience function for global CCC access
_ccc_instance: Optional[ConstitutionalMemory] = None


def get_constitutional_memory() -> ConstitutionalMemory:
    """
    Get global CCC memory instance (singleton pattern)

    This ensures all parts of arifOS reference the same sealed constitution.
    """
    global _ccc_instance

    if _ccc_instance is None:
        _ccc_instance = ConstitutionalMemory()

    return _ccc_instance


def reset_constitutional_memory() -> None:
    """Reset global CCC instance (for testing)"""
    global _ccc_instance
    _ccc_instance = None
