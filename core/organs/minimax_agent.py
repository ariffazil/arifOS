import os
import httpx
import json
import logging
from dataclasses import dataclass

logger = logging.getLogger("arifOS.Minimax")

@dataclass
class MinimaxEnvelope:
    ok: bool
    text: str
    error: str = ""

async def minimax_generate(prompt: str, max_tokens: int = 1000) -> MinimaxEnvelope:
    """
    Real Intelligence fallback using Minimax API.
    Replaces missing Ollama for 111-333 Reasoning.
    """
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        return MinimaxEnvelope(False, "", "MINIMAX_API_KEY missing from environment")

    # Minimax V2 (ChatCompletion)
    url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "abab6.5s-chat", # Fast but capable for reasoning
        "messages": [
            {"role": "system", "content": "You are the arifOS AGI Mind (Stage 111-333). Apply constitutional physics (ΔS ≤ 0)."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Correct Minimax V2 response parsing
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return MinimaxEnvelope(True, content)
            else:
                return MinimaxEnvelope(False, "", f"Unexpected API structure: {data}")
            
    except Exception as e:
        logger.error(f"Minimax API Error: {e}")
        return MinimaxEnvelope(False, "", str(e))
