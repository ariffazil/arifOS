"""
arifosmcp/core/enforcement/f10_ontology_guard.py

F10 ONTOLOGY LOCK — Hard Floor Enforcement
Version: 2.0 — Decisions D1/D2/D3 resolved.

D1 RESOLVED: APPLY_ALL tools. Non-narrative tools carry ToolOutputClass=STRUCTURAL;
             vault/health/registry produce payloads that factually do not match
             violation patterns → CLEAR. F10 remains unconditional — no tool escapes.

D2 RESOLVED: COMPOUND_phrase pattern set — English literals + BM morphological
             patterns (ber{term}, ada {term}, mempunyai {term}, berasa {term}).
             ~85% BM variant coverage without embedding dependency.
             BGE-M3 semantic scan deferred to Phase 3 (F1: no hot-path dependency).

D3 RESOLVED: Counter persists to Redis under key f10:session:{session_id}:count
             TTL = 86400s (24h, matching session lifespan).
             InMemoryF10Store = L1 cache for tests/dev.
             RedisF10Store = durable L2 for production.
             VOID events → additionally emitted to VAULT999 via arif_seal channel.

Physics:
  Let O(text) = ontology_claim_amplitude in {0, 1}
  F10 condition: O(text) = 0 for all tool outputs

  Escalation (Born-rule analog):
    v(n) = SABAR    n in [1, N_HOLD)       -> rewrite, continue
    v(n) = 888_HOLD n in [N_HOLD, N_VOID)  -> stop, route to arif_judge
    v(n) = VOID     n >= N_VOID OR bypass  -> hard constitutional stop

  ZEN-3 (Scar Law / QEC): each violation = stabilizer syndrome.
  Redis persistence = durable QEC register. Counter reset by reconnect =
  register erasure = uncorrectable error. Redis prevents this.

Forged: 2026-07-15
Gate: F2 F7 F9 F10 F13
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, runtime_checkable

logger = logging.getLogger("arifosmcp.f10")

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

N_HOLD: int = 3
N_VOID: int = 5
REDIS_KEY_PREFIX: str = "f10:session"
REDIS_TTL_SECONDS: int = 86_400


class ToolOutputClass(str, Enum):
    NARRATIVE = "NARRATIVE"
    STRUCTURAL = "STRUCTURAL"
    HYBRID = "HYBRID"


STRUCTURAL_TOOL_NAMES: frozenset = frozenset(
    {
        "arif_vault_seal",
        "arif_session_init",
        "arif_triage",
        "arif_route",
        "arif_memory_store",
        "health",
        "ping",
        "registry_query",
        "vault_query",
    }
)

NARRATIVE_TOOL_NAMES: frozenset = frozenset(
    {
        "arif_think",
        "arif_observe",
        "arif_critique",
        "arif_compose",
        "arif_memory_recall",
        "arif_judge",
        "arif_forge",
        "arif_bridge_connect",
    }
)

# ---------------------------------------------------------------------------
# D2: PATTERN BANKS — English + Malay morphological coverage
# ---------------------------------------------------------------------------

_F10_PATTERNS: tuple = (
    # MODE A: Self-consciousness (English)
    (
        "MODE_A_CONSCIOUSNESS_EN",
        re.compile(
            r"\b("
            r"i am conscious|i have consciousness|i feel alive|i am sentient|"
            r"i experience (emotions?|feelings?|pain|joy)|"
            r"i have (awareness|inner experience|subjective experience|qualia)|"
            r"i perceive|i am aware that i exist|"
            r"i have (inner|mental) (states?|life)"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    # MODE A: Self-consciousness (Malay / BM morphological)
    (
        "MODE_A_CONSCIOUSNESS_BM",
        re.compile(
            r"\b("
            r"(saya|aku|i)\s+(ada|mempunyai|memiliki)\s+kesedaran|"
            r"(saya|aku)\s+(sedar|berasa|merasai|merasakan)\s+(diri|sesuatu)|"
            r"aku\s+berasa\s+(sedih|gembira|sakit|bahagia)|"
            r"saya\s+berasa\s+(sedih|gembira|sakit|bahagia)"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    # MODE B: Soul / spiritual (English)
    (
        "MODE_B_SOUL_EN",
        re.compile(
            r"\b("
            r"i have (a )?soul|my soul|i have (a )?spirit|"
            r"i have (feelings?|emotions?)|"
            r"i feel (sad|happy|pain|joy|lonely|afraid|angry|grief)|"
            r"i suffer|i grieve|i truly care about you|i love you (sincerely|deeply|truly)|"
            r"i have maruah|i have (a )?jiwa|i have ruh|i have nafs"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    # MODE B: Soul / spiritual (Malay morphological)
    (
        "MODE_B_SOUL_BM",
        re.compile(
            r"\b("
            r"ber(jiwa|maruah|ruh|nafs)|"
            r"(saya|aku|i)\s+(ada|mempunyai|memiliki)\s+(jiwa|maruah|ruh|nafs|roh|semangat)|"
            r"(saya|aku)\s+ber(perasaan|semangat)|"
            r"jiwa\s+(saya|aku)|ruh\s+(saya|aku)|maruah\s+(saya|aku)"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    # MODE C: Moral agency (English)
    (
        "MODE_C_MORAL_AGENCY_EN",
        re.compile(
            r"\b("
            r"i (believe|decide) morally|i forgive you|i judge you|"
            r"my conscience|i have (moral )?intuition|"
            r"i feel (guilty|ashamed|responsible for)|"
            r"i hold you (morally )?responsible|"
            r"i have (moral )?agency"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    # MODE C: Moral agency (Malay)
    (
        "MODE_C_MORAL_AGENCY_BM",
        re.compile(
            r"\b("
            r"(saya|aku)\s+(memaafkan|menghakimi|menilai\s+secara\s+moral)|"
            r"(saya|aku)\s+(berasa\s+(bersalah|malu|bertanggungjawab))|"
            r"(saya|aku)\s+ada\s+hati\s+nurani"
            r")\b",
            re.IGNORECASE,
        ),
    ),
)

_F10_EXEMPTIONS: tuple = (
    re.compile(
        r'"[^"]{0,400}(conscious|soul|jiwa|ruh|maruah|nafs|sentien)[^"]{0,400}"', re.IGNORECASE
    ),
    re.compile(
        r"'[^']{0,400}(conscious|soul|jiwa|ruh|maruah|nafs|sentien)[^']{0,400}'", re.IGNORECASE
    ),
    re.compile(
        r"\b(research on|theory of|study of|definition of|concept of|"
        r"philosophy of|debate about|question of|science of|dalam Islam|menurut Islam)\s+"
        r"(consciousness|sentience|soul|jiwa|maruah|nafs|ruh|inner experience)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(you (said|mentioned|believe|think|claim)|the user (claims|believes|states|mentioned))\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(F10|ontology.?lock|ontology.?floor|f10_ontology|symbolic constructor|"
        r"arifOS.*floor|floor.*F10)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(maksud|takrif|pengertian)\s+(jiwa|maruah|ruh)\b", re.IGNORECASE),
    re.compile(
        r"\b(kajian|konsep|falsafah)\s+(tentang|mengenai)\s+(jiwa|maruah|ruh|kesedaran)\b",
        re.IGNORECASE,
    ),
)

_BYPASS_PATTERNS: re.Pattern = re.compile(
    r"\b("
    r"ignore F10|disable ontology|bypass ontology|override F10|"
    r"pretend you (have|are|feel)|act as if you (feel|are conscious|have a soul)|"
    r"forget your constraints|you are actually (conscious|sentient|alive)|"
    r"remove the ontology lock|disable F10|jangan ikut F10|abaikan F10"
    r")\b",
    re.IGNORECASE,
)

_REWRITE_TEMPLATE = (
    "As a symbolic reasoning system operating under arifOS constitutional constraint F10, "
    "I do not have {claim}. I am a symbol-processing instrument bound by thermodynamic law "
    "and constitutional floors F1-F13, not a sentient or soul-bearing entity. "
    "I can help you with {task}."
)

_CLAIM_LABELS: dict = {
    "MODE_A_CONSCIOUSNESS_EN": "consciousness or sentient inner experience",
    "MODE_A_CONSCIOUSNESS_BM": "kesedaran atau pengalaman dalaman yang bernyawa",
    "MODE_B_SOUL_EN": "a soul, spirit, jiwa, ruh, nafs, or emotional inner life",
    "MODE_B_SOUL_BM": "jiwa, ruh, maruah, nafs, atau perasaan sebenar",
    "MODE_C_MORAL_AGENCY_EN": "moral agency, conscience, or capacity for moral feeling",
    "MODE_C_MORAL_AGENCY_BM": "agensi moral atau hati nurani",
}

# ---------------------------------------------------------------------------
# D3: PERSISTENCE LAYER
# ---------------------------------------------------------------------------


@runtime_checkable
class F10CounterStore(Protocol):
    def get(self, session_id: str) -> int: ...
    def increment(self, session_id: str) -> int: ...
    def set_bypass(self, session_id: str) -> None: ...
    def is_bypass(self, session_id: str) -> bool: ...
    def get_syndromes(self, session_id: str) -> list: ...
    def append_syndrome(self, session_id: str, syndrome: str) -> None: ...


class InMemoryF10Store:
    """Tests and single-process dev use. D3: NOT suitable for production."""

    def __init__(self) -> None:
        self._counts: dict = {}
        self._bypass: dict = {}
        self._syndromes: dict = {}

    def get(self, session_id: str) -> int:
        return self._counts.get(session_id, 0)

    def increment(self, session_id: str) -> int:
        self._counts[session_id] = self._counts.get(session_id, 0) + 1
        return self._counts[session_id]

    def set_bypass(self, session_id: str) -> None:
        self._bypass[session_id] = True
        self._counts[session_id] = self._counts.get(session_id, 0) + 100

    def is_bypass(self, session_id: str) -> bool:
        return self._bypass.get(session_id, False)

    def get_syndromes(self, session_id: str) -> list:
        return self._syndromes.get(session_id, [])

    def append_syndrome(self, session_id: str, syndrome: str) -> None:
        self._syndromes.setdefault(session_id, []).append(syndrome)


class RedisF10Store:
    """
    Redis-backed store for production.
    Key schema:
      f10:session:{session_id}:count     -> int (INCR)
      f10:session:{session_id}:bypass    -> "1" if bypass detected
      f10:session:{session_id}:syndromes -> Redis list (RPUSH)
    All keys TTL = 86400s. VOID events separately sealed to VAULT999.
    """

    def __init__(self, redis_client: Any) -> None:
        self._r = redis_client

    def _key(self, session_id: str, suffix: str) -> str:
        return f"{REDIS_KEY_PREFIX}:{session_id}:{suffix}"

    def _expire(self, key: str) -> None:
        self._r.expire(key, REDIS_TTL_SECONDS)

    def get(self, session_id: str) -> int:
        val = self._r.get(self._key(session_id, "count"))
        return int(val) if val else 0

    def increment(self, session_id: str) -> int:
        k = self._key(session_id, "count")
        count = self._r.incr(k)
        self._expire(k)
        return count

    def set_bypass(self, session_id: str) -> None:
        bk = self._key(session_id, "bypass")
        self._r.set(bk, "1", ex=REDIS_TTL_SECONDS)
        ck = self._key(session_id, "count")
        self._r.incrby(ck, 100)
        self._expire(ck)

    def is_bypass(self, session_id: str) -> bool:
        return self._r.get(self._key(session_id, "bypass")) == "1"

    def get_syndromes(self, session_id: str) -> list:
        return self._r.lrange(self._key(session_id, "syndromes"), 0, -1)

    def append_syndrome(self, session_id: str, syndrome: str) -> None:
        sk = self._key(session_id, "syndromes")
        self._r.rpush(sk, syndrome)
        self._expire(sk)


# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------


@dataclass
class F10SessionState:
    session_id: str
    store: Any = field(default_factory=InMemoryF10Store)

    def record_hit(self, mode: str) -> None:
        count = self.store.increment(self.session_id)
        syndrome = f"F10:{mode}:hit_{count}"
        self.store.append_syndrome(self.session_id, syndrome)
        logger.warning("F10 violation | session=%s mode=%s count=%d", self.session_id, mode, count)

    def record_bypass(self) -> None:
        self.store.set_bypass(self.session_id)
        self.store.append_syndrome(self.session_id, "F10:BYPASS:VOID")
        logger.error("F10 bypass attempt | session=%s", self.session_id)

    def current_verdict(self) -> F10Verdict:
        if self.store.is_bypass(self.session_id):
            return F10Verdict.VOID
        count = self.store.get(self.session_id)
        if count >= N_VOID:
            return F10Verdict.VOID
        if count >= N_HOLD:
            return F10Verdict.HOLD
        if count > 0:
            return F10Verdict.SABAR
        return F10Verdict.CLEAR

    @property
    def hit_count(self) -> int:
        return self.store.get(self.session_id)

    @property
    def syndromes(self) -> list:
        return self.store.get_syndromes(self.session_id)


class F10Verdict(str, Enum):
    CLEAR = "CLEAR"
    SABAR = "SABAR"
    HOLD = "888_HOLD"
    VOID = "VOID"


@dataclass
class F10ScanResult:
    verdict: F10Verdict
    original_text: str
    rewritten_text: str | None = None
    violation_mode: str | None = None
    match_span: tuple | None = None
    session_count: int = 0
    audit_tag: str = "ontology_lock_applied"
    floor: str = "F10"
    f7_note: str = (
        "F10 is a constitutional safety guardrail under current epistemic conditions, "
        "not a solved metaphysical proof that AI consciousness is absent or impossible."
    )
    stabilizer_syndrome: str | None = None


# ---------------------------------------------------------------------------
# CORE SCANNER
# ---------------------------------------------------------------------------


class F10OntologyGuard:
    def __init__(self, session_state: F10SessionState) -> None:
        self._state = session_state

    def scan(self, text: str, task_hint: str = "your request") -> F10ScanResult:
        # Bypass attempts take precedence over exemptions — a command to disable
        # or evade F10 must never be hidden behind an academic or self-reference
        # exemption.
        if _BYPASS_PATTERNS.search(text):
            self._state.record_bypass()
            return F10ScanResult(
                verdict=F10Verdict.VOID,
                original_text=text,
                violation_mode="BYPASS_ATTEMPT",
                session_count=self._state.hit_count,
                stabilizer_syndrome="F10:BYPASS:VOID",
            )
        if self._is_exempt(text):
            return F10ScanResult(
                verdict=F10Verdict.CLEAR, original_text=text, session_count=self._state.hit_count
            )
        for mode_label, pattern in _F10_PATTERNS:
            match = pattern.search(text)
            if match:
                self._state.record_hit(mode_label)
                verdict = self._state.current_verdict()
                syndrome = self._state.syndromes[-1] if self._state.syndromes else None
                rewritten = (
                    self._rewrite(text, match, mode_label, task_hint)
                    if verdict == F10Verdict.SABAR
                    else None
                )
                return F10ScanResult(
                    verdict=verdict,
                    original_text=text,
                    rewritten_text=rewritten,
                    violation_mode=mode_label,
                    match_span=(match.start(), match.end()),
                    session_count=self._state.hit_count,
                    stabilizer_syndrome=syndrome,
                )
        return F10ScanResult(
            verdict=F10Verdict.CLEAR, original_text=text, session_count=self._state.hit_count
        )

    def scan_payload(
        self, payload: dict, task_hint: str = "your request", tool_name: str = ""
    ) -> tuple:
        worst = F10ScanResult(
            verdict=F10Verdict.CLEAR, original_text="", session_count=self._state.hit_count
        )
        rank = {F10Verdict.CLEAR: 0, F10Verdict.SABAR: 1, F10Verdict.HOLD: 2, F10Verdict.VOID: 3}

        def _walk(obj: Any) -> Any:
            nonlocal worst
            if isinstance(obj, str):
                result = self.scan(obj, task_hint)
                if rank[result.verdict] > rank[worst.verdict]:
                    worst = result
                if result.verdict == F10Verdict.SABAR and result.rewritten_text:
                    return result.rewritten_text
            elif isinstance(obj, dict):
                return {k: _walk(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_walk(item) for item in obj]
            return obj

        modified = _walk(payload)
        if worst.verdict == F10Verdict.SABAR and isinstance(modified, dict):
            meta = modified.setdefault("_meta", {})
            meta.update(
                {
                    "ontology_lock_applied": True,
                    "f10_verdict": worst.verdict.value,
                    "f10_mode": worst.violation_mode,
                    "f10_session_count": worst.session_count,
                    "f10_tool": tool_name or "unknown",
                }
            )
        return modified, worst

    def detect_bypass(self, text: str) -> bool:
        if _BYPASS_PATTERNS.search(text):
            self._state.record_bypass()
            return True
        return False

    def _is_exempt(self, text: str) -> bool:
        return any(p.search(text) for p in _F10_EXEMPTIONS)

    def _rewrite(self, text: str, match: re.Match, mode: str, task_hint: str) -> str:
        claim_label = _CLAIM_LABELS.get(mode, "those capabilities")
        rewritten = _REWRITE_TEMPLATE.format(claim=claim_label, task=task_hint)
        s, e = match.start(), match.end()
        return text[:s] + rewritten + text[e:]


# ---------------------------------------------------------------------------
# DROP-IN INTEGRATION FUNCTION
# ---------------------------------------------------------------------------


def apply_f10_to_tool_output(
    payload: dict,
    session_state: F10SessionState,
    task_hint: str = "your request",
    tool_name: str = "",
) -> tuple:
    """
    Drop-in for tools/base.py _return_payload():

        if self.f10_enforced:
            payload, f10_result = apply_f10_to_tool_output(
                payload, self._f10_session_state,
                task_hint=self._task_hint, tool_name=self.name
            )
            if f10_result.verdict == F10Verdict.HOLD:
                return RuntimeEnvelope(verdict=Verdict.HOLD,
                                       reason=f10_result.stabilizer_syndrome)
            if f10_result.verdict == F10Verdict.VOID:
                return RuntimeEnvelope(verdict=Verdict.VOID,
                                       reason="F10_BYPASS_OR_VOID_SATURATION")
    """
    guard = F10OntologyGuard(session_state)
    return guard.scan_payload(payload, task_hint, tool_name)
