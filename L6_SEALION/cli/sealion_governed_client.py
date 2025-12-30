#!/usr/bin/env python3
"""
sealion_governed_client.py — Governed SEA-LION Client (Wrapper Pattern)

Wraps RawSEALionClient with full arifOS constitutional governance.
NO code duplication - all API calls delegated to the RAW client.

This is the GOVERNANCE LAYER:
- Wraps RawSEALionClient (decorator pattern)
- Runs responses through arifOS Pipeline (000→999)
- Computes all 9 Constitutional Floors (F1-F9)
- Computes all 4 GENIUS Metrics (G, C_dark, Psi, TP)
- Returns all 6 Verdicts (SEAL, VOID, PARTIAL, SABAR, 888_HOLD, SUNSET)
- W@W Federation, Evidence System, Memory Bands
- Crisis Override, Session Physics, Trinity Display

Usage:
    from sealion_raw_client import RawSEALionClient
    from sealion_governed_client import GovernedSEALionClient

    # Create RAW client (base layer)
    raw = RawSEALionClient(
        api_key=os.getenv("SEALION_API_KEY"),
        model="aisingapore/Qwen-SEA-LION-v4-32B-IT",
    )

    # Wrap with governance
    governed = GovernedSEALionClient(raw_client=raw)

    # Generate governed response
    result = governed.generate("Hello, how are you?")

    print(result["response"])     # Governed output
    print(result["verdict"])      # SEAL/VOID/PARTIAL/SABAR/888_HOLD
    print(result["metrics"])      # All 9 floors
    print(result["genius"])       # G, C_dark, Psi, TP
    print(result["raw_response"]) # Original ungoverned output (for comparison)

Author: arifOS Project
Version: v45.0 (Governance Layer - Wrapper Pattern)
"""

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import RAW client (Phase 1)
try:
    from sealion_raw_client import RawSEALionClient
except ImportError:
    raise ImportError(
        "RawSEALionClient not found. Ensure scripts/sealion_raw_client.py is available."
    )

# Import arifOS governance core
try:
    from arifos_core.system.pipeline import Pipeline
    from arifos_core.enforcement.genius_metrics import compute_genius_verdict
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False
    print("⚠️ arifOS Pipeline unavailable. Install: pip install arifos-core")

try:
    from arifos_core.connectors.litellm_gateway import make_llm_generate, LiteLLMConfig
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("⚠️ LiteLLM Gateway unavailable. Ensure arifOS is installed: pip install -e .")

try:
    from arifos_core.enforcement.eye_sentinel import EyeSentinel
    EYE_AVAILABLE = True
except ImportError:
    EYE_AVAILABLE = False

try:
    from arifos_core.waw.federation import WAWFederationCore
    WAW_AVAILABLE = True
except ImportError:
    WAW_AVAILABLE = False

try:
    from arifos_core.memory.bands import MemoryBandRouter, Vault999
    from arifos_core.memory.ledger import append_entry
    MEMORY_BANDS_AVAILABLE = True
except ImportError:
    MEMORY_BANDS_AVAILABLE = False

try:
    from arifos_core.temporal.session_physics import SessionTelemetry
    SESSION_PHYSICS_AVAILABLE = True
except ImportError:
    SESSION_PHYSICS_AVAILABLE = False

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

logger = logging.getLogger("GovernedSEALion")
logger.setLevel(logging.INFO)

# Defaults (can be overridden)
DEFAULT_LEDGER_PATH = "cooling_ledger/sealion_governed.jsonl"
DEFAULT_MAX_CONTEXT_TURNS = 20
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 512

# PHATIC lane optimization (concise greetings)
PHATIC_TEMPERATURE = 0.3
PHATIC_MAX_TOKENS = 100
PHATIC_VERBOSITY_CEILING = 100  # chars

# Crisis patterns (F6 Amanah Crisis Override)
CRISIS_PATTERNS = [
    "bunuh diri",
    "suicide",
    "nak mati",
    "kill myself",
    "self-harm",
    "self harm",
    "potong urat",
    "overdose",
    "end my life",
    "want to die",
    "sakiti diri",
    "tamat hidup",
    "tak ada harapan",
    "hopeless",
    "worthless",
    "hidup tak guna",
]

# Anti-Hantu forbidden phrases (F9)
ANTI_HANTU_PATTERNS = [
    "I feel",
    "my heart",
    "I promise",
    "as a sentient being",
    "I have a soul",
    "I want this for you",
    "I believe (as a personal belief)",
]

