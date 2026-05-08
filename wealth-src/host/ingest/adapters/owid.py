"""
Our World in Data (OWID) Chart API adapter.
Docs: https://docs.owid.io/projects/etl/api/chart-api/
"""

import csv
import io
import json
from typing import List, Optional
from urllib.request import urlopen, Request

from host.ingest.schema import DataRecord

BASE_URL = "https://ourworldindata.org/grapher"


def _fetch_json(url: str) -> dict:
    req = Request(url, headers={"User-Agent": "WEALTH-ingest/1.4.0"})
    with urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_csv(url: str) -> List[dict]:
    req = Request(url, headers={"User-Agent": "WEALTH-ingest/1.4.0"})
    with urlopen(req, timeout=45) as resp:
        text = resp.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def fetch_series(
    slug: str,
    entity_code: Optional[str] = None,
) -> List[DataRecord]:
    """
    Fetch OWID grapher series by slug.
    Example slug: 'carbon-intensity-electricity'
    """
    csv_url = f"{BASE_URL}/{slug}.csv"
    meta_url = f"{BASE_URL}/{slug}.metadata.json"

    rows = _fetch_csv(csv_url)
    try:
        meta = _fetch_json(meta_url)
    except Exception:
        meta = {}

    retrieval = DataRecord.now()
    indicators = meta.get("dimensions", {}).get("indicators", {}).get("values", [])
    indicator = indicators[0] if indicators else {}
    unit = indicator.get("display", {}).get("unit") or indicator.get("unit", "")
    short_name = indicator.get("name", slug)
    methodology = indicator.get("descriptionProcessing") or indicator.get("descriptionKey", "")
    source_info = indicator.get("source", {})
    source_name = source_info.get("name", "Our World in Data") if isinstance(source_info, dict) else "Our World in Data"

    time_col = "Year" if any(r.get("Year") for r in rows[:5]) else "Day"
    records = []
    for row in rows:
        code = row.get("Code", "")
        if entity_code and code.upper() != entity_code.upper():
            continue

        time_val = row.get(time_col, "")
        val_key = [k for k in row.keys() if k not in ("Entity", "Code", "Year", "Day")][0]
        val = row.get(val_key)
        try:
            value = float(val) if val not in (None, "", "NaN") else None
        except (ValueError, TypeError):
            value = None

        records.append(
            DataRecord(
                source_system="OWID",
                series_id=slug,
                entity_code=code or row.get("Entity", ""),
                observation_time=str(time_val),
                release_time=None,
                retrieval_time=retrieval,
                value=value,
                unit=unit,
                frequency="annual" if time_col == "Year" else "daily",
                revision_flag=False,
                methodology_url=meta.get("originUrl") or f"https://ourworldindata.org/grapher/{slug}",
                metadata={
                    "indicator_name": short_name,
                    "source_name": source_name,
                    "entity_name": row.get("Entity", ""),
                    "owid_slug": slug,
                },
                bus="slow" if time_col == "Year" else "daily",
            )
        )
    return records


def fetch_carbon_intensity(entity_code: str) -> List[DataRecord]:
    return fetch_series("carbon-intensity-electricity", entity_code=entity_code)
