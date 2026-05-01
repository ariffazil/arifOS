"""
GEOX Utility Modules
DITEMPA BUKAN DIBERI

Utility subpackage for the GEOX geological intelligence coprocessor.

Modules:
    provenance  — Build, verify, and merge ProvenanceRecord objects
    units       — GeoUnit enum, conversion, and formatting functions
    time_utils  — Geological time parsing and UTC timestamp utilities
"""

from arifos.geox.utils.provenance import (
    build_provenance,
    compute_checksum,
    merge_provenances,
    verify_provenance_chain,
)
from arifos.geox.utils.time_utils import (
    format_time_window,
    geological_age_to_datetime,
    is_within_window,
    now_utc,
    parse_geo_time,
)
from arifos.geox.utils.units import (
    GeoUnit,
    convert,
    format_quantity,
    parse_unit_string,
)

__all__ = [
    # provenance
    "build_provenance",
    "compute_checksum",
    "verify_provenance_chain",
    "merge_provenances",
    # units
    "GeoUnit",
    "convert",
    "parse_unit_string",
    "format_quantity",
    # time_utils
    "now_utc",
    "parse_geo_time",
    "format_time_window",
    "geological_age_to_datetime",
    "is_within_window",
]
