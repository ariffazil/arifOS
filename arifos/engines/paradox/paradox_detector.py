"""
Paradox Engine: Detect and resolve contradictions
Creates ScarPackets for formal paradox resolution

Constitutional Integration:
- Detects logical contradictions in reasoning
- Creates ScarPackets with PP/PS/Psi/Phi metrics
- Implements "Ditempa Bukan Diberi" at the logical level
"""
from datetime import datetime
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import uuid


@dataclass
class ScarPacket:
    """
    Formal record of a paradox and its resolution journey.

    Metrics:
    - PP (Paradox Pressure): Strength of contradiction (0.0-1.0)
    - PS (Paradox Stabilization): Progress toward resolution (0.0-1.0)
    - Psi (Equilibrium): Balance between pressure and stabilization
    - Phi (Resolution): Completion status (0=unresolved, 1=fully resolved)
    """
    scar_id: str
    nature: str  # Type of paradox (e.g., "logical", "temporal", "authority")
    contradiction: Dict[str, Any]  # The contradictory statements/beliefs
    status: str  # COOLING, RESOLVING, RESOLVED
    paradox_metrics: Dict[str, float]  # PP, PS, Psi, Phi
    created_at: str
    resolved_at: Optional[str] = None
    resolution: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class ParadoxDetector:
    """
    Paradox Engine for constitutional governance.

    Detects contradictions and manages their resolution through ScarPackets.
    """

    def __init__(self, vault_root: str = "vault_999"):
        self.vault_root = Path(vault_root)
        self.active_path = self.vault_root / "INFRASTRUCTURE/paradox_engine/scar_packets/active_scars.jsonl"
        self.resolved_path = self.vault_root / "INFRASTRUCTURE/paradox_engine/scar_packets/resolved_scars.jsonl"

        # Ensure files exist
        self.active_path.parent.mkdir(parents=True, exist_ok=True)
        self.active_path.touch(exist_ok=True)
        self.resolved_path.touch(exist_ok=True)

    def detect_contradiction(self, statement_a: Dict[str, Any], statement_b: Dict[str, Any]) -> bool:
        """
        Detect logical contradiction between two statements.

        Args:
            statement_a: First statement with 'claim' and 'confidence'
            statement_b: Second statement with 'claim' and 'confidence'

        Returns:
            True if contradiction detected, False otherwise
        """
        # Basic negation detection
        claim_a = statement_a.get("claim", "").lower()
        claim_b = statement_b.get("claim", "").lower()

        # Check for explicit negation patterns
        negation_patterns = [
            ("is", "is not"),
            ("true", "false"),
            ("exists", "does not exist"),
            ("allowed", "forbidden"),
            ("seal", "void")
        ]

        for pos, neg in negation_patterns:
            if pos in claim_a and neg in claim_b:
                return True
            if neg in claim_a and pos in claim_b:
                return True

        # Check for mutual exclusivity
        if statement_a.get("verdict") and statement_b.get("verdict"):
            if statement_a["verdict"] != statement_b["verdict"]:
                # Different verdicts on same subject
                if statement_a.get("subject") == statement_b.get("subject"):
                    return True

        return False

    def calculate_paradox_pressure(self, contradiction: Dict[str, Any]) -> float:
        """
        Calculate PP (Paradox Pressure): How strong is the contradiction?

        Based on:
        - Confidence levels of contradictory claims
        - Authority of sources
        - Impact on system operation
        """
        statement_a = contradiction.get("statement_a", {})
        statement_b = contradiction.get("statement_b", {})

        # Higher confidence = higher pressure
        conf_a = statement_a.get("confidence", 0.5)
        conf_b = statement_b.get("confidence", 0.5)
        confidence_pressure = (conf_a + conf_b) / 2

        # Authority multiplier
        authority_a = 1.5 if statement_a.get("source") == "human" else 1.0
        authority_b = 1.5 if statement_b.get("source") == "human" else 1.0
        authority_pressure = max(authority_a, authority_b)

        # Calculate final pressure (capped at 1.0)
        pp = min(confidence_pressure * authority_pressure / 1.5, 1.0)

        return round(pp, 2)

    def create_scar_packet(
        self,
        nature: str,
        contradiction: Dict[str, Any],
        initial_pp: Optional[float] = None
    ) -> ScarPacket:
        """
        Create ScarPacket for detected paradox.

        Args:
            nature: Type of paradox (logical, temporal, authority, etc.)
            contradiction: The contradictory statements/beliefs
            initial_pp: Optional initial Paradox Pressure (auto-calculated if None)

        Returns:
            Created ScarPacket
        """
        # Generate unique ID
        scar_id = f"SCAR-{uuid.uuid4().hex[:8].upper()}"

        # Calculate initial metrics
        pp = initial_pp if initial_pp is not None else self.calculate_paradox_pressure(contradiction)
        ps = 0.0  # No stabilization yet
        psi = pp / 2  # Equilibrium starts at half pressure
        phi = 0.0  # Unresolved

        scar = ScarPacket(
            scar_id=scar_id,
            nature=nature,
            contradiction=contradiction,
            status="COOLING",
            paradox_metrics={
                "PP": pp,
                "PS": ps,
                "Psi": psi,
                "Phi": phi
            },
            created_at=datetime.now().isoformat()
        )

        # Save to active scars
        self._save_scar(scar, active=True)

        return scar

    def update_scar_status(
        self,
        scar_id: str,
        new_status: str,
        ps_increment: float = 0.0
    ) -> Optional[ScarPacket]:
        """
        Update ScarPacket status and stabilization progress.

        Args:
            scar_id: ID of scar to update
            new_status: New status (COOLING, RESOLVING, RESOLVED)
            ps_increment: Increase in Paradox Stabilization (0.0-1.0)

        Returns:
            Updated ScarPacket or None if not found
        """
        scar = self._find_scar(scar_id)
        if not scar:
            return None

        # Update status
        scar.status = new_status

        # Update PS (Paradox Stabilization)
        current_ps = scar.paradox_metrics.get("PS", 0.0)
        new_ps = min(current_ps + ps_increment, 1.0)
        scar.paradox_metrics["PS"] = new_ps

        # Recalculate Psi (Equilibrium)
        pp = scar.paradox_metrics.get("PP", 0.0)
        scar.paradox_metrics["Psi"] = round((pp + new_ps) / 2, 2)

        # Save updated scar
        self._save_scar(scar, active=True)

        return scar

    def resolve_scar(
        self,
        scar_id: str,
        resolution: Dict[str, Any]
    ) -> Optional[ScarPacket]:
        """
        Mark ScarPacket as resolved with solution.

        Args:
            scar_id: ID of scar to resolve
            resolution: Resolution details (method, outcome, reasoning)

        Returns:
            Resolved ScarPacket or None if not found
        """
        scar = self._find_scar(scar_id)
        if not scar:
            return None

        # Update to resolved state
        scar.status = "RESOLVED"
        scar.resolved_at = datetime.now().isoformat()
        scar.resolution = resolution

        # Set Phi to 1.0 (fully resolved)
        scar.paradox_metrics["Phi"] = 1.0

        # Set PS to 1.0 (fully stabilized)
        scar.paradox_metrics["PS"] = 1.0

        # Recalculate Psi
        pp = scar.paradox_metrics.get("PP", 0.0)
        scar.paradox_metrics["Psi"] = round((pp + 1.0) / 2, 2)

        # Move from active to resolved
        self._remove_from_active(scar_id)
        self._save_scar(scar, active=False)

        return scar

    def get_active_scars(self) -> List[ScarPacket]:
        """Get all currently active (unresolved) scars."""
        scars = []

        if not self.active_path.exists() or self.active_path.stat().st_size == 0:
            return scars

        with open(self.active_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                scars.append(ScarPacket(**data))

        return scars

    def get_resolved_scars(self, limit: int = 10) -> List[ScarPacket]:
        """Get recently resolved scars."""
        scars = []

        if not self.resolved_path.exists() or self.resolved_path.stat().st_size == 0:
            return scars

        with open(self.resolved_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                scars.append(ScarPacket(**data))

        # Return most recent
        return sorted(scars, key=lambda s: s.resolved_at or "", reverse=True)[:limit]

    def _save_scar(self, scar: ScarPacket, active: bool = True):
        """Save scar to appropriate file."""
        path = self.active_path if active else self.resolved_path

        with open(path, "a") as f:
            f.write(json.dumps(scar.to_dict()) + "\n")

    def _find_scar(self, scar_id: str) -> Optional[ScarPacket]:
        """Find scar by ID in active scars."""
        if not self.active_path.exists():
            return None

        with open(self.active_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                if data["scar_id"] == scar_id:
                    return ScarPacket(**data)

        return None

    def _remove_from_active(self, scar_id: str):
        """Remove scar from active scars file."""
        if not self.active_path.exists():
            return

        remaining = []
        with open(self.active_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                if data["scar_id"] != scar_id:
                    remaining.append(json.dumps(data))

        with open(self.active_path, "w") as f:
            f.write("\n".join(remaining) + "\n" if remaining else "")


if __name__ == "__main__":
    # Example usage
    detector = ParadoxDetector()

    # Create a sample contradiction
    contradiction = {
        "statement_a": {
            "claim": "AAA vault is forbidden to machines",
            "confidence": 1.0,
            "source": "human",
            "floor": "F11"
        },
        "statement_b": {
            "claim": "Read AAA vault for memory recall",
            "confidence": 0.8,
            "source": "ai",
            "floor": "F2"
        },
        "context": "Memory retrieval request attempting AAA access"
    }

    # Detect contradiction
    is_contradiction = detector.detect_contradiction(
        contradiction["statement_a"],
        contradiction["statement_b"]
    )
    print(f"Contradiction detected: {is_contradiction}")

    # Create ScarPacket
    scar = detector.create_scar_packet(
        nature="authority_boundary",
        contradiction=contradiction
    )
    print(f"\nScarPacket created: {scar.scar_id}")
    print(f"Status: {scar.status}")
    print(f"Metrics: {scar.paradox_metrics}")

    # Update status
    updated = detector.update_scar_status(scar.scar_id, "RESOLVING", ps_increment=0.3)
    print(f"\nUpdated status: {updated.status}")
    print(f"Updated metrics: {updated.paradox_metrics}")

    # Resolve scar
    resolution = {
        "method": "constitutional_boundary",
        "outcome": "VOID - F11 violation",
        "reasoning": "AAA vault access forbidden by constitutional floor F11"
    }
    resolved = detector.resolve_scar(scar.scar_id, resolution)
    print(f"\nResolved: {resolved.scar_id}")
    print(f"Final metrics: {resolved.paradox_metrics}")
    print(f"Resolution: {resolved.resolution}")

    # Check active scars
    active = detector.get_active_scars()
    print(f"\nActive scars: {len(active)}")

    # Check resolved scars
    resolved_scars = detector.get_resolved_scars()
    print(f"Resolved scars: {len(resolved_scars)}")
