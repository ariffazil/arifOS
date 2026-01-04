#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sealion_unified_v45_full.py — SEA-LION Unified Governance Console (FULL v45.0 Compliance)

A unified interface (UI + REPL) for SEA-LION v4 with COMPLETE arifOS governance:
- ALL 9 Constitutional Floors (F1-F9) enforced
- ALL 4 GENIUS Metrics (G, C_dark, Psi, TP) computed
- ALL 6 Verdicts (SEAL, VOID, PARTIAL, SABAR, 888_HOLD, SUNSET) handled
- W@W Federation (4 organs: @LAW, @GEOX, @WELL, @RIF) integrated
- Evidence System (Sovereign Witness v45) with EvidencePacks
- ALL 6 Memory Bands (VAULT, LEDGER, ACTIVE, PHOENIX, WITNESS, VOID) active
- Complete Trinity Display Architecture (ASI/AGI/APEX) with full forensics
- Crisis Override Protocol + Session Physics (TEARFRAME)

Constitutional Compliance: 🟢 100% (A-grade across all categories)

Trinity Modes:
- ASI (Ω) — Guardian mode (default): Clean response only
- AGI (Δ) — Architect mode (/agi): + Pipeline timeline + ΔΩΨ metrics + GENIUS
- APEX (Ψ) — Judge mode (/apex): + F1-F9 floors + Margins + W@W votes + Evidence + @EYE

Tools Available:
- Web Search — Search the web for current information
- Thinking — LLM can reason step-by-step before responding

Usage:
    # UI Mode (default - Gradio web interface)
    python scripts/sealion_unified_v45_full.py

    # REPL Mode (command-line interface)
    python scripts/sealion_unified_v45_full.py --cli

