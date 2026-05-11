"""
GEOX Volume App Tools — DITEMPA BUKAN DIBERI

MCP tools for volume context visualization.

Model-visible tools:
- geox_open_volume_context
- geox_volume_render_snapshot
- geox_volume_launch_interactive

Backend tools (hidden from model):
- geox_renderer_cigvis_build_nodes
- geox_renderer_cigvis_render_png
- geox_renderer_cigvis_launch_server
"""

from __future__ import annotations

from typing import Any

from arifos.geox.apps.volume_app.app import VolumeApp

_volume_app_instance: VolumeApp | None = None


def get_volume_app() -> VolumeApp:
    """Get or create the volume app singleton."""
    global _volume_app_instance
    if _volume_app_instance is None:
        _volume_app_instance = VolumeApp()
    return _volume_app_instance


async def geox_open_volume_context(
    basin: str,
    survey_name: str | None = None,
    requester_id: str = "unknown",
    **kwargs,
) -> dict[str, Any]:
    """
    Open a 3D volume context view when assets support it.

    Use this when you want to explore a 3D seismic volume
    with horizon, fault, and well overlays.

    Args:
        basin: Sedimentary basin name
        survey_name: Optional 3D survey name
        requester_id: Requesting user or system ID

    Returns:
        Volume context response with context_id
    """
    app = get_volume_app()
    return app.open_volume_context(
        basin=basin,
        survey_name=survey_name,
        requester_id=requester_id,
        **kwargs,
    )


async def geox_volume_compile_scene(
    context_id: str,
) -> dict[str, Any]:
    """
    Compile a volume context scene to neutral primitives.

    Args:
        context_id: Context to compile

    Returns:
        Compiled scene with metadata
    """
    app = get_volume_app()
    return app.compile_scene(context_id)


async def geox_volume_render_snapshot(
    context_id: str,
    output_path: str | None = None,
    width: int = 1200,
    height: int = 800,
) -> dict[str, Any]:
    """
    Render a volume context to static PNG snapshot.

    This is the safer option for MCP hosts that don't support
    interactive websocket sessions.

    Args:
        context_id: Context to render
        output_path: Optional output path
        width: Image width in pixels
        height: Image height in pixels

    Returns:
        Render result with artifact_path
    """
    app = get_volume_app()
    return app.render_snapshot(
        context_id=context_id,
        output_path=output_path,
        width=width,
        height=height,
    )


async def geox_volume_launch_interactive(
    context_id: str,
    port: int | None = None,
    ttl_seconds: int = 300,
) -> dict[str, Any]:
    """
    Launch an interactive viserplot session.

    Requires the MCP host to support websocket connections.

    Args:
        context_id: Context to launch
        port: Optional specific port
        ttl_seconds: Session time-to-live (default 300)

    Returns:
        Session info with access_url
    """
    app = get_volume_app()
    return app.launch_interactive(
        context_id=context_id,
        port=port,
        ttl_seconds=ttl_seconds,
    )


async def geox_volume_add_horizon(
    context_id: str,
    horizon_id: str,
    name: str,
    vertices: list[list[float]],
    color: str = "#0000FF",
    opacity: float = 0.7,
) -> dict[str, Any]:
    """
    Add a horizon overlay to a volume context.

    Args:
        context_id: Context to add to
        horizon_id: Unique horizon identifier
        name: Horizon name
        vertices: List of [x, y, z] tuples
        color: Hex color string
        opacity: Opacity 0-1

    Returns:
        Update result
    """
    app = get_volume_app()
    return app.add_horizon(
        context_id=context_id,
        horizon_id=horizon_id,
        name=name,
        vertices=[tuple(v) for v in vertices],
        color=color,
        opacity=opacity,
    )


async def geox_volume_add_wells(
    context_id: str,
    wells: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Add wells to a volume context.

    Args:
        context_id: Context to add to
        wells: List of well data dicts

    Returns:
        Update result
    """
    app = get_volume_app()
    return app.add_wells(context_id=context_id, wells=wells)


# Backend-only tools (not exposed to model)
# These are internal implementation details


async def _geox_renderer_cigvis_build_nodes(
    scene: dict[str, Any],
) -> dict[str, Any]:
    """
    Internal: Build cigvis nodes from neutral scene.

    NOT exposed to model - implementation detail.
    """
    from arifos.geox.renderers import CigvisAdapter

    adapter = CigvisAdapter()
    return adapter.compile_scene(scene)


async def _geox_renderer_cigvis_render_png(
    scene: dict[str, Any],
    output_path: str | None = None,
    width: int = 1200,
    height: int = 800,
) -> dict[str, Any]:
    """
    Internal: Render cigvis scene to PNG.

    NOT exposed to model - implementation detail.
    """
    from arifos.geox.renderers import CigvisAdapter

    adapter = CigvisAdapter()
    result = adapter.render_snapshot(scene, output_path, width, height)
    return {
        "success": result.success,
        "artifact_path": result.artifact_path,
        "errors": result.errors,
    }


async def _geox_renderer_cigvis_launch_server(
    scene: dict[str, Any],
    port: int | None = None,
    ttl_seconds: int = 300,
) -> dict[str, Any]:
    """
    Internal: Launch cigvis viserplot server.

    NOT exposed to model - implementation detail.
    """
    from arifos.geox.renderers import CigvisAdapter

    adapter = CigvisAdapter()
    result = adapter.launch_interactive(scene, port, ttl_seconds)
    return {
        "success": result.success,
        "session_id": result.session.session_id if result.session else None,
        "access_url": result.embedded_url,
        "errors": result.errors,
    }
