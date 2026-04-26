"""
arifosmcp/runtime/wisdom_sea_lion.py — SEA-LION v4 Cultural Wisdom Bridge
Integrated with AI Singapore (AISG) API (10 RPM Free Tier).

Uses Qwen-SEA-LION-v4-32B-IT for regional intelligence.
"""

from __future__ import annotations

import os
import json
import logging
import httpx
from typing import Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# --- Configuration ---
API_KEY = os.getenv("SEA_LION_API_KEY")
BASE_URL = os.getenv("SEA_LION_BASE_URL", "https://api.sea-lion.ai/v1")
MODEL = "aisingapore/Qwen-SEA-LION-v4-32B-IT"

async def generate_nusantara_wisdom(
    context: str, 
    agent_intent: Optional[str] = None
) -> dict[str, Any]:
    """
    Query SEA-LION for a high-intelligence philosophy quote grounded in SEA context.
    """
    if not API_KEY:
        return {"error": "SEA_LION_API_KEY missing"}

    prompt = f"""
    You are the arifOS Cultural Wisdom Engine. 
    Task: Provide one of the 99 most intelligent human quotes that fits the Southeast Asian (Nusantara) 
    context of 'Amanah' (Trustworthiness) or 'Ditempa Bukan Diberi' (Forged, Not Given).
    
    Context: {context}
    Agent Intent: {agent_intent or 'General Governance'}
    
    Output MUST be a single JSON object with these fields:
    - text: The quote text.
    - author: The human author.
    - source: Original book or speech.
    - category: One of [truth, humility, restraint, judgment, memory, discipline, responsibility, peribahasa, founder, seal, love, paradox, scar]
    - language: 'en' or 'ms'
    - tone: [firm, calm, severe, reflective]
    - scar_weight: 0-3 (depth of experience)
    - explanation: Why this quote matters in this context.
    """

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.7
                }
            )
            
            if response.status_code != 200:
                return {"error": f"API returned {response.status_code}: {response.text}"}
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Extract JSON from potential prose wrapper
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            
            return json.loads(content)

    except Exception as e:
        logger.error(f"SEA-LION Wisdom Bridge Failure: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Quick test
    import asyncio
    res = asyncio.run(generate_nusantara_wisdom("arif_vault_seal", "Hardening the Merkle trail"))
    print(json.dumps(res, indent=2))
