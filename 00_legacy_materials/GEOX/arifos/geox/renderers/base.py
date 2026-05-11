"""
GEOX Renderer Base Interface — DITEMPA BUKAN DIBERI

GEOX owns visual semantics, not the LLM.
Renderer adapters translate canonical state to render primitives.

Architecture:
  Canonical state → Scene compiler → Renderer adapter → cigvis renderer

This module defines the abstract base for all renderer adapters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class RenderMode(str, Enum):
    """Rendering mode selection."""

    STATIC_SNAPSHOT = "static_snapshot"
    INTERACTIVE_REMOTE = "interactive_remote"


@dataclass
class RenderSession:
    """Ephemeral rendering session for interactive mode."""

    session_id: str
    started_at: datetime
    scene_id: str
    access_url: str | None = None
    port: int | None = None
    ttl_seconds: int = 300
    active: bool = True

    def is_expired(self) -> bool:
        """Check if session has exceeded TTL."""
        elapsed = (datetime.now(timezone.utc) - self.started_at).total_seconds()
        return elapsed > self.ttl_seconds


class RenderResult:
    """Result from a render operation."""

    def __init__(
        self,
        success: bool,
        scene_id: str | None = None,
        artifact_path: str | None = None,
        embedded_url: str | None = None,
        session: RenderSession | None = None,
        scene_summary: dict[str, Any] | None = None,
        errors: list[str] | None = None,
        warnings: list[str] | None = None,
    ):
        self.success = success
        self.scene_id = scene_id or str(uuid4())
        self.artifact_path = artifact_path
        self.embedded_url = embedded_url
        self.session = session
        self.scene_summary = scene_summary or {}
        self.errors = errors or []
        self.warnings = warnings or []


class RendererAdapter(ABC):
    """
    Abstract base for GEOX renderer adapters.

    Renderer adapters are responsible for:
    - Converting neutral render primitives into renderer-specific nodes
    - Managing render sessions (especially for interactive mode)
    - Producing artifacts (PNG, HTML, etc.)
    - Cleanup of resources

    What they are NOT responsible for:
    - Intent parsing
    - Audit logic
    - Hold logic
    - Geological claim generation
    - Canonical schema ownership
    """

    name: str
    supports_interactive: bool = False

    @abstractmethod
    def compile_scene(self, canonical_state: dict[str, Any]) -> dict[str, Any]:
        """
        Compile canonical GEOX state into neutral render primitives.

        Args:
            canonical_state: GeoXDisplayState, GeoXCrossSectionState,
                          GeoXSeismicSectionState, or GeoXTriAppState

        Returns:
            Neutral primitives ready for rendering
        """
        pass

    @abstractmethod
    def render_snapshot(
        self,
        scene: dict[str, Any],
        output_path: str | None = None,
        width: int = 1200,
        height: int = 800,
    ) -> RenderResult:
        """
        Render a static snapshot image.

        Args:
            scene: Compiled scene primitives
            output_path: Optional path to save PNG
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            RenderResult with artifact_path
        """
        pass

    def launch_interactive(
        self,
        scene: dict[str, Any],
        port: int | None = None,
        ttl_seconds: int = 300,
    ) -> RenderResult:
        """
        Launch an interactive rendering session.

        Default implementation returns error if not supported.
        Override in subclasses that support interactive mode.

        Args:
            scene: Compiled scene primitives
            port: Optional specific port, or None for auto-allocation
            ttl_seconds: Session time-to-live

        Returns:
            RenderResult with session and access_url
        """
        return RenderResult(
            success=False,
            errors=[f"{self.name} does not support interactive mode"],
        )

    def shutdown_session(self, session_id: str) -> bool:
        """
        Shutdown a rendering session.

        Args:
            session_id: Session to shutdown

        Returns:
            True if session was found and shutdown
        """
        return False

    def get_active_sessions(self) -> list[RenderSession]:
        """Return list of currently active sessions."""
        return []

    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions. Returns count of removed sessions."""
        return 0
