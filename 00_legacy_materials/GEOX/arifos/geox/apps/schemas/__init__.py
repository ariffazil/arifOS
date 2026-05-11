"""
GEOX App Schemas — JSON Schema definitions for app manifests.

DITEMPA BUKAN DIBERI
"""

import json
from pathlib import Path


def get_manifest_schema() -> dict:
    """Load the GEOX App Manifest JSON Schema."""
    schema_path = Path(__file__).parent / "geox-app-manifest.json"
    with open(schema_path) as f:
        return json.load(f)


__all__ = ["get_manifest_schema"]
