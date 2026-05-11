# GEOX UI Event Contract — JSON-RPC Bridge

from typing import Literal
from pydantic import BaseModel, Field


class GeoxEvent(BaseModel):
    """Base class for all GEOX UI Bridge events."""

    jsonrpc: str = "2.0"
    id: int | None = None
    timestamp: str = Field(..., description="ISO 8601 timestamp of the event.")


class AppInitialize(GeoxEvent):
    """Emitted when the app is first mounted in the host."""

    method: Literal["app.initialize"] = "app.initialize"
    params: dict[str, any] = Field(
        ..., description="Initial context, user id, and host caps."
    )


class UIAction(GeoxEvent):
    """Emitted when a user interacts with the GEOX UI."""

    method: Literal["ui.action"] = "ui.action"
    params: dict[str, any] = Field(
        ..., description="Action name, coordinates, or payload."
    )


class UIStateSync(GeoxEvent):
    """Emitted to sync local app state (e.g. current slice) back to LLM context."""

    method: Literal["ui.state.sync"] = "ui.state.sync"
    params: dict[str, any] = Field(
        ..., description="The app state snippet for the LLM to remember."
    )


class ContextPatch(GeoxEvent):
    """Received by the app when the host environment changes (e.g. new prompt)."""

    method: Literal["app.context.patch"] = "app.context.patch"
    params: dict[str, any] = Field(..., description="The context update delta.")


class CallServerTool(GeoxEvent):
    """Emitted by the app to call an MCP tool via the host bridge (Standard FastMCP)."""

    method: Literal["callServerTool"] = "callServerTool"
    params: dict[str, any] = Field(..., description="Tool name and arguments.")
