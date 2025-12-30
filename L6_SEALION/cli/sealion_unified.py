#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sealion_unified.py — SEA-LION Unified Governance Console

A unified interface (UI + REPL) for SEA-LION v4 with real arifOS governance,
Trinity Display Architecture (ASI/AGI/APEX), web search tool, and thinking capability.

Trinity Modes:
- ASI (Ω) — Guardian mode (default): Clean response only
- AGI (Δ) — Architect mode (/agi): + Pipeline timeline + ΔΩΨ metrics
- APEX (Ψ) — Judge mode (/apex): + F1-F9 floors + Claims + Reasoning

Tools Available:
- Web Search — Search the web for current information
- Thinking — LLM can reason step-by-step before responding

Usage:
    # UI Mode (default - Gradio web interface)
    python scripts/sealion_unified.py

    # REPL Mode (command-line interface)
    python scripts/sealion_unified.py --cli

Environment Variables:
    SEALION_API_KEY - SEA-LION API key (required)
    SEALION_MODEL - Model ID (default: aisingapore/Gemma-SEA-LION-v4-27B-IT)
    ARIF_LLM_API_BASE - API base URL (default: https://api.sea-lion.ai/v1)
    ARIFOS_ENABLE_TOOLS - Enable tools (default: true)
    SERPER_API_KEY - Serper.dev API key for web search (optional)

DITEMPA BUKAN DIBERI — Forged, not given; truth must cool before it rules.
"""

import os
import sys
import json
import time
import argparse
import logging
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List, Tuple, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import Gradio (for UI mode)
try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False
    logging.warning("gradio not available - UI mode disabled (install: pip install gradio)")

# Try to import requests (for API calls and web search)
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    raise ImportError("requests library required (install: pip install requests)")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# =============================================================================
# NAMED CONSTANTS (F4-CODE: Clarity - No Magic Numbers)
# =============================================================================

# API Configuration
DEFAULT_MODEL = "aisingapore/Gemma-SEA-LION-v4-27B-IT"
DEFAULT_API_BASE = "https://api.sea-lion.ai/v1"
DEFAULT_MAX_TOKENS = 512
DEFAULT_TEMPERATURE = 0.3
PHATIC_TEMPERATURE = 0.5
PHATIC_MAX_TOKENS = 24
PHATIC_MAX_CHARS = 100
PHATIC_FALLBACK_GREETING = "Hi there! 👋 How can I help you today?"

# Chat Memory
DEFAULT_MAX_CONTEXT_TURNS = 6
HARD_MAX_TURNS = 200

# Retry Logic
MAX_RETRIES = 3
RETRY_DELAY_BASE = 1.0

# Display
MAX_DUAL_STREAM_LINES = 10
MAX_REWRITE_ATTEMPTS = 2

# Tools
ENABLE_TOOLS = os.getenv("ARIFOS_ENABLE_TOOLS", "true").lower() == "true"
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

# Import arifOS components
try:
    from arifos_core.system.pipeline import Pipeline
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False
    logger.warning("arifos_core.system.pipeline not available")

try:
    from arifos_core.connectors.litellm_gateway import make_llm_generate, LiteLLMConfig
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    logger.warning("arifos_core.connectors.litellm_gateway not available")

try:
    from arifos_core.system.apex_prime import Verdict
    VERDICT_ENUM_AVAILABLE = True
except ImportError:
    VERDICT_ENUM_AVAILABLE = False
    logger.warning("Verdict enum not available")

try:
    from arifos_core.utils.eye_sentinel import EyeSentinel
    EYE_AVAILABLE = True
except ImportError:
    EYE_AVAILABLE = False
    logger.warning("@EYE Sentinel not available")


# =============================================================================
# SHARED UTILITIES
# =============================================================================

def get_api_key() -> Optional[str]:
    """Resolve API key with priority order."""
    for var in ["SEALION_API_KEY", "ARIF_LLM_API_KEY", "LLM_API_KEY", "OPENAI_API_KEY"]:
        key = os.getenv(var)
        if key:
            return key
    return None


def estimate_tokens(text: str) -> int:
    """Rough token estimate (BPE approximation)."""
    return int(len(text) * 0.3)


def get_verdict_string(state) -> str:
    """Extract verdict string from pipeline state (F8-CODE: Governed pattern)."""
    if not hasattr(state, "verdict") or not state.verdict:
        return "UNKNOWN"

    if VERDICT_ENUM_AVAILABLE:
        if hasattr(state.verdict, "verdict"):
            if isinstance(state.verdict.verdict, Verdict):
                return state.verdict.verdict.value
            return str(state.verdict.verdict.value) if hasattr(state.verdict.verdict, "value") else str(state.verdict.verdict)
        elif isinstance(state.verdict, Verdict):
            return state.verdict.value

    if hasattr(state.verdict, "verdict"):
        return str(state.verdict.verdict.value) if hasattr(state.verdict.verdict, "value") else str(state.verdict.verdict)
    elif hasattr(state.verdict, "value"):
        return str(state.verdict.value)
    else:
        return str(state.verdict)


def get_empathetic_refusal(verdict: str, lane: str) -> str:
    """
    Generate empathetic, actionable refusal messages (F6-CODE: Empathy).
    Per Communication Law v45: No metrics leakage, human-centered.
    """
    if verdict == "VOID":
        if lane == "REFUSE":
            return "I can't help with that. If you want to understand the topic itself, I can explain it in general terms."
        else:
            return "I can't give reliable guidance on this. Can you rephrase your question or narrow it down?"
    elif verdict == "SABAR":
        return "Hold on - I want to make sure I understand. What are you actually trying to do here?"
    elif verdict == "888_HOLD":
        return "This needs your judgment, not mine. What kind of help are you looking for?"
    return "I'm having trouble with this request. Can you rephrase or break it down?"


# =============================================================================
# SEA-LION API CLIENT (Shared across all modes)
# =============================================================================

class SEALionClient:
    """Shared SEA-LION API client with retry logic and tool support."""

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        api_base: str = DEFAULT_API_BASE,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ):
        self.api_key = api_key
        self.model = model
        self.api_base = api_base
        self.temperature = temperature
        self.max_tokens = max_tokens

    def call(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """Call SEA-LION API with exponential backoff retry."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature or self.temperature,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60,
                )
                latency_ms = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    data = response.json()
                    message = data["choices"][0]["message"]

                    # Handle tool calls
                    tool_calls = message.get("tool_calls", [])

                    metadata = {
                        "model": self.model,
                        "latency_ms": latency_ms,
                        "usage": data.get("usage", {}),
                        "attempt": attempt,
                        "tool_calls": tool_calls,
                    }

                    return message.get("content", "").strip(), metadata

                elif response.status_code == 429 or response.status_code >= 500:
                    delay = RETRY_DELAY_BASE * (2 ** (attempt - 1))
                    logger.warning(f"Rate limited/Server error. Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    last_error = f"{response.status_code}"

                elif response.status_code in [401, 403]:
                    return (
                        f"[AUTH ERROR] Invalid API key (status {response.status_code})",
                        {"status_code": response.status_code, "error": response.text[:500]},
                    )

                else:
                    return (
                        f"[API ERROR] Status {response.status_code}",
                        {"status_code": response.status_code, "error": response.text[:500]},
                    )

            except requests.exceptions.Timeout:
                delay = RETRY_DELAY_BASE * (2 ** (attempt - 1))
                logger.warning(f"Timeout. Retrying in {delay:.1f}s...")
                time.sleep(delay)
                last_error = "Timeout"

            except requests.exceptions.ConnectionError as e:
                return f"[CONNECTION ERROR] {e}", {}

            except (ValueError, KeyError, TypeError) as e:
                return f"[PARSE ERROR] {e}", {}

        return f"[FAILED] Max retries exceeded. Last error: {last_error}", {}


# =============================================================================
# WEB SEARCH TOOL
# =============================================================================

class WebSearchClient:
    """Web search client using Serper.dev API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_base = "https://google.serper.dev/search"

    def search(self, query: str, num_results: int = 3) -> str:
        """
        Search the web and return formatted results.

        Returns:
            Formatted search results string or error message
        """
        if not self.api_key:
            return "[Web Search Unavailable] Set SERPER_API_KEY environment variable"

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "q": query,
            "num": num_results,
        }

        try:
            response = requests.post(self.api_base, headers=headers, json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                results = []

                # Extract organic results
                for item in data.get("organic", [])[:num_results]:
                    title = item.get("title", "")
                    link = item.get("link", "")
                    snippet = item.get("snippet", "")
                    results.append(f"• {title}\n  {snippet}\n  {link}")

                if results:
                    return "\n\n".join(results)
                else:
                    return "[No results found]"

            else:
                return f"[Search Error] Status {response.status_code}"

        except Exception as e:
            return f"[Search Error] {e}"


# =============================================================================
# TOOLS REGISTRY
# =============================================================================

def get_tools_schema() -> List[Dict]:
    """Return OpenAI function calling schema for available tools."""
    tools = []

    if ENABLE_TOOLS and SERPER_API_KEY:
        tools.append({
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for current information, news, or facts. Use this when you need up-to-date information or when asked about current events.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query (e.g., 'latest news about AI', 'current weather in Paris')"
                        }
                    },
                    "required": ["query"]
                }
            }
        })

    return tools


def execute_tool(tool_name: str, arguments: Dict, web_search_client: Optional[WebSearchClient] = None) -> str:
    """Execute a tool and return its result."""
    if tool_name == "web_search":
        if web_search_client:
            query = arguments.get("query", "")
            return web_search_client.search(query)
        else:
            return "[Web search unavailable]"

    return f"[Unknown tool: {tool_name}]"


# =============================================================================
# GOVERNANCE ENGINE
# =============================================================================

class GovernanceEngine:
    """Real arifOS governance engine with Trinity Display."""

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        api_base: str = DEFAULT_API_BASE,
        ledger_path: Optional[str] = None,
    ):
        self.api_key = api_key
        self.model = model
        self.api_base = api_base
        self.ledger_path = ledger_path or "cooling_ledger/sealion_unified_sessions.jsonl"

        # Trinity Display state
        self.agi_mode = False
        self.apex_mode = False

        # Session state
        self.session_id = f"sealion_unified_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        self.turns: List[Tuple[str, str]] = []
        self.max_context_turns = DEFAULT_MAX_CONTEXT_TURNS

        # Statistics
        self.session_count = 0
        self.verdicts = {"SEAL": 0, "VOID": 0, "PARTIAL": 0, "SABAR": 0, "888_HOLD": 0}
        self.lanes = {"PHATIC": 0, "SOFT": 0, "HARD": 0, "REFUSE": 0}
        self.session_start = datetime.now()
        self.last_state = None

        # Initialize clients
        self.sealion_client = SEALionClient(api_key, model, api_base)
        self.web_search_client = WebSearchClient(SERPER_API_KEY) if SERPER_API_KEY else None

        # Initialize governance components
        if not PIPELINE_AVAILABLE or not LITELLM_AVAILABLE:
            raise RuntimeError("Missing required dependencies: arifos_core.system.pipeline or litellm_gateway")

        # Create ledger sink
        self.ledger_sink = self._create_ledger_sink()

        # Initialize @EYE Sentinel
        self.eye_sentinel = None
        if EYE_AVAILABLE:
            try:
                self.eye_sentinel = EyeSentinel()
            except Exception as e:
                logger.warning(f"@EYE Sentinel init failed ({e})")

        # Create governed LLM generator
        self.governed_generate = self._create_governed_generator()

        # Create pipeline
        self.pipeline = Pipeline(
            llm_generate=self.governed_generate,
            context_retriever=self._get_chat_context_blocks,
            context_retriever_at_stage_111=True,
            ledger_sink=self.ledger_sink,
            eye_sentinel=self.eye_sentinel,
        )

    def _create_ledger_sink(self):
        """Create hash-chained JSONL ledger sink."""
        path = Path(self.ledger_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            from arifos_core.memory.cooling_ledger import append_entry
        except Exception as e:
            logger.warning(f"Cooling ledger unavailable ({e})")
            return lambda _: None

        def sink(entry: dict) -> None:
            try:
                append_entry(path, dict(entry))
            except Exception as e:
                logger.warning(f"Ledger append failed: {e}")

        return sink

    def _create_governed_generator(self):
        """Create governed SEA-LION generator with lane-aware configuration."""
        config = LiteLLMConfig(
            provider="openai",
            api_base=self.api_base,
            api_key=self.api_key,
            model=self.model,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
        )
        base_generate = make_llm_generate(config)

        phatic_generate = None

        def governed_wrapper(prompt: str, lane: str | None = None):
            nonlocal phatic_generate
            lane_value = lane or "UNKNOWN"

            # PHATIC lane optimization
            if lane_value == "PHATIC":
                if phatic_generate is None:
                    phatic_config = LiteLLMConfig(
                        provider="openai",
                        api_base=self.api_base,
                        api_key=self.api_key,
                        model=self.model,
                        temperature=PHATIC_TEMPERATURE,
                        max_tokens=PHATIC_MAX_TOKENS,
                    )
                    phatic_generate = make_llm_generate(phatic_config)

                phatic_prompt = f"{prompt}\n\nReply in ONE short sentence (max 15 words). Be friendly. No lists."
                response = phatic_generate(phatic_prompt)
            else:
                response = base_generate(prompt)

            metadata = {
                "model": self.model,
                "lane": lane_value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "prompt_hash": hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16],
            }

            if self.ledger_sink:
                ledger_entry = {
                    "event": "unified_generation",
                    "model": self.model,
                    "lane": lane_value,
                    "timestamp": metadata["timestamp"],
                    "prompt_hash": metadata["prompt_hash"],
                }
                try:
                    self.ledger_sink(ledger_entry)
                except Exception as e:
                    logger.warning(f"Ledger write failed: {e}")

            if lane is None:
                return response

            return response, metadata

        return governed_wrapper

    def _get_chat_context_blocks(self, _query: str) -> List[Dict]:
        """Return recent chat turns as pipeline context blocks."""
        if not self.turns or self.max_context_turns <= 0:
            return []

        recent = self.turns[-self.max_context_turns :]
        blocks: List[Dict] = []
        for user_text, assistant_text in reversed(recent):
            user_flat = " ".join(user_text.strip().split())[:90]
            assistant_flat = " ".join(assistant_text.strip().split())[:90]
            blocks.append({
                "type": "chat_turn",
                "text": f"U: {user_flat}\nA: {assistant_flat}",
            })
        return blocks

    def _store_turn(self, user_text: str, assistant_text: str) -> None:
        """Store a completed chat turn in memory (bounded)."""
        self.turns.append((user_text, assistant_text))
        if len(self.turns) > HARD_MAX_TURNS:
            self.turns = self.turns[-HARD_MAX_TURNS:]

    def _forge_rewrite_phatic(self, verbose_response: str) -> str:
        """Rewrite verbose response into PHATIC-compliant format."""
        sentences = verbose_response.split(".")
        if sentences and len(sentences[0].strip()) <= PHATIC_MAX_CHARS:
            return sentences[0].strip() + "."

        logger.debug(f"PHATIC rewrite fallback used (original: {len(verbose_response)} chars)")
        return PHATIC_FALLBACK_GREETING

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process user query through governed pipeline.

        Returns dict with:
            - response: Final response text
            - verdict: Verdict string
            - lane: Query lane
            - state: Full pipeline state (for Trinity Display)
        """
        self.session_count += 1

        # Enable verbose mode for StageInspector (if AGI/APEX)
        if self.agi_mode or self.apex_mode:
            os.environ["ARIFOS_VERBOSE"] = "1"
        else:
            os.environ["ARIFOS_VERBOSE"] = "0"

        try:
            # Run through governed pipeline
            state = self.pipeline.run(query, user_id=self.session_id)
            self.last_state = state

            verdict_str = get_verdict_string(state)
            lane = getattr(state, "applicability_lane", "UNKNOWN")

            # Emission gate + FORGE rewrite loop
            attempt = 0
            final_response = None
            final_verdict = verdict_str

            while attempt < MAX_REWRITE_ATTEMPTS:
                if verdict_str == "SEAL":
                    final_response = state.raw_response or state.draft_response
                    final_verdict = "SEAL"
                    break

                elif verdict_str == "PARTIAL":
                    if lane == "PHATIC":
                        original_response = state.raw_response or state.draft_response or ""
                        rewritten_response = self._forge_rewrite_phatic(original_response)

                        if len(rewritten_response) <= PHATIC_MAX_CHARS:
                            final_response = rewritten_response
                            final_verdict = "PARTIAL"
                            break
                        else:
                            attempt += 1
                            if attempt >= MAX_REWRITE_ATTEMPTS:
                                final_response = PHATIC_FALLBACK_GREETING
                                final_verdict = "PARTIAL"
                    else:
                        final_response = state.raw_response or state.draft_response
                        final_verdict = "PARTIAL"
                        break

                elif verdict_str in {"VOID", "SABAR", "888_HOLD"}:
                    final_response = get_empathetic_refusal(verdict_str, lane)
                    final_verdict = verdict_str
                    break

                else:
                    final_response = "⚠️ Unable to process request."
                    final_verdict = "UNKNOWN"
                    break

            # Update statistics
            if final_verdict in self.verdicts:
                self.verdicts[final_verdict] += 1
            if lane in self.lanes:
                self.lanes[lane] += 1

            # Store turn
            response_text = final_response or "⚠️ No response generated."
            self._store_turn(query, response_text)

            return {
                "response": response_text,
                "verdict": final_verdict,
                "lane": lane,
                "state": state,
            }

        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            return {
                "response": f"❌ Pipeline Error: {e}",
                "verdict": "UNKNOWN",
                "lane": "UNKNOWN",
                "state": None,
            }


# =============================================================================
# TRINITY DISPLAY FORMATTERS
# =============================================================================

def format_asi_response(response: str, verdict: str) -> str:
    """Format response for ASI mode (clean output only)."""
    verdict_emoji_map = {
        "SEAL": "✅",
        "PARTIAL": "⚠️",
        "VOID": "❌",
        "SABAR": "⏸️",
        "888_HOLD": "🛑",
    }
    emoji = verdict_emoji_map.get(verdict, "❓")

    return f"{emoji} {response}"


def format_agi_response(response: str, verdict: str, state) -> str:
    """Format response for AGI mode (pipeline + ΔΩΨ)."""
    output = []

    # Pipeline timeline
    if hasattr(state, "stage_trace") and state.stage_trace:
        output.append("┌" + "─" * 58 + "┐")
        output.append("│ 🔬 PIPELINE TIMELINE (000→999)".ljust(59) + "│")
        output.append("├" + "─" * 58 + "┤")

        stages = state.stage_trace
        stage_times = getattr(state, "stage_times", {})

        for i, stage in enumerate(stages[-5:]):  # Show last 5 stages
            stage_code = stage.split("_")[0] if "_" in stage else stage
            arrow = "└─>" if i == len(stages[-5:]) - 1 else "├─>"
            output.append(f"│ {arrow} {stage:<30}".ljust(59) + "│")

        output.append("└" + "─" * 58 + "┘")
        output.append("")

    # Trinity metrics (ΔΩΨ)
    m = getattr(state, "metrics", None)
    if m:
        truth = getattr(m, "truth", 0.0)
        delta_s = getattr(m, "delta_s", 0.0)
        delta = (truth + delta_s) / 2.0

        kappa_r = getattr(m, "kappa_r", 0.0)
        amanah = 1.0 if getattr(m, "amanah", False) else 0.0
        rasa = getattr(m, "rasa", 0.0)
        omega = kappa_r * amanah * rasa

        psi = getattr(m, "psi", 0.0)

        verdict_emoji = {"SEAL": "✅", "PARTIAL": "⚠️", "VOID": "❌", "SABAR": "⏸️", "888_HOLD": "🛑"}.get(verdict, "❓")
        output.append(f"🧠 Δ={delta:.2f}  ❤️ Ω={omega:.2f}  ⚖️ Ψ={psi:.2f}  {verdict_emoji}")
        output.append("")

    output.append(response)
    return "\n".join(output)


def format_apex_response(response: str, verdict: str, state) -> str:
    """Format response for APEX mode (full forensic)."""
    output = []

    # Start with AGI mode output
    agi_output = format_agi_response(response, verdict, state)
    lines = agi_output.split("\n")

    # Find where response starts (after metrics line)
    response_start_idx = -1
    for i, line in enumerate(lines):
        if line.startswith("🧠 Δ="):
            response_start_idx = i + 2  # Skip metrics line and empty line
            break

    if response_start_idx > 0:
        output.extend(lines[:response_start_idx])

    # F1-F9 Floors
    m = getattr(state, "metrics", None)
    if m:
        output.append("┌" + "─" * 58 + "┐")
        output.append("│ 🏛️  CONSTITUTIONAL FLOORS (F1-F9)".ljust(59) + "│")
        output.append("├" + "─" * 58 + "┤")

        floors = [
            ("F1 Amanah", getattr(m, "amanah", False), "LOCK", "boolean"),
            ("F2 Truth", getattr(m, "truth", 0.0), 0.99, "gte"),
            ("F4 ΔS", getattr(m, "delta_s", 0.0), 0.0, "gte"),
            ("F5 Peace²", getattr(m, "peace_squared", 0.0), 1.0, "gte"),
        ]

        for name, value, threshold, check_type in floors:
            if check_type == "boolean":
                status = "✓" if value else "✗"
                output.append(f"│ {name:<20} {str(value):<10} {status}".ljust(59) + "│")
            elif check_type == "gte":
                status = "✓" if value >= threshold else "✗"
                output.append(f"│ {name:<20} {value:.3f} {status} [≥{threshold}]".ljust(59) + "│")

        output.append("└" + "─" * 58 + "┘")
        output.append("")

    # Verdict box
    output.append("╔" + "═" * 58 + "╗")
    output.append("║ ⚖️  888_JUDGE VERDICT".ljust(59) + "║")
    output.append("╠" + "═" * 58 + "╣")

    verdict_emoji_map = {
        "SEAL": "✅",
        "PARTIAL": "⚠️",
        "VOID": "❌",
        "SABAR": "⏸️",
        "888_HOLD": "🛑",
    }
    emoji = verdict_emoji_map.get(verdict, "❓")
    lane = getattr(state, "applicability_lane", "UNKNOWN")
    truth = getattr(m, "truth", 0.0) if m else 0.0

    output.append(f"║ {emoji} {verdict:<10} │ Lane: {lane:<10}".ljust(59) + "║")
    output.append("╚" + "═" * 58 + "╝")
    output.append("")

    output.append(response)
    return "\n".join(output)


# =============================================================================
# UI MODE (Gradio)
# =============================================================================

def create_ui(governance_engine: GovernanceEngine):
    """Create Gradio UI with Trinity Display tabs."""
    if not GRADIO_AVAILABLE:
        print("❌ Gradio not available. Install with: pip install gradio")
        sys.exit(1)

    def chat_fn(message: str, history: List[Tuple[str, str]], mode: str) -> Tuple[str, List[Tuple[str, str]]]:
        """Process chat message and return response."""
        if not message.strip():
            return "", history

        # Set Trinity mode
        governance_engine.agi_mode = mode in ["AGI", "APEX"]
        governance_engine.apex_mode = mode == "APEX"

        # Process query
        result = governance_engine.process_query(message)

        # Format response based on mode
        if mode == "ASI":
            formatted_response = format_asi_response(result["response"], result["verdict"])
        elif mode == "AGI":
            formatted_response = format_agi_response(result["response"], result["verdict"], result["state"]) if result["state"] else result["response"]
        else:  # APEX
            formatted_response = format_apex_response(result["response"], result["verdict"], result["state"]) if result["state"] else result["response"]

        history.append((message, formatted_response))
        return "", history

    def clear_fn():
        """Clear chat history."""
        governance_engine.turns = []
        return []

    def get_stats():
        """Get session statistics."""
        elapsed = (datetime.now() - governance_engine.session_start).total_seconds()
        elapsed_str = f"{int(elapsed // 60)}m {int(elapsed % 60)}s"

        stats = f"""
**Session Statistics**

- Sessions: {governance_engine.session_count}
- Elapsed: {elapsed_str}

**Verdicts:**
- SEAL: {governance_engine.verdicts['SEAL']}
- PARTIAL: {governance_engine.verdicts['PARTIAL']}
- VOID: {governance_engine.verdicts['VOID']}
- SABAR: {governance_engine.verdicts['SABAR']}

**Lanes:**
- PHATIC: {governance_engine.lanes['PHATIC']}
- SOFT: {governance_engine.lanes['SOFT']}
- HARD: {governance_engine.lanes['HARD']}
- REFUSE: {governance_engine.lanes['REFUSE']}
"""
        return stats

    with gr.Blocks(title="🔥 SEA-LION Unified Governance Console", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🔥 SEA-LION v45Ω Unified Governance Console\n**Real arifOS Governance • Trinity Display Architecture • Tools Enabled**")

        with gr.Tabs():
            # Main chat tab
            with gr.Tab("💬 Chat"):
                with gr.Row():
                    mode_selector = gr.Radio(
                        choices=["ASI", "AGI", "APEX"],
                        value="ASI",
                        label="Trinity Display Mode",
                        info="ASI (Ω): Clean output only | AGI (Δ): + Pipeline + ΔΩΨ | APEX (Ψ): + Floors + Claims"
                    )

                chatbot = gr.Chatbot(height=500, show_label=False)
                msg = gr.Textbox(placeholder="Type your message...", label="Message", show_label=False)

                with gr.Row():
                    submit = gr.Button("Send 🔥", variant="primary")
                    clear = gr.Button("Clear")

                gr.Examples(
                    examples=[
                        "Hi, how are you?",
                        "What is the capital of Malaysia?",
                        "Search the web for latest news about AI",
                        "Siapakah Arif Fazil?",
                    ],
                    inputs=msg,
                )

                submit.click(chat_fn, [msg, chatbot, mode_selector], [msg, chatbot])
                msg.submit(chat_fn, [msg, chatbot, mode_selector], [msg, chatbot])
                clear.click(clear_fn, outputs=[chatbot])

            # Stats tab
            with gr.Tab("📊 Statistics"):
                stats_text = gr.Markdown(get_stats())
                refresh_stats = gr.Button("Refresh Stats")
                refresh_stats.click(lambda: get_stats(), outputs=[stats_text])

            # About tab
            with gr.Tab("ℹ️ About"):
                gr.Markdown("""
## Trinity Display Architecture (v45.0)

### ASI Mode (Ω) — Guardian (Default)
**Symbol:** Ω (Omega - Humility/Empathy field)
**Authority:** Public (no authorization required)
**What you see:** Clean response only, minimal UX

**Philosophy:** "Measure everything. Show nothing."

### AGI Mode (Δ) — Architect
**Symbol:** Δ (Delta - Clarity/Entropy Reduction field)
**Authority:** Developer (toggle with mode selector)
**What you see:** + Pipeline timeline + ΔΩΨ Trinity metrics (3 numbers)

**Trinity Metrics:**
- 🧠 Δ (Clarity) = (truth + delta_s) / 2
- ❤️ Ω (Empathy) = kappa_r × amanah × rasa
- ⚖️ Ψ (Vitality) = composite metric (lane-aware)

### APEX Mode (Ψ) — Judge
**Symbol:** Ψ (Psi - Vitality/Homeostasis field)
**Authority:** Auditor (toggle with mode selector)
**What you see:** + F1-F9 floors + Claims + Verdict reasoning

**Full Forensic Transparency:**
- Constitutional floors (F1-F9) with pass/fail
- Claim detection analysis
- Verdict reasoning
- W@W organ votes (if available)
- @EYE telemetry (if available)

---

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.
                """)

    return demo


# =============================================================================
# REPL MODE (CLI)
# =============================================================================

def run_repl(governance_engine: GovernanceEngine):
    """Run command-line REPL interface."""
    print("\n" + "═" * 80)
    print("🔥 SEA-LION v45Ω Unified Governance Console (REPL Mode) 🔥".center(80))
    print("═" * 80)
    print(f"\n📦 Model: {governance_engine.model}")
    print(f"🌐 API: {governance_engine.api_base}")
    print(f"🧠 Session: {governance_engine.session_id}")

    mode = "ASI (Guardian)" if not governance_engine.agi_mode else "AGI (Architect)"
    if governance_engine.apex_mode:
        mode = "APEX (Judge)"
    print(f"👁️  Mode: {mode}")

    print("\n💡 Commands: /agi /apex /stats /clear /help /exit")
    print("═" * 80 + "\n")

    while True:
        try:
            user_input = input("🔥 > ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith("/"):
                cmd = user_input.lower()

                if cmd == "/exit":
                    print("\n👋 Exiting. DITEMPA BUKAN DIBERI.\n")
                    break

                elif cmd == "/help":
                    print("\n💡 Available Commands:")
                    print("  /agi    - Toggle AGI Architect mode (pipeline + ΔΩΨ)")
                    print("  /apex   - Toggle APEX Judge mode (full forensic)")
                    print("  /stats  - Show session statistics")
                    print("  /clear  - Clear chat memory")
                    print("  /help   - Show this help")
                    print("  /exit   - Exit REPL\n")

                elif cmd == "/agi":
                    governance_engine.agi_mode = not governance_engine.agi_mode
                    status = "ENABLED ✓" if governance_engine.agi_mode else "DISABLED ✗"
                    print(f"\n🧠 AGI Mode (Architect): {status}\n")

                elif cmd == "/apex":
                    governance_engine.apex_mode = not governance_engine.apex_mode
                    status = "ENABLED ✓" if governance_engine.apex_mode else "DISABLED ✗"
                    print(f"\n⚖️  APEX Mode (Judge): {status}\n")
                    if governance_engine.apex_mode:
                        governance_engine.agi_mode = True  # APEX implies AGI

                elif cmd == "/stats":
                    elapsed = (datetime.now() - governance_engine.session_start).total_seconds()
                    elapsed_str = f"{int(elapsed // 60)}m {int(elapsed % 60)}s"

                    print("\n┌" + "─" * 78 + "┐")
                    print("│ SESSION STATISTICS".ljust(79) + "│")
                    print("├" + "─" * 78 + "┤")
                    print(f"│ Sessions: {governance_engine.session_count:<10} | Elapsed: {elapsed_str}".ljust(79) + "│")
                    print("├" + "─" * 78 + "┤")
                    print("│ Verdicts:".ljust(79) + "│")
                    for v, count in governance_engine.verdicts.items():
                        pct = (count / governance_engine.session_count * 100) if governance_engine.session_count > 0 else 0
                        print(f"│   {v:<10} {count:>3} ({pct:>5.1f}%)".ljust(79) + "│")
                    print("└" + "─" * 78 + "┘\n")

                elif cmd == "/clear":
                    governance_engine.turns = []
                    print("\n✅ Chat memory cleared.\n")

                else:
                    print(f"\n❌ Unknown command: {user_input}")
                    print("💡 Type /help for available commands\n")

                continue

            # Process query
            result = governance_engine.process_query(user_input)

            # Format and display response
            if governance_engine.apex_mode:
                formatted = format_apex_response(result["response"], result["verdict"], result["state"]) if result["state"] else result["response"]
            elif governance_engine.agi_mode:
                formatted = format_agi_response(result["response"], result["verdict"], result["state"]) if result["state"] else result["response"]
            else:
                formatted = format_asi_response(result["response"], result["verdict"])

            print(f"\n{formatted}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Type /exit to quit.\n")
        except EOFError:
            print("\n\n👋 Exiting REPL.\n")
            break


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Main entry point for SEA-LION Unified Console."""
    parser = argparse.ArgumentParser(description="SEA-LION Unified Governance Console")
    parser.add_argument("--cli", action="store_true", help="Run in REPL mode (default: UI mode)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model name")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="API base URL")
    args = parser.parse_args()

    # Get API key
    api_key = get_api_key()
    if not api_key:
        print("❌ ERROR: No API key found.")
        print("   Set one of: SEALION_API_KEY, ARIF_LLM_API_KEY, or add to .env")
        sys.exit(1)

    # Initialize governance engine
    try:
        governance_engine = GovernanceEngine(
            api_key=api_key,
            model=args.model,
            api_base=args.api_base,
        )
    except Exception as e:
        print(f"❌ Failed to initialize governance engine: {e}")
        sys.exit(1)

    # Launch UI or REPL
    if args.cli:
        run_repl(governance_engine)
    else:
        if not GRADIO_AVAILABLE:
            print("❌ Gradio not available for UI mode. Install with: pip install gradio")
            print("   Or run in REPL mode: python scripts/sealion_unified.py --cli")
            sys.exit(1)

        demo = create_ui(governance_engine)
        demo.launch()


if __name__ == "__main__":
    main()
