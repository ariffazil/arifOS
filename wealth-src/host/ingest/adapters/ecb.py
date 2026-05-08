"""
ECB Data Portal adapter (SDMX-CSV simplified).
Docs: https://data.ecb.europa.eu/help/api/overview
"""

import csv
import io
from typing import List, Optional
from urllib.parse import urlencode
from urllib.request import urlopen, Request

from host.ingest.schema import DataRecord

BASE_URL = "https://data-api.ecb.europa.eu/data"


def _fetch_csv(url: str) -> List[dict]:
    req = Request(url, headers={"User-Agent": "WEALTH-ingest/1.4.0"})
    with urlopen(req, timeout=45) as resp:
        text = resp.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def fetch_series(
    flow_ref: str,
    key: str = "",
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    entity_code: str = "EA",
) -> List[DataRecord]:
    """
    Fetch ECB SDMX series as CSV.
    Example flow_ref='EXR', key='D.USD.EUR.SP00.A' (daily USD/EUR spot)
    """
    path = f"{flow_ref}/{key}".rstrip("/")
    params = {"format": "csv"}
    if start_period:
        params["startPeriod"] = start_period
    if end_period:
        params["endPeriod"] = end_period

    url = f"{BASE_URL}/{path}?{urlencode(params)}"
    rows = _fetch_csv(url)
    retrieval = DataRecord.now()

    records = []
    for row in rows:
        time = row.get("TIME_PERIOD") or row.get("DATE") or row.get("obsTime")
        val = row.get("OBS_VALUE")
        try:
            value = float(val) if val not in (None, "", "NaN") else None
        except (ValueError, TypeError):
            value = None
        freq = row.get("FREQ") or row.get("frequency")
        unit = row.get("UNIT") or row.get("TITLE_COMPL")
        series = row.get("SERIES_NAME") or row.get("TITLE") or f"{flow_ref}:{key}"
        records.append(
            DataRecord(
                source_system="ECB",
                series_id=series,
                entity_code=entity_code,
                observation_time=str(time) if time else "",
                release_time=None,
                retrieval_time=retrieval,
                value=value,
                unit=unit,
                frequency=_map_freq(freq),
                revision_flag=False,
                methodology_url=f"https://data.ecb.europa.eu/data/datasets/{flow_ref}",
                metadata={"flow_ref": flow_ref, "key": key, **row},
                bus="daily" if freq in {"D", "B", "W"} else "slow",
            )
        )
    return records


def _map_freq(code: Optional[str]) -> str:
    mapping = {
        "D": "daily",
        "B": "daily",
        "W": "weekly",
        "M": "monthly",
        "Q": "quarterly",
        "A": "annual",
        "H": "semiannual",
    }
    return mapping.get(str(code).upper(), "unknown") if code else "unknown"


def fetch_fx_rate(currency: str = "USD", base: str = "EUR") -> List[DataRecord]:
    """Daily FX spot rate wrapper."""
    key = f"D.{currency}.{base}.SP00.A"
    return fetch_series("EXR", key, entity_code=base)


def fetch_policy_rate() -> List[DataRecord]:
    """ECB deposit facility rate (key policy rate)."""
    key = "D.FR.M.DE+ES+FR+IT.N"
    return fetch_series("FM", key, entity_code="EA")
