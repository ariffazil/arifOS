import asyncio

from arifosmcp.runtime.chatgpt_integration.apps_sdk_tools import (
    _build_vault_seal_structured_content,
)
from arifosmcp.runtime.server import app, mcp
from tests.conftest import SyncASGIClient


def test_vault_seal_structured_content_contract():
    payload = _build_vault_seal_structured_content(verdict="SEAL")
    assert payload["verdict"] == "SEAL"
    assert "seal_id" in payload
    assert "summary" in payload
    assert "floors" in payload
    assert "witness" in payload
    assert "zkpc" in payload


def test_chatgpt_widget_preview_route():
    client = SyncASGIClient(app)
    response = client.get("/chatgpt/widgets/vault-seal.html")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Constitutional Health Check" in response.text
    assert "renderFromToolResult" in response.text


def test_chatgpt_app_tools_registered():
    """Verify the 13 canonical arif_* tools are registered on the MCP server."""
    tools = asyncio.run(mcp.list_tools())
    names = {tool.name for tool in tools}
    canonical_13 = {
        "arif_evidence_fetch",
        "arif_forge_execute",
        "arif_gateway_connect",
        "arif_heart_critique",
        "arif_judge_deliberate",
        "arif_kernel_route",
        "arif_memory_recall",
        "arif_mind_reason",
        "arif_ops_measure",
        "arif_reply_compose",
        "arif_sense_observe",
        "arif_session_init",
        "arif_vault_seal",
    }
    assert canonical_13.issubset(names), f"Missing: {canonical_13 - names}"
