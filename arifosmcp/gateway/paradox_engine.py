"""
Paradox Engine — arifOS Constitutional Perception Pipeline
═════════════════════════════════════════════════════════════

v0.2.0 — Heuristic tension detector with Pydantic v2 belief graph output.

Pipeline:
  ARTICLE TEXT IN
    → frame geometry extracted (actors, claims, quoted/unquoted, passive/active)
    → tension classifier (PROMISE_VS_OUTCOME, PASSIVE_OBSTACLE, SLIP_PHRASE, etc.)
    → severity scoring (shadow_score, meaning_leak_intensity, maruah_impact)
    → candidate ParadoxTensionNode emitted
    → auto-tag governance trigger (PUBLIC_INTEREST_HIGH / INSTITUTIONAL_OPACITY_DETECTED)
    → seal receipt into Merkle log
    → HOLD (NEVER auto-escalate to irreversible action)

CONSTITUTIONAL CONSTRAINT:
  - NO mutation to external state
  - NO public disclosure
  - NO auto-escalation to irreversible action
  - Output = candidate receipts only, menunggu 888 review

Author: omega-forge-agent
Forged: 2026-06-13 05:30 MYT
Authority: F13 SOVEREIGN (888)
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from typing import Any

from .merkle_log import MerkleTree
from .tension_node import (
    ActivityNode,
    ActorNode,
    ActorRole,
    BeliefGraph,
    ClaimNode,
    ClaimType,
    EpistemicTag,
    EvidenceNode,
    GovernanceBinding,
    ParadoxTensionNode,
    Provenance,
    ReceiptNode,
    Severity,
    TensionClass,
    TensionScores,
    TensionStatus,
)

# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS — Bahasa Melayu linguistic detectors
# ═══════════════════════════════════════════════════════════════════════════

# Passive voice markers in BM (di- prefix verbs = disembunyikan agency)
PASSIVE_MARKERS_BM: list[str] = [
    "didedahkan", "diteliti", "diserahkan", "dilaporkan", "dinyatakan",
    "diputuskan", "ditangguhkan", "disekat", "diberitahu", "dimaklumkan",
    "dijelaskan", "dikongsi", "diproses", "diluluskan", "disemak",
    "ditahan", "dikemukakan", "diadakan", "dibuat", "dilakukan",
    "diperlu", "dipatuhi", "dipertimbangkan", "disiasat", "dikenal pasti",
    "ditetapkan", "diselesaikan", "dibentangkan", "diterima",
]

# Hedging/qualification language — signals that soften or evade commitment
HEDGING_MARKERS_BM: list[str] = [
    "perlu", "mungkin", "tertakluk", "terutama", "bagaimanapun",
    "walau bagaimanapun", "namun", "tetapi", "sebaik", "sekiranya",
    "jika", "akan", "belum", "masih", "dalam proses", "sedang",
    "terpulang", "bergantung", "tertakluk kepada", "mengikut",
    "selaras", "mempertimbangkan", "implikasi", "aspek",
    "beberapa", "antara", "pihak terlibat", "pihak berkaitan",
]

# Promise/commitment language — signals of intent that create expectation
PROMISE_MARKERS_BM: list[str] = [
    "bersedia", "akan mendedahkan", "akan dikongsi", "komited",
    "janji", "dijamin", "pasti", "insya-Allah", "secepat mungkin",
    "dalam masa terdekat", "sebaik selesai", "sedang diusahakan",
]

# Deadline/void markers — absence or vagueness of timeline
DEADLINE_VOID_MARKERS_BM: list[str] = [
    "sebaik selesai", "apabila siap", "dalam masa terdekat",
    "sedang diteliti", "masih menunggu", "belum ada tarikh",
    "tiada tempoh", "tertakluk kepada", "bergantung kepada",
]

# Jurisdiction/choke markers
JURISDICTION_MARKERS_BM: list[str] = [
    "bidang kuasa", "perundangan", "persekutuan", "negeri",
    "agensi persekutuan", "kerajaan persekutuan", "kerajaan negeri",
    "mahkamah", "akta", "undang-undang", "perlembagaan",
]

# Named entity patterns (proper nouns that indicate specific actors)
NAMED_ENTITY_PATTERNS: list[str] = [
    r"(?:seperti|termasuk|antaranya)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
    r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})",  # multi-word proper nouns
]


# ═══════════════════════════════════════════════════════════════════════════
# FRAME EXTRACTOR
# ═══════════════════════════════════════════════════════════════════════════

class FrameExtractor:
    """Extract actors, claims, and framing signals from BM article text."""

    def __init__(self, text: str, meta: dict[str, str] | None = None):
        self.text = text
        self.meta = meta or {}
        self.sentences = self._split_sentences(text)

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        """Split BM text into sentences."""
        # BM sentence boundaries
        parts = re.split(r'(?<=[.!?])\s+', text)
        return [p.strip() for p in parts if len(p.strip()) > 20]

    def detect_passive_voice_ratio(self) -> float:
        """Ratio of sentences containing passive di- verbs."""
        if not self.sentences:
            return 0.0
        passive_count = sum(
            1 for s in self.sentences
            if any(m in s.lower() for m in PASSIVE_MARKERS_BM)
        )
        return passive_count / len(self.sentences)

    def detect_hedging_ratio(self) -> float:
        """Ratio of hedging markers per sentence."""
        if not self.sentences:
            return 0.0
        total_hedging = sum(
            sum(1 for m in HEDGING_MARKERS_BM if m in s.lower())
            for s in self.sentences
        )
        return min(total_hedging / (len(self.sentences) * 3), 1.0)

    def detect_quote_asymmetry(self) -> dict[str, int]:
        """Count direct vs indirect quotes."""
        direct_markers = ["katanya", "ujarnya", "jelasnya", "tambahnya",
                          "katanya lagi", "ujar", "kata", "jelas"]
        indirect_markers = ["menurut", "melaporkan", "memetik", "berkata"]

        direct_count = sum(1 for m in direct_markers if m in self.text.lower())
        indirect_count = sum(1 for m in indirect_markers if m in self.text.lower())
        return {"direct": direct_count, "indirect": indirect_count}

    def detect_promise_markers(self) -> list[str]:
        """Extract sentences containing promise/commitment language."""
        return [
            s for s in self.sentences
            if any(m in s.lower() for m in PROMISE_MARKERS_BM)
        ]

    def detect_deadline_void(self) -> bool:
        """Check if article contains deadline-void patterns."""
        return any(
            m in self.text.lower() for m in DEADLINE_VOID_MARKERS_BM
        ) and not re.search(r'(?:pada|sebelum|menjelang)\s+\d{1,2}\s+\w+\s+\d{4}', self.text)

    def detect_jurisdiction_language(self) -> float:
        """Ratio of jurisdiction-related terms."""
        count = sum(
            1 for m in JURISDICTION_MARKERS_BM if m in self.text.lower()
        )
        return min(count / len(JURISDICTION_MARKERS_BM), 1.0)

    def extract_named_entities(self) -> list[str]:
        """Extract named entities (proper nouns) from text."""
        entities: list[str] = []
        for pattern in NAMED_ENTITY_PATTERNS:
            matches = re.findall(pattern, self.text)
            for m in matches:
                entity = m if isinstance(m, str) else m[0]
                entity = entity.strip()
                # Filter out generic terms
                if len(entity) > 4 and entity.lower() not in {
                    "yang", "dalam", "untuk", "pada", "dengan", "akan",
                    "telah", "bagi", "dari", "oleh", "ini", "itu",
                }:
                    entities.append(entity)
        return list(dict.fromkeys(entities))  # deduplicate

    def extract_actors(self) -> list[dict[str, Any]]:
        """Heuristic actor extraction from BM news article."""
        actors: list[dict[str, Any]] = []

        # Known actor patterns for MY governance context
        known_patterns: list[tuple[str, str, ActorRole]] = [
            ("Amirudin|Amiruddin|MB Selangor|Menteri Besar Selangor",
             "actor_mb_selangor", ActorRole.GATEKEEPER),
            ("Petronas|Petronas Gas|PGB", "actor_petronas",
             ActorRole.OPERATOR),
            ("kerajaan persekutuan|kerajaan Persekutuan|Persekutuan",
             "actor_kerajaan_persekutuan", ActorRole.GATEKEEPER),
            ("kerajaan negeri|kerajaan Negeri", "actor_kerajaan_negeri",
             ActorRole.INSTITUTION),
            ("mahkamah|Mahkamah Tinggi|Mahkamah", "actor_mahkamah",
             ActorRole.LEGAL),
            ("penduduk|mangsa|penghuni|komuniti", "actor_residents",
             ActorRole.VICTIM),
            ("jawatankuasa|Jawatankuasa Bebas|AGC|Peguam Negara",
             "actor_agc", ActorRole.LEGAL),
            ("wartawan|pemberita|media|Kosmo|BH|Utusan|Malaysiakini|FMT|The Edge",
             "actor_media", ActorRole.MEDIA),
        ]

        for pattern, actor_id, role in known_patterns:
            if re.search(pattern, self.text, re.IGNORECASE):
                # Count mentions
                mentions = len(re.findall(pattern, self.text, re.IGNORECASE))
                # Detect if directly quoted
                quoted = bool(re.search(
                    rf'(?:katanya|ujarnya|jelasnya|katanya lagi|kata|jelas|ujar).*?(?:{pattern})',
                    self.text, re.IGNORECASE
                )) or bool(re.search(
                    rf'(?:{pattern}).*?(?:berkata|menegaskan|menjelaskan|memaklumkan)',
                    self.text, re.IGNORECASE
                ))

                actors.append({
                    "actor_id": actor_id,
                    "name": pattern.split("|")[0].replace("\\", ""),
                    "role": role,
                    "mentions": mentions,
                    "quoted": quoted,
                    "visibility": min(mentions / 10, 1.0),
                    "power": 0.5,  # default, to be refined
                })

        return actors

    def extract_claims(self, actors: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Heuristic claim extraction from sentences."""
        claims: list[dict[str, Any]] = []
        claim_idx = 0

        for sent in self.sentences:
            claim_idx += 1

            # Determine claim type
            if any(m in sent.lower() for m in PROMISE_MARKERS_BM):
                claim_type = ClaimType.PROMISE
            elif any(m in sent.lower() for m in ["tiada", "tidak", "bukan", "nafi"]):
                claim_type = ClaimType.DENIAL
            elif any(m in sent.lower() for m in ["sebab", "kerana", "disebabkan", "faktor"]):
                claim_type = ClaimType.EXPLANATION
            elif any(m in sent.lower() for m in ["didakwa", "dakwa", "tuduh"]):
                claim_type = ClaimType.ACCUSATION
            elif any(m in sent.lower() for m in ["lapor", "siasat", "dapati", "semak"]):
                claim_type = ClaimType.FINDING
            elif any(m in sent.lower() for m in ["perlu", "proses", "undang", "ikut"]):
                claim_type = ClaimType.MITIGATION
            else:
                claim_type = ClaimType.FINDING

            # Find likely speaker
            speaker = "unknown"
            for a in actors:
                if a["name"].lower() in sent.lower():
                    speaker = a["actor_id"]
                    break

            # Score hedging
            hedging_score = sum(
                0.15 for m in HEDGING_MARKERS_BM if m in sent.lower()
            )
            hedging_score = min(hedging_score, 1.0)

            # Epistemic tag
            if any(w in sent.lower() for w in ["pasti", "disahkan", "fakta"]):
                epistemic = EpistemicTag.FACT
            elif any(w in sent.lower() for w in ["mungkin", "dipercayai", "dijangka"]):
                epistemic = EpistemicTag.PLAUSIBLE
            else:
                epistemic = EpistemicTag.CLAIM

            claims.append({
                "claim_id": f"claim_extracted_{claim_idx:03d}",
                "text": sent[:200],
                "claim_type": claim_type,
                "speaker": speaker,
                "epistemic_tag": epistemic,
                "hedging_score": hedging_score,
                "verifiable": epistemic == EpistemicTag.FACT,
            })

        return claims


