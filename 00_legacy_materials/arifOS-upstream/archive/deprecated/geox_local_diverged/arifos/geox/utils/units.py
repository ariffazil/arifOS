"""
GEOX Unit Utilities
DITEMPA BUKAN DIBERI

Unit conversion and formatting for geological quantities.
All conversions are exact or best-available scientific values.

Supported unit families:
  Length:      METER, KILOMETER, FEET
  Pressure:    PSI, MPA, KPA, BAR
  Temperature: DEGC, DEGF
  Density:     KG_M3, G_CM3
  Ratio:       FRACTION, PERCENT
  Seismic:     MS_US (milliseconds / microseconds TWT), M_S (velocity)
  Velocity:    M_S, KM_S, FT_S

Constitutional note: F4 Clarity requires that all quantities in GEOX
carry explicit unit labels. This module provides the canonical unit
enum and formatting functions used throughout the pipeline.
"""

from __future__ import annotations

from enum import Enum

# ---------------------------------------------------------------------------
# GeoUnit Enum
# ---------------------------------------------------------------------------

class GeoUnit(str, Enum):
    """
    Canonical geological unit identifiers.

    Values are human-readable strings that double as unit labels.
    Use GeoUnit.value for display; use GeoUnit members for comparisons.
    """

    # Length
    METER = "m"
    KILOMETER = "km"
    FEET = "ft"

    # Pressure
    PSI = "psi"
    MPA = "MPa"
    KPA = "kPa"
    BAR = "bar"

    # Temperature
    DEGC = "degC"
    DEGF = "degF"

    # Density
    KG_M3 = "kg/m3"
    G_CM3 = "g/cm3"

    # Dimensionless
    FRACTION = "fraction"
    PERCENT = "%"

    # Seismic time
    MS_TWT = "ms_TWT"   # milliseconds Two-Way Time
    US_TWT = "us_TWT"   # microseconds Two-Way Time

    # Velocity
    M_S = "m/s"
    KM_S = "km/s"
    FT_S = "ft/s"

    # Maturity
    PERCENT_RO = "%Ro"   # vitrinite reflectance

    # API gravity (petroleum)
    API = "API"

    def __str__(self) -> str:
        return self.value


# ---------------------------------------------------------------------------
# Conversion factors
# ---------------------------------------------------------------------------

# Conversion table: {(from_unit, to_unit): factor}
# value_to = value_from * factor
_CONVERSION_FACTORS: dict[tuple[GeoUnit, GeoUnit], float] = {
    # Length conversions
    (GeoUnit.METER, GeoUnit.KILOMETER): 1e-3,
    (GeoUnit.METER, GeoUnit.FEET): 3.28084,
    (GeoUnit.KILOMETER, GeoUnit.METER): 1e3,
    (GeoUnit.KILOMETER, GeoUnit.FEET): 3280.84,
    (GeoUnit.FEET, GeoUnit.METER): 0.3048,
    (GeoUnit.FEET, GeoUnit.KILOMETER): 3.048e-4,

    # Pressure conversions
    (GeoUnit.MPA, GeoUnit.PSI): 145.038,
    (GeoUnit.MPA, GeoUnit.KPA): 1000.0,
    (GeoUnit.MPA, GeoUnit.BAR): 10.0,
    (GeoUnit.PSI, GeoUnit.MPA): 0.00689476,
    (GeoUnit.PSI, GeoUnit.KPA): 6.89476,
    (GeoUnit.PSI, GeoUnit.BAR): 0.0689476,
    (GeoUnit.KPA, GeoUnit.MPA): 1e-3,
    (GeoUnit.KPA, GeoUnit.PSI): 0.145038,
    (GeoUnit.KPA, GeoUnit.BAR): 0.01,
    (GeoUnit.BAR, GeoUnit.MPA): 0.1,
    (GeoUnit.BAR, GeoUnit.PSI): 14.5038,
    (GeoUnit.BAR, GeoUnit.KPA): 100.0,

    # Density conversions
    (GeoUnit.KG_M3, GeoUnit.G_CM3): 1e-3,
    (GeoUnit.G_CM3, GeoUnit.KG_M3): 1e3,

    # Dimensionless
    (GeoUnit.FRACTION, GeoUnit.PERCENT): 100.0,
    (GeoUnit.PERCENT, GeoUnit.FRACTION): 0.01,

    # Velocity
    (GeoUnit.M_S, GeoUnit.KM_S): 1e-3,
    (GeoUnit.M_S, GeoUnit.FT_S): 3.28084,
    (GeoUnit.KM_S, GeoUnit.M_S): 1e3,
    (GeoUnit.KM_S, GeoUnit.FT_S): 3280.84,
    (GeoUnit.FT_S, GeoUnit.M_S): 0.3048,
    (GeoUnit.FT_S, GeoUnit.KM_S): 3.048e-4,

    # Seismic time
    (GeoUnit.MS_TWT, GeoUnit.US_TWT): 1000.0,
    (GeoUnit.US_TWT, GeoUnit.MS_TWT): 1e-3,
}

