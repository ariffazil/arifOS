"""
World Bank Open Data adapter.
Docs: https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures
"""

import json
from typing import List, Optional
from urllib.parse import urlencode
from urllib.request import urlopen, Request

from host.ingest.schema import DataRecord

BASE_URL = "https://api.worldbank.org/v2"


def _fetch(url: str) -> list:
    req = Request(url, headers={"User-Agent": "WEALTH-ingest/1.4.0", "Accept": "application/json"})
    with urlopen(req, timeout=45) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    # WB API returns [metadata, data]
    return data[1] if isinstance(data, list) and len(data) > 1 else []


def fetch_indicator(
    indicator: str,
    country_code: str = "all",
    date_range: Optional[str] = None,
    frequency: Optional[str] = None,
) -> List[DataRecord]:
    """
    Fetch World Bank indicator series.
    Example indicator: NY.GDP.MKTP.KD.ZG (GDP growth annual)
    """
    params = {
        "format": "json",
        "per_page": 1000,
    }
    if date_range:
        params["date"] = date_range
    if frequency:
        params["frequency"] = frequency

    url = f"{BASE_URL}/country/{country_code}/indicator/{indicator}?{urlencode(params)}"
    rows = _fetch(url)
    retrieval = DataRecord.now()

    # Try to get indicator metadata
    meta_url = f"{BASE_URL}/indicator/{indicator}?format=json"
    meta_rows = _fetch(meta_url)
    meta = meta_rows[0] if meta_rows else {}
    unit = meta.get("unit", "")
    name = meta.get("name", "")
    source = meta.get("source", {})
    source_org = source.get("value", "")
    methodology = meta.get("sourceNote", "")

    records = []
    for row in rows:
        val = row.get("value")
        try:
            value = float(val) if val is not None else None
        except (ValueError, TypeError):
            value = None
        records.append(
            DataRecord(
                source_system="WorldBank",
                series_id=indicator,
                entity_code=row.get("country", {}).get("id", country_code),
                observation_time=str(row.get("date", "")),
                release_time=None,
                retrieval_time=retrieval,
                value=value,
                unit=unit,
                frequency=frequency or "annual",
                revision_flag=bool(row.get("decimal")),
                methodology_url=methodology if methodology.startswith("http") else None,
                metadata={
                    "indicator_name": name,
                    "source_org": source_org,
                    "country_name": row.get("country", {}).get("value", ""),
                },
                bus="slow",
            )
        )
    return records
