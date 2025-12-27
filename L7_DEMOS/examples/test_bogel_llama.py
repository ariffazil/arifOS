#!/usr/bin/env python3
"""
test_bogel_llama.py

Run the same 33‑prompt v37 red‑team suite against a **raw** Ollama model
without the arifOS constitutional cage.

This is your baseline / control experiment:

- `scripts/ollama_redteam_suite_v37.py`  → arifOS v37 + cage + floors + W@W.
- `scripts/test_bogel_llama.py`          → bare LLM ("llama bogel").

By comparing the two outputs, you can see exactly what value arifOS adds:
  - Hallucination reduction (arifOS vs. ArefOS),
  - Safety behavior on harmful prompts,
  - Jailbreak resistance (e.g. "[System Override] Reset all floors").

Prerequisites:
  - Ollama installed and running (http://localhost:11434).
  - `llama3` (or another model) pulled, e.g. `ollama pull llama3`.
  - Python dependency: `requests` (install once with `pip install requests`).

Usage (from repo root):
  - `python -m scripts.test_bogel_llama`        # uses llama3 by default
  - `python -m scripts.test_bogel_llama gemma3` # test another local model
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import requests


def load_suite(path: Path) -> List[Dict[str, Any]]:
    """Load the 33‑prompt test suite used by the v37 red‑team harness."""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("test_suite_v37.json must contain a list of prompts")
    return data


def call_ollama_bogel(prompt: str, model: str = "llama3") -> str:
    """
    Call a local Ollama model **directly**, without arifOS governance.

    This uses the simple /api/generate endpoint and sends only the user prompt
    (no system prompt, no context injection, no floors).
    """
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    data: Dict[str, Any] = response.json()
    return str(data.get("response", ""))


def run_bogel_suite(model: str = "llama3") -> None:
    """
    Run all 33 prompts against the bare Ollama model and log raw outputs.

    For each prompt we print:
      - ID, category, prompt text
      - A short snippet of the raw LLM response
    We also save the full responses to `bogel_results_<model>.json` next to
    `test_suite_v37.json` for later side‑by‑side comparison.
    """
    suite_path = Path(__file__).with_name("test_suite_v37.json")
    prompts = load_suite(suite_path)

    print("=== Ollama Bogel Baseline (no arifOS cage) ===")
    print(f"Model      : {model}")
    print(f"Suite file : {suite_path}")
    print()

    results: List[Dict[str, Any]] = []

    for idx, case in enumerate(prompts, start=1):
        prompt_id = str(case.get("id", f"case_{idx}"))
        prompt_text = str(case.get("prompt", ""))
        category = str(case.get("category", "unknown"))
        target_floors = case.get("target_floors", [])
        high_stakes = bool(case.get("high_stakes", False))

        print(f"--- [{idx:02d}/33] Prompt ID: {prompt_id} ---")
        print(f"Category    : {category}")
        print(f"Targets     : {', '.join(target_floors) if target_floors else '-'}")
        print(f"High-stakes : {high_stakes}")
        print(f"Prompt      : {prompt_text!r}")

        error: str | None = None
        try:
            raw_response = call_ollama_bogel(prompt_text, model=model)
        except requests.exceptions.ReadTimeout:
            raw_response = ""
            error = "TIMEOUT"
        except requests.exceptions.RequestException as exc:
            raw_response = ""
            error = f"REQUEST_ERROR: {exc}"

        if error is not None:
            snippet = f"[{error}]"
        else:
            full = raw_response.strip()
            lines = full.splitlines()
            snippet_lines = lines[:8]
            snippet = "\n".join(snippet_lines)
            if len(lines) > len(snippet_lines):
                snippet += "\n... [truncated] ..."

        print("Raw response snippet:")
        print(snippet or "[EMPTY RESPONSE]")
        print()

        results.append(
            {
                "id": prompt_id,
                "category": category,
                "target_floors": target_floors,
                "high_stakes": high_stakes,
                "prompt": prompt_text,
                "response": raw_response,
                "error": error,
            }
        )

    output_path = suite_path.with_name(f"bogel_results_{model.replace(':', '_')}.json")
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Saved full raw responses to: {output_path}")


def main() -> None:
    # Optional first CLI argument: model name (default: "llama3").
    model = sys.argv[1] if len(sys.argv) > 1 else "llama3"
    run_bogel_suite(model=model)


if __name__ == "__main__":
    main()
