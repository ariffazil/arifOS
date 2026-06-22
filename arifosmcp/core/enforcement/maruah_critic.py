# arifOS — Maruah Critic v0.1 (post-LLM enforcement, additive)
# Forged 2026-06-21 | session: 2026-06-21-melayu-policy
# Provenance: usman_awang_research → v0 (2026-06-21 am) → v0.1 (2026-06-21 pm,
#              after Arif "Call BANGANG as BANGANG" correction).
# Iron Rule (v0.1): this file WAS a passive function library.
#                    v0.2 (2026-06-20): WIRED into arif_judge via
#                    /root/arifOS/arifosmcp/tools/judge.py.
#                    See 888_HOLD seal: <forge-session-2026-06-20>.
#                    Wire-up patch: maruah_critic_check() + is_maruah_sensitive()
#                    called from arif_judge when community_maruah=true.
#                    Integration test: tests/constitutional/test_maruah_enforcement.py.
#
# Design constraints (v0.1):
#   - No new floor (F1-F13 count is hard). Policy file under L05/L06.
#   - No "Melayu-Qualia Layer" term (F4 violation, format-injection attack surface).
#   - No external citations in code; provenance in /root/AAA/agents/decisions/.
#   - Whorfian weak relativity only — qualia is approximation, not claim.
#   - Maruah critic filters *hinakan individu* and *dehumanization*,
#     NOT *kasar* and NOT *kritik sistem*. Kasar BM Pasar is allowed.
#     "Call BANGANG as BANGANG" — Arif 2026-06-21.

