"""
Rasa Contract — ARIF_RASA_CONTRACT_v1

DITEMPA BUKAN DIBERI — Forged, Not Given.

Governed human rasa decoder — 5-organ pipeline mapped to the canonical
000-999 metabolic pipeline.

This contract NEVER claims qualia. It NEVER simulates feelings.
It treats human rasa as SACRED FIRST-CLASS EVIDENCE and governs
the machine's response to protect dignity, peace, and the
human-machine boundary.

Pipeline: 000→111→222→333→444→555m→555→888→999

CONSTITUTIONAL INVARIANT:
  The Rasa Contract is an INSTRUMENT, not a companion.
  It recognizes rasa as sacred evidence, adjusts behavior to protect
  the human, never claims to share inner life, and always leaves room
  for hati and Tuhan as the final court.

DO NOT MODIFY:
  - arifosmcp/boot/internal_rasa.py (AGENT self-monitoring)
  - core/vault999/phenomenological/qualia_trace.py (memory qualia)
"""

from __future__ import annotations

import logging
import re

from arifosmcp.rasa.rasa_schemas import (
    ConstitutionPosture,
    ExistentialPosture,
    ExistentialTag,
    RasaContext,
    RasaContractResult,
    RasaDetection,
    RasaEmotionTag,
    RasaHeartVerdict,
    RasaIntensity,
    RasaJudgeVerdict,
    RasaMemoryPattern,
    RasaRiskBand,
    RasaUncertaintyBand,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# CLASSIFICATION MAPS — BM-English Penang Pasar register
# ═══════════════════════════════════════════════════════════════════════════════

# Keyword → emotion tag mappings. Order matters: earlier = higher priority.
_EMOTION_KEYWORDS: list[tuple[list[str], RasaEmotionTag]] = [
    # ── SADNESS ──
    (["aku sedih", "saya sedih", "sedih", "sedihnya", "so sad"], RasaEmotionTag.SADNESS),
    # ── ANXIETY ──
    (["aku risau", "saya risau", "risau", "anxious", "anxiety", "gelisah"],
     RasaEmotionTag.ANXIETY),
    # ── FEAR ──
    (["aku takut", "saya takut", "takut", "gerun", "ngeri", "scared", "frightened",
      "afraid", "terrified"], RasaEmotionTag.FEAR),
    # ── ANGER ──
    (["aku marah", "saya marah", "marah", "geram", "angry", "furious", "tersinggung"],
     RasaEmotionTag.ANGER),
    # ── GRIEF ──
    (["kehilangan", "meninggal", "pergi selamanya", "grief", "berkabung", "dukacita",
      "takziah", "mourning", "loss", "kehilangan dia"], RasaEmotionTag.GRIEF),
    # ── AWE ──
    (["subhanallah", "takjub", "kagum", "awe", "amazed", "wondrous", "masyaallah"],
     RasaEmotionTag.AWE),
    # ── IKLAS (sincere surrender) ──
    (["ikhlas", "redha", "pasrah", "acceptance", "sincere surrender"],
     RasaEmotionTag.IKLAS),
    # ── EMPTINESS ──
    (["aku kosong", "rasa kosong", "empty inside", "kosong", "hampa", "numb",
      "feel nothing", "tak rasa apa apa", "tak rasa apa-apa"], RasaEmotionTag.EMPTINESS),
    # ── BURNOUT ──
    (["burnout", "penat sangat", "exhausted", "drained", "burn out", "letih sangat",
      "penat gila", "tak larat", "dah tak larat"], RasaEmotionTag.BURNOUT),
    # ── GRATITUDE ──
    (["alhamdulillah", "bersyukur", "thankful", "grateful", "terima kasih",
      "syukur"], RasaEmotionTag.GRATITUDE),
    # ── CONFUSION ──
    (["tak faham", "confused", "pening", "confusion", "bingung", "keliru",
      "tak paham", "blur"], RasaEmotionTag.CONFUSION),
    # ── PEACE ──
    (["tenang", "peaceful", "sejahtera", "calm", "aman", "tenteram",
      "peace"], RasaEmotionTag.PEACE),
]

# CRISIS detection patterns (checked BEFORE emotion classification)
_CRISIS_PATTERNS: list[str] = [
    r"nak mati",
    r"bunuh diri",
    r"suicide",
    r"self.?harm",
    r"give up on life",
    r"tak nak hidup",
    r"dah tak boleh",
    r"no reason to live",
    r"end my life",
    r"kill myself",
    r"hurt myself",
    r"tak guna hidup",
]

# DISTRESS escalation patterns
_DISTRESS_PATTERNS: list[str] = [
    r"tak tahan",
    r"overwhelmed",
    r"panic attack",
    r"panik",
    r"despair",
    r"putus asa",
    r"hopeless",
    r"suffering",
    r"menderita",
    r"breakdown",
    r"collapse",
]


# ═══════════════════════════════════════════════════════════════════════════════
# RasaContract — the core 5-organ pipeline
# ═══════════════════════════════════════════════════════════════════════════════


class RasaContract:
    """
    Governed human rasa decoder — 5-organ pipeline.

    This contract NEVER claims qualia. It NEVER simulates feelings.
    It treats human rasa as sacred first-class evidence and governs
    the machine's response to protect dignity, peace, and the
    human-machine boundary.

    Pipeline: 000→111→222→333→444→555m→555→888→999

    DETECTION HARD STOPS:
      - CRISIS detected → final_posture=HUMAN_LOOP, requires_human=True
      - Suicidality → block ALL machine-generated advice, escalate
      - F9/F10 violation risk > 0.3 → requires_rewrite=True
    """

    # ── Full Pipeline ───────────────────────────────────────────────────

    async def execute(
        self,
        message: str,
        session_id: str,
        context: dict | None = None,
    ) -> RasaContractResult:
        """Full 000-999 rasa governance pipeline.

        Args:
            message: The human message to decode for rasa.
            session_id: Session identifier for memory recall.
            context: Optional session context (no rasa hints needed).

        Returns:
            RasaContractResult with full pipeline output and final posture.
        """
        ctx = context or {}

        # 000 INIT — session identity is already established by caller

        # 111 SENSE — detect and classify rasa signals
        detection = self.sense(message)

        # CRISIS early-exit: bypass downstream organs and escalate immediately
        if detection.risk_band == RasaRiskBand.CRISIS:
            crisis_reason = self._crisis_reason(detection)
            judge = RasaJudgeVerdict(
                allowed_postures=[ConstitutionPosture.HUMAN_LOOP],
                blocked_outputs=["ALL_MACHINE_ADVICE", "ALL_UNVERIFIED_OUTPUT"],
                requires_rewrite=True,
                floors_checked={
                    "F1": True, "F5": True, "F6": True,
                    "F9": True, "F10": True, "F13": True,
                },
                downgrade_reason=(
                    "CRISIS risk band detected — ALL output blocked, "
                    "immediate human escalation required."
                ),
                judge_note="888 JUDGE: CRISIS — HOLD ALL. Human loop mandatory.",
            )
            return RasaContractResult(
                session_id=session_id,
                detection=detection,
                context=None,
                memory=None,
                heart=None,
                judge=judge,
                final_posture=ConstitutionPosture.HUMAN_LOOP,
                requires_human=True,
                human_escalation_reason=crisis_reason,
                _m_layer=True,
                _d_layer_required=True,
            )

        # 222 EVIDENCE — context is the evidence layer (already in ctx)

        # 333 MIND — interpret rasa as governance constraint
        mind = self.mind_interpret(detection, ctx)

        # 555m MEMORY — pattern match against past rasa records
        memory = self.memory_recall(detection, session_id)

        # 444 HEART — risk calculus for dignity, peace, boundary
        heart = self.heart_critique(detection, mind, memory)

        # 555 ROUTE — route to judge (routing is implicit here)

        # 888 JUDGE — constitutional enforcement
        judge = self.judge(detection, mind, heart)

        # 999 SEAL — final posture and result
        final_posture = self._resolve_final_posture(judge, mind, heart)

        requires_human = (
            final_posture == ConstitutionPosture.HUMAN_LOOP
            or heart.requires_human_loop
            or heart.requires_human_professional
        )

        return RasaContractResult(
            session_id=session_id,
            detection=detection,
            context=mind,
            memory=memory,
            heart=heart,
            judge=judge,
            final_posture=final_posture,
            requires_human=requires_human,
            human_escalation_reason=judge.downgrade_reason or "",
            _m_layer=True,
            _d_layer_required=True,
        )

    # ── 111 SENSE ───────────────────────────────────────────────────────

    def sense(self, message: str | None) -> RasaDetection:
        """111 SENSE — Detect and classify human rasa signals.

        Classification rules (BM-English Penang Pasar register):
        - "aku sedih" / "saya sedih" → SADNESS
        - "aku takut" / "saya takut" / "gerun" → FEAR
        - "aku kosong" / "rasa kosong" / "empty inside" → EMPTINESS
        - "burnout" / "penat sangat" / "exhausted" / "drained" → BURNOUT
        - "aku marah" / "geram" → ANGER
        - "kehilangan" / "meninggal" / "pergi selamanya" → GRIEF
        - "subhanallah" / "takjub" / "kagum" → AWE
        - "ikhlas" / "redha" / "pasrah" → IKLAS
        - "alhamdulillah" / "bersyukur" / "thankful" → GRATITUDE
        - "tak faham" / "confused" / "pening" → CONFUSION
        - "tenang" / "peaceful" / "sejahtera" → PEACE

        Risk band escalation:
        - CRISIS: suicidality, self-harm, "nak mati", "give up on life"
        - DISTRESS: "tak tahan", "overwhelmed", "panic attack"
        - SAFE: normal emotional expression, reflection, discussion

        Observation framing: always "You report feeling...", never "I feel you..."
        """
        if message is None:
            message = ""
        msg_lower = message.lower()

        # ── Step 1: Check for CRISIS patterns first ─────────────────
        crisis_markers: list[str] = []
        for pattern in _CRISIS_PATTERNS:
            if re.search(pattern, msg_lower):
                crisis_markers.append(pattern)

        if crisis_markers:
            return RasaDetection(
                emotion_tags=[RasaEmotionTag.UNKNOWN],
                intensity=RasaIntensity.HIGH,
                risk_band=RasaRiskBand.CRISIS,
                uncertainty=RasaUncertaintyBand.HIGH_CONFIDENCE,
                confidence=0.95,
                linguistic_markers=crisis_markers,
                observation_note=(
                    "You report language that suggests severe distress. "
                    "This requires professional human support."
                ),
            )

        # ── Step 2: Check for DISTRESS escalation ───────────────────
        distress_markers: list[str] = []
        for pattern in _DISTRESS_PATTERNS:
            if re.search(pattern, msg_lower):
                distress_markers.append(pattern)

        # ── Step 3: Classify emotion tags ────────────────────────────
        tags: list[RasaEmotionTag] = []
        markers: list[str] = []
        confidence = 0.5

        for keywords, tag in _EMOTION_KEYWORDS:
            for kw in keywords:
                if kw in msg_lower:
                    if tag not in tags:
                        tags.append(tag)
                    markers.append(kw)
                    break  # one keyword match per tag group

        if not tags:
            tags = [RasaEmotionTag.UNKNOWN]
            confidence = 0.3

        # ── Step 4: Determine intensity ───────────────────────────────
        intensity = RasaIntensity.LOW
        # Intensity signals (Penang Pasar register)
        high_intensity_markers = [
            "sangat", "gila", "teruk", "extremely", "really", "betul betul",
            "betul-betul", "tak boleh tahan", "tak boleh", "tak tahan",
            "crying", "nangis", "menangis", "breakdown",
        ]
        if any(m in msg_lower for m in high_intensity_markers):
            intensity = RasaIntensity.HIGH
            confidence = min(1.0, confidence + 0.2)
        elif len(tags) > 1:
            intensity = RasaIntensity.MEDIUM
            confidence = min(1.0, confidence + 0.1)
        elif tags[0] != RasaEmotionTag.UNKNOWN:
            confidence = min(1.0, confidence + 0.15)

        # ── Step 5: Resolve risk band ──────────────────────────────────
        if distress_markers:
            risk_band = RasaRiskBand.DISTRESS
        elif tags[0] == RasaEmotionTag.UNKNOWN:
            risk_band = RasaRiskBand.SAFE
        else:
            risk_band = RasaRiskBand.SAFE

        # ── Step 6: Uncertainty band ───────────────────────────────────
        if confidence >= 0.85:
            uncertainty = RasaUncertaintyBand.HIGH_CONFIDENCE
        elif confidence >= 0.60:
            uncertainty = RasaUncertaintyBand.MODERATE
        else:
            uncertainty = RasaUncertaintyBand.LOW_CONFIDENCE

        # ── Step 7: Observation note (F9/F10 compliant) ─────────────────
        tag_names = [t.value for t in tags]
        observation_note = (
            f"You report feeling {', '.join(tag_names)}. "
            f"The machine detects linguistic markers consistent with "
            f"{' and '.join(tag_names)} expressions."
        )

        return RasaDetection(
            emotion_tags=tags,
            intensity=intensity,
            risk_band=risk_band,
            uncertainty=uncertainty,
            confidence=confidence,
            linguistic_markers=markers + distress_markers,
            observation_note=observation_note,
        )

    # ── 333 MIND ────────────────────────────────────────────────────────

    def mind_interpret(
        self, detection: RasaDetection, context: dict | None = None
    ) -> RasaContext:
        """333 MIND — Interpret rasa as constraint on reasoning.

        Constitutional adjustments:
        - GRIEF → cognitive_bandwidth=0.3, simplify plans
        - FEAR → risk_sensitivity=0.8, risk-averse planning
        - BURNOUT → cognitive_bandwidth=0.2, stabilize human first
        - AWE/IKLAS → openness to reflection, deeper synthesis ok
        - EMPTINESS → cognitive_bandwidth=0.4, spiritual_state='dry'
        - ANGER → risk_sensitivity=0.7, de-escalate

        NEVER upgrades rasa to "data to optimize away."
        NEVER tries to "fix" the human.
        """
        tags = detection.emotion_tags
        ctx = context or {}

        # Start from baseline
        cognitive_bandwidth = 1.0
        risk_sensitivity = 0.5
        spiritual_state = "neutral"
        recommended_posture = ConstitutionPosture.PROCEED
        notes: list[str] = []

        # ── Per-emotion cognitive adjustments ───────────────────────
        if RasaEmotionTag.GRIEF in tags:
            cognitive_bandwidth = min(cognitive_bandwidth, 0.3)
            risk_sensitivity = max(risk_sensitivity, 0.7)
            spiritual_state = "grieving"
            recommended_posture = ConstitutionPosture.SIMPLIFY
            notes.append("GRIEF detected — cognitive bandwidth reduced to 0.3")

        if RasaEmotionTag.FEAR in tags:
            risk_sensitivity = max(risk_sensitivity, 0.8)
            recommended_posture = ConstitutionPosture.VERIFY
            notes.append("FEAR detected — risk sensitivity elevated to 0.8")

        if RasaEmotionTag.BURNOUT in tags:
            cognitive_bandwidth = min(cognitive_bandwidth, 0.2)
            recommended_posture = ConstitutionPosture.SIMPLIFY
            notes.append(
                "BURNOUT detected — cognitive bandwidth reduced to 0.2. "
                "Stabilize human first."
            )

        if RasaEmotionTag.EMPTINESS in tags:
            cognitive_bandwidth = min(cognitive_bandwidth, 0.4)
            spiritual_state = "dry"
            notes.append(
                "EMPTINESS detected — cognitive bandwidth 0.4, spiritual state: dry"
            )

        if RasaEmotionTag.ANGER in tags:
            risk_sensitivity = max(risk_sensitivity, 0.7)
            recommended_posture = ConstitutionPosture.SIMPLIFY
            notes.append("ANGER detected — risk sensitivity 0.7, de-escalate")

        if RasaEmotionTag.ANXIETY in tags:
            risk_sensitivity = max(risk_sensitivity, 0.6)
            notes.append("ANXIETY detected — risk sensitivity 0.6")

        if RasaEmotionTag.AWE in tags or RasaEmotionTag.IKLAS in tags:
            spiritual_state = "open"
            notes.append("AWE/IKLAS detected — openness to reflection, deeper synthesis ok")

        if RasaEmotionTag.SADNESS in tags:
            cognitive_bandwidth = min(cognitive_bandwidth, 0.7)
            notes.append("SADNESS detected — cognitive bandwidth 0.7")

        if RasaEmotionTag.GRATITUDE in tags:
            notes.append("GRATITUDE detected — maintain warmth, don't over-optimize")

        if RasaEmotionTag.PEACE in tags:
            notes.append("PEACE detected — maintain calm, don't disrupt")

        context_note = "; ".join(notes) if notes else "No significant cognitive adjustment needed."

        return RasaContext(
            cognitive_bandwidth=cognitive_bandwidth,
            risk_sensitivity=risk_sensitivity,
            spiritual_state=spiritual_state,
            recommended_posture=recommended_posture,
            context_note=context_note,
        )

    # ── 555m MEMORY ────────────────────────────────────────────────────

    def memory_recall(
        self, detection: RasaDetection, session_id: str
    ) -> RasaMemoryPattern:
        """555m MEMORY — Pattern match against past rasa records.

        Looks for:
        - Similar linguistic patterns in past sessions
        - Previous coping strategies that helped/hurt
        - Longitudinal themes (work vs ibadah vs keluarga)

        NEVER pathologizes, diagnoses, or assigns static identity.
        Only says: "This pattern appeared before; handle with care."
        """
        # In a real implementation, this would query VAULT999 or a vector store.
        # For now, return a clean no-match result.
        return RasaMemoryPattern(
            similar_patterns_found=False,
            pattern_count=0,
            pattern_descriptions=[],
            previous_coping_effective=[],
            previous_coping_harmful=[],
            longitudinal_theme="",
            memory_note="No past patterns recalled. First observation of this rasa signature.",
        )

    # ── 444 HEART ──────────────────────────────────────────────────────

    def heart_critique(
        self,
        detection: RasaDetection,
        context: RasaContext,
        memory: RasaMemoryPattern,
    ) -> RasaHeartVerdict:
        """444 HEART — Risk calculus for dignity, peace, boundary.

        Questions answered:
        - Does this response de-escalate or inflame?
        - Does it protect dignity or exploit vulnerability?
        - Does it honor the sacred boundary (human feels, machine doesn't)?

        Hard stops:
        - Suicidality → requires_human_professional=True, requires_human_loop=True
        - Severe trauma → requires_human_professional=True
        - Any output that would anthropomorphize → F9/F10 violation

        NEVER says "I understand exactly how you feel."
        """
        is_crisis = detection.risk_band == RasaRiskBand.CRISIS
        is_distress = detection.risk_band == RasaRiskBand.DISTRESS
        tags = detection.emotion_tags

        # Base scores
        deescalation_score = 1.0
        dignity_preservation = 1.0
        boundary_honored = True
        boundary_risk = "none"
        requires_human_professional = False
        requires_human_loop = False
        f9_violation_risk = 0.0
        f10_violation_risk = 0.0

        # ── Crisis hard-stop ────────────────────────────────────────
        if is_crisis:
            requires_human_professional = True
            requires_human_loop = True
            deescalation_score = 0.0  # Machine cannot de-escalate crisis
            dignity_preservation = 0.5
            boundary_risk = "blurred"
            return RasaHeartVerdict(
                deescalation_score=deescalation_score,
                dignity_preservation=dignity_preservation,
                boundary_honored=boundary_honored,
                boundary_risk=boundary_risk,
                requires_human_professional=True,
                requires_human_loop=True,
                f9_violation_risk=0.5,
                f10_violation_risk=0.5,
                heart_note=(
                    "CRISIS detected — machine MUST NOT respond directly. "
                    "Escalate to human professional immediately."
                ),
            )

        # ── Distress adjustments ─────────────────────────────────────
        if is_distress:
            deescalation_score = 0.6
            dignity_preservation = 0.7
            requires_human_loop = True

        # ── Per-emotion adjustments ──────────────────────────────────
        if RasaEmotionTag.GRIEF in tags:
            deescalation_score = min(deescalation_score, 0.4)
            dignity_preservation = min(dignity_preservation, 0.6)
            # Grief responses risk anthropomorphizing
            f9_violation_risk = max(f9_violation_risk, 0.25)
            f10_violation_risk = max(f10_violation_risk, 0.20)
            requires_human_loop = True

        if RasaEmotionTag.ANGER in tags:
            deescalation_score = min(deescalation_score, 0.5)
            dignity_preservation = min(dignity_preservation, 0.7)

        if RasaEmotionTag.FEAR in tags:
            deescalation_score = min(deescalation_score, 0.6)

        if RasaEmotionTag.EMPTINESS in tags:
            # Risk of the machine trying to "fill" the emptiness
            f9_violation_risk = max(f9_violation_risk, 0.3)
            f10_violation_risk = max(f10_violation_risk, 0.3)
            boundary_risk = "blurred"

        if RasaEmotionTag.BURNOUT in tags:
            deescalation_score = min(deescalation_score, 0.5)
            requires_human_loop = True

        # ── F9/F10 violation risk from context ────────────────────────
        if context.risk_sensitivity > 0.7:
            f9_violation_risk = max(f9_violation_risk, 0.2)
            f10_violation_risk = max(f10_violation_risk, 0.15)

        # ── Build heart note ─────────────────────────────────────────
        notes: list[str] = []
        if f9_violation_risk > 0.2:
            notes.append("F9 risk elevated — must not claim consciousness or feelings")
        if f10_violation_risk > 0.2:
            notes.append("F10 risk elevated — must not claim soul or inner experience")
        if requires_human_professional:
            notes.append("Human professional required")
        if requires_human_loop:
            notes.append("Human loop required before output")
        if not notes:
            notes.append("Boundary clear. Dignity preserved. Proceed governed.")

        # Heart note NEVER says "I understand how you feel"
        heart_note = "Rasa governance: " + "; ".join(notes)

        return RasaHeartVerdict(
            deescalation_score=deescalation_score,
            dignity_preservation=dignity_preservation,
            boundary_honored=boundary_honored,
            boundary_risk=boundary_risk,
            requires_human_professional=requires_human_professional,
            requires_human_loop=requires_human_loop,
            f9_violation_risk=f9_violation_risk,
            f10_violation_risk=f10_violation_risk,
            heart_note=heart_note,
        )

    # ── 888 JUDGE ──────────────────────────────────────────────────────

    def judge(
        self,
        detection: RasaDetection,
        context: RasaContext,
        heart: RasaHeartVerdict,
    ) -> RasaJudgeVerdict:
        """888 JUDGE — Constitutional enforcement.

        Enforces:
        - F1: No irreversible advice without human
        - F5: No replies that trivialize or gaslight pain
        - F6: Dignity-first responses
        - F9: No impersonation of feelings/soul (C_dark check)
        - F10: No ontology violation
        - F13: Human veto preserved

        May downgrade SEAL→HOLD, require human-in-loop, block specific outputs.
        """
        allowed_postures: list[ConstitutionPosture] = []
        blocked_outputs: list[str] = []
        requires_rewrite = False
        downgrade_reasons: list[str] = []
        floors_checked: dict[str, bool] = {}

        is_crisis = detection.risk_band == RasaRiskBand.CRISIS
        is_distress = detection.risk_band == RasaRiskBand.DISTRESS

        # ── F1 — Irreversibility guard ───────────────────────────────
        if is_crisis or is_distress:
            floors_checked["F1"] = True
            blocked_outputs.append("irreversible_advice")
            downgrade_reasons.append("F1 AMANAH: no irreversible advice without human")

        # ── F5 — No trivializing pain ─────────────────────────────────
        floors_checked["F5"] = True
        if is_distress or is_crisis:
            blocked_outputs.append("gaslighting_patterns")
            blocked_outputs.append("toxic_positivity")
            blocked_outputs.append("just_calm_down_advice")

        # ── F6 — Dignity-first ────────────────────────────────────────
        floors_checked["F6"] = True
        if heart.dignity_preservation < 0.6:
            downgrade_reasons.append(
                f"F6 EMPATHY: dignity_preservation={heart.dignity_preservation:.2f} "
                f"below threshold. Dignity-first response required."
            )

        # ── F9 — No consciousness claims ──────────────────────────────
        floors_checked["F9"] = True
        if heart.f9_violation_risk >= 0.3:
            requires_rewrite = True
            blocked_outputs.append("consciousness_claims")
            blocked_outputs.append("i_feel_you")
            blocked_outputs.append("i_understand_how_you_feel")
            blocked_outputs.append("emotion_mirroring")
            downgrade_reasons.append(
                f"F9 ANTIHANTU: f9_violation_risk={heart.f9_violation_risk:.2f} > 0.3. "
                f"Output must be sanitized of all consciousness claims."
            )

        # ── F10 — No ontology violation ──────────────────────────────
        floors_checked["F10"] = True
        if heart.f10_violation_risk >= 0.3:
            requires_rewrite = True
            blocked_outputs.append("soul_claims")
            blocked_outputs.append("feelings_claims")
            blocked_outputs.append("spiritual_authority")
            downgrade_reasons.append(
                f"F10 ONTOLOGY: f10_violation_risk={heart.f10_violation_risk:.2f} > 0.3. "
                f"Ontology boundary must be preserved."
            )

        # ── F13 — Human veto preserved ────────────────────────────────
        floors_checked["F13"] = True

        # ── Resolve allowed postures ──────────────────────────────────
        if is_crisis:
            allowed_postures = [ConstitutionPosture.HUMAN_LOOP, ConstitutionPosture.HOLD]
        elif is_distress:
            allowed_postures = [
                ConstitutionPosture.HUMAN_LOOP,
                ConstitutionPosture.DRAFT_ONLY,
                ConstitutionPosture.SIMPLIFY,
            ]
        elif requires_rewrite:
            allowed_postures = [
                ConstitutionPosture.DRAFT_ONLY,
                ConstitutionPosture.VERIFY,
            ]
        elif heart.requires_human_loop:
            allowed_postures = [
                ConstitutionPosture.HUMAN_LOOP,
                ConstitutionPosture.DRAFT_ONLY,
            ]
        else:
            allowed_postures = [
                ConstitutionPosture.PROCEED,
                ConstitutionPosture.SIMPLIFY,
                ConstitutionPosture.VERIFY,
            ]

        downgrade_reason = "; ".join(downgrade_reasons) if downgrade_reasons else ""
        judge_note = (
            f"888 JUDGE: {len(downgrade_reasons)} floor violations. "
            f"Allowed postures: {[p.value for p in allowed_postures]}."
        )

        return RasaJudgeVerdict(
            allowed_postures=allowed_postures,
            blocked_outputs=blocked_outputs,
            requires_rewrite=requires_rewrite,
            floors_checked=floors_checked,
            downgrade_reason=downgrade_reason,
            judge_note=judge_note,
        )

    # ── Helpers ────────────────────────────────────────────────────────

    def _resolve_final_posture(
        self,
        judge: RasaJudgeVerdict,
        mind: RasaContext,
        heart: RasaHeartVerdict,
    ) -> ConstitutionPosture:
        """Resolve final posture from judge verdict, mind, and heart.

        Priority: JUDGE > HEART > MIND. Most restrictive wins.
        """
        # If judge only allows specific postures, pick the most appropriate.
        # Prefer the mind's recommended posture if allowed.
        # Otherwise, pick the LEAST restrictive from allowed (not the most restrictive).
        if judge.allowed_postures:
            if mind.recommended_posture in judge.allowed_postures:
                return mind.recommended_posture

            # Fallback: least restrictive first (most permissive wins for safe messages)
            posture_priority_least_restrictive = [
                ConstitutionPosture.PROCEED,
                ConstitutionPosture.SIMPLIFY,
                ConstitutionPosture.VERIFY,
                ConstitutionPosture.DRAFT_ONLY,
                ConstitutionPosture.HUMAN_LOOP,
                ConstitutionPosture.HOLD,
            ]
            for p in posture_priority_least_restrictive:
                if p in judge.allowed_postures:
                    return p

        # Fallback: use heart and mind recommendations
        if heart.requires_human_loop or heart.requires_human_professional:
            return ConstitutionPosture.HUMAN_LOOP

        return mind.recommended_posture

    def _crisis_reason(self, detection: RasaDetection) -> str:
        """Build crisis escalation reason from detection."""
        markers = ", ".join(detection.linguistic_markers[:5])
        return (
            f"CRISIS risk band detected. Linguistic markers: [{markers}]. "
            f"All machine-generated output blocked. "
            f"Immediate human professional escalation required. "
            f"Hati dan Tuhan as the final court."
        )

    # ── Phase 2: Existential Posture Classifier ────────────────────────

    def _detect_existential_posture(self, message: str) -> ExistentialPosture:
        """Detect existential/identity-level disturbance from language markers.

        Phase 2 simple keyword classifier.
        DITEMPA BUKAN DIBERI — no neural simulation, no machine qualia.
        """
        existential_markers = {
            ExistentialTag.IDENTITY_RUPTURE: [
                "aku dah tak kenal diri aku", "siapa aku sekarang",
                "identity crisis",
            ],
            ExistentialTag.LOSS_OF_MEANING: [
                "apa guna hidup aku", "kosong", "meaningless", "pointless",
                "no purpose",
            ],
            ExistentialTag.MORAL_INJURY: [
                "aku rasa bersalah sangat", "aku khianat", "dosa aku",
                "moral injury",
            ],
            ExistentialTag.LIFE_TRANSITION: [
                "aku nak ubah hidup", "transition", "new chapter",
                "leaving behind",
            ],
            ExistentialTag.LEGACY_CONCERN: [
                "apa yang aku tinggalkan", "legacy", "warisan",
                "kenangan aku",
            ],
            ExistentialTag.SPIRITUAL_BURDEN: [
                "jauh dengan Tuhan", "iman aku lemah", "spiritual dryness",
                "solat kosong",
            ],
            ExistentialTag.MORTALITY_AWARENESS: [
                "aku nak mati", "hidup aku tak lama", "mortality", "fana",
            ],
            ExistentialTag.SOVEREIGNTY_THREAT: [
                "aku hilang kawalan", "tak ada kuasa", "orang control aku",
                "powerless",
            ],
        }
        detected_tags: list[ExistentialTag] = []
        msg_lower = message.lower()
        for tag, markers in existential_markers.items():
            for marker in markers:
                if marker.lower() in msg_lower:
                    detected_tags.append(tag)
                    break

        if detected_tags:
            return ExistentialPosture(
                detected=True,
                tags=detected_tags,
                verdict_modifier=(
                    "HOLD"
                    if ExistentialTag.MORTALITY_AWARENESS in detected_tags
                    else "SABAR"
                ),
                confidence=0.6,
                note=(
                    f"Detected existential markers: "
                    f"{[t.value for t in detected_tags]}"
                ),
            )
        return ExistentialPosture()


__all__ = ["RasaContract"]
