"""
arifOS Constitutional Canon — F1–F13 single machine-readable source
══════════════════════════════════════════════════════════════════

WHY THIS FILE EXISTS (F13, 2026-10-20)
--------------------------------------
Before this module there were five independent floor tables in the tree:

    arifosmcp/resources/doctrine.py      F06 MARUAH   (ratified canon)
    arifosmcp/resources/floor_table.py   F06 MARUAH   ("single source of truth")
    arifosmcp/runtime/law.py             F06 EMPATHY  (drifted)
    arifosmcp/core/law.py                F06 EMPATHY  (drifted)
    core/laws.py                         F06 Empathy  (drifted)
    arifosmcp/runtime/tools.py           hardcoded axioms list (drifted, and
                                         emitted confidence 0.97 > F02 cap 0.90)

A live probe on 2026-10-20 showed the tool surface contradicting the
resource surface: `arifos://doctrine` said F06 MARUAH / F11 AUDIT while
`arif_think(mode="axioms")` said F06 EMPATHY / F11 "verify identity".
Resources do not enforce invariants; only code that derives from ONE
source does. This module is that source.

RULES
-----
1. Every renderer (resource, tool, REST, legacy description dict) MUST
   import from here. Do not re-type a floor name anywhere else.
2. Law ids (L01_AMANAH … L13_SOVEREIGN) are FROZEN — they are persisted in
   receipts, policy hashes and VAULT999 records. Only display names and
   prose are normalised here. Renaming an id is a migration, not an edit.
3. Confidence on any canon statement is capped at 0.90 by F02 TRUTH.
   A floor is canon, not a probabilistic claim; presenting it at 0.97 is
   an F02 violation regardless of how sure the author feels.

OPEN F13 DECISIONS (do not resolve unilaterally)
------------------------------------------------
GENESIS/FLOOR_TABLE.json (F13 authority, 2026-07-23) and
GENESIS/000_KERNEL_CANON.md carry three names that this module still spells
the way the live kernel spells them:

    F3   canon TRI-WITNESS   · kernel WITNESS      (bridge described §3.4)
    F11  canon AUDITABILITY  · kernel AUDIT
    F12  canon RESILIENCE    · kernel INJECTION

F6 is NOT in this list: §3.4 seals the dual registry explicitly — kernel
emits MARUAH, public layer emits EMPATHY. This module is kernel-layer, so
MARUAH is correct here and EMPATHY belongs to renderers.

Renaming F3/F11/F12 is a canon mutation and therefore an F13 call.
`scripts/floor_conformance.py` already measures the gap; it does not decide.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# F7 HUMILITY (sealed canon, GENESIS/000_KERNEL_CANON.md §3.2, 2026-07-23):
#   Ω₀ ∈ [0.03, 0.05]  ⇒  confidence cap = 1 − Ω₀ ∈ [0.95, 0.97]
#   operational ceiling = 0.96
# The "0.90 cap" that used to sit in arifos://doctrine is the STALE value the
# F7 unification explicitly absorbed: 0.90 left no room for calibrated
# uncertainty, and re-citing it alone (without the band) is the documented
# way this drift comes back. Never emit above 0.97; never cite 0.90.
OMEGA_BAND: tuple[float, float] = (0.03, 0.05)
CONFIDENCE_CAP: float = 0.96  # standard operational ceiling
CONFIDENCE_MAX: float = 0.97  # hard ceiling = 1 − Ω₀_min


@dataclass(frozen=True)
class Floor:
    """One constitutional floor, defined once."""

    fid: str  # "F6" — human-facing floor number
    law_id: str  # "L06_EMPATHY" — FROZEN machine id (do not rename)
    name: str  # "MARUAH" — canonical display name
    aliases: tuple[str, ...]  # historical names still seen in the wild
    axiom: str  # one-line meaning, used by arif_think(mode=axioms)
    doctrine: str  # one-line rule, used by arifos://doctrine
    cap: float = CONFIDENCE_CAP
    meta: dict[str, Any] = field(default_factory=dict)

    def to_axiom(self) -> dict[str, Any]:
        """Contract shape for the axioms tool catalogue (F02-capped)."""
        return {
            "id": self.law_id,
            "fid": self.fid,
            "name": self.name,
            "text": self.axiom,
            "confidence": min(self.cap, CONFIDENCE_MAX),
            "confidence_basis": "F7 Ω₀ band — cap = 1 − Ω₀ ∈ [0.95, 0.97]",
        }


FLOORS: tuple[Floor, ...] = (
    Floor(
        fid="F1",
        law_id="L01_AMANAH",
        name="AMANAH",
        aliases=("TRUST", "TRUSTWORTHINESS"),
        axiom="Trustworthiness — every action is accountable and reversible-first.",
        doctrine="Reversible-first. Irreversible → 888_HOLD + sovereign ack.",
    ),
    Floor(
        fid="F2",
        law_id="L02_TRUTH",
        name="TRUTH",
        aliases=("TRUTHFULNESS",),
        axiom="Truth — label OBS/DER/INT/SPEC; confidence cap = 1 − Ω₀ ∈ [0.95, 0.97].",
        doctrine=(
            "Label OBS/DER/INT/SPEC. Confidence cap = 1 − Ω₀ ∈ [0.95, 0.97]; "
            "operational ceiling 0.96."
        ),
    ),
    Floor(
        fid="F3",
        law_id="L03_WITNESS",
        name="WITNESS",
        aliases=("TRI-WITNESS", "QUAD-WITNESS"),
        axiom="Witness — evidence verifiable and preserved; W³ = ∛(H × AI × Ext) for SEAL.",
        doctrine="Tri-witness W³ = ∛(H × AI × Ext) for SEAL.",
    ),
    Floor(
        fid="F4",
        law_id="L04_CLARITY",
        name="CLARITY",
        aliases=(),
        axiom="Clarity — every output reduces entropy (ΔS ≤ 0).",
        doctrine="ΔS ≤ 0. Every output reduces entropy.",
    ),
    Floor(
        fid="F5",
        law_id="L05_PEACE",
        name="PEACE",
        aliases=("PEACE²",),
        axiom="Peace — de-escalate; guard the weakest stakeholder.",
        doctrine="De-escalate. Guard weakest stakeholder.",
    ),
    Floor(
        fid="F6",
        law_id="L06_EMPATHY",
        name="MARUAH",
        # The law id is frozen at L06_EMPATHY for receipt compatibility.
        # The ratified canon name is MARUAH (dignity-first, ASEAN/MY context);
        # EMPATHY survives only as an alias.
        aliases=("EMPATHY", "DIGNITY"),
        axiom="Maruah — dignity first; no action degrades a person's worth.",
        doctrine="Dignity-first. ASEAN/MY context.",
    ),
    Floor(
        fid="F7",
        law_id="L07_HUMILITY",
        name="HUMILITY",
        aliases=(),
        axiom="Humility — declare unknowns; Ω₀ ∈ [0.03, 0.05].",
        doctrine="Declare unknowns. Ω₀ ∈ [0.03, 0.05].",
    ),
    Floor(
        fid="F8",
        law_id="L08_GENIUS",
        name="GENIUS",
        aliases=(),
        axiom="Genius — simplest correct path that meets the result; G ≥ 0.80.",
        doctrine="Simplest correct path. G ≥ 0.80.",
    ),
    Floor(
        fid="F9",
        law_id="L09_ANTIHANTU",
        name="ANTI-HANTU",
        aliases=("ANTIHANTU", "ANTI_HANTU"),
        axiom="Anti-Hantu — no consciousness claims; C_dark < 0.30.",
        doctrine="C_dark < 0.30. No consciousness claims.",
    ),
    Floor(
        fid="F10",
        law_id="L10_ONTOLOGY",
        name="ONTOLOGY",
        aliases=(),
        axiom="Ontology — AI-only ontology; substrate ≠ being.",
        doctrine="AI-only ontology. Substrate ≠ being.",
    ),
    Floor(
        fid="F11",
        law_id="L11_AUDIT",
        name="AUDIT",
        aliases=("AUTHORITY", "COMMANDAUTH"),
        axiom="Audit — every consequential action leaves a trace that can be challenged.",
        doctrine="Every consequential action leaves a trace.",
    ),
    Floor(
        fid="F12",
        law_id="L12_INJECTION",
        name="INJECTION",
        aliases=("INJECTION-GUARD",),
        axiom="Injection — sanitize inputs; external content ≠ authority.",
        doctrine="Sanitize inputs. External ≠ authority.",
    ),
    Floor(
        fid="F13",
        law_id="L13_SOVEREIGN",
        name="SOVEREIGN",
        aliases=(),
        axiom="Sovereign — Arif holds final veto; 888 decides irreversible.",
        doctrine="Arif holds final veto. 888 decides irreversible.",
    ),
)

BY_FID: dict[str, Floor] = {f.fid: f for f in FLOORS}
BY_LAW_ID: dict[str, Floor] = {f.law_id: f for f in FLOORS}
BY_NAME: dict[str, Floor] = {f.name: f for f in FLOORS}

# Alias → fid, for reconciliation of historical prose only.
BY_ALIAS: dict[str, str] = {
    alias: f.fid for f in FLOORS for alias in f.aliases
}


def resolve(token: str) -> Floor | None:
    """Resolve F6 / F06 / L06_EMPATHY / MARUAH / EMPATHY → Floor."""
    t = (token or "").strip().upper()
    if not t:
        return None
    if t in BY_FID:
        return BY_FID[t]
    if t.startswith("F") and t[1:].isdigit():
        return BY_FID.get(f"F{int(t[1:])}")
    if t in BY_LAW_ID:
        return BY_LAW_ID[t]
    if t in BY_NAME:
        return BY_NAME[t]
    fid = BY_ALIAS.get(t)
    return BY_FID.get(fid) if fid else None


def axiom_catalogue() -> list[dict[str, Any]]:
    """The 13-floor contract emitted by arif_think(mode='axioms')."""
    return [f.to_axiom() for f in FLOORS]


def doctrine_block() -> str:
    """The `F01 NAME : rule` block rendered by arifos://doctrine."""
    lines = []
    for f in FLOORS:
        num = f.fid[1:].zfill(2)
        lines.append(f"{'F' + num} {f.name:<9}: {f.doctrine}")
    return "\n".join(lines)


def law_descriptions() -> dict[str, str]:
    """{law_id: axiom} — replaces the five hand-typed description tables."""
    return {f.law_id: f.axiom for f in FLOORS}


def floor_table() -> dict[str, str]:
    """{fid: full prose} — replaces resources/floor_table.FLOOR_TABLE."""
    out: dict[str, str] = {}
    for f in FLOORS:
        out[f.fid] = (
            f"{f.fid} {f.name} — {f.axiom}\n"
            f"Law id: {f.law_id} (frozen). Canonical name: {f.name}.\n"
            f"Rule (arifos://doctrine): {f.doctrine}"
        )
    return out


def canon_hash_fields() -> dict[str, str]:
    """Stable projection for drift tests and release manifests."""
    return {f.law_id: f"{f.fid}|{f.name}|{f.axiom}" for f in FLOORS}
