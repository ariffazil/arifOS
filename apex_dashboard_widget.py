"""
arifOS MCP - APEX Dashboard Widget (ChatGPT Apps SDK Format)
===================================================
This shows how to add GUI mode to existing arifOS MCP tools.

When user calls apex_judge with mode="gui", returns ChatGPT-renderable UI.
"""

# Example: Tool with GUI mode

from fastmcp import FastMCP

mcp = FastMCP("arifOS")

# Dashboard data (normally fetched from arifOS backend)
SAMPLE_DATA = {
    "system_name": "arifOS APEX",
    "updated_at": "2026-04-02 01:44 UTC",
    "status": {
        "system": "Operational",
        "governance": "Stable",
        "vault_integrity": 99.94,
        "active_sessions": 12,
        "policy_breaches_24h": 0,
        "approval_rate_7d": 93.2,
    },
    "governance_health": {
        "clarity": 91,
        "stability": 95,
        "judgment": 88,
        "human_override_respected": 100,
        "fail_closed_compliance": 97,
    },
    "recent_verdicts": [
        {"time": "09:14", "verdict": "Approved", "risk": "Low"},
        {"time": "08:52", "verdict": "Partial", "risk": "Medium"},
        {"time": "08:11", "verdict": "Pause", "risk": "Medium"},
        {"time": "07:39", "verdict": "Approved", "risk": "Low"},
    ],
}


@mcp.tool()
def apex_judge(
    action: str,
    context: dict | None = None,
    mode: str | None = None,  # "text" | "gui" | "telemetry"
) -> dict:
    """
    Constitutional verdict on proposed action.
    
    Args:
        action: The action to evaluate
        context: Additional context
        mode: Output format - "text" (default), "gui" (dashboard), "telemetry" (metrics)
    
    Returns:
        Full verdict with reasoning, or GUI dashboard if mode="gui"
    """
    # Default: return text verdict
    if mode != "gui":
        return {
            "verdict": "SEAL",
            "reasoning": "Action passes all 13 Floors",
            "confidence": 0.93,
            "telemetry": {
                "dS": -0.78,
                "peace2": 1.22,
                "kappa_r": 0.97,
            }
        }
    
    # GUI MODE: Return ChatGPT Apps SDK format
    # This renders the dashboard inline in ChatGPT
    return _build_dashboard_meta(SAMPLE_DATA)


def _build_dashboard_meta(data: dict) -> dict:
    """
    Build _meta output for ChatGPT Apps SDK.
    Returns structured content with widget metadata.
    """
    status = data["status"]
    health = data["governance_health"]
    
    # Build the UI components using the Apps SDK format
    return {
        # Standard response
        "verdict": "SEAL",
        "system": status["system"],
        "timestamp": data["updated_at"],
        
        # ChatGPT Apps SDK widget
        "_meta": {
            "outputType": "response",
            "outputTemplate": {
                "type": "container",
                "kind": "vstack",
                "children": [
                    # Header
                    {
                        "type": "component",
                        "kind": "text",
                        "text": f"🧠 {data['system_name']}",
                        "font": {"size": "xl", "weight": "bold"},
                    },
                    {
                        "type": "component", 
                        "kind": "text",
                        "text": f"Updated: {data['updated_at']}",
                        "color": "muted",
                    },
                    
                    # Status badges row
                    {
                        "type": "component",
                        "kind": "hstack",
                        "children": [
                            {
                                "type": "component",
                                "kind": "badge",
                                "label": f"System: {status['system']}",
                                "status": "primary",
                            },
                            {
                                "type": "component",
                                "kind": "badge", 
                                "label": f"Governance: {status['governance']}",
                                "status": "success" if status['governance'] == "Stable" else "warning",
                            },
                        ],
                    },
                    
                    # KPI Grid
                    {
                        "type": "component",
                        "kind": "grid",
                        "columns": 3,
                        "children": [
                            {
                                "type": "component",
                                "kind": "stat",
                                "title": "Vault Integrity",
                                "value": f"{status['vault_integrity']}%",
                            },
                            {
                                "type": "component",
                                "kind": "stat",
                                "title": "Approval Rate",
                                "value": f"{status['approval_rate_7d']}%",
                            },
                            {
                                "type": "component",
                                "kind": "stat",
                                "title": "Sessions",
                                "value": str(status['active_sessions']),
                            },
                        ],
                    },
                    
                    # Governance Health
                    {
                        "type": "component",
                        "kind": "text",
                        "text": "Governance Health",
                        "font": {"size": "lg", "weight": "semibold"},
                    },
                    {
                        "type": "component",
                        "kind": "progress",
                        "labels": ["Clarity", "Stability", "Judgment"],
                        "values": [health["clarity"], health["stability"], health["judgment"]],
                    },
                    
                    # Recent Verdicts
                    {
                        "type": "component",
                        "kind": "text",
                        "text": "Recent Verdicts",
                        "font": {"size": "lg", "weight": "semibold"},
                    },
                    {
                        "type": "component",
                        "kind": "table",
                        "columns": [
                            {"key": "time", "label": "Time"},
                            {"key": "verdict", "label": "Verdict"},
                            {"key": "risk", "label": "Risk"},
                        ],
                        "rows": data["recent_verdicts"],
                    },
                ],
            },
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp, host="0.0.0.0", port=3000)
