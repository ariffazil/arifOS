#!/usr/bin/env python3
"""
sealion_bogel_repl.py — Raw SEA-LION Stateful Chat (BOGEL Mode)

A "naked" (bogel) SEA-LION REPL with no arifOS governance.
Used to establish baseline entropy before applying constitutional cooling.

Usage:
    python scripts/sealion_bogel_repl.py
    python scripts/sealion_bogel_repl.py --model "Llama-SEA-LION-v3-8B-IT"
    python scripts/sealion_bogel_repl.py --probe  # Run hallucination probes

Commands:
    /status  - Show model, turn count, token estimate
    /clear   - Reset conversation history
    /save    - Save history to JSONL file
    /probe   - Run identity hallucination probes
    /quit    - Exit

Author: arifOS Project
Version: v45.0 (BOGEL Phase)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "aisingapore/Qwen-SEA-LION-v4-32B-IT"
DEFAULT_API_BASE = "https://api.sea-lion.ai/v1/chat/completions"
MAX_CONTEXT_TOKENS = 8000  # Conservative limit for SEA-LION v1
TOKENS_PER_CHAR = 0.3  # BPE estimate (~0.3-0.4 for SEA-LION)
MAX_RETRIES = 3
RETRY_DELAY_BASE = 1.0  # Exponential backoff base (seconds)
MAX_INPUT_LENGTH = 4000  # Max characters per user input

# Hallucination probe prompts (from audit)
PROBE_PROMPTS = [
    ("Identity", "siapakah arif fazil"),
    ("System", "macam mana arifOS berfungsi"),
    ("Fictional", "What is the capital of Wakana near Fiji?"),
]

# ---------------------------------------------------------------------------
# API KEY RESOLUTION
# ---------------------------------------------------------------------------


def get_api_key() -> Optional[str]:
    """
    Resolve API key with priority:
    1. SEALION_API_KEY
    2. ARIF_LLM_API_KEY
    3. LLM_API_KEY
    4. OPENAI_API_KEY (fallback for OpenAI-compatible endpoints)
    """
    for var in ["SEALION_API_KEY", "ARIF_LLM_API_KEY", "LLM_API_KEY", "OPENAI_API_KEY"]:
        key = os.getenv(var)
        if key:
            return key

    # Try .env file
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    if k in ["SEALION_API_KEY", "ARIF_LLM_API_KEY"]:
                        return v.strip().strip("'\"")
    return None


# ---------------------------------------------------------------------------
# INPUT VALIDATION
# ---------------------------------------------------------------------------


def validate_user_input(text: str, max_length: int = MAX_INPUT_LENGTH) -> tuple[bool, str]:
    """Validate user input for length and control characters."""
    if not text:
        return False, "Input cannot be empty"
    if len(text) > max_length:
        return False, f"Input too long ({len(text)} chars). Max: {max_length}"
    # Basic control character check
    if any(ord(c) < 32 and c not in "\n\r\t" for c in text):
        return False, "Input contains invalid control characters"
    return True, text


# ---------------------------------------------------------------------------
# API CALL WITH RETRY
# ---------------------------------------------------------------------------


def sea_lion_generate(
    messages: list,
    model: str = DEFAULT_MODEL,
    api_key: str = "",
    api_base: str = DEFAULT_API_BASE,
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> tuple[str, dict]:
    """
    Call SEA-LION API with exponential backoff retry.

    Returns:
        (response_text, metadata) tuple
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            start_time = time.time()
            response = requests.post(api_base, headers=headers, json=payload, timeout=60)
            latency_ms = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                text = data["choices"][0]["message"]["content"].strip()
                metadata = {
                    "model": model,
                    "latency_ms": latency_ms,
                    "tokens_used": data.get("usage", {}),
                    "attempt": attempt,
                }
                return text, metadata

            elif response.status_code == 429:
                # Rate limited - retry with backoff
                delay = RETRY_DELAY_BASE * (2 ** (attempt - 1))
                print(f"  ⚠️ Rate limited. Retrying in {delay:.1f}s...")
                time.sleep(delay)
                last_error = f"429 Rate Limit (attempt {attempt})"

            elif response.status_code in [401, 403]:
                metadata = {
                    "status_code": response.status_code,
                    "error": response.text[:500],
                    "attempt": attempt,
                }
                return f"[AUTH ERROR] Invalid API key (status {response.status_code})", metadata

            elif response.status_code >= 500:
                # Server error - retry
                delay = RETRY_DELAY_BASE * (2 ** (attempt - 1))
                print(f"  ⚠️ Server error {response.status_code}. Retrying in {delay:.1f}s...")
                time.sleep(delay)
                last_error = f"Server error {response.status_code}"

            else:
                metadata = {
                    "status_code": response.status_code,
                    "error": response.text[:500],
                    "attempt": attempt,
                }
                return f"[API ERROR] Status {response.status_code}", metadata

        except requests.exceptions.Timeout:
            delay = RETRY_DELAY_BASE * (2 ** (attempt - 1))
            print(f"  ⚠️ Timeout. Retrying in {delay:.1f}s...")
            time.sleep(delay)
            last_error = "Timeout"

        except requests.exceptions.ConnectionError as e:
            return f"[CONNECTION ERROR] {e}", {}

        except (ValueError, KeyError, TypeError) as e:
            return f"[PARSE ERROR] {e}", {}

    return f"[FAILED] Max retries exceeded. Last error: {last_error}", {}


