# Web Search Integration in arifos.sense

**Version:** 2.0.0-canonical  
**Status:** SEALED 🔐

---

## Design Principle

> **Web search is a retrieval backend, not the brain.**

Live search is subordinate to the constitutional protocol:
```
user query
  → PARSE
  → CLASSIFY truth type
  → DECIDE if live search needed
  → if needed → execute_sensing() → web search backend
  → NORMALIZE evidence
  → RANK sources
  → CHECK time/conflict/ambiguity
  → EMIT sense_packet
```

---

## Integration Architecture

### Layer A — Constitutional Front-End (`governed_sense_impl.py`)

**Responsibilities:**
- `parse_query()` → Extract entities, intent, time_scope
- `classify_truth()` → 7 truth classes
- `build_evidence_plan()` → Decide retrieval lane

**Trigger Matrix Implemented:**

| Query Type | Truth Class | Live Search? |
|------------|-------------|--------------|
| Math/logic/thermodynamics | `absolute_invariant` | ❌ No |
| Stable definitions | `absolute_invariant` | ❌ No |
| Formal rules in fixed system | `conditional_invariant` | ❌ No |
| "Current", "latest", "now" | `time_sensitive_fact` | ✅ Yes |
| People/roles/status | `time_sensitive_fact` | ✅ Yes |
| Prices/markets/releases | `time_sensitive_fact` | ✅ Yes |
| Weather/events/elections | `time_sensitive_fact` | ✅ Yes |
| Vague/underspecified | `ambiguous_query` | 🛑 HOLD first |

### Layer B — Retrieval Adapter (`execute_sensing()`)

```python
async def execute_sensing(sense_input, evidence_plan, session_id):
    # Gate 1: Skip if offline_reason or hold
    if evidence_plan.retrieval_lane in ("offline_reason", "hold"):
        return []
    
    # Gate 2: Respect offline_first policy
    if sense_input.policy.offline_first:
        return []
    
    # Gate 3: Execute via reality_handler
    bundle = await reality_handler.handle_compass(bundle_input, auth_context)
    
    # Convert to EvidenceItems
    items = []
    for result in bundle.results:
        item = EvidenceItem(
            source_name=result.engine,  # "brave", "ddgs"
            source_type="search_engine",
            source_rank=6,  # Aggregator by default
            url=r.get("url"),
            title=r.get("title"),
            snippets=[r.get("description", "")],
        )
        items.append(item)
    
    # Gate 4: Apply rank filtering from evidence_plan
    items = [i for i in items if i.source_rank <= evidence_plan.min_rank_required]
    
    return items
```

**Web Search Provider Pattern:**
- Current: `reality_handler.handle_compass()` uses Brave API → DDGS fallback
- Future: Can swap providers without changing protocol

### Layer C — Evidence Normalizer (`normalize_evidence()`)

Converts raw search results to structured `EvidenceItem`:
```python
@dataclass
class EvidenceItem:
    id: str
    source_name: str      # "brave", "ddgs"
    source_type: str      # "search_engine"
    source_rank: int      # 6 (aggregator) → can upgrade based on domain
    url: str | None
    title: str | None
    issuer: str | None
    author: str | None
    published_at: str | None
    observed_at: str      # When we fetched it
    extracted_claims: list[ExtractedClaim]
    snippets: list[str]
    quality_flags: list[QualityFlag]
```

### Layer D — Epistemic Gate

```python
# Temporal grounding
temporal = TemporalGrounding(
    query_time_class=TimeScope.LIVE,
    freshness_required=True,
    staleness_risk=StalenessRisk.HIGH,
)

# Conflict detection
conflict = detect_conflicts(items)  # 6 conflict types

# Uncertainty with Ω₀
uncertainty = calculate_uncertainty(
    items, ambiguity, conflict, truth_classification
)
# → UncertaintyBand with sigma, omega0_cap, 5-dimensional basis
```

---

## Code Flow (Actual Implementation)

```python
# Entry point: governed_sense_v2()
async def governed_sense_v2(raw_input, session_id=None):
    
    # STAGE 1: PARSE
    sense_input = parse_input(raw_input)
    # → SenseInput with intent, query_frame, policy, budget, actor
    
    # STAGE 2: CLASSIFY
    truth_classification = classify_truth(sense_input)
    # → TruthClassification with truth_class, search_required, temporal_dependency
    
    # STAGE 4: PLAN
    evidence_plan = build_evidence_plan(sense_input, truth_classification)
    # → EvidencePlan with retrieval_lane, min_rank_required, freshness_requirement
    
    # STAGE 5: SENSE (Live Search Integration)
    items = []
    if execute_search and evidence_plan.retrieval_lane == "web_search":
        items = await execute_sensing(sense_input, evidence_plan, session_id)
        # → Calls reality_handler.handle_compass() → Brave/DDGS
        # → Returns EvidenceItem[]
    
    # STAGE 6: NORMALIZE
    items, findings = normalize_evidence(items, sense_input)
    
    # STAGE 7: GATE
    ambiguity = assess_ambiguity(sense_input, items)
    conflict = detect_conflicts(items)
    uncertainty = calculate_uncertainty(items, ambiguity, conflict, truth_classification)
    
    # STAGE 8: HANDOFF
    routing = determine_routing(truth_classification, uncertainty, ambiguity, conflict)
    # → RoutingDecision with next_stage (mind|heart|judge|hold)
    
    return SensePacket, IntelligenceState
```

