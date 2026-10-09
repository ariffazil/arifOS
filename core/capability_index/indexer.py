"""
Capability Index Auto-Reindexing Engine.

Harvests tools from:
  1. /root/AAA/registries/CAPABILITY_INDEX.json
  2. /root/forge_work/2026-08-10-p0-stabilize/mcp_inventory.json
  3. /root/.gemini/antigravity-cli/mcp/
  4. Live organ tools/list endpoints

Applies /root/AAA/governance/classification_policy.yaml to assign action_class,
effective_class, authority_ceiling, and risk_tier.

Tracks schema digests to trigger event-driven reindexing upon MCP restart/mutation.

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from capability_index.models import CapabilityRecord
from capability_index.store import CapabilityStore

# Import classifier
import sys
if "/root" not in sys.path:
    sys.path.insert(0, "/root")
from AAA.governance.classifier import ClassificationEngine

logger = logging.getLogger("capability-indexer")
logging.basicConfig(level=logging.INFO)

CAPABILITY_INDEX_JSON = Path("/root/AAA/registries/CAPABILITY_INDEX.json")
MCP_INVENTORY_JSON = Path("/root/forge_work/2026-08-10-p0-stabilize/mcp_inventory.json")
MCP_DIR = Path("/root/.gemini/antigravity-cli/mcp")
STATE_FILE = Path("/root/.local/share/arifos/capability_index_state.json")


class CapabilityIndexer:
    """Discovers, classifies, and indexes all tools across the federation."""

    def __init__(self, store: Optional[CapabilityStore] = None) -> None:
        self.store = store or CapabilityStore()
        self.classifier = ClassificationEngine()

    @staticmethod
    def canonical_server(server: str) -> str:
        """Canonical organ identity (D4 alias pass, 2026-09-17).

        Sources disagree on casing (seed 'arifOS'/'WEALTH'/'WELL' vs live
        'arifos'/'wealth'/'well') — same organ, two identities, duplicate-SOT
        smell. Federation convention is lowercase. Existing consumers are
        case-insensitive (store._apply_filters lowercases both sides), so this
        is a safe unification at the single ingestion chokepoint.
        """
        return server.strip().lower()

    def discover_tools(self) -> List[CapabilityRecord]:
        """Harvest tools across all federation sources."""
        tools_by_id: Dict[str, CapabilityRecord] = {}

        # Source 1: CAPABILITY_INDEX.json
        if CAPABILITY_INDEX_JSON.exists():
            try:
                with open(CAPABILITY_INDEX_JSON, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for t in data.get("tools", []):
                        name = t.get("name") or t.get("id") or t.get("tool_name")
                        server = self.canonical_server(t.get("server", "unknown"))
                        desc = t.get("description", "")
                        tags = t.get("tags", [])
                        epistemic = t.get("epistemic_tag", "CLAIM")
                        risk = t.get("risk_tier", "low")

                        classification = self.classifier.classify_tool(name, server)
                        rec = CapabilityRecord(
                            tool_name=name,
                            server=server,
                            description=desc,
                            tags=tags,
                            epistemic_tag=epistemic,
                            action_class=classification["action_class"],
                            effective_class=classification["effective_class"],
                            risk_tier=risk,
                            authority_ceiling=classification["authority_ceiling"],
                        )
                        tools_by_id[f"{server}:{name}"] = rec
            except Exception as e:
                logger.warning("Error reading CAPABILITY_INDEX.json: %s", e)

        # Source 2: MCP schema directory (/root/.gemini/antigravity-cli/mcp/)
        if MCP_DIR.exists():
            for server_dir in MCP_DIR.iterdir():
                if not server_dir.is_dir():
                    continue
                server_name = self.canonical_server(server_dir.name)
                for schema_file in server_dir.glob("*.json"):
                    tool_name = schema_file.stem
                    try:
                        with open(schema_file, "r", encoding="utf-8") as sf:
                            schema = json.load(sf)
                            desc = schema.get("description", "")
                            classification = self.classifier.classify_tool(tool_name, server_name)
                            key = f"{server_name}:{tool_name}"
                            if key not in tools_by_id:
                                tools_by_id[key] = CapabilityRecord(
                                    tool_name=tool_name,
                                    server=server_name,
                                    description=desc,
                                    parameters=schema.get("parameters"),
                                    tags=[server_name, tool_name.split("_")[0]],
                                    epistemic_tag="CLAIM",
                                    action_class=classification["action_class"],
                                    effective_class=classification["effective_class"],
                                    risk_tier="low" if classification["effective_class"] == "OBSERVE" else "medium",
                                    authority_ceiling=classification["authority_ceiling"],
                                )
                    except Exception as e:
                        logger.warning("Error reading schema %s: %s", schema_file, e)

        # Source 3: Seeded capabilities fallback
        try:
            from capability_index.seed import SEED_CAPABILITIES
            for rec in SEED_CAPABILITIES:
                rec.server = self.canonical_server(rec.server)
                key = f"{rec.server}:{rec.tool_name}"
                if key not in tools_by_id:
                    classification = self.classifier.classify_tool(rec.tool_name, rec.server)
                    rec.action_class = classification["action_class"]
                    rec.effective_class = classification["effective_class"]
                    rec.authority_ceiling = classification["authority_ceiling"]
                    tools_by_id[key] = rec
        except Exception as e:
            logger.warning("Error reading SEED_CAPABILITIES: %s", e)

        records = list(tools_by_id.values())
        logger.info("Discovered and classified %d unique tools across federation", len(records))
        return records

    def compute_digest(self, records: Sequence[CapabilityRecord]) -> str:
        """Compute SHA256 digest of all capability definitions."""
        sorted_records = sorted(records, key=lambda r: f"{r.server}:{r.tool_name}")
        payload = json.dumps([r.model_dump() for r in sorted_records], sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def sync_to_registry_json(self, records: Sequence[CapabilityRecord]) -> None:
        """Write canonical registry JSON update."""
        sorted_records = sorted(records, key=lambda r: f"{r.server}:{r.tool_name}")
        
        # Calculate server breakdown
        servers_map: Dict[str, int] = {}
        for r in sorted_records:
            servers_map[r.server] = servers_map.get(r.server, 0) + 1

        servers_list = [{"name": s, "tools": cnt} for s, cnt in sorted(servers_map.items())]

        registry_payload = {
            "$schema": "arifOS/AAA-capability-index/v2.0.0",
            "protocol": "MCP",
            "protocolVersion": "2026-07-28",
            "forgedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "total_tools": len(sorted_records),
            "digest": self.compute_digest(sorted_records),
            "servers": servers_list,
            "tools": [r.model_dump() for r in sorted_records],
        }

        CAPABILITY_INDEX_JSON.parent.mkdir(parents=True, exist_ok=True)
        with open(CAPABILITY_INDEX_JSON, "w", encoding="utf-8") as f:
            json.dump(registry_payload, f, indent=2)
        logger.info("Saved %d tools to %s", len(sorted_records), CAPABILITY_INDEX_JSON)

    def reindex(self, force: bool = False) -> Dict[str, Any]:
        """Perform full reindexing into Qdrant/vector store if digest changed."""
        records = self.discover_tools()
        current_digest = self.compute_digest(records)

        # Check existing state
        last_state = {}
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as sf:
                    last_state = json.load(sf)
            except Exception:
                pass

        if not force and last_state.get("digest") == current_digest:
            logger.info("Capability index digest unchanged (%s). Skipping upsert.", current_digest[:8])
            return {
                "status": "UP_TO_DATE",
                "tool_count": len(records),
                "digest": current_digest,
            }

        # Update registry JSON
        self.sync_to_registry_json(records)

        # Upsert into vector store (claim == measurement: the return value is
        # the truth, not the absence of an exception)
        try:
            self.store.create_collection(recreate=False)
            upsert_ok = bool(self.store.upsert(records))
            if upsert_ok:
                logger.info("Successfully reindexed %d tools into Qdrant store", len(records))
            else:
                logger.warning("Vector store upsert did not complete — local fallback only")
        except Exception as e:
            logger.warning("Vector store upsert deferred or offline: %s", e)
            upsert_ok = False

        # Save state
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        new_state = {
            "digest": current_digest,
            "tool_count": len(records),
            "reindexed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "vector_store_ok": upsert_ok,
        }
        with open(STATE_FILE, "w", encoding="utf-8") as sf:
            json.dump(new_state, sf, indent=2)

        return {
            "status": "REINDEXED",
            "tool_count": len(records),
            "digest": current_digest,
            "vector_store_ok": upsert_ok,
        }


def auto_reindex(force: bool = False) -> Dict[str, Any]:
    indexer = CapabilityIndexer()
    return indexer.reindex(force=force)


if __name__ == "__main__":
    res = auto_reindex(force=True)
    print(json.dumps(res, indent=2))