# Temperature conversions require offsets, handled separately
_TEMP_CONVERSIONS: set[tuple[GeoUnit, GeoUnit]] = {
    (GeoUnit.DEGC, GeoUnit.DEGF),
    (GeoUnit.DEGF, GeoUnit.DEGC),
}


# ---------------------------------------------------------------------------
# convert()
# ---------------------------------------------------------------------------

def convert(value: float, from_unit: GeoUnit, to_unit: GeoUnit) -> float:
    """
    Convert a value from one GeoUnit to another.

    Supports all unit pairs defined in the conversion table plus
    temperature conversions (°C ↔ °F).

    Args:
        value:     Numeric value to convert.
        from_unit: Source unit (GeoUnit enum member).
        to_unit:   Target unit (GeoUnit enum member).

    Returns:
        Converted float value.

    Raises:
        ValueError: If conversion between the given units is not defined.

    Example:
        mpa = convert(2500.0, GeoUnit.PSI, GeoUnit.MPA)  # → 17.237 MPa
        pct = convert(0.18, GeoUnit.FRACTION, GeoUnit.PERCENT)  # → 18.0 %
        ft  = convert(2500.0, GeoUnit.METER, GeoUnit.FEET)  # → 8202.1 ft
    """
    if from_unit == to_unit:
        return value

    # Temperature: offset-based conversions
    if (from_unit, to_unit) in _TEMP_CONVERSIONS:
        if from_unit == GeoUnit.DEGC and to_unit == GeoUnit.DEGF:
            return value * 9.0 / 5.0 + 32.0
        if from_unit == GeoUnit.DEGF and to_unit == GeoUnit.DEGC:
            return (value - 32.0) * 5.0 / 9.0

    # Factor-based conversions
    key = (from_unit, to_unit)
    if key in _CONVERSION_FACTORS:
        return value * _CONVERSION_FACTORS[key]

    # Try two-step via intermediate unit (e.g. PSI → m/s not defined)
    raise ValueError(
        f"No direct conversion defined from '{from_unit}' to '{to_unit}'. "
        f"Available conversions: {[f'{a} → {b}' for a, b in _CONVERSION_FACTORS]}"
    )


# ---------------------------------------------------------------------------
# parse_unit_string()
# ---------------------------------------------------------------------------

