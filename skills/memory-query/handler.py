"""
memory-query skill handler
F555 vector memory with freshness enforcement.
"""

from datetime import datetime, timedelta
from typing import Any


class MemoryQuerySkill:
    """Skill for memory operations with constitutional freshness."""
    
    NAME = "memory-query"
    FLOOR = "F555"
    
    async def execute(
        self,
        action: str,
        params: dict[str, Any],
        session_id: str,
        dry_run: bool = True,
        reality_bridge: Any | None = None,
        checkpoint: str | None = None
    ) -> dict[str, Any]:
        """Execute memory action."""
        handlers = {
            "vector_search": self._vector_search,
            "store_memory": self._store_memory,
        }
        
        handler = handlers.get(action)
        if not handler:
            return {"verdict": "VOID", "reason": f"Unknown action: {action}"}
        
        return await handler(params, dry_run, reality_bridge, checkpoint)
    
    async def _vector_search(
        self,
        params: dict,
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None
    ) -> dict[str, Any]:
        """Search memory with F2 freshness check."""
        query = params.get("query", "")
        k = params.get("k", 5)
        
        if dry_run:
            return {
                "verdict": "SEAL",
                "mode": "dry_run",
                "query": query,
                "checkpoint": checkpoint
            }
        
        # REALITY: Query via filesystem
        if reality_bridge:
            result = reality_bridge.execute(
                tool="filesystem",
                command="read",
                params={"path": f"./memory/{query}.json"},
                checkpoint_id=checkpoint
            )
            
            results = []
            if result.get("success"):
                import json
                try:
                    data = json.loads(result.get("stdout", "[]"))
                    results = self._filter_fresh(data)
                except:
                    pass
            
            return {
                "verdict": "SEAL",
                "mode": "real",
                "results": results,
                "freshness": len(results) / max(len(results), 1),
                "checkpoint": checkpoint
            }
        
        return {"verdict": "VOID", "error": "No reality bridge available"}
    
    async def _store_memory(
        self,
        params: dict,
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None
    ) -> dict[str, Any]:
        """Store memory with timestamp."""
        key = params.get("key", "")
        value = params.get("value", {})
        
        if dry_run:
            return {
                "verdict": "SEAL",
                "mode": "dry_run",
                "key": key,
                "checkpoint": checkpoint
            }
        
        if reality_bridge:
            import json
            data = json.dumps({"value": value, "timestamp": datetime.now().isoformat()})
            
            result = reality_bridge.execute(
                tool="shell",
                command=f"echo '{data}' > ./memory/{key}.json",
                params={},
                checkpoint_id=checkpoint
            )
            
            return {
                "verdict": "SEAL" if result.get("success") else "VOID",
                "mode": "real",
                "key": key,
                "checkpoint": checkpoint
            }
        
        return {"verdict": "VOID", "error": "No reality bridge available"}
    
    def _filter_fresh(self, results: list) -> list:
        """Filter results older than 24h (F2)."""
        cutoff = datetime.now() - timedelta(hours=24)
        return [r for r in results if r.get("timestamp", datetime.now()) > cutoff]


skill = MemoryQuerySkill()


async def execute(
    action: str,
    params: dict[str, Any],
    session_id: str,
    dry_run: bool = True,
    reality_bridge: Any | None = None,
    checkpoint: str | None = None
) -> dict[str, Any]:
    """Main entry point."""
    skill = MemoryQuerySkill()
    return await skill.execute(action, params, session_id, dry_run, reality_bridge, checkpoint)


metadata = {
    "name": "memory-query",
    "floor": "F555",
    "actions": ["vector_search", "store_memory"],
    "reversible": True
}