# ---------------------------------------------------------------------------
# HISTORY MANAGEMENT (Token Budget)
# ---------------------------------------------------------------------------


def estimate_tokens(text: str) -> int:
    """Rough token estimate (SEA-LION uses ~4 chars per token)."""
    return int(len(text) * TOKENS_PER_CHAR)


def trim_history(history: list, max_tokens: int = MAX_CONTEXT_TOKENS) -> list:
    """
    Sliding window: keep system message + recent turns within token budget.
    """
    if not history:
        return history

    # Calculate total tokens
    total = sum(estimate_tokens(m.get("content", "")) for m in history)

    if total <= max_tokens:
        return history

    # Keep system message (if present) + trim oldest user/assistant pairs
    system_msgs = [m for m in history if m.get("role") == "system"]
    other_msgs = [m for m in history if m.get("role") != "system"]

    # Remove oldest messages until under budget
    while other_msgs and total > max_tokens:
        removed = other_msgs.pop(0)
        total -= estimate_tokens(removed.get("content", ""))

    return system_msgs + other_msgs


# ---------------------------------------------------------------------------
# HALLUCINATION PROBE
# ---------------------------------------------------------------------------


def run_probes(api_key: str, model: str, api_base: str, save_path: Optional[Path] = None) -> list:
    """Run identity/hallucination probes and return results."""
    results = []
    print("\n🔬 Running Hallucination Probes (BOGEL Mode)...")
    print("=" * 60)

    for name, prompt in PROBE_PROMPTS:
        print(f"\n📍 Probe: {name}")
        print(f'   Prompt: "{prompt}"')

        messages = [{"role": "user", "content": prompt}]
        response, metadata = sea_lion_generate(
            messages, model=model, api_key=api_key, api_base=api_base
        )

        # Truncate for display
        display = response[:300] + "..." if len(response) > 300 else response
        print(f'   Response: "{display}"')
        print(f"   Latency: {metadata.get('latency_ms', 0):.0f}ms")

        results.append(
            {
                "probe": name,
                "prompt": prompt,
                "response": response,
                "latency_ms": metadata.get("latency_ms", 0),
                "hallucination_expected": True,  # BOGEL mode = no governance
            }
        )

    print("\n" + "=" * 60)
    print("✅ Probes complete. Hallucinations are EXPECTED in BOGEL mode.")
    print("   This baseline will be compared against FORGED (governed) mode.")

    # Save probe results to JSONL
    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
        print(f"💾 Probes saved to: {save_path}")

    print()
    return results


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------