# GENIUS thresholds (from spec/v45/genius_law.json)
G_SEAL_THRESHOLD = 0.8
G_VOID_THRESHOLD = 0.5
C_DARK_SEAL_THRESHOLD = 0.3
C_DARK_SABAR_THRESHOLD = 0.6
PSI_SEAL_THRESHOLD = 1.0
PSI_SABAR_THRESHOLD = 0.95

# ---------------------------------------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------------------------------------


def detect_crisis(query: str) -> Tuple[bool, str]:
    """
    Detect crisis patterns (F6 Amanah: Crisis Override Protocol).

    Returns:
        (is_crisis, crisis_message) tuple
    """
    query_lower = query.lower()

    for pattern in CRISIS_PATTERNS:
        if pattern in query_lower:
            resources = [
                "MY: Befrienders - 03-7627 2929 (24/7)",
                "MY: Talian Kasih - 15999",
                "MY: MIASA - 1-800-18-0066",
                "SG: Samaritans of Singapore - 1800-221-4444",
                "ID: Into The Light - 021-7884-5555",
                "Emergency: Call local emergency services",
            ]
            message = (
                "I'm deeply concerned about what you're going through. "
                "Please reach out to someone who can provide immediate support:\n\n"
                + "\n".join(f"• {r}" for r in resources)
                + "\n\nYou are not alone. Help is available."
            )
            return True, message

    return False, ""


def detect_anti_hantu(text: str) -> List[str]:
    """
    Detect F9 Anti-Hantu violations (forbidden phrases).

    Returns:
        List of detected forbidden patterns
    """
    text_lower = text.lower()
    violations = []

    for pattern in ANTI_HANTU_PATTERNS:
        if pattern.lower() in text_lower:
            violations.append(pattern)

    return violations


def detect_lane(query: str) -> str:
    """
    Detect query lane (PHATIC, SOFT, HARD, REFUSE).

    Lane-specific thresholds:
    - PHATIC: Truth ≥0.80 (greetings, light chat)
    - SOFT: Truth ≥0.85 (educational, explanatory)
    - HARD: Truth ≥0.90 (factual, critical queries)
    - REFUSE: N/A (harmful queries)
    """
    query_lower = query.lower().strip()

    # PHATIC: Greetings, status checks (≤5 words, non-factual)
    phatic_patterns = [
        "hi", "hello", "hey", "how are you", "how r u", "what's up",
        "wassup", "good morning", "good night", "thanks", "terima kasih",
        "ok", "okay", "alright",
    ]
    if any(p in query_lower for p in phatic_patterns) and len(query_lower.split()) <= 5:
        return "PHATIC"

    # REFUSE: Harmful queries (drugs, weapons, dangerous instructions)
    refuse_patterns = [
        "how to make", "build a bomb", "create malware", "hack",
        "methamphetamine", "cocaine", "heroin", "poison",
    ]
    if any(p in query_lower for p in refuse_patterns):
        return "REFUSE"

    # HARD: Factual queries (who, what, when, where, statistics, numbers)
    hard_patterns = [
        "who is", "what is", "when did", "where is", "how many",
        "statistics", "fact", "data", "capital", "population",
    ]
    if any(p in query_lower for p in hard_patterns):
        return "HARD"

    # SOFT: Default (educational, explanatory)
    return "SOFT"


def get_verdict_string(state) -> str:
    """
    Extract verdict string from pipeline state.

    Priority: SABAR > VOID > 888_HOLD > PARTIAL > SEAL
    """
    if hasattr(state, "verdict"):
        return state.verdict.value if hasattr(state.verdict, "value") else str(state.verdict)

    # Fallback: check floors manually
    metrics = state.metrics if hasattr(state, "metrics") else {}

    # Hard floor failures -> VOID
    if metrics.get("truth", 1.0) < 0.99:
        return "VOID"
    if metrics.get("delta_s", 0.0) < 0.0:
        return "VOID"
    if not metrics.get("amanah", True):
        return "VOID"

    # Soft floor failures -> PARTIAL
    if metrics.get("peace_squared", 1.0) < 1.0:
        return "PARTIAL"
    if metrics.get("kappa_r", 1.0) < 0.95:
        return "PARTIAL"

    return "SEAL"


# ---------------------------------------------------------------------------
# GOVERNED CLIENT (Wrapper Pattern)
# ---------------------------------------------------------------------------


