#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEA-LION RAW REPL - Direct LLM interaction (NO governance)

Minimal interactive script for testing SEA-LION models without arifOS governance.
Use this for baseline testing, prompt engineering, or comparing with governed outputs.

Usage:
    python scripts/sealion_raw_repl.py

Environment Variables:
    SEALION_API_KEY - SEA-LION API key (required)
    SEALION_MODEL - Model ID (default: aisingapore/Gemma-SEA-LION-v4-27B-IT)

Commands:
    /model <name> - Switch model
    /temp <0.0-2.0> - Set temperature
    /max <tokens> - Set max tokens
    /clear - Clear conversation history
    /help - Show help
    /exit - Exit
"""

import os
import sys
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

try:
    from litellm import completion
except ImportError:
    print("❌ LiteLLM not installed!")
    print("\nInstall with: pip install litellm")
    sys.exit(1)


class RawREPL:
    """Simple RAW REPL for SEA-LION (no governance)."""

    def __init__(self):
        # API configuration
        self.api_key = (
            os.getenv("SEALION_API_KEY")
            or os.getenv("ARIF_LLM_API_KEY")
            or os.getenv("LLM_API_KEY")
        )

        if not self.api_key:
            print("❌ API Key not found!")
            print("\nSet environment variable:")
            print("  Windows: $env:SEALION_API_KEY = 'your-key'")
            print("  Linux/Mac: export SEALION_API_KEY='your-key'")
            sys.exit(1)

        # Model settings
        self.model = os.getenv("SEALION_MODEL", "aisingapore/Gemma-SEA-LION-v4-27B-IT")
        self.api_base = os.getenv("ARIF_LLM_API_BASE", "https://api.sea-lion.ai/v1")
        self.temperature = 0.7
        self.max_tokens = 512

        # Conversation history
        self.messages = []
        self.session_count = 0

    def print_banner(self):
        """Print REPL banner."""
        print("\n" + "=" * 70)
        print("🦁 SEA-LION RAW REPL — Direct LLM (No Governance) 🦁".center(70))
        print("=" * 70)
        print(f"\n📦 Model: {self.model}")
        print(f"🌐 API: {self.api_base}")
        print(f"🌡️  Temp: {self.temperature} | Max Tokens: {self.max_tokens}")
        print("\n💡 Commands: /model /temp /max /clear /help /exit")
        print("=" * 70 + "\n")

    def print_help(self):
        """Print help."""
        print("\n" + "─" * 70)
        print("COMMANDS:")
        print("  /model <name>    Switch model (e.g., /model aisingapore/Qwen-SEA-LION-v4-32B-IT)")
        print("  /temp <value>    Set temperature (0.0-2.0, default: 0.7)")
        print("  /max <tokens>    Set max tokens (default: 512)")
        print("  /clear           Clear conversation history")
        print("  /help            Show this help")
        print("  /exit            Exit REPL")
        print("─" * 70 + "\n")

    def call_llm(self, prompt: str) -> str:
        """Call SEA-LION API directly (no governance)."""
        # Add user message to history
        self.messages.append({"role": "user", "content": prompt})

        try:
            # Direct LiteLLM call (SEA-LION is OpenAI-compatible)
            response = completion(
                model=self.model,
                messages=self.messages,
                api_key=self.api_key,
                api_base=self.api_base,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=30,
                custom_llm_provider="openai",  # FIX: Tell LiteLLM this is OpenAI-compatible
            )

            # Extract response text
            assistant_message = response.choices[0].message.content

            # Add to history
            self.messages.append({"role": "assistant", "content": assistant_message})

            return assistant_message

        except Exception as e:
            return f"❌ API Error: {e}"

    def process_query(self, query: str):
        """Process user query and display response."""
        self.session_count += 1

        print(f"\n{'─' * 70}")
        print(f"🦁 Query #{self.session_count} | {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'─' * 70}")

        # Call LLM
        response = self.call_llm(query)

        # Display response
        print(f"\n💬 {response}\n")

    def run(self):
        """Run the REPL."""
        self.print_banner()

        while True:
            try:
                # Get user input
                user_input = input("🦁 > ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith('/'):
                    parts = user_input.split(maxsplit=1)
                    cmd = parts[0].lower()

                    if cmd == '/exit':
                        print("\n👋 Exiting RAW REPL.\n")
                        break

                    elif cmd == '/help':
                        self.print_help()

                    elif cmd == '/clear':
                        self.messages = []
                        self.session_count = 0
                        print("\n✅ Conversation history cleared.\n")

                    elif cmd == '/model':
                        if len(parts) > 1:
                            self.model = parts[1]
                            print(f"\n✅ Model switched to: {self.model}\n")
                        else:
                            print(f"\n📦 Current model: {self.model}")
                            print("Available models:")
                            print("  - aisingapore/Gemma-SEA-LION-v4-27B-IT (default)")
                            print("  - aisingapore/Qwen-SEA-LION-v4-32B-IT (flagship)")
                            print("  - aisingapore/Qwen-SEA-LION-v4-8B-VL (vision)")
                            print("  - aisingapore/Llama-SEA-LION-v3-70B-IT (large)\n")

                    elif cmd == '/temp':
                        if len(parts) > 1:
                            try:
                                temp = float(parts[1])
                                if 0.0 <= temp <= 2.0:
                                    self.temperature = temp
                                    print(f"\n✅ Temperature set to: {self.temperature}\n")
                                else:
                                    print("\n❌ Temperature must be between 0.0 and 2.0\n")
                            except ValueError:
                                print("\n❌ Invalid temperature value\n")
                        else:
                            print(f"\n🌡️  Current temperature: {self.temperature}\n")

                    elif cmd == '/max':
                        if len(parts) > 1:
                            try:
                                tokens = int(parts[1])
                                if 1 <= tokens <= 4096:
                                    self.max_tokens = tokens
                                    print(f"\n✅ Max tokens set to: {self.max_tokens}\n")
                                else:
                                    print("\n❌ Max tokens must be between 1 and 4096\n")
                            except ValueError:
                                print("\n❌ Invalid token count\n")
                        else:
                            print(f"\n🔢 Current max tokens: {self.max_tokens}\n")

                    else:
                        print(f"\n❌ Unknown command: {cmd}")
                        print("💡 Type /help for available commands\n")

                    continue

                # Process as query
                self.process_query(user_input)

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Type /exit to quit.\n")
            except EOFError:
                print("\n\n👋 Exiting RAW REPL.\n")
                break


def main():
    """Entry point."""
    repl = RawREPL()
    repl.run()


if __name__ == "__main__":
    main()
