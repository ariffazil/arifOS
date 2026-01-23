"""
Paradox Metrics Tracker: PP, PS, Psi, Phi

Constitutional Integration:
- PP (Paradox Pressure): Strength of contradiction
- PS (Paradox Stabilization): Progress toward resolution
- Psi (Equilibrium): Balance between pressure and stabilization
- Phi (Resolution): Completion status (0→1 as resolved)
"""
from typing import Dict, List, Tuple
from datetime import datetime
import json
from pathlib import Path


class ParadoxMetrics:
    """
    Calculate and track paradox resolution metrics.

    The four core metrics form a complete picture of paradox lifecycle:
    - PP: How hard is the problem? (Pressure)
    - PS: How much progress have we made? (Stabilization)
    - Psi: Are we balanced? (Equilibrium)
    - Phi: Are we done? (Resolution)
    """

    def __init__(self, vault_root: str = "vault_999"):
        self.vault_root = Path(vault_root)
        self.metrics_log = self.vault_root / "INFRASTRUCTURE/paradox_engine/metrics_log.jsonl"

        # Ensure file exists
        self.metrics_log.parent.mkdir(parents=True, exist_ok=True)
        self.metrics_log.touch(exist_ok=True)

    def calculate_pp(
        self,
        contradiction_strength: float,
        confidence_a: float = 0.5,
        confidence_b: float = 0.5,
        authority_multiplier: float = 1.0
    ) -> float:
        """
        Calculate PP (Paradox Pressure): How strong is the contradiction?

        Args:
            contradiction_strength: Base strength of contradiction (0.0-1.0)
            confidence_a: Confidence of first statement (0.0-1.0)
            confidence_b: Confidence of second statement (0.0-1.0)
            authority_multiplier: Authority weight (1.0=normal, 1.5=human source)

        Returns:
            PP value (0.0-1.0), higher = stronger contradiction
        """
        # Weighted average of confidences
        avg_confidence = (confidence_a + confidence_b) / 2

        # Combined pressure
        pp = contradiction_strength * avg_confidence * authority_multiplier

        # Cap at 1.0
        return min(round(pp, 2), 1.0)

    def calculate_ps(
        self,
        stabilization_attempts: int,
        successful_attempts: int = 0,
        time_elapsed_hours: float = 0.0
    ) -> float:
        """
        Calculate PS (Paradox Stabilization): Progress toward resolution.

        Args:
            stabilization_attempts: Total attempts to stabilize
            successful_attempts: Number of successful stabilization steps
            time_elapsed_hours: Hours since paradox creation

        Returns:
            PS value (0.0-1.0), higher = more stabilized
        """
        if stabilization_attempts == 0:
            return 0.0

        # Success rate component
        success_rate = successful_attempts / stabilization_attempts

        # Time component (diminishing returns after 72h)
        time_factor = min(time_elapsed_hours / 72.0, 1.0)

        # Combined stabilization (success more important than time)
        ps = (success_rate * 0.7) + (time_factor * 0.3)

        return min(round(ps, 2), 1.0)

    def calculate_psi(self, pp: float, ps: float) -> float:
        """
        Calculate Psi (Equilibrium): Balance between pressure and stabilization.

        Args:
            pp: Paradox Pressure (0.0-1.0)
            ps: Paradox Stabilization (0.0-1.0)

        Returns:
            Psi value (0.0-1.0), higher = better equilibrium

        Interpretation:
        - Psi < 0.3: High pressure, low stabilization (crisis)
        - Psi 0.3-0.7: Transitioning (working on it)
        - Psi > 0.7: High stabilization approaching resolution
        """
        # Simple average gives equilibrium
        psi = (pp + ps) / 2

        return round(psi, 2)

    def calculate_phi(
        self,
        resolution_quality: float,
        validation_passed: bool = False,
        human_approved: bool = False
    ) -> float:
        """
        Calculate Phi (Resolution): Completion status.

        Args:
            resolution_quality: Quality of resolution (0.0-1.0)
            validation_passed: Constitutional validation passed
            human_approved: Human approval received

        Returns:
            Phi value (0.0-1.0), 0=unresolved, 1=fully resolved

        Interpretation:
        - Phi = 0.0: Unresolved paradox
        - Phi = 0.5: Partial resolution (machine approved)
        - Phi = 1.0: Full resolution (human sealed)
        """
        # Base quality
        phi = resolution_quality

        # Validation bonus
        if validation_passed:
            phi = min(phi + 0.2, 1.0)

        # Human approval seals it
        if human_approved:
            phi = 1.0

        return round(phi, 2)

    def track_metrics(
        self,
        scar_id: str,
        pp: float,
        ps: float,
        psi: float,
        phi: float,
        status: str,
        metadata: Dict = None
    ) -> Dict:
        """
        Log metrics for a ScarPacket.

        Args:
            scar_id: ScarPacket identifier
            pp: Paradox Pressure
            ps: Paradox Stabilization
            psi: Equilibrium
            phi: Resolution
            status: Current status (COOLING, RESOLVING, RESOLVED)
            metadata: Additional context

        Returns:
            Logged entry
        """
        entry = {
            "scar_id": scar_id,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "PP": pp,
                "PS": ps,
                "Psi": psi,
                "Phi": phi
            },
            "status": status,
            "metadata": metadata or {}
        }

        # Save to log
        with open(self.metrics_log, "a") as f:
            f.write(json.dumps(entry) + "\n")

        return entry

    def get_scar_history(self, scar_id: str) -> List[Dict]:
        """
        Get metric history for a specific ScarPacket.

        Args:
            scar_id: ScarPacket identifier

        Returns:
            List of metric entries ordered by timestamp
        """
        history = []

        if not self.metrics_log.exists() or self.metrics_log.stat().st_size == 0:
            return history

        with open(self.metrics_log, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                if entry["scar_id"] == scar_id:
                    history.append(entry)

        return sorted(history, key=lambda e: e["timestamp"])

    def calculate_trajectory(self, scar_id: str) -> Dict:
        """
        Calculate resolution trajectory for a ScarPacket.

        Analyzes metric changes over time to predict resolution.

        Args:
            scar_id: ScarPacket identifier

        Returns:
            Trajectory analysis with predictions
        """
        history = self.get_scar_history(scar_id)

        if len(history) < 2:
            return {
                "scar_id": scar_id,
                "trajectory": "insufficient_data",
                "prediction": None
            }

        # Get first and last entries
        first = history[0]["metrics"]
        last = history[-1]["metrics"]

        # Calculate deltas
        delta_ps = last["PS"] - first["PS"]
        delta_phi = last["Phi"] - first["Phi"]

        # Determine trajectory
        if delta_ps > 0.3 and delta_phi > 0.3:
            trajectory = "accelerating_resolution"
            prediction = "likely_resolved_within_24h"
        elif delta_ps > 0 and delta_phi > 0:
            trajectory = "steady_progress"
            prediction = "likely_resolved_within_72h"
        elif delta_ps == 0 and delta_phi == 0:
            trajectory = "stalled"
            prediction = "requires_intervention"
        else:
            trajectory = "regressing"
            prediction = "requires_human_attention"

        return {
            "scar_id": scar_id,
            "trajectory": trajectory,
            "prediction": prediction,
            "metrics_delta": {
                "PS": round(delta_ps, 2),
                "Phi": round(delta_phi, 2)
            },
            "entries_analyzed": len(history)
        }

    def get_aggregate_stats(self) -> Dict:
        """
        Get aggregate statistics across all tracked scars.

        Returns:
            Statistical summary
        """
        if not self.metrics_log.exists() or self.metrics_log.stat().st_size == 0:
            return {
                "total_scars": 0,
                "avg_pp": 0.0,
                "avg_ps": 0.0,
                "avg_psi": 0.0,
                "avg_phi": 0.0
            }

        scars = {}

        # Get latest entry for each scar
        with open(self.metrics_log, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                scar_id = entry["scar_id"]
                scars[scar_id] = entry["metrics"]

        if not scars:
            return {
                "total_scars": 0,
                "avg_pp": 0.0,
                "avg_ps": 0.0,
                "avg_psi": 0.0,
                "avg_phi": 0.0
            }

        # Calculate averages
        total = len(scars)
        sum_pp = sum(m["PP"] for m in scars.values())
        sum_ps = sum(m["PS"] for m in scars.values())
        sum_psi = sum(m["Psi"] for m in scars.values())
        sum_phi = sum(m["Phi"] for m in scars.values())

        return {
            "total_scars": total,
            "avg_pp": round(sum_pp / total, 2),
            "avg_ps": round(sum_ps / total, 2),
            "avg_psi": round(sum_psi / total, 2),
            "avg_phi": round(sum_phi / total, 2),
            "resolved_count": sum(1 for m in scars.values() if m["Phi"] == 1.0)
        }


if __name__ == "__main__":
    # Example usage
    tracker = ParadoxMetrics()

    # Calculate metrics for a sample paradox
    print("=== Paradox Metrics Calculation ===\n")

    # Initial state: High pressure, no stabilization
    pp = tracker.calculate_pp(
        contradiction_strength=0.9,
        confidence_a=1.0,
        confidence_b=0.8,
        authority_multiplier=1.5
    )
    ps = tracker.calculate_ps(
        stabilization_attempts=0,
        successful_attempts=0,
        time_elapsed_hours=0.0
    )
    psi = tracker.calculate_psi(pp, ps)
    phi = tracker.calculate_phi(
        resolution_quality=0.0,
        validation_passed=False,
        human_approved=False
    )

    print("Initial State (Paradox Detected):")
    print(f"  PP (Pressure): {pp}")
    print(f"  PS (Stabilization): {ps}")
    print(f"  Psi (Equilibrium): {psi}")
    print(f"  Phi (Resolution): {phi}")

    # Track initial state
    tracker.track_metrics(
        scar_id="SCAR-TEST-001",
        pp=pp, ps=ps, psi=psi, phi=phi,
        status="COOLING"
    )

    # After 24h: Some progress
    ps = tracker.calculate_ps(
        stabilization_attempts=3,
        successful_attempts=2,
        time_elapsed_hours=24.0
    )
    psi = tracker.calculate_psi(pp, ps)
    phi = tracker.calculate_phi(
        resolution_quality=0.5,
        validation_passed=False,
        human_approved=False
    )

    print("\nAfter 24h (Working on Resolution):")
    print(f"  PP (Pressure): {pp}")
    print(f"  PS (Stabilization): {ps}")
    print(f"  Psi (Equilibrium): {psi}")
    print(f"  Phi (Resolution): {phi}")

    tracker.track_metrics(
        scar_id="SCAR-TEST-001",
        pp=pp, ps=ps, psi=psi, phi=phi,
        status="RESOLVING"
    )

    # After 72h: Resolved with human approval
    ps = tracker.calculate_ps(
        stabilization_attempts=5,
        successful_attempts=5,
        time_elapsed_hours=72.0
    )
    psi = tracker.calculate_psi(pp, ps)
    phi = tracker.calculate_phi(
        resolution_quality=0.9,
        validation_passed=True,
        human_approved=True
    )

    print("\nAfter 72h (Resolved with Human Approval):")
    print(f"  PP (Pressure): {pp}")
    print(f"  PS (Stabilization): {ps}")
    print(f"  Psi (Equilibrium): {psi}")
    print(f"  Phi (Resolution): {phi}")

    tracker.track_metrics(
        scar_id="SCAR-TEST-001",
        pp=pp, ps=ps, psi=psi, phi=phi,
        status="RESOLVED"
    )

    # Analyze trajectory
    print("\n=== Trajectory Analysis ===")
    trajectory = tracker.calculate_trajectory("SCAR-TEST-001")
    print(f"Trajectory: {trajectory['trajectory']}")
    print(f"Prediction: {trajectory['prediction']}")
    print(f"Metrics Delta: {trajectory['metrics_delta']}")

    # Get aggregate stats
    print("\n=== Aggregate Statistics ===")
    stats = tracker.get_aggregate_stats()
    print(f"Total Scars Tracked: {stats['total_scars']}")
    print(f"Average PP: {stats['avg_pp']}")
    print(f"Average PS: {stats['avg_ps']}")
    print(f"Average Psi: {stats['avg_psi']}")
    print(f"Average Phi: {stats['avg_phi']}")
    print(f"Resolved Count: {stats['resolved_count']}")