# ═══════════════════════════════════════════════════════════════════════════
# TENSION CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════════

class TensionClassifier:
    """Classify detected tensions from frame analysis signals."""

    def __init__(self, extractor: FrameExtractor):
        self.ext = extractor
        self.text = extractor.text

    def detect_all(self) -> list[dict[str, Any]]:
        """Run all tension detectors and return candidate tensions."""
        tensions: list[dict[str, Any]] = []

        # T1: PROMISE_VS_OUTCOME — promises made but outcome contradicts
        promise_sents = self.ext.detect_promise_markers()
        hedging_ratio = self.ext.detect_hedging_ratio()
        if promise_sents and hedging_ratio > 0.3:
            tensions.append({
                "tension_id": "auto-t1",
                "title": "Promise vs Outcome Discrepancy",
                "tension_class": TensionClass.INSTITUTIONAL_PARADOX,
                "summary": f"{len(promise_sents)} promise/commitment sentences detected "
                           f"with hedging ratio {hedging_ratio:.2f}. "
                           f"Declarative intent may conflict with actual outcome.",
                "severity": Severity.HIGH if hedging_ratio > 0.5 else Severity.MEDIUM,
                "claim_refs": [],
                "scores": self._compute_scores(0.80, 0.75, 0.85, hedging_ratio),
            })

        # T2: PASSIVE_OBSTACLE — passive voice masks agency
        passive_ratio = self.ext.detect_passive_voice_ratio()
        if passive_ratio > 0.4:
            tensions.append({
                "tension_id": "auto-t2",
                "title": "Passive Obstacle Construction",
                "tension_class": TensionClass.MEANING_LEAK,
                "summary": f"Passive voice ratio {passive_ratio:.2f}. "
                           f"Agency is grammatically obscured — who acts is hidden.",
                "severity": Severity.MEDIUM,
                "claim_refs": [],
                "scores": self._compute_scores(0.75, 0.70, 0.75, passive_ratio),
            })

        # T3: SLIP_PHRASE — named entity appears under hedged/qualified context
        named_entities = self.ext.extract_named_entities()
        if named_entities and hedging_ratio > 0.25:
            tensions.append({
                "tension_id": "auto-t3",
                "title": "Named Entity Under Hedge",
                "tension_class": TensionClass.MEANING_LEAK,
                "summary": f"Named entities ({', '.join(named_entities[:3])}) "
                           f"appear under hedging/qualification language (ratio {hedging_ratio:.2f}). "
                           f"Specific actors named within otherwise generalized/hedged frame.",
                "severity": Severity.CRITICAL if any(
                    e.lower() in ["petronas", "petronas gas", "tnb", "khazanah",
                                   "kwap", "epf", "pnb", "ltat"]
                    for e in named_entities
                ) else Severity.HIGH,
                "claim_refs": [],
                "scores": self._compute_scores(0.95, 0.90, 0.85, hedging_ratio),
            })

        # T4: VOICE_ASYMMETRY — quote asymmetry between powerful and powerless
        quote_asym = self.ext.detect_quote_asymmetry()
        if quote_asym["direct"] > 3 and quote_asym["indirect"] < quote_asym["direct"]:
            tensions.append({
                "tension_id": "auto-t4",
                "title": "Voice Asymmetry Detected",
                "tension_class": TensionClass.PUBLIC_PRIVATE_DIVERGENCE,
                "summary": f"Direct quotes: {quote_asym['direct']}, "
                           f"indirect: {quote_asym['indirect']}. "
                           f"Narrative dominated by institutional speakers; "
                           f"affected parties may lack direct voice.",
                "severity": Severity.MEDIUM,
                "claim_refs": [],
                "scores": self._compute_scores(0.70, 0.65, 0.55, 0.72),
            })

        # T5: EXPLICIT_VS_IMPLICIT — article presents two conflicting narratives
        if passive_ratio > 0.3 and hedging_ratio > 0.25:
            tensions.append({
                "tension_id": "auto-t5",
                "title": "Explicit vs Implicit Narrative Conflict",
                "tension_class": TensionClass.HARD_CONTRADICTION,
                "summary": "Article structure suggests competing narratives: "
                           "one explicit (official/attributed), one implicit (between lines). "
                           "Passive voice and hedging language together create cognitive dissonance.",
                "severity": Severity.HIGH,
                "claim_refs": [],
                "scores": self._compute_scores(0.80, 0.72, 0.90, max(passive_ratio, hedging_ratio)),
            })

        # T6: DEADLINE_VOID — commitment without timeline
        if self.ext.detect_deadline_void() and promise_sents:
            tensions.append({
                "tension_id": "auto-t6",
                "title": "Deadline Void — Commitment Without Timeline",
                "tension_class": TensionClass.TIMELINE_INCOHERENCE,
                "summary": "Promise/commitment language present but no specific "
                           "deadline or completion date. Indefinite review dressed as due diligence.",
                "severity": Severity.HIGH,
                "claim_refs": [],
                "scores": self._compute_scores(0.90, 0.85, 0.92, 0.82),
            })

        # T7: JURISDICTION_TRAP — responsibility split across jurisdictions
        jurisdiction_ratio = self.ext.detect_jurisdiction_language()
        if jurisdiction_ratio > 0.3:
            tensions.append({
                "tension_id": "auto-t7",
                "title": "Jurisdiction Trap — Split Authority",
                "tension_class": TensionClass.ROLE_RESPONSIBILITY_GAP,
                "summary": f"Jurisdiction/legal language density: {jurisdiction_ratio:.2f}. "
                           f"Responsibility appears fragmented across multiple authorities — "
                           f"no single actor holds both accountability and capability.",
                "severity": Severity.MEDIUM,
                "claim_refs": [],
                "scores": self._compute_scores(0.75, 0.70, 0.65, jurisdiction_ratio),
            })

        return tensions

    @staticmethod
    def _compute_scores(
        confidence: float, credibility: float, coherence_strain: float,
        shadow_driver: float,
    ) -> dict[str, float]:
        """Compute TensionScores fields from classifier outputs."""
        shadow_score = min(0.50 + shadow_driver * 0.50, 1.0)
        meaning_leak_intensity = min(shadow_driver * 1.2, 1.0)
        public_interest = min(0.50 + shadow_driver * 0.60, 1.0)
        harm_potential = min(shadow_driver * 1.1, 1.0)
        maruah_impact = -(shadow_driver * 0.90)  # negative = dignity loss

        return {
            "confidence": round(confidence, 2),
            "credibility": round(credibility, 2),
            "coherence_strain": round(coherence_strain, 2),
            "public_interest": round(public_interest, 2),
            "harm_potential": round(harm_potential, 2),
            "shadow_score": round(shadow_score, 2),
            "meaning_leak_intensity": round(meaning_leak_intensity, 2),
            "maruah_impact": round(maruah_impact, 2),
        }

    @staticmethod
    def required_action(tension_class: TensionClass, severity: Severity) -> str:
        """Map tension class + severity to governance action code."""
        if severity == Severity.CRITICAL:
            return "activate_ACCIDENT_REPORT_LITIGATION_HOLD"
        if tension_class == TensionClass.MEANING_LEAK:
            return "audit_meaning_leak"
        if tension_class == TensionClass.TIMELINE_INCOHERENCE:
            return "escalate_deadline_breach"
        if tension_class == TensionClass.ROLE_RESPONSIBILITY_GAP:
            return "audit_jurisdiction_choke"
        if tension_class == TensionClass.HARD_CONTRADICTION:
            return "escalate_to_contradiction_audit"
        if tension_class == TensionClass.INSTITUTIONAL_PARADOX:
            return "escalate_review_timeout"
        return "888_HOLD"


