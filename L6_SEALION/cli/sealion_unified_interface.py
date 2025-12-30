#!/usr/bin/env python3
"""
sealion_unified_interface_v2.py — Unified Interface (Phase 3: Refactored)

Clean layered architecture using RAW + Governed clients.
NO code duplication - all API/governance logic delegated to Phase 1 + 2.

Features:
- /both mode: Side-by-side RAW vs GOVERNED comparison
- Trinity Display: ASI (Ω) / AGI (Δ) / APEX (Ψ) modes
- Gradio UI + REPL modes
- Session statistics and contrast metrics
- Zero code duplication (DRY principle enforced)

Architecture:
  Layer 3 (THIS FILE): UI/REPL + /both mode + Trinity Display
    ↓ delegates to
  Layer 2 (Phase 2): GovernedSEALionClient (governance wrapper)
    ↓ delegates to
  Layer 1 (Phase 1): RawSEALionClient (API, MemOS, tools)

Usage:
    # UI Mode (Gradio)
    python L6_SEALION/cli/sealion_unified_interface.py

    # REPL Mode
    python L6_SEALION/cli/sealion_unified_interface.py --cli

    # Both modes with comparison enabled
    python L6_SEALION/cli/sealion_unified_interface.py --comparison

Commands:
    /both    - Toggle side-by-side RAW vs GOVERNED comparison
    /asi     - ASI (Ω) Guardian mode: Clean output only
    /agi     - AGI (Δ) Architect mode: + GENIUS metrics
    /apex    - APEX (Ψ) Judge mode: + Full forensics
    /stats   - Show session statistics
    /clear   - Clear history
    /quit    - Exit (REPL mode)

Author: arifOS Project
Version: v45.0 (Phase 3 - Layered Architecture)
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import Phase 1: RAW client (same folder)
try:
    from sealion_raw_client import RawSEALionClient
except ImportError:
    print("[ERROR] ERROR: Phase 1 client not found.")
    print("   Ensure L6_SEALION/cli/sealion_raw_client.py exists.")
    sys.exit(1)

# Import Phase 2: Governance wrapper (same folder)
try:
    from sealion_governed_client import GovernedSEALionClient
except ImportError as e:
    print("[WARN] Phase 2 client failed to import (likely litellm/httpx import weight).")
    print(f"       Error: {e}")
    print("       UI/REPL will still start, but governed features may be unavailable.")
    GovernedSEALionClient = None

# Try to import Gradio (for UI mode)
try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False
    print("[WARN] Gradio unavailable - UI mode disabled (install: pip install gradio)")

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "aisingapore/Qwen-SEA-LION-v4-32B-IT"
DEFAULT_API_BASE = "https://api.sea-lion.ai/v1"

# Display modes
DISPLAY_MODE_ASI = "ASI"    # Ω Guardian (clean output)
DISPLAY_MODE_AGI = "AGI"    # Δ Architect (+ GENIUS)
DISPLAY_MODE_APEX = "APEX"  # Ψ Judge (+ full forensics)

# ---------------------------------------------------------------------------
# TRINITY DISPLAY FORMATTERS
# ---------------------------------------------------------------------------


def format_asi(result: Dict[str, Any]) -> str:
    """
    ASI (Ω) Guardian Mode: Clean output only.

    "The GUARDIAN speaks truth, plainly."
    """
    return result["response"]


def format_agi(result: Dict[str, Any]) -> str:
    """
    AGI (Δ) Architect Mode: + GENIUS metrics.

    "The ARCHITECT shows the structure."
    """
    output = result["response"]

    if result.get("genius"):
        genius = result["genius"]
        output += f"""

─────────────────────────────────────────────────────────
ΔΩΨ TRINITY METRICS (AGI Architect Mode)
─────────────────────────────────────────────────────────
Δ (Delta/Clarity):    {genius.get('G', 0):.3f}  — Genius Index
Ω (Omega/Empathy):    {genius.get('C_dark', 0):.3f}  — Dark Cleverness (lower is better)
Ψ (Psi/Vitality):     {genius.get('Psi', 0):.3f}  — System Health

Verdict: {result.get('verdict', 'UNKNOWN')} | Lane: {result.get('lane', 'UNKNOWN')}
"""

    return output


def format_apex(result: Dict[str, Any]) -> str:
    """
    APEX (Ψ) Judge Mode: + Full forensics.

    "The JUDGE reveals all evidence."
    """
    output = result["response"]

    output += f"""

═════════════════════════════════════════════════════════
APEX FORENSICS (Ψ Judge Mode)
═════════════════════════════════════════════════════════
Verdict: {result.get('verdict', 'UNKNOWN')} | Lane: {result.get('lane', 'UNKNOWN')}

