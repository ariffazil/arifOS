"""
arifosmcp/integrations/memory_bridge.py — Governed Knowledge Graph Substrate (F2/F11)

Bridges arifOS to the mcp_memory substrate, treating it as:
- Crossing-session Entity Graph: services, repos, clusters, tools.
- Operational Knowledge: user preferences, project goals, stability facts.

DITEMPA BUKAN DIBERI — 999 SEAL
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from arifosmcp.integrations.substrate_bridge import bridge
from arifosmcp.runtime.models import RuntimeEnvelope as _RE
from arifosmcp.runtime.models import Verdict
from arifosmcp.runtime.governance_enforcer import get_enforcer

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class KGEntity:
    """Knowledge Graph Entity (arifOS-native representation)"""
    name: str
    entity_type: str
    observations: list[str]
    metadata: dict[str, any]
    f2_truth_confidence: float = 0.5
    f7_uncertainty: float = 0.05
    source: str = "unknown"

# ═══════════════════════════════════════════════════════════════════════════════
# CORE BRIDGE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def kg_upsert_entity(
    entity_id: str,
    entity_type: str,
    observations: list[str],
    actor_id: str,
    session_id: str | None = None,
    truth_confidence: float = 0.5,
    uncertainty: float = 0.05,
    source: str = "arifos_mind",
) -> tuple[bool, str | None]:
    """Upsert an entity to the MCP memory KG via substrate_bridge."""
    
    # F2/F11 Optimized Governance
    gov = get_enforcer().evaluate_intent(
        tool_name="arifos_memory",
        action="memory_write",
        parameters={"entity_id": entity_id, "entity_type": entity_type},
        actor_id=actor_id,
        session_id=session_id
    )
    
    if not gov.ok:
        return False, f"Governance blocked: {gov.detail}"

    try:
        enriched_observations = []
        for obs in observations:
            meta = {
                "f2_truth": truth_confidence,
                "f7_uncertainty": uncertainty,
                "source": source,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            enriched_observations.append(f"{obs} [meta:{json.dumps(meta)}]")
        
        payload = {
            "entities": [{
                "name": entity_id,
                "entityType": entity_type,
                "observations": enriched_observations,
            }]
        }
        
        await bridge.memory.call_tool("create_entities", payload)
        return True, None
    except Exception as e:
        return False, str(e)

async def kg_link_entities(
    from_id: str,
    to_id: str,
    relation_type: str,
    actor_id: str,
    session_id: str | None = None
) -> tuple[bool, str | None]:
    """Create a relation between entities."""
    
    gov = get_enforcer().evaluate_intent(
        tool_name="arifos_memory",
        action="memory_link",
        parameters={"from": from_id, "to": to_id, "type": relation_type},
        actor_id=actor_id,
        session_id=session_id
    )
    
    if not gov.ok:
        return False, f"Governance blocked: {gov.detail}"

    try:
        payload = {
            "relations": [{
                "from": from_id,
                "to": to_id,
                "relationType": relation_type,
            }]
        }
        await bridge.memory.call_tool("create_relations", payload)
        return True, None
    except Exception as e:
        return False, str(e)

async def kg_search(
    query: str,
    actor_id: str = "anonymous",
    session_id: str | None = None,
    entity_types: list[str] | None = None,
    limit: int = 10,
) -> list[KGEntity]:
    """Search the MCP memory KG."""
    
    gov = get_enforcer().evaluate_intent(
        tool_name="arifos_memory",
        action="memory_read",
        parameters={"query": query},
        actor_id=actor_id,
        session_id=session_id
    )
    
    if not gov.ok:
        return []

    try:
        data = await bridge.memory.call_tool("search_nodes", {"query": query})
        entities = []
        
        for node in data.get("entities", [])[:limit]:
            obs_list = node.get("observations", [])
            
            if entity_types and node.get("entityType") not in entity_types:
                continue
            
            entity = KGEntity(
                name=node.get("name", ""),
                entity_type=node.get("entityType", "unknown"),
                observations=obs_list,
                metadata=node.get("metadata", {}),
            )
            entities.append(entity)
        return entities
    except Exception as e:
        logger.error(f"KG search error: {e}")
        return []

async def kg_delete_entity(
    entity_id: str,
    actor_id: str,
    session_id: str | None = None
) -> tuple[bool, str | None]:
    """Delete an entity from the MCP memory KG."""
    
    gov = get_enforcer().evaluate_intent(
        tool_name="arifos_memory",
        action="memory_delete",
        parameters={"entity_id": entity_id},
        actor_id=actor_id,
        session_id=session_id
    )
    
    if not gov.ok:
        return False, f"Governance blocked: {gov.detail}"

    try:
        await bridge.memory.call_tool("delete_entities", {"entityNames": [entity_id]})
        return True, None
    except Exception as e:
        return False, str(e)

# ═══════════════════════════════════════════════════════════════════════════════
# ARIFOS TOOL INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

async def arifos_memory_query(
    query: str,
    actor_id: str = "anonymous",
    session_id: str | None = None,
    entity_types: list[str] | None = None,
) -> _RE:
    """Tool-level interface for querying MCP memory."""
    entities = await kg_search(query, actor_id, session_id, entity_types)
    
    return _RE(
        ok=True,
        tool="arifos_memory",
        payload={
            "query": query,
            "entities": [
                {
                    "name": e.name,
                    "type": e.entity_type,
                    "observations": e.observations,
                    "truth_confidence": e.f2_truth_confidence,
                    "uncertainty": e.f7_uncertainty,
                }
                for e in entities
            ]
        }
    )

async def arifos_memory_write(
    entity_id: str,
    entity_type: str,
    observations: list[str],
    actor_id: str,
    relations: list[dict] | None = None,
    session_id: str | None = None,
    truth_confidence: float = 0.5,
    uncertainty: float = 0.05,
) -> _RE:
    """Tool-level interface for writing to MCP memory."""
    success, error = await kg_upsert_entity(
        entity_id=entity_id,
        entity_type=entity_type,
        observations=observations,
        actor_id=actor_id,
        session_id=session_id,
        truth_confidence=truth_confidence,
        uncertainty=uncertainty
    )
    
    if not success:
        return _RE(ok=False, detail=error, verdict=Verdict.VOID)
    
    if relations:
        for rel in relations:
            await kg_link_entities(
                from_id=entity_id,
                to_id=rel["to"],
                relation_type=rel["type"],
                actor_id=actor_id,
                session_id=session_id
            )
    
    return _RE(
        ok=True,
        tool="arifos_memory",
        verdict=Verdict.SEAL,
        payload={"entity_id": entity_id, "status": "stored"}
    )
