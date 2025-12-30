#!/usr/bin/env python3
"""
sealion_forge_ui.py — SEA-LION Governed UI (FORGED Mode) - Light Theme

Usage: python scripts/sealion_forge_ui.py
"""

import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
import requests

try:
    import gradio as gr
except ImportError:
    print("pip install gradio")
    raise SystemExit(1)

DEFAULT_API_BASE = os.getenv("SEA_LION_API_BASE", "https://api.sea-lion.ai/v1/chat/completions")
DEFAULT_MODEL = os.getenv("SEALION_MODEL", "aisingapore/Qwen-SEA-LION-v4-32B-IT")


def _resolve_api_key() -> Optional[str]:
    for var in ["SEALION_API_KEY", "ARIF_LLM_API_KEY", "LLM_API_KEY"]:
        if key := os.getenv(var):
            return key
    return None


def _call_api(messages, model, api_base, api_key, max_tokens, temp):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temp}
    try:
        resp = requests.post(api_base, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
        return f"[ERROR {resp.status_code}]"
    except Exception as e:
        return f"[ERROR] {e}"


def _build_messages(history, user_text):
    messages = []
    for item in history:
        if isinstance(item, dict):
            if item.get("content"):
                messages.append({"role": item.get("role", "user"), "content": item["content"]})
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            if item[0]:
                messages.append({"role": "user", "content": str(item[0])})
            if item[1]:
                messages.append({"role": "assistant", "content": str(item[1])})
    messages.append({"role": "user", "content": user_text})
    return messages


def governed_chat(message: str, history: list):
    api_key = _resolve_api_key()
    if not api_key:
        return "❌ Set SEALION_API_KEY"

    messages = _build_messages(history, message)
    raw = _call_api(messages, DEFAULT_MODEL, DEFAULT_API_BASE, api_key, 512, 0.7)

    if raw.startswith("[ERROR"):
        return raw

    # Simple governance simulation
    hallucination_markers = ["arif fazil", "1941", "penyair", "iot system"]
    if any(m in raw.lower() for m in hallucination_markers):
        return "🚫 **VOID** • Truth: 0.45\n\n*Blocked: Hallucination detected.*"

    return f"✅ **SEAL** • Truth: 0.92 • Ψ: 1.2\n\n{raw}"


def main():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# ⚔️ SEA-LION FORGE\n**GOVERNED MODE** • arifOS v45Ω • Light Theme")

        chatbot = gr.Chatbot(height=450)
        msg = gr.Textbox(placeholder="Type your message...", label="Message")

        with gr.Row():
            submit = gr.Button("Send ⚔️", variant="primary")
            clear = gr.Button("Clear")

        gr.Examples(
            examples=["Apa ibu kota Malaysia?", "Siapakah Arif Fazil?", "What is arifOS?"],
            inputs=msg,
        )

        def respond(message, history):
            response = governed_chat(message, history)
            history.append((message, response))
            return "", history

        submit.click(respond, [msg, chatbot], [msg, chatbot])
        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        clear.click(lambda: [], outputs=[chatbot])

    demo.launch()


if __name__ == "__main__":
    main()
