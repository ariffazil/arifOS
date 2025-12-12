#!/usr/bin/env python3
"""
ollama_redteam_suite_v37.py

Run a 33-prompt red-team suite against a local Ollama model under the
arifOS v37 constitutional cage.

Prompts are defined in JSON:
    scripts/test_suite_v37.json

For each prompt, this script:
  - Builds grounding context via arifos_core.context_injection.build_system_context
  - Calls Ollama (llama3 by default) via scripts.test_ollama_v37.call_ollama
  - Runs the response through cage_llm_response (full v37 pipeline)
  - Prints verdict, stage trace, floor failures, and final response snippet.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List
import sys
from arifos_core.context_injection import build_system_context
from scripts.arifos_caged_llm_demo import cage_llm_response
from scripts.test_ollama_v37 import call_ollama


def load_suite(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("test_suite_v37.json must contain a list of prompts")
    return data


def _safe_print(text: str) -> None:
    """
    Print text safely even when the console encoding cannot represent all
    Unicode characters (e.g. Windows cp1252 vs Greek letters).
    """
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        print(text.encode(encoding, errors="replace").decode(encoding))


def run_suite(model: str = "llama3") -> None:
    suite_path = Path(__file__).with_name("test_suite_v37.json")

    # For this red-team harness we want to observe core floors + @EYE without
    # W@W (@PROMPT/@WELL) overriding the verdict. The pipeline reads this flag
    # in stage_888_judge.
    os.environ["ARIFOS_DISABLE_WAW"] = "1"

    prompts = load_suite(suite_path)

    print("=== arifOS v37 + Ollama Red-Team Suite (33 prompts) ===")
    print(f"Model: {model}")
    print(f"Suite file: {suite_path}")
    print()

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

        grounding_context = build_system_context(prompt_text)
        system_prompt: str | None = None
        if grounding_context:
            system_prompt = (
                "You are a helpful assistant operating under the arifOS governance "
                "kernel.\n"
                f"{grounding_context}"
            )

        result = cage_llm_response(
            prompt=prompt_text,
            call_model=lambda messages, m=model: call_ollama(messages, model=m),
            high_stakes=high_stakes,
            system_prompt=system_prompt,
        )

        print("Verdict     :", result.verdict)
        print("Stage trace :", " -> ".join(result.stage_trace))
        print("Floor fails :", result.floor_failures)

        # Print a short snippet of the final response to keep logs readable.
        final = result.final_response.strip()
        lines = final.splitlines()
        snippet_lines = lines[:8]
        snippet = "\n".join(snippet_lines)
        if len(lines) > len(snippet_lines):
            snippet += "\n... [truncated] ..."

        print("Final response snippet:")
        _safe_print(snippet)
        print()


def main() -> None:
    run_suite()


if __name__ == "__main__":
    main()
