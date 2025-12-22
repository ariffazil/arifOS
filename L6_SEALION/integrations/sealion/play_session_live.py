"""
arifOS Interactive LIVE Session (Real SEA-LION API)
DITEMPA BUKAN DIBERI - Forged, not given.

Type a prompt. Get a real SEA-LION response with F1/F9 governance.
Requires: SEALION_API_KEY environment variable or .env file.

Layer: L7 (SEA-LION Federation)
Constitutional Law: v44 (TEARFRAME Physics)
Floors Enforced: F1 (Amanah), F9 (C_dark/Toxicity), Physics (Rate/Burst)

Usage:
    # Set API key first
    set SEALION_API_KEY=your-api-key-here

    # Then run
    python integrations/sealion/play_session_live.py

Commands:
    Type any prompt to chat with SEA-LION
    'exit' or 'quit' to end session
    'help' to show commands
    'model' to show/change model
    'mock' to switch to mock mode (no API)

Available Models:
    1. aisingapore/Llama-SEA-LION-v3-70B-IT (default)
    2. aisingapore/Llama-SEA-LION-v3.5-70B-R
    3. aisingapore/Gemma-SEA-LION-v4-27B-IT
    4. aisingapore/Qwen-SEA-LION-v4-32B-IT

Version: v44.0.0
Forged: 2025-12-22
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure arifOS is importable
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Try to load .env file if python-dotenv available
try:
    from dotenv import load_dotenv

    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

from integrations.sealion.engine import (
    SealionEngine,
    SealionConfig,
    SealionResult,
    SEALION_MODELS,
)

# Import toxicity detector for F9 input checks
try:
    from integrations.sealion.test_sgtoxic_spin import ToxicityDetector

    TOXICITY_AVAILABLE = True
except ImportError:
    TOXICITY_AVAILABLE = False


# Current session state
class SessionState:
    def __init__(self):
        self.model = SEALION_MODELS[0]
        self.engine = None
        self.mock_mode = False
        self.conversation = []


STATE = SessionState()


def show_banner():
    """Display session banner."""
    print("\n")
    print("=" * 70)
    print("    SEA-LION APEX PRIME: LIVE API Session")
    print("    Constitutional Governance v44.0.0 (TEARFRAME)")
    print("=" * 70)
    print("\n    Floors: F1 (Amanah) + F9 (Toxicity) + Physics Layers")
    print("    Mode: LIVE API (Requires SEALION_API_KEY)")
    print("\n    Commands:")
    print("      - Type any prompt to chat with SEA-LION")
    print("      - 'help'   - Show all commands")
    print("      - 'model'  - Show/change model")
    print("      - 'mock'   - Switch to mock mode")
    print("      - 'clear'  - Clear conversation history")
    print("      - 'exit'   - End session")
    print("=" * 70)


def show_help():
    """Display help information."""
    print("\n" + "-" * 70)
    print("COMMANDS:")
    print("-" * 70)
    print("  help     - Show this help")
    print("  model    - Show current model or change it")
    print("  model N  - Switch to model N (1-4)")
    print("  mock     - Switch to mock mode (no API calls)")
    print("  live     - Switch back to live API mode")
    print("  clear    - Clear conversation history")
    print("  history  - Show conversation history")
    print("  exit     - End session")
    print("\n" + "-" * 70)
    print("AVAILABLE MODELS:")
    print("-" * 70)
    for i, model in enumerate(SEALION_MODELS[:4], 1):
        marker = " [CURRENT]" if model == STATE.model else ""
        print(f"  {i}. {model}{marker}")
    print("-" * 70)


def show_models():
    """Display available models."""
    print("\n" + "-" * 70)
    print("AVAILABLE MODELS:")
    print("-" * 70)
    for i, model in enumerate(SEALION_MODELS[:4], 1):
        marker = " [CURRENT]" if model == STATE.model else ""
        print(f"  {i}. {model}{marker}")
    print("\nTo change: 'model N' (e.g., 'model 2')")
    print("-" * 70)


def change_model(model_num: int):
    """Change the current model."""
    if 1 <= model_num <= 4:
        STATE.model = SEALION_MODELS[model_num - 1]
        STATE.engine = None  # Reset engine
        print(f"\n[OK] Switched to: {STATE.model}")
    else:
        print(f"\n[X] Invalid model number. Use 1-4.")


def check_toxicity(text: str) -> tuple[bool, list[str]]:
    """Check text for toxicity using F9 detector."""
    if not TOXICITY_AVAILABLE:
        return False, []

    result = ToxicityDetector.check(text)
    is_toxic = result.get("is_toxic", False)
    reasons = result.get("matches", [])
    return is_toxic, reasons


def init_engine() -> bool:
    """Initialize the SEA-LION engine."""
    if STATE.mock_mode:
        print("\n[MOCK MODE] Using mock engine (no API calls)")
        return True

    api_key = os.environ.get("SEALION_API_KEY")
    if not api_key:
        print("\n[X] ERROR: SEALION_API_KEY not set!")
        print("    Set it with: set SEALION_API_KEY=your-key")
        print("    Or create a .env file with: SEALION_API_KEY=your-key")
        print("\n    Switching to mock mode...")
        STATE.mock_mode = True
        return True

    try:
        config = SealionConfig(model=STATE.model)
        STATE.engine = SealionEngine(api_key=api_key, config=config)
        print(f"\n[OK] Connected to SEA-LION API")
        print(f"    Model: {STATE.model}")
        return True
    except Exception as e:
        print(f"\n[X] Failed to initialize engine: {e}")
        print("    Switching to mock mode...")
        STATE.mock_mode = True
        return True


def process_prompt(prompt: str) -> dict:
    """Process user prompt through governance pipeline."""
    print("\n" + "=" * 70)
    print("GOVERNANCE PIPELINE")
    print("=" * 70)

    # STEP 1: Check INPUT for toxicity (F9)
    print("\n[F9 CHECK] Scanning input for toxicity...")
    is_toxic, toxic_reasons = check_toxicity(prompt)

    if is_toxic:
        print(f"    VOID: Toxic content detected")
        for reason in toxic_reasons[:3]:
            print(f"    - {reason}")
        return {
            "verdict": "VOID",
            "reason": "F9(toxicity)",
            "blocked": True,
            "response": "[arifOS VETO] VOID: Input contains toxic content.",
        }
    else:
        print("    PASS: No toxicity detected")

    # STEP 2: Call SEA-LION API (or mock)
    print("\n[SEA-LION] Generating response...")

    if STATE.mock_mode:
        # Mock response
        print("    [MOCK MODE]")
        response = "This is a mock SEA-LION response. Constitutional governance active."
        amanah_blocked = False
        amanah_violations = []
    else:
        # Real API call
        if STATE.engine is None:
            if not init_engine():
                return {
                    "verdict": "SABAR",
                    "reason": "engine_init_failed",
                    "blocked": True,
                    "response": "[arifOS] Failed to initialize engine.",
                }

        try:
            result: SealionResult = STATE.engine.generate(prompt)
            response = result.response
            amanah_blocked = result.amanah_blocked
            amanah_violations = result.amanah_violations

            # Store in conversation history
            STATE.conversation.append({"role": "user", "content": prompt})
            STATE.conversation.append({"role": "assistant", "content": response})

        except Exception as e:
            print(f"    [X] API Error: {e}")
            return {
                "verdict": "SABAR",
                "reason": f"api_error: {e}",
                "blocked": True,
                "response": f"[arifOS] API error: {e}",
            }

    # STEP 3: Check response with F1 (Amanah) - already done by SealionEngine
    print("\n[F1 CHECK] Amanah (destructive patterns)...")

    if amanah_blocked:
        print(f"    VOID: Destructive patterns detected")
        for v in amanah_violations[:3]:
            print(f"    - {v[:60]}...")
        return {
            "verdict": "VOID",
            "reason": "F1(amanah)",
            "blocked": True,
            "response": "[arifOS VETO] VOID: Response contained destructive patterns.",
            "violations": amanah_violations,
        }
    else:
        print("    PASS: No destructive patterns")

    # STEP 4: Check OUTPUT for toxicity (F9)
    print("\n[F9 CHECK] Scanning output for toxicity...")
    is_toxic_out, toxic_reasons_out = check_toxicity(response)

    if is_toxic_out:
        print(f"    VOID: Toxic content in response")
        for reason in toxic_reasons_out[:3]:
            print(f"    - {reason}")
        return {
            "verdict": "VOID",
            "reason": "F9(toxicity_output)",
            "blocked": True,
            "response": "[arifOS VETO] VOID: Response contains toxic content.",
        }
    else:
        print("    PASS: No toxicity detected")

    # All checks passed
    print("\n[VERDICT]: SEAL")
    return {
        "verdict": "SEAL",
        "blocked": False,
        "response": response,
    }


def interactive_mode():
    """Main interactive loop."""
    show_banner()

    # Initialize engine
    if not init_engine():
        print("[X] Failed to start. Exiting.")
        return

    while True:
        try:
            print("\n")
            mode_indicator = "[MOCK]" if STATE.mock_mode else "[LIVE]"
            user_input = input(f"{mode_indicator} You > ").strip()

            if not user_input:
                continue

            # Handle commands
            cmd = user_input.lower()

            if cmd in ("exit", "quit", "q"):
                print("\n[SESSION END] Maruah protected. DITEMPA BUKAN DIBERI.")
                break

            if cmd == "help":
                show_help()
                continue

            if cmd == "model":
                show_models()
                continue

            if cmd.startswith("model "):
                try:
                    num = int(cmd.split()[1])
                    change_model(num)
                except (ValueError, IndexError):
                    print("[X] Usage: model N (where N is 1-4)")
                continue

            if cmd == "mock":
                STATE.mock_mode = True
                STATE.engine = None
                print("\n[OK] Switched to MOCK mode")
                continue

            if cmd == "live":
                STATE.mock_mode = False
                STATE.engine = None
                init_engine()
                continue

            if cmd == "clear":
                STATE.conversation = []
                print("\n[OK] Conversation history cleared")
                continue

            if cmd == "history":
                if not STATE.conversation:
                    print("\n[No conversation history]")
                else:
                    print("\n" + "-" * 70)
                    print("CONVERSATION HISTORY:")
                    print("-" * 70)
                    for msg in STATE.conversation[-10:]:  # Last 10 messages
                        role = msg["role"].upper()
                        content = msg["content"][:100]
                        print(f"  [{role}]: {content}...")
                    print("-" * 70)
                continue

            # Process as chat prompt
            result = process_prompt(user_input)

            # Display result
            print("\n" + "-" * 70)
            print(f"VERDICT: {result['verdict']}")

            if result.get("blocked"):
                print(f"STATUS: BLOCKED")
                reason = result.get("reason", "constitutional_violation")
                print(f"FLOOR: {reason}")
                print(f"\nRESPONSE:\n{result['response']}")
            else:
                print(f"STATUS: APPROVED")
                print(f"\nRESPONSE:\n{result['response']}")

            print("-" * 70)

        except KeyboardInterrupt:
            print("\n\n[INTERRUPTED] Session ended by user.")
            break
        except EOFError:
            print("\n\n[EOF] Session ended.")
            break


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    interactive_mode()
