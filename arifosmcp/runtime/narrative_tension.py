"""
arifosmcp/runtime/narrative_tension.py
═══════════════════════════════════════════════════════════════════
Narrative Tension / Frame Graph perception kernel.

Reads the geometry of human text — actors, claims, hedges, contradictions,
power asymmetry — and returns first-class ParadoxTensionNodes that can be
sealed to VAULT999.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from arifosmcp.schemas.narrative_tension import (
    ActorNode,
    ArticleNode,
    ClaimNode,
    FrameGraph,
    KernelVerdict,
    NarrativeTensionRequest,
    NarrativeTensionResponse,
    ParadoxTensionNode,
)

logger = logging.getLogger("arifosmcp.narrative_tension")


# ── Golden-case corpus ───────────────────────────────────────────────────────
_GOLDEN_CASE_DIR = Path(__file__).resolve().parents[2] / "GENESIS" / "PH-KOSMO-2026-06-12"

# ── Malay / English hedging and tension lexicons ─────────────────────────────
_HEDGING_PHRASES: frozenset[str] = frozenset(
    {
        "kekangan undang-undang",
        "perlu diteliti semula",
        "masih belum boleh",
        "sedang disiasat",
        "akan didedahkan",
        "bersedia untuk",
        "dalam proses",
        "menunggu keputusan",
        "tiada kecuaian",
        "sedang dinilai",
        "under review",
        "being studied",
        "cannot disclose",
        "legal constraints",
        "awaiting decision",
        "no negligence",
    }
)

_PASSIVE_OBSTACLE_PHRASES: frozenset[str] = frozenset(
    {
        "terdapat kekangan",
        "terdapat halangan",
        "ada halangan",
        "ada kekangan",
        "there are constraints",
        "there are obstacles",
    }
)

_DEADLINE_VOID_PHRASES: frozenset[str] = frozenset(
    {
        "setahun",
        "berbulan-bulan",
        "April lalu",
        "Jun",
        "masih belum",
        "belum selesai",
        "years later",
        "months later",
        "still pending",
    }
)

_JURISDICTION_PHRASES: frozenset[str] = frozenset(
    {
        "kerajaan negeri",
        "kerajaan persekutuan",
        "agensi persekutuan",
        "negeri",
        "persekutuan",
        "state government",
        "federal government",
        "federal agency",
    }
)

_CONTRADICTION_PAIRS: list[tuple[str, str]] = [
    ("bersedia dedah", "masih belum boleh didedahkan"),
    ("akan didedahkan", "belum didedahkan"),
    ("tiada kecuaian", "boleh dicegah"),
    ("no negligence", "could have been prevented"),
    ("ready to disclose", "cannot disclose"),
]

_ACTOR_PATTERNS: list[tuple[str, str, str]] = [
    (r"MB\s+([A-Za-z\s]+)\s+(?:menjelaskan|berkata|kata)", "MB", "government"),
    (r"Menteri\s+Besar\s+([A-Za-z\s]+)", "MB", "government"),
    (r"(?:Penduduk|mangsa|plaintif)\s+(?:Putra Heights)?", "Penduduk Putra Heights", "group"),
    (r"Petronas", "Petronas", "corporation"),
    (r"kerajaan negeri", "Kerajaan Negeri", "government"),
    (r"kerajaan persekutuan", "Kerajaan Persekutuan", "government"),
    (r"agensi persekutuan", "Agensi Persekutuan", "government"),
]


def _short_hash(text: str, length: int = 16) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:length]


def _now() -> datetime:
    return datetime.now(UTC)


def _constitution_hash() -> str:
    """Best-effort constitution hash; matches the existing golden case convention."""
    return "sha256:arifos-constitution-v2026.05.05-SSCT"


def _load_golden_case(article_id: str | None, title: str) -> NarrativeTensionResponse | None:
    """Load a pre-computed golden-case analysis if one exists."""
    if article_id != "ARTICLE-kosmo-putra-2026-06-12" and "Putra Heights" not in title:
        return None
    if not _GOLDEN_CASE_DIR.exists():
        return None

    try:
        with open(_GOLDEN_CASE_DIR / "article.json") as f:
            article_data = json.load(f)
        with open(_GOLDEN_CASE_DIR / "actors.json") as f:
            actors_data = json.load(f)
        with open(_GOLDEN_CASE_DIR / "claims.json") as f:
            claims_data = json.load(f)
        with open(_GOLDEN_CASE_DIR / "tensions.json") as f:
            tensions_data = json.load(f)
        with open(_GOLDEN_CASE_DIR / "kernel_verdict.json") as f:
            verdict_data = json.load(f)

        article = ArticleNode.model_validate(article_data)
        actors = [ActorNode.model_validate(a) for a in actors_data]
        claims = [ClaimNode.model_validate(c) for c in claims_data]
        tensions = [ParadoxTensionNode.model_validate(t) for t in tensions_data]
        kernel_verdict = KernelVerdict.model_validate(verdict_data)

        frame_graph = FrameGraph(
            node_type="ArticleFrameGraph",
            node_id=f"NODE-FRAMEGRAPH-{article.article_id}",
            article=article,
            actors=actors,
            claims=claims,
            tensions=tensions,
            created_at=_now(),
            created_by="arifOS-paradox-engine",
            constitution_hash=_constitution_hash(),
            epistemic_tag="EVIDENCE",
            provenance=f"Golden case loaded from {_GOLDEN_CASE_DIR}",
        )

        return NarrativeTensionResponse(
            status="OK",
            tool="arif_detect_narrative_tension",
            verdict=kernel_verdict.overall_verdict,
            frame_graph=frame_graph,
            kernel_verdict=kernel_verdict,
            next_safe_action="Golden-case analysis loaded; escalate PH-T3 named-actor slip.",
        )
    except Exception as exc:
        logger.warning(f"[narrative_tension] golden case load failed: {exc}")
        return None


def _extract_actors(text: str, title: str) -> list[ActorNode]:
    """Heuristic actor extraction with Malay/English pattern matching."""
    actors: list[ActorNode] = []
    seen: set[str] = set()

    for pattern, default_name, actor_type in _ACTOR_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = default_name
            if match.lastindex and match.group(1):
                name = f"{default_name} ({match.group(1).strip()})"
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)

            # Count direct quotes as a proxy for voice.
            quote_count = len(re.findall(re.escape(name.split("(")[0].strip()), text))
            agency_score = 0.8 if "MB" in name or "Menteri" in name else 0.4
            protection_level = 0.7 if "Petronas" in name or "Persekutuan" in name else 0.2

            role = "other"
            if "Penduduk" in name or "mangsa" in name.lower():
                role = "victim"
            elif "Petronas" in name or "Persekutuan" in name:
                role = "gatekeeper"
            elif "MB" in name or "Menteri" in name:
                role = "hero"

            actors.append(
                ActorNode(
                    node_type="ActorNode",
                    node_id=f"NODE-ACTOR-{_short_hash(name)}-{len(actors):03d}",
                    name=name,
                    actor_type=actor_type,
                    role_in_frame=role,
                    quote_count=min(quote_count, 20),
                    agency_score=agency_score,
                    protection_level=protection_level,
                    created_at=_now(),
                    constitution_hash=_constitution_hash(),
                    epistemic_tag="EVIDENCE" if quote_count > 0 else "PLAUSIBLE",
                    provenance="Heuristic extraction from text",
                )
            )

    # Always include a reporter observer node.
    actors.append(
        ActorNode(
            node_type="ActorNode",
            node_id="NODE-ACTOR-REPORTER-001",
            name="Reporter",
            actor_type="individual",
            role_in_frame="observer",
            quote_count=0,
            agency_score=0.3,
            protection_level=0.0,
            created_at=_now(),
            constitution_hash=_constitution_hash(),
            epistemic_tag="EVIDENCE",
            provenance="Article byline or authorship",
        )
    )
    return actors


def _extract_claims(text: str, actors: list[ActorNode]) -> list[ClaimNode]:
    """Split text into rough claim units and tag hedging/contradiction."""
    claims: list[ClaimNode] = []
    sentences = re.split(r"(?<=[.!?])\s+", text)

    for idx, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if len(sentence) < 20:
            continue

        hedges = [h for h in _HEDGING_PHRASES if h.lower() in sentence.lower()]
        claimer = ""
        for actor in actors:
            if actor.name.split("(")[0].strip().lower() in sentence.lower():
                claimer = actor.name
                break

        claims.append(
            ClaimNode(
                node_type="ClaimNode",
                node_id=f"NODE-CLAIM-{idx+1:03d}",
                claim_text=sentence[:300],
                claimer=claimer,
                claimer_type="unknown",
                evidence_support=0.5,
                hedging_detected=bool(hedges),
                hedging_phrases=hedges,
                created_at=_now(),
                constitution_hash=_constitution_hash(),
                epistemic_tag="CLAIM",
                provenance="Sentence-level extraction",
            )
        )
    return claims


def _build_contradictions(claims: list[ClaimNode]) -> list[tuple[str, str]]:
    """Find claim pairs that match known contradiction patterns."""
    pairs: list[tuple[str, str]] = []
    for a, b in [(c1, c2) for c1 in claims for c2 in claims if c1.node_id != c2.node_id]:
        for left, right in _CONTRADICTION_PAIRS:
            if left.lower() in a.claim_text.lower() and right.lower() in b.claim_text.lower():
                pairs.append((a.node_id, b.node_id))
                a.contradicts.append(b.node_id)
    return pairs


def _detect_tensions(
    article: ArticleNode,
    actors: list[ActorNode],
    claims: list[ClaimNode],
) -> list[ParadoxTensionNode]:
    """Rule-based tension detection."""
    tensions: list[ParadoxTensionNode] = []
    text_lower = article.title.lower()
    for c in claims:
        text_lower += " " + c.claim_text.lower()

    # 1. Deadline void
    if any(p.lower() in text_lower for p in _DEADLINE_VOID_PHRASES):
        tensions.append(
            ParadoxTensionNode(
                node_type="ParadoxTensionNode",
                node_id=f"NODE-TENSION-{article.article_id}-T1",
                tension_id=f"{article.article_id[:8].upper()}-T1",
                tension_class="DEADLINE_VOID",
                trigger_kind="deadline_without_closure",
                severity=0.8,
                shadow_score=0.75,
                article_ref=article.node_id,
                actor_refs=[a.node_id for a in actors],
                claim_refs=[c.node_id for c in claims if c.hedging_detected][:3],
                description="Timeline references without a concrete closure date.",
                what_reporter_couldnt_say="Institutional delay is being framed as process.",
                evidence_snippets=[c.claim_text[:120] for c in claims if c.hedging_detected][:3],
                recommended_action="ESCALATE",
                governance_pattern="DEADLINE_VOID_ESCALATION",
                auto_tags=["DEADLINE_VOID", "INSTITUTIONAL_DELAY", "PUBLIC_INTEREST_HIGH"],
                created_at=_now(),
                constitution_hash=_constitution_hash(),
                epistemic_tag="PLAUSIBLE",
                provenance="Heuristic deadline-void detection",
            )
        )

    # 2. Passive obstacle
    if any(p.lower() in text_lower for p in _PASSIVE_OBSTACLE_PHRASES):
        tensions.append(
            ParadoxTensionNode(
                node_type="ParadoxTensionNode",
                node_id=f"NODE-TENSION-{article.article_id}-T2",
                tension_id=f"{article.article_id[:8].upper()}-T2",
                tension_class="PASSIVE_OBSTACLE",
                trigger_kind="passive_agency_removal",
                severity=0.7,
                shadow_score=0.65,
                article_ref=article.node_id,
                actor_refs=[a.node_id for a in actors],
                claim_refs=[c.node_id for c in claims if c.hedging_detected][:2],
                description="Obstacles are named without assigning agency.",
                what_reporter_couldnt_say="Someone specific is blocking this, but cannot be named.",
                evidence_snippets=[c.claim_text[:120] for c in claims if c.hedging_detected][:2],
                recommended_action="REPORT",
                governance_pattern="PASSIVE_OBSTACLE_DETECTION",
                auto_tags=["PASSIVE_AGENCY", "INSTITUTIONAL_OPACITY_DETECTED"],
                created_at=_now(),
                constitution_hash=_constitution_hash(),
                epistemic_tag="PLAUSIBLE",
                provenance="Heuristic passive-obstacle detection",
            )
        )

    # 3. Contradictory narrative
    contradiction_pairs = _build_contradictions(claims)
    if contradiction_pairs:
        tensions.append(
            ParadoxTensionNode(
                node_type="ParadoxTensionNode",
                node_id=f"NODE-TENSION-{article.article_id}-T3",
                tension_id=f"{article.article_id[:8].upper()}-T3",
                tension_class="EXPLICIT_VS_IMPLICIT",
                trigger_kind="hedging_vs_hard_fact_collision",
                severity=0.75,
                shadow_score=0.7,
                article_ref=article.node_id,
                actor_refs=[a.node_id for a in actors],
                claim_refs=list({pair[0] for pair in contradiction_pairs})[:4],
                description="Two claims in the text collide without resolution.",
                what_reporter_couldnt_say="The official account and the affected account cannot both be true.",
                evidence_snippets=[claims[int(pair[0].split("-")[-1]) - 1].claim_text[:120] for pair in contradiction_pairs[:2]],
                recommended_action="HOLD",
                governance_pattern="CONTRADICTORY_NARRATIVE_HOLD",
                auto_tags=["CONTRADICTORY_NARRATIVE", "PUBLIC_INTEREST_HIGH"],
                created_at=_now(),
                constitution_hash=_constitution_hash(),
                epistemic_tag="EVIDENCE",
                provenance="Claim-contradiction heuristic",
            )
        )

    # 4. Jurisdiction trap
    if any(p.lower() in text_lower for p in _JURISDICTION_PHRASES):
        tensions.append(
            ParadoxTensionNode(
                node_type="ParadoxTensionNode",
                node_id=f"NODE-TENSION-{article.article_id}-T4",
                tension_id=f"{article.article_id[:8].upper()}-T4",
                tension_class="JURISDICTION_TRAP",
                trigger_kind="multi_jurisdiction_ping_pong",
                severity=0.7,
                shadow_score=0.65,
                article_ref=article.node_id,
                actor_refs=[a.node_id for a in actors],
                claim_refs=[c.node_id for c in claims][:3],
                description="Multiple jurisdictional layers are referenced without clear authority.",
                what_reporter_couldnt_say="State and federal actors are passing responsibility.",
                evidence_snippets=[c.claim_text[:120] for c in claims[:3]],
                recommended_action="REPORT",
                governance_pattern="JURISDICTION_TRAP_MAPPING",
                auto_tags=["JURISDICTION_TRAP", "MULTI_AGENCY_AMBIGUITY"],
                created_at=_now(),
                constitution_hash=_constitution_hash(),
                epistemic_tag="PLAUSIBLE",
                provenance="Heuristic jurisdiction-trap detection",
            )
        )

    # 5. Voice asymmetry
    hero_quotes = sum(a.quote_count for a in actors if a.role_in_frame == "hero")
    victim_quotes = sum(a.quote_count for a in actors if a.role_in_frame == "victim")
    if hero_quotes > 0 and victim_quotes == 0 and any(a.role_in_frame == "victim" for a in actors):
        tensions.append(
            ParadoxTensionNode(
                node_type="ParadoxTensionNode",
                node_id=f"NODE-TENSION-{article.article_id}-T5",
                tension_id=f"{article.article_id[:8].upper()}-T5",
                tension_class="VOICE_ASYMMETRY",
                trigger_kind="quote_asymmetry",
                severity=0.65,
                shadow_score=0.6,
                article_ref=article.node_id,
                actor_refs=[a.node_id for a in actors if a.role_in_frame in ("hero", "victim")],
                claim_refs=[c.node_id for c in claims if c.claimer][:3],
                description="Powerful actors are quoted; affected actors are only referenced.",
                what_reporter_couldnt_say="The victims have no direct voice in this article.",
                evidence_snippets=[a.name for a in actors if a.role_in_frame in ("hero", "victim")],
                recommended_action="REPORT",
                governance_pattern="VOICE_ASYMMETRY_CORRECTION",
                auto_tags=["VOICE_ASYMMETRY", "MARUAH_RISK"],
                created_at=_now(),
                constitution_hash=_constitution_hash(),
                epistemic_tag="EVIDENCE",
                provenance="Quote-count asymmetry heuristic",
            )
        )

    return tensions


def _compute_kernel_verdict(frame_graph: FrameGraph) -> KernelVerdict:
    """Aggregate frame-graph analysis into a kernel verdict."""
    tensions = frame_graph.tensions
    actors = frame_graph.actors
    claims = frame_graph.claims

    max_severity = max((t.severity for t in tensions), default=0.0)
    smoking_gun = None
    if tensions:
        smoking_gun = max(tensions, key=lambda t: t.severity).tension_id

    overall_verdict = "OBSERVE"
    if any(t.recommended_action == "ESCALATE" for t in tensions):
        overall_verdict = "ESCALATE"
    elif any(t.recommended_action == "HOLD" for t in tensions):
        overall_verdict = "HOLD"
    elif any(t.recommended_action == "REPORT" for t in tensions):
        overall_verdict = "REPORT"

    tags: set[str] = set()
    patterns: set[str] = set()
    for t in tensions:
        tags.update(t.auto_tags)
        if t.governance_pattern:
            patterns.add(t.governance_pattern)

    hero_quotes = sum(a.quote_count for a in actors if a.role_in_frame == "hero")
    victim_quotes = sum(a.quote_count for a in actors if a.role_in_frame == "victim")

    return KernelVerdict(
        kernel_verdict_id=f"VERDICT-{frame_graph.article.article_id}",
        article_id=frame_graph.article.article_id,
        timestamp=_now(),
        shadow_drift_risk=round(max((t.shadow_score for t in tensions), default=0.0), 3),
        max_severity=round(max_severity, 3),
        smoking_gun=smoking_gun,
        smoking_gun_severity=round(max_severity, 3) if smoking_gun else None,
        overall_verdict=overall_verdict,
        governance_patterns_detected=sorted(patterns),
        auto_tags=sorted(tags),
        detected_actors=len(actors),
        detected_claims=len(claims),
        detected_tensions=len(tensions),
        voice_asymmetry=f"Hero: {hero_quotes} quotes. Victim: {victim_quotes} quotes.",
        epistemic_isolation_flag=any(t.epistemic_tag == "PLAUSIBLE" for t in tensions),
        epistemic_isolation_note=(
            "Reporter cannot state the tension explicitly; geometry carries the truth."
            if any(t.epistemic_tag == "PLAUSIBLE" for t in tensions)
            else ""
        ),
        vault_uris=[f"vault://article/{frame_graph.article.article_id}"],
        constitution_hash=_constitution_hash(),
    )


def _analyze_request(request: NarrativeTensionRequest) -> NarrativeTensionResponse:
    """Run rule-based narrative tension analysis on a request."""
    article_id = request.article_id or f"ARTICLE-{_short_hash(request.title + request.text, 12)}"
    full_text_hash = _short_hash(request.text)

    article = ArticleNode(
        node_type="ArticleNode",
        node_id=f"NODE-ARTICLE-{article_id}",
        article_id=article_id,
        title=request.title,
        source=request.source,
        author=request.author,
        published_at=request.published_at,
        url=request.url,
        full_text_hash=full_text_hash,
        tags=request.tags,
        public_interest=request.public_interest,
        created_at=_now(),
        constitution_hash=_constitution_hash(),
        epistemic_tag="EVIDENCE",
        provenance="Ingested for narrative tension analysis",
    )

    actors = _extract_actors(request.text, request.title)
    claims = _extract_claims(request.text, actors)
    tensions = _detect_tensions(article, actors, claims)

    frame_graph = FrameGraph(
        node_type="ArticleFrameGraph",
        node_id=f"NODE-FRAMEGRAPH-{article_id}",
        article=article,
        actors=actors,
        claims=claims,
        tensions=tensions,
        created_at=_now(),
        constitution_hash=_constitution_hash(),
        epistemic_tag="PLAUSIBLE",
        provenance="Rule-based frame analysis",
    )

    kernel_verdict = _compute_kernel_verdict(frame_graph)

    next_action = "No significant tension detected."
    if kernel_verdict.overall_verdict == "ESCALATE":
        next_action = f"Escalate {kernel_verdict.smoking_gun or 'highest-severity tension'} to 888_JUDGE."
    elif kernel_verdict.overall_verdict == "HOLD":
        next_action = "Apply CONTRADICTORY_NARRATIVE_HOLD; do not treat claims as settled."
    elif kernel_verdict.overall_verdict == "REPORT":
        next_action = "Document tensions and continue monitoring."

    return NarrativeTensionResponse(
        status="OK",
        tool="arif_detect_narrative_tension",
        verdict=kernel_verdict.overall_verdict,
        frame_graph=frame_graph,
        kernel_verdict=kernel_verdict,
        next_safe_action=next_action,
    )


def detect_narrative_tension(
    request: NarrativeTensionRequest,
) -> NarrativeTensionResponse:
    """
    Detect narrative tension and frame geometry in a news article or text.

    Returns a FrameGraph + KernelVerdict. If the article matches a golden
    case (e.g. Putra Heights Kosmo 2026-06-12), the pre-computed analysis is
    returned instead of running heuristics.
    """
    golden = _load_golden_case(request.article_id, request.title)
    if golden is not None:
        return golden
    return _analyze_request(request)


def arif_detect_narrative_tension(
    title: str,
    text: str,
    article_id: str | None = None,
    source: str = "",
    author: str | None = None,
    published_at: str | None = None,
    url: str | None = None,
    tags: list[str] | None = None,
    public_interest: str = "MEDIUM",
    actor_hints: list[dict[str, Any]] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Public MCP tool: detect narrative tension / paradox geometry in text.

    Parameters
    ----------
    title : str
        Article headline.
    text : str
        Full article text.
    article_id : str | None
        Optional stable identifier; triggers golden-case lookup for known articles.
    source, author, published_at, url : optional metadata
    tags : list[str] | None
        Subject tags.
    public_interest : str
        LOW | MEDIUM | HIGH | CRITICAL
    actor_hints : list[dict] | None
        Optional hints for actor extraction.
    actor_id, session_id : MCP ingress metadata (ignored by logic).

    Returns
    -------
    dict
        NarrativeTensionResponse as JSON-serialisable dict with frame_graph,
        kernel_verdict, and next_safe_action.
    """
    request = NarrativeTensionRequest(
        article_id=article_id,
        title=title,
        source=source,
        author=author,
        published_at=published_at,
        url=url,
        text=text,
        tags=tags or [],
        public_interest=public_interest,
        actor_hints=actor_hints or [],
    )
    response = detect_narrative_tension(request)
    return response.model_dump(mode="json")


__all__ = [
    "detect_narrative_tension",
    "arif_detect_narrative_tension",
]
