"""
Ember open data adapter for electricity generation, demand, and emissions.
Docs: https://ember-energy.org/data/
"""

import csv
import io
from typing import List, Optional
from urllib.parse import urlencode
from urllib.request import urlopen, Request

from host.ingest.schema import DataRecord

# Ember yearly full release (long format) — stable enough for MVP
# Users can override with EMBER_CSV_URL env var if the URL changes.
import os
DEFAULT_EMBER_URL = "https://storage.googleapis.com/emb-prod-bkt-publicdata/public-downloads/yearly_full_release_long_format.csv"
EMBER_CSV_URL = os.environ.get("EMBER_CSV_URL", DEFAULT_EMBER_URL)


def _fetch_csv(url: str) -> List[dict]:
    req = Request(url, headers={"User-Agent": "WEALTH-ingest/1.4.0"})
    with urlopen(req, timeout=60) as resp:
        text = resp.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def fetch_electricity_data(
    entity_code: Optional[str] = None,
    year: Optional[int] = None,
    variable: Optional[str] = None,
) -> List[DataRecord]:
    """
    Fetch Ember yearly electricity data.
    Filters by country (entity_code ISO3), year, and/or variable (e.g. 'Demand', 'Generation').
    """
    rows = _fetch_csv(EMBER_CSV_URL)
    retrieval = DataRecord.now()

    records = []
    for row in rows:
        row_year = row.get("Year", "")
        row_country = row.get("Country code", "")
        row_variable = row.get("Variable", "")

        if entity_code and row_country.upper() != entity_code.upper():
            continue
        if year and str(row_year) != str(year):
            continue
        if variable and variable.lower() not in row_variable.lower():
            continue

        val = row.get("Value")
        try:
            value = float(val) if val not in (None, "", "NaN") else None
        except (ValueError, TypeError):
            value = None

        records.append(
            DataRecord(
                source_system="Ember",
                series_id=f"ember:{row_variable}:{row_country}",
                entity_code=row_country,
                observation_time=f"{row_year}-12-31",
                release_time=None,
                retrieval_time=retrieval,
                value=value,
                unit=row.get("Unit", ""),
                frequency="annual",
                revision_flag=False,
                methodology_url="https://ember-energy.org/data/data-methods/",
                metadata={
                    "country": row.get("Country", ""),
                    "variable": row_variable,
                    "category": row.get("Category", ""),
                    "subcategory": row.get("Subcategory", ""),
                },
                bus="slow",
            )
        )
    return records


def fetch_demand(entity_code: str, year: Optional[int] = None) -> List[DataRecord]:
    return fetch_electricity_data(entity_code=entity_code, year=year, variable="Demand")


def fetch_generation(entity_code: str, year: Optional[int] = None) -> List[DataRecord]:
    return fetch_electricity_data(entity_code=entity_code, year=year, variable="Generation")


def fetch_carbon_intensity(entity_code: str, year: Optional[int] = None) -> List[DataRecord]:
    return fetch_electricity_data(entity_code=entity_code, year=year, variable="CO2 intensity")
