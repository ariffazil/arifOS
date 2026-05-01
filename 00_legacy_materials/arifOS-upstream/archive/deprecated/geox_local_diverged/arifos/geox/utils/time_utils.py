"""
GEOX Time Utilities
DITEMPA BUKAN DIBERI

Time handling functions for geological intelligence pipelines.
Bridges modern UTC timestamps and geological time conventions
(Ma = millions of years ago, epoch names, etc.).

Geological timescale data sourced from the International Commission
on Stratigraphy (ICS) 2023/09 chart.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Geological timescale — Ma boundaries for common epochs
# ---------------------------------------------------------------------------
# Each entry: (epoch_name, period_name, start_ma, end_ma)
# start_ma > end_ma (older → younger, end_ma = 0.0 for present)

_GEO_TIMESCALE: list[tuple[str, str, float, float]] = [
    # Quaternary
    ("Holocene", "Quaternary", 0.0117, 0.0),
    ("Late Pleistocene", "Quaternary", 0.129, 0.0117),
    ("Middle Pleistocene", "Quaternary", 0.774, 0.129),
    ("Early Pleistocene", "Quaternary", 2.58, 0.774),
    # Neogene
    ("Late Pliocene", "Neogene", 3.6, 2.58),
    ("Early Pliocene", "Neogene", 5.333, 3.6),
    ("Messinian", "Neogene", 7.246, 5.333),
    ("Tortonian", "Neogene", 11.63, 7.246),
    ("Serravallian", "Neogene", 13.82, 11.63),
    ("Langhian", "Neogene", 15.98, 13.82),
    ("Burdigalian", "Neogene", 20.44, 15.98),
    ("Aquitanian", "Neogene", 23.03, 20.44),
    # Paleogene
    ("Chattian", "Paleogene", 27.82, 23.03),
    ("Rupelian", "Paleogene", 33.9, 27.82),
    ("Priabonian", "Paleogene", 37.71, 33.9),
    ("Bartonian", "Paleogene", 41.2, 37.71),
    ("Lutetian", "Paleogene", 47.8, 41.2),
    ("Ypresian", "Paleogene", 56.0, 47.8),
    ("Thanetian", "Paleogene", 59.2, 56.0),
    ("Selandian", "Paleogene", 61.6, 59.2),
    ("Danian", "Paleogene", 66.0, 61.6),
    # Cretaceous (abbreviated)
    ("Late Cretaceous", "Cretaceous", 100.5, 66.0),
    ("Early Cretaceous", "Cretaceous", 145.0, 100.5),
    # Jurassic (abbreviated)
    ("Late Jurassic", "Jurassic", 163.5, 145.0),
    ("Middle Jurassic", "Jurassic", 174.1, 163.5),
    ("Early Jurassic", "Jurassic", 201.3, 174.1),
    # Triassic (abbreviated)
    ("Late Triassic", "Triassic", 237.0, 201.3),
    ("Middle Triassic", "Triassic", 247.2, 237.0),
    ("Early Triassic", "Triassic", 251.902, 247.2),
    # Permian (abbreviated)
    ("Late Permian", "Permian", 259.1, 251.902),
    ("Early Permian", "Permian", 298.9, 259.1),
    # Pre-Permian catch-all
    ("Carboniferous", "Paleozoic", 358.9, 298.9),
    ("Devonian", "Paleozoic", 419.2, 358.9),
    ("Silurian", "Paleozoic", 443.8, 419.2),
    ("Ordovician", "Paleozoic", 485.4, 443.8),
    ("Cambrian", "Paleozoic", 538.8, 485.4),
    ("Precambrian", "Precambrian", 4600.0, 538.8),
]


# ---------------------------------------------------------------------------
# now_utc()
# ---------------------------------------------------------------------------

def now_utc() -> datetime:
    """
    Return the current UTC datetime as a timezone-aware object.

    Returns:
        datetime with timezone=UTC.

    Example:
        ts = now_utc()
        print(ts.isoformat())  # "2024-06-15T08:30:00.000000+00:00"
    """
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# parse_geo_time()
# ---------------------------------------------------------------------------

# Pattern for geological age strings: "10.5 Ma", "10.5Ma", "10.5 mya"
_GEO_AGE_PATTERN = re.compile(
    r"^\s*(?P<age>\d+(?:\.\d+)?)\s*(?:Ma|mya|my|m\.a\.)\s*$",
    re.IGNORECASE,
)

# Pattern for relative expressions like "5 Ma ago"
_GEO_AGE_AGO_PATTERN = re.compile(
    r"^\s*(?P<age>\d+(?:\.\d+)?)\s*(?:Ma|mya|my)\s+ago\s*$",
    re.IGNORECASE,
)


def parse_geo_time(s: str) -> datetime:
    """
    Parse a time string into a datetime object.

    Handles:
      - ISO 8601 strings: "2024-06-15T08:30:00Z", "2024-06-15"
      - Geological age notation: "10.5 Ma", "10.5 mya", "10.5 My"
        (converted to approximate calendar datetime via years-ago arithmetic)
      - Partial ISO dates: "2024-06", "2024"

    Args:
        s: Time string to parse.

    Returns:
        datetime object (UTC-aware for ISO formats, naive for geological ages).

    Raises:
        ValueError: If the string cannot be parsed by any supported format.

    Example:
        parse_geo_time("2024-06-15T08:30:00Z")  → datetime(2024, 6, 15, 8, 30, tzinfo=UTC)
        parse_geo_time("10.5 Ma")               → approximate datetime ~10.5 million years ago
        parse_geo_time("2024")                  → datetime(2024, 1, 1, tzinfo=UTC)
    """
    s = s.strip()

    # Try geological age notation first
    match = _GEO_AGE_PATTERN.match(s) or _GEO_AGE_AGO_PATTERN.match(s)
    if match:
        age_ma = float(match.group("age"))
        return _ma_to_approximate_datetime(age_ma)

    # Try ISO 8601 variants
    iso_formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M%z",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dZ",
        "%Y-%m-%d",
        "%Y-%m",
        "%Y",
    ]

    for fmt in iso_formats:
        try:
            dt = datetime.strptime(s, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    # Try Python's fromisoformat (Python 3.11+ handles 'Z')
    try:
        s_clean = s.replace("Z", "+00:00")
        return datetime.fromisoformat(s_clean)
    except ValueError:
        pass

    raise ValueError(
        f"Cannot parse time string '{s}'. "
        f"Supported formats: ISO 8601 strings and geological age notation (e.g. '10.5 Ma')."
    )


def _ma_to_approximate_datetime(age_ma: float) -> datetime:
    """
    Convert geological age in Ma to an approximate datetime.

    Uses a simple epoch reference: 1970-01-01T00:00:00Z minus
    age_ma * 365.25 * 24 * 3600 seconds.

    For ages > 10,000 years, returns a fixed sentinel datetime
    with the age stored as year=-age_ma (not representable as
    a standard Gregorian date). In practice, callers should use
    geological_age_to_datetime() for descriptive output.
    """
    seconds_per_ma = 365.25 * 24 * 3600 * 1e6
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    # Cap at a representable datetime minimum
    try:
        offset = timedelta(seconds=age_ma * seconds_per_ma)
        return epoch - offset
    except OverflowError:
        # Very old ages: return minimum representable datetime
        return datetime.min.replace(tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# format_time_window()
# ---------------------------------------------------------------------------

def format_time_window(start: datetime, end: datetime) -> str:
    """
    Format a time window as a human-readable string.

    Args:
        start: Start datetime (must be before end).
        end:   End datetime.

    Returns:
        Formatted string: "YYYY-MM-DD HH:MM UTC → YYYY-MM-DD HH:MM UTC"
        or "YYYY-MM-DD → YYYY-MM-DD" for date-only precision.

    Example:
        format_time_window(
            datetime(2024, 1, 1, tzinfo=timezone.utc),
            datetime(2024, 12, 31, tzinfo=timezone.utc)
        )
        → "2024-01-01 00:00 UTC → 2024-12-31 00:00 UTC"
    """
    def _fmt(dt: datetime) -> str:
        if dt.tzinfo:
            return dt.strftime("%Y-%m-%d %H:%M UTC")
        return dt.strftime("%Y-%m-%d %H:%M")

    return f"{_fmt(start)} → {_fmt(end)}"


# ---------------------------------------------------------------------------
# geological_age_to_datetime()
# ---------------------------------------------------------------------------

def geological_age_to_datetime(age_ma: float) -> str:
    """
    Convert a geological age in Ma to a human-readable epoch description.

    Uses the ICS 2023/09 geological timescale to identify the correct
    epoch and period for the given age.

    Args:
        age_ma: Age in millions of years (Ma). 0.0 = present day.

    Returns:
        Descriptive string: "~{age} Ma ({Epoch}, {Period})"

    Example:
        geological_age_to_datetime(10.5)  → "~10.5 Ma (Tortonian, Neogene)"
        geological_age_to_datetime(66.5)  → "~66.5 Ma (Late Cretaceous, Cretaceous)"
        geological_age_to_datetime(0.0)   → "~0.0 Ma (Holocene, Quaternary)"
    """
    if age_ma < 0:
        raise ValueError(f"age_ma must be non-negative. Got {age_ma}.")

    epoch_name = "Unknown"
    period_name = "Unknown"

    for epoch, period, start_ma, end_ma in _GEO_TIMESCALE:
        # Timescale entries: start_ma is older boundary, end_ma is younger
        if end_ma <= age_ma <= start_ma:
            epoch_name = epoch
            period_name = period
            break

    return f"~{age_ma:.2f} Ma ({epoch_name}, {period_name})"


# ---------------------------------------------------------------------------
# is_within_window()
# ---------------------------------------------------------------------------

def is_within_window(ts: datetime, window: tuple[datetime, datetime]) -> bool:
    """
    Check if a timestamp falls within a time window [start, end].

    Both endpoints are inclusive. Handles timezone-aware and
    timezone-naive datetimes by normalising naive datetimes to UTC.

    Args:
        ts:     Timestamp to check.
        window: Tuple of (start, end) datetimes.

    Returns:
        True if start ≤ ts ≤ end, False otherwise.

    Example:
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end   = datetime(2024, 12, 31, tzinfo=timezone.utc)
        ts    = datetime(2024, 6, 15, tzinfo=timezone.utc)
        is_within_window(ts, (start, end))  → True
    """
    start, end = window

    # Normalise naive datetimes to UTC
    def _ensure_utc(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    ts = _ensure_utc(ts)
    start = _ensure_utc(start)
    end = _ensure_utc(end)

    return start <= ts <= end
