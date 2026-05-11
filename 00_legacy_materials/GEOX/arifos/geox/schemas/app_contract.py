from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field


class AppAuthMode(Enum):
    PUBLIC = "public"
    OAUTH = "oauth"
    SOVEREIGN = "sovereign"


class HostRenderingMode(Enum):
    ADAPTIVE_CARD = "adaptive_card"
    IFRAME_WEB_SHELL = "iframe_web_shell"
    STATIC_JSON = "static_json"


class GeoxAppContract(BaseModel):
    """
    Canonical GEOX App Contract (F11 Authority).
    Defines the stable boundary between a GEOX app and its host.
    """

    app_id: str = Field(..., description="Unique slug for the app")
    app_version: str = Field("0.1.0", description="SemVer version")
    domain: Literal["seismic", "basin", "well", "document", "generic"] = "generic"

    # Capability Requirements
    required_tools: list[str] = Field(default_factory=list)
    optional_tools: list[str] = Field(default_factory=list)

    # UI Surface
    ui_entry: str = Field(..., description="URI to the UI entry point (resource path)")
    preferred_rendering: HostRenderingMode = HostRenderingMode.IFRAME_WEB_SHELL
    fallback_mode: HostRenderingMode = HostRenderingMode.STATIC_JSON

    # Security & Policy
    auth_mode: AppAuthMode = AppAuthMode.SOVEREIGN
    ui_permissions: list[str] = Field(default_factory=list)
    csp_allowlist: list[str] = Field(default_factory=list)

    # Lifecycle & Events
    event_types: list[str] = Field(
        default_factory=lambda: [
            "initialize",
            "context.patch",
            "ui.action",
            "ui.state.sync",
        ]
    )

    class ConfigDict:
        use_enum_values = True


class GeoxEvent(BaseModel):
    """Canonical event structure for the app-host bridge."""

    event_id: str
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(..., description="ISO8601 UTC")
    audit_id: str | None = None
