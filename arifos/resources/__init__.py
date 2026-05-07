import json


async def well_agi() -> str:
    return json.dumps(
        {
            "uri": "organ://well/agi",
            "organ": "WELL",
            "maps_to": "AGI",
            "purpose": "Biological substrate, operator readiness, stability",
            "status": "available",
        },
        ensure_ascii=False,
    )


async def wealth_asi() -> str:
    return json.dumps(
        {
            "uri": "organ://wealth/asi",
            "organ": "WEALTH",
            "maps_to": "ASI",
            "purpose": "Capital engine, resource allocation, operational economics",
            "status": "available",
        },
        ensure_ascii=False,
    )


async def geox_apex() -> str:
    return json.dumps(
        {
            "uri": "organ://geox/apex",
            "organ": "GEOX",
            "maps_to": "APEX",
            "purpose": "Earth intelligence, spatial and subsurface witness context",
            "status": "available",
        },
        ensure_ascii=False,
    )


RESOURCES = {
    "organ://well/agi": well_agi,
    "organ://wealth/asi": wealth_asi,
    "organ://geox/apex": geox_apex,
}

__all__ = ["RESOURCES", "geox_apex", "wealth_asi", "well_agi"]
