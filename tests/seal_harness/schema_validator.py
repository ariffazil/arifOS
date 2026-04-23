"""
Schema Discovery and Drift Detection

Validates that the MCP server's capabilities match the expected snapshot.
Detects:
- Missing tools (breaking changes)
- New tools (potential drift)
- Schema changes (breaking changes)
"""

import json
import hashlib
import os
from typing import Dict, Any, List, Tuple
from .client import MCPClient


class SchemaValidator:
    """
    Validates MCP server schema against a snapshot.
    """

    def __init__(self, client: MCPClient, snapshot_path: str = "aaa-schema-snapshot.json"):
        self.client = client
        self.snapshot_path = snapshot_path

    def _hash_schema(self, obj: Any) -> str:
        """Generate stable hash of schema object."""
        # Normalize: sort keys, ensure consistent formatting
        normalized = json.dumps(obj, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    async def capture_capabilities(self) -> Dict[str, Any]:
        """Capture current server capabilities."""
        print("  Discovering tools...")
        tools = await self.client.list_tools()

        print("  Discovering resources...")
        resources = await self.client.list_resources()

        print("  Discovering prompts...")
        prompts = await self.client.list_prompts()

        # Build capability map
        caps = {
            "version": "2026.3.1",
            "tools": {},
            "resources": {},
            "prompts": {},
            "allow_new_tools": [],
        }

        for tool in tools:
            name = tool.get("name")
            if name:
                # Hash of inputSchema for change detection
                schema_hash = self._hash_schema(tool.get("inputSchema", {}))
                caps["tools"][name] = {
                    "hash": schema_hash,
                    "description_hash": self._hash_schema(tool.get("description", "")),
                }

        for resource in resources:
            uri = resource.get("uri") or resource.get("name")
            if uri:
                caps["resources"][uri] = {"hash": self._hash_schema(resource)}

        for prompt in prompts:
            name = prompt.get("name")
            if name:
                caps["prompts"][name] = {"hash": self._hash_schema(prompt)}

        return caps

    def load_snapshot(self) -> Dict[str, Any]:
        """Load existing snapshot or return empty."""
        if not os.path.exists(self.snapshot_path):
            return {}

        with open(self.snapshot_path, "r") as f:
            return json.load(f)

    def save_snapshot(self, snapshot: Dict[str, Any]):
        """Save snapshot to disk."""
        with open(self.snapshot_path, "w") as f:
            json.dump(snapshot, f, indent=2)
        print(f"  Snapshot saved to {self.snapshot_path}")

    def compare_capabilities(
        self, current: Dict[str, Any], snapshot: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare current capabilities against snapshot.

        Returns dict with:
        - added_tools: new tools not in snapshot
        - removed_tools: tools in snapshot but not current
        - changed_tools: tools with different schemas
        - ok: True if no breaking changes
        """
        current_tools = set(current.get("tools", {}).keys())
        snapshot_tools = set(snapshot.get("tools", {}).keys())

        added = list(current_tools - snapshot_tools)
        removed = list(snapshot_tools - current_tools)

        # Check for schema changes in common tools
        changed = []
        for tool_name in current_tools & snapshot_tools:
            current_hash = current["tools"][tool_name].get("hash")
            snapshot_hash = snapshot["tools"][tool_name].get("hash")
            if current_hash != snapshot_hash:
                changed.append(tool_name)

        # Check allow_new_tools list
        allowed_new = set(snapshot.get("allow_new_tools", []))
        unauthorized_new = [t for t in added if t not in allowed_new]

        # Determine if changes are breaking
        breaking = removed or changed or unauthorized_new

        return {
            "ok": not breaking,
            "added_tools": added,
            "removed_tools": removed,
            "changed_tools": changed,
            "unauthorized_new_tools": unauthorized_new,
            "allowed_but_new": [t for t in added if t in allowed_new],
        }

    async def validate(self, bootstrap: bool = False) -> Dict[str, Any]:
        """
        Main validation entrypoint.

        If bootstrap=True or no snapshot exists, creates snapshot and exits.
        Otherwise, compares current against snapshot.
        """
        print("\n📋 Schema Validation")
        print("─" * 50)

        # Capture current state
        current = await self.capture_capabilities()

        # Check for existing snapshot
        snapshot = self.load_snapshot()

        if not snapshot or bootstrap:
            # Bootstrap mode: create initial snapshot
            print("\n  🆕 Bootstrap mode: Creating initial snapshot")
            self.save_snapshot(current)
            return {
                "ok": True,
                "mode": "bootstrap",
                "tools_count": len(current.get("tools", {})),
                "resources_count": len(current.get("resources", {})),
                "prompts_count": len(current.get("prompts", {})),
            }

        # Compare mode
        print("\n  🔍 Comparing against existing snapshot")
        comparison = self.compare_capabilities(current, snapshot)

        # Print results
        if comparison["added_tools"]:
            print(f"    ⚠️  New tools: {comparison['added_tools']}")
        if comparison["removed_tools"]:
            print(f"    ❌ Removed tools: {comparison['removed_tools']}")
        if comparison["changed_tools"]:
            print(f"    ❌ Changed tools: {comparison['changed_tools']}")
        if comparison["unauthorized_new_tools"]:
            print(f"    ❌ Unauthorized new: {comparison['unauthorized_new_tools']}")

        if comparison["ok"]:
            print("    ✅ No breaking changes detected")
        else:
            print("    ❌ Breaking changes detected!")

        return comparison
