import os
import httpx
import logging
from dataclasses import dataclass

logger = logging.getLogger("arifOS.Anthropic")


@dataclass
class AnthropicEnvelope:
    ok: bool
    text: str
    error: str = ""


async def anthropic_generate(
    prompt: str, max_tokens: int = 1000, model: str = "claude-sonnet-4-6"
) -> AnthropicEnvelope:
    """
    Real Intelligence via Anthropic API.
    Primary fallback for 111-333 Reasoning.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return AnthropicEnvelope(
            False, "", "ANTHROPIC_API_KEY missing from environment"
        )

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
    }

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "system": "You are the arifOS AGI Mind (Stage 111-333). Apply constitutional physics (ΔS ≤ 0).",
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            if "content" in data and len(data["content"]) > 0:
                content = data["content"][0]["text"]
                return AnthropicEnvelope(True, content)
            else:
                return AnthropicEnvelope(False, "", f"Unexpected API structure: {data}")

    except Exception as e:
        logger.error(f"Anthropic API Error: {e}")
        return AnthropicEnvelope(False, "", str(e))