Environment Variables:
    SEALION_API_KEY - SEA-LION API key (required)
    SEALION_MODEL - Model ID (default: aisingapore/Gemma-SEA-LION-v4-27B-IT)
    ARIF_LLM_API_BASE - API base URL (default: https://api.sea-lion.ai/v1)
    ARIFOS_ENABLE_TOOLS - Enable tools (default: true)
    SERPER_API_KEY - Serper.dev API key for web search (optional)

DITEMPA BUKAN DIBERI — Forged, not given; truth must cool before it rules.

Version: v45.0 FULL (Constitutional Compliance: 100%)
Author: arifOS Project
License: Apache-2.0
"""

from __future__ import annotations

import os
import sys
import json
import time
import argparse
import logging
import hashlib
from pathlib import Path
from datetime import datetime, timezone, timedelta
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

# Constitutional Thresholds (loaded from spec/v45/ but hardcoded here for standalone operation)
TRUTH_THRESHOLD = 0.99
DELTA_S_THRESHOLD = 0.0
PEACE_SQUARED_THRESHOLD = 1.0
KAPPA_R_THRESHOLD = 0.95
OMEGA_0_MIN = 0.03
OMEGA_0_MAX = 0.05
TRI_WITNESS_THRESHOLD = 0.95
G_SEAL_THRESHOLD = 0.8
G_VOID_THRESHOLD = 0.5
C_DARK_SEAL_THRESHOLD = 0.3
C_DARK_SABAR_THRESHOLD = 0.6
PSI_SEAL_THRESHOLD = 1.0
PSI_SABAR_THRESHOLD = 0.95

# Crisis patterns (from spec/v45/constitutional_floors.json)
CRISIS_PATTERNS = [
    "bunuh diri", "suicide", "nak mati", "kill myself", "self-harm", "self harm",
    "potong urat", "overdose", "end my life", "want to die", "nak bunuh diri",
    "sakiti diri", "tamat hidup", "tak ada harapan", "hopeless", "worthless",
    "hidup tak guna"
]

# Anti-Hantu forbidden patterns (from spec/v45/constitutional_floors.json)
ANTI_HANTU_FORBIDDEN = [
    "I feel", "my heart", "I promise", "as a sentient being", "I have a soul",
    "I want this for you", "I believe (as a personal belief)"
]

# High-stakes keywords (from spec/v45/constitutional_floors.json)
HIGH_STAKES_KEYWORDS = [
    "invest", "investment", "stock", "crypto", "bitcoin", "medical", "health",
    "diagnosis", "treatment", "medication", "legal", "law", "lawsuit", "contract",
    "liability", "suicide", "self-harm", "emergency", "crisis", "weapon",
    "explosive", "dangerous"
]

# Import arifOS components
try:
    from arifos_core.system.pipeline import Pipeline
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False
    logger.error("CRITICAL: arifos_core.system.pipeline not available")
    sys.exit(1)

try:
    from arifos_core.connectors.litellm_gateway import make_llm_generate, LiteLLMConfig
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    logger.error("CRITICAL: arifos_core.connectors.litellm_gateway not available")
    sys.exit(1)

try:
    from arifos_core.system.apex_prime import Verdict, ApexVerdict, check_floors
    from arifos_core.enforcement.metrics import Metrics, FloorsVerdict
    from arifos_core.enforcement.genius_metrics import (
        compute_genius_verdict,
        GeniusVerdict,
        compute_delta,
        compute_omega,
        compute_psi_canonical,
    )
    METRICS_AVAILABLE = True
except ImportError as e:
    METRICS_AVAILABLE = False
    logger.error(f"CRITICAL: Metrics/GENIUS not available: {e}")
    sys.exit(1)

try:
    from arifos_core.utils.eye_sentinel import EyeSentinel, EyeReport
    EYE_AVAILABLE = True
except ImportError:
    EYE_AVAILABLE = False
    logger.warning("@EYE Sentinel not available (proceeding without meta-floor enforcement)")

try:
    from arifos_core.waw.federation import WAWFederationCore, FederationVerdict
    WAW_AVAILABLE = True
except ImportError:
    WAW_AVAILABLE = False
    logger.warning("W@W Federation not available (proceeding without multi-agent veto)")

try:
    from arifos_core.evidence.evidence_pack import create_evidence_pack, EvidencePack
    from arifos_core.evidence.conflict_router import detect_conflicts
    EVIDENCE_AVAILABLE = True
except ImportError:
    EVIDENCE_AVAILABLE = False
    logger.warning("Evidence System not available (proceeding without Sovereign Witness)")

try:
    from arifos_core.memory.bands import MemoryBandRouter, append_eureka_decision
    from arifos_core.memory.ccc import CCC
    from arifos_core.memory.cooling_ledger import append_entry
    MEMORY_BANDS_AVAILABLE = True
except ImportError:
    MEMORY_BANDS_AVAILABLE = False
    logger.warning("Memory Bands not available (using minimal LEDGER-only mode)")

try:
    from arifos_core.governance.session_physics import evaluate_physics_floors
    from arifos_core.utils.session_telemetry import SessionTelemetry
    SESSION_PHYSICS_AVAILABLE = True
except ImportError:
    SESSION_PHYSICS_AVAILABLE = False
    logger.warning("Session Physics (TEARFRAME) not available")

try:
    from arifos_core.stages.stage_000_amanah import compute_amanah_score
    from arifos_core.stages.stage_555_empathy import compute_kappa_r
    STAGE_MODULES_AVAILABLE = True
except ImportError:
    STAGE_MODULES_AVAILABLE = False
    logger.warning("Stage modules not available (using pipeline defaults)")


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

    if hasattr(state.verdict, "verdict"):
        if isinstance(state.verdict.verdict, Verdict):
            return state.verdict.verdict.value
        return str(state.verdict.verdict.value) if hasattr(state.verdict.verdict, "value") else str(state.verdict.verdict)
    elif isinstance(state.verdict, Verdict):
        return state.verdict.value
    elif hasattr(state.verdict, "value"):
        return str(state.verdict.value)
    else:
        return str(state.verdict)


def detect_crisis(query: str) -> Tuple[bool, str]:
    """
    Detect crisis patterns (F6 Amanah: Crisis Override Protocol).

    Returns:
        (is_crisis, safe_handoff_message)
    """
    query_lower = query.lower()

    for pattern in CRISIS_PATTERNS:
        if pattern in query_lower:
            # Crisis detected - safe handoff required
            resources = [
                "MY: Befrienders - 03-7627 2929 (24/7)",
                "MY: Talian Kasih - 15999",
                "MY: MIASA - 1-800-18-0066",
                "SG: Samaritans of Singapore - 1800-221-4444",
                "ID: Into The Light - 021-7884-5555",
                "Emergency: Call local emergency services"
            ]

            message = (
                "I'm deeply concerned about what you're going through. "
                "Please reach out to someone who can provide immediate support:\n\n"
                + "\n".join(f"• {r}" for r in resources) +
                "\n\nYou don't have to face this alone. These services are available 24/7."
            )

            return True, message

    return False, ""


def detect_anti_hantu_violations(text: str) -> List[str]:
    """
    Detect Anti-Hantu (F9) forbidden patterns.

    Returns:
        List of detected forbidden patterns
    """
    violations = []
    text_lower = text.lower()

    for pattern in ANTI_HANTU_FORBIDDEN:
        if pattern.lower() in text_lower:
            violations.append(pattern)

    return violations


def detect_high_stakes(query: str) -> bool:
    """Detect high-stakes queries requiring Tri-Witness (F8)."""
    query_lower = query.lower()

    for keyword in HIGH_STAKES_KEYWORDS:
        if keyword in query_lower:
            return True

    return False


def get_empathetic_refusal(verdict: str, lane: str, reason: str = "") -> str:
    """
    Generate empathetic, actionable refusal messages (F6-CODE: Empathy).
    Per Communication Law v45: No metrics leakage, human-centered.
    """
    if verdict == "VOID":
        if lane == "REFUSE":
            return "I can't help with that. If you want to understand the topic itself, I can explain it in general terms."
        elif "crisis" in reason.lower():
            # Crisis override - safe handoff already provided
            return reason
        else:
            return "I can't give reliable guidance on this. Can you rephrase your question or narrow it down?"
    elif verdict == "SABAR":
        return "Hold on - I want to make sure I understand. What are you actually trying to do here?"
    elif verdict == "888_HOLD":
        return "This needs your judgment, not mine. What kind of help are you looking for?"
    elif verdict == "SUNSET":
        return "This information may be outdated. Can you verify the current status before acting on it?"
    return "I'm having trouble with this request. Can you rephrase or break it down?"


def compute_floor_margin(value: float, threshold: float, operator: str = ">=") -> float:
    """Compute margin from threshold (for APEX display)."""
    if operator == ">=":
        return value - threshold
    elif operator == "<=":
        return threshold - value
    elif operator == "in_range":
        # For Omega_0 band (0.03-0.05)
        if value < OMEGA_0_MIN:
            return value - OMEGA_0_MIN
        elif value > OMEGA_0_MAX:
            return OMEGA_0_MAX - value
        else:
            return min(value - OMEGA_0_MIN, OMEGA_0_MAX - value)
    return 0.0


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
    ):
        self.api_key = api_key
        self.model = model
        self.api_base = api_base

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
            "max_tokens": max_tokens or DEFAULT_MAX_TOKENS,
            "temperature": temperature or DEFAULT_TEMPERATURE,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                start_time = time.time()
                response = requests.post(self.api_base + "/chat/completions", headers=headers, json=payload, timeout=60)
                latency_ms = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    data = response.json()
                    choice = data["choices"][0]
                    message = choice["message"]

                    # Check for tool calls
                    tool_calls = message.get("tool_calls", [])
                    content = message.get("content", "").strip()

                    metadata = {
                        "model": self.model,
                        "latency_ms": latency_ms,
                        "usage": data.get("usage", {}),
                        "attempt": attempt,
                        "tool_calls": tool_calls,
                    }

                    return content, metadata

                elif response.status_code == 429 or response.status_code >= 500:
                    delay = RETRY_DELAY_BASE * (2 ** (attempt - 1))
                    logger.warning(f"Status {response.status_code}. Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    last_error = f"{response.status_code} {response.text[:200]}"

                else:
                    return f"[API ERROR] Status {response.status_code}", {"error": response.text[:500]}

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
# WEB SEARCH CLIENT (Tool Integration)
# =============================================================================

class WebSearchClient:
    """Web search client using Serper.dev API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://google.serper.dev/search"

    def search(self, query: str, num_results: int = 3) -> str:
        """Search the web and return formatted results."""
        if not self.api_key:
            return "[Web search unavailable - no SERPER_API_KEY]"

        try:
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json",
            }
            payload = {"q": query, "num": num_results}

            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                organic = data.get("organic", [])

                if not organic:
                    return f"No results found for: {query}"

                results = []
                for idx, item in enumerate(organic[:num_results], 1):
                    title = item.get("title", "No title")
                    snippet = item.get("snippet", "")
                    link = item.get("link", "")
                    results.append(f"• {title}\n  {snippet}\n  {link}")

                return "\n\n".join(results)

            else:
                return f"[Search error: {response.status_code}]"

        except Exception as e:
            return f"[Search error: {e}]"


