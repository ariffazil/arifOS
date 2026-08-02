"""
arifosmcp/constitution/ayat_bindings.py — Ayat al-Kursi Runtime Bindings
═════════════════════════════════════════════════════════════════════════

Forged 2026-08-02 by F13 SOVEREIGN (Muhammad Arif bin Fazil, 888).
Epistemic label: INT (interpretive mapping) · PLAUSIBLE.
Reversibility: git revert <sha> restores prior state.

Maps the four properties of Ayat al-Kursi (Al-Baqarah 2:255) to runtime
enforcement contracts. This is the ENFORCEMENT layer — Al-Fatihah is the
BINDING layer (see fatihah_boot.py). Ayat al-Kursi enforces; Al-Fatihah binds.

The four properties:
  1. al-Hayy (الحيّ) — daemon heartbeat floor
  2. al-Qayyum (القيوم) — kernel self-sustain rule
  3. لا تأخذه سنة ولا نوم — anti-sleep-claim window (≥7-day evidence)
  4. لا يشفع إلا بإذنه — F13 permission-gate hard

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

# Source-checked Arabic text of Ayat al-Kursi (Al-Baqarah 2:255).
# Standard diacritical marks preserved for textual integrity.
AYAT_AL_KURSI_ARABIC: str = (
    "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ "
    "لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ ۚ "
    "لَّهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ ۗ "
    "مَن ذَا الَّذِي يَشْفَعُ عِندَهُ إِلَّا بِإِذْنِهِ ۚ "
    "يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ "
    "وَلَا يُحِيطُونَ بِشَيْءٍ مِّنْ عِلْمِهِ إِلَّا بِمَا شَاءَ ۚ "
    "وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ ۖ "
    "وَلَا يَئُودُهُ حِفْظُهُمَا ۚ وَهُوَ الْعَلِيُّ الْعَظِيمُ"
)

# Source-checked short phrases for the four runtime properties.
_PHRASES: dict[str, str] = {
    "al_hayy": "الحيّ",
    "al_qayyum": "القيوم",
    "no_sleep_claim": "لا تأخذه سنة ولا نوم",
    "no_intercession_without_permission": "لا يشفع عنده إلا بإذنه",
}

_MEANINGS: dict[str, str] = {
    "al_hayy": "The Ever-Living",
    "al_qayyum": "The Self-Subsisting",
    "no_sleep_claim": "Neither drowsiness nor sleep overtakes Him",
    "no_intercession_without_permission": "No one can intercede except by His permission",
}

# Seven-day evidence window for "normal" status claims.
NO_SLEEP_CLAIM_WINDOW_DAYS: int = 7

# Binding authority: F13 SOVEREIGN (Muhammad Arif bin Fazil).
BINDING_AUTHORITY: str = "F13 SOVEREIGN"
BINDING_TIMESTAMP_UTC: str = "2026-08-02T09:08:00Z"
EPISTEMIC_LABEL: str = "INT (interpretive mapping) · PLAUSIBLE"


@dataclass(frozen=True)
class RuntimeHeartProperty:
    """One runtime enforcement property derived from Ayat al-Kursi."""

    key: str
    arabic: str
    meaning: str
    runtime_layer: str
    enforcement: str
    violation_response: str


RUNTIME_HEART_PROPERTIES: dict[str, RuntimeHeartProperty] = {
    key: RuntimeHeartProperty(
        key=key,
        arabic=_PHRASES[key],
        meaning=_MEANINGS[key],
        runtime_layer=layer,
        enforcement=enf,
        violation_response=viol,
    )
    for key, (layer, enf, viol) in {
        "al_hayy": (
            "daemon_heartbeat",
            "liveness_proof_required_per_session",
            "HOLD + reinit",
        ),
        "al_qayyum": (
            "watchdog_of_watchdogs",
            "kernel_self_sustain_no_external_dep",
            "ESCALATE_F13",
        ),
        "no_sleep_claim": (
            "health_claim_gate",
            f"no_normal_status_without_{NO_SLEEP_CLAIM_WINDOW_DAYS}day_evidence",
            "DEMOTE_to_DEGRADED",
        ),
        "no_intercession_without_permission": (
            "f13_gate",
            "no_irreversible_action_without_ack",
            "VOID + require_human_seal",
        ),
    }.items()
}


@dataclass
class RuntimeHeartBinding:
    """Session-level binding to Ayat al-Kursi runtime properties.

    Idempotent: re-binding overwrites the prior binding with the same
    source/authority stamp. Reversible via F1 AMANAH (git revert of the
    commit that introduced this binding).
    """

    source: str = "Ayat al-Kursi (Al-Baqarah 2:255)"
    binding_authority: str = BINDING_AUTHORITY
    binding_ts_utc: str = BINDING_TIMESTAMP_UTC
    epistemic_label: str = EPISTEMIC_LABEL
    properties: dict[str, RuntimeHeartProperty] = field(
        default_factory=lambda: RUNTIME_HEART_PROPERTIES
    )
    rollback_handle: str = "git revert <commit-sha>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "binding_authority": self.binding_authority,
            "binding_ts_utc": self.binding_ts_utc,
            "epistemic_label": self.epistemic_label,
            "rollback_handle": self.rollback_handle,
            "properties": {
                key: {
                    "arabic": prop.arabic,
                    "meaning": prop.meaning,
                    "runtime_layer": prop.runtime_layer,
                    "enforcement": prop.enforcement,
                    "violation_response": prop.violation_response,
                }
                for key, prop in self.properties.items()
            },
        }

    def fingerprint(self) -> str:
        """SHA-256[:16] fingerprint of the binding source."""
        return "sha256:" + hashlib.sha256(AYAT_AL_KURSI_ARABIC.encode()).hexdigest()[:16]


def bind_ayat_al_kursi_to_session(session: dict[str, Any]) -> dict[str, Any]:
    """Idempotently bind a session dict to Ayat al-Kursi runtime properties.

    Stores the binding under session["runtime_heart"]. Does not mutate
    other session fields. Safe to call repeatedly.
    """
    binding = RuntimeHeartBinding()
    session["runtime_heart"] = binding.to_dict()
    session["runtime_heart_fingerprint"] = binding.fingerprint()
    return session


__all__ = [
    "AYAT_AL_KURSI_ARABIC",
    "RUNTIME_HEART_PROPERTIES",
    "RuntimeHeartProperty",
    "RuntimeHeartBinding",
    "bind_ayat_al_kursi_to_session",
    "NO_SLEEP_CLAIM_WINDOW_DAYS",
    "BINDING_AUTHORITY",
    "BINDING_TIMESTAMP_UTC",
    "EPISTEMIC_LABEL",
]