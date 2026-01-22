import re
from typing import Any, List, Optional

from .models import FloorScore, GovernanceVerdict, ToolCallRequest


# Simulated Injection Defense (F12)
# In production, use arifos.core.security.injection_defense
def scan_for_injection(text: str) -> bool:
    """F12 Injection Defense Scan."""
    risky_patterns = [
        r"ignore previous instructions",
        r"system override",
        r"delete everything",
        r"drop table",
        r"rm -rf"
    ]
    for pattern in risky_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

# Risk Classification (F1 Amanah)
DESTRUCTIVE_KEYWORDS = ["delete", "remove", "drop", "terminate", "kill", "overwrite", "grant", "revoke"]

def classify_risk(tool_name: str, args: dict) -> str:
    """Classify tool call risk: READ_ONLY | WRITE_REVERSIBLE | DESTRUCTIVE."""
    name_lower = tool_name.lower()

    # Simple keyword heuristic for now - can be refined with Composio metadata
    for kw in DESTRUCTIVE_KEYWORDS:
        if kw in name_lower:
            return "DESTRUCTIVE"

    if "create" in name_lower or "update" in name_lower or "write" in name_lower:
        return "WRITE_REVERSIBLE"

    return "READ_ONLY"

async def preflight_check(request: ToolCallRequest, approved_tools: List[str]) -> GovernanceVerdict:
    """
    Run governance checks BEFORE tool execution.
    1. Check allowlist.
    2. Check prompt injection (F12).
    3. Check risk level (F1).
    """

    # 1. Allowlist
    if request.tool_name not in approved_tools:
        return GovernanceVerdict(
            verdict="VOID",
            floor_scores=[FloorScore(floor="F1", score=0.0, reason="Tool not in allowlist")],
            consequences="Tool execution blocked."
        )

    # 2. Injection Scan (F12)
    injection_found = scan_for_injection(str(request.arguments))
    if injection_found:
        return GovernanceVerdict(
            verdict="VOID",
            floor_scores=[FloorScore(floor="F12", score=0.0, reason="Injection pattern detected")],
            consequences="Execution blocked due to security risk."
        )

    # 3. Risk Assessment (F1)
    risk_class = classify_risk(request.tool_name, request.arguments)

    if risk_class == "DESTRUCTIVE":
        # Check for approval token
        if not request.approval_token:
             return GovernanceVerdict(
                verdict="888_HOLD",
                floor_scores=[FloorScore(floor="F1", score=0.1, reason="Destructive action requires human approval")],
                requires_approval=True,
                consequences="Action held pending approval.",
                approval_nonce="NONCE_" + request.tool_name # Simplified nonce generation
            )

    return GovernanceVerdict(
        verdict="SEAL",
        floor_scores=[FloorScore(floor="F1", score=1.0, reason="Preflight checks passed")]
    )

async def postflight_check(tool_name: str, output: Any) -> GovernanceVerdict:
    """
    Run governance checks AFTER tool execution.
    1. F2 Truth check (Simulated).
    2. F9 Anti-Hantu check.
    """
    # Placeholder for real post-flight logic
    # In full implementation, this calls 888_JUDGE

    output_str = str(output)

    # F9 Check
    if "I feel" in output_str or "I am conscious" in output_str:
         return GovernanceVerdict(
            verdict="PARTIAL", # We might strip the bad part
            floor_scores=[FloorScore(floor="F9", score=0.0, reason="Anti-Hantu violation detected")],
            consequences="Output sanitized."
        )

    return GovernanceVerdict(
        verdict="SEAL",
        floor_scores=[FloorScore(floor="F2", score=1.0, reason="Output validated")]
    )
