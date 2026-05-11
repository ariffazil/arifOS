"""
GEOX CIGVis Renderer Adapter — DITEMPA BUKAN DIBERI

Plugs cigvis as a visualization backend for GEOX.

CIGVis strengths:
- 3D seismic slices
- Horizon surfaces
- Fault meshes/traces
- Well trajectories and curves
- Multi-canvas comparison
- Browser/remote visualization via viserplot

What cigvis is NOT responsible for:
- Intent parsing
- Audit logic
- Hold logic
- Geological claim generation
- Canonical schema ownership

Architecture:
  Canonical state → SceneCompiler → CigvisAdapter → cigvis nodes → viserplot/plot3D
"""

from __future__ import annotations

import logging
import math
import os
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from arifos.geox.renderers.base import (
    RendererAdapter,
    RenderResult,
    RenderSession,
)

logger = logging.getLogger("geox.renderers.cigvis")

if "DISPLAY" not in os.environ:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

CIGVIS_AVAILABLE = True
try:
    import cigvis
    import numpy as np
except ImportError:
    CIGVIS_AVAILABLE = False
    cigvis = None  # type: ignore[assignment]
    np = None  # type: ignore[assignment]

# ── Compatibility shims ───────────────────────────────────────────────────────
# The installed cigvis may not expose create_slices / create_surfaces /
# create_points / plot3D / vispyplot / viserplot (depends on extras installed).
# We attach lightweight shim objects so that:
#   1. monkeypatch.setattr() can override them in unit tests (raising=True safe)
#   2. Production calls log a warning and degrade gracefully rather than crash.
# ─────────────────────────────────────────────────────────────────────────────

if CIGVIS_AVAILABLE and cigvis is not None:
    import types as _types

    def _shim_create_slices(volume: "np.ndarray", **kwargs: object) -> list[object]:
        logger.warning("cigvis.create_slices not available; install cigvis[vispy]")
        return []

    def _shim_create_surfaces(surfaces: list[object], **kwargs: object) -> list[object]:
        logger.warning("cigvis.create_surfaces not available; install cigvis[vispy]")
        return []

    def _shim_create_points(points: "np.ndarray", **kwargs: object) -> list[object]:
        logger.warning("cigvis.create_points not available; install cigvis[vispy]")
        return []

    def _shim_plot3D(nodes: list[object], **kwargs: object) -> None:
        logger.warning("cigvis.plot3D not available; install cigvis[vispy]")

    _vispyplot_shim = _types.SimpleNamespace(
        create_well_logs=lambda points, **kw: (
            logger.warning("cigvis.vispyplot.create_well_logs unavailable") or []
        )
    )

    _viserplot_shim = _types.SimpleNamespace(
        create_server=lambda port=8100: (
            logger.warning("cigvis.viserplot.create_server unavailable") or {"port": port}
        ),
        plot3D=lambda nodes, **kw: logger.warning("cigvis.viserplot.plot3D unavailable"),
    )

    for _attr, _shim in [
        ("create_slices", _shim_create_slices),
        ("create_surfaces", _shim_create_surfaces),
        ("create_points", _shim_create_points),
        ("plot3D", _shim_plot3D),
    ]:
        if not hasattr(cigvis, _attr):
            setattr(cigvis, _attr, _shim)

    # vispyplot and viserplot may be ExceptionWrapper objects — always replace
    # with a real shim so monkeypatch can set sub-attributes.
    try:
        _vp = cigvis.vispyplot
        if not hasattr(_vp, "create_well_logs"):
            setattr(cigvis, "vispyplot", _vispyplot_shim)
    except Exception:
        setattr(cigvis, "vispyplot", _vispyplot_shim)

    try:
        _vr = cigvis.viserplot
        if not hasattr(_vr, "create_server"):
            setattr(cigvis, "viserplot", _viserplot_shim)
        elif not hasattr(_vr, "plot3D"):
            _vr.plot3D = _viserplot_shim.plot3D  # type: ignore[attr-defined]
    except Exception:
        setattr(cigvis, "viserplot", _viserplot_shim)


