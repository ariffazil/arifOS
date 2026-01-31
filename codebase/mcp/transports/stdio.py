"""
arifOS MCP Stdio Transport
Standard input/output transport for local clients (Claude Desktop, Cursor).

v55.1: Spec-compliant tool listing with outputSchema, annotations, title.
       Structured JSON output alongside human-readable text.
"""

import json as _json
import logging
import sys
import time
import mcp.types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from typing import Any

from .base import BaseTransport
from ..core.tool_registry import ToolRegistry
from ...enforcement.metrics import record_stage_metrics, record_verdict_metrics
from ...system.orchestrator.presenter import AAAMetabolizer
from ..services.constitutional_metrics import record_verdict
from ..config.modes import get_mcp_mode

logger = logging.getLogger(__name__)


class StdioTransport(BaseTransport):
    """Stdio transport implementation using mcp-python SDK."""

    def __init__(self, tool_registry: ToolRegistry):
        super().__init__(tool_registry)
        self.server = Server("arifOS-Stdio")
        self.presenter = AAAMetabolizer()

    @property
    def name(self) -> str:
        return "stdio"

    async def start(self) -> None:
        """Start the MCP server over stdio."""
        mode = get_mcp_mode()
        print(
            f"[BOOT] arifOS MCP v55.1 StdioTransport starting in {mode.value} mode",
            file=sys.stderr,
        )

        # Register handlers
        self._register_handlers()

        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream, self.server.create_initialization_options()
            )

    async def stop(self) -> None:
        pass  # Stdio server handles its own cleanup context

    async def send_response(self, request_id: str, response: Any) -> None:
        pass  # Handled internally by mcp server

    def _register_handlers(self):
        """Register tool handlers with the internal MCP server."""

        @self.server.list_tools()
        async def handle_list_tools() -> list[mcp.types.Tool]:
            tools = []
            for name, tool_def in self.tool_registry.list_tools().items():
                # Build ToolAnnotations from registry dict
                annotations = None
                if tool_def.annotations:
                    annotations = mcp.types.ToolAnnotations(
                        title=tool_def.annotations.get("title"),
                        readOnlyHint=tool_def.annotations.get("readOnlyHint"),
                        destructiveHint=tool_def.annotations.get("destructiveHint"),
                        idempotentHint=tool_def.annotations.get("idempotentHint"),
                        openWorldHint=tool_def.annotations.get("openWorldHint"),
                    )

                tools.append(
                    mcp.types.Tool(
                        name=tool_def.name,
                        title=tool_def.title,
                        description=tool_def.description,
                        inputSchema=tool_def.input_schema,
                        outputSchema=tool_def.output_schema,
                        annotations=annotations,
                    )
                )
            return tools

        # Phase 3: MCP Resources - Expose floor definitions and VAULT ledger
        @self.server.list_resources()
        async def handle_list_resources() -> list[mcp.types.Resource]:
            resources = []
            for res_def in self.resource_registry.list_resources():
                resources.append(
                    mcp.types.Resource(
                        uri=res_def.uri,
                        name=res_def.name,
                        description=res_def.description,
                        mimeType=res_def.mime_type,
                    )
                )
            return resources

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            return self.resource_registry.read_resource(uri)

        # Phase 3: MCP Prompts - Reusable constitutional templates
        @self.server.list_prompts()
        async def handle_list_prompts() -> list[mcp.types.Prompt]:
            prompts = []
            for prompt_def in self.prompt_registry.list_prompts():
                args = None
                if prompt_def.arguments:
                    args = [
                        mcp.types.PromptArgument(
                            name=arg["name"],
                            description=arg.get("description", ""),
                            required=arg.get("required", "false") == "true",
                        )
                        for arg in prompt_def.arguments
                    ]
                prompts.append(
                    mcp.types.Prompt(
                        name=prompt_def.name,
                        description=prompt_def.description,
                        arguments=args,
                    )
                )
            return prompts

        @self.server.get_prompt()
        async def handle_get_prompt(name: str, arguments: dict | None = None) -> str:
            return self.prompt_registry.render_prompt(name, arguments)

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict | None
        ) -> list[mcp.types.TextContent | mcp.types.ImageContent | mcp.types.EmbeddedResource]:
            start_time = time.time()
            arguments = arguments or {}
            tool_def = self.tool_registry.get(name)

            if not tool_def:
                raise ValueError(f"Tool not found: {name}")

            try:
                result = await tool_def.handler(**arguments)

                # Metrics
                duration = time.time() - start_time
                duration_ms = duration * 1000
                verdict = result.get("verdict", "UNKNOWN")
                mode = get_mcp_mode()

                record_verdict(tool=name, verdict=verdict, duration=duration, mode=mode.value)
                record_stage_metrics(name, duration_ms)
                record_verdict_metrics(verdict)

                # Return human-readable presentation + machine-readable JSON
                formatted_text = self.presenter.process(result)
                return [
                    mcp.types.TextContent(type="text", text=formatted_text),
                    mcp.types.TextContent(type="text", text=_json.dumps(result, default=str)),
                ]

            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [mcp.types.TextContent(type="text", text=f"ERROR: {str(e)}")]
