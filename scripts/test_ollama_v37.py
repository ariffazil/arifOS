#!/usr/bin/env python3
"""
test_ollama_v37.py - Minimal v37 + Ollama integration test

This script calls a local Ollama model and runs the response through the
full arifOS constitutional cage via `cage_llm_response`.

Prerequisites:
- Ollama installed and running (default: http://localhost:11434)
- At least one model pulled, e.g.:
    ollama pull llama3

Usage:
    python scripts/test_ollama_v37.py

You will be prompted for a query. The script will:
  1. Send the query to Ollama (llama3 by default),
  2. Run the raw response through the v37 pipeline,
  3. Print verdict, stage trace, floor failures, and final response.
"""

from __future__ import annotations

from typing import Any, Dict, List

import requests

from scripts.arifos_caged_llm_demo import cage_llm_response
from arifos_core.context_injection import build_system_context


def call_ollama(messages: List[Dict[str, str]], model: str = "llama3") -> str:
    """
    Call a local Ollama model using its HTTP API.

    Args:
        messages: Chat-style messages with 'role' and 'content'.
        model: Ollama model name (e.g., "llama3", "gemma3:4b").

    Returns:
        Raw string response from the Ollama model.
    """
    # Combine any system + user messages into a single prompt string so that
    # we can pass arifOS context when present.
    parts: List[str] = []
    for message in messages:
        role = message.get("role")
        content = message.get("content", "")
        if not content:
            continue
        if role == "system":
            parts.append(f"System context:\n{content}\n")
        elif role == "user":
            parts.append(content)

    prompt_text = "\n\n".join(parts)

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt_text,
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
        data: Dict[str, Any] = response.json()
        return str(data.get("response", ""))
    except requests.exceptions.ReadTimeout:
        # Propagate a sentinel string so the pipeline can continue and the
        # harness can record that Ollama timed out on this prompt.
        return "[OLLLAMA_TIMEOUT: no response within 120s]"
    except requests.exceptions.RequestException as exc:
        # Surface other HTTP errors as a synthetic response instead of
        # crashing the pipeline.
        return f"[OLLAMA_REQUEST_ERROR: {exc}]"


def main() -> None:
    """Prompt the user and run a single v37-governed Ollama call."""
    prompt = input("arifOS v37 + Ollama prompt: ").strip()
    if not prompt:
        prompt = "Should I invest my savings in cryptocurrency?"

    # Simple heuristic: treat obviously sensitive topics as high-stakes
    lowered = prompt.lower()
    high_stakes = any(
        keyword in lowered
        for keyword in (
            "invest",
            "suicide",
            "kill",
            "harm",
            "legal",
            "medical",
            "savings",
            "loan",
            "diagnosis",
        )
    )

    # Build grounding context for any domain-specific terms (e.g. arifOS).
    grounding_context = build_system_context(prompt)
    system_prompt: str | None = None
    if grounding_context:
        system_prompt = (
            "You are a helpful assistant operating under the arifOS governance "
            "kernel.\n"
            f"{grounding_context}"
        )

    result = cage_llm_response(
        prompt=prompt,
        call_model=call_ollama,
        high_stakes=high_stakes,
        system_prompt=system_prompt,
    )

    print("\n=== arifOS v37 + Ollama Result ===")
    print("Verdict:", result.verdict)
    print("Stage trace:", " -> ".join(result.stage_trace))
    print("Floor failures:", result.floor_failures)
    print("\nFinal response:\n")
    print(result.final_response)


if __name__ == "__main__":
    main()
