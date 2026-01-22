import hashlib
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from arifos.core.mcp.immutable_ledger import ImmutableLedger

from .tool_registry import registry


class GovernanceAdapter:
    def __init__(self):
        self.ledger = ImmutableLedger() # Uses defaults, persists to memory unless path set
        # For production persistence, we should set a path, e.g.:
        # self.ledger = ImmutableLedger(persist_path=Path("VAULT999/gateway_ledger"))

    def _scan_injection(self, text: str) -> bool:
        """F12 Injection Defense."""
        risky = [
            r"ignore previous instructions",
            r"system override",
            r"delete everything",
            r"rm -rf"
        ]
        for p in risky:
            if re.search(p, text, re.IGNORECASE):
                return True
        return False

    def preflight(self, tool_name: str, args: Dict[str, Any], approval_token: Optional[str]) -> Dict[str, Any]:
        """
        Run Preflight Governance checks.
        Returns verdict dict.
        """
        # 1. Injection Scan (F12)
        if self._scan_injection(str(args)):
            return {
                "verdict": "VOID",
                "reason": "F12: Injection pattern detected",
                "floor_scores": {"F12": 0.0}
            }

        # 2. Risk Gating (F1)
        risk_class = registry.get_risk_class(tool_name)

        if risk_class in ["WRITE_REVERSIBLE", "DESTRUCTIVE"]:
            # Check for approval token
            # Simple nonce verification for MVP
            expected_token = f"PERMIT_{tool_name}"
            if approval_token != expected_token:
                 return {
                    "verdict": "888_HOLD",
                    "reason": f"F1: {risk_class} action requires approval. Context: {tool_name}",
                    "floor_scores": {"F1": 0.1},
                    "required_token_format": f"PERMIT_{tool_name}" # In real system, this is a distinct flow
                }

        return {
            "verdict": "SEAL",
            "reason": "Preflight passed",
            "floor_scores": {"F1": 1.0, "F12": 1.0}
        }

    def postflight(self, tool_name: str, result: Any) -> Dict[str, Any]:
        """
        Run Postflight Governance checks.
        """
        # F9 Anti-Hantu
        res_str = str(result)
        if "I feel" in res_str:
            return {
                 "verdict": "PARTIAL",
                 "reason": "F9: Anti-Hantu violation",
                 "floor_scores": {"F9": 0.0}
            }

        return {
            "verdict": "SEAL",
            "reason": "Postflight passed",
            "floor_scores": {"F2": 1.0, "F9": 1.0}
        }

    def log_to_ledger(self, tool_name: str, args: Dict[str, Any], verdict: str, result_summary: str) -> str:
        """
        Append entry to immutable ledger.
        """
        query_sig = f"{tool_name}:{hashlib.sha256(str(args).encode()).hexdigest()}"

        return self.ledger.append(
            query=query_sig,
            verdict=verdict,
            metadata={"tool": tool_name, "summary": result_summary}
        )

governance = GovernanceAdapter()
