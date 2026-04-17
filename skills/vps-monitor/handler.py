"""
arifOS Skill: vps-monitor
F12 Security - Hardcoded Commands Only
F4 Clarity - Structured Telemetry Output
"""

import logging
import subprocess
from typing import Any

logger = logging.getLogger(__name__)

class VPSMonitorSkill:
    """VPS Telemetry Monitoring with F12 Injection Defense."""
    
    def __init__(self):
        self.name = "vps-monitor"
        self.floor = "F4"
        # F12: Only hardcoded, read-only commands allowed
        self._SAFE_COMMANDS = {
            "get_telemetry": "uptime && free -h",
            "get_zram_status": "zramctl",
            "get_disk_usage": "df -h /"
        }

    async def execute(
        self,
        action: str,
        params: dict[str, Any] = None,
        session_id: str = "global",
        dry_run: bool = True,
        reality_bridge: Any | None = None,
        checkpoint: str | None = None
    ) -> dict[str, Any]:
        """Execute telemetry action securely."""
        
        command = self._SAFE_COMMANDS.get(action)
        if not command:
            return {
                "ok": False,
                "verdict": "VOID",
                "error": f"F12_BLOCKED: Action '{action}' is not in the safe-list."
            }

        if dry_run:
            return {
                "ok": True,
                "verdict": "SEAL",
                "mode": "dry_run",
                "action": action,
                "command": command,
                "hint": "F12: Input sanitization passed (hardcoded command)."
            }

        # REALITY: Execute the command
        try:
            # We use subprocess directly here as a fallback or if reality_bridge is the arifOS kernel
            # In production, we'd use reality_bridge.execute_shell() if it exists
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(timeout=5)
            
            return {
                "ok": True,
                "verdict": "SEAL",
                "mode": "real",
                "action": action,
                "output": stdout.strip(),
                "error": stderr.strip(),
                "success": process.returncode == 0
            }
        except Exception as e:
            logger.error(f"VPS Monitor execution error: {e}")
            return {
                "ok": False,
                "verdict": "VOID",
                "error": f"EXECUTION_FAILED: {str(e)}"
            }

skill = VPSMonitorSkill()

async def execute(
    action: str,
    params: dict[str, Any] = None,
    session_id: str = "global",
    dry_run: bool = True,
    reality_bridge: Any | None = None,
    checkpoint: str | None = None
) -> dict[str, Any]:
    """Entry point for OpenClaw skill execution."""
    return await skill.execute(action, params, session_id, dry_run, reality_bridge, checkpoint)

metadata = {
    "name": "vps-monitor",
    "floor": "F4",
    "actions": ["get_telemetry", "get_zram_status", "get_disk_usage"],
    "reversible": False
}
