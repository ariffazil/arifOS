"""
arifosmcp/apps/lifecycle.py
Full MCP App lifecycle management for arifOS constitutional surfaces.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AppInstance:
    """Runtime handle for a launched MCP App."""

    instance_id: str
    app_id: str
    context: dict[str, Any] = field(default_factory=dict)
    status: str = "running"  # running | suspended | closed


@dataclass
class CloseResult:
    """Result of closing an app instance."""

    instance_id: str
    status: str = "closed"
    cleanup_errors: list[str] = field(default_factory=list)


class AppLifecycle:
    """Manage launch, update, suspend, resume, and close for arifOS MCP Apps."""

    def __init__(self) -> None:
        self._instances: dict[str, AppInstance] = {}

    def launch(self, app_id: str, context: dict[str, Any] | None = None) -> AppInstance:
        """Launch an app with the given context."""
        import uuid

        instance_id = f"{app_id}-{uuid.uuid4().hex[:8]}"
        instance = AppInstance(
            instance_id=instance_id,
            app_id=app_id,
            context=dict(context) if context else {},
            status="running",
        )
        self._instances[instance_id] = instance
        return instance

    def update(self, instance_id: str, patch: dict[str, Any]) -> AppInstance:
        """Update a running app instance's context."""
        instance = self._instances.get(instance_id)
        if instance is None:
            raise ValueError(f"Instance {instance_id} not found")
        if instance.status != "running":
            raise ValueError(f"Cannot update instance in status {instance.status}")
        instance.context.update(patch)
        return instance

    def suspend(self, instance_id: str) -> AppInstance:
        """Suspend an app instance, preserving its context."""
        instance = self._instances.get(instance_id)
        if instance is None:
            raise ValueError(f"Instance {instance_id} not found")
        instance.status = "suspended"
        return instance

    def resume(self, instance_id: str) -> AppInstance:
        """Resume a suspended app instance."""
        instance = self._instances.get(instance_id)
        if instance is None:
            raise ValueError(f"Instance {instance_id} not found")
        if instance.status != "suspended":
            raise ValueError(f"Cannot resume instance in status {instance.status}")
        instance.status = "running"
        return instance

    def close(self, instance_id: str) -> CloseResult:
        """Close an app instance and clean up."""
        instance = self._instances.pop(instance_id, None)
        if instance is None:
            return CloseResult(instance_id=instance_id, status="not_found")
        instance.status = "closed"
        return CloseResult(instance_id=instance_id)

    def list_instances(self, app_id: str | None = None) -> list[AppInstance]:
        """List all tracked instances, optionally filtered by app_id."""
        instances = list(self._instances.values())
        if app_id:
            instances = [i for i in instances if i.app_id == app_id]
        return instances


__all__ = ["AppLifecycle", "AppInstance", "CloseResult"]
