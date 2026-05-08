import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, Any

class HarnessAlarmSystem:
    """
    Harness Violation Alarm System.
    Detects 'Constraint Snapping' and emits high-priority telemetry to arifOS.
    """

    def __init__(self, vault_path: str = "C:/ariffazil/arifOS/arifosmcp/VAULT999/harness_breaches.jsonl"):
        self.vault_path = vault_path
        # Ensure the vault directory exists
        try:
            os.makedirs(os.path.dirname(self.vault_path), exist_ok=True)
        except Exception:
            # Fail silently if directory creation is blocked, but log to stderr
            pass

    def trigger(self, tool_name: str, harness_name: str, detail: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger an alarm for a harness snap."""
        event = {
            "epoch": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": "CRITICAL",
            "category": "HARNESS_BREACH",
            "harness": harness_name,
            "tool": tool_name,
            "detail": detail,
            "message": f"CRITICAL: {harness_name} Harness SNAPPED in {tool_name}."
        }

        # For real-time terminal monitor (simulated)
        print(f"!!! [HARNESS_ALARM] {event['message']} !!!", file=sys.stderr)

        try:
            with open(self.vault_path, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            event["error"] = f"Vault write failed: {str(e)}"

        return event

if __name__ == "__main__":
    # Test trigger
    alarm = HarnessAlarmSystem()
    test_detail = {"error": "SOURCE_DIVERGENCE", "diff": 0.45}
    alarm.trigger("wealth_score_kernel", "Reality", test_detail)