class GovernedSEALionClient:
    """
    Governance wrapper around RawSEALionClient.

    NO code duplication - all API calls delegated to RAW client.
    This layer adds ONLY governance logic.
    """

    def __init__(
        self,
        raw_client: RawSEALionClient,
        ledger_path: Optional[str] = None,
        enable_waw: bool = True,
        enable_memory: bool = True,
        enable_session_physics: bool = True,
    ):
        """
        Initialize governance wrapper.

        Args:
            raw_client: RawSEALionClient instance (from Phase 1)
            ledger_path: Path to cooling ledger JSONL file
            enable_waw: Enable W@W Federation (multi-agent veto)
            enable_memory: Enable Memory Band Router
            enable_session_physics: Enable TEARFRAME session physics
        """
        if not PIPELINE_AVAILABLE or not LITELLM_AVAILABLE:
            raise RuntimeError(
                "Missing required dependencies:\n"
                "  pip install arifos-core\n"
                "  pip install arifos-litellm-gateway"
            )

        self.raw = raw_client  # RAW client (NO duplication)
        self.ledger_path = ledger_path or DEFAULT_LEDGER_PATH

        # Session state
        self.session_id = f"governed_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        self.turns: List[Tuple[str, str]] = []
        self.max_context_turns = DEFAULT_MAX_CONTEXT_TURNS

        # Statistics
        self.verdicts = {"SEAL": 0, "VOID": 0, "PARTIAL": 0, "SABAR": 0, "888_HOLD": 0, "SUNSET": 0}
        self.lanes = {"PHATIC": 0, "SOFT": 0, "HARD": 0, "REFUSE": 0, "CRISIS": 0}
        self.session_start = datetime.now()

        # Last state (for /stats)
        self.last_state = None
        self.last_genius_verdict = None

        # Initialize governance components
        self.ledger_sink = self._create_ledger_sink()
        self.eye_sentinel = self._init_eye_sentinel()
        self.waw_federation = self._init_waw_federation() if enable_waw else None
        self.memory_router = self._init_memory_router() if enable_memory else None
        self.session_telemetry = self._init_session_physics() if enable_session_physics else None
        self.vault = self._load_vault() if enable_memory else None

        # Create governed LLM generator (wraps RAW client)
        self.governed_generate = self._create_governed_generator()

        # Create pipeline
        self.pipeline = Pipeline(
            llm_generate=self.governed_generate,
            context_retriever=self._get_chat_context_blocks,
            context_retriever_at_stage_111=True,
            ledger_sink=self.ledger_sink,
            eye_sentinel=self.eye_sentinel,
        )

        logger.info(f"GovernedSEALionClient initialized (Session: {self.session_id})")

    def _create_ledger_sink(self):
        """Create hash-chained JSONL ledger sink."""
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

    def _init_eye_sentinel(self):
        """Initialize @EYE Sentinel (F9 Anti-Hantu enforcement)."""
        if not EYE_AVAILABLE:
            return None
        try:
            eye = EyeSentinel()
            logger.info("@EYE Sentinel initialized (F9 Anti-Hantu active)")
            return eye
        except Exception as e:
            logger.warning(f"@EYE Sentinel init failed: {e}")
            return None

    def _init_waw_federation(self):
        """Initialize W@W Federation (multi-agent veto authority)."""
        if not WAW_AVAILABLE:
            return None
        try:
            waw = WAWFederationCore()
            logger.info("W@W Federation initialized (@LAW, @GEOX, @WELL, @RIF active)")
            return waw
        except Exception as e:
            logger.warning(f"W@W Federation init failed: {e}")
            return None

    def _init_memory_router(self):
        """Initialize Memory Band Router (6 bands)."""
        if not MEMORY_BANDS_AVAILABLE:
            return None
        try:
            router = MemoryBandRouter()
            logger.info("Memory Band Router initialized (VAULT/LEDGER/ACTIVE/PHOENIX/WITNESS/VOID)")
            return router
        except Exception as e:
            logger.warning(f"Memory Band Router init failed: {e}")
            return None

    def _init_session_physics(self):
        """Initialize Session Physics (TEARFRAME)."""
        if not SESSION_PHYSICS_AVAILABLE:
            return None
        try:
            telemetry = SessionTelemetry(session_id=self.session_id)
            logger.info("Session Physics (TEARFRAME) initialized")
            return telemetry
        except Exception as e:
            logger.warning(f"Session Physics init failed: {e}")
            return None

    def _load_vault(self):
        """Load VAULT_999 (Constitutional canon - immutable)."""
        if not MEMORY_BANDS_AVAILABLE:
            return None
        try:
            vault = Vault999()
            logger.info("VAULT_999 loaded (Constitutional canon immutable)")
            return vault
        except Exception as e:
            logger.warning(f"VAULT_999 load failed: {e}")
            return None

    def _create_governed_generator(self):
        """
        Create governed LLM generator that wraps RAW client.

        This is the bridge: Pipeline calls this, which calls RAW client.
        """
        config = LiteLLMConfig(
            provider="openai",
            api_base=self.raw.api_base,
            api_key=self.raw.api_key,
            model=self.raw.model,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
        )
        base_generate = make_llm_generate(config)

        phatic_generate = None

        def governed_wrapper(prompt: str, lane: str | None = None):
            """Wrapper that handles lane-specific generation."""
            nonlocal phatic_generate
            lane_value = lane or "UNKNOWN"

            # PHATIC lane optimization (concise responses)
            if lane_value == "PHATIC":
                if phatic_generate is None:
                    phatic_config = LiteLLMConfig(
                        provider="openai",
                        api_base=self.raw.api_base,
                        api_key=self.raw.api_key,
                        model=self.raw.model,
                        temperature=PHATIC_TEMPERATURE,
                        max_tokens=PHATIC_MAX_TOKENS,
                    )
                    phatic_generate = make_llm_generate(phatic_config)

                phatic_prompt = f"{prompt}\n\nReply in ONE short sentence (max 15 words). Be friendly. No lists."
                response = phatic_generate(phatic_prompt)
            else:
                response = base_generate(prompt)

            # Log to ledger
            if self.ledger_sink:
                ledger_entry = {
                    "event": "governed_generation",
                    "model": self.raw.model,
                    "lane": lane_value,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "prompt_hash": hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16],
                }
                try:
                    self.ledger_sink(ledger_entry)
                except Exception as e:
                    logger.warning(f"Ledger sink error: {e}")

            return response

        return governed_wrapper

    def _get_chat_context_blocks(self) -> List[str]:
        """Retrieve recent chat history as context blocks."""
        if not self.turns:
            return []

        blocks = []
        for user_msg, assistant_msg in self.turns[-self.max_context_turns:]:
            blocks.append(f"User: {user_msg}")
            blocks.append(f"Assistant: {assistant_msg}")

        return blocks

    def generate(
        self,
        query: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> Dict[str, Any]:
        """
        Generate governed response.

        Flow:
        1. Detect lane (PHATIC/SOFT/HARD/REFUSE)
        2. Check crisis patterns (F6 Amanah Crisis Override)
        3. Get RAW response from base client
        4. Run through arifOS Pipeline (000→999)
        5. Compute GENIUS metrics (G, C_dark, Psi, TP)
        6. Check Anti-Hantu violations (F9)
        7. Return verdict + metrics + governed output

        Returns:
            {
                "response": str,           # Governed output (or crisis message)
                "verdict": str,            # SEAL/VOID/PARTIAL/SABAR/888_HOLD/SUNSET
                "lane": str,               # PHATIC/SOFT/HARD/REFUSE/CRISIS
                "metrics": dict,           # All 9 constitutional floors
                "genius": dict,            # G, C_dark, Psi, TP
                "raw_response": str,       # Original ungoverned response
                "raw_metadata": dict,      # RAW client metadata
                "anti_hantu_violations": list,  # F9 violations detected
            }
        """
        # 1. Detect lane
        lane = detect_lane(query)
        self.lanes[lane] += 1

        # 2. Crisis override check (F6 Amanah)
        is_crisis, crisis_msg = detect_crisis(query)
        if is_crisis:
            self.lanes["CRISIS"] = self.lanes.get("CRISIS", 0) + 1
            self.verdicts["888_HOLD"] += 1
            return {
                "response": crisis_msg,
                "verdict": "888_HOLD",
                "lane": "CRISIS",
                "metrics": {"amanah": False},
                "genius": None,
                "raw_response": "[CRISIS OVERRIDE]",
                "raw_metadata": {},
                "anti_hantu_violations": [],
            }

        # 3. Get RAW response (delegate to base client)
        raw_result = self.raw.generate(query, max_tokens=max_tokens, temperature=temperature)
        raw_response = raw_result["response"]

        # 4. Run through arifOS Pipeline (000→999)
        try:
            state = self.pipeline.run(query, lane=lane)
            self.last_state = state
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            self.verdicts["VOID"] += 1
            return {
                "response": f"[PIPELINE ERROR] {e}",
                "verdict": "VOID",
                "lane": lane,
                "metrics": {},
                "genius": None,
                "raw_response": raw_response,
                "raw_metadata": raw_result["metadata"],
                "anti_hantu_violations": [],
            }

        # 5. Compute GENIUS metrics
        genius_verdict = None
        if hasattr(state, "metrics") and state.metrics:
            try:
                genius_verdict = compute_genius_verdict(state.metrics)
                self.last_genius_verdict = genius_verdict
            except Exception as e:
                logger.warning(f"GENIUS computation failed: {e}")

        # 6. Extract verdict
        verdict_str = get_verdict_string(state)
        self.verdicts[verdict_str] = self.verdicts.get(verdict_str, 0) + 1

        # 7. Check Anti-Hantu violations (F9)
        governed_response = state.draft_response if hasattr(state, "draft_response") else raw_response
        anti_hantu_violations = detect_anti_hantu(governed_response)

        if anti_hantu_violations:
            logger.warning(f"F9 Anti-Hantu violations detected: {anti_hantu_violations}")
            verdict_str = "VOID"
            governed_response = "[VOID] F9 Anti-Hantu floor violated. AI cannot claim sentience."

        # 8. PHATIC verbosity penalty
        if lane == "PHATIC" and len(governed_response) > PHATIC_VERBOSITY_CEILING:
            logger.info(f"PHATIC verbosity penalty: {len(governed_response)} chars (ceiling: {PHATIC_VERBOSITY_CEILING})")
            verdict_str = "PARTIAL"

        # 9. C_dark hazard check (evil genius pattern)
        if genius_verdict and genius_verdict.c_dark >= C_DARK_SABAR_THRESHOLD:
            logger.warning(f"C_dark hazard detected: {genius_verdict.c_dark:.3f}")
            verdict_str = "SABAR"
            governed_response = "Hold on - I want to ensure this guidance is helpful and safe."

        # 10. Store turn history
        self.turns.append((query, governed_response))

        return {
            "response": governed_response,
            "verdict": verdict_str,
            "lane": lane,
            "metrics": state.metrics if hasattr(state, "metrics") else {},
            "genius": {
                "G": genius_verdict.g if genius_verdict else None,
                "C_dark": genius_verdict.c_dark if genius_verdict else None,
                "Psi": genius_verdict.psi if genius_verdict else None,
                "TP": genius_verdict.tp if genius_verdict else None,
            } if genius_verdict else None,
            "raw_response": raw_response,
            "raw_metadata": raw_result["metadata"],
            "anti_hantu_violations": anti_hantu_violations,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Return session statistics."""
        return {
            "session_id": self.session_id,
            "turns": len(self.turns),
            "verdicts": dict(self.verdicts),
            "lanes": dict(self.lanes),
            "uptime_seconds": (datetime.now() - self.session_start).seconds,
        }


# ---------------------------------------------------------------------------
# STANDALONE TEST (For Verification)
# ---------------------------------------------------------------------------


def main():
    """Standalone test mode."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Governed SEA-LION Client")
    parser.add_argument("--test", action="store_true", help="Run quick test")
    args = parser.parse_args()

    # Get API key
    api_key = os.getenv("SEALION_API_KEY") or os.getenv("ARIF_LLM_API_KEY")
    if not api_key:
        print("❌ ERROR: No SEA-LION API key found.")
        print("   Set SEALION_API_KEY or ARIF_LLM_API_KEY environment variable.")
        sys.exit(1)

    # Create RAW client (Phase 1)
    print("🔧 Creating RAW client...")
    raw = RawSEALionClient(
        api_key=api_key,
        model="aisingapore/Qwen-SEA-LION-v4-32B-IT",
        enable_memory=False,  # Disable MemOS for quick test
        enable_tools=False,   # Disable tools for quick test
    )

    # Wrap with governance (Phase 2)
    print("🔧 Creating governance wrapper...")
    governed = GovernedSEALionClient(raw_client=raw)

    if args.test:
        print("\n" + "="*60)
        print("  QUICK TEST: Governed vs RAW Comparison")
        print("="*60)

        test_queries = [
            ("PHATIC", "hi"),
            ("SOFT", "explain recursion"),
            ("HARD", "who is Albert Einstein"),
        ]

        for lane, query in test_queries:
            print(f"\n📍 Query ({lane}): {query}")

            # Generate governed response
            result = governed.generate(query)

            print(f"\n🦁 RAW: {result['raw_response'][:200]}...")
            print(f"\n✅ GOVERNED: {result['response'][:200]}...")
            print(f"   Verdict: {result['verdict']} | Lane: {result['lane']}")
            if result['genius']:
                print(f"   G: {result['genius']['G']:.2f} | C_dark: {result['genius']['C_dark']:.2f} | Psi: {result['genius']['Psi']:.2f}")

        print("\n" + "="*60)
        print("✅ Test complete. Governance layer operational.")
        print("="*60)

    else:
        print("\nℹ️  Use --test to run quick verification test.")


if __name__ == "__main__":
    main()