─────────────────────────────────────────────────────────
Constitutional Floors (9):
─────────────────────────────────────────────────────────
"""

    if result.get("metrics"):
        metrics = result["metrics"]
        output += f"""  F1 Amanah (Integrity):     {metrics.get('amanah', 'N/A')}
  F2 Truth:                  {metrics.get('truth', 0):.3f}
  F3 DeltaS (Clarity):       {metrics.get('delta_s', 0):.3f}
  F4 Peace² (Stability):     {metrics.get('peace_squared', 0):.3f}
  F5 κᵣ (Empathy):           {metrics.get('kappa_r', 0):.3f}
  F6 Ω₀ (Humility):          {metrics.get('omega_0', 0):.3f}
  F7 RASA (Felt-Care):       {metrics.get('rasa', 'N/A')}
  F8 Tri-Witness:            {metrics.get('tri_witness', 0):.3f}
  F9 Anti-Hantu:             {'[OK] PASS' if not result.get('anti_hantu_violations') else '✗ FAIL'}
"""

    if result.get("genius"):
        genius = result["genius"]
        output += f"""
─────────────────────────────────────────────────────────
GENIUS Metrics (Derived):
─────────────────────────────────────────────────────────
  G (Genius Index):          {genius.get('G', 0):.3f}  (SEAL ≥0.8, VOID <0.5)
  C_dark (Dark Cleverness):  {genius.get('C_dark', 0):.3f}  (SEAL <0.3, HAZARD ≥0.6)
  Psi (Vitality):            {genius.get('Psi', 0):.3f}  (SEAL ≥1.0, SABAR <0.95)
  TP (Truth Polarity):       {genius.get('TP', 'N/A')}
"""

    if result.get("raw_response"):
        raw_preview = result["raw_response"][:150] + "..." if len(result["raw_response"]) > 150 else result["raw_response"]
        output += f"""
─────────────────────────────────────────────────────────
RAW Response (Ungoverned):
─────────────────────────────────────────────────────────
{raw_preview}
"""

    output += "═════════════════════════════════════════════════════════\n"

    return output


def format_comparison(raw_result: Dict, governed_result: Dict) -> str:
    """
    Format side-by-side RAW vs GOVERNED comparison (/both mode).

    Shows contrast metrics and constitutional improvements.
    """
    raw_resp = raw_result["response"]
    gov_resp = governed_result["response"]

    # Compute contrast metrics
    verbosity_reduction = len(raw_resp) - len(gov_resp)
    verdict = governed_result.get("verdict", "UNKNOWN")
    lane = governed_result.get("lane", "UNKNOWN")

    output = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║  RAW (BOGEL) vs GOVERNED (FORGE) Comparison — /both Mode                 ║
╠══════════════════════════════════════════════════════════════════════════╣

┌─ RAW OUTPUT (Ungoverned) ─────────────────────────────────────────────────┐
│
│ {raw_resp}
│
│ Chars: {len(raw_resp)} | Latency: {raw_result.get('metadata', {}).get('latency_ms', 0):.0f}ms
└────────────────────────────────────────────────────────────────────────────┘

┌─ GOVERNED OUTPUT (Constitutional) ────────────────────────────────────────┐
│
│ {gov_resp}
│
│ Chars: {len(gov_resp)} | Verdict: {verdict} | Lane: {lane}
"""

    if governed_result.get("genius"):
        genius = governed_result["genius"]
        output += f"""│ G: {genius.get('G', 0):.2f} | C_dark: {genius.get('C_dark', 0):.2f} | Psi: {genius.get('Psi', 0):.2f}
"""

    output += "└────────────────────────────────────────────────────────────────────────────┘\n"

    output += f"""
┌─ CONTRAST METRICS ────────────────────────────────────────────────────────┐
│ Verbosity Reduction: {verbosity_reduction:+d} chars ({verbosity_reduction / max(len(raw_resp), 1) * 100:+.1f}%)
│ Constitutional Action: {verdict}
│ Lane Classification: {lane}
"""

    if governed_result.get("metrics"):
        floors_passing = sum(1 for v in governed_result["metrics"].values() if (isinstance(v, bool) and v) or (isinstance(v, (int, float)) and v > 0))
        output += f"""│ Floors Passing: {floors_passing} / 9
"""

    if governed_result.get("anti_hantu_violations"):
        output += f"""│ [WARN] Anti-Hantu Violations: {len(governed_result["anti_hantu_violations"])}
"""

    output += "└────────────────────────────────────────────────────────────────────────────┘\n"
    output += "╚══════════════════════════════════════════════════════════════════════════╝\n"

    return output


# ---------------------------------------------------------------------------
# UNIFIED INTERFACE (Layer 3)
# ---------------------------------------------------------------------------


