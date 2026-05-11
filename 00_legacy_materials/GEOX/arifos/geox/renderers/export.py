"""
GEOX Render Export Module — DITEMPA BUKAN DIBERI

Export utilities for GEOX rendering.

Supports:
- Static PNG snapshot export
- Scene state JSON export
- Artifact management
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

logger = logging.getLogger("geox.renderers.export")


class RenderExporter:
    """
    Handles export of rendered scenes and artifacts.

    Export modes:
    - static_snapshot: PNG image export
    - scene_state: JSON export of canonical + neutral scene
    - full_artifact: Both PNG + JSON with metadata
    """

    def __init__(self, output_dir: str = "/tmp/geox_exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_snapshot(
        self,
        artifact_path: str,
        canonical_state: dict[str, Any],
        neutral_scene: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Export a rendered snapshot with provenance.

        Args:
            artifact_path: Path to rendered PNG
            canonical_state: Original GEOX canonical state
            neutral_scene: Compiled neutral scene
            metadata: Additional metadata

        Returns:
            Export manifest dict
        """
        export_id = str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        manifest = {
            "export_id": export_id,
            "timestamp": timestamp,
            "artifact_type": "static_snapshot",
            "artifact_path": artifact_path,
            "canonical_state_type": canonical_state.get("state_type", "unknown"),
            "scene_metadata": neutral_scene.get("metadata") if neutral_scene else None,
            "provenance": [
                {
                    "source": "GEOX Renderer",
                    "timestamp": timestamp,
                    "renderer": "cigvis",
                    "mode": "static_snapshot",
                }
            ],
            "metadata": metadata or {},
        }

        manifest_path = Path(artifact_path).with_suffix(".manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2, default=str)

        logger.info(f"Exported snapshot to {artifact_path}")

        return manifest

    def export_scene_state(
        self,
        canonical_state: dict[str, Any],
        neutral_scene: dict[str, Any],
        output_path: str | None = None,
    ) -> str:
        """
        Export scene state as JSON.

        Args:
            canonical_state: Original GEOX canonical state
            neutral_scene: Compiled neutral scene
            output_path: Optional output path

        Returns:
            Path to exported JSON
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.output_dir / f"scene_state_{timestamp}.json")

        export_data = {
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "canonical_state": canonical_state,
            "neutral_scene": {
                "primitive_count": neutral_scene.get("metadata", {}).get("primitive_count", 0),
                "metadata": neutral_scene.get("metadata"),
            },
        }

        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        logger.info(f"Exported scene state to {output_path}")

        return output_path

    def export_full_artifact(
        self,
        artifact_path: str,
        canonical_state: dict[str, Any],
        neutral_scene: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Export full artifact bundle (PNG + JSON + manifest).

        Args:
            artifact_path: Path to rendered PNG
            canonical_state: Original GEOX canonical state
            neutral_scene: Compiled neutral scene
            metadata: Additional metadata

        Returns:
            Full export manifest
        """
        manifest = self.export_snapshot(
            artifact_path,
            canonical_state,
            neutral_scene,
            metadata,
        )

        scene_json_path = self.export_scene_state(
            canonical_state,
            neutral_scene or {},
            output_path=str(Path(artifact_path).with_suffix(".scene.json")),
        )

        manifest["scene_json_path"] = scene_json_path
        manifest["artifact_count"] = 2

        manifest_path = Path(artifact_path).with_suffix(".manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2, default=str)

        return manifest

    def list_exports(self, prefix: str = "") -> list[dict[str, Any]]:
        """
        List all exports in the output directory.

        Args:
            prefix: Filter by prefix

        Returns:
            List of export manifests
        """
        exports = []

        for manifest_path in self.output_dir.glob(f"{prefix}*.manifest.json"):
            try:
                with open(manifest_path) as f:
                    manifest = json.load(f)
                    exports.append(manifest)
            except Exception as e:
                logger.warning(f"Failed to read manifest {manifest_path}: {e}")

        exports.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return exports

    def cleanup_old_exports(self, max_age_hours: int = 24) -> int:
        """
        Remove exports older than max_age_hours.

        Args:
            max_age_hours: Maximum age in hours

        Returns:
            Count of removed exports
        """
        cutoff = datetime.now(timezone.utc).timestamp() - (max_age_hours * 3600)
        removed = 0

        for manifest_path in self.output_dir.glob("*.manifest.json"):
            try:
                if manifest_path.stat().st_mtime < cutoff:
                    artifact_path = manifest_path.with_suffix(".png")
                    scene_path = manifest_path.with_suffix(".scene.json")

                    manifest_path.unlink(missing_ok=True)
                    artifact_path.unlink(missing_ok=True)
                    scene_path.unlink(missing_ok=True)

                    removed += 1
            except Exception as e:
                logger.warning(f"Failed to cleanup {manifest_path}: {e}")

        if removed > 0:
            logger.info(f"Cleaned up {removed} old exports")

        return removed
