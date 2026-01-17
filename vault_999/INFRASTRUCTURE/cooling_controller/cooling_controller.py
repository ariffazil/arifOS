"""
Phoenix-72 Cooling Controller
Enforces 72-hour window for PARTIAL verdicts before auto-void.

Constitutional Integration:
- PARTIAL verdicts must cool for 72 hours before becoming SEAL
- Auto-void after deadline if no human decision
- Implements "Ditempa Bukan Diberi" (forged not given) principle
"""
from datetime import datetime, timedelta
import json
import logging
import uuid
from pathlib import Path
from typing import Optional, List, Dict

# Import database connection (will gracefully fallback if unavailable)
try:
    from arifos_core.memory.ledger.db_connection import DatabaseConnection
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    DatabaseConnection = None

logger = logging.getLogger(__name__)


class CoolingController:
    """
    Cooling Controller for Phoenix-72 constitutional governance.

    Enforces mandatory 72-hour cooling period for PARTIAL verdicts.
    Auto-voids entries that expire without human decision.
    """

    def __init__(self, vault_root: str = "vault_999"):
        self.vault_root = Path(vault_root)
        self.timers_path = self.vault_root / "INFRASTRUCTURE/cooling_controller/cooling_timers.jsonl"
        self.void_log_path = self.vault_root / "INFRASTRUCTURE/cooling_controller/auto_void_log.jsonl"
        self.cooling_window = timedelta(hours=72)

        # Ensure files exist
        self.timers_path.parent.mkdir(parents=True, exist_ok=True)
        self.timers_path.touch(exist_ok=True)
        self.void_log_path.touch(exist_ok=True)

    def start_cooling(self, entry_id: str, verdict: str, timestamp: Optional[datetime] = None) -> Optional[datetime]:
        """
        Start 72h cooling timer for PARTIAL verdict.

        Args:
            entry_id: Unique identifier for the entry
            verdict: Verdict type (only PARTIAL triggers cooling)
            timestamp: Optional timestamp (defaults to now)

        Returns:
            Cooling deadline datetime if PARTIAL, None otherwise
        """
        if verdict != "PARTIAL":
            return None

        if timestamp is None:
            timestamp = datetime.now()

        deadline = timestamp + self.cooling_window
        timer_entry = {
            "entry_id": entry_id,
            "verdict": verdict,
            "started": timestamp.isoformat(),
            "deadline": deadline.isoformat(),
            "status": "COOLING"
        }

        with open(self.timers_path, "a") as f:
            f.write(json.dumps(timer_entry) + "\n")

        return deadline

    def check_expired(self) -> List[Dict]:
        """
        Check for expired cooling timers and auto-void them.

        Returns:
            List of expired timer entries that were auto-voided
        """
        now = datetime.now()
        expired = []

        if not self.timers_path.exists() or self.timers_path.stat().st_size == 0:
            return expired

        with open(self.timers_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                timer = json.loads(line)
                if timer["status"] == "COOLING":
                    deadline = datetime.fromisoformat(timer["deadline"])
                    if now > deadline:
                        expired.append(timer)

        for timer in expired:
            self._auto_void(timer)

        return expired

    def cancel_cooling(self, entry_id: str, reason: str = "Human decision made") -> bool:
        """
        Cancel cooling timer (e.g., when human makes decision before deadline).

        Args:
            entry_id: Entry to cancel cooling for
            reason: Reason for cancellation

        Returns:
            True if timer was found and cancelled, False otherwise
        """
        if not self.timers_path.exists():
            return False

        updated_timers = []
        cancelled = False

        with open(self.timers_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                timer = json.loads(line)
                if timer["entry_id"] == entry_id and timer["status"] == "COOLING":
                    timer["status"] = "CANCELLED"
                    timer["cancelled_at"] = datetime.now().isoformat()
                    timer["cancel_reason"] = reason
                    cancelled = True
                updated_timers.append(json.dumps(timer))

        if cancelled:
            with open(self.timers_path, "w") as f:
                f.write("\n".join(updated_timers) + "\n")

        return cancelled

    def get_active_timers(self) -> List[Dict]:
        """
        Get all currently active cooling timers.

        Returns:
            List of active timer entries
        """
        active = []

        if not self.timers_path.exists() or self.timers_path.stat().st_size == 0:
            return active

        with open(self.timers_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                timer = json.loads(line)
                if timer["status"] == "COOLING":
                    active.append(timer)

        return active

    def _auto_void(self, timer: Dict) -> None:
        """
        Auto-void an expired PARTIAL verdict.

        Args:
            timer: Timer entry that has expired
        """
        void_entry = {
            **timer,
            "status": "AUTO_VOIDED",
            "voided_at": datetime.now().isoformat(),
            "reason": "72h Phoenix cooling window expired without human decision",
            "constitutional_floor": "Phoenix-72 (Ditempa Bukan Diberi)"
        }

        with open(self.void_log_path, "a") as f:
            f.write(json.dumps(void_entry) + "\n")

        # Update timer status in timers file
        self.cancel_cooling(timer["entry_id"], "Auto-voided after 72h expiration")


if __name__ == "__main__":
    # Example usage
    controller = CoolingController()

    # Start cooling for a PARTIAL verdict
    deadline = controller.start_cooling("test_entry_001", "PARTIAL")
    print(f"Cooling started, deadline: {deadline}")

    # Check active timers
    active = controller.get_active_timers()
    print(f"Active timers: {len(active)}")

    # Cancel cooling (simulating human decision)
    cancelled = controller.cancel_cooling("test_entry_001", "Human approved before deadline")
    print(f"Cancelled: {cancelled}")
