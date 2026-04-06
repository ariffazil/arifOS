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
    tools = asyncio.run(mcp.list_tools())
    names = {tool.name for tool in tools}
    assert "vault_seal_card" in names
    assert "render_vault_seal" in names
