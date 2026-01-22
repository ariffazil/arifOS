import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from arifos.core.integration.composio.client import client as composio_client

from .governance import governance
from .tool_registry import registry

app = FastAPI(title="arifOS OpenAI Gateway", version="1.0.0")

# Models
class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    approval_token: Optional[str] = None
    request_id: Optional[str] = None

class ToolCallResponse(BaseModel):
    verdict: str
    tool_result: Optional[Any]
    floor_scores: Dict[str, float]
    ledger_hash: Optional[str]
    reasons: List[str]

@app.get("/health")
def health_check():
    return {
        "status": "SEAL",
        "version": "v50.0.0",
        "service": "openai-gateway",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/tools")
def list_tools():
    """Return tools in OpenAI JSON Schema format."""
    return registry.get_openai_tools()

@app.post("/call", response_model=ToolCallResponse)
def call_tool(req: ToolCallRequest):
    """
    Execute tool with full arifOS governance.
    1. Preflight (F1/F12/Risk)
    2. Execution (Composio)
    3. Postflight (F2/F9)
    4. Audit (Ledger)
    """

    # 1. Preflight
    pre = governance.preflight(req.tool_name, req.arguments, req.approval_token)

    if pre["verdict"] in ["VOID", "888_HOLD"]:
        ledger_hash = governance.log_to_ledger(req.tool_name, req.arguments, pre["verdict"], pre["reason"])
        return {
            "verdict": pre["verdict"],
            "tool_result": None,
            "floor_scores": pre["floor_scores"],
            "ledger_hash": ledger_hash,
            "reasons": [pre["reason"]]
        }

    # 2. Execution
    try:
        slug = registry.get_composio_slug(req.tool_name)
        result = composio_client.execute(slug, req.arguments)
    except Exception as e:
        # Runtime failure (F5 Peace violation)
        ledger_hash = governance.log_to_ledger(req.tool_name, req.arguments, "VOID", f"Execution error: {str(e)}")
        return {
            "verdict": "VOID",
            "tool_result": None,
            "floor_scores": pre["floor_scores"],
            "ledger_hash": ledger_hash,
            "reasons": [f"Execution failed: {str(e)}"]
        }

    # 3. Postflight
    post = governance.postflight(req.tool_name, result)

    # Final Ledger Entry
    final_verdict = post["verdict"] if post["verdict"] != "SEAL" else "SEAL"
    ledger_hash = governance.log_to_ledger(req.tool_name, req.arguments, final_verdict, str(result)[:100])

    return {
        "verdict": final_verdict,
        "tool_result": result,
        "floor_scores": {**pre["floor_scores"], **post["floor_scores"]},
        "ledger_hash": ledger_hash,
        "reasons": [pre["reason"], post["reason"]]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
