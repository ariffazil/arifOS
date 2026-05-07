# UW-Macrostrat Analysis for GEOX Integration

> **Exploration Mode Assessment** — ARIF
> **Date:** 2026-03-26
> **Verdict:** ✅ HIGHLY BENEFICIAL — API integration recommended, no clone needed

---

## What is Macrostrat?

**UW-Macrostrat** is a geological data platform from the University of Wisconsin-Madison, supported by:
- US National Science Foundation (NSF)
- DARPA
- UW-Madison Department of Geoscience

**Website:** https://macrostrat.org
**API Docs:** https://macrostrat.org/api
**License:** CC-BY-4.0 (Free to use with attribution)

---

## Scale of Data (Massive)

| Resource | Count |
|----------|-------|
| Regional rock columns | 1,400 |
| Rock units | 33,903 |
| Geologic map polygons | 2,500,000 |
| Stratigraphic names | 51,212 |
| Geologic maps integrated | 225+ |

**Coverage:** Global — North America, Caribbean, New Zealand, Deep Sea, etc.

---

## Why It's Perfect for GEOX

### Direct Tool Mappings

| GEOX Tool | Macrostrat API Endpoint | Value |
|-----------|------------------------|-------|
| `EarthModelTool` | `/columns` — Rock column data | Stratigraphic framework |
| `EarthModelTool` | `/units` — Rock unit definitions | Lithology, age, environment |
| `GeoRAGTool` | `/defs` — Stratigraphic definitions | Literature-backed context |
| `GeoRAGTool` | `/geologic_units` — Map polygons | Spatial geology |
| `SimulatorTool` | `/intervals` — Geologic time | Temporal constraints |

### API Endpoints (v2)

```
https://macrostrat.org/api/v2/
├── /columns          # Stratigraphic columns (regional)
├── /units            # Rock units (33k+ entries)
├── /geologic_units   # Map polygons (2.5M+)
├── /defs
│   ├── /stratigraphic_names    # 51k+ names
│   ├── /lithologies            # Rock types
│   ├── /environments           # Depositional environments
│   └── /minerals               # Mineralogy
├── /intervals        # Geologic time scale
└── /fossils          # Paleontological data
```

---

## Integration Strategy (No Clone Needed)

Since Macrostrat provides a **REST API**, you can integrate directly without cloning:

### Option 1: Direct API Client (Recommended)

Add a `MacrostratTool` to GEOX's `geox_tools.py`:

```python
import httpx

class MacrostratTool(BaseTool):
    """Large Earth Model proxy via Macrostrat API."""

    name = "MacrostratTool"
    description = "Query Macrostrat geological database for stratigraphic columns, units, and map data"
    base_url = "https://macrostrat.org/api/v2"

    async def run(self, inputs: dict) -> GeoToolResult:
        endpoint = inputs.get("endpoint", "columns")
        params = {
            "lat": inputs["location"].latitude,
            "lng": inputs["location"].longitude,
            "all": "true" if inputs.get("all", False) else "false"
        }

        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/{endpoint}", params=params)
            data = resp.json()

        # Convert to GeoQuantity objects
        quantities = self._parse_to_quantities(data)
        return GeoToolResult(
            tool_name=self.name,
            success=True,
            quantities=quantities
        )
```

### Option 2: Cached Local Copy (Future)

If you need offline access or faster queries:

```bash
# Download specific datasets via API (not clone)
curl "https://macrostrat.org/api/v2/columns?all&format=geojson" > macrostrat_columns.geojson
curl "https://macrostrat.org/api/v2/units?all" > macrostrat_units.json
```

Store in your `CIV/@GEOX` GDrive folder for GEOX RAG ingestion.

---

## Data Quality Assessment

| Criterion | Rating | Notes |
|-----------|--------|-------|
| **Authority** | ⭐⭐⭐⭐⭐ | NSF-funded, peer-reviewed |
| **Coverage** | ⭐⭐⭐⭐⭐ | Global, 225+ maps |
| **Precision** | ⭐⭐⭐⭐☆ | Regional scale (not well-log resolution) |
| **License** | ⭐⭐⭐⭐⭐ | CC-BY-4.0 (attribution only) |
| **API Stability** | ⭐⭐⭐⭐⭐ | v2 active since 2014 |
| **Documentation** | ⭐⭐⭐⭐☆ | Good API docs, some gaps |

