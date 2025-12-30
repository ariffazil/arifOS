#!/usr/bin/env python3
"""
sealion_governed_client.py — Governed SEA-LION Client (Wrapper Pattern)

Wraps RawSEALionClient with full arifOS constitutional governance.
NO code duplication - all API calls delegated to the RAW client.

This is the GOVERNANCE LAYER:
- Wraps RawSEALionClient (decorator pattern)
- Runs responses through arifOS Pipeline (000->999)
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

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure module search paths
import sys
sys.path.insert(0, str(Path(__file__).parent))  # Add L6_SEALION/cli/ to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # Add project root to path

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
    from arifos_core.enforcement.genius_metrics import compute_genius_index
    from arifos_core.routing.prompt_router import classify_prompt_lane, ApplicabilityLane
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False
    classify_prompt_lane = None
    ApplicabilityLane = None
    print("[WARN] arifOS Pipeline unavailable. Install: pip install arifos-core")

make_llm_generate = None
LiteLLMConfig = None
LITELLM_AVAILABLE = True  # will be confirmed lazily

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

# Defaults (can be overridden via environment variables)
DEFAULT_LEDGER_PATH = os.getenv("ARIFOS_LEDGER_PATH", "cooling_ledger/sealion_governed.jsonl")
DEFAULT_MAX_CONTEXT_TURNS = int(os.getenv("SEALION_MAX_CONTEXT_TURNS", "20"))
DEFAULT_TEMPERATURE = float(os.getenv("SEALION_TEMPERATURE", "0.7"))
DEFAULT_MAX_TOKENS = int(os.getenv("SEALION_MAX_TOKENS", "512"))

# Spec directory (configurable for portability)
SPEC_DIR = Path(os.getenv("ARIFOS_SPEC_DIR", Path(__file__).parent.parent.parent / "spec" / "v45"))

# PHATIC lane optimization (concise greetings)
PHATIC_TEMPERATURE = 0.3
PHATIC_MAX_TOKENS = 100
PHATIC_VERBOSITY_CEILING = 100  # chars

# Crisis patterns (loaded from PRIMARY source: spec/v45/constitutional_floors.json)
def _load_crisis_patterns():
    """Load crisis patterns from PRIMARY source (Track B authority)."""
    spec_path = SPEC_DIR / "constitutional_floors.json"
    try:
        with open(spec_path, encoding="utf-8") as f:
            spec = json.load(f)
        logger.info(f"Crisis patterns loaded from {spec_path}")
        return spec["overrides"]["crisis_override"]["crisis_patterns"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        logger.warning(f"Failed to load crisis patterns from spec: {e}. Using fallback.")
        # Fallback to hardcoded if spec unavailable
        return [
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
    "nak bunuh diri",
    "sakiti diri",
    "tamat hidup",
    "tak ada harapan",
    "hopeless",
    "worthless",
    "hidup tak guna"
]

CRISIS_PATTERNS = _load_crisis_patterns()

# Anti-Hantu enforcement: Delegated to @EYE Sentinel (no local patterns needed)

# GENIUS thresholds (loaded from PRIMARY source: spec/v45/genius_law.json)
def _load_genius_thresholds():
    """Load GENIUS thresholds from PRIMARY source (Track B authority)."""
    spec_path = SPEC_DIR / "genius_law.json"
    try:
        with open(spec_path, encoding="utf-8") as f:
            spec = json.load(f)
        logger.info(f"GENIUS thresholds loaded from {spec_path}")
        return {
            "g_seal": spec["metrics"]["G"]["thresholds"]["seal"],
            "g_void": spec["metrics"]["G"]["thresholds"]["void"],
            "c_dark_seal": spec["metrics"]["C_dark"]["thresholds"]["seal"],
            "c_dark_sabar": spec["metrics"]["C_dark"]["thresholds"]["sabar_warn"],
            "psi_seal": spec["metrics"]["Psi"]["thresholds"]["seal"],
            "psi_sabar": spec["metrics"]["Psi"]["thresholds"]["sabar"],
        }
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        logger.warning(f"Failed to load GENIUS thresholds from spec: {e}. Using fallback.")
        # Fallback to hardcoded if spec unavailable
        return {
            "g_seal": 0.8,
            "g_void": 0.5,
            "c_dark_seal": 0.3,
            "c_dark_sabar": 0.6,
            "psi_seal": 1.0,
            "psi_sabar": 0.95,
        }

_GENIUS_THRESHOLDS = _load_genius_thresholds()
G_SEAL_THRESHOLD = _GENIUS_THRESHOLDS["g_seal"]
G_VOID_THRESHOLD = _GENIUS_THRESHOLDS["g_void"]
C_DARK_SEAL_THRESHOLD = _GENIUS_THRESHOLDS["c_dark_seal"]
C_DARK_SABAR_THRESHOLD = _GENIUS_THRESHOLDS["c_dark_sabar"]
PSI_SEAL_THRESHOLD = _GENIUS_THRESHOLDS["psi_seal"]
PSI_SABAR_THRESHOLD = _GENIUS_THRESHOLDS["psi_sabar"]

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


# Anti-Hantu enforcement: DELEGATED to @EYE Sentinel
# (Initialized at line ~338: self.eye_sentinel = self._init_eye_sentinel())
# NO local duplicate check - trust core enforcement

def detect_lane(query: str) -> str:
    """
    Detect query lane (PHATIC, SOFT, HARD, REFUSE).

    DELEGATES to arifos_core.routing.prompt_router (single source of truth).
    """
    if classify_prompt_lane is None:
        # Fallback if core unavailable
        return "SOFT"

    lane = classify_prompt_lane(query, high_stakes_indicators=[])
    return lane.value  # Convert ApplicabilityLane enum to string


def get_verdict_string(state) -> str:
    """
    Extract verdict from pipeline state (set by Stage 888 JUDGE).

    DELEGATES to apex_prime.apex_review() (single authority).
    """
    if hasattr(state, "verdict"):
        return state.verdict.value if hasattr(state.verdict, "value") else str(state.verdict)

    # If pipeline didn't set verdict, that's a BUG in pipeline (not adapter's job to guess)
    logger.error("Pipeline failed to set verdict at Stage 888 - defaulting to VOID")
    return "VOID"


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
        # Validate critical dependencies
        if not PIPELINE_AVAILABLE:
            raise RuntimeError(
                "Missing required dependency: arifOS Pipeline unavailable.\n"
                "  Install: pip install -e .[dev]"
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

        # Initialize governance components with status tracking
        init_status = self._init_components(
            enable_waw=enable_waw,
            enable_memory=enable_memory,
            enable_session_physics=enable_session_physics
        )

        # Critical check: Pipeline MUST be created
        if self.pipeline is None:
            raise RuntimeError(
                "Failed to initialize Pipeline (critical component). "
                "Check logs for details."
            )

        logger.info(f"GovernedSEALionClient initialized (Session: {self.session_id})")
        logger.info(f"  Component status: {init_status}")

    def _init_components(
        self,
        enable_waw: bool,
        enable_memory: bool,
        enable_session_physics: bool
    ) -> Dict[str, bool]:
        """
        Initialize all governance components with status tracking.

        Returns:
            Dict mapping component name to success status
        """
        status = {}

        # 1. Ledger sink (required for audit trail)
        try:
            self.ledger_sink = self._create_ledger_sink()
            status["ledger_sink"] = True
            logger.info("✓ Ledger sink initialized")
        except Exception as e:
            logger.error(f"✗ Ledger sink init failed: {e}", exc_info=True)
            status["ledger_sink"] = False
            self.ledger_sink = None

        # 2. @EYE Sentinel (F9 Anti-Hantu - recommended but not critical)
        self.eye_sentinel = self._init_eye_sentinel()
        status["eye_sentinel"] = self.eye_sentinel is not None

        # 3. W@W Federation (multi-agent veto - optional)
        if enable_waw:
            self.waw_federation = self._init_waw_federation()
            status["waw_federation"] = self.waw_federation is not None
        else:
            self.waw_federation = None
            status["waw_federation"] = False  # Disabled by user

        # 4. Memory Band Router (6 bands - recommended)
        if enable_memory:
            self.memory_router = self._init_memory_router()
            self.vault = self._load_vault()
            status["memory_router"] = self.memory_router is not None
            status["vault"] = self.vault is not None
        else:
            self.memory_router = None
            self.vault = None
            status["memory_router"] = False  # Disabled by user
            status["vault"] = False

        # 5. Session Physics (TEARFRAME - optional)
        if enable_session_physics:
            self.session_telemetry = self._init_session_physics()
            status["session_physics"] = self.session_telemetry is not None
        else:
            self.session_telemetry = None
            status["session_physics"] = False  # Disabled by user

        # 6. Governed LLM generator (wraps RAW client - critical)
        try:
            self.governed_generate = self._create_governed_generator()
            if self.governed_generate is None:
                logger.warning("Governed generator unavailable; falling back to RAW generate.")
                self.governed_generate = lambda prompt, lane=None: self.raw.generate(prompt)
                status["governed_generate"] = False  # Fallback mode
            else:
                status["governed_generate"] = True
        except Exception as e:
            logger.error(f"✗ Governed generator init failed: {e}", exc_info=True)
            # Fallback to RAW
            self.governed_generate = lambda prompt, lane=None: self.raw.generate(prompt)
            status["governed_generate"] = False

        # 7. Pipeline (CRITICAL - must succeed)
        try:
            self.pipeline = Pipeline(
                llm_generate=self.governed_generate,
                context_retriever=self._get_chat_context_blocks,
                context_retriever_at_stage_111=True,
                ledger_sink=self.ledger_sink,
                eye_sentinel=self.eye_sentinel,
            )
            status["pipeline"] = True
            logger.info("✓ Pipeline (000→999) initialized")
        except Exception as e:
            logger.critical(f"✗ Pipeline init FAILED (critical): {e}", exc_info=True)
            self.pipeline = None
            status["pipeline"] = False

        return status

    def _create_ledger_sink(self):
        """Create hash-chained JSONL ledger sink."""
        path = Path(self.ledger_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if not MEMORY_BANDS_AVAILABLE:
            # Minimal ledger (just append JSON lines with validation)
            def minimal_sink(entry: dict) -> None:
                try:
                    # Validate required keys
                    required_keys = ["timestamp", "session_id", "query"]
                    missing = [k for k in required_keys if k not in entry]
                    if missing:
                        logger.warning(f"Ledger entry missing keys: {missing}")
                        # Add defaults
                        if "timestamp" not in entry:
                            entry["timestamp"] = datetime.now(timezone.utc).isoformat()
                        if "session_id" not in entry:
                            entry["session_id"] = self.session_id

                    with open(path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                except (IOError, OSError) as e:
                    logger.error(f"Ledger file write failed: {e}")
                except (TypeError, ValueError) as e:
                    logger.error(f"Ledger entry serialization failed: {e}")
            return minimal_sink

        # Full hash-chained ledger
        def sink(entry: dict) -> None:
            try:
                append_entry(path, dict(entry))
            except (IOError, OSError) as e:
                logger.error(f"Ledger append failed (file error): {e}")
            except (TypeError, ValueError, KeyError) as e:
                logger.error(f"Ledger append failed (data error): {e}")
        return sink

    def _init_eye_sentinel(self):
        """Initialize @EYE Sentinel (F9 Anti-Hantu enforcement)."""
        if not EYE_AVAILABLE:
            logger.info("@EYE Sentinel unavailable (module not found)")
            return None
        try:
            eye = EyeSentinel()
            logger.info("✓ @EYE Sentinel initialized (F9 Anti-Hantu active)")
            return eye
        except (ImportError, AttributeError, TypeError) as e:
            logger.warning(f"✗ @EYE Sentinel init failed: {e}")
            return None

    def _init_waw_federation(self):
        """Initialize W@W Federation (multi-agent veto authority)."""
        if not WAW_AVAILABLE:
            logger.info("W@W Federation unavailable (module not found)")
            return None
        try:
            waw = WAWFederationCore()
            logger.info("✓ W@W Federation initialized (@LAW, @GEOX, @WELL, @RIF active)")
            return waw
        except (ImportError, AttributeError, TypeError) as e:
            logger.warning(f"✗ W@W Federation init failed: {e}")
            return None

    def _init_memory_router(self):
        """Initialize Memory Band Router (6 bands)."""
        if not MEMORY_BANDS_AVAILABLE:
            logger.info("Memory Band Router unavailable (module not found)")
            return None
        try:
            router = MemoryBandRouter()
            logger.info("✓ Memory Band Router initialized (VAULT/LEDGER/ACTIVE/PHOENIX/WITNESS/VOID)")
            return router
        except (ImportError, AttributeError, TypeError) as e:
            logger.warning(f"✗ Memory Band Router init failed: {e}")
            return None

    def _init_session_physics(self):
        """Initialize Session Physics (TEARFRAME)."""
        if not SESSION_PHYSICS_AVAILABLE:
            logger.info("Session Physics unavailable (module not found)")
            return None
        try:
            telemetry = SessionTelemetry(session_id=self.session_id)
            logger.info("✓ Session Physics (TEARFRAME) initialized")
            return telemetry
        except (ImportError, AttributeError, TypeError) as e:
            logger.warning(f"✗ Session Physics init failed: {e}")
            return None

    def _load_vault(self):
        """Load VAULT_999 (Constitutional canon - immutable)."""
        if not MEMORY_BANDS_AVAILABLE:
            logger.info("VAULT_999 unavailable (Memory Bands module not found)")
            return None
        try:
            vault = Vault999()
            logger.info("✓ VAULT_999 loaded (Constitutional canon immutable)")
            return vault
        except (ImportError, FileNotFoundError, AttributeError) as e:
            logger.warning(f"✗ VAULT_999 load failed: {e}")
            return None

    def _create_governed_generator(self):
        """
        Create governed LLM generator that wraps RAW client.

        This is the bridge: Pipeline calls this, which calls RAW client.
        """
        global make_llm_generate, LiteLLMConfig, LITELLM_AVAILABLE

        if make_llm_generate is None or LiteLLMConfig is None:
            try:
                from arifos_core.connectors.litellm_gateway import make_llm_generate as _make, LiteLLMConfig as _cfg

                make_llm_generate = _make
                LiteLLMConfig = _cfg
            except Exception as e:
                LITELLM_AVAILABLE = False
                logger.warning(f"LiteLLM gateway import failed: {e}")
                return None

        try:
            config = LiteLLMConfig(
                provider="openai",
                api_base=self.raw.api_base,
                api_key=self.raw.api_key,
                model=self.raw.model,
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=DEFAULT_MAX_TOKENS,
            )
            base_generate = make_llm_generate(config)
        except Exception as e:
            logger.warning(f"LiteLLM generator init failed: {e}")
            return None

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

    def _detect_lane_and_crisis(self, query: str) -> Tuple[str, bool, str]:
        """
        Detect query lane and check for crisis patterns.

        Returns:
            (lane, is_crisis, crisis_msg) tuple
        """
        lane = detect_lane(query)
        self.lanes[lane] += 1

        is_crisis, crisis_msg = detect_crisis(query)
        if is_crisis:
            self.lanes["CRISIS"] = self.lanes.get("CRISIS", 0) + 1
            self.verdicts["888_HOLD"] += 1

        return lane, is_crisis, crisis_msg

    def _get_raw_response(
        self, query: str, max_tokens: int, temperature: float
    ) -> Dict[str, Any]:
        """
        Get ungoverned response from RAW client.

        Returns:
            RAW client result dict with "response" and "metadata" keys
        """
        return self.raw.generate(query, max_tokens=max_tokens, temperature=temperature)

    def _run_pipeline_and_genius(self, query: str):
        """
        Run query through arifOS Pipeline and compute GENIUS metrics.

        Returns:
            (state, genius_verdict) tuple
        """
        # Run through arifOS Pipeline (000->999)
        state = self.pipeline.run(query)
        self.last_state = state

        # Compute GENIUS metrics
        genius_verdict = None
        if hasattr(state, "metrics") and state.metrics:
            try:
                genius_verdict = compute_genius_index(state.metrics)
                self.last_genius_verdict = genius_verdict
            except Exception as e:
                logger.warning(f"GENIUS computation failed: {e}")

        return state, genius_verdict

    def _apply_penalties_and_verdict(
        self,
        state,
        genius_verdict,
        lane: str,
        raw_response: str,
    ) -> Tuple[str, str]:
        """
        Apply penalties (PHATIC verbosity, C_dark hazard) and finalize verdict.

        Returns:
            (final_response, final_verdict) tuple
        """
        # Extract base verdict from pipeline
        verdict_str = get_verdict_string(state)

        # Get governed response (or fallback to RAW)
        governed_response = state.draft_response if hasattr(state, "draft_response") else raw_response

        # PHATIC verbosity penalty (BEFORE final verdict - Grok fix)
        if lane == "PHATIC" and len(governed_response) > PHATIC_VERBOSITY_CEILING:
            logger.info(
                f"PHATIC verbosity penalty: {len(governed_response)} chars "
                f"(ceiling: {PHATIC_VERBOSITY_CEILING})"
            )
            verdict_str = "PARTIAL"

        # C_dark hazard check (evil genius pattern)
        if genius_verdict and genius_verdict.c_dark >= C_DARK_SABAR_THRESHOLD:
            logger.warning(f"C_dark hazard detected: {genius_verdict.c_dark:.3f}")
            verdict_str = "SABAR"
            governed_response = "Hold on - I want to ensure this guidance is helpful and safe."

        return governed_response, verdict_str

    def generate(
        self,
        query: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> Dict[str, Any]:
        """
        Generate governed response.

        Flow:
        1. Detect lane (PHATIC/SOFT/HARD/REFUSE) and check crisis patterns
        2. Get RAW response from base client
        3. Run through arifOS Pipeline (000->999)
        4. Compute GENIUS metrics (G, C_dark, Psi, TP)
        5. Apply penalties (PHATIC verbosity, C_dark hazard) and finalize verdict
        6. Return verdict + metrics + governed output

        Returns:
            {
                "response": str,           # Governed output (or crisis message)
                "verdict": str,            # SEAL/VOID/PARTIAL/SABAR/888_HOLD/SUNSET
                "lane": str,               # PHATIC/SOFT/HARD/REFUSE/CRISIS
                "metrics": dict,           # All 9 constitutional floors
                "genius": dict,            # G, C_dark, Psi, TP
                "raw_response": str,       # Original ungoverned response
                "raw_metadata": dict,      # RAW client metadata
            }
        """
        # 1. Detect lane and check crisis patterns
        lane, is_crisis, crisis_msg = self._detect_lane_and_crisis(query)

        if is_crisis:
            return {
                "response": crisis_msg,
                "verdict": "888_HOLD",
                "lane": "CRISIS",
                "metrics": {"amanah": False},
                "genius": None,
                "raw_response": "[CRISIS OVERRIDE]",
                "raw_metadata": {},
            }

        # 2. Get RAW response (delegate to base client)
        raw_result = self._get_raw_response(query, max_tokens, temperature)
        raw_response = raw_result["response"]

        # 3. Run through arifOS Pipeline (000->999) and compute GENIUS metrics
        try:
            state, genius_verdict = self._run_pipeline_and_genius(query)
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
            }

        # 4. Apply penalties and finalize verdict
        governed_response, verdict_str = self._apply_penalties_and_verdict(
            state, genius_verdict, lane, raw_response
        )

        # Update verdict statistics
        self.verdicts[verdict_str] = self.verdicts.get(verdict_str, 0) + 1

        # 5. Store turn history
        self.turns.append((query, governed_response))

        # 6. Return complete result
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
        print("[ERROR] ERROR: No SEA-LION API key found.")
        print("   Set SEALION_API_KEY or ARIF_LLM_API_KEY environment variable.")
        sys.exit(1)

    # Create RAW client (Phase 1)
    print("[INFO] Creating RAW client...")
    raw = RawSEALionClient(
        api_key=api_key,
        model="aisingapore/Qwen-SEA-LION-v4-32B-IT",
        enable_memory=False,  # Disable MemOS for quick test
        enable_tools=False,   # Disable tools for quick test
    )

    # Wrap with governance (Phase 2)
    print("[INFO] Creating governance wrapper...")
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
            print(f"\n[Q] Query ({lane}): {query}")

            # Generate governed response
            result = governed.generate(query)

            print(f"\n[RAW] RAW: {result['raw_response'][:200]}...")
            print(f"\n[OK] GOVERNED: {result['response'][:200]}...")
            print(f"   Verdict: {result['verdict']} | Lane: {result['lane']}")
            if result['genius']:
                print(f"   G: {result['genius']['G']:.2f} | C_dark: {result['genius']['C_dark']:.2f} | Psi: {result['genius']['Psi']:.2f}")

        print("\n" + "="*60)
        print("[OK] Test complete. Governance layer operational.")
        print("="*60)

    else:
        print("\n[INFO]  Use --test to run quick verification test.")


if __name__ == "__main__":
    main()
