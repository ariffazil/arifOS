"""
arifosmcp/runtime/widgets/widget_resource.py
Widget-as-Resource bridge for MCP Apps embedded UI contract.
"""

from __future__ import annotations

from typing import Any

from fastmcp.resources.types import TextResource
from fastmcp.utilities.mime import UI_MIME_TYPE


class WidgetResource:
    """Wrap an HTML widget as an embeddable MCP resource."""

    def __init__(
        self,
        widget_id: str,
        title: str,
        html: str,
        app_id: str = "arifos",
        state: dict[str, Any] | None = None,
    ) -> None:
        self.widget_id = widget_id
        self.title = title
        self.html = html
        self.app_id = app_id
        self.state = dict(state) if state else {}

    def render_html(self) -> str:
        """Return the raw HTML payload."""
        return self.html

    def get_state(self) -> dict[str, Any]:
        """Return the current widget state patch."""
        return dict(self.state)

    def to_embedded_resource(self) -> dict[str, Any]:
        """Serialize to an MCP Apps embedded_resource dict."""
        return {
            "type": "embedded_resource",
            "resource": {
                "uri": f"ui://{self.widget_id}",
                "mimeType": UI_MIME_TYPE,
                "text": self.render_html(),
                "title": self.title,
            },
            "mount_action": "open_or_update",
            "state_patch": self.get_state(),
        }

    def to_text_resource(self) -> TextResource:
        """Return a FastMCP TextResource for direct registration."""
        return TextResource(
            uri=f"ui://{self.widget_id}",
            name=self.title,
            text=self.render_html(),
            mime_type=UI_MIME_TYPE,
            meta={
                "ui": {
                    "resourceUri": f"ui://{self.widget_id}",
                    "domain": "https://arifosmcp.arif-fazil.com",
                }
            },
        )


__all__ = ["WidgetResource"]
