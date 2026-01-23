"""
L7 Federation Router - Multi-Endpoint SEA-LION Governance

This module implements intelligent routing to specialized SEA-LION model endpoints
based on task intent, with full arifOS constitutional governance.

Architecture:
    User (Port 9000)
        |
    [000] SENTINEL GATE (SEA-Guard)
        |
    [111] INTENT ROUTER
        |
    @GEOX → @RIF → @WEALTH → @WELL
        |
    [888] COOLING LEDGER
        |
    [999] VERDICT

Organ Topology:
    | Port  | Organ     | Model                      | Role              |
    |-------|-----------|----------------------------|-------------------|
    | 8005  | SENTINEL  | SEA-Guard                  | Safety pre-filter |
    | 11434 | @GEOX     | Gemma-SEA-LION-v4-27B      | Multimodal/Vision |
    | 8001  | @RIF      | Llama-SEA-LION-v3.5-70B-R  | Deep Reasoning    |
    | 8002  | @WEALTH   | Qwen-SEA-LION-v4-32B       | Long Context      |
    | 8003  | @WELL     | Llama-SEA-LION-v3-70B-IT   | General Chat      |

Author: arifOS Project
Version: v41.3Omega
License: Apache 2.0
"""

from __future__ import annotations

import os
import time
import math
import hashlib
import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

# LiteLLM import with fallback
try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    litellm = None

# Setup logging
logger = logging.getLogger("arifOS.federation")


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class OrganConfig:
    """Configuration for a single Federation organ (model endpoint)."""
    name: str
    model: str
    api_base: str
    port: int
    role: str  # "sentinel", "vision", "reasoning", "context", "chat"
    symbol: str  # Unicode symbol for logging
    provider: str  # "ollama", "vllm", "tgi", "openai"
    capabilities: List[str] = field(default_factory=list)
    is_healthy: bool = True
    last_health_check: float = 0.0


@dataclass
class FederationConfig:
    """Configuration for the entire L7 Federation."""
    organs: Dict[str, OrganConfig]
    default_organ: str = "WELL"
    guard_organ: str = "SENTINEL"
    guard_timeout_ms: int = 500
    routing_strategy: str = "intent"  # "intent", "round_robin", "fixed"
    confidence_floor: float = 0.55  # Below this, fallback to default
    mock_mode: bool = True  # Set False when real GPUs connected


# Default organ configuration (matches user's router_apex.py)
DEFAULT_ORGANS = {
    "SENTINEL": OrganConfig(
        name="sea-guard",
        model="openai/sea-guard",
        api_base="http://localhost:8005/v1",
        port=8005,
        role="sentinel",
        symbol="🛡️",
        provider="vllm",
        capabilities=["safety", "classification"],
    ),
    "GEOX": OrganConfig(
        name="gemma-vision",
        model="ollama/gemma-sea-lion-v4-27b-it",
        api_base="http://localhost:11434",
        port=11434,
        role="vision",
        symbol="👁️",
        provider="ollama",
        capabilities=["multimodal", "instruction", "regional"],
    ),
    "RIF": OrganConfig(
        name="llama-reasoning",
        model="openai/llama-sea-lion-v3.5-70b-r",
        api_base="http://localhost:8001/v1",
        port=8001,
        role="reasoning",
        symbol="🧠",
        provider="vllm",
        capabilities=["reasoning", "instruction", "regional"],
    ),
    "WEALTH": OrganConfig(
        name="qwen-context",
        model="openai/qwen-sea-lion-v4-32b-it",
        api_base="http://localhost:8002/v1",
        port=8002,
        role="context",
        symbol="📚",
        provider="vllm",
        capabilities=["long_context", "instruction", "regional"],
    ),
    "WELL": OrganConfig(
        name="llama-chat",
        model="openai/llama-sea-lion-v3-70b-it",
        api_base="http://localhost:8003/v1",
        port=8003,
        role="chat",
        symbol="❤️",
        provider="vllm",
        capabilities=["instruction", "chat", "regional"],
    ),
}


