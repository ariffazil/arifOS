"""
codebase.mcp.external_gateways.context7_client (v53.2.2)
Technical documentation search client via Context7 API.
F11/F7 compliant: Scope-limited search with uncertainty metrics.
"""

import httpx
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class Context7Client:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.context7.io"):
        self.api_key = api_key or os.environ.get("CONTEXT7_API_KEY")
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def search(
        self,
        query: str,
        allowed_paths: List[str],
        scar_weight: float
    ) -> Dict[str, Any]:
        """
        Query technical documentation with scope limits.
        """
        if not self.api_key:
            logger.warning("Context7: API Key missing, returning fallback")
            return {
                "source": "Context7",
                "error": "API Key missing",
                "fallback": "Using local knowledge",
                "omega_0_update": 0.08
            }
            
        payload = {
            "query": query,
            "scope": allowed_paths,
            "return_confidence": True
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            logger.info(f"Context7 search: query='{query}' scope_count={len(allowed_paths)}")
            response = await self.client.post(
                f"{self.base_url}/v1/search",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "source": "Context7",
                "results": result.get("results", []),
                "scope_applied": allowed_paths,
                "omega_0_update": 0.03, # Reduced uncertainty
                "timestamp": result.get("timestamp")
            }
        
        except Exception as e:
            logger.error(f"Context7 API error: {e}")
            return {
                "source": "Context7",
                "error": str(e),
                "fallback": "Using local memory only",
                "omega_0_update": 0.06
            }
    
    async def close(self):
        await self.client.aclose()
