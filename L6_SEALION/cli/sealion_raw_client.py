#!/usr/bin/env python3
"""
sealion_raw_client.py — Pure SEA-LION Client with MemOS Memory (RAW/BOGEL Mode)

A minimal, ungoverned SEA-LION client that serves as the foundation layer for
governed wrappers. Provides:
- Pure SEA-LION API calls (no arifOS governance)
- MemOS integration for chat history (cross-session memory)
- Web search tool support (Serper.dev)
- Retry logic with exponential backoff
- Token management

This is the single source of truth for SEA-LION API interactions.
Governed wrappers build on TOP of this client, not alongside it.

Usage:
    # As a library (for governance wrapper)
    from sealion_raw_client import RawSEALionClient

    client = RawSEALionClient(
        api_key=os.getenv("SEALION_API_KEY"),
        model="aisingapore/Qwen-SEA-LION-v4-32B-IT"
    )

    response = client.generate("Hello, how are you?")

    # Standalone REPL mode
    python scripts/sealion_raw_client.py
    python scripts/sealion_raw_client.py --no-memory  # Disable MemOS

Author: arifOS Project
Version: v45.0 (RAW Phase - Base Layer)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "aisingapore/Qwen-SEA-LION-v4-32B-IT"
DEFAULT_API_BASE = "https://api.sea-lion.ai/v1/chat/completions"
DEFAULT_MEMOS_BASE = "https://memos.memtensor.cn/api/openmem/v1"

MAX_CONTEXT_TOKENS = 8000  # Conservative limit for SEA-LION v4
TOKENS_PER_CHAR = 0.3  # BPE estimate (~0.3-0.4 for SEA-LION)
MAX_RETRIES = 3
RETRY_DELAY_BASE = 1.0  # seconds
MAX_INPUT_LENGTH = 4000  # characters

# Tool configuration
SERPER_API_BASE = "https://google.serper.dev/search"

# ---------------------------------------------------------------------------
# API KEY RESOLUTION
# ---------------------------------------------------------------------------


def get_api_key(key_name: str = "SEALION_API_KEY") -> Optional[str]:
    """
    Resolve API key with priority:
    1. Environment variable (key_name)
    2. Fallback to common alternatives
    3. .env file in parent directory
    """
    # Primary key
    key = os.getenv(key_name)
    if key:
        return key

    # Fallback keys for SEA-LION
    if key_name == "SEALION_API_KEY":
        for var in ["ARIF_LLM_API_KEY", "LLM_API_KEY", "OPENAI_API_KEY"]:
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
                    if k == key_name or (key_name == "SEALION_API_KEY" and k in ["ARIF_LLM_API_KEY"]):
                        return v.strip().strip("'\"")
    return None


# ---------------------------------------------------------------------------
# MEMOS CLIENT (Minimal Integration)
# ---------------------------------------------------------------------------


class SimpleMemOSClient:
    """
    Minimal MemOS client for chat history storage/retrieval.
    Avoids full dependency on MemOS SDK - only uses chat history API.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("MEMOS_BASE_URL") or DEFAULT_MEMOS_BASE
        self.api_key = api_key or os.getenv("MEMOS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "MemOS API key required. Set MEMOS_API_KEY environment variable."
            )
        self.headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }

    def add_messages(
        self,
        messages: List[Dict[str, Any]],
        user_id: str = "default",
        conversation_id: Optional[str] = None,
    ) -> bool:
        """Store messages to MemOS (chat history only)."""
        try:
            payload = {
                "user_id": user_id,
                "conversation_id": conversation_id or "default",
                "messages": messages,
            }
            # Note: Actual MemOS API may differ - adjust endpoint as needed
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=10,
            )
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️ MemOS store failed: {e}")
            return False

    def get_messages(
        self,
        user_id: str = "default",
        conversation_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Retrieve chat history from MemOS."""
        try:
            params = {
                "user_id": user_id,
                "conversation_id": conversation_id or "default",
                "limit": limit,
            }
            response = requests.get(
                f"{self.base_url}/messages",
                headers=self.headers,
                params=params,
                timeout=10,
            )
            if response.status_code == 200:
                return response.json().get("messages", [])
        except Exception as e:
            print(f"⚠️ MemOS retrieve failed: {e}")
        return []


# ---------------------------------------------------------------------------
# RAW SEA-LION CLIENT
# ---------------------------------------------------------------------------


class RawSEALionClient:
    """
    Pure ungoverned SEA-LION client with MemOS memory.

    This is the BASE LAYER for all SEA-LION interactions.
    No arifOS governance applied here - just raw API calls.
    """

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        api_base: str = DEFAULT_API_BASE,
        memos_client: Optional[SimpleMemOSClient] = None,
        enable_memory: bool = True,
        enable_tools: bool = True,
        serper_api_key: Optional[str] = None,
    ):
        """
        Initialize RAW client.

        Args:
            api_key: SEA-LION API key
            model: Model name
            api_base: API endpoint URL
            memos_client: Optional MemOS client (if None and enable_memory=True, creates one)
            enable_memory: Enable MemOS chat history
            enable_tools: Enable web search tool
            serper_api_key: Serper.dev API key (required if enable_tools=True)
        """
        self.api_key = api_key
        self.model = model
        self.api_base = api_base
        self.enable_memory = enable_memory
        self.enable_tools = enable_tools

        # MemOS setup
        if enable_memory:
            if memos_client:
                self.memos = memos_client
            else:
                try:
                    self.memos = SimpleMemOSClient()
                except ValueError:
                    print("⚠️ MemOS disabled (no API key). Chat history will be session-local only.")
                    self.enable_memory = False
                    self.memos = None
        else:
            self.memos = None

        # Tool setup
        self.serper_api_key = serper_api_key or os.getenv("SERPER_API_KEY")
        if enable_tools and not self.serper_api_key:
            print("⚠️ Web search disabled (no SERPER_API_KEY).")
            self.enable_tools = False

        # Session state
        self.conversation_id = f"sealion_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.user_id = "default"
        self.local_history: List[Dict] = []  # Fallback if MemOS unavailable

    def _call_api(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> Tuple[str, Dict]:
        """
        Call SEA-LION API with retry logic.

        Returns:
            (response_text, metadata) tuple
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                start_time = time.time()
                response = requests.post(
                    self.api_base, headers=headers, json=payload, timeout=60
                )
                latency_ms = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    data = response.json()
                    text = data["choices"][0]["message"]["content"].strip()
                    metadata = {
                        "model": self.model,
                        "latency_ms": latency_ms,
                        "tokens_used": data.get("usage", {}),
                        "attempt": attempt,
                        "status": "success",
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
                        "status": "auth_error",
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
                        "status": "api_error",
                    }
                    return f"[API ERROR] Status {response.status_code}", metadata

            except requests.exceptions.Timeout:
                delay = RETRY_DELAY_BASE * (2 ** (attempt - 1))
                print(f"  ⚠️ Timeout. Retrying in {delay:.1f}s...")
                time.sleep(delay)
                last_error = "Timeout"

            except requests.exceptions.ConnectionError as e:
                return f"[CONNECTION ERROR] {e}", {"status": "connection_error"}

            except (ValueError, KeyError, TypeError) as e:
                return f"[PARSE ERROR] {e}", {"status": "parse_error"}

        return f"[FAILED] Max retries exceeded. Last error: {last_error}", {"status": "retry_exhausted"}

    def _web_search(self, query: str) -> str:
        """Execute web search using Serper.dev API."""
        if not self.enable_tools or not self.serper_api_key:
            return "[Web search unavailable]"

        try:
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json",
            }
            payload = {"q": query, "num": 5}

            response = requests.post(
                SERPER_API_BASE, headers=headers, json=payload, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get("organic", [])[:3]:
                    title = item.get("title", "")
                    snippet = item.get("snippet", "")
                    link = item.get("link", "")
                    results.append(f"{title}\n{snippet}\nSource: {link}")
                return "\n\n".join(results) if results else "[No results found]"
            else:
                return f"[Search API error: {response.status_code}]"

        except Exception as e:
            return f"[Search failed: {e}]"

    def generate(
        self,
        query: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Generate response (RAW - no governance).

        Args:
            query: User input
            max_tokens: Max tokens in response
            temperature: Sampling temperature

        Returns:
            {
                "response": str,          # Generated text
                "metadata": dict,         # API metadata (latency, tokens, etc.)
                "history_length": int,    # Number of messages in context
                "memory_stored": bool,    # Whether stored to MemOS
            }
        """
        # Retrieve context from MemOS or local history
        if self.enable_memory and self.memos:
            history = self.memos.get_messages(
                user_id=self.user_id,
                conversation_id=self.conversation_id,
                limit=20,
            )
        else:
            history = self.local_history.copy()

        # Add user message
        user_msg = {"role": "user", "content": query}
        history.append(user_msg)

        # Trim if needed (token budget)
        history = self._trim_history(history)

        # Call API
        response_text, metadata = self._call_api(
            history, max_tokens=max_tokens, temperature=temperature
        )

        # Add assistant response to history
        assistant_msg = {
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now().isoformat(),
        }
        history.append(assistant_msg)

        # Store to MemOS or local history
        memory_stored = False
        if self.enable_memory and self.memos:
            memory_stored = self.memos.add_messages(
                messages=[user_msg, assistant_msg],
                user_id=self.user_id,
                conversation_id=self.conversation_id,
            )
        else:
            self.local_history.extend([user_msg, assistant_msg])

        return {
            "response": response_text,
            "metadata": metadata,
            "history_length": len(history),
            "memory_stored": memory_stored,
        }

    def _trim_history(
        self, history: List[Dict], max_tokens: int = MAX_CONTEXT_TOKENS
    ) -> List[Dict]:
        """Sliding window: keep recent turns within token budget."""
        total = sum(self._estimate_tokens(m.get("content", "")) for m in history)

        if total <= max_tokens:
            return history

        # Keep system message (if present) + trim oldest pairs
        system_msgs = [m for m in history if m.get("role") == "system"]
        other_msgs = [m for m in history if m.get("role") != "system"]

        while other_msgs and total > max_tokens:
            removed = other_msgs.pop(0)
            total -= self._estimate_tokens(removed.get("content", ""))

        return system_msgs + other_msgs

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimate (SEA-LION uses ~3-4 chars per token)."""
        return int(len(text) * TOKENS_PER_CHAR)

    def clear_history(self):
        """Clear session history (local only - MemOS data persists)."""
        self.local_history = []
        print("🗑️ Local session history cleared.")


# ---------------------------------------------------------------------------
# STANDALONE REPL (For Testing)
# ---------------------------------------------------------------------------


def main():
    """Standalone REPL mode for testing RAW client."""
    parser = argparse.ArgumentParser(description="RAW SEA-LION Client with MemOS")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model name")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="API endpoint")
    parser.add_argument("--no-memory", action="store_true", help="Disable MemOS")
    parser.add_argument("--no-tools", action="store_true", help="Disable web search")
    parser.add_argument("--max-tokens", type=int, default=512, help="Max tokens")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature")
    args = parser.parse_args()

    # Get API key
    api_key = get_api_key("SEALION_API_KEY")
    if not api_key:
        print("❌ ERROR: No SEA-LION API key found.")
        print("   Set one of: SEALION_API_KEY, ARIF_LLM_API_KEY, or add to .env")
        sys.exit(1)

    # Create client
    try:
        client = RawSEALionClient(
            api_key=api_key,
            model=args.model,
            api_base=args.api_base,
            enable_memory=not args.no_memory,
            enable_tools=not args.no_tools,
        )
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize client: {e}")
        sys.exit(1)

    # Banner
    print("=" * 60)
    print("  🦁 RAW SEA-LION Client (BOGEL Mode)")
    print("=" * 60)
    print(f"  Model: {args.model}")
    print(f"  API: {args.api_base}")
    print(f"  Memory: {'MemOS' if client.enable_memory else 'Local only'}")
    print(f"  Tools: {'Web search' if client.enable_tools else 'Disabled'}")
    print("  Commands: /status, /clear, /quit")
    print("=" * 60)

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
            print("\n📊 Status:")
            print(f"   Model: {client.model}")
            print(f"   Conversation ID: {client.conversation_id}")
            print(f"   Turns: {turn_count}")
            print(f"   Local history: {len(client.local_history)} messages")
            print(f"   Session: {(datetime.now() - session_start).seconds}s")
            continue

        elif user_input.lower() == "/clear":
            client.clear_history()
            turn_count = 0
            continue

        # Generate
        turn_count += 1
        print("  ⏳ Generating...", end="\r")
        result = client.generate(
            user_input, max_tokens=args.max_tokens, temperature=args.temperature
        )

        # Display
        print(f"\n🦁 SEA-LION: {result['response']}")
        print(
            f"   [Latency: {result['metadata'].get('latency_ms', 0):.0f}ms | "
            f"History: {result['history_length']} msgs | "
            f"Memory: {'✓' if result['memory_stored'] else '✗'}]"
        )


if __name__ == "__main__":
    main()
