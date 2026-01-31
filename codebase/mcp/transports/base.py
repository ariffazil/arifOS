"""
arifOS MCP Base Transport
Abstract Base Class for all MCP transports.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..core.tool_registry import ToolRegistry
from ..core.resource_registry import ResourceRegistry
from ..core.prompt_registry import PromptRegistry


class BaseTransport(ABC):
    """Abstract transport layer - all transports implement this."""

    def __init__(
        self,
        tool_registry: ToolRegistry,
        resource_registry: Optional[ResourceRegistry] = None,
        prompt_registry: Optional[PromptRegistry] = None
    ):
        self.tool_registry = tool_registry
        self.resource_registry = resource_registry or ResourceRegistry()
        self.prompt_registry = prompt_registry or PromptRegistry()

    @abstractmethod
    async def start(self) -> None:
        """Start the transport, registering all tools from the registry."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Gracefully shut down the transport."""
        ...

    @abstractmethod
    async def send_response(self, request_id: str, response: Dict[str, Any]) -> None:
        """Send a response back to the client."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Transport identifier (e.g., 'stdio', 'sse', 'http')."""
        ...