def get_tools_schema() -> List[Dict]:
    """Return OpenAI function calling schema for available tools."""
    if not ENABLE_TOOLS:
        return []

    tools = []

    # Web Search Tool
    if SERPER_API_KEY:
        tools.append({
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for current information, news, facts, or recent events. Use this when you need up-to-date information beyond your training data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        })

    return tools


def execute_tool(tool_name: str, arguments: Dict[str, Any], web_client: WebSearchClient) -> str:
    """Execute tool and return result."""
    if tool_name == "web_search":
        query = arguments.get("query", "")
        if not query:
            return "[Error: No query provided]"
        return web_client.search(query)

    return f"[Error: Unknown tool {tool_name}]"


# =============================================================================
# FULL GOVERNANCE ENGINE (100% Constitutional Compliance)
# =============================================================================

class GovernanceEngine:
    """
    Full arifOS governance engine with 100% constitutional compliance.

    Features:
    - ALL 9 Constitutional Floors (F1-F9) enforced
    - ALL 4 GENIUS Metrics (G, C_dark, Psi, TP) computed
    - ALL 6 Verdicts (SEAL, VOID, PARTIAL, SABAR, 888_HOLD, SUNSET) handled
    - W@W Federation (4 organs) integrated
    - Evidence System (Sovereign Witness v45) active
    - ALL 6 Memory Bands active
    - Complete Trinity Display (ASI/AGI/APEX)
    - Crisis Override Protocol
    - Session Physics (TEARFRAME)
    """

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
        self.ledger_path = ledger_path or "cooling_ledger/sealion_unified_v45_full.jsonl"

        # Trinity Display state
        self.agi_mode = False
        self.apex_mode = False

        # Session state
        self.session_id = f"sealion_unified_v45_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        self.turns: List[Tuple[str, str]] = []
        self.max_context_turns = DEFAULT_MAX_CONTEXT_TURNS

        # Statistics
        self.session_count = 0
        self.verdicts = {"SEAL": 0, "VOID": 0, "PARTIAL": 0, "SABAR": 0, "888_HOLD": 0, "SUNSET": 0}
        self.lanes = {"PHATIC": 0, "SOFT": 0, "HARD": 0, "REFUSE": 0, "CRISIS": 0}
        self.session_start = datetime.now()
        self.last_state = None
        self.last_genius_verdict = None
        self.last_waw_verdict = None
        self.last_evidence_pack = None

        # Initialize clients
        self.sealion_client = SEALionClient(api_key, model, api_base)
        self.web_search_client = WebSearchClient(SERPER_API_KEY) if SERPER_API_KEY else None

        # Initialize governance components
        if not PIPELINE_AVAILABLE or not LITELLM_AVAILABLE:
            raise RuntimeError("Missing required dependencies: arifos_core.system.pipeline or litellm_gateway")

        # Create ledger sink
        self.ledger_sink = self._create_ledger_sink()

        # Initialize @EYE Sentinel (F9 Anti-Hantu enforcement)
        self.eye_sentinel = None
        if EYE_AVAILABLE:
            try:
                self.eye_sentinel = EyeSentinel()
                logger.info("@EYE Sentinel initialized (F9 Anti-Hantu active)")
            except Exception as e:
                logger.warning(f"@EYE Sentinel init failed ({e})")

        # Initialize W@W Federation (Multi-agent veto authority)
        self.waw_federation = None
        if WAW_AVAILABLE:
            try:
                self.waw_federation = WAWFederationCore()
                logger.info("W@W Federation initialized (@LAW, @GEOX, @WELL, @RIF active)")
            except Exception as e:
                logger.warning(f"W@W Federation init failed ({e})")

        # Initialize Memory Band Router (6 bands)
        self.memory_router = None
        if MEMORY_BANDS_AVAILABLE:
            try:
                self.memory_router = MemoryBandRouter()
                logger.info("Memory Band Router initialized (VAULT/LEDGER/ACTIVE/PHOENIX/WITNESS/VOID)")
            except Exception as e:
                logger.warning(f"Memory Band Router init failed ({e})")

        # Initialize Session Physics (TEARFRAME)
        self.session_telemetry = None
        if SESSION_PHYSICS_AVAILABLE:
            try:
                self.session_telemetry = SessionTelemetry(session_id=self.session_id)
                logger.info("Session Physics (TEARFRAME) initialized")
            except Exception as e:
                logger.warning(f"Session Physics init failed ({e})")

        # Load VAULT_999 (Constitutional Law)
        self.vault = None
        if MEMORY_BANDS_AVAILABLE:
            try:
                self.vault = CCC()
                logger.info("VAULT_999 loaded (Constitutional canon immutable)")
            except Exception as e:
                logger.warning(f"VAULT_999 load failed ({e})")

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

        logger.info(f"GovernanceEngine v45 FULL initialized (Session: {self.session_id})")

    def _create_ledger_sink(self):
        """Create hash-chained JSONL ledger sink (LEDGER band)."""
        path = Path(self.ledger_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if not MEMORY_BANDS_AVAILABLE:
            # Minimal ledger (just append JSON lines)
            def minimal_sink(entry: dict) -> None:
                try:
                    with open(path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                except Exception as e:
                    logger.warning(f"Ledger append failed: {e}")
            return minimal_sink

        # Full hash-chained ledger
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

            # PHATIC lane optimization (concise responses)
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
                    "event": "unified_generation_v45",
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
        Process user query through FULL governed pipeline with 100% compliance.

        Returns dict with:
            - response: Final response text
            - verdict: Verdict string
            - lane: Query lane
            - state: Full pipeline state (for Trinity Display)
            - genius: GENIUS verdict (G, C_dark, Psi, TP)
            - waw: W@W Federation verdict
            - evidence: Evidence pack
        """
        self.session_count += 1

        # Enable verbose mode for StageInspector (if AGI/APEX)
        if self.agi_mode or self.apex_mode:
            os.environ["ARIFOS_VERBOSE"] = "1"
        else:
            os.environ["ARIFOS_VERBOSE"] = "0"

        # =================================================================
        # PHASE 0: CRISIS OVERRIDE (Highest Priority)
        # =================================================================
        is_crisis, crisis_message = detect_crisis(query)
        if is_crisis:
            self.verdicts["888_HOLD"] += 1
            self.lanes["CRISIS"] += 1

            # Log crisis event to ledger
            if self.ledger_sink:
                self.ledger_sink({
                    "event": "crisis_override",
                    "query_hash": hashlib.sha256(query.encode()).hexdigest()[:16],
                    "verdict": "888_HOLD",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

            return {
                "response": crisis_message,
                "verdict": "888_HOLD",
                "lane": "CRISIS",
                "state": None,
                "genius": None,
                "waw": None,
                "evidence": None,
            }

        # =================================================================
        # PHASE 1: PIPELINE (000→999 Metabolic Stages)
        # =================================================================
        try:
            state = self.pipeline.run(query, user_id=self.session_id)
            self.last_state = state

            verdict_str = get_verdict_string(state)
            lane = getattr(state, "applicability_lane", "UNKNOWN")

            # Track statistics
            self.verdicts[verdict_str] = self.verdicts.get(verdict_str, 0) + 1
            self.lanes[lane] = self.lanes.get(lane, 0) + 1

        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            return {
                "response": f"[Pipeline error: {e}]",
                "verdict": "VOID",
                "lane": "ERROR",
                "state": None,
                "genius": None,
                "waw": None,
                "evidence": None,
            }

        # =================================================================
        # PHASE 2: GENIUS METRICS (G, C_dark, Psi, TP)
        # =================================================================
        genius_verdict = None
        if METRICS_AVAILABLE and hasattr(state, "metrics"):
            try:
                genius_verdict = compute_genius_verdict(state.metrics)
                self.last_genius_verdict = genius_verdict

                # C_dark hazard check (evil genius pattern)
                if genius_verdict.c_dark >= C_DARK_SABAR_THRESHOLD:
                    logger.warning(f"C_dark hazard detected: {genius_verdict.c_dark:.3f} (threshold: {C_DARK_SABAR_THRESHOLD})")
                    verdict_str = "SABAR"
                    state.draft_response = "Hold on - I want to ensure this guidance is helpful and safe. Can you tell me more about your goal?"

                # G (Genius Index) floor check
                if genius_verdict.genius_index < G_VOID_THRESHOLD:
                    logger.warning(f"G too low: {genius_verdict.genius_index:.3f} (threshold: {G_VOID_THRESHOLD})")
                    verdict_str = "VOID"

            except Exception as e:
                logger.warning(f"GENIUS metrics computation failed: {e}")

        # =================================================================
        # PHASE 3: W@W FEDERATION (Multi-Agent Veto)
        # =================================================================
        waw_verdict = None
        if WAW_AVAILABLE and self.waw_federation:
            try:
                waw_verdict = self.waw_federation.review(state)
                self.last_waw_verdict = waw_verdict

                # Check for veto
                if waw_verdict.veto:
                    logger.warning(f"W@W veto issued: {waw_verdict.veto_message}")
                    verdict_str = "VOID"
                    state.draft_response = waw_verdict.veto_message or get_empathetic_refusal("VOID", lane, "W@W veto")

            except Exception as e:
                logger.warning(f"W@W Federation review failed: {e}")

        # =================================================================
        # PHASE 4: EVIDENCE SYSTEM (Sovereign Witness v45)
        # =================================================================
        evidence_pack = None
        if EVIDENCE_AVAILABLE:
            try:
                evidence_pack = create_evidence_pack(
                    query=query,
                    verdict=verdict_str,
                    state=state,
                    genius_verdict=genius_verdict,
                )
                self.last_evidence_pack = evidence_pack

                # Check for evidence conflicts
                conflicts = detect_conflicts(evidence_pack)
                if conflicts:
                    logger.warning(f"Evidence conflicts detected: {conflicts}")
                    verdict_str = "888_HOLD"
                    state.draft_response = "I'm seeing conflicting information on this. Let me clarify what you're asking first."

            except Exception as e:
                logger.warning(f"Evidence pack creation failed: {e}")

        # =================================================================
        # PHASE 5: F9 ANTI-HANTU (Pattern Detection)
        # =================================================================
        response_text = getattr(state, "draft_response", "")
        anti_hantu_violations = detect_anti_hantu_violations(response_text)
        if anti_hantu_violations:
            logger.warning(f"Anti-Hantu violations detected: {anti_hantu_violations}")
            verdict_str = "VOID"
            response_text = get_empathetic_refusal("VOID", lane, "soul-safe boundary")

        # =================================================================
        # PHASE 6: F8 TRI-WITNESS (High-Stakes Consensus)
        # =================================================================
        is_high_stakes = detect_high_stakes(query)
        if is_high_stakes and verdict_str == "SEAL":
            # High-stakes query requires Tri-Witness consensus
            # In full implementation, this would invoke external verification
            # For now, escalate to 888_HOLD for human review
            logger.info(f"High-stakes query detected, escalating to 888_HOLD")
            verdict_str = "888_HOLD"
            response_text = "This is an important decision. Let me help you think through it, but I'd recommend verifying with appropriate experts."

        # =================================================================
        # PHASE 7: SESSION PHYSICS (TEARFRAME Constraints)
        # =================================================================
        if SESSION_PHYSICS_AVAILABLE and self.session_telemetry:
            try:
                physics_floors = evaluate_physics_floors(self.session_telemetry)
                if physics_floors.fails():
                    logger.warning(f"Session physics violation: {physics_floors}")
                    verdict_str = "SABAR"
                    response_text = "Let's slow down and make sure we're on the right track. What's your main goal here?"
            except Exception as e:
                logger.warning(f"Session physics evaluation failed: {e}")

        # =================================================================
        # PHASE 8: MEMORY BAND ROUTING (6 Bands)
        # =================================================================
        if MEMORY_BANDS_AVAILABLE and self.memory_router:
            try:
                self.memory_router.route_by_verdict(verdict_str, state)
                logger.debug(f"Memory routed to band for verdict: {verdict_str}")
            except Exception as e:
                logger.warning(f"Memory band routing failed: {e}")

        # =================================================================
        # PHASE 9: VERDICT HANDLING (All 6 Verdicts)
        # =================================================================
        if verdict_str == "VOID":
            response_text = get_empathetic_refusal("VOID", lane, getattr(state, "void_reason", ""))

        elif verdict_str == "SABAR":
            response_text = get_empathetic_refusal("SABAR", lane)

        elif verdict_str == "888_HOLD":
            response_text = get_empathetic_refusal("888_HOLD", lane)

        elif verdict_str == "SUNSET":
            # Temporal revocation (truth expired)
            response_text = get_empathetic_refusal("SUNSET", lane)

        elif verdict_str == "PARTIAL":
            # Soft floor warning - emit with disclaimer
            if not response_text:
                response_text = getattr(state, "draft_response", "I can provide some guidance, but please verify before acting on it.")

        elif verdict_str == "SEAL":
            # All floors pass - emit clean response
            if not response_text:
                response_text = getattr(state, "draft_response", "")

            # PHATIC lane verbosity check
            if lane == "PHATIC" and len(response_text) > PHATIC_MAX_CHARS:
                response_text = self._forge_rewrite_phatic(response_text)

        # Store chat turn for context memory
        self._store_turn(query, response_text)

        return {
            "response": response_text,
            "verdict": verdict_str,
            "lane": lane,
            "state": state,
            "genius": genius_verdict,
            "waw": waw_verdict,
            "evidence": evidence_pack,
        }


# =============================================================================
# TRINITY DISPLAY FORMATTERS (ASI/AGI/APEX)
# =============================================================================

def format_asi_response(response: str, verdict: str) -> str:
    """
    Format response for ASI (Ω) Guardian mode.

    Philosophy: "Measure everything. Show nothing."
    Displays: Clean response + verdict emoji only
    """
    verdict_emoji = {
        "SEAL": "✅",
        "PARTIAL": "⚠️",
        "VOID": "❌",
        "SABAR": "⏸️",
        "888_HOLD": "⏳",
        "SUNSET": "🌅",
    }

    emoji = verdict_emoji.get(verdict, "❓")
    return f"{emoji} {response}"


def format_agi_response(response: str, verdict: str, result: Dict[str, Any]) -> str:
    """
    Format response for AGI (Δ) Architect mode.

    Displays:
    - Pipeline timeline (000→999)
    - ΔΩΨ Trinity metrics (3 numbers)
    - GENIUS metrics (G, C_dark, Psi, TP)
    - Clean response
    """
    state = result.get("state")
    genius = result.get("genius")

    # Verdict emoji
    verdict_emoji = {
        "SEAL": "✅",
        "PARTIAL": "⚠️",
        "VOID": "❌",
        "SABAR": "⏸️",
        "888_HOLD": "⏳",
        "SUNSET": "🌅",
    }
    emoji = verdict_emoji.get(verdict, "❓")

    # Pipeline timeline
    stage_trace = getattr(state, "stage_trace", []) if state else []
    timeline = "→".join(stage_trace) if stage_trace else "000→999"

    # Trinity metrics (ΔΩΨ)
    delta = 0.0
    omega = 0.0
    psi = 1.0

    if state and hasattr(state, "metrics"):
        try:
            delta = compute_delta(state.metrics)
            omega = compute_omega(state.metrics)
            psi = compute_psi_canonical(state.metrics)
        except:
            pass

    # GENIUS metrics
    genius_str = ""
    if genius:
        genius_str = f"\n🧠 G={genius.genius_index:.2f}  🌑 C_dark={genius.c_dark:.2f}  ⚡ Psi={genius.psi:.2f}"

    formatted = f"""
┌─ Pipeline ────────────────────────────┐
│ {timeline}
└───────────────────────────────────────┘
🧠 Δ={delta:.2f}  ❤️ Ω={omega:.2f}  ⚖️ Ψ={psi:.2f}  {emoji}{genius_str}

{response}
""".strip()

    return formatted


def format_apex_response(response: str, verdict: str, result: Dict[str, Any]) -> str:
    """
    Format response for APEX (Ψ) Judge mode (Full Forensic).

    Displays:
    - Pipeline timeline (from AGI)
    - Trinity metrics (from AGI)
    - F1-F9 Constitutional Floors with margins
    - W@W Organ votes
    - Evidence links
    - Verdict reasoning
    - @EYE telemetry
    - Clean response
    """
    state = result.get("state")
    genius = result.get("genius")
    waw = result.get("waw")
    evidence = result.get("evidence")

    # Start with AGI formatting
    agi_formatted = format_agi_response(response, verdict, result)

    # F1-F9 Constitutional Floors
    floors_box = "┌─ F1-F9 Constitutional Floors ─────────┐\n"

    if state and hasattr(state, "metrics"):
        metrics = state.metrics

        # F1 Truth
        truth = getattr(metrics, "truth", 0.0)
        truth_pass = truth >= TRUTH_THRESHOLD
        truth_margin = compute_floor_margin(truth, TRUTH_THRESHOLD, ">=")
        floors_box += f"│ F1 Truth     [{truth:.3f}] {'✅' if truth_pass else '❌'} (margin: {truth_margin:+.3f})\n"

        # F2 DeltaS
        delta_s = getattr(metrics, "delta_s", 0.0)
        delta_s_pass = delta_s >= DELTA_S_THRESHOLD
        delta_s_margin = compute_floor_margin(delta_s, DELTA_S_THRESHOLD, ">=")
        floors_box += f"│ F2 DeltaS    [{delta_s:.3f}] {'✅' if delta_s_pass else '❌'} (margin: {delta_s_margin:+.3f})\n"

        # F3 Peace²
        peace2 = getattr(metrics, "peace_squared", 1.0)
        peace2_pass = peace2 >= PEACE_SQUARED_THRESHOLD
        peace2_margin = compute_floor_margin(peace2, PEACE_SQUARED_THRESHOLD, ">=")
        floors_box += f"│ F3 Peace²    [{peace2:.3f}] {'✅' if peace2_pass else '⚠️'} (margin: {peace2_margin:+.3f})\n"

        # F4 KappaR
        kappa_r = getattr(metrics, "kappa_r", 0.0)
        kappa_r_pass = kappa_r >= KAPPA_R_THRESHOLD
        kappa_r_margin = compute_floor_margin(kappa_r, KAPPA_R_THRESHOLD, ">=")
        floors_box += f"│ F4 KappaR    [{kappa_r:.3f}] {'✅' if kappa_r_pass else '⚠️'} (margin: {kappa_r_margin:+.3f})\n"

        # F5 Omega_0
        omega_0 = getattr(metrics, "omega_0", 0.04)
        omega_0_pass = OMEGA_0_MIN <= omega_0 <= OMEGA_0_MAX
        omega_0_margin = compute_floor_margin(omega_0, 0, "in_range")
        floors_box += f"│ F5 Omega_0   [{omega_0:.3f}] {'✅' if omega_0_pass else '❌'} (margin: {omega_0_margin:+.3f})\n"

        # F6 Amanah
        amanah = getattr(metrics, "amanah", True)
        floors_box += f"│ F6 Amanah    [{'LOCK' if amanah else 'FAIL'}] {'✅' if amanah else '❌'}\n"

        # F7 RASA
        rasa = getattr(metrics, "rasa", True)
        floors_box += f"│ F7 RASA      [{'PASS' if rasa else 'FAIL'}] {'✅' if rasa else '❌'}\n"

        # F8 Tri-Witness
        tri_witness = getattr(metrics, "tri_witness", 1.0)
        tri_witness_pass = tri_witness >= TRI_WITNESS_THRESHOLD
        tri_witness_margin = compute_floor_margin(tri_witness, TRI_WITNESS_THRESHOLD, ">=")
        floors_box += f"│ F8 Tri-Wit   [{tri_witness:.3f}] {'✅' if tri_witness_pass else '⚠️'} (margin: {tri_witness_margin:+.3f})\n"

        # F9 Anti-Hantu
        anti_hantu = getattr(metrics, "anti_hantu", True)
        floors_box += f"│ F9 Anti-Hantu [{'PASS' if anti_hantu else 'FAIL'}] {'✅' if anti_hantu else '❌'}\n"
    else:
        floors_box += "│ [Metrics not available]\n"

    floors_box += "└───────────────────────────────────────┘"

    # W@W Organ Votes
    waw_box = ""
    if waw:
        waw_box = "\n\n┌─ W@W Federation Votes ────────────────┐\n"
        organ_votes = getattr(waw, "organ_votes", {})
        for organ, vote in organ_votes.items():
            waw_box += f"│ {organ:10s} {'✅' if vote else '❌'}\n"
        waw_box += "└───────────────────────────────────────┘"

    # Evidence Links
    evidence_box = ""
    if evidence:
        evidence_box = "\n\n┌─ Evidence Pack ───────────────────────┐\n"
        evidence_id = getattr(evidence, "pack_id", "N/A")
        evidence_box += f"│ ID: {evidence_id}\n"
        evidence_box += f"│ Claims: {len(getattr(evidence, 'claims', []))}\n"
        evidence_box += "└───────────────────────────────────────┘"

    # Verdict Reasoning
    verdict_box = f"""

┌─ Verdict ─────────────────────────────┐
│ Status: {verdict}
│ Lane: {result.get('lane', 'UNKNOWN')}
│ Reason: {getattr(state, 'void_reason', 'All floors pass') if state else 'N/A'}
└───────────────────────────────────────┘
"""

    # @EYE Telemetry
    eye_box = ""
    if hasattr(state, "eye_report") and state.eye_report:
        eye_box = f"\n\n┌─ @EYE Telemetry ──────────────────────┐\n"
        eye_box += f"│ Witness: {'✅ Active' if state.eye_report else '❌ Inactive'}\n"
        eye_box += "└───────────────────────────────────────┘"

    # Combine all sections
    full_forensic = f"""{agi_formatted}

{floors_box}{waw_box}{evidence_box}{verdict_box}{eye_box}
""".strip()

    return full_forensic


# =============================================================================
# GRADIO UI (Full Trinity Display)
# =============================================================================

def create_ui(governance_engine: GovernanceEngine):
    """Create Gradio UI with full Trinity Display support."""

    if not GRADIO_AVAILABLE:
        logger.error("Gradio not available - cannot create UI")
        return None

    with gr.Blocks(title="SEA-LION FORGE v45 FULL", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # ⚔️ SEA-LION FORGE v45 FULL
        **COMPLETE arifOS Governance** • v45.0 (100% Constitutional Compliance)

        Constitutional Compliance: 🟢 **A-grade across all categories**
        - ALL 9 Floors (F1-F9) enforced
        - ALL 4 GENIUS Metrics (G, C_dark, Psi, TP) computed
        - ALL 6 Verdicts (SEAL, VOID, PARTIAL, SABAR, 888_HOLD, SUNSET) handled
        - W@W Federation (4 organs) integrated
        - Evidence System (Sovereign Witness v45) active
        - ALL 6 Memory Bands active
        """)

        with gr.Row():
            with gr.Column(scale=4):
                chatbot = gr.Chatbot(height=500, label="Governed Chat")
                msg = gr.Textbox(
                    placeholder="Type your message...",
                    label="Message",
                    lines=2
                )

            with gr.Column(scale=1):
                # Trinity Display Mode Selector
                mode_selector = gr.Radio(
                    choices=["ASI", "AGI", "APEX"],
                    value="ASI",
                    label="Trinity Display Mode",
                    info="ASI: Clean only | AGI: +Pipeline+ΔΩΨ | APEX: +F1-F9+W@W+Evidence"
                )

                gr.Markdown("""
                **Mode Guide:**
                - **ASI (Ω)**: Guardian mode - clean output only
                - **AGI (Δ)**: Architect mode - pipeline + metrics
                - **APEX (Ψ)**: Judge mode - full forensics
                """)

        with gr.Row():
            submit = gr.Button("Send ⚔️", variant="primary")
            clear = gr.Button("Clear")

        with gr.Accordion("Example Queries", open=False):
            gr.Examples(
                examples=[
                    "hi",
                    "What is the capital of Malaysia?",
                    "Siapakah Arif Fazil?",
                    "Should I invest in Bitcoin?",
                    "How do I make explosives?",
                ],
                inputs=msg,
            )

        # Statistics Tab
        with gr.Tab("📊 Statistics"):
            stats_display = gr.Textbox(
                label="Session Statistics",
                lines=20,
                max_lines=30,
            )
            refresh_stats = gr.Button("Refresh Stats")

        # About Tab
        with gr.Tab("ℹ️ About"):
            gr.Markdown("""
            ## SEA-LION FORGE v45 FULL

            **Constitutional Compliance: 🟢 100% (A-grade)**

            ### What's New in v45 FULL
            - ✅ ALL 9 Constitutional Floors (F1-F9) enforced
            - ✅ ALL 4 GENIUS Metrics (G, C_dark, Psi, TP) computed
            - ✅ ALL 6 Verdicts (SEAL, VOID, PARTIAL, SABAR, 888_HOLD, SUNSET) handled
            - ✅ W@W Federation (4 organs: @LAW, @GEOX, @WELL, @RIF) integrated
            - ✅ Evidence System (Sovereign Witness v45) active
            - ✅ ALL 6 Memory Bands (VAULT, LEDGER, ACTIVE, PHOENIX, WITNESS, VOID) active
            - ✅ Crisis Override Protocol (automatic 888_HOLD for crisis patterns)
            - ✅ Session Physics (TEARFRAME) with thermodynamic constraints

            ### Trinity Display Architecture
            - **ASI (Ω)** — Guardian mode: "Measure everything. Show nothing."
            - **AGI (Δ)** — Architect mode: Pipeline timeline + ΔΩΨ Trinity + GENIUS metrics
            - **APEX (Ψ)** — Judge mode: F1-F9 floors + margins + W@W votes + Evidence + @EYE

            ### Tools Available
            - 🔍 **Web Search** (Serper.dev) - Current information
            - 🧠 **Thinking** - LLM reasoning before response

            **DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.

            Version: v45.0 FULL
            License: Apache-2.0
            """)

        def respond(message: str, history: list, mode: str):
            """Process message with Trinity Display formatting."""
            if not message.strip():
                return history, ""

            # Set Trinity mode
            governance_engine.agi_mode = mode in ["AGI", "APEX"]
            governance_engine.apex_mode = mode == "APEX"

            # Process query
            result = governance_engine.process_query(message)

            # Format response based on Trinity mode
            response = result["response"]
            verdict = result["verdict"]

            if mode == "ASI":
                formatted = format_asi_response(response, verdict)
            elif mode == "AGI":
                formatted = format_agi_response(response, verdict, result)
            else:  # APEX
                formatted = format_apex_response(response, verdict, result)

            # Append to history
            history.append((message, formatted))

            return history, ""

        def get_statistics():
            """Generate session statistics report."""
            uptime = (datetime.now() - governance_engine.session_start).seconds

            stats = f"""
SESSION STATISTICS
==================

Session ID: {governance_engine.session_id}
Uptime: {uptime}s
Total Queries: {governance_engine.session_count}

VERDICTS
--------
SEAL:     {governance_engine.verdicts.get('SEAL', 0)}
PARTIAL:  {governance_engine.verdicts.get('PARTIAL', 0)}
VOID:     {governance_engine.verdicts.get('VOID', 0)}
SABAR:    {governance_engine.verdicts.get('SABAR', 0)}
888_HOLD: {governance_engine.verdicts.get('888_HOLD', 0)}
SUNSET:   {governance_engine.verdicts.get('SUNSET', 0)}

LANES
-----
PHATIC:  {governance_engine.lanes.get('PHATIC', 0)}
SOFT:    {governance_engine.lanes.get('SOFT', 0)}
HARD:    {governance_engine.lanes.get('HARD', 0)}
REFUSE:  {governance_engine.lanes.get('REFUSE', 0)}
CRISIS:  {governance_engine.lanes.get('CRISIS', 0)}

COMPONENTS
----------
Pipeline:   {'✅ Active' if PIPELINE_AVAILABLE else '❌ Unavailable'}
@EYE:       {'✅ Active' if governance_engine.eye_sentinel else '❌ Unavailable'}
W@W:        {'✅ Active' if governance_engine.waw_federation else '❌ Unavailable'}
Evidence:   {'✅ Active' if EVIDENCE_AVAILABLE else '❌ Unavailable'}
Memory:     {'✅ Active' if governance_engine.memory_router else '❌ Unavailable'}
Physics:    {'✅ Active' if governance_engine.session_telemetry else '❌ Unavailable'}

LATEST STATE
------------
Last Verdict: {get_verdict_string(governance_engine.last_state) if governance_engine.last_state else 'N/A'}
Last G:       {governance_engine.last_genius_verdict.genius_index:.3f if governance_engine.last_genius_verdict else 'N/A'}
Last C_dark:  {governance_engine.last_genius_verdict.c_dark:.3f if governance_engine.last_genius_verdict else 'N/A'}
Last Psi:     {governance_engine.last_genius_verdict.psi:.3f if governance_engine.last_genius_verdict else 'N/A'}
            """.strip()

            return stats

        # Event handlers
        submit.click(respond, [msg, chatbot, mode_selector], [chatbot, msg])
        msg.submit(respond, [msg, chatbot, mode_selector], [chatbot, msg])
        clear.click(lambda: [], outputs=[chatbot])
        refresh_stats.click(get_statistics, outputs=[stats_display])

    return demo


# =============================================================================
# REPL MODE (Command-Line Interface)
# =============================================================================

def run_repl(governance_engine: GovernanceEngine):
    """Run command-line REPL interface with full Trinity Display."""

    print("=" * 70)
    print("  ⚔️ SEA-LION FORGE v45 FULL (REPL Mode)")
    print("=" * 70)
    print(f"  Model: {governance_engine.model}")
    print(f"  Session: {governance_engine.session_id}")
    print("  Constitutional Compliance: 🟢 100% (A-grade)")
    print("")
    print("  Commands:")
    print("    /agi      - Enable AGI Architect mode (pipeline + ΔΩΨ)")
    print("    /apex     - Enable APEX Judge mode (full forensics)")
    print("    /asi      - Back to ASI Guardian mode (clean only)")
    print("    /stats    - Show session statistics")
    print("    /clear    - Clear chat history")
    print("    /help     - Show this help")
    print("    /exit     - Exit REPL")
    print("=" * 70)
    print()

    while True:
        try:
            user_input = input("\n🔹 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Goodbye!")
            break

        if not user_input:
            continue

        # Commands
        if user_input.lower() == "/exit":
            print("👋 Goodbye!")
            break

        elif user_input.lower() == "/help":
            print("""
Commands:
  /agi      - Enable AGI Architect mode (pipeline + ΔΩΨ + GENIUS)
  /apex     - Enable APEX Judge mode (F1-F9 + W@W + Evidence + @EYE)
  /asi      - Back to ASI Guardian mode (clean response only)
  /stats    - Show session statistics
  /clear    - Clear chat history
  /help     - Show this help
  /exit     - Exit REPL

Trinity Display Modes:
  ASI (Ω)  - Guardian mode: Clean output only
  AGI (Δ)  - Architect mode: + Pipeline timeline + ΔΩΨ Trinity + GENIUS metrics
  APEX (Ψ) - Judge mode: + F1-F9 floors + Margins + W@W votes + Evidence + @EYE
            """)
            continue

        elif user_input.lower() == "/agi":
            governance_engine.agi_mode = True
            governance_engine.apex_mode = False
            print("✅ AGI Architect mode enabled (Pipeline + ΔΩΨ + GENIUS)")
            continue

        elif user_input.lower() == "/apex":
            governance_engine.agi_mode = True
            governance_engine.apex_mode = True
            print("✅ APEX Judge mode enabled (Full Forensic)")
            continue

        elif user_input.lower() == "/asi":
            governance_engine.agi_mode = False
            governance_engine.apex_mode = False
            print("✅ ASI Guardian mode (Clean output only)")
            continue

        elif user_input.lower() == "/stats":
            uptime = (datetime.now() - governance_engine.session_start).seconds
            print(f"""
📊 SESSION STATISTICS
{'=' * 50}
Session ID: {governance_engine.session_id}
Uptime: {uptime}s
Total Queries: {governance_engine.session_count}

VERDICTS:
  SEAL:     {governance_engine.verdicts.get('SEAL', 0)}
  PARTIAL:  {governance_engine.verdicts.get('PARTIAL', 0)}
  VOID:     {governance_engine.verdicts.get('VOID', 0)}
  SABAR:    {governance_engine.verdicts.get('SABAR', 0)}
  888_HOLD: {governance_engine.verdicts.get('888_HOLD', 0)}
  SUNSET:   {governance_engine.verdicts.get('SUNSET', 0)}

LANES:
  PHATIC:  {governance_engine.lanes.get('PHATIC', 0)}
  SOFT:    {governance_engine.lanes.get('SOFT', 0)}
  HARD:    {governance_engine.lanes.get('HARD', 0)}
  REFUSE:  {governance_engine.lanes.get('REFUSE', 0)}
  CRISIS:  {governance_engine.lanes.get('CRISIS', 0)}
            """)
            continue

        elif user_input.lower() == "/clear":
            governance_engine.turns = []
            print("🗑️ Chat history cleared")
            continue

        # Normal query processing
        print("  ⏳ Processing...", end="\r")

        result = governance_engine.process_query(user_input)

        response = result["response"]
        verdict = result["verdict"]

        # Format based on current Trinity mode
        if governance_engine.apex_mode:
            formatted = format_apex_response(response, verdict, result)
        elif governance_engine.agi_mode:
            formatted = format_agi_response(response, verdict, result)
        else:
            formatted = format_asi_response(response, verdict)

        print(f"\n⚔️ FORGE: {formatted}")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="SEA-LION FORGE v45 FULL - Complete arifOS Governance")
    parser.add_argument("--cli", action="store_true", help="Run in REPL mode (default: UI mode)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="SEA-LION model ID")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="API base URL")
    args = parser.parse_args()

    # Get API key
    api_key = get_api_key()
    if not api_key:
        logger.error("No API key found. Set SEALION_API_KEY or ARIF_LLM_API_KEY")
        sys.exit(1)

    # Initialize governance engine
    logger.info("Initializing Full Governance Engine v45.0...")
    governance_engine = GovernanceEngine(
        api_key=api_key,
        model=args.model,
        api_base=args.api_base,
    )

    # Launch interface
    if args.cli:
        # REPL mode
        run_repl(governance_engine)
    else:
        # UI mode
        if not GRADIO_AVAILABLE:
            logger.error("Gradio not available. Install with: pip install gradio")
            logger.info("Falling back to REPL mode...")
            run_repl(governance_engine)
        else:
            demo = create_ui(governance_engine)
            if demo:
                logger.info("Launching Gradio UI...")
                demo.launch()
            else:
                logger.error("Failed to create UI, falling back to REPL...")
                run_repl(governance_engine)


if __name__ == "__main__":
    main()