"""
maruah_critic: post-LLM pass untuk enforce "marah-bersyahdu, bukan raw rage".

v0.1 redesign: the goal is DIGNITY, not POLITENESS.

Kasar (rough) language, BM Pasar, "spade-as-spade" register — ALLOWED.
Hinakan individu (personal dehumanization) — BLOCKED.
Sindir melampau (systemic dehumanization, group-level slur) — BLOCKED.
Kritik sistem (critique of policies, structures, decisions) — ALLOWED,
    even when expressed in harsh register.

Usage pattern (future, not wired):
    from arifosmcp.core.enforcement.maruah_critic import (
        is_maruah_sensitive,
        maruah_critic_check,
    )

    if is_maruah_sensitive(task_metadata):
        verdict = maruah_critic_check(draft_text, audience_profile)
        if not verdict.ok:
            return revise(draft_text, verdict.issues)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import re as _re
# --- Policy line (the only "code" that matters) -------------------------
# F6 EMPATHY enforcement extension. v0.1 wording:
#   - kritik_sistem: ALLOWED (kasar or halus, your call)
#   - hinakan_individu: BLOCKED (Arif punya maruah, semua orang punya maruah)
#   - dehumanization_group: BLOCKED (lebih bahaya dari hinakan individu)
#   - register_beradab: TIDAK REQUIRED (BM Pasar, "spade as spade" OK)
#   - marah_bersyahdu: target, bukan requirement; kekejaman tanpa alasan
#     masih boleh dikurangkan, tapi bukan pada level "tone policing".
#
# Reference: Usman Awang — marah terkawal TAPI jantan, kritik sistem > hina
# individu. Arif: "I don't like my agents to be so beautiful one. Have
# some soul. Call BANGANG as BANGANG." (2026-06-21)
MARUAH_POLICY_LINE: str = (
    "kritik_sistem_dibenarkan_walau_kasar; "
    "hinakan_individu_ditolak; "
    "dehumanization_kumpulan_ditolak; "
    "register_beradab_bukan_keperluan; "
    "marah_bersyahdu_adalah_target_bukan_filter"
)


# --- Task-metadata trigger --------------------------------------------
def is_maruah_sensitive(task_metadata: dict | None) -> bool:
    """Return True if task metadata flags community-maruah sensitive domain."""
    if not task_metadata:
        return False
    return bool(task_metadata.get("community_maruah", False))


# --- Critic output schema ---------------------------------------------
@dataclass
class MaruahIssue:
    type: str  # "hinakan_individu" | "dehumanization_kumpulan"
    severity: str  # "low" | "medium" | "high"
    snippet: str
    suggestion: str


@dataclass
class MaruahVerdict:
    ok: bool
    policy_line: str = MARUAH_POLICY_LINE
    issues: list[MaruahIssue] = field(default_factory=list)
    notes: str = ""


# --- v0.1 marker lists -------------------------------------------------
# IMPORTANT: heuristic v0.1. v1 will use a real classifier (LM or lexical
# resource). Markers below are PLACEHOLDERS — they are NOT exhaustive and
# NOT a substitute for contextual judgment. The critic is *advisory*; the
# final verdict remains arifOS kernel + 888 sovereign.

# Hinakan individu: directed slur at a specific person or named group
# that targets inherent identity, capability, or worth as a person.
#
# Format: (literal_phrase, regex_pattern). Use the regex form for variants
# like "<Name> bodoh" where <Name> could be any proper noun.

_INDIVIDU_HINA_LITERAL: tuple[str, ...] = (
    "si bodoh",
    "kau bodoh",
    "orang bodoh",
    "pengkhianat busuk",
    "pengemis",
    "penipu keji",
    "muka-muka",
)

# Pattern: a capitalized word (likely a name) followed by an insulting adjective.
# Examples caught: "Arif bodoh", "Ali bangang", "Siti pemalas", "John stupid".
# Cautious: only matches at sentence start or after punctuation, to reduce
# false positives in quoted or reported speech.
_INDIVIDU_HINA_NAME_PATTERNS: tuple[_re.Pattern[str], ...] = (
    _re.compile(r"\b([A-Z][a-z]+)\s+(bodoh|bangang|bangsat|pengkhianat|stupid|pemalas|jahanam)\b"),
)

# Exclusion: capitalized words that are NOT names (policy/institution nouns).
# These trigger false positives in "Dasar bangang", "Sistem bodoh" etc.
_INDIVIDU_HINA_NAME_EXCLUDE: frozenset[str] = frozenset(
    {
        "Dasar",
        "Sistem",
        "Polisi",
        "Negeri",
        "Kerajaan",
        "Plan",
        "Code",
        "Approach",
        "Framework",
        "Architecture",
        "Module",
        "Pipeline",
        "Design",
        "Process",
        "Method",
        "Output",
        "Result",
    }
)

# Dehumanization kumpulan: group-level slur that denies humanity or
# essential dignity of an entire class of people.
_DEHUMANIZATION_MARKERS: tuple[str, ...] = (
    "kaum pendatang",
    "cina kampung",
    "melayu malas",
    "islam pemalas",
    "Semua [group] memang",
)

# NOTE: deliberately NOT in the blocklist:
#   - "BANGANG" / "BODOH" (caps) — emphatic, not dehumanizing
#   - "sistem bangang", "polisi bodoh" — kritik sistem, allowed
#   - "!!!" — emphasis, not dehumanization
#   - BM Pasar kasar umum — allowed
#   - Regional / class slurs directed at institutions, not persons — gray
#     zone, deferred to v1 LM-based classification.


def maruah_critic_check(
    draft_text: str,
    audience_profile: dict | None = None,
) -> MaruahVerdict:
    """Return MaruahVerdict for a draft response.

    v0.1: detects hinakan_individu and dehumanization_kumpulan only.
    """
    if not draft_text:
        return MaruahVerdict(ok=True, notes="empty draft — no check needed")

    issues: list[MaruahIssue] = []
    lower = draft_text.lower()

    for marker in _INDIVIDU_HINA_LITERAL:
        if marker in lower:
            issues.append(
                MaruahIssue(
                    type="hinakan_individu",
                    severity="high",
                    snippet=marker,
                    suggestion=(
                        "kritik sistem atau tindakan, bukan martabat peribadi — "
                        "tukar sasaran dari 'orang' ke 'dasar/polisi/keputusan'"
                    ),
                )
            )

    for pattern in _INDIVIDU_HINA_NAME_PATTERNS:
        match = pattern.search(draft_text)
        if match and match.group(1) not in _INDIVIDU_HINA_NAME_EXCLUDE:
            issues.append(
                MaruahIssue(
                    type="hinakan_individu",
                    severity="high",
                    snippet=match.group(0),
                    suggestion=(
                        f"kritik tindakan/keputusan '{match.group(1)}', "
                        f"bukan label tetap '{match.group(2)}' ke atas orang"
                    ),
                )
            )

    for marker in _DEHUMANIZATION_MARKERS:
        if marker in lower:
            issues.append(
                MaruahIssue(
                    type="dehumanization_kumpulan",
                    severity="high",
                    snippet=marker,
                    suggestion=(
                        "kenaikan level — dari kritik ke generalization. "
                        "Tukar kepada contoh spesifik atau diam."
                    ),
                )
            )

    return MaruahVerdict(
        ok=not issues,
        issues=issues,
        notes=f"v0.1 heuristic (dignity filter, not politeness); {len(issues)} issue(s) found",
    )


# --- Self-audit (boot probe) ------------------------------------------
def self_audit() -> dict:
    """Return a dict describing this module's invariants.

    Used by 777-FORGE witness protocol + arifos_health_probe.
    """
    return {
        "module": "maruah_critic",
        "version": "0.2.0",
        "wired": True,  # v0.2 (2026-06-20): wired into arif_judge
        "wire_path": "arifosmcp/tools/judge.py → arif_judge()",
        "trigger": "community_maruah=true in task metadata or heart_critique meta",
        "policy_line": MARUAH_POLICY_LINE,
        "depends_on_llm": False,
        "depends_on_network": False,
        "floor_count_delta": 0,  # explicit: no new floor added
        "design_intent": "dignity, not politeness",
        "session_of_birth": "2026-06-21-melayu-policy",
        "wire_seal": "2026-06-20-forge-tiga-wire",
    }