---

## Freshness & Constraints

### Domain-Specific Freshness
```python
DOMAIN_FRESHNESS_HOURS = {
    "finance": 1,      # 1 hour for prices
    "software": 168,   # 1 week for versions
    "security": 24,    # 1 day for CVEs
    "news": 4,         # 4 hours
    "weather": 1,      # 1 hour
}
```

### Evidence Rank Enforcement
```python
# After retrieval, filter by minimum rank
items = [i for i in items if i.source_rank <= evidence_plan.min_rank_required]

# Decision-critical requires rank ≤ 2 (primary source or official issuer)
# Preparatory requires rank ≤ 4 (technical documentation)
# Informational requires rank ≤ 5 (reputable secondary)
```

---

## Usage Examples

### Example 1: Invariant Query (No Search)
```python
result = await arifos.sense(
    mode="governed",
    query="Does entropy always increase?"
)
# truth_class: absolute_invariant
# search_required: False
# retrieval_lane: offline_reason
# evidence_items: []  # No web search executed
```

### Example 2: Time-Sensitive Query (Live Search)
```python
result = await arifos.sense(
    mode="governed", 
    query="Who is the current CEO of OpenAI?"
)
# truth_class: time_sensitive_fact
# search_required: True
# retrieval_lane: web_search
# evidence_items: [EvidenceItem, ...]  # From Brave/DDGS
# temporal_grounding.staleness_risk: HIGH
```

### Example 3: Ambiguous Query (HOLD)
```python
result = await arifos.sense(
    mode="governed",
    query="Is this true?"  # "this" is undefined
)
# truth_class: ambiguous_query
# search_required: False
# retrieval_lane: hold
# verdict: HOLD
# routing.next_stage: hold
```

---

## Provider Interface (Future Extension)

```python
class WebSearchProvider(Protocol):
    async def search(
        self, 
        query: str, 
        top_k: int = 5,
        freshness_days: int | None = None
    ) -> list[dict]:
        ...

# Current implementation uses reality_handler
# Future: Can inject BraveProvider, GoogleProvider, etc.
```

---

## Output Format (After Live Search)

```json
{
  "truth_classification": {
    "truth_class": "time_sensitive_fact",
    "search_required": true,
    "search_reason": "Time-sensitive information requires current grounding",
    "temporal_dependency": true
  },
  "temporal_grounding": {
    "query_time_class": "live",
    "freshness_required": true,
    "staleness_risk": "high"
  },
  "evidence_plan": {
    "retrieval_lane": "web_search",
    "preferred_sources": ["official company website", "exchange filings"],
    "min_rank_required": 3,
    "freshness_requirement": {
      "required": true,
      "max_age_days": 30
    }
  },
  "evidence_items": [
    {
      "id": "abc123",
      "source_name": "brave",
      "source_type": "search_engine",
      "source_rank": 6,
      "url": "https://openai.com/blog/",
      "title": "OpenAI Leadership Update",
      "observed_at": "2026-04-07T00:00:00Z",
      "extracted_claims": [...],
      "quality_flags": []
    }
  ],
  "uncertainty": {
    "level": "moderate",
    "sigma": 0.25,
    "omega0_cap": 0.75,
    "narrative_note": "awaiting official issuer confirmation"
  },
  "routing": {
    "next_stage": "arifos.mind",
    "route_reason": "Evidence packet prepared for synthesis",
    "requires_live_verification": true
  }
}
```

---

## Key Design Wins

1. **Search is gated by classification** — No reflex search
2. **Freshness is domain-aware** — Finance: 1hr, Software: 1 week
3. **Rank filtering post-retrieval** — Quality enforcement
4. **Conflict detection** — Never merge disagreement silently
5. **Ω₀ humility cap** — Confidence bounded by uncertainty
6. **Provider abstraction** — Can swap search engines without protocol changes

---

## Bottom Line

✅ **Web search is integrated as a retrieval backend**  
✅ **Governed by 8-stage constitutional protocol**  
✅ **Classification decides IF search happens**  
✅ **Evidence hierarchy ranks results**  
✅ **Temporal grounding assesses staleness**  
✅ **Normalized output, not raw links**

**The invariant is the protocol. Search is just a tool.** 🔐
