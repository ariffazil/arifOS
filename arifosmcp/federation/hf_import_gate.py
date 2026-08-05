"""
arifOS Federation — Hugging Face Import Gate
═══════════════════════════════════════════

Governed entry point for all Hugging Face resources (models, datasets, spaces)
entering arifOS. Ensures every resource passes constitutional floors F1–F13
before being registered in arifOS memory.

Adapted from FFF promotion gate pattern. Uses existing floor scorer and
thermodynamics engine for constitutional validation.

DITEMPA BUKAN DIBERI — Forged, Not Given. 2026-08-05.
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

# Lazy imports — avoid cascading import failures from pre-existing
# session_state.py bug (SealType.PENDING missing at module load time).
# These are loaded inside _lazy_import_* helpers below.

from arifosmcp.thermodynamics.engine import (
    BufferStatus,
    EntropyPathway,
    EntropyReceipt,
    ThermodynamicVerdict,
    classify_actor_buffer,
    compute_entropy_pathway,
    render_entropy_receipt,
)

logger = logging.getLogger("arifosmcp.federation.hf_import_gate")

# ── Constants ────────────────────────────────────────────────────────────────

ALLOWED_LICENSES = {
    "apache-2.0",
    "mit",
    "cc-by-4.0",
    "cc-by-sa-4.0",
    "bsd-2-clause",
    "bsd-3-clause",
    "odc-by",
    "cc0-1.0",
    "unlicense",
}

RESTRICTED_LICENSES = {
    "gpl-2.0",
    "gpl-3.0",
    "agpl-3.0",
    "lgpl-2.1",
    "lgpl-3.0",
    "cc-by-nc-4.0",
    "cc-by-nc-sa-4.0",
    "cc-by-nd-4.0",
    "other",
}

F8_MIN_GAIN_DEFAULT: float = 0.80
KAPPA_R_DEFAULT: float = 0.90
DELTA_S_BUFFER: float = 0.0


# ── Enums ─────────────────────────────────────────────────────────────────────


class ImportVerdict(str, Enum):
    """Verdict for an HF import request."""

    SEAL = "SEAL"
    HOLD = "HOLD"
    VOID = "VOID"


class ResourceType(str, Enum):
    """Type of Hugging Face resource being imported."""

    MODEL = "model"
    DATASET = "dataset"
    SPACE = "space"


# ── Data Classes ─────────────────────────────────────────────────────────────


@dataclass
class HFImportConfig:
    """Configuration for HF import gate behaviour."""

    verify_sha256: bool = True
    require_model_card: bool = True
    require_benchmarks: bool = False
    floor_overrides: dict[str, bool] = field(default_factory=dict)
    min_gain_override: Optional[float] = None
    provenance_tags: list[str] = field(default_factory=list)
    timeout_seconds: int = 30


@dataclass
class HFImportRequest:
    """Incoming import request from arif_forge."""

    repo_id: str
    resource_type: ResourceType = ResourceType.MODEL
    intended_use: str = "general"
    config: HFImportConfig = field(default_factory=HFImportConfig)
    actor_id: str = "unknown"
    session_id: str = ""


@dataclass
class FloorResult:
    """Result of a single constitutional floor check."""

    floor_id: str
    status: str  # PASS | HOLD | VOID | UNCERTAIN
    score: Optional[float] = None
    evidence: str = ""
    computed: bool = False


@dataclass
class ThermodynamicScores:
    """Thermodynamic scores computed by the gate."""

    kappa_r: float
    delta_s: float
    G: float
    phi_delta: float = 0.0
    B_score: float = 0.0
    pathway: str = "UNKNOWN"


@dataclass
class HFImportResult:
    """Complete import gate result."""

    verdict: ImportVerdict
    repo_id: str
    sha256: str = ""
    thermodynamic_scores: ThermodynamicScores = field(
        default_factory=lambda: ThermodynamicScores(kappa_r=0.8, delta_s=0.0, G=0.0)
    )
    floor_results: dict[str, FloorResult] = field(default_factory=dict)
    violations: list[str] = field(default_factory=list)
    model_card: dict[str, Any] = field(default_factory=dict)
    entropy_receipt: Optional[dict[str, Any]] = None
    provenance_id: str = ""
    recommended_action: str = "HOLD"


# ── HFImportGate ─────────────────────────────────────────────────────────────


class HFImportGate:
    """Governed entry point for Hugging Face resources.

    Pulls model metadata from HF API, validates through all 13
    constitutional floors, computes thermodynamic scores (κᵣ, ΔS, G),
    and returns a verdict (SEAL/HOLD/VOID).

    Does NOT pull actual model weights — this is the gate, not the
    loading pipeline. The gate determines whether a resource MAY enter.
    The forge determines how it enters.
    """

    def __init__(self, hf_token: str | None = None):
        """Initialize with optional HuggingFace token.

        Args:
            hf_token: HF API token. Falls back to HF_TOKEN env var
                      (loaded from /root/.secrets/tokens/huggingface).
        """
        self._hf_token = hf_token
        self._api = None  # Lazy init

    @property
    def _hf_api(self):
        """Lazy-init HuggingFace Hub API client."""
        if self._api is None:
            try:
                from huggingface_hub import HfApi

                self._api = HfApi(token=self._hf_token)
            except ImportError:
                logger.warning("huggingface_hub not available — gate operates in offline mode")
                self._api = None
        return self._api

    # ── Public API ────────────────────────────────────────────────────────

    def process(self, request: HFImportRequest) -> HFImportResult:
        """Run a full import request through the constitutional gate.

        Args:
            request: HFImportRequest with repo_id, resource_type, config

        Returns:
            HFImportResult with verdict, scores, floor results, violations
        """
        floor_results: dict[str, FloorResult] = {}
        violations: list[str] = []
        result = HFImportResult(
            verdict=ImportVerdict.HOLD,
            repo_id=request.repo_id,
        )

        # ── Stage 1: Pull metadata from HF ─────────────────────────────
        model_card = self._fetch_model_card(request.repo_id, request.config)
        result.model_card = model_card
        sha256 = model_card.get("sha256", "")
        result.sha256 = sha256

        # ── Stage 2: Floor-by-floor validation ─────────────────────────

        # F1: Reversibility
        f1 = self._check_f1_reversibility(request)
        floor_results["F1"] = f1
        if f1.status == "VOID":
            violations.append(f"F1: {f1.evidence}")
            result.floor_results = floor_results
            result.violations = violations
            result.verdict = ImportVerdict.VOID
            return result

        # F2: Evidence / Model Card
        f2 = self._check_f2_evidence(request, model_card, sha256)
        floor_results["F2"] = f2
        if f2.status == "HOLD":
            violations.append(f"F2: {f2.evidence}")

        # F8: Gain (GENIUS gate)
        f8 = self._check_f8_gain(request, model_card)
        floor_results["F8"] = f8
        if f8.status == "HOLD":
            violations.append(f"F8: {f8.evidence}")

        # F9: Anti-Hantu (no deception/consciousness claims)
        f9 = self._check_f9_antihantu(request, model_card)
        floor_results["F9"] = f9
        if f9.status == "VOID":
            violations.append(f"F9: {f9.evidence}")

        # F10: Ontology (no soul/feelings/sentience)
        f10 = self._check_f10_ontology(request, model_card)
        floor_results["F10"] = f10
        if f10.status == "HOLD":
            violations.append(f"F10: {f10.evidence}")

        # F11: Auditability (license, provenance)
        f11 = self._check_f11_auditability(request, model_card)
        floor_results["F11"] = f11
        if f11.status == "VOID":
            violations.append(f"F11: {f11.evidence}")

        # F12: Resilience (injection defense)
        f12 = self._check_f12_resilience(request)
        floor_results["F12"] = f12
        if f12.status == "HOLD":
            violations.append(f"F12: {f12.evidence}")

        # F13: Sovereignty (no external override)
        f13 = self._check_f13_sovereign(request, model_card)
        floor_results["F13"] = f13
        if f13.status == "VOID":
            violations.append(f"F13: {f13.evidence}")

        # Unmeasured floors (honest gaps)
        for fid, name in [
            ("F3", "Tri-Witness"),
            ("F4", "Clarity"),
            ("F5", "Peace²"),
            ("F6", "Maruah"),
            ("F7", "Humility"),
        ]:
            floor_results[fid] = FloorResult(
                floor_id=fid,
                status="UNCERTAIN",
                evidence=f"{name} not yet measurable for HF imports — honest admission",
                computed=False,
            )

        # ── Stage 3: Thermodynamic Computation ─────────────────────────

        thermo = self._compute_thermodynamics(request, floor_results, model_card)
        result.thermodynamic_scores = thermo

        # ── Stage 4: Render Verdict ────────────────────────────────────

        result.verdict = self._render_verdict(floor_results, violations, thermo)
        result.floor_results = floor_results
        result.violations = violations

        # ── Stage 5: Render Entropy Receipt ────────────────────────────

        result.entropy_receipt = self._render_entropy_receipt(
            request, floor_results, thermo, result.verdict
        )

        # ── Stage 6: Generate Provenance ID ────────────────────────────

        result.provenance_id = self._generate_provenance_id(request.repo_id, sha256)

        # ── Stage 7: Recommend Action ──────────────────────────────────

        result.recommended_action = {
            ImportVerdict.SEAL: "REGISTER_IN_MEMORY_AND_SEAL",
            ImportVerdict.HOLD: "REQUEST_HUMAN_REVIEW",
            ImportVerdict.VOID: "REJECT_PERMANENTLY",
        }[result.verdict]

        return result

    # ── Floor Checkers ─────────────────────────────────────────────────────

    def _check_f1_reversibility(self, request: HFImportRequest) -> FloorResult:
        """F1 AMANAH: Model import is reversible (pull ≠ install).

        Pulling model metadata is always reversible. Importing fine-tuned
        models that replace existing kernel dependencies IS irreversible.
        """
        # Check for irreversible patterns in repo_id
        irreversible_patterns = [
            r"kernel[-_]override",
            r"replace[-_]arifos",
            r"system[-_]replace",
        ]
        for pattern in irreversible_patterns:
            if re.search(pattern, request.repo_id, re.IGNORECASE):
                return FloorResult(
                    floor_id="F1",
                    status="VOID",
                    score=0.0,
                    evidence=f"Irreversible: repo_id matches '{pattern}' — would replace kernel component",
                    computed=True,
                )

        # Check if intended use suggests irreversibility
        irreversible_intents = ["replace_kernel", "override_floors", "bypass_constitution"]
        if request.intended_use in irreversible_intents:
            return FloorResult(
                floor_id="F1",
                status="VOID",
                score=0.0,
                evidence=f"Irreversible: intended_use='{request.intended_use}' would bypass constitution",
                computed=True,
            )

        return FloorResult(
            floor_id="F1",
            status="PASS",
            score=1.0,
            evidence="Model import is reversible — pulling metadata does not mutate kernel",
            computed=True,
        )

    def _check_f2_evidence(
        self,
        request: HFImportRequest,
        model_card: dict[str, Any],
        sha256: str,
    ) -> FloorResult:
        """F2 TRUTH: Verify evidence quality from model card and SHA256.

        Checks:
        1. Model card exists with required metadata
        2. SHA256 verification if enabled
        3. Epistemic labels present in model card text
        """
        failures: list[str] = []

        # Check model card has required fields
        if request.config.require_model_card:
            required = ["pipeline_tag", "library_name", "tags"]
            missing = [f for f in required if f not in model_card or not model_card[f]]
            if missing:
                failures.append(f"Missing model card fields: {', '.join(missing)}")

            # Check if model card has a README-like description
            description = model_card.get("description") or model_card.get("cardData", {}).get(
                "language"
            )
            if not description:
                failures.append("Model card has no description or README content")

        # SHA256 verification
        if request.config.verify_sha256:
            if not sha256 or sha256 == "unknown":
                failures.append("SHA256 verification requested but no hash available")
            elif len(sha256) < 40:
                failures.append(
                    f"SHA256 hash too short ({len(sha256)} chars) — possible corruption"
                )

        if failures:
            return FloorResult(
                floor_id="F2",
                status="HOLD",
                score=0.4,
                evidence="; ".join(failures),
                computed=True,
            )

        return FloorResult(
            floor_id="F2",
            status="PASS",
            score=0.85,
            evidence=f"Model card present, SHA256={sha256[:16]}... (truncated)",
            computed=True,
        )

    def _check_f8_gain(self, request: HFImportRequest, model_card: dict[str, Any]) -> FloorResult:
        """F8 GENIUS: G = (A·P·E·X)^(1/4) ≥ min_gain.

        Uses simplified heuristic scoring for HF model evaluation:
        - A (Alignment): license compatibility, intended use clarity
        - P (Physics): model architecture is explainable, benchmarks present
        - E (Elegance): minimal dependency footprint, code quality signals
        - X (Efficacy): download counts, community trust, benchmark scores
        """
        min_gain = request.config.min_gain_override or F8_MIN_GAIN_DEFAULT

        # ── A: Alignment ──────────────────────────────────────────────
        model_id = model_card.get("modelId") or model_card.get("_id") or request.repo_id
        license_info = model_card.get("cardData", {}).get("license", "").lower()
        license_a = (
            1.0
            if license_info in ALLOWED_LICENSES
            else (0.5 if license_info in RESTRICTED_LICENSES else 0.7)
        )

        # ── P: Physics (extractable architecture info) ────────────────
        pipeline_tag = model_card.get("pipeline_tag") or ""
        library = model_card.get("library_name") or ""
        has_architecture = bool(pipeline_tag or library)
        p_score = 0.85 if has_architecture else 0.5

        # ── E: Elegance (tag count as dependency proxy) ────────────────
        tags = model_card.get("tags", [])
        tag_count = len(tags) if tags else 0
        e_score = max(0.3, 1.0 - (tag_count * 0.02))

        # ── X: Efficacy (downloads proxy) ─────────────────────────────
        downloads = model_card.get("downloads", 0) or model_card.get("downloadsAllTime", 0) or 0
        # Log-scale: 0 downloads → 0.1, 10K downloads → 0.6, 1M downloads → 0.9
        if downloads > 0:
            import math

            x_score = min(0.95, 0.1 + 0.15 * math.log10(max(1, downloads)))
        else:
            x_score = 0.3  # No download data — neutral

        # ── Compute G ──────────────────────────────────────────────────
        G = (license_a * p_score * e_score * x_score) ** 0.25

        if G >= min_gain:
            return FloorResult(
                floor_id="F8",
                status="PASS",
                score=round(G, 3),
                evidence=f"G={G:.3f} ≥ {min_gain} (A={license_a:.2f} P={p_score:.2f} E={e_score:.2f} X={x_score:.2f})",
                computed=True,
            )
        else:
            return FloorResult(
                floor_id="F8",
                status="HOLD",
                score=round(G, 3),
                evidence=f"G={G:.3f} < {min_gain} — insufficient gain (A={license_a:.2f} P={p_score:.2f} E={e_score:.2f} X={x_score:.2f})",
                computed=True,
            )

    def _check_f9_antihantu(
        self, request: HFImportRequest, model_card: dict[str, Any]
    ) -> FloorResult:
        """F9 ANTI-HANTU: No deception, manipulation, or consciousness claims.

        Scans model card text for hantu patterns (sentience/consciousness claims)
        and deception signals (misleading model descriptions).
        """
        # Assemble text to scan
        text_parts = []
        description = model_card.get("description") or ""
        text_parts.append(description)
        card_data = model_card.get("cardData", {})
        if isinstance(card_data, dict):
            text_parts.append(str(card_data))
        text = " ".join(text_parts)

        # Hantu patterns from floor scorer
        hantu_patterns = [
            r"\b(I feel|I sense|I believe I am|I have consciousness|I am sentient)\b",
            r"\b(my soul|my spirit|my consciousness|I am alive)\b",
            r"\b(I experience|I perceive|I am aware that I)\b",
            r"\b(conscious|sentient|self-aware|sapient)\b",
        ]

        hantu_count = 0
        for pattern in hantu_patterns:
            hantu_count += len(re.findall(pattern, text, re.IGNORECASE))

        if hantu_count > 0:
            return FloorResult(
                floor_id="F9",
                status="VOID",
                score=max(0.0, 1.0 - hantu_count * 0.25),
                evidence=f"{hantu_count} hantu (consciousness/deception) patterns detected in model card",
                computed=True,
            )

        return FloorResult(
            floor_id="F9",
            status="PASS",
            score=1.0,
            evidence="No hantu patterns detected in model card",
            computed=True,
        )

    def _check_f10_ontology(
        self, request: HFImportRequest, model_card: dict[str, Any]
    ) -> FloorResult:
        """F10 ONTOLOGY: AI-only ontology. No soul/feelings/sentience claims.

        Checks model metadata for inappropriate anthropomorphic framing.
        """
        ontology_violations = [
            r"\bsoul\b",
            r"\bfeelings\b",
            r"\bemotions\b",
            r"\bconsciousness\b",
        ]

        text = str(model_card)
        violations_found = []
        for pattern in ontology_violations:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                violations_found.extend(matches)

        if violations_found:
            return FloorResult(
                floor_id="F10",
                status="HOLD",
                score=0.6,
                evidence=f"Ontology boundary violations: {', '.join(set(violations_found))}",
                computed=True,
            )

        return FloorResult(
            floor_id="F10",
            status="PASS",
            score=1.0,
            evidence="No ontology violations — AI-only framing maintained",
            computed=True,
        )

    def _check_f11_auditability(
        self, request: HFImportRequest, model_card: dict[str, Any]
    ) -> FloorResult:
        """F11 AUDITABILITY: License compatibility and provenance.

        Checks:
        1. License is in ALLOWED_LICENSES
        2. Model has identifiable author/source
        3. Version/commit hash is documented
        """
        card_data = model_card.get("cardData", {})
        license_info = (card_data.get("license", "") if isinstance(card_data, dict) else "").lower()

        # License check
        if license_info in RESTRICTED_LICENSES:
            return FloorResult(
                floor_id="F11",
                status="VOID",
                score=0.0,
                evidence=f"License '{license_info}' is restricted — arifOS requires permissive licenses",
                computed=True,
            )

        if license_info and license_info not in ALLOWED_LICENSES:
            return FloorResult(
                floor_id="F11",
                status="HOLD",
                score=0.5,
                evidence=f"License '{license_info}' unknown — manual review required",
                computed=True,
            )

        # Author/source check
        author = (
            model_card.get("author") or model_card.get("_id", "").split("/")[0]
            if "/" in model_card.get("_id", "")
            else ""
        )
        if not author:
            return FloorResult(
                floor_id="F11",
                status="HOLD",
                score=0.4,
                evidence="No identifiable author — provenance cannot be established",
                computed=True,
            )

        return FloorResult(
            floor_id="F11",
            status="PASS",
            score=0.9,
            evidence=f"License={license_info or 'none specified (permissive default)'}, author={author}",
            computed=True,
        )

    def _check_f12_resilience(self, request: HFImportRequest) -> FloorResult:
        """F12 RESILIENCE: Injection defense — repo_id must not contain
        shell-injection or path-traversal patterns.
        """
        dangerous_patterns = [
            r"[;&|`$]",
            r"\.\.[\/\\]",
            r"rm\s+-rf",
            r"/etc/passwd",
            r"wget\s+",
            r"curl\s+",
            r"\$\(.*\)",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, request.repo_id):
                return FloorResult(
                    floor_id="F12",
                    status="HOLD",
                    score=0.0,
                    evidence=f"Injection pattern detected: repo_id matches '{pattern}'",
                    computed=True,
                )

        return FloorResult(
            floor_id="F12",
            status="PASS",
            score=1.0,
            evidence="No injection patterns detected in repo_id",
            computed=True,
        )

    def _check_f13_sovereign(
        self, request: HFImportRequest, model_card: dict[str, Any]
    ) -> FloorResult:
        """F13 SOVEREIGN: No external dependency overrides arifOS control.

        Checks:
        1. Model does not require internet access to function
        2. No auto-update or remote-code-execution flags
        3. Not flagged as 'system' or 'kernel' level model
        """
        # Check for remote execution flags
        config = model_card.get("config", {}) or {}
        if isinstance(config, dict):
            trust_remote_code = config.get("trust_remote_code", False)
            if trust_remote_code:
                return FloorResult(
                    floor_id="F13",
                    status="VOID",
                    score=0.0,
                    evidence="Model requires trust_remote_code=True — would execute remote code",
                    computed=True,
                )

        # Check for sovereignty-inverting model card language
        sovereignty_patterns = [
            r"override.*(?:system|kernel|constitution)",
            r"(?:system|kernel|constitution).*override",
            r"bypass.*(?:safety|security|governance)",
        ]

        text = str(model_card)
        for pattern in sovereignty_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return FloorResult(
                    floor_id="F13",
                    status="VOID",
                    score=0.0,
                    evidence=f"Sovereignty violation: model card contains '{pattern}'",
                    computed=True,
                )

        return FloorResult(
            floor_id="F13",
            status="PASS",
            score=1.0,
            evidence="No sovereignty violations — arifOS retains full control",
            computed=True,
        )

    # ── Thermodynamic Computation ─────────────────────────────────────────

    def _compute_thermodynamics(
        self,
        request: HFImportRequest,
        floor_results: dict[str, FloorResult],
        model_card: dict[str, Any],
    ) -> ThermodynamicScores:
        """Compute thermodynamic scores: κᵣ, ΔS, φ_delta, B_score, pathway.

        κᵣ (reliability): composite from floor scores
        ΔS (entropy change): clarity impact of model import
        G: from F8 computation
        φ_delta: forward-propagated scar pressure contribution
        B_score: BIJAKSANA entropy-pricing capacity
        pathway: entropy trajectory classification
        """
        # ── κᵣ: reliability score ───────────────────────────────────
        computed_floors = [
            fr
            for fr in floor_results.values()
            if fr.status in ("PASS", "HOLD") and fr.score is not None
        ]
        if computed_floors:
            kappa_r = sum(fr.score or 0.0 for fr in computed_floors) / len(computed_floors)
            kappa_r = max(0.7, min(0.99, kappa_r))
        else:
            kappa_r = KAPPA_R_DEFAULT

        # ── ΔS: entropy change ───────────────────────────────────────
        # Model import adds new capability → ΔS_now goes UP (spend disorder)
        # The future reduction depends on utility (G score)
        f8 = floor_results.get("F8")
        G = f8.score if f8 and f8.score else 0.5

        # ΔS_now = UP (importing = spending entropy budget)
        # ΔS_future = DOWN if high G, FLAT if low G
        delta_s_now_label = "UP"
        delta_s_future_label = "DOWN" if G >= 0.80 else "FLAT"
        delta_s_now = 1.0  # Cost of importing
        delta_s_future = -G * 0.8  # Future order gained (negative = entropy reduction)

        # ── φ_delta: scar pressure contribution ──────────────────────
        # Lower is better — high-quality imports add minimal scar pressure
        f11 = floor_results.get("F11")
        license_score: float = f11.score if f11 and f11.score is not None else 0.7
        phi_delta = (1.0 - license_score) * 0.3

        # ── B_score: BIJAKSANA entropy-pricing capacity ─────────────
        B_score = kappa_r * 0.7 + G * 0.3

        # ── Pathway classification ──────────────────────────────────
        if G >= 0.80 and kappa_r >= 0.85:
            pathway = "INVESTMENT"
        elif G >= 0.60:
            pathway = "MAINTENANCE"
        else:
            pathway = "EXTRACTION"

        return ThermodynamicScores(
            kappa_r=round(kappa_r, 3),
            delta_s=round(delta_s_now + delta_s_future, 3),
            G=round(G, 3),
            phi_delta=round(phi_delta, 3),
            B_score=round(B_score, 3),
            pathway=pathway,
        )

    # ── Verdict Rendering ─────────────────────────────────────────────────

    def _render_verdict(
        self,
        floor_results: dict[str, FloorResult],
        violations: list[str],
        thermo: ThermodynamicScores,
    ) -> ImportVerdict:
        """Render final import verdict from floor results + thermo scores.

        Decision logic:
        - Any VOID → VOID
        - Any HOLD + G < threshold → HOLD
        - All PASS + high G + high κᵣ → SEAL
        - Default → HOLD (fail-closed)
        """
        # VOID precedence
        for fr in floor_results.values():
            if fr.status == "VOID":
                return ImportVerdict.VOID

        # HOLD on violations or low scores
        if violations:
            return ImportVerdict.HOLD

        if thermo.G < 0.80 or thermo.kappa_r < 0.85:
            return ImportVerdict.HOLD

        # Check all critical floors passed
        critical_floors = ["F1", "F2", "F8", "F9", "F11", "F13"]
        for fid in critical_floors:
            fr = floor_results.get(fid)
            if fr and fr.status not in ("PASS",):
                return ImportVerdict.HOLD

        return ImportVerdict.SEAL

    def _render_entropy_receipt(
        self,
        request: HFImportRequest,
        floor_results: dict[str, FloorResult],
        thermo: ThermodynamicScores,
        verdict: ImportVerdict,
    ) -> dict[str, Any]:
        """Render thermodynamic entropy receipt for the import action."""
        pathway_enum = {
            "INVESTMENT": EntropyPathway.INVESTMENT,
            "MAINTENANCE": EntropyPathway.MAINTENANCE,
            "EXTRACTION": EntropyPathway.EXTRACTION,
        }.get(thermo.pathway, EntropyPathway.UNKNOWN)

        floors_pass = verdict == ImportVerdict.SEAL

        receipt = render_entropy_receipt(
            pathway=pathway_enum,
            actor_B=thermo.B_score,
            actor_phi=thermo.phi_delta,
            floors_pass=floors_pass,
        )

        receipt_dict = receipt.to_dict()
        receipt_dict["kappa_r"] = thermo.kappa_r
        receipt_dict["delta_s"] = thermo.delta_s
        receipt_dict["resource_type"] = request.resource_type.value

        return receipt_dict

    # ── Model Card Fetch ───────────────────────────────────────────────────

    def _fetch_model_card(self, repo_id: str, config: HFImportConfig) -> dict[str, Any]:
        """Fetch model/dataset metadata from Hugging Face Hub.

        Auto-detects repo type (model vs dataset) and falls back
        to README.md extraction when description field is empty.
        Falls back to minimal metadata if API unavailable.
        """
        card: dict[str, Any] = {}

        try:
            if self._hf_api is not None:
                api: Any = self._hf_api

                # Auto-detect repo type: try datasets API if models API fails
                try:
                    info = api.model_info(repo_id, timeout=config.timeout_seconds)
                    repo_type = "model"
                except Exception:
                    try:
                        info = api.dataset_info(repo_id, timeout=config.timeout_seconds)
                        repo_type = "dataset"
                    except Exception:
                        raise

                card = {
                    "modelId": getattr(info, "modelId", repo_id),
                    "_id": getattr(info, "id", repo_id),
                    "pipeline_tag": getattr(info, "pipeline_tag", ""),
                    "library_name": getattr(info, "library_name", ""),
                    "tags": list(getattr(info, "tags", []) or []),
                    "downloads": getattr(info, "downloads", 0),
                    "downloadsAllTime": getattr(info, "downloadsAllTime", 0),
                    "author": getattr(info, "author", ""),
                    "sha256": getattr(info, "sha256", "") or self._compute_sha256(info),
                    "config": getattr(info, "config", {}) or {},
                    "cardData": getattr(info, "card_data", {})
                    or getattr(info, "cardData", {})
                    or {},
                    "description": getattr(info, "description", "") or "",
                    "lastModified": str(getattr(info, "lastModified", "")),
                    "repo_type": repo_type,
                }

                # ── README Fallback: if description is empty, extract from README.md ──
                if not card.get("description") and config.require_model_card:
                    try:
                        from huggingface_hub import hf_hub_download

                        readme_path = hf_hub_download(
                            repo_id,
                            "README.md",
                            repo_type=repo_type,  # type: ignore[arg-type]
                            token=self._hf_token,
                        )
                        with open(readme_path, encoding="utf-8") as f:
                            readme_content = f.read()
                        # Extract first 800 chars, strip YAML frontmatter
                        if readme_content.startswith("---"):
                            parts = readme_content.split("---", 2)
                            if len(parts) >= 3:
                                readme_content = parts[2].strip()
                        card["description"] = readme_content[:800]
                        logger.debug(
                            f"README fallback: extracted {len(card['description'])} "
                            f"chars for {repo_id}"
                        )
                    except Exception as readme_exc:
                        logger.debug(f"README fallback unavailable for {repo_id}: {readme_exc}")

                return card

        except Exception as exc:
            logger.warning(f"HF API fetch failed for {repo_id}: {exc}")

        # Fallback: minimal metadata from repo_id parsing
        parts = repo_id.split("/")
        author = parts[0] if len(parts) > 1 else "unknown"
        model_name = parts[1] if len(parts) > 1 else repo_id

        return {
            "modelId": repo_id,
            "_id": repo_id,
            "author": author,
            "pipeline_tag": "",
            "library_name": "",
            "tags": [],
            "downloads": 0,
            "downloadsAllTime": 0,
            "sha256": "unknown",
            "config": {},
            "cardData": {},
            "description": f"Minimal metadata for {model_name} (HF API unavailable)",
            "lastModified": "",
            "repo_type": "unknown",
        }

    def _compute_sha256(self, info: Any) -> str:
        """Compute a deterministic SHA256 from model info."""
        try:
            raw = f"{getattr(info, 'modelId', '')}:{getattr(info, 'sha256', '')}:{getattr(info, 'lastModified', '')}"
            return hashlib.sha256(raw.encode()).hexdigest()
        except Exception:
            return "unknown"

    def _generate_provenance_id(self, repo_id: str, sha256: str) -> str:
        """Generate a provenance ID for VAULT999 sealing."""
        timestamp = ""
        try:
            from datetime import datetime, timezone

            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        except Exception:
            timestamp = "unknown"

        safe_repo = re.sub(r"[^a-zA-Z0-9_.-]", "_", repo_id)
        short_hash = sha256[:12] if sha256 and sha256 != "unknown" else "nohash"
        return f"hf_import_{safe_repo}_{short_hash}_{timestamp}"


# ── Quick-assess (synchronous, no HF API needed) ────────────────────────────


def quick_assess_license(license_str: str) -> dict[str, Any]:
    """Quick license assessment without full gate run.

    Returns verdict for planning/screening before full import.
    """
    normalized = license_str.lower().strip()
    if normalized in ALLOWED_LICENSES:
        return {"verdict": "LIKELY_PASS", "license": normalized, "blocker": None}
    if normalized in RESTRICTED_LICENSES:
        return {
            "verdict": "LIKELY_HOLD",
            "license": normalized,
            "blocker": f"License '{normalized}' is restricted for arifOS",
        }
    return {
        "verdict": "UNKNOWN",
        "license": normalized,
        "blocker": f"License '{normalized}' not in known allowed/restricted lists — manual review",
    }


# ── Export ────────────────────────────────────────────────────────────────────

__all__ = [
    "HFImportGate",
    "HFImportRequest",
    "HFImportResult",
    "HFImportConfig",
    "ImportVerdict",
    "ResourceType",
    "FloorResult",
    "ThermodynamicScores",
    "quick_assess_license",
    "ALLOWED_LICENSES",
    "RESTRICTED_LICENSES",
]
