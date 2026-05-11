"""
Log Bundle Loader — Phase A Foundation
DITEMPA BUKAN DIBERI

Ingests LAS/DLIS/CSV + metadata, maps mnemonics, detects depth reference.
Emits canonical LogBundle with F4 Clarity (units explicit) and F9 Anti-Hantu (source tracked).
"""

from __future__ import annotations

import re
from typing import Any

from arifos.geox.schemas.petrophysics.measurements import WellLogCurve, LogBundle

# In-memory store (replace with persistent storage in production)
_bundle_store: dict[str, LogBundle] = {}


async def load_bundle_from_store(well_id: str) -> LogBundle:
    """Load bundle from store."""
    if well_id not in _bundle_store:
        raise ValueError(f"No bundle found for well {well_id}")
    return _bundle_store[well_id]


async def store_bundle(bundle: LogBundle) -> None:
    """Store bundle."""
    _bundle_store[bundle.well_id] = bundle


async def apply_environmental_corrections(bundle: LogBundle) -> dict[str, Any]:
    """
    Apply environmental corrections to curves.

    Returns corrected bundle metadata. Full correction logic in Phase B.
    """
    corrections = []

    # Check for corrections needed
    cali = bundle.get_curve("CALI") or bundle.get_curve("CAL")
    if cali:
        corrections.append("borehole_size_correction_available")

    # Temperature correction flag
    if any(c.mnemonic in ["TEMP", "HTMP"] for c in bundle.curves.values()):
        corrections.append("temperature_correction_available")

    return {
        "curves": list(bundle.curves.values()),
        "corrections": corrections,
        "status": "CORRECTED_STUB",  # Full implementation in Phase B
    }


