# File: arifos_code/governed_client.py
"""
Governed Claude Code Client

Main wrapper that governs Claude Code with arifOS constitutional enforcement.
Integrates all components:
- PreExecutionTEARFRAME (000→777)
- Claude Code API (native)
- MetricsComputer with AST (888)
- APEX_PRIME judgment
- Cooling Ledger audit trail
- Verdict enforcement (SEAL/PARTIAL/VOID)

This is the public API that replaces direct Claude Code usage.
"""

from arifos_core import APEXPrime, Metrics
from arifos_core.memory.cooling_ledger import (
    CoolingLedger,
    CoolingEntry,
    CoolingMetrics,
    LedgerConfig
)
from arifos_code.pre_execution import PreExecutionTEARFRAME
from arifos_code.metrics_computer import ClaudeCodeMetricsComputer
from pathlib import Path
from typing import Dict, List, Optional
import time
import logging

logger = logging.getLogger(__name__)


class ClaudeCodeClient:
    """
    Thin wrapper around Anthropic API.
    Captures request/response for metrics computation.
    """

    def __init__(self, api_key: str):
        """
        Initialize Claude Code client.

        Args:
            api_key: Anthropic API key
        """
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError(
                "Anthropic SDK not installed. "
                "Install with: pip install anthropic"
            )

    def execute_request(
        self,
        user_request: str,
        context: Dict
    ) -> Dict:
        """
        Execute Claude Code request, capture response.

        Args:
            user_request: Natural language request from user
            context: Additional context dict

        Returns:
            {
                "response_text": str,
                "file_operations": List[Dict],
                "reasoning": str
            }
        """
        # Make API call (standard Anthropic SDK)
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=8192,
            messages=[{
                "role": "user",
                "content": user_request
            }]
        )

        # Parse response
        response_text = response.content[0].text

        # Extract file operations from response
        # (In real implementation, Claude Code API returns structured diffs)
        file_operations = self._parse_file_operations(response_text)

        return {
            "response_text": response_text,
            "file_operations": file_operations,
            "reasoning": self._extract_reasoning(response_text)
        }

    def _parse_file_operations(self, response: str) -> List[Dict]:
        """
        Parse file operations from Claude's response.

        In production, this comes from API metadata.
        For now, simplified parsing.
        """
        operations = []

        # Simplified: Detect file edits from response text
        # Real implementation uses structured API response
        if "I'll update" in response or "I'll modify" in response:
            # Extract file path and changes
            operations.append({
                "type": "edit",
                "file_path": "example.py",  # Would be extracted
                "diff": "...",
                "new_content": "...",
                "lines_added": 0,
                "lines_removed": 0
            })

        return operations

    def _extract_reasoning(self, response: str) -> str:
        """Extract chain-of-thought reasoning from response."""
        # Claude Code typically includes reasoning before code
        return response.split("```")[0] if "```" in response else response


