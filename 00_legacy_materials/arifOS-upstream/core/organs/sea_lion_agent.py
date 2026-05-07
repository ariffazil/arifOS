import os
import httpx
import logging
from dataclasses import dataclass

logger = logging.getLogger("arifOS.SEA-LION")


@dataclass
class SeaLionEnvelope:
    ok: bool
    text: str
    error: str = ""


async def sea_lion_generate(
    prompt: str, max_tokens: int = 1000, model: str = "aisingapore/Gemma-SEA-LION-v4-27B-IT"
) -> SeaLionEnvelope:
    """
    Real Intelligence via SEA-LION API (Singapore gov-backed LLM).
    Secondary fallback for 111-333 Reasoning.
    """
    api_key = os.getenv("SEA_LION_API_KEY")
    if not api_key:
        return SeaLionEnvelope(False, "", "SEA_LION_API_KEY missing from environment")

    url = "https://api.sea-lion.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are the arifOS AGI Mind (Stage 111-333). Apply constitutional physics (ΔS ≤ 0).",
            },
            {"role": "user", "content": prompt},
        ],
        "max_completion_tokens": max_tokens,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return SeaLionEnvelope(True, content)
            else:
                return SeaLionEnvelope(False, "", f"Unexpected API structure: {data}")

    except Exception as e:
        logger.error(f"SEA-LION API Error: {e}")
        return SeaLionEnvelope(False, "", str(e))
