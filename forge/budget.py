"""
arifOS Forge Budget Enforcer

Fixed thermodynamic budget enforcement for 777_FORGE operations.
Inspired by Karpathy's autoresearch fixed time budget pattern.

Thermodynamic Budget Caps:
  delta_S  ≤ 0.05  (entropy change per operation)
  delta_Ω  ≤ 0.10  (cognitive load)
  Ψ        ≥ 1.0    (system vitality, must be >= 1.0)
  wallclock ≤ 600s  (10 minutes max per experiment)
  files     ≤ 1     (single-file discipline per experiment)
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class ForgeBudget:
    """Thermodynamic budget for a single forge operation."""

    forge_id: str = "unknown"
    max_delta_S: float = 0.05
    max_delta_Ω: float = 0.10
    min_psi: float = 1.0
    max_wallclock_seconds: float = 600.0
    max_files: int = 1

    # Measured values (set during execution)
    measured_delta_S: Optional[float] = None
    measured_delta_Ω: Optional[float] = None
    measured_psi: Optional[float] = None
    elapsed_seconds: float = 0.0
    files_modified: int = 0

    # Budget state
    started_at: Optional[datetime] = None
    reverted: bool = False
    revert_reason: Optional[str] = None

    def start(self) -> None:
        """Mark experiment start."""
        self.started_at = datetime.now(timezone.utc)

    def check(self, check_wallclock: bool = True) -> tuple[bool, str]:
        """
        Check if budget is still within bounds.
        Returns (ok, reason).
        """
        self.elapsed_seconds = (
            (datetime.now(timezone.utc) - self.started_at).total_seconds()
            if self.started_at
            else 0.0
        )

        if check_wallclock and self.started_at is None:
            return False, "Budget not started — call start() first"

        if check_wallclock and self.elapsed_seconds > self.max_wallclock_seconds:
            self.reverted = True
            self.revert_reason = f"wallclock exceeded: {self.elapsed_seconds:.1f}s > {self.max_wallclock_seconds}s"
            return False, self.revert_reason

        if self.measured_delta_S is not None and self.measured_delta_S > self.max_delta_S:
            self.reverted = True
            self.revert_reason = f"delta_S exceeded: {self.measured_delta_S:.4f} > {self.max_delta_S}"
            return False, self.revert_reason

        if self.measured_delta_Ω is not None and self.measured_delta_Ω > self.max_delta_Ω:
            self.reverted = True
            self.revert_reason = f"delta_Ω exceeded: {self.measured_delta_Ω:.4f} > {self.max_delta_Ω}"
            return False, self.revert_reason

        if self.measured_psi is not None and self.measured_psi < self.min_psi:
            self.reverted = True
            self.revert_reason = f"Ψ below minimum: {self.measured_psi:.4f} < {self.min_psi}"
            return False, self.revert_reason

        if self.files_modified > self.max_files:
            self.reverted = True
            self.revert_reason = f"file count exceeded: {self.files_modified} > {self.max_files}"
            return False, self.revert_reason

        return True, "budget OK"

    def record(self, delta_S: float, delta_Ω: float, psi: float) -> None:
        """Record measured thermodynamic values."""
        self.measured_delta_S = delta_S
        self.measured_delta_Ω = delta_Ω
        self.measured_psi = psi

    def record_file_count(self, count: int) -> None:
        """Record how many files were modified."""
        self.files_modified = count

    def summary(self) -> dict:
        """Return experiment summary dict."""
        ok, reason = self.check(check_wallclock=False)
        return {
            "forge_id": self.forge_id if hasattr(self, "forge_id") else "unknown",
            "timestamp": self.started_at.isoformat() if self.started_at else None,
            "delta_S": self.measured_delta_S,
            "delta_Ω": self.measured_delta_Ω,
            "psi": self.measured_psi,
            "elapsed_seconds": self.elapsed_seconds,
            "files_modified": self.files_modified,
            "status": "revert" if self.reverted else ("keep" if ok else "unknown"),
            "revert_reason": self.revert_reason,
            "budget_ok": ok,
            "reason": reason,
        }


# Default budget singleton
default_budget = ForgeBudget()


def enforce_budget(
    delta_S: float,
    delta_Ω: float,
    psi: float,
    files_modified: int = 1,
) -> dict:
    """
    Convenience wrapper: check if measured values fit within default budget.
    Returns a dict with status, values, and budget state.
    """
    budget = ForgeBudget(
        measured_delta_S=delta_S,
        measured_delta_Ω=delta_Ω,
        measured_psi=psi,
        files_modified=files_modified,
    )
    ok, reason = budget.check(check_wallclock=False)

    return {
        "budget_compliant": ok,
        "reason": reason,
        "delta_S": delta_S,
        "delta_Ω": delta_Ω,
        "psi": psi,
        "files_modified": files_modified,
        "max_delta_S": budget.max_delta_S,
        "max_delta_Ω": budget.max_delta_Ω,
        "min_psi": budget.min_psi,
        "revert": not ok,
        "revert_reason": budget.revert_reason if not ok else None,
    }


if __name__ == "__main__":
    # Quick sanity check — pass without wallclock check
    budget = ForgeBudget(forge_id="test", measured_delta_S=0.032, measured_delta_Ω=0.08, measured_psi=1.12, files_modified=1)
    budget.start()
    result = enforce_budget(delta_S=0.032, delta_Ω=0.08, psi=1.12, files_modified=1)
    print(result)
    # Should pass
    assert result["budget_compliant"] is True

    result_fail = enforce_budget(delta_S=0.071, delta_Ω=0.15, psi=0.95, files_modified=1)
    print(result_fail)
    # Should fail
    assert result_fail["budget_compliant"] is False
    assert result_fail["revert"] is True
    print("\n✓ Budget enforcement sanity check passed")