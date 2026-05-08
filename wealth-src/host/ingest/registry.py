"""
Ingest registry and bus manager.
Handles 4 buses: slow, daily, fast, archive.
Provides caching, health tracking, stale detection, and series metadata registry.
"""

import inspect
import json
import os
import tempfile
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from host.ingest.schema import DataRecord, validate_record
from host.ingest.health import get_tracker


def _resolve_cache_dir() -> str:
    configured = os.environ.get(
        "WEALTH_CACHE_DIR",
        os.path.join(os.getcwd(), "data", "ingest_cache"),
    )
    try:
        os.makedirs(configured, exist_ok=True)
        probe = os.path.join(configured, ".write-test")
        with open(probe, "w", encoding="utf-8") as handle:
            handle.write("")
        os.remove(probe)
        return configured
    except OSError:
        fallback = os.path.join(tempfile.gettempdir(), "wealth", "ingest_cache")
        os.makedirs(fallback, exist_ok=True)
        return fallback


CACHE_DIR = _resolve_cache_dir()

BUS_TTL_HOURS = {
    "slow": 24 * 7,      # weekly refresh for macro
    "daily": 24,         # daily refresh for rates/FX
    "fast": 1,           # hourly refresh for energy grid
    "archive": 24 * 30,  # monthly refresh for vintages
}

OBSERVATION_FRESHNESS_DAYS = {
    "annual": 730,      # 2 years
    "quarterly": 180,
    "monthly": 60,
    "weekly": 14,
    "daily": 7,
    "intraday": 1,
}


def _cache_path(series_id: str, source: str, entity_code: str) -> str:
    safe = f"{source}_{entity_code}_{series_id}".replace("/", "_").replace(":", "_")
    return os.path.join(CACHE_DIR, f"{safe}.json")


def _is_fresh(path: str, bus: str) -> bool:
    if not os.path.exists(path):
        return False
    mtime = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)
    ttl = timedelta(hours=BUS_TTL_HOURS.get(bus, 24))
    return datetime.now(timezone.utc) - mtime < ttl


def _cache_age_hours(path: str) -> float:
    if not os.path.exists(path):
        return float("inf")
    mtime = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)
    return (datetime.now(timezone.utc) - mtime).total_seconds() / 3600.0


def load_cache(series_id: str, source: str, entity_code: str, bus: str) -> Optional[List[DataRecord]]:
    path = _cache_path(series_id, source, entity_code)
    if not _is_fresh(path, bus):
        return None
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [DataRecord(**item) for item in raw]


def save_cache(records: List[DataRecord]) -> None:
    if not records:
        return
    first = records[0]
    path = _cache_path(first.series_id, first.source_system, first.entity_code)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump([r.to_dict() for r in records], f, indent=2)
    except OSError:
        return


def _field_completeness(records: List[DataRecord]) -> float:
    if not records:
        return 0.0
    total_fields = 0
    filled_fields = 0
    required = ["source_system", "series_id", "entity_code", "observation_time", "value", "unit", "retrieval_time"]
    for r in records:
        total_fields += len(required)
        for field in required:
            val = getattr(r, field)
            if val is not None and val != "":
                filled_fields += 1
    return filled_fields / total_fields if total_fields > 0 else 0.0


def _latest_observation(records: List[DataRecord]) -> Optional[str]:
    if not records:
        return None
    times = [r.observation_time for r in records if r.observation_time]
    return max(times) if times else None


def _is_observation_stale(observation_time: Optional[str], frequency: Optional[str]) -> bool:
    if not observation_time:
        return True
    try:
        obs = datetime.fromisoformat(observation_time.replace("Z", "+00:00"))
    except Exception:
        return True
    threshold_days = OBSERVATION_FRESHNESS_DAYS.get(frequency or "annual", 730)
    return (datetime.now(timezone.utc) - obs) > timedelta(days=threshold_days)


