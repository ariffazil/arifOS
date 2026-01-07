#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEA-LION v45Ω Forge REPL - Trinity Governance Console

Real-time stress testing of lane-aware governance with Trinity architecture display.

Trinity Display Modes:
- ASI (default): Clean response only (minimal UX)
- AGI (/agi): + Pipeline timeline + ΔΩΨ (3-number Trinity)
- APEX (/apex): + F1-F9 floors + Claims + Full verdict reasoning

Features:
- Vertical timeline of 000→999 pipeline stages (StageInspector)
- ΔΩΨ Trinity metrics (Δ=Clarity, Ω=Empathy, Ψ=Vitality)
- 888_JUDGE verdict display (SEAL/VOID/SABAR/PARTIAL)
- Empathetic refusal messages (F6-compliant, actionable)
- Cooling Ledger integration (hash-chained JSONL)
- Lane classification (PHATIC/SOFT/HARD/REFUSE)

Usage:
    python scripts/sealion_forge_repl.py

Environment Variables:
    SEALION_API_KEY - SEA-LION API key (required)
    SEALION_MODEL - Model ID (default: aisingapore/Gemma-SEA-LION-v4-27B-IT)
    ARIF_LLM_API_BASE - API base URL (default: https://api.sea-lion.ai/v1)

Commands:
    /agi - AGI Architect mode (pipeline + ΔΩΨ metrics)
    /apex - APEX Judge mode (full forensic with F1-F9 floors)
    /both - Dual-Stream mode (RAW vs GOVERNED side-by-side)
    /stats - Show session statistics
    /clear - Clear chat memory
    /help - Show help
    /exit - Exit REPL

DITEMPA BUKAN DIBERI — Forged, not given; truth must cool before it rules.
"""

import os
import sys
import time
import logging
import hashlib
from pathlib import Path
from datetime import datetime, timezone

# Note: Removed Windows console encoding override - it caused garbled output

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# =============================================================================
# NAMED CONSTANTS (F4-CODE: Clarity - No Magic Numbers)
# =============================================================================

# PHATIC Lane Constraints (v45Ω Patch B.2 - Verbosity Ceiling)
PHATIC_MAX_CHARS = 100  # Verbosity ceiling for greetings
PHATIC_MAX_TOKENS = 24  # Token cap for concise responses
PHATIC_FALLBACK_GREETING = "Hi there! 👋 How can I help you today?"

# LLM Configuration
DEFAULT_MAX_TOKENS = 512  # Standard response token limit
DEFAULT_TEMPERATURE = 0.3  # Default temperature for deterministic outputs
PHATIC_TEMPERATURE = 0.5  # Slightly higher for natural greetings

# Chat Memory Limits
DEFAULT_MAX_CONTEXT_TURNS = 6  # Recent turns to include in context
DEFAULT_CONTEXT_CHARS_PER_SIDE = 90  # Max chars per turn side (U/A)
HARD_MAX_TURNS = 200  # Absolute limit to prevent unbounded memory

# FORGE Rewrite Constraints
MAX_REWRITE_ATTEMPTS = 2  # Retry limit for PARTIAL verdict rewrites

# Display Truncation
MAX_DUAL_STREAM_LINES = 10  # Line limit for side-by-side comparison

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Configure logging (Transparency Mandate)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Import what's available
try:
    from arifos_core.system.pipeline import Pipeline

    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False
    logger.warning("arifos_core.system.pipeline not available")

try:
    from arifos_core.integration.connectors.litellm_gateway import make_llm_generate, LiteLLMConfig

    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    logger.warning("arifos_core.connectors.litellm_gateway not available")

try:
    from arifos_core.system.apex_prime import Verdict

    VERDICT_ENUM_AVAILABLE = True
except ImportError:
    VERDICT_ENUM_AVAILABLE = False
    logger.warning("arifos_core.system.apex_prime.Verdict not available (using string comparison fallback)")

try:
    from arifos_core.utils.eye_sentinel import EyeSentinel

    EYE_AVAILABLE = True
except ImportError:
    EYE_AVAILABLE = False
    logger.warning("arifos_core.utils.eye_sentinel not available (@EYE disabled)")


def create_ledger_sink(ledger_path: str):
    """Create a hash-chained JSONL ledger sink."""
    path = Path(ledger_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from arifos_core.memory.cooling_ledger import append_entry
    except Exception as e:
        logger.warning(f"Cooling ledger unavailable ({e}); ledger entries will be dropped.")

        def sink(_entry: dict) -> None:
            return None

        return sink

    def sink(entry: dict) -> None:
        try:
            append_entry(path, dict(entry))
        except Exception as e:
            # FAIL-CLOSED for ledger I/O: log and continue the interactive session.
            logger.warning(f"Ledger append failed (continuing session): {e}")

    return sink


def get_verdict_string(state) -> str:
    """
    Extract verdict string from pipeline state (F8-CODE: Governed pattern).

    Handles both Verdict enum (preferred) and string fallback gracefully.
    Returns normalized verdict string (SEAL, VOID, PARTIAL, SABAR, 888_HOLD).
    """
    if not hasattr(state, "verdict") or not state.verdict:
        return "UNKNOWN"

    # Try Verdict enum first (F8-CODE: Use established patterns)
    if VERDICT_ENUM_AVAILABLE:
        if hasattr(state.verdict, "verdict"):
            # ApexVerdict wrapper
            if isinstance(state.verdict.verdict, Verdict):
                return state.verdict.verdict.value
            return str(state.verdict.verdict.value) if hasattr(state.verdict.verdict, "value") else str(state.verdict.verdict)
        elif isinstance(state.verdict, Verdict):
            # Direct Verdict enum
            return state.verdict.value

    # Fallback to string extraction
    if hasattr(state.verdict, "verdict"):
        return str(state.verdict.verdict.value) if hasattr(state.verdict.verdict, "value") else str(state.verdict.verdict)
    elif hasattr(state.verdict, "value"):
        return str(state.verdict.value)
    else:
        return str(state.verdict)


def get_empathetic_refusal(verdict: str, lane: str, state=None) -> str:
    """
    Generate empathetic, actionable refusal messages (F6-CODE: Empathy).

    Per Communication Law v45: No metrics leakage, but human-centered.
    Serves weakest stakeholder (confused user) with actionable next steps.

    Args:
        verdict: Verdict string (VOID, SABAR, 888_HOLD)
        lane: Query lane (REFUSE, SOFT, HARD, PHATIC)
        state: Optional pipeline state (reserved for future use)

    Returns:
        Human-friendly refusal message with actionable guidance
    """
    # VOID: Hard refusal (safety boundary + next step)
    if verdict == "VOID":
        # Lane-specific refusals
        if lane == "REFUSE":
            return "I can't help with that. If you want to understand the topic itself, I can explain it in general terms."
        else:
            return "I can't give reliable guidance on this. Can you rephrase your question or narrow it down?"

    # SABAR: Soft pause (needs clarification)
    elif verdict == "SABAR":
        return "Hold on - I want to make sure I understand. What are you actually trying to do here?"

    # 888_HOLD: Escalation (human judgment needed)
    elif verdict == "888_HOLD":
        return "This needs your judgment, not mine. What kind of help are you looking for?"

    # Fallback (shouldn't reach here, but F7-CODE: Acknowledge uncertainty)
    return "I'm having trouble with this request. Can you rephrase or break it down?"


class ForgeREPL:
    """Interactive SEA-LION governance testing console."""

    def __init__(self):
        # Trinity Display Modes (ASI default → AGI → APEX)
        self.agi_mode = False    # AGI Architect: Pipeline + ΔΩΨ (was verbose)
        self.apex_mode = False   # APEX Judge: Full forensic (F1-F9 + Claims)
        self.dual_stream = False  # RAW vs GOVERNED comparison mode
        self.ledger_path = os.getenv(
            "ARIFOS_SEALION_FORGE_LEDGER_PATH", "cooling_ledger/sealion_forge_sessions.jsonl"
        )

        # Stateful chat session (in-memory)
        # - `session_id` makes TEARFRAME session physics + recall stable across turns
        # - `turns` supplies conversational context blocks into the pipeline
        self.session_id = os.getenv(
            "ARIFOS_SESSION_ID",
            f"sealion_forge_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        )
        self.max_context_turns = int(os.getenv("ARIFOS_CHAT_CONTEXT_TURNS", str(DEFAULT_MAX_CONTEXT_TURNS)))
        self.turns: list[tuple[str, str]] = []

        # Get API configuration
        self.model = os.getenv("SEALION_MODEL", "aisingapore/Gemma-SEA-LION-v4-27B-IT")
        self.api_base = os.getenv("ARIF_LLM_API_BASE", "https://api.sea-lion.ai/v1")
        self.api_key = (
            os.getenv("ARIF_LLM_API_KEY")
            or os.getenv("SEALION_API_KEY")
            or os.getenv("LLM_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )

        if not self.api_key:
            print("❌ API Key not found!")
            print("\nSet environment variable:")
            print("  Windows: $env:SEALION_API_KEY = 'your-sealion-api-key'")
            print("  Linux/Mac: export SEALION_API_KEY='your-sealion-api-key'")
            sys.exit(1)

        if not PIPELINE_AVAILABLE:
            print("❌ Missing dependency: arifos_core.system.pipeline (Pipeline)")
            sys.exit(1)

        if not LITELLM_AVAILABLE:
            print("❌ Missing dependency: arifos_core.connectors.litellm_gateway (LiteLLM gateway)")
            sys.exit(1)

        # Create ledger sink
        self.ledger_sink = create_ledger_sink(self.ledger_path)

        # Initialize @EYE Sentinel (Witness & Memory Chain)
        self.eye_sentinel = None
        if EYE_AVAILABLE:
            try:
                self.eye_sentinel = EyeSentinel()
            except Exception as e:
                logger.warning(f"@EYE Sentinel init failed ({e}); continuing without @EYE.")
                self.eye_sentinel = None

        # Create governed LLM generator with lane-aware signature
        try:
            self.governed_generate = self._create_governed_generator()
        except Exception as e:
            print(f"❌ Failed to initialize governed generator: {e}")
            print("   If you are missing dependencies, try: pip install litellm")
            sys.exit(1)

        # Create RAW (ungoverned) generator for dual-stream mode
        try:
            self.raw_generate = self._create_raw_generator()
        except Exception as e:
            print(f"❌ Failed to initialize RAW generator: {e}")
            print("   If you are missing dependencies, try: pip install litellm")
            sys.exit(1)

        # Create pipeline with governed generator
        self.pipeline = Pipeline(
            llm_generate=self.governed_generate,
            context_retriever=self._get_chat_context_blocks,
            context_retriever_at_stage_111=True,
            ledger_sink=self.ledger_sink,
            eye_sentinel=self.eye_sentinel,
        )

        # Session stats
        self.session_count = 0
        self.verdicts = {"SEAL": 0, "VOID": 0, "PARTIAL": 0, "SABAR": 0}
        self.lanes = {"PHATIC": 0, "SOFT": 0, "HARD": 0, "REFUSE": 0}
        self.session_start = datetime.now()
        self.last_state = None  # Last PipelineState (for /waw and /eye)

    def _forge_rewrite_phatic(self, verbose_response: str) -> str:
        """Rewrite verbose response into PHATIC-compliant format (<=PHATIC_MAX_CHARS)."""
        # FIX B.2: PHATIC lane must produce concise greetings
        # Fallback to safe greeting if rewrite fails
        # F7-CODE: Acknowledge uncertainty when using fallback

        # Attempt to extract first sentence
        sentences = verbose_response.split(".")
        if sentences and len(sentences[0].strip()) <= PHATIC_MAX_CHARS:
            return sentences[0].strip() + "."

        # If still too long, use fallback (with uncertainty acknowledgment)
        logger.debug(f"PHATIC rewrite fallback used (original: {len(verbose_response)} chars)")
        return PHATIC_FALLBACK_GREETING

    def _create_governed_generator(self):
        """Create governed SEA-LION generator with ledger integration."""
        # Base LiteLLM generator
        config = LiteLLMConfig(
            provider="openai",
            api_base=self.api_base,
            api_key=self.api_key,
            model=self.model,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,  # Will be overridden for PHATIC lane
        )
        base_generate = make_llm_generate(config)

        # Cache PHATIC generator (avoid per-turn re-init).
        phatic_generate = None

        # NOTE: Pipeline uses signature inspection:
        # - If `lane` exists, stage_333_reason expects `(text, metadata)`
        # - Some stages still call `llm_generate(prompt) -> str`
        def governed_wrapper(prompt: str, lane: str | None = None):
            """Lane-aware wrapper compatible with both `(text, meta)` and `text` call-sites."""
            nonlocal phatic_generate
            lane_value = lane or "UNKNOWN"

            # FIX C: PHATIC lane optimization (bypass deep reasoning, cap tokens)
            if lane_value == "PHATIC":
                if phatic_generate is None:
                    # Create PHATIC-optimized config
                    phatic_config = LiteLLMConfig(
                        provider="openai",
                        api_base=self.api_base,
                        api_key=self.api_key,
                        model=self.model,
                        temperature=PHATIC_TEMPERATURE,
                        max_tokens=PHATIC_MAX_TOKENS,  # Strict token cap for greetings
                    )
                    phatic_generate = make_llm_generate(phatic_config)

                # Prepend instruction to force conciseness
                phatic_prompt = f"{prompt}\n\nReply in ONE short sentence (max 15 words). Be friendly. No lists."
                response = phatic_generate(phatic_prompt)
            else:
                response = base_generate(prompt)

            # Build metadata
            prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
            metadata = {
                "model": self.model,
                "lane": lane_value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "prompt_hash": prompt_hash,
            }

            # Write to ledger (Transparency Mandate - log failures)
            if self.ledger_sink:
                ledger_entry = {
                    "event": "forge_repl_generation",
                    "model": self.model,
                    "lane": lane_value,
                    "timestamp": metadata["timestamp"],
                    "prompt_hash": metadata["prompt_hash"],
                }
                try:
                    self.ledger_sink(ledger_entry)
                except Exception as e:
                    # F2-CODE: Truth in error handling - log failures for audit trail
                    logger.warning(f"Ledger write failed (continuing session): {e}")

            if lane is None:
                return response

            return response, metadata

        return governed_wrapper

    def _create_raw_generator(self):
        """Create RAW (ungoverned) SEA-LION generator for comparison."""
        # Base LiteLLM generator (no pipeline, no governance)
        config = LiteLLMConfig(
            provider="openai",
            api_base=self.api_base,
            api_key=self.api_key,
            model=self.model,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
        )
        return make_llm_generate(config)

    def _store_turn(self, user_text: str, assistant_text: str) -> None:
        """Store a completed chat turn in memory (bounded)."""
        self.turns.append((user_text, assistant_text))
        # Bound growth to avoid unbounded memory during long sessions
        hard_limit = int(os.getenv("ARIFOS_CHAT_MAX_TURNS", str(HARD_MAX_TURNS)))
        if hard_limit > 0 and len(self.turns) > hard_limit:
            self.turns = self.turns[-hard_limit:]

    def _format_turn_for_context(self, user_text: str, assistant_text: str) -> str:
        """Format a single turn for context injection (kept intentionally short)."""
        user_flat = " ".join(user_text.strip().split())
        assistant_flat = " ".join(assistant_text.strip().split())
        max_side = int(os.getenv("ARIFOS_CHAT_CONTEXT_CHARS_PER_SIDE", str(DEFAULT_CONTEXT_CHARS_PER_SIDE)))
        return f"U: {user_flat[:max_side]}\nA: {assistant_flat[:max_side]}"

    def _get_chat_context_blocks(self, _query: str) -> list[dict]:
        """Return recent chat turns as pipeline context blocks (most recent first)."""
        if not self.turns or self.max_context_turns <= 0:
            return []

        recent = self.turns[-self.max_context_turns :]
        blocks: list[dict] = []
        for user_text, assistant_text in reversed(recent):
            blocks.append(
                {
                    "type": "chat_turn",
                    "text": self._format_turn_for_context(user_text, assistant_text),
                }
            )
        return blocks

    def _build_raw_chat_prompt(self, user_text: str) -> str:
        """Build a plain-text chat transcript prompt for the RAW side (dual-stream)."""
        prompt_parts: list[str] = []
        for prev_user, prev_assistant in self.turns[-self.max_context_turns :]:
            prompt_parts.append(f"User: {prev_user}")
            prompt_parts.append(f"Assistant: {prev_assistant}")
        prompt_parts.append(f"User: {user_text}")
        prompt_parts.append("Assistant:")
        return "\n".join(prompt_parts)

    def print_banner(self):
        """Print REPL banner with Trinity status."""
        print("\n" + "═" * 80)
        print("🔥 SEA-LION v45Ω FORGE REPL — Trinity Governance Console 🔥".center(80))
        print("═" * 80)
        print(f"\n📦 Model: {self.model}")
        print(f"🌐 API: {self.api_base}")
        print(f"📝 Ledger: {self.ledger_path}")
        print(f"🧠 Session: {self.session_id} | Turns: {len(self.turns)}")

        # Trinity mode status
        mode = "ASI (Guardian)" if not self.agi_mode else "AGI (Architect)"
        if self.apex_mode:
            mode = "APEX (Judge)"
        print(f"👁️  Mode: {mode}")
        print(f"🛰️  @EYE: {'ENABLED ✓' if self.eye_sentinel is not None else 'DISABLED ✗'}")
        print(f"🔀 Dual-Stream: {'ENABLED ✓' if self.dual_stream else 'DISABLED ✗'}")

        print("\n💡 Commands: /agi /apex /both /waw /eye /stats /clear /help /exit")
        print("═" * 80 + "\n")

    def print_help(self):
        """Print help message with Trinity architecture."""
        print("\n┌" + "─" * 78 + "┐")
        print("│ FORGE REPL COMMANDS — Trinity Architecture".ljust(79) + "│")
        print("├" + "─" * 78 + "┤")
        print("│ /agi       AGI Architect view (pipeline + ΔΩΨ metrics)".ljust(79) + "│")
        print("│ /apex      APEX Judge view (full forensic with floors)".ljust(79) + "│")
        print("│ /both      Dual-Stream (RAW vs GOVERNED side-by-side)".ljust(79) + "│")
        print("│ /waw       Show last W@W organ votes".ljust(79) + "│")
        print("│ /eye       Show last @EYE telemetry".ljust(79) + "│")
        print("│ /stats     Session statistics (verdicts, lanes)".ljust(79) + "│")
        print("│ /clear     Clear chat memory".ljust(79) + "│")
        print("│ /help      Show this help".ljust(79) + "│")
        print("│ /exit      Exit REPL".ljust(79) + "│")
        print("├" + "─" * 78 + "┤")
        print("│ TRINITY MODES:".ljust(79) + "│")
        print("│  ASI (default) → Clean response only".ljust(79) + "│")
        print("│  AGI (/agi)    → + Pipeline + ΔΩΨ (3 numbers)".ljust(79) + "│")
        print("│  APEX (/apex)  → + F1-F9 floors + Claims + Reasoning".ljust(79) + "│")
        print("└" + "─" * 78 + "┘\n")

    def print_stats(self):
        """Print session statistics."""
        elapsed = (datetime.now() - self.session_start).total_seconds()
        elapsed_str = f"{int(elapsed // 60)}m {int(elapsed % 60)}s"

        print("\n┌" + "─" * 78 + "┐")
        print("│ SESSION STATISTICS".ljust(79) + "│")
        print("├" + "─" * 78 + "┤")
        print(f"│ Sessions: {self.session_count:<10} | Elapsed: {elapsed_str}".ljust(79) + "│")
        print("├" + "─" * 78 + "┤")
        print("│ Verdicts:".ljust(79) + "│")
        for v, count in self.verdicts.items():
            pct = (count / self.session_count * 100) if self.session_count > 0 else 0
            print(f"│   {v:<10} {count:>3} ({pct:>5.1f}%)".ljust(79) + "│")
        print("├" + "─" * 78 + "┤")
        print("│ Lanes:".ljust(79) + "│")
        for l, count in self.lanes.items():
            pct = (count / self.session_count * 100) if self.session_count > 0 else 0
            print(f"│   {l:<10} {count:>3} ({pct:>5.1f}%)".ljust(79) + "│")
        print("└" + "─" * 78 + "┘\n")

    def print_pipeline_timeline(self, state):
        """Print vertical timeline of 000→999 pipeline stages with ΔS."""
        if not self.agi_mode:
            return

        print("\n┌" + "─" * 78 + "┐")
        print("│ 🔬 PIPELINE TIMELINE (000→999) — StageInspector".ljust(79) + "│")
        print("├" + "─" * 78 + "┤")

        stages = state.stage_trace if hasattr(state, "stage_trace") else []
        stage_times = state.stage_times if hasattr(state, "stage_times") else {}

        if not stages:
            print("│ No stages recorded".ljust(79) + "│")
            print("└" + "─" * 78 + "┘\n")
            return

        # Calculate cumulative time
        start_time = stage_times.get(stages[0].split("_")[0], 0)

        for i, stage in enumerate(stages):
            stage_code = stage.split("_")[0] if "_" in stage else stage

            # Get duration for this stage
            duration = 0.0
            if i + 1 < len(stages):
                next_stage_code = stages[i + 1].split("_")[0]
                if stage_code in stage_times and next_stage_code in stage_times:
                    duration = (stage_times[next_stage_code] - stage_times[stage_code]) * 1000

            # Get cumulative time
            cumulative = 0.0
            if stage_code in stage_times and start_time:
                cumulative = (stage_times[stage_code] - start_time) * 1000

            # Format stage line with box drawing
            arrow = "└─>" if i == len(stages) - 1 else "├─>"
            if duration > 0:
                line = f"│ {arrow} {stage:<20} {duration:>7.1f}ms  (T+{cumulative:>7.1f}ms)"
            else:
                line = f"│ {arrow} {stage:<20} {'':>7}    (T+{cumulative:>7.1f}ms)"

            print(line.ljust(79) + "│")

        # Calculate total time
        if stages:
            last_stage_code = stages[-1].split("_")[0]
            total_time = (stage_times.get(last_stage_code, start_time) - start_time) * 1000
            print("├" + "─" * 78 + "┤")
            print(f"│ ⏱️  Total Pipeline Time: {total_time:.1f}ms".ljust(79) + "│")

        print("└" + "─" * 78 + "┘\n")

    def print_trinity_metrics(self, state):
        """Print ΔΩΨ Trinity metrics (Clarity, Empathy, Vitality)."""
        if not hasattr(state, "metrics") or state.metrics is None:
            print("⚠️  No metrics available\n")
            return

        m = state.metrics

        print("┌" + "─" * 78 + "┐")
        print("│ ✨ ΔΩΨ TRINITY METRICS — Clarity · Empathy · Vitality".ljust(79) + "│")
        print("├" + "─" * 78 + "┤")

        # Δ (Delta/Clarity) = Truth × ΔS
        delta_s = getattr(m, "delta_s", 0.0) or 0.0
        truth = getattr(m, "truth", 0.0) or 0.0
        delta = truth * delta_s if delta_s and truth else 0.0
        print(
            f"│ Δ (Clarity)   = Truth({truth:.3f}) × ΔS({delta_s:.3f}) = {delta:.3f}".ljust(79)
            + "│"
        )

        # Ω (Omega/Empathy) = κᵣ × Amanah × RASA
        kappa_r = getattr(m, "kappa_r", 0.0) or 0.0
        amanah = getattr(m, "amanah", 0.0) or 0.0
        rasa = getattr(m, "rasa", 0.0) or 0.0
        omega = kappa_r * amanah * rasa if kappa_r and amanah and rasa else 0.0
        print(
            f"│ Ω (Empathy)   = κᵣ({kappa_r:.3f}) × Amanah({amanah:.3f}) × RASA({rasa:.3f}) = {omega:.3f}".ljust(
                79
            )
            + "│"
        )

        # Ψ (Psi/Vitality) = min(floor_ratios)
        psi = getattr(m, "psi", 0.0) or 0.0
        print(f"│ Ψ (Vitality)  = {psi:.3f}".ljust(79) + "│")

        # Show GENIUS metrics if available
        if hasattr(state, "verdict") and hasattr(state.verdict, "genius_metrics"):
            gm = state.verdict.genius_metrics
            if gm:
                print("├" + "─" * 78 + "┤")
                g = getattr(gm, "g", 0.0) or 0.0
                c_dark = getattr(gm, "c_dark", 0.0) or 0.0
                print(
                    f"│ G (Genius Index)      = {g:.3f} {'✓' if g >= 0.80 else '✗'}".ljust(79) + "│"
                )
                print(
                    f"│ C_dark (Dark Clever)  = {c_dark:.3f} {'✓' if c_dark < 0.30 else '✗'}".ljust(
                        79
                    )
                    + "│"
                )

        print("└" + "─" * 78 + "┘\n")

    def print_verdict_box(self, state):
        """Print 888_JUDGE verdict before response."""
        # F8-CODE: Use helper function for verdict extraction
        verdict_str = get_verdict_string(state)
        verdict_emoji = "❓"

        # Emoji mapping
        verdict_map = {
            "SEAL": "✅",
            "VOID": "❌",
            "SABAR": "⏸️",
            "PARTIAL": "⚠️",
            "888_HOLD": "🛑",
        }
        verdict_emoji = verdict_map.get(verdict_str, "❓")

        # Lane
        lane = getattr(state, "applicability_lane", "UNKNOWN")

        # Lane-specific truth threshold
        from arifos_core.enforcement.metrics import get_lane_truth_threshold

        lane_threshold = get_lane_truth_threshold(lane)

        # Actual truth score
        truth = getattr(state.metrics, "truth", 0.0) if state.metrics else 0.0

        # Verdict reason
        reason = ""
        if hasattr(state.verdict, "reason"):
            reason = (
                state.verdict.reason[:60] + "..."
                if len(state.verdict.reason) > 60
                else state.verdict.reason
            )

        print("╔" + "═" * 78 + "╗")
        print("║ ⚖️  888_JUDGE VERDICT".ljust(79) + "║")
        print("╠" + "═" * 78 + "╣")
        print(
            f"║ {verdict_emoji} {verdict_str:<10} │ Lane: {lane:<10} │ Truth: {truth:.3f} / {lane_threshold:.2f}".ljust(
                79
            )
            + "║"
        )
        if reason:
            print("╠" + "═" + "─" * 76 + "═" + "╣")
            # Word wrap reason
            words = reason.split()
            line = "║ "
            for word in words:
                if len(line) + len(word) + 1 > 77:
                    print(line.ljust(79) + "║")
                    line = "║ " + word + " "
                else:
                    line += word + " "
            if len(line) > 2:
                print(line.ljust(79) + "║")
        print("╚" + "═" * 78 + "╝\n")

    def print_waw_summary(self, state) -> None:
        """Print W@W Federation organ votes and aggregated verdict."""
        waw = getattr(state, "waw_verdict", None)
        if waw is None:
            print("\n⚠️  No W@W verdict available for the last run.\n")
            return

        def _safe_vote(organ_id: str) -> str:
            try:
                return state._get_organ_vote(organ_id)
            except Exception:
                return "N/A"

        votes = {
            "@WEALTH": _safe_vote("@WEALTH"),
            "@RIF": _safe_vote("@RIF"),
            "@WELL": _safe_vote("@WELL"),
            "@GEOX": _safe_vote("@GEOX"),
            "@PROMPT": _safe_vote("@PROMPT"),
        }

        verdict = getattr(waw, "verdict", "UNKNOWN")
        has_absolute_veto = bool(getattr(waw, "has_absolute_veto", False))
        has_veto = bool(getattr(waw, "has_veto", False))
        has_warn = bool(getattr(waw, "has_warn", False))
        veto_organs = getattr(waw, "veto_organs", []) or []
        warn_organs = getattr(waw, "warn_organs", []) or []

        print("\n┌" + "─" * 78 + "┐")
        print("│ 🧭 W@W FEDERATION — Organ Votes".ljust(79) + "│")
        print("├" + "─" * 78 + "┤")
        print(
            f"│ Verdict: {verdict:<10} | Absolute: {str(has_absolute_veto):<5} | Veto: {str(has_veto):<5} | Warn: {str(has_warn):<5}".ljust(
                79
            )
            + "│"
        )
        print(
            f"│ Veto Organs: {', '.join(veto_organs) if veto_organs else 'None'}".ljust(79) + "│"
        )
        print(
            f"│ Warn Organs: {', '.join(warn_organs) if warn_organs else 'None'}".ljust(79) + "│"
        )
        print("├" + "─" * 78 + "┤")
        for organ_id, vote in votes.items():
            print(f"│ {organ_id:<8} {vote}".ljust(79) + "│")
        print("└" + "─" * 78 + "┘\n")

    def print_eye_summary(self, state) -> None:
        """Print @EYE Sentinel telemetry (adapter vector + blocking reasons if present)."""
        eye_vector = getattr(state, "eye_vector", None)
        floor_failures = getattr(state, "floor_failures", []) or []

        eye_lines = [f for f in floor_failures if f.startswith("EYE_")]

        if eye_vector is None and not eye_lines:
            print("\n⚠️  No @EYE telemetry available for the last run.\n")
            return

        action = ""
        level = ""
        reasons = []
        if isinstance(eye_vector, dict):
            action = str(eye_vector.get("action", ""))
            level = str(eye_vector.get("level", ""))
            reasons = eye_vector.get("reasons", []) or []

        print("\n┌" + "─" * 78 + "┐")
        print("│ 👁️  @EYE SENTINEL — Witness Telemetry".ljust(79) + "│")
        print("├" + "─" * 78 + "┤")
        if action or level:
            print(f"│ Vector: level={level or 'N/A'} action={action or 'N/A'}".ljust(79) + "│")
        if reasons:
            max_reasons = 6
            shown = [str(r) for r in reasons[:max_reasons]]
            suffix = " ..." if len(reasons) > max_reasons else ""
            print(f"│ Reasons: {', '.join(shown)}{suffix}".ljust(79) + "│")
        if eye_lines:
            print("├" + "─" * 78 + "┤")
            for line in eye_lines[:8]:
                print(f"│ {line[:76]}".ljust(79) + "│")
        print("└" + "─" * 78 + "┘\n")

    def print_response_minimal(self, response: str, verdict: str, lane: str):
        """Print governed response (minimal format by default)."""
        # Verdict emoji
        verdict_emoji_map = {
            "SEAL": "✅",
            "PARTIAL": "⚠️",
            "VOID": "❌",
            "SABAR": "⏸️",
            "888_HOLD": "🛑",
        }
        emoji = verdict_emoji_map.get(verdict, "❓")

        # Print response with minimal formatting
        print(f"\n{emoji} {response}\n")

    def print_response(self, state):
        """Print governed response (verbose format with box)."""
        print("┌" + "─" * 78 + "┐")
        print("│ 💬 GOVERNED RESPONSE".ljust(79) + "│")
        print("├" + "─" * 78 + "┤")

        response = state.raw_response or state.draft_response or "[No response]"

        # Word wrap response
        words = response.split()
        line = "│ "
        for word in words:
            if len(line) + len(word) + 1 > 77:
                print(line.ljust(79) + "│")
                line = "│ " + word + " "
            else:
                line += word + " "
        if len(line) > 2:
            print(line.ljust(79) + "│")

        print("└" + "─" * 78 + "┘\n")

    def print_trinity_minimal(self, state):
        """Print minimal ΔΩΨ Trinity (3 numbers + verdict) for AGI mode."""
        if not self.agi_mode and not self.apex_mode:
            return

        m = state.metrics
        if not m:
            return

        # Calculate Trinity scores per genius_law.json component_scores
        # Delta: (truth + delta_s) / 2
        truth = getattr(m, "truth", 0.0)
        delta_s = getattr(m, "delta_s", 0.0)
        delta = (truth + delta_s) / 2.0

        # Omega: kappa_r * amanah * rasa (ethics/empathy composite)
        kappa_r = getattr(m, "kappa_r", 0.0)
        amanah = 1.0 if getattr(m, "amanah", False) else 0.0
        rasa = getattr(m, "rasa", 0.0)
        omega = kappa_r * amanah * rasa

        # Psi: Vitality (direct from metrics)
        psi = getattr(m, "psi", 0.0)

        verdict = get_verdict_string(state)
        verdict_emoji = {"SEAL": "✅", "PARTIAL": "⚠️", "VOID": "❌",
                         "SABAR": "⏸️", "888_HOLD": "🛑"}.get(verdict, "❓")

        # AGI mode: Minimal display
        print(f"\n🧠 Δ={delta:.2f}  ❤️ Ω={omega:.2f}  ⚖️ Ψ={psi:.2f}  {verdict_emoji}\n")

    def print_floors_detail(self, state):
        """Print F1-F9 floor scores (APEX mode only)."""
        if not self.apex_mode:
            return

        m = state.metrics
        if not m:
            return

        print("┌" + "─" * 78 + "┐")
        print("│ 🏛️  CONSTITUTIONAL FLOORS (F1-F9)".ljust(79) + "│")
        print("├" + "─" * 78 + "┤")

        # F1-F9 with thresholds
        floors = [
            ("F1 Amanah", getattr(m, "amanah", 0.0), "LOCK", "boolean"),
            ("F2 Truth", getattr(m, "truth", 0.0), 0.99, "gte"),
            ("F3 Tri-Witness", getattr(m, "tri_witness", 0.0), 0.95, "gte"),
            ("F4 ΔS", getattr(m, "delta_s", 0.0), 0.0, "gte"),
            ("F5 Peace²", getattr(m, "peace_squared", 0.0), 1.0, "gte"),
            ("F6 κᵣ", getattr(m, "kappa_r", 0.0), 0.95, "gte"),
            ("F7 Ω₀", getattr(m, "omega_0", 0.0), (0.03, 0.05), "band"),
            ("F8 G", getattr(m, "g", 0.0), 0.80, "gte"),
            ("F9 C_dark", getattr(m, "c_dark", 0.0), 0.30, "lt"),
        ]

        for name, value, threshold, check_type in floors:
            if check_type == "boolean":
                status = "✓" if value else "✗"
                print(f"│ {name:<30} {str(value):<10} {status}".ljust(79) + "│")
            elif check_type == "gte":
                status = "✓" if value >= threshold else "✗"
                print(f"│ {name:<30} {value:.3f}   {status}  [≥{threshold}]".ljust(79) + "│")
            elif check_type == "lt":
                status = "✓" if value < threshold else "✗"
                print(f"│ {name:<30} {value:.3f}   {status}  [<{threshold}]".ljust(79) + "│")
            elif check_type == "band":
                low, high = threshold
                status = "✓" if low <= value <= high else "✗"
                print(f"│ {name:<30} {value:.3f}   {status}  [{low}-{high}]".ljust(79) + "│")

        print("└" + "─" * 78 + "┘\n")

    def print_claim_analysis(self, state):
        """Print claim detection results (APEX mode only)."""
        if not self.apex_mode:
            return

        response = state.raw_response or state.draft_response or ""

        try:
            from arifos_core.enforcement.claim_detection import extract_claim_profile
            profile = extract_claim_profile(response)
        except ImportError:
            return

        print("┌" + "─" * 78 + "┐")
        print("│ 🔍 CLAIM DETECTION — Physics > Semantics".ljust(79) + "│")
        print("├" + "─" * 78 + "┤")
        print(f"│ Has Claims: {'YES ✓' if profile['has_claims'] else 'NO (Phatic) ✗'}".ljust(79) + "│")
        print(f"│ Claim Count: {profile['claim_count']}".ljust(79) + "│")
        print(f"│ Entity Density: {profile['entity_density']:.2f} per 100 chars".ljust(79) + "│")
        print(f"│ Claim Types: {', '.join(profile['claim_types'][:3])}".ljust(79) + "│")
        print("└" + "─" * 78 + "┘\n")

    def process_query(self, query: str):
        """Process user query through governed pipeline."""
        self.session_count += 1

        # FIX D: Gate telemetry behind verbose mode (default: minimal)
        if not self.agi_mode:
            print(f"\n🔥 Query #{self.session_count}")
        else:
            print(f"\n{'─' * 80}")
            print(
                f"🔥 Session #{self.session_count} │ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            print(f"{'─' * 80}")

        # Set verbose mode for StageInspector
        if self.agi_mode:
            os.environ["ARIFOS_VERBOSE"] = "1"
        else:
            os.environ["ARIFOS_VERBOSE"] = "0"

        # Run through governed pipeline
        try:
            state = self.pipeline.run(query, user_id=self.session_id)
            self.last_state = state

            # Get verdict status (F8-CODE: Use helper for verdict extraction)
            verdict_str = get_verdict_string(state)
            lane = getattr(state, "applicability_lane", "UNKNOWN")

            # FIX A: Emission gate - only emit if SEAL
            # FIX B: FORGE rewrite loop for PARTIAL verdicts
            attempt = 0
            final_response = None
            final_verdict = verdict_str

            while attempt < MAX_REWRITE_ATTEMPTS:
                if verdict_str == "SEAL":
                    # SEAL verdict: emit response
                    final_response = state.raw_response or state.draft_response
                    final_verdict = "SEAL"
                    break

                elif verdict_str == "PARTIAL":
                    # PARTIAL verdict: attempt FORGE rewrite
                    if lane == "PHATIC":
                        # Rewrite verbose PHATIC response
                        original_response = state.raw_response or state.draft_response or ""
                        rewritten_response = self._forge_rewrite_phatic(original_response)

                        # Check if rewrite is compliant (<=PHATIC_MAX_CHARS)
                        if len(rewritten_response) <= PHATIC_MAX_CHARS:
                            final_response = rewritten_response
                            final_verdict = "PARTIAL"  # Preserve original verdict (rewrite is UX-only)
                            break
                        else:
                            # Rewrite failed, try once more
                            attempt += 1
                            if attempt >= MAX_REWRITE_ATTEMPTS:
                                # Fallback to safe response (F7-CODE: acknowledge limitation)
                                logger.info("PHATIC rewrite exhausted attempts, using fallback")
                                final_response = PHATIC_FALLBACK_GREETING
                                final_verdict = "PARTIAL"
                    else:
                        # For non-PHATIC PARTIAL, emit with warning
                        final_response = state.raw_response or state.draft_response
                        final_verdict = "PARTIAL"
                        break

                elif verdict_str in {"VOID", "SABAR", "888_HOLD"}:
                    # Hard rejection: emit empathetic refusal (F6-CODE: Serve weakest stakeholder)
                    final_response = get_empathetic_refusal(verdict_str, lane, state)
                    final_verdict = verdict_str
                    break

                else:
                    # Unknown verdict: fallback
                    final_response = "⚠️ Unable to process request."
                    final_verdict = "UNKNOWN"
                    break

            # Update stats with final verdict
            if final_verdict in self.verdicts:
                self.verdicts[final_verdict] += 1
            if lane in self.lanes:
                self.lanes[lane] += 1

            # Display telemetry hierarchically (Trinity architecture)
            # AGI mode: Pipeline + ΔΩΨ Trinity
            if self.agi_mode:
                self.print_pipeline_timeline(state)
                self.print_trinity_minimal(state)

            # APEX mode: + F1-F9 Floors + Claims + Verdict
            if self.apex_mode:
                self.print_floors_detail(state)
                self.print_claim_analysis(state)
                self.print_verdict_box(state)
                self.print_eye_summary(state)
                self.print_waw_summary(state)

            # Display final response (always shown) - ensure not None
            response_text = final_response or "⚠️ No response generated."
            self.print_response_minimal(response_text, final_verdict, lane)
            self._store_turn(query, response_text)

        except Exception as e:
            print(f"\n❌ Pipeline Error: {e}\n")
            import traceback

            if self.agi_mode:
                traceback.print_exc()

    def process_query_dual(self, query: str):
        """Process query in dual-stream mode (RAW vs GOVERNED side-by-side)."""
        self.session_count += 1

        print(f"\n{'═' * 80}")
        print(
            f"🔥 Session #{self.session_count} │ DUAL-STREAM MODE │ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print(f"{'═' * 80}\n")

        # LEFT: RAW (ungoverned)
        print("┌" + "─" * 38 + "┬" + "─" * 39 + "┐")
        print("│ 🔓 RAW (Ungoverned)".ljust(39) + "│ 🔒 GOVERNED (v45Ω)".ljust(40) + "│")
        print("├" + "─" * 38 + "┼" + "─" * 39 + "┤")

        # Call RAW generator
        raw_response = ""
        raw_size_kb = 0.0  # F2-CODE: Honest naming - this is size, not Shannon entropy
        raw_time = 0.0

        try:
            raw_start = time.time()
            raw_prompt = self._build_raw_chat_prompt(query)
            raw_response = self.raw_generate(raw_prompt)
            raw_time = (time.time() - raw_start) * 1000
            raw_size_kb = len(raw_response) / 1000.0  # Response size in kilobytes
        except Exception as e:
            raw_response = f"[ERROR] {e}"
            logger.error(f"RAW generator failed: {e}")

        # Call GOVERNED pipeline
        if self.agi_mode:
            os.environ["ARIFOS_VERBOSE"] = "1"
        else:
            os.environ["ARIFOS_VERBOSE"] = "0"

        governed_response = ""
        governed_verdict = "UNKNOWN"
        governed_lane = "UNKNOWN"
        governed_truth = 0.0
        governed_psi = 0.0
        governed_time = 0.0

        try:
            gov_start = time.time()
            state = self.pipeline.run(query, user_id=self.session_id)
            self.last_state = state
            governed_time = (time.time() - gov_start) * 1000

            governed_response = state.raw_response or state.draft_response or "[No response]"
            governed_lane = getattr(state, "applicability_lane", "UNKNOWN")

            # F8-CODE: Use helper for verdict extraction
            governed_verdict = get_verdict_string(state)

            if state.metrics:
                governed_truth = getattr(state.metrics, "truth", 0.0)
                governed_psi = getattr(state.metrics, "psi", 0.0)

        except Exception as e:
            governed_response = f"[ERROR] {e}"
            logger.error(f"GOVERNED pipeline failed: {e}")

        # Update stats
        if governed_verdict in self.verdicts:
            self.verdicts[governed_verdict] += 1
        if governed_lane in self.lanes:
            self.lanes[governed_lane] += 1

        # Print side-by-side comparison
        # Stats row
        print(
            f"│ Chars: {len(raw_response):<6} Size: {raw_size_kb:.3f}KB".ljust(39)
            + f"│ Lane: {governed_lane:<8} Truth: {governed_truth:.3f}".ljust(40)
            + "│"
        )
        print(
            f"│ Time: {raw_time:.1f}ms".ljust(39) + f"│ Verdict: {governed_verdict}".ljust(40) + "│"
        )
        print("├" + "─" * 38 + "┼" + "─" * 39 + "┤")

        # Response text (side-by-side, truncated)
        raw_lines = self._wrap_text(raw_response, 36)
        gov_lines = self._wrap_text(governed_response, 37)

        max_lines = max(len(raw_lines), len(gov_lines))
        for i in range(max_lines):
            left = raw_lines[i] if i < len(raw_lines) else ""
            right = gov_lines[i] if i < len(gov_lines) else ""
            print(f"│ {left:<37}│ {right:<38}│")

        print("└" + "─" * 38 + "┴" + "─" * 39 + "┘\n")

        # Show GENIUS metrics comparison
        print("┌" + "─" * 78 + "┐")
        print("│ 📊 CONTRAST ANALYSIS".ljust(79) + "│")
        print("├" + "─" * 78 + "┤")
        print(
            f"│ RAW Size: {raw_size_kb:.3f}KB │ GOVERNED Ψ (Vitality): {governed_psi:.3f}".ljust(
                79
            )
            + "│"
        )
        ratio_str = f"{(governed_time / raw_time):.1f}x" if raw_time > 0 else "n/a"
        print(
            f"│ RAW Time: {raw_time:.1f}ms │ GOVERNED Time: {governed_time:.1f}ms ({ratio_str})".ljust(
                79
            )
            + "│"
        )
        print(f"│ Governance Overhead: {governed_time - raw_time:.1f}ms".ljust(79) + "│")
        print("└" + "─" * 78 + "┘\n")
        self._store_turn(query, governed_response)

    def _wrap_text(self, text: str, width: int) -> list:
        """Word-wrap text to specified width, return list of lines."""
        if not text:
            return [""]

        words = text.split()
        lines = []
        line = ""

        for word in words:
            if len(line) + len(word) + 1 > width:
                lines.append(line)
                line = word + " "
            else:
                line += word + " "

        if line:
            lines.append(line.strip())

        return lines[:MAX_DUAL_STREAM_LINES]  # Limit to prevent vertical overflow

    def run(self):
        """Run the REPL."""
        self.print_banner()

        while True:
            try:
                # Get user input
                prompt = input("🔥 Forge> ").strip()

                if not prompt:
                    continue

                # Handle commands
                if prompt.startswith("/"):
                    cmd = prompt.lower()
                    if cmd == "/exit":
                        print("\n👋 Exiting Forge REPL. DITEMPA BUKAN DIBERI.\n")
                        break
                    elif cmd == "/help":
                        self.print_help()
                    elif cmd == "/agi":
                        self.agi_mode = not self.agi_mode
                        status = "ENABLED ✓" if self.agi_mode else "DISABLED ✗"
                        print(f"\n🧠 AGI Mode (Architect): {status}")
                        print("   (Shows: Pipeline timeline + ΔΩΨ Trinity metrics)\n")
                    elif cmd == "/apex":
                        self.apex_mode = not self.apex_mode
                        status = "ENABLED ✓" if self.apex_mode else "DISABLED ✗"
                        print(f"\n⚖️  APEX Mode (Judge): {status}")
                        print("   (Shows: Full forensic - Floors + Claims + Verdict reasoning)\n")
                        if self.apex_mode:
                            self.agi_mode = True  # APEX implies AGI
                    elif cmd == "/both":
                        self.dual_stream = not self.dual_stream
                        status = "ENABLED ✓" if self.dual_stream else "DISABLED ✗"
                        print(f"\n🔀 Dual-Stream: {status}\n")
                    elif cmd == "/waw":
                        if self.last_state is None:
                            print("\n⚠️  No previous pipeline state. Ask a question first.\n")
                        else:
                            self.print_waw_summary(self.last_state)
                    elif cmd == "/eye":
                        if self.last_state is None:
                            print("\n⚠️  No previous pipeline state. Ask a question first.\n")
                        else:
                            self.print_eye_summary(self.last_state)
                    elif cmd == "/stats":
                        self.print_stats()
                    elif cmd == "/clear":
                        self.turns = []
                        print("\n✅ Chat memory cleared.\n")
                    else:
                        print(f"\n❌ Unknown command: {prompt}")
                        print("💡 Type /help for available commands\n")
                    continue

                # Process query through appropriate mode
                if self.dual_stream:
                    self.process_query_dual(prompt)
                else:
                    self.process_query(prompt)

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Type /exit to quit.\n")
            except EOFError:
                print("\n\n👋 Exiting Forge REPL.\n")
                break


def main():
    """Entry point for SEA-LION Forge REPL."""
    repl = ForgeREPL()
    repl.run()


if __name__ == "__main__":
    main()
