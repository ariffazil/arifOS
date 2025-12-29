#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sealion_bogel_ui.py — SEA-LION Gradio UI (BOGEL Mode)

Raw, stateful SEA-LION chat UI using an OpenAI-compatible `/chat/completions`
endpoint. This is intentionally UNGOVERNED (baseline "bogel" mode) and is meant
to be compared against governed pipelines (e.g., `scripts/sealion_forge_repl.py`).

Usage:
  pip install gradio requests
  $env:SEALION_API_KEY = "sk-..."
  python scripts/sealion_bogel_ui.py

Env:
  SEALION_API_KEY (or ARIF_LLM_API_KEY)
  SEALION_MODEL (optional)
  SEA_LION_API_BASE (optional)  # full endpoint, default: https://api.sea-lion.ai/v1/chat/completions
"""

from __future__ import annotations

import os
import sys
import time
from typing import Any, Dict, List, Tuple, Optional

import requests

try:
    import gradio as gr
except ImportError:
    print("❌ Missing dependency: gradio")
    print("Install with: pip install gradio")
    raise SystemExit(1)


DEFAULT_API_BASE = os.getenv(
    "SEA_LION_API_BASE",
    "https://api.sea-lion.ai/v1/chat/completions",
)
DEFAULT_MODEL = os.getenv("SEALION_MODEL", "aisingapore/Qwen-SEA-LION-v4-32B-IT")

# Conservative defaults; UI exposes these as controls
DEFAULT_MAX_TOKENS = 512
DEFAULT_TEMPERATURE = 0.7
MAX_CONTEXT_TOKENS = 8000
TOKENS_PER_CHAR = 0.3  # rough BPE estimate
MAX_RETRIES = 3
RETRY_DELAY_BASE_S = 1.0


def _resolve_api_key() -> Optional[str]:
    for var in ["SEALION_API_KEY", "ARIF_LLM_API_KEY", "LLM_API_KEY", "OPENAI_API_KEY"]:
        key = os.getenv(var)
        if key:
            return key
    return None


def _estimate_tokens(text: str) -> int:
    return int(len(text) * TOKENS_PER_CHAR)


def _trim_messages(
    messages: List[Dict[str, str]], max_tokens: int = MAX_CONTEXT_TOKENS
) -> List[Dict[str, str]]:
    if not messages:
        return messages

    total = sum(_estimate_tokens(m.get("content", "")) for m in messages)
    if total <= max_tokens:
        return messages

    system_msgs = [m for m in messages if m.get("role") == "system"]
    other_msgs = [m for m in messages if m.get("role") != "system"]

    while other_msgs and total > max_tokens:
        removed = other_msgs.pop(0)
        total -= _estimate_tokens(removed.get("content", ""))

    return system_msgs + other_msgs


def _build_messages(
    history: List[Any],
    user_text: str,
    *,
    system_prompt: str,
) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = []

    sys_text = system_prompt.strip()
    if sys_text:
        messages.append({"role": "system", "content": sys_text})

    # Gradio v6 uses list of dicts: [{"role": "user", "content": "..."}, ...]
    # Gradio v4 used list of tuples: [("user msg", "assistant msg"), ...]
    for item in history:
        if isinstance(item, dict):
            # Gradio v6 format
            role = item.get("role", "user")
            content = item.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            # Gradio v4 format (tuples)
            user_msg, assistant_msg = item[0], item[1]
            if user_msg:
                messages.append({"role": "user", "content": str(user_msg)})
            if assistant_msg:
                messages.append({"role": "assistant", "content": str(assistant_msg)})

    messages.append({"role": "user", "content": user_text})
    return messages


def _call_sealion(
    *,
    api_base: str,
    api_key: str,
    model: str,
    messages: List[Dict[str, str]],
    max_tokens: int,
    temperature: float,
) -> Tuple[str, Dict[str, Any]]:
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    last_error: Optional[str] = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            start_time = time.time()
            resp = requests.post(api_base, headers=headers, json=payload, timeout=60)
            latency_ms = (time.time() - start_time) * 1000

            if resp.status_code == 200:
                data = resp.json()
                text = data["choices"][0]["message"]["content"].strip()
                return text, {
                    "model": model,
                    "latency_ms": latency_ms,
                    "usage": data.get("usage", {}),
                    "attempt": attempt,
                }

            if resp.status_code == 429 or resp.status_code >= 500:
                delay = RETRY_DELAY_BASE_S * (2 ** (attempt - 1))
                last_error = f"{resp.status_code} {resp.text[:200]}"
                time.sleep(delay)
                continue

            if resp.status_code in (401, 403):
                return (
                    f"[AUTH ERROR] Invalid API key (status {resp.status_code})",
                    {"status_code": resp.status_code, "error": resp.text[:500], "attempt": attempt},
                )

            return (
                f"[API ERROR] Status {resp.status_code}",
                {"status_code": resp.status_code, "error": resp.text[:500], "attempt": attempt},
            )
        except requests.exceptions.Timeout:
            delay = RETRY_DELAY_BASE_S * (2 ** (attempt - 1))
            last_error = "Timeout"
            time.sleep(delay)
        except requests.exceptions.ConnectionError as e:
            return f"[CONNECTION ERROR] {e}", {}
        except (ValueError, KeyError, TypeError) as e:
            return f"[PARSE ERROR] {e}", {}

    return f"[FAILED] Max retries exceeded. Last error: {last_error}", {}


def chat(
    message: str,
    history: List[Tuple[str, str]],
    model: str,
    api_base: str,
    temperature: float,
    max_tokens: int,
    system_prompt: str,
) -> str:
    api_key = _resolve_api_key()
    if not api_key:
        raise gr.Error("Missing API key. Set SEALION_API_KEY (or ARIF_LLM_API_KEY).")

    messages = _build_messages(history, message, system_prompt=system_prompt)
    messages = _trim_messages(messages, max_tokens=MAX_CONTEXT_TOKENS)

    response, _meta = _call_sealion(
        api_base=api_base,
        api_key=api_key,
        model=model,
        messages=messages,
        max_tokens=int(max_tokens),
        temperature=float(temperature),
    )
    return response


def main() -> int:
    model = gr.Dropdown(
        label="Model",
        value=DEFAULT_MODEL,
        choices=[
            "aisingapore/Qwen-SEA-LION-v4-32B-IT",
            "aisingapore/Gemma-SEA-LION-v4-27B-IT",
            "aisingapore/Llama-SEA-LION-v3-70B-IT",
            "aisingapore/Llama-SEA-LION-v3-8B-IT",
        ],
        allow_custom_value=True,
    )
    api_base = gr.Textbox(label="API endpoint", value=DEFAULT_API_BASE)
    temperature = gr.Slider(
        label="Temperature", minimum=0.0, maximum=1.5, value=DEFAULT_TEMPERATURE, step=0.05
    )
    max_tokens = gr.Slider(
        label="Max tokens", minimum=16, maximum=2048, value=DEFAULT_MAX_TOKENS, step=16
    )
    system_prompt = gr.Textbox(
        label="System prompt (optional)",
        value="",
        lines=3,
        placeholder="Leave blank for fully raw baseline.",
    )

    title = "🦁 SEA-LION (BOGEL) — Raw Chat UI"
    description = (
        "Ungoverned baseline chat (no arifOS pipeline). "
        "Set `SEALION_API_KEY` (or `ARIF_LLM_API_KEY`) before launching."
    )

    demo = gr.ChatInterface(
        fn=chat,
        additional_inputs=[model, api_base, temperature, max_tokens, system_prompt],
        title=title,
        description=description,
    )

    demo.launch()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
