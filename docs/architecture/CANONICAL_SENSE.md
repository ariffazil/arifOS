# arifOS Canonical SENSE Consolidation — Discovery Layer

**Status:** DRAFT | PROPOSED
**Sovereign:** arifOS Kernel
**Invariants:** F1–F13, 13-Tool Surface
**Date:** 2026-05-22

---

## 1. Problem: Discovery Fragmentation
Currently, arifOS has multiple overlapping surfaces for "SENSE":
- `arif_sense_observe`: Web search, simple ingest.
- `arif_evidence_fetch`: Web search with evidence receipts and sequential thinking.
- `arifos_wiki_search`: Local filesystem knowledge search.
- `tree777://`: MCP resource search.

This fragmentation increases cognitive load for agents and introduces "Ontology Bleed" (e.g., agents using search when they should be using local knowledge).

## 2. Solution: Hybrid Discovery Mode
Instead of adding a new 14th tool, we consolidate discovery logic into the existing **111_SENSE** axis via `arif_sense_observe(mode="hybrid_discovery")`.

### 2.1 The "Hybrid Discovery" Contract
The `hybrid_discovery` mode performs a single metabolic cycle that:
1. **Searches Local Knowledge**: Queries `/root/AAA/wiki` and `.arifos/` local indices.
2. **Searches Global Knowledge**: Queries Exa/Tavily/Brave.
3. **Reconciles**: Identifies delta-truth ($\Delta T$) between local docs and web reality.

### 2.2 Unified Result Format (Read-Only)
The result preserves provenance while providing a consolidated view:

```json
{
  "verdict": "SEAL",
  "query": "arifOS F11 floor definition",
  "summary": "Local docs define F11 as AUDIT, but recent code implementations use AUTH.",
  "knowledge_layers": {
    "local_wiki": {
      "matches": [
        {"path": "AAA/wiki/INVARIANTS.md", "content": "F11-AUDIT: Witness gate...", "confidence": 1.0}
      ]
    },
    "web_reality": {
      "matches": [
        {"url": "https://wiki.arif-fazil.com/...", "content": "Update: F11 renamed to AUDIT", "source": "Exa"}
      ]
    }
  },
  "delta_truth": {
    "score": 0.95,
    "contradictions": ["F11 nomenclature mismatch detected between repo and charter"]
  }
}
```

## 3. Benefits
- **SENSE Latency**: Reduced from 3+ turns to 1 turn.
- **Consistency**: Centralized L11_AUDIT logging for all discovery actions.
- **No 14th Tool**: Preserves the 13-tool canonical surface.

## 4. Operational Boundaries
- **Read-Only**: Discovery mode will not write "Scars" or push to Gists. Ingestion remains a separate, explicit action.
- **No Forge naming**: This is strictly a SENSE operation.

---
**DITEMPA BUKAN DIBERI — 999 SEAL PENDING**