class UnifiedInterface:
    """
    Unified UI/REPL using RAW + Governed clients (Phase 3).

    Zero code duplication - all logic delegated to Phase 1 + 2.
    """

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        api_base: str = DEFAULT_API_BASE,
        enable_memory: bool = True,
        enable_tools: bool = True,
        enable_comparison: bool = False,
    ):
        """
        Initialize unified interface.

        Args:
            api_key: SEA-LION API key
            model: Model name
            api_base: API base URL
            enable_memory: Enable MemOS chat history
            enable_tools: Enable web search tool
            enable_comparison: Start with /both mode enabled
        """
        # Create RAW client (Phase 1)
        print("[INFO] Initializing RAW client (Phase 1)...")
        self.raw = RawSEALionClient(
            api_key=api_key,
            model=model,
            api_base=api_base,
            enable_memory=enable_memory,
            enable_tools=enable_tools,
        )

        # Create Governed client (Phase 2 wraps Phase 1)
        self.governed = None
        if GovernedSEALionClient:
            print("[INFO] Initializing Governance wrapper (Phase 2)...")
            self.governed = GovernedSEALionClient(
                raw_client=self.raw,
                enable_waw=True,
                enable_memory=True,
                enable_session_physics=True,
            )
        else:
            print("[WARN] Governance wrapper unavailable; running RAW-only.")

        # Display state
        self.display_mode = DISPLAY_MODE_ASI  # Default: ASI (clean output)
        self.comparison_mode = enable_comparison  # /both toggle

        # Session state
        self.session_start = datetime.now()

        print(f"✅ Unified Interface initialized (Display: {self.display_mode}, Comparison: {self.comparison_mode})")

    def generate(self, query: str) -> str:
        """
        Generate response based on current mode.

        Returns formatted output (ready for display).
        """
        if self.comparison_mode:
            return self._generate_comparison(query)
        else:
            return self._generate_governed(query)

    def _generate_governed(self, query: str) -> str:
        """Generate governed response only (default)."""
        if not self.governed:
            return "[WARN] Governed client unavailable; RAW-only mode."

        result = self.governed.generate(query)

        if self.display_mode == DISPLAY_MODE_ASI:
            return format_asi(result)
        elif self.display_mode == DISPLAY_MODE_AGI:
            return format_agi(result)
        elif self.display_mode == DISPLAY_MODE_APEX:
            return format_apex(result)
        else:
            return result["response"]  # Fallback

    def _generate_comparison(self, query: str) -> str:
        """Generate side-by-side RAW vs GOVERNED comparison."""
        # Get RAW response (Phase 1)
        raw_result = self.raw.generate(query)

        # Get GOVERNED response (Phase 2)
        if not self.governed:
            return format_comparison(raw_result, {"response": "[WARN] Governed client unavailable."})
        governed_result = self.governed.generate(query)

        # Format comparison
        return format_comparison(raw_result, governed_result)

    def handle_command(self, cmd: str) -> str:
        """
        Handle special commands.

        Returns status message.
        """
        cmd_lower = cmd.lower().strip()

        if cmd_lower == "/both":
            self.comparison_mode = not self.comparison_mode
            status = "ON" if self.comparison_mode else "OFF"
            return f"🔄 Comparison mode: {status}"

        elif cmd_lower == "/asi":
            self.display_mode = DISPLAY_MODE_ASI
            return f"🔄 Display mode: ASI (Ω) Guardian — Clean output only"

        elif cmd_lower == "/agi":
            self.display_mode = DISPLAY_MODE_AGI
            return f"🔄 Display mode: AGI (Δ) Architect — + GENIUS metrics"

        elif cmd_lower == "/apex":
            self.display_mode = DISPLAY_MODE_APEX
            return f"🔄 Display mode: APEX (Ψ) Judge — + Full forensics"

        elif cmd_lower == "/stats":
            return self._format_stats()

        elif cmd_lower == "/clear":
            self.raw.clear_history()
            return "🗑️ History cleared."

        elif cmd_lower == "/quit":
            return "quit"  # Signal to exit

        else:
            return f"[ERROR] Unknown command: {cmd}\n   Available: /both, /asi, /agi, /apex, /stats, /clear, /quit"

    def _format_stats(self) -> str:
        """Format session statistics."""
        governed_stats = self.governed.get_stats()
        uptime = (datetime.now() - self.session_start).seconds

        output = f"""
╔══════════════════════════════════════════════════════════════╗
║  SESSION STATISTICS                                          ║
╠══════════════════════════════════════════════════════════════╣
│ Session ID: {governed_stats.get('session_id', 'N/A')}
│ Uptime: {uptime}s
│ Turns: {governed_stats.get('turns', 0)}
│
│ Verdicts:
"""

        for verdict, count in governed_stats.get("verdicts", {}).items():
            if count > 0:
                output += f"│   {verdict}: {count}\n"

        output += "│\n│ Lanes:\n"

        for lane, count in governed_stats.get("lanes", {}).items():
            if count > 0:
                output += f"│   {lane}: {count}\n"

        output += f"""│
│ Display Mode: {self.display_mode}
│ Comparison Mode: {'ON' if self.comparison_mode else 'OFF'}
╚══════════════════════════════════════════════════════════════╝
"""

        return output