**Use Case Fit:**
- ✅ Regional basin screening
- ✅ Stratigraphic framework
- ✅ Geologic map integration
- ✅ Literature-backed context
- ❌ Well-log scale detail (need petrophysical data)

---

## Repositories (For Reference, Not Clone)

| Repo | Purpose | Clone? |
|------|---------|--------|
| `macrostrat-api` | API server code | ❌ Use HTTP API instead |
| `macrostrat` | Core platform | ❌ API access sufficient |
| `web-components` | React UI components | ❌ Not needed for GEOX |
| `web-legacy` | Old web interface | ❌ Deprecated |

**Total repos:** 90+ (mostly web/app code — not needed for GEOX backend)

---

## Constitutional Compliance (arifOS Floors)

| Floor | Macrostrat Compliance |
|-------|----------------------|
| F2 (Truth ≥ 0.99) | ✅ Peer-reviewed data, NSF-funded |
| F4 (Clarity) | ✅ CC-BY-4.0 license, clear attribution |
| F7 (Humility) | ⚠️ Regional scale — uncertainty bounds needed |
| F9 (Anti-Hantu) | ✅ Physical data, no AI hallucination |
| F10 (Ontology) | ✅ Standard stratigraphic nomenclature |

**Risk:** Medium — always verify with local well data before drilling decisions.

---

## Implementation Sketch

```python
# In GEOX: arifos/geox/geox_tools.py

class MacrostratTool(BaseTool):
    """
    Macrostrat geological database integration.
    Provides stratigraphic columns, units, and geologic map data.
    """

    name = "MacrostratTool"
    description = "Query Macrostrat for regional geological context"

    async def run(self, inputs: dict) -> GeoToolResult:
        location = inputs["location"]

        # Query stratigraphic column at location
        column_data = await self._query_columns(location)

        # Query rock units
        units_data = await self._query_units(location)

        # Convert to GeoQuantity
        quantities = []
        for unit in units_data.get("success", {}).get("data", []):
            quantities.append(GeoQuantity(
                value=unit.get("t_age", 0),  # Top age (Ma)
                units="Ma",
                quantity_type="stratigraphic_age",
                coordinates=location,
                timestamp=datetime.now(timezone.utc),
                uncertainty=5.0,  # Macrostrat's typical precision
                provenance=ProvenanceRecord(
                    source_id=f"macrostrat-{unit.get('unit_id')}",
                    source_type="literature",
                    confidence=0.85
                )
            ))

        return GeoToolResult(
            tool_name=self.name,
            success=True,
            quantities=quantities,
            metadata={
                "column_id": column_data.get("column_id"),
                "unit_count": len(quantities),
                "source": "macrostrat.org/api/v2"
            }
        )
```

---

## Action Items

### Immediate (Today)
1. ✅ **NO CLONE NEEDED** — Use REST API directly
2. Add `MacrostratTool` to GEOX's `geox_tools.py`
3. Test API calls with Malay Basin coordinates

### Short-term (This Week)
1. Cache frequently accessed regions (Malay Basin, Sabah Basin)
2. Add Macrostrat attribution to GEOX reports (CC-BY-4.0 requirement)
3. Document uncertainty bounds in `geox_schemas.py`

### Long-term (Future)
1. Contribute Malaysian geological data back to Macrostrat (collaboration)
2. Integrate with xDD/GeoDeepDive for literature mining
3. Use Macrostrat columns as LEM (Large Earth Model) training context

---

## Conclusion

| Question | Answer |
|----------|--------|
| **Clone needed?** | ❌ NO — use REST API |
| **Beneficial for GEOX?** | ✅ YES — massive geological database |
| **Integration complexity?** | LOW — simple HTTP client |
| **License compatible?** | ✅ YES — CC-BY-4.0 (attribution) |
| **ASEAN relevance?** | ⚠️ PARTIAL — mostly North America, but global columns exist |

**Recommendation:** Integrate via API, don't clone. Add `MacrostratTool` to GEOX's tool registry for instant access to 33k+ rock units and 2.5M map polygons.

---

**DITEMPA BUKAN DIBERI** — Leverage existing geological knowledge, build governance on top.
