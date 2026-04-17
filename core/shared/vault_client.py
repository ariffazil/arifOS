import os
import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from supabase import create_client, Client

class VaultClient:
    """
    Shared VAULT999 client.
    Import this in every organ MCP server.
    One instance per process — pass organ_id at init.
    """
    def __init__(self, organ_id: str):
        # organ_id: "arifos" | "wealth" | "well" | "geox"
        self.organ_id = organ_id
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            # Fallback to SERVICE_ROLE_KEY if SERVICE_KEY is not set
            key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            
        if not url or not key:
            self.client = None
            print(f"WARN: VaultClient({organ_id}) Supabase config missing. Sealing disabled.")
        else:
            self.client = create_client(url, key)

    async def seal(
        self,
        verdict: str,           # SEAL | HOLD | PARTIAL | VOID
        tool_name: str,
        session_id: str,
        actor_id: str,
        payload: Dict[str, Any],
        floor_results: List[Dict[str, Any]],
        g_star: float
    ) -> Dict[str, Any]:
        if not self.client:
            return {"ok": False, "error": "Supabase client not initialized"}

        prev_hash = await self._get_last_hash()
        record = {
            "organ":        self.organ_id,
            "tool_name":    tool_name,
            "session_id":   session_id,
            "actor_id":     actor_id,
            "verdict":      verdict,
            "payload":      payload,
            "floor_results": floor_results,
            "g_star":       g_star,
            "prev_hash":    prev_hash,
            "timestamp":    datetime.utcnow().isoformat()
        }
        record["hash"] = self._merkle_hash(record)
        
        try:
            result = self.client.table("arifosmcp_vault_seals")\
                                  .insert(record).execute()
            return result.data[0]
        except Exception as e:
            print(f"ERROR: Vault seal failed: {e}")
            return {"ok": False, "error": str(e)}

    def _merkle_hash(self, record: Dict[str, Any]) -> str:
        content = json.dumps(record, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    async def _get_last_hash(self) -> str:
        if not self.client:
            return "GENESIS"
        try:
            result = self.client.table("arifosmcp_vault_seals")\
                .select("hash")\
                .order("timestamp", desc=True)\
                .limit(1).execute()
            if result.data:
                return result.data[0]["hash"]
        except Exception as e:
            print(f"WARN: Failed to fetch last hash: {e}")
        return "GENESIS"
