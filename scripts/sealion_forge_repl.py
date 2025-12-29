#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEA-LION v45Ω Forge REPL - Interactive Governance Console

Real-time stress testing of lane-aware governance with full pipeline transparency.

Features:
- Vertical timeline of 000→999 pipeline stages (StageInspector)
- ΔΩΨ Trinity metrics (Clarity, Empathy, Vitality)
- 888_JUDGE verdict display (SEAL/VOID/SABAR/PARTIAL)
- Cooling Ledger integration via make_llm_generate_governed()
- Lane classification (PHATIC/SOFT/HARD/REFUSE)

Usage:
    python scripts/sealion_forge_repl.py

Environment Variables:
    SEALION_API_KEY - SEA-LION API key (required)
    SEALION_MODEL - Model ID (default: aisingapore/Gemma-SEA-LION-v4-27B-IT)
    ARIF_LLM_API_BASE - API base URL (default: https://api.sea-lion.ai/v1)

Commands:
    /verbose - Toggle StageInspector timeline (000→999 with ΔS)
    /both - Toggle Dual-Stream mode (RAW vs GOVERNED side-by-side)
    /stats - Show session statistics
    /help - Show help
    /exit - Exit REPL

DITEMPA BUKAN DIBERI — Forged, not given; truth must cool before it rules.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Fix Windows console encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from arifos_core.adapters.llm_sealion import create_ledger_sink
from arifos_core.system.pipeline import Pipeline
from arifos_core.connectors.litellm_gateway import make_llm_generate, LiteLLMConfig


class ForgeREPL:
    """Interactive SEA-LION governance testing console."""

    def __init__(self):
        self.verbose = False  # FIX D: Telemetry OFF by default (minimal UX)
        self.dual_stream = False  # RAW vs GOVERNED comparison mode
        self.ledger_path = "cooling_ledger/sealion_forge_sessions.jsonl"

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

        # Create ledger sink
        self.ledger_sink = create_ledger_sink(self.ledger_path)

        # Create governed LLM generator with lane-aware signature
        self.governed_generate = self._create_governed_generator()

        # Create RAW (ungoverned) generator for dual-stream mode
        self.raw_generate = self._create_raw_generator()

        # Create pipeline with governed generator
        self.pipeline = Pipeline(llm_generate=self.governed_generate)

        # Session stats
        self.session_count = 0
        self.verdicts = {"SEAL": 0, "VOID": 0, "PARTIAL": 0, "SABAR": 0}
        self.lanes = {"PHATIC": 0, "SOFT": 0, "HARD": 0, "REFUSE": 0}
        self.session_start = datetime.now()

    def _forge_rewrite_phatic(self, verbose_response: str) -> str:
        """Rewrite verbose response into PHATIC-compliant format (<=100 chars)."""
        # FIX B.2: PHATIC lane must produce concise greetings
        # Fallback to safe greeting if rewrite fails
        fallback = "Hi there! 👋 How can I help you today?"

        # Attempt to extract first sentence
        sentences = verbose_response.split('.')
        if sentences and len(sentences[0].strip()) <= 100:
            return sentences[0].strip() + '.'

        # If still too long, use fallback
        return fallback

    def _create_governed_generator(self):
        """Create governed SEA-LION generator with ledger integration."""
        # Base LiteLLM generator
        config = LiteLLMConfig(
            provider="openai",
            api_base=self.api_base,
            api_key=self.api_key,
            model=self.model,
            temperature=0.3,
            max_tokens=512,  # Will be overridden for PHATIC lane
        )
        base_generate = make_llm_generate(config)

        # Wrap with lane-aware signature matching make_llm_generate_governed
        def governed_wrapper(prompt: str, lane: str = "UNKNOWN") -> tuple[str, dict]:
            """Lane-aware wrapper that matches make_llm_generate_governed signature."""
            # FIX C: PHATIC lane optimization (bypass deep reasoning, cap tokens)
            if lane == "PHATIC":
                # Create PHATIC-optimized config
                phatic_config = LiteLLMConfig(
                    provider="openai",
                    api_base=self.api_base,
                    api_key=self.api_key,
                    model=self.model,
                    temperature=0.5,
                    max_tokens=24,  # Strict token cap for greetings
                )
                phatic_generate = make_llm_generate(phatic_config)
                # Prepend instruction to force conciseness
                phatic_prompt = f"{prompt}\n\nReply in ONE short sentence (max 15 words). Be friendly. No lists."
                response = phatic_generate(phatic_prompt)
            else:
                response = base_generate(prompt)

            # Build metadata
            metadata = {
                "model": self.model,
                "lane": lane,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "prompt_hash": hash(prompt) & 0xFFFFFFFF,
            }

            # Write to ledger
            if self.ledger_sink:
                ledger_entry = {
                    "event": "forge_repl_generation",
                    "model": self.model,
                    "lane": lane,
                    "timestamp": metadata["timestamp"],
                    "prompt_hash": metadata["prompt_hash"],
                }
                try:
                    self.ledger_sink(ledger_entry)
                except Exception as e:
                    pass  # Silent fail - don't disrupt session

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
            temperature=0.3,
            max_tokens=512,
        )
        return make_llm_generate(config)

    def print_banner(self):
        """Print REPL banner."""
        print("\n" + "═" * 80)
        print("🔥 SEA-LION v45Ω FORGE REPL — Interactive Governance Console 🔥".center(80))
        print("═" * 80)
        print(f"\n📦 Model: {self.model}")
        print(f"🌐 API: {self.api_base}")
        print(f"📝 Ledger: {self.ledger_path}")
        print(f"🔍 StageInspector: {'ENABLED ✓' if self.verbose else 'DISABLED ✗'}")
        print(f"🔀 Dual-Stream: {'ENABLED ✓' if self.dual_stream else 'DISABLED ✗'}")
        print("\n💡 Commands: /verbose /both /stats /help /exit")
        print("═" * 80 + "\n")

    def print_help(self):
        """Print help message."""
        print("\n┌" + "─" * 78 + "┐")
        print("│ FORGE REPL COMMANDS".ljust(79) + "│")
        print("├" + "─" * 78 + "┤")
        print("│ /verbose   Toggle dev mode (show pipeline, metrics, timings)".ljust(79) + "│")
        print("│ /both      Toggle Dual-Stream (RAW vs GOVERNED side-by-side)".ljust(79) + "│")
        print("│ /stats     Show session statistics (verdicts, lanes)".ljust(79) + "│")
        print("│ /help      Show this help".ljust(79) + "│")
        print("│ /exit      Exit REPL".ljust(79) + "│")
        print("├" + "─" * 78 + "┤")
        print("│ NOTE: By default, only final response shown (minimal UX).".ljust(79) + "│")
        print("│       Use /verbose to see full governance pipeline.".ljust(79) + "│")
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
        if not self.verbose:
            return

        print("\n┌" + "─" * 78 + "┐")
        print("│ 🔬 PIPELINE TIMELINE (000→999) — StageInspector".ljust(79) + "│")
        print("├" + "─" * 78 + "┤")

        stages = state.stage_trace if hasattr(state, 'stage_trace') else []
        stage_times = state.stage_times if hasattr(state, 'stage_times') else {}

        if not stages:
            print("│ No stages recorded".ljust(79) + "│")
            print("└" + "─" * 78 + "┘\n")
            return

        # Calculate cumulative time
        start_time = stage_times.get(stages[0].split('_')[0], 0)

        for i, stage in enumerate(stages):
            stage_code = stage.split('_')[0] if '_' in stage else stage

            # Get duration for this stage
            duration = 0.0
            if i + 1 < len(stages):
                next_stage_code = stages[i + 1].split('_')[0]
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
            last_stage_code = stages[-1].split('_')[0]
            total_time = (stage_times.get(last_stage_code, start_time) - start_time) * 1000
            print("├" + "─" * 78 + "┤")
            print(f"│ ⏱️  Total Pipeline Time: {total_time:.1f}ms".ljust(79) + "│")

        print("└" + "─" * 78 + "┘\n")

    def print_trinity_metrics(self, state):
        """Print ΔΩΨ Trinity metrics (Clarity, Empathy, Vitality)."""
        if not hasattr(state, 'metrics') or state.metrics is None:
            print("⚠️  No metrics available\n")
            return

        m = state.metrics

        print("┌" + "─" * 78 + "┐")
        print("│ ✨ ΔΩΨ TRINITY METRICS — Clarity · Empathy · Vitality".ljust(79) + "│")
        print("├" + "─" * 78 + "┤")

        # Δ (Delta/Clarity) = Truth × ΔS
        delta_s = getattr(m, 'delta_s', 0.0) or 0.0
        truth = getattr(m, 'truth', 0.0) or 0.0
        delta = truth * delta_s if delta_s and truth else 0.0
        print(f"│ Δ (Clarity)   = Truth({truth:.3f}) × ΔS({delta_s:.3f}) = {delta:.3f}".ljust(79) + "│")

        # Ω (Omega/Empathy) = κᵣ × Amanah × RASA
        kappa_r = getattr(m, 'kappa_r', 0.0) or 0.0
        amanah = getattr(m, 'amanah', 0.0) or 0.0
        rasa = getattr(m, 'rasa', 0.0) or 0.0
        omega = kappa_r * amanah * rasa if kappa_r and amanah and rasa else 0.0
        print(f"│ Ω (Empathy)   = κᵣ({kappa_r:.3f}) × Amanah({amanah:.3f}) × RASA({rasa:.3f}) = {omega:.3f}".ljust(79) + "│")

        # Ψ (Psi/Vitality) = min(floor_ratios)
        psi = getattr(m, 'psi', 0.0) or 0.0
        print(f"│ Ψ (Vitality)  = {psi:.3f}".ljust(79) + "│")

        # Show GENIUS metrics if available
        if hasattr(state, 'verdict') and hasattr(state.verdict, 'genius_metrics'):
            gm = state.verdict.genius_metrics
            if gm:
                print("├" + "─" * 78 + "┤")
                g = getattr(gm, 'g', 0.0) or 0.0
                c_dark = getattr(gm, 'c_dark', 0.0) or 0.0
                print(f"│ G (Genius Index)      = {g:.3f} {'✓' if g >= 0.80 else '✗'}".ljust(79) + "│")
                print(f"│ C_dark (Dark Clever)  = {c_dark:.3f} {'✓' if c_dark < 0.30 else '✗'}".ljust(79) + "│")

        print("└" + "─" * 78 + "┘\n")

    def print_verdict_box(self, state):
        """Print 888_JUDGE verdict before response."""
        verdict_str = "UNKNOWN"
        verdict_emoji = "❓"

        if hasattr(state, 'verdict') and state.verdict:
            if hasattr(state.verdict, 'verdict'):
                # ApexVerdict
                verdict_str = str(state.verdict.verdict.value)
            elif hasattr(state.verdict, 'value'):
                verdict_str = str(state.verdict.value)
            else:
                verdict_str = str(state.verdict)

        # Emoji mapping
        verdict_map = {
            "SEAL": "✅",
            "VOID": "❌",
            "SABAR": "⏸️",
            "PARTIAL": "⚠️",
            "888_HOLD": "🛑",
        }
        verdict_emoji = verdict_map.get(verdict_str, "❓")

        # Update stats
        if verdict_str in self.verdicts:
            self.verdicts[verdict_str] += 1

        # Lane
        lane = getattr(state, 'applicability_lane', 'UNKNOWN')
        if lane in self.lanes:
            self.lanes[lane] += 1

        # Lane-specific truth threshold
        from arifos_core.enforcement.metrics import get_lane_truth_threshold
        lane_threshold = get_lane_truth_threshold(lane)

        # Actual truth score
        truth = getattr(state.metrics, 'truth', 0.0) if state.metrics else 0.0

        # Verdict reason
        reason = ""
        if hasattr(state.verdict, 'reason'):
            reason = state.verdict.reason[:60] + "..." if len(state.verdict.reason) > 60 else state.verdict.reason

        print("╔" + "═" * 78 + "╗")
        print("║ ⚖️  888_JUDGE VERDICT".ljust(79) + "║")
        print("╠" + "═" * 78 + "╣")
        print(f"║ {verdict_emoji} {verdict_str:<10} │ Lane: {lane:<10} │ Truth: {truth:.3f} / {lane_threshold:.2f}".ljust(79) + "║")
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

    def process_query(self, query: str):
        """Process user query through governed pipeline."""
        self.session_count += 1

        # FIX D: Gate telemetry behind verbose mode (default: minimal)
        if not self.verbose:
            print(f"\n🔥 Query #{self.session_count}")
        else:
            print(f"\n{'─' * 80}")
            print(f"🔥 Session #{self.session_count} │ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'─' * 80}")

        # Set verbose mode for StageInspector
        if self.verbose:
            os.environ["ARIFOS_VERBOSE"] = "1"
        else:
            os.environ["ARIFOS_VERBOSE"] = "0"

        # Run through governed pipeline
        try:
            state = self.pipeline.run(query)

            # Get verdict status
            verdict_str = "UNKNOWN"
            if hasattr(state, 'verdict') and state.verdict:
                if hasattr(state.verdict, 'verdict'):
                    verdict_str = str(state.verdict.verdict.value)
                elif hasattr(state.verdict, 'value'):
                    verdict_str = str(state.verdict.value)
                else:
                    verdict_str = str(state.verdict)

            lane = getattr(state, 'applicability_lane', 'UNKNOWN')

            # FIX A: Emission gate - only emit if SEAL
            # FIX B: FORGE rewrite loop for PARTIAL verdicts
            max_attempts = 2
            attempt = 0
            final_response = None
            final_verdict = verdict_str

            while attempt < max_attempts:
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

                        # Check if rewrite is compliant (<=100 chars)
                        if len(rewritten_response) <= 100:
                            final_response = rewritten_response
                            final_verdict = "SEAL"  # Rewrite succeeded
                            break
                        else:
                            # Rewrite failed, try once more
                            attempt += 1
                            if attempt >= max_attempts:
                                # Fallback to safe response
                                final_response = "Hi there! 👋 How can I help you today?"
                                final_verdict = "SEAL"
                    else:
                        # For non-PHATIC PARTIAL, emit with warning
                        final_response = state.raw_response or state.draft_response
                        final_verdict = "PARTIAL"
                        break

                elif verdict_str in {"VOID", "SABAR", "888_HOLD"}:
                    # Hard rejection: emit refusal message only
                    refusal_messages = {
                        "VOID": "❌ This request cannot be processed (constitutional violation).",
                        "SABAR": "⏸️ This request requires clarification. Please rephrase.",
                        "888_HOLD": "🛑 This request requires human review.",
                    }
                    final_response = refusal_messages.get(verdict_str, "⚠️ Request could not be completed.")
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

            # Display telemetry ONLY if verbose mode
            if self.verbose:
                self.print_pipeline_timeline(state)
                self.print_trinity_metrics(state)
                self.print_verdict_box(state)

            # Display final response (always shown)
            self.print_response_minimal(final_response, final_verdict, lane)

        except Exception as e:
            print(f"\n❌ Pipeline Error: {e}\n")
            import traceback
            if self.verbose:
                traceback.print_exc()

    def process_query_dual(self, query: str):
        """Process query in dual-stream mode (RAW vs GOVERNED side-by-side)."""
        self.session_count += 1

        print(f"\n{'═' * 80}")
        print(f"🔥 Session #{self.session_count} │ DUAL-STREAM MODE │ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'═' * 80}\n")

        # LEFT: RAW (ungoverned)
        print("┌" + "─" * 38 + "┬" + "─" * 39 + "┐")
        print("│ 🔓 RAW (Ungoverned)".ljust(39) + "│ 🔒 GOVERNED (v45Ω)".ljust(40) + "│")
        print("├" + "─" * 38 + "┼" + "─" * 39 + "┤")

        # Call RAW generator
        raw_response = ""
        raw_entropy = 0.0
        raw_time = 0.0

        try:
            import time
            raw_start = time.time()
            raw_response = self.raw_generate(query)
            raw_time = (time.time() - raw_start) * 1000
            raw_entropy = len(raw_response) / 1000.0  # Approx entropy
        except Exception as e:
            raw_response = f"[ERROR] {e}"

        # Call GOVERNED pipeline
        if self.verbose:
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
            state = self.pipeline.run(query)
            governed_time = (time.time() - gov_start) * 1000

            governed_response = state.raw_response or state.draft_response or "[No response]"
            governed_lane = getattr(state, 'applicability_lane', 'UNKNOWN')

            if hasattr(state, 'verdict') and state.verdict:
                if hasattr(state.verdict, 'verdict'):
                    governed_verdict = str(state.verdict.verdict.value)
                elif hasattr(state.verdict, 'value'):
                    governed_verdict = str(state.verdict.value)
                else:
                    governed_verdict = str(state.verdict)

            if state.metrics:
                governed_truth = getattr(state.metrics, 'truth', 0.0)
                governed_psi = getattr(state.metrics, 'psi', 0.0)

        except Exception as e:
            governed_response = f"[ERROR] {e}"

        # Update stats
        if governed_verdict in self.verdicts:
            self.verdicts[governed_verdict] += 1
        if governed_lane in self.lanes:
            self.lanes[governed_lane] += 1

        # Print side-by-side comparison
        # Stats row
        print(f"│ Chars: {len(raw_response):<6} ΔS: {raw_entropy:.3f}".ljust(39) +
              f"│ Lane: {governed_lane:<8} Truth: {governed_truth:.3f}".ljust(40) + "│")
        print(f"│ Time: {raw_time:.1f}ms".ljust(39) +
              f"│ Verdict: {governed_verdict}".ljust(40) + "│")
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
        print(f"│ RAW Entropy (ΔS): {raw_entropy:.3f} │ GOVERNED Ψ (Vitality): {governed_psi:.3f}".ljust(79) + "│")
        print(f"│ RAW Time: {raw_time:.1f}ms │ GOVERNED Time: {governed_time:.1f}ms ({governed_time/raw_time:.1f}x)".ljust(79) + "│")
        print(f"│ Governance Overhead: {governed_time - raw_time:.1f}ms".ljust(79) + "│")
        print("└" + "─" * 78 + "┘\n")

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

        return lines[:10]  # Limit to 10 lines for display

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
                if prompt.startswith('/'):
                    cmd = prompt.lower()
                    if cmd == '/exit':
                        print("\n👋 Exiting Forge REPL. DITEMPA BUKAN DIBERI.\n")
                        break
                    elif cmd == '/help':
                        self.print_help()
                    elif cmd == '/verbose':
                        self.verbose = not self.verbose
                        status = "ENABLED ✓" if self.verbose else "DISABLED ✗"
                        print(f"\n🔍 StageInspector: {status}\n")
                    elif cmd == '/both':
                        self.dual_stream = not self.dual_stream
                        status = "ENABLED ✓" if self.dual_stream else "DISABLED ✗"
                        print(f"\n🔀 Dual-Stream: {status}\n")
                    elif cmd == '/stats':
                        self.print_stats()
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
