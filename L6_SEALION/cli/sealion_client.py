#!/usr/bin/env python3
"""
Shared SEA-LION client helpers for bogel/forge tools.
Utilities only: key resolution, token estimates, trimming, and API calls with retry.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import requests

DEFAULT_MODEL = "aisingapore/Qwen-SEA-LION-v4-32B-IT"
DEFAULT_API_BASE = "https://api.sea-lion.ai/v1/chat/completions"
MAX_CONTEXT_TOKENS = 8000
TOKENS_PER_CHAR = 0.3
MAX_RETRIES = 3
RETRY_DELAY_BASE_S = 1.0


def resolve_api_key() -> Optional[str]:
    """Resolve API key from env or local .env (cwd first, then script dir)."""
    for var in ["SEALION_API_KEY", "SEA_LION_API_KEY", "LLM_API_KEY", "OPENAI_API_KEY"]:
        key = os.getenv(var)
        if key:
            return key

    env_paths = [Path.cwd() / ".env", Path(__file__).resolve().parent / ".env"]
    for env_path in env_paths:
        if not env_path.exists():
            continue
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    if k in ["SEALION_API_KEY", "SEA_LION_API_KEY", "OPENAI_API_KEY", "LLM_API_KEY"]:
                        return v.strip().strip("'\"")
    return None


def estimate_tokens(text: str) -> int:
    """Rough token estimate using TOKENS_PER_CHAR."""
    return int(len(text) * TOKENS_PER_CHAR)


def trim_messages(messages: Sequence[Dict[str, str]], max_tokens: int = MAX_CONTEXT_TOKENS) -> List[Dict[str, str]]:
    """Sliding window: keep system message + recent turns within token budget."""
    messages = list(messages)
    if not messages:
        return messages

    total = sum(estimate_tokens(m.get("content", "")) for m in messages)
    if total <= max_tokens:
        return messages

    system_msgs = [m for m in messages if m.get("role") == "system"]
    other_msgs = [m for m in messages if m.get("role") != "system"]

    while other_msgs and total > max_tokens:
        removed = other_msgs.pop(0)
        total -= estimate_tokens(removed.get("content", ""))

    return system_msgs + other_msgs


def _strip_markers(text: str) -> str:
    """Remove trailing verdict markers like '... ✓ SEAL' or '... 🛑 REFUSE HARD'."""
    if not text:
        return text
    return (
        text.replace("✓ SEAL", "")
        .replace("⚠️ REFUSE SOFT", "")
        .replace("🛑 REFUSE HARD", "")
        .replace("⏳ SABAR", "")
        .replace("❓ PARTIAL", "")
        .replace("🔒 VOID", "")
        .replace("🔒 888_HOLD", "")
    ).rstrip()


def build_messages_from_history(
    history: List[Any],
    user_text: str,
    *,
    system_prompt: str = "",
    use_history: bool = True,
) -> List[Dict[str, str]]:
    """Normalize history (gradio tuple/dict) into OpenAI-style message list."""
    messages: List[Dict[str, str]] = []
    sys_text = system_prompt.strip()
    if sys_text:
        messages.append({"role": "system", "content": sys_text})

    if use_history:
        for item in history:
            if isinstance(item, dict):
                role = item.get("role", "user")
                content = _strip_markers(item.get("content", ""))
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                user_msg, assistant_msg = item[0], item[1]
                if user_msg:
                    messages.append({"role": "user", "content": _strip_markers(str(user_msg))})
                if assistant_msg:
                    messages.append({"role": "assistant", "content": _strip_markers(str(assistant_msg))})

    messages.append({"role": "user", "content": user_text})
    return messages


def call_sealion(
    *,
    session: requests.Session,
    api_base: str,
    api_key: str,
    model: str,
    messages: List[Dict[str, str]],
    max_tokens: int,
    temperature: float,
    timeout_s: float = 60.0,
    stream: bool = False,
) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    Call SEA-LION API with exponential backoff retry.
    Returns (text or None, metadata)
    """
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if stream:
        payload["stream"] = True

    last_error: Optional[str] = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            start_time = time.time()
            resp = session.post(api_base, headers=headers, json=payload, timeout=timeout_s, stream=stream)
            latency_ms = (time.time() - start_time) * 1000

            if resp.status_code == 200:
                if stream:
                    full_chunks: List[str] = []
                    for line in resp.iter_lines():
                        if not line:
                            continue
                        if line.startswith(b"data: "):
                            line = line[len(b"data: ") :]
                        if line.strip() == b"[DONE]":
                            break
                        try:
                            chunk = json.loads(line.decode("utf-8"))
                        except json.JSONDecodeError:
                            continue
                        choices = chunk.get("choices") or []
                        if not choices:
                            continue
                        delta = choices[0].get("delta", {}) or {}
                        content_piece = delta.get("content") or ""
                        if content_piece:
                            full_chunks.append(content_piece)
                        # streaming finish_reason appears at end
                    text = "".join(full_chunks).strip()
                    return text, {
                        "ok": True,
                        "model": model,
                        "latency_ms": latency_ms,
                        "usage": {},
                        "attempt": attempt,
                        "status_code": resp.status_code,
                        "stream": True,
                    }

                data = resp.json()
                choice0 = (data.get("choices") or [{}])[0] or {}
                message = choice0.get("message") or {}
                content = message.get("content")
                if content is None:
                    tool_calls = message.get("tool_calls")
                    if tool_calls:
                        content = json.dumps({"tool_calls": tool_calls}, ensure_ascii=False)
                    else:
                        content = choice0.get("text") or ""
                text = str(content).strip()
                return text, {
                    "ok": True,
                    "model": model,
                    "latency_ms": latency_ms,
                    "usage": data.get("usage", {}),
                    "attempt": attempt,
                    "status_code": resp.status_code,
                    "finish_reason": choice0.get("finish_reason"),
                }

            if resp.status_code in (429,) or resp.status_code >= 500:
                delay = RETRY_DELAY_BASE_S * (2 ** (attempt - 1))
                last_error = f"{resp.status_code} {resp.text[:200]}"
                time.sleep(delay)
                continue

            if resp.status_code in (401, 403):
                return None, {
                    "ok": False,
                    "fatal": True,
                    "status_code": resp.status_code,
                    "error": resp.text[:500],
                    "attempt": attempt,
                }

            return None, {
                "ok": False,
                "status_code": resp.status_code,
                "error": resp.text[:500],
                "attempt": attempt,
            }
        except requests.exceptions.Timeout:
            delay = RETRY_DELAY_BASE_S * (2 ** (attempt - 1))
            last_error = "Timeout"
            time.sleep(delay)
        except requests.exceptions.ConnectionError as e:
            return None, {"ok": False, "error": str(e), "error_type": "connection_error"}
        except (ValueError, KeyError, TypeError) as e:
            return None, {"ok": False, "error": str(e), "error_type": "parse_error"}

    return None, {"ok": False, "error": f"Max retries exceeded. Last error: {last_error}"}
