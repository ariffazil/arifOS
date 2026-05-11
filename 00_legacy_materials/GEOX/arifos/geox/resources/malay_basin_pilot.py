"""
GEOX MCP Resources — Malay Basin Pilot Data
DITEMPA BUKAN DIBERI

Structured data for the Malay Basin petroleum exploration demo.
Derived from the 50-year exploration study (1968–2018).
"""

from __future__ import annotations
from typing import Any

MALAY_BASIN_STATS = {
    "name": "Malay Basin",
    "period": "1968–2018",
    "area_km2": 83000,
    "discoveries": 181,
    "total_wells": 2100,
    "exploratory_wells_pre_2014": 700,
    "cumulative_resource_bboe": 14.8,
    "resource_concentration_pct": 40,
    "median_field_size_mmboe": 82.7,
    "remaining_potential_bboe": 2.0,
    "well_density_index": 42.2,
}

CREAMING_CURVE_PHASES = [
    {
        "phase": "EDP1",
        "period": "1968–1976",
        "description": "Basin-centre anticlinal play",
        "resource_added_bboe": 8.7,
        "percentage_of_total": 60,
        "median_field_mmboe": 191.6,
    },
    {
        "phase": "EDP2",
        "period": "1977–1989",
        "description": "Basin-centre play exhaustion; giant fields plateau",
        "resource_added_bboe": 2.5,  # Estimated delta
    },
    {
        "phase": "EDP3",
        "period": "1990–2000",
        "description": "Flank plays rejuvenation (NE ramp, JDA)",
        "resource_added_bboe": 1.5,
    },
    {
        "phase": "EDP4",
        "period": "2001–2010",
        "description": "Marginal fields, deep reservoirs",
        "average_discovery_mmboe": 50,
    },
    {
        "phase": "EDP5",
        "period": "2011–2018",
        "description": "Residual mop-up; HPHT, tight sands, fractured basement",
        "state": "Mopping phase",
    },
]

PLAY_TYPES = [
    {
        "code": "P1",
        "type": "Basin-centre anticline",
        "examples": "Tapis, Jerneh, Dulang",
        "resource_pct": 60,
        "median_mmboe": 191.6,
    },
    {
        "code": "P2",
        "type": "Basin-centre fault-related",
        "examples": "Gajah, Cakerawala",
        "resource_pct": None,
        "median_mmboe": None,
    },
    {
        "code": "P3",
        "type": "Normal fault/dip closure",
        "examples": "Bergading, Abu",
        "resource_pct": "Medium",
        "median_mmboe": 52,
    },
    {
        "code": "P4",
        "type": "Eastern half-graben",
        "examples": "Bunga Pakma, Raya",
        "resource_pct": "Small",
        "median_mmboe": 31,
    },
    {
        "code": "P5",
        "type": "Western Hinge Fault Zone",
        "examples": "Resak, Beranang",
        "resource_pct": "Medium",
        "median_mmboe": None,
    },
    {
        "code": "P6",
        "type": "Tenggol Arch basement-drape",
        "examples": "Malong",
        "resource_pct": "Niche",
        "median_mmboe": None,
    },
    {
        "code": "P7",
        "type": "Fractured basement",
        "examples": "Anding (hold)",
        "resource_pct": "Frontier",
        "median_mmboe": None,
    },
    {
        "code": "P8",
        "type": "Stratigraphic channel",
        "examples": "Bindu, Seroja",
        "resource_pct": "Small",
        "median_mmboe": None,
    },
    {
        "code": "P9",
        "type": "Deep HPHT/tight/synrift",
        "examples": "Bergading Deep, Sepat",
        "resource_pct": "Emerging",
        "median_mmboe": None,
    },
]

# Geometries for visual pilots (Approximate polygons/points for demo purposes)
MALAY_BASIN_GEOMETRY = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "id": "basin_boundary",
            "properties": {"name": "Malay Basin Boundary", "type": "Basin"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [102.0, 5.0],
                        [105.0, 7.5],
                        [107.0, 5.0],
                        [105.0, 3.0],
                        [102.0, 5.0],
                    ]
                ],
            },
        },
        {
            "type": "Feature",
            "id": "p1_zone",
            "properties": {
                "name": "P1: Basin-centre Anticline",
                "play": "P1",
                "fill": "#ff4444",
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [103.5, 5.5],
                        [105.0, 6.0],
                        [105.5, 5.5],
                        [104.5, 4.5],
                        [103.5, 5.5],
                    ]
                ],
            },
        },
        {
            "type": "Feature",
            "id": "tapis_field",
            "properties": {
                "name": "Tapis Field",
                "type": "Oil Field",
                "play": "P1",
                "discovery_year": 1969,
            },
            "geometry": {"type": "Point", "coordinates": [104.9, 5.5]},
        },
        {
            "type": "Feature",
            "id": "jerneh_field",
            "properties": {
                "name": "Jerneh Field",
                "type": "Gas Field",
                "play": "P1",
                "discovery_year": 1973,
            },
            "geometry": {"type": "Point", "coordinates": [103.8, 6.5]},
        },
    ],
}


class MalayBasinPilotResource:
    """
    URI: geox://basin/malay-basin/pilot

    Integrated feasibility data for the Malay Basin demo.
    """

    uri_template = "geox://basin/malay-basin/pilot"

    async def read(self) -> dict[str, Any]:
        return {
            "uri": "geox://basin/malay-basin/pilot",
            "stats": MALAY_BASIN_STATS,
            "phases": CREAMING_CURVE_PHASES,
            "play_types": PLAY_TYPES,
            "geometry": MALAY_BASIN_GEOMETRY,
            "provenance": "GEOLOGICAL_SOCIETY_MALAYSIA_2018",
            "status": "DEMO_READY",
        }
