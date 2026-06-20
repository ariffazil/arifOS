"""
Putra Heights Kosmo Article — Full Belief Graph with 7 Tension Nodes
══════════════════════════════════════════════════════════════════════

Concrete annotation of Kosmo! 2026-06-12 article by Iskandar Shah Mohamed.
Every tension is a first-class kernel object with receipts.
DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

from __future__ import annotations

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
)


def putra_heights_belief_graph() -> BeliefGraph:
    """Forge the complete Kosmo article belief graph with all 7 tension nodes."""

    g = BeliefGraph(
        graph_id="bg-putra-20260612",
        title="Putra Heights Report Disclosure — Kosmo! 2026-06-12 Frame Graph",
    )

    # ══════════════════════════════════════════════════════════════════════
    # ACTORS
    # ══════════════════════════════════════════════════════════════════════

    g.actors = [
        ActorNode(
            actor_id="actor_iskandar_shah",
            name="Iskandar Shah Mohamed",
            role=ActorRole.MEDIA,
            entity_type="media",
            power_score=0.30,
            visibility_score=0.75,
            accountability_score=0.60,
        ),
        ActorNode(
            actor_id="actor_mb_selangor",
            name="Datuk Seri Amirudin Shari (MB Selangor)",
            role=ActorRole.GATEKEEPER,
            entity_type="government",
            jurisdiction="negeri",
            power_score=0.65,
            visibility_score=0.90,
            accountability_score=0.55,
        ),
        ActorNode(
            actor_id="actor_petronas",
            name="Petronas / Petronas Gas Berhad",
            role=ActorRole.OPERATOR,
            entity_type="glc",
            jurisdiction="persekutuan",
            power_score=0.92,
            visibility_score=0.35,
            accountability_score=0.28,
        ),
        ActorNode(
            actor_id="actor_residents",
            name="36 Penduduk Taman Putra Harmoni",
            role=ActorRole.VICTIM,
            entity_type="community",
            power_score=0.10,
            visibility_score=0.25,
            accountability_score=0.05,
        ),
        ActorNode(
            actor_id="actor_agc",
            name="Jawatankuasa Bebas / Attorney-General Chambers",
            role=ActorRole.LEGAL,
            entity_type="government",
            jurisdiction="persekutuan",
            power_score=0.70,
            visibility_score=0.20,
            accountability_score=0.30,
        ),
        ActorNode(
            actor_id="actor_kerajaan_negeri",
            name="Kerajaan Negeri Selangor",
            role=ActorRole.INSTITUTION,
            entity_type="government",
            jurisdiction="negeri",
            power_score=0.55,
            visibility_score=0.80,
            accountability_score=0.50,
        ),
        ActorNode(
            actor_id="actor_kerajaan_persekutuan",
            name="Kerajaan Persekutuan",
            role=ActorRole.GATEKEEPER,
            entity_type="government",
            jurisdiction="persekutuan",
            power_score=0.85,
            visibility_score=0.40,
            accountability_score=0.25,
        ),
        ActorNode(
            actor_id="actor_mahkamah",
            name="Mahkamah Tinggi Shah Alam",
            role=ActorRole.LEGAL,
            entity_type="court",
            jurisdiction="persekutuan",
            power_score=0.75,
            visibility_score=0.30,
            accountability_score=0.45,
        ),
    ]

    # ══════════════════════════════════════════════════════════════════════
    # EVIDENCE
    # ══════════════════════════════════════════════════════════════════════

    g.evidence = [
        EvidenceNode(
            evidence_id="ev_kosmo_2026_06_12",
            evidence_type="news_article",
            description="Kosmo! report on MB Selangor statement regarding Putra Heights report",
            source_uri="https://www.kosmo.com.my/2026/06/12/pendedahan-laporan-putra-heights-berdepan-kekangan-undang-undang/",
            hash="sha256:kosmo-putra-2026-06-12",
            reliability=0.85,
        ),
        EvidenceNode(
            evidence_id="ev_mb_statement_may",
            evidence_type="prior_statement",
            description="Kosmo! 22 Mei: kerajaan negeri bersedia mendedahkan laporan penuh",
            source_uri="https://www.kosmo.com.my/2026/05/22/",
            reliability=0.80,
        ),
        EvidenceNode(
            evidence_id="ev_litigation_filing",
            evidence_type="court_record",
            description="Saman sivil 36 penduduk di Mahkamah Tinggi Shah Alam",
            source_uri="",
            reliability=0.95,
        ),
    ]

    # ══════════════════════════════════════════════════════════════════════
    # CLAIMS
    # ══════════════════════════════════════════════════════════════════════

    g.claims = [
        ClaimNode(  # C1
            claim_id="claim_bersedia_dedah",
            text="Kerajaan negeri bersedia mendedahkan laporan penuh insiden itu",
            claim_type=ClaimType.PROMISE,
            speaker="actor_mb_selangor",
            epistemic_tag=EpistemicTag.CLAIM,
            source_uri="ev_kosmo_2026_06_12",
            contradicts=["claim_kekangan_undang"],
            hedging_score=0.15,
            verifiable=True,
        ),
        ClaimNode(  # C2
            claim_id="claim_kekangan_undang",
            text="Pendedahan laporan berdepan kekangan susulan tindakan undang-undang",
            claim_type=ClaimType.MITIGATION,
            speaker="actor_mb_selangor",
            epistemic_tag=EpistemicTag.CLAIM,
            source_uri="ev_kosmo_2026_06_12",
            contradicts=["claim_bersedia_dedah"],
            hedging_score=0.35,
            verifiable=True,
        ),
        ClaimNode(  # C3
            claim_id="claim_perlu_teliti_petronas",
            text="Beberapa bahagian laporan perlu diteliti semula terutama melibatkan agensi persekutuan seperti Petronas",
            claim_type=ClaimType.FINDING,
            speaker="actor_mb_selangor",
            epistemic_tag=EpistemicTag.PLAUSIBLE,
            source_uri="ev_kosmo_2026_06_12",
            hedging_score=0.70,
            verifiable=False,
        ),
        ClaimNode(  # C4
            claim_id="claim_laporan_diserah_april",
            text="Laporan semakan siasatan daripada Jawatankuasa Bebas telah diserahkan pada April lalu",
            claim_type=ClaimType.FINDING,
            speaker="actor_mb_selangor",
            epistemic_tag=EpistemicTag.FACT,
            source_uri="ev_kosmo_2026_06_12",
            hedging_score=0.05,
            verifiable=True,
        ),
        ClaimNode(  # C5
            claim_id="claim_negeri_tiada_halangan",
            text="Kerajaan negeri tiada halangan mendedahkan laporan itu",
            claim_type=ClaimType.PROMISE,
            speaker="actor_mb_selangor",
            epistemic_tag=EpistemicTag.CLAIM,
            source_uri="ev_kosmo_2026_06_12",
            contradicts=["claim_kekangan_undang"],
            hedging_score=0.40,
            verifiable=False,
        ),
        ClaimNode(  # C6
            claim_id="claim_akan_didedah_sebaik_selesai",
            text="Laporan itu akan dikongsi kepada umum sebaik semua proses berkenaan selesai",
            claim_type=ClaimType.PROMISE,
            speaker="actor_mb_selangor",
            epistemic_tag=EpistemicTag.CLAIM,
            source_uri="ev_kosmo_2026_06_12",
            hedging_score=0.55,
            verifiable=False,
        ),
        ClaimNode(  # C7
            claim_id="claim_penduduk_saman",
            text="36 penduduk memfailkan tindakan sivil di Mahkamah Tinggi Shah Alam terhadap lima pihak",
            claim_type=ClaimType.FINDING,
            speaker="actor_residents",
            epistemic_tag=EpistemicTag.FACT,
            source_uri="ev_kosmo_2026_06_12",
            hedging_score=0.05,
            verifiable=True,
        ),
        ClaimNode(  # C8
            claim_id="claim_ikut_proses",
            text="Perlu melalui proses betul kerana ada aspek bidang kuasa, perundangan dan pihak terlibat di peringkat persekutuan",
            claim_type=ClaimType.MITIGATION,
            speaker="actor_mb_selangor",
            epistemic_tag=EpistemicTag.CLAIM,
            source_uri="ev_kosmo_2026_06_12",
            hedging_score=0.65,
            verifiable=False,
        ),
        ClaimNode(  # C9 — needed for PH-T3 contradiction
            claim_id="claim_agensi_persekutuan_generik",
            text="Melibatkan agensi persekutuan — dilaporkan sebagai kategori generik tanpa nama",
            claim_type=ClaimType.MITIGATION,
            speaker="actor_mb_selangor",
            epistemic_tag=EpistemicTag.CLAIM,
            source_uri="ev_kosmo_2026_06_12",
            contradicts=["claim_perlu_teliti_petronas"],
            hedging_score=0.80,
            verifiable=False,
        ),
    ]

    # ══════════════════════════════════════════════════════════════════════
    # ACTIVITIES
    # ══════════════════════════════════════════════════════════════════════

    g.activities = [
        ActivityNode(
            activity_id="activity_reporter_geometry",
            activity_type="detect",
            description="Reporter writes article with embedded meaning leak geometry",
            started_at="2026-06-12T15:26:00+08:00",
            actors_involved=["actor_iskandar_shah"],
            produced_refs=["ev_kosmo_2026_06_12"],
        ),
        ActivityNode(
            activity_id="activity_tension_detect",
            activity_type="detect",
            description="Kernel detects 7 paradox tensions from article frame graph",
            started_at="2026-06-13T04:00:00+08:00",
            actors_involved=["agent_arifos_reasoner"],
            used_refs=["ev_kosmo_2026_06_12"],
            produced_refs=[
                "ptn_ph_t1", "ptn_ph_t2", "ptn_ph_t3", "ptn_ph_t4",
                "ptn_ph_t5", "ptn_ph_t6", "ptn_ph_t7",
            ],
        ),
    ]

    # ══════════════════════════════════════════════════════════════════════
    # 7 PARADOX TENSION NODES
    # ══════════════════════════════════════════════════════════════════════

    def _tension(tid, title, tclass, severity, summary, claims, scores, required_action):
        return ParadoxTensionNode(
            tension_id=tid,
            title=title,
            tension_class=tclass,
            severity=severity,
            summary=summary,
            claim_refs=claims,
            evidence_refs=["ev_kosmo_2026_06_12"],
            actor_refs=["actor_mb_selangor", "actor_petronas", "actor_residents", "actor_kerajaan_persekutuan"],
            provenance=Provenance(
                generated_by_activity="activity_tension_detect",
                generated_by_agent="agent_arifos_reasoner",
            ),
            scores=scores,
            governance=GovernanceBinding(required_action=required_action),
        )

    g.tensions = [
        _tension(  # PH-T1: PROMISE_VS_OUTCOME
            "ptn_ph_t1", "Disclosure Promise vs Report Withheld",
            TensionClass.INSTITUTIONAL_PARADOX, Severity.HIGH,
            "3 minggu dari 'bersedia dedah' (22 Mei) ke 'tak boleh dedah' (12 Jun). Niat deklaratif bercanggah dengan outcome sebenar.",
            ["claim_bersedia_dedah", "claim_kekangan_undang"],
            TensionScores(confidence=0.80, credibility=0.75, coherence_strain=0.85,
                         public_interest=0.95, harm_potential=0.75, shadow_score=0.60,
                         meaning_leak_intensity=0.65, maruah_impact=-0.55),
            "escalate_review_timeout",
        ),
        _tension(  # PH-T2: PASSIVE_OBSTACLE
            "ptn_ph_t2", "Passive Obstacle Construction",
            TensionClass.MEANING_LEAK, Severity.MEDIUM,
            "MB kata 'tiada halangan' untuk dedah — tapi ayat berikutnya menyenaraikan halangan. Passive voice menyembunyikan agency. Siapa yang SEBENARNYA menahan?",
            ["claim_negeri_tiada_halangan", "claim_kekangan_undang"],
            TensionScores(confidence=0.75, credibility=0.70, coherence_strain=0.75,
                         public_interest=0.65, harm_potential=0.45, shadow_score=0.70,
                         meaning_leak_intensity=0.88, maruah_impact=-0.30),
            "audit_passive_obstacle",
        ),
        _tension(  # PH-T3: SLIP_PHRASE — THE SMOKING GUN
            "ptn_ph_t3", "Named Actor Slip: 'Seperti Petronas'",
            TensionClass.MEANING_LEAK, Severity.CRITICAL,
            "Ayat paling jujur dalam artikel: 'melibatkan agensi persekutuan seperti Petronas'. Petronas disebut NAMA — bukan 'agensi persekutuan' generik. Reporter sengaja letak nama. Ini bendera merah untuk seksyen laporan yang paling sensitif.",
            ["claim_agensi_persekutuan_generik", "claim_perlu_teliti_petronas"],
            TensionScores(confidence=0.95, credibility=0.90, coherence_strain=0.85,
                         public_interest=0.98, harm_potential=0.90, shadow_score=0.91,
                         meaning_leak_intensity=0.97, maruah_impact=-0.80),
            "activate_ACCIDENT_REPORT_LITIGATION_HOLD",
        ),
        _tension(  # PH-T4: VOICE_ASYMMETRY
            "ptn_ph_t4", "Voice Asymmetry: MB Dominates, Residents Silent",
            TensionClass.PUBLIC_PRIVATE_DIVERGENCE, Severity.MEDIUM,
            "MB mendapat 4 petikan langsung. Penduduk: sifar petikan. Artikel melaporkan mangsa melalui naratif MB — bukan suara mereka sendiri. Geometry = power.",
            ["claim_bersedia_dedah", "claim_kekangan_undang", "claim_penduduk_saman"],
            TensionScores(confidence=0.70, credibility=0.65, coherence_strain=0.55,
                         public_interest=0.75, harm_potential=0.55, shadow_score=0.55,
                         meaning_leak_intensity=0.72, maruah_impact=-0.65),
            "audit_voice_balance",
        ),
        _tension(  # PH-T5: EXPLICIT_VS_IMPLICIT
            "ptn_ph_t5", "Explicit vs Implicit: No Negligence vs Preventable",
            TensionClass.HARD_CONTRADICTION, Severity.HIGH,
            "Laporan siasatan kata 'tiada kecuaian' (naratif rasmi). Mangsa dakwa 'boleh dicegah' (naratif komuniti). Dua naratif bertembung — tapi hanya satu dapat ruang dalam artikel.",
            ["claim_perlu_teliti_petronas", "claim_penduduk_saman"],
            TensionScores(confidence=0.80, credibility=0.72, coherence_strain=0.90,
                         public_interest=0.92, harm_potential=0.85, shadow_score=0.68,
                         meaning_leak_intensity=0.60, maruah_impact=-0.72),
            "escalate_to_contradiction_audit",
        ),
        _tension(  # PH-T6: DEADLINE_VOID
            "ptn_ph_t6", "Deadline Void: Indefinite Review",
            TensionClass.TIMELINE_INCOHERENCE, Severity.HIGH,
            "Laporan diserah April. Jun masih 'diteliti semula'. Tiada tarikh tamat disebut. 'Penelitian semula' tanpa deadline = indefinite hold dressed as due diligence.",
            ["claim_laporan_diserah_april", "claim_akan_didedah_sebaik_selesai"],
            TensionScores(confidence=0.90, credibility=0.85, coherence_strain=0.92,
                         public_interest=0.90, harm_potential=0.78, shadow_score=0.82,
                         meaning_leak_intensity=0.55, maruah_impact=-0.70),
            "escalate_deadline_breach",
        ),
        _tension(  # PH-T7: JURISDICTION_TRAP
            "ptn_ph_t7", "Jurisdiction Trap: Negeri vs Persekutuan",
            TensionClass.ROLE_RESPONSIBILITY_GAP, Severity.MEDIUM,
            "MB Selangor kata 'tiada halangan' — tapi proses libatkan 'bidang kuasa persekutuan'. Negeri nak dedah tapi tak pegang kunci. Siapa yang sekat sebenarnya?",
            ["claim_negeri_tiada_halangan", "claim_ikut_proses"],
            TensionScores(confidence=0.75, credibility=0.70, coherence_strain=0.65,
                         public_interest=0.78, harm_potential=0.60, shadow_score=0.73,
                         meaning_leak_intensity=0.68, maruah_impact=-0.45),
            "audit_jurisdiction_choke",
        ),
    ]

    # ══════════════════════════════════════════════════════════════════════
    # RECEIPTS — one per tension node (detection receipt)
    # ══════════════════════════════════════════════════════════════════════

    for i, t in enumerate(g.tensions, 1):
        g.receipts.append(ReceiptNode(
            receipt_id=f"rcpt_ph_t{i}_detect_01",
            action_type="TENSION_DETECTED",
            object_ref=t.tension_id,
            actor_ref="agent_arifos_reasoner",
            timestamp="2026-06-13T04:00:00+08:00",
            reason_code="FRAME_GRAPH_DETECTION",
            hash=f"sha256:tension-detect-{t.tension_id}",
        ))

    return g


def seal_belief_graph_to_merkle(g: BeliefGraph, merkle: MerkleTree) -> dict:
    """Seal all belief graph objects into the Merkle log.

    Returns a dict with leaf indices, checkpoint, and proofs.
    """
    leaves = {}

    # Article evidence
    for ev in g.evidence:
        leaves[ev.evidence_id] = merkle.append_canonical(ev.model_dump())

    # Claims
    for c in g.claims:
        leaves[c.claim_id] = merkle.append_canonical(c.model_dump())

    # Actors
    for a in g.actors:
        leaves[a.actor_id] = merkle.append_canonical(a.model_dump())

    # Tensions (the critical ones)
    for t in g.tensions:
        leaves[t.tension_id] = merkle.append_canonical(t.model_dump())

    # Receipts
    for r in g.receipts:
        leaves[r.receipt_id] = merkle.append_canonical(r.model_dump())

    # Activities
    for act in g.activities:
        leaves[act.activity_id] = merkle.append_canonical(act.model_dump())

    checkpoint = merkle.checkpoint()

    return {
        "graph_id": g.graph_id,
        "tree_size": merkle.tree_size,
        "root_hash": checkpoint["root_hash"],
        "leaves": {k: {"index": v, "hash": merkle.leaves[v].hex()} for k, v in leaves.items()},
        "checkpoint": checkpoint,
        "inclusion_proofs": {
            t.tension_id: merkle.inclusion_proof(leaves[t.tension_id])
            for t in g.tensions
        },
        "consistency_proofs": {
            f"{merkle.tree_size - 20}-{merkle.tree_size}": (
                merkle.consistency_proof(merkle.tree_size - 20, merkle.tree_size)
                if merkle.tree_size > 20 else None
            ),
        },
    }
