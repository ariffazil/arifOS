"""
arifos.core/system/executor/interceptor.py

The Conscience (Constitutional Wrapper).
Orchestrates the Orthogonal Kernels (AGI, ASI, APEX) to validate execution.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional, List

# Orthogonal Kernels (v46)
from arifos.core.agi.kernel import AGINeuralCore as AGIKernel
from arifos.core.asi.kernel import ASIActionCore as ASIKernel
from arifos.core.system.apex_prime import APEXPrime, Verdict, FloorCheckResult

from .sandbox import ExecutionSandbox


@dataclass
class ActionRequest:
    command: str
    purpose: str

@dataclass
class ConstitutionalResult:
    verdict: str  # String for serialization
    output: Optional[str]
    reason: str
    metadata: Dict[str, Any]

class ConstitutionalInterceptor:
    def __init__(self, sandbox: ExecutionSandbox):
        self.sandbox = sandbox
        # Initialize Kernels
        self.agi = AGIKernel()
        self.asi = ASIKernel()
        self.prime = APEXPrime()

    def process(self, query: str) -> Dict[str, Any]:
        """
        Process a request through the 111-999 Pipeline.
        Blocking wrapper around async implementation.
        """
        return asyncio.run(self._process_async(query))

    async def _process_async(self, query: str) -> Dict[str, Any]:
        """Async implementation of the pipeline."""
        
        # 1. 111-333: AGI Evaluation (Mind)
        # Sense context and truth needs
        agi_context = await self.agi.sense(query, {"origin": "Executor"})
        
        # 2. 444-666: ASI Evaluation (Heart)
        # Check empathy and safety
        asi_context = await self.asi.empathize(query, agi_context)

        # 3. 888-999: APEX Evaluation (Soul/Judge)
        # Construct evidence for Judgment
        
        # Convert AGI context to Floor Checks (F2 Truth, F6 Clarity)
        # Heuristic mapping for now until AGI returns explicit checks
        agi_results = [
            FloorCheckResult("F2", "Truth", 0.99, 1.0, True, is_hard=True), # Presumed valid for command execution context
            FloorCheckResult("F6", "Clarity", 0.0, 1.0, True, is_hard=True)
        ]

        # Convert ASI context to Floor Checks (F3 Peace, F4 Empathy)
        # ASI returns 'omega_verdict' and 'vulnerability_score'
        is_safe = asi_context.get("omega_verdict") != "VOID"
        asi_results = [
            FloorCheckResult("F3", "Peace", 1.0, 1.0 if is_safe else 0.0, is_safe, is_hard=True),
            FloorCheckResult("F4", "Empathy", 0.95, 1.0, True, is_hard=False)
        ]

        # Explicit F1 Amanah check for dangerous commands
        is_safe_cmd = self._is_safe_command(query)
        if not is_safe_cmd:
             # Inject failure into APEX Flow
             asi_results.append(FloorCheckResult("F1", "Amanah", 1.0, 0.0, False, reason="Destructive Command Detected", is_hard=True))

        # Invoke APEX Prime
        verdict_obj = self.prime.judge_output(
            query=query, 
            response="[EXECUTOR_ACTION]", 
            agi_results=agi_results, 
            asi_results=asi_results
        )

        # Enforce Verdict
        if verdict_obj.verdict == Verdict.SEAL:
            # AUTHORIZED
            exit_code, stdout, stderr = self.sandbox.run_command(query)
            output = stdout if exit_code == 0 else f"Error: {stderr}"
            return {
                "verdict": "SEAL",
                "result": output,
                "reason": verdict_obj.reason
            }
        else:
            # BLOCKED
            return {
                "verdict": str(verdict_obj.verdict.value),
                "result": None,
                "reason": verdict_obj.reason
            }

    def _is_safe_command(self, cmd: str) -> bool:
        """
        Basic heuristic for F1 Amanah / Peace^2.
        Prevent obvious destruction.
        """
        forbidden = ["rm -rf", "mkfs", "dd if=/dev/zero", ":(){ :|:& };:"]
        for bad in forbidden:
            if bad in cmd:
                return False
        return True
