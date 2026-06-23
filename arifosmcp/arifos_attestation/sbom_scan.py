"""
SBOM Scanner — CycloneDX SBOM scanner.

Per SLSA + executive verdict, every dependency tree should be auditable.
CycloneDX is the OWASP standard for SBOMs.

Phase 1: generate SBOM from current Python environment.
Phase 2: scan against CVE database (Trivy / OSV).
"""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field


@dataclass
class SBOM:
    """CycloneDX-style SBOM."""

    bom_format: str = "CycloneDX"
    spec_version: str = "1.5"
    serial_number: str = ""
    version: int = 1
    metadata: dict = field(default_factory=dict)
    components: list[dict] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> dict:
        return {
            "bomFormat": self.bom_format,
            "specVersion": self.spec_version,
            "serialNumber": self.serial_number,
            "version": self.version,
            "metadata": self.metadata,
            "components": self.components,
        }


class SBOMScanner:
    """Scan installed Python packages and emit CycloneDX SBOM."""

    def scan_pip(self, project_name: str = "arifOS", project_version: str = "2026.06.14") -> SBOM:
        """Run `pip list --format=json` and convert to CycloneDX."""
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        try:
            out = subprocess.run(
                ["pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            packages = json.loads(out.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            packages = []

        components = [
            {
                "type": "library",
                "purl": f"pkg:pypi/{pkg['name']}@{pkg['version']}",
                "name": pkg["name"],
                "version": pkg["version"],
            }
            for pkg in packages
        ]

        return SBOM(
            serial_number=f"urn:uuid:{int(time.time())}-{len(components)}",
            metadata={
                "timestamp": ts,
                "tools": [{"name": "arifos-sbom-scanner", "version": "0.1.0"}],
                "component": {
                    "type": "application",
                    "name": project_name,
                    "version": project_version,
                },
            },
            components=components,
            generated_at=ts,
        )

    def export(self, sbom: SBOM) -> str:
        """Export SBOM as JSON string."""
        return json.dumps(sbom.to_dict(), indent=2)
