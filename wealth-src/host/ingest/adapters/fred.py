"""
FRED / ALFRED adapter for US macro, rates, and vintage history.
Docs: https://fred.stlouisfed.org/docs/api/fred/
"""

import json
import os
from typing import List, Optional
from urllib.parse import urlencode
from urllib.request import urlopen, Request

from host.ingest.schema import DataRecord

FRED_API_KEY = os.environ.get("FRED_API_KEY", "")
BASE_URL = "https://api.stlouisfed.org/fred"


def _fetch(url: str) -> dict:
    req = Request(url, headers={"User-Agent": "WEALTH-ingest/1.4.0"})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_series(
    series_id: str,
    entity_code: str = "USA",
    frequency: Optional[str] = None,
    observation_start: Optional[str] = None,
    observation_end: Optional[str] = None,
    vintage_dates: Optional[List[str]] = None,
) -> List[DataRecord]:
    if not FRED_API_KEY:
        raise RuntimeError("FRED_API_KEY is not configured")

    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1000,
    }
    if observation_start:
        params["observation_start"] = observation_start
    if observation_end:
        params["observation_end"] = observation_end
    if frequency:
        params["frequency"] = frequency

    endpoint = "series/observations"
    if vintage_dates:
        endpoint = "series/observations"
        params["vintage_dates"] = ",".join(vintage_dates)

    url = f"{BASE_URL}/{endpoint}?{urlencode(params)}"
    data = _fetch(url)

    # Fetch series metadata for unit/frequency
    meta_url = f"{BASE_URL}/series?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
    meta = _fetch(meta_url).get("seriess", [{}])[0]

    unit = meta.get("units")
    freq = meta.get("frequency")
    title = meta.get("title", "")
    retrieval = DataRecord.now()

    records = []
    for obs in data.get("observations", []):
        val = obs.get("value")
        try:
            value = float(val) if val not in (None, ".", "") else None
        except (ValueError, TypeError):
            value = None
        vintage_date = obs.get("vintage_date")
        realtime_start = obs.get("realtime_start")
        records.append(
            DataRecord(
                source_system="FRED",
                series_id=series_id,
                entity_code=entity_code,
                observation_time=obs["date"],
                release_time=realtime_start,
                retrieval_time=retrieval,
                value=value,
                unit=unit,
                frequency=freq or frequency,
                revision_flag=bool(vintage_date) and bool(realtime_start) and realtime_start != vintage_date,
                vintage_id=vintage_date,
                methodology_url=f"https://fred.stlouisfed.org/series/{series_id}",
                metadata={"title": title, "vintage_date": vintage_date, "realtime_end": obs.get("realtime_end")},
                bus="daily" if freq in {"d", "w", "bw", "wef"} else "slow",
            )
        )
    return records


def fetch_vintage_dates(series_id: str) -> List[str]:
    if not FRED_API_KEY:
        raise RuntimeError("FRED_API_KEY is not configured")
    url = f"{BASE_URL}/series/vintagedates?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
    data = _fetch(url)
    return [v for v in data.get("vintage_dates", []) if v]