# ═══════════════════════════════════════════════════════════════════════════
# PARADOX ENGINE (main)
# ═══════════════════════════════════════════════════════════════════════════

class ParadoxEngine:
    """Constitutional perception engine.

    Ingests article text → produces auditable BeliefGraph with:
    - Actors, claims, evidence
    - Detected tensions with severity scores
    - Candidate receipts (NEVER auto-escalated)
    - Merkle-sealed leaves for VAULT999

    CONSTRAINT: Output is CANDIDATE only. All governance actions
    require 888 review. This engine perceives; it does not execute.
    """

    def __init__(self, merkle: MerkleTree | None = None):
        self.merkle = merkle or MerkleTree()
        self.engine_version = "0.2.0"
        self.engine_hash = hashlib.sha256(
            self.engine_version.encode()
        ).hexdigest()[:12]

    def ingest(
        self,
        article_text: str,
        metadata: dict[str, str] | None = None,
        article_id: str | None = None,
    ) -> BeliefGraph:
        """Full ingestion pipeline: text → BeliefGraph.

        Args:
            article_text: Raw article text (BM or English).
            metadata: Optional dict with keys: url, title, date, reporter, publication.
            article_id: Optional graph ID. Auto-generated if None.

        Returns:
            BeliefGraph with all extracted nodes, tensions, and receipts.
        """
        meta = metadata or {}
        ts = datetime.now(UTC).isoformat()

        if article_id is None:
            article_id = f"bg-{hashlib.sha256(article_text.encode()).hexdigest()[:12]}"

        graph = BeliefGraph(
            graph_id=article_id,
            title=meta.get("title", "Untitled Analysis"),
        )

        # ── Step 1: Extract frame geometry ──
        extractor = FrameExtractor(article_text, meta)

        # Actors
        raw_actors = extractor.extract_actors()
        for ra in raw_actors:
            graph.actors.append(ActorNode(
                actor_id=ra["actor_id"],
                name=ra["name"],
                role=ra["role"],
                entity_type=self._entity_type_for(ra["actor_id"]),
                jurisdiction=self._jurisdiction_for(ra["actor_id"]),
                power_score=ra["power"],
                visibility_score=ra["visibility"],
                accountability_score=0.5,
            ))

        # Evidence
        evidence_node = EvidenceNode(
            evidence_id=f"ev_{article_id}",
            evidence_type="news_article",
            description=meta.get("title", "Article under constitutional analysis"),
            source_uri=meta.get("url", ""),
            hash=f"sha256:{hashlib.sha256(article_text.encode()).hexdigest()[:16]}",
            reliability=0.85,
        )
        graph.evidence.append(evidence_node)

        # Claims
        raw_claims = extractor.extract_claims(raw_actors)
        for rc in raw_claims[:20]:  # cap at 20 claims per article
            c = ClaimNode(
                claim_id=rc["claim_id"],
                text=rc["text"],
                claim_type=rc["claim_type"],
                speaker=rc["speaker"],
                epistemic_tag=rc["epistemic_tag"],
                source_uri=f"ev_{article_id}",
                hedging_score=rc["hedging_score"],
                verifiable=rc["verifiable"],
            )
            graph.claims.append(c)

        # ── Step 2: Classify tensions ──
        classifier = TensionClassifier(extractor)
        raw_tensions = classifier.detect_all()

        for i, rt in enumerate(raw_tensions, 1):
            # Map claim refs to actual claim IDs
            claim_refs = rt.get("claim_refs", []) or [
                c.claim_id for c in graph.claims[:2]  # default: first 2 claims
            ]

            # Actor refs
            actor_refs = [a.actor_id for a in graph.actors[:4]]

            # Scores object
            sc = rt["scores"]
            scores = TensionScores(
                confidence=sc["confidence"],
                credibility=sc["credibility"],
                coherence_strain=sc["coherence_strain"],
                public_interest=sc["public_interest"],
                harm_potential=sc["harm_potential"],
                shadow_score=sc["shadow_score"],
                meaning_leak_intensity=sc["meaning_leak_intensity"],
                maruah_impact=sc["maruah_impact"],
            )

            # Required action
            action = TensionClassifier.required_action(
                rt["tension_class"], rt["severity"]
            )

            tension = ParadoxTensionNode(
                tension_id=rt["tension_id"],
                title=rt["title"],
                status=TensionStatus.OPEN,
                severity=rt["severity"],
                tension_class=rt["tension_class"],
                summary=rt["summary"],
                incident_refs=[],
                subject_refs=[],
                claim_refs=claim_refs,
                actor_refs=actor_refs,
                evidence_refs=[f"ev_{article_id}"],
                provenance=Provenance(
                    generated_by_activity=f"activity_ingest_{article_id}",
                    generated_by_agent=f"paradox_engine_v{self.engine_version}",
                ),
                scores=scores,
                relations={
                    "supports": [], "attacks": [], "refines": [],
                    "undercuts": [], "depends_on": [], "triggered_by": [],
                    "resolved_by": [], "masked_by": [], "witnessed_by": [],
                },
                governance=GovernanceBinding(
                    floor_bindings=["F1", "F2", "F5", "F13"],
                    required_action=action,
                    hold_code="888_REVIEW_REQUIRED",
                    escalate_after_s=0,  # DO NOT auto-escalate
                    epistemic_tag=EpistemicTag.PLAUSIBLE,
                    requires_888_hold=(
                        rt["severity"] in {Severity.CRITICAL, Severity.HIGH}
                    ),
                ),
            )
            graph.tensions.append(tension)

            # ── Step 3: Generate receipt (CANDIDATE ONLY) ──
            receipt = ReceiptNode(
                receipt_id=f"rcpt_{article_id}_t{i}_detect_v{self.engine_version}",
                action_type="TENSION_CANDIDATE_DETECTED",
                object_ref=tension.tension_id,
                actor_ref=f"paradox_engine_v{self.engine_version}",
                timestamp=ts,
                reason_code="HEURISTIC_DETECTION_PENDING_888_REVIEW",
                hash=f"sha256:{hashlib.sha256(tension.tension_id.encode()).hexdigest()[:16]}",
            )
            graph.receipts.append(receipt)

        # ── Step 4: Activity provenance ──
        graph.activities.append(ActivityNode(
            activity_id=f"activity_ingest_{article_id}",
            activity_type="constitutional_perception",
            description=f"Paradox engine v{self.engine_version}: ingested article, "
                        f"extracted {len(graph.actors)} actors, {len(graph.claims)} claims, "
                        f"detected {len(graph.tensions)} tensions",
            started_at=ts,
            actors_involved=[f"paradox_engine_v{self.engine_version}"],
            produced_refs=(
                [t.tension_id for t in graph.tensions] +
                [r.receipt_id for r in graph.receipts] +
                [f"ev_{article_id}"]
            ),
            used_refs=[],
            status="completed",
        ))

        return graph

    def seal_to_merkle(self, graph: BeliefGraph) -> dict[str, Any]:
        """Seal all BeliefGraph objects into the Merkle log.

        Returns dict with tree metadata, leaf indices, and inclusion proofs.
        """
        leaves: dict[str, int] = {}

        for ev in graph.evidence:
            leaves[f"ev_{ev.evidence_id}"] = self.merkle.append_canonical(
                ev.model_dump()
            )
        for c in graph.claims:
            leaves[f"claim_{c.claim_id}"] = self.merkle.append_canonical(
                c.model_dump()
            )
        for a in graph.actors:
            leaves[f"actor_{a.actor_id}"] = self.merkle.append_canonical(
                a.model_dump()
            )
        for t in graph.tensions:
            leaves[f"tension_{t.tension_id}"] = self.merkle.append_canonical(
                t.model_dump()
            )
        for r in graph.receipts:
            leaves[f"receipt_{r.receipt_id}"] = self.merkle.append_canonical(
                r.model_dump()
            )
        for act in graph.activities:
            leaves[f"activity_{act.activity_id}"] = self.merkle.append_canonical(
                act.model_dump()
            )

        # Graph root object
        graph_leaf_idx = self.merkle.append_canonical({
            "object_type": "BELIEF_GRAPH",
            "graph_id": graph.graph_id,
            "title": graph.title,
            "actor_count": len(graph.actors),
            "claim_count": len(graph.claims),
            "tension_count": len(graph.tensions),
            "receipt_count": len(graph.receipts),
            "engine_version": self.engine_version,
            "engine_hash": self.engine_hash,
            "created_at": graph.created_at,
        })
        leaves["belief_graph_root"] = graph_leaf_idx

        checkpoint = self.merkle.checkpoint()

        # Inclusion proofs for each tension (THE critical ones)
        inclusion_proofs = {}
        for t in graph.tensions:
            key = f"tension_{t.tension_id}"
            if key in leaves:
                inclusion_proofs[t.tension_id] = self.merkle.inclusion_proof(
                    leaves[key]
                )

        return {
            "graph_id": graph.graph_id,
            "engine_version": self.engine_version,
            "engine_hash": self.engine_hash,
            "tree_size": self.merkle.tree_size,
            "root_hash": checkpoint["root_hash"],
            "leaves": {
                k: {"index": v, "hash": self.merkle.leaves[v].hex()}
                for k, v in leaves.items()
            },
            "checkpoint": checkpoint,
            "inclusion_proofs": inclusion_proofs,
            "tensions_sealed": len(graph.tensions),
            "receipts_sealed": len(graph.receipts),
            "verdict": "CANDIDATE_ONLY — PENDING_888_REVIEW",
        }

    @staticmethod
    def _entity_type_for(actor_id: str) -> str:
        mapping = {
            "actor_mb_selangor": "government",
            "actor_petronas": "glc",
            "actor_kerajaan_persekutuan": "government",
            "actor_kerajaan_negeri": "government",
            "actor_mahkamah": "court",
            "actor_residents": "community",
            "actor_agc": "government",
            "actor_media": "media",
        }
        return mapping.get(actor_id, "unknown")

    @staticmethod
    def _jurisdiction_for(actor_id: str) -> str:
        mapping = {
            "actor_mb_selangor": "negeri",
            "actor_petronas": "persekutuan",
            "actor_kerajaan_persekutuan": "persekutuan",
            "actor_kerajaan_negeri": "negeri",
            "actor_mahkamah": "persekutuan",
            "actor_residents": "negeri",
            "actor_agc": "persekutuan",
            "actor_media": "both",
        }
        return mapping.get(actor_id, "")


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE FACTORY
# ═══════════════════════════════════════════════════════════════════════════

