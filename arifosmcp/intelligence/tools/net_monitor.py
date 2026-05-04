from __future__ import annotations


async def check_connectivity(host: str = "https://example.com", timeout: float = 5.0) -> dict:
    return {"ok": True, "host": host, "timeout": timeout}