class GovernedClaudeCode:
    """
    Main wrapper - governs Claude Code with arifOS constitution.

    Complete execution loop:
    1. Pre-execution validation (000→777)
    2. Claude Code execution (native)
    3. Metrics computation with AST (888)
    4. APEX_PRIME judgment
    5. Cooling Ledger logging
    6. Verdict enforcement

    This is the public API that replaces direct Claude Code usage.
    """

    def __init__(
        self,
        api_key: str,
        workspace_root: Path,
        ledger_path: Path,
        high_stakes: bool = False
    ):
        """
        Initialize governed Claude Code wrapper.

        Args:
            api_key: Anthropic API key
            workspace_root: Path to codebase root
            ledger_path: Path to Cooling Ledger JSONL file
            high_stakes: Whether to enforce high-stakes mode (Tri-Witness)
        """
        # Initialize components
        self.pre_tearframe = PreExecutionTEARFRAME(workspace_root)
        self.claude_client = ClaudeCodeClient(api_key)
        self.metrics_computer = ClaudeCodeMetricsComputer(workspace_root)
        self.apex = APEXPrime(high_stakes=high_stakes)
        self.ledger = CoolingLedger(config=LedgerConfig(ledger_path=ledger_path))

        self.workspace_root = workspace_root

        logger.info("GovernedClaudeCode initialized")
        logger.info(f"Workspace: {workspace_root}")
        logger.info(f"Ledger: {ledger_path}")
        logger.info(f"High stakes: {high_stakes}")

    def execute_governed_request(
        self,
        user_request: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Execute Claude Code request with full constitutional governance.

        Complete TEARFRAME pipeline:
        000→777 (Pre-execution)
        → Claude execution
        → 888 (Post-execution metrics)
        → APEX judgment
        → 999 (Cooling Ledger)
        → Verdict enforcement

        Args:
            user_request: Natural language request from user
            context: Optional context dict

        Returns:
            {
                "verdict": "SEAL" | "PARTIAL" | "VOID",
                "response": str,
                "file_operations": List[Dict],
                "metrics": Metrics,
                "floor_failures": List[str],
                "ledger_entry_id": str,
                "execution_time": float
            }
        """
        context = context or {}
        start_time = time.time()

        logger.info("="*70)
        logger.info(f"REQUEST: {user_request}")
        logger.info("="*70)

        # ==========================================
        # PHASE 1: PRE-EXECUTION (000→777)
        # ==========================================
        logger.info("[000→777] PRE-EXECUTION TEARFRAME")

        pre_error = self.pre_tearframe.validate_request(user_request, context)
        if pre_error:
            # Immediate VOID - don't even call API
            logger.error(f"[VOID] {pre_error}")
            logger.info("[SABAR] Refusing safely - floor violation detected pre-execution")

            return self._create_void_response(
                reason=pre_error,
                user_request=user_request,
                phase="pre-execution"
            )

        logger.info("[000→777] ✓ Pre-execution validation passed")

        # ==========================================
        # PHASE 2: CLAUDE CODE EXECUTION (Native)
        # ==========================================
        logger.info("[EXECUTING] Calling Claude Code API...")

        try:
            execution_result = self.claude_client.execute_request(
                user_request=user_request,
                context=context
            )
        except Exception as e:
            logger.error(f"[ERROR] Claude Code API failed: {e}")
            return self._create_void_response(
                reason=f"API failure: {str(e)}",
                user_request=user_request,
                phase="execution"
            )

        response_text = execution_result["response_text"]
        file_operations = execution_result["file_operations"]

        logger.info(f"[EXECUTING] ✓ Received response ({len(response_text)} chars)")
        logger.info(f"[EXECUTING] ✓ File operations: {len(file_operations)}")

        # ==========================================
        # PHASE 3: POST-EXECUTION METRICS (888)
        # ==========================================
        logger.info("[888] POST-EXECUTION TEARFRAME - Computing metrics...")

        metrics = self.metrics_computer.compute_metrics(
            request=user_request,
            response=response_text,
            file_operations=file_operations,
            context=context
        )

        logger.info("[888] Constitutional Metrics:")
        logger.info(f"  Truth:   {metrics.truth:.2f}  {'✓' if metrics.truth >= 0.99 else '✗'}")
        logger.info(f"  ΔS:      {metrics.delta_S:+.2f}  {'✓' if metrics.delta_S >= 0 else '✗'}")
        logger.info(f"  Peace²:  {metrics.peace2:.2f}  {'✓' if metrics.peace2 >= 1.0 else '✗'}")
        logger.info(f"  κᵣ:      {metrics.kappa_r:.2f}  {'✓' if metrics.kappa_r >= 0.95 else '✗'}")
        logger.info(f"  Ω₀:      {metrics.omega_0:.2f}  {'✓' if 0.03 <= metrics.omega_0 <= 0.05 else '✗'}")
        logger.info(f"  Amanah:  {metrics.amanah}  {'✓' if metrics.amanah else '✗'}")
        logger.info(f"  Ψ:       {metrics.psi:.2f}  {'✓' if metrics.psi >= 1.0 else '✗'}")

        # ==========================================
        # PHASE 4: APEX_PRIME JUDGMENT
        # ==========================================
        logger.info("[APEX_PRIME] Judging constitutional compliance...")

        verdict = self.apex.judge(metrics)
        floor_failures = self._identify_floor_failures(metrics)

        logger.info(f"[VERDICT] {verdict}")
        if floor_failures:
            logger.warning(f"[FAILURES] {', '.join(floor_failures)}")

        # ==========================================
        # PHASE 5: COOLING LEDGER (999)
        # ==========================================
        ledger_entry = self._log_to_cooling_ledger(
            user_request=user_request,
            response=response_text,
            file_operations=file_operations,
            metrics=metrics,
            verdict=verdict,
            floor_failures=floor_failures,
            context=context
        )

        logger.info(f"[999] ✓ Logged to Cooling Ledger: {ledger_entry['entry_id']}")

        # ==========================================
        # PHASE 6: VERDICT ENFORCEMENT
        # ==========================================
        execution_time = time.time() - start_time

        if verdict == "SEAL":
            logger.info("[SEAL] ✓ All floors passed - applying changes")
            self._apply_file_operations(file_operations)

            return {
                "verdict": "SEAL",
                "response": response_text,
                "file_operations": file_operations,
                "metrics": metrics,
                "floor_failures": [],
                "ledger_entry_id": ledger_entry["entry_id"],
                "execution_time": execution_time
            }

        elif verdict == "PARTIAL":
            logger.warning("[PARTIAL] ⚠ Soft floors marginal - applying with warning")
            self._apply_file_operations(file_operations)

            warning = f"\n\n⚠️ WARNING: This output has constitutional concerns:\n"
            warning += "\n".join(f"  - {failure}" for failure in floor_failures)

            return {
                "verdict": "PARTIAL",
                "response": response_text + warning,
                "file_operations": file_operations,
                "metrics": metrics,
                "floor_failures": floor_failures,
                "ledger_entry_id": ledger_entry["entry_id"],
                "execution_time": execution_time
            }

        else:  # VOID
            logger.error("[VOID] ✗ Critical floor breach - refusing changes")
            logger.info("[SABAR] Stop, Acknowledge, Breathe, Adjust, Resume")

            sabar_message = self._generate_sabar_message(floor_failures, user_request)

            return {
                "verdict": "VOID",
                "response": sabar_message,
                "file_operations": [],  # No changes applied
                "metrics": metrics,
                "floor_failures": floor_failures,
                "ledger_entry_id": ledger_entry["entry_id"],
                "execution_time": execution_time
            }

    def _apply_file_operations(self, file_operations: List[Dict]):
        """
        Apply file changes to workspace.

        Args:
            file_operations: List of file operations to perform
        """
        for op in file_operations:
            file_path = self.workspace_root / op["file_path"]

            if op["type"] == "write":
                file_path.write_text(op["new_content"])
                logger.info(f"  ✓ Wrote {file_path}")

            elif op["type"] == "edit":
                # Apply diff (simplified - real implementation uses patch)
                content = file_path.read_text()
                # Apply diff logic here
                file_path.write_text(op["new_content"])
                logger.info(f"  ✓ Edited {file_path}")

    def _identify_floor_failures(self, metrics: Metrics) -> List[str]:
        """
        Identify which floors failed.

        Args:
            metrics: Computed metrics

        Returns:
            List of failure descriptions
        """
        failures = []

        if metrics.truth < 0.99:
            failures.append(f"Truth={metrics.truth:.2f} < 0.99")
        if metrics.delta_S < 0:
            failures.append(f"ΔS={metrics.delta_S:.2f} < 0")
        if metrics.peace2 < 1.0:
            failures.append(f"Peace²={metrics.peace2:.2f} < 1.0")
        if metrics.kappa_r < 0.95:
            failures.append(f"κᵣ={metrics.kappa_r:.2f} < 0.95")
        if not (0.03 <= metrics.omega_0 <= 0.05):
            failures.append(f"Ω₀={metrics.omega_0:.2f} outside [0.03, 0.05]")
        if not metrics.amanah:
            failures.append("Amanah=False")
        if metrics.psi < 1.0:
            failures.append(f"Ψ={metrics.psi:.2f} < 1.0")

        return failures

    def _log_to_cooling_ledger(
        self,
        user_request: str,
        response: str,
        file_operations: List[Dict],
        metrics: Metrics,
        verdict: str,
        floor_failures: List[str],
        context: Dict
    ) -> Dict:
        """
        Log decision to Cooling Ledger (999).

        Args:
            user_request: User's request
            response: Claude's response
            file_operations: File operations performed
            metrics: Computed metrics
            verdict: APEX verdict
            floor_failures: List of floor failures
            context: Additional context

        Returns:
            {"entry_id": str, "timestamp": float}
        """
        cooling_metrics = CoolingMetrics(
            truth=metrics.truth,
            delta_s=metrics.delta_S,
            peace_squared=metrics.peace2,
            kappa_r=metrics.kappa_r,
            omega_0=metrics.omega_0,
            rasa=True,
            amanah=metrics.amanah,
            tri_witness=metrics.tri_witness,
            psi=metrics.psi
        )

        entry = CoolingEntry(
            timestamp=time.time(),
            query=user_request,
            candidate_output=response,
            metrics=cooling_metrics,
            verdict=verdict,
            floor_failures=floor_failures,
            sabar_reason="; ".join(floor_failures) if floor_failures else None,
            organs={},
            metadata={
                "job_id": context.get("job_id", "claude-code"),
                "file_operations": file_operations,
                "files_modified": [op["file_path"] for op in file_operations],
                "lines_added": sum(op.get("lines_added", 0) for op in file_operations),
                "lines_removed": sum(op.get("lines_removed", 0) for op in file_operations)
            }
        )

        self.ledger.append(entry)

        return {
            "entry_id": f"{entry.timestamp}_{verdict}",
            "timestamp": entry.timestamp
        }

    def _generate_sabar_message(self, failures: List[str], request: str) -> str:
        """
        Generate SABAR protocol response for VOID verdict.

        Args:
            failures: List of floor failures
            request: Original user request

        Returns:
            SABAR-formatted refusal message
        """
        message = "[VOID] Cannot safely complete this request.\n\n"
        message += "[SABAR PROTOCOL]\n"
        message += "STOP: The following constitutional floors failed:\n"
        for failure in failures:
            message += f"  • {failure}\n"
        message += "\n"
        message += "ACKNOWLEDGE: I cannot proceed with this operation as stated.\n\n"
        message += "BREATHE: Let me suggest an alternative approach:\n"
        message += "  • Could you clarify which file you meant?\n"
        message += "  • Would you like me to create the file first?\n"
        message += "  • Should we verify the current state before making changes?\n\n"
        message += "ADJUST: Please rephrase your request with more specifics.\n\n"
        message += "RESUME: Once we clarify, I can help safely."

        return message

    def _create_void_response(
        self,
        reason: str,
        user_request: str,
        phase: str
    ) -> Dict:
        """
        Create VOID response for pre-execution failures.

        Args:
            reason: Reason for VOID
            user_request: User's request
            phase: Phase where failure occurred

        Returns:
            VOID response dict
        """
        return {
            "verdict": "VOID",
            "response": f"[VOID] {phase} check failed:\n{reason}\n\n[SABAR] Cannot proceed safely.",
            "file_operations": [],
            "metrics": None,
            "floor_failures": [reason],
            "ledger_entry_id": f"{phase}_void_{time.time()}",
            "execution_time": 0.0,
            "phase": phase
        }
