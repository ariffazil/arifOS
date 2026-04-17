"""
arifOS Tool Base Class
======================

All arifOS tools inherit from the Tool base class.
This ensures consistent behavior across all tools.

Status: PHASE 1 - Base class definition
Branch: refactor/v2.0-abi
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel

from arifosmcp.abi.v1_0 import get_request_schema, get_response_schema
from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict


class FloorResult:
    """Result of floor evaluation."""

    def __init__(
        self,
        verdict: Verdict,
        violations: list[str],
        message: str = ""
    ):
        self.verdict = verdict
        self.violations = violations
        self.message = message


class Tool(ABC):
    """
    Base class for all arifOS tools.

    All tools MUST:
    1. Define name, stage, and floors
    2. Implement execute() method
    3. Return RuntimeEnvelope

    Example:
    class MyTool(Tool):
        name = "my_tool"
        stage = "444_ROUTER"
        floors = ["F1", "F2", "F4"]

        async def execute(self, payload: dict) -> dict:
            return {"result": "..."}
    """

    # Tool metadata - MUST be overridden
    name: str = ""
    stage: str = ""
    floors: list[str] = []
    readonly: bool = True

    # Schema references (auto-loaded from ABI)
    request_schema: type[BaseModel] | None = None
    response_schema: type[BaseModel] | None = None

    def __init__(self):
        """Initialize tool with schema lookup."""
        if not self.name:
            raise ValueError(f"Tool {self.__class__.__name__} must define 'name'")
        if not self.stage:
            raise ValueError(f"Tool {self.name} must define 'stage'")

        # Auto-load schemas from ABI
        if self.request_schema is None:
            self.request_schema = get_request_schema(self.name)
        if self.response_schema is None:
            self.response_schema = get_response_schema(self.name)

    async def validate(self, payload: dict) -> BaseModel | dict:
        """
        Validate payload against request schema.

        Raises:
            ValueError: If validation fails
        """
        if self.request_schema:
            return self.request_schema(**payload)
        return payload

    async def check_floors(self, payload: dict) -> FloorResult:
        """
        Check constitutional floors before execution.

        Override to customize floor checking.
        """
        from core.floors import ConstitutionalFloors

        floors = ConstitutionalFloors()
        result = floors.evaluate(
            action=payload.get("query", ""),
            tool_name=self.name,
            parameters=payload,
            actor_id=payload.get("actor_id", "anonymous"),
            session_id=payload.get("session_id"),
        )

        return FloorResult(
            verdict=result.verdict,
            violations=result.violations,
            message=result.message,
        )

    @abstractmethod
    async def execute(self, payload: dict) -> dict:
        """
        Execute the tool with validated payload.

        Args:
            payload: Validated request payload

        Returns:
            Tool-specific result dictionary
        """
        pass

    async def run(
        self,
        payload: dict,
        session_id: str | None = None,
        auth_context: dict | None = None
    ) -> RuntimeEnvelope:
        """
        Run the tool with full governance.

        This is the main entry point for tool execution.
        It handles validation, floor checking, and execution.
        """
        import time
        start_time = time.time()

        try:
            # 1. Validate input
            validated = await self.validate(payload)

            # 2. Check floors
            floor_result = await self.check_floors(payload)

            # 3. If VOID, return early
            if floor_result.verdict == Verdict.VOID:
                return RuntimeEnvelope(
                    tool=self.name,
                    stage=self.stage,
                    status=RuntimeStatus.ERROR,
                    verdict=Verdict.VOID,
                    payload={"error": floor_result.message},
                    session_id=session_id,
                    latency_ms=(time.time() - start_time) * 1000
                )

            # 4. Execute
            result = await self.execute(
                validated.dict() if hasattr(validated, 'dict') else validated
            )

            # 5. If already a RuntimeEnvelope (from legacy delegates), pass through
            if isinstance(result, RuntimeEnvelope):
                result.latency_ms = (time.time() - start_time) * 1000
                return result

            # 6. Wrap dict result in envelope
            return RuntimeEnvelope(
                tool=self.name,
                stage=self.stage,
                status=RuntimeStatus.SUCCESS,
                verdict=floor_result.verdict,
                payload=result,
                session_id=session_id,
                latency_ms=(time.time() - start_time) * 1000
            )

        except Exception as e:
            return RuntimeEnvelope(
                tool=self.name,
                stage=self.stage,
                status=RuntimeStatus.ERROR,
                verdict=Verdict.VOID,
                payload={"error": str(e)},
                session_id=session_id,
                errors=[{"code": "EXECUTION_ERROR", "message": str(e)}],
                latency_ms=(time.time() - start_time) * 1000
            )


class ToolRegistry:
    """
    Central registry for all arifOS tools.

    Usage:
        # Register a tool
        ToolRegistry.register(MyTool())

        # Get a tool
        tool = ToolRegistry.get("my_tool")

        # List all tools
        tools = ToolRegistry.list_tools()
    """

    _tools: dict[str, Tool] = {}

    @classmethod
    def register(cls, tool: Tool) -> None:
        """Register a tool."""
        cls._tools[tool.name] = tool

    @classmethod
    def get(cls, name: str) -> Tool | None:
        """Get a tool by name."""
        return cls._tools.get(name)

    @classmethod
    def list_tools(cls) -> list[str]:
        """List all registered tool names."""
        return list(cls._tools.keys())

    @classmethod
    def get_tools_by_stage(cls, stage: str) -> list[Tool]:
        """Get all tools for a metabolic stage."""
        return [t for t in cls._tools.values() if t.stage == stage]

    @classmethod
    def clear(cls) -> None:
        """Clear all registered tools (for testing)."""
        cls._tools.clear()


__all__ = [
    "FloorResult",
    "Tool",
    "ToolRegistry",
]