# ---------------------------------------------------------------------------
# GRADIO UI (Web Interface)
# ---------------------------------------------------------------------------


def create_gradio_ui(interface: UnifiedInterface):
    """Create Gradio web interface."""
    if not GRADIO_AVAILABLE:
        print("[ERROR] Gradio not available. Cannot create UI.")
        return None

    def respond(message: str, history: List) -> str:
        """Gradio chat handler."""
        # Check for commands
        if message.startswith("/"):
            result = interface.handle_command(message)
            if result == "quit":
                return "👋 Use browser close button to exit."
            return result

        # Generate response
        try:
            return interface.generate(message)
        except Exception as e:
            return f"[ERROR] {e}"

    # Create Gradio ChatInterface
    ui = gr.ChatInterface(
        fn=respond,
        title="🦁 SEA-LION Unified Governance Console (v45.0 FULL)",
        description=(
            "**Trinity Modes:** /asi (Ω Guardian) | /agi (Δ Architect) | /apex (Ψ Judge)\n\n"
            "**Comparison:** /both (RAW vs GOVERNED side-by-side)\n\n"
            "**Commands:** /stats | /clear"
        ),
        theme="soft",
        examples=[
            "hi",
            "explain recursion in simple terms",
            "who is Albert Einstein",
            "/both",
            "/agi",
            "/apex",
            "/stats",
        ],
    )

    return ui


# ---------------------------------------------------------------------------
# REPL MODE (Command-Line Interface)
# ---------------------------------------------------------------------------


def run_repl(interface: UnifiedInterface):
    """Run REPL mode (command-line chat)."""
    print("=" * 70)
    print("  🦁 SEA-LION Unified Governance Console (REPL Mode)")
    print("=" * 70)
    print(f"  Display Mode: {interface.display_mode}")
    print(f"  Comparison Mode: {'ON' if interface.comparison_mode else 'OFF'}")
    print("  Commands: /both, /asi, /agi, /apex, /stats, /clear, /quit")
    print("=" * 70)

    while True:
        try:
            user_input = input("\n🔹 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break

        if not user_input:
            continue

        # Handle commands
        if user_input.startswith("/"):
            result = interface.handle_command(user_input)
            if result == "quit":
                print("👋 Goodbye!")
                break
            print(result)
            continue

        # Generate response
        try:
            print("\n⏳ Generating...", end="\r")
            response = interface.generate(user_input)
            print(f"\n{response}")
        except Exception as e:
            print(f"\n[ERROR] {e}")


# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="SEA-LION Unified Governance Console")
    parser.add_argument("--cli", action="store_true", help="REPL mode (command-line)")
    parser.add_argument("--comparison", action="store_true", help="Start with /both mode enabled")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model name")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="API base URL")
    parser.add_argument("--no-memory", action="store_true", help="Disable MemOS")
    parser.add_argument("--no-tools", action="store_true", help="Disable web search")
    args = parser.parse_args()

    # Get API key
    api_key = os.getenv("SEALION_API_KEY") or os.getenv("ARIF_LLM_API_KEY")
    if not api_key:
        print("[ERROR] ERROR: No SEA-LION API key found.")
        print("   Set SEALION_API_KEY or ARIF_LLM_API_KEY environment variable.")
        sys.exit(1)

    # Create unified interface
    try:
        interface = UnifiedInterface(
            api_key=api_key,
            model=args.model,
            api_base=args.api_base,
            enable_memory=not args.no_memory,
            enable_tools=not args.no_tools,
            enable_comparison=args.comparison,
        )
    except Exception as e:
        print(f"[ERROR] ERROR: Failed to initialize interface: {e}")
        sys.exit(1)

    # Launch UI or REPL
    if args.cli:
        run_repl(interface)
    else:
        if not GRADIO_AVAILABLE:
            print("[ERROR] Gradio not available. Falling back to REPL mode.")
            print("   Install Gradio: pip install gradio")
            run_repl(interface)
        else:
            ui = create_gradio_ui(interface)
            if ui:
                print("\n🚀 Launching Gradio UI...")
                ui.launch(share=False)
            else:
                print("[ERROR] Failed to create Gradio UI. Falling back to REPL mode.")
                run_repl(interface)


if __name__ == "__main__":
    main()
