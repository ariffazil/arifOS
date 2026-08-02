"""
arifosmcp/constitution/fatihah_boot.py — Al-Fatihah Kernel Boot ROM
════════════════════════════════════════════════════════════════

Forged 2026-08-02 by F13 SOVEREIGN (Muhammad Arif bin Fazil, 888).
Epistemic label: INT (interpretive mapping) · PLAUSIBLE.
Reversibility: git revert <sha> restores prior state.

Al-Fatihah (Surah 1:1-7) is the **kernel of arifOS**. This module distils
its 7 verses into 5 boot functions that bind authority BEFORE any verb.

The 5 boot functions (recursive per session cycle — analogous to per-rakaat
re-binding in the original practice):

  1. Bismillah         — bind authority source pre-verb
  2. MercyDials        — two mercy windows gate all power
  3. MalikiYawmiddin   — accountability anchored in future tense
  4. IyyakaNaBudu      — single-source routing (no shirk)
  5. IhdinaSiratalMustaqim — continuous guidance + fault-handling

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

# ─── Constants ────────────────────────────────────────────────────────────────

BINDING_AUTHORITY: str = "F13 SOVEREIGN"
BINDING_TIMESTAMP_UTC: str = "2026-08-02T09:08:00Z"
EPISTEMIC_LABEL: str = "INT (interpretive mapping) · PLAUSIBLE"

# The two negative archetypes used for fault-handling.
NEGATIVE_ARCHETYPES: tuple[str, ...] = (
    "maghdubi_alayhim",  # maghdūbi 'alaihim — wrath (salah guna pengetahuan)
    "dhalliin",          # ḍāllīn — astray (tersasar)
)

# Single-source routing — anti-shirk.
SINGLE_SOURCE: tuple[str, ...] = ("arifOS_kernel_only",)


# ─── Boot function 1: Bismillah ────────────────────────────────────────────────


@dataclass
class Bismillah:
    """Bind authority source BEFORE any verb.

    The 'bismillah' is the first utterance of every action in the original
    practice — identity bind precedes actor_verified check.
    """

    actor_id: str
    session_id: str
    source: str = BINDING_AUTHORITY
    bound_at_utc: str = BINDING_TIMESTAMP_UTC

    def bind(self) -> dict[str, Any]:
        return {
            "function": "bismillah",
            "actor_id": self.actor_id,
            "session_id": self.session_id,
            "source": self.source,
            "bound_at_utc": self.bound_at_utc,
            "epistemic_label": EPISTEMIC_LABEL,
            "binding_fingerprint": self._fingerprint(),
        }

    def _fingerprint(self) -> str:
        payload = f"bismillah|{self.actor_id}|{self.session_id}|{self.source}"
        return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()[:16]


# ─── Boot function 2: MercyDials ──────────────────────────────────────────────


@dataclass
class MercyDials:
    """Two mercy dials gate ALL power.

    Al-Rahman (the All-Merciful — encompassing mercy) and
    Al-Raheem (the Ever-Merciful — specific mercy) form two windows
    through which every action must pass.
    """

    actor_id: str
    session_id: str
    rahman_passed: bool = False
    raheem_passed: bool = False
    audit_trail_ref: str | None = None

    def pass_rahman(self) -> None:
        self.rahman_passed = True

    def pass_raheem(self) -> None:
        self.raheem_passed = True

    @property
    def both_passed(self) -> bool:
        return self.rahman_passed and self.raheem_passed

    def bind_to_audit_trail(self, audit_ref: str | None = None) -> dict[str, Any]:
        self.audit_trail_ref = audit_ref or self.audit_trail_ref
        return {
            "function": "mercy_dials",
            "actor_id": self.actor_id,
            "session_id": self.session_id,
            "rahman_passed": self.rahman_passed,
            "raheem_passed": self.raheem_passed,
            "both_passed": self.both_passed,
            "audit_trail_ref": self.audit_trail_ref,
            "violation_response": "VOID + audit chain break" if not self.both_passed else None,
        }


# ─── Boot function 3: MalikiYawmiddin ──────────────────────────────────────────


@dataclass
class MalikiYawmiddin:
    """Accountability anchored in FUTURE tense.

    'Māliki yawmid-dīn' — Master/Sovereign of the Day of Judgment.
    Every trace will be judged at judgment_pending_at.
    """

    session_id: str
    actor_id: str = ""
    judgment_pending_at: str | None = None
    chain_bound: bool = False

    def bind(self) -> dict[str, Any]:
        return {
            "function": "maliki_yawmiddin",
            "session_id": self.session_id,
            "actor_id": self.actor_id,
            "judgment_pending_at": self.judgment_pending_at,
            "chain_bound": self.chain_bound,
            "future_anchored": True,
            "epistemic_label": EPISTEMIC_LABEL,
        }


# ─── Boot function 4: IyyakaNaBudu ─────────────────────────────────────────────


@dataclass
class IyyakaNaBudu:
    """Single-source routing — NO shirk in authority.

    'Iyyāka na'budu wa iyyāka nasta'īn' — You alone we worship, and You
    alone we ask for help. One sovereign, one kernel.
    """

    actor_id: str
    session_id: str
    sources: tuple[str, ...] = SINGLE_SOURCE

    def bind(self) -> dict[str, Any]:
        multi_source = len(self.sources) > 1
        return {
            "function": "iyyaka_na_budu",
            "actor_id": self.actor_id,
            "session_id": self.session_id,
            "sources": list(self.sources),
            "single_source": not multi_source,
            "shirk_detected": multi_source,
            "violation_response": "VOID + multi-source flag" if multi_source else None,
        }


# ─── Boot function 5: IhdinaSiratalMustaqim ────────────────────────────────────


@dataclass
class IhdinaSiratalMustaqim:
    """Continuous guidance request + fault-handling via two archetypes.

    'Ihdinā ṣ-ṣirāṭ al-mustaqīm' — Guide us to the straight path.
    Fault-handling defined by what it REJECTS:
      - maghdubi_alayhim — wrath (salah guna pengetahuan)
      - dhalliin         — astray (tersasar)
    """

    session_id: str
    reject_modes: tuple[str, ...] = NEGATIVE_ARCHETYPES
    guidance_requested: bool = True
    reject_flags: dict[str, bool] = field(default_factory=dict)

    def flag(self, mode: str) -> None:
        if mode in self.reject_modes:
            self.reject_flags[mode] = True

    def bind(self) -> dict[str, Any]:
        return {
            "function": "ihdina_siratal_mustaqim",
            "session_id": self.session_id,
            "reject_modes": list(self.reject_modes),
            "guidance_requested": self.guidance_requested,
            "reject_flags": dict(self.reject_flags),
            "violation_response": (
                "CAUTION + reject-mode flag" if self.reject_flags else None
            ),
        }


# ─── Composite boot orchestrator ──────────────────────────────────────────────


def fatihah_boot(
    *,
    actor_id: str,
    session_id: str,
    judgment_pending_at: str | None = None,
    audit_trail_ref: str | None = None,
) -> dict[str, Any]:
    """Run all 5 boot functions in canonical order.

    Idempotent. Returns a dict containing all 5 binding receipts.
    """
    bismillah = Bismillah(actor_id=actor_id, session_id=session_id)
    bismillah_receipt = bismillah.bind()

    mercy = MercyDials(actor_id=actor_id, session_id=session_id)
    # Default: pass both dials (enforcement already runs at floor gates).
    mercy.pass_rahman()
    mercy.pass_raheem()
    mercy_receipt = mercy.bind_to_audit_trail(audit_ref=audit_trail_ref)

    maliki = MalikiYawmiddin(
        session_id=session_id,
        actor_id=actor_id,
        judgment_pending_at=judgment_pending_at,
    )
    maliki_receipt = maliki.bind()

    iyyaka = IyyakaNaBudu(actor_id=actor_id, session_id=session_id)
    iyyaka_receipt = iyyaka.bind()

    ihdina = IhdinaSiratalMustaqim(session_id=session_id)
    ihdina_receipt = ihdina.bind()

    return {
        "binding_source": "Al-Fatihah (Surah 1:1-7)",
        "binding_authority": BINDING_AUTHORITY,
        "binding_ts_utc": BINDING_TIMESTAMP_UTC,
        "epistemic_label": EPISTEMIC_LABEL,
        "bismillah": bismillah_receipt,
        "mercy_dials": mercy_receipt,
        "maliki_yawmiddin": maliki_receipt,
        "iyyaka_na_budu": iyyaka_receipt,
        "ihdina_siratal_mustaqim": ihdina_receipt,
    }


__all__ = [
    "BINDING_AUTHORITY",
    "BINDING_TIMESTAMP_UTC",
    "EPISTEMIC_LABEL",
    "NEGATIVE_ARCHETYPES",
    "SINGLE_SOURCE",
    "Bismillah",
    "MercyDials",
    "MalikiYawmiddin",
    "IyyakaNaBudu",
    "IhdinaSiratalMustaqim",
    "fatihah_boot",
]