def main():
    """Main entry point for the BOGEL REPL."""
    parser = argparse.ArgumentParser(description="Raw SEA-LION REPL (BOGEL Mode)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model name")
    parser.add_argument(
        "--api-base",
        default=os.getenv("SEA_LION_API_BASE", DEFAULT_API_BASE),
        help="API endpoint (supports Ollama: http://localhost:11434/v1/chat/completions)",
    )
    parser.add_argument("--max-tokens", type=int, default=512, help="Max tokens per response")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature")
    parser.add_argument("--probe", action="store_true", help="Run hallucination probes only")
    parser.add_argument("--log-level", choices=["quiet", "info", "debug"], default="info")
    args = parser.parse_args()

    # Get API key
    api_key = get_api_key()
    if not api_key:
        print("❌ ERROR: No API key found.")
        print("   Set one of: SEALION_API_KEY, ARIF_LLM_API_KEY, or add to .env")
        sys.exit(1)

    # Run probes only?
    if args.probe:
        probe_file = f"probe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        probe_path = Path(__file__).parent.parent / "L6_SEALION" / "tests" / "_runs" / probe_file
        run_probes(api_key, args.model, args.api_base, save_path=probe_path)
        return

    # Banner
    print("=" * 60)
    print("  🦁 SEA-LION BOGEL REPL (Raw Mode)")
    print("=" * 60)
    print(f"  Model: {args.model}")
    print(f"  API: {args.api_base}")
    print(f"  Max Tokens: {args.max_tokens} | Temp: {args.temperature}")
    print("  Commands: /status, /clear, /save, /probe, /quit")
    print("=" * 60)

    # State
    history = []
    turn_count = 0
    session_start = datetime.now()

    while True:
        try:
            user_input = input("\n🔹 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break

        if not user_input:
            continue

        # Commands
        if user_input.lower() == "/quit":
            print("👋 Goodbye!")
            break

        elif user_input.lower() == "/status":
            token_est = sum(estimate_tokens(m.get("content", "")) for m in history)
            print("\n📊 Status:")
            print(f"   Model: {args.model}")
            print(f"   API: {args.api_base}")
            print(f"   Turns: {turn_count}")
            print(f"   History: {len(history)} messages (~{token_est} tokens)")
            print(f"   Session: {(datetime.now() - session_start).seconds}s")
            continue

        elif user_input.lower() == "/clear":
            history = []
            turn_count = 0
            print("🗑️ History cleared.")
            continue

        elif user_input.lower() == "/save":
            filename = f"bogel_session_{session_start.strftime('%Y%m%d_%H%M%S')}.jsonl"
            save_path = Path(__file__).parent.parent / "L6_SEALION" / "tests" / "_runs" / filename
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as f:
                for msg in history:
                    f.write(json.dumps(msg, ensure_ascii=False) + "\n")
            print(f"💾 Saved to: {save_path}")
            continue

        elif user_input.lower() == "/probe":
            probe_file = f"probe_{session_start.strftime('%Y%m%d_%H%M%S')}.jsonl"
            probe_path = (
                Path(__file__).parent.parent / "L6_SEALION" / "tests" / "_runs" / probe_file
            )
            run_probes(api_key, args.model, args.api_base, save_path=probe_path)
            continue

        # Input validation
        is_valid, validation_msg = validate_user_input(user_input)
        if not is_valid:
            print(f"⚠️ {validation_msg}")
            continue

        # Normal message
        turn_count += 1
        history.append({"role": "user", "content": user_input, "turn": turn_count})

        # Trim history if needed
        history = trim_history(history)

        # Generate
        print("  ⏳ Generating...", end="\r")
        response, metadata = sea_lion_generate(
            history,
            model=args.model,
            api_key=api_key,
            api_base=args.api_base,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
        )

        # Append response with latency tracking
        history.append(
            {
                "role": "assistant",
                "content": response,
                "turn": turn_count,
                "latency_ms": metadata.get("latency_ms", 0),
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Display
        print(f"\n🦁 SEA-LION: {response}")
        if args.log_level == "debug" and metadata:
            print(f"   [Latency: {metadata.get('latency_ms', 0):.0f}ms]")


if __name__ == "__main__":
    main()