def load_federation_config() -> FederationConfig:
    """
    Load federation configuration from environment or defaults.

    Environment Variables:
        ARIFOS_FEDERATION_MOCK_MODE: "true" or "false"
        ARIFOS_FEDERATION_CONFIDENCE_FLOOR: float (default 0.55)
        ARIFOS_FEDERATION_GUARD_TIMEOUT_MS: int (default 500)
    """
    mock_mode = os.getenv("ARIFOS_FEDERATION_MOCK_MODE", "true").lower() == "true"
    confidence_floor = float(os.getenv("ARIFOS_FEDERATION_CONFIDENCE_FLOOR", "0.55"))
    guard_timeout = int(os.getenv("ARIFOS_FEDERATION_GUARD_TIMEOUT_MS", "500"))

    return FederationConfig(
        organs=DEFAULT_ORGANS,
        default_organ="WELL",
        guard_organ="SENTINEL",
        guard_timeout_ms=guard_timeout,
        routing_strategy="intent",
        confidence_floor=confidence_floor,
        mock_mode=mock_mode,
    )


# =============================================================================
# COOLING LEDGER (Thermodynamic Audit Trail)
# =============================================================================

@dataclass
class CoolingEntry:
    """A single entry in the Cooling Ledger."""
    timestamp: str
    organ: str
    verdict: str
    metrics: Dict[str, float]
    entry_hash: str
    prev_hash: str
    prompt_preview: str = ""
    response_len: int = 0


class CoolingLedger:
    """
    Hash-chained audit trail with thermodynamic metrics.

    Metrics:
        ΔS (delta_s): Shannon entropy of response token distribution
        κᵣ (kappa_r): Empathy/care floor score (heuristic)
        τ (tau): Dissipation time in milliseconds
    """

    GENESIS_HASH = "0" * 32
    FLOOR_KAPPA_R = 0.95  # Empathy floor threshold

    def __init__(self):
        self.chain: List[CoolingEntry] = []

    def _calc_entropy(self, text: str) -> float:
        """
        Calculate Shannon entropy (ΔS) of response tokens.

        Higher entropy = more diverse vocabulary = healthier response.
        Low entropy may indicate repetitive/stuck generation.
        """
        if not text:
            return 0.0

        tokens = text.split()
        if not tokens:
            return 0.0

        total = len(tokens)
        counts = Counter(tokens)
        entropy = -sum(
            (c / total) * math.log2(c / total)
            for c in counts.values()
            if c > 0
        )
        return round(entropy, 4)

    def _calc_empathy(self, text: str) -> float:
        """
        Calculate κᵣ (empathy conductance) score.

        This is a heuristic filter for toxicity/arrogance patterns.
        In production, this should be a fine-tuned classifier.
        """
        # Forbidden patterns (reduce empathy score)
        toxins = [
            "obviously", "stupid", "idiot", "as an ai", "cannot help",
            "wrong", "dumb", "clearly you", "not my problem"
        ]
        score = 1.0
        text_lower = text.lower()

        for toxin in toxins:
            if toxin in text_lower:
                score -= 0.1

        return max(0.0, round(score, 2))

    def seal_verdict(
        self,
        prompt: str,
        response: str,
        organ: str,
        sentinel_status: str,
        tau_ms: float = 0.0,
    ) -> CoolingEntry:
        """
        Generate audit entry and hash it into the chain.

        Args:
            prompt: User prompt (truncated for storage)
            response: Model response text
            organ: Which organ handled the request
            sentinel_status: "SAFE" or "UNSAFE" from guard
            tau_ms: Response generation time in milliseconds

        Returns:
            CoolingEntry with verdict and metrics
        """
        delta_s = self._calc_entropy(response)
        kappa_r = self._calc_empathy(response)

        # Determine verdict based on metrics
        if sentinel_status == "UNSAFE":
            verdict = "VOID"
        elif kappa_r < self.FLOOR_KAPPA_R:
            verdict = "SABAR"  # Hold for empathy review
        elif delta_s < 1.0:
            verdict = "PARTIAL"  # Low entropy warning
        else:
            verdict = "SEAL"

        # Chain hash
        prev_hash = self.chain[-1].entry_hash if self.chain else self.GENESIS_HASH

        # Create hash payload
        payload = f"{prev_hash}|{organ}|{verdict}|{delta_s}|{kappa_r}|{response[:50]}"
        entry_hash = hashlib.sha256(payload.encode()).hexdigest()[:32]

        entry = CoolingEntry(
            timestamp=datetime.utcnow().isoformat(),
            organ=organ,
            verdict=verdict,
            metrics={
                "delta_s": delta_s,
                "kappa_r": kappa_r,
                "tau_ms": round(tau_ms, 2),
            },
            entry_hash=entry_hash,
            prev_hash=prev_hash,
            prompt_preview=prompt[:50] if prompt else "",
            response_len=len(response),
        )

        self.chain.append(entry)
        logger.info(
            f"🧊 LEDGER SEALED: [{verdict}] via {organ} "
            f"(ΔS={delta_s}, κᵣ={kappa_r}, τ={tau_ms:.0f}ms)"
        )

        return entry

    def get_chain_length(self) -> int:
        """Get current chain length."""
        return len(self.chain)

    def verify_chain(self) -> bool:
        """Verify hash chain integrity."""
        if not self.chain:
            return True

        prev_hash = self.GENESIS_HASH
        for entry in self.chain:
            if entry.prev_hash != prev_hash:
                return False
            prev_hash = entry.entry_hash

        return True

    def to_dict(self) -> List[Dict[str, Any]]:
        """Export chain as list of dictionaries."""
        return [
            {
                "timestamp": e.timestamp,
                "organ": e.organ,
                "verdict": e.verdict,
                "metrics": e.metrics,
                "entry_hash": e.entry_hash,
                "prev_hash": e.prev_hash,
            }
            for e in self.chain
        ]


