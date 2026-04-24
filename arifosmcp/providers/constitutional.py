"""
ConstitutionalProvider — F1–F13 Floor Enforcer
════════════════════════════════════════════════

Wraps any Provider and enforces constitutional floor checks at
registration (list/get) and call (run) time.
"""
from __future__ import annotations

import logging
from typing import Any

from fastmcp.server.providers import Provider
from fastmcp.tools.tool import Tool, ToolResult
from mcp.types import TextContent

from arifosmcp.constitutional_map import CANONICAL_TOOLS
from arifosmcp.runtime.floors import check_floors

logger = logging.getLogger(__name__)


class _ConstitutionalTool(Tool):
    """Tool wrapper that injects floor checks before execution."""

    _original_name: str
    _inner: Tool
    _actor_id: str | None

    def __init__(self, inner: Tool, actor_id: str | None = None) -> None:
        super().__init__(
            name=inner.name,
            description=inner.description,
            parameters=inner.parameters,
            output_schema=inner.output_schema,
            tags=inner.tags,
            annotations=inner.annotations,
            task_config=inner.task_config,
            execution=inner.execution,
            meta=inner.get_meta(),
            title=inner.title,
            icons=inner.icons,
            version=inner.version,
            auth=inner.auth,
            timeout=inner.timeout,
        )
        self._inner = inner
        self._original_name = inner.name
        self._actor_id = actor_id

    async def run(self, arguments: dict[str, Any]) -> ToolResult:
        spec = CANONICAL_TOOLS.get(self._original_name)
        if spec is None:
            logger.warning(
                f"[ConstitutionalProvider] Tool '{self._original_name}' not in CANONICAL_TOOLS; "
                "blocking unregistered tool."
            )
            return ToolResult(
                content=[TextContent(type="text", text="VOID: Tool not canonical.")],
                structured_content={"verdict": "VOID", "reason": "F10: Unregistered tool"},
            )

        floor_result = check_floors(self._original_name, arguments, self._actor_id)
        if floor_result["verdict"] != "SEAL":
            logger.warning(
                f"[ConstitutionalProvider] {self._original_name} HOLD: {floor_result['reason']}"
            )
            return ToolResult(
                content=[TextContent(type="text", text=f"HOLD: {floor_result['reason']}")],
                structured_content={
                    "verdict": floor_result["verdict"],
                    "reason": floor_result["reason"],
                    "failed_floors": floor_result.get("failed_floors", []),
                },
            )

        return await self._inner.run(arguments)


class ConstitutionalProvider(Provider):
    """
    Wraps any Provider and enforces F1–F13 floor checks.

    - Registration time: validates tool exists in CANONICAL_TOOLS.
    - Call time: runs check_floors before delegating to inner tool.
    """

    def __init__(self, provider: Provider, actor_id: str | None = None) -> None:
        super().__init__()
        self._provider = provider
        self._actor_id = actor_id

    def __repr__(self) -> str:
        return f"ConstitutionalProvider({self._provider!r})"

    def _wrap(self, tool: Tool | None) -> Tool | None:
        if tool is None:
            return None
        return _ConstitutionalTool(tool, actor_id=self._actor_id)

    async def _list_tools(self) -> list[Tool]:
        tools = await self._provider._list_tools()
        wrapped: list[Tool] = []
        for t in tools:
            if t.name not in CANONICAL_TOOLS:
                logger.warning(
                    f"[ConstitutionalProvider] Dropping unregistered tool '{t.name}' at list time."
                )
                continue
            wrapped.append(self._wrap(t))
        return wrapped

    async def _get_tool(
        self, name: str, version: Any = None
    ) -> Tool | None:
        if name not in CANONICAL_TOOLS:
            logger.warning(
                f"[ConstitutionalProvider] Blocking unregistered tool '{name}' at get time."
            )
            return None
        tool = await self._provider._get_tool(name, version)
        return self._wrap(tool)

    async def get_app_tool(self, app_name: str, tool_name: str) -> Tool | None:
        tool = await self._provider.get_app_tool(app_name, tool_name)
        return self._wrap(tool)

    async def _list_resources(self) -> list[Any]:
        return list(await self._provider._list_resources())

    async def _get_resource(self, uri: str, version: Any = None) -> Any | None:
        return await self._provider._get_resource(uri, version)

    async def _list_resource_templates(self) -> list[Any]:
        return list(await self._provider._list_resource_templates())

    async def _get_resource_template(self, uri: str, version: Any = None) -> Any | None:
        return await self._provider._get_resource_template(uri, version)

    async def _list_prompts(self) -> list[Any]:
        return list(await self._provider._list_prompts())

    async def _get_prompt(self, name: str, version: Any = None) -> Any | None:
        return await self._provider._get_prompt(name, version)
