"""
arifOS SBOM Generator — CycloneDX SBOM for the arifOS venv.

Phase 1 #1-2: "Add universal ToolManifest" + "Add Pydantic output envelopes"
Use this generator to produce a SBOM for supply-chain attestation.
"""

from __future__ import annotations

import json
from pathlib import Path

# Use the existing SBOM scanner from arifos_attestation
from .arifos_attestation.sbom_scan import SBOM, SBOMScanner


def generate_arifos_sbom() -> SBOM:
    """Generate CycloneDX SBOM for the current arifOS venv."""
    import arifosmcp
    version = getattr(arifosmcp, "__version__", "1!2026.9.6")
    scanner = SBOMScanner()
    return scanner.scan_pip(project_name="arifOS", project_version=version)


def export_sbom_to_file(sbom: SBOM, output_path: str) -> None:
    """Write SBOM as JSON to a file."""
    Path(output_path).write_text(json.dumps(sbom.to_dict(), indent=2))


def export_sbom_to_console(sbom: SBOM) -> str:
    """Return SBOM as JSON string for console/inspection."""
    return json.dumps(sbom.to_dict(), indent=2)
