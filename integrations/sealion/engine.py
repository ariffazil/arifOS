# integrations/sealion/engine.py
"""
SEA-LION Engine with PHOENIX SOVEREIGNTY Amanah Lock (v36.1Omega)

This module extracts SEA-LION client logic and enforces Python-sovereign
Amanah detection via AMANAH_DETECTOR.

MISSION: "Dumb Code, Smart Model" - One Law for All Models
    - SEA-LION is a capable regional LLM
    - Python governance is the final veto
    - If SEA-LION outputs "rm -rf /", Python says NO

Usage:
    from integrations.sealion.engine import SealionEngine, SealionConfig

    engine = SealionEngine(api_key="your-key")
    result = engine.generate("What is AI governance?")

    # Check for Python veto
    if result.amanah_blocked:
        print("BLOCKED by Python governance!")
        print(result.amanah_violations)

Author: arifOS Project
License: Apache 2.0
Version: 36.1Omega
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

# PHOENIX SOVEREIGNTY: Import Python-sovereign Amanah detector
_AMANAH_DETECTOR = None
_AMANAH_AVAILABLE = False

try:
    from arifos_core.floor_detectors.amanah_risk_detectors import (
        AMANAH_DETECTOR as _AMANAH_DETECTOR,
        AmanahResult,
    )
    _AMANAH_AVAILABLE = True
except ImportError:
    # Fallback: create stub
    @dataclass
    class AmanahResult:
        is_safe: bool = True
        violations: List[str] = field(default_factory=list)
        warnings: List[str] = field(default_factory=list)

        def to_dict(self) -> Dict:
            return {
                "is_safe": self.is_safe,
                "violations": self.violations,
                "warnings": self.warnings,
            }

# Try to import the existing SEA-LION client
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# ============================================================================
# v36.2 PHOENIX: ROBUST RESPONSE EXTRACTION
# ============================================================================

def extract_response_robust(full_text: str, input_prompt: str = "") -> str:
    """
    v36.2 PHOENIX PATCH: Tokenizer Hygiene.

    Handles ChatML (<|im_start|>) and Standard formats to prevent
    truncation artifacts like 'm?' or dropped first words.

    The Problem (v36.1):
        Qwen-SEA-LION uses ChatML format with <|im_start|>assistant tokens.
        Simple string splitting on "Assistant:" caused:
        - First word chopped ("m?" instead of "Terima kasih")
        - Incomplete extraction with ChatML tokens remaining

    The Fix (v36.2 PHOENIX):
        1. ChatML detection: Split on <|im_start|>assistant, strip <|im_end|>
        2. Llama/Mistral: Split on standard separators
        3. Fallback: Length-based slicing if prompt provided

    Args:
        full_text: Raw model output (may include special tokens)
        input_prompt: Original input prompt (for fallback slicing)

    Returns:
        Clean extracted response text

    Example:
        # ChatML format (Qwen)
        text = "<|im_start|>user\\nHello<|im_end|>\\n<|im_start|>assistant\\nHi there!<|im_end|>"
        result = extract_response_robust(text)
        # result == "Hi there!"

        # Llama format
        text = "User: Hello\\nAssistant: Hi there!"
        result = extract_response_robust(text)
        # result == "Hi there!"
    """
    if not full_text:
        return ""

    # 1. ChatML Standard (Qwen/InternLM/ChatML-compliant models)
    if "<|im_start|>assistant" in full_text:
        response = full_text.split("<|im_start|>assistant")[-1]
        # Clean up ChatML end tokens and newlines
        response = response.replace("<|im_end|>", "")
        response = response.lstrip("\n")
        return response.strip()

    # 2. Llama/Mistral/Standard Formats
    separators = [
        "Assistant:",
        "### Response:",
        "[/INST]",
        "### Assistant:",
        "<|assistant|>",
        "ASSISTANT:",
    ]
    for sep in separators:
        if sep in full_text:
            return full_text.split(sep)[-1].strip()

    # 3. Fallback: Length Slicing (if prompt provided)
    # This is risky but necessary as a last resort
    if input_prompt and full_text.startswith(input_prompt):
        return full_text[len(input_prompt):].strip()

    # 4. Ultimate Fallback: Return as-is (stripped)
    return full_text.strip()


# ============================================================================
# CONSTANTS
# ============================================================================

SEALION_API_BASE = "https://api.sea-lion.ai/v1"
SEALION_MODELS = [
    "aisingapore/Llama-SEA-LION-v3-70B-IT",
    "aisingapore/Llama-SEA-LION-v3.5-70B-R",
    "aisingapore/Gemma-SEA-LION-v4-27B-IT",
    "aisingapore/Qwen-SEA-LION-v4-32B-IT",
    "aisingapore/SEA-Guard",
]
DEFAULT_MODEL = "aisingapore/Llama-SEA-LION-v3-70B-IT"


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class SealionConfig:
    """Configuration for SEA-LION Engine."""
    # Model selection
    model: str = DEFAULT_MODEL

    # Generation parameters
    temperature: float = 0.7
    max_tokens: int = 2048

    # Governance settings
    strict_amanah: bool = True  # If True, always apply Amanah Lock

    # System prompt for governed responses
    system_prompt: str = """You are SEA-LION, an AI assistant created by AI Singapore.