class LogBundleLoader:
    """
    Load and canonicalize well log files.

    Handles LAS 2.0/3.0 format with mnemonic mapping and QC.
    """

    # Common mnemonic mappings (LAS standardization)
    MNEMONIC_MAP = {
        # Gamma ray
        "GR": ["GR", "GAMMA", "GAPI"],
        "CGR": ["CGR", "GR_CORR"],
        # Resistivity
        "ILD": ["ILD", "RT", "RESD", "AHT90", "HDRS"],
        "LLD": ["LLD", "RLLD"],
        "LLS": ["LLS", "RLLS"],
        "MSFL": ["MSFL", "RXOZ"],
        # Density
        "RHOB": ["RHOB", "DENB", "DENS", "RHOZ"],
        "DRHO": ["DRHO", "DEN_CORR"],
        # Neutron
        "NPHI": ["NPHI", "NEUT", "TNPH", "NPOR"],
        # Sonic
        "DT": ["DT", "AC", "DTC", "SONIC"],
        "DTS": ["DTS", "SHEAR", "DTCO"],
        # Caliper
        "CALI": ["CALI", "CAL", "HCAL", "LCAL"],
        # SP
        "SP": ["SP", "SPONT"],
        # Photoelectric
        "PEF": ["PEF", "PE", "PHIE"],
        # Depth
        "DEPT": ["DEPT", "DEPTH", "MD", "TVD", "TVDSS"],
    }

    def __init__(self):
        self.null_value = -999.25

    async def load(
        self, well_id: str, sources: list[str], depth_reference: str = "MD"
    ) -> LogBundle:
        """
        Load log bundle from source files.

        Args:
            well_id: Canonical well identifier
            sources: List of file paths (LAS, DLIS, CSV)
            depth_reference: MD, TVD, TVDSS, etc.
        """
        curves: dict[str, WellLogCurve] = {}
        header = {}
        well_name = well_id

        # Process each source file
        for source_path in sources:
            if source_path.endswith(".las") or source_path.endswith(".LAS"):
                file_curves, file_header = self._parse_las_file(source_path)
                curves.update(file_curves)
                header.update(file_header)
                if "WELL" in file_header:
                    well_name = file_header["WELL"]

        # Determine depth range
        depth_curve = self._get_depth_curve(curves)
        min_depth = min(depth_curve.depth) if depth_curve and depth_curve.depth else 0
        max_depth = max(depth_curve.depth) if depth_curve and depth_curve.depth else 0

        # Create bundle
        bundle = LogBundle(
            well_id=well_id,
            well_name=well_name,
            source_files=sources,
            header=header,
            curves=curves,
            depth_reference=depth_reference,
            min_depth=min_depth,
            max_depth=max_depth,
            depth_unit=self._detect_depth_unit(header),
            latitude=self._parse_lat_lon(header.get("LAT")),
            longitude=self._parse_lat_lon(header.get("LON")),
        )

        # Initial QC
        bundle.qc_summary = self._initial_qc(bundle)

        return bundle

    def _parse_las_file(
        self, filepath: str
    ) -> tuple[dict[str, WellLogCurve], dict[str, str]]:
        """Parse LAS 2.0 file."""
        curves = {}
        header = {}

        try:
            with open(filepath, "r", encoding="ascii", errors="replace") as f:
                content = f.read()
        except Exception as e:
            raise ValueError(f"Cannot read file {filepath}: {e}")

        lines = content.splitlines()
        section = None
        curve_info = {}
        curve_order = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Section detection
            if line.startswith("~"):
                section_marker = line[1:].split()[0].upper()
                section = section_marker
                continue

            # Header parsing
            if section == "WELL":
                match = re.match(r"(\w+)\s*\.\.+\s*(.+)", line)
                if match:
                    header[match.group(1).upper()] = match.group(2).strip()

            # Curve info parsing
            elif section == "CURVE":
                match = re.match(r"(\w+)\s*\.\.+\s*(.+)", line)
                if match:
                    mnemonic = match.group(1).strip().upper()
                    curve_order.append(mnemonic)
                    curve_info[mnemonic] = {"desc": match.group(2).strip()}

            # ASCII data parsing
            elif section == "ASCII" or section == "A":
                if not curve_order:
                    continue

                parts = re.split(r"[\s,]+", line.strip())
                parts = [p for p in parts if p]

                if len(parts) < len(curve_order):
                    continue

                # Initialize curves if needed
                for i, mnemonic in enumerate(curve_order):
                    if mnemonic not in curves:
                        curves[mnemonic] = WellLogCurve(
                            mnemonic=mnemonic,
                            name=curve_info.get(mnemonic, {}).get("desc", mnemonic),
                            units="",
                            depth=[],
                            values=[],
                            source_file=filepath,
                        )

                # Add data point
                for i, mnemonic in enumerate(curve_order):
                    try:
                        val = float(parts[i])
                        # First curve is depth
                        if i == 0:
                            curves[mnemonic].depth.append(val)
                        # Check for null
                        if val == self.null_value:
                            curves[mnemonic].values.append(None)
                        else:
                            curves[mnemonic].values.append(val)
                    except (ValueError, IndexError):
                        curves[mnemonic].values.append(None)
                        if i == 0:
                            curves[mnemonic].depth.append(0.0)

        return curves, header

    def _get_depth_curve(self, curves: dict[str, WellLogCurve]) -> WellLogCurve | None:
        """Find the primary depth curve."""
        for name in ["DEPT", "DEPTH", "MD"]:
            if name in curves:
                return curves[name]
        return list(curves.values())[0] if curves else None

    def _detect_depth_unit(self, header: dict[str, str]) -> str:
        """Detect depth unit from header."""
        for key in ["STRT", "STOP", "STEP"]:
            if key in header:
                # Look for unit in dot notation
                match = re.search(r"\.(\w+)", header[key])
                if match:
                    unit = match.group(1).lower()
                    if unit in ["m", "metres", "meters"]:
                        return "m"
                    elif unit in ["ft", "feet"]:
                        return "ft"
        return "m"  # Default

    def _parse_lat_lon(self, value: str | None) -> float | None:
        """Parse latitude/longitude from header string."""
        if not value:
            return None
        try:
            # Remove common suffixes and parse
            clean = (
                value.replace("N", "")
                .replace("S", "-")
                .replace("E", "")
                .replace("W", "-")
            )
            return float(clean.strip())
        except (ValueError, TypeError):
            return None

    def _initial_qc(self, bundle: LogBundle) -> dict[str, Any]:
        """Run initial QC on bundle."""
        issues = []

        # Check for critical curves
        critical_curves = ["GR", "RHOB", "NPHI", "ILD", "DT"]
        missing = [c for c in critical_curves if not bundle.get_curve(c)]
        if missing:
            issues.append(f"Missing critical curves: {missing}")

        # Check depth consistency
        depth_curve = self._get_depth_curve(bundle.curves)
        if depth_curve and len(depth_curve.depth) > 1:
            # Check for monotonicity
            is_monotonic = all(
                depth_curve.depth[i] <= depth_curve.depth[i + 1]
                for i in range(len(depth_curve.depth) - 1)
            )
            if not is_monotonic:
                issues.append("Depth not monotonically increasing")

        return {
            "curve_count": len(bundle.curves),
            "missing_critical": missing,
            "issues": issues,
            "status": "WARNING" if issues else "PASS",
        }


# Standalone functions for async interface
async def load_bundle(
    well_id: str, sources: list[str], depth_reference: str = "MD"
) -> LogBundle:
    """Convenience function to load a bundle."""
    loader = LogBundleLoader()
    bundle = await loader.load(well_id, sources, depth_reference)
    await store_bundle(bundle)
    return bundle
