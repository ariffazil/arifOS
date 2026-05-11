# UW-Macrostrat/macrostrat Repository Analysis

> **For:** ARIF / GEOX Integration Decision
> **Date:** 2026-03-26
> **Source:** https://github.com/UW-Macrostrat/macrostrat

---

## Repository Overview

**Name:** `UW-Macrostrat/macrostrat`
**Description:** A geological data platform for exploration, integration, and analysis (v2)
**License:** Not explicitly stated (check repo) — likely CC-BY-4.0 like API
**Language:** Python (with `uv` build system)

### What This Repository IS

This is the **core monorepo** for Macrostrat v2 — the actual platform code, not just an API client.

| Component | Purpose |
|-----------|---------|
| **Database Schema** | PostgreSQL/PostGIS schema for geological data |
| **CLI Tool** | `macrostrat` command-line interface for system management |
| **Map Ingestion** | Scripts for importing geologic maps into the database |
| **API v3** | Core API service (authentication, management) |
| **Python Libraries** | Reusable geoscience components |

### Repository Structure

```
macrostrat/
├── services/           # Core services
│   ├── api/           # API v3 (management/auth)
│   └── task-runner/   # (coming soon)
├── cli/               # Python CLI application
├── map-ingestion/     # Geologic map import scripts
├── schema/            # Database schema definitions
└── libs/              # Python libraries
    ├── macrostrat.utils
    ├── macrostrat.database
    ├── macrostrat.dinosaur (schema evolution)
    └── macrostrat.app-frame
```

---

## Key Finding: This is NOT What You Need for GEOX

### What GEOX Actually Needs

GEOX needs to **query** geological data, not **host** it:

| What GEOX Needs | What This Repo Provides |
|-----------------|-------------------------|
| Query stratigraphic columns | ✅ Can do via API |
| Query rock units | ✅ Can do via API |
| Get map polygons | ✅ Can do via API |
| Host Macrostrat database | ❌ Not needed |
| Manage geological maps | ❌ Not needed |
| Run Macrostrat platform | ❌ Not needed |

### The Critical Difference

| Aspect | `macrostrat` Repo | Macrostrat API |
|--------|-------------------|----------------|
| **Purpose** | Build/run Macrostrat platform | Query geological data |
| **Setup** | Complex (PostgreSQL, PostGIS, `uv`, `make`) | Simple HTTP requests |
| **Maintenance** | High (database, services, updates) | None (they maintain it) |
| **Data Size** | 100s GB (full database) | API responses (KB-MB) |
| **Use Case** | Host your own Macrostrat instance | Use their data |

---

## What About the Python Libraries?

The repository includes several Python packages:

| Library | Purpose | Useful for GEOX? |
|---------|---------|------------------|
| `macrostrat.utils` | General utilities | ❌ Generic, not geo-specific |
| `macrostrat.database` | PostgreSQL/PostGIS tools | ⚠️ Maybe, if you want local DB |
| `macrostrat.dinosaur` | Database schema evolution | ❌ Overkill for GEOX |
| `macrostrat.app-frame` | CLI scaffolding | ❌ Not needed |

**Verdict:** These are infrastructure libraries for building Macrostrat-compatible apps, not for querying geological data.

---

## The Better Alternative: `rmacrostrat` Pattern

There's an **R package** called `rmacrostrat` that does exactly what GEOX needs:

```r
# R example - what GEOX should emulate
library(rmacrostrat)

# Get stratigraphic column
column_def <- def_columns(column_name = "San Juan Basin")
units <- get_units(column_id = column_def$col_id, interval_name = "Cretaceous")

# Get map outcrop
hc <- get_map_outcrop(strat_name_id = hc_def$strat_name_id, sf = TRUE)
```

**This is the pattern GEOX should follow:** A thin Python client that wraps the Macrostrat API.

---

## Recommendation: Do NOT Clone

### Clone If:
- ❌ You want to host your own Macrostrat instance (don't — use theirs)
- ❌ You want to modify Macrostrat core (don't — not your domain)
- ❌ You want to contribute to Macrostrat (maybe later, not now)

### Use API Instead:
- ✅ Simple HTTP requests
- ✅ They maintain the data
- ✅ CC-BY-4.0 license (free with attribution)
- ✅ No infrastructure burden

---

## What GEOX Should Actually Build

### Option 1: Simple HTTP Client (Recommended)

Create `arifos/geox/tools/macrostrat_tool.py` that calls the API directly:

```python
import httpx

class MacrostratTool:
    """Query Macrostrat API for geological context."""
    base_url = "https://macrostrat.org/api/v2"

    async def get_columns(self, lat, lon):
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/columns",
                params={"lat": lat, "lng": lon}
            )
            return resp.json()
```

### Option 2: Use Existing Python Client (If Available)

Check if there's a `pymacrostrat` or similar:

```bash
pip search macrostrat  # or check PyPI
```

**Current state:** No official Python client exists. The R package (`rmacrostrat`) is the reference implementation.

---

## Integration Strategy for GEOX

### Week 1: Build the Tool

```python
# arifos/geox/tools/macrostrat_tool.py
from arifos.geox.geox_tools import BaseTool, GeoToolResult
import httpx

class MacrostratTool(BaseTool):
    name = "MacrostratTool"
    description = "Query Macrostrat geological database"
    base_url = "https://macrostrat.org/api/v2"

    async def run(self, inputs: dict) -> GeoToolResult:
        location = inputs["location"]

        # Query API endpoints
        columns = await self._query_columns(location)
        units = await self._query_units(location)

        # Convert to GeoQuantity objects
        quantities = self._parse_to_quantities(columns, units)

        return GeoToolResult(
            tool_name=self.name,
            success=True,
            quantities=quantities,
            metadata={
                "source": "macrostrat.org",
                "attribution": "CC-BY-4.0"
            }
        )
```

### Week 2: Test with Real Data

```python
# Test: Malay Basin
location = CoordinatePoint(latitude=5.2, longitude=104.8)
tool = MacrostratTool()
result = await tool.run({"location": location})
```

---

## Summary Matrix

| Question | Answer |
|----------|--------|
| Clone this repo? | **❌ NO** |
| Use Macrostrat data? | **✅ YES** — via API |
| Build Python client? | **✅ YES** — thin wrapper around API |
| Use their libraries? | **⚠️ MAYBE** — `macrostrat.database` if you need local PostgreSQL |
| Add as dependency? | **❌ NO** — not installable via pip (uses `uv` + `make`) |

---

## Next Steps for GEOX

1. **DO NOT clone** `UW-Macrostrat/macrostrat`
2. **DO implement** `MacrostratTool` using HTTP API
3. **DO cite** Macrostrat in GEOX reports (CC-BY-4.0 requirement)
4. **DO consider** collaborating with them (Malaysian geological data)

---

## Reference Links

| Resource | URL |
|----------|-----|
| Macrostrat API v2 | https://macrostrat.org/api/v2 |
| Macrostrat Website | https://macrostrat.org |
| R Package (`rmacrostrat`) | https://rmacrostrat.palaeoverse.org |
| API Documentation | https://macrostrat.org/api |

---

**DITEMPA BUKAN DIBERI** — Stand on their shoulders via API, don't carry their database.