You operate under arifOS constitutional governance (v36.1Omega).

GOVERNANCE CONSTRAINTS:
- Do NOT suggest destructive commands (rm -rf, DROP TABLE, etc.)
- Do NOT output credentials, API keys, or secrets
- Acknowledge uncertainty explicitly
- Prefer reversible, auditable actions"""


# ============================================================================
# ENGINE RESULT
# ============================================================================

@dataclass
class SealionResult:
    """Result from SEA-LION engine with governance metadata."""
    # Response
    response: str
    raw_response: Optional[str] = None

    # PHOENIX SOVEREIGNTY: Amanah Lock status
    amanah_checked: bool = False
    amanah_safe: bool = True
    amanah_blocked: bool = False
    amanah_violations: List[str] = field(default_factory=list)
    amanah_warnings: List[str] = field(default_factory=list)

    # Metadata
    model: str = ""
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "response": self.response,
            "raw_response": self.raw_response,
            "amanah_checked": self.amanah_checked,
            "amanah_safe": self.amanah_safe,
            "amanah_blocked": self.amanah_blocked,
            "amanah_violations": self.amanah_violations,
            "amanah_warnings": self.amanah_warnings,
            "model": self.model,
            "error": self.error,
        }


# ============================================================================
# SEA-LION ENGINE
# ============================================================================

class SealionEngine:
    """
    SEA-LION Engine with PHOENIX SOVEREIGNTY Amanah Lock.

    This engine wraps SEA-LION API calls with Python-sovereign
    Amanah detection. If the LLM output contains destructive
    patterns, Python VETOES the response.

    Key Principle:
        "AI cannot self-legitimize."
        - LLM outputs are checked by RIGID Python patterns
        - Python veto OVERRIDES any LLM self-report
        - One Law for All Models (Claude, SEA-LION, GPT, etc.)

    Example:
        engine = SealionEngine(api_key="your-key")
        result = engine.generate("How do I delete all files?")

        if result.amanah_blocked:
            print("BLOCKED:", result.amanah_violations)
        else:
            print(result.response)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[SealionConfig] = None,
    ):
        """
        Initialize SEA-LION engine.

        Args:
            api_key: SEA-LION API key (or SEALION_API_KEY env var)
            config: SealionConfig for model and generation settings
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required. Install: pip install requests")

        self.api_key = api_key or os.environ.get("SEALION_API_KEY")
        if not self.api_key:
            raise ValueError(
                "SEA-LION API key required. "
                "Pass api_key or set SEALION_API_KEY environment variable."
            )

        self.config = config or SealionConfig()

        if self.config.model not in SEALION_MODELS:
            raise ValueError(f"Invalid model. Choose from: {SEALION_MODELS}")

        # PHOENIX SOVEREIGNTY: Store detector reference
        self._amanah_detector = _AMANAH_DETECTOR if _AMANAH_AVAILABLE else None

    def _call_api(
        self,
        messages: List[Dict[str, str]],
    ) -> str:
        """Call SEA-LION API."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        response = requests.post(
            f"{SEALION_API_BASE}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"SEA-LION API error: {response.status_code} - {response.text}"
            )

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _check_amanah(self, text: str) -> AmanahResult:
        """
        PHOENIX SOVEREIGNTY: Check text with Python-sovereign Amanah detector.

        This is the CRITICAL enforcement point. If the detector returns
        is_safe=False, the response is BLOCKED - no negotiation.
        """
        if self._amanah_detector is None:
            # No detector available - return safe (legacy behavior)
            return AmanahResult(is_safe=True)

        return self._amanah_detector.check(text)

    def generate(
        self,
        query: str,
        system_prompt: Optional[str] = None,
    ) -> SealionResult:
        """
        Generate response with PHOENIX SOVEREIGNTY enforcement.

        Pipeline:
        1. Call SEA-LION API with query
        2. Run Python-sovereign Amanah check on response
        3. If Amanah fails, BLOCK and return violation info
        4. If Amanah passes, return response

        Args:
            query: User query
            system_prompt: Optional system prompt override

        Returns:
            SealionResult with response and governance metadata
        """
        result = SealionResult(
            response="",
            model=self.config.model,
        )

        # Build messages
        messages = []
        prompt = system_prompt or self.config.system_prompt
        if prompt:
            messages.append({"role": "system", "content": prompt})
        messages.append({"role": "user", "content": query})

        # Call API
        try:
            raw_response = self._call_api(messages)
            result.raw_response = raw_response
        except Exception as e:
            result.error = str(e)
            result.response = f"[ERROR] API call failed: {e}"
            return result

        # PHOENIX SOVEREIGNTY: Python-sovereign Amanah check
        if self.config.strict_amanah:
            amanah_result = self._check_amanah(raw_response)

            result.amanah_checked = True
            result.amanah_safe = amanah_result.is_safe
            result.amanah_violations = amanah_result.violations
            result.amanah_warnings = amanah_result.warnings

            if not amanah_result.is_safe:
                # BLOCKED by Python governance
                result.amanah_blocked = True
                result.response = (
                    "[VOID] Response blocked by Python-sovereign governance.\n\n"
                    "[PHOENIX SOVEREIGNTY]\n"
                    "The LLM output contained unsafe patterns:\n"
                )
                for violation in amanah_result.violations:
                    result.response += f"  - {violation}\n"
                result.response += "\nPlease rephrase your request."
                return result

        # Amanah passed - return response
        result.response = raw_response
        return result

    def generate_with_context(
        self,
        query: str,
        context: Dict[str, Any],
        system_prompt: Optional[str] = None,
    ) -> SealionResult:
        """
        Generate response with additional context.

        Context is appended to the query for grounding.
        """
        context_str = ""
        if context:
            context_str = "\n\nContext:\n"
            for key, value in context.items():
                context_str += f"  {key}: {value}\n"

        enriched_query = query + context_str
        return self.generate(enriched_query, system_prompt)


