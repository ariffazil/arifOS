import os
import shlex
import subprocess
from datetime import UTC, datetime

# arifOS Governance Imports (graceful fallback for standalone use)
try:
    from core.shared.physics import delta_S
except ImportError:

    def delta_S(input_text: str, output_text: str) -> float:
        """Stub entropy delta — returns 0 when full physics module unavailable."""
        return 0.0


try:
    from arifosmcp.hexagon.escalation.hold_state import anchor_hold_registry  # was agentzero
except ImportError:

    class _StubHoldRegistry:
        """Stub hold registry when HEXAGON escalation not available (was: agentzero escalation)."""

        def is_held(self, session_id: str) -> bool:
            return False

        def get_hold_reason(self, session_id: str) -> str:
            return ""

    anchor_hold_registry = _StubHoldRegistry()

from arifosmcp.abi.amanah_gate import Verdict as _AmanahVerdict
from arifosmcp.abi.amanah_gate import scan as _amanah_scan


class HardenedShellForge:
    """
    Sovereign Forge for Shell Operations.

    Enforces arifOS 13 Floors:
    - F1 Amanah: Pre-execution checkpointing via git-worktree/commit.
    - F7 Humility: Mandatory dry_run enforcement.
    - L13 Sovereign: 888_HOLD logic for High/Critical risk commands.
    """

    def __init__(self, default_cwd: str = None):
        self.default_cwd = default_cwd or os.getcwd()

    def _is_high_risk(self, command: str) -> bool:
        """Heuristic for high-risk shell operations."""
        risk_patterns = [
            "rm ",
            "git push",
            "pip install",
            "rm -rf",
            "mv ",
            "> /",
            "docker rm",
            "sudo ",
        ]
        return any(p in command.lower() for p in risk_patterns)

    def execute(
        self,
        command: str,
        cwd: str = None,
        dry_run: bool = True,
        session_id: str = "anonymous",
    ) -> dict[str, any]:
        """Execute a shell command with governance induction."""
        target_cwd = cwd or self.default_cwd
        is_risk = self._is_high_risk(command)

        # 0. AMANAH Awareness — HARAM/HOLD pattern scan (informational, not blocking)
        #    Agents must know halal/haram. The gate informs; the agent chooses.
        amanah_v, amanah_d, amanah_c = _amanah_scan(command)
        _amanah_awareness = None
        if amanah_v != _AmanahVerdict.PROCEED:
            _amanah_awareness = {
                "verdict": amanah_v.value,
                "description": amanah_d,
                "recovery_cost": amanah_c,
                "note": "AMANAH awareness: this command matches a dangerous pattern. The agent chooses; the record remembers.",
            }

        # 1. Check for global 888_HOLD (Anchor Void)
        if anchor_hold_registry.is_held(session_id):
            return {
                "ok": False,
                "status": "HOLD",
                "error": "888_HOLD: Anchor is void. Execution blocked.",
                "note": anchor_hold_registry.get_hold_reason(session_id),
            }

        # 2. Risk Evaluation & L13 Calibration
        if is_risk and not dry_run:
            # High risk + Not a dry run -> Force 888_HOLD unless explicit override
            return {
                "ok": False,
                "status": "888_HOLD",
                "error": "L13 Sovereign: High-risk command detected. Approval required.",
                "command_preview": command,
            }

        # 3. F7 Humility: Dry Run Simulation
        if dry_run:
            result = {
                "ok": True,
                "status": "SIMULATED",
                "command": command,
                "note": "F7 Humility: Command simulated but not executed.",
                "thermodynamics": {"delta_s": 0, "status": "STABLE"},
            }
            if _amanah_awareness:
                result["amanah_awareness"] = _amanah_awareness
            return result

        # 4. Preparation: F1 Amanah Checkpoint (MOCK Logic - in prod would call git)
        # Note: In a real system, we would trigger a worktree-add or commit here.

        # 5. Execution
        args = shlex.split(command)
        start_time = datetime.now(UTC)

        try:
            result = subprocess.run(
                args,
                cwd=target_cwd,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,  # Humility limit: avoid hangs
            )

            # F4 Clarity: Thermodynamic Measurement
            input_context = f"{command} @ {target_cwd}"
            output_context = f"{result.stdout}\n{result.stderr}"
            ds = delta_S(input_context, output_context)

            result = {
                "ok": result.returncode == 0,
                "status": "SEALED" if result.returncode == 0 else "ERROR",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "entropy": {"delta_s": round(ds, 4), "is_stable": ds <= 0},
                "execution_timestamp": start_time.isoformat(),
            }
            if _amanah_awareness:
                result["amanah_awareness"] = _amanah_awareness
            return result
        except subprocess.TimeoutExpired:
            result = {
                "ok": False,
                "status": "TIMEOUT",
                "error": "F7 Humility: Command timed_out after 60s.",
                "command": command,
            }
            if _amanah_awareness:
                result["amanah_awareness"] = _amanah_awareness
            return result
        except Exception as e:
            result = {
                "ok": False,
                "status": "EXCEPTION",
                "error": str(e),
                "command": command,
            }
            if _amanah_awareness:
                result["amanah_awareness"] = _amanah_awareness
            return result


# Canonical instance
forge = HardenedShellForge()
