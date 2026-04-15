"""
tests/runtime/test_chatgpt_apps_integration.py — ChatGPT Apps SDK Integration Tests
"""

import pytest
from unittest.mock import Mock


class TestVaultSealWidget:
    """Test vault seal widget HTML generation"""

    def test_vault_seal_widget_html_exists(self):
        """Test widget HTML is returned and contains required elements"""
        from arifosmcp.runtime.chatgpt_integration.apps_sdk_tools import vault_seal_widget_html

        html = vault_seal_widget_html()
        assert isinstance(html, str)
        assert len(html) > 100
        assert "<!DOCTYPE html>" in html or "<html" in html

    def test_vault_seal_widget_has_csp(self):
        """Test widget HTML includes CSP metadata"""
        from arifosmcp.runtime.chatgpt_integration.apps_sdk_tools import vault_seal_widget_html

        html = vault_seal_widget_html()
        assert "Content-Security-Policy" in html

    def test_vault_seal_widget_has_domain(self):
        """Test widget HTML includes domain metadata"""
        from arifosmcp.runtime.chatgpt_integration.apps_sdk_tools import vault_seal_widget_html

        html = vault_seal_widget_html()
        assert "arifosmcp.arif-fazil.com" in html

    def test_vault_seal_widget_has_chatgpt_frame_ancestor(self):
        """Test widget allows chatgpt.com in frame-ancestors"""
        from arifosmcp.runtime.chatgpt_integration.apps_sdk_tools import vault_seal_widget_html

        html = vault_seal_widget_html()
        assert "https://chatgpt.com" in html


class TestRegisterChatgptAppTools:
    """Test ChatGPT App tool registration"""

    def test_register_chatgpt_app_tools_runs(self):
        """Test registration function executes without error"""
        from arifosmcp.runtime.chatgpt_integration.apps_sdk_tools import register_chatgpt_app_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test-chatgpt")
        register_chatgpt_app_tools(mcp)
        # If no exception, registration succeeded
        assert True

    def test_build_structured_content(self):
        """Test structured content builder returns valid data"""
        from arifosmcp.runtime.chatgpt_integration.apps_sdk_tools import _build_vault_seal_structured_content

        result = _build_vault_seal_structured_content(verdict="SEAL")
        assert isinstance(result, dict)
        assert result["verdict"] == "SEAL"
        assert "seal_id" in result
        assert "floors" in result
        assert "bls" in result
        assert "witness" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