class IngestRegistry:
    """Unified registry for fetching, caching, validating, and health-tracking data records."""

    def __init__(self):
        self._adapters: Dict[str, Any] = {}
        self._health = get_tracker()
        self._register_defaults()

    def _register_defaults(self):
        try:
            from host.ingest.adapters import fred
            self._adapters["FRED"] = fred
        except Exception:
            pass
        try:
            from host.ingest.adapters import worldbank
            self._adapters["WorldBank"] = worldbank
        except Exception:
            pass
        try:
            from host.ingest.adapters import ecb
            self._adapters["ECB"] = ecb
        except Exception:
            pass
        try:
            from host.ingest.adapters import ember
            self._adapters["Ember"] = ember
        except Exception:
            pass
        try:
            from host.ingest.adapters import owid
            self._adapters["OWID"] = owid
        except Exception:
            pass

    def available_sources(self) -> List[str]:
        return list(self._adapters.keys())

    def fetch(
        self,
        source: str,
        series_id: str,
        entity_code: str,
        use_cache: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        adapter = self._adapters.get(source)
        if adapter is None:
            self._health.record_attempt(source, False, 0.0, error_message=f"ADAPTER_NOT_FOUND:{source}")
            return {
                "records": [],
                "flags": [f"ADAPTER_NOT_FOUND:{source}"],
                "count": 0,
            }

        bus = kwargs.get("bus", "slow")
        path = _cache_path(series_id, source, entity_code)
        cache_age = _cache_age_hours(path)

        # Try cache first
        if use_cache:
            cached = load_cache(series_id, source, entity_code, bus)
            if cached is not None:
                latest_obs = _latest_observation(cached)
                freq = cached[0].frequency if cached else None
                stale = _is_observation_stale(latest_obs, freq)
                completeness = _field_completeness(cached)
                flags = []
                if stale:
                    flags.append(f"STALE_OBSERVATION:{series_id}")
                    self._health.flag_stale(source, series_id, "observation_freshness")
                self._health.record_attempt(
                    source,
                    True,
                    0.0,
                    record_count=len(cached),
                    field_completeness_rate=completeness,
                    latest_observation_time=latest_obs,
                    cache_age_hours=cache_age,
                    stale=stale,
                    flags=flags,
                )
                return {
                    "records": [r.to_dict() for r in cached],
                    "flags": flags,
                    "count": len(cached),
                    "cached": True,
                    "cache_age_hours": cache_age,
                }

        # Live fetch
        start = time.time()
        try:
            if source == "FRED":
                records = self._call_adapter(
                    adapter.fetch_series,
                    series_id,
                    entity_code,
                    **kwargs,
                )
            elif source == "WorldBank":
                records = self._call_adapter(
                    adapter.fetch_indicator,
                    series_id,
                    entity_code,
                    **kwargs,
                )
            elif source == "ECB":
                records = self._call_adapter(
                    adapter.fetch_series,
                    series_id,
                    entity_code=entity_code,
                    **kwargs,
                )
            elif source == "Ember":
                records = self._call_adapter(
                    adapter.fetch_electricity_data,
                    entity_code=entity_code,
                    **kwargs,
                )
            elif source == "OWID":
                records = self._call_adapter(
                    adapter.fetch_series,
                    series_id,
                    entity_code=entity_code,
                    **kwargs,
                )
            else:
                records = []
        except Exception as exc:
            latency_ms = (time.time() - start) * 1000
            self._health.record_attempt(source, False, latency_ms, error_message=str(exc))
            return {
                "records": [],
                "flags": [f"FETCH_ERROR:{source}:{exc}"],
                "count": 0,
                "latency_ms": latency_ms,
            }

        latency_ms = (time.time() - start) * 1000

        # Validate
        flags = []
        for r in records:
            flags.extend(validate_record(r))
        flags = list(dict.fromkeys(flags))

        # Missing-series alert
        if not records:
            flags.append(f"MISSING_SERIES:{series_id}:{entity_code}")
            self._health.flag_missing(source, series_id, entity_code)

        # Stale observation check
        latest_obs = _latest_observation(records)
        freq = records[0].frequency if records else None
        stale = _is_observation_stale(latest_obs, freq)
        if stale:
            flags.append(f"STALE_OBSERVATION:{series_id}")
            self._health.flag_stale(source, series_id, "observation_freshness")

        completeness = _field_completeness(records)

        if records and use_cache:
            save_cache(records)
            cache_age = 0.0

        self._health.record_attempt(
            source,
            True,
            latency_ms,
            record_count=len(records),
            field_completeness_rate=completeness,
            latest_observation_time=latest_obs,
            cache_age_hours=cache_age,
            stale=stale,
            flags=flags,
        )

        return {
            "records": [r.to_dict() for r in records],
            "flags": flags,
            "count": len(records),
            "cached": False,
            "latency_ms": latency_ms,
            "cache_age_hours": cache_age,
        }

    @staticmethod
    def _call_adapter(fetcher: Any, *args, **kwargs):
        signature = inspect.signature(fetcher)
        accepted_kwargs = {
            key: value
            for key, value in kwargs.items()
            if key in signature.parameters
        }
        return fetcher(*args, **accepted_kwargs)

    def snapshot(self, entity_code: str, sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fetch a cross-source snapshot for a given geography."""
        sources = sources or self.available_sources()
        snapshot: Dict[str, Any] = {}
        all_flags: List[str] = []

        # Minimum viable snapshot — key series per source
        specs = {
            "WorldBank": [
                {"series_id": "NY.GDP.MKTP.KD.ZG", "kwargs": {}},  # GDP growth
                {"series_id": "FP.CPI.TOTL.ZG", "kwargs": {}},     # CPI inflation
                {"series_id": "SL.UEM.TOTL.ZS", "kwargs": {}},     # Unemployment
            ],
            "OWID": [
                {"series_id": "carbon-intensity-electricity", "kwargs": {}},
            ],
            "Ember": [
                {"series_id": "demand", "kwargs": {"variable": "Demand"}},
                {"series_id": "generation", "kwargs": {"variable": "Generation"}},
            ],
        }

        for source in sources:
            source_specs = specs.get(source, [])
            for spec in source_specs:
                result = self.fetch(source, spec["series_id"], entity_code, **spec.get("kwargs", {}))
                key = f"{source}:{spec['series_id']}"
                # Keep only latest observation per series for snapshot
                latest = None
                if result["records"]:
                    latest = max(result["records"], key=lambda r: r.get("observation_time", ""))
                snapshot[key] = latest
                all_flags.extend(result["flags"])

        all_flags = list(dict.fromkeys(all_flags))
        return {
            "entity_code": entity_code,
            "snapshot": snapshot,
            "flags": all_flags,
            "coverage": len([v for v in snapshot.values() if v is not None]),
        }

    def health(self, adapter: Optional[str] = None) -> Dict[str, Any]:
        return self._health.get_health(adapter)

    def reconcile(self, entity_code: str) -> Dict[str, Any]:
        """Cross-source divergence detection for a geography."""
        snapshot_result = self.snapshot(entity_code, sources=["WorldBank", "Ember", "OWID"])
        snap = snapshot_result.get("snapshot", {})
        divergences = []
        flags = []

        # Extract signals safely
        gdp = snap.get("WorldBank:NY.GDP.MKTP.KD.ZG") or {}
        elec_demand = snap.get("Ember:demand") or {}
        carbon = snap.get("OWID:carbon-intensity-electricity") or {}

        gdp_val = gdp.get("value")
        elec_val = elec_demand.get("value")
        carbon_val = carbon.get("value")

        # Missing coverage flag
        if gdp_val is None or elec_val is None or carbon_val is None:
            flags.append("INSUFFICIENT_SNAPSHOT_COVERAGE")

        # GDP vs electricity demand direction check
        if gdp_val is not None and elec_val is not None:
            # Simple heuristic: if both exist but one is strongly negative and other strongly positive
            # This is a naive direction check; real reconciliation would need YoY changes
            pass

        # Carbon intensity vs economic scale heuristic
        if carbon_val is not None and gdp_val is not None:
            if carbon_val > 500 and gdp_val > 5.0:
                divergences.append({
                    "signal": "HIGH_CARBON_HIGH_GROWTH",
                    "severity": "WARNING",
                    "reason": "High carbon intensity alongside rapid GDP growth suggests dirty-growth path.",
                })
                self._health.flag_divergence("OWID", "WorldBank", "HIGH_CARBON_HIGH_GROWTH", "dirty_growth")

        flags = [d["signal"] for d in divergences] if divergences else []
        return {
            "entity_code": entity_code,
            "divergences": divergences,
            "flags": flags,
            "snapshot_coverage": snapshot_result.get("coverage", 0),
        }


# Global singleton
_registry = IngestRegistry()


def get_registry() -> IngestRegistry:
    return _registry
