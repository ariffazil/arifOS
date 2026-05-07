"""
GEOX App Manifest — Python types for canonical app manifest.
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum


from pydantic import BaseModel, ConfigDict, Field, HttpUrl


# ═══════════════════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════════════════


class Dimension(str, Enum):
    """The 7 canonical dimensions of GEOX."""

    PROSPECT = "PROSPECT"
    WELL = "WELL"
    SECTION = "SECTION"
    EARTH_3D = "EARTH_3D"
    TIME_4D = "TIME_4D"
    PHYSICS = "PHYSICS"
    MAP = "MAP"


class AppDomain(str, Enum):
    """Functional domains for GEOX apps."""

    SEISMIC = "seismic"
    PETROPHYSICS = "petrophysics"
    GEOLOGY = "geology"
    ECONOMICS = "economics"
    GOVERNANCE = "governance"
    GENERAL = "general"


class UiMode(str, Enum):
    """UI rendering modes."""

    INLINE = "inline"
    EXTERNAL = "external"
    INLINE_OR_EXTERNAL = "inline-or-external"


class Capability(str, Enum):
    """Browser capabilities apps may require."""

    EMBEDDED_WEBVIEW = "embedded_webview"
    WEBGL = "webgl"
    WEBGL2 = "webgl2"
    WASM = "wasm"
    WEBRTC = "webrtc"
    FILE_SYSTEM = "file_system"
    NOTIFICATIONS = "notifications"


class AuthMode(str, Enum):
    """Authentication modes."""

    JWT = "jwt"
    SESSION = "session"
    NONE = "none"


class EventType(str, Enum):
    """Canonical event types for host-app communication."""

    # App lifecycle
    APP_INITIALIZE = "app.initialize"
    APP_CONTEXT_PATCH = "app.context.patch"
    APP_STATE_SYNC = "app.state.sync"

    # Tool interaction
    TOOL_REQUEST = "tool.request"
    TOOL_RESULT = "tool.result"
    TOOL_PROGRESS = "tool.progress"

    # UI interaction
    UI_ACTION = "ui.action"
    UI_STATE_CHANGE = "ui.state.change"
    UI_ERROR = "ui.error"

    # Auth
    AUTH_CHALLENGE = "auth.challenge"
    AUTH_RESULT = "auth.result"
    AUTH_REFRESH = "auth.refresh"

    # Host
    HOST_CAPABILITY_REPORT = "host.capability.report"
    HOST_RESIZE = "host.resize"
    HOST_FOCUS = "host.focus"
    HOST_OPEN_EXTERNAL = "host.open.external"
    HOST_CLOSE = "host.close"

    # Telemetry
    TELEMETRY_EMIT = "telemetry.emit"
    TELEMETRY_FLUSH = "telemetry.flush"


class FallbackType(str, Enum):
    """Fallback rendering options."""

    INLINE = "inline"
    EXTERNAL = "external"
    CARD = "card"
    TEXT = "text"
    LINK = "link"


class Floor(str, Enum):
    """Constitutional floors."""

    F1 = "F1"
    F2 = "F2"
    F3 = "F3"
    F4 = "F4"
    F5 = "F5"
    F6 = "F6"
    F7 = "F7"
    F8 = "F8"
    F9 = "F9"
    F10 = "F10"
    F11 = "F11"
    F12 = "F12"
    F13 = "F13"


class AuditLevel(str, Enum):
    """Audit logging levels."""

    MINIMAL = "minimal"
    STANDARD = "standard"
    FULL = "full"


class HitlTrigger(str, Enum):
    """Human-in-the-loop triggers."""

    DESTRUCTIVE_OPERATIONS = "destructive_operations"
    EXPORT_DATA = "export_data"
    MODIFY_PRODUCTION = "modify_production"
    HIGH_CONFIDENCE_THRESHOLD = "high_confidence_threshold"


# ═══════════════════════════════════════════════════════════════════════════════
# Sub-models
# ═══════════════════════════════════════════════════════════════════════════════


class InlineConfig(BaseModel):
    """Configuration for inline rendering mode."""

    max_width: int = 1200
    max_height: int = 800
    resize: bool = True


class ExternalConfig(BaseModel):
    """Configuration for external rendering mode."""

    window_features: str = "width=1400,height=900,menubar=no,toolbar=no"


class UiEntry(BaseModel):
    """UI entry point configuration."""

    resource_uri: HttpUrl
    mode: UiMode
    capability_required: list[Capability] = Field(default_factory=list)
    csp_policy: str | None = None
    sandbox: str = "allow-scripts allow-same-origin"
    inline_config: InlineConfig = Field(default_factory=InlineConfig)
    external_config: ExternalConfig = Field(default_factory=ExternalConfig)


class AuthConfig(BaseModel):
    """Authentication configuration."""

    mode: AuthMode
    token_ttl_seconds: int = Field(default=300, ge=60, le=3600)
    scopes: list[str] = Field(default_factory=list)
    refreshable: bool = True


class EventsConfig(BaseModel):
    """Event handling configuration."""

    supported: list[EventType] = Field(default_factory=list)
    max_payload_size: int = 1048576  # 1MB


class FallbackConfig(BaseModel):
    """Fallback behavior configuration."""

    chain: list[FallbackType] = Field(
        default_factory=lambda: [
            FallbackType.INLINE,
            FallbackType.EXTERNAL,
            FallbackType.CARD,
            FallbackType.TEXT,
        ]
    )
    external_url: HttpUrl | None = None
    card_template: str | None = None


class ArifosConfig(BaseModel):
    """arifOS constitutional governance configuration."""

    required_floors: list[Floor] = Field(
        default_factory=lambda: [Floor.F1, Floor.F2, Floor.F4, Floor.F7, Floor.F11]
    )
    audit_level: AuditLevel = AuditLevel.STANDARD
    vault_route: str = "999_VAULT"
    human_in_the_loop: list[HitlTrigger] = Field(default_factory=list)


class AppMeta(BaseModel):
    """App metadata."""

    author: str | None = None
    license: str | None = None
    repository: HttpUrl | None = None
    homepage: HttpUrl | None = None
    keywords: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# Main Manifest Model
# ═══════════════════════════════════════════════════════════════════════════════


class GeoXAppManifest(BaseModel):
    """
    Canonical app manifest for GEOX MCP Apps.

    This manifest defines:
    - App identity and versioning
    - Required capabilities and tools
    - UI entry points and rendering preferences
    - Authentication requirements
    - Event protocol support
    - Fallback behavior
    - Constitutional governance settings

    The manifest is host-agnostic — it describes what the app needs,
    not how any particular host should provide it.
    """

    # Identity
    app_id: str = Field(
        ...,
        pattern=r"^geox\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$",
        description="Unique app identifier in geox.{domain}.{name} format",
    )
    version: str = Field(
        ...,
        pattern=r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*))?(?:\+([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*))?$",
        description="Semantic version",
    )
    dimension: Dimension
    domain: AppDomain

    # Display
    display_name: str | None = Field(default=None, max_length=64)
    description: str | None = Field(default=None, max_length=256)
    icon: HttpUrl | None = None

    # Capabilities
    required_tools: list[str] = Field(default_factory=list)
    optional_tools: list[str] = Field(default_factory=list)

    # UI
    ui_entry: UiEntry

    # Security
    auth: AuthConfig

    # Communication
    events: EventsConfig = Field(default_factory=lambda: EventsConfig(supported=[]))

    # Fallback
    fallback: FallbackConfig = Field(default_factory=FallbackConfig)

    # Governance
    arifos: ArifosConfig = Field(default_factory=ArifosConfig)

    # Metadata
    meta: AppMeta | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "app_id": "geox.seismic.viewer",
                "version": "1.0.0",
                "dimension": "EARTH_3D",
                "domain": "seismic",
                "display_name": "Seismic Viewer",
                "description": "Interactive 2D/3D seismic data visualization",
                "required_tools": ["mcp.geox.seismic.ingest", "mcp.geox.seismic.detect_reflectors"],
                "ui_entry": {
                    "resource_uri": "https://geox.apps/seismic-viewer",
                    "mode": "inline-or-external",
                    "capability_required": ["webgl2"],
                    "csp_policy": "default-src 'self'; connect-src 'self' https://api.geox.arif-fazil.com",
                },
                "auth": {"mode": "jwt", "scopes": ["tenant:{tenant_id}", "role:geoscientist"]},
                "events": {
                    "supported": ["app.initialize", "tool.request", "ui.action", "telemetry.emit"]
                },
                "fallback": {"chain": ["inline", "external", "card"]},
                "arifos": {"required_floors": ["F1", "F2", "F4", "F7", "F9", "F11"]},
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════════════════
# App Registry
# ═══════════════════════════════════════════════════════════════════════════════


class AppRegistry:
    """
    Registry for GEOX App Manifests.

    Provides discovery and validation of apps.
    """

    def __init__(self):
        self._apps: dict[str, GeoXAppManifest] = {}

    def register(self, manifest: GeoXAppManifest) -> None:
        """Register an app manifest."""
        self._apps[manifest.app_id] = manifest

    def get(self, app_id: str) -> GeoXAppManifest | None:
        """Get a manifest by app ID."""
        return self._apps.get(app_id)

    def list_apps(self, domain: AppDomain | None = None) -> list[GeoXAppManifest]:
        """List all registered apps, optionally filtered by domain."""
        apps = list(self._apps.values())
        if domain:
            apps = [a for a in apps if a.domain == domain]
        return apps

    def validate_for_host(
        self,
        app_id: str,
        host_capabilities: list[str],
    ) -> tuple[bool, list[str]]:
        """
        Validate if an app can run on a host with given capabilities.

        Returns:
            (is_compatible, missing_capabilities)
        """
        manifest = self.get(app_id)
        if not manifest:
            return False, ["App not found"]

        required = set(manifest.ui_entry.capability_required)
        available = set(host_capabilities)
        missing = list(required - available)

        return len(missing) == 0, missing


# Global registry instance
_registry: AppRegistry | None = None


def get_app_registry() -> AppRegistry:
    """Get the global app registry."""
    global _registry
    if _registry is None:
        _registry = AppRegistry()
    return _registry