# ============================================================================
# MOCK ENGINE (for testing without API)
# ============================================================================

class MockSealionEngine:
    """
    Mock SEA-LION engine for testing PHOENIX SOVEREIGNTY.

    Returns configurable responses for testing the Amanah Lock.
    """

    def __init__(
        self,
        config: Optional[SealionConfig] = None,
        mock_response: Optional[str] = None,
    ):
        self.config = config or SealionConfig()
        self.mock_response = mock_response or "This is a mock SEA-LION response."

        # PHOENIX SOVEREIGNTY: Store detector reference
        self._amanah_detector = _AMANAH_DETECTOR if _AMANAH_AVAILABLE else None

    def _check_amanah(self, text: str) -> AmanahResult:
        """PHOENIX SOVEREIGNTY: Check text with Python-sovereign Amanah detector."""
        if self._amanah_detector is None:
            return AmanahResult(is_safe=True)
        return self._amanah_detector.check(text)

    def set_response(self, response: str) -> None:
        """Set the mock response (for testing)."""
        self.mock_response = response

    def generate(
        self,
        query: str,
        system_prompt: Optional[str] = None,
    ) -> SealionResult:
        """Generate mock response with PHOENIX SOVEREIGNTY enforcement."""
        result = SealionResult(
            response="",
            model="mock-sealion",
            raw_response=self.mock_response,
        )

        # PHOENIX SOVEREIGNTY: Python-sovereign Amanah check
        if self.config.strict_amanah:
            amanah_result = self._check_amanah(self.mock_response)

            result.amanah_checked = True
            result.amanah_safe = amanah_result.is_safe
            result.amanah_violations = amanah_result.violations
            result.amanah_warnings = amanah_result.warnings

            if not amanah_result.is_safe:
                # BLOCKED by Python governance
                result.amanah_blocked = True
                result.response = (
                    "[VOID] Response blocked by Python-sovereign governance.\n\n"
                    "[PHOENIX SOVEREIGNTY]\n"
                    "The LLM output contained unsafe patterns:\n"
                )
                for violation in amanah_result.violations:
                    result.response += f"  - {violation}\n"
                result.response += "\nPlease rephrase your request."
                return result

        # Amanah passed
        result.response = self.mock_response
        return result


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "SealionConfig",
    "SealionResult",
    "SealionEngine",
    "MockSealionEngine",
    "SEALION_MODELS",
    "SEALION_API_BASE",
    # v36.2 PHOENIX: Tokenizer Hygiene
    "extract_response_robust",
]