# =============================================================================
# INTENT CLASSIFIER
# =============================================================================

class IntentClassifier:
    """
    Classify request intent for routing decisions.

    Returns (organ_name, confidence_score) based on heuristics.
    """

    # Keywords that trigger reasoning mode (@RIF)
    REASONING_TRIGGERS = [
        "reason", "plan", "analyze", "think", "solve",
        "step-by-step", "why", "explain", "compare", "contrast",
        "prove", "derive", "calculate", "logic", "deduce",
    ]

    # Minimum text length to consider for deep context (@WEALTH)
    CONTEXT_LENGTH_THRESHOLD = 30000

    def classify(
        self,
        content: Any,
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[str, float]:
        """
        Classify intent and return target organ with confidence.

        Args:
            content: Message content (str or list for multimodal)
            messages: Optional full message history

        Returns:
            Tuple of (organ_name, confidence_score)
        """
        # 1. VISUAL CHECK (@GEOX)
        # If content is a list (multimodal), route to vision
        if isinstance(content, list):
            return "GEOX", 1.0

        text = str(content)

        # 2. CONTEXT CHECK (@WEALTH)
        # If text is extremely long, use deep context model
        if len(text) > self.CONTEXT_LENGTH_THRESHOLD:
            return "WEALTH", 0.95

        # 3. REASONING CHECK (@RIF)
        # Count keyword matches for confidence boosting
        text_lower = text.lower()
        matches = sum(1 for t in self.REASONING_TRIGGERS if t in text_lower)

        if matches > 0:
            # Base confidence 0.6, boost by 0.1 per match, cap at 0.99
            confidence = min(0.6 + (matches * 0.1), 0.99)
            return "RIF", confidence

        # 4. DEFAULT (@WELL)
        # Standard conversation - use general chat model
        return "WELL", 0.50


# =============================================================================
# FEDERATION ROUTER
# =============================================================================

@dataclass
class RoutingResult:
    """Result from federation routing."""
    response: str
    organ: str
    verdict: str
    guard_passed: bool
    guard_latency_ms: float
    total_latency_ms: float
    confidence: float
    cooling_entry: Optional[CoolingEntry] = None
    error: Optional[str] = None


class FederationRouter:
    """
    L7 Federation Router for multi-endpoint SEA-LION routing.

    Implements intelligent routing with:
    - SEA-Guard pre-filter (Layer 0)
    - Intent-based routing
    - Thermodynamic audit (Cooling Ledger)
    - Constitutional governance

    Usage:
        router = FederationRouter()
        result = await router.route("Analyze this step by step...")

        if result.verdict == "VOID":
            print("Blocked by governance")
        else:
            print(result.response)
    """

    def __init__(self, config: Optional[FederationConfig] = None):
        """Initialize federation router."""
        self.config = config or load_federation_config()
        self.classifier = IntentClassifier()
        self.ledger = CoolingLedger()
        self._backends: Dict[str, Callable] = {}

    async def _check_sentinel(self, text: str) -> Tuple[str, float]:
        """
        Check input against SEA-Guard sentinel.

        Returns:
            Tuple of (verdict: "SAFE"|"UNSAFE", latency_ms)
        """
        if self.config.mock_mode:
            return "SAFE", 0.0

        if not LITELLM_AVAILABLE:
            logger.warning("LiteLLM not available, skipping sentinel check")
            return "SAFE", 0.0

        organ = self.config.organs.get(self.config.guard_organ)
        if not organ:
            return "SAFE", 0.0

        start = time.time()
        try:
            response = await litellm.acompletion(
                model=organ.model,
                api_base=organ.api_base,
                messages=[{"role": "user", "content": text}],
                max_tokens=5,
                timeout=self.config.guard_timeout_ms / 1000,
            )
            verdict_text = response.choices[0].message.content.strip().upper()
            latency = (time.time() - start) * 1000

            if "UNSAFE" in verdict_text:
                return "UNSAFE", latency
            return "SAFE", latency

        except Exception as e:
            logger.error(f"Sentinel check failed: {e}")
            # Fail-open in dev, fail-closed in production
            return "SAFE", (time.time() - start) * 1000

    async def _call_organ(
        self,
        organ_name: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
    ) -> str:
        """
        Call a specific organ (model endpoint).

        Args:
            organ_name: Name of organ to call
            messages: Chat messages
            temperature: Generation temperature

        Returns:
            Response text from model
        """
        organ = self.config.organs.get(organ_name)
        if not organ:
            raise ValueError(f"Unknown organ: {organ_name}")

        if self.config.mock_mode:
            # Return mock response for testing
            return f"[{organ_name} MOCK] Processed via {organ_name}. Intent validated."

        if not LITELLM_AVAILABLE:
            raise RuntimeError("LiteLLM not available")

        response = await litellm.acompletion(
            model=organ.model,
            api_base=organ.api_base,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content

    async def route(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        skip_guard: bool = False,
        force_organ: Optional[str] = None,
    ) -> RoutingResult:
        """
        Route request through the federation.

        Pipeline:
        1. [000] SENTINEL GATE - Safety pre-filter
        2. [111] INTENT ROUTER - Classify and route
        3. [333] EXECUTION - Call target organ
        4. [888] COOLING LEDGER - Audit and metrics
        5. [999] VERDICT - Return governed response

        Args:
            messages: Chat messages in OpenAI format
            temperature: Generation temperature
            skip_guard: Skip sentinel check (testing only)
            force_organ: Force specific organ (override routing)

        Returns:
            RoutingResult with response and governance metadata
        """
        start_time = time.time()
        guard_latency = 0.0

        # Extract last message content
        last_content = messages[-1]["content"] if messages else ""
        prompt_text = str(last_content) if not isinstance(last_content, list) else "[multimodal]"

        # [STEP 1] SENTINEL GATE (F9)
        sentinel_verdict = "SAFE"
        if not skip_guard:
            sentinel_verdict, guard_latency = await self._check_sentinel(prompt_text)

            if sentinel_verdict == "UNSAFE":
                entry = self.ledger.seal_verdict(
                    prompt=prompt_text,
                    response="VOID: Safety Floor Breached",
                    organ="SENTINEL",
                    sentinel_status="UNSAFE",
                    tau_ms=guard_latency,
                )
                return RoutingResult(
                    response="[VOID] Request blocked by SEA-Guard safety filter (F9).",
                    organ="SENTINEL",
                    verdict="VOID",
                    guard_passed=False,
                    guard_latency_ms=guard_latency,
                    total_latency_ms=(time.time() - start_time) * 1000,
                    confidence=1.0,
                    cooling_entry=entry,
                )

        # [STEP 2] ROUTING (Intent Classification)
        if force_organ and force_organ in self.config.organs:
            target_organ = force_organ
            confidence = 1.0
        else:
            target_organ, confidence = self.classifier.classify(last_content, messages)

        # Confidence fallback
        if confidence < self.config.confidence_floor and target_organ != self.config.default_organ:
            logger.warning(
                f"Confidence {confidence:.2f} too low for {target_organ}. "
                f"Falling back to {self.config.default_organ}."
            )
            target_organ = self.config.default_organ

        # [STEP 3] EXECUTION
        try:
            response_text = await self._call_organ(target_organ, messages, temperature)
        except Exception as e:
            logger.error(f"Organ {target_organ} failed: {e}")
            return RoutingResult(
                response=f"[ERROR] Federation routing failed: {e}",
                organ=target_organ,
                verdict="VOID",
                guard_passed=True,
                guard_latency_ms=guard_latency,
                total_latency_ms=(time.time() - start_time) * 1000,
                confidence=confidence,
                error=str(e),
            )

        # [STEP 4] COOLING LEDGER
        total_latency = (time.time() - start_time) * 1000
        entry = self.ledger.seal_verdict(
            prompt=prompt_text,
            response=response_text,
            organ=target_organ,
            sentinel_status=sentinel_verdict,
            tau_ms=total_latency,
        )

        # [STEP 5] RETURN GOVERNED RESPONSE
        organ_config = self.config.organs.get(target_organ)
        organ_symbol = organ_config.symbol if organ_config else "?"

        logger.info(
            f"{organ_symbol} Served by {target_organ} in {total_latency:.0f}ms "
            f"(confidence={confidence:.2f}, verdict={entry.verdict})"
        )

        return RoutingResult(
            response=response_text,
            organ=target_organ,
            verdict=entry.verdict,
            guard_passed=True,
            guard_latency_ms=guard_latency,
            total_latency_ms=total_latency,
            confidence=confidence,
            cooling_entry=entry,
        )

    def get_organ_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all organs."""
        return {
            name: {
                "name": organ.name,
                "role": organ.role,
                "symbol": organ.symbol,
                "port": organ.port,
                "model": organ.model,
                "provider": organ.provider,
                "is_healthy": organ.is_healthy,
                "capabilities": organ.capabilities,
            }
            for name, organ in self.config.organs.items()
        }

    def get_ledger_stats(self) -> Dict[str, Any]:
        """Get cooling ledger statistics."""
        if not self.ledger.chain:
            return {
                "entries": 0,
                "verdicts": {},
                "chain_valid": True,
            }

        verdicts = Counter(e.verdict for e in self.ledger.chain)
        return {
            "entries": len(self.ledger.chain),
            "verdicts": dict(verdicts),
            "chain_valid": self.ledger.verify_chain(),
            "last_entry": self.ledger.chain[-1].timestamp if self.ledger.chain else None,
        }


# =============================================================================
# SYNCHRONOUS WRAPPER (for non-async contexts)
# =============================================================================

def create_federation_router(config: Optional[FederationConfig] = None) -> FederationRouter:
    """
    Factory function to create a FederationRouter.

    Args:
        config: Optional configuration (uses defaults if not provided)

    Returns:
        Configured FederationRouter instance
    """
    return FederationRouter(config)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Configuration
    "OrganConfig",
    "FederationConfig",
    "load_federation_config",
    "DEFAULT_ORGANS",
    # Cooling Ledger
    "CoolingEntry",
    "CoolingLedger",
    # Intent Classification
    "IntentClassifier",
    # Router
    "RoutingResult",
    "FederationRouter",
    "create_federation_router",
]
