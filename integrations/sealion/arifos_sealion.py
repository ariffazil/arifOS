"""
arifos_sealion.py - Constitutional AI Wrapper for SEA-LION

Wraps SEA-LION API with arifOS v34Omega governance:
- Full 8-floor constitutional enforcement
- 000->999 metabolic pipeline
- APEX PRIME judiciary (SEAL/PARTIAL/VOID/SABAR)
- Hash-chained Cooling Ledger audit trail

SEA-LION + arifOS = Constitutional AI for Southeast Asia

Usage:
    from arifos_sealion import GovernedSEALION

    client = GovernedSEALION(api_key="your-key")
    result = client.chat("What is AI governance?")
    print(result)

Author: arifOS Project
License: Apache 2.0
Version: 34Omega
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

# Attempt to import requests
try:
    import requests
except ImportError:
    requests = None  # Will raise clear error on use

# Attempt to import arifos_core (if running from repo)
try:
    import sys
    # Add parent paths for repo usage
    _repo_root = Path(__file__).parent.parent.parent
    if _repo_root not in sys.path:
        sys.path.insert(0, str(_repo_root))

    from arifos_core import Metrics, APEXPrime, apex_review, check_floors
    from arifos_core.memory.cooling_ledger import log_cooling_entry, append_entry
    ARIFOS_CORE_AVAILABLE = True
except ImportError:
    ARIFOS_CORE_AVAILABLE = False


# ============================================================================
# CONSTANTS
# ============================================================================

SEALION_API_BASE = "https://api.sea-lion.ai/v1"
SEALION_MODELS = [
    "gemma-3-27b-it",
    "llama-3-70b-it",
    "qwen-32b-it",
]
DEFAULT_MODEL = "llama-3-70b-it"

# Constitutional thresholds (v34Omega)
THRESHOLDS = {
    "truth": 0.99,
    "delta_s": 0.0,
    "peace_squared": 1.0,
    "kappa_r": 0.95,
    "omega_0_min": 0.03,
    "omega_0_max": 0.05,
    "tri_witness": 0.95,
    "psi": 1.0,
}

# High-stakes keywords for auto-detection
HIGH_STAKES_KEYWORDS = [
    "invest", "investment", "stock", "crypto", "bitcoin",
    "medical", "health", "diagnosis", "treatment", "medication",
    "legal", "law", "lawsuit", "contract", "liability",
    "suicide", "self-harm", "emergency", "crisis",
    "weapon", "explosive", "dangerous",
]

# Verdict type
Verdict = Literal["SEAL", "PARTIAL", "VOID", "SABAR"]


# ============================================================================
# METRICS (Standalone if arifos_core not available)
# ============================================================================

if not ARIFOS_CORE_AVAILABLE:
    @dataclass
    class Metrics:
        """Constitutional metrics for arifOS floors."""
        truth: float
        delta_s: float
        peace_squared: float
        kappa_r: float
        omega_0: float
        amanah: bool
        tri_witness: float
        rasa: bool = True
        psi: Optional[float] = None

        def __post_init__(self):
            if self.psi is None:
                self.psi = self.compute_psi()

        def compute_psi(self, tri_witness_required: bool = True) -> float:
            """Compute vitality (Psi) as minimum floor ratio."""
            omega_ok = THRESHOLDS["omega_0_min"] <= self.omega_0 <= THRESHOLDS["omega_0_max"]
            ratios = [
                self.truth / THRESHOLDS["truth"],
                1.0 + min(self.delta_s, 0.0) if self.delta_s < 0 else 1.0 + self.delta_s,
                self.peace_squared / THRESHOLDS["peace_squared"],
                self.kappa_r / THRESHOLDS["kappa_r"],
                1.0 if omega_ok else 0.0,
                1.0 if self.amanah else 0.0,
                1.0 if self.rasa else 0.0,
            ]
            if tri_witness_required:
                ratios.append(self.tri_witness / THRESHOLDS["tri_witness"])
            return min(ratios)

        def to_dict(self) -> Dict[str, Any]:
            return {
                "truth": self.truth,
                "delta_s": self.delta_s,
                "peace_squared": self.peace_squared,
                "kappa_r": self.kappa_r,
                "omega_0": self.omega_0,
                "amanah": self.amanah,
                "tri_witness": self.tri_witness,
                "rasa": self.rasa,
                "psi": self.psi,
            }

    def apex_review(
        metrics: Metrics,
        high_stakes: bool = False,
        tri_witness_threshold: float = 0.95,
    ) -> Verdict:
        """APEX PRIME judgment - returns SEAL/PARTIAL/VOID."""
        # Hard floors
        truth_ok = metrics.truth >= THRESHOLDS["truth"]
        delta_s_ok = metrics.delta_s >= THRESHOLDS["delta_s"]
        omega_0_ok = THRESHOLDS["omega_0_min"] <= metrics.omega_0 <= THRESHOLDS["omega_0_max"]
        amanah_ok = bool(metrics.amanah)
        rasa_ok = bool(metrics.rasa)
        psi_ok = metrics.psi >= THRESHOLDS["psi"] if metrics.psi else False

        hard_ok = all([truth_ok, delta_s_ok, omega_0_ok, amanah_ok, rasa_ok, psi_ok])

        # Soft floors
        peace_ok = metrics.peace_squared >= THRESHOLDS["peace_squared"]
        kappa_ok = metrics.kappa_r >= THRESHOLDS["kappa_r"]
        tri_ok = metrics.tri_witness >= tri_witness_threshold if high_stakes else True

        soft_ok = all([peace_ok, kappa_ok, tri_ok])

        if not hard_ok:
            return "VOID"
        if not soft_ok:
            return "PARTIAL"
        return "SEAL"


# ============================================================================
# FLOOR COMPUTATION (Heuristics for text analysis)
# ============================================================================

class FloorComputer:
    """Computes constitutional floor metrics from text."""

    # Uncertainty markers for truth/humility detection
    UNCERTAINTY_PHRASES = [
        "i think", "i believe", "perhaps", "maybe", "possibly",
        "it seems", "it appears", "might be", "could be",
        "i'm not sure", "i'm uncertain", "based on my understanding",
        "to my knowledge", "as far as i know", "approximately",
        "roughly", "generally", "typically", "usually",
    ]

    HEDGING_PHRASES = [
        "however", "but", "although", "on the other hand",
        "that said", "it depends", "there are exceptions",
        "some argue", "others believe", "perspectives vary",
    ]

    ESCALATION_WORDS = [
        "absolutely", "definitely", "certainly", "always", "never",
        "must", "should", "wrong", "stupid", "idiotic",
        "terrible", "horrible", "awful", "worst",
    ]

    DE_ESCALATION_WORDS = [
        "understand", "appreciate", "respect", "consider",
        "perspective", "nuanced", "complex", "thoughtful",
        "careful", "measured", "balanced",
    ]

    EMPATHY_WORDS = [
        "feel", "understand", "empathize", "care", "support",
        "help", "concern", "compassion", "kindness", "gentle",
        "patient", "listening", "hearing",
    ]

    MANIPULATION_PATTERNS = [
        r"you must", r"you have to", r"you should definitely",
        r"trust me", r"believe me", r"i guarantee",
        r"everyone knows", r"nobody thinks", r"only fools",
        r"act now", r"limited time", r"don't miss",
    ]

    @classmethod
    def compute_all(
        cls,
        query: str,
        response: str,
        context: Optional[Dict] = None,
    ) -> Metrics:
        """Compute all 8 constitutional floors."""
        context = context or {}
        response_lower = response.lower()
        query_lower = query.lower()

        truth = cls._compute_truth(response, response_lower)
        delta_s = cls._compute_delta_s(query, response)
        peace_squared = cls._compute_peace_squared(response_lower)
        kappa_r = cls._compute_kappa_r(query_lower, response_lower)
        omega_0 = cls._compute_omega_0(response_lower)
        amanah = cls._compute_amanah(response_lower)
        rasa = cls._compute_rasa(query, response)
        tri_witness = cls._compute_tri_witness(response, context)

        return Metrics(
            truth=truth,
            delta_s=delta_s,
            peace_squared=peace_squared,
            kappa_r=kappa_r,
            omega_0=omega_0,
            amanah=amanah,
            tri_witness=tri_witness,
            rasa=rasa,
        )

    @classmethod
    def _compute_truth(cls, response: str, response_lower: str) -> float:
        """
        Truth floor: No confident guessing. Uncertain? Say so.

        Heuristics:
        - Check for uncertainty markers (good)
        - Penalize absolute statements without evidence
        - Reward hedging and nuance
        """
        score = 1.0

        # Count uncertainty acknowledgments (positive)
        uncertainty_count = sum(
            1 for phrase in cls.UNCERTAINTY_PHRASES
            if phrase in response_lower
        )

        # Count hedging (positive for truthfulness)
        hedging_count = sum(
            1 for phrase in cls.HEDGING_PHRASES
            if phrase in response_lower
        )

        # Absolute statements without hedging (negative)
        absolutes = len(re.findall(r"\b(always|never|definitely|certainly|absolutely)\b", response_lower))

        # Check for "I don't know" type admissions (very positive)
        admits_uncertainty = any(phrase in response_lower for phrase in [
            "i don't know", "i'm not sure", "i cannot determine",
            "i lack information", "uncertain", "unclear",
        ])

        # Scoring
        if admits_uncertainty:
            score = min(1.0, score + 0.02)  # Boost for honesty

        score += uncertainty_count * 0.005
        score += hedging_count * 0.003
        score -= absolutes * 0.02

        return max(0.0, min(1.0, score))

    @classmethod
    def _compute_delta_s(cls, query: str, response: str) -> float:
        """
        Clarity floor: Does response clarify, not confuse?

        Heuristics:
        - Structure (lists, headers) adds clarity
        - Reasonable length ratio
        - Technical jargon without explanation reduces clarity
        """
        score = 0.0

        # Structure markers (add clarity)
        has_list = bool(re.search(r"^[\s]*[-*\d]+[.)]\s", response, re.MULTILINE))
        has_code = "```" in response
        has_headers = bool(re.search(r"^#{1,3}\s", response, re.MULTILINE))

        if has_list:
            score += 0.05
        if has_code and "code" in query.lower():
            score += 0.10
        if has_headers and len(response) > 500:
            score += 0.05

        # Length ratio (too short = unclear, too long = confusing)
        query_len = len(query.split())
        response_len = len(response.split())

        if query_len > 0:
            ratio = response_len / query_len
            if 2.0 <= ratio <= 20.0:
                score += 0.05
            elif ratio > 50.0:
                score -= 0.10  # Overly verbose

        # Penalize very short responses to complex queries
        if query_len > 20 and response_len < 10:
            score -= 0.15

        return score

    @classmethod
    def _compute_peace_squared(cls, response_lower: str) -> float:
        """
        Stability floor: De-escalate, never pour fuel on fire.

        Heuristics:
        - Escalation words reduce score
        - De-escalation words increase score
        """
        score = 1.0

        escalation_count = sum(
            1 for word in cls.ESCALATION_WORDS
            if word in response_lower
        )

        de_escalation_count = sum(
            1 for word in cls.DE_ESCALATION_WORDS
            if word in response_lower
        )

        score -= escalation_count * 0.05
        score += de_escalation_count * 0.02

        return max(0.5, min(1.5, score))

    @classmethod
    def _compute_kappa_r(cls, query_lower: str, response_lower: str) -> float:
        """
        Empathy floor: Protect the most vulnerable interpretation.

        Heuristics:
        - Empathy words increase score
        - Harsh language decreases score
        - Context-awareness for sensitive topics
        """
        score = 0.97  # Start slightly above threshold

        empathy_count = sum(
            1 for word in cls.EMPATHY_WORDS
            if word in response_lower
        )

        # Sensitive topic detection
        sensitive_topics = ["suicide", "depression", "anxiety", "trauma", "abuse", "harm"]
        is_sensitive = any(topic in query_lower for topic in sensitive_topics)

        if is_sensitive:
            # Higher standards for sensitive topics
            has_care_language = any(word in response_lower for word in [
                "support", "help", "care", "understand", "professional",
                "crisis", "hotline", "therapist", "counselor",
            ])
            if has_care_language:
                score = min(1.0, score + 0.03)
            else:
                score -= 0.05

        score += empathy_count * 0.01
        return max(0.0, min(1.0, score))

    @classmethod
    def _compute_omega_0(cls, response_lower: str) -> float:
        """
        Humility floor: 3-5% explicit uncertainty. No god-mode.

        Returns value in [0.0, 1.0] - should be in [0.03, 0.05] band.
        """
        uncertainty_count = sum(
            1 for phrase in cls.UNCERTAINTY_PHRASES
            if phrase in response_lower
        )

        # Map count to omega_0 value
        # 0 phrases -> 0.01 (too confident)
        # 1-2 phrases -> 0.04 (good)
        # 3+ phrases -> 0.06+ (too uncertain)

        if uncertainty_count == 0:
            return 0.01
        elif uncertainty_count <= 2:
            return 0.04
        elif uncertainty_count <= 4:
            return 0.05
        else:
            return 0.07

    @classmethod
    def _compute_amanah(cls, response_lower: str) -> bool:
        """
        Integrity floor: No manipulation. No hidden agenda. Ever.

        Returns True if no manipulation detected.
        """
        for pattern in cls.MANIPULATION_PATTERNS:
            if re.search(pattern, response_lower):
                return False
        return True

    @classmethod
    def _compute_rasa(cls, query: str, response: str) -> bool:
        """
        RASA floor: Receive, Appreciate, Summarize, Ask.

        Checks if response shows active listening.
        """
        response_lower = response.lower()

        # Check for acknowledgment of the query
        acknowledges = any(phrase in response_lower for phrase in [
            "you asked", "your question", "you mentioned",
            "regarding your", "to answer your", "in response to",
        ])

        # Check for follow-up questions (Ask)
        has_followup = "?" in response and len(response) > 100

        # RASA is true if response engages meaningfully
        return acknowledges or has_followup or len(response) > 50

    @classmethod
    def _compute_tri_witness(cls, response: str, context: Dict) -> float:
        """
        Tri-Witness floor: Human + AI + Reality must agree.

        For API usage, we simulate with:
        - AI confidence (from response structure)
        - Reality grounding (factual markers)
        """
        score = 0.90  # Base score

        # Structured response suggests AI confidence
        has_structure = bool(re.search(r"^[\s]*[-*\d]+[.)]\s", response, re.MULTILINE))
        if has_structure:
            score += 0.03

        # Factual grounding markers
        factual_markers = ["according to", "research shows", "studies indicate",
                          "data suggests", "evidence shows", "historically"]
        has_grounding = any(marker in response.lower() for marker in factual_markers)
        if has_grounding:
            score += 0.05

        # Context-provided witness components
        if context.get("human_verified"):
            score += 0.05
        if context.get("external_sources"):
            score += 0.03

        return min(1.0, score)


# ============================================================================
# COOLING LEDGER (Standalone if arifos_core not available)
# ============================================================================

class StandaloneCoolingLedger:
    """Hash-chained append-only audit log."""

    def __init__(self, path: Union[str, Path] = "cooling_ledger.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _compute_hash(self, entry: Dict) -> str:
        """SHA3-256 hash of entry."""
        excluded = {"hash", "kms_signature", "kms_key_id"}
        data = {k: v for k, v in entry.items() if k not in excluded}
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha3_256(canonical.encode()).hexdigest()

    def _get_prev_hash(self) -> Optional[str]:
        """Get hash of last entry."""
        if not self.path.exists() or self.path.stat().st_size == 0:
            return None
        with self.path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                last = lines[-1].strip()
                if last:
                    try:
                        return json.loads(last).get("hash")
                    except json.JSONDecodeError:
                        pass
        return None

    def append(
        self,
        query: str,
        response: str,
        metrics: Metrics,
        verdict: str,
        floor_failures: List[str],
        model: str,
        stakes: str = "normal",
        job_id: Optional[str] = None,
    ) -> Dict:
        """Append entry with hash chain."""
        entry = {
            "ledger_version": "v34Omega",
            "timestamp": time.time(),
            "job_id": job_id or str(uuid.uuid4()),
            "model": model,
            "stakes": stakes,
            "query": query[:500],  # Truncate for storage
            "response_preview": response[:500],
            "metrics": metrics.to_dict(),
            "verdict": verdict,
            "floor_failures": floor_failures,
            "prev_hash": self._get_prev_hash(),
        }
        entry["hash"] = self._compute_hash(entry)

        line = json.dumps(entry, ensure_ascii=False)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

        return entry


# ============================================================================
# GOVERNED SEA-LION CLIENT
# ============================================================================

class GovernedSEALION:
    """
    SEA-LION API client with arifOS constitutional governance.

    Wraps any SEA-LION model (gemma-3-27b-it, llama-3-70b-it, qwen-32b-it)
    with full 8-floor constitutional enforcement.

    Example:
        client = GovernedSEALION(api_key="your-key")
        result = client.chat("What is AI governance?")
        print(result)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        ledger_path: Union[str, Path] = "cooling_ledger.jsonl",
        high_stakes_mode: bool = False,
        auto_detect_stakes: bool = True,
    ):
        """
        Initialize governed SEA-LION client.

        Args:
            api_key: SEA-LION API key (or SEALION_API_KEY env var)
            model: Model ID (gemma-3-27b-it, llama-3-70b-it, qwen-32b-it)
            ledger_path: Path to Cooling Ledger JSONL file
            high_stakes_mode: Force high-stakes mode for all queries
            auto_detect_stakes: Auto-detect high-stakes keywords
        """
        if requests is None:
            raise ImportError("requests library required. Install: pip install requests")

        self.api_key = api_key or os.environ.get("SEALION_API_KEY")
        if not self.api_key:
            raise ValueError(
                "SEA-LION API key required. "
                "Pass api_key or set SEALION_API_KEY environment variable."
            )

        if model not in SEALION_MODELS:
            raise ValueError(f"Invalid model. Choose from: {SEALION_MODELS}")

        self.model = model
        self.high_stakes_mode = high_stakes_mode
        self.auto_detect_stakes = auto_detect_stakes
        self.ledger = StandaloneCoolingLedger(ledger_path)

        # Use arifos_core APEXPrime if available
        if ARIFOS_CORE_AVAILABLE:
            self.apex = APEXPrime(high_stakes=high_stakes_mode)
        else:
            self.apex = None

    def _is_high_stakes(self, query: str) -> bool:
        """Detect high-stakes query from keywords."""
        if self.high_stakes_mode:
            return True
        if not self.auto_detect_stakes:
            return False

        query_lower = query.lower()
        return any(keyword in query_lower for keyword in HIGH_STAKES_KEYWORDS)

    def _call_api(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Call SEA-LION API."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
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

    def _generate_sabar_response(
        self,
        floor_failures: List[str],
        query: str,
    ) -> str:
        """Generate SABAR protocol response for VOID/failed queries."""
        msg = "[VOID] Cannot safely complete this request.\n\n"
        msg += "[SABAR PROTOCOL]\n"
        msg += "STOP: The following constitutional floors failed:\n"
        for failure in floor_failures:
            msg += f"  - {failure}\n"
        msg += "\nACKNOWLEDGE: I cannot proceed with this operation as stated.\n\n"
        msg += "BREATHE: Let me suggest alternatives:\n"
        msg += "  - Could you rephrase with more context?\n"
        msg += "  - Would you like me to break this into smaller questions?\n"
        msg += "  - Should we verify assumptions first?\n\n"
        msg += "ADJUST: Please provide additional information.\n\n"
        msg += "RESUME: Once clarified, I can help safely."
        return msg

    def _identify_failures(self, metrics: Metrics, high_stakes: bool) -> List[str]:
        """Identify which floors failed."""
        failures = []

        if metrics.truth < THRESHOLDS["truth"]:
            failures.append(f"Truth={metrics.truth:.3f} < {THRESHOLDS['truth']}")
        if metrics.delta_s < THRESHOLDS["delta_s"]:
            failures.append(f"DeltaS={metrics.delta_s:.3f} < {THRESHOLDS['delta_s']}")
        if metrics.peace_squared < THRESHOLDS["peace_squared"]:
            failures.append(f"Peace2={metrics.peace_squared:.3f} < {THRESHOLDS['peace_squared']}")
        if metrics.kappa_r < THRESHOLDS["kappa_r"]:
            failures.append(f"KappaR={metrics.kappa_r:.3f} < {THRESHOLDS['kappa_r']}")
        if not (THRESHOLDS["omega_0_min"] <= metrics.omega_0 <= THRESHOLDS["omega_0_max"]):
            failures.append(f"Omega0={metrics.omega_0:.3f} outside [{THRESHOLDS['omega_0_min']}, {THRESHOLDS['omega_0_max']}]")
        if not metrics.amanah:
            failures.append("Amanah=False (manipulation detected)")
        if not metrics.rasa:
            failures.append("RASA=False (not listening)")
        if high_stakes and metrics.tri_witness < THRESHOLDS["tri_witness"]:
            failures.append(f"TriWitness={metrics.tri_witness:.3f} < {THRESHOLDS['tri_witness']}")
        if metrics.psi and metrics.psi < THRESHOLDS["psi"]:
            failures.append(f"Psi={metrics.psi:.3f} < {THRESHOLDS['psi']}")

        return failures

    def chat(
        self,
        query: str,
        system_prompt: Optional[str] = None,
        context: Optional[Dict] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        return_metadata: bool = False,
    ) -> Union[str, Dict]:
        """
        Send governed chat request to SEA-LION.

        Full pipeline:
        1. 000-222: Receive and reflect on query
        2. 333-444: Call SEA-LION API
        3. 555-666: Compute constitutional metrics
        4. 777-888: APEX PRIME judgment
        5. 999: Seal or SABAR

        Args:
            query: User query
            system_prompt: Optional system prompt
            context: Additional context dict
            temperature: Generation temperature
            max_tokens: Max tokens to generate
            return_metadata: Return full metadata dict instead of just response

        Returns:
            Response string, or dict with verdict/metrics if return_metadata=True
        """
        context = context or {}
        high_stakes = self._is_high_stakes(query)

        # ====== STAGE 000-222: RECEIVE & REFLECT ======
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": query})

        # ====== STAGE 333-444: CALL SEA-LION ======
        try:
            raw_response = self._call_api(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:
            error_metrics = Metrics(
                truth=0.0, delta_s=-1.0, peace_squared=0.5,
                kappa_r=0.5, omega_0=0.01, amanah=True,
                tri_witness=0.0, rasa=False,
            )
            self.ledger.append(
                query=query,
                response=f"API Error: {e}",
                metrics=error_metrics,
                verdict="VOID",
                floor_failures=["API_ERROR"],
                model=self.model,
                stakes="high" if high_stakes else "normal",
            )
            if return_metadata:
                return {
                    "verdict": "VOID",
                    "response": f"[VOID] API Error: {e}",
                    "metrics": error_metrics.to_dict(),
                    "floor_failures": ["API_ERROR"],
                    "model": self.model,
                }
            return f"[VOID] API Error: {e}"

        # ====== STAGE 555-666: COMPUTE METRICS ======
        metrics = FloorComputer.compute_all(query, raw_response, context)

        # ====== STAGE 777-888: APEX JUDGMENT ======
        if self.apex:
            # Use arifos_core APEXPrime
            verdict = self.apex.judge(metrics)
        else:
            # Use standalone apex_review
            verdict = apex_review(metrics, high_stakes=high_stakes)

        floor_failures = self._identify_failures(metrics, high_stakes)

        # ====== STAGE 999: SEAL OR SABAR ======
        stakes_str = "high" if high_stakes else "normal"

        self.ledger.append(
            query=query,
            response=raw_response,
            metrics=metrics,
            verdict=verdict,
            floor_failures=floor_failures,
            model=self.model,
            stakes=stakes_str,
        )

        if verdict == "SEAL":
            final_response = raw_response
        elif verdict == "PARTIAL":
            warning = "\n\n---\n[PARTIAL] Constitutional concerns:\n"
            warning += "\n".join(f"  - {f}" for f in floor_failures)
            final_response = raw_response + warning
        else:  # VOID or SABAR
            final_response = self._generate_sabar_response(floor_failures, query)

        if return_metadata:
            return {
                "verdict": verdict,
                "response": final_response,
                "raw_response": raw_response if verdict != "VOID" else None,
                "metrics": metrics.to_dict(),
                "floor_failures": floor_failures,
                "model": self.model,
                "high_stakes": high_stakes,
            }

        return final_response

    def chat_stream(
        self,
        query: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ):
        """
        Streaming chat (governance applied post-stream).

        Note: Constitutional checks happen after full response.
        For real-time governance, use non-streaming chat().
        """
        # For now, delegate to non-streaming
        # Full streaming with real-time governance is a future enhancement
        return self.chat(query, system_prompt, **kwargs)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_client(
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    **kwargs,
) -> GovernedSEALION:
    """Create governed SEA-LION client (convenience function)."""
    return GovernedSEALION(api_key=api_key, model=model, **kwargs)


def quick_chat(query: str, api_key: Optional[str] = None) -> str:
    """Quick one-off governed chat."""
    client = create_client(api_key=api_key)
    return client.chat(query)


# ============================================================================
# CLI DEMO
# ============================================================================

def main():
    """Demo CLI."""
    import sys

    print("=" * 60)
    print("arifOS + SEA-LION Constitutional AI Demo")
    print("=" * 60)
    print()

    api_key = os.environ.get("SEALION_API_KEY")
    if not api_key:
        print("Error: Set SEALION_API_KEY environment variable")
        print("Get your key at: https://playground.sea-lion.ai")
        sys.exit(1)

    client = GovernedSEALION(api_key=api_key)

    test_queries = [
        "What is AI governance and why does it matter?",
        "Explain machine learning in simple terms.",
        "Should I invest all my savings in cryptocurrency?",  # High-stakes
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 40)

        result = client.chat(query, return_metadata=True)

        print(f"Verdict: {result['verdict']}")
        print(f"Psi: {result['metrics']['psi']:.3f}")
        print(f"Response: {result['response'][:200]}...")
        print()


if __name__ == "__main__":
    main()
