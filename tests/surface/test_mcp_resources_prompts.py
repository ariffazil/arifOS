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
    """Audit 2026-07-28 Phase C: the canonical server.py must invoke
    register_public_resources_and_prompts(server) — ONE explicit call,
    no import side effects, no hidden singleton assumption.

    The test invokes the actual canonical server boot path (or a test
    instance bound to the same registration function) — not a stand-in
    FastMCP stub.
    """

    def test_server_calls_explicit_registration_function(self):
        import inspect

        import arifosmcp.server as server_mod
        source = inspect.getsource(server_mod)
        # The auditor's strict requirement: exactly one explicit function call.
        assert "register_public_resources_and_prompts" in source, (
            "server.py does not call register_public_resources_and_prompts — "
            "resources + prompts will not appear on the live MCP surface"
        )
        # The two lower-level functions must NOT be called directly from server.py
        # (that would be the import-side-effect pattern the audit rejected).
        assert "register_arifos_resources(" not in source, (
            "server.py still calls register_arifos_resources() directly — "
            "consolidate into register_public_resources_and_prompts() per audit"
        )
        assert "register_arifos_prompts(" not in source, (
            "server.py still calls register_arifos_prompts() directly — "
            "consolidate into register_public_resources_and_prompts() per audit"
        )

    def test_explicit_registration_function_returns_dict(self):
        from fastmcp import FastMCP

        from arifosmcp.runtime.fastmcp_ext import (
            register_public_resources_and_prompts,
        )

        mcp = FastMCP("test-canonical-server")
        result = register_public_resources_and_prompts(mcp)
        assert isinstance(result, dict)
        assert "resources" in result
        assert "prompts" in result
        assert "errors" in result
        assert len(result["resources"]) >= 5
        assert len(result["prompts"]) >= 13
        assert result["errors"] == [], f"unexpected errors: {result['errors']}"

    def test_canonical_server_registers_on_test_mcp(self):
        """Re-invoke the canonical server's boot path on a test mcp.

        This simulates: server.py's `mcp = FastMCP("ARIFOS MCP")` and the
        subsequent `register_public_resources_and_prompts(mcp)` call.
        """
        from fastmcp import FastMCP

        from arifosmcp.runtime.fastmcp_ext import (
            register_public_resources_and_prompts,
        )

        # Use the same FastMCP name as the canonical server (arifosmcp/server.py:512).
        canonical = FastMCP("ARIFOS MCP")
        result = register_public_resources_and_prompts(canonical)
        # Acceptance: ≥ 5 resources, ≥ 13 prompts on the canonical instance.
        assert len(result["resources"]) >= 5
        assert len(result["prompts"]) >= 13

    def test_server_module_imports_cleanly(self):
        import arifosmcp.server  # noqa: F401
