import asyncio
import json
import logging
import os
import threading
from datetime import UTC, datetime

import httpx

logger = logging.getLogger(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://utbmmjmbolmuahwixjqc.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", os.environ.get("SUPABASE_SERVICE_ROLE_KEY", ""))


async def _send_receipt_async(payload: dict):
    if not SUPABASE_KEY:
        logger.debug("SUPABASE_KEY not found. Skipping receipt write (fail-soft).")
        return

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    url = f"{SUPABASE_URL}/rest/v1/arifosmcp_tool_calls"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers, timeout=5.0)
            if resp.status_code not in (200, 201, 204):
                logger.error(f"Supabase receipt write failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        logger.error(f"Supabase receipt write error (fail-soft): {e}")


def _send_receipt_sync(payload: dict):
    if not SUPABASE_KEY:
        return

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    url = f"{SUPABASE_URL}/rest/v1/arifosmcp_tool_calls"

    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=5.0)
        if resp.status_code not in (200, 201, 204):
            logger.error(f"Supabase receipt write failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        logger.error(f"Supabase receipt write error (fail-soft): {e}")


def sanitize(obj):
    try:
        return json.loads(json.dumps(obj, default=str))
    except Exception:
        return str(obj)


def dispatch_tool_receipt(
    tool_name: str, kwargs: dict, response: dict, session_id: str = None, actor_id: str = None
):
    try:
        payload = {
            "tool_name": tool_name,
            "session_id": session_id,
            "actor_id": actor_id or "arifOS-MCP",
            "kwargs_snapshot": sanitize(kwargs),
            "response_snapshot": sanitize(response),
            "timestamp": datetime.now(UTC).isoformat(),
        }

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(_send_receipt_async(payload))
        except RuntimeError:
            # No running event loop, use a background thread
            threading.Thread(target=_send_receipt_sync, args=(payload,), daemon=True).start()

    except Exception as e:
        logger.error(f"Failed to dispatch tool receipt: {e}")
