"""
codebase.mcp.external_gateways.brave_client (v53.2.2)
Reality grounding search client via Brave Search API.
F7 (Humility): Explicit uncertainty logging and disclosure.
"""

import httpx
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class BraveSearchClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("BRAVE_API_KEY")
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def search(
        self,
        query: str,
        intent: str,
        scar_weight: float
    ) -> Dict[str, Any]:
        """
        Reality check via Brave Search.
        """
        if not query or not query.strip():
            logger.warning("Brave Search: empty query, returning fallback")
            return {
                "source": "Brave Search",
                "error": "Empty query — nothing to search",
                "fallback": "Using cached knowledge",
                "omega_0_update": 0.08,
            }

        if not self.api_key:
            logger.warning("Brave Search: API Key missing, returning fallback")
            return {
                "source": "Brave Search",
                "error": "API Key missing",
                "fallback": "Using cached knowledge",
                "omega_0_update": 0.10
            }

        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        }
        
        try:
            # Brave News endpoint for time-sensitive queries
            logger.info(f"Brave Search: query='{query}' intent='{intent}'")
            response = await self.client.get(
                "https://api.search.brave.com/res/v1/news/search",
                params={
                    "q": query,
                    "count": 5,
                    "freshness": "pd"  # Past day for news
                },
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "source": "Brave Search",
                "news": result.get("results", []),
                "omega_0_update": 0.04,
                "disclosure": "Results sourced from Brave Search (real-time external data)",
                "timestamp": result.get("search_url")
            }
        
        except Exception as e:
            logger.error(f"Brave Search API error: {e}")
            return {
                "source": "Brave Search",
                "error": str(e),
                "fallback": "Using cached knowledge",
                "omega_0_update": 0.08
            }

    async def close(self):
        await self.client.aclose()