_UNIT_STRING_MAP: dict[str, GeoUnit] = {
    # METER variants
    "m": GeoUnit.METER,
    "meter": GeoUnit.METER,
    "meters": GeoUnit.METER,
    "metre": GeoUnit.METER,
    "metres": GeoUnit.METER,
    # KILOMETER variants
    "km": GeoUnit.KILOMETER,
    "kilometer": GeoUnit.KILOMETER,
    "kilometres": GeoUnit.KILOMETER,
    "kilometre": GeoUnit.KILOMETER,
    # FEET variants
    "ft": GeoUnit.FEET,
    "feet": GeoUnit.FEET,
    "foot": GeoUnit.FEET,
    # Pressure
    "psi": GeoUnit.PSI,
    "mpa": GeoUnit.MPA,
    "megapascal": GeoUnit.MPA,
    "megapascals": GeoUnit.MPA,
    "kpa": GeoUnit.KPA,
    "kilopascal": GeoUnit.KPA,
    "bar": GeoUnit.BAR,
    # Temperature
    "degc": GeoUnit.DEGC,
    "°c": GeoUnit.DEGC,
    "celsius": GeoUnit.DEGC,
    "degf": GeoUnit.DEGF,
    "°f": GeoUnit.DEGF,
    "fahrenheit": GeoUnit.DEGF,
    # Density
    "kg/m3": GeoUnit.KG_M3,
    "kg_m3": GeoUnit.KG_M3,
    "kg m-3": GeoUnit.KG_M3,
    "g/cm3": GeoUnit.G_CM3,
    "g/cc": GeoUnit.G_CM3,
    "g cm-3": GeoUnit.G_CM3,
    # Dimensionless
    "fraction": GeoUnit.FRACTION,
    "%": GeoUnit.PERCENT,
    "percent": GeoUnit.PERCENT,
    "pct": GeoUnit.PERCENT,
    # Seismic time
    "ms_twt": GeoUnit.MS_TWT,
    "ms twt": GeoUnit.MS_TWT,
    "ms": GeoUnit.MS_TWT,
    "us_twt": GeoUnit.US_TWT,
    "us twt": GeoUnit.US_TWT,
    # Velocity
    "m/s": GeoUnit.M_S,
    "m s-1": GeoUnit.M_S,
    "km/s": GeoUnit.KM_S,
    "km s-1": GeoUnit.KM_S,
    "ft/s": GeoUnit.FT_S,
    "ft s-1": GeoUnit.FT_S,
    # Maturity
    "%ro": GeoUnit.PERCENT_RO,
    "ro": GeoUnit.PERCENT_RO,
    "vr": GeoUnit.PERCENT_RO,
    # API
    "api": GeoUnit.API,
    "°api": GeoUnit.API,
}


def parse_unit_string(s: str) -> GeoUnit | None:
    """
    Parse a unit string into a GeoUnit enum member.

    Case-insensitive. Handles common abbreviations and variants.

    Args:
        s: Unit string to parse (e.g. "m/s", "MPa", "degC", "g/cm3").

    Returns:
        GeoUnit member if recognised, None otherwise.

    Example:
        parse_unit_string("m/s")   → GeoUnit.M_S
        parse_unit_string("MPa")   → GeoUnit.MPA
        parse_unit_string("g/cm3") → GeoUnit.G_CM3
        parse_unit_string("xyz")   → None
    """
    if not s:
        return None
    normalised = s.strip().lower()
    return _UNIT_STRING_MAP.get(normalised)


# ---------------------------------------------------------------------------
# format_quantity()
# ---------------------------------------------------------------------------

def format_quantity(value: float, unit: GeoUnit, uncertainty: float) -> str:
    """
    Format a value with its uncertainty into a human-readable string.

    The uncertainty is treated as a fractional (0.0–1.0) value and
    converted to an absolute ± value for display.

    Format: "{value} ± {abs_uncertainty} {unit}"

    Args:
        value:       The central value of the measurement.
        unit:        GeoUnit enum member for the unit label.
        uncertainty: Fractional uncertainty [0.0, 1.0].

    Returns:
        Formatted string, e.g.:
          "2450 ± 196 m/s"
          "0.185 ± 0.018 fraction"
          "25.3 ± 2.02 degC"

    Example:
        format_quantity(2450.0, GeoUnit.M_S, 0.08)
        → "2450.0 ± 196.0 m/s"

        format_quantity(0.18, GeoUnit.FRACTION, 0.10)
        → "0.18 ± 0.018 fraction"
    """
    abs_uncertainty = abs(value * uncertainty)
    unit_str = unit.value

    # Determine number of significant figures based on magnitude
    if abs(value) >= 1000:
        val_str = f"{value:.1f}"
        unc_str = f"{abs_uncertainty:.1f}"
    elif abs(value) >= 10:
        val_str = f"{value:.2f}"
        unc_str = f"{abs_uncertainty:.2f}"
    elif abs(value) >= 1:
        val_str = f"{value:.3f}"
        unc_str = f"{abs_uncertainty:.3f}"
    else:
        val_str = f"{value:.4f}"
        unc_str = f"{abs_uncertainty:.4f}"

    return f"{val_str} ± {unc_str} {unit_str}"