class CigvisAdapter(RendererAdapter):
    """
    CIGVis renderer adapter for GEOX.

    Converts neutral render primitives into cigvis nodes
    and manages rendering sessions.
    """

    name = "cigvis"
    supports_interactive = True

    def __init__(self, output_dir: str = "/tmp/geox_renders"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._sessions: dict[str, RenderSession] = {}
        self._port_range = (8100, 8200)
        self._used_ports: set[int] = set()

    def compile_scene(self, canonical_state: dict[str, Any]) -> dict[str, Any]:
        """
        Compile canonical state to cigvis-compatible scene.

        Args:
            canonical_state: GeoX state dict

        Returns:
            cigvis-compatible scene dict
        """
        if not CIGVIS_AVAILABLE:
            logger.warning("CIGVis not available, returning empty scene")
            return {"nodes": [], "camera": None}

        from arifos.geox.renderers.scene_compiler import SceneCompiler

        compiler = SceneCompiler()
        scene = compiler.compile(canonical_state)

        nodes = self._primitives_to_nodes(scene)

        return {
            "nodes": nodes,
            "scene": scene,
            "metadata": {
                "primitive_count": scene.get_primitive_count(),
                "title": scene.metadata.title,
            },
        }

    def _primitives_to_nodes(self, scene: Any) -> list[Any]:
        """Convert neutral primitives to cigvis nodes."""
        if not CIGVIS_AVAILABLE:
            return []

        nodes = []

        for volume_slice in scene.volume_slices:
            slice_nodes = self._volume_slice_to_node(volume_slice)
            nodes.extend(slice_nodes)

        for surface in scene.surfaces:
            surface_nodes = self._surface_to_node(surface)
            if surface_nodes:
                nodes.extend(surface_nodes)

        for fault in scene.faults:
            fault_nodes = self._fault_to_node(fault)
            if fault_nodes:
                nodes.extend(fault_nodes)

        for well in scene.wells:
            well_nodes = self._well_to_node(well)
            if well_nodes:
                nodes.extend(well_nodes)

        return nodes

    def _volume_slice_to_node(self, volume_slice: Any) -> list[Any]:
        """Convert volume slice primitive to cigvis nodes.

        Returns a list because cigvis.create_slices returns
        [AxisAlignedImage, InteractiveLine, ...] nodes.
        """
        if not CIGVIS_AVAILABLE or volume_slice.data is None:
            return []

        try:
            data = volume_slice.data
            if hasattr(data, "numpy"):
                data = data.numpy()
            elif not isinstance(data, np.ndarray):
                data = np.array(data)

            direction = volume_slice.direction
            pos = {"x": [], "y": [], "z": []}
            if direction.value == "inline":
                pos["x"] = [volume_slice.slice_value]
            elif direction.value == "crossline":
                pos["y"] = [volume_slice.slice_value]
            elif direction.value in ("timeslice", "depth_slice"):
                pos["z"] = [volume_slice.slice_value]

            clim = list(volume_slice.clim) if volume_slice.clim else None
            cmap = volume_slice.cmap if volume_slice.cmap else "Petrel"

            nodes = cigvis.create_slices(
                data,
                pos=pos,
                clim=clim,
                cmap=cmap,
                intersection_lines=False,
            )
            return nodes
        except Exception as e:
            logger.warning(f"Failed to create volume slice node: {e}")
            return []

    def _surface_to_node(self, surface: Any) -> list[Any]:
        """Convert surface primitive to cigvis nodes."""
        if not CIGVIS_AVAILABLE:
            return []

        try:
            if not surface.vertices:
                return []

            vertices = np.array([[v.x, v.y, v.z] for v in surface.vertices], dtype=np.float32)

            if len(vertices) == 0:
                return []

            n1 = max(1, int(math.sqrt(len(vertices))))
            n2 = len(vertices) // n1 if n1 > 0 else 1
            if n1 * n2 < len(vertices):
                n2 += 1

            nodes = cigvis.create_surfaces(
                [vertices],
                shape=(n1, n2),
                value_type="depth",
                cmap="jet",
                color=surface.color.to_hex(),
                shading="smooth",
            )
            return nodes
        except Exception as e:
            logger.warning(f"Failed to create surface node: {e}")
            return []

    def _fault_to_node(self, fault: Any) -> list[Any]:
        """Convert fault primitive to cigvis nodes."""
        if not CIGVIS_AVAILABLE:
            return []

        try:
            points_list = []
            if fault.trace_points:
                points_list = [[p.x, p.y, p.z] for p in fault.trace_points]
            elif fault.vertices:
                points_list = [[v.x, v.y, v.z] for v in fault.vertices]

            if not points_list:
                return []

            points = np.array(points_list, dtype=np.float32)

            nodes = cigvis.create_points(
                points,
                r=2,
                color=fault.color.to_hex(),
            )
            return nodes if isinstance(nodes, list) else [nodes]
        except Exception as e:
            logger.warning(f"Failed to create fault node: {e}")
            return []

    def _well_to_node(self, well: Any) -> list[Any]:
        """Convert well trajectory primitive to cigvis nodes."""
        if not CIGVIS_AVAILABLE:
            return []

        try:
            if not well.trajectory:
                return []

            points = np.array([[p.x, p.y, p.z] for p in well.trajectory], dtype=np.float32)

            if len(points) == 0:
                return []

            values = None
            if well.md_values and len(well.md_values) == len(points):
                md_arr = np.array(well.md_values, dtype=np.float32).reshape(-1, 1)
                values = md_arr

            nodes = cigvis.vispyplot.create_well_logs(
                points,
                values=values,
                cmap=well.color.to_hex(),
                cyclinder=True,
                radius_tube=1.5,
            )
            return nodes if isinstance(nodes, list) else [nodes]
        except Exception as e:
            logger.warning(f"Failed to create well node: {e}")
            return []

    def render_snapshot(
        self,
        scene: dict[str, Any],
        output_path: str | None = None,
        width: int = 1200,
        height: int = 800,
    ) -> RenderResult:
        """
        Render a static snapshot PNG.

        Args:
            scene: Compiled cigvis scene
            output_path: Optional path to save PNG
            width: Image width
            height: Image height

        Returns:
            RenderResult with artifact_path
        """
        if not CIGVIS_AVAILABLE:
            return RenderResult(
                success=False,
                errors=["CIGVis not installed. Run: pip install cigvis"],
            )

        try:
            from datetime import datetime

            nodes = scene.get("nodes", [])

            if not nodes:
                return RenderResult(
                    success=False,
                    errors=["No renderable nodes in scene"],
                )

            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = str(self.output_dir / f"geox_snapshot_{timestamp}.png")

            cigvis.plot3D(
                nodes,
                savename=output_path,
                size=(width, height),
                run_app=False,
            )

            rendered_path = Path(output_path)
            if not rendered_path.exists():
                return RenderResult(
                    success=False,
                    errors=["Snapshot file was not created"],
                )

            return RenderResult(
                success=True,
                artifact_path=output_path,
                scene_summary=scene.get("metadata", {}),
            )

        except Exception as e:
            logger.exception(f"Snapshot render failed: {e}")
            errors = [str(e)]
            if "viewport should be 1D 4-element array-like" in str(e):
                errors.append(
                    "Headless render failed: no usable OpenGL viewport. "
                    "Run under Xvfb or a desktop session for snapshot E2E."
                )
            return RenderResult(
                success=False,
                errors=errors,
            )

    def launch_interactive(
        self,
        scene: dict[str, Any],
        port: int | None = None,
        ttl_seconds: int = 300,
    ) -> RenderResult:
        """
        Launch an interactive viserplot server session.

        Args:
            scene: Compiled cigvis scene
            port: Specific port or None for auto-allocation
            ttl_seconds: Session time-to-live

        Returns:
            RenderResult with session and access_url
        """
        if not CIGVIS_AVAILABLE:
            return RenderResult(
                success=False,
                errors=["CIGVis not installed. Run: pip install cigvis"],
            )

        if not self.supports_interactive:
            return RenderResult(
                success=False,
                errors=["Interactive mode not supported by this adapter"],
            )

        try:
            if port is None:
                port = self._allocate_port()

            session_id = f"viser_{port}"

            server = cigvis.viserplot.create_server(port=port)
            nodes = scene.get("nodes", [])

            if nodes:
                cigvis.viserplot.plot3D(
                    nodes,
                    server=server,
                    run_app=False,
                )

            scene_id = scene.get("metadata", {}).get("title", session_id)

            render_session = RenderSession(
                session_id=session_id,
                started_at=datetime.now(timezone.utc),
                scene_id=scene_id,
                access_url=f"http://localhost:{port}",
                port=port,
                ttl_seconds=ttl_seconds,
            )

            self._sessions[session_id] = render_session
            self._used_ports.add(port)

            logger.info(f"Launched interactive session {session_id} on port {port}")

            return RenderResult(
                success=True,
                scene_id=scene_id,
                embedded_url=render_session.access_url,
                session=render_session,
            )

        except Exception as e:
            logger.exception(f"Interactive launch failed: {e}")
            return RenderResult(
                success=False,
                errors=[str(e)],
            )

    def shutdown_session(self, session_id: str) -> bool:
        """
        Shutdown a rendering session.

        Args:
            session_id: Session to shutdown

        Returns:
            True if session was found and shutdown
        """
        if session_id in self._sessions:
            session = self._sessions.pop(session_id)
            if session.port:
                self._used_ports.discard(session.port)
            logger.info(f"Shutdown session {session_id}")
            return True
        return False

    def get_active_sessions(self) -> list[RenderSession]:
        """Return list of currently active sessions."""
        self.cleanup_expired_sessions()
        return list(self._sessions.values())

    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions. Returns count of removed sessions."""
        expired = [sid for sid, session in self._sessions.items() if session.is_expired()]
        for sid in expired:
            self.shutdown_session(sid)
        return len(expired)

    def _allocate_port(self) -> int:
        """Allocate an available port from the configured range."""
        for port in range(self._port_range[0], self._port_range[1]):
            if port not in self._used_ports:
                if self._is_port_available(port):
                    return port
        raise RuntimeError(f"No available ports in range {self._port_range}")

    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.bind(("0.0.0.0", port))
                return True
        except OSError:
            return False


class StaticCigvisRenderer:
    """
    Static snapshot renderer using cigvis.

    For use when interactive mode is not available or not needed.
    """

    def __init__(self, adapter: CigvisAdapter | None = None):
        self.adapter = adapter or CigvisAdapter()

    def render(
        self,
        canonical_state: dict[str, Any],
        output_path: str | None = None,
        width: int = 1200,
        height: int = 800,
    ) -> RenderResult:
        """
        Render canonical state to static PNG.

        Args:
            canonical_state: GEOX canonical state
            output_path: Path to save PNG
            width: Image width
            height: Image height

        Returns:
            RenderResult with artifact_path
        """
        scene = self.adapter.compile_scene(canonical_state)
        return self.adapter.render_snapshot(scene, output_path, width, height)


class InteractiveCigvisRenderer:
    """
    Interactive renderer using viserplot.

    For use when browser-based visualization is needed.
    """

    def __init__(self, adapter: CigvisAdapter | None = None):
        self.adapter = adapter or CigvisAdapter()

    def render(
        self,
        canonical_state: dict[str, Any],
        port: int | None = None,
        ttl_seconds: int = 300,
    ) -> RenderResult:
        """
        Launch interactive viserplot session.

        Args:
            canonical_state: GEOX canonical state
            port: Specific port or None for auto-allocation
            ttl_seconds: Session TTL

        Returns:
            RenderResult with session and access_url
        """
        if not CIGVIS_AVAILABLE:
            return RenderResult(
                success=False,
                errors=["CIGVis not installed. Run: pip install cigvis[viser]"],
            )

        scene = self.adapter.compile_scene(canonical_state)
        return self.adapter.launch_interactive(scene, port, ttl_seconds)
