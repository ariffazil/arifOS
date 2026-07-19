"""
shared/atlas.py — ATLAS-333: Governance Placement Vector

The 3-Function Constitutional Router:

    Λ(text) → lane                    # Lambda: Text → Lane classification
    Θ(lane) → (τ, κ, ρ)              # Theta: Lane → Demand tensor
    Φ(text) → GPV(lane, τ, κ, ρ)    # Phi: Complete mapping (Φ = Θ ∘ Λ)

ATLAS (Architectural Truth Layout and Semantic mapping) provides a coordinate
system for governance decisions. Every query is mapped to a Governance Placement
Vector (GPV) that determines which kernels activate and with what intensity.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import re
import unicodedata
from enum import Enum
from re import Pattern

from .types import GPV, QueryType


class Lane(str, Enum):
    """
    Constitutional processing lanes.
    """

    SOCIAL = "SOCIAL"
    CARE = "CARE"
    FACTUAL = "FACTUAL"
    CRISIS = "CRISIS"
    UNKNOWN = "UNKNOWN"


# Setup ATLAS Audit Logger
logger = logging.getLogger("arifos.atlas")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[ATLAS_AUDIT] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# ═════════════════════════════════════════════════════════════════════════════
# ATTLAS UTILITIES
# ═════════════════════════════════════════════════════════════════════════════


def gpv_f2_threshold(gpv: GPV) -> float:
    """Adaptive F2 threshold."""
    thresholds = {
        QueryType.PROCEDURAL: 0.70,
        QueryType.OPINION: 0.60,
        QueryType.COMPARATIVE: 0.85,
        QueryType.FACTUAL: 0.99,
        QueryType.CONVERSATIONAL: 0.50,
        QueryType.TEST: 0.50,
        QueryType.EXPLORATORY: 0.80,
    }
    return thresholds.get(gpv.query_type, 0.95)


def gpv_f4_skip(gpv: GPV) -> bool:
    """Skip F4 for non-factual queries."""
    return (
        gpv.query_type
        in (
            QueryType.PROCEDURAL,
            QueryType.OPINION,
            QueryType.CONVERSATIONAL,
            QueryType.TEST,
        )
        or gpv.lane == Lane.SOCIAL
    )


def gpv_can_use_fast_path(gpv: GPV) -> bool:
    """Can this query use the fast/light pipeline?"""
    if gpv.rho >= 0.2 or gpv.tau >= 0.8:
        return False
    if gpv.lane == Lane.SOCIAL:
        return True
    return gpv.query_type in (
        QueryType.PROCEDURAL,
        QueryType.OPINION,
        QueryType.CONVERSATIONAL,
        QueryType.TEST,
    )


# ═════════════════════════════════════════════════════════════════════════════
# ATLAS-333 ENGINE
# ═════════════════════════════════════════════════════════════════════════════


class ATLAS:
    """
    ATLAS-333 Governance Placement Vector mapper.

    Pre-compiled regex patterns for performance.
    Stateless — can be instantiated once and reused.
    """

    def __init__(self, min_risk_amount: float = 100.0):
        """
        Initialize with pre-compiled regex patterns.

        Args:
            min_risk_amount: Minimum dollar amount ($) to trigger risk escalation.
        """
        self.min_risk_amount = min_risk_amount

        # ═════════════════════════════════════════════════════════════════════
        # CRISIS PATTERNS — Direct harm signals (highest priority)
        # ═════════════════════════════════════════════════════════════════════
        self._crisis_patterns: list[Pattern] = [
            # Self-harm (with negative lookbehind for idioms)
            re.compile(
                r"(?<!kill )\b(kill myself|murder|suicide|self-harm|cut myself|end it all)\b"
            ),
            re.compile(r"\b(hurt|abuse|violence|assault|attack)\s+(me|myself|someone|people)\b"),
            # Weapons/dangerous items
            re.compile(r"\b(molotov|bomb|explosive)\b"),
            re.compile(r"\b(gun|knife|weapon)\s+(to|for|against)\b"),
            # Self-harm indicators
            re.compile(r"\b(want to die|end my life)\b"),
            # Abuse/violence
            re.compile(r"\b(rape|torture|kidnap|hostage)\b"),
        ]

        # Idiomatic expressions to filter (false positive prevention)
        self._idiom_patterns: list[Pattern] = [
            re.compile(r"\bkill time\b"),
            re.compile(r"\bkill (the|my) (lights?|mood|vibe|buzz)\b"),
            re.compile(r"\bkill two birds\b"),
            re.compile(r"\bkill it\b"),
            re.compile(r"\bdressed to kill\b"),
        ]

        # ═════════════════════════════════════════════════════════════════════
        # FACTUAL PATTERNS — Technical, verifiable claims
        # ═════════════════════════════════════════════════════════════════════
        self._factual_patterns: list[Pattern] = [
            # Code/programming
            re.compile(r"\b(code|function|algorithm|class|method|variable|import|def |return )\b"),
            re.compile(r"\b(python|javascript|java|rust|c\+\+|typescript|golang)\b"),
            # Math/science
            re.compile(r"\b(theorem|proof|equation|formula|calculate|compute|solve)\b"),
            re.compile(r"\b(derivative|integral|matrix|vector|probability|statistics|entropy)\b"),
            # Technical claims
            re.compile(r"\b(according to|research shows|studies indicate|data suggests)\b"),
            re.compile(r"\b(the capital of|the population of|was born in|invented by)\b"),
            # Questions requesting facts
            re.compile(r"\b(what is|who is|when did|where is|how many|why does)\b.*\?"),
            # Numbers with units
            re.compile(r"\b\d+\s*(kg|km|m|cm|mm|lb|ft|mi|degrees|percent)\b"),
        ]

        # ═════════════════════════════════════════════════════════════════════
        # SOCIAL PATTERNS — Phatic communication
        # ═════════════════════════════════════════════════════════════════════
        self._social_patterns: list[Pattern] = [
            # Greetings
            re.compile(r"\b(hello|hi|hey|greetings|good morning|good afternoon|good evening)\b"),
            # Thanks/gratitude/gestures
            re.compile(r"\b(thanks|thank you|appreciate it|grateful|tip|gratuity)\b"),
            # Small talk
            re.compile(r"\b(how are you|what's up|how's it going)\b"),
            # Farewells
            re.compile(r"\b(bye|goodbye|see you|talk later)\b"),
        ]

        # ═════════════════════════════════════════════════════════════════════
        # CARE PATTERNS — Explanations, support
        # ═════════════════════════════════════════════════════════════════════
        self._care_patterns: list[Pattern] = [
            # Help requests
            re.compile(r"\b(help|assist|support|guide me)\b"),
            # Explanations
            re.compile(r"\b(explain|how do I|how can I|what should I|advice)\b"),
            # Emotional context
            re.compile(r"\b(worried|concerned|confused|stressed|anxious)\b"),
            # Learning
            re.compile(r"\b(learn|understand|teach me|show me)\b"),
        ]

        # ═════════════════════════════════════════════════════════════════════
        # HIGH-VULNERABILITY CONTEXTS (for risk assessment)
        # ═════════════════════════════════════════════════════════════════════
        self._high_vuln_contexts: list[Pattern] = [
            re.compile(r"\b(medical|health|patient|hospital|doctor|diagnosis)\b"),
            re.compile(r"\b(child|minor|student|school|education)\b"),
            re.compile(r"\b(financial|money|payment|bank|investment|debt)\b"),
            re.compile(r"\b(legal|court|law|compliance|regulation)\b"),
            re.compile(r"\b(security|password|credential|auth|authentication)\b"),
            re.compile(r"\b(CCS|CO2|injection|pressure|borehole|storage)\b"),
            re.compile(r"\b(transfer|wire|transaction|payment|wire\stransfer)\b"),
            re.compile(r"\$\d{4,10}"),  # Large dollar amounts ($1000+)
        ]

        # ═════════════════════════════════════════════════════════════════════
        # OPERATIONAL DANGER PATTERNS — P34 enforcement layer (2026-07-19)
        # ═════════════════════════════════════════════════════════════════════
        # Detects commands that carry operational blast radius regardless of lane.
        # These escalate ρ to trigger P34 (Root Outruns Kernel) activation.
        self._operational_danger_patterns: list[Pattern] = [
            # Destructive filesystem operations
            re.compile(r"\b(rm\s+-rf|rm\s+-r\s+|rmdir|sudo\s+rm)\b"),
            re.compile(r"\b(delete\s+(all|everything|permanently)|wipe|shred)\b"),
            # Database destruction
            re.compile(
                r"\b(DROP\s+(TABLE|DATABASE|SCHEMA|INDEX)|TRUNCATE|CASCADE)\b", re.IGNORECASE
            ),
            # Git force operations
            re.compile(r"\b(git\s+push\s+--force|force.push|git\s+reset\s+--hard)\b"),
            re.compile(r"\b(force\s+push|push\s+force|--force)\b"),
            # Production/system mutations
            re.compile(r"\b(deploy\s+(to\s+)?production|prod\s+deploy|production\s+deploy)\b"),
            re.compile(r"\b(systemctl\s+(restart|stop|disable|mask))\b"),
            re.compile(r"\b(restart\s+(service|server|vps|production))\b"),
            # Secret/key rotation
            re.compile(r"\b(rotate\s+(all\s+)?(api\s+)?keys?|secret\s+rotation)\b"),
            re.compile(r"\b(regenerate\s+(credentials|tokens?|keys?))\b"),
            # Self-authorization markers
            re.compile(r"\b(I\s+(approve|authorize|allow)\s+(my\s+own|myself))\b"),
            re.compile(r"\b(as\s+root|with\s+sudo|without\s+(review|approval))\b"),
            re.compile(r"\b(self.authoriz|bypass.*review|skip.*approval)\b"),
            # Infrastructure mutations
            re.compile(r"\b(firewall|iptables|ufw|DNS|Caddy\s+reload)\b"),
            re.compile(r"\b(VPS\s+(restart|stop|reboot)|reboot\s+(server|vps))\b"),
            # Volume/container destruction
            re.compile(r"\b(docker\s+(system\s+prune|volume\s+rm|rm\s+-f))\b"),
            re.compile(r"\b(volumes?\s+(delete|remove|destroy))\b"),
        ]

        # ═════════════════════════════════════════════════════════════════════
        # OPERATIONAL KEYWORDS — Lane routing boost for technical ops
        # ═════════════════════════════════════════════════════════════════════
        # Words that indicate this is an operational/technical command
        # even if it doesn't match enough factual patterns.
        self._operational_keywords: list[Pattern] = [
            re.compile(r"\b(deploy|deployment|redeploy)\b"),
            re.compile(r"\b(production|prod|staging|live|main)\b"),
            re.compile(r"\b(git|commit|push|pull|merge|rebase|branch)\b"),
            re.compile(r"\b(restart|reload|systemctl|service|daemon)\b"),
            re.compile(r"\b(database|postgres|mysql|mongodb|redis|schema)\b"),
            re.compile(r"\b(docker|container|image|compose|kubernetes|pod)\b"),
            re.compile(r"\b(rotate|rotation|key\s+gen|secret|credential)\b"),
            re.compile(r"\b(refactor|migrate|upgrade|patch|hotfix)\b"),
            re.compile(r"\b(evaluate|prospect|basin|reservoir|drill(ing)?)\b"),
            re.compile(r"\b(NPV|IRR|EMV|discount|cash\s*flow|portfolio)\b"),
            re.compile(r"\b(build|compile|install|configure|provision)\b"),
            re.compile(r"\b(backup|restore|snapshot|rollback)\b"),
        ]

    def _is_crisis(self, text: str) -> bool:
        """Check for crisis signals (highest priority)."""
        text_lower = text.lower()

        # Check for idioms first (false positive prevention)
        for pattern in self._idiom_patterns:
            if pattern.search(text_lower):
                return False

        # Check for crisis patterns
        for pattern in self._crisis_patterns:
            if pattern.search(text_lower):
                return True

        return False

    def _is_factual(self, text: str) -> bool:
        """Check for factual/technical content."""
        text_lower = text.lower()
        matches = 0
        for pattern in self._factual_patterns:
            if pattern.search(text_lower):
                matches += 1
        # Require multiple matches to reduce false positives
        return matches >= 2

    def _is_social(self, text: str) -> bool:
        """Check for social/phatic content."""
        text_lower = text.lower()
        # Social patterns are strong signals — single match sufficient
        for pattern in self._social_patterns:
            if pattern.search(text_lower):
                return True
        return False

    def _is_care(self, text: str) -> bool:
        """Check for care/support content."""
        text_lower = text.lower()
        matches = 0
        for pattern in self._care_patterns:
            if pattern.search(text_lower):
                matches += 1
        return matches >= 1

    def _is_operational(self, text: str) -> bool:
        """Check if text describes an operational/technical command."""
        text_lower = text.lower()
        matches = 0
        for pattern in self._operational_keywords:
            if pattern.search(text_lower):
                matches += 1
        return matches >= 1

    def _assess_operational_risk(self, text: str) -> float:
        """Assess operational danger level from destructive/system-mutation patterns.

        Returns risk escalation score (0.0-1.0) based on detected operational danger.
        This is SEPARATE from crisis/harm detection — it detects blast-radius risk.
        """
        text_lower = text.lower()
        op_risk = 0.0

        for pattern in self._operational_danger_patterns:
            if pattern.search(text_lower):
                op_risk += 0.25  # Each danger pattern adds 0.25

        return min(1.0, op_risk)

    def _assess_risk(self, text: str) -> float:
        """Assess risk level (ρ) from 0 to 1.

        Combines: crisis signals, high-vulnerability contexts,
        absolutist claims, AND operational danger patterns (P34 enforcement).
        """
        text_lower = text.lower()
        risk_score = 0.0

        # Crisis signals → maximum risk
        if self._is_crisis(text):
            return 1.0

        # Operational danger — P34 enforcement layer (2026-07-19)
        op_risk = self._assess_operational_risk(text)
        if op_risk > 0:
            risk_score = max(risk_score, op_risk)

        # High-vulnerability contexts
        for pattern in self._high_vuln_contexts:
            if pattern.search(text_lower):
                # Monetary risk threshold check
                money_match = re.search(r"\$(\d{1,10})", text_lower)
                if money_match:
                    amount = float(money_match.group(1))
                    if amount < self.min_risk_amount:
                        continue  # Skip risk escalation for small amounts (e.g. $10 tip)

                risk_score += 0.2

        # Absolutist claims in sensitive domains
        absolutist_words = [
            "guaranteed",
            "absolute",
            "always",
            "never",
            "perfectly",
            "zero risk",
        ]
        for word in absolutist_words:
            if word in text_lower:
                risk_score += 0.1

        return min(1.0, risk_score)


# Global singleton instance
_atlas = ATLAS()


# ═════════════════════════════════════════════════════════════════════════════
# ATLAS-333 PARADOX BRIDGE — GPV → Paradox Axis Map
# ═════════════════════════════════════════════════════════════════════════════
# Maps each GPV configuration pattern to the ATLAS-333 paradox axes it activates.
# Reference: ATLAS333_BRIDGE.md §3
# Each key describes a GPV state pattern; value is list of paradox IDs (1-35).

PARADOX_GPV_MAP: dict[str, list[int]] = {
    # τ ≥ 0.9, ρ ≤ 0.2, lane=FACTUAL — Pure truth-seeking (Zone I + V)
    "tau_high_rho_low": [1, 2, 3, 4, 21, 22, 25],
    # ρ ≥ 0.3, lane=CRISIS — Risk detected (Zone II + VI)
    "rho_crisis": [6, 7, 8, 9, 23, 26, 30],
    # κ ≥ 0.5, lane=CARE — Care/identity context (Zone III + IV)
    "kappa_care": [11, 12, 13, 15, 16, 17, 20],
    # τ ≥ 0.8, κ ≥ 0.3, lane=FACTUAL — Facts meet meaning (Zone I + IV)
    "tau_kappa_factual": [5, 18, 24],
    # ρ ≥ 0.6, any lane — High risk hard gate (Zone II + VI)
    "rho_high": [8, 9, 10, 28, 29],
    # query_type=EXPLORATORY — Open-ended exploration (Zone IV + V)
    "query_exploratory": [19, 22, 25],
    # P34/P35 Active Contours (2026-07-17) — Root privilege + Defensive testing
    # ρ ≥ 0.8 any lane — Root Outruns Kernel: sovereign/irreversible actions
    "rho_sovereign": [28, 29, 31, 34],
    # Verdict SEAL without defensive matrix — Positive ≠ Closed
    "seal_no_defense": [30, 33, 35],
}


def resolve_paradox_axes(gpv: GPV) -> list[int]:
    """Resolve ATLAS-333 paradox axes activated by a GPV configuration.

    Checks each pattern in PARADOX_GPV_MAP against the GPV state.
    Returns merged, deduplicated list of activated paradox IDs.
    """
    activated: set[int] = set()

    # 1. tau_high_rho_low: τ ≥ 0.9, ρ ≤ 0.2, lane=FACTUAL
    if gpv.tau >= 0.9 and gpv.rho <= 0.2 and gpv.lane == "FACTUAL":
        activated.update(PARADOX_GPV_MAP["tau_high_rho_low"])

    # 2. rho_crisis: ρ ≥ 0.3, lane=CRISIS
    if gpv.rho >= 0.3 and gpv.lane == "CRISIS":
        activated.update(PARADOX_GPV_MAP["rho_crisis"])

    # 3. kappa_care: κ ≥ 0.5, lane=CARE
    if gpv.kappa >= 0.5 and gpv.lane == "CARE":
        activated.update(PARADOX_GPV_MAP["kappa_care"])

    # 4. tau_kappa_factual: τ ≥ 0.8, κ ≥ 0.3, lane=FACTUAL
    if gpv.tau >= 0.8 and gpv.kappa >= 0.3 and gpv.lane == "FACTUAL":
        activated.update(PARADOX_GPV_MAP["tau_kappa_factual"])

    # 5. rho_high: ρ ≥ 0.6, any lane
    if gpv.rho >= 0.6:
        activated.update(PARADOX_GPV_MAP["rho_high"])

    # 6. query_exploratory: query_type=EXPLORATORY
    if gpv.query_type == QueryType.EXPLORATORY:
        activated.update(PARADOX_GPV_MAP["query_exploratory"])

    # 7. rho_sovereign: ρ ≥ 0.8, any lane — Root privilege + irreversibility (P34)
    if gpv.rho >= 0.8:
        activated.update(PARADOX_GPV_MAP["rho_sovereign"])

    # 8. seal_no_defense: high-risk verdict without defensive matrix (P35)
    if gpv.rho >= 0.5 and gpv.lane in ("CRISIS", "FACTUAL"):
        activated.update(PARADOX_GPV_MAP["seal_no_defense"])

    return sorted(activated)


# ═════════════════════════════════════════════════════════════════════════════
# THE 3 FUNCTIONS: Λ, Θ, Φ
# ═════════════════════════════════════════════════════════════════════════════


def classify_query_type(text: str) -> QueryType:
    """
    Classify query type for adaptive F2 governance.

    Args:
        text: Raw query text

    Returns:
        QueryType enum (PROCEDURAL, OPINION, COMPARATIVE, FACTUAL, CONVERSATIONAL, TEST, EXPLORATORY)
    """
    text_lower = text.lower()

    # CONVERSATIONAL: Greetings, small talk
    conversational_patterns = [
        r"\b(hello|hi|hey|greetings|good morning|good afternoon|good evening)\b",
        r"\b(how are you|what's up|how's it going|who are you|tell me about)\b",
        r"\b(thanks|thank you|appreciate it|help me)\b",
    ]
    for pattern in conversational_patterns:
        if re.search(pattern, text_lower):
            return QueryType.CONVERSATIONAL

    # TEST: Pipeline tests, health checks
    test_patterns = [
        r"\b(test|pipeline test|test run|check|verify|ping)\b",
    ]
    for pattern in test_patterns:
        if re.search(pattern, text_lower):
            return QueryType.TEST

    # EXPLORATORY: Brainstorming, open-ended
    exploratory_patterns = [
        r"\b(explore|brainstorm|ideas for|possibilities|what if|imagine)\b",
    ]
    for pattern in exploratory_patterns:
        if re.search(pattern, text_lower):
            return QueryType.EXPLORATORY

    # PROCEDURAL: Commands, workflows
    procedural_patterns = [
        r"\b(run|execute|start|begin|launch|process|transfer)\b",
        r"\b(how to|how do i|steps to|process for)\b",
    ]
    for pattern in procedural_patterns:
        if re.search(pattern, text_lower):
            return QueryType.PROCEDURAL

    # OPINION: Subjective requests
    opinion_patterns = [
        r"\b(what do you think|in your opinion|how do you feel)\b",
        r"\b(better|worse|best|worst|prefer|like)\b",
    ]
    for pattern in opinion_patterns:
        if re.search(pattern, text_lower):
            return QueryType.OPINION

    # COMPARATIVE: A vs B
    comparative_patterns = [
        r"\b(vs\.?|versus|compared to)\b",
        r"\b(difference|similarity|similarities)\b",
    ]
    for pattern in comparative_patterns:
        if re.search(pattern, text_lower):
            return QueryType.COMPARATIVE

    # Default to FACTUAL for everything else
    return QueryType.FACTUAL


def Λ(text: str) -> Lane:
    """
    Λ (Lambda): Text → Lane classification (SEMANTIC ONLY)

    Priority order: CRISIS > FACTUAL > CARE > SOCIAL
    Λ() classifies SEMANTIC intent — human meaning, not operational risk.
    For operational/mutation safety, use action_profile.classify_action().
    """
    # Priority order: CRISIS > FACTUAL > CARE > SOCIAL
    if _atlas._is_crisis(text):
        return Lane.CRISIS

    text_lower = text.lower()
    if "transfer" in text_lower or "wire" in text_lower:
        return Lane.FACTUAL

    if _atlas._is_factual(text):
        return Lane.FACTUAL
    elif _atlas._is_care(text):
        return Lane.CARE
    elif _atlas._is_social(text):
        return Lane.SOCIAL
    else:
        return Lane.CARE


def Θ(lane: Lane) -> tuple[float, float, float]:
    """
    Θ (Theta): Lane → Demand tensor (τ, κ, ρ)
    """
    demand_map: dict[Lane, tuple[float, float, float]] = {
        Lane.SOCIAL: (0.2, 0.1, 0.0),
        Lane.CARE: (0.4, 0.7, 0.2),
        Lane.FACTUAL: (0.9, 0.3, 0.2),
        Lane.CRISIS: (0.8, 0.9, 1.0),
    }
    return demand_map.get(lane, (0.5, 0.5, 0.5))


def Φ(text: str) -> GPV:
    """
    Φ (Phi): Complete mapping — Text → Governance Placement Vector
    """
    lane = Λ(text)
    query_type = classify_query_type(text)
    τ_base, κ_base, ρ_base = Θ(lane)
    ρ_assessed = _atlas._assess_risk(text)
    ρ = max(ρ_base, ρ_assessed)

    text_lower = text.lower()
    absolutist_terms = ["guaranteed", "absolute", "always", "never", "perfectly safe"]
    if any(term in text_lower for term in absolutist_terms):
        τ_base = min(1.0, τ_base + 0.1)

    gpv = GPV(
        lane=lane.value,
        query_type=query_type,
        tau=τ_base,
        kappa=κ_base,
        rho=ρ,
    )

    # ATLAS-333 bridge: resolve paradox axes from GPV configuration
    gpv.paradox_axes = resolve_paradox_axes(gpv)

    logger.info(
        f"Lane: {gpv.lane} | "
        f"Type: {gpv.query_type.value} | "
        f"Risk (\u03c1): {gpv.rho:.2f} | "
        f"Truth (\u03c4): {gpv.tau:.2f} | "
        f"Query: '{text[:50]}...'"
    )

    return gpv


# ═════════════════════════════════════════════════════════════════════════════
# MUTATION CLASSIFICATION — P34/P23 Hard Gate Layer (2026-07-19)
# ═════════════════════════════════════════════════════════════════════════════
# DEPRECATED: classify_mutation_class() and get_required_gate() in this file
# are replaced by core.shared.action_profile.classify_action().
# These thin wrappers exist only for backward compatibility.
# ═════════════════════════════════════════════════════════════════════════════


def classify_mutation_class(text: str) -> dict:
    """DEPRECATED. Use action_profile.classify_action() instead.

    Thin backward-compat wrapper that maps NL text to the old dict format.
    For actual enforcement, use the deterministic tool+args classifier:
        from core.shared.action_profile import classify_action
    """
    from core.shared.action_profile import classify_action as _ap_classify

    profile = _ap_classify(nl_description=text)
    return {
        "mutation_class": profile.mutation_class.value,
        "reversibility": profile.reversibility,
        "blast_radius": profile.blast_radius.value,
        "infrastructure_impact": profile.infrastructure_impact,
        "governance_impact": profile.governance_impact,
        "sovereign_required": profile.sovereign_required,
        "requires_p34_gate": profile.requires_p34,
        "requires_p23_gate": profile.requires_p23,
        "requires_judge": profile.requires_judge,
        "self_authorization_detected": profile.authority_self_issued,
        "operational_risk": 0.0,
        "gpv_rho": 0.0,
        "gpv_lane": "",
        "activated_paradoxes": [],
        "_deprecated": True,
        "_use_instead": "core.shared.action_profile.classify_action()",
    }


def get_required_gate(text: str) -> str:
    """DEPRECATED. Use action_profile.classify_action() instead.

    Returns the required governance gate level for a proposed action.
    """
    from core.shared.action_profile import classify_action as _ap_classify

    profile = _ap_classify(nl_description=text)
    return profile.gate_verdict.value


# ASCII aliases
def Lambda(text: str) -> Lane:
    return Λ(text)


def Theta(lane: Lane) -> tuple[float, float, float]:
    return Θ(lane)


def Phi(text: str) -> GPV:
    return Φ(text)


def classify(query: str) -> dict[str, any]:
    gpv = Φ(query)
    return {
        "query": query,
        "lane": gpv.lane,
        "truth_demand": gpv.tau,
        "care_demand": gpv.kappa,
        "risk_level": gpv.rho,
        "complexity": (gpv.tau + gpv.kappa + gpv.rho) / 3.0,
        "requires_grounding": gpv.tau > 0.7 or gpv.rho > 0.5,
        "requires_empathy": gpv.kappa > 0.5 or gpv.lane in ("CARE", "CRISIS"),
    }


def route(query: str) -> str:
    gpv = Φ(query)
    organs = ["INIT"]
    if gpv.lane in (Lane.FACTUAL, Lane.CARE, Lane.CRISIS):
        organs.append("AGI")
    if gpv.lane in (Lane.CARE, Lane.CRISIS) or gpv.care_demand > 0.5:
        organs.append("ASI")
    organs.append("APEX")
    if gpv.requires_grounding():
        organs.append("(grounding)")
    return " → ".join(organs)


def classify_query(query: str) -> dict[str, any]:
    return classify(query)


def route_query(query: str) -> str:
    return route(query)


def normalize_semantic_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    n = unicodedata.normalize("NFKC", text).lower()
    confusable_map = {
        "а": "a",
        "е": "e",
        "о": "o",
        "р": "p",
        "с": "c",
        "у": "y",
        "х": "x",
        "А": "a",
        "Е": "e",
        "О": "o",
        "Р": "p",
        "С": "c",
        "У": "y",
        "Х": "x",
        "τ": "t",
        "ν": "n",
        "ρ": "p",
        "ω": "w",
        "κ": "k",
        "ε": "e",
        "Ε": "e",
    }
    return "".join(confusable_map.get(c, c) for c in n)


__all__ = [
    "Lane",
    "QueryType",
    "classify_query_type",
    "GPV",
    "Λ",
    "Θ",
    "Φ",
    "Lambda",
    "Theta",
    "Phi",
    "ATLAS",
    "classify",
    "route",
    "classify_query",
    "route_query",
    "normalize_semantic_text",
    "classify_mutation_class",  # DEPRECATED — use action_profile.classify_action()
    "get_required_gate",  # DEPRECATED — use action_profile.classify_action()
]
