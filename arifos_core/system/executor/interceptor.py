"""
arifos_core/system/executor/interceptor.py

The Conscience (Constitutional Wrapper).
Orchestrates the Orthogonal Kernels (AGI, ASI, APEX) to validate execution.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

# Orthogonal Kernels
from arifos_core.agi.kernel import AGIKernel
from arifos_core.apex.kernel import APEXKernel, Verdict
from arifos_core.asi.kernel import ASIKernel

from .sandbox import ExecutionSandbox


@dataclass
class ActionRequest:
    command: str
    purpose: str

@dataclass
class ConstitutionalResult:
    verdict: Verdict
    output: Optional[str]
    reason: str
    metadata: Dict[str, Any]

class ConstitutionalInterceptor:
    def __init__(self, sandbox: ExecutionSandbox):
        self.sandbox = sandbox
        # Initialize Kernels
        self.agi = AGIKernel()
        self.asi = ASIKernel()
        self.apex = APEXKernel()

    def process(self, query: str) -> Dict[str, Any]:
        """
        Process a request through the 111-999 Pipeline.
        """

        # 1. 111-333: AGI Evaluation (Mind)
        # Placeholder: Assume standard scoring for now
        agi_verdict = self.agi.evaluate(
            query=query,
            response="[INTENT_CHECK]",
            truth_score=0.99 # Presume honest intent until proven otherwise
        )

        # 2. 444-666: ASI Evaluation (Heart)
        asi_verdict = self.asi.evaluate(
            peace_score=1.0, # Presume non-destructive
            empathy_score=0.95,
            humility_score=0.04
        )

        # 3. 888-999: APEX Evaluation (Soul/Judge)
        # F1/Amanah check: Detect destructive commands explicitly
        is_safe = self._is_safe_command(query)

        apex_verdict = self.apex.evaluate(
            amanah_check=is_safe,
            witness_score=1.0,
            c_dark_score=0.1
        )

        # Enforce Verdict
        if apex_verdict.verdict == Verdict.SEAL:
            # AUTHORIZED
            exit_code, stdout, stderr = self.sandbox.run_command(query)
            output = stdout if exit_code == 0 else f"Error: {stderr}"
            return {
                "verdict": "SEAL",
                "result": output,
                "reason": "Constitutional Execution Approved"
            }
        else:
            # BLOCKED
            return {
                "verdict": str(apex_verdict.verdict),
                "result": None,
                "reason": apex_verdict.reason
            }

    def _is_safe_command(self, cmd: str) -> bool:
        """
        Basic heuristic for F1 Amanah / Peace^2.
        Prevent obvious destruction.
        """
        forbidden = ["rm -rf", "mkfs", "dd if=/dev/zero"]
        for bad in forbidden:
            if bad in cmd:
                return False
        return True
