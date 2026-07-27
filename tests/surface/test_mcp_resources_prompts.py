"""Regression test for MCP resources + prompts exposure.

Audit finding (GPT-5.6 external probe, 2026-07-27):
  - MCP resources/list returned 0 entries — kernel advertised tools but no
    resources/prompts.
  - resources.py and prompts.py defined @mcp.resource / @mcp.prompt decorators
    inside register_*_arifos_*(mcp) functions, but those functions were never
    called on the canonical kernel mcp instance.

Fix (2026-07-27):
  - server.py now imports register_arifos_resources and register_arifos_prompts
    and calls them after register_tools(mcp).
  - resources.py had a FastMCP 3.x bug: URI templates must contain at least
    one `{param}`. The OpenCode INIT-prompt loop used static-name interpolation
    `f"arifos://init/opencode/{name.lower()}"` which produced templates with no
    parameters. Refactored to a single templated resource with `{name}` param.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import pytest

EXPECTED_MIN_RESOURCES = 5
EXPECTED_MIN_PROMPTS = 13


class TestMCPResources:
    def test_resources_module_exposes_register_function(self):
        from arifosmcp.runtime.fastmcp_ext.resources import register_arifos_resources
        assert callable(register_arifos_resources)

    def test_resources_register_on_test_mcp(self):
        from fastmcp import FastMCP

        from arifosmcp.runtime.fastmcp_ext.resources import register_arifos_resources

        mcp = FastMCP("test-resources")
        registered = register_arifos_resources(mcp)
        assert isinstance(registered, list)
        assert len(registered) >= EXPECTED_MIN_RESOURCES, (
            f"resources: got {len(registered)}, expected >= {EXPECTED_MIN_RESOURCES}"
        )

    def test_resources_include_canonical_uris(self):
        from fastmcp import FastMCP

        from arifosmcp.runtime.fastmcp_ext.resources import register_arifos_resources

        mcp = FastMCP("test-resources-uri")
        registered = register_arifos_resources(mcp)
        # Spot-check: verdict + continuity + init paths must be present
        assert any("verdict" in r for r in registered), (
            f"verdict resource missing from {registered}"
        )
        assert any("continuity" in r for r in registered), (
            f"continuity resource missing from {registered}"
        )
        assert any("init" in r for r in registered), (
            f"init resource missing from {registered}"
        )

    def test_init_resource_uses_template_parameter(self):
        """FastMCP 3.x requires URI templates with at least one {param}.

        The 2026-07-27 audit caught a regression where the OpenCode INIT
        loop used `f"arifos://init/opencode/{name.lower()}"` which produces
        no template parameter.
        """
        from fastmcp import FastMCP

        from arifosmcp.runtime.fastmcp_ext.resources import register_arifos_resources

        mcp = FastMCP("test-init-template")
        registered = register_arifos_resources(mcp)
        # The init resource must be templated with {name}
        init_uris = [r for r in registered if "init" in r.lower()]
        assert init_uris, "no init resource registered"
        # At least one init resource must have a {param}
        assert any("{" in uri and "}" in uri for uri in init_uris), (
            f"init resource URIs must include {{param}}: {init_uris}"
        )


class TestMCPPrompts:
    def test_prompts_module_exposes_register_function(self):
        from arifosmcp.runtime.fastmcp_ext.prompts import register_arifos_prompts
        assert callable(register_arifos_prompts)

    def test_prompts_register_on_test_mcp(self):
        from fastmcp import FastMCP

        from arifosmcp.runtime.fastmcp_ext.prompts import register_arifos_prompts

        mcp = FastMCP("test-prompts")
        registered = register_arifos_prompts(mcp)
        assert isinstance(registered, list)
        assert len(registered) >= EXPECTED_MIN_PROMPTS, (
            f"prompts: got {len(registered)}, expected >= {EXPECTED_MIN_PROMPTS}"
        )


class TestKernelServerWiresResources:
    """Verify that arifosmcp.server (the canonical kernel main) registers
    resources and prompts during boot."""

    def test_server_imports_resource_and_prompt_registrars(self):
        import inspect

        import arifosmcp.server as server_mod
        source = inspect.getsource(server_mod)
        assert "register_arifos_resources" in source, (
            "server.py does not call register_arifos_resources — resources will not "
            "appear on the live MCP surface"
        )
        assert "register_arifos_prompts" in source, (
            "server.py does not call register_arifos_prompts — prompts will not "
            "appear on the live MCP surface"
        )

    def test_server_module_imports_cleanly(self):
        import arifosmcp.server  # noqa: F401
