"""
GEOX Volume App — DITEMPA BUKAN DIBERI

Volume context app for 3D geophysical visualization.

Uses cigvis as the rendering backend via adapter pattern.
Supports:
- Volume slice rendering
- Horizon/fault/well overlays
- Interactive viserplot sessions
- Static snapshot export

App visible tools:
- geox_open_volume_context
- geox_volume_render_snapshot
- geox_volume_launch_interactive

Backend tools (hidden from model):
- geox_renderer_cigvis_build_nodes
- geox_renderer_cigvis_render_png
- geox_renderer_cigvis_launch_server
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import uuid4

from arifos.geox.renderers import CigvisAdapter, SceneCompiler
from arifos.geox.renderers.export import RenderExporter
from arifos.geox.volume_context import VolumeSceneBuilder

logger = logging.getLogger("geox.apps.volume_app")


class VolumeApp:
    """
    Volume context application for GEOX.

    Manages volume scenes and rendering via cigvis adapter.
    """

    def __init__(self, output_dir: str = "/tmp/geox_volume"):
        self.scene_compiler = SceneCompiler()
        self.renderer_adapter = CigvisAdapter(output_dir=output_dir)
        self.exporter = RenderExporter(output_dir=output_dir)
        self._active_contexts: dict[str, dict[str, Any]] = {}

    def open_volume_context(
        self,
        basin: str,
        survey_name: str | None = None,
        requester_id: str = "unknown",
        **kwargs,
    ) -> dict[str, Any]:
        """
        Open a new volume context view.

        Args:
            basin: Sedimentary basin name
            survey_name: Optional 3D survey name
            requester_id: Requesting user or system
            **kwargs: Additional parameters

        Returns:
            Volume context response
        """
        context_id = str(uuid4())

        builder = VolumeSceneBuilder()
        builder.set_bounding_box(
            min_x=0,
            max_x=100,
            min_y=0,
            max_y=100,
            min_z=-5000,
            max_z=0,
        )

        scene = builder.build()
        scene["context_id"] = context_id
        scene["state_type"] = "volume_context"
        scene["basin"] = basin
        scene["survey_name"] = survey_name

        self._active_contexts[context_id] = scene

        return {
            "success": True,
            "context_id": context_id,
            "state": "idle",
            "scene_id": scene.get("metadata", {}).get("scene_id"),
            "warnings": [],
            "errors": [],
        }

    def compile_scene(self, context_id: str) -> dict[str, Any]:
        """
        Compile volume context to neutral scene.

        Args:
            context_id: Context to compile

        Returns:
            Compiled scene
        """
        if context_id not in self._active_contexts:
            return {
                "success": False,
                "errors": [f"Context {context_id} not found"],
            }

        context = self._active_contexts[context_id]
        context["state_type"] = "volume_context"

        try:
            compiled = self.scene_compiler.compile(context)
            return {
                "success": True,
                "context_id": context_id,
                "scene": compiled,
                "metadata": {
                    "primitive_count": compiled.get_primitive_count(),
                },
            }
        except Exception as e:
            logger.exception(f"Scene compilation failed: {e}")
            return {
                "success": False,
                "context_id": context_id,
                "errors": [str(e)],
            }

    def render_snapshot(
        self,
        context_id: str,
        output_path: str | None = None,
        width: int = 1200,
        height: int = 800,
    ) -> dict[str, Any]:
        """
        Render volume context to static PNG.

        Args:
            context_id: Context to render
            output_path: Optional output path
            width: Image width
            height: Image height

        Returns:
            Render result with artifact_path
        """
        if context_id not in self._active_contexts:
            return {
                "success": False,
                "errors": [f"Context {context_id} not found"],
            }

        compiled_result = self.compile_scene(context_id)
        if not compiled_result.get("success"):
            return compiled_result

        scene = compiled_result.get("scene", {})
        result = self.renderer_adapter.render_snapshot(
            scene,
            output_path=output_path,
            width=width,
            height=height,
        )

        export_manifest = None
        if result.success:
            export_manifest = self.exporter.export_snapshot(
                result.artifact_path,
                self._active_contexts[context_id],
                scene,
            )

        return {
            "success": result.success,
            "context_id": context_id,
            "artifact_path": result.artifact_path,
            "scene_summary": result.scene_summary,
            "export_manifest": export_manifest,
            "errors": result.errors,
            "warnings": result.warnings,
        }

    def launch_interactive(
        self,
        context_id: str,
        port: int | None = None,
        ttl_seconds: int = 300,
    ) -> dict[str, Any]:
        """
        Launch interactive viserplot session.

        Args:
            context_id: Context to launch
            port: Optional specific port
            ttl_seconds: Session TTL

        Returns:
            Launch result with session and access_url
        """
        if context_id not in self._active_contexts:
            return {
                "success": False,
                "errors": [f"Context {context_id} not found"],
            }

        compiled_result = self.compile_scene(context_id)
        if not compiled_result.get("success"):
            return compiled_result

        scene = compiled_result.get("scene", {})
        result = self.renderer_adapter.launch_interactive(
            scene,
            port=port,
            ttl_seconds=ttl_seconds,
        )

        return {
            "success": result.success,
            "context_id": context_id,
            "session_id": result.session.session_id if result.session else None,
            "access_url": result.embedded_url,
            "ttl_seconds": ttl_seconds,
            "errors": result.errors,
            "warnings": result.warnings,
        }

    def add_horizon(
        self,
        context_id: str,
        horizon_id: str,
        name: str,
        vertices: list[tuple[float, float, float]],
        color: str = "#0000FF",
        opacity: float = 0.7,
    ) -> dict[str, Any]:
        """Add a horizon to the volume context."""
        if context_id not in self._active_contexts:
            return {"success": False, "errors": [f"Context {context_id} not found"]}

        builder = VolumeSceneBuilder()
        builder._scene_data = self._active_contexts[context_id]
        builder.add_horizon(horizon_id, name, vertices, color, opacity)
        self._active_contexts[context_id] = builder.build()

        return {"success": True, "context_id": context_id, "action": "add_horizon"}

    def add_wells(
        self,
        context_id: str,
        wells: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Add wells to the volume context."""
        if context_id not in self._active_contexts:
            return {"success": False, "errors": [f"Context {context_id} not found"]}

        context = self._active_contexts[context_id]
        if "wells" not in context:
            context["wells"] = []

        for well in wells:
            context["wells"].append(well)

        return {"success": True, "context_id": context_id, "action": "add_wells"}

    def get_active_contexts(self) -> list[str]:
        """Return list of active context IDs."""
        return list(self._active_contexts.keys())

    def shutdown_context(self, context_id: str) -> bool:
        """Shutdown and cleanup a volume context."""
        if context_id in self._active_contexts:
            del self._active_contexts[context_id]
            return True
        return False