def ingest_article(
    text: str,
    url: str = "",
    title: str = "",
    reporter: str = "",
    date: str = "",
    publication: str = "",
    merkle: MerkleTree | None = None,
) -> dict[str, Any]:
    """Single-call pipeline: article → sealed belief graph with proofs.

    Returns the full sealing envelope — ready for VAULT999 storage
    or MCP resource exposure.

    HARD CONSTRAINT: Output is CANDIDATE ONLY. All governance actions
    require 888 review. This function perceives; it does not execute.
    """
    metadata = {
        "url": url,
        "title": title,
        "date": date,
        "reporter": reporter,
        "publication": publication,
    }

    engine = ParadoxEngine(merkle)
    graph = engine.ingest(text, metadata)
    envelope = engine.seal_to_merkle(graph)

    return envelope


def ingest_putra_heights() -> dict[str, Any]:
    """Reference pipeline for the canonical Putra Heights article.

    Uses the same engine pipeline — heuristic detection, not hardcoded
    annotation. Compare output to putra_heights_graph.py for validation.
    """
    article_text = (
        "Kosmo! pada 22 Mei lalu melaporkan kerajaan negeri bersedia "
        "mendedahkan laporan penuh insiden itu selepas menerimanya daripada "
        "kerajaan Persekutuan. "
        "Menteri Besar Selangor, Datuk Seri Amirudin Shari berkata, laporan "
        "itu akan didedahkan kepada umum sebaik semua proses selesai. "
        "Bagaimanapun, Amirudin menegaskan, kerajaan negeri tiada halangan "
        "mendedahkan laporan itu namun perlu mematuhi proses dan "
        "mempertimbangkan implikasi undang-undang. "
        "Beberapa bahagian laporan perlu diteliti semula terutama melibatkan "
        "agensi persekutuan seperti Petronas. "
        "Laporan semakan siasatan daripada Jawatankuasa Bebas telah "
        "diserahkan pada April lalu. "
        "Pada masa sama, seramai 36 penduduk Taman Putra Harmoni telah "
        "memfailkan tindakan sivil di Mahkamah Tinggi Shah Alam terhadap "
        "lima pihak termasuk Petronas Gas Berhad. "
        "Penduduk mendakwa letupan paip gas itu adalah buatan manusia dan "
        "boleh dicegah. Mereka melantik Tommy Thomas sebagai peguam. "
        "Amirudin menjelaskan, ada aspek bidang kuasa, perundangan dan "
        "pihak terlibat di peringkat persekutuan yang perlu dipatuhi. "
        "Laporan awal siasatan menyatakan tiada bukti jenayah atau kecuaian."
    )

    return ingest_article(
        text=article_text,
        url="https://www.kosmo.com.my/2026/06/12/pendedahan-laporan-putra-heights-berdepan-kekangan-undang-undang/",
        title="Pendedahan laporan Putra Heights berdepan kekangan undang-undang",
        reporter="ISKANDAR SHAH MOHAMED",
        date="2026-06-12",
        publication="Kosmo!",
    )


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "ParadoxEngine",
    "FrameExtractor",
    "TensionClassifier",
    "ingest_article",
    "ingest_putra_heights",
]
