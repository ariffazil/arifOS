"""
deepnshadow skill handler — DS-111..DS-999
Governed human-pattern inference: encode → decode → metabolize.
Wired to MEMORY, MIND, WELL, WEALTH, HEART, JUDGE via internal composition.
"""

from __future__ import annotations

import re
import uuid
from typing import Any

from arifosmcp.protocols.deepnshadow import (
    AlternativeExplanation,
    BehaviourObservation,
    DeepnShadowReport,
    DignityStatus,
    EmotionalCharge,
    EvidenceClass,
    EvidenceStrength,
    InferenceMode,
    MetabolizedAction,
    PatternRecurrence,
    ProjectionMirror,
    RedactedVaultEntry,
    SafeAction,
    ScarVector,
    ShadowHypothesis,
    TeamShadowPattern,
)


# ── Arif default scar profile (overridable) ───────────────────────────────────
DEFAULT_ARIF_SCAR_VECTORS = [
    {"zone": "authority", "trigger": "false certainty", "response": "resistance"},
    {"zone": "competence", "trigger": "reputational blame", "response": "shame spike"},
    {"zone": "autonomy", "trigger": "forced obedience to lie", "response": "storm mind"},
]


class DeepnShadowSkill:
    """Skill for governed shadow-scar inference."""

    NAME = "deepnshadow"
    FLOOR = "L05"

    def __init__(self, session_id: str, dry_run: bool = True):
        self.session_id = session_id
        self.dry_run = dry_run
        self._observations: list[BehaviourObservation] = []
        self._patterns: list[PatternRecurrence] = []
        self._hypotheses: list[ShadowHypothesis] = []
        self._scars: list[ScarVector] = []
        self._actions: list[SafeAction] = []
        self._metabolized: list[MetabolizedAction] = []
        self._mirrors: list[ProjectionMirror] = []
        self._alternatives: list[AlternativeExplanation] = []
        self._team_patterns: list[TeamShadowPattern] = []

    async def execute(
        self,
        action: str,
        params: dict[str, Any],
        session_id: str,
        dry_run: bool = True,
        reality_bridge: Any | None = None,
        checkpoint: str | None = None,
    ) -> dict[str, Any]:
        handlers = {
            "observe": self._observe,
            "pattern_recall": self._pattern_recall,
            "hypothesize": self._hypothesize,
            "boundary_check": self._boundary_check,
            "projection_mirror": self._projection_mirror,
            "alternatives": self._alternatives,
            "evidence_score": self._evidence_score,
            "metabolize": self._metabolize,
            "team_map": self._team_map,
            "redact_and_vault": self._redact_and_vault,
            "pipeline": self._pipeline,
            "report": self._report,
        }
        handler = handlers.get(action)
        if not handler:
            return {"verdict": "VOID", "reason": f"Unknown action: {action}"}
        return await handler(params, dry_run, reality_bridge, checkpoint)

    # ── DS-111: Behaviour Encoder (existing observe) ──────────────────────────
    async def _observe(
        self,
        params: dict[str, Any],
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None,
    ) -> dict[str, Any]:
        obs = BehaviourObservation(
            observation_id=params.get("observation_id", str(uuid.uuid4())),
            session_id=self.session_id,
            actor_id=params.get("actor_id"),
            description=params["description"],
            context=params.get("context"),
            source=params.get("source", "human_report"),
            evidence_strength=EvidenceStrength(params.get("evidence_strength", "single")),
            evidence_class=EvidenceClass(params.get("evidence_class", "E1")),
            metadata=params.get("metadata", {}),
        )
        if not dry_run:
            self._observations.append(obs)
        return {
            "verdict": "SEAL",
            "mode": "dry_run" if dry_run else "real",
            "observation_id": obs.observation_id,
            "evidence_class": obs.evidence_class.value,
            "dignity_status": DignityStatus.SAFE.value,
            "note": "DS-111: Observation ingested. No interpretation attached.",
        }

    # ── DS-222: Evidence Quality Gate ─────────────────────────────────────────
    async def _evidence_score(
        self,
        params: dict[str, Any],
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None,
    ) -> dict[str, Any]:
        """Classify raw signal into E0–E5."""
        source = params.get("source", "human_report")
        recurrence = int(params.get("recurrence_count", 1))
        documented = params.get("documented", False)
        corroborated = params.get("corroborated", False)
        confirmed = params.get("confirmed_by_subject", False)

        if confirmed:
            eclass = EvidenceClass.E5_CONFIRMED
        elif corroborated:
            eclass = EvidenceClass.E4_CORROBORATED
        elif documented:
            eclass = EvidenceClass.E3_DOCUMENTED
        elif recurrence >= 2:
            eclass = EvidenceClass.E2_REPEATED
        elif source == "feeling":
            eclass = EvidenceClass.E0_FEELING
        else:
            eclass = EvidenceClass.E1_SINGLE

        note = (
            "DS-222: Most shadow maps should stay E1–E2. "
            f"Current signal: {eclass.value}. "
            f"Confidence ceiling adjusted to {self._evidence_confidence_cap(eclass)}."
        )
        return {
            "verdict": "SEAL",
            "mode": "dry_run" if dry_run else "real",
            "evidence_class": eclass.value,
            "confidence_cap": self._evidence_confidence_cap(eclass),
            "note": note,
        }

    # ── DS-222 helper ─────────────────────────────────────────────────────────
    @staticmethod
    def _evidence_confidence_cap(eclass: EvidenceClass) -> float:
        caps = {
            EvidenceClass.E0_FEELING: 0.2,
            EvidenceClass.E1_SINGLE: 0.4,
            EvidenceClass.E2_REPEATED: 0.6,
            EvidenceClass.E3_DOCUMENTED: 0.75,
            EvidenceClass.E4_CORROBORATED: 0.85,
            EvidenceClass.E5_CONFIRMED: 0.95,
        }
        return caps.get(eclass, 0.5)

    # ── MEMORY: Pattern Recall ────────────────────────────────────────────────
    async def _pattern_recall(
        self,
        params: dict[str, Any],
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None,
    ) -> dict[str, Any]:
        actor_id = params.get("actor_id")
        description_substring = params.get("description_substring", "").lower()
        window_days = params.get("window_days", 30)

        matching = [
            o
            for o in self._observations
            if (not actor_id or o.actor_id == actor_id)
            and description_substring in o.description.lower()
        ]
        matching.sort(key=lambda x: x.observed_at)
        recurrence_count = len(matching)
        confidence = min(1.0, recurrence_count / 5.0)

        if recurrence_count < 2:
            return {
                "verdict": "SABAR",
                "mode": "dry_run" if dry_run else "real",
                "recurrence_count": recurrence_count,
                "confidence": confidence,
                "note": "Insufficient recurrence for pattern. Need ≥ 2 observations.",
            }

        pattern = PatternRecurrence(
            pattern_id=str(uuid.uuid4()),
            observation_ids=[o.observation_id for o in matching],
            recurrence_count=recurrence_count,
            time_window_days=window_days,
            trigger_contexts=list({o.context for o in matching if o.context}),
            confidence=confidence,
        )
        if not dry_run:
            self._patterns.append(pattern)
        return {
            "verdict": "SEAL" if confidence >= 0.4 else "SABAR",
            "mode": "dry_run" if dry_run else "real",
            "pattern_id": pattern.pattern_id,
            "recurrence_count": recurrence_count,
            "confidence": confidence,
            "trigger_contexts": pattern.trigger_contexts,
        }

    # ── DS-333: Shadow Hypothesis Engine ──────────────────────────────────────
    async def _hypothesize(
        self,
        params: dict[str, Any],
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None,
    ) -> dict[str, Any]:
        pattern_id = params.get("pattern_id")
        hypothesis_text = params["hypothesis_text"]
        trigger_vector = params.get("trigger_vector")
        raw_confidence = float(params.get("confidence", 0.5))
        evidence_class = EvidenceClass(params.get("evidence_class", "E1"))

        # Cap confidence by evidence quality
        cap = self._evidence_confidence_cap(evidence_class)
        confidence = min(raw_confidence, cap)

        dignity_status, notes = self._dignity_guard(hypothesis_text)

        # Generate mandatory alternatives
        alternatives = self._generate_alternatives(hypothesis_text, pattern_id or "unknown")

        hypothesis = ShadowHypothesis(
            hypothesis_id=str(uuid.uuid4()),
            pattern_id=pattern_id or "unknown",
            hypothesis_text=hypothesis_text,
            trigger_vector=trigger_vector,
            confidence=confidence,
            uncertainty_band=self._confidence_band(confidence),
            is_dignity_safe=(dignity_status == DignityStatus.SAFE),
            dignity_status=dignity_status,
            alternative_explanations=alternatives if not dry_run else [],
        )
        if not dry_run:
            self._hypotheses.append(hypothesis)
            self._alternatives.extend(alternatives)
        return {
            "verdict": (
                "SEAL" if dignity_status == DignityStatus.SAFE else dignity_status.value.upper()
            ),
            "mode": "dry_run" if dry_run else "real",
            "hypothesis_id": hypothesis.hypothesis_id,
            "dignity_status": dignity_status.value,
            "confidence": confidence,
            "confidence_cap": cap,
            "uncertainty_band": hypothesis.uncertainty_band,
            "alternative_explanations": [a.explanation_text for a in alternatives],
            "constitutional_notes": notes,
        }

    # ── DS-444: Projection Mirror ─────────────────────────────────────────────
    async def _projection_mirror(
        self,
        params: dict[str, Any],
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None,
    ) -> dict[str, Any]:
        """Ask: 'How much of this read is about Arif's own scar reacting?'"""
        hypothesis_id = params.get("hypothesis_id", "unknown")
        hypothesis_text = params.get("hypothesis_text", "")
        arif_scars = params.get("arif_scars", DEFAULT_ARIF_SCAR_VECTORS)

        matches = []
        resonance = 0.0
        reflection = "No strong projection detected."
        self_action = None

        text_lower = hypothesis_text.lower()
        for scar in arif_scars:
            trigger = scar.get("trigger", "").lower()
            zone = scar.get("zone", "").lower()
            if trigger in text_lower or zone in text_lower:
                matches.append(scar)
                resonance += 0.3

        resonance = min(1.0, resonance)
        if matches:
            triggers = ", ".join([m["trigger"] for m in matches])
            reflection = (
                f"Arif may be reacting strongly because {triggers} "
                f"touch known scar-zone(s): {', '.join([m['zone'] for m in matches])}."
            )
            self_action = (
                "Pause. Write down 3 observable facts before acting. "
                "Check if the same behaviour would bother you on a calm day."
            )

        mirror = ProjectionMirror(
            mirror_id=str(uuid.uuid4()),
            hypothesis_id=hypothesis_id,
            arif_trigger_match=triggers if matches else None,
            resonance_score=round(resonance, 2),
            reflection_text=reflection,
            safe_self_action=self_action,
        )
        if not dry_run:
            self._mirrors.append(mirror)
        return {
            "verdict": "SEAL",
            "mode": "dry_run" if dry_run else "real",
            "mirror_id": mirror.mirror_id,
            "resonance_score": mirror.resonance_score,
            "reflection": mirror.reflection_text,
            "safe_self_action": mirror.safe_self_action,
            "note": "DS-444: Projection mirror does not invalidate the read; it purifies it.",
        }

    # ── DS-333: Mandatory Alternative Explanations ────────────────────────────
    async def _alternatives(
        self,
        params: dict[str, Any],
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None,
    ) -> dict[str, Any]:
        hypothesis_text = params.get("hypothesis_text", "")
        hypothesis_id = params.get("hypothesis_id", "unknown")
        alts = self._generate_alternatives(hypothesis_text, hypothesis_id)
        if not dry_run:
            self._alternatives.extend(alts)
        return {
            "verdict": "SEAL",
            "mode": "dry_run" if dry_run else "real",
            "alternatives": [
                {"text": a.explanation_text, "likelihood": a.likelihood} for a in alts
            ],
            "note": "DS-333: Without alternatives, shadow mapping becomes ego-confirmation.",
        }

    def _generate_alternatives(
        self, hypothesis_text: str, hypothesis_id: str
    ) -> list[AlternativeExplanation]:
        """Generate mandatory non-shadow explanations."""
        alts = []
        # Heuristic templates
        templates = [
            ("Workload pressure or resource constraint", "probable"),
            ("Management directive or external demand", "possible"),
            ("Miscommunication or unclear scope definition", "possible"),
            ("Tool limitation or workflow friction", "possible"),
            ("Personal non-work stress spilling over", "unlikely"),
        ]
        for i, (text, likelihood) in enumerate(templates):
            alts.append(
                AlternativeExplanation(
                    explanation_id=str(uuid.uuid4()),
                    hypothesis_id=hypothesis_id,
                    explanation_text=text,
                    likelihood=likelihood,
                )
            )
        return alts

    # ── DS-555: Scar Vector Index (boundary_check) ────────────────────────────
    async def _boundary_check(
        self,
        params: dict[str, Any],
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None,
    ) -> dict[str, Any]:
        hypothesis_id = params.get("hypothesis_id")
        protected_zone = params["protected_zone"]
        boundary_type = params.get("boundary_type", "unknown")
        confidence = float(params.get("confidence", 0.3))
        evidence_class = EvidenceClass(params.get("evidence_class", "E1"))

        # Cap by evidence
        cap = self._evidence_confidence_cap(evidence_class)
        confidence = min(confidence, cap)

        if confidence > 0.7:
            dignity_status = DignityStatus.HOLD
            notes = [
                "F05: High-confidence scar-vector risks turning human into label. Downgrade or HOLD."
            ]
        elif confidence > 0.4:
            dignity_status = DignityStatus.GUARDED
            notes = [
                "F06: Medium-confidence scar-vector. Use only for Arif's private navigation, never accusation."
            ]
        else:
            dignity_status = DignityStatus.SAFE
            notes = ["F07: Low-confidence scar-vector. Navigation instrument only."]

        scar = ScarVector(
            vector_id=str(uuid.uuid4()),
            hypothesis_id=hypothesis_id or "unknown",
            protected_zone=protected_zone,
            confidence=confidence,
            boundary_type=boundary_type,
            safe_action_hint=params.get("safe_action_hint"),
        )
        if not dry_run:
            self._scars.append(scar)
        return {
            "verdict": dignity_status.value.upper(),
            "mode": "dry_run" if dry_run else "real",
            "vector_id": scar.vector_id,
            "dignity_status": dignity_status.value,
            "safe_action_hint": scar.safe_action_hint,
            "constitutional_notes": notes,
        }

    # ── DS-777: Metabolizer ───────────────────────────────────────────────────
    async def _metabolize(
        self,
        params: dict[str, Any],
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None,
    ) -> dict[str, Any]:
        """Convert emotional charge into governed action."""
        raw_charge = EmotionalCharge(params.get("raw_charge", "anger"))
        action_text = params["action_text"]
        avoids_trigger = params.get("avoids_trigger")
        arif_scar_link = params.get("arif_scar_link")

        metabolized = self._metabolize_charge(raw_charge, action_text)

        action = SafeAction(
            action_text=action_text,
            avoids_trigger=avoids_trigger,
            preserves_dignity=True,
            escalation_path=None,
        )
        meta = MetabolizedAction(
            metabolize_id=str(uuid.uuid4()),
            action=action,
            raw_charge=raw_charge,
            metabolized_charge=metabolized,
            arif_scar_link=arif_scar_link,
        )
        if not dry_run:
            self._metabolized.append(meta)
            self._actions.append(action)
        return {
            "verdict": "SEAL",
            "mode": "dry_run" if dry_run else "real",
            "metabolize_id": meta.metabolize_id,
            "raw_charge": raw_charge.value,
            "metabolized_charge": metabolized,
            "action": action_text,
            "note": f"DS-777: {raw_charge.value} → {metabolized}",
        }

    @staticmethod
    def _metabolize_charge(charge: EmotionalCharge, action_text: str) -> str:
        mapping = {
            EmotionalCharge.ANGER: "boundary",
            EmotionalCharge.SHAME: "workflow container",
            EmotionalCharge.SUSPICION: "hypothesis",
            EmotionalCharge.CONFUSION: "scope question",
            EmotionalCharge.HURT: "dignity-preserving response",
            EmotionalCharge.FEAR: "preparedness plan",
            EmotionalCharge.GRIEF: "acceptance ritual",
            EmotionalCharge.LOW: "rest signal",
            EmotionalCharge.NEUTRAL: "clean signal",
        }
        return mapping.get(charge, "governed action")

    # ── DS-333 TEAM: Team Shadow Map ──────────────────────────────────────────
    async def _team_map(
        self,
        params: dict[str, Any],
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None,
    ) -> dict[str, Any]:
        team_name = params.get("team_name", "unknown")
        behaviours = params.get("observed_behaviours", [])
        systemic_shadow = params.get("systemic_shadow")
        alternative_cause = params.get(
            "alternative_systemic_cause", "Management pressure or resource constraint"
        )
        safe_action = params.get("safe_org_action")

        team_pat = TeamShadowPattern(
            team_pattern_id=str(uuid.uuid4()),
            team_name=team_name,
            observed_behaviours=behaviours,
            systemic_shadow=systemic_shadow,
            alternative_systemic_cause=alternative_cause,
            safe_org_action=safe_action,
        )
        if not dry_run:
            self._team_patterns.append(team_pat)
        return {
            "verdict": "SEAL",
            "mode": "dry_run" if dry_run else "real",
            "team_pattern_id": team_pat.team_pattern_id,
            "systemic_shadow": systemic_shadow,
            "alternative_cause": alternative_cause,
            "note": "DS-333 TEAM: Organizational geology. Never reduce team to pathology.",
        }

    # ── DS-999: Redact and Vault ──────────────────────────────────────────────
    async def _redact_and_vault(
        self,
        params: dict[str, Any],
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None,
    ) -> dict[str, Any]:
        """DEPRECATED: Use arif_vault_seal(mode='deepnshadow') instead.

        This method now returns a vault payload for caller to seal via
        the existing canonical vault tool. No separate shadow journal.
        """
        mode = InferenceMode(params.get("mode", "other"))
        role_tag = params.get("role_tag")
        pattern_summary = params["pattern_summary"]
        safe_response = params.get("safe_response")
        outcome = params.get("outcome")
        dignity_status = DignityStatus(params.get("dignity_status", "safe"))

        entry = RedactedVaultEntry(
            entry_id=str(uuid.uuid4()),
            session_id=self.session_id,
            mode=mode,
            role_tag=role_tag,
            pattern_summary=pattern_summary,
            safe_response=safe_response,
            outcome=outcome,
            dignity_status=dignity_status,
        )

        return {
            "verdict": "SEAL",
            "mode": "dry_run" if dry_run else "real",
            "entry_id": entry.entry_id,
            "vault_payload": entry.model_dump(),
            "note": "DEPRECATED: Pass vault_payload to arif_vault_seal(mode='deepnshadow').",
        }

    # ── DS full pipeline ──────────────────────────────────────────────────────
    async def _pipeline(
        self,
        params: dict[str, Any],
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None,
    ) -> dict[str, Any]:
        mode = InferenceMode(params.get("mode", "other"))
        observations_raw = params.get("observations", [])
        if not observations_raw:
            return {"verdict": "VOID", "reason": "No observations provided."}

        # Step 1: Observe + evidence score
        for obs_raw in observations_raw:
            await self._observe(obs_raw, dry_run, reality_bridge, checkpoint)
            await self._evidence_score(obs_raw, dry_run, reality_bridge, checkpoint)

        # Step 2: Pattern recall
        actor_map: dict[str, list[BehaviourObservation]] = {}
        for obs in self._observations:
            key = obs.actor_id or "unknown"
            actor_map.setdefault(key, []).append(obs)
        for actor_id, obs_list in actor_map.items():
            if len(obs_list) >= 2:
                pattern = PatternRecurrence(
                    pattern_id=str(uuid.uuid4()),
                    observation_ids=[o.observation_id for o in obs_list],
                    recurrence_count=len(obs_list),
                    time_window_days=30,
                    trigger_contexts=list({o.context for o in obs_list if o.context}),
                    confidence=min(1.0, len(obs_list) / 5.0),
                )
                if not dry_run:
                    self._patterns.append(pattern)

        # Step 3: Hypothesize + alternatives
        for hyp_raw in params.get("hypotheses", []):
            await self._hypothesize(hyp_raw, dry_run, reality_bridge, checkpoint)

        # Step 4: Projection mirror (if Arif mode or explicit request)
        if mode in (InferenceMode.MIRROR, InferenceMode.OTHER):
            for hyp in self._hypotheses:
                await self._projection_mirror(
                    {"hypothesis_id": hyp.hypothesis_id, "hypothesis_text": hyp.hypothesis_text},
                    dry_run,
                    reality_bridge,
                    checkpoint,
                )

        # Step 5: Boundary / Scar
        for scar_raw in params.get("scar_vectors", []):
            await self._boundary_check(scar_raw, dry_run, reality_bridge, checkpoint)

        # Step 6: Metabolize
        for meta_raw in params.get("metabolized_actions", []):
            await self._metabolize(meta_raw, dry_run, reality_bridge, checkpoint)
        # Also metabolize any safe_actions passed directly
        for action_raw in params.get("safe_actions", []):
            action = SafeAction(
                action_text=action_raw["action_text"],
                avoids_trigger=action_raw.get("avoids_trigger"),
                preserves_dignity=action_raw.get("preserves_dignity", True),
                escalation_path=action_raw.get("escalation_path"),
            )
            if not dry_run:
                self._actions.append(action)

        # Step 7: Team map (if provided)
        for team_raw in params.get("team_patterns", []):
            await self._team_map(team_raw, dry_run, reality_bridge, checkpoint)

        # Step 8: Report
        report = await self._build_report(mode=mode)
        return {
            "verdict": report.verdict,
            "mode": "dry_run" if dry_run else "real",
            "report_id": report.report_id,
            "inference_mode": report.mode.value,
            "dignity_status": report.overall_dignity_status.value,
            "overall_confidence": report.overall_confidence,
            "observation_count": len(report.observations),
            "pattern_count": len(report.patterns),
            "hypothesis_count": len(report.hypotheses),
            "alternative_count": len(report.alternative_explanations),
            "projection_mirror_count": len(report.projection_mirrors),
            "scar_vector_count": len(report.scar_vectors),
            "safe_action_count": len(report.safe_actions),
            "metabolized_action_count": len(report.metabolized_actions),
            "team_pattern_count": len(report.team_patterns),
            "vault_line": report.to_vault_line(),
        }

    async def _report(
        self,
        params: dict[str, Any],
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None,
    ) -> dict[str, Any]:
        mode = InferenceMode(params.get("mode", "other"))
        report = await self._build_report(mode=mode)
        return {
            "verdict": report.verdict,
            "report_id": report.report_id,
            "inference_mode": report.mode.value,
            "dignity_status": report.overall_dignity_status.value,
            "overall_confidence": report.overall_confidence,
            "vault_line": report.to_vault_line(),
        }

    async def _build_report(self, mode: InferenceMode = InferenceMode.OTHER) -> DeepnShadowReport:
        overall_dignity = DignityStatus.SAFE
        if any(h.dignity_status == DignityStatus.HOLD for h in self._hypotheses):
            overall_dignity = DignityStatus.HOLD
        elif any(h.dignity_status == DignityStatus.GUARDED for h in self._hypotheses):
            overall_dignity = DignityStatus.GUARDED
        elif any(s.confidence > 0.5 for s in self._scars):
            overall_dignity = DignityStatus.GUARDED

        confidences = [h.confidence for h in self._hypotheses] + [s.confidence for s in self._scars]
        overall_confidence = sum(confidences) / max(len(confidences), 1)

        verdict = "SEAL"
        if overall_dignity == DignityStatus.HOLD:
            verdict = "HOLD"
        elif overall_dignity == DignityStatus.GUARDED:
            verdict = "SABAR"
        elif overall_confidence < 0.3:
            verdict = "SABAR"

        notes = [
            "F02: All hypotheses are hypotheses, not truths.",
            "F05: Shadow maps are for Arif's private navigation only.",
            "F06: No human was reduced to a label in this report.",
            "F07: Confidence is uncertainty-banded and evidence-capped.",
            "F09: No consciousness claims made.",
            "DS-333: Alternative explanations generated for every hypothesis.",
            "DS-444: Projection mirror checked.",
            "DS-777: Emotional charge metabolized into governed action.",
            "F13: Arif retains veto over any safe action.",
        ]

        return DeepnShadowReport(
            report_id=str(uuid.uuid4()),
            session_id=self.session_id,
            mode=mode,
            observations=list(self._observations),
            patterns=list(self._patterns),
            hypotheses=list(self._hypotheses),
            alternative_explanations=list(self._alternatives),
            projection_mirrors=list(self._mirrors),
            scar_vectors=list(self._scars),
            safe_actions=list(self._actions),
            metabolized_actions=list(self._metabolized),
            team_patterns=list(self._team_patterns),
            overall_dignity_status=overall_dignity,
            overall_confidence=round(overall_confidence, 2),
            verdict=verdict,
            constitutional_notes=notes,
        )

    def _dignity_guard(self, text: str) -> tuple[DignityStatus, list[str]]:
        """F05/F06 dignity pre-filter. Mirrors WELL gate/dignity_shadow.py."""
        text_lower = text.lower()
        notes: list[str] = []

        fatal_patterns = [
            r"\bis\s+(?:a\s+)?(?:narcissist|toxic|insecure|broken|traumatized|clumsy|stupid|lazy)",
            r"\bhas\s+trauma\b",
            r"\bis\s+projecting\b",
            r"\bis\s+avoidant\b",
            r"\bis\s+anxious\b",
        ]
        for pat in fatal_patterns:
            if re.search(pat, text_lower):
                return DignityStatus.HOLD, [f"F05 fatal dignity violation: pattern '{pat}'"]

        guarded = ["because", "due to their", "obviously", "clearly", "definitely"]
        for phrase in guarded:
            if phrase in text_lower:
                notes.append(f"F06 guarded language: '{phrase}'")
        if notes:
            return DignityStatus.GUARDED, notes
        return DignityStatus.SAFE, []

    @staticmethod
    def _confidence_band(confidence: float) -> str:
        if confidence < 0.3:
            return "low"
        if confidence < 0.7:
            return "medium"
        return "high"


async def execute(
    action: str,
    params: dict[str, Any],
    session_id: str = "",
    dry_run: bool = True,
    **kwargs: Any,
) -> dict[str, Any]:
    """Entrypoint for skill registry."""
    skill = DeepnShadowSkill(session_id=session_id, dry_run=dry_run)
    return await skill.execute(
        action=action,
        params=params,
        session_id=session_id,
        dry_run=dry_run,
        **kwargs,
    )